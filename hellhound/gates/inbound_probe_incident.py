from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

# Incidents are meaningful, low-frequency, human-review-worthy — they live
# in the vault (git-backed, visible in Obsidian), matching hellhound.py's own
# pattern of writing timeline/ to the vault while keeping high-frequency raw
# data (SQLite, JSONL) in the local runtime dir.
INCIDENT_DIR = Path.home() / "Obsidian" / "hellhound" / "incidents"


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-").lower()


def _yaml_value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return json.dumps(v)
    return str(v)


def write_incident(event: dict, rule: dict, blocked: bool, block_note: str = "") -> str:
    INCIDENT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    incident_id = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}_{_slug(rule['id'])}"
    path = INCIDENT_DIR / f"{incident_id}.md"
    raw_lines = event.get("raw_lines", [])
    if not isinstance(raw_lines, list):
        raw_lines = [str(raw_lines)]

    frontmatter = {
        "ts": now.isoformat(),
        "rule_id": rule["id"],
        "ip": event.get("ip"),
        "surface": event.get("surface"),
        "blocked": blocked,
        "notified": True,
    }

    body = [
        "---",
        *(f"{k}: {_yaml_value(v)}" for k, v in frontmatter.items()),
        "---",
        "",
        f"# Incident: {rule['id']} — {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"**IP:** {event.get('ip', 'unknown')}  ",
        f"**Surface:** {event.get('surface', 'unknown')}  ",
        f"**Trigger:** {rule.get('description', rule['id'])}  ",
        f"**Action:** {'ufw deny inserted' if blocked else 'alert only'}  ",
        f"**Block note:** {block_note or 'n/a'}  ",
        "",
        "## Event",
        "",
        "```json",
        json.dumps(event, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Raw Events",
        "",
        "```text",
        *[str(line) for line in raw_lines],
        "```",
        "",
        "## Notes",
        "",
        "AI summary may be appended later by a separate report step. Detection, blocking, and notification are deterministic only.",
        "",
    ]
    path.write_text("\n".join(body), encoding="utf-8")
    return incident_id
