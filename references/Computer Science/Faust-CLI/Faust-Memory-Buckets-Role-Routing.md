---
title: "Faust Memory Buckets & Role Routing"
created: 2026-05-19
modified: 2026-05-19
tags: [faust, memory-buckets, role-routing, langgraph, python, multi-model, state-management, ephemeral-state]
source: "Perplexity AI Export"
category: "Computer Science/Faust-CLI"
---

## Summary
Step 7 of the Faust project: formalizing memory buckets and introducing minimal multi-model role routing. Covers the classification of state into checkpoint, long-term, and ephemeral buckets, plus role routing for assistant, reasoner, and coder models.

## Key Points
- Explicit distinction between checkpoint memory, long-term memory, and ephemeral state
- Role routing layer selects assistant, reasoner, or coder based on task type
- Each role reads from shared `FaustState` and writes back in normalized format
- Scoped self-test loop allows coding workflows to request and run pytest tests
- Minimal state additions: `requested_role`, `active_agent`, `task_type`, `ephemeral_context`, `requested_tests`, `execution_notes`
- Preserves Step 6 memory behavior (47 tests still green)

## Details

### Memory Bucket Classification

#### Checkpoint Memory
- Thread/session continuity
- Messages (conversation history)
- Current task state
- Active role
- Resumable graph outputs
- **Scoped by**: `thread_id`
- **Storage**: InMemorySaver or SqliteSaver

#### Long-Term Memory
- Durable user facts and preferences
- Narrow slot model: `profile.name`, `profile.birthdate`, `preference.favorite_editor`
- **Scoped by**: `user_id`
- **Storage**: InMemoryStore or SqliteStore
- **Namespace**: `(config.memory.namespace, user_id)`

#### Ephemeral State
- Temporary routing hints
- Pending correction context
- Current plan
- Requested tests
- Transient reasoning that should not persist
- **Scoped by**: Current turn only
- **Storage**: FaustState fields (not persisted)

### Proposed State Additions
| Field | Type | Bucket | Purpose |
|-------|------|--------|---------|
| `requested_role` | str | Ephemeral | What role should handle this turn |
| `active_agent` | str | Checkpoint | Which role actually ran |
| `task_type` | str | Ephemeral | general, reasoning, coding, memory |
| `ephemeral_context` | dict | Ephemeral | Short-lived routing or correction hints |
| `requested_tests` | list | Ephemeral | Tests proposed by coder/reasoner |
| `execution_notes` | str | Ephemeral | Normalized internal output from a role |

### Role Routing
Narrow rules for role selection:
- **assistant**: General conversation (default)
- **reasoner**: Planning and task decomposition (triggered by "plan this", "think about")
- **coder**: Code-focused implementation and test selection (triggered by "write code for", "implement")

### Role Output Contract
All roles return the same normalized format:
- `response`: The role's output text
- `intent`: Classified intent of the response
- `active_agent`: Which role generated this
- `requested_tests`: Tests to run (coder/reasoner only)
- `execution_notes`: Internal notes for downstream processing

### Implementation Order
1. **Phase 1: Bucket Map** — Inventory current state fields, classify into buckets
2. **Phase 2: Role State** — Add minimal state fields, normalize role output shape
3. **Phase 3: Routing** — Add router node in graph, wire conditional edges
4. **Phase 4: Self-Test Loop** — Add graph node that runs scoped tests via pytest

### What Step 7 Should NOT Do
- Build a full autonomous supervisor swarm
- Introduce broad fuzzy memory extraction beyond narrow slots
- Add tool explosion or complex planner recursion
- Redesign the whole CLI around agents

### Success Criteria
- Faust explicitly distinguishes checkpoint, long-term, and ephemeral state
- Graph has small role-routing layer for assistant/reasoner/coder
- Each role reads bounded, consistent context from shared state
- Each role writes results back in normalized format
- Code-oriented flows can run scoped tests before final completion
- Existing Step 6 memory behavior continues to pass unchanged

## References
- LangGraph StateGraph: https://langchain-ai.github.io/langgraph/reference/graphs/
- Perplexity AI Chat Export (2026-05-19)

## Related
- [[Faust-CLI-Project-Hub]]
- [[Faust Memory Router]]
- [[Faust Memory Retrieval]]
- [[Faust-Memory-Router]]
- [[Faust-Long-Term-Memory-Foundation]]
- [[HERMES Model Framework]]
