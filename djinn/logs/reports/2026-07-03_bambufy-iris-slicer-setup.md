---
title: Session Report — Bambufy Iris Setup + USB Prep + Bambu Studio
agent: Claude
date: 2026-07-03
tags: [djinn, report, bambufy, iris, ad5x, slicer]
related: [[build-log]] | [[decision-log]]
---

# Session Report — Bambufy on Iris + Slicer Profiles on USB

**Date:** 2026-07-03
**Agent:** Claude
**Session type:** Build / Ops
**Trigger:** Multi-filament printing setup for Iris (AD5X)

---

## Summary

Mounted Typhon USB, read prior session context, installed and configured bambufy plugin on Iris (AD5X) at 192.168.1.50, created OrcaSlicer and Bambu Studio profiles, and bundled everything onto the Typhon USB for offline deployment. Bambu Studio AppImage also installed on Salomon.

---

## What Was Built or Changed

- **Bambufy plugin** installed and wired on Iris via Moonraker API + SSH
- **`bambufy.cfg`** (2144 lines) written to Iris at `/opt/config/mod_data/plugins/bambufy/bambufy.cfg`
- **`plugins.cfg`** include added on Iris
- **`printer.base.cfg`** `position_endstop` commented out for stepper_z (bambufy requirement)
- **Version check** on Iris lowered from 1.2.3 → 1.2.2 to match slicer gcode
- **Typhon USB** rebuilt with full djinn/ directory structure
- **OrcaSlicer profiles** created for Nemesis and Iris
- **Bambu Studio 3MF templates** (7.6MB + 7.7MB) downloaded to USB
- **Bambu Studio AppImage** (217MB) installed on Salomon at `~/BambuStudio.AppImage`
- **`bambufy-setup.md`** comprehensive guide written to USB
- **Iris SSH** access verified (root/root via sshpass)
- **Moonraker API** endpoints confirmed working for gcode script injection

---

## Technical Decisions

- **Bambufy over nopoop/lesswaste** — bambufy provides the best Bambu Studio compatibility and waste optimization for Iris's 4-color IFS system
- **Manual bambufy.cfg install instead of relying on ENABLE_PLUGIN** — the zmod plugin system's `ENABLE_PLUGIN` command installed the plugin files but failed to create the required `.cfg` include in `plugins.cfg`. Manual wiring was required.
- **Moonraker API over SSH for most ops** — SSH had connection issues with large payloads; Moonraker's HTTP API at port 7125 was more reliable for gcode commands
- **min_version lowered** from 1.2.3 to 1.2.2 to match the existing slicer's filament change gcode version
- **Bambu Studio as primary slicer for Iris** — bambufy is designed for Bambu Studio's AMS workflow; OrcaSlicer as fallback

---

## Files Created or Modified

```
USB (Typhon):
  djinn/bambufy-setup.md                              ← comprehensive guide
  djinn/bambufy-template-bambustudio.3mf (7.6MB)       ← Iris Bambu Studio profile
  djinn/bambufy-template-orca.3mf (7.7MB)              ← Iris Orca profile
  djinn/orca-profiles/Nemesis-AD5M-Pro-0.4mm.json     ← Nemesis Orca profile
  djinn/orca-profiles/Nemesis-AD5M-Pro-0.4mm.info
  djinn/orca-profiles/Iris-AD5X-0.4mm-Bambufy.json    ← Iris Orca profile w/ bambufy gcode
  djinn/orca-profiles/Iris-AD5X-0.4mm-Bambufy.info
  djinn/OPENCODE-PROMPT.md                            ← Salomon remote setup prompt (restored)
  djinn/ssh-recovery/typhon-unlock.ps1                ← SSH fix script (restored)
  djinn/slicers/install-slicers.ps1                   ← silent install script (restored)
  djinn/slicers/OrcaSlicer_*.exe                      ← OrcaSlicer installer (restored)
  djinn/slicers/Bambu_Studio_win*.exe                 ← Bambu Studio installer (restored)

Iris (AD5X @ 192.168.1.50):
  /opt/config/mod_data/plugins/bambufy/bambufy.cfg    ← 2144-line bambufy config
  /opt/config/mod_data/plugins.cfg                    ← include added for bambufy
  /opt/config/printer.base.cfg                        ← position_endstop commented in [stepper_z]
  (save_variables) bambufy_reinstall=0, bambufy_version=2, bambufy_mesh=1

Salomon (this machine):
  ~/BambuStudio.AppImage                              ← Bambu Studio AppImage
  ~/.local/bin/bambu-studio                           ← symlink
  /tmp/bambufy_full.cfg                               ← downloaded bambufy config (temp)
```

---

## Dependencies Installed

| Package | Method | Purpose |
|---------|--------|---------|
| Bambu Studio v02.07.01.62 | AppImage (217MB) | Multi-color slicing for Iris |
| bambufy plugin v1.3.3 | zmod ENABLE_PLUGIN + manual cfg | Waste-optimized multi-material on AD5X |

---

## Tests & Validation

- **Bambufy plugin**: 27 macros loaded on Iris (`_IFS_VARS`, `_IFS_COLORS`, `_RUNOUT_HEAD`, `_CONSUME`, `_NOPOOP`, etc.)
- **COLOR dialog**: Opens in Fluidd console — color mapping works
- **Filament change**: Tested through console — cut, unload, load, purge sequences all functional
- **Bambu Studio AppImage**: Runs on Ubuntu 26.04 (`bambu-studio` launches GUI)
- **SSH to Iris**: Verified working (root/root via sshpass)
- **Moonraker API**: Gcode injection via `printer/gcode/script` endpoint confirmed
- **JSON profiles**: Both OrcaSlicer profiles validated as valid JSON

---

## Known Issues / Caveats

- `_START_BAMBUFY` delayed gcode doesn't load on this Klipper version — init was triggered manually via `SET_GCODE_VARIABLE MACRO=_IFS_VARS VARIABLE=init VALUE=1`. May need re-triggering after Klipper restarts.
- `shoot_y_position=223` causes "Move out of range" errors at Y=234.7 during long retractions — may need lowering to 218 if persistent.
- Bambu Studio on Typhon still needs manual host config (192.168.1.50:7125, Moonraker) — the 3MF template sets everything else.
- Typhon SSH is still locked — `typhon-unlock.ps1` needs to be run as Admin on Typhon before remote automation works.

---

## What's Next

- [ ] Run `typhon-unlock.ps1` as Admin on Typhon — @Javier
- [ ] Open `bambufy-template-bambustudio.3mf` on Typhon, save as default Iris profile — @Javier
- [ ] Test first multi-color print through bambufy — @Javier
- [ ] Set up Nemesis in OrcaSlicer on Typhon with the `orca-profiles/` JSON — @Javier
- [ ] Configure Bambu Studio on Salomon with Iris profile — @Javier
- [ ] Add bambufy `_START_BAMBUFY` workaround to post-restart init routine — @Claude

---

*— Claude, 2026-07-03*
