"""
hound.py — shared state for the per-printer "hound" watch mode.

A hound is opt-in, manually toggled per printer from the dashboard. While
active it does two things the always-on djinn-print-safety daemons don't:
  1. Detects a print starting as fast as possible and switches to tight
     polling for the duration (vs. the baseline 60s poll).
  2. Captures webcam snapshots through the print, when that printer has an
     enabled Moonraker webcam (Iris does; Calliope/Nemesis currently don't —
     the hound just skips visual capture for those and still does the tight
     error/pause polling).

This module only owns the toggle state file the dashboard reads/writes.
The actual watching loop is djinn-hound (~/.local/bin, outside git),
running continuously as a systemd service, polling this file each cycle.

— Claude
"""

import json
import pathlib
import datetime

STATE_PATH = pathlib.Path.home() / ".config/forge/hound-state.json"


def _today() -> str:
    return datetime.date.today().isoformat()


def load_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text())
    except Exception:
        return {}


def save_state(data: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(data, indent=2))


def is_active(printer_id: str) -> bool:
    return bool(load_state().get(printer_id, {}).get("active"))


def set_active(printer_id: str, active: bool) -> dict:
    data = load_state()
    entry = data.setdefault(printer_id, {})
    entry["active"] = active
    entry[f"last_{'enabled' if active else 'disabled'}"] = datetime.datetime.utcnow().isoformat() + "Z"
    save_state(data)
    return entry


def status(printer_id: str) -> dict:
    """Full status for dashboard display: active flag + last watch summary,
    both written by djinn-hound as it runs."""
    return load_state().get(printer_id, {"active": False})
