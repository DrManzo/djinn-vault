---
subject: business/management-methods/faust-cli-step-10
tags:
  - cs/software-development
  - cs/testing
  - cs/refactoring
  - cs/cli-tools
created: 2026-05-23
source: Perplexity export
---

# Faust Step 10 Operator Prompt

## Summary
This note outlines the steps and requirements for completing Phase 1, Phase 2, and Phase 3 of Faust's development. The focus is on CLI polish, controlled-loop implementation, and refactor after real use.

## Key Points
- **Phase 1 — CLI Polish and Persistence Cleanup**
  - Fix piped stdin path to ensure clean exit.
  - Clean up interactive exit handling.
  - Review single-shot behavior and close known persistence gaps.
  - Preserve existing working behavior in interactive mode.
  
- **Phase 2 — Controlled-loop Implementation**
  - Faust should draft narrow code changes for its own repo.
  - Present proposed code and tests for human approval first.
  - Run only approved, scoped pytest targets under safety gate.
  - Keep Javier and Marcus in the approval loop.

- **Phase 3 — Refactor After Real Use**
  - Refactor based on real friction observed during Step 10 usage.
  - Prefer structural cleanup that improves readability, testability, and role separation.
  - Do not refactor speculatively.
  - Keep each refactor atomic and test-backed.

## Details
The development process for Faust is structured into three phases to ensure stability and controlled self-improvement. Phase 1 focuses on cleaning up the CLI behavior, ensuring reliable user interaction and state persistence. Phase 2 introduces a supervised control loop where Faust can draft code changes and run approved tests. Finally, Phase 3 involves refactoring based on real usage feedback.

### Phase 1 — CLI Polish and Persistence Cleanup
- **Fix piped stdin path**: Ensure that Faust exits cleanly without trailing `Aborted.` behavior after valid `/exit` or `quit` handling.
- **Clean up interactive exit handling**: Make sure `exit`, `quit`, and `/exit` consistently terminate before another model turn is attempted.
- **Review single-shot behavior**: Address the known persistence gap where `faust run` does not persist to checkpoint memory.
- **Preserve existing working behavior**: Ensure no regression in existing graph behavior.

### Phase 2 — Controlled-loop Implementation
- **Draft narrow code changes**: Faust should be able to draft code for its own repository.
- **Human approval first**: Present proposed code and tests for human approval before execution.
- **Run approved, scoped pytest targets**: Only execute approved, targeted pytest tests under the existing safety gate.
- **Approval loop**: Keep Javier and Marcus in the approval loop for every production change.

### Phase 3 — Refactor After Real Use
- **Real friction observed**: Refactor based on actual usage feedback during Step 10.
- **Structural cleanup**: Focus on improving readability, testability, and role separation.
- **No speculative refactoring**: Avoid making changes without clear justification or observed issues.
- **Atomic commits**: Ensure each refactor is a single, atomic change with proper testing.

### Commit Rules
- Each commit must be well commented and professionally structured.
- Use one logical change per commit.
- Write the subject line in imperative mood (e.g., `fix(cli): handle piped stdin exit cleanly`).
- Explain why the change was made, what behavior changed, and what was intentionally left unchanged.

### Working Rules
- Make the smallest safe change first.
- Run narrowest relevant tests after each meaningful change.
- Do not bundle CLI cleanup and controlled-loop work into one commit.
- Preserve existing documented positioning of Faust as a local-first, graph-routed, memory-aware, approval-gated AI CLI.

## References
- [Faust Step 10 Operator Prompt](https://www.perplexity.ai/search/df22fc61-04f3-4a04-99f1-d71ad523935a)

## Related
- [[Faust-Steps-10-12-Operator-Prompts]] — similarity
- [[Faust-Step-9-Refactoring-Guidelines]] — refactoring-guidelines
