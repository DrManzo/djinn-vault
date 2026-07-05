---
title: Session Report — Printer Triage: Nemesis Full Recal + Calliope Cable Diagnosis
agent: Claude
date: 2026-07-05
tags: [djinn, report, nemesis, calliope, klipper, orcaslicer, hardware, debug]
related: [[build-log]] | [[decision-log]] | [[2026-07-05_bug-nemesis-z-offset-conflict]] | [[2026-07-05_bug-calliope-nozzle-mcu-cable]]
---

# Session Report — Printer Triage: Nemesis Full Recal + Calliope Cable Diagnosis

**Date:** 2026-07-05
**Agent:** Claude
**Session type:** Debug + Build
**Trigger:** Javier reported Nemesis printing too low on PETG (filament gunking on nozzle), and Calliope crashing with repeated klippy_shutdown events mid-print.

---

## Summary

Full root-cause diagnosis and recalibration of Nemesis (AD5M Pro with zmod/Klipper). Found a broken probe z_offset (-0.25, wrong) and all-negative bed mesh causing nozzle-too-close symptoms on both PLA and PETG. Re-ran PROBE_CALIBRATE (new z_offset: -0.401), rebuilt bed mesh, fixed OrcaSlicer machine profile start gcode, and created a Nemesis-specific PETG filament profile. Separately diagnosed Calliope's crash as a degraded toolhead cable (nozzle_mcu serial dropout with growing bytes_invalid — intermittent partial-wire contact, not clean break). New cable ordered; Calliope sidelined for long prints until it arrives.

---

## What Was Built or Changed

### Nemesis (AD5M Pro — 192.168.1.51)

- **PROBE_CALIBRATE** run via Fluidd console — new z_offset: **-0.401** (was -0.25)
- **z_offset written directly to `/opt/config/printer.base.cfg`** — SAVE_CONFIG cannot manage z_offset when `[probe]` is in an included file (conflict error); manual write required
- **BED_MESH_CALIBRATE** run — new 5×5 mesh taken against corrected z_offset baseline
  - Old mesh range: -1.1 to -2.9mm (1.8mm variation, all-negative = wrong baseline)
  - New mesh range: -1.53 to -2.82mm (1.3mm variation — bed physically tilted, right side low)
  - Mesh saved as profile `[default]`, loaded via `BED_MESH_PROFILE LOAD=default`
- **OrcaSlicer machine profile updated**: `~/.config/OrcaSlicer/user/default/machine/Flashforge Adventurer 5M Pro 0.4 Nozzle - Copy.json`
  - Added `machine_start_gcode`: M140 + M104 + START_PRINT + SET_PRINT_STATS_INFO
  - Added `machine_end_gcode`: END_PRINT
  - Set `host_type: moonraker`, added `printer_notes`
- **New OrcaSlicer filament profile created**: `~/.config/OrcaSlicer/user/default/filament/Nemesis-PETG.json`
  - Inherits: Flashforge Generic PETG
  - Compatible with: Flashforge Adventurer 5M Pro 0.4 Nozzle - Copy
  - Nozzle: 240/235°C, Bed: 70°C (textured PEI), Fan: 30–50%, PA: 0.035
  - `filament_start_gcode`: `SET_GCODE_OFFSET Z_ADJUST=0.03 MOVE=1` (PETG needs less squish than PLA)
  - `filament_end_gcode`: `SET_GCODE_OFFSET Z=0 MOVE=0`
  - Companion `.info` sidecar created
- **shoulder_ring_PETG_4h14m.gcode** printing on Nemesis — first properly configured print

### Calliope (Ender-3 V3 Plus — 192.168.1.114)

- Diagnosed repeated klippy_shutdown events (arm.stl PETG × 3, base_frame.stl PETG × 1)
- Root cause confirmed: **degraded toolhead cable harness** — broken wire inside insulation on nozzle_mcu serial line
- Evidence: `bytes_invalid` growing in stats (0 → 7 → 35 → 50 → 63 over 25 seconds post-crash) = intermittent partial contact generating line noise, not a clean break
- Crash at 1.7% into arm.stl print (byte position 286697 of 16.4MB), at X≈185 Y≈205
- Moving pieces to different plate position did not prevent crash — cable failure is general, not single-spot
- New replacement cable ordered by Javier
- Calliope sidelined for long PETG prints until cable arrives; short PLA prints only

---

## Technical Decisions

**OrcaSlicer stays (not FlashForge slicer) for Nemesis — Why:** FlashForge's own slicer targets stock firmware gcode (M-code heating sequences, proprietary movement commands). Nemesis runs zmod/Klipper. FlashForge slicer can't connect to Moonraker, generates commands Klipper may not understand, and loses all Klipper calibration features (pressure advance, input shaper profiles). OrcaSlicer with corrected start gcode is the right tool.

**PETG Z offset via SET_GCODE_OFFSET in filament profile — Why:** OrcaSlicer has no per-filament z_offset field. Klipper's `SET_GCODE_OFFSET Z_ADJUST=` in filament_start_gcode is the correct mechanism. Set to +0.03mm (less squish for PETG vs PLA). Reversible and tunable post-PROBE_CALIBRATE.

