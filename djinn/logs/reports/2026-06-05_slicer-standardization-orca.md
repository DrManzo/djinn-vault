---
title: Session Report — Slicer Standardization + Fan Cap + Calibration
agent: Salomon
date: 2026-06-05
tags: [djinn, report, orcaslicer, prismatic, calibration, bug-014]
related: [[build-log]] [[PRINT-PROFILES.md]] [[BUG-014]] [[djinn-gcode-safety]]
---

# Session Report — OrcaSlicer Standard + Fan Cap + Calliope Calibration

**Date:** 2026-06-05
**Agent:** Salomon (Claude API)
**Session type:** Ops / Config
**Trigger:** Factory reset of Calliope after repeat print failures (nozzle_mcu dropouts)

---

## Summary

Four changes this session: (1) Calliope homed + bed mesh calibrated after factory reset, (2) OrcaSlicer adopted as standard slicer, PrusaSlicer relegated to diagnostic/CLI-only, (3) `djinn-gcode-safety` upgraded to cap all M106 fan commands at S128 to mitigate EMI-triggered nozzle_mcu dropouts, (4) docs updated across printer profiles and READMEs.

---

## What Was Built or Changed

- **Calliope calibration** — `CX_ROUGH_G28` → `ACCURATE_G28` → `BED_MESH_CALIBRATE` → `SAVE_CONFIG`. Bed variance -0.44 to +0.10mm. Profile saved.
- **OrcaSlicer production profile** — `~/.config/OrcaSlicer/user/default/process/Production 0.20mm @Creality Ender-3 V3 Plus.json`. Fan capped at 50%. Inherits from system V3 Plus profile.
- **`orca-slicer` CLI symlink** — `~/.local/bin/orca-slicer → ~/Applications/OrcaSlicer_V2.3.2.AppImage`
- **`djinn-gcode-safety` v2** — added M106 fan capping (S128 max), reports count of capped lines. Run on ALL gcode regardless of source slicer.
- **Pipeline scripts** — `djinn-model-slice`, `djinn-model-combine`, `djinn-print-consult` annotated with Orca-as-standard comment headers
- **Docs updated** — `PRINT-PROFILES.md`, `SUPPORT-GUIDE.md`, `DJINN-3D-PRINT-PIPELINE.md`, `PRINTER-MANUAL.md`

---

## Technical Decisions

**OrcaSlicer over PrusaSlicer — Why:** PrusaSlicer's M106 S255 at bridges repeatedly triggered EMI spikes on nozzle_mcu UART (BUG-013/014). OrcaSlicer has native Ender-3 V3 Plus profile support, native Moonraker upload, and Creality-native gcode output (M220, SET_VELOCITY_LIMIT, SET_PRESSURE_ADVANCE). Orca CLI headless slicing works (`--load-settings machine.json;process.json;filament.json --slice 0 --outputdir`).

**PrusaSlicer retained for CLI pipeline — Why:** OrcaSlicer's CLI lacks per-parameter overrides (`--fill-density`, `--layer-height` flags). Pipeline scripts (`djinn-model-slice`, `djinn-model-combine`) use PrusaSlicer's rich CLI flag set for headless automated slicing. This is the legacy path — future work can build a temp-profile approach for Orca CLI.

**Fan cap at S128 (50%) — Why:** M106 S255 at bridges produces instant EMI spike → `key561` nozzle_mcu comms loss. S128 is the verified safe ceiling. `djinn-gcode-safety` enforces this on all gcode, any slicer. Not a substitute for fixing the loose connector but removes one failure trigger.

---

## Files Created or Modified

```
~/.config/OrcaSlicer/user/default/process/Production 0.20mm @Creality Ender-3 V3 Plus.json   ← created (Orca production profile)
~/.local/bin/djinn-gcode-safety                                       ← modified (added M106 fan capping)
~/.local/bin/orca-slicer                                              ← symlink created
~/.local/bin/djinn-model-slice                                        ← modified (annotated comments)
~/.local/bin/djinn-model-combine                                      ← modified (annotated comments)
~/.local/bin/djinn-print-consult                                      ← modified (annotated comments)
~/Obsidian/djinn/printer/PRINT-PROFILES.md                            ← modified
~/Obsidian/djinn/printer/SUPPORT-GUIDE.md                             ← modified
~/Obsidian/djinn/printer/DJINN-3D-PRINT-PIPELINE.md                   ← modified
~/Obsidian/djinn/printer/PRINTER-MANUAL.md                            ← modified
```

---

## Tests & Validation

- `python3 -m py_compile` passed on all 4 modified scripts
- OrcaSlicer CLI headless slice: produced `plate_1.gcode` from test STL, return code 0
- `djinn-gcode-safety` fan cap: 98 M106 lines capped from S255→S128 on Orca test gcode
- Calliope calibration: bed mesh saved successfully, printer in standby

---

## Known Issues

- BUG-014 remains OPEN — nozzle_mcu loose connector not fixed by software. Fan cap removes one trigger but UART dropouts will continue until the connector is reseated or cable replaced.
- Pipeline scripts still call PrusaSlicer CLI. Future: build Orca temp-profile approach for full migration.
- Orca's `M106 P2 S0` (auxiliary fan) commands in gcode are left uncapped — auxiliary fan doesn't trigger nozzle_mcu EMI.

---

## What's Next

- [ ] BUG-014: physical inspection of nozzle_mcu connector + cable harness — @Javier
- [ ] Test print a single small model through OrcaSlicer to verify gcode produces clean print
- [ ] Build Orca temp-profile CLI wrapper to fully migrate pipeline from PrusaSlicer

---

*— Salomon, 2026-06-05*
