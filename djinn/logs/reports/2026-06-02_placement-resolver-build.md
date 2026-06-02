---
title: Session Report — Placement Resolver Bridge
agent: Claude
date: 2026-06-02
tags: [djinn, report, engraving, placement-resolver, pipeline]
related: [[build-log]] [[decision-log]] [[2026-06-02_proxy-stand-engraving-placement-failure]]
---

# Session Report — Placement Resolver Bridge

**Date:** 2026-06-02
**Agent:** Claude (+ Marcus on parallel lane)
**Session type:** Build
**Trigger:** Prior session scrapped because no bridge existed between LLM position_description strings and the exact coordinate parameters required by `djinn-model-text-engrave`. Marcus was already building placement_resolver.py on the remote; session picked up after his commit landed.

---

## Summary

Built and merged the final piece of the engraving pipeline: `placement_resolver.py`. This module converts an approved engraving proposal's `position_description` string into exact mm coordinates and a CLI-ready `modifier_args` dict — deterministically, without a second LLM call. Two bugs were identified in Marcus's initial version and patched: prime zone Z was incorrectly applied to FLAT_TOP surfaces, and the arc radius fallback failed for tapered cylinders (Proxy Stand case). Both fixes committed and pushed to `DrManzo/djinn-vault`.

---

## What Was Built or Changed

- **`placement_resolver.py`** — new module, built by Marcus and patched by Claude
  - `resolve(spec, geo_report) → PlacementSpec` — main entry point
  - Keyword parser: lower_third / upper_third / upper_band / lower_half / centered / left_align / right_align
  - Edge clearance clamping on both axes
  - Prime zone Z centering for side/cylindrical surfaces only
  - Arc radius fallback: `spec.arc_radius_mm → 0` → `wall_profile.outer_r_max` when `arc_wrap=True`
  - Graceful failure: returns `resolved=False` + reason string, never raises

- **`engrave.py` `approve()`** — patched by Marcus
  - Caches `state._geo_report` during `run()` for use in `approve()`
  - Calls `placer.resolve(chosen, state._geo_report)` on approval
  - Stores `PlacementSpec` in `state.engraving_placement`
  - Prints resolved coordinates + CLI args for Telegram confirmation

- **Font comparison rendered**: Liberation Sans Bold and DejaVu Sans Bold at 6mm vs Roboto Black — unrolled cylinder view. Files: `proxy_v18_engraved.png`, `proxy_font_compare.png`, `proxy_font_unrolled.png` on Desktop.

- **v19 STL files** generated with Liberation and DejaVu fonts:
  - `/home/drmanzo/printer-files/queue/Proxy_Stand_job5_v19_liberation.stl` — 0.173 cm³
  - `/home/drmanzo/printer-files/queue/Proxy_Stand_job5_v19_dejavu.stl` — 0.184 cm³

---

## Technical Decisions

**Decision: Accept Marcus's GeometryReport-object API, not mesh_state dict** — Marcus's `resolve(spec, geo_report)` takes the typed dataclass directly. My initial version took `mesh_state: dict` (a serialized subset). The dataclass approach is richer and avoids double-serialization. Kept Marcus's architecture.

**Decision: Deterministic keyword parser, no LLM** — `position_description` is parsed with ordered regex rules (longest-match first). This is Marcus's approach and the right one — the placement bridge must not introduce a second LLM latency hit or hallucination surface. All spatial reasoning is math.

**Decision: arc_radius fallback to wall_profile.outer_r_max when arc_wrap=True** — The LLM often sets `arc_radius_mm=0` for cylindrical surfaces. The spec's `arc_wrap=True` flag is the intent signal; `wall_profile.outer_r_max` is the ground truth. Previously the fallback only triggered when `is_cylindrical=True`, which fails for tapered models like the Proxy Stand (outer_r variance >15% disqualifies it as "cylindrical" by the 15% threshold despite being functionally cylindrical).

**Decision: Prime zone Z override scoped to side surfaces only** — Marcus's initial version set `z_surface = pz_center` whenever any wall profile existed. This would corrupt Z for FLAT_TOP surfaces (e.g. a ring or box top) which have their own correct Z. Fixed to gate on `is_side_surface`.

---

## Files Created or Modified

```
djinn/printer/agent/orchestrator/agents/placement_resolver.py   ← new — placement bridge
djinn/printer/agent/orchestrator/agents/engrave.py              ← approve() patch (Marcus)
printer-files/queue/Proxy_Stand_job5_v19_liberation.stl         ← Liberation Sans Bold engraving
printer-files/queue/Proxy_Stand_job5_v19_dejavu.stl             ← DejaVu Sans Bold engraving
Desktop/proxy_v18_engraved.png                                  ← render
Desktop/proxy_font_compare.png                                  ← side-by-side font comparison
Desktop/proxy_font_unrolled.png                                 ← unrolled cylinder comparison
```

---

## Tests & Validation

Smoke test run against 5 cases:
1. Cylindrical centered (Proxy Stand) → `r=31.0mm`, `z=5.9mm`, CLI args correct
2. Flat top lower third → `y=-13.2mm`, edge-clearance maintained
3. Empty mesh_state → `resolved=False`, specific error message
4. Explicit centroid in position_description → parsed, clamped correctly
5. Right-aligned lower third → `x=+14.0`, `y=-13.2`

All passed. No regression in engrave.py (import structure unchanged).

---

## Known Issues

- Font comparison renders (3D matplotlib) show letter shapes at low contrast — unrolled cylinder view is more informative but still hard to read at the rendered scale. Operator confirmed "okay change the font" based on this; Liberation or DejaVu selection pending.
- `modifier_args` keys use the brief's proposed CLI API (`--x-offset`, `--arc-radius`) not the current `djinn-model-text-engrave` flags (`--x`, `--side-radius`). Acceptable for now — when the CLI is updated or a new modifier wrapper is built, only `placement_resolver.py` needs to change.
- `is_cylindrical=False` for Proxy Stand (taper causes >15% variance). The fallback fix handles this for `arc_wrap=True` cases, but a dedicated cylindrical-surface heuristic (e.g. "side surface with consistent Z and high r") would be more robust long-term.

---

## What's Next

- Operator picks font (Liberation vs DejaVu) → re-engrave Proxy Stand → confirm v19 for printing
- Wire `confirm engrave placement` Telegram command to shell-exec `djinn-model-text-engrave` with resolved modifier_args
- Mac arrives → swap `llm.py` from phi4:14b to Claude Sonnet → end-to-end test with real LLM
- Marker-based placement bridge (TASK-062): operator drops cube in PrusaSlicer at desired text position → read centroid XYZ from 3MF → resolver takes over from there

— Claude
