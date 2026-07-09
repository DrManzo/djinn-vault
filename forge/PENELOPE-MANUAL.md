================================================================================
                      PENELOPE — COMPLETE USER MANUAL
               Djinn 3D Print Pipeline | Ender-3 Pro
================================================================================
Version: 1.0 | Last updated: 2026-06-21 | Maintained by: DrManzo / Claude

> This document is a full standalone handoff. A new operator who has never
> used Penelope should be able to go from zero to a confirmed print using
> only this file. Do not mix files, profiles, or gcode with Calliope —
> the two machines are not compatible.

---

## Purpose

This manual is the complete operator guide for **Penelope**, the Creality
Ender 3 Pro in the Djinn printer fleet. Penelope is a Bowden-extruder machine
running stock Marlin firmware on an ATmega1284P 8-bit board. She is controlled
through **OctoPrint 1.11.7** on Salomon at http://localhost:5001 and through
the `djinn-penelope` CLI.

---

## Machine Identity

| Field              | Value                                      |
|--------------------|--------------------------------------------|
| Printer name       | Penelope                                   |
| Machine            | Creality Ender 3 Pro                       |
| Firmware           | Stock Marlin 1.1.6 / ATmega1284P 8-bit    |
| Extruder           | Bowden / stock                             |
| Build volume       | 220 × 220 × 250 mm                        |
| Host machine       | Salomon (192.168.1.225)                    |
| Connection         | /dev/ttyUSB0 at 115200 baud               |
| Web interface      | http://localhost:5001                      |
| OctoPrint login    | djinn / djinnprint                        |
| CLI                | djinn-penelope                            |
| Z offset (EEPROM)  | -0.5mm                                    |

---

## Core Differences from Calliope

Penelope is not a smaller copy of Calliope. She uses a different extrusion
path, different firmware, lower speed ceilings, and a completely separate
slicing pipeline. Gcode is NOT cross-compatible between the two machines.

| Category           | Calliope                       | Penelope                    |
|--------------------|--------------------------------|-----------------------------|
| Extruder           | Direct drive / Sprite          | Bowden / stock              |
| Firmware           | Klipper                        | Marlin                      |
| Retraction         | 0.5–0.6mm                      | 5.5mm                       |
| Build volume       | 300×300×330mm                  | 220×220×250mm               |
| Advanced tuning    | Pressure advance, input shaping| None                        |
| Host stack         | Moonraker / Fluidd             | OctoPrint                   |
| Slicer pipeline    | Calliope-specific OrcaSlicer   | Penelope-specific OrcaSlicer|
| Speed ceiling      | 100–200mm/s                    | 40–60mm/s                   |

---

## Absolute Rules

1. **Never send Creality Print gcode to Penelope.** Creality Print targets
   Klipper. Its start sequence uses macros (START_PRINT, EXCLUDE_OBJECT,
   SET_VELOCITY_LIMIT) that Marlin silently ignores. The bed never heats.
   Nothing prints.

2. **OrcaSlicer only**, with Penelope-specific profiles.

3. **Retraction is 5.5mm at 45mm/s.** Do not use direct-drive values.
   Penelope's Bowden tube is ~40cm — lower retraction causes stringing.

4. **Speed caps: 40 / 50 / 60 mm/s** (outer wall / inner wall / infill).
   The 8-bit board cannot handle Calliope speeds.

5. **No pressure advance. No input shaping.** Stock Marlin only.

6. **If a print stops more than once without a clear error, check bed
   leveling** before retrying. Do not loop re-sending the print.

7. **Never start a print without Javier's explicit per-job approval.**
   Upload is fine. Print start requires a go.

8. **Every print gets a maker's mark** before slicing (both printers).
   Show bottom-view preview for hollow models before proceeding.

9. **All STLs and 3MFs go to ~/Desktop/Review/ first.** Nothing is sliced
   or printed until Javier reviews and approves.

---

## Access and Control

### OctoPrint Web UI

- URL: http://localhost:5001
- Username: `djinn`
- Password: `djinnprint`

Use for: visual status, temperature graphs, file browser, terminal access.

### CLI

```bash
djinn-penelope status          # state, temps, progress
djinn-penelope files           # list uploaded gcode files
djinn-penelope upload <file>   # upload gcode to OctoPrint
djinn-penelope print <file>    # start a print (requires Javier approval)
djinn-penelope cancel          # cancel active print
```

Always run `djinn-penelope status` before and after every action.
A healthy idle printer shows: State = Operational.

### Serial Reconnect (after error or restart)

```bash
# If OctoPrint loses serial connection:
curl -s -X POST \
    -H "X-Api-Key: KOYv4Nj2nx7jvcxPnpCvxLqA9sF9IKCx8k5BueDc" \
    -H "Content-Type: application/json" \
    -d '{"command":"connect","port":"/dev/ttyUSB0","baudrate":115200}' \
    http://localhost:5001/api/connection
```

