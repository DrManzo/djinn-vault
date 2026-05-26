# 01 — Temperature Tower (180-230°C)

## Purpose
Find the optimal printing temperature for the current PLA filament before running any other calibration tests.

## Method
- **File:** `temperature-tower-with-rounds-_v003.stl`
- **Slicer:** OrcaSlicer GUI — Calibration → Temperature menu
- **Profile:** 0.20mm Standard @Creality Ender3V3Plus 0.4 nozzle
- **Bed temp:** 60°C
- **Cooling:** 100% after layer 3
- **Range:** 180°C (top) to 230°C (bottom), 5°C increments

## Workflow
1. Open OrcaSlicer
2. Load `temperature-tower-with-rounds-_v003.stl`
3. Select printer profile: Creality Ender-3 V3 Plus 0.4 nozzle
4. Select process: 0.20mm Standard @Creality Ender3V3Plus
5. Click Calibration → Temperature → select tower STL
6. Set range: 180-230°C, 5°C steps
7. Slice → Export gcode → Upload via Moonraker → Print

## Results
| Temp (°C) | Layer Adhesion | Stringing | Surface Quality | Notes |
|-----------|---------------|-----------|-----------------|-------|
| 230 | | | | |
| 225 | | | | |
| 220 | | | | |
| 215 | | | | |
| 210 | | | | |
| 205 | | | | |
| 200 | | | | |
| 195 | | | | |
| 190 | | | | |
| 185 | | | | |
| 180 | | | | |

**Optimal temp:** _____ °C

## Photos
<!-- Insert photos here -->

## Notes
- [ ] Inspect each temperature block for stringing
- [ ] Check layer adhesion — does the part hold together?
- [ ] Surface quality — glossy vs matte, layer lines visible?
- [ ] Set print temp to optimal value before next test
