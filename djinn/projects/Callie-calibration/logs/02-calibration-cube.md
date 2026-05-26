# 02 — Calibration Cube (20×20×20mm)

## Purpose
Verify dimensional accuracy of X, Y, and Z axes. Adjust steps-per-mm if needed.

## Method
- **File:** `20mm_XYZ_EdgelessSafetyCalibrationCube.stl`
- **Slicer:** PrusaSlicer headless (via djinn-model-slice pipeline)
- **Temp:** Optimal from temperature tower test
- **Profile:** 0.20mm default, all speeds standard
- **Flow rate:** 100%

## Workflow
1. Queue via pipeline: `djinn-model-slice --temp <OPTIMAL_TEMP>`
2. Print
3. Measure X, Y, Z with calipers
4. Record deviation
5. Adjust steps/mm if outside ±0.2mm
6. Re-print to verify if adjusted

## Results
| Axis | Expected | Measured | Deviation | Steps/mm (before) | Steps/mm (after) |
|------|----------|----------|-----------|-------------------|------------------|
| X | 20.00mm | 20.00mm | 0.00mm | stock | stock |
| Y | 20.00mm | 20.00mm | 0.00mm | stock | stock |
| Z | 20.00mm | 20.00mm | 0.00mm | stock | stock |

## Adjustment Calculation
New steps/mm = Current steps/mm × (Expected / Measured)
- X: _____
- Y: _____
- Z: _____

## Photos
<!-- Insert photos here -->

## Notes
- [ ] Measure each axis 3 times, take average
- [ ] Check for elephant's foot on bottom
- [ ] Check for Z-banding
- [ ] Verify cube is square (measure diagonals)
- [ ] Update printer.cfg if adjusting steps/mm
