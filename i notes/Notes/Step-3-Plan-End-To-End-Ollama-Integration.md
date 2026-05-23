---
subject: business/project-management/modules/roles/faust/cli/core/adapters
tags:
  - business/technology/integration
  - cs/software-engineering
  - cs/api-integration
  - business/career-strategies
created: 2026-05-23
source: Perplexity export
---

# Step 3 Plan: End-to-End Ollama Integration for Faust CLI

## Summary
This note outlines the steps to integrate `llama3:8b` via the OllamaAdapter into the Faust CLI, ensuring a functional `faust run "..."` and `faust chat` experience.

## Key Points
- **Task 1:** Configure default backend and model in `configs/default.yaml`.
- **Task 2:** Refine adapter interface for LangGraph compatibility.
- **Task 3:** Validate LangGraph graph wiring.

## Details

### Task 1: Configure Default Backend and Model
**File:** `configs/default.yaml`
**Changes:**
- Set `backend: ollama`
- Set `model: llama3:8b`
- Add Ollama-specific config (if needed): `ollama_base_url: http://localhost:11434`

**Behavior:** Ensures Faust uses Ollama with `llama3:8b` as the default model when no override is provided.
**Test:** Verify config loader reads these values correctly (unit test in `test_config_loader.py`).

### Task 2: Refine Adapter Interface for LangGraph Compatibility
**File:** `src/faust/adapters/ollama.py` (create if missing)
**Changes:**
- Implement `OllamaAdapter` class conforming to the adapter interface expected by LangGraph graph.
- Key method:
  - `generate(messages: List[Dict[str, str]], stream: bool = True) -> Iterator[str]`
    - For streaming: call Ollama `/api/chat` endpoint with `stream=True`, yield content chunks.
    - For non-streaming: aggregate chunks and return full response (used internally by graph if needed).
- Handle message format conversion (FaustState → Ollama chat format).

**Behavior:** Adapter correctly interacts with the local Ollama instance to stream tokens from `llama3:8b`.
**Test:**
- Unit test: Mock Ollama HTTP requests, validate chunk iteration and error handling (`test_ollama_adapter.py`).
- Integration test: Spin up a real Ollama instance (via fixture), confirm adapter streams response (`test_ollama_integration.py`).

### Task 3: Validate LangGraph Graph Wiring
**File:** `src/faust/adapters/graph.py` (inspect; likely no changes needed if interface is correct)
**Changes:**
- Confirm `build_prompt` node constructs message list from `FaustState` (e.g., combines system prompt, history, user input).
- Confirm `llm` node calls `adapter.generate(messages, stream=True)` and yields tokens to update state.
- Ensure graph compiles with `SqliteSaver.from_conn_string("data/faust.db")`.

**Behavior:** Graph correctly routes state through prompt construction → LLM streaming → state update.
**Test:**
- Unit test: Mock adapter, verify graph executes nodes in sequence and updates state (`test_graph_flow.py`).
- Integration test: Use a real OllamaAdapter to confirm the flow.

## References
- [Faust CLI Project Repository](https://github.com/DrManzo/Faust_CLI)
- [Ollama Adapter Implementation](src/faust/adapters/ollama.py)

## Related
- [[Faust-Ollama-Integration]] — integration details
- [[Faust-Project-Setup-Architecture]] — project setup context
