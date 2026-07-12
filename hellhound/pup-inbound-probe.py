#!/usr/bin/env python3
"""
pup-inbound-probe.py — Inbound reconnaissance/brute-force detection pup

Watches surfaces Salomon can actually see: SSH into Salomon itself, and
the Forge dashboard (also hosted on Salomon). Moonraker is NOT watched
here — it runs on each printer's own board, not on Salomon, so this
process has no visibility into traffic hitting it. Real Moonraker
protection would need an agent running on each printer host, which is a
separate, future task.

Detection is deterministic — plain sliding-window thresholds against
hellhound/gates/inbound_probe_rules.py. No model inference anywhere in
this file. Every trigger: block (unless LAN + soft rule) -> incident
file in the vault -> Telegram alert -> also reported to hellhound's own
registry via pup.observe(), for visibility/health-check purposes only.

Environment variables (from hellhound-inbound-probe.env):
    PUP_NAME  — injected by systemd pup@.service (expected: inbound-probe)
    HH_TOKEN  — pre-shared hellhound auth token
"""

import asyncio
import ipaddress
import logging
import os
import re
import subprocess
import sys
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Deque, Dict, List, Optional, Tuple

from pup import PupClient, RecallReceived

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gates.inbound_probe_block import block_ip
from gates.inbound_probe_incident import write_incident
from gates.inbound_probe_notify import notify_telegram
from gates.inbound_probe_rules import RULES

log = logging.getLogger("pup-inbound-probe")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

PUP_NAME = os.environ.get("PUP_NAME", "inbound-probe")
HH_TOKEN = os.environ.get("HH_TOKEN", "")

BASE_DIR = Path.home() / ".local/share/hellhound"
TRUSTED_IPS_PATH = BASE_DIR / "config/trusted-ips.txt"

# Only surfaces this process can actually observe from Salomon.
# djinn-shop-dashboard is a --user unit; ssh is a system unit.
DASHBOARD_UNIT = "djinn-shop-dashboard.service"
SSH_UNIT = "ssh"

DASHBOARD_LOG_RE = re.compile(
    r'^(?P<ip>\d+\.\d+\.\d+\.\d+) \S+ \S+ \[[^\]]+\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) [^"]+" (?P<status>\d{3})'
)
SSH_FAIL_RE = re.compile(
    r"Failed (?:password|publickey) for (?:invalid user )?(?P<user>\S+) "
    r"from (?P<ip>\d+\.\d+\.\d+\.\d+) port (?P<port>\d+)"
)
SSH_INVALID_USER_RE = re.compile(
    r"Invalid user (?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+) port (?P<port>\d+)"
)
ALLOWED_SSH_USERS = {"drmanzo", "javier"}


def _load_trusted_ips() -> set:
    ips = set()
    if not TRUSTED_IPS_PATH.exists():
        return ips
    for raw in TRUSTED_IPS_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        try:
            ipaddress.ip_address(line)
        except ValueError:
            continue
        ips.add(line)
    return ips


class JournalTailer:
    """Tails `journalctl -f` for a given unit, system or --user scope."""

    def __init__(self, unit: str, user_scope: bool = False):
        self.unit = unit
        self.user_scope = user_scope
        self.proc: Optional[asyncio.subprocess.Process] = None

    async def start(self) -> None:
        cmd = ["journalctl"]
        if self.user_scope:
            cmd.append("--user")
        cmd += ["-u", self.unit, "-f", "-n", "0", "-o", "cat"]
        self.proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
        )

    async def lines(self):
        if self.proc is None or self.proc.stdout is None:
            return
        while True:
            raw = await self.proc.stdout.readline()
            if not raw:
                return
            yield raw.decode("utf-8", errors="replace").rstrip("\n")


