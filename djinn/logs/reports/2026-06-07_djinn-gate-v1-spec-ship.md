## djinn-gate v1 + spec-v1.0 batch ship — 2026-06-07

**Status:** Complete
**Commit:** 4389f17

**Files changed:**
- `djinn/tools/djinn-gate/gate.py` — NEW
- `djinn/tools/djinn-gate/routing.toml` — NEW
- `djinn/tools/delta-guard/delta_guard.py` — NEW
- `djinn/core/llm.py` — profile system added
- `~/.local/bin/heartbeat` — delta_guard push guard added
- `djinn/GATEWAY.md` — lane discipline section added (Tier 4, explicit Javier instruction)

**Notes:**

gate.py: phrase-first routing (substring match), keyword fallback (word-boundary regex),
first match wins, no default lane, exit 0/1. HTTP mode on :7070 via --serve flag.
Profile validation (`validate_profile`) is exported from gate.py but the canonical
implementation lives in `llm.py:resolve_profile()`.

routing.toml: Nine lanes populated from session taxonomy + ROUTING.md.
ops lane: llm_allowed=false (enforced in gate output, callers must check).
student lane: isolated=true, escalation_allowed=false.

delta_guard: /tmp/djinn-state/ is ephemeral (clears on reboot). State key collisions
are the caller's responsibility — use unique keys per timer. SHA-256 on JSON
serialization with sort_keys=True for stable hashing.

llm.py: profile is now a required positional-style arg in chat(). Old callers of
djinn.core.llm.chat() don't exist yet (no production scripts use this module yet),
so no migration needed. The printer/agent/orchestrator/llm.py and djinn-3d both
have their own LLM abstractions — those are separate and unchanged per spec scope.

heartbeat: push now only fires when GPU, RAM, disk, or Ollama model count changes.
Timestamp changes alone do not trigger a push. Reduces push cadence from every-5-min
to push-on-state-change.

GATEWAY.md: Lane discipline entry added under Hard Rules. Explicitly bars Claude
invocation for ops, clerk, production, shop, and coding tasks without djinn-gate
rejection first. Profile requirements codified there as well.

**Deviations from spec:**
- `gate.py:validate_profile()` added as a module-level export (bonus utility, not
  in spec). Spec only required profile system in llm.py.
- `djinn-3d` and printer/agent callers not updated — they use separate LLM
  abstractions that don't route through `djinn.core.llm.chat()`. Flagging for
  Marcus review: should those eventually be migrated to djinn.core.llm?

— Claude
