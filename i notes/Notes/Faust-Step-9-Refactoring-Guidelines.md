---
subject: business/project-management/modules/roles/faust/cli/core/adapters
tags:
  - business/career-strategies
  - cs/software-engineering
  - personal/productivity
  - topic/project-management
  - context/faust-cli-project
  - relevant/refactoring-guidelines
  - commonality/code-organization
  - specific-step9
created: 2026-05-23
source: Perplexity export
---

# Faust Step 9 Refactoring Guidelines

## Summary
The project context and goals for Faust, a local CLI assistant, are to make it more useful as a human-controlled helper. The focus is on minimal structural cleanup, preserving key behaviors, and adding a narrow tests-only workflow without broad autonomy.

## Key Points
- **Project Context**: Faust is an offline-first CLI assistant with existing functionalities like checkpoint memory, long-term memory, deterministic slot recall, and retrieval of saved facts.
- **Product Direction**: Faust should remain under human control, helping with testing, validation, and reporting but not implementing production code autonomously.
- **Step 9 Goal**: Ensure Faust runs reliably as a local helper that can understand new behavior, propose tests, run approved pytest targets, write reports, and support its own development without directly editing production code.
- **Critical Boundaries**: Faust should not write production code automatically; it may draft tests, revise them, run scoped pytest targets, summarize results, and write report files but must ask for approval before implementation.

## Details
### Refactor Policy
1. **Minimal Structural Cleanup**: Only refactor necessary files to support Step 9 workflow safely.
2. **Preserve Key Behaviors**:
   - Deterministic direct recall of supported slots.
   - Saved-fact retrieval behavior.
   - User scoping and thread separation rules.
3. **Tests-Only Workflow**:
   - Identify when the user is asking for test coverage or a draft.
   - Generate proposed tests or updates as output/state.
   - Limit test targets to explicit files or pytest node IDs under `tests/`.
   - Run only approved/scoped pytest targets.
   - Record pass/fail and execution notes.
   - Write report files for detailed outputs.

### Important Design Constraints
1. Keep the implementation narrow, explicit, and testable.
2. Do not add embeddings, vector search, or broad semantic memory frameworks.
3. Do not build broad agent autonomy.
4. Prefer copy-pasteable, file-by-file changes.
5. Keep tests in the repository and update them as the code evolves.

## References
- [Faust Step 9 Refactoring Guidelines](https://www.skool.com/aianswers)

## Related
- [[Faust-CLI-Project-Hub]] — project context and goals
- [[Faust-Step-8-Retrieval-Layer-Implementation]] — previous step implementation
