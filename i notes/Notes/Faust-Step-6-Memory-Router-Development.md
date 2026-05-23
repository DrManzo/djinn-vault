---
subject: business/project-management/modules/roles/faust/cli/core/adapters
tags:
  - faust/cli/memory-routing/architecture
  - project-management/data-models/faust-step-6
created: 2026-05-23
source: Perplexity export
---

# Faust Step 6 Memory Router Development

## Summary
This note outlines the current architecture and steps needed for Step 6 of the Faust project, focusing on developing a memory router to ensure deterministic recall answers.

## Key Points
- Current Architecture from Step 5: Typer command flow, LangGraph nodes with long-term memory retrieval.
- Likely Source of Routing Inconsistency: String rules or state-shape mismatch in the memory router.
- First File to Inspect/Patch: The LangGraph routing entrypoint (likely `src/faust/graph/router.py`).

## Details
The Faust project is a local, offline-first CLI assistant built with Typer, LangGraph, and Ollama/OpenAI-compatible adapters. Step 5 completed the foundational architecture by adding:
- A configurable long-term memory store layer.
- User-scoped memory namespaces for `profile.name`, `profile.birthdate`, and `preference.favorite_editor`.
- Explicit memory write handling for "remember that..." inputs.
- Memory retrieval logic in the graph, with deterministic recall routing before the normal LLM path.

However, real CLI tests revealed inconsistent surface behavior. Some recall queries still fall back to the normal LLM path instead of using the deterministic memory path. This inconsistency is likely due to:
1. The deterministic branch being too narrowly keyed or too late in the graph/CLI flow.
2. State-shape mismatch between CLI/session/checkpoint state and the memory router, where the graph has enough data but the router checks the wrong field, message role, or only raw text instead of normalized intent/slot signals.

For Step 6, the focus should be on making routing stricter, earlier, and more normalization-driven. The first exact file to inspect or patch is the LangGraph routing entrypoint, which decides whether a turn is a memory write, deterministic recall, or normal LLM traffic. This will likely involve modifying `src/faust/graph/router.py` to ensure that simple recall questions like "What is my favorite editor?" consistently return direct memory answers.

## References
- [Perplexity Export](https://www.perplexity.ai/search/304cced7-b838-4c12-a09d-03b20e813bbd)

## Related
- [[Faust-Step-5-Architecture]] — Architecture details from Step 5.
- [[LangGraph-Core-Concepts]] — Core concepts and usage of LangGraph in Faust.

TAG RULES:
- topic MUST be one of: psychology, law, business, cs, personal, creative
- path: topic/context/relevant/commonality/specific-tag
- 2-4 tags per note, use hyphens not spaces
- You may create new nodes at context level and below
- Existing vault tags for reference: bio.libretexts.org/Bookshelves/Introductory_and_General_Biology/General_Biology_, bio/neuroscience/executive-functions, bio/neuroscience/memories, biology/cell-biology/mitosis, biology/conception, biology/neuroscience/brain-pathways, biology/neuroscience/cerebellum, biology/neuroscience/motor-control, biology/neuroscience/symptoms, business/career-strategies, business/human-resources, business/llc-formation/california/software-development-company, business/marketing-revenue-models, business/marketing-revenue-models/toy-industry, business/passive-income-strategies/neuro-architecture-assets, business/passive-income-strategies/power-user-bluebeam-market, business/project-management/data-model/outcome-orientation, business/project-management/data-models/faust/core/models, business/project-management/milestones/scenarios, business/project-management/modules/roles, business/project-management/modules/roles/faust/cli/core/adapters, business/project-management/structure/phases, business/project-management/tasks/results, business/project-management/tasks/results/faust/chat, business/strategic-planning, career/career-factors/growth-opportunities, career/career-factors/income-stability, career/career-factors/job-security, career/career-factors/personality-fit, career/career-factors/work-life-balance, caregiving-support/adult-development, caregiving-support/adult-development/loss-of-autonomy, caregiving-support/postpartum-period, child-psychology/cognitive-development/piaget, child-psychology/community-resources, child-psychology/developmental-neonatology, child-psychology/developmental-neonatology/disability-awareness, child-psychology/developmental-tools, commonality/memory-classification, commonality/reconstructive-memory