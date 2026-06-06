---
title: Session Report — Camood TTHQ Engraving Fixed
agent: Claude
date: 2026-06-05
tags: [djinn, report, 3dprint, engraving, camood, bugfix]
related: [[build-log]] [[2026-06-05_djinn-detect-surfaces]]
---

# Session Report — Camood TTHQ Engraving Fixed

**Date:** 2026-06-05
**Agent:** Claude
**Session type:** Build / Debug
**Trigger:** Javier provided clean Camood base (no manufacturer text) from MakerWorld cup_stls.zip and asked to fix rendering issues with T and e glyphs in DancingScript-Bold.

---

## Summary

Identified clean Camood base STL (same geometry, no Terp Tribe branding, 14,726 faces vs 18,436 on branded), saved to library. Fixed two root-cause rendering bugs in `camood_tthq_engrave.py`: (1) `qCurveTo` was doing linear interpolation instead of quadratic bezier — every curve in DancingScript came out faceted; (2) glyph hole detection used unary_union instead of subtracting counter rings, so `e`, `o`, `p` etc. rendered as filled blobs. Also fixed XY centering for clean model's non-origin export coordinates. Final `Camood_TTHQ_engraved.stl` built from clean base, "Terp Tribe HQ" DancingScript-Bold 9mm at 2.5mm depth, TF anvil on bottom. Watertight, legibility PASS.

---

## What Was Built or Changed

- **`~/printer-files/library/originals/terp-tribe/Camood_clean.stl`** — clean Camood base from MakerWorld (cup_stls.zip), no manufacturer text
- **`~/printer-files/library/originals/terp-tribe/Camood_clean_surfaces.json`** — djinn-detect-surfaces scan of clean model
- **`~/printer-files/scripts/camood_tthq_engrave.py`** — three fixes + source/depth update (see Technical Decisions)
- **`~/printer-files/library/engraved/terp-tribe/Camood_TTHQ_engraved.stl`** — final output, clean base + TTHQ text + TF anvil

---

## Technical Decisions

**`qCurveTo` quadratic bezier fix — Why:** Original code was doing linear interpolation between consecutive point pairs in the spline, not computing `(1-t)²P0 + 2(1-t)tP1 + t²P2`. DancingScript is TrueType (quadratic), so every curve in every letter was wrong. T crossbar junction and e bowl were most visibly broken. Fixed to proper bezier with implied on-curve midpoints for multi-off-curve splines per TrueType spec.

**Glyph winding fix (CW = outer, CCW = hole) — Why:** TrueType convention is CW for outer contours, CCW for holes — opposite of standard math. `glyph_polygons` was sending all rings to `unary_union`, which unions the inner counter with the outer body instead of subtracting it. Fixed: signed area < 0 → outer, ≥ 0 → hole. Subtract holes from unioned outers.

**XY centering before probe — Why:** `Camood_clean.stl` exports at X=[95,161] Y=[74,182] (Fusion/OnShape origin), not centered. Probe points and text placement are hardcoded to X=0 center. Added translate([-cx, -cy, 0]) after bed-align so all downstream coords are model-agnostic.

**Depth 1.8mm → 2.5mm — Why:** Javier confirmed this part carries no structural load. Deeper cut = more contrast, easier to read post-print. 0.0139 cm³/char at 2.5mm vs 0.0099 at 1.8mm — both pass legibility gate (min 0.008).

**Source changed to Camood_clean.stl — Why:** Original was using branded Terp Tribe STL (with manufacturer embossed text). Clean MakerWorld base is the correct starting point for a shop-branded print.

---

## Files Created or Modified

```
~/printer-files/library/originals/terp-tribe/Camood_clean.stl           ← clean base, no mfg text
~/printer-files/library/originals/terp-tribe/Camood_clean_surfaces.json ← surface scan
~/printer-files/scripts/camood_tthq_engrave.py                          ← qCurveTo, winding, XY-center, depth=2.5
~/printer-files/library/engraved/terp-tribe/Camood_TTHQ_engraved.stl   ← final output
```

---

## Tests & Validation

```
Rendering glyphs...
Scaled text: 45.63mm wide × 9.00mm tall
Back face at Y = 51.553mm (ray-cast median from 20 hits)
Carving 2.5mm inward
7 cutter solid(s) — watertight=True
Result manifold: 42786 tris, status=Error.NoError

Volume removed:   0.15291 cm³
Per character:    0.01390 cm³   ← PASS (min 0.008)
Final watertight: True
Final faces:      43232
```

Legibility gate: ✅ PASS all gates (height 9mm ≥ 3mm flat, depth 2.5mm ≥ 0.8mm, vol/char 0.014 ≥ 0.008, font = DancingScript-Bold).

---

## Known Issues / Caveats

- `rtree` was not installed in pyenv python3 — installed via pip during this session. Required by trimesh ray_triangle backend for spatial indexing.
- `djinn-detect-surfaces` curvature pass still running but finding no additional surfaces on this model (all geometry is flat-panel, curvature pass finds nothing beyond raycast).

---

## What's Next

- [ ] Slice `Camood_TTHQ_engraved.stl` for 4× print — send `slice 9` through Discord/Telegram to Salomon
- [ ] Job 9 physical fix: inspect toolhead cable at ~107mm height before restart
- [ ] TASK-027: Fill SHIPPO_API_KEY in `~/.config/forge/shop.env`

---

*— Claude, 2026-06-05*
