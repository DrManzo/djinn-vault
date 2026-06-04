# Callie Calibration Bench — Ender-3 V3 Plus

**Printer:** Ender-3 V3 Plus (codename: Callie/Calliope)
**Nozzle:** 0.4mm hardened steel
**Filament:** PLA
**Firmware:** Klipper (Nebula)
**Slicer:** OrcaSlicer 2.3.2 (GUI) + PrusaSlicer (headless pipeline)
**Moonraker:** http://192.168.1.113:7125

## Benchmark Plan

### Phase 1 — Baseline Calibration
| # | Test | Purpose | Status |
|---|------|---------|--------|
| 1 | Temperature Tower (180-230°C) | Find PLA sweet spot | pending |
| 2 | Calibration Cube (20mm) | Dial steps/mm | pending |
| 3 | First Layer Square (200×200mm) | Z-offset + mesh leveling | pending |

### Phase 2 — Speed & Flow
| # | Test | Purpose | Status |
|---|------|---------|--------|
| 4 | CNC Kitchen Extrusion Benchmark | Max volumetric flow | pending |
| 5 | SpeedBoat Benchy (×3 speeds) | Ringing, bridging, hull quality | pending |
| 6 | Vibration/Ringing Tower | Input shaping validation | pending |

### Phase 3 — Quality
| # | Test | Purpose | Status |
|---|------|---------|--------|
| 7 | Overhang Tower (20-80°) | Part cooling tune | pending |
| 8 | Bridging Test | Bridge speed + fan | pending |
| 9 | Fine Detail Torture Test | Resolution ceiling | pending |

### Phase 4 — Dimensional Accuracy
| # | Test | Purpose | Status |
|---|------|---------|--------|
| 10 | Tolerance/Clearance Gauge | Min clearance for functional parts | pending |
| 11 | Functional Parts Test | Hinge/snap-fit/threaded usability | pending |

## Slicer Starting Points (PLA)
| Setting | Value |
|---------|-------|
| Print Temp | TBD from temp tower |
| Bed Temp | 60°C |
| Part Cooling | 100% after layer 3 |
| Initial Speed | 100mm/s |
| Layer Height | 0.2mm for benchmarks |
| Flow Rate | 100% (adjust after cube) |

## Results
Final tuned config stored in `results.md`.

— djinn
