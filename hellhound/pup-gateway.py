#!/usr/bin/env python3
"""
pup-gateway.py — Discord Gateway Pup
Wraps the existing djinn-discord-gateway logic and reports every
routed message as a structured observation to hellhound.

Environment variables expected:
    PUP_NAME       — injected by systemd pup@.service (default: gateway)
    DISCORD_TOKEN  — bot token
    HH_TOKEN       — pre-shared hellhound auth token

Install:
    cp pup-gateway.py ~/.local/share/hellhound/pup-gateway.py
    systemctl --user start pup@gateway
"""

import asyncio
import logging
import os
import sys

# ---------------------------------------------------------------------------
# Try to import existing djinn discord gateway.
# Adjust this import path to match your actual project layout.
# ---------------------------------------------------------------------------
try:
    # If djinn package is on PYTHONPATH or installed as a package:
    from djinn.gateway import DiscordGateway  # type: ignore
except ImportError:
    DiscordGateway = None   # fallback: run in stub mode for testing

from pup import PupClient, RecallReceived

log = logging.getLogger("pup-gateway")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

PUP_NAME      = os.environ.get("PUP_NAME", "gateway")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")
HH_TOKEN      = os.environ.get("HH_TOKEN", "")


# ---------------------------------------------------------------------------
# Stub gateway for testing without a real Discord token
# ---------------------------------------------------------------------------
class StubGateway:
    """Emits a fake observation every 10 seconds. Remove when integrating real gateway."""

    def __init__(self, on_message):
        self.on_message = on_message

    async def run(self):
        import time
        log.warning("[stub] Running StubGateway — no real Discord connection")
        counter = 0
        while True:
            await asyncio.sleep(10)
            counter += 1
            await self.on_message({
                "author":  "stub-user",
                "channel": "#stub-channel",
                "content": f"stub message {counter}",
                "routed_to": "djinn-core",
            })


# ---------------------------------------------------------------------------
# Main pup logic
# ---------------------------------------------------------------------------
async def run_pup():
    if not HH_TOKEN:
        log.error("HH_TOKEN not set — cannot authenticate with hellhound")
        sys.exit(1)

    async with PupClient(name=PUP_NAME, gate="discord-dm", token=HH_TOKEN) as pup:
        log.info("[%s] Hellhound connected", PUP_NAME)

        # Announce startup
        await pup.observe(
            domain="lifecycle",
            event="pup_start",
            payload={"pup": PUP_NAME, "gate": "discord-dm"},
            severity="info",
        )

        # ------------------------------------------------------------------
        # Message handler — called by gateway on every received message
        # ------------------------------------------------------------------
        async def on_message(msg: dict):
            await pup.observe(
                domain="comms",
                event="msg_routed",
                payload={
                    "author":    msg.get("author"),
                    "channel":   msg.get("channel"),
                    "routed_to": msg.get("routed_to"),
                    # Never log raw message content — only metadata
                },
                severity="info",
            )

        # ------------------------------------------------------------------
        # Choose real or stub gateway
        # ------------------------------------------------------------------
        if DiscordGateway is not None and DISCORD_TOKEN:
            gateway = DiscordGateway(token=DISCORD_TOKEN, on_message=on_message)
        else:
            gateway = StubGateway(on_message=on_message)

        # Run gateway + wait_recall concurrently
        try:
            await asyncio.gather(
                gateway.run(),
                pup.wait_recall(),
            )
        except RecallReceived as r:
            await pup.observe(
                domain="lifecycle",
                event="pup_recall",
                payload={"reason": r.reason, "ref": r.ref},
                severity="warning",
            )
            log.info("[%s] Exiting cleanly after RECALL", PUP_NAME)


if __name__ == "__main__":
    asyncio.run(run_pup())
