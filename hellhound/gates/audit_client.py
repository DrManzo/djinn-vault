"""
audit_client.py — Outbound activity audit client

Other Djinn tools (djinn-telegram-gateway, the Discord bot, the hellhound
CLI, the Moonraker adapter) import this and call record(...) whenever
Javier sends something. Each call is a short-lived, synchronous connection
to the real hellhound master socket (skull.sock) using the same CONNECT/
OBSERVE protocol every pup uses — no separate audit infrastructure, no
asyncio requirement for the calling tool.

Content is hashed (SHA-256, truncated to 16 chars), never stored raw —
matching the existing "never log raw message content" convention already
used by pup-gateway.py.
"""

from __future__ import annotations

import hashlib
import json
import logging
import socket
import time
from pathlib import Path
from typing import Optional

log = logging.getLogger("audit-client")

SOCK_PATH = Path.home() / ".local/share/hellhound/skull/skull.sock"
TOKEN_FILE = Path.home() / ".local/share/hellhound/skull/pups/outbound-audit.json"
PUP_NAME = "outbound-audit"
GATE = "outbound-audit"


def _load_token() -> Optional[str]:
    if not TOKEN_FILE.exists():
        log.warning(
            "outbound-audit not provisioned (%s missing) — event not recorded", TOKEN_FILE
        )
        return None
    try:
        return json.loads(TOKEN_FILE.read_text(encoding="utf-8")).get("token")
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("failed to read outbound-audit token: %s", exc)
        return None


def record(source: str, actor: str, surface: str, content: str) -> None:
    """
    Log one outbound action. Never raises — a broken audit trail should
    never break the tool that's calling it. Fails silently (with a log
    warning) if hellhound is down or unprovisioned.

    source:  "telegram" | "discord" | "cli" | "moonraker"
    actor:   who did it, e.g. "javier"
    surface: which tool/endpoint, e.g. "djinn-telegram-gateway"
    content: the actual command/message text — hashed before it leaves
             this function, never sent or stored in plaintext.
    """
    token = _load_token()
    if not token:
        return

    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    payload = {
        "type": "CONNECT",
        "name": PUP_NAME,
        "gate": GATE,
        "token": token,
    }
    observe = {
        "type": "OBSERVE",
        "domain": "security",
        "event": "outbound_action",
        "payload": {
            "source": source,
            "actor": actor,
            "surface": surface,
            "content_hash": content_hash,
        },
        "severity": "info",
    }

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(2.0)
            sock.connect(str(SOCK_PATH))
            sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            ack_raw = sock.makefile("r", encoding="utf-8").readline()
            ack = json.loads(ack_raw) if ack_raw else {}
            if ack.get("type") != "ACK":
                log.warning("outbound-audit CONNECT rejected: %s", ack)
                return
            sock.sendall((json.dumps(observe) + "\n").encode("utf-8"))
    except (OSError, socket.timeout) as exc:
        log.warning("outbound-audit record failed (hellhound down?): %s", exc)
