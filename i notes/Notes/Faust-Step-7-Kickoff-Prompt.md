---
subject: business/project-management/modules/roles/faust/cli/core/adapters
tags:
  - business/project-management/tasks/results/faust/chat
created: 2026-05-23
source: Perplexity export
---

# Faust Step 7 Kickoff Prompt

## Summary
The Faust project is advancing to Step 7, which aims to formalize memory buckets and introduce minimal multi-model role routing. This step will classify state into checkpoint, long-term, and ephemeral categories while ensuring all model roles read from a consistent shared state contract.

## Key Points
- **Memory Bucket Classification**: 
  - Checkpoint Memory: Thread/session continuity, messages, current task state, active role, resumable graph outputs.
  - Long-Term Memory: Durable user facts and preferences (continuing the narrow slot model from Step 6).
  - Ephemeral State: Temporary routing hints, pending correction context, current plan, requested tests, transient reasoning that should not persist.

- **Shared State Contract**: Ensure all model roles read from the same `FaustState` structure and write back in a consistent format.
  
- **Minimal Role Routing**:
  - Assistant: General conversation.
  - Reasoner: Planning and task decomposition.
  - Coder: Code-focused implementation and test selection.

- **Scoped Self-Test Loop**: Allow coding workflows to request and run relevant tests, with actual test execution (pytest) as the source of truth.

## Details
Step 7 is structured into three main phases:
1. **Bucket Map**:
   - Inspect current `FaustState` definition in `src/faust/core/models.py`.
   - Inventory all current state fields.
   - Label each field as checkpoint, long-term, or ephemeral.
   - Document the mapping in code comments or a small design doc.

2. **Role State**:
   - Add minimal state fields for requested role and task type.
   - Normalize role output shape so all roles return the same core keys.
   - Update `FaustState` model with new fields.
   - Update tests to verify new fields can be set and read.

3. **Routing**:
   - Add a small router node in `src/faust/adapters/graph.py` that selects assistant, reasoner, or coder.
   - Use narrow rules first (e.g., if user says "plan this" → reasoner; if user says "write code for..." → coder; else → assistant).
   - Wire the router into the graph flow.
   - Add conditional edges for role decisions.

## References
- [Perplexity](https://www.perplexity.ai/search/6495b70c-138b-4f1b-ab00-d205ee87d8d3)

## Related
- [[Faust-Step-6-Kickoff-Prompt]] — Context and background for the Faust project.
- [[Faust-Core-Models]] — Detailed documentation on `FaustState` structure.