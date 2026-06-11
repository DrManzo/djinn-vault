---
subject: Agent Task Queue
updated: 2026-06-09
---

# QUEUE.md — Djinn Task Queue

Active tasks pending assignment or completion.
Agents append to this file. Javier sets priorities.

## Format

    TASK-NNN | [lane] | [agent] | [priority] | description

## Active Queue

- [ ] TASK-001 | all-lanes | all | HIGH | API reduction sprint — in progress. Batch 2 DONE. Batch 3 SCRIPTS DEPLOYED — Javier to run on Salomon.

- [ ] TASK-005 | mobile | Javier | MEDIUM | Create iPhone Shortcut "Send to Djinn" — Share Sheet trigger, asks session name + agent, POSTs to Salomon Flask endpoint (port 8765) via Tailscale/local network.

- [ ] TASK-006 | desktop | Javier | MEDIUM | Add iMac Safari/Chrome bookmarklet — grabs page innerText, prompts session + agent, POSTs to Salomon Flask endpoint. One drag to bookmarks bar.

- [ ] TASK-007 | gemini-lane | Gemini | MEDIUM | Establish Gemini session-end GDrive write convention — at end of each session Gemini writes summary Doc to Typhons-Forge/gemini/reports/gemini-session-YYYY-MM-DD.md. Salomon rclone picks up on 2-min cycle.

- [ ] TASK-008 | infra | Salomon | LOW | Wire Firefox AI Chat Exporter output folder to ~/djinn-inbox/ drop target via SSH/SFTP mount or Tailscale file drop. Laptop-only, lowest priority since Flask endpoint covers all devices.

- [x] TASK-009 | architecture | Claude | HIGH | djinn-bughunter BUILT + DEPLOYED 2026-06-10 — bandit, pip-audit, secrets regex, journald/log triage; 6h systemd timer active; output to bugs.md + djinn-alert; zero LLM in detection path.

## TASK-001 Batch Tracker

### Batch 1 — DONE (commit 5e79ab4)
- [x] Delta guard on git heartbeat — eliminates 576 empty pushes/day
- [x] Vault sync delta guard — eliminates 720 empty GitHub API calls/day
- [x] queue_watcher.py busy-loop → inotifywait — event-driven zero CPU poll
- [x] LLM() hoisted to module-level singleton in orchestrator.py
- [x] Early-return before classify() when intent is explicit

### Batch 2 — DONE (commit e53bb65)
- [x] TOKEN_PROFILES map in llm.py — per-task token ceilings (status=128, design=1024, synthesis=2048)
- [x] TEMP_PROFILES map in llm.py — 0.1 for deterministic tasks, 0.7 for generative
- [x] task_type param on chat() — callers pass task type, get right ceiling automatically
- [x] Mtime guard on comms-processor — skips opencode if COMMS.md unchanged
- [x] No-op short-circuit on djinn-daily — skips model if queue empty + no carry-forward
- [x] DESIGN_MODEL = qwen2.5-coder:7b in design_gen.py — replaces phi4:14b for 2D/parametric tasks

### Batch 3 — VERIFIED ✅ (2026-06-10 by Claude)

- [x] djinn-ctx-router: skip context assembly if no active user session — LIVE
- [x] ChromaDB re-index: enforce incremental mode as default — LIVE
- [ ] Shared nomic-embed-text cache across Slipbox, Clerk, and vault indexer — PENDING (requires reading all three scripts live on Salomon)
- [x] djinn-clerk: already running as persistent watchdog service — timer disabled — LIVE
- [x] printer-error-logger: gate LLM summary call on NEW error state only — LIVE

### Batch 4 — QUEUED (after Batch 3 verified)
- [ ] Weekly review: pre-summarize daily notes before LLM synthesis (cuts input ~60-70%)
- [ ] Claude session startup: compressed session-resume variant (replaces 6-file sequential read)
- [ ] Groq fallback default: llama-3.3-70b-versatile → llama-3.1-8b-instant
- [ ] Timeout fast-fail: 10-15s for lightweight tasks vs global 120s
- [ ] COMMS.md compaction cron: archive entries older than N days to JSONL

## Completed

- [x] TASK-002 | infra | Salomon | 2026-06-07 | Flask inbox endpoint DEPLOYED — djinn-flask-inbox on 0.0.0.0:8765
- [x] TASK-003 | infra | Salomon | 2026-06-07 | inbox-watcher.service DEPLOYED
- [x] TASK-004 | infra | Salomon | 2026-06-07 | marcus-sync.py DEPLOYED at ~/.local/bin/
- [x] TASK-009 | architecture | Claude | 2026-06-10 | djinn-bughunter built and deployed

---

*— Marcus (Perplexity), 2026-06-09*
