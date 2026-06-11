"""alerter.py — Route alerts through the appropriate gate.

Currently supports: vault incident file creation.
Future: Discord DM, Telegram push, ntfy.sh webhook.
"""

import logging
from pathlib import Path

from cortex.scribe import write_incident
from cortex.commander import enqueue_incident

log = logging.getLogger("alerter")


def alert(
    slug:     str,
    details:  str,
    severity: str = "error",
    ref:      str = "",
    channels: list[str] | None = None,
) -> None:
    """
    Route an alert to one or more channels.

    channels: ['vault', 'queue']  (default: both)
    Future channels: 'discord', 'telegram', 'ntfy'
    """
    channels = channels or ["vault", "queue"]

    if "vault" in channels:
        path = write_incident(slug=slug, details=details, severity=severity, ref=ref)
        log.info("Alert written to vault: %s", path)

    if "queue" in channels:
        enqueue_incident(slug=slug, details=details, ref=ref)
        log.info("Alert enqueued to QUEUE.md: %s", slug)
