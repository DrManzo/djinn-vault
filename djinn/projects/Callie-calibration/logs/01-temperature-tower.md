# 01 — Temperature Tower (180-230°C)

## Purpose
Find the optimal printing temperature for the current PLA filament before running any other calibration tests.

## Method
- **File:** `temperature-tower-with-rounds-_v003.stl`
- **Slicer:** PrusaSlicer 2.9.4 (headless) + gcode post-process for temp changes
- **Profile:** 0.20mm, PLA, 60°C bed
- **Cooling:** 100% after layer 3
- **Gcode fix:** Creality START_PRINT/END_PRINT macros injected
- **Zone temps:** 230°C (bottom) → 190°C (top), 5 zones, ~36mm tall

## Run
| Date | Gcode | Status |
|------|-------|--------|
| 2026-05-25 | `temp-tower-fixed.gcode` | **PRINTING** |

## Results
| Temp (°C) | Layer Adhesion | Stringing | Surface Quality | Notes |
|-----------|---------------|-----------|-----------------|-------|
| 230 | | | | |
| 220 | | | | |
| 210 | | | | |
| 200 | | | | |
| 190 | | | | |

**Optimal temp:** _____ °C

## Photos
<!-- Insert photos here -->

## Notes
- [ ] Wait for print to complete (~1-2 hrs)
- [ ] Inspect each temperature zone for stringing
- [ ] Check layer adhesion — does the part hold together?
- [ ] Surface quality — glossy vs matte, layer lines visible?
- [ ] Set print temp to optimal value before next test (cube)
