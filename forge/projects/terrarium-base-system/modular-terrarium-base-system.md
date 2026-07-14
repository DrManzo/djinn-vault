---
title: Modular Terrarium Base System
status: concept-validated
phase: 3D-Printing / Terrarium Line
created: 2026-07-13
tags: [3d-printing, terrariums, petg, parametric, openscad, forge]
related:
  - "[[djinn-generate-3d]]"
  - "[[Phase 9 - Printer Integration]]"
  - "[[Typhon Forge]]"
---

# Modular Terrarium Base System

## Concept

One universal 3-part base system for mini terrariums. Container shape/material varies per build (apothecary jar, PETG vase-mode print, dome, etc.) — the base mechanics stay constant. Designed to scale from one-off builds to small commission batches without redesigning from scratch each time.

## Fixed rules (never change)

- **Stack order, bottom to top:** reservoir → perforated riser → planting shelf → container
- **Connector spec:** bayonet twist-lock, 3 lugs per ring, 8mm wide, 120° apart, quarter-turn to lock. Identical on every ring regardless of diameter — any part fits any other part in the system.
- **Wall thickness:** reservoir (Part 3) minimum 2.4mm / 6 perimeters at 0.4mm nozzle — only part that holds standing water long-term. Parts 1–2 can run thinner (~1.2mm / 2 perimeters).
- **Channel alignment:** Part 2's perforations line up directly under Part 1's slots so water drops straight through instead of pooling visibly.

## Variable per terrarium (parametric inputs)

- Outer diameter (matched to container mouth)
- Overall stack height / reservoir depth (deeper for closed/moss builds, shallow for open/succulent)
- Outer profile shape (round, hex, square — bayonet lug logic scales proportionally)

## The 3 parts

1. **Part 1 — Planting shelf.** Holds soil/moss. Slotted floor, no basin.
2. **Part 2 — Perforated riser.** False floor. Channels aligned to Part 1 above.
3. **Part 3 — Water reservoir.** Sealed base, holds standing water. The "hydro" layer — roots wick moisture up through Parts 1–2.

Optional: side viewing port in Part 3 to check water level without disassembly.

## Print notes

- Clear PETG for container + Part 1 (visible layer lines become part of the aesthetic rather than a flaw to hide).
- Part 3 can be opaque PETG — hidden under soil.
- Parts 1 & 2 print flat (floor down) for slot accuracy.
- Part 3 prints upright — vase mode if no side port is included (single continuous wall, no seam, best leak resistance).

## Status / open items

- [ ] Measure actual apothecary jar mouth diameter → plug into parametric model
- [ ] First test print at default 100mm diameter to validate bayonet fit before scaling
- [ ] Decide per-terrarium reservoir depth (open/succulent vs closed/moss profile)
- [ ] Test clear PETG vase-mode container for leak resistance vs glass baseline

## Reference diagrams

Two working diagrams produced during design pass (top/front/exploded/cross-section views): see attached SVGs in this folder —
`terrarium-base-concept.svg` (initial cross-section) and `terrarium-base-multiview.svg` (4-view technical sheet).

## Parametric model

See [[terrarium_base.scad]] — OpenSCAD file with diameter, height, and shape as top-level variables. New terrarium = new parameter values, not a new design.

## Meshy AI / arbitrary container pipeline

For containers generated in Meshy (or sculpted in Blender) that need to mate with the base system, use [[djinn_terrarium_fit_agent.py]] — same pattern as `djinn_makers_mark_agent.py`:

**Pipeline:** Meshy shell generation → Blender cleanup → `djinn_terrarium_fit_agent.py` (auto-detects base diameter, generates matching ring via `terrarium_base.scad`, booleans it on via manifold3d) → `validate_and_fix_engraving.py` (final manifold check) → slicer

Rationale: Meshy is good for organic/decorative shell geometry, not for precision connector fit — AI-generated meshes are rarely manifold and have no concept of bayonet tolerances. The fit agent keeps `terrarium_base.scad` as the single source of truth for connector spec and only asks Meshy/Blender for the part that's actually aesthetic.

```bash
python djinn_terrarium_fit_agent.py \
    --input meshy_container_cleaned.stl \
    --output container_fitted.stl \
    --ring-scad terrarium_base.scad \
    --part 1 \
    --mode union
```

### Open items
- [ ] Confirm `manifold3d` + `trimesh` installed on Salomon
- [ ] Test `detect_base_diameter()` against a real Meshy export (assumes Z-up, flat-bottomed mesh — may need reorientation step first)
- [ ] Decide whether fit agent should call `validate_and_fix_engraving.py` directly as a subprocess instead of just recommending it
