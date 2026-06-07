"""
djinn/printer/agent/orchestrator/llm.py
────────────────────────────────────────────────────────────────
LLM backend for the printer orchestrator.

PHASE 4 MIGRATION (2026-06-07, Marcus)
  Previous implementation had a silent Anthropic escalation path:
  if ANTHROPIC_API_KEY was present in ~/.config/djinn/claude.env,
  all printer orchestrator calls routed to claude-sonnet-4-6 without
  any gate, profile, or cost check.

  This is replaced. All calls now route through djinn.core.llm.chat()
  with declared profiles. Anthropic path is removed from this module.
  Printer tasks are ops/production lane — they do not require Claude.

PROFILE ASSIGNMENTS
  design tasks    → "synthesis"        (temp=0.7, max=2048)
  code tasks      → "structured_output" (temp=0.2, max=1024)
  classification  → "deterministic"    (temp=0.1, max=512)

BACKEND
  djinn.core.llm respects DJINN_USE_GROQ and DJINN_MODEL env vars.
  Default: Ollama qwen2.5:7b. Model overrides via DJINN_MODEL.
  For code tasks: set DJINN_MODEL=qwen2.5-coder:7b before calling.
"""

import os
import sys

# Ensure djinn root is importable when running from this subdirectory
_vault_root = None
_search = __file__
for _ in range(6):
    _search = os.path.dirname(_search)
    if os.path.isfile(os.path.join(_search, "djinn", "core", "llm.py")):
        _vault_root = _search
        break
if _vault_root and _vault_root not in sys.path:
    sys.path.insert(0, _vault_root)

from djinn.core.llm import chat as _core_chat, get_backend


class LLM:
    """
    Drop-in replacement for the old printer LLM abstraction.

    API is intentionally compatible with the previous LLM class so that
    orchestrator.py and agents/*.py require no changes. The key difference:
    - No Anthropic path. All calls are local via djinn.core.llm.
    - profile is declared per call type, not buried in defaults.
    """

    def __init__(self, prefer_code: bool = False):
        self._prefer_code = prefer_code
        # Override model for code-specific instantiation
        if prefer_code:
            os.environ.setdefault("DJINN_MODEL", "qwen2.5-coder:7b")

    def chat(
        self,
        system: str,
        messages: list,
        max_tokens: int = None,   # ignored — profile controls this
        profile: str = None,
    ) -> str:
        """
        Route a chat request through djinn.core.llm with an explicit profile.

        Args:
            system:    System prompt string.
            messages:  List of {role, content} dicts.
            max_tokens: Ignored. Profile controls max_tokens. Kept for
                        backward-compat so callers don't break.
            profile:   Required. One of: deterministic, structured_output,
                       synthesis. Inferred from self._prefer_code if not given.

        Returns:
            str: Assistant reply.
        """
        if profile is None:
            profile = "structured_output" if self._prefer_code else "synthesis"

        # Build flat prompt from messages list for djinn.core.llm.chat()
        # (core chat handles system separately)
        user_content = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                user_content = content   # last user message wins for simple calls
            elif role == "assistant":
                pass  # multi-turn not needed for printer ops

        return _core_chat(
            prompt=user_content,
            profile=profile,
            system=system,
            messages=None,  # let core build from prompt+system
        )

    @property
    def name(self) -> str:
        return f"djinn.core.llm/{get_backend()}"