Or restart the service: `sudo systemctl restart djinn-penelope.service`

---

## Print Workflow — Mandatory Order

Every Penelope print follows this sequence without exception:

```
STL/3MF → ~/Desktop/Review/ → Javier approves
    → djinn-model-mark (maker's mark)
    → preview (mandatory for hollow models)
    → OrcaSlicer slice with Penelope profiles
    → verify gcode (temps, retraction)
    → djinn-penelope upload
    → Javier says go
    → djinn-penelope print
```

### Step 1 — Drop to Review

Place the STL or 3MF in `~/Desktop/Review/`. Do nothing else until
Javier approves the model.

### Step 2 — Apply Maker's Mark

```bash
djinn-model-mark /path/to/file.stl \
    --size 20 --depth 0.5 \
    --output /path/to/file-marked.stl
```

**Hollow models** (tube, ring, pipe): check inner radius first. Adjust
`--size` and/or `--x`/`--y` offset so the mark lands on wall material.
Render a bottom-view preview and show Javier before proceeding — this
step is mandatory.

### Step 3 — Slice with OrcaSlicer

```bash
MACHINE="Creality Ender-3 Pro 0.4 nozzle"
OUTPUT="$HOME/.local/share/forge/gcode"

/opt/orca-slicer/AppRun \
    --load-settings \
        "/opt/orca-slicer/resources/profiles/Creality/machine/${MACHINE}.json;\
${HOME}/Obsidian/djinn/printer/forge-slicer/profiles/process/Penelope-Standard.json" \
    --load-filaments \
        "${HOME}/Obsidian/djinn/printer/forge-slicer/profiles/filament/Penelope-PLA.json" \
    --slice 0 \
    --outputdir "$OUTPUT" \
    /path/to/file-marked.stl
```

Output lands at `~/.local/share/forge/gcode/plate_1.gcode`.

**With tree supports**, replace process profile with:
`Penelope-Standard-TreeSupports.json`

**Multiple copies**: pass the STL path multiple times (not `--repetitions`):
```bash
    file.stl file.stl file.stl
```

### Step 4 — Verify Gcode

Before uploading, confirm the gcode is correct:

```bash
python3 - << 'EOF'
import re
g = open('/path/to/file.gcode').read()
for line in g.split('\n'):
    if any(x in line for x in ['estimated','filament used [cm3]','M190','M109']):
        print(line.strip())
retracts = re.findall(r'G1 E(-[\d.]+) F\d+', g)
if retracts: print(f"Retraction: {min(float(e) for e in retracts)}mm")
EOF
```

Expected values:
- Bed temp: `M190 S65` (first layer) then `M140 S60`
- Hotend: `M109 S220`
- Retraction: `-5.5mm`
- No `START_PRINT`, `SET_VELOCITY_LIMIT`, or `EXCLUDE_OBJECT` lines

### Step 5 — Upload and Print

```bash
cp ~/.local/share/forge/gcode/plate_1.gcode \
   ~/.local/share/forge/gcode/penelope-<jobname>.gcode

djinn-penelope upload ~/.local/share/forge/gcode/penelope-<jobname>.gcode
# Wait for Javier go-ahead
djinn-penelope print penelope-<jobname>.gcode
```

---

## Profile Reference

Profiles live at:
`~/Obsidian/djinn/printer/forge-slicer/profiles/`

### Process Profiles

| Profile                          | Use                                      |
|----------------------------------|------------------------------------------|
| Penelope-Standard                | Default — no supports, no brim           |
| Penelope-Standard-TreeSupports   | Tree(auto) supports + 8mm brim           |
| Penelope-Standard-Supports       | Same as TreeSupports (compatibility)     |
| Penelope-Production              | 4 walls, 5 top shells, 8mm brim          |

All profiles share:
- Layer height: 0.2mm
- Infill: Gyroid 14%
- Speeds: 40 / 50 / 60 mm/s (outer / inner / infill)
- No pressure advance, no input shaping

### Filament Profile — Penelope-PLA

| Setting              | Value                    |
|----------------------|--------------------------|
| Hotend (print)       | 220°C                    |
| Hotend (first layer) | 220°C                    |
| Bed (first layer)    | 65°C                     |
| Bed (remaining)      | 60°C                     |
| Retraction           | 5.5mm at 45mm/s          |
| Max volumetric speed | 9 mm³/s                  |
| Flow ratio           | 0.98                     |

---

## Z Offset

Penelope's Z offset is set to **-0.5mm**, saved in EEPROM.

To verify or re-set after a reset:
```bash
# In OctoPrint terminal, or via API command:
M851 Z-0.5    # set offset
M500          # save to EEPROM
M503          # verify — look for "Z Probe Offset" line
```

