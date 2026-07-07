---
title: Bug Report — Bambu Studio Injects M981/M624/M625 Even with klipper gcode_flavor
agent: Claude
date: 2026-07-06
tags: [djinn, bug, iris, bambu-studio, klipper, gcode]
related: [[2026-07-06_iris-profile-fix-fleet-up]]
---

# Bug Report — Bambu Studio Injects M981/M624/M625 Even with klipper gcode_flavor

**Date:** 2026-07-06
**System:** Iris (AD5X, zmod/Klipper, 192.168.1.50) + Bambu Studio 02.07.01.62
**Severity:** High — every print crashes without fix
**Status:** Fixed (Klipper no-op macros + time_lapse_gcode override)

---

## What Happened

Every gcode sliced with Bambu Studio using the Iris profile crashed on Klipper with either:
- `Unknown command: M981` — immediately after START_PRINT (line ~612)
- `Move out of range: -48.200 128.232` — at first layer change (line ~1630)
- `Unknown command: M624` / `Unknown command: M625` — at every layer change throughout

Prints with gcode sliced from the `AD5X Iris (zmod)` standalone profile worked fine.

---

## Root Cause

Three separate injection sources, all coming from `Iris.json` inheriting `Bambu Lab A1 0.4 nozzle`:

1. **M981** — Bambu spaghetti detector. Injected as a printer feature by Bambu Studio regardless of `gcode_flavor`. Setting `gcode_flavor: klipper` does NOT suppress it.

2. **M624 / M625** — Bambu AMS layer markers. Injected at every layer change by Bambu Studio's internal layer code. Also not suppressed by `gcode_flavor: klipper`.

3. **`time_lapse_gcode`** — Inherited from A1 parent profile. Contains `G1 X-48.2 F3000` (Bambu A1 center-origin X for timelapse shutter position). On Iris corner-origin 0–215mm bed, this is out of range. Also contains M622.1, M1002, M622, M1004 — all Bambu-proprietary.

---

## Discovery Method

Compared two files:
- `proxy_Med_Core_clean_marked.gcode` — sliced with `AD5X Iris (zmod)` (standalone, `inherits: ""`): clean, only M73
- `nut.gcode` — sliced with `Iris` profile (inherits A1): M981 at line 612, M624/M625 throughout, G1 X-48.2 at line 1630

`grep -n "M981\|M624\|M625\|M622\|M1002\|X-[0-9]"` on both files confirmed the difference.

---

## Fix Applied

**1. `Iris.json`** — Override `time_lapse_gcode` to empty string:
```json
"time_lapse_gcode": ""
```
This kills M622/M1002/M1004/G1 X-48.2 from the layer-change injection.

**2. `/opt/config/mod_data/user.cfg` on Iris (192.168.1.50)**:
```ini
[gcode_macro M981]
gcode:

[gcode_macro M624]
gcode:

[gcode_macro M625]
gcode:
```
These swallow the spaghetti detector and AMS marker codes that Bambu Studio continues to inject regardless of profile settings.

---

## Rule / Lesson

**Setting `gcode_flavor: klipper` in a Bambu Studio profile that inherits from a Bambu printer does NOT suppress all Bambu-proprietary M-codes.** M981 (spaghetti detection) and M624/M625 (AMS layer markers) are injected by Bambu Studio's internal code generation, not by user-configurable profile fields.

**Fix pattern for any Klipper printer using Bambu Studio:**
1. Override `time_lapse_gcode: ""` in the printer profile
2. Add no-op Klipper macros for M981, M624, M625 in user.cfg

**Detection pattern:** `grep -n "M981\|M624\|M625\|X-[0-9]"` on sliced gcode, excluding comment lines (`grep -v "^[0-9]*:;"`). Any hits = Bambu injection present.

*— Claude, 2026-07-06*
