---
title: "Faust CLI Project Hub"
created: 2026-05-19
modified: 2026-05-19
tags: [faust, cli, llm, local-ai, python, project-hub, langgraph, typer, ollama, multi-agent]
source: "Perplexity AI Exports"
category: "Computer Science/Faust-CLI"
---

## Summary
Central reference hub for the Faust CLI AI assistant project. Faust is a local, offline-first command-line AI assistant built with Python, Typer, LangGraph, and Ollama. This hub organizes all development steps from initial architecture through operator prompts.

## Project Overview
- **Repository**: DrManzo/Faust_CLI
- **Goal**: Local CLI AI assistant running entirely on user's machine
- **Phase 1**: Clean conversational CLI using local LLMs
- **Phase 2**: Multi-agent system orchestrated by LangGraph
- **Tech Stack**: Python, Typer, LangGraph, Pydantic v2, Rich, httpx, PyYAML, Ollama

## Development Steps

### Foundation
- [[Faust Project Setup & Architecture]] — Component-based architecture, import rules, technology stack selection, LangGraph vs CrewAI decision, model role assignments

### Core Integration
- [[Faust Ollama Integration]] — End-to-end Ollama integration, LangGraph graph wiring, CLI commands, manual verification of multi-turn memory

### Testing
- [[Faust Testing & Test Report]] — pytest setup, test layout, unit/integration/architecture tests, test report generation

### Memory System
- [[Faust Long-Term Memory Foundation]] — LangGraph store abstraction, memory schema, user-scoped namespaces, slot-based memory handling
- [[Faust Memory Router]] — Deterministic recall routing, implicit memory writes, correction-aware slot overwrites, intent-based classification
- [[Faust Memory Buckets & Role Routing]] — Memory bucket classification (checkpoint/long-term/ephemeral), multi-model role routing (assistant/reasoner/coder)
- [[Faust Memory Retrieval]] — Search over stored memories, ranking/filtering, prompt injection, cross-thread verification

### Polish & Automation
- [[Faust Steps 10-12 Operator Prompts]] — CLI polish, supervised self-coding loop, refactoring standards, commit message conventions

### Strategic Decisions
- [[Faust Open Claude Consideration]] — Multi-LLM workflow design, Claude as co-worker, OpenClaw platform evaluation

## Architecture Summary
```
faust/
├── cli/          # Interface & Rendering (Typer, Rich)
├── core/         # Business Logic & Data Models (Pydantic)
├── adapters/     # LLM Backend Implementations (Ollama, OpenAI-compat)
└── agents/       # Future Multi-Agent System (LangGraph)
```

### Import Rules
- `cli/` → `core/`, `adapters/` (top of dependency chain)
- `adapters/` → `core/` only
- `core/` → standard library only
- `agents/` → `core/`, `adapters/`

### Memory Architecture
| Type | Scope | Storage |
|------|-------|---------|
| Checkpoint | Thread ID | InMemorySaver/SqliteSaver |
| Long-term | User ID | InMemoryStore/SqliteStore |
| Ephemeral | Turn only | FaustState fields |

### Model Roles
| Model | Role | Purpose |
|-------|------|---------|
| llama3.3:8b | General | Chat, Q&A, instruction-following |
| deepseek-r1:8b | Reasoner | Planning, chain-of-thought, teaching |
| qwen2.5-coder:14b | Coder | Code generation, debugging, test selection |

## Cross-References
- All steps follow incremental, test-backed development
- Memory system builds layer by layer: foundation → router → buckets → retrieval
- CLI polish and safety gates prioritized before self-coding automation
- Multi-LLM workflow (Claude + Perplexity) complements Faust's local architecture

## Tags
`#faust` `#cli` `#llm` `#local-ai` `#python` `#project-hub` `#langgraph` `#typer` `#ollama` `#multi-agent`
