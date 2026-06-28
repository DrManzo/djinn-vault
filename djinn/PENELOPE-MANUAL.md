# PENELOPE-MANUAL

## Purpose

This manual is the complete operator guide for **Penelope**, the Creality Ender 3 Pro in the Djinn printer fleet. Penelope is an Ender 3 Pro with a Bowden extruder, stock Marlin firmware, and an ATmega1284P 8-bit board [file:13]. She is controlled through **OctoPrint 1.11.7** on Salomon at [http://localhost:5001](http://localhost:5001) and through the `djinn-penelope` CLI [file:10][file:13].

A new operator should be able to go from zero to a confirmed print by following this file in order. Penelope uses a different control stack and different slicing assumptions than Calliope, so files and settings must not be mixed across the two printers [file:10][file:13].

## Machine Identity

| Field | Value |
|---|---|
| Printer name | Penelope |
| Machine | Creality Ender 3 Pro [file:13] |
| Motion / firmware | Stock Marlin 1.1.6 on ATmega1284P 8-bit board [file:13] |
| Extruder | Bowden extruder |
| Build volume | 220×220×250mm [file:12][file:13] |
| Host machine | Salomon [file:10][file:13] |
| Printer connection | `/dev/ttyUSB0` at 115200 baud |
| Web interface | [http://localhost:5001](http://localhost:5001) |
| OctoPrint login | `djinn` / `djinnprint` |
| CLI | `djinn-penelope` |
| Saved Z offset | -0.5mm |

## Core Differences from Calliope

Penelope is **not** a smaller copy of Calliope. She is a different machine with a different extrusion path, a different firmware stack, lower speed ceilings, and a completely separate slicing pipeline [file:10][file:12][file:13].

| Category | Calliope | Penelope |
|---|---|---|
| Extruder | Direct drive / Sprite | Bowden / stock |
| Firmware | Klipper | Marlin |
| Retraction | 0.5–0.6mm class | 5.5mm |
| Build volume | 300×300×330mm [file:2][file:13] | 220×220×250mm [file:12][file:13] |
| Advanced tuning | Pressure advance, input shaping | None |
| Host stack | Moonraker | OctoPrint |
| Slicing pipeline | Calliope-specific | Penelope-specific |

The practical result is simple: **gcode is not cross-compatible**. Never assume a file or profile prepared for Calliope is safe for Penelope, and never assume Penelope settings can be reused on Calliope without conversion [file:10][file:13].

## Absolute Rules

- Never send **Creality Print** gcode to Penelope. Penelope uses Marlin, and Creality Print outputs in this environment target Klipper behavior and can silently fail on Penelope.
- Use **OrcaSlicer only** for Penelope jobs.
- Never use direct-drive retraction values on Penelope; Penelope's Bowden setup requires 5.5mm retraction at 45mm/s.
- Do not exceed the Penelope speed caps of 40/50/60mm/s for outer wall, inner wall, and infill.
- Do not assume pressure advance, input shaping, or other Klipper-only features exist on Penelope.
- If a print stops more than once without a clear error, check bed leveling before trying again.
- Do not start a print without Javier's explicit approval.

## Access and Control

Penelope can be operated from either the web UI or the CLI. The web UI is useful for visual confirmation, file selection, and status checks. The CLI is the preferred control surface for scripted or repeatable actions [file:10][file:13].

### OctoPrint

- URL: [http://localhost:5001](http://localhost:5001)
- Username: `djinn`
- Password: `djinnprint`

Use OctoPrint to confirm connection status, inspect uploaded files, watch temperatures, and verify that Penelope is in an idle or operational state before a job begins.

### CLI

Primary commands:

```bash
djinn-penelope status
djinn-penelope files
djinn-penelope upload <file.gcode>
djinn-penelope print <filename>
djinn-penelope cancel
```

Use `djinn-penelope status` before and after every major action. A healthy idle printer should report as operational with live bed and hotend readings [file:10].

## Slicer Policy

Penelope uses **OrcaSlicer only**. Do not use Creality Print for Penelope under any circumstance because the generated gcode in this Djinn workflow is tied to Klipper behavior and is not reliable on Marlin.

This rule exists because Penelope and Calliope run separate printer stacks. A slicer pipeline that is valid for Calliope can fail silently on Penelope, which is worse than an obvious hard failure because it wastes time and material.

## Penelope Profiles

Penelope slicing profiles live at:

```text
~/Obsidian/djinn/printer/forge-slicer/profiles/
```

### Process Profiles

| Profile | Use |
|---|---|
| `Penelope-Standard` | Default print profile; 0.2mm layer height, 14% gyroid, 3 walls, no supports, no brim |
| `Penelope-Standard-TreeSupports` | Same base profile plus tree(auto) supports and 8mm brim |
| `Penelope-Standard-Supports` | Compatibility alias; same as TreeSupports |
| `Penelope-Production` | Final-strength profile; 0.2mm layer height, 14% gyroid, 4 walls, 5 top shells, 8mm brim |

### Filament Profile

| Profile | Settings |
|---|---|
| `Penelope-PLA` | 220°C hotend, 65°C first layer bed, 60°C bed after first layer, 5.5mm retraction at 45mm/s |

### Speed Limits

Penelope's 8-bit Marlin board cannot keep up with Calliope-class motion settings. Treat these as hard caps unless Javier explicitly requests controlled testing:

| Move Type | Cap |
|---|---|
| Outer wall | 40 mm/s |
| Inner wall | 50 mm/s |
| Infill | 60 mm/s |

## Pre-Print Checklist

Run this checklist in order before every job.

1. Confirm the model fits within **220×220×250mm**.
2. Confirm the source file has been placed in `~/Desktop/Review/`.
3. Confirm Javier has reviewed or approved the model for next-step handling.
4. Check whether the part needs a maker's mark.
5. Confirm Penelope is operational with `djinn-penelope status`.
6. Confirm filament is loaded and feeding cleanly.
7. Confirm the bed surface is clean.
8. Confirm the correct OrcaSlicer process profile and `Penelope-PLA` filament profile are selected.
9. Confirm the generated output is Penelope-specific gcode, not Calliope or Creality Print output.
10. Get explicit go-ahead from Javier before starting the print command.

## Mandatory Workflow

This order is required. Do not rearrange it.

### 1. Stage the model for review

Drop the STL or 3MF into:

```text
~/Desktop/Review/
```

Do not slice immediately. The model waits there for Javier approval.

### 2. Apply maker's mark

Run `djinn-model-mark` before slicing. Check internal geometry first. For hollow models, show a preview before committing the mark placement so the marker does not break visible surfaces or internal voids.

### 3. Slice in OrcaSlicer

Open OrcaSlicer and select the correct Penelope process profile plus `Penelope-PLA`. Do **not** substitute Creality Print, and do not use Calliope profiles.

Select the appropriate process profile based on part intent:

- `Penelope-Standard` for ordinary working parts.
- `Penelope-Standard-TreeSupports` when supported geometry is needed.
- `Penelope-Standard-Supports` only when compatibility naming matters.
- `Penelope-Production` for stronger or presentation-ready parts.

### 4. Upload the gcode

Use the CLI:

```bash
djinn-penelope upload <file.gcode>
```

After upload, verify the file appears in OctoPrint or in `djinn-penelope files`.

### 5. Wait for Javier's approval to start

Upload is not permission to print. Ask for and receive explicit go-ahead before the start command.

### 6. Start the print

```bash
djinn-penelope print <filename>
```

Then immediately verify state, temperatures, and initial motion in OctoPrint or with `djinn-penelope status`.

## First Layer and Z Offset

Penelope requires a saved Z offset. Penelope originally shipped with no Z offset configured, and reliable first-layer behavior depends on having that correction stored.

The current saved Z offset is:

```text
-0.5mm
```

This value is saved to EEPROM. If first layers start too high, fail to adhere, or print as loose lines instead of a slightly flattened bead, verify the offset before making other changes. If the printer starts acting inconsistently after repeated unexplained stops, also check bed leveling.

### First-Layer Visual Standard

A correct first layer should look slightly squished, continuous, and bonded to the bed without gouging or elephant-foot-level overcompression. Use this quick interpretation guide:

- Too high: lines are round, separate, or drag loose behind the nozzle.
- Too low: lines are overly flattened, rough, or the nozzle scrapes.
- Correct: adjacent lines gently merge into a smooth surface.

## Filament Loading and Extrusion Problems

Penelope uses a Bowden extrusion path, so feed problems present differently than on Calliope. Retraction is longer, the stock extruder is less forgiving, and low tension on the extruder arm can cause slipping.

### If filament will not pull consistently

Check extruder tension first. If the drive gear is chewing, slipping, or failing to advance filament, increase spring tension on the extruder arm.

### If strings or blobs appear unexpectedly

Do not import Calliope retraction logic. Penelope's correct PLA baseline is **5.5mm retraction at 45mm/s**, not direct-drive values.

### If flow stops during a print

- Confirm the spool moves freely.
- Check the Bowden path for kinks or drag.
- Inspect the drive gear for filament dust.
- Re-check extruder tension.
- Verify nozzle temperature is at the profile target.

## Bed Leveling and Repeat Failures

If a print stops more than once and there is no obvious error message, treat bed leveling as a likely cause. Repeated unexplained failures often waste more time than a quick re-level and first-layer check.

A good operator response sequence is:

1. Cancel the bad attempt.
2. Clear any debris from the bed and nozzle.
3. Re-check bed leveling.
4. Confirm Z offset remains at -0.5mm.
5. Restart only after the first-layer path looks correct.

## Known Bugs and Fixed Lessons

These are not theory notes; they are operational lessons already learned on Penelope.

### OctoPrint checksum behavior

`alwaysSendChecksum` causes a Marlin resend loop on Penelope. The correct behavior is `neverSendChecksum: true`.

### Z offset requirement

Penelope does not behave correctly without a configured Z offset. The current saved value is **-0.5mm**.

### SD card support

`sdSupport: false` is the correct setting. This suppresses an unnecessary Creality firmware warning path.

### Extruder tension

If the extruder spring tension is too low, filament slips on the drive gear. Increase tension before changing slicer settings if the printer is not pulling material reliably.

## Confirming a Good Start

A job is not considered safely started just because the print command was accepted. Confirm the following within the first moments of the print:

- OctoPrint shows the printer as active and the file as printing.
- Bed and hotend temperatures are rising toward or holding profile targets.
- The nozzle homes normally and begins the first layer without hesitation.
- Filament is visibly extruding.
- The first layer adheres with a smooth, lightly compressed line.

If any of these checks fail, stop early and diagnose immediately. Early cancellation is cheaper than recovering from a bad first layer halfway through a part.

## Quick Command Reference

```bash
# Check printer state
djinn-penelope status

# List uploaded files
djinn-penelope files

# Upload sliced gcode
djinn-penelope upload part.gcode

# Start approved file
djinn-penelope print part.gcode

# Cancel active job
djinn-penelope cancel
```

## Operator Defaults

When there is no special instruction from Javier, use these defaults:

- Review folder first.
- Apply maker's mark before slicing.
- OrcaSlicer only.
- `Penelope-Standard` for general parts.
- `Penelope-Production` for stronger or cleaner final parts.
- `Penelope-PLA` for standard PLA work.
- Respect 40/50/60mm/s speed caps.
- Require explicit approval before `djinn-penelope print`.

## Final Reminder

Penelope is dependable when treated like the machine she actually is: a Bowden, Marlin, 8-bit Ender 3 Pro with conservative speeds and a dedicated OrcaSlicer workflow. Most failures come from treating her like Calliope, using the wrong gcode pipeline, or forgetting that Bowden retraction and first-layer setup matter much more here than on the direct-drive Klipper machine.

— Claude / Marcus, 2026-06-21
