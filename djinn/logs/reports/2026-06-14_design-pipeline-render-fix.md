---
title: Session Report — Design Pipeline Render Fix & Design-to-Print Bridge
agent: Claude
date: 2026-06-14
tags: [djinn, report, pipeline, openscad, design]
related: [[build-log]] | [[decision-log]]
---

# Session Report — Design Pipeline Render Fix & Design-to-Print Bridge

**Date:** 2026-06-14
**Agent:** Claude
**Session type:** Debug / Build
**Trigger:** Continuation of prior session; `proto_opt` OpenSCAD render was failing for LLM-generated SCAD, causing `.scad` fallback paths to reach `plate_nest`, which crashed with `NotImplementedError: file_type 'scad' not supported`.

---

## Summary

Diagnosed that `design_gen.py` was generating OpenSCAD with undefined module calls (`sd_card_holder()` and `fillet_all()` — called but never defined), producing empty geometry. Fixed the LLM prompt to explicitly prohibit this pattern. Fixed `proto_opt.py` to surface the actual OpenSCAD stderr and raise a clean `RuntimeError` instead of silently falling back to a `.scad` path. Fixed `djinn-model-slice` to read `doe_profile` (correct queue field) instead of `doe` (nonexistent). Full pipeline now runs end-to-end: `djinn-design "..." --full` → SCAD → STL → DOE → plate → price → `djinn-model-slice N`.

---

## What Was Built or Changed

- **`design_gen.py`** — Strengthened SYSTEM prompt with explicit OpenSCAD validity rules: forbid calling undefined modules, forbid `fillet_all()`/`hull_r()`/utility helpers not defined in-file, explain children() call trap, require mental trace of every module call to its definition
- **`proto_opt.py`** — `_render_stl()` now returns `(ok, stderr)` tuple; on render failure, logs full OpenSCAD stderr and raises `RuntimeError` with diagnostic hint instead of falling back to `.scad` path
- **`orchestrator.py`** — Catches `RuntimeError` from `proto_opt.run()`, prints error + fix instructions, returns state gracefully so pipeline doesn't crash
- **`djinn-model-slice`** — Fixed DOE key lookup: `job.get("doe_profile") or job.get("doe") or {}` (was `job.get("doe")` which was always empty for design jobs)

---

## Technical Decisions

**Raise RuntimeError instead of .scad fallback** — The prior fallback was silent data corruption (a `.scad` path stored where an `.stl` path was expected). Failing loudly with the actual stderr is always better. The user can then inspect/fix the SCAD.

**Prompt-level fix in design_gen vs. post-processing validation** — Chose to fix the prompt because the LLM generates the full SCAD in one shot; validating after-the-fact would require parsing OpenSCAD AST or running openscad --check, which is slower and more complex. The prompt rule is "trace every call to a definition" — simple, verifiable by the model.

**`doe_profile` key lookup with fallback to `doe`** — `doe_profile` is the ProjectState field name; added `or job.get("doe")` as a fallback for any hand-crafted commission jobs that might use the shorter key.

---

## Files Created or Modified

```
~/Obsidian/djinn/printer/agent/orchestrator/agents/design_gen.py   ← strengthened SYSTEM prompt
~/Obsidian/djinn/printer/agent/orchestrator/agents/proto_opt.py    ← _render_stl returns (ok, stderr); raises RuntimeError on failure
~/Obsidian/djinn/printer/agent/orchestrator/orchestrator.py        ← catches RuntimeError from proto_opt, reports cleanly
~/.local/bin/djinn-model-slice                                      ← reads doe_profile key (was doe)
```

---

## Tests & Validation

Full pipeline test — `djinn-design "small SD card holder, 4 slots, PLA, wall mount" --full`:
- design_gen → SCAD generated with valid module definitions ✓
- proto_opt → prototype.stl (2KB) + production.stl (5KB) rendered ✓
- doe_opt → 68/108 candidates, prototype_fast profile ✓
- plate_nest → plate_job2.stl created ✓
- price → cost floor $11.41, fair market $11.41 ✓
- Job #2 → status: priced ✓

Bridge test — `djinn-model-slice 2`:
- Found job2 (priced status) ✓
- Resolved plate_stl path ✓
- DOE goal `prototype_fast` → tier=proto ✓ (was incorrectly `production` before fix)
- Slicer invoked with correct Calliope-Proto.json profile ✓
- Slicer itself fails: `F002-0.4.def.json's from unsupported` (pre-existing Creality Print config bug — unrelated to this fix)

---

## Known Issues / Caveats

- Creality Print machine config `F002-0.4.def.json` causes slicer crash (`from unsupported`). Pre-existing issue — not introduced here. Needs separate investigation.
- `plate_nest.py` sets `state.status = "priced"` instead of `"plate_nest"`. The orchestrator works around this by capturing `_pre_plate_status` before calling `plate_nest.run()`. The root cause (wrong status set in plate_nest) is left as-is to avoid introducing more risk mid-session.
- LLM-generated SCAD can still fail in ways the prompt doesn't catch. The new error path at least surfaces the exact openscad stderr so the failure is diagnosable.

---

## What's Next

- [ ] Fix Creality Print slicer config (`F002-0.4.def.json's from unsupported`) — @Salomon or manual
- [ ] Fix `djinn-bughunter` bandit JSON parse error — @Claude
- [ ] Commission flow end-to-end test — @Javier
- [ ] `snap` command live test in Discord — @Javier
- [ ] Update CVE packages: aiohttp, chromadb, pip 24→26, setuptools 65.5 — @Salomon

---

*— Claude, 2026-06-14*
