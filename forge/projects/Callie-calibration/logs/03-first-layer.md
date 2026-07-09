# 03 — First Layer / Large Flat Square (200×200mm)

## Purpose
Dial Z-offset and validate CR Touch mesh leveling consistency across the full 300×300mm bed.

## Method
- **File:** `first_layer_200x200mm.stl` (generated, 200×200×1mm flat square)
- **Slicer:** PrusaSlicer headless (via djinn-model-slice pipeline)
- **Temp:** Optimal from temperature tower
- **Layer height:** 0.3mm (first layer)
- **Speed:** 30mm/s first layer
- **Bed temp:** 60°C

## Workflow
1. Queue via pipeline
2. Print — watch first layer carefully
3. Inspect extrusion quality across entire print area
4. Look for: gaps, ridges, inconsistent squish
5. Adjust Z-offset if needed
6. Repeat until perfect

## Z-Offset
| Attempt | Z-offset value | Observations |
|---------|---------------|--------------|
| 1 | | |
| 2 | | |
| 3 | | |

**Final Z-offset:** _____ mm

## Bed Mesh Notes
- Center height: _____
- Corners (check visually):
  - Front-left: _____
  - Front-right: _____
  - Back-left: _____
  - Back-right: _____

## Photos
<!-- Insert photos here -->

## Notes
- [ ] Print with first layer at slow speed (20-30mm/s)
- [ ] Watch the first pass — should lay down smoothly with slight squish
- [ ] After 5-10 layers, check for consistent surface finish
- [ ] Run CR Touch bed mesh calibration if results are uneven
