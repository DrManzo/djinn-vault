---
subject: business/management-methods/faust-cli-step-11/operator-prompt
tags:
  - cs/software-development
  - cs/testing/unit-testing
  - cs/cli-tools
  - business/career-strategies
created: 2026-05-23
source: Perplexity export
---

# Faust Step 11 Operator Prompt

## Summary
This note outlines the steps for Phase 1 of Faust CLI development, focusing on agent-level unit tests. It also provides guidance for future phases including an edit-and-propose cycle and a plugin/tool registry.

## Key Points
- **Agent-level Unit Tests**
  - Fill `tests/agents/` with isolated unit tests.
  - Required nodes: `assistant`, `reasoner`, `coder`, `test_proposer`, `memory_writer`.
  - Each test must stub the LLM adapter, assert on state fields, and be fully isolated.

- **faust loop Edit-and-Propose Cycle**
  - Extend `faust loop` to propose real code changes.
  - Show a unified diff before writing any files.
  - Run approved tests after file write; reject proposals if tests fail.

- **Plugin/Tool Registry**
  - Introduce a `PluginRegistry` in `src/faust/core/plugins.py`.
  - Define initial tools: `read_file`, `run_pytest`.

## Details
### Phase 1 — Agent-level Unit Tests

Fill the `tests/agents/` directory with isolated unit tests for each agent node:

- **assistant**:
  - Responds to general Q&A input.
  - Assertions on response, state fields like `active_agent`.
  
- **reasoner**:
  - Produces step-by-step output on planning input.
  - Assertions on response and intent.

- **coder**:
  - Generates code and sets `test_approved` correctly.
  - Assertions on response, state fields.

- **test_proposer**:
  - Drafts a proposal without calling `subprocess.run`.
  - Assertions on test proposal and approval flag.

- **memory_writer**:
  - Writes a slot to the memory store.
  - Assertions on slot writing.

### Phase 2 — faust loop Edit-and-Propose Cycle

Extend `faust loop` so it can propose real code changes:

- Draft narrow code changes and render unified diffs in the proposal panel.
- Show diffs before any file writes; write only after explicit approval.
- Run approved tests, discard proposals on rejection.

### Phase 3 — Plugin/Tool Registry

Introduce a `PluginRegistry` for first-class graph operations:

- Define built-in tools: `read_file`, `run_pytest`.
- Add a `tool_call` node to dispatch to registered plugins.
- Route through existing validation gates.

## References
- [Faust CLI Step 11 Operator Prompt](https://www.perplexity.ai/search/0296de04-cc38-42d9-bd67-b64d7067f929)

## Related
- [[Faust-Step-10-Operator-Prompt]] — similarity
- [[Faust-Cli-Core-Adapters]] — adapter-pattern
