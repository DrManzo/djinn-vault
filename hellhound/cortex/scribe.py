"""scribe.py — Write structured observations to the Obsidian vault.

Responsibilities:
    - Append to per-gate activity logs  (vault/gates/<gate>.md)
    - Update pups.md summary
    - Write incident files on critical severity
"""

import time
from datetime import datetime, timezone
from pathlib import Path

VAULT_BASE = Path.home() / "Obsidian" / "djinn" / "hellhound"


def _ts_human(ts: float | None = None) -> str:
    t = ts or time.time()
    return datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def write_gate_log(obs: dict) -> None:
    """
    Append a formatted line to the gate-specific activity log.
    gates/<gate>.md
    """
    gate = obs.get("pup", "unknown")
    gate_dir = VAULT_BASE / "gates"
    gate_dir.mkdir(parents=True, exist_ok=True)
    gate_file = gate_dir / f"{gate}.md"

    if not gate_file.exists():
        gate_file.write_text(f"# {gate.capitalize()} Gate Log\n\n")

    ts_str   = _ts_human(obs.get("ts"))
    event    = obs.get("event", "?")
    domain   = obs.get("domain", "?")
    severity = obs.get("severity", "info")
    payload  = obs.get("payload", {})

    icon = {"info": "ℹ️", "warning": "⚠️", "error": "🔴", "critical": "🚨"}.get(
        severity, "ℹ️"
    )

    line = f"- `{ts_str}` {icon} `{domain}/{event}`"
    if payload:
        import json
        line += f" — `{json.dumps(payload, separators=(',', ':'))}`"
    line += "\n"

    with gate_file.open("a") as f:
        f.write(line)


def write_incident(
    slug:     str,
    details:  str,
    severity: str = "error",
    ref:      str = "",
) -> Path:
    """
    Create an incident file in vault/incidents/.
    Returns the path to the created file.
    """
    incidents_dir = VAULT_BASE / "incidents"
    incidents_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ifile = incidents_dir / f"{today}_{slug}.md"
    ifile.write_text(
        f"# Incident: {slug}\n"
        f"**Severity:** {severity}\n"
        f"**Detected:** {_ts_human()}\n"
        f"**Ref:** {ref}\n\n"
        f"{details}\n"
    )
    return ifile


def update_pups_summary(pups: dict) -> None:
    """
    Regenerate vault/pups.md from the current registry snapshot.
    """
    lines = ["# Active Pups\n", f"_Updated: {_ts_human()}_\n\n", "| Pup | Gate | Status | Uptime | Observations |\n", "|-----|------|--------|--------|--------------|\n"]
    for name, rec in pups.items():
        uptime_s = rec.get("uptime", 0)
        uptime   = f"{int(uptime_s // 3600)}h {int((uptime_s % 3600) // 60)}m"
        lines.append(
            f"| {name} | {rec.get('gate','?')} | "
            f"{rec.get('status','?')} | {uptime} | "
            f"{rec.get('observations_sent', 0)} |\n"
        )
    (VAULT_BASE / "pups.md").write_text("".join(lines))
