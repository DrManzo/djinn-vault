---
title: Session Report — Proxy Stand Print Failures Root Cause + PLA Profile Fix
agent: Claude
date: 2026-06-02
tags: [djinn, report, calliope, printer, prusaslicer, emi, pla, debug]
related: [[error_log]] | [[bugs.md]] | [[2026-06-02_calliope-m106-emi-root-cause]] | [[build-log]]
---

# Session Report — Proxy Stand Print Failures + PLA Profile Fix

**Date:** 2026-06-02  
**Agent:** Claude  
**Session type:** Debug + Build  
**Trigger:** Proxy Stand pair (Typhons Forge + Terp Tribe HQ) failing repeatedly mid-print on Calliope (Ender-3 V3 Plus, 2 weeks old)

---

## Summary

Multiple Proxy Stand prints failed with `key561 — Lost communication with MCU 'nozzle_mcu'`. The session spent significant time pursuing a hardware cable diagnosis before the real cause was identified: PrusaSlicer's PLA profile had `bridge_fan_speed = 100%`, generating `M106 S255` (full fan) at bridge infill layers. This creates an EMI spike that instantly kills the nozzle_mcu serial connection. The calibration cube (Creality slicer, no fan during print) ran clean throughout, which was the key diagnostic signal. Fix: updated PLA profile to 50% fan across all settings, cube-style start gcode, bed at 60°C. Both proxy stand gcodes resliced and uploaded clean.

---

## What Was Built or Changed

- **`~/.local/bin/djinn-print-tracer`** — new real-time diagnostic. Polls Moonraker every 5s, logs nozzle_mcu retransmit stats + XY position per sample. Sends Telegram alert on degradation. Essential for distinguishing instant EMI spikes from gradual cable failures.
- **`~/.config/djinn/ender3-v3-plus.ini`** — PLA profile corrected:
  - `max_fan_speed`: 100 → 50
  - `bridge_fan_speed`: 100 → 50
  - `min_fan_speed`: 100 → 50
  - `bed_temperature`: 55 → 60 (matches Creality cube baseline)
  - `start_gcode`: now matches Creality slicer style (`M82 → M140 S0 → M104 S0 → START_PRINT`) — no blocking pre-wait
- **`~/printer-files/queue/ProxyStandTF.gcode`** — clean reslice, no supports, `M106 S127.5`, cube-style start
- **`~/printer-files/queue/ProxyStandTTHQ.gcode`** — same
- **`~/Obsidian/djinn/printer/prints/2026-06-02_proxy-stands/`** — archived STLs + patched gcodes + README
- **`~/Obsidian/djinn/printer/error_log.md`** — key561 history + triage protocol added
- **`~/Obsidian/djinn/printer/SUPPORT-GUIDE.md`** — cube-first triage protocol added
- **QUEUE.md TASK-065** — spec for Salomon to automate the triage protocol in djinn-print-monitor

---

## Root Cause

**PrusaSlicer profile had `bridge_fan_speed = 100%`.** At bridge infill layers, PrusaSlicer emits `M106 S255`. On the Ender-3 V3 Plus, spinning the part cooling fan to full speed induces EMI on the nozzle_mcu serial cable, instantly dropping the connection (`retransmit_seq` jumps 0 → 100% in one 5s polling interval).

### How the cube proved it
The calibration cube (Creality slicer) never uses `M106 S255` during the print — fan stays off. It ran the entire session without a single nozzle_mcu issue. Every failed print used PrusaSlicer with `bridge_fan_speed = 100`.

### The diagnostic signal that was missed
All failures happened at **consistent duration** (363s, 462s, 522s) not consistent XY position. That pattern means a specific gcode command, not hardware. Cable failures are random timing. We chased the cable for too long.

---

## Misdiagnosis Timeline

