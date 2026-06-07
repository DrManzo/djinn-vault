"""
djinn/tools/delta-guard/delta_guard.py
────────────────────────────────────────────────────────────────
Single public function: should_fire(current_state, state_key) -> bool

State is persisted to /tmp/djinn-state/{state_key}.json.
Returns True if current_state differs from the last known state,
and writes the new state before returning.
Returns False if current_state matches — caller should skip its action.

Every stateless timer in the fleet wraps its payload in this before acting.
"""

import json
import hashlib
import pathlib
from typing import Any

_STATE_DIR = pathlib.Path("/tmp/djinn-state")


def should_fire(current_state: dict, state_key: str) -> bool:
    """
    Return True if current_state has changed since last known state.

    Args:
        current_state: Dict representing observable state to compare.
        state_key:     Unique slot identifier — used as the filename.

    Side effects:
        Writes updated state to /tmp/djinn-state/{state_key}.json on True.

    Returns:
        True  → state changed; caller should act.
        False → state unchanged; caller should skip.
    """
    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_file = _STATE_DIR / f"{state_key}.json"
    current_hash = _hash(current_state)

    if state_file.exists():
        try:
            prior = json.loads(state_file.read_text())
            if prior.get("hash") == current_hash:
                return False
        except (json.JSONDecodeError, KeyError):
            pass

    state_file.write_text(json.dumps({
        "hash": current_hash,
        "state": current_state,
    }))
    return True


def _hash(obj: Any) -> str:
    serialized = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()
