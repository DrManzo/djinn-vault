---
subject: business/project-management/modules/roles/faust/cli/core/adapters
tags:
  - cs/software-engineering
  - cs/architecture/design
  - business/technology/startup
  - ai/models/integration
created: 2026-05-23
source: Perplexity export
---

# Faust CLI Core Adapters

## Summary
The note covers the architecture and design decisions of the Faust project, focusing on its core components including adapters for different AI models.

## Key Points
- **Project Vision**: Faust is a local, offline-first command-line AI assistant.
- **Architecture Decisions**:
  - **High-Level Structure**: Component-based structure with specific directories for configurations and tests.
  - **Components**:
    - `cli/`: Interface & rendering.
    - `core/`: Business logic & data models.
    - `adapters/`: LLM backends & graph.
- **LangGraph vs CrewAI**: LangGraph is chosen over CrewAI due to explicit state, easier testing and debugging, and support for complex flows.
- **Model Strategy**:
  - Three local models via Ollama: `llama3.3:8b`, `deepseek-r1:8b`, and `qwen2.5-coder:14b`.
  - Phase 1: Manual model selection; Phase 2: Router node decides the appropriate model.
- **Storage and Persistence Plan**:
  - SQLite + LangGraph SqliteSaver for graph state and checkpoints.
  - JSON session exports for debugging.

## Details
The Faust project is structured to be a local, offline-first command-line AI assistant. It runs entirely on the user's machine without requiring cloud services or API keys. The architecture is component-based with specific directories dedicated to configurations, tests, core logic, and adapters. 

### High-Level Structure
- **Project Root**:
  - `pyproject.toml`: Python package configuration and Faust CLI entry point.
  - `Makefile`: Build commands for installation, running, testing, and linting.
  - `configs/default.yaml`: Configuration settings including model, backend, temperature, context window, system prompt.
  - `docs/`: Documentation for architecture, CLI reference, adapter guide, and config reference.
  - `tests/`: Unit test skeletons for core, CLI, adapters.
- **Core Directory**:
  - `__init__.py`: Version and package metadata.
  - `main.py`: Bootstrap script to load configuration, choose adapter, build LangGraph graph, and start the Typer CLI.
  - `config.py`: YAML loader for AppConfig.
  - `exceptions.py`: FaustError hierarchy.
- **CLI Directory**:
  - `app.py`: Typer root app that registers chat, run, config commands.
  - `renderer.py`: All Rich console output.
  - `commands/chat.py`: Interactive loop for the faust chat command.
  - `commands/run.py`: Single-shot call with "faust run <prompt>".
  - `commands/config.py`: Show and set configuration options.

### LangGraph vs CrewAI
LangGraph is chosen over CrewAI due to its explicit state, easier testing and debugging capabilities, and better support for complex flows. LangGraph uses a typed state (FaustState as TypedDict) with conditional edges for easy model and agent routing, checkpointing/replay for step-by-step inspection, and flexible graph shapes.

### Model Strategy
Three local models via Ollama are defined:
- **llama3.3:8b**: General brain; instruction-following, general chat, Q&A.
- **deepseek-r1:8b**: Reasoner; reasoning and explicit chain-of-thought for planning and teaching.
- **qwen2.5-coder:14b**: Code specialist; code generation, review, and explanation.

In Phase 1, models are manually selected using `faust config set model <model_name>`. In Phase 2, a router node in LangGraph will decide which model to use based on the request type (general vs reasoning vs code).

### Storage and Persistence Plan
- **State Management**: SQLite + LangGraph SqliteSaver for graph state and checkpoints.
- **Session Exports**: JSON session exports for teaching and debugging.

## References
- [Faust CLI Core Adapters](/spaces/faust-final-j_w3HlbtSFKHsjBnuMyJAg)

TAG RULES:
- topic MUST be one of: psychology, law, business, cs, personal, creative
- path: topic/context/relevant/commonality/specific-tag
- 2-4 tags per note, use hyphens not spaces
- You may create new nodes at context level and below
- Existing vault tags for reference: bio.libretexts.org/Bookshelves/Introductory_and_General_Biology/General_Biology_, bio/neuroscience/executive-functions, bio/neuroscience/memories, biology/cell-biology/mitosis, biology/conception, biology/neuroscience/brain-pathways, biology/neuroscience/cerebellum, biology/neuroscience/motor-control, biology/neuroscience/symptoms, business/career-strategies, business/human-resources, business/leadership/critical-thinking, business/llc-formation/california/software-development-company, business/management-methods, business/marketing-revenue-models, business/marketing-revenue-models/toy-industry, business/passive-income-strategies/neuro-architecture-assets, business/passive-income-strategies/power-user-bluebeam-market, business/project-management, business/project-management/data-models/faust/core/models, business/project-management/modules/roles/faust/cli/core/adapters, business/project-management/tasks/results/faust/chat, business/strategic-planning, career/career-factors/growth-opportunities, career/career-factors/income-stability, career/career-factors/job-security, career/career-factors/personality-fit, career/career-factors/work-life-balance, caregiving-support/adult-development, caregiving-support/adult-development/loss-of-autonomy, caregiving-support/postpartum-period, child-psychology/cognitive-development/piaget, child-psychology/community-resources, child-psychology/developmental-neonatology, child-psychology/developmental-neonatology/disability-awareness, child-psychology/developmental-tools, commonality/memory-classification, commonality/reconstructive-memory, commonality/research-findings, creative/presentation-skills

## Related
- [[Faust-Project-Setup-Architecture]] — similarity
- [[Faust-Component-Based-Architecture-Specification]] — similarity
- [[Faust-Ollama-Integration]] — integration strategy
