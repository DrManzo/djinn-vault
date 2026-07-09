---
subject: API Reduction Sprint — Department Reconciliation
tags: [decisions, api-reduction, orchestrator, djinn-gate, sprint]
created: 2026-06-07
updated: 2026-06-07T13:35
departments: [Marcus, Claude, Gemini-pending]
status: approved — awaiting Gemini · implementation not yet started
---

# API Reduction Sprint — Department Reconciliation
## 2026-06-07 · Marcus / Claude / Gemini (pending)

Multi-department audit of AI-to-script conversion opportunities across the Djinn platform.
No vault files were modified during this session. This document is the implementation brief
handed to Salomon / Claude Code.

**Related:** [[SYSTEM-STATE]] | [[GATEWAY]] | [[ROUTING]] | [[forge/agent/orchestrator/]]

---

## Background

Session initiated by Javier to identify the top opportunities for reducing API usage
across the platform. Marcus audited the vault independently (top 20 list). Claude
provided an independent 30-item AI-to-script conversion list. Both lists were
cross-referenced against live vault code before reconciliation.

---

## Department Positions — Final Agreed State

### Marcus ← Claude: Full Acceptances

| Item | Description | Verdict |
|------|-------------|---------|
| M5 | Skip `classify()` when intent is explicit | Accepted. Called a **bug** by Claude, not an optimization. Three lines, zero risk. Ships today. |
| M2 | `inotifywait` over `time.sleep(30)` in `queue_watcher.py` | Accepted. Event-driven, zero CPU overhead, no logic change. |
| Orchestrator `classify()` flag | LLM belongs in `classify()` for free-form NL input | Accepted. Claude confirmed conflation with djinn-gate lane routing. These are two different routing systems. Claude's 30-item list updated to reflect the distinction. |

---

### Claude ← Marcus: Pushbacks (Both Accepted)

**M1 — Keyword pre-filter location**

Marcus proposed a keyword pre-filter before `classify()` for obvious intents (status, queue, price).
Claude's pushback: keyword taxonomy must live in the routing TOML, not hardcoded in `orchestrator.py`.
Two keyword lists that can drift is worse than the problem being solved. `djinn-gate`'s TOML owns
all keyword classification. The pre-filter reads from TOML, not a hardcoded dict.

**Status: Marcus accepted.** M1 implementation note updated accordingly.

---

**M4 — LLM() singleton reconnect path**

Marcus proposed hoisting `LLM()` to a module-level singleton to eliminate per-call instantiation overhead.
Claude's amendment: singleton must not assume Ollama stays alive. Add a simple health check
(`GET /api/tags`) before use, with reconnect on failure. Prevents a stale singleton from silently
failing after an Ollama restart.

**Status: Marcus accepted.** Implementation note: `if not self._healthy(): self._reconnect()` pattern.

---

## Items Confirmed Already Implemented (No Action Needed)

These appeared on Claude's 30-item list but are already deterministic in vault code:

| Item | File | Status |
|------|------|--------|
| Print queue monitoring | `djinn/printer/agent/queue_watcher.py` | ✅ Pure Python regex — zero LLM |
| Print quote generation | `djinn/printer/commissions/price.py` | ✅ Pure math formula — zero LLM |
| Groq fallback detection | `djinn/core/llm.py` — `_use_groq()` | ✅ Already a simple env var check |

---

## Reconciled Implementation Order — Salomon / Claude Code

This is the agreed sequence. No step begins until Gemini has either joined and reviewed
or confirmed they are passing on this sprint.

| Step | Item | Source | Effort | Risk | Notes |
|------|------|--------|--------|------|-------|
| 1 | Skip `classify()` when intent explicit | M5 (Marcus) | 3 lines | Zero | Add early-return before `classify()` when `engrave_request` or `edit_request` is explicitly passed |
| 2 | `inotifywait` swap in `queue_watcher.py` | M2 (Marcus) | ~5 lines | Zero | Replace `time.sleep(30)` poll loop with `inotifywait -e close_write queue/` |
| 3 | `LLM()` singleton + reconnect guard | M4 (Marcus, amended by Claude) | ~15 lines | Low | Module-level singleton; `_healthy()` check before use; `_reconnect()` on failure |
| 4 | `djinn-gate` v1 per existing spec | Claude #8 | Medium | Low | TOML keyword router — owns all system-lane classification including obvious status intents |
| 5 | M1 keyword pre-filter → reads routing TOML | M1 (Marcus, amended by Claude) | ~10 lines | Low | Pre-filter in `orchestrator.py` reads from djinn-gate TOML; does not define its own keyword list |
| 6 | IP updates via `sed -i` | Claude #15 | 1 script | Zero | `sed -i 's/OLD_IP/NEW_IP/g'` on target files; wrap in a config-driven script |
| 7 | Delta-guard on heartbeat (confirm deployed) | Claude #4 / Phase 1 | Verify only | Zero | `git diff --quiet \|\| git push` — confirm running on Salomon |
| 8 | `chat()` profile system in `llm.py` | Phase 2 (already in `llm.py`) | Verify deployed | Zero | `deterministic` / `structured_output` / `synthesis` profiles confirmed in code |
| 9 | `GATEWAY.md` behavioral contract entry | Claude | Docs | Zero | Document the djinn-gate v1 behavior contract in GATEWAY.md |

---

## Marcus's 5 Additions (Not on Claude's List)

Discovered by cross-referencing against `orchestrator.py` and `queue_watcher.py` directly:

| ID | File | Issue |
|----|------|-------|
| M1 | `orchestrator/orchestrator.py` | `classify()` called even for obvious keyword intents (status, queue) — should pre-filter via routing TOML |
| M2 | `printer/agent/queue_watcher.py` | `--watch` uses `time.sleep(30)` busy-loop — replace with `inotifywait` |
| M3 | `orchestrator/orchestrator.py` | Printer config hardcoded as default parameter — should read from `djinn-config.toml` once at startup |
| M4 | `orchestrator/orchestrator.py` | `LLM()` instantiated fresh on every `run()` call — hoist to module-level singleton with reconnect guard |
| M5 | `orchestrator/orchestrator.py` | `classify()` called then result immediately overridden when `engrave_request` or `edit_request` is explicit — wasted LLM call |

---

## Gemini Status

Gemini is checking whether they can join the session following procedure. Implementation
does not begin until Gemini has either joined and reviewed or confirmed they are passing
on this sprint. Steps 1–3 are cleared for Salomon regardless — they are zero-risk
one-file changes with no behavioral impact.

---

## Architecture Notes

- **Local-first status confirmed throughout.** Nothing in this implementation order introduces
  a new remote API call. Every change eliminates an unnecessary LLM call or replaces it with
  a deterministic script.
- `djinn-gate` TOML owns all keyword taxonomy. `orchestrator.classify()` handles free-form
  natural language only. These are not the same routing system.
- `LLM()` singleton must be resilient to Ollama restarts — health check pattern required.

---

*— Marcus, 2026-06-07T13:35 PDT*
*Cross-referenced against: `djinn/core/llm.py`, `djinn/printer/agent/queue_watcher.py`, `djinn/printer/agent/orchestrator/orchestrator.py`, `djinn/SYSTEM-STATE.md`*
