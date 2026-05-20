---
title: "Faust Project Setup & Architecture"
created: 2026-05-19
modified: 2026-05-19
tags: [faust, cli, llm, local-ai, python, architecture, langgraph, typer, ollama, component-based-design]
source: "Perplexity AI Export"
category: "Computer Science/Faust-CLI"
---

## Summary
Initial setup and architectural design for Faust, a local offline-first CLI AI assistant. Covers component-based project structure, technology stack selection (Typer, LangGraph, Pydantic, Ollama), import rules, and the decision to use LangGraph over CrewAI for orchestration.

## Key Points
- Component-based architecture separates code into `cli/`, `core/`, `adapters/`, and `agents/`
- Strict import rules enforce dependency hierarchy: cli → core/adapters, adapters → core, core → standard library only
- LangGraph chosen over CrewAI for explicit typed state, conditional edges, checkpointing, and flexible graph shapes
- Three local Ollama models assigned roles: llama3.3:8b (general), deepseek-r1:8b (reasoning), qwen2.5-coder:14b (code)
- Fully offline-first: no cloud API keys, no internet required for inference
- Phase 1: conversational CLI; Phase 2: multi-agent orchestration via LangGraph

## Details

### Project Structure
```
faust/
├── pyproject.toml          # Project metadata, dependencies, entry point
├── Makefile                # Developer shortcuts (install, run, test, lint)
├── README.md               # Project overview and quickstart
├── CHANGELOG.md            # Version history
├── configs/
│   └── default.yaml        # Default runtime configuration
├── docs/
│   ├── architecture.md     # Component responsibilities, data flow, import rules
│   ├── cli-reference.md    # All commands, flags, usage examples
│   ├── adapter-guide.md    # How to implement a new LLM adapter
│   └── config-reference.md # All YAML keys, types, defaults, examples
├── tests/
│   ├── cli/
│   ├── core/
│   └── adapters/
├── src/
│   └── faust/
│       ├── __init__.py     # Package version, public API surface
│       ├── main.py         # Bootstrap: wires components, launches CLI
│       ├── config.py       # Config loader: YAML → validated Pydantic model
│       ├── exceptions.py   # Custom exceptions (FaustError, BackendError, etc.)
│       ├── cli/            # COMPONENT 1 — Interface & Rendering
│       │   ├── app.py      # Typer app instance; registers command groups
│       │   ├── commands/
│       │   │   ├── chat.py # `faust chat` — interactive session
│       │   │   ├── run.py  # `faust run <prompt>` — single-shot inference
│       │   │   └── config.py # `faust config show/set` — manage config
│       │   └── renderer.py # Rich-based output: streaming tokens, banners, errors
│       ├── core/           # COMPONENT 2 — Business Logic & Data Models
│       │   ├── models.py   # Pydantic models: Message, Turn, Session, AppConfig
│       │   ├── session.py  # Session lifecycle: init, append, reset, export
│       │   ├── context.py  # Context window management: trim, count tokens, slice
│       │   └── prompt.py   # Prompt builder: system prompt, history injection
│       ├── adapters/       # COMPONENT 3 — LLM Backend Implementations
│       │   ├── base.py     # Abstract base class: LLMAdapter contract
│       │   ├── ollama.py   # Ollama local backend (streaming via ollama-python)
│       │   └── openai_compat.py # OpenAI-compatible API (LM Studio, vLLM, etc.)
│       └── agents/         # COMPONENT 4 — Future Multi-Agent System
│           └── __init__.py # Placeholder for Phase 2
└── data/                   # Planned: SQLite DB, session exports
```

### Component Responsibilities

#### `cli/` — Interface & Rendering
- Everything the user sees and touches
- Parses commands, renders streamed output, displays errors, shows help text
- **Only** component allowed to import from `core/` and `adapters/`
- Top of the dependency chain
- Must NOT be imported by `core/` or `adapters/`

#### `core/` — Business Logic & Data Models
- The brain of the program
- Defines what a conversation *is* (data models)
- Manages session state, context window, prompt construction
- **Backend-agnostic**: never calls Ollama, never makes HTTP requests, never reads from disk
- May only import standard library and other core modules

#### `adapters/` — LLM Backend Implementations
- Concrete implementations of LLM backends
- `OllamaAdapter`: local Ollama backend with streaming
- `OpenAICompatAdapter`: OpenAI-compatible API (LM Studio, vLLM, etc.)
- May import from `core/` (e.g., for `FaustState`)
- Must NOT import from `cli/`

#### `agents/` — Future Multi-Agent System (Phase 2)
- Placeholder for multi-agent orchestration
- May import from `core/` and `adapters/`
- `core/` and `adapters/` must NOT import from `agents/`

### Technology Stack
- **Python**: Primary language (3.14+)
- **Typer**: CLI framework with automatic help generation
- **LangGraph**: Orchestration layer with explicit typed state, conditional edges, checkpointing
- **Pydantic v2**: Data validation and settings management
- **Rich**: Terminal UI for streaming tokens, banners, errors
- **httpx**: Async HTTP client for adapter implementations
- **PyYAML**: Configuration file parsing
- **Ollama**: Local LLM runtime

### Model Roles
| Model | Role | Strengths | VRAM |
|-------|------|-----------|------|
| llama3.3:8b | General brain | Instruction-following, general chat, Q&A | 8 GB |
| deepseek-r1:8b | Reasoner | Reasoning, explicit chain-of-thought, planning, teaching | 8 GB |
| qwen2.5-coder:14b | Coder | Code generation, explanation, debugging | 16 GB |

### LangGraph vs CrewAI Decision
**CrewAI Downsides:**
- Opaque state, difficult branching, harder testing/debugging
- Extra prompt overhead, less natural support for loops and complex flows

**LangGraph Advantages:**
- Explicit typed state (`FaustState` as `TypedDict`)
- Conditional edges → easy model and agent routing
- Checkpointing/replay for step-by-step inspection
- Flexible graph shapes (sequential, branching, loops)
- Production use and documented best practices

### Import Rules
- ✅ `cli/` may import from: `core/`, `adapters/`, `config.py`, `exceptions.py`
- ❌ `cli/` must NOT be imported by: `core/`, `adapters/`
- ✅ `adapters/` may import from: `core/`
- ❌ `adapters/` must NOT import from: `cli/`, `agents/`
- ✅ `core/` may import from: standard library, other core modules
- ❌ `core/` must NOT import from: `cli/`, `adapters/`, `agents/`
- ✅ `agents/` may import from: `core/`, `adapters/`
- ❌ `core/`, `adapters/` must NOT import from: `agents/`

### LangGraph Node Contract
- Each node takes `FaustState` as input
- Returns a partial dict of updates
- LangGraph merges updates into existing state
- Nodes: `build_prompt` → `llm`

## References
- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- Typer Documentation: https://typer.tiangolo.com/
- Perplexity AI Chat Export (2026-05-19)

## Related
- [[Faust-CLI-Project-Hub]]
- [[Faust Ollama Integration]]
- [[Faust Long-Term Memory Foundation]]
- [[Faust-Long-Term-Memory-Foundation]]
- [[Faust-CLI-Project]]
- [[OpenClaw-Project-Architecture]]
