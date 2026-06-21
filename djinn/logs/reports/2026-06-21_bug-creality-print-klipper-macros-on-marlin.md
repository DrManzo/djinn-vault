---
title: Bug — Creality Print V7 gcode contains Klipper macros, fails silently on Marlin
date: 2026-06-21
severity: high
status: documented
system: Penelope/Creality Print
tags: [djinn, bug, penelope, klipper, marlin, gcode, creality-print]
---

# Bug — Creality Print V7 gcode contains Klipper macros, fails silently on Marlin

**Date:** 2026-06-21
**Severity:** High
**Status:** Documented (workflow rule enforced)
**System:** Penelope (Ender 3 Pro / Marlin) vs Calliope (Ender 3 V3 Plus / Klipper)

## Symptom

Gcode sliced in Creality Print V7 uploaded to Penelope via OctoPrint. Print appears to start but no material deposits. Bed target shows 0°C. Hotend stays cold. Print "runs" but nothing happens.

## Root Cause

Creality Print V7 slices assuming a Klipper firmware target. The start sequence contains Klipper-specific macros:

```gcode
M140 S0          ; set bed to 0
M104 S0          ; set hotend to 0
START_PRINT EXTRUDER_TEMP=220 BED_TEMP=65   ; Klipper macro — heats both
SET_VELOCITY_LIMIT ACCEL=2000 ACCEL_TO_DECEL=500
SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=8
EXCLUDE_OBJECT_DEFINE NAME=...
EXCLUDE_OBJECT_START NAME=...
```

Marlin firmware silently ignores unknown commands. `START_PRINT` never executes. Temps stay at 0. Retraction was also 0.6mm (Calliope direct drive) instead of 5.5mm (Penelope Bowden).

## Fix / Rule

**Penelope must only be sliced with OrcaSlicer using Penelope-specific profiles.**

Creality Print gcode is Calliope-only. Never send it to Penelope.

Pipeline for Penelope:
1. STL → `djinn-model-mark` → marked STL
2. OrcaSlicer + `Penelope-Standard*.json` process + `Penelope-PLA.json` filament
3. Upload via `djinn-penelope upload` → print via `djinn-penelope print`

## Lesson

Creality Print V7 is tightly coupled to Klipper. The two machines (Calliope = Klipper, Penelope = Marlin) require completely separate slicing pipelines. Never cross-send gcode between them.

*— Claude, 2026-06-21*
