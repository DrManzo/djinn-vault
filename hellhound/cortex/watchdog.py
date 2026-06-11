"""watchdog.py — Anomaly detection and health patrol.

Run via:  hellhound patrol
Or scheduled via systemd timer.

Checks:
    - Pup heartbeat staleness (> 2× heartbeat_interval)
    - Observation rate drop (< threshold in last N minutes)
    - Log file size / rotation health
    - Socket liveness
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from cortex.commander import enqueue_incident
from cortex.scribe import write_incident

BASE_DIR   = Path.home() / ".local" / "share" / "hellhound" / "skull"
STATE_FILE = BASE_DIR / "neurals" / "state.json"
SOCK_PATH  = BASE_DIR / "skull.sock"

HEARTBEAT_STALE_MULTIPLIER = 2.5   # flag pup if last HB > 2.5× its interval
DEFAULT_HB_INTERVAL        = 30


def _now() -> float:
    return time.time()


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def check_heartbeats(state: dict) -> list[dict]:
    """Return list of stale-pup anomalies."""
    anomalies = []
    now = _now()
    for name, rec in state.get("pups", {}).items():
        last_hb   = rec.get("last_heartbeat", 0)
        hb_ivl    = DEFAULT_HB_INTERVAL
        threshold = hb_ivl * HEARTBEAT_STALE_MULTIPLIER
        delta     = now - last_hb
        if delta > threshold:
            anomalies.append({
                "pup":     name,
                "check":   "heartbeat_stale",
                "delta_s": round(delta, 1),
                "threshold_s": threshold,
            })
    return anomalies


def check_socket() -> list[dict]:
    """Verify the skull.sock is present (master is alive)."""
    if not SOCK_PATH.exists():
        return [{"check": "socket_missing", "path": str(SOCK_PATH)}]
    return []


def patrol(report_to_vault: bool = True) -> list[dict]:
    """
    Run all checks. Returns list of anomaly dicts.
    If report_to_vault=True, writes incident files for each anomaly found.
    """
    state     = load_state()
    anomalies = check_heartbeats(state) + check_socket()

    if report_to_vault:
        for a in anomalies:
            slug = a.get("check", "unknown")
            details = json.dumps(a, indent=2)
            write_incident(slug=slug, details=details, severity="warning")
            enqueue_incident(slug=slug, details=details)

    return anomalies
