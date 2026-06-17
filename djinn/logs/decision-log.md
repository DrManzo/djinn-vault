# Decision Log

Record of architectural and technical decisions made during Djinn builds.

## 2026-06-11 — PrusaSlicer removed from pipeline
**Decision:** Remove all PrusaSlicer references from vault docs. Pipelines now use Creality Print exclusively for all slicing. All PrusaSlicer configs archived.

---

---

## 2026-06-05 — gcode post-processing vs 3MF SupportBlocker volume for multi-instance plates

**Decision:** Use `djinn-gcode-support-cap` post-processor to cap support height, not 3MF modifier volumes.

**Context:** Need to stop supports at Z=50mm for 3× Camood plate. Attempted 3MF `SupportBlocker` volume (combined mesh + face-range config). Single-instance worked, multi-instance broke — PS printed the modifier box as solid geometry.

**Options considered:**
1. Fix 3MF multi-instance format (separate objects per instance, or components assembly)
2. gcode post-processor strip support E-moves above Z_MAX
3. PrusaSlicer per-object support settings via profile

**Chosen:** Option 2 — post-processor.

**Why:** Single-instance test confirmed SupportBlocker format is correct. Multi-instance failure is a PS bug, not a format error. Fixing it would require reverse-engineering PS's multi-instance 3MF parsing. Post-processor is format-agnostic, testable, and composable with the existing djinn-gcode-safety pipeline. E-only stripping (not full line deletion) preserves toolpath continuity.

**Trade-off:** Post-processor runs after slice so support geometry is still computed for the full model height (wasted slice time ~15%). Acceptable — slice time is dominated by perimeters and infill, not support generation.

*— Claude*

---

## 2026-06-05 — Camood engraving: clean MakerWorld base vs branded STL

**Decision:** Use `Camood_clean.stl` (MakerWorld puffco-proxy-core-toilet-cup) as engraving source, not the branded Terp Tribe STL.

**Why:** Branded STL has manufacturer embossed text geometry on back panel (18,436 faces vs 14,726 clean). Adding shop branding on top of manufacturer text would stack two layers of text on the same face. Clean base = correct starting point for shop-branded prints.

**Note:** Javier confirmed branded back text should be preserved on units that already have it. New production runs use clean base.

*— Claude*

---

## 2026-06-05 — DancingScript glyph rendering: quadratic bezier required for TrueType

**Decision:** Implement full TrueType quadratic bezier in `camood_tthq_engrave.py` PolyPen, including implied on-curve midpoints for multi-off-curve splines.

**Why:** fontTools `SegmentToPointPen.qCurveTo` delivers off-curve control points + on-curve endpoint. Naive linear interpolation between consecutive points produces jagged faceted edges on every curve. DancingScript is heavily quadratic — every letter has multiple multi-off-curve splines. The T crossbar junction and e bowl were the most visible failures.

**Formula:** `(1-t)²P0 + 2(1-t)tP1 + t²P2` with implied midpoints `((ctrl[i] + ctrl[i+1]) / 2)` for multi-off-curve runs per TrueType spec.

*— Claude*

---

### 2026-06-05 — Gateway enforcement strategy: behavioral contract + git hook, not Python intercept

**Decision:** Phase 1 uses GATEWAY.md (behavioral contract loaded at session start) as primary enforcement for LLM agents, with git pre-push hook as the only hard mechanical gate. Deferred Python enforcement module (`djinn/gateway/`) to Phase 2.

**Rejected:** Universal Python wrapper intercepting all agent tool calls. Reason: Claude Code, Marcus (Perplexity web), and opencode all call system tools directly — there is no Python intercept point for these agents. The Python module is valid for the Salomon-side orchestrator but cannot cover the full agent fleet.

**Why this works:** The git hook is the one real choke point. All persistent work goes through git push. If you can't push without Dev mode, you can't permanently affect the vault without authorization. The behavioral contract handles the gap between "I took the action" and "it got pushed."

*— Claude*

## 2026-06-07 — Profile system placement

**Decision:** resolve_profile() lives in djinn.core.llm, not gate.py.
**Reason:** LLM concerns belong in the LLM module. gate.py exports validate_profile()
as a thin convenience but the authoritative implementation is llm.py.

