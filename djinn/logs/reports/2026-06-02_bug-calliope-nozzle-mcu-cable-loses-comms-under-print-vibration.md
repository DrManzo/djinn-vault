---
title: Bug Report — Calliope nozzle_mcu loses comms under print vibration (frame flex)
agent: Claude
date: 2026-06-02
severity: high
status: fixed
tags: [djinn, bug, calliope, klipper, hardware]
related: [[bugs]] | [[build-log]] | [[SUPPORT-GUIDE]]
---

# Bug Report — Calliope nozzle_mcu loses comms under print vibration (frame flex)

**Date:** 2026-06-02  
**Agent:** Claude  
**System:** Calliope (Ender-3 V3 Plus)  
**Severity:** high  
**Status:** fixed  

---

## Root Cause

**Two compounding failure modes, both now resolved:**

### Failure Mode 1 — EMI (resolved 2026-06-02)
`bridge_fan_speed=100` in PrusaSlicer profile generated `M106 S255` at bridge infill sections. 100% fan on the Sprite Pro extruder causes EMI that corrupts nozzle_mcu serial comms → `bytes_invalid` spikes → `retransmit_seq` skyrockets → Klipper `klippy_shutdown` (key561).

**Signature:** Gradual `retransmit_seq` climb with `bytes_invalid > 0` at moment of dropout.

**Fix:** Capped all fan settings to 50% in both PrusaSlicer profiles (`~/.config/djinn/` and `~/.config/forge/`) and OrcaSlicer Calliope PLA filament profile.

---

### Failure Mode 2 — Frame flex / cable stress (resolved 2026-06-03)
A cross-support brace on the Calliope frame was significantly loose. Under toolhead movement, the frame flexed — at specific XY positions (observed: Y=124–136 on the proxy stand geometry) the flex was enough to stress the nozzle_mcu cable bundle and momentarily break the signal path.

**Signature:** Instant `retransmit_seq` spike with `bytes_invalid = 0` at moment of dropout (complete signal loss, no corruption → physical disconnect, not EMI). Failures were position-dependent and intermittent.

**Fix:** Javier physically tightened the loose cross-support brace (2026-06-03).

---

## Symptom

- Klipper key561: "Lost communication with MCU 'nozzle_mcu'"
- Print aborts after 8–15 minutes consistently
- Two distinct patterns in the telemetry:
  - EMI: `bytes_invalid` rises at spike time
  - Frame flex: `bytes_invalid = 0` at spike time, clean silence

---

## Steps to Reproduce

1. Slice a model with engraved/embossed text (creates many bridge sections) using default PrusaSlicer profile (bridge_fan=100)
2. Print on a Calliope with a loose frame cross-support
3. At bridge infill sections (~8–15 min), M106 S255 fires + frame vibration at specific toolhead positions → dual failure

---

## Fix Applied

1. All PrusaSlicer profiles: `bridge_fan_speed = 50`, `max_fan_speed = 50`, `min_fan_speed = 50`
2. OrcaSlicer Calliope PLA filament: `fan_max_speed = 50`, `overhang_fan_speed = 50`
3. Frame cross-support brace physically tightened by Javier

---

## Verification

Pending — Tornado Recycler print will be the first post-fix test. Run `djinn-print-tracer --interval 5 &` before starting.

---

## Rule / Lesson

> **Rule:** On any Klipper printer, distinguish nozzle_mcu dropout patterns by `bytes_invalid` at the moment of spike: `> 0` = EMI (fix: cap fan speed); `= 0` = physical disconnect or power glitch (fix: inspect cable, frame rigidity, power supply). Treat them as separate bugs — the EMI fix will not resolve the physical one.

> **Secondary rule:** After any print failure on the Ender-3 V3 Plus, check all frame cross-support braces for tightness. PLA prints generate significant vibration; frame flex compounds cable stress at specific toolhead positions.

---

*— Claude, 2026-06-03*
