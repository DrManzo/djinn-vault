---
title: Session Report — Context Router Phase 1
agent: Claude
date: 2026-05-25
tags: [djinn, report, architecture, context-router, salomon]
related: [[2026-05-25_telegram-hybrid-gateway]] | [[build-log]] | [[SPEC-djinn-context-router]]
---

# Session Report — Context Router Phase 1

**Date:** 2026-05-25
**Agent:** Claude
**Session type:** Architecture + Build
**Trigger:** Salomon operating without USER.md, MEMORY.md, or SOUL.md — all crowded out by 11,490-char AGENTS.md consuming the 15,000-char bootstrap budget.

---

## Summary

Built the Phase 1 context router: a separate Python service that assembles context in priority order (Soul → User → Agent Identity → Agent Skills → Live State) and writes it to a single CONTEXT.md file the workspace loads automatically. AGENTS.md was trimmed from 11,490 to 1,904 chars. The vault (688 files) is now indexed into ChromaDB via nomic-embed-text, enabling per-message semantic memory recall. All services: 11/11 OK.

---

## What Was Built or Changed

- **djinn-vault-indexer** — walks ~/Obsidian/, chunks 688 markdown files into 8,284 vectors via nomic-embed-text, stores in ChromaDB at `~/.local/share/djinn/vault-index/`. Incremental on re-run (MD5 hash per file). Skips RAW/ and COMMS.md (too large, low signal).

- **djinn-ctx-assembler** — CLI: given a query string, does semantic search against the vault index and returns a context package (User → Memory → Agent State) within a char budget. Used by Telegram gateway for per-message vault recall.

- **djinn-ctx-router** (service) — runs every 5 minutes:
  1. Polls Moonraker, Ollama, print queue, vault sync
  2. Writes `~/.openclaw/agents/salomon/STATE.md` (live machine state)
  3. Assembles and writes `~/.openclaw/workspace/CONTEXT.md` (Soul + User trim + Identity + Skills + State)
  4. Triggers incremental vault reindex in background

- **djinn-agent-doctor** — 11-check health report: all services, Ollama, Calliope, print queue, vault sync, vault index, disk. `--short` for Telegram, `--json` for scripting.

- **Salomon agent dir** (`~/.openclaw/agents/salomon/`) — IDENTITY.md, SKILLS.md, STATE.md (machine-written). Replaces the tool/skill documentation that was bloating AGENTS.md.

- **AGENTS.md** — trimmed from 11,490 → 1,904 chars. Kept: red lines, model routing table, lane boundaries, report standard. Removed: vault layout docs, daily plan detail, workflow descriptions (moved to agent dir).

- **Workspace budget fixed**:
  - Before: AGENTS.md (11,490) ate 76% of budget → USER.md, SOUL.md, MEMORY.md never loaded
  - After: AGENTS.md (1,904) + CONTEXT.md (8,743 including SOUL + USER) = all critical context loads within 14,204/15,000 chars

- **Telegram gateway** — `/status` command added (calls djinn-agent-doctor --short). ctx-assembler wired in for per-message vault recall before every model call.

---

## Technical Decisions

**SOUL.md embedded in CONTEXT.md** — SOUL.md (3,308 chars) was being skipped alphabetically after SCHEDULE.md used the remaining budget. Rather than rename files or increase the budget, ctx-router now includes SOUL.md content in CONTEXT.md directly. This guarantees it always loads regardless of workspace file ordering.

**USER.md capped at 2,500 chars in CONTEXT.md** — Full USER.md is 9,509 chars, mostly relationship notes and history. The first 2,500 chars contain the identity, communication style, and values — the high-signal portion. Full file stays in workspace as fallback.

**pyenv Python 3.11 for all context router scripts** — chromadb was installed in pyenv 3.11, not system Python. Shebangs explicitly point to `/home/drmanzo/.pyenv/versions/3.11.11/bin/python3`.

**Separate service, not OpenClaw hook** — Context router runs independently; OpenClaw picks up CONTEXT.md as a normal workspace file. Clean separation: context router doesn't need to know about OpenClaw's internals.

**Per-message vault recall in Telegram, static for Discord** — Telegram gateway calls ctx-assembler with the user's message as query. Discord uses the static CONTEXT.md (updated every 5 min). This is the right tradeoff: Telegram is fully under our control; Discord is controlled by OpenClaw.

---

## Files Created or Modified

```
~/.local/bin/djinn-vault-indexer                new — vault → ChromaDB indexer
~/.local/bin/djinn-ctx-assembler               new — per-message context assembler
~/.local/bin/djinn-ctx-router                  new — context router service
~/.local/bin/djinn-agent-doctor                new — 11-check health report
~/.local/bin/djinn-telegram-gateway            updated — /status command + ctx-assembler
~/.config/systemd/user/djinn-ctx-router.service  new — systemd user service
~/.openclaw/agents/salomon/IDENTITY.md         new — Salomon identity
~/.openclaw/agents/salomon/SKILLS.md           new — Salomon tool reference
~/.openclaw/agents/salomon/STATE.md            new — machine-written live state
~/.openclaw/workspace/AGENTS.md               trimmed 11,490 → 1,904 chars
~/.openclaw/workspace/CONTEXT.md              new — machine-written, assembles all critical context
~/.local/share/djinn/vault-index/             new — ChromaDB persistent store (8,284 chunks)
```

---

## Dependencies Installed

| Package | Method | Purpose |
|---------|--------|---------|
| chromadb | pip3 (pyenv 3.11) | Vector database for vault index |

(nomic-embed-text already available on Ollama)

---

## Tests & Validation

- djinn-agent-doctor: 11/11 OK ✓
- Vault index: 8,284 chunks across 688 files ✓
- ctx-assembler query test ("proxy bubbler print quote"): USER.md + relevant chunks returned ✓
- CONTEXT.md size: 8,743 chars — loads fully within 15K budget ✓
- Workspace budget simulation: 14,204/15,000 — all critical files load ✓
- Telegram /status: command registered, calls djinn-agent-doctor --short ✓
- ctx-router service: active, 5-min tick confirmed in logs ✓

---

## Known Issues / Caveats

- **Discord still uses static context** — per-message semantic recall only on Telegram. Discord would require a middleware layer similar to Telegram gateway. Tracked for Phase 2.
- **First Ollama call after djinn-idle.timer (22:00) eviction** — deepseek-r1:7b needs to load. ~30s cold start. Acceptable but users may notice delay.
- **CONTEXT.md updated every 5 min** — if Calliope state changes mid-print, Salomon's context may be up to 5 min stale. STATE.md update frequency could be tuned down for active prints.
- **telegram-main agent + bindings still in openclaw.json** — dead code from the failed OpenClaw Telegram attempts. Harmless but should be cleaned up.

---

## What's Next

- [ ] Test `/status` on Telegram — @Javier
- [ ] Test conversational vault recall on Telegram (ask about proxy bubbler, coins, etc.) — @Javier
- [ ] Clean up telegram-main agent and bindings from openclaw.json — @Claude
- [ ] Phase 2: Discord middleware for per-message recall (low priority, static context is good enough) — @Claude
- [ ] Tune STATE.md update frequency for active prints (1-min instead of 5) — @Claude

---

*— Claude, 2026-05-25*
