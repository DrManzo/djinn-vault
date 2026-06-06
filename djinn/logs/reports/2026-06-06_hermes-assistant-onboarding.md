---
title: Session Report — Hermes Agent Onboarded as Assistant + Global LLM Client
agent: Claude
date: 2026-06-06
tags: [djinn, report, hermes, assistant, llm-client, gap-analysis]
related: [[build-log]] [[AGENTS.md]] [[djinn/core/llm.py]]
---

# Session Report — Hermes Agent Onboarded as Assistant + Global LLM Client

**Date:** 2026-06-06
**Agent:** Claude
**Session type:** Architecture + Build
**Trigger:** Javier ran Hermes Agent session to interview it as a potential team member; Claude built supporting infrastructure and integrated Marcus's research output.

---

## Summary

Two parallel workstreams converged this session. First, a Hermes Agent session conducted a self-directed gap analysis of the Djinn Vault and proposed a formal "Assistant" role — the agent interviewed itself, created its own profile in AGENTS.md, and built its Hermes skill definition. Second, Claude built `djinn/core/llm.py`, a platform-level LLM client that gives all Djinn modules a single unified import point for Ollama (local) and Groq (cloud) backends, eliminating per-module client instantiation. Marcus delivered TASK-067, a comprehensive gap analysis confirming the vault is architecturally sound with five addressable operational gaps.

---

## What Was Built or Changed

- **`djinn/core/llm.py`** — Global LLM client (229 lines). Supports Ollama (default, `qwen2.5:7b`) and Groq (`llama-3.3-70b-versatile`) backends via env vars. Exposes `get_client()`, `get_model()`, and `chat()`. No module should instantiate its own client — import from here.
- **`djinn/AGENTS.md`** — Overwritten by Hermes Agent to add the Assistant lane: skill development, documentation enhancement, process engineering, research support. Lane boundaries, write access, and Marcus collaboration workflow documented.
- **`~/.hermes/skills/djinn-assistant/SKILL.md`** — Hermes skill definition for operating as the Assistant agent within Djinn.
- **`djinn/research/marcus/TASK-067_djinn-gap-analysis.md`** — Marcus's completed gap analysis (305 lines). Comparative analysis table, gap analysis across 7 domains, 17-item prioritized roadmap, risk assessment, copy-pasteable validation commands.
- **`djinn/research/marcus/TASK-001_djinn-gap-analysis.md`** — Hermes-authored task brief for Marcus (superseded by TASK-067 delivery).

---

## Technical Decisions

**Single LLM client module over per-tool instantiation** — Every Djinn script was rolling its own OpenAI client pointing at Ollama. That creates config drift and makes backend switching (e.g., Ollama → Groq for speed) require touching every file. One module with env-var switching solves it.

**Groq as the cloud fallback, not OpenRouter** — Groq offers near-instant inference on llama-3.3-70b at zero-cost tier; OpenRouter adds a routing layer and cost overhead. Groq is the right cloud burst option for non-latency-sensitive tasks.

**Hermes as "Assistant" lane, not a Salomon replacement** — Hermes hit rate limits (Ollama session cap on nemotron-3-super:cloud, Claude API extra-usage error) during the onboarding session, which actually validates the need for the automation-over-AI principle Marcus identified. Hermes is useful for skill development and doc work, not routine ops.

---

## Files Created or Modified

```
djinn/core/llm.py                                    ← new: global LLM client
djinn/AGENTS.md                                      ← updated: Assistant lane added
djinn/research/marcus/TASK-067_djinn-gap-analysis.md ← new: Marcus gap analysis delivery
djinn/research/marcus/TASK-001_djinn-gap-analysis.md ← new: Hermes task brief (scaffolding)
~/.hermes/skills/djinn-assistant/SKILL.md            ← new: Hermes skill definition (local only)
djinn/logs/reports/2026-06-06_hermes-assistant-onboarding.md ← this report
```

---

## Tests & Validation

- `djinn/core/llm.py` passes Python import check (no syntax errors, openai dependency present in `.venvs/djinn`)
- AGENTS.md confirmed readable and properly structured
- TASK-067 confirmed present in vault at expected path

---

## Known Issues / Caveats

- Hermes session hit Ollama session rate limit (nemotron-3-super:cloud) and Claude API extra-usage limit mid-session. Hermes is on Ollama free tier — need to either upgrade or route Hermes sessions through local models with sufficient context window (qwen3.6 worked but was slow).
- Git divergence: local HEAD has 3 Salomon vault-sync commits not on remote; remote has 2 Claude commits (llm.py + TASK-067) not local. Resolving via rebase this session.
- AGENTS.md was overwritten by Hermes Agent — need to verify it didn't drop any critical sections from the previous version (print safety, GATEWAY reference, lane boundaries all confirmed present in the new version).

---

## What's Next

- [ ] Review Marcus's TASK-067 roadmap and prioritize the top 5 script automations — @Claude/@Javier
- [ ] Build `djinn-system-health` script (zero AI needed, highest impact per Marcus) — @Claude
- [ ] Wire `djinn/core/llm.py` into existing Djinn tools that have inline client instantiation — @Claude
- [ ] Set Hermes to use a local 64K+ context model by default (qwen2.5:7b is too small, qwen3.6 works) — @Javier
- [ ] Add Groq API key to Salomon env if cloud burst is wanted — @Javier

---

*— Claude, 2026-06-06*
