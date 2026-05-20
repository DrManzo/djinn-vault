---
title: "Faust Ollama Integration"
created: 2026-05-19
modified: 2026-05-19
tags: [faust, ollama, langgraph, cli, python, integration, streaming, checkpointing, local-ai]
source: "Perplexity AI Export"
category: "Computer Science/Faust-CLI"
---

## Summary
Step 3 of the Faust project: end-to-end integration of Ollama with the CLI using LangGraph. Covers configuration, adapter implementation, LangGraph graph wiring, CLI command implementation, and manual verification of multi-turn memory and state serialization.

## Key Points
- `configs/default.yaml` defaults to `backend: "ollama"` and `model: "llama3:8b"`
- `OllamaAdapter` implements `generate(messages, stream=True)` calling POST `/api/chat` with streaming
- LangGraph `StateGraph(FaustState)` with `build_prompt` and `llm_node` nodes
- CLI supports `faust`, `faust chat`, `faust run "<prompt>"`, and `faust <prompt...>`
- InMemorySaver with JsonPlusSerializer configured with `allowed_msgpack_modules` for type safety
- Verified: multi-turn memory, JSON object recall, constraint-based reasoning

## Details

### Configuration
```yaml
# configs/default.yaml
backend: "ollama"
model: "llama3:8b"
ollama:
  base_url: "http://localhost:11434"
  request_timeout: 120
openai_compat:
  base_url: "http://localhost:1234/v1"
  api_key: "local"
```

### Config Loading
- `faust/config.py` loads YAML into Pydantic `AppConfig` model
- Exposes: `backend`, `model`, `temperature`, `context_window`, `system_prompt`
- Nested `OllamaSettings` and `OpenAICompatConfig` for backend-specific options

### Core Data Models
- `Role` enum: `SYSTEM`, `USER`, `ASSISTANT`
- `Message`: role, content, timestamp
- `Turn`: user_message, assistant_message
- `Session`: id, model, turns, system_prompt, created_at
- `AppConfig`: full configuration schema
- `FaustState`: shared LangGraph state TypedDict

### Ollama Adapter
```python
# faust/adapters/ollama.py
class OllamaAdapter:
    def generate(self, messages: List[Dict[str, str]], stream: bool = True) -> Iterator[str]:
        # Calls POST /api/chat on local Ollama server via httpx
        # Streams message.content chunks
        # Handles message format conversion (FaustState → Ollama chat format)
```

### LangGraph Wiring
```python
# faust/adapters/graph.py
def build_graph(adapter, config):
    # StateGraph(FaustState)
    # Nodes:
    #   build_prompt: ensures system prompt is present as SYSTEM message
    #   llm_node: converts Message objects to dicts, calls adapter.generate(),
    #             concatenates streamed chunks, returns response + error
    # Checkpointing: InMemorySaver with JsonPlusSerializer
    #   configured with allowed_msgpack_modules for AppConfig, Message, Role
```

### CLI Behavior (Typer)
- `faust` → interactive chat (REPL) with llama3:8b
- `faust chat` → same as above, explicit
- `faust run "<prompt>"` → one-shot prompt, prints response and exits
- `faust <prompt...>` → treated as `faust run "<prompt>"` via root callback

### main.py Wiring
```python
# faust/main.py
# 1. Load config
# 2. Pick adapter (Ollama or stubbed OpenAI-compat)
# 3. Build graph
# 4. Launch Typer app with adapter, config, graph in ctx.obj
```

### Manual Verification Tests
1. **Fact Memory Test**: Three facts (codename, secret number, backend) followed by recall question → Faust answered correctly, confirming multi-turn memory and checkpointing
2. **Structured JSON Recall**: Generated JSON user object and reproduced it character-for-character → confirmed state/serialization round-tripping
3. **Constraint + Design Mapping**: Remembered three architectural constraints and mapped them to design decisions → confirmed longer multi-step reasoning over previous context

### Architecture Compliance
- `core` does NOT import `cli` or `adapters`
- `adapters` may import `core` (e.g., for `FaustState`)
- `cli` may import `core` and `adapters`
- Clean layering enables future agents/model routing without violating constraints

## References
- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md
- Perplexity AI Chat Export (2026-05-19)

## Related
- [[Faust-CLI-Project-Hub]]
- [[Faust Project Setup & Architecture]]
- [[Faust Testing & Test Report]]
- [[Faust-Project-Setup-Architecture]]
- [[AI-Coding-Model-Comparison]]
