# 01 — Temperature Tower (180-230°C)

## Purpose
Find the optimal printing temperature for the current PLA filament.

## Run Log
| Date | Gcode | Duration | Filament | Result |
|------|-------|----------|----------|--------|
| 2026-05-25 | `temp-tower-v3.gcode` | 62.5 min | 3.4m | **COMPLETE** |

## Method
- **File:** `temperature-tower-with-rounds-_v003.stl`
- **Slicer:** PrusaSlicer + Creality macros + M104 temp changes
- **Initial temp:** 205°C (START_PRINT default)
- **Zones:** M104 S220, S210, S200, S190 at layer boundaries

## Results
| Zone | Z Range | Temp °C | Layer Adhesion | Stringing | Surface Quality | Notes |
|------|---------|---------|---------------|-----------|-----------------|-------|
| 1 (bottom) | 0.3-5.9mm | 205 | | | | |
| 2 | 5.9-12.9mm | 220 | | | | |
| 3 | 12.9-19.9mm | 210 | | | | |
| 4 | 19.9-26.9mm | 200 | | | | |
| 5 (top) | 26.9-36.1mm | 190 | | | | |

**Optimal temp:** _____ °C (fill in after inspection)

## Notes
- [ ] Inspect each zone boundary — should see transition marks
- [ ] Best temp = cleanest surface, least stringing, good adhesion
- [ ] Set `PLA_TEMP=<optimal>` before running calibration cube
