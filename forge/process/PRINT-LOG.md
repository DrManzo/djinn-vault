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

---

## 2026-05-23 — Puffco Proxy Tornado Recycler

| Field | Value |
|-------|-------|
| File | puffco_proxy_recycler.gcode |
| Source | `Proxy+Tornado+Recycler.3mf` (MakerWorld, Bambu profile) |
| Slicer | OrcaSlicer 2.3.2 — re-sliced from scratch (stripped Bambu macros) |
| Material | PLA |
| Hotend temp | 220°C |
| Bed temp | 55°C |
| Layer height | 0.16mm (user preference for detail on uptake tubes) |
| Walls | 4 (watertight chamber walls) |
| Infill | 15% gyroid |
| Top shells | 5 |
| Bottom shells | 4 |
| Supports | Normal auto, build-plate only, 25° threshold |
| Brim | 5mm (tall print — 219.5mm) |
| Est. time | ~13.7h |
| Outcome | ✅ Success (Javier confirmed print came out well) |
| Notes | Applied all cup debugging lessons: fan off first layer, preheat before homing, no Bambu macros. Model had 17 open edges originally — manifold repair applied during slice. |

---

## 2026-05-24 — Mario Pipe + Typhon's Forge Coins × 4

| Field | Value |
|-------|-------|
| File | model_job1.gcode |
| Source | `proxy_parts_mario_pipe.3mf` (Discord) + `coin_38_final.stl` × 4 |
| Slicer | PrusaSlicer (via djinn-model-slice) |
| Material | PLA |
| Hotend temp | 220°C |
| Bed temp | 55°C |
| Layer height | 0.2mm |
| Infill | 15% |
| Supports | YES (pipe: 20.3% faces >45° overhang) |
| Brim | None |
| Est. time | 3h 20m 43s |
| Filament | 59.83g |
| Outcome | 🖨️ In progress (started 2026-05-24) |
| Notes | Plate required pymeshlab decimation — coins at 1M faces each caused PrusaSlicer to silently drop the pipe (~202MB combined). Decimated to 15k faces each → 3.3MB plate → sliced correctly. |
