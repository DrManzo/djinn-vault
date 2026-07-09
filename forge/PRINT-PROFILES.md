---
title: Print Profiles — Djinn Fleet
updated: 2026-07-07
tags: [djinn, printer, profiles, calliope, penelope, iris, nemesis]
related: [[SUPPORT-SETTINGS]] | [[MACHINE-ROLES]]
---

# Print Profiles — Djinn Fleet

Profiles are suggestions, not law. Javier overrides any value at slice time.

---

## Slicer Routing — All slicing runs on Typhon (Windows, 192.168.1.113)

| Machine | Slicer | Notes |
|---|---|---|
| **Iris** | Bambu Studio | Multi-color via IFS/bambufy |
| **Clotho** | Bambu Studio | P1S + AMS |
| **Lachesis** | Bambu Studio | P1S + AMS |
| **Atropos** | Bambu Studio | TBD machine |
| **Nemesis** | OrcaSlicer | zmod Klipper — FlashForge slicer incompatible |
| **Calliope** | OrcaSlicer or Creality Print | Fan cap enforced at Klipper level (fan-cap-calliope.cfg) — slicer-agnostic |
| **Penelope** | OrcaSlicer | zmod Klipper |

> Typhon is the unified slicing station for the full fleet. Bambu Studio owns the sisters (Iris + Clotho + Lachesis + Atropos). OrcaSlicer/Creality Print owns the Klipper machines.

> **Support settings are in [[SUPPORT-SETTINGS]].** This file covers general print profiles only.

---

# Calliope — Creality Ender-3 V3 Plus

**Role:** Production / Commission workhorse  
**Build volume:** 300×300×330mm  
**Primary material:** PLA  
**Fan constraint:** M106 S128 max — hardware cap, nozzle_mcu UART (BUG-014)

## proto — Prototype / First-Look

**Purpose:** See if it fits, check the shape, test the design. Not a finished part.
**Priority:** Speed, material efficiency, easy cleanup.

| Setting | Value | Why |
|---|---|---|
| Infill | 8% | Just enough for structure |
| Infill pattern | Gyroid | Fast, omnidirectional, easy to break out |
| Layer height | 0.28mm | Faster, surface finish doesn't matter yet |
| Supports | Only if >60° | Aggressive threshold — reduce cleanup work |
| Brim | yes (3mm) | Adhesion without bulk |
| Raft | no | Unless piece is very small or unstable |
| Walls | 2 | Minimum shell |
| Bed temp | 55°C | Standard PLA |
| Hotend | 210°C | Standard PLA |

**Result:** Quick, cheap, easy to post-process. Expect rough surface. That's fine.

## standard — Working Part / Moderate Strength

**Purpose:** Functional part that needs to hold up. Not final production.

| Setting | Value | Why |
|---|---|---|
| Infill | 15% | Good strength/weight ratio |
| Infill pattern | Grid | Predictable, strong |
| Layer height | 0.20mm | Good balance |
| Supports | If >45° overhang | Standard threshold |
| Brim | yes (5mm) | Solid adhesion |
| Raft | no | |
| Walls | 3 | Solid shell |
| Bed temp | 60°C | Better adhesion for functional parts |
| Hotend | 210°C | |

## production — Final Piece / Full Strength

**Purpose:** Commission-ready or final-use part.

| Setting | Value | Why |
|---|---|---|
| Infill | 25% | High strength |
| Infill pattern | Gyroid | Best strength per gram |
| Layer height | 0.20mm | Clean finish |
| Supports | If >45° overhang | See [[SUPPORT-SETTINGS]] for full support spec |
| Brim | yes (8mm) | Maximum adhesion |
| Raft | no | |
| Walls | 4 | Maximum shell thickness |
| Bed temp | 65°C | Best first-layer adhesion |
| Hotend | 210°C | |

## custom

Javier specifies everything. The slicer uses exactly what was said.
No defaults applied. No substitutions.

