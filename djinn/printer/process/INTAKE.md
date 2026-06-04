---
title: Print Intake SOP
tags: [printer, process, sop]
links: [PRINT-LOG, BENCHMARKS, FILAMENT-PROFILES, error_log, benchy_trace]
updated: 2026-05-23
---

# Print Intake SOP

Standard process for taking any 3D print file and getting it reliably running on the Ender-3 V3 Plus.
Covers: external downloads, pre-sliced gcode, raw geometry, stock printer models, personal designs.

**Related:** [[PRINT-LOG]] | [[BENCHMARKS]] | [[FILAMENT-PROFILES]] | [[FILAMENT-TEST]] | [[error_log]]

---

## Step 1 — Identify the File Type

| Source | Format | Action |
|--------|--------|--------|
| External (Printables, Thingiverse, etc.) | STL / OBJ / 3MF | → Reslice (Step 2) |
| External | Pre-sliced gcode, Creality slicer | → Validate (Step 3), skip to Step 4 |
| External | Pre-sliced gcode, other slicer | → Validate + patch (Step 3) |
| Stock printer models | Pre-sliced gcode | → Upload, log in [[PRINT-LOG]], record result in [[BENCHMARKS]] |
| Personal design | STL from CAD | → Reslice (Step 2) |

---

## Step 2 — Reslice (for geometry files)

**Slicer:** Creality Print (preferred) — produces compatible start sequences and fan behavior.

**Profile: Ender-3 V3 Plus — PLA baseline**

| Setting | Value |
|---------|-------|
| Nozzle diameter | 0.4 mm |
| Layer height | 0.2 mm |
| Walls | 3 |
| Infill | 15% (decorative) / 20–40% (functional) |
| Hotend temp | 215°C (PLA) |
| Bed temp | 60°C (PLA) |
| Fan — layer 1 | OFF (M106 S0) |
| Fan — layer 3+ | 100% |
| Outer wall speed | 40 mm/s |
| Inner wall speed | 50 mm/s |
| Travel speed | 150 mm/s |
| Supports | Tree (auto), threshold 30° |
| Pressure advance | K=0.042 |

See [[FILAMENT-PROFILES]] for material-specific adjustments.

---

## Step 3 — Gcode Validation

Run before sending any external gcode to the printer. Flag and fix any ❌ before printing.

| Check | What to verify | Pass |
|-------|---------------|------|
| Start sequence | `M190 Sxx` (bed wait) before `START_PRINT` | ✅ / ❌ |
| Hotend preheat | `M104 Sxxx` before `START_PRINT` | ✅ / ❌ |
| START_PRINT call | `START_PRINT EXTRUDER_TEMP=xxx BED_TEMP=xxx` | ✅ / ❌ |
| Fan — layer 1 | No `M106 S[>0]` before layer 2 | ✅ / ❌ |
| Fan — layer 2 ramp | Value ≤ S128 (50%) at first fan-on | ✅ / ❌ |
| Pressure advance | `M900 K0.042000` present after START_PRINT | ✅ / ❌ |

**Known bad pattern:** PrusaSlicer ramps fan to `M106 S155.55` at the brim→layer 1 boundary. This causes a deterministic EMI spike on nozzle_mcu, triggering `key564`. Always patch to `M106 S0` for layer 1. See [[error_log]] for full root cause.

**Quick patch (replace aggressive layer-1 fan ramp):**
```bash
sed -i 's/M106 S15[0-9]\.[0-9]*/M106 S0/g' yourfile.gcode
```

---

## Step 4 — Pre-Print Checklist

- [ ] File uploaded to printer (Moonraker: http://192.168.1.113:7125 or via Telegram `/print <filename>`)
- [ ] Correct filament loaded and colour/material noted for log
- [ ] Bed clean — IPA wipe if last print had adhesion issues
- [ ] printer.cfg verify_heater settings: `check_gain_time:120`, `max_error:999`, `hysteresis:20`
- [ ] Log entry started in [[PRINT-LOG]] (file, material, slicer, estimated time)

---

## Step 5 — During Print

- Monitor first layer for adhesion and fan behaviour
- If using Telegram bot: send `/print_status` to check state
- For new files or materials: watch nozzle_mcu stats in Klippy logs for rising `retransmit_seq`
- Any failure → document in [[error_log]] before next attempt

---

## Step 6 — Post-Print

- Update [[PRINT-LOG]] entry with actual time, outcome, and notes
- If shape is a new type → add baseline entry to [[BENCHMARKS]]
- If new filament → add or update profile in [[FILAMENT-PROFILES]]
- If failure → root cause in [[error_log]], fix in INTAKE before next run

---

## Reference

| Doc | Purpose |
|-----|---------|
| [[PRINT-LOG]] | Every print: outcome, settings, duration |
| [[BENCHMARKS]] | Shape reference library — what a clean print looks like |
| [[FILAMENT-PROFILES]] | Per-material temp, fan, retraction, flow settings |
| [[FILAMENT-TEST]] | Protocol for characterising a new filament |
| [[error_log]] | All failures, root causes, and fixes |
| [[benchy_trace]] | Hardware health baseline (retx=0, inv=0 all 185 layers) |
| [[print_monitor_log]] | Raw telemetry — minute-by-minute during prints |
