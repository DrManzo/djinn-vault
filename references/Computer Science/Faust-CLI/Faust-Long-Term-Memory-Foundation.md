---
title: "Faust Long-Term Memory Foundation"
created: 2026-05-19
modified: 2026-05-19
tags: [faust, long-term-memory, langgraph, store, persistence, python, memory-architecture, user-scoping]
source: "Perplexity AI Export"
category: "Computer Science/Faust-CLI"
---

## Summary
Step 5 of the Faust project: building a configurable long-term memory store layer using LangGraph's store abstraction. Covers memory schema design, user-scoped namespaces, slot-based memory handling, explicit memory writes, and the distinction between short-term checkpoint memory and long-term durable memory.

## Key Points
- LangGraph's clean mental model: **checkpointer = thread memory**, **store = durable user memory**
- Short-term memory is thread-scoped checkpoint state (conversation within a thread ID)
- Long-term memory persists across sessions and thread IDs, stored in namespaces and keys
- Memory schema: type, text, source, confidence, timestamps, tags
- User-scoped namespaces prevent memory leakage between users
- Slot-based memory handling for structured facts (profile.name, profile.birthdate, preference.favorite_editor)
- Explicit "remember that..." style inputs trigger memory writes

## Details

### Memory Architecture Distinction
| Type | Scope | Storage | Purpose |
|------|-------|---------|---------|
| Short-term | Thread ID | Checkpointer (InMemorySaver/SqliteSaver) | Conversation continuity within a session |
| Long-term | User ID | Store (InMemoryStore/SqliteStore) | Durable facts across sessions |
| Ephemeral | Turn only | FaustState fields | Routing hints, transient reasoning |

### Memory Schema
```json
{
  "type": "preference|profile|constraint|fact",
  "text": "User prefers concise responses.",
  "source": "explicit|inferred",
  "confidence": 0.0,
  "created_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp",
  "tags": ["style", "response"]
}
```

### Supported Slots
- `profile.name` — User's name
- `profile.birthdate` — User's birthdate
- `preference.favorite_editor` — User's preferred code editor

### Memory Write Detection
Patterns recognized for explicit memory writes:
- "my favorite editor is..." → `preference.favorite_editor`
- "i prefer...editor" → `preference.favorite_editor`
- "my name is..." → `profile.name`
- "i was born on..." → `profile.birthdate`
- "my birthdate is..." → `profile.birthdate`

### Memory Retrieval Flow
1. Inspect current user message
2. Search durable memory store under current user namespace
3. Rank/filter small number of relevant matches (top 1-3)
4. Attach recalled facts to state
5. Inject into prompt construction before assistant responds
6. Verify works across thread boundaries

### Implementation Design
1. **Store Abstraction**: `InMemoryStore` for dev/tests, `SqliteStore` for production
2. **User ID**: Stable identifier in invocation context/config
3. **Graph Compilation**: Pass both checkpointer and store to compiled graph
4. **Pre-LLM Retrieval**: Derive namespace from user_id, search store, select top memories, serialize into prompt
5. **Write-Back Logic**: Explicit save for "remember" commands, optional heuristic extraction for durable preferences

### Namespace Structure
- Namespace tuple: `(config.memory.namespace, user_id)`
- Example: `("memories", "default")`
- Ensures user isolation and clean organization

### Testing Targets
- Long-term memory persists across separate sessions with same `user_id`
- Long-term memory not visible across different `user_id` namespaces
- Explicit "remember" requests store memory correctly
- Retrieved memory injected before generation
- Short-term checkpoint memory behaves exactly as before within a thread
- Store-free or memory-disabled configurations fail gracefully

### Reality Check
The architecture for memory is in place, but surface behavior may still be inconsistent. Some recall turns may fall back to normal LLM-style answers or hallucinated facts instead of always using the deterministic memory path. Step 5 should be treated as **architectural bedrock**, not as a fully polished end-user memory experience.

## References
- LangGraph Long-Term Memory: https://langchain-ai.github.io/langgraph/how-tos/memory/
- LangGraph Store API: https://langchain-ai.github.io/langgraph/reference/store/
- Perplexity AI Chat Export (2026-05-19)

## Related
- [[Faust-CLI-Project-Hub]]
- [[Faust Memory Router]]
- [[Faust Memory Retrieval]]
- [[Faust-Memory-Router]]
- [[Faust-Memory-Retrieval]]
- [[Faust-Project-Setup-Architecture]]
