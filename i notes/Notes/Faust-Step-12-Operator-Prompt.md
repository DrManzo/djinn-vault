---
subject: business/management-methods/faust/cli/core/adapters
tags:
  - cs/software-development
  - cs/cli-tools
  - business/collaboration-strategies
  - business/career-strategies
created: 2026-05-23
source: Perplexity export
---

# Faust Step 12 Operator Prompt

## Summary
This note outlines the steps and requirements for Phase 12 of the Faust CLI project, focusing on strengthening the core platform to support future domain agents.

## Key Points
- **Phase 1** involves adding project-awareness tools like `list_project_files` and `search_in_files`.
- **Phase 2** focuses on building foundational scheduling contracts.
- **Phase 3** aims to enhance observability and development profiles.

## Details
### Phase 1 - Project-awareness Tools

1. **Tool Definition**
   - Define `list_project_files` as a plugin in the existing registry system with no approval required.
   - Define `search_in_files` similarly, ensuring safe and deterministic behavior.

2. **Intent Requirements**
   - `list_project_files`: Returns a structured listing of files within approved repo areas.
   - `search_in_files`: Searches text safely inside approved repo areas, returning structured matches.

3. **Boundaries**
   - Read-only only
   - No writes or subprocess execution unless absolutely required and safely wrapped
   - No traversal outside allowed repo boundaries

4. **Graph Behavior**
   - Route file-listing/search intents through `classify_task` and `route_role`.
   - Ensure `tool_call` dispatches these tools as first-class graph operations.

5. **Validation**
   - Run tests: `pytest tests/core/ -v --tb=short`, `pytest tests/adapters/test_graph.py -v --tb=short`
   - Manual smoke tests:
     - `faust loop --task "list the project files under src/faust and summarize the structure"`
     - `faust loop --task "find where approval logic is implemented"`

### Phase 2 - Domain Contracts for Scheduling

1. **Contract Targets**
   - Define minimal contracts: `Course`, `ScheduleBlock`, `Assignment`, `StudentPreference`.

2. **Requirements**
   - Place these contracts in an appropriate core/domain module.
   - Keep the schema minimal and strongly typed, with validation where necessary.

3. **Avoid Overbuilding**
   - Focus on compatibility with Faust’s existing memory model.
   - Do not add speculative features beyond the minimum needed for a narrow future scheduling MVP.

4. **Validation**
   - Add targeted tests: `pytest tests/core/ -v --tb=short`, `pytest tests/ -v --tb=short`.

### Phase 3 - Observability and Development Profile

1. **Visibility Enhancements**
   - Strengthen visibility into Faust’s operations.
   - Ensure the contracts are compatible with existing memory models.

## References
- [Faust CLI Repository](https://github.com/DrManzo/Faust_CLI)

## Related
- [[Faust-Step-11-Operator-Prompt]] — continuity
- [[Faust-Cli-Core-Adapters]] — core-components