| Step | What we thought | Why it was wrong |
|------|----------------|-----------------|
| Early failures | Cable tension at Y=120–140 | Failure duration was consistent, not position |
| Cable reseated | Hardware fix | Duration improved slightly (less noise), not because routing fixed |
| Jog test Y=112 passed | Cable confirmed good | No fan during jog = no EMI = always passes |
| Cube passed | Hardware good | Cube never fires M106 |
| Code comparison | Found M106 S255 | ✅ Actual root cause |

**Time lost to hardware diagnosis: ~4 hours.**

---

## Notes for Next Time

### Rule 1 — Consistent duration = gcode command, always
If the same print dies at the same point every run, stop touching hardware. Open the gcode and find what command fires at that duration. `grep M106`, `grep M104`, `grep M204`. Hardware failures are random. Gcode failures are deterministic.

### Rule 2 — Run the cube before touching anything
The calibration cube (`CRtestcube_Ender-3 V3 Plus_26m.gcode`) is the hardware baseline. It's always on the printer. If the cube prints clean, the hardware is clean. Full stop. Go straight to gcode analysis.

### Rule 3 — Check the slicer profile before blaming the print
`bridge_fan_speed = 100` was in the profile from day one. Every PrusaSlicer slice on this machine had `M106 S255` baked in. The fix was in the profile, not in the gcode, not in the hardware.

### Rule 4 — PrusaSlicer ≠ Creality slicer
PrusaSlicer's defaults are aggressive for this printer:
- Full fan at bridge infill — causes EMI on nozzle_mcu
- Blocking `M190`/`M109` before `START_PRINT` — redundant, can cause timing issues
- Relative extrusion (M83) vs absolute (M82) — not a problem but different
- 55°C bed vs 60°C — slightly less adhesion

Always compare against what Creality's own slicer generates for the same model. If Creality's version works and PrusaSlicer's doesn't, the profile is wrong.

### Rule 5 — djinn-print-tracer tells you everything
Run it on every failed print. The trace shows:
- `retransmit_seq` jumps 0→100% instantly → EMI from a gcode command
- `retransmit_seq` climbs gradually over minutes → physical cable issue
- XY position is frozen after failure → that's where the toolhead was when it died, not necessarily the cause

### Rule 6 — If it survived the first 30 seconds, the start position is not the problem
The proxy stand brim starts at Y=112. The prints died at 363–462 seconds. If Y=112 was the issue, it would have died in the first 10 seconds. Never chase position if the print survives the brim.

---

## Files Created or Modified

```
~/.local/bin/djinn-print-tracer                              ← new: real-time nozzle_mcu + XY tracer
~/.config/djinn/ender3-v3-plus.ini                          ← fan 50%, bed 60°C, cube start gcode
~/printer-files/queue/ProxyStandTF.gcode                     ← clean reslice, no supports
~/printer-files/queue/ProxyStandTTHQ.gcode                   ← clean reslice, no supports
~/Obsidian/djinn/printer/prints/2026-06-02_proxy-stands/     ← full job archive
~/Obsidian/djinn/printer/error_log.md                        ← key561 history + triage protocol
~/Obsidian/djinn/printer/SUPPORT-GUIDE.md                    ← cube-first triage protocol
~/Obsidian/djinn/logs/bugs.md                                ← M106 EMI bug logged
~/Obsidian/djinn/logs/reports/2026-06-02_calliope-m106-emi-root-cause.md  ← detailed EMI report
~/Obsidian/djinn/communications/QUEUE.md                     ← TASK-065: automate triage
```

---

## What's Next

- [ ] Confirm ProxyStandTF.gcode prints clean end-to-end — @Javier
- [ ] After TF done: run ProxyStandTTHQ.gcode — @Claude (queue it)
- [ ] TASK-065: Wire triage protocol into djinn-print-monitor (cube auto-queues on failure) — @Salomon
- [ ] Re-seat 4 strain gauge connectors under bed (error 3343 still unresolved) — @Javier
- [ ] Mac Djinn node: complete setup (vault clone, workspace symlink, env files) — @Javier

---

*— Claude, 2026-06-02*
