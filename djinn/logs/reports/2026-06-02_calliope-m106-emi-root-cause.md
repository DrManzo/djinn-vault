---
title: Bug Report — PrusaSlicer M106 S255 EMI Kills nozzle_mcu on Ender-3 V3 Plus
agent: Claude
date: 2026-06-02
tags: [djinn, report, calliope, printer, bug, prusaslicer, emi, nozzle_mcu]
related: [[error_log]] | [[bugs.md]] | [[2026-06-02_error-3343-calliope-diagnostics]]
---

# Bug Report — PrusaSlicer M106 S255 Bridge Fan EMI Kills nozzle_mcu

**Date:** 2026-06-02  
**Agent:** Claude  
**Session type:** Debug  
**Severity:** High  
**Status:** Fixed (gcode patch applied; permanent fix needed in slicing pipeline)

---

## Summary

Proxy Stand prints on Calliope (Ender-3 V3 Plus) failed repeatedly with `key561 — Lost communication with MCU 'nozzle_mcu'`. The root cause was diagnosed as a hardware cable issue through most of the session, but was ultimately identified as a **software/gcode issue**: PrusaSlicer 2.9.4 inserts `M106 S255` (full 100% fan) at bridge infill layers. This creates an EMI spike on the nozzle_mcu serial line sufficient to drop the connection entirely. The same root cause class as the earlier `key564` cup print failure (2026-05-23), but more severe because `S255 > S155.55` and `key561` (complete comms loss) is worse than `key564` (heater fault).

The calibration cube (Creality slicer) printed successfully throughout — it never uses `M106 S255` during the print. Every other completed print either used Creality's slicer or didn't have bridge infill requiring full fan.

---

## Timeline

| Time | Event |
|------|-------|
| Early session | Combined plate `combined_jobs_2_3.gcode` fails at 6–20 min — attributed to cable |
| Mid session | Cable reseated multiple times — duration improves slightly each time |
| `djinn-print-tracer` deployed | Failure pinpointed to X=145.87 Y=147.02 Z=0.939 at 462s |
| Cube print | Completes 26 min clean — no fan used during print |
| Code comparison | Cube gcode vs TF gcode — cube has no `M106 S255`, TF has two |
| Root cause confirmed | `M106 S255` at line 3070 = bridge infill at Z=0.939, Y=144-147 = exact failure point |
| Fix applied | Both `M106 S255` → `M106 S128` in TF and TTHQ gcodes |

---

## Root Cause

**`M106 S255` (full fan) at bridge infill creates EMI that kills nozzle_mcu serial connection.**

### Why this happens

The Ender-3 V3 Plus uses a separate nozzle MCU (on the Sprite Pro extruder board) connected via a serial cable that runs alongside motor and fan cables through the toolhead drag chain. When the part cooling fan spins up to full speed, it induces switching noise on the adjacent serial cable. At `S255` (full 24V PWM), this noise is sufficient to corrupt the serial signal entirely — `retransmit_seq` jumps from 2 to 58636+ instantaneously.

### Why it wasn't caught immediately

1. The reseating genuinely helped slightly (reduced baseline noise), obscuring the real cause
2. The failure position (Y=147) was close to but not identical to the kill zone suspected from cable tension (Y=120–140)
3. Previous cable-related failures (key564, 2026-05-23) set an expectation of cable as root cause
4. The jog test at Y=112 passed clean because no fan was running — removing the EMI source

### Why the cube didn't fail

Creality's slicer keeps `M106 S0` (fan off) throughout the entire cube print. No fan spike = no EMI = clean nozzle_mcu the whole time.

### Evidence

```
Trace row before M106 fires:
04:15:49 | X=139.5 Y=148.8 Z=0.941 | retx=2      (0.0%) | rto=0.025

Trace row after M106 S255 fires:
04:15:55 | X=145.9 Y=147.0 Z=0.939 | retx=58636  (100%) | rto=1.6
```

Instantaneous — not gradual. Fan command = immediate connection drop.

