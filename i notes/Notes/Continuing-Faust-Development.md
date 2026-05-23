---
subject: business/project-management/data-model/outcome-orientation
tags:
  - business/project-management/modules/roles/faust/cli/core/adapters
  - business/project-management/tasks/results/faust/chat
created: 2026-05-23
source: Perplexity export
---

# Continuing Faust Development

## Summary
The next step in the development of Faust, a local, offline-first CLI LLM app, is to implement long-term memory using LangGraph's store-backed persistence. This will allow the assistant to remember user-specific facts across sessions and inject them into the graph before generation.

## Key Points
- Preserve current short-term memory behavior via existing checkpointer.
- Add a LangGraph store for durable memory.
- Namespace memories by stable user identifier.
- Represent long-term memories as structured JSON documents.
- Retrieve relevant memories using semantic search if available.
- Inject retrieved memories into the graph during response generation.

## Details
The current state of Faust includes:
- A working CLI with Typer, LangGraph, and Ollama/OpenAI-compatible adapters.
- Config loading, Pydantic models for messages/sessions/config.
- Correctly wired LangGraph flow with prompt injection and streamed response aggregation.
- Passing automated tests.

To implement long-term memory, the following steps are required:
1. **Preserve Short-Term Memory**: Keep the existing checkpoint system that ensures short-term conversation continuity within a thread ID.
2. **Add Long-Term Memory Layer**: Integrate a store-backed layer for durable user facts across sessions and thread IDs.
3. **Namespace Memories**: Use namespaces like `(user_id, "memories")` or `("memories", user_id)` to organize memories.
4. **Structured JSON Documents**: Represent long-term memories as structured JSON documents in the LangGraph store.
5. **Semantic Search Integration**: Utilize semantic search capabilities provided by LangGraph for retrieving relevant memories.

## References
- [LangChain Documentation](https://docs.langchain.com/oss/python/langchain/long-term-memory)

## Related
- [[Faust-Final]] — Current state of Faust development
- [[LangGraph-Integration]] — Integration details and best practices

TAG RULES:
- topic MUST be one of: psychology, law, business, cs, personal, creative
- path: topic/context/relevant/commonality/specific-tag
- 2-4 tags per note, use hyphens not spaces
- You may create new nodes at context level and below
- Existing vault tags for reference: bio.libretexts.org/Bookshelves/Introductory_and_General_Biology/General_Biology_, bio/neuroscience/executive-functions, bio/neuroscience/memories, biology/cell-biology/mitosis, biology/conception, biology/neuroscience/brain-pathways, biology/neuroscience/cerebellum, biology/neuroscience/motor-control, biology/neuroscience/symptoms, business/career-strategies, business/human-resources, business/llc-formation/california/software-development-company, business/marketing-revenue-models, business/marketing-revenue-models/toy-industry, business/passive-income-strategies/neuro-architecture-assets, business/passive-income-strategies/power-user-bluebeam-market, business/project-management/data-model/outcome-orientation, business/project-management/data-models/faust/core/models, business/project-management/milestones/scenarios, business/project-management/modules/roles, business/project-management/modules/roles/faust/cli/core/adapters, business/project-management/structure/phases, business/project-management/tasks/results, business/project-management/tasks/results/faust/chat