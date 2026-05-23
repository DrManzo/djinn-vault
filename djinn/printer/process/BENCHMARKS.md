---
title: Shape Benchmarks
tags: [printer, benchmarks, reference]
links: [PRINT-LOG, INTAKE, FILAMENT-PROFILES, error_log]
updated: 2026-05-23
---

# Shape Benchmarks

Reference library of known-good print results by shape type on the Ender-3 V3 Plus.
Each entry is established when a shape prints cleanly with documented settings.
Over time this becomes the ground truth for what this machine can produce.

**Related:** [[INTAKE]] | [[PRINT-LOG]] | [[FILAMENT-PROFILES]] | [[error_log]]

---

## How to Use

**Starting a new print:**
Find the closest shape below. Use the baseline settings as a starting point.

**After a clean print of a new shape:**
Add an entry here. Link back to the [[PRINT-LOG]] entry. Note any surprises.

**When a print degrades vs baseline:**
First check [[error_log]] quick-reference table. Then compare current settings to baseline entry here.

---

## Established Baselines

### Benchy — Calibration Boat

- **Print log:** [[PRINT-LOG#2026-05-23--benchy-diagnostic-baseline]]
- **File:** `3DBenchy-Ender-3 V3 Plus_14m28.gcode` (stock, Creality pre-sliced)
- **Material:** PLA / 210°C / 60°C bed
- **Result:** ✅ 185 layers clean. retx=0, inv=0 throughout. 14m 41s actual.
- **Significance:** Hardware health baseline. If Benchy fails, the problem is hardware or config — not the gcode. If Benchy passes and another file fails, it's the file.
- **Telemetry:** [[benchy_trace]]
- **Status:** ✅ Baseline established 2026-05-23

---

### Cylinder / Cup

- **Print log:** [[PRINT-LOG#2026-05-23--cup-geometry-proxy-cup]]
- **File:** `cup_geometry_creality_fixed.gcode`
- **Material:** PLA / 215°C / 60°C bed / 15% infill / 0.2mm layers
- **Key risk:** Fan ramp at layer 1→2 (PrusaSlicer-generated files). Keep fan OFF layer 1.
- **Result:** 🖨️ In progress — clean at 2.8h elapsed
- **Status:** ⏳ Baseline pending (in progress 2026-05-23)

---

## Pending Benchmarks — Stock Models

These files are already on the printer. Print each one, log it, and add a baseline here.
Run in order of shortest to longest for fastest benchmark coverage.

| File | Est. Time | Shape type | Priority |
|------|-----------|-----------|---------|
| `CRtestcube_Ender-3 V3 Plus_26m.gcode` | 26m | Calibration cube — dimensional accuracy | High |
| `Scraper-Ender-3 V3 Plus_34m.gcode` | 34m | Flat functional part | Medium |
| `Spool guider-part B 1213-Ender-3 V3 Plus_20m.gcode` | 20m | Small clip/bracket | Medium |
| `Phone_Stand_V2 by Layer_Adder-Ender-3 V3 Plus_1h.gcode` | 1h | Stand — overhang + flat base | Medium |
| `Spool guider-part A 1213-Ender-3 V3 Plus_1h4m.gcode` | 1h 4m | Curved bracket | Medium |
| `Cam-mount-Ender-3 V3 Plus_1h12m.gcode` | 1h 12m | Mount — thin walls + holes | Medium |
| `spoolholder-sidev2-Ender-3 V3 Plus_1h4m.gcode` | 1h 4m | Structural — large flat | Low |
| `top-spool-holder-Ender-3 V3 Plus_1h41m.gcode` | 1h 41m | Structural — large + overhangs | Low |
| `ksr_fdmtest_v4 by Autodesk&kickstart-Ender-3 V3 Plus_1h58m.gcode` | 1h 58m | FDM test — all shape types | High (do last, most comprehensive) |

---

## Shape Reference Index

As benchmarks are established, entries move from "pending" to "established" above.

| Shape type | Status | Notes |
|-----------|--------|-------|
| Calibration boat (Benchy) | ✅ Established | Hardware health check |
| Cylinder / cup | ⏳ In progress | Fan layer-1 risk |
| Calibration cube | ⏳ Pending | Dimensional accuracy reference |
| Flat functional (scraper, bracket) | ⏳ Pending | |
| Overhang | ⏳ Pending | |
| Bridge | ⏳ Pending | |
| Thin wall | ⏳ Pending | |
| Fine detail | ⏳ Pending | |
| FDM comprehensive test | ⏳ Pending | ksr_fdmtest covers most types |
