---
title: Session Report — Camood "Terp Tribe HQ" Tank Engraving
agent: Claude
date: 2026-06-04
tags: [djinn, report, engraving, camood, terp-tribe, 3d-print]
related: [[build-log]] [[camood]]
---

# Session Report — Camood TTHQ Tank Engraving

**Date:** 2026-06-04
**Agent:** Claude
**Session type:** Build / Debug
**Trigger:** Engrave "Terp Tribe HQ" DancingScript-Bold on the flat back tank panel of the Camood, 6mm below center

---

## Summary

Successfully engraved "Terp Tribe HQ" in DancingScript-Bold (9mm cap height) on the flat back tank face of the Camood model. The engraving is centered horizontally at Z=71mm (6mm below tank center), 1.8mm deep. After two sessions of iteration the key blocker was discovered: the mesh bounding box Y=54.09mm is NOT the tank back face — the actual flat surface is at Y=51.553mm, determined by ray-casting. Once that was corrected, the boolean cut produced 0.121 cm³ removed (0.011 cm³/char, above LG-3 threshold), watertight result.

---

## What Was Built or Changed

- **Engraving script** `/home/drmanzo/.claude/jobs/04e6fec6/tmp/engrave_tank.py` — standalone pipeline: fontTools glyph rendering → shapely polygons → trimesh.creation.extrude_polygon (watertight, replaces manual ring-face construction) → coordinate transform to Y-facing extrusion → manifold3d boolean subtract
- **Output STL** `~/printer-files/staging/Camood_TTHQ_tank_v3.stl` — final engraved model
- **Library copy** `~/printer-files/library/engraved/terp-tribe/Camood_TTHQ_engraved.stl`
- **Original reorganized** moved to `~/printer-files/library/originals/terp-tribe/`
- **Vault piece note** `~/Obsidian/djinn/printer/library/pieces/camood.md` — updated geometry, correct face Y, all file paths, processing log

---

## Technical Decisions

**Ray-cast to find actual face Y vs bounding box — Why:** The bounding box Y_max=54.09mm is at the curved crown of the model body, NOT the flat tank face. The tank back face is at Y=51.553mm, consistent across all X/Z positions in the tank zone. Using bounding box would have placed the cutter 2.5mm above the surface (in air), removing 0 material.

**trimesh.creation.extrude_polygon over manual face construction — Why:** Manual ring→face construction produced non-manifold cutters (not watertight). extrude_polygon is guaranteed to produce a valid closed solid. The extruded solid is in XY plane; a 4×4 rotation matrix maps it to the XZ plane (text X→model X, text Y→model Z, extrusion Z→model −Y from surface).

**manifold3d Manifold(mesh) API — Why:** API changed from `Manifold.of_mesh()` to `Manifold(mesh_obj)` constructor. The older form throws AttributeError.

**fontTools over freetype-py — Why:** freetype-py not installed in djinn-orchestrator venv. fontTools 4.63.0 is available and provides full glyph outline access via SegmentPen/PolyPen interface.

**DancingScript-Bold at 9mm cap height — Why:** Previous sessions established this as the legibility target for the proxy stand (same brand). Consistent branding across TTHQ pieces.

---

## Files Created or Modified

```
~/printer-files/staging/Camood_TTHQ_tank_v3.stl                      ← final engraved Camood (print-ready)
~/printer-files/library/engraved/terp-tribe/Camood_TTHQ_engraved.stl ← library copy
~/printer-files/library/originals/terp-tribe/The Terp Tribe - Camood.stl ← reorganized original
~/Obsidian/djinn/printer/library/pieces/camood.md                     ← updated piece note
```

---

## Tests & Validation

| Check | Result |
|-------|--------|
| Cutter watertight | ✅ True |
| Boolean status | ✅ Error.NoError |
| Result watertight | ✅ True |
| Volume removed | 0.121 cm³ |
| Per-character | 0.011 cm³ (LG-3 min: 0.008) ✅ |
| Contains probe at letter strokes | ✅ 29/90 X positions confirmed cut at Y=50.7mm |

---

## Known Issues

- `djinn-model-text-engrave` CLI still does not support flat vertical faces — the engrave_tank.py script is standalone and not integrated into the tool. If this pattern recurs for other flat-panel pieces, the tool should gain a `--flat-panel` mode with ray-cast surface detection.
- The engraving script is in the temp job dir — it should be saved permanently if we do more Camood variants.

---

## What's Next

- Slice `Camood_TTHQ_engraved.stl` for print — **needs explicit approval from Javier before printing**
- Proxy core cylinder: 38mm × 50.5mm with bore matching Camood inner circle
- MakerWorld link for Camood: https://makerworld.com/en/models/2801075-puffco-proxy-core-toilet-cup#profileId-3116028 — add to piece note
- Applacrabus: ON HOLD pending better support strategy (tree supports or reorientation)
- TASK-027: Fill SHIPPO_API_KEY in `~/.config/forge/shop.env`

*— Claude, 2026-06-04*
