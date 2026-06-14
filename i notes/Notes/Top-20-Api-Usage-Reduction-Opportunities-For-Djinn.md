---
subject: 3d-printing/models/upgrades-requirements/forge
tags:
  - cs/api-optimization
  - cs/efficiency
  - business/cost-reduction
  - business/process-improvement
created: 2026-06-14
source: Perplexity export
---

# Top 20 API Usage Reduction Opportunities for Djinn Vault

## Summary
This note outlines the top 20 opportunities to reduce API usage in the Djinn Vault, focusing on both premium and local Ollama API calls. The document is intended for a multi-department discussion between Marcus, Claude, Gemini, and DrManzo.

## Key Points
- Heartbeat commits every 5 minutes to GitHub are unnecessary.
- Comms-processor fires every 3 minutes regardless of changes.
- History limit in OpenClaw is too low, causing session bloat.
- Fallback to Claude for simple tasks is inefficient.
- Daily triggers invoke models unconditionally.

## Details
### Tier 1 — Highest Impact (Do First)
1. **Heartbeat commits every 5 min to GitHub**
   - **Location:** `djinn/skills/djinn-heartbeat.md`
   - **Impact:** 288 git operations/day per machine.
   - **Department:** All

2. **comms-processor fires every 3 min regardless of COMMS.md changes**
   - **Location:** `SYSTEM-STATE.md` — `comms-processor` timer
   - **Impact:** Empty-pass LLM invocation if no new entries.
   - **Department:** Salomon / DrManzo

3. **historyLimit=5 is too low — causing session bloat and reloads**
   - **Location:** `SYSTEM-STATE.md` — OpenClaw gateway `historyLimit=5`
   - **Impact:** Re-injecting full identity/context files repeatedly.
   - **Department:** Claude / DrManzo

4. **Claude is the fallback for djinn-design even on simple tasks**
   - **Location:** `SYSTEM-STATE.md` — `DesignGenAgent` note: `phi4:14b → Claude if API key set`
   - **Impact:** Silent routing to Claude's Anthropic API.
   - **Department:** Claude / DrManzo

5. **djinn-daily triggers opencode with deepseek-r1:7b for PLAN.md every morning regardless**
   - **Location:** `SYSTEM-STATE.md` — djinn-daily timer `opencode wired, deepseek-r1:7b for PLAN.md`
   - **Impact:** Invocation of the model even on days with zero carry-forward.
   - **Department:** Salomon

### Tier 2 — High Impact
6. **Default max_tokens=2048 in llm.py with no per-task override**
   - **Location:** `djinn/core/llm.py` — `_DEFAULT_MAX_TOKENS = 2048`
   - **Impact:** Every `chat()` call reserves 2048 output tokens.
   - **Department:** All

7. **Temperature=0.7 default on deterministic tasks**
   - **Location:** `djinn/core/llm.py` — `_DEFAULT_TEMPERATURE = 0.7`
   - **Impact:** Longer, more verbose outputs with higher token consumption.
   - **Department:** All

8. **Clerk runs hourly on ALL RAW/ files even with processed-state tracking**
   - **Location:** `SYSTEM-STATE.md` — `djinn-clerk timer (1-hr)` + `clerk-processed.json`
   - **Impact:** Scan overhead fires regardless of new file existence.
   - **Department:** Salomon

9. **Vault indexer (djinn-vault-indexer) running on 688 files / 8,284 chunks**
   - **Location:** `INFRASTRUCTURE.md` — `djinn-vault-indexer ChromaDB`
   - **Impact:** Full re-index is expensive.
   - **Department:** Salomon

10. **Context window fixed at 16384 for qwen2.5:7b even on short tasks**
    - **Location:** `SYSTEM-STATE.md` — Ollama context table
    - **Impact:** Full KV cache allocation for short queries.
    - **Department:** Salomon

### Tier 3 — Medium Impact
11. **Marcus session brief loaded fresh every Perplexity session with no compression**
    - **Location:** `djinn/AGENTS.md` — `MARCUS-SESSION-BRIEF.md`
    - **Impact:** Full vault context dump grows over time.
    - **Department:** Marcus / DrManzo

12. **djinn-ctx-router fires every 5 min writing CONTEXT.md + STATE.md**
    - **Location:** `SYSTEM-STATE.md` — `djinn-ctx-router timer`
    - **Impact:** Frequent writes to CONTEXT and STATE files.
    - **Department:** Salomon

## References
- [Perplexity](https://www.perplexity.ai/search/2fd1c25d-12d7-45a0-a4f6-37281c5e3e48)

---

This note provides a structured overview of the top 20 API usage reduction opportunities in the Djinn Vault, focusing on both premium and local Ollama API calls. The document is intended for a multi-department discussion to optimize resource utilization.

## Related
- [[pplx_6162517d-e5cf-47e6-ba80-fd9db6a3f494]] — similarity 0.72
- [[2026-06-01_github-in-the-djinn-vault-repo-you-are-in-this-case-marcus-and-i-need-]] — similarity 0.72
