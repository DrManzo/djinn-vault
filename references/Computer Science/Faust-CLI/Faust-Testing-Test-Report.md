---
title: "Faust Testing & Test Report"
created: 2026-05-19
modified: 2026-05-19
tags: [faust, testing, pytest, python, unit-tests, integration-tests, test-report, cli-testing]
source: "Perplexity AI Export"
category: "Computer Science/Faust-CLI"
---

## Summary
Step 4 of the Faust project: automated testing setup and test report generation. Covers pytest configuration, test layout for config, models, adapters, graph, and CLI, plus a script to run tests and generate a markdown test report.

## Key Points
- pytest setup with structured test layout matching component architecture
- Unit tests for config loading, model serialization, adapter mocking
- Graph tests using FakeAdapter to verify node behavior without external dependencies
- CLI tests using Typer's CliRunner for command invocation testing
- Test report generation script outputs markdown summary to `reports/test-report.md`
- Integration tests marked optional in CI to avoid requiring live Ollama instance

## Details

### Test Layout
```
tests/
├── cli/
│   ├── test_chat_command.py    # faust chat with fake adapter
│   └── test_run_command.py     # faust run "..." and faust "..."
├── core/
│   ├── test_config.py          # AppConfig + loader
│   └── test_models.py          # Message.to_dict, FaustState shape
└── adapters/
    ├── test_ollama_adapter.py  # Mocked httpx requests
    ├── test_graph_flow.py      # FakeAdapter verifies node sequence
    └── test_architecture.py    # Import rule enforcement
```

### Test Categories

#### Unit Tests
- **Config**: Verify config loader reads YAML values correctly
- **Models**: Test `Message.to_dict()`, `FaustState` structure
- **Adapter**: Mock Ollama HTTP requests, validate chunk iteration and error handling
- **Graph**: Mock adapter, verify graph executes nodes in sequence and updates state

#### Integration Tests
- **Ollama Adapter**: Spin up real Ollama instance, confirm adapter streams response
- **Graph Integration**: Use real OllamaAdapter, run graph with sample input, check state evolution
- **CLI Commands**: Real Ollama, verify commands return non-empty responses

#### Architecture Tests
- Import linting to enforce dependency rules
- Verify `OllamaAdapter` subclasses `BaseLLMAdapter`
- Ensure `core` does not import `cli` or `adapters`

### Test Report Generation
- Script or Make target runs full test suite
- Outputs markdown summary to `reports/test-report.md`
- Includes pass/fail counts, failure details, and coverage metrics

### Key Testing Patterns
- **CliRunner**: Typer's test utility for invoking commands with mocked I/O
- **FakeAdapter**: Mock adapter for graph testing without external dependencies
- **httpx mocking**: Intercept HTTP requests to Ollama API for unit tests
- **Integration markers**: `@pytest.mark.integration` for tests requiring live Ollama

### Testing Strategy
- Mock external dependencies (Ollama HTTP) for unit tests
- Use real Ollama for critical integration tests (marked optional in CI)
- Fast feedback loop: unit tests run on every commit
- Integration tests run on demand or in nightly CI

## References
- pytest Documentation: https://docs.pytest.org/
- Typer Testing: https://typer.tiangolo.com/tutorial/testing/
- Perplexity AI Chat Export (2026-05-19)

## Related
- [[Faust-CLI-Project-Hub]]
- [[Faust Ollama Integration]]
- [[Faust Long-Term Memory Foundation]]
- [[Faust-Project-Setup-Architecture]]
- [[Faust-Steps-10-12-Operator-Prompts]]