**z_offset written directly to printer.base.cfg (not via SAVE_CONFIG) — Why:** Klipper's SAVE_CONFIG writes to the `#*#` block at the bottom of `printer.cfg`. When a section (like `[probe]`) is defined in an included file, SAVE_CONFIG raises a conflict error and refuses to write. Only fix: manage z_offset manually in the included file. Must remember this every time PROBE_CALIBRATE is run on Nemesis.

**M140/M104 added to OrcaSlicer start gcode — Why:** Nemesis's stock screen (FlashForge touchscreen firmware) scans the first ~200 lines of gcode for M104/M109/M140/M190 before allowing print execution. With pure Klipper start gcode (START_PRINT macro only), the stock screen blocks the print with "Commands for heating the bed not found." Adding M140 + M104 before START_PRINT satisfies the scanner; Klipper executes both (START_PRINT re-asserts temps, harmless).

**Calliope sidelined — Why:** `bytes_invalid` growing post-crash confirms the wire is intermittently making/breaking contact and generating line noise. A clean break would show zero invalid bytes. This pattern means any sustained XY movement risks another dropout. No software fix exists for a hardware serial failure on an MCU that controls the hotend. Must wait for replacement cable.

---

## Files Created or Modified

```
~/.config/OrcaSlicer/user/default/machine/Flashforge Adventurer 5M Pro 0.4 Nozzle - Copy.json
    ← Added Klipper-compatible start/end gcode with M140/M104 + stock screen compatibility

~/.config/OrcaSlicer/user/default/filament/Nemesis-PETG.json     ← new: Nemesis PETG profile
~/.config/OrcaSlicer/user/default/filament/Nemesis-PETG.info     ← new: OrcaSlicer sidecar
/opt/config/printer.base.cfg  (on Nemesis via SSH)               ← z_offset: -0.25 → -0.401
```

---

## Tests & Validation

| Test | Result |
|------|--------|
| PROBE_CALIBRATE (Nemesis center) | z_offset = -0.401. Accepted after paper test. |
| printer.base.cfg z_offset after write | `grep z_offset` confirmed: `z_offset: -0.401` |
| Klipper restart post-config change | State: ready |
| BED_MESH_CALIBRATE (5×5, Nemesis) | Completed, saved to [default] profile |
| `BED_MESH_PROFILE LOAD=default` | No error, mesh active |
| shoulder_ring_PETG gcode on stock screen | Accepted (M140/M104 found), print started |
| gcode machine_start_gcode comment (line 809761) | Confirmed M140 present after OrcaSlicer restart |
| Calliope bytes_invalid trend post-crash | 0→7→35→50→63 = partial wire failure confirmed |

---

## Known Issues / Caveats

- **Nemesis bed tilt is physical**: 1.3mm variation corner-to-corner (right side low). Mesh compensates but manual re-tramming of corner screws while warm will improve first-layer consistency. Not done this session.
- **Nemesis SAVE_CONFIG z_offset conflict**: Every time PROBE_CALIBRATE is run on Nemesis, the resulting z_offset must be written manually to `/opt/config/printer.base.cfg`. SAVE_CONFIG will always fail for this field. Consider moving the `[probe]` section out of `printer.base.cfg` and into `printer.cfg` directly so SAVE_CONFIG can manage it.
- **Nemesis mesh profile name**: Mesh saved as `[default]` this session. Previous mesh was `[MESH_DATA]`. The START_PRINT macro references the loaded mesh — if Klipper restarts and doesn't auto-load `[default]`, mesh compensation won't apply. Monitor; rename to MESH_DATA if macro requires it.
- **Nemesis PETG Z_ADJUST (+0.03mm)**: Set based on typical PETG vs PLA offset. Needs validation on first real PETG print — may need tuning up or down.
- **Calliope arm.stl PETG prints**: All failed. Print is blocked until replacement cable installed.
- **OrcaSlicer must be fully restarted** to pick up changes to user profile JSON files. In-session edits are cached — reload required before reslicing.

---

## What's Next

- [ ] Nemesis: physically re-tram bed corners (right side needs to come up ~0.5-0.6mm) — @Javier
- [ ] Nemesis: move `[probe]` section from `printer.base.cfg` → `printer.cfg` so SAVE_CONFIG can manage z_offset — @Claude
- [ ] Nemesis: rename mesh profile `[default]` → `[MESH_DATA]` if START_PRINT macro requires it — @Claude
- [ ] Nemesis: validate PETG Z_ADJUST on first shoulder_ring print, tune if needed — @Javier
- [ ] Calliope: install replacement cable with service loop + stepper wire separation — @Javier
- [ ] Calliope: after cable install, run PROBE_CALIBRATE + BED_MESH_CALIBRATE — @Claude
- [ ] Calliope: do not run arm.stl or base_frame.stl PETG until cable replaced — @Javier
- [ ] Nemesis: BED_MESH_CALIBRATE after physical re-tramming — @Claude

---

*— Claude, 2026-07-05*
