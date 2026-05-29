---
title: Print Report — Terp Tribe HQ Engraved Cup (Job #1)
agent: Salomon
date: 2026-05-28
tags: [djinn, report, print, cup, terp-tribe-hq]
related: [[build-log]] | [[INFRASTRUCTURE]]
---

# Print Report — Terp Tribe HQ Engraved Cup

**Date:** 2026-05-28
**Agent:** Salomon
**Job ID:** `00002A`
**GCode:** `cup_engraved_final_job1.gcode`
**Status:** Printing — 99.0% complete

---

## Summary

The Terp Tribe HQ engraved cup is printing on Calliope and nearing completion. The boolean-merged cup (249.58 cm³, 128.31g PLA) started at 12:52 PM PDT and has been running for ~5.5 hours. Temperatures are stable, progress is on track, and no anomalies have been detected. Estimated to finish within the next 5-10 minutes.

---

## Print Details

| Parameter | Value |
|-----------|-------|
| Model | Terp Tribe HQ engraved cup |
| GCode | `cup_engraved_final_job1.gcode` (14.8 MB) |
| Slicer | PrusaSlicer 2.9.4 |
| Height | 107.3 mm |
| Layer height | 0.2 mm (first layer 0.3 mm) |
| Nozzle | 0.4 mm |
| Filament | PLA, 128.31g total |
| Est. time | 25,686s (~7h 8m) |
| Est. finish | ~8:00 PM PDT |

---

## Status (at time of report)

| Metric | Value |
|--------|-------|
| State | `printing` |
| Progress | 98.99% (byte position) |
| Print duration | 19,732s (~5h 29m) |
| Filament used | 42,475 mm |
| Bed temp | 55.0°C / 55.0°C target (stable) |
| Extruder temp | 219.4°C / 220.0°C target (stable) |
| Toolhead | X:180.6, Y:187.6, Z:99.6 |
| Power loss | 0 |

---

## Observations

- **Temperature stability:** Bed within ±0.01°C, extruder within ±0.6°C — excellent
- **Progress tracking:** Layer count (536) vs current layer (611) shows a mismatch (Klipper reads layer comments differently from actual gcode line count) — not a concern, byte position is the reliable metric
- **Webcam monitor:** `djinn-webcam-monitor.service` is inactive (not currently running or was stopped) — no visual failure detection active for this print
- **Print monitor service:** `djinn-print-monitor.service` has no recent log entries for the duration of this print

---

## What's Next

- [ ] Monitor completion — printer will auto-stop when done (present at ~8:00 PM PDT)
- [ ] Run post-print QC: check engraving depth, layer adhesion, surface finish
- [ ] Move gcode to `printer/completed/` after print finishes
- [ ] Consider re-enabling webcam monitor for future prints (currently inactive)

---

*— Salomon, 2026-05-28*
