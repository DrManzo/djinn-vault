#!/usr/bin/env python3
"""
pup.py — Pup Client Library
Every pup imports this and uses PupClient to talk to hellhound.py.

Usage:
    from pup import PupClient

    async def main():
        async with PupClient(name="gateway", gate="discord-dm", token="...") as pup:
            await pup.observe(domain="comms", event="msg_routed", payload={...})
            await pup.wait_recall()   # blocks until RECALL received
"""

import asyncio
import json
import logging
import os
import socket
import time
from pathlib import Path


def sd_notify(state: str) -> None:
    """
    Minimal sd_notify(3) implementation — no systemd-python dependency.
    Sends a datagram to the socket path in $NOTIFY_SOCKET, per the
    documented protocol. No-op if the env var isn't set (e.g. running
    outside systemd, or Type= isn't notify).
    """
    addr = os.environ.get("NOTIFY_SOCKET")
    if not addr:
        return
    if addr.startswith("@"):
        addr = "\0" + addr[1:]  # abstract socket namespace
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sock:
            sock.connect(addr)
            sock.sendall(state.encode())
    except OSError as exc:
        log.warning("sd_notify(%r) failed: %s", state, exc)


SOCK_PATH = Path.home() / ".local" / "share" / "hellhound" / "skull" / "skull.sock"
WATCHDOG_PING_SEC = 10  # comfortably under pup@.service's WatchdogSec=30

log = logging.getLogger("pup")


class RecallReceived(Exception):
    """Raised when the master sends a RECALL command."""
    def __init__(self, reason: str = "", ref: str = ""):
        self.reason = reason
        self.ref    = ref
        super().__init__(f"RECALL: {reason} (ref={ref})")


class PupClient:
    """
    Async context manager wrapping the hellhound Unix socket protocol.

    Parameters
    ----------
    name  : unique pup identifier (matches pup@<name>.service)
    gate  : gate type string (e.g. 'discord-dm', 'moonraker')
    token : pre-shared secret provisioned by `hellhound pup new <name>`
    """

    def __init__(
        self,
        name:  str,
        gate:  str,
        token: str,
        sock_path: Path = SOCK_PATH,
    ):
        self.name      = name
        self.gate      = gate
        self.token     = token
        self.sock_path = sock_path

        self._reader:   asyncio.StreamReader  | None = None
        self._writer:   asyncio.StreamWriter  | None = None
        self._pup_id:   str | None = None
        self._recall_ev = asyncio.Event()
        self._recall_reason: str = ""
        self._recall_ref:    str = ""

        self._connected_at     = 0.0
        self._observations_sent = 0
        self._hb_interval      = 30
        self._hb_task:  asyncio.Task | None = None
        self._recv_task: asyncio.Task | None = None
        self._watchdog_task: asyncio.Task | None = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------
    async def __aenter__(self) -> "PupClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------
    async def connect(self):
        self._reader, self._writer = await asyncio.open_unix_connection(
            str(self.sock_path)
        )
        log.info("[%s] Connected to hellhound socket", self.name)

        # CONNECT handshake
        await self._send({
            "type":  "CONNECT",
            "name":  self.name,
            "gate":  self.gate,
            "token": self.token,
        })
        ack = await self._recv_one()
        if ack.get("type") != "ACK":
            raise RuntimeError(f"CONNECT rejected: {ack}")

        self._pup_id      = ack["pup_id"]
        self._hb_interval = ack.get("heartbeat_interval", 30)
        self._connected_at = time.time()
        log.info("[%s] Registered as %s", self.name, self._pup_id)

        # Start background tasks
        self._recv_task = asyncio.create_task(self._recv_loop(), name=f"{self.name}-recv")
        self._hb_task   = asyncio.create_task(self._heartbeat_loop(), name=f"{self.name}-hb")
        self._watchdog_task = asyncio.create_task(self._watchdog_loop(), name=f"{self.name}-watchdog")

        # First successful connect proves the process is alive and useful —
        # tell systemd. Fixes the 27-day silent-death bug: Type=simple never
        # asked the process to prove it was still healthy after this point.
        sd_notify("READY=1")

    async def disconnect(self):
        for task in (self._hb_task, self._recv_task, self._watchdog_task):
            if task and not task.done():
                task.cancel()
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
        log.info("[%s] Disconnected", self.name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def observe(
        self,
        domain:   str,
        event:    str,
        payload:  dict | None = None,
        severity: str = "info",
    ):
        """
        Send a structured observation to hellhound.
        severity: 'debug' | 'info' | 'warning' | 'error' | 'critical'
        """
        await self._send({
            "type":     "OBSERVE",
            "domain":   domain,
            "event":    event,
            "payload":  payload or {},
            "severity": severity,
        })
        self._observations_sent += 1

    async def wait_recall(self):
        """
        Block until hellhound sends a RECALL command, then raise RecallReceived.
        Call this at the end of your pup's main loop so the pup exits cleanly.
        """
        await self._recall_ev.wait()
        raise RecallReceived(self._recall_reason, self._recall_ref)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    async def _recv_loop(self):
        """Background task: listen for server-initiated messages (RECALL)."""
        try:
            while True:
                msg = await self._recv_one()
                if msg.get("type") == "RECALL":
                    self._recall_reason = msg.get("reason", "")
                    self._recall_ref    = msg.get("ref", "")
                    log.warning("[%s] RECALL received: %s", self.name, self._recall_reason)
                    self._recall_ev.set()
                    return
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            log.error("[%s] recv loop error: %s", self.name, exc)
            self._recall_ev.set()   # unblock wait_recall on error

    async def _heartbeat_loop(self):
        """Background task: send periodic HEARTBEAT messages."""
        try:
            while True:
                await asyncio.sleep(self._hb_interval)
                uptime = time.time() - self._connected_at
                await self._send({
                    "type":               "HEARTBEAT",
                    "uptime":             round(uptime, 1),
                    "observations_sent": self._observations_sent,
                })
        except asyncio.CancelledError:
            pass

    async def _watchdog_loop(self):
        """
        Background task: tell systemd this process is still alive, more
        frequently than the hellhound heartbeat. Independent of whether
        the connection to hellhound itself is healthy — if this loop is
        still running, the event loop isn't hung, which is what the
        systemd watchdog actually needs to know.
        """
        try:
            while True:
                sd_notify("WATCHDOG=1")
                await asyncio.sleep(WATCHDOG_PING_SEC)
        except asyncio.CancelledError:
            pass

    async def _send(self, obj: dict):
        self._writer.write((json.dumps(obj) + "\n").encode())
        await self._writer.drain()

    async def _recv_one(self) -> dict:
        raw = await self._reader.readline()
        return json.loads(raw.decode().strip())
