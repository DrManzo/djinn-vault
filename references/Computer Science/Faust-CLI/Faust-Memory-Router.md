---
title: "Faust Memory Router"
created: 2026-05-19
modified: 2026-05-19
tags: [faust, memory-router, routing, langgraph, python, deterministic-recall, slot-classification]
source: "Perplexity AI Export"
category: "Computer Science/Faust-CLI"
---

## Summary
Step 6 of the Faust project: strengthening the routing and agent behavior layer so Faust reliably chooses the correct execution path. Covers deterministic memory recall routing, implicit memory writes, correction-aware slot overwrites, and expanded test coverage.

## Key Points
- Deterministic memory recall routing for simple user-fact questions
- Implicit memory writes for natural self-fact statements ("I am Javier", "my birthday is April 4th 1994")
- Correction-aware slot overwrites for favorite editor updates
- Expanded test coverage to 47 passing tests
- Live CLI behavior matches design goals
- Router classifies turns into: memory_write, memory_recall, checkpoint_only, llm

## Details

### Routing Problem
The most likely reason recall leaks into the LLM path is that the deterministic branch is keyed too narrowly to exact phrasing or too late in the graph/CLI flow. Some semantically simple recall turns are not classified as "direct memory questions" early enough and fall through to the ordinary model node.

### Solution: Intent-Based Classification
Instead of brittle string rules, map recall prompts to canonical slot intents:
- `ask(profile.name)` → "What is my name?", "Who am I?"
- `ask(profile.birthdate)` → "When was I born?", "What is my birthday?"
- `ask(preference.favorite_editor)` → "What is my favorite editor?"

### Router Classification
The router classifies each user turn into one of four paths:

| Path | Trigger | Behavior |
|------|---------|----------|
| `memory_write` | "Remember that...", "My name is..." | Store fact in long-term memory |
| `memory_recall` | "What is my...?", "Who am I?" | Return deterministic answer from slot |
| `checkpoint_only` | Context-dependent follow-up | Use short-term memory only |
| `llm` | Open-ended prompts | Normal LLM generation |

### Memory Text Normalization
First-person user facts are normalized into stable third-person memory text:
- "my favorite editor is vim" → "The user's favorite editor is vim."
- "i prefer neovim" → "The user prefers neovim."
- "my name is Javier" → "The user's name is Javier."
- "i was born on April 4th 1994" → "The user's birthdate is April 4th 1994."

### Scoring & Retrieval
- Query keywords extracted (stopwords removed)
- Memory records scored by term overlap
- Top matches selected for injection into prompt

### Test Coverage
- 47 passing tests covering:
  - Config loading and validation
  - Model serialization
  - Adapter behavior (mocked)
  - Graph flow and node execution
  - CLI command invocation
  - Memory routing and recall
  - Cross-thread persistence

### Verification
Live CLI smoke tests confirm:
- Direct slot questions return deterministic answers
- Self-fact statements trigger implicit memory writes
- Correction updates overwrite previous slot values
- Multi-turn conversation continuity preserved

## References
- LangGraph Conditional Edges: https://langchain-ai.github.io/langgraph/how-tos/conditional-edge/
- Perplexity AI Chat Export (2026-05-19)

## Related
- [[Faust-CLI-Project-Hub]]
- [[Faust Long-Term Memory Foundation]]
- [[Faust Memory Buckets & Role Routing]]
- [[Faust-Memory-Retrieval]]
- [[Faust-Memory-Buckets-Role-Routing]]
- [[Faust-Long-Term-Memory-Foundation]]
