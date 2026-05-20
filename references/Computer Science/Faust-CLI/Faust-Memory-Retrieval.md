---
title: "Faust Memory Retrieval"
created: 2026-05-19
modified: 2026-05-19
tags: [faust, memory-retrieval, langgraph, store, search, python, cross-thread, user-scoping]
source: "Perplexity AI Export"
category: "Computer Science/Faust-CLI"
---

## Summary
Step 8 of the Faust project: adding retrieval for saved facts. Covers search over stored memories, ranking and filtering, prompt injection of recalled facts, and cross-thread verification.

## Key Points
- Retrieval layer runs before prompt generation for non-direct-recall turns
- Exact slot match first, then lightweight keyword/text matching
- Top 1-3 results only, no semantic embeddings yet
- Retrieved memories stored in ephemeral execution state
- User-scoped retrieval prevents cross-user leakage
- Preserves deterministic slot recall for supported direct questions

## Details

### Retrieval Strategy
1. **Exact Slot Match**: Direct lookup for known slot keys
2. **Keyword Matching**: Lightweight text matching over stored fact text
3. **Top-K Selection**: Return only top 1-3 most relevant memories
4. **No Embeddings**: Semantic/vector search deferred to future step

### Implementation Shape
- Add retrieval node or pre-model retrieval hook in graph
- Add state fields: `recalled_memories` / `memory_hits`
- Update `build_prompt()` to include recalled facts when present
- Preserve direct deterministic recall behavior for supported slot questions

### Required Validation
1. **Automated Tests**:
   - Saved fact retrievable on different thread for same user
   - Irrelevant facts not injected
   - Retrieval does not break direct deterministic slot recall
   - Recalled facts appear in state before prompt generation
   - Retrieval isolated by user namespace

2. **Live CLI Smoke Tests**:
   - Memory-informed recall beyond simple direct slot questions

### Design Constraints
- Keep implementation narrow, explicit, and testable
- No embeddings, vector search, broad fuzzy memory extraction
- No large autonomous agent framework
- Preserve existing deterministic memory-answer path
- Keep Step 7 memory-bucket architecture intact

### Retrieval Flow
```
User Message → Router → (not direct recall) → Retrieval Node
                                                    ↓
                                        Search long-term store
                                        (user namespace only)
                                                    ↓
                                        Rank/filter top 1-3
                                                    ↓
                                        Attach to state.recalled_memories
                                                    ↓
                                        build_prompt() injects into context
                                                    ↓
                                        LLM generates informed response
```

### State Fields
- `recalled_memories`: List of MemoryRecord objects retrieved from store
- `memory_hits`: Count of relevant memories found
- Both stored in ephemeral state (not persisted to checkpoint or long-term)

## References
- LangGraph Store Search: https://langchain-ai.github.io/langgraph/reference/store/
- Perplexity AI Chat Export (2026-05-19)

## Related
- [[Faust-CLI-Project-Hub]]
- [[Faust Long-Term Memory Foundation]]
- [[Faust Memory Router]]
- [[Faust-Memory-Router]]
- [[Faust-Long-Term-Memory-Foundation]]
