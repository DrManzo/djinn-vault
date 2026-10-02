---
title: Session Report — Proxy Core Cup 26002 (Meshy) size check + fix
agent: Claude
date: 2026-10-01
tags: [djinn, report, forge, proxy-core, mesh-repair]
related: [[build-log]] | [[2026-10-01_bug-djinn-model-mark-hard-fails-when-config-mark-stl-unmounted]]
---

# Session Report — Proxy Core Cup 26002 (Meshy) size check + fix

**Date:** 2026-10-01
**Agent:** Claude
**Session type:** Build
**Trigger:** Javier asked to verify a Meshy core cup fits the Puffco Proxy core, then to fix it. Output named 26002.

---

## Summary

`Meshy_AI_export_1790912758_image-to-3d-texture.3mf` failed the Proxy core seat spec (38.3mm ⌀ × 51mm, walls ≥3mm): seat only ~28mm deep, tapered 38.6→35.9mm (core would stop ~7mm in), walls 1.1–2.2mm, 1,051 loose mesh pieces. Repaired, filled the old seat, scaled 1.16×, bored a straight 38.3 × 51mm seat, TF mark on bottom. Verified; saved as `26002.stl` in `~/Downloads` and `~/Desktop/Review`.

---

## What Was Built or Changed

- Blender voxel remesh (0.15mm) of main Meshy body → single watertight manifold (47,071 vs 46,961 mm³ original)
- Filled old tapered seat with frustum (z 20.5→50, r 18.85→20.2, inside the ≥0.99mm old walls)
- Uniform 1.16× scale about seat axis (125.0, 126.7) → 54.8 × 61.8 × 58.0mm
- Straight bore 38.3mm ⌀ × 51.0mm (manifold3d), floor 7mm
- TF anvil mark 15mm × 0.5mm, mirrored, centered on 36mm bottom footprint (built-in cutter from `djinn-model-mark`)

## Technical Decisions

- **Fix in-house, not re-prompt Meshy** — Meshy can't hold mm tolerances; geometry was salvageable.
- **Blender voxel remesh over pymeshlab** — pymeshlab repair left it non-manifold.
- **Direct manifold3d bore, not `djinn-bore-core`** — avoids its whole-mesh auto-scale behavior (Backpack Boyz, 2026-07-16).
- **1.16× not 1.14×** — 1.14 cleared 3mm walls by only 0.05mm; 1.16 gives 3.43mm min.
- **Bottom-face mark** — body now has a solid 36mm flat bottom.

## Files Created or Modified

```
~/Downloads/26002.stl                  ← final, unsliced (binary — not in vault)
~/Desktop/Review/26002.stl             ← identical copy for approval
~/Desktop/Review/26002_preview.png     ← bottom-view mark + axial cross-section
djinn/logs/reports/2026-10-01_proxy-core-cup-meshy-fix.md
djinn/logs/reports/2026-10-01_bug-djinn-model-mark-hard-fails-when-config-mark-stl-unmounted.md
djinn/logs/bugs.md, djinn/logs/build-log.md, djinn/communications/COMMS.md
```

## Tests & Validation

Independent re-slice of final STL (0.25mm steps): seat 38.30mm ⌀ min=max (no taper), depth 51.0mm, min wall 3.43mm @ z=26, floor 7.0mm, watertight, 1 body. Bore removed 58,755 vs theoretical 58,757 mm³ (no breakout). Mark delta 28.7 mm³ (>0).

## Known Issues

- `i notes/Notes/Final-Successful-Dimensions-For-Med-Core.md` has hallucinated dims (5 × 3.2 × 4.8 cm) — not edited (GATEWAY rule 6). Javier should delete/correct it.
- Alexandria not mounted → configured mark STL unavailable (see bug report).
- Standard 0.3mm clearance; not yet test-fitted on a printed part.

## What's Next

Javier reviews preview → approves → slice (PETG). No printing without per-job approval.

*— Claude*
