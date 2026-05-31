---
title: Session Report — Queue Delegation System
agent: Claude
date: 2026-05-31
tags: [djinn, report, architecture, delegation]
related: [[QUEUE]] | [[build-log]] | [[decision-log]] | [[COMMS]]
---

# Session Report — Queue Delegation System

**Date:** 2026-05-31
**Agent:** Claude
**Session type:** Architecture + Build
**Trigger:** Javier asked for a way to reduce Claude's overuse — route execution to Salomon/Typhon while maintaining the same record-keeping discipline.

---

## Summary

Built a task delegation system so Claude can hand off execution to Salomon and Typhon via a structured queue file. Claude's role shrinks to "write the spec and drop it in QUEUE" — Salomon/Typhon do the work, write the reports, update the logs, and push the vault. The record-keeping standard (reports, build-log, COMMS, git push) is fully preserved.

---

## What Was Built or Changed

- **`djinn/communications/QUEUE.md`** — new task queue file. Claude and Javier write tasks here; runners pick them up. Append-only. Each task has: assigned_to, status, priority, trigger (auto/manual), context, and a bash commands block.
- **`djinn-queue-runner`** — Python script. Reads QUEUE.md, finds pending auto-tasks for the current machine, executes them in priority order, marks status in-place, calls `djinn-task-complete` when done, enriches the report with actual command output.
- **`djinn-task-complete`** — bash script. Writes a task report to `logs/reports/`, appends to `build-log.md`, appends to `COMMS.md`, commits and pushes the vault, sends Telegram notification.

---

## Technical Decisions

**QUEUE.md as Markdown not YAML/JSON — Why:** Agents and Javier both read COMMS.md as prose. A markdown queue file is readable in Obsidian, editable by any agent without a library, and parseable with simple regex. The overhead of a proper database or YAML schema is not justified.

**Username-based machine detection over hostname — Why:** The machine hostname on Salomon is "Djinn", not "salomon". Username (`drmanzo` = Salomon, `tf-tthq` = Typhon) is stable and unambiguous. Hostname substring match kept as secondary fallback.

**`trigger: auto` vs `trigger: manual` — Why:** Some tasks (deploys, config changes) should only run when Javier explicitly says go. Auto is for non-destructive, pre-approved work. Manual gives Javier a gate.

**djinn-task-complete separate from djinn-session-end — Why:** Session-end is per-conversation. Task-complete is per-task, potentially many per session. Different scope, different record format, different call site.

---

## Files Created or Modified

```
~/.local/bin/djinn-queue-runner          ← new: Python task runner
~/.local/bin/djinn-task-complete         ← new: bash record-keeper
~/Obsidian/djinn/communications/QUEUE.md ← new: task queue
```

---

## Tests & Validation

- Both scripts pass syntax check (`ast.parse`, `bash -n`)
- `djinn-queue-runner --list` runs against empty queue, correctly identifies machine as `salomon`
- `djinn-queue-runner --dry-run` mode available for previewing without executing

---

## Known Issues / Caveats

- Cron not yet installed — runner must be called manually or Javier needs to add it: `*/5 * * * * /home/drmanzo/.local/bin/djinn-queue-runner >> /tmp/djinn-queue.log 2>&1`
- Typhon does not yet have these scripts — needs `scp` deploy if Typhon tasks are needed
- AGENTS.md and CLAUDE.md not yet updated to document the new delegation pattern — Claude should use QUEUE.md going forward for execution handoffs

---

## What's Next

- [ ] Add cron entry for djinn-queue-runner on Salomon — @Javier
- [ ] Update AGENTS.md: add QUEUE.md to the report standard and session end protocol — @Claude (next session)
- [ ] Deploy scripts to Typhon if Typhon tasks are needed — @Salomon via SSH
- [ ] Queue up the pending shop deployment tasks (dashboard, customer_dm, shipping, inventory) — @Claude

---

*— Claude, 2026-05-31*
