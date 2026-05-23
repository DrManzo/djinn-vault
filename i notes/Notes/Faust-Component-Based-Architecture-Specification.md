---
subject: business/project-management/modules/roles
tags:
  - business/project-management/modules/roles/faust/cli/core/adapters
created: 2026-05-23
source: Perplexity export
---

# Faust — Component-Based Architecture Specification

## Summary
The architecture of the Faust CLI LLM Local AI is organized by component, with `cli`, `core`, and `adapters` each handling distinct aspects of the program. This separation ensures that changes in one area do not affect others.

## Key Points
- **Component Separation**: The codebase is divided into three main components: `cli/`, `core/`, and `adapters/`.
  - **`cli/`**: Handles user interface, command parsing, rendering output.
  - **`core/`**: Manages chat logic and data models.
  - **`adapters/`**: Implements LLM backends.

## Details
The architecture is designed to be modular and maintainable. Each component has a specific responsibility:
- **`cli/`** changes when the user interface or rendering changes (new commands, flags).
- **`core/`** changes when chat logic or data models change.
- **`adapters/`** changes when new LLM backends are added.

### Full Directory Layout
```plaintext
faust/
│
├── pyproject.toml # Project metadata, dependencies, entry point
├── Makefile # Developer shortcuts
├── README.md # Project overview and quickstart
├── CHANGELOG.md # Version history
│
├── configs/
│ └── default.yaml # Default runtime configuration
│
├── docs/
│ ├── architecture.md # Component responsibilities, data flow, import rules
│ ├── cli-reference.md # All commands, flags, and usage examples
│ ├── adapter-guide.md # How to implement a new LLM adapter
│ └── config-reference.md # All YAML keys, types, defaults, and examples
│
├── tests/
│ ├── cli/
│ │ └── test_commands.py
│ ├── core/
│ │ ├── test_session.py
│ │ └── test_prompt.py
│ └── adapters/
│ └── test_ollama.py
│
└── src/
 └── faust/
 ├── __init__.py # Package version, public API surface
 ├── main.py # Bootstrap: wires components, launches CLI
 ├── config.py # Config loader: YAML → validated Pydantic model
 ├── exceptions.py # All custom exceptions (FaustError, BackendError, etc.)
 │
 ├── cli/ # COMPONENT 1 — Interface & Rendering
 │ ├── __init__.py
 │ ├── app.py # Typer app instance; registers all command groups
 │ ├── commands/
 │ │ ├── __init__.py
 │ │ ├── chat.py # `faust chat` — starts interactive session
 │ │ ├── run.py # `faust run <prompt>` — single-shot inference
 │ │ └── config.py # `faust config show/set` — manage config from CLI
 │ └── renderer.py # Rich-based output: streaming tokens, banners, errors
 │
 ├── core/ # COMPONENT 2 — Business Logic & Data Models
 │ ├── __init__.py
 │ ├── models.py # Pydantic models: Message, Turn, Session, AppConfig
 │ ├── session.py # Session lifecycle: init, append turn, reset, export
 │ ├── context.py # Context window management: trim, count tokens, slice
 │ └── prompt.py # Prompt builder: system prompt, history injection
 │
 └── adapters/ # COMPONENT 3 — LLM Backend Implementations
 ├── __init__.py
 ├── base.py # Abstract base class: LLMAdapter (the contract)
 ├── ollama.py # Ollama local backend (streaming via ollama-python)
 └── openai_compat.py # OpenAI-compatible API (LM Studio, vLLM, etc.)
```

### Component 1 — `cli/`
- **Responsibility**: Everything the user sees and touches.
- **Files**:
  - **`app.py`**: Typer application root. Registers command groups from `cli/commands/`.
  - **`chat.py`**: Handles interactive loop for `faust chat`.
  - **`run.py`**: Handles single-shot inference calls with `faust run <prompt>`.
  - **`config.py`**: Manages configuration settings.

### Component 2 — `core/`
- **Responsibility**: Business logic and data models.
- **Files**:
  - **`models.py`**: Pydantic models for messages, turns, sessions, app config.
  - **`session.py`**: Session lifecycle management.
  - **`context.py`**: Context window management.
  - **`prompt.py`**: Prompt builder.

### Component 3 — `adapters/`
- **Responsibility**: LLM backend implementations.
- **Files**:
  - **`base.py`**: Abstract base class for adapters (LLMAdapter).
  - **`ollama.py`**: Ollama local backend implementation.
  - **`openai_compat.py`**: OpenAI-compatible API.

## References
- [Perplexity](https://www.perplexity.ai/search/aa2a035c-eed1-408b-84b4-0848e9f685c5)

## Related
- [[Faust-Final]] — Detailed final architecture and documentation for Faust CLI LLM Local AI.
- [[Project-Management-Strategies]] — General strategies for project management in software development.