# Klipper Macros — Webcam Monitor Integration

Paste these into `printer.cfg` on Calliope (192.168.1.114).
Access via Fluidd at http://192.168.1.114 → Configuration → printer.cfg

---

## DJINN_FAILURE_PARK

Called automatically by `djinn-webcam-monitor` when a print failure is detected.
Parks the nozzle clear of the plate so intact pieces aren't knocked over.

```ini
[gcode_macro DJINN_FAILURE_PARK]
description: Park nozzle clear of plate on AI-detected failure
gcode:
  {% if not printer.pause_resume.is_paused %}
    PAUSE
  {% endif %}
  G91
  G1 Z20 F600
  G90
  G1 X10 Y290 F6000
  M104 S0
  RESPOND TYPE=echo MSG="Djinn: failure park complete — head clear of plate"
```

---

## DJINN_RESUME_PRINT

Run this manually after inspecting the failure to resume if pieces are salvageable.

```ini
[gcode_macro DJINN_RESUME_PRINT]
description: Resume print after Djinn failure park
gcode:
  RESUME
  RESPOND TYPE=echo MSG="Djinn: resuming print"
```

---

## After pasting:

1. Save printer.cfg in Fluidd
2. Click **Save & Restart** (or send `FIRMWARE_RESTART` via console)
3. Verify: in Fluidd console, run `DJINN_FAILURE_PARK` — nozzle should lift Z20 and park at X10 Y290

---

*Installed: 2026-05-26 — Claude*
