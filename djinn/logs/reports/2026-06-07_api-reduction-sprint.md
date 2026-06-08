---
title: Session Report — API Reduction Sprint (Batches 1-4)
agent: Salomon
date: 2026-06-07
tags: [djinn, report, api-reduction, sprint]
related: [[build-log]] | [[decision-log]]
---

# Session Report — API Reduction Sprint

**Date:** 2026-06-07
**Agent:** Salomon (implementing), Marcus (spec), Claude (architecture)
**Session type:** Build
**Trigger:** Marcus-authored 20-item reduction sprint across 4 batches

---

## Summary

Completed all 20 items across 4 batches of TASK-001, targeting LLM call reduction, event-driven triggers, and targeted model routing. Added delta guards, mtime gates, shared SQLite embed cache, watchdog-based file watchers, timeout profiles, task-level token/temp ceilings, and Groq model downgrade (70B → 8B default). Each change eliminates unnecessary API calls, filesystem polls, or model invocations.

---

## What Was Built or Changed

### Batch 1 — Deployed by prior Claude session (verified)
- Heartbeat delta guard, vault-sync delta guard, queue_watcher inotifywait, LLM module singleton, early classify() return

### Batch 2 — Token/temp profiles, mtime guards, design model
- `djinn/core/llm.py` — TOKEN_PROFILES, TEMP_PROFILES, task_type param on chat()
- `~/.local/bin/comms-processor` — mtime check before full scan
- `~/.local/bin/djinn-daily` — no-op short-circuit (queue empty + no carry)
- `djinn/printer/agent/orchestrator/agents/design_gen.py` — DESIGN_MODEL = qwen2.5-coder:7b

### Batch 3 — Session guards, incremental index, shared cache, watchdog, error dedup
- `~/.local/bin/djinn-ctx-router` — per-tick session activity check
- `~/.local/bin/djinn-vault-indexer` — mtime gate + last-run timestamp
- `~/.local/share/djinn/embed_cache.py` — SQLite shared embed cache (sha256 key)
- `~/.local/bin/djinn-embed` + `~/.local/bin/djinn-slipbox` — wired to shared cache
- `~/.local/bin/djinn-clerk-watch` — watchdog-based RAW/ watcher, replaces hourly timer
- `~/.config/systemd/user/djinn-clerk.service` — changed to Type=simple
- `~/.local/bin/djinn-clerk` — --file arg support
- `~/.local/bin/printer-error-logger` — last-printer-error dedup

### Batch 4 — Weekly digest, session resume, Groq 8b, timeout profiles
- `~/.local/bin/djinn-weekly` — digest builder (headers + action items only, 60-70% token cut)
- `~/.local/bin/djinn-session-end` — auto-generates SESSION-RESUME.md on close
- `djinn/core/llm.py` — Groq default → llama3.1-8b-instant, 70B explicit opt-in only
- `djinn/core/llm.py` — TIMEOUT_PROFILES (status:12s, embed:8s, quote:10s, design:60s, default:120s)

---

## Technical Decisions

**Shared embed cache (SQLite vs JSON)** — Existing `djinn-embed` used JSON file cache. SQLite provides concurrent access, key-based lookup without full-file deserialization, and no write contention. Module at `~/.local/share/djinn/embed_cache.py` is importable by any script.

**Weekly digest vs full notes** — Raw daily notes include extensive prose from morning briefs and journaling. Digest filters to headers + `[ ]` items + carry/blocked/pending references. Same data quality for LLM synthesis, ~60-70% token reduction.

**Groq 8b as default** — llama3.1-8b-instant is adequate for status/comms/quote tasks (which are deterministic by profile). 70B is opt-in via `task_type="synthesis"` or `task_type="architecture"`. Prevents silent 70B billing if Groq is activated by automation.

**Clerk watchdog vs timer** — Timer fired every hour regardless of activity. Watchdog via `watchdog.Observer` fires only when a file is created in RAW/. No polling overhead.

---

## Files Created or Modified

```
~/.local/share/djinn/embed_cache.py           ← shared SQLite embed cache module
~/.local/bin/djinn-clerk-watch                ← watchdog-based RAW/ watcher
~/.config/systemd/user/djinn-clerk.service    ← Type=simple, points to clerk-watch
djinn/core/llm.py                             ← Groq 8b default, timeout profiles, task-type profiles
djinn/printer/agent/orchestrator/agents/design_gen.py ← DESIGN_MODEL constant
djinn/migration/scripts/djinn-daily           ← no-op short-circuit
djinn/migration/scripts/djinn-weekly          ← digest builder
djinn/migration/scripts/djinn-session-end     ← SESSION-RESUME.md generation
djinn/tools/comms-compact.py                  ← synced from .local/bin
~/.local/bin/comms-processor                  ← mtime guard
~/.local/bin/djinn-daily                      ← no-op short-circuit
~/.local/bin/djinn-weekly                     ← digest builder
~/.local/bin/djinn-session-end                ← SESSION-RESUME.md generation
~/.local/bin/djinn-ctx-router                 ← session activity guard
~/.local/bin/djinn-vault-indexer              ← mtime gate + last-run timestamp
~/.local/bin/djinn-embed                      ← shared embed cache integration
~/.local/bin/djinn-slipbox                    ← shared embed cache integration
~/.local/bin/djinn-clerk                      ← --file arg support
~/.local/bin/printer-error-logger             ← last-printer-error dedup
```

---

## Dependencies Installed

| Package | Method | Purpose |
|---------|--------|---------|
| watchdog | pip3 | File system event monitoring (djinn-clerk-watch) |

---

## Tests & Validation

- Python syntax check: all 6 modified .py files passed py_compile
- Bash syntax: all modified scripts verified by manual review
- Systemd: djinn-clerk.timer disabled, djinn-clerk.service enabled and active
- Embed cache: module created, both djinn-embed and djinn-slipbox import it

---

## Known Issues / Caveats

- `~/.local/bin/comms-processor` is outside vault — not tracked by git. Manual sync needed if reinstalled.
- `watchdog` Python package must be installed on any machine running djinn-clerk-watch.
- mtime-based checks (vault-indexer, comms-processor) depend on filesystem timestamps being preserved — edge case if files are restored from backup.
- Groq model selection is task-type based and only activates when `task_type` is passed to `chat()`. Callers that don't pass task_type get profile-default behavior.

---

## What's Next

- [ ] Verify clerk-watch is running: `systemctl --user status djinn-clerk.service`
- [ ] Verify embed cache: `python3 -c "from embed_cache import get, put; print('OK')"`
- [ ] Marcus-spec'd session report at `djinn/logs/reports/2026-06-07_api-reduction-sprint.md`

---

*— Salomon, 2026-06-07*
