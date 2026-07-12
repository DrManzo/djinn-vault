from __future__ import annotations

import logging
import os
from pathlib import Path

import requests

log = logging.getLogger("inbound-probe-notify")

# Same credential source as the real djinn-telegram-gateway's send() —
# NOT ~/.config/djinn/telegram.conf, which is a stale/different bot token
# (confirmed via live test: telegram.conf's token returns 401 Unauthorized).
OPS_TG_ENV = Path.home() / ".config/djinn/ops-tg.env"
DEFAULT_CHAT_ID = "7620067588"  # matches DJINN_TG_ALLOWED default across the vault


def _load_token() -> str:
    if OPS_TG_ENV.exists():
        for line in OPS_TG_ENV.read_text(encoding="utf-8").splitlines():
            if line.startswith("DJINN_TG_TOKEN="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("DJINN_TG_TOKEN", "")


def _load_chat_id() -> str:
    return os.environ.get("DJINN_TG_ALLOWED", DEFAULT_CHAT_ID).split(",")[0]


def send_hellhound_alert(msg: str) -> None:
    """
    Fire a Telegram alert. Non-fatal if Telegram is unreachable or
    unconfigured — a failed notification should never crash detection or
    blocking, which already happened before this function is called.
    Checked against a live send during integration: this must verify the
    HTTP response, not just the absence of a network exception — a bad
    token returns 200-reachable-but-401-rejected, which a bare try/except
    around requests.post silently swallows.
    """
    token = _load_token()
    chat_id = _load_chat_id()
    if not token or not chat_id:
        log.warning("ops-tg.env missing DJINN_TG_TOKEN — alert not sent: %s", msg)
        return
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg},
            timeout=10,
        )
        if resp.status_code != 200:
            log.warning(
                "Telegram alert rejected (status=%s): %s — original message: %s",
                resp.status_code, resp.text[:300], msg,
            )
    except requests.RequestException as exc:
        log.warning("Telegram alert failed (non-fatal): %s", exc)


def notify_telegram(msg: str) -> None:
    send_hellhound_alert(msg)
