"""effector/scribe.py — Thin re-export for backwards compatibility.
The real implementation lives in cortex/scribe.py.
Import from cortex.scribe in all new code.
"""

from cortex.scribe import write_gate_log, write_incident, update_pups_summary  # noqa: F401
