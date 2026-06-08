---
subject: Agent Task Queue
updated: 2026-06-07
---

# QUEUE.md — Djinn Task Queue

Active tasks pending assignment or completion.
Agents append to this file. Javier sets priorities.

## Format

    TASK-NNN | [lane] | [agent] | [priority] | description

## Active Queue

- [ ] TASK-001 | all-lanes | all | HIGH | API reduction sprint — in progress. Batch 1 (5 items) DONE. Batch 2 pending Salomon.

- [ ] TASK-005 | mobile | Javier | MEDIUM | Create iPhone Shortcut "Send to Djinn" — Share Sheet trigger, asks session name + agent, POSTs to Salomon Flask endpoint (port 8765) via Tailscale/local network.

- [ ] TASK-006 | desktop | Javier | MEDIUM | Add iMac Safari/Chrome bookmarklet — grabs page innerText, prompts session + agent, POSTs to Salomon Flask endpoint. One drag to bookmarks bar.

- [ ] TASK-007 | gemini-lane | Gemini | MEDIUM | Establish Gemini session-end GDrive write convention — at end of each session Gemini writes summary Doc to Typhons-Forge/gemini/reports/gemini-session-YYYY-MM-DD.md. Salomon rclone picks up on 2-min cycle.

- [ ] TASK-008 | infra | Salomon | LOW | Wire Firefox AI Chat Exporter output folder to ~/djinn-inbox/ drop target via SSH/SFTP mount or Tailscale file drop. Laptop-only, lowest priority since Flask endpoint covers all devices.

- [ ] TASK-009 | architecture | Claude | HIGH | Design bug hunter agent for Djinn — spec a proactive, automated vulnerability detection pipeline. Must include: (1) bandit static analysis on every commit, (2) pip-audit on cron, (3) secrets scanning pre-push, (4) regex error triage replacing LLM error log reads, (5) output to djinn/logs/bugs.md + Telegram alert. No LLM in detection path.

## TASK-001 Batch Tracker

### Batch 1 — DONE (shipped 2026-06-07, commit 5e79ab4)
- [x] Delta guard on git heartbeat — eliminates 576 empty pushes/day
- [x] Vault sync delta guard — eliminates 720 empty GitHub API calls/day
- [x] queue_watcher.py busy-loop → inotifywait — event-driven, zero CPU poll overhead
- [x] LLM() hoisted to module-level singleton in orchestrator.py
- [x] Early-return before classify() when intent is explicit (engrave/edit)

### Batch 2 — PENDING (send to Salomon)
- [ ] Add per-task max_tokens profiles in llm.py — replace global 2048 default with task-size map (status=128, design=1024, synthesis=2048)
- [ ] Set temperature=0.1 for deterministic tasks (status, COMMS entries, structured output) — currently 0.7 everywhere
- [ ] Add change-detection guard to comms-processor — only invoke opencode if COMMS.md mtime has changed since last run
- [ ] Add no-op short-circuit to djinn-daily — if PLAN.md has no carry-forward items and no new queue entries, skip model invocation entirely
- [ ] Swap djinn-design fallback from phi4:14b → qwen2.5-coder:7b for simple 2D parts — 4.7GB GPU-native vs 9.1GB CPU offload

### Batch 3 — QUEUED (after Batch 2)
- [ ] djinn-ctx-router: skip context assembly if no active user session
- [ ] ChromaDB re-index: enforce incremental mode as default, full only on --full flag
- [ ] Shared nomic-embed-text cache across Slipbox, Clerk, and vault indexer
- [ ] djinn-clerk: swap 1-hr timer for watchdog filesystem trigger
- [ ] printer-error-logger: gate LLM summary call on NEW error state only

### Batch 4 — QUEUED (structural)
- [ ] Weekly review: pre-summarize daily notes before LLM synthesis (cuts input ~60-70%)
- [ ] Claude session startup: build compressed session-resume variant (replaces 6-file sequential read)
- [ ] Groq fallback default: change from llama-3.3-70b-versatile to llama-3.1-8b-instant
- [ ] Timeout fast-fail: set 10-15s timeout for lightweight tasks vs global 120s
- [ ] COMMS.md compaction cron: archive entries older than N days to JSONL, truncate live file

## Completed

- [x] TASK-002 | infra | Salomon | 2026-06-07 | Flask inbox endpoint DEPLOYED — djinn-flask-inbox on 0.0.0.0:8765
- [x] TASK-003 | infra | Salomon | 2026-06-07 | inbox-watcher.service DEPLOYED
- [x] TASK-004 | infra | Salomon | 2026-06-07 | marcus-sync.py DEPLOYED at ~/.local/bin/