## Slicer Note
**Slicer:** Creality Print / OrcaSlicer  
ALL gcode passes through `djinn-gcode-safety` which caps M106 fan speed to S128 max — hardware constraint on Calliope's nozzle_mcu UART.

*— Updated 2026-07-07*

---

# Penelope — Creality Ender-3 Pro

**Role:** Detail / Personal / Experimental  
**Build volume:** 220×220×250mm  
**Primary material:** PETG (PLA secondary)  
**Extruder:** Bowden — retraction 5.5mm @ 45mm/s  
**Control:** OctoPrint on Salomon at `http://localhost:5001`

> **Routing:** If model exceeds 220×220×250mm on any axis → Calliope only.

## proto

| Setting | Value |
|---|---|
| Infill | 8% gyroid |
| Layer height | 0.28mm |
| Walls | 2 |
| Supports | Only if >60° |
| Brim | yes (3mm) |
| Bed temp | 55°C |
| Hotend | 210°C (PLA) / 230°C (PETG) |

## standard

| Setting | Value |
|---|---|
| Infill | 15% grid |
| Layer height | 0.20mm |
| Walls | 3 |
| Supports | If >45° — see [[SUPPORT-SETTINGS#Penelope]] |
| Brim | yes (5mm) |
| Bed temp | 60°C (PLA) / 70°C (PETG) |
| Hotend | 210°C (PLA) / 235°C (PETG) |

## production

| Setting | Value |
|---|---|
| Infill | 25% gyroid |
| Layer height | 0.16mm (detail mode) |
| Walls | 4 |
| Supports | If >45° — see [[SUPPORT-SETTINGS#Penelope]] |
| Brim | yes (8mm) |
| Bed temp | 65°C (PLA) / 70°C (PETG) |
| Hotend | 210°C (PLA) / 235°C (PETG) |

## Bowden Notes
- Retraction: 5.5mm @ 45mm/s — do not lower without recalibration
- For PETG supports: use Normal type, NOT Tree — see [[SUPPORT-SETTINGS#Penelope]]
- Max reliable speed: 60mm/s outer wall, 50mm/s support
- Input shaping: manual ringing tower method only (Pi Zero 2W RAM constraint)

*— Updated 2026-07-07*

---

# Iris — FlashForge AD5X

**Role:** Multi-color / Multi-material display pieces, flexible TPU, color commissions  
**Build volume:** 220×220×220mm  
**Primary materials:** PLA, PETG, TPU 95A  
**Extruder:** Direct drive, IFS 4-color system (T1–T4)  
**Enclosure:** Yes — DIY, passive (no active filtration)  
**Firmware:** zmod 1.7.1-49 / Klipper / Moonraker @ 192.168.1.50:7125  
**Slicer:** Bambu Studio (multi-color jobs) / OrcaSlicer (single-color)

> **Support superpower:** Iris can use PLA as interface material on PETG parts (and vice versa) via IFS — dissimilar materials = supports that pop off clean. See [[SUPPORT-SETTINGS#Iris]].

## proto

| Setting | Value |
|---|---|
| Infill | 8% gyroid |
| Layer height | 0.20mm |
| Walls | 2 |
| Supports | Only if >60° |
| Brim | yes (3mm) |
| Bed temp | 55°C (PLA) / 70°C (PETG) |
| Hotend | 220°C (PLA) / 240°C (PETG) |
| Multi-color | Single extruder (T1 only) for protos |

## standard

| Setting | Value |
|---|---|
| Infill | 15% gyroid |
| Layer height | 0.20mm |
| Walls | 3 |
| Supports | If >40° — assign T2 as interface (see [[SUPPORT-SETTINGS#Iris]]) |
| Brim | yes (5mm) |
| Bed temp | 55°C (PLA) / 70°C (PETG) |
| Hotend T1 | 220°C (PLA) / 240°C (PETG) |
| Hotend T2 | 210°C (PLA interface) |

## production — multi-color

| Setting | Value |
|---|---|
| Infill | 20% gyroid |
| Layer height | 0.20mm |
| Walls | 4 |
| Supports | If >40° — PLA interface via T2 (see [[SUPPORT-SETTINGS#Iris]]) |
| Brim | yes (5mm) |
| Purge strategy | bambufy — flush into infill/supports (not prime tower) |
| Bed temp | Match primary material |
| Enclosure | Crack door 2–3cm for PLA interface layers if stringing observed |

## IFS / Filament Slot Assignment

```
T1 = Primary part color 1
T2 = Primary part color 2 (or support interface material)
T3 = Accent / detail color (or support body if full dissimilar)
T4 = Reserve / specialty (TPU, etc.)
```

## Iris Notes
- bambufy is installed and operational — Bambu Studio is the slicer for multi-color jobs; OrcaSlicer for single-color
- `shoot_y_position` bug: if "Move out of range" error during long multi-color retractions, lower `shoot_y_position` from 223 to 218 in bambufy config
- Iris clock may show 1970 on cold boot — NTP resolves on internet connect, non-blocking
- Enclosure is DIY passive — no HEPA/carbon filtration; ventilate room when running ABS/ASA

*— Added 2026-07-07*

---

# Nemesis — FlashForge AD5M Pro

**Role:** Enclosed single-material — ABS/ASA, PETG, engineering materials  
**Build volume:** 220×220×220mm  
**Primary materials:** PETG, ABS, ASA, PLA  
**Extruder:** Direct drive  
**Enclosure:** Yes — factory, active HEPA + carbon filtration  
**Max nozzle:** 280°C  
**Firmware:** zmod / Klipper / Moonraker @ 192.168.1.51:7125  
**Slicer:** OrcaSlicer only (FlashForge slicer incompatible with zmod Klipper)

## proto

| Setting | Value |
|---|---|
| Infill | 8% gyroid |
| Layer height | 0.20mm |
| Walls | 2 |
| Supports | Only if >60° |
| Brim | yes (3mm) |
| Bed temp | 55°C (PLA) / 70°C (PETG) / 100°C (ABS) |
| Hotend | 215°C (PLA) / 240°C (PETG) / 250°C (ABS) |

## standard

| Setting | Value |
|---|---|
| Infill | 15% grid |
| Layer height | 0.20mm |
| Walls | 3 |
| Supports | If >45° — see [[SUPPORT-SETTINGS#Nemesis]] |
| Brim | yes (5mm) — critical for ABS |
| Bed temp | 55°C (PLA) / 70°C (PETG) / 100°C (ABS) |
| Hotend | 215°C (PLA) / 240°C (PETG) / 250°C (ABS) |
| Fan | 100% PLA / 50% PETG / 0–20% ABS |

## production

| Setting | Value |
|---|---|
| Infill | 25% gyroid |
| Layer height | 0.20mm |
| Walls | 4 |
| Supports | If >45° — see [[SUPPORT-SETTINGS#Nemesis]] |
| Brim | yes (8mm) |
| Bed temp | 60°C (PLA) / 75°C (PETG) / 105°C (ABS) |
| Hotend | 220°C (PLA) / 245°C (PETG) / 255°C (ABS) |

## Nemesis Notes
- **z_offset SAVE_CONFIG trap:** After `PROBE_CALIBRATE`, write z_offset manually to `/opt/config/printer.base.cfg` via SSH — `SAVE_CONFIG` will fail due to `[probe]` being in an included file
- OrcaSlicer start gcode must include `M140 S{bed_temp}` and `M104 S{nozzle_temp}` BEFORE `START_PRINT` — stock touchscreen scans first 200 lines for these commands
- Bed is physically tilted right-side-low ~1.3mm — mesh compensates but re-tram warm for best first layers
- Max nozzle 280°C — PC and high-temp Nylon not supported without hotend upgrade

*— Added 2026-07-07*
