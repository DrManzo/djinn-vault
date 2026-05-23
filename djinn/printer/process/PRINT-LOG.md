---
title: Print Log
tags: [printer, log]
links: [INTAKE, BENCHMARKS, FILAMENT-PROFILES, error_log]
updated: 2026-05-23
---

# Print Log

One entry per print job. Outcome, settings, and notes.
Raw telemetry lives in [[print_monitor_log]]. This is the human+AI readable record.

**Related:** [[INTAKE]] | [[BENCHMARKS]] | [[FILAMENT-PROFILES]] | [[error_log]]

---

## Entry Template

```markdown
## YYYY-MM-DD — filename.gcode

| Field | Value |
|-------|-------|
| File | filename.gcode |
| Source | Printables / Thingiverse / personal / stock |
| Slicer | Creality / PrusaSlicer / OrcaSlicer / other |
| Material | PLA / PETG / TPU / etc. |
| Brand | (filament brand if known) |
| Hotend temp | °C |
| Bed temp | °C |
| Layer height | mm |
| Infill | % |
| Est. time | h |
| Actual time | h |
| Outcome | ✅ Success / ❌ Failed / ⚠️ Partial / 🖨️ In progress |
| Failure mode | (if applicable — link to [[error_log]] entry) |
| Notes | |

Benchmark: [[BENCHMARKS#anchor]] (if this establishes or updates a shape baseline)
```

---

## 2026-05-23 — Benchy (diagnostic baseline)

| Field | Value |
|-------|-------|
| File | 3DBenchy-Ender-3 V3 Plus_14m28.gcode |
| Source | Stock (Creality pre-sliced) |
| Slicer | Creality |
| Material | PLA |
| Brand | Unknown (stock spool) |
| Hotend temp | 210°C |
| Bed temp | 60°C |
| Layer height | — |
| Infill | — |
| Est. time | 14m 28s |
| Actual time | 14m 41s |
| Outcome | ✅ Success |
| Failure mode | — |
| Notes | Diagnostic print to prove hardware health after nozzle_mcu EMI investigation. retx=0, inv=0 all 185 layers. Hotend held ±0.6°C throughout. See [[benchy_trace]] for full per-layer trace. |

Benchmark: [[BENCHMARKS#benchy--calibration-boat]]

---

## 2026-05-23 — Cup geometry (proxy cup)

| Field | Value |
|-------|-------|
| File | cup_geometry_creality_fixed.gcode |
| Source | Personal — extracted from cup.3mf (Puffco Proxy), geometry only |
| Slicer | Creality (patched from PrusaSlicer source) |
| Material | PLA |
| Brand | Unknown (stock spool) |
| Hotend temp | 215°C |
| Bed temp | 60°C |
| Layer height | 0.2mm |
| Infill | 15% |
| Est. time | ~5.8h |
| Actual time | In progress |
| Outcome | 🖨️ In progress (~2.8h elapsed, clean) |
| Failure mode | — (previous attempts failed — see [[error_log]]) |
| Notes | Preceded by 6 failed attempts across cup_geometry_klipper_patched.gcode. Root cause: PrusaSlicer fan ramp at layer 1→2 + tight verify_heater. Fixed by patching gcode and relaxing verify_heater. This file is the resolved version. |

Benchmark: [[BENCHMARKS#cylinder--cup]]
