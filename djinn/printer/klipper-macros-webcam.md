# Klipper Macros — Djinn Print Safety

Paste these into `printer.cfg` on Calliope (192.168.1.114).
Access via Fluidd at http://192.168.1.114 → Configuration → printer.cfg

**Replace any previous DJINN_FAILURE_PARK macro with this full set.**

---

## 1. DJINN_PARK_CONFIG — variable store

Holds the safe park coordinates calculated per-print by `djinn-park-calc`.
Set automatically by `djinn-confirm-print` via `SET_DJINN_PARK` right after print starts.

```ini
[gcode_macro DJINN_PARK_CONFIG]
description: Stores per-print safe park position — set by djinn-confirm-print
variable_park_x: 5.0
variable_park_y: 220.0
variable_park_z: 50.0
gcode:
  # This macro only holds variables. Do not call directly.
```

---

## 2. SET_DJINN_PARK — called by djinn-confirm-print

```ini
[gcode_macro SET_DJINN_PARK]
description: Set safe park position for this print (called by djinn-confirm-print)
gcode:
  SET_GCODE_VARIABLE MACRO=DJINN_PARK_CONFIG VARIABLE=park_x VALUE={params.X|default(5)|float}
  SET_GCODE_VARIABLE MACRO=DJINN_PARK_CONFIG VARIABLE=park_y VALUE={params.Y|default(220)|float}
  SET_GCODE_VARIABLE MACRO=DJINN_PARK_CONFIG VARIABLE=park_z VALUE={params.Z|default(50)|float}
  RESPOND TYPE=echo MSG="Djinn: park position set — X{params.X} Y{params.Y} Z{params.Z}"
```

---

## 3. DJINN_FAILURE_PARK — dynamic park on failure

Uses the calculated values. Raises Z to the stored safe height (above all objects),
then moves XY to the clearest zone. Safe even on a full bed.

```ini
[gcode_macro DJINN_FAILURE_PARK]
description: Park nozzle safely above all objects on AI-detected failure
gcode:
  {% set px = printer["gcode_macro DJINN_PARK_CONFIG"].park_x %}
  {% set py = printer["gcode_macro DJINN_PARK_CONFIG"].park_y %}
  {% set pz = printer["gcode_macro DJINN_PARK_CONFIG"].park_z %}
  {% if not printer.pause_resume.is_paused %}
    PAUSE
  {% endif %}
  G90
  G1 Z{pz} F600
  G1 X{px} Y{py} F6000
  M104 S0
  M140 S0
  RESPOND TYPE=echo MSG="Djinn: parked at X{px} Y{py} Z{pz} — head clear of all pieces"
```

---

## 4. DJINN_RESUME_PRINT

```ini
[gcode_macro DJINN_RESUME_PRINT]
description: Resume print after Djinn failure park inspection
gcode:
  M104 S{printer.extruder.target}
  M140 S{printer.heater_bed.target}
  TEMPERATURE_WAIT SENSOR=extruder MINIMUM={printer.extruder.target - 5}
  RESUME
  RESPOND TYPE=echo MSG="Djinn: resuming print"
```

---

## After pasting all four:

1. Save printer.cfg in Fluidd
2. Click **Save & Restart**
3. Verify: in Fluidd console, run:
   ```
   SET_DJINN_PARK X=10 Y=220 Z=60
   ```
   Should respond: `Djinn: park position set — X10 Y220 Z60`

**Note:** `djinn-confirm-print` calls `SET_DJINN_PARK` automatically with the correct
values for every job. You never need to set it manually unless testing.

---

*Updated: 2026-05-27 — Claude*
