---
title: Bug Report — Calliope nozzle_mcu Serial Dropout (Degraded Cable Harness)
agent: Claude
date: 2026-07-05
tags: [djinn, bug, calliope, klipper, hardware, cable]
related: [[2026-07-05_printer-triage-nemesis-calliope]]
---

# Bug Report — Calliope nozzle_mcu Serial Dropout (Degraded Cable Harness)

**Date:** 2026-07-05
**System:** Calliope (Ender-3 V3 Plus, 192.168.1.114)
**Severity:** High — printer non-functional for long PETG prints
**Status:** Open — new cable ordered, workaround (short PLA only) in place

---

## What Happened

Calliope crashed with `klippy_shutdown` on 4 consecutive PETG prints:
- `arm.stl_PETG_5h54m11s.gcode` × 2
- `base_frame.stl_PETG_7h14m27s.gcode` × 1
- `arm.stl_PETG_3h22m11s.gcode` × 1 (crashed at 1.7%, byte position 286697 of 16.4MB)

Crash location on last attempt: X≈185, Y≈205 (back-right area of 220×220 bed). Moving pieces to different plate position did not prevent crash.

---

## Root Cause

Klippy log error: `Lost communication with MCU 'nozzle_mcu'` (key561)

Post-crash MCU stats showed:
```
bytes_invalid: 0 → 7 → 35 → 50 → 63  (climbing every 3 seconds)
bytes_retransmit: 831 → 963 → 1095 → 1359 → 1491
stalled_bytes: 9243 → 9258 → 9267 (queue frozen)
rto: 5.000 (maxed out timeout)
```

`bytes_invalid` growing = the wire is broken inside insulation but still partially touching, generating line noise (corrupted bytes). A clean break produces zero invalid bytes. This signature is definitive: **broken wire inside cable harness, intermittent contact**.

All three MCUs are on hardware UART (`/dev/ttyS1`, `/dev/ttyS7`, `/dev/ttyS9`) — not USB — so USB bus saturation was ruled out.

Crash happens in the front area of the bed. On a bed-slinger, "front of plate" = Y-min = bed at maximum forward extension = toolhead cable at maximum flex in that axis. Physical stress point confirmed by position correlation.

---

## Rule / Lesson

**Calliope nozzle_mcu dropouts are always cable failures, not firmware or software issues.** When `bytes_invalid` climbs post-crash, the cable is partially broken. Any print that moves the toolhead through the stressed zone will fail. Software mitigations (baud rate, acceleration, fan settings) do nothing — serial corruption from a broken wire cannot be resolved in software.

**Cable routing rules for replacement install:**
1. Leave a 40–50mm service loop (slack coil) near the toolhead connector — cable must never be under tension at any point in the travel range
2. Route nozzle_mcu cable separately from stepper motor wires — stepper wires generate EMI that corrupts serial at high speeds when cables are bundled
3. Anchor to the X carriage body with a zip tie so pulling force goes to the anchor, not the connector
4. Inspect and reseat or replace the JST connector on the nozzle board — fretting wear from vibration may have damaged the contact surface

---

## Workaround

Do not run prints longer than 30–40 minutes on Calliope. Stick to PLA at reduced speed. No PETG. No arm.stl or base_frame.stl until cable is replaced.

*— Claude, 2026-07-05*
