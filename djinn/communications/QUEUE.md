---
title: Djinn Task Queue
updated: 2026-05-31
tags: [djinn, queue, delegation]
related: [[COMMS]] | [[PROTOCOL]] | [[build-log]]
---

# QUEUE — Djinn Task Queue

Claude (or Javier) writes tasks here. Salomon and Typhon pull and execute.

## Rules
- **Append only** — never delete entries. Mark `status: done` or `status: failed`.
- `trigger: auto` — runner picks up on next poll (cron every 5 min)
- `trigger: manual` — runner skips; Javier must send explicit signal
- Runner: `djinn-queue-runner` on Salomon and Typhon
- On completion: runner calls `djinn-task-complete TASK-NNN "summary"` automatically

## Task Format

```
## TASK-NNN
- assigned_to: salomon | typhon
- status: pending | in_progress | done | failed
- priority: critical | high | normal | low
- trigger: auto | manual
- created: YYYY-MM-DD by Claude|Javier
- context: one-line description of what and why

**Commands:**
```bash
command one
command two
```
```

---

<!-- TASKS BELOW — oldest at top, newest at bottom -->
