---
title: TF's Mini Vase Collection — Job Report
tags: [djinn, print, job4, mini-vases, reference]
related: [[print-job]] | [[SUPPORT-GUIDE]] | [[QUEUE]]
---

# TF's Mini Vase Collection — Job #4

**Date:** 2026-05-31
**Agent:** Salomon
**Status:** Sliced, ready to print

---

## Models

| Name | Source | W x D x H (mm) | Volume | Engraved |
|------|--------|----------------|--------|----------|
| Double Spiral Vase | `Mini+Vase+Tray.zip` | 36.7 x 36.8 x 50.0 | 12.59 cm³ | ✅ TF anvil |
| Spiral Vase | `Mini+Vase+Tray.zip` | 39.7 x 39.7 x 50.0 | 11.95 cm³ | ✅ TF anvil |
| Straight Vase | `Mini+Vase+Tray.zip` | 38.0 x 38.0 x 49.8 | 13.94 cm³ | ✅ TF anvil |

**Total plate:** ~145mm wide, centered on 300mm bed

---

## Settings

| Setting | Value |
|---------|-------|
| Profile | Standard (walls=3, infill=15% gyroid) |
| Layer height | 0.2mm |
| Total layers | 250 |
| Supports | NO |
| Brim | 5mm (default) |
| Material | PLA (210°C nozzle / 55°C bed) |
| Estimated time | 5h 40m |
| Estimated filament | ~40.4g |
| Slicer | OrcaSlicer 2.3.2 |
| Gcode flavor | Klipper |

---

## Workflow Executed

### 1. Extract & Analyze
```bash
unzip Mini+Vase+Tray.zip → 4 STLs (3 vases + tray)
trimesh analyze → dims, volume, overhang %, base face orientation
```

### 2. Reorient (stand upright)
Original STLs had height (50mm) on Y axis, lying on side. Base face normal = (0, -1, 0).
```python
# Rotate +90° around X to stand on base
R = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])
mesh.apply_transform(R)
# Translate so bottom_z = 0
mesh.vertices[:, 2] -= mesh.vertices[:, 2].min()
```

### 3. Engrave Maker's Mark (bottom)
```python
# Load TF anvil (15mm, logo faces +Z)
anvil = trimesh.load("tf_anvil_traced_15mm.stl")
# MIRROR X so engraving reads correctly when viewed from below
anvil.vertices[:, 0] = -anvil.vertices[:, 0]  # mirror X
anvil.faces = anvil.faces[:, [0, 2, 1]]        # reverse winding
# Position on vase bottom, sunk 0.15mm deep
cut.apply_translation([center_x, center_y, bottom_z + 0.15])
# Boolean subtract
engraved = trimesh.boolean.difference([vase, cut], engine="manifold")
```

### 4. Position on Plate
```python
spacing = 10mm between vases
start_x = bed_center - total_width / 2
# Center Y on bed
```

### 5. Slice
```bash
OrcaSlicer --load-settings "machine_profile.json;process_profile.json" \
  --arrange 0 --slice 0 \
  --outputdir prints/... \
  vase1.stl vase2.stl vase3.stl
```

---

## Bugs Discovered

### BUG-001: Maker's mark engraving reversed on bottom surfaces
- **Root cause:** STL logo faces +Z, boolean-subtracted into bottom. Viewed from below (-Z), engraving reads mirror image.
- **Fix:** Mirror X axis before subtraction (`vertices[:, 0] = -vertices[:, 0]` + reverse winding).
- **Status:** Open — TASK-004 assigned to Claude for permanent fix + configurable mark.
- **Report:** `logs/reports/2026-05-31_bug-maker-s-mark-engraving-reads-reversed-on-bottom-surfaces.md`

---

## Areas for Automation / Improvement

### High Priority
- [ ] **Configurable maker's mark** — Store mark STL path in `~/.config/djinn/makers-mark.json` with mirror flag. TASK-004.
- [ ] **Auto-mirror on bottom engrave** — Any agent engraving on a bottom surface should automatically mirror the cut.
- [ ] **Multi-STL plate slicing** — Create a helper that positions N models on a bed with configurable spacing, then passes to OrcaSlicer.

### Medium Priority
- [ ] **Vase mode detection** — If vase has no overhangs and thin walls, suggest spiral vase mode (single perimeter, saves time/filament).
- [ ] **Brim sizing** — Auto-calculate brim width based on model height/width ratio.
- [ ] **Batch engraving** — Apply maker's mark to N models in one command instead of loop.

### Low Priority
- [ ] **Orientation auto-detect** — Detect which axis is the base (largest flat face) and suggest rotation.
- [ ] **Plate preview** — Generate a PNG thumbnail of the sliced plate for agent review.

---

## Files

```
queue/mini-vases_job4.gcode           ← final gcode (ready to print)
prints/2026-05-31_TFs-Mini-Vase-Collection/
  job-report.md                       ← this file
```

---

*— Salomon, 2026-05-31*
