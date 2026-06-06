---
title: Session Report — djinn-detect-surfaces build + Camood surface scan
agent: Claude
date: 2026-06-05
tags: [djinn, report, 3dprint, engraving, tool-build, camood]
related: [[build-log]] [[decision-log]]
---

# Session Report — djinn-detect-surfaces + Camood Surface Scan

**Date:** 2026-06-05
**Agent:** Claude
**Session type:** Build / Debug
**Trigger:** Original Camood engraving script was using bbox depth instead of actual face position, causing boolean subtract to miss or undershoot. Original STL already has manufacturer branding on the back — needed a pre-flight scanner before touching geometry.

---

## Summary

Built `djinn-detect-surfaces`, a pre-flight surface scanner that fires 20×20 ray grids in all 6 cardinal directions to find actual flat engravable panels (not bounding box). Ran it on the Camood STL, confirmed the back panel sits at Y=51.305mm (2.79mm inside the bbox), and confirmed the manufacturer's "Terp Tribe" branding is already on the back — so no additional text is needed. Final `Camood_TTHQ_engraved.stl` (original + TF anvil maker's mark on bottom) is the correct file.

---

## What Was Built or Changed

- **`~/.local/bin/djinn-detect-surfaces`** — new CLI tool, chmod +x, executable system-wide
  - Ray-cast pass: 20×20 grid per direction, 6 directions = 2,400 rays
  - Histogram-peak algorithm: 0.5mm bins, dominant plane extraction, ±1mm local flatness std
  - Curvature pass: `mesh.vertex_defects` (Gaussian curvature per vertex), clusters flat zones by normal bucket
  - Outputs `surfaces.json` consumed by `djinn-model-text-engrave --surface-data`
- **`~/printer-files/library/originals/terp-tribe/Camood_surfaces.json`** — scan result

---

## Technical Decisions

**Histogram-peak instead of median/std — Why:** The Camood is a curved body with a flat inset panel. The global std across all 303 back-face hits was 8.89mm because the surrounding curved geometry pollutes the average. Peak-bin approach extracts the dominant flat plane correctly: back panel local std = 0.229mm after filtering to ±1mm of peak.

**`mesh.vertex_defects` not `mesh.vertex_defects()` — Why:** In this trimesh version, `vertex_defects` is a property (returns ndarray directly), not a method. Calling with `()` raises `'numpy.ndarray' object is not callable`.

**Ray origin direction fix (>`0`, not `<0`) — Why:** Original code placed ray origins on the wrong side of the model — rays shooting away from it, yielding 0 hits. Fix: place origin on the far side in the direction of the face normal, shoot inward (`-d`).

**No additional text on Camood — Why:** Javier confirmed original STL already has manufacturer branding engraved on the back. Current `Camood_TTHQ_engraved.stl` (original + TF anvil bottom mark) is the correct final file.

---

## Files Created or Modified

```
~/.local/bin/djinn-detect-surfaces                         ← new tool, ray-cast + curvature surface scanner
~/printer-files/library/originals/terp-tribe/Camood_surfaces.json  ← scan output
```

---

## Tests & Validation

```
djinn-detect-surfaces "The Terp Tribe - Camood.stl"

── Ray-cast pass (6 directions × 400 rays) ──
  back    : 303/400 hits  peak@51.3mm (29%)  local_std=0.229mm  area=2669mm²  → ✓ ENGRAVABLE
  front   : 303/400 hits  peak@15.7mm (24%)  local_std=0.133mm  area=2335mm²  → ✓ ENGRAVABLE
  right   : 217/400 hits  peak@19.2mm (35%)  local_std=0.167mm  area=3601mm²  → ✓ ENGRAVABLE
  left    : 217/400 hits  peak@-19.3mm (35%)  local_std=0.167mm  area=3601mm²  → ✓ ENGRAVABLE
  top     : 304/400 hits  peak@99.8mm (40%)  local_std=0.142mm  area=2355mm²  → ✓ ENGRAVABLE
  bottom  : 304/400 hits  peak@0.2mm (53%)   local_std=0.000mm  area=3602mm²  → ✓ ENGRAVABLE (TF anvil)

6 surfaces detected, 6 engravable
```

Key geometry confirmed:
- Back panel actual depth: Y=51.305mm (bbox=54.09mm, 2.79mm inset) — explains old script miss
- Bottom: perfectly flat (std=0.000mm) — TF anvil mark placement is correct

---

## Known Issues / Caveats

- `front` detection (Y=15.73mm, 69.8mm inside bbox front) is likely an interior chamber wall visible through the mouthpiece opening — not a reliable exterior engraving target. No warning generated; future improvement could flag faces with very large bbox offset.
- pyembree not installed — ray_triangle backend used (~100× slower). For large meshes, install `pip install pyembree` for production speed.
- Curvature pass runs but finds no new surfaces beyond raycast on this model (18k faces, all flat-panel geometry).

---

## What's Next

- [ ] Job 9 failed at ~107mm height (physical cable disconnect on nozzle_mcu) — Javier must inspect toolhead cable at ~107mm before restarting print
- [ ] When Job 9 restarts, confirm 4× Camood prints complete — update `camood.md` and print-queue.json
- [ ] TASK-027: Fill SHIPPO_API_KEY in `~/.config/forge/shop.env`

---

*— Claude, 2026-06-05*
