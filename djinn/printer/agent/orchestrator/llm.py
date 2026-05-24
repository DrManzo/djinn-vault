"""
LLM backend abstraction.

Priority:
  1. Anthropic (Claude) — if ANTHROPIC_API_KEY is set in ~/.config/djinn/claude.env
  2. Ollama phi4:14b  — always available locally (best reasoning model on Salomon)

To activate Claude routing:
  echo "ANTHROPIC_API_KEY=sk-ant-..." >> ~/.config/djinn/claude.env
  chmod 600 ~/.config/djinn/claude.env
"""
import os, pathlib

CLAUDE_ENV  = pathlib.Path.home() / ".config/djinn/claude.env"
CLAUDE_MODEL = "claude-sonnet-4-6"
OLLAMA_DESIGN_MODEL = "phi4:14b"      # best reasoning on Salomon
OLLAMA_CODE_MODEL   = "qwen2.5-coder:7b"  # code generation


def _load_env():
    if CLAUDE_ENV.exists():
        for line in CLAUDE_ENV.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_env()


class LLM:
    def __init__(self, prefer_code: bool = False):
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if key:
            import anthropic as _ant
            self.backend = "anthropic"
            self._client = _ant.Anthropic(api_key=key)
            self.model = CLAUDE_MODEL
        else:
            import ollama as _oll
            self.backend = "ollama"
            self._client = _oll
            self.model = OLLAMA_CODE_MODEL if prefer_code else OLLAMA_DESIGN_MODEL

    def chat(self, system: str, messages: list, max_tokens: int = 4096) -> str:
        if self.backend == "anthropic":
            resp = self._client.messages.create(
                model=self.model,
                system=system,
                messages=messages,
                max_tokens=max_tokens,
            )
            return resp.content[0].text
        else:
            full = [{"role": "system", "content": system}] + messages
            resp = self._client.chat(
                model=self.model,
                messages=full,
                options={"temperature": 0.2, "num_ctx": 8192},
            )
            return resp["message"]["content"]

    @property
    def name(self) -> str:
        return f"{self.backend}/{self.model}"
