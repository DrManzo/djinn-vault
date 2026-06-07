# Decision Log

Record of architectural and technical decisions made during Djinn builds.

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
