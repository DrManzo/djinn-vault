---
title: Session Report — Iris Profile Fix + Fleet Back Online
agent: Claude
date: 2026-07-06
tags: [djinn, report, iris, bambu-studio, klipper, printing]
related: [[2026-07-05_printer-triage-nemesis-calliope]] | [[build-log]] | [[decision-log]]
---

# Session Report — Iris Profile Fix + Fleet Back Online

**Date:** 2026-07-06
**Agent:** Claude
**Session type:** Debug + Build
**Trigger:** Iris print crashes persisting (X=-48.200 out of range) from prior session; continued diagnosis and full fix applied this session.

---

## Summary

Diagnosed and fixed all root causes of Iris print crashes. The core issue was `Iris.json` inheriting from `Bambu Lab A1 0.4 nozzle`, which injected Bambu-proprietary M-codes (M981, M624, M625) and a timelapse gcode sequence containing `G1 X-48.2` (center-origin coordinate, out of range on a 0–215mm corner-origin bed). Fixed via profile overrides and Klipper no-op macros. Iris is now printing. Nemesis is printing. Calliope awaiting cable parts.

---

## What Was Built or Changed

**Iris.json profile fixes:**
- Added `"gcode_flavor": "klipper"` — suppresses most Bambu M-code injection
- Added `"time_lapse_gcode": ""` — kills the layer-change timelapse sequence that contains `G1 X-48.2`
- Added full `change_filament_gcode` (bambufy-compatible, `_GOTO_TRASH`/`_SBROS_TRASH`, `G1 Y210` safe exit)
- Added `"layer_change_gcode"` — proper Klipper layer progress tracking
- Added `"print_host": "192.168.1.50:7125"`
- Added `"time_lapse_gcode": ""` — empty, overrides inherited A1 timelapse injection

**Iris Klipper no-op macros (`/opt/config/mod_data/user.cfg` on 192.168.1.50):**
- `M981` — Bambu spaghetti detector, no-op
- `M624` — Bambu AMS layer marker, no-op
- `M625` — Bambu AMS layer marker, no-op
- Klipper restarted to load macros

**New Bambu Studio filament profiles:**
- `FLASHFORGE PETG Basic @Iris` — 240°C/230°C, bed 70°C, `compatible_printers: ["Iris"]`
- `FLASHFORGE PLA Basic @Iris` — 220°C, bed 45°C, `compatible_printers: ["Iris"]`
- Both have clean `filament_start_gcode` (no `M106 P3` chamber fan)

---

## Technical Decisions

**Klipper no-op macros vs profile-only suppression** — Even with `gcode_flavor: klipper`, Bambu Studio still injects M981/M624/M625 from printer features inherited from the A1 parent. No JSON key was found to suppress these via profile alone. No-op macros in `user.cfg` are the robust solution — they intercept regardless of slicer output.

**`time_lapse_gcode: ""`** — The A1 parent's timelapse gcode runs at every layer change and contains `G1 X-48.2 F3000` (valid center-origin on A1, out of range on Iris). Overriding with empty string is the correct fix. Cannot be fixed in Klipper because bambufy does not re-translate coordinates.

**Filament profiles locked to Iris** — `compatible_printers: ["Iris"]` (matching `printer_settings_id` in `Iris.json`). The old A1-locked PETG profile was not showing up in Bambu Studio when Iris was selected as printer.

**Why old gcode files could not be salvaged** — bambufy's `===Processing===` step strips some Bambu M-codes but cannot re-translate center-origin coordinates. Any gcode sliced with the old broken Iris profile needed to be re-sliced.

---

## Files Created or Modified

```
~/.config/BambuStudio/user/2893337220/machine/Iris.json                          ← added gcode_flavor, time_lapse_gcode, change_filament_gcode, layer_change_gcode, print_host
/opt/config/mod_data/user.cfg (on 192.168.1.50)                                  ← new: M981/M624/M625 no-op macros
~/.config/BambuStudio/user/2893337220/filament/FLASHFORGE PETG Basic @Iris.json  ← new: Iris-compatible PETG profile
~/.config/BambuStudio/user/2893337220/filament/FLASHFORGE PLA Basic @Iris.json   ← new: Iris-compatible PLA profile
```

---

## Dependencies Installed

None.

---

## Tests & Validation

- `bolt_head_PETG_3h20m.gcode` re-sliced with fixed Iris profile → bambufy processed successfully → print running
- Klipper FIRMWARE_RESTART after `user.cfg` write → `{"result":"ok"}` from Moonraker
- Compared `nut.gcode` (broken) vs `proxy_Med_Core_clean_marked.gcode` (working): confirmed M981/M624/M625/G1 X-48.2 in broken file, absent in working file
- Fleet status: Iris printing ✓, Nemesis printing ✓, Calliope offline (cable) ✓

---

## Known Issues / Caveats

- `Iris.json` still `inherits: "Bambu Lab A1 0.4 nozzle"` — the A1 parent provides kinematic limits but also is the source of the injected Bambu features. The overrides in place are sufficient, but a future clean option is to change `inherits` to `"AD5X Iris (zmod)"` for a fully standalone Iris profile with no A1 legacy.
- `G1 Y220` in `change_filament_gcode` of `AD5X Iris (zmod).json` (the base profile) may be out of range on Iris's 215mm bed. Our `Iris.json` has `G1 Y210` which is safe. Monitor first multi-color print carefully.
- bambufy version check: `change_filament_gcode` header says `VERSION=1.2.2`. If bambufy on Iris is updated past min_version, the header may need updating.
- Calliope: replacement cable not yet installed. No PETG prints until cable swap done with service loop and EMI-separated routing.
- Nemesis: `[probe]` still in `printer.base.cfg` — SAVE_CONFIG workaround required for every future PROBE_CALIBRATE.

---

## What's Next

- [ ] Monitor Iris bolt_head first multi-color tool change — confirm `_GOTO_TRASH` fires correctly — @Javier
- [ ] After Iris first successful print, check first layer and tune ZOFFSET via zmod if needed — @Javier
- [ ] Install Calliope cable when parts arrive — service loop, EMI-separated routing, anchor to X carriage — @Javier
- [ ] Move `[probe]` from `printer.base.cfg` to `printer.cfg` on Nemesis — one-time fix, permanent — @Claude
- [ ] Rename Nemesis bed mesh from `[default]` to match START_PRINT macro expectation — @Claude
- [ ] Consider switching `Iris.json` `inherits` to `"AD5X Iris (zmod)"` for a clean standalone profile — @Claude

---

*— Claude, 2026-07-06*