class InboundProbeDetector:
    """
    Owns the sliding-window state and rule evaluation. Pure detection
    logic — no I/O beyond the tail sources it's handed.
    """

    def __init__(self, pup: PupClient):
        self.pup = pup
        self.trusted_ips = _load_trusted_ips()
        self.auth_windows: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)
        self.request_windows: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)
        self.port_windows: Dict[str, Deque[Tuple[float, int]]] = defaultdict(deque)
        self.new_ip_last_alert: Dict[str, float] = {}

    def _prune(self, dq: Deque, now: float, window_sec: float, is_tuple: bool = False) -> None:
        while dq:
            ts = dq[0][0] if is_tuple else dq[0]
            if now - ts > window_sec:
                dq.popleft()
            else:
                break

    async def _respond(self, rule: dict, event: dict) -> None:
        blocked, note = block_ip(
            ip=event["ip"],
            rule_id=rule["id"],
            reason=rule.get("description", rule["id"]),
            allow_lan_block=rule.get("auto_block_lan", False),
        )
        incident_id = write_incident(event, rule, blocked, note)
        status = "BLOCKED" if blocked else "ALERT"
        notify_telegram(
            f"🐕 Hellhound [{status}]\n"
            f"Rule: {rule['id']}\n"
            f"IP: {event.get('ip', 'unknown')}\n"
            f"Surface: {event.get('surface', 'unknown')}\n"
            f"Incident: {incident_id}\n"
            f"Note: {note or 'n/a'}"
        )
        log.warning(
            "TRIGGER rule=%s ip=%s surface=%s blocked=%s incident=%s",
            rule["id"], event.get("ip"), event.get("surface"), blocked, incident_id,
        )
        try:
            await self.pup.observe(
                domain="security",
                event="rule_triggered",
                payload={
                    "rule_id": rule["id"],
                    "ip": event.get("ip"),
                    "surface": event.get("surface"),
                    "blocked": blocked,
                    "incident_id": incident_id,
                },
                severity="warning" if blocked else "error",
            )
        except Exception as exc:
            log.warning("pup.observe failed (non-fatal): %s", exc)

    async def handle_ssh_line(self, line: str) -> None:
        m = SSH_FAIL_RE.search(line)
        if m:
            ip, user = m.group("ip"), m.group("user")
            now = time.time()
            key = (ip, "ssh")
            dq = self.auth_windows[key]
            dq.append(now)
            self._prune(dq, now, RULES["rapid-auth-fail"]["window_sec"])
            event = {"ip": ip, "surface": "ssh", "event_type": "auth_fail",
                      "raw_lines": [line]}
            if len(dq) >= RULES["rapid-auth-fail"]["threshold"]:
                dq.clear()
                await self._respond(RULES["rapid-auth-fail"], event)
            if user not in ALLOWED_SSH_USERS:
                await self._respond(
                    RULES["ssh-new-user-attempt"],
                    {"ip": ip, "surface": "ssh", "event_type": "invalid_user",
                     "raw_lines": [line]},
                )
            return
        m = SSH_INVALID_USER_RE.search(line)
        if m and m.group("user") not in ALLOWED_SSH_USERS:
            await self._respond(
                RULES["ssh-new-user-attempt"],
                {"ip": m.group("ip"), "surface": "ssh", "event_type": "invalid_user",
                 "raw_lines": [line]},
            )

    async def handle_dashboard_line(self, line: str) -> None:
        m = DASHBOARD_LOG_RE.search(line)
        if not m:
            return
        ip = m.group("ip")
        now = time.time()

        # new-source-ip-forge: fires for any untrusted IP, LAN or not —
        # block_ip() itself enforces the never-auto-block-LAN rule via
        # auto_block_lan=False on this rule, so no branching needed here.
        # Deduped so a new device isn't re-alerted on every single request,
        # only once per window_sec per IP.
        if ip not in self.trusted_ips:
            rule = RULES["new-source-ip-forge"]
            last = self.new_ip_last_alert.get(ip, 0.0)
            if now - last > rule["window_sec"]:
                self.new_ip_last_alert[ip] = now
                await self._respond(rule, {
                    "ip": ip, "surface": "forge", "event_type": "request",
                    "raw_lines": [line],
                })

        # request-rate-spike
        rule = RULES["request-rate-spike"]
        key = (ip, "forge")
        dq = self.request_windows[key]
        dq.append(now)
        self._prune(dq, now, rule["window_sec"])
        if len(dq) >= rule["threshold"]:
            dq.clear()
            await self._respond(rule, {
                "ip": ip, "surface": "forge", "event_type": "request",
                "raw_lines": [line],
            })


async def run_pup() -> None:
    if not HH_TOKEN:
        log.error("HH_TOKEN not set — cannot authenticate with hellhound")
        sys.exit(1)

    async with PupClient(name=PUP_NAME, gate="network-security", token=HH_TOKEN) as pup:
        log.info("[%s] Hellhound connected", PUP_NAME)
        await pup.observe(
            domain="lifecycle", event="pup_start",
            payload={"pup": PUP_NAME, "gate": "network-security"},
        )

        detector = InboundProbeDetector(pup)
        ssh_tailer = JournalTailer(SSH_UNIT, user_scope=False)
        dash_tailer = JournalTailer(DASHBOARD_UNIT, user_scope=True)
        await ssh_tailer.start()
        await dash_tailer.start()

        async def watch_ssh():
            async for line in ssh_tailer.lines():
                await detector.handle_ssh_line(line)

        async def watch_dashboard():
            async for line in dash_tailer.lines():
                await detector.handle_dashboard_line(line)

        try:
            await asyncio.gather(
                watch_ssh(),
                watch_dashboard(),
                pup.wait_recall(),
            )
        except RecallReceived as r:
            await pup.observe(
                domain="lifecycle", event="pup_recall",
                payload={"reason": r.reason, "ref": r.ref},
                severity="warning",
            )
            log.info("[%s] Exiting cleanly after RECALL", PUP_NAME)
        finally:
            for tailer in (ssh_tailer, dash_tailer):
                if tailer.proc is not None and tailer.proc.returncode is None:
                    tailer.proc.terminate()


if __name__ == "__main__":
    asyncio.run(run_pup())
