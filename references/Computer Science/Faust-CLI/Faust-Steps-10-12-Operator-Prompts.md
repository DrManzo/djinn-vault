---
title: "Faust Steps 10-12 Operator Prompts"
created: 2026-05-19
modified: 2026-05-19
tags: [faust, operator-prompts, cli-polish, self-coding-loop, refactoring, commit-standards, python, langgraph]
source: "Perplexity AI Export"
category: "Computer Science/Faust-CLI"
---

## Summary
Steps 10-12 of the Faust project: CLI polish, supervised self-coding loop implementation, and refactoring based on real usage. Covers stdin handling, exit behavior, persistence gaps, approval-gated test execution, and commit standards.

## Key Points
- Three-phase approach: CLI polish → controlled-loop → refactor (in that order)
- Fix piped stdin exit behavior to eliminate trailing "Aborted." message
- Clean up interactive exit handling for `exit`, `quit`, `/exit`
- Close persistence gap where `faust run` does not persist to checkpoint memory
- Implement supervised self-coding loop with human approval gate
- No execution without explicit approval, no shell injection acceptance
- Strict commit message standards with imperative mood and detailed bodies

## Details

### Phase 1 — CLI Polish and Persistence Cleanup
**Focus**: User-facing reliability and state continuity

**Required Targets:**
- Fix piped stdin path so Faust exits cleanly without trailing `Aborted.` after valid `/exit` or `quit`
- Clean up interactive exit handling so `exit`, `quit`, `/exit` consistently terminate before another model turn
- Review single-shot behavior and close persistence gap where `faust run` does not persist to checkpoint memory
- Preserve all existing working behavior in interactive mode

**Validation:**
- Interactive launch with `faust`
- Piped input: `printf '...\n/exit\n' | faust`
- Clean exit with `quit`
- No regression in existing graph behavior
- Re-run targeted graph suite: `pytest tests/adapters/test_graph.py -v --tb=short`

### Phase 2 — Controlled-Loop Implementation
**Focus**: First supervised self-coding loop for Faust working on Faust

**Required Intent:**
- Faust drafts narrow code changes for its own repo
- Presents proposed code and/or tests for human approval first
- Runs only approved, scoped pytest targets under existing safety gate
- Returns concise execution notes and report paths when tests run

**Safety Boundaries (Non-Negotiable):**
- No execution without explicit approval
- No pytest targets outside `tests/`
- No shell injection acceptance
- No silent production code writes outside approved workflow

### Phase 3 — Refactor After Real Use
**Focus**: Structural cleanup based on observed friction

**Refactor Intent:**
- Refactor based on real friction observed during Step 10 usage
- Prefer structural cleanup that improves readability, testability, role separation
- Do not refactor speculatively
- Keep each refactor atomic and test-backed

### Commit Standards
**Required Format:**
```text
type(scope): short imperative summary

Why this change was needed.
What behavior changed.
What was intentionally not changed.
How it was validated.
```

**Examples:**
```text
fix(cli): handle piped stdin exit cleanly

Catch prompt abort/EOF on exhausted stdin so piped sessions
terminate without the trailing abort message.

Preserves the current interactive quit behavior and does not
change graph routing.

Validated with interactive exit, piped /exit, and graph tests.
```

```text
feat(loop): add approval-gated self-coding control loop

Introduce a supervised control loop that lets Faust draft repo
changes and run only approved scoped tests.

Keeps existing Step 9 safety boundaries intact and does not allow
execution outside validated tests/ targets.

Validated with targeted graph tests and manual CLI smoke checks.
```

**Commit Rules:**
- One logical change per commit
- Subject line in imperative mood
- Keep subject line concise
- Add commit body whenever reason is not obvious from diff
- Avoid vague messages like "update file", "misc fixes", "WIP"

### Working Rules
- Make the smallest safe change first
- After each meaningful change, run the narrowest relevant tests before moving on
- Do not start with refactoring; CLI rough edges must be cleaned up first
- Current graph, routing, memory, and approval-gated test system are stable enough for supervised self-improvement

## References
- Conventional Commits: https://www.conventionalcommits.org/
- Perplexity AI Chat Export (2026-05-19)

## Related
- [[Faust-CLI-Project-Hub]]
- [[Faust Memory Buckets & Role Routing]]
- [[Faust Memory Retrieval]]
- [[Faust-Project-Setup-Architecture]]
- [[Faust-Testing-Test-Report]]
