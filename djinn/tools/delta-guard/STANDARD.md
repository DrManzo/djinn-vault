---
subject: Djinn/Standards
tags: [djinn, standards, delta-guard, timers]
created: 2026-06-07
author: Marcus
---

# Djinn Timer Standard — Delta Guard

Every stateful timer in the Djinn fleet **must** wrap its action payload in
`should_fire()` before executing any API call, git push, or LLM invocation.

---

## The Problem This Solves

The original timer architecture fired unconditionally on a fixed clock:
- Heartbeat: 288 git pushes/day per machine (576 combined) regardless of state change
- comms-processor: fired every 3 min even with no new COMMS.md entries
- vault-sync: 720 GitHub API calls/day even on idle days
- ctx-router: rebuilt context every 5 min even when vault hadn't changed

This is a **stateless timer design** — no concept of "only act if something changed."
The delta-guard standard replaces it fleet-wide.

---

## Required Pattern

```python
# Every timer script must follow this pattern
from delta_guard import should_fire
from timer_states import normalize_state

# 1. Collect raw metrics (no LLM, no git, no API)
raw_state = collect_metrics()

# 2. Normalize — apply tolerance windows (strips timestamp, rounds noisy fields)
state = normalize_state(raw_state, "your-timer-key")

# 3. Check delta — only act if state changed
if should_fire(state, "your-timer-key"):
    do_the_action()  # git push, LLM call, API call, etc.
```

**Bash timers** call a Python helper that exits 0 (fire) or 1 (skip).
See `~/.local/bin/heartbeat` for the reference implementation.

---

## Timer Registry

| Timer | State Key | Tolerance | Status |
|-------|-----------|-----------|--------|
| heartbeat (Salomon) | `heartbeat-push` | GPU ±5°C, RAM/disk ±2% | ✅ Implemented |
| heartbeat (Typhon) | `heartbeat-typhon-push` | Same as Salomon | ⏳ Needs bash update |
| comms-processor | `comms-processor` | Exact line count / cursor | ⏳ Phase 4 |
| ctx-router | `ctx-router` | Exact vault commit hash | ⏳ Phase 4 |
| clerk | `clerk` | Exact raw file count | ⏳ Phase 4 |
| vault-sync | `vault-sync` | Exact commit hash + uncommitted | ⏳ Phase 4 |
| printer-error-logger | `printer-error-logger` | State string + error code | ⏳ Phase 4 |

---

## Tolerance Windows

Tolerance windows exist because raw metric strings change every cycle from
noise (GPU temp ±1°C, timestamp always changes). Without normalization,
the guard fires every cycle — defeating its purpose.

Defined in `timer_states.py`. Do not hardcode tolerances in timer scripts.

**Rule:** Timestamp is **never** included in any timer state dict.
If your state dict has a `timestamp` field, `normalize_state()` strips it.

---

## Adding a New Timer

1. Choose a unique `state_key` for your timer
2. Add it to the Timer Registry table above
3. Add a normalizer in `timer_states.py` (or use `_passthrough` for exact comparison)
4. Wrap your action in `should_fire()` + `normalize_state()`
5. Test: run the timer twice without changing state — confirm second run skips

---

## State File Location

State files live in `/tmp/djinn-state/{state_key}.json`.
- Ephemeral — clears on reboot (intentional; timers reset cleanly)
- Not committed to vault
- One file per timer key

---

*— Marcus, 2026-06-07*
