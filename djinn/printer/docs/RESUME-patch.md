# RESUME Patch — Ender 3 V3 Plus Power-Loss Recovery Speed Lock

**Status:** Active known issue on Calliope  
**Root cause:** Creality's `RESUME` macro sets `M220 S20` (20% speed) as a safety
measure during power-loss recovery. When the print resumes after a PLR event,
Klipper does not reset the speed factor. The printer runs at 20% indefinitely
and the UI does not always show this visually.

---

## Symptom

- Print resumes after power loss but runs extremely slowly
- `M220` shows `S20` in console
- Speed slider in Mainsail shows 100% but actual is 20%

## Manual Fix

At Mainsail console:
```
M220 S100
```

## Guardian Fix (automatic)

`djinn-print-guardian` detects `speed_factor < 0.25` during any active or paused
print and injects `M220 S100` automatically. No manual intervention required.

## Permanent Fix (optional — modifies firmware macros)

Edit the Creality RESUME macro in `printer.cfg`:
```
[gcode_macro RESUME]
rename_existing: RESUME_BASE
gcode:
  RESUME_BASE {rawparams}
  M220 S100   ; restore speed after PLR resume
```

> Backup printer.cfg before editing. Guardian handles this automatically
> without requiring a config change.

---

*Documented by djinn-print-guardian research pass — 2026-06-05*
