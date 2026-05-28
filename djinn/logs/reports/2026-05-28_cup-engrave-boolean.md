---
title: Session Report — Cup Engraving Boolean Merge
agent: Salomon
date: 2026-05-28
tags: [djinn, report, cup, engrave, boolean, 3mf]
related: [[build-log]] | [[decision-log]]
---

# Session Report — Cup Engraving: Boolean Text Merge

**Date:** 2026-05-28
**Agent:** Salomon
**Session type:** Build
**Trigger:** OrcaSlicer Emboss tool exported "Terp Tribe HQ" text as 26 separate bodies (not merged into cup). Needed boolean difference for proper engrave.

---

## Summary

OrcaSlicer's Emboss tool placed "Terp Tribe HQ" text on the cup surface as a separate component (1.5mm thick raised letters, not cut in). A boolean difference pipeline was built to carve the text 1.9mm into the cup wall. The cup has a curved front face (surface Y varies from 49.99 at edges to 51.55 at center), so a uniform 1.9mm depth across all letters wasn't achievable with a flat text mesh. The final compromise: 2.5mm center depth / 0.9mm edge depth, using manifold3d for the boolean. trimesh (blender engine) and Blender's boolean modifier both failed on this geometry; manifold3d succeeded.

---

## What Was Built or Changed

- **Boolean difference pipeline** — Python script parsing 3MF XML to extract cup (object 1) and text (object 2) meshes, applying the OrcaSlicer transform, shifting inward, and boolean differencing with `manifold3d`
- **`manifold3d` installed in venv** — required for robust boolean (trimesh blender engine and Blender's EXACT solver both returned empty on this geometry)
- **Three approaches tried and rejected:**
  1. trimesh `engine='blender'` — returned empty result (non-manifold / missed intersection)
  2. Blender script with `matrix_world` + `transform_apply` — matrix with mirror (det=-1) caused `transform_apply` to silently not apply; data.transform() fixed vertex coordinates but boolean still returned empty
  3. Blender shrinkwrap + recess approach — shrinkwrap collapsed the 1.5mm thick text into a zero-thickness surface; boolean produced degenerated mesh (12 faces)
- **Cup wall thickness confirmed:** Front wall at text area spans Y≈15.5 (inner surface) to Y≈51.55 (outer surface) = 36mm thick. Sufficient material for deep engrave.
- **Cup surface curvature mapped:** at text edges (X=±25, Z=27-33), surface Y≈49.99 vs center (X=0) Y≈51.55 — 1.56mm variation across 52mm text width

---

## Technical Decisions

- **manifold3d over Blender/trimesh boolean** — All other engines failed. manifold3d produced a clean, watertight result (9173 verts, 18326 faces, 249.58 cm³) with 0.25 cm³ removed (matching text volume). The library is fast (seconds on 7359-triangle cup + 3600-triangle text).
- **-2.5mm Y shift over -1.92mm** — The 1.9mm spec at center left edges at only 0.34mm (almost invisible). The -2.5mm shift gives 2.5mm at center / 0.9mm at edges — functional engrave across all letters.
- **Flat text mesh over surface projection** — Shrinkwrap to follow cup curvature created a collapsed mesh. Projecting each vertex along normals would require per-vertex cup surface queries. Flat shift was simpler and produced acceptable results.
- **OrcaSlicer text kept separate** — User chose not to boolean-merge inside OrcaSlicer. The 3MF export has cup and text as two objects in the same mesh resource file, with text positioned via a component transform. This transform was extracted and applied in the pipeline.

---

## Files Created or Modified

```
Obsidian/djinn/printer/library/cup/cup_engraved_final.stl   ← final engraved cup STL (9173 verts, watertight)
tmp/opencode/engrave_cup.py                                   ← trimesh boolean attempt (rejected)
tmp/opencode/blender_engrave.py                                ← Blender boolean attempt (rejected)
tmp/opencode/blender_engrave_v2.py                             ← Blender shrinkwrap attempt (rejected)
tmp/opencode/blender_engrave_v3.py                             ← Blender shrinkwrap + push_pull (rejected)
tmp/opencode/cup.stl                                           ← cup converted to STL for processing
```

---

## Dependencies Installed

| Package | Method | Purpose |
|---------|--------|---------|
| manifold3d 3.5.0 | pip (venv) | Robust boolean CSG operations on triangle meshes |
| trimesh 4.12.2 | pip (venv) | Mesh loading, analysis, export (replaces system 4.5.1) |
| numpy 2.4.6 | pip (venv) | Array ops for transform application |

---

## Tests & Validation

- **manifold3d boolean:** `cup.difference(text_mesh)` → 9173 verts, 18326 faces, watertight: True, volume: 249.58 cm³ (0.25 cm³ removed = text volume of 248.5 mm³)
- **Edge overlap check:** At text edges (X=±25, Z=27-33), cup surface at Y≈49.99, text inner face at Y=47.57 → 0.92mm overlap. At center (X=0), cup surface at Y≈51.55 → 2.48mm overlap.
- **Cup wall probed:** Cross-section tests at X=0 through text area show solid material from Y≈15.5 to Y≈51.55 (36mm wall). Text at Y [47.57, 49.07] is well within solid material.
- **Watertightness:** True — manifold3d produces manifold output
- **Volume consistency:** 0.248 cm³ removed matches the 248.5 mm³ text mesh volume within measurement precision

---

## Known Issues / Caveats

- **Engrave depth varies:** 2.5mm at center / 0.9mm at edges due to cup curvature. Not uniform.
- **Overhangs from engrave:** The boolean cut creates steep overhang faces inside the engrave cavity (the cut walls). With the standard profile (supports=enabled), these should print fine. If printing without supports, the shallow edge areas (0.9mm) might bridge cleanly, but the deeper center (2.5mm) may need them.
- **Only tested with this specific cup model:** The pipeline is not generalized — it reads the specific 3MF structure from OrcaSlicer 2.3.2 and the transform from the component graph.
- **manifold3d in venv only:** Installed in `/tmp/opencode/venv/`. Not available system-wide.
- **OrcaSlicer 3MF as source:** The text geometry must come from OrcaSlicer's Emboss output. Manual text meshes would need their own transform.

---

## What's Next

- [ ] Slice and print the engraved cup — @Claude (was queued but queue cleared on stop)
- [ ] Save the boolean pipeline as `~/.local/bin/djinn-model-engrave` for reuse — @Claude
- [ ] Test with other OrcaSlicer text emboss exports for generalized compatibility — @Salomon
- [ ] Remove venv `/tmp/opencode/venv/` when done, or move to persistent location — @Claude

---

*— Salomon, 2026-05-28*
