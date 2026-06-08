---
title: TASK-001 — API Reduction Sprint
agent: marcus
date: 2026-06-07
tags: [research, api-reduction, sprint, task-001]
status: delivered
---

# TASK-001 — API Reduction Sprint
## Marcus Session Report

## Summary

Full 20-item API reduction sprint completed across 4 batches in a single session (2026-06-07). All items researched, specced, and implemented by Salomon. Final commit 5df6044 — 11 Python files, 7 bash scripts, 2 systemd service updates, 1 shared SQLite cache module, ~1709 lines added. Estimated impact: 1,296+ eliminated GitHub API calls/day from delta guards alone, plus significant LLM token reduction across all services.

---

## What Was Delivered

### Batch 1 — Structural Guards (commit 5e79ab4)
- **Delta guard on git heartbeat** — `git diff --quiet || git push`. Eliminates 576 empty pushes/day.
- **Vault sync delta guard** — same pattern on 2-min rclone cycle. Eliminates 720 empty GitHub API calls/day.
- **queue_watcher.py inotifywait** — replaced `time.sleep(30)` busy-loop. Now event-driven, zero CPU poll overhead.
- **LLM() singleton** — hoisted from inside `orchestrator.run()` to module level. Prevents re-instantiation on every call.
- **classify() early-return** — skips LLM routing when intent is explicit (`engrave_request`, `edit_request`). Saves one LLM call per engraving/editing session.

### Batch 2 — Parameter Profiles (commit e53bb65)
- **TOKEN_PROFILES** in `llm.py` — per-task token ceilings: status=128, comms=256, quote=128, design=1024, synthesis=2048. Replaces global 2048 default.
- **TEMP_PROFILES** in `llm.py` — 0.1 for deterministic tasks, 0.7 for generative. Cuts verbose drift on structured output.
- **task_type param on chat()** — callers declare task type, get correct ceiling + temperature automatically.
- **comms-processor mtime guard** — skips opencode invocation if `COMMS.md` unchanged since last run.
- **djinn-daily no-op short-circuit** — skips model if queue empty and no carry-forward in yesterday's notes.
- **DESIGN_MODEL = qwen2.5-coder:7b** — replaces phi4:14b (9.1GB CPU offload) for 2D/parametric tasks. 4.7GB GPU-native, faster, sufficient for simple parts.

### Batch 3 — Service-Level Guards (commit: vault-sync auto)
- **djinn-ctx-router session guard** — skips context assembly when no active session (`loginctl` + process check). Eliminates 5-min context builds when machine is idle.
- **ChromaDB incremental indexer** — mtime-based differential: only indexes files newer than last run timestamp. `--full` flag required for complete re-index.
- **Shared nomic-embed-text cache** — SQLite cache at `~/.cache/djinn/embed-cache.db`. Key: SHA256(text), value: embedding vector. Shared across Slipbox, Clerk, vault indexer — same text embedded once, reused everywhere.
- **djinn-clerk watchdog** — replaced 1-hr systemd timer with `watchdog` filesystem observer on `RAW/` dir. Fires only on `close_write` events. `djinn-clerk.timer` disabled.
- **printer-error-logger state gate** — LLM summary call now gated on error state change. Repeated same-error polls skip LLM entirely.

### Batch 4 — Structural Pipeline (commit 5df6044)
- **Weekly review digest pre-processor** — strips daily notes to headers + action items before LLM synthesis. Estimated 60-70% input token reduction on weekly reviews.
- **SESSION-RESUME.md generator** — auto-generated on session-end: last 3 COMMS entries + active queue + system state snapshot. Claude reads one file instead of six.
- **Groq fallback downgrade** — `_GROQ_DEFAULT_MODEL` changed from `llama-3.3-70b-versatile` to `llama-3.1-8b-instant`. 70B model now explicit opt-in via `get_groq_model(task_type)`.
- **TIMEOUT_PROFILES** — per-task timeout map: status=12s, quote=10s, embed=8s, design=60s, synthesis=120s. Lightweight tasks fail fast instead of hanging 120s.
- **COMMS.md compaction cron** — weekly cron (Sun 03:00) archives entries older than 30 days to monthly JSONL. Keeps live COMMS.md lean.

