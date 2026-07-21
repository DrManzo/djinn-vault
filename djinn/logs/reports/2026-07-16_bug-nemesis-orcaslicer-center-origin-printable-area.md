---
title: Bug Report — Nemesis OrcaSlicer Profile Had Center-Origin printable_area, Real Firmware Is Corner-Origin
agent: Claude
date: 2026-07-16
tags: [djinn, bug, nemesis, orcaslicer, klipper, printable-area]
related: [[bugs]] | [[build-log]] | [[decision-log]]
---

# Bug Report — Nemesis OrcaSlicer Profile Center-Origin Mismatch

**Date:** 2026-07-16
**System:** Nemesis (Flashforge AD5M Pro) / OrcaSlicer machine profile
**Severity:** High
**Status:** ⚠️ CORRECTED 2026-07-20 — original diagnosis was wrong, see addendum at bottom

---

## ⚠️ Correction (2026-07-20)

**This report's root-cause diagnosis was backwards.** During the 2026-07-19/20 Z-offset recalibration investigation (see [[2026-07-19_bug-nemesis-z-offset-recalibration-too-aggressive-nozzle-scraping]]), live verification of Nemesis's actual Klipper config proved the opposite of what's written below:

- `printer.base.cfg`: `mesh_min: -105,-105` / `mesh_max: 105,105`
- Live `toolhead` object: `axis_minimum`/`axis_maximum`: `-125` to `125`
- `SCREWS_TILT_CALCULATE`'s own probe coordinates: all in the -105..105 range

**Nemesis is genuinely center-origin.** The `"0x0"→"220x220"` corner-origin fix applied below on 2026-07-16 was itself the bug — it silently broke correct positioning on Salomon's copy of the profile from that date forward. Typhon's independent copy of the same profile was never "fixed" this way and had been correct the whole time, which is how the discrepancy surfaced.

**Re-fixed 2026-07-20:** `~/.config/OrcaSlicer/user/default/machine/Flashforge Adventurer 5M Pro 0.4 Nozzle - Copy.json` on Salomon reverted to center-origin:
```json
"printable_area": ["-110x-110", "110x-110", "110x110", "-110x110"]
```
Confirmed via direct Read against the live file — this is the value now in place.

**Real lesson (supersedes the one below):** verify a firmware's coordinate convention against *live Klipper state* (`axis_minimum/maximum`, `mesh_min/max`, actual probe coordinates), not against inference from a "Move out of range" symptom plus a plausible-sounding stock-profile-inheritance story. The original diagnosis fit the symptom but was never checked against the printer's own reported geometry.

---

## Symptom

`2camood-v1_marked_PETG_8h18m.gcode` (staged in `Desktop/Review/Nemesis/`) threw "Move out of range" when attempted. Javier asked why.

---

## Root Cause

The active OrcaSlicer machine profile for Nemesis — `Flashforge Adventurer 5M Pro 0.4 Nozzle - Copy` (`print_host: 192.168.1.51`, confirmed the real Nemesis profile) — never overrides `printable_area`. It inherits from the stock system chain (`Flashforge Adventurer 5M Pro 0.4 Nozzle` → `fdm_adventurer5m_common`), which defines:

```json
"printable_area": ["-110x-110", "110x-110", "110x110", "-110x110"]
```

That's **center-origin** (bed spans -110mm to +110mm on both axes). But Nemesis's actual Klipper firmware — like the rest of this fleet — is **corner-origin** (0 to 220mm). The slicer had no reason to keep the model in positive coordinate space; it happily generated gcode with the object centered near (0,0), producing negative X/Y moves. Klipper rejected them outright.

Same bug class as the Iris/A1 `time_lapse_gcode` issue from 2026-07-06 (a different symptom, same root pattern: a stock Bambu/Flashforge-family profile assumes an origin convention that doesn't match how this specific Klipper install is actually configured) — just never caught here because it hadn't been triggered yet.

**Confirmed via direct comparison, not just theory:**

| File | X range | Y range |
|---|---|---|
| `2camood-v1_marked_PETG_8h18m.gcode` (failed) | -88.36 to 87.98 | -54.63 to 54.60 |
| `camood_marked_PETG_7h4m.gcode` (previously printed clean) | 31.05 to 183.95 | 49.65 to 161.38 |

The working file's coordinates are entirely positive — it happened to have the object manually positioned in the UI at a location that was safe regardless of the profile's mistaken origin. The failing file didn't get that manual placement (or the object was reset/re-centered), and the underlying misconfiguration surfaced.

---

## Fix

Added an explicit `printable_area` override to the user profile itself, so it no longer inherits the wrong default:

```json
"printable_area": [
    "0x0",
    "220x0",
    "220x220",
    "0x220"
],
```

File: `~/.config/OrcaSlicer/user/default/machine/Flashforge Adventurer 5M Pro 0.4 Nozzle - Copy.json`

**OrcaSlicer was running at the time of the fix (PID confirmed active since 09:20 today) — profile JSON edits are cached in-session and require a full restart to take effect**, per the established lesson from prior profile fixes on this fleet. Did not kill Javier's running instance; flagged that he needs to restart it himself before the next Nemesis slice.

---

## Rule / Lesson

**Any Bambu/Flashforge-family stock OrcaSlicer profile applied to a Klipper machine needs its `printable_area` (and, separately, `time_lapse_gcode` — see the Iris precedent) checked against the machine's actual firmware coordinate convention, not assumed from the stock profile.** These vendor profiles are written for the vendor's own stock firmware conventions, which frequently differ from how the same physical bed is configured once Klipper/zmod is installed. Don't wait for a specific object placement to expose the mismatch — check `printable_area` proactively on any new/copied machine profile in this fleet.

---

## What's Next

- [ ] Javier: restart OrcaSlicer before slicing the next Nemesis job
- [ ] Re-slice `2camood-v1` (or any pending Nemesis job) once restarted, confirm the new gcode's X/Y stays within 0-220
- [ ] Worth auditing Calliope's and Iris's active machine profiles for the same unaudited-inheritance pattern, even though neither has hit this specific symptom yet

---

*— Claude, 2026-07-16*
