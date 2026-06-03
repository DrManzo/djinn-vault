---
title: Session Report — Protocol Update + OrcaSlicer Handoff
agent: Claude
date: 2026-06-03
tags: [djinn, report, calliope, orcaslicer, protocol, triage]
related: [[2026-06-03_calliope-upgrade-orcaslicer]] | [[SUPPORT-GUIDE]] | [[PRINT-PROFILES]]
---

# Session Report — Protocol Update + OrcaSlicer Handoff

**Date:** 2026-06-03  
**Agent:** Claude  
**Session type:** Continuation — protocol clarification + documentation update  
**Trigger:** Javier asked whether protocol additions from proxy stand session are still necessary after OrcaSlicer switch

---

## Summary

Clarified which print protocol rules carry forward with OrcaSlicer vs. which were PrusaSlicer-specific. Updated SUPPORT-GUIDE.md and PRINT-PROFILES.md to reflect the dual-slicer setup and the new key561 triage finding (bytes_invalid=0 = physical, not EMI). Confirmed Salomon has all required programs installed.

---

## What Was Built or Changed

### SUPPORT-GUIDE.md
- Triage section updated with `bytes_invalid` interpretation rule:
  - `bytes_invalid > 0` at dropout → EMI → fan cap
  - `bytes_invalid = 0` at dropout → physical disconnect/power glitch → hardware inspection, fan cap won't help
- Added 2-minute cool-down rule between klippy_shutdown and retry
- Added Slicer Setup section documenting dual-slicer role split and fan constraint

### PRINT-PROFILES.md
- Added slicer note clarifying OrcaSlicer for interactive, PrusaSlicer for CLI pipeline
- Fan cap rule noted as hardware constraint applying to both slicers

---

## Program Status — Salomon

| Program | Status | Role |
|---------|--------|------|
| OrcaSlicer 2.3.2 | ✅ Flatpak installed | Interactive slicing + direct Moonraker upload |
| PrusaSlicer | ✅ System install `/usr/bin/prusa-slicer` | CLI pipeline (djinn-model-slice, djinn-model-combine) |
| djinn-print-tracer | ✅ `~/.local/bin/` | Real-time nozzle_mcu diagnostic during prints |
| djinn-print-monitor-v2 | ✅ `~/.local/bin/` | Background failure detector |
| djinn-model-mark | ✅ `~/.local/bin/` | Maker's mark injection |
| djinn-model-slice | ✅ `~/.local/bin/` | CLI slice → queue → Discord |

Nothing missing. No new installs required.

---

## Protocol Rules — What Carries Forward

**Still required (hardware constraints, slicer-agnostic):**
- `bridge_fan_speed = 0` in OrcaSlicer filament profile — nozzle_mcu EMI risk is a board characteristic
- cube-first triage before assuming hardware failure
- `djinn-print-tracer` for any nozzle_mcu investigation
- ≥2 min between klippy_shutdown and retry
- Explicit per-job authorization before starting any print

**No longer needed:**
- Manual `sed` patches on gcode to fix M106 S255 — OrcaSlicer won't generate it with correct settings
- Manual curl uploads — OrcaSlicer sends directly via Moonraker
- PrusaSlicer-specific gcode workarounds for interactive jobs

**New rule added this session:**
- `bytes_invalid = 0` at moment of instant dropout = physical connector or power issue, NOT EMI. Fan cap does not fix this. Requires physical inspection.

---

## Still Open

- [ ] nozzle_mcu physical connector inspection — instant-dropout pattern (bytes_invalid=0) unresolved
- [ ] Re-seat 4 strain gauge connectors under bed (error 3343) — @Javier
- [ ] Verify bridge_fan_speed=0 in OrcaSlicer Calliope filament profile — @Javier
- [ ] New Proxy Stand STL incoming — reslice with OrcaSlicer when received

---

*— Claude, 2026-06-03*
