---
title: Bug Report — Camood PETG nozzle_mcu dropouts (BUG-014 recurrence)
agent: Claude
date: 2026-06-28
tags: [djinn, bug, printing, calliope, nozzle_mcu, key561, bug-014]
related: [[bugs]] | [[2026-06-28_camood-petg-print]] | [[2026-06-05_camood-job17-eco-nozzle-mcu]]
---

# Bug Report — Camood PETG nozzle_mcu Dropouts

**Date:** 2026-06-28  
**System:** Calliope (Ender-3 V3 Plus) — nozzle_mcu UART cable/connector  
**Severity:** high  
**Status:** open — hardware replacement required

---

## This is BUG-014 Recurring

BUG-014 was first documented 2026-06-05 (12+ dropout events). A connector reseat on 2026-06-03 provided ~23 days of stability. Today it returned.

---

## Symptoms

Two key561 (`Lost communication with MCU 'nozzle_mcu'`) events during Camood PETG prints:

**Event 1 — 2026-06-28 06:36:59 PDT (13:36 UTC):**
- Camood_TTHQ_engraved print body had just finished (`Finished SD card print` at 06:36:53)
- nozzle_mcu timed out 6 seconds later during END_PRINT parking gcode
- Position: X=10, Y=295, Z=165 (park position)
- Part is complete — Klipper crash in end-gcode only

**Event 2 — 2026-06-28 20:01:17 PDT (03:01 UTC June 29):**
- Camood_clean-marked print running mid-body
- nozzle_mcu timed out at Z=47.92mm (~45% of 107mm print)
- Position: X=150.29, Y=108.76, Z=47.92
- Part is SCRAPPED

Both events: `Timeout with MCU 'nozzle_mcu'` → `key561` → Klipper emergency shutdown → auto-restart → standby.

---

## Root Cause

UART connector or cable between Klipper host and the nozzle_mcu board loses contact intermittently. Not a thermal event, not a voltage spike — pure communication timeout. The connector reseat from June 3 was not a permanent fix. The issue is either:
- A cracked or degraded cable with intermittent internal continuity
- A connector that reseats superficially but doesn't make lasting mechanical contact
- Board-side connector solder joint deterioration

The fact that it recurred after 23 days (not minutes/hours as in early June) suggests the reseat does help temporarily but the underlying fault is progressive.

---

## Previous Remediation Attempts

| Date | Action | Result |
|------|--------|--------|
| 2026-06-03 | Connector reseat | Stable for 23 days |
| 2026-06-05 | BUG-014 first documented | 12+ dropouts in one session |

---

## Fix Required

**Replace the nozzle_mcu cable harness.** Connector reseat is not sufficient.

Options in order of preference:
1. Replace entire cable run from nozzle_mcu board to host header
2. Replace just the connector (if board-side joint is intact)
3. Add strain relief loop + cable slack as secondary hardening

Until replaced, every long PETG/tall print on Calliope is at dropout risk.

---

## Lesson

key561 on Calliope = nozzle_mcu UART loss = cable/connector hardware fault. Connector reseat buys weeks, not permanence. When it recurs, it means the fault is progressing — replace the hardware, don't reseat again.

---

*— Claude, 2026-06-28*
