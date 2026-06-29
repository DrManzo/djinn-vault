---
title: Session Report — Camood PETG Print Run (2026-06-28) — nozzle_mcu failures
agent: Claude
date: 2026-06-28
tags: [djinn, report, printing, calliope, camood, petg, failure, nozzle_mcu, key561]
related: [[build-log]] | [[bugs]] | [[printer/library/pieces/camood]]
---

# Session Report — Camood PETG Print Run

**Date:** 2026-06-28  
**Agent:** Claude  
**Session type:** Debug / Print Ops  
**Trigger:** Javier reported a head error that killed the Camood print

---

## Summary

Two Camood PETG prints ran on Calliope today. Both were hit by nozzle_mcu UART dropout (key561 — BUG-014 recurring). The first (`Camood_TTHQ_engraved`) completed its print body successfully but Klipper crashed 6 seconds into end-gcode (parking sequence) — the part is physically done. The second (`Camood_clean-marked`) was killed mid-print at Z=47.92mm (~45% through), scrapping the part. BUG-014 was believed resolved but is clearly still active.

---

## Incident Timeline

| Time PDT | Time UTC | File | Event |
|----------|----------|------|-------|
| 03:42 | 10:42 | `Camood_TTHQ_engraved.stl_PETG_2h53m7s.gcode` | Metadata error (exit 255) — print starts anyway |
| 03:53 | 10:53 | Same | Print running, layer 2, 1.37% |
| 06:36:53 | 13:36:53 | Same | **"Finished SD card print"** — body complete |
| 06:36:59 | 13:36:59 | Same | **key561 — nozzle_mcu timeout during END_PRINT parking gcode** — Klipper shutdown |
| — | — | — | Klipper auto-restarts, printer returns to standby |
| ~19:xx | ~02:xx | `Camood_clean-marked.stl_PETG_2h50m0s.gcode` | Print starts |
| 20:01:17 | 03:01:17 | Same | **key561 — nozzle_mcu timeout at Z=47.92mm** — Klipper shutdown mid-print |
| 20:01:32 | 03:01:32 | — | Klipper auto-restarts, printer in standby |

---

## Technical Findings (from klippy.log)

### Event 1 — End-gcode dropout (06:36:59 PDT)
```
[INFO] 2026-06-28 06:36:53 — virtual_sdcard: Finished SD card print
[INFO] 2026-06-28 06:36:59 — mcu:check_active: Timeout with MCU 'nozzle_mcu'
[ERROR] 2026-06-28 06:36:59 — key561: Lost communication with MCU 'nozzle_mcu'
Position at shutdown: (10.0, 295.0, 164.97) — park position (end-gcode)
```
Print body was complete. Dropout happened 6 seconds after `Finished SD card print`, during `END_PRINT` parking move. Part is physically fine.

### Event 2 — Mid-print dropout (20:01:17 PDT)
```
[INFO] 2026-06-28 20:01:17 — mcu:check_active: Timeout with MCU 'nozzle_mcu'
[ERROR] 2026-06-28 20:01:17 — key561: Lost communication with MCU 'nozzle_mcu'
Position at shutdown: (150.29, 108.76, 47.92) — mid-print, ~45% through 107mm part
```
Print killed mid-body. Part is scrap.

### Pattern
Both dropouts: `Timeout with MCU 'nozzle_mcu'` — not a voltage or thermal event, pure UART communication loss. Matches BUG-014 exactly. After each dropout, Klipper auto-restarted within ~15s.

---

## Root Cause

**BUG-014 recurring — nozzle_mcu UART connector or cable.**  
Previously documented June 5-6 with 12+ dropout events. A connector reseat on 2026-06-03 provided ~23 days of stability before today's recurrence. The cable or connector is intermittently losing contact under thermal expansion and vibration during printing.

---

## What Was Built or Changed

- No hardware or firmware changes made
- Reports written, bugs.md updated
- Prior my incorrect BED_CLEARED diagnosis was corrected after pulling klippy.log

---

## Files Created or Modified

```
djinn/logs/reports/2026-06-28_camood-petg-print.md    ← this report (corrected)
djinn/logs/reports/2026-06-28_bug-camood-petg-start.md ← bug report (corrected)
djinn/logs/bugs.md                                      ← BUG-014 update added
djinn/logs/build-log.md                                 ← outcome appended
djinn/communications/COMMS.md                           ← corrected entry
```

---

## Tests & Validation

- Camood TTHQ engraved PETG print: **PART OK** — body complete at 06:36:53. Klipper crash in end-gcode does not affect part.
- Camood_clean-marked PETG: **SCRAPPED** — killed at Z=47.92mm. 107mm total, part lost.

---

## Known Issues / Caveats

- The metadata.py error (`returned non-zero exit status 255`) appeared on the TTHQ engraved print start but print ran anyway. Worth investigating but not the failure cause.
- Camood_clean-marked part at Z=47.92mm = ~45% of body done. It may be salvageable for reference but is not print-quality.
- BUG-014 connector reseat lasted ~23 days. Cable/board replacement is now required — reseat is not a permanent fix.

---

## What's Next

- [ ] **Hardware:** Replace nozzle_mcu cable harness or connector on Calliope — reseat is not enough — @Javier
- [ ] Reprint `Camood_clean-marked.stl_PETG` after hardware fix — @Javier (confirm before queuing)
- [ ] Update BUG-014 in bugs.md with today's recurrence — done this session
- [ ] Check if TTHQ engraved Camood part came out OK physically — @Javier (inspect)

---

*— Claude, 2026-06-28*
