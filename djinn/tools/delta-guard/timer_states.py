"""
djinn/tools/delta-guard/timer_states.py
────────────────────────────────────────────────────────────────
Per-timer meaningful field definitions with tolerance windows.

PURPOSE
  delta_guard.should_fire() does exact hash comparison by default.
  Raw equality on nvidia-smi output means a 1C GPU temp fluctuation
  triggers a push every cycle — defeating the purpose of the guard.

  This module provides normalize_state(state, timer_key) which applies
  tolerance rounding before the state dict is passed to should_fire().
  Callers pass their raw collected state through normalize_state first.

USAGE
  from delta_guard import should_fire
  from timer_states import normalize_state

  raw_state = collect_metrics()           # raw nvidia-smi, df, free output
  state = normalize_state(raw_state, "heartbeat-push")
  if should_fire(state, "heartbeat-push"):
      do_git_push()

TOLERANCE WINDOWS
  heartbeat-push:
    gpu_temp_c    → round to nearest 5°C
    gpu_util_pct  → round to nearest 10%
    vram_used_mb  → round to nearest 512MB
    ram_used_pct  → round to nearest 2%
    disk_used_pct → round to nearest 2%
    model_count   → exact (0 or N — meaningful change)

  comms-processor:
    comms_line_count → exact (any new line = act)
    comms_cursor     → exact (cursor position change = act)

  ctx-router:
    vault_commit_hash → exact (any vault change = rebuild context)

  clerk:
    raw_file_count → exact (new file = process)

  vault-sync:
    vault_commit_hash → exact (new commit = push)
    uncommitted_files → exact (any pending = push)

  printer-error-logger:
    printer_state     → exact (state string change only)
    error_code        → exact (new error code = alert)
    # timestamp is NEVER included in any timer state
"""

import math
from typing import Any


def normalize_state(state: dict, timer_key: str) -> dict:
    """
    Apply tolerance rounding to raw state before delta comparison.

    Args:
        state:     Raw state dict from the timer's metric collection.
        timer_key: Timer identifier matching the keys in TOLERANCES.

    Returns:
        New dict with tolerance-rounded values. Unknown keys pass through.
        Unknown timer_key passes state through unchanged (safe fallback).
    """
    handlers = {
        "heartbeat-push":          _normalize_heartbeat,
        "heartbeat-typhon-push":   _normalize_heartbeat,
        "comms-processor":         _passthrough,
        "ctx-router":              _passthrough,
        "clerk":                   _passthrough,
        "vault-sync":              _passthrough,
        "printer-error-logger":    _normalize_printer_error,
    }
    handler = handlers.get(timer_key, _passthrough)
    return handler(state)


# ─── Per-timer normalizers ────────────────────────────────────────────────────

def _normalize_heartbeat(state: dict) -> dict:
    """Round GPU/RAM/disk metrics to avoid noise-triggered pushes."""
    out = {}
    for k, v in state.items():
        if k == "gpu_temp_c" and v not in (None, "N/A"):
            out[k] = _round_to(float(v), 5)       # nearest 5°C
        elif k == "gpu_util_pct" and v not in (None, "N/A"):
            out[k] = _round_to(float(v), 10)      # nearest 10%
        elif k == "vram_used_mb" and v not in (None, "N/A"):
            out[k] = _round_to(float(v), 512)     # nearest 512MB
        elif k == "ram_used_pct" and v not in (None, "N/A"):
            out[k] = _round_to(float(v), 2)       # nearest 2%
        elif k == "disk_used_pct" and v not in (None, "N/A"):
            out[k] = _round_to(float(v), 2)       # nearest 2%
        elif k == "timestamp":
            pass                                   # timestamp NEVER included
        else:
            out[k] = v
    return out


def _normalize_printer_error(state: dict) -> dict:
    """Strip timestamp, keep printer_state and error_code only."""
    allowed = {"printer_state", "error_code", "model_count"}
    return {k: v for k, v in state.items() if k in allowed}


def _passthrough(state: dict) -> dict:
    """No normalization — exact comparison. Strip timestamp."""
    return {k: v for k, v in state.items() if k != "timestamp"}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _round_to(value: float, nearest: float) -> float:
    """Round value to the nearest multiple of 'nearest'."""
    return round(value / nearest) * nearest