To adjust live during a print (babystepping):
```bash
curl -s -X POST \
    -H "X-Api-Key: KOYv4Nj2nx7jvcxPnpCvxLqA9sF9IKCx8k5BueDc" \
    -H "Content-Type: application/json" \
    -d '{"commands": ["M290 Z-0.1"]}' \
    http://localhost:5001/api/printer/command
```

Adjust in -0.1mm increments until first layer squishes flat against bed.
Save the final value to EEPROM when done.

**Signs the Z offset is wrong:**
- Too high: first layer looks like a shadow, no material bonding, ghosting
- Too low: nozzle drags, print tears, grinding sound

---

## Filament Change

1. Heat hotend: OctoPrint → Control → set hotend to 220°C, wait
2. In OctoPrint terminal: `M600`
3. Printer will pause, retract filament, and wait
4. Pull old filament out from the top of the Bowden tube
5. Insert new filament, push until it reaches the hotend
6. Confirm extrusion in OctoPrint to resume

**Never send M600 with a cold hotend.** Marlin will reject it and may
trigger an emergency stop (M112), requiring a full reconnect.

---

## Bed Leveling

Penelope has no ABL (auto bed leveling). Manual leveling required.

1. Home all axes: `G28`
2. Disable steppers: `M84`
3. Move nozzle to each corner and center by hand
4. Adjust bed knobs until a sheet of paper slides with slight resistance
5. Re-run after any crash or significant temperature change

**If a print stops more than once without a clear error — check bed
leveling first before any other diagnosis.**

---

## Troubleshooting

### Print stops immediately / comm error

Check OctoPrint logs:
```bash
tail -30 ~/.octoprint-penelope/logs/octoprint.log | grep -iE "error|state|resend"
```

If you see `Printer keeps requesting line 1` — this is the Marlin checksum
resend loop. Reconnect and verify config has `neverSendChecksum: true`.

### No material / ghost first layer

Z offset too high. Babystep down in -0.1mm increments during print.
After confirmed good layer, save with `M851 Z-X.X` + `M500`.

### Filament won't pull / extruder skipping

Extruder arm spring tension too low. The drive gear is slipping on the
filament. Increase tension on the extruder arm screw.
Also check: is hotend at temp? Cold nozzle will always jam.

### OctoPrint shows Error / Offline after error

```bash
sudo systemctl restart djinn-penelope.service
sleep 8
# Then reconnect via API (see serial reconnect section above)
```

### Firmware warning in OctoPrint

"Broken implementation of communication protocol" from Creality Marlin
is cosmetic. Fixed by `sdSupport: false` in config — already set.

### Wrong bed temp in gcode (shows M190 S0 or S35)

Wrong filament profile used. Use `Penelope-PLA.json` only.
The field is `cool_plate_temp`, not `bed_temperature`.

---

## Known Bugs and Lessons

| Bug | Root cause | Status |
|-----|-----------|--------|
| Checksum resend loop | `alwaysSendChecksum: true` conflicts with Creality Marlin | Fixed — `neverSendChecksum: true` |
| Creality Print gcode silent fail | Klipper macros ignored by Marlin, bed never heats | Documented — OrcaSlicer only |
| Z offset unconfigured on first install | Stock Marlin ships with 0 offset | Fixed — -0.5mm saved to EEPROM |
| M600 with cold hotend triggers M112 emergency stop | Marlin safety feature | Always heat to 220°C before M600 |
| OctoPrint 1.11.x global API key read-only | Breaking change in 1.11.x | Fixed — user-specific key in users.yaml |

---

## OctoPrint Config Reference

Key settings in `~/.octoprint-penelope/config.yaml`:

```yaml
serial:
  neverSendChecksum: true        # required — alwaysSendChecksum breaks Marlin
  alwaysSendChecksum: false
  waitForStartOnConnect: true
  helloCommand: "M110 N0"
  timeout:
    communication: 30

feature:
  sdSupport: false               # prevents Creality firmware warning

accessControl:
  enabled: false                 # local machine, no network exposure
```

---

## File Locations

| Item | Path |
|------|------|
| OctoPrint config | ~/.octoprint-penelope/config.yaml |
| OctoPrint users | ~/.octoprint-penelope/users.yaml |
| API key (env) | ~/.config/djinn/printers.env |
| CLI | ~/.local/bin/djinn-penelope |
| Process profiles | ~/Obsidian/djinn/printer/forge-slicer/profiles/process/Penelope-*.json |
| Filament profile | ~/Obsidian/djinn/printer/forge-slicer/profiles/filament/Penelope-PLA.json |
| Workflow doc | ~/Obsidian/djinn/printer/PENELOPE-WORKFLOW.md |
| Gcode output | ~/.local/share/forge/gcode/ |

---

*— Claude / Marcus, 2026-06-21*
