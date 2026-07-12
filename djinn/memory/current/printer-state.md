---
title: Printer State — Canonical
authority: Typhon
write_gate: djinn-typhon-write
updated: 2026-06-05
status: DEPRECATED — see note below (2026-07-12)
---

# Printer State

> **⚠️ STALE, NOT CANONICAL (flagged 2026-07-12).** Typhon has had zero write
> access to the vault since its Windows reinstall (2026-06-25) — nobody has
> been able to update this file since. It's also actively wrong: BUG-014
> below says "RESOLVED (hardware fix, connector reseated)" — that was an
> earlier, ineffective attempt; the real fix was a full cable replacement on
> 2026-07-09 (see `djinn/logs/bugs.md`). Do not trust anything below as
> current fact. For real current printer state, check the fleet dashboard
> (`http://192.168.1.80:8420`) or `forge/hardware/fleet-capability-matrix.md`.
> Left in place rather than deleted since it's a real historical snapshot of
> 2026-06-05 state — just don't read it as "now."

This is the canonical current state of Calliope (Ender-3 V3 Plus).
Typhon is the sole writer. Do not modify this file directly.
Submit updates via `djinn/memory/requests/`.

## Machine State

```
Status:          idle
Last job:        (none logged yet)
Queue depth:     0
Bed temp:        ambient
Hotend temp:     ambient
Firmware:        Klipper (Creality V3 Plus profile)
```

## Slicer State

```
Active slicer:   OrcaSlicer
Active profile:  Production 0.20mm @Creality Ender-3 V3 Plus
Fan cap:         S128 (50%) — enforced by djinn-gcode-safety
Speed reduction: M220 S53 at Z≥90mm — enforced by djinn-gcode-safety
Pause injection: PAUSE at Z≥104mm — enforced by djinn-gcode-safety
Legacy slicer:   PrusaSlicer CLI (diagnostic/pipeline only — no direct prints)
```

## Active Bugs

```
BUG-013:  M106 S255 → EMI spike — MITIGATED (gcode-safety S128 cap)
BUG-014:  nozzle_mcu connector dropout — RESOLVED (hardware fix, connector reseated)
```

## Deferred Work

```
djinn-print-guardian:  deferred — revisit Dec 2026 or on recurrence of dropouts
```

---
*Last written by Typhon. Do not edit manually.*
