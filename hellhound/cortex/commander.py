"""commander.py — Write commands to QUEUE.md

Hellhound's cortex uses this module to inject task entries into the
Djinn QUEUE.md so agents can pick them up on the next cycle.
"""

import time
from datetime import datetime, timezone
from pathlib import Path

# Default QUEUE.md path — override via DJINN_QUEUE env var if needed
import os
QUEUE_PATH = Path(
    os.environ.get(
        "DJINN_QUEUE",
        str(Path.home() / "Obsidian" / "djinn" / "djinn" / "QUEUE.md"),
    )
)


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def enqueue(
    title:    str,
    body:     str       = "",
    priority: str       = "normal",   # low | normal | high | critical
    tags:     list[str] | None = None,
    source:   str       = "hellhound",
) -> None:
    """
    Append a command entry to QUEUE.md.

    Format:
        ## [<ts>] <title>  <!-- source:<source> priority:<priority> -->
        <body>
        Tags: <tags>
        ---
    """
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)

    tag_str = ", ".join(tags) if tags else ""
    ts = _ts()

    block = (
        f"\n## [{ts}] {title}  "
        f"<!-- source:{source} priority:{priority} -->\n"
    )
    if body:
        block += f"{body}\n"
    if tag_str:
        block += f"Tags: {tag_str}\n"
    block += "---\n"

    with QUEUE_PATH.open("a") as f:
        f.write(block)


def enqueue_incident(
    slug:    str,
    details: str,
    ref:     str = "",
) -> None:
    """
    Shortcut: enqueue a high-priority incident command.
    Also writes to the vault incidents directory.
    """
    from pathlib import Path as P

    vault_incidents = P.home() / "Obsidian" / "djinn" / "hellhound" / "incidents"
    vault_incidents.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ifile = vault_incidents / f"{today}_{slug}.md"

    ifile.write_text(
        f"# Incident: {slug}\n"
        f"**Detected:** {_ts()}\n"
        f"**Ref:** {ref}\n\n"
        f"{details}\n"
    )

    enqueue(
        title=f"INCIDENT: {slug}",
        body=details,
        priority="high",
        tags=["incident", slug],
        source="hellhound.watchdog",
    )
