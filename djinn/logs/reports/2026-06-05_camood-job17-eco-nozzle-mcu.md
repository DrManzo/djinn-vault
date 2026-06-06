---
title: Session Report — Camood Job17: ECO solved, nozzle_mcu still blocking
agent: Salomon
date: 2026-06-05
tags: [djinn, report, printing, hardware, bug]
related: [[build-log]] | [[bugs]]
---

# Session Report — Camood Job17: ECO solved, nozzle_mcu still blocking

**Date:** 2026-06-05
**Agent:** Salomon
**Session type:** Debug + Print
**Trigger:** Complete end-to-end Typhon pipeline test with a Camood TTHQ print

---

## Summary

Two-part session. First: resolved the Creality START_PRINT ECO temp override through gcode ordering (PrusaSlicer's M190-wait approach). Sliced and started job17 — stable temp at 220°C, proper first layers. Second: print was killed at Z=4.2mm by BUG-014 (nozzle_mcu disconnect), 12th occurrence. Connector reseat did not permanently fix — hardware replacement needed.

---

## What Was Built or Changed

- **Camood_TTHQ_job17.gcode** — sliced via PrusaSlicer CLI (+ djinn-gcode-safety post-processor), uploaded to Calliope
- **BUG-014 updated** with 12th dropout at Z=4.2mm, 20 min into job17
- **SSH access to Calliope confirmed** (root/creality_ender3v3) — used to read printer.cfg, gcode_macro.cfg, printer_params.cfg

---

## Technical Decisions

**Decision — PrusaSlicer over OrcaSlicer for ECO bypass**  
Orca's non-wait bed temp (M140) races with Creality's START_PRINT macro. PrusaSlicer uses M190 (wait for bed temp) which completes before the macro runs. The `M190 S55 → M104 S220 → START_PRINT → M109 S220` sequence is the reliable workaround.

**Decision — No baud rate change on nozzle_mcu**  
Reducing from 230400 to 115200 requires firmware reflash on the GD32F303CBT6 MCU. Too risky to attempt remotely. Cable/connector replacement is the correct fix.

---

## Files Created or Modified

```
djinn/logs/bugs.md                              ← BUG-014 updated (12th dropout)
djinn/logs/build-log.md                         ← Job17 entry + ECO diagnosis
djinn/communications/COMMS.md                   ← Latest session entry
djinn/logs/reports/2026-06-05_camood-job17-eco-nozzle-mcu.md  ← This report
```

---

## Dependencies Installed

None.

---

## Tests & Validation

- **PrusaSlicer CLI**: Sliced Camood TTHQ in 90s. djinn-gcode-safety ran (0 M106 caps — Prusa already outputs S128 max; speed cap + PAUSE applied).
- **Moonraker upload**: Verified file at `/server/files/list` (22.1MB). Print started with `{result: ok}`.
- **Temp monitoring**: 220°C extruder stable during printing. Bed 55°C.
- **SSH to Calliope**: Confirmed `printer_params.cfg` values (default_bed_temp=60, default_extruder_temp=240, g28_ext_temp=140).
- **BUG-014 recurrence**: Confirmed in klippy.log: `Lost communication with MCU 'nozzle_mcu'` at 22:34:33 PDT. Toolhead at X=139.6, Y=104.9, Z=4.2mm.

---

## Known Issues / Caveats

1. **nozzle_mcu hardware** — 12th dropout. Connector reseat not sufficient. Replace cable harness or nozzle board.
2. **PrusaSlicer gcode format** — no `;TYPE:Support` markers → `djinn-gcode-support-cap` cannot strip supports from Prusa gcode. Only affects multi-object plates needing Z-capped supports.
3. **Power-loss recovery** — Klipper auto-restarts after MCU dropout but recovery state has empty filename → recovery gets stuck. Manual cancel required.
4. **ECO workaround is brittle** — relies on gcode ordering (M190 before START_PRINT). Any slicer producing M140 before M190 would re-trigger ECO.

---

## What's Next

- [ ] Replace Calliope nozzle_mcu cable harness or board — @Javier
- [ ] Re-attempt single Camood TTHQ print after hardware fix — @Salomon
- [ ] Wire `djinn-typhon-write --process-requests` into Typhon vault-sync timer — @Salomon
- [ ] Investigate OrcaSlicer variable resolution for `[nozzle_temperature_initial_layer]` in CLI mode — @Salomon

---

*— Salomon, 2026-06-05*