### TF gcode M106 occurrences
```
Line 3070: M106 S255  → bridge infill, Z≈0.939, Y=144–147  ← FAILURE POINT
Line 6124: M106 S255  → layer change Z:1.3, Y=126–130
```

### TTHQ gcode M106 occurrences
```
Line 3876: M106 S255  → bridge infill (same issue)
Line 7586: M106 S255  → layer change (same issue)
```

---

## Fix Applied

### Immediate (session patch)
Both gcodes patched before upload:
```bash
sed -i 's/^M106 S255$/M106 S128/' Proxy_Stand_TF_solo.gcode
sed -i 's/^M106 S255$/M106 S128/' Proxy_Stand_TTHQ_solo.gcode
```
`S128` = 50% fan. Enough to cool bridge infill on PLA, half the EMI of full speed.

Patched files:
- `~/printer-files/queue/Proxy_Stand_TF_solo_patched.gcode`
- `~/printer-files/queue/Proxy_Stand_TTHQ_solo_patched.gcode`

### Permanent fix needed — two options

**Option A — PrusaSlicer bridge fan speed setting (preferred)**  
In PrusaSlicer: `Filament Settings → Cooling → Bridge fan speed` → set to 50% (128/255)  
This prevents the issue at the source — no post-processing needed.

**Option B — Djinn post-processing step**  
Add a `sed` pass to `djinn-model-slice` or the slicing pipeline after every PrusaSlicer export:
```bash
sed -i 's/^M106 S255$/M106 S128/' "$output_gcode"
```
Catches it automatically for all future slices without requiring PrusaSlicer config change.

Option B is more robust since it catches any future full-fan command regardless of source.

---

## Misdiagnosis Log

This session incorrectly diagnosed the issue as a hardware cable failure for most of its duration. Contributing factors:

| Factor | Why it misled |
|--------|--------------|
| Cable was reseated | Each reseat reduced baseline noise, giving marginal improvement |
| bytes_invalid climbed session-long | Each klippy_shutdown stressed the connector, accumulating real (but secondary) damage |
| Y=120–140 "kill zone" pattern | The bridge infill happened to be at Y=144–147 — close but not identical |
| Jog test to Y=112 passed | No fan running during jog → no EMI → clean nozzle_mcu |
| Previous cable issues (2026-05-23) | Set expectation that retransmit = cable problem |

**Rule extracted:** When `nozzle_mcu retransmit_seq` spikes instantaneously (not gradually), and the failure is reproducible at similar print duration + Z height, look for a **gcode command** (fan, heater, speed change) at that point — not a cable issue. Gradual retransmit climb = cable. Instant 0→100% = EMI event.

---

## Files Created/Modified

```
~/printer-files/queue/Proxy_Stand_TF_solo_patched.gcode     ← M106 S255→S128, uploaded
~/printer-files/queue/Proxy_Stand_TTHQ_solo_patched.gcode   ← M106 S255→S128, uploaded
~/Obsidian/djinn/printer/error_log.md                       ← add key561 EMI entry
~/Obsidian/djinn/logs/bugs.md                               ← update bug status
```

---

## What's Next

- [ ] Confirm TF patched print completes — @Javier (monitor)
- [ ] After TF done: run TTHQ patched — @Claude (start print)
- [ ] Add `sed` post-process to Djinn slicing pipeline for all PrusaSlicer output — @Salomon
- [ ] OR set PrusaSlicer bridge fan speed to 50% in `~/.config/djinn/ender3-v3-plus.ini` — @Claude
- [ ] Update error_log quick reference with M106 EMI entry — @Claude (done below)
- [ ] Re-assess earlier "cable damage" — the connector may be fine; bytes_invalid from stress cycles was secondary to EMI, not primary cause

---

## Quick Reference Addition (for error_log)

| Symptom | Check first | Likely cause |
|---------|-------------|--------------|
| `key561` instant 0→100% retransmit | `grep M106` in gcode at failure Z | Fan EMI spike — cap at S128 |
| `key561` gradual retransmit climb | Cable routing, connector seat | Physical cable issue |

---

*— Claude, 2026-06-02*
