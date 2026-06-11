#!/usr/bin/env python3
"""
pup-template.py — Copy this file to create a new pup.

Steps:
    1. hellhound pup new <name>   →  creates pup-<name>.py from this template
    2. Set the GATE variable below
    3. Add your gate-specific logic inside run_gate()
    4. systemctl --user start pup@<name>
"""

import asyncio
import logging
import os
import sys

from pup import PupClient, RecallReceived

log = logging.getLogger("pup-template")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

PUP_NAME = os.environ.get("PUP_NAME", "template")
HH_TOKEN = os.environ.get("HH_TOKEN", "")
GATE     = "change-me"   # ← set this to your gate type


async def run_gate(pup: PupClient):
    """
    Your gate-specific logic goes here.
    Call await pup.observe(...) whenever something interesting happens.
    This coroutine runs until cancelled (by RECALL or shutdown).
    """
    while True:
        await asyncio.sleep(60)
        await pup.observe(
            domain="example",
            event="tick",
            payload={"note": "replace with real gate logic"},
        )


async def main():
    if not HH_TOKEN:
        log.error("HH_TOKEN not set")
        sys.exit(1)

    async with PupClient(name=PUP_NAME, gate=GATE, token=HH_TOKEN) as pup:
        await pup.observe(
            domain="lifecycle", event="pup_start",
            payload={"pup": PUP_NAME, "gate": GATE},
        )
        try:
            await asyncio.gather(
                run_gate(pup),
                pup.wait_recall(),
            )
        except RecallReceived as r:
            await pup.observe(
                domain="lifecycle", event="pup_recall",
                payload={"reason": r.reason, "ref": r.ref},
                severity="warning",
            )
            log.info("[%s] Clean exit after RECALL", PUP_NAME)


if __name__ == "__main__":
    asyncio.run(main())
