"""
djinn/core/llm.py
─────────────────────────────────────────────────────────────────────────────
Global LLM client for the entire Djinn platform.

PURPOSE
    Single import point for all Djinn tools, agents, and services.
    No module should instantiate its own LLM client. Import from here.

USAGE
    from djinn.core.llm import get_client, get_model, chat

    # Simple one-shot call
    reply = chat("Summarize this: ...")

    # Full control
    client = get_client()
    model  = get_model()
    resp   = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Hello"}]
    )

BACKENDS
    ┌─────────────┬──────────────────────────────────────────────────────────┐
    │ Backend     │ When active                                              │
    ├─────────────┼──────────────────────────────────────────────────────────┤
    │ Ollama      │ Default. DJINN_USE_GROQ is unset or "0"                  │
    │ Groq        │ DJINN_USE_GROQ=1 + GROQ_API_KEY set                      │
    └─────────────┴──────────────────────────────────────────────────────────┘

ENV VARS
    DJINN_USE_GROQ    "1" to route all calls to Groq, "0" or unset = Ollama
    GROQ_API_KEY      Required when DJINN_USE_GROQ=1
    DJINN_MODEL       Override the default model for current backend
    OLLAMA_BASE_URL   Override Ollama endpoint (default: http://localhost:11434/v1)
    DJINN_TIMEOUT     Request timeout in seconds (default: 120)
    DJINN_TEMPERATURE Default temperature (default: 0.7)
    DJINN_MAX_TOKENS  Default max tokens (default: 2048)

DEFAULT MODELS
    Ollama  →  qwen2.5:7b          (fast, good for most tasks on Salomon)
    Groq    →  llama-3.3-70b-versatile  (best quality, near-instant via Groq)

ADDING A BACKEND
    1. Add a new branch in _build_client() below
    2. Add its default model in _default_model()
    3. Document it in this docstring

Written by Marcus (Claude), 2026-06-06
"""

import os
import sys
from openai import OpenAI
from typing import Optional


# ─── Constants ────────────────────────────────────────────────────────────────

_OLLAMA_DEFAULT_URL   = "http://localhost:11434/v1"
_OLLAMA_DEFAULT_MODEL = "qwen2.5:7b"

_GROQ_BASE_URL        = "https://api.groq.com/openai/v1"
_GROQ_DEFAULT_MODEL   = "llama-3.3-70b-versatile"

_DEFAULT_TIMEOUT      = 120
_DEFAULT_TEMPERATURE  = 0.7
_DEFAULT_MAX_TOKENS   = 2048


# ─── Backend detection ────────────────────────────────────────────────────────

def _use_groq() -> bool:
    """Return True if Groq backend is requested and a key is available."""
    return (
        os.environ.get("DJINN_USE_GROQ", "0").strip() == "1"
        and bool(os.environ.get("GROQ_API_KEY", "").strip())
    )


def _default_model() -> str:
    """Return the default model for the active backend."""
    if _use_groq():
        return _GROQ_DEFAULT_MODEL
    return _OLLAMA_DEFAULT_MODEL


# ─── Client factory ───────────────────────────────────────────────────────────

def _build_client() -> OpenAI:
    """Instantiate and return an OpenAI-compatible client for the active backend."""
    if _use_groq():
        api_key = os.environ["GROQ_API_KEY"]
        return OpenAI(
            api_key=api_key,
            base_url=_GROQ_BASE_URL,
            timeout=int(os.environ.get("DJINN_TIMEOUT", _DEFAULT_TIMEOUT)),
        )

    # Ollama (default)
    base_url = os.environ.get("OLLAMA_BASE_URL", _OLLAMA_DEFAULT_URL)
    return OpenAI(
        api_key="ollama",          # Ollama ignores this but the SDK requires it
        base_url=base_url,
        timeout=int(os.environ.get("DJINN_TIMEOUT", _DEFAULT_TIMEOUT)),
    )


# Module-level singleton — rebuilt only when env changes would matter.
# Use get_client() rather than importing _client directly.
_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    """
    Return the platform-level LLM client (singleton).

    The client is created once per process. If you need to switch backends
    within the same process (rare), call reset_client() first.
    """
    global _client
    if _client is None:
        _client = _build_client()
    return _client


def reset_client() -> None:
    """Force recreation of the client on the next get_client() call."""
    global _client
    _client = None


# ─── Model accessor ───────────────────────────────────────────────────────────

def get_model() -> str:
    """
    Return the model name for the active backend.

    Respects DJINN_MODEL env var override, otherwise returns backend default.
    """
    return os.environ.get("DJINN_MODEL", _default_model()).strip()


# ─── Backend info ─────────────────────────────────────────────────────────────

def get_backend() -> str:
    """Return a human-readable string identifying the active backend."""
    if _use_groq():
        return f"groq:{get_model()}"
    base = os.environ.get("OLLAMA_BASE_URL", _OLLAMA_DEFAULT_URL)
    return f"ollama:{get_model()} @ {base}"


# ─── Convenience wrapper ──────────────────────────────────────────────────────

def chat(
    prompt: str,
    system: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    messages: Optional[list] = None,
) -> str:
    """
    One-shot chat completion. Returns the assistant's reply as a string.

    Args:
        prompt:      User message (required unless you pass `messages` directly).
        system:      Optional system prompt prepended to the conversation.
        model:       Override the active model for this call only.
        temperature: Sampling temperature (default: DJINN_TEMPERATURE or 0.7).
        max_tokens:  Max output tokens (default: DJINN_MAX_TOKENS or 2048).
        messages:    Full message list override — ignores `prompt` and `system`
                     if provided. Useful for multi-turn context passing.

    Returns:
        str: The assistant reply content.

    Raises:
        RuntimeError: If the API call fails after retries.
    """
    client = get_client()
    _model = model or get_model()
    _temp  = temperature if temperature is not None else float(
        os.environ.get("DJINN_TEMPERATURE", _DEFAULT_TEMPERATURE)
    )
    _max   = max_tokens or int(
        os.environ.get("DJINN_MAX_TOKENS", _DEFAULT_MAX_TOKENS)
    )

    if messages is None:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=_model,
            messages=messages,
            temperature=_temp,
            max_tokens=_max,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        raise RuntimeError(
            f"[djinn.core.llm] Chat completion failed on backend "
            f"'{get_backend()}': {exc}"
        ) from exc


# ─── CLI smoke test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Quick sanity check from the terminal:

        python -m djinn.core.llm
        DJINN_USE_GROQ=1 GROQ_API_KEY=gsk_... python -m djinn.core.llm
    """
    print(f"[djinn.core.llm] Backend : {get_backend()}")
    print(f"[djinn.core.llm] Sending test prompt...")
    try:
        reply = chat("Reply with exactly: DJINN ONLINE")
        print(f"[djinn.core.llm] Response: {reply}")
    except RuntimeError as e:
        print(f"[djinn.core.llm] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