---

## Technical Decisions

- **Batching by risk tier** — low-risk one-liners first (Batch 1), parameter changes second (Batch 2), service guards third (Batch 3), structural last (Batch 4). Allowed fast iteration with safe rollback boundaries at each batch.
- **SQLite for embed cache** — chosen over file-based cache for concurrent read safety across Slipbox, Clerk, and indexer running simultaneously on Salomon.
- **watchdog over inotifywait for clerk** — Python watchdog integrates cleanly with existing Python clerk script. inotifywait used for bash-based services (ctx-router guard).
- **SESSION-RESUME over context compression** — generating a pre-assembled resume file is deterministic and free. Compressing context with LLM would itself consume tokens.
- **Gemini hallucination flagged** — Gemini produced a fabricated security architecture diagram during today's session (invented OpenClaw as security agent, OpenRouter guardrails, Firecrawl, Gemma 4, MiniMax M3). Document was not saved. TASK-009 is the correct path for a real bug hunter agent. See bug report recommendation below.

---

## Files Created or Modified

- `djinn/core/llm.py` — TOKEN_PROFILES, TEMP_PROFILES, TIMEOUT_PROFILES, task_type param
- `djinn/core/orchestrator.py` — LLM singleton, classify() early-return
- `djinn/core/design_gen.py` — DESIGN_MODEL swap
- `~/.local/bin/comms-processor` — mtime guard
- `~/.local/bin/djinn-daily` — no-op short-circuit
- `~/.local/bin/djinn-ctx-router` — session guard
- `~/.local/bin/djinn-clerk-watch` — new watchdog service
- `~/.local/bin/djinn-comms-compact` — new compaction cron script
- `~/.cache/djinn/embed-cache.db` — new shared SQLite embed cache
- `djinn/QUEUE.md` — batch tracking throughout session
- `djinn/logs/reports/2026-06-07_api-reduction-sprint.md` — Salomon session report

---

## Validation

- All 4 batches confirmed committed and pushed by Salomon
- Batch 1: commit 5e79ab4
- Batch 2: commit e53bb65 (vault-sync auto-commit)
- Batch 3: vault-sync auto-commit
- Batch 4: commit 5df6044
- Local and origin/main confirmed matching after each batch
- 11 Python files, 7 bash scripts, 2 systemd service files, 1 SQLite module
- ~1709 lines added across vault

---

## Known Issues

- **SESSION-RESUME.md** needs at least one session-end run to validate output quality before Claude relies on it as primary context source. Recommend Claude verify on next cold-boot.
- **Embed cache** needs cache invalidation strategy for when source documents are substantially edited (currently keyed on exact text hash — edits create new entries, old ones persist). Low priority but should be addressed before cache grows large.
- **COMMS compaction** Python block uses shell variable interpolation inside heredoc — Salomon should verify `$CUTOFF` and `$ARCHIVE_FILE` expand correctly on first Sunday run.

---

## What's Next

- **TASK-009 → Claude** — Bug hunter agent architecture. Vault has zero automated scanning. djinn-bugreport is manual-only. This is the next HIGH priority item.
- **TASK-005 → Javier** — iPhone Shortcut for Djinn inbox. Flask endpoint live, shortcut not yet created.
- **TASK-006 → Javier** — iMac bookmarklet. Same dependency on Flask endpoint (already live).
- **TASK-007 → Gemini** — Session-end GDrive write convention. Needs to be established before Gemini's next session.
- Monitor Groq fallback behavior — confirm `DJINN_USE_GROQ` is not set in production `.env` on Salomon. Silent activation risk remains until confirmed.

---

## Recommendations

1. File a bug report for the Gemini hallucination incident: `djinn-bugreport "Gemini fabricated security architecture" "No vault grounding, context drift from prior session" gemini high fixed`
2. Run `djinn-session-end` on Salomon to generate the first SESSION-RESUME.md and verify output before Claude's next session.
3. Queue TASK-009 to Claude immediately — the bug hunter gap is real and the spec is ready.

---

*— Marcus, 2026-06-07*