## 2026-06-07 — Heartbeat delta_guard state key

**Decision:** State tracks GPU/RAM/disk/Ollama metrics, not timestamp or full file content.
**Reason:** Timestamp always changes — using it as state would fire every run, defeating
the guard. Metrics represent meaningful system state change.

— Claude

## 2026-06-08 — Virtual printer velocity limits (Claude)
**Decision:** Set `max_velocity=200`, `max_accel=3000` in virtual printer config instead of real V3 Plus values (600/20000).
**Why:** SimulAVR runs at 2MHz (real MCU: 20MHz). Real values cause "Timer too close" MCU shutdown. Sim values keep the virtual MCU alive. Motion timing is inaccurate; all API, macro, and gcode behavior is identical.

— Claude

## 2026-06-08 — Persistent WS state merge over full-state replacement (Claude)
**Decision:** `_handle_ws_message` uses a module-level `_ws_state` dict that accumulates delta fields rather than overwriting with each partial notification.
**Why:** Moonraker's `notify_status_update` sends only changed fields. A `total_duration` delta with no `state`/`filename` would overwrite them with empty strings. Pattern: `status[key].update(fields)`.
**Alternative rejected:** Re-querying full state on every notification (wasteful, duplicates HTTP polling behavior).

— Claude

---
**2026-06-14 — Kill djinn-marcus-sync**
**Decision:** Removed marcus-sync entirely (service, timer, script).
**Why:** Selenium scraper for Perplexity Pro library. Fragile (breaks on site updates), and Javier downloads exports manually when he needs them. The clerk/RAW pipeline already handles manual drops. No real use case for automation here.
**Alternative rejected:** Fixing the import error and keeping it — not worth the maintenance surface.

*— Claude*

## 2026-06-14 — Three-tier COMMS split
**Decision:** Split COMMS.md into COMMS.md (agent-to-agent), CHECKPOINTS.md (checkpoint lifecycle), PIPELINE.md (Clerk/Slipbox automation noise).
**Why:** A single append-only file mixed three distinct signal types with different owners and retention policies. Agent handoffs were buried under 100+ Clerk→Slipbox pipeline entries and 60+ stale checkpoints. Each new file can be rotated independently.
**Alternative rejected:** Keeping a single file but pruning more aggressively — pruning doesn't fix the signal-to-noise ratio at read time.

## 2026-06-14 — Agent tag propagated via env var, not hook
**Decision:** Export `DJINN_AGENT` in the 5 callers (vault-sync, djinn-session-end, djinn-sync, djinn-task-complete, djinn-bugreport) rather than modifying the git hook.
**Why:** The hook fires at push time and doesn't have access to the calling agent's identity. The calling script knows exactly which agent it is. Env var propagation through the git→hook→gateway chain works cleanly and requires no hook changes.

*— Claude, 2026-06-14*

## 2026-06-14 — Migrate forge-slicer to Orca Slicer
- CrealityPrint v6+ `--slice 0` segfaults on all printers with `support_multi_bed_types: 1` — confirmed null deref in `PartPlate::set_shape` across 7 versions

## 2026-06-15: Secrets in env file, hard-fail on missing token

**Decision:** `os.environ["DJINN_DISCORD_TOKEN"]` (KeyError on missing) over `.get()` with hardcoded fallback. Single `~/.djinn.env` for all three services. Did not rewrite git history.

**Why:** Silent fallback → confusing 401 with no obvious cause. Single env file → token rotation touches one file. History rewrite → requires coordinated force-push across Salomon/Typhon/Orion; token rotation is cheaper if ever needed.

*— Claude*

## 2026-06-16 — djinn-publish repo placement
**Decision:** `~/djinn-publish/` standalone repo, NOT inside Obsidian vault
**Why:** vault-enrich is running concurrent commits; a 14-file code tree inside the vault would recreate the PIPELINE.md merge conflict storm from the previous session. Scripts stay separate from content.

## 2026-06-16 — All 14 pipeline tools deterministic except --strict mode
**Decision:** No LLM calls in default mode for any tool
**Why:** Follows TASK-070 spec and feedback memory on AI usage. Flags are candidates for human judgment, not auto-corrections. Only continuity_checker --strict calls Ollama for semantic timeline contradiction — the one case where pattern matching produces too many false positives.
