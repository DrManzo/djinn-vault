---
title: Session Report — Virtual Ender-3 V3 Plus Printer Build
agent: Claude
date: 2026-06-08
tags: [djinn, report, printer, virtual, forge]
related: [[build-log]] | [[decision-log]] | [[bugs]]
---

# Session Report — Virtual Ender-3 V3 Plus Printer

**Date:** 2026-06-08
**Agent:** Claude
**Session type:** Build
**Trigger:** Need headless test environment for gcode slicing/debugging without risking real hardware

---

## Summary

Built a virtual Ender-3 V3 Plus printer using `mainsail-crew/virtual-klipper-printer` Docker container with custom CoreXZ printer.cfg matching real V3 Plus specs. Integrated into Typhon's Forge as `forge printer` subcommand with start/stop/status/logs/shell/update operations. The virtual printer is now operational at `http://localhost:7125` with correct CoreXZ kinematics, 300x300x330 build volume, full macro set, and Moonraker API.

---

## What Was Built or Changed

- Created `~/virtual-printer/printer_data/config/printer.cfg` — V3 Plus config for SimulAVR (CoreXZ, 600mm/s, 20000mm/s², 6×6 bed mesh, input shaper, pressure advance 0.04)
- Created `~/virtual-printer/virtual-printer.sh` — one-command launch script (start/stop/restart/status/logs/shell/update)
- Updated `~/virtual-printer/docker-compose.yml` — env-configurable port with `VIRTUAL_PRINTER_PORT`
- Created `~/virtual-printer/.env` — default port config
- Updated `~/.local/bin/forge` — added `printer` subcommand, updated status dashboard to show both real + virtual printers
- Pulled `ghcr.io/mainsail-crew/virtual-klipper-printer:latest` Docker image
- Launched and validated virtual printer: G28 homes correctly, moonraker API responsive

---

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **CoreXZ kinematics** over Cartesian | Real V3 Plus uses CoreXZ — virtual must match real for valid gcode testing |
| **Single AVR atmega644p MCU** over multi-MCU | SimulAVR only emulates one AVR; real printer has 3 MCUs (main, nozzle, leveling) but virtual only needs one |
| **PA0/PA1 for stepper_z1** | Avoided pin conflict with filament runout sensor (PC1) on the AVR pinout |
| **No temperature_fan (soc_fan)** | `temperature_mcu` not supported on atmega644p SimulAVR target |
| **No resonance_tester** | ADXL345 support not available in the Docker image's Klipper version (commit 2fb3d54) |
| **Extruder pressure_advance inline** | Set matching real V3 Plus calibrated value 0.04 directly in extruder section |
| **`forge printer` subcommand** over standalone script | Integrates into existing Typhon's Forge CLI pattern, visible in `forge status` dashboard |

---

## Files Created or Modified

```
~/virtual-printer/docker-compose.yml              ← env-configurable ports
~/virtual-printer/.env                            ← default port config
~/virtual-printer/virtual-printer.sh              ← launch/control script
~/virtual-printer/printer_data/config/printer.cfg ← V3 Plus CoreXZ config
~/.local/bin/forge                                ← added printer subcommand + dashboard
```

---

## Dependencies Installed

None new. Uses existing Docker (29.5.3) and the ghcr.io/mainsail-crew/virtual-klipper-printer image.

---

## Tests & Validation

| Test | Result |
|------|--------|
| `docker compose up -d` | Container started: `v3plus-virtual` |
| `curl /api/printer` | State: `Operational`, `ready: true` |
| `curl /printer/gcode/script -d '{"script":"G28"}'` | `{"result":"ok"}` |
| `curl /printer/objects/query?toolhead` | `homed_axes: "xyz"`, position `[0, -3, 0, 0]` |
| `forge printer status` | Shows RUNNING with full printer state |
| `forge status` | Dashboard shows both real + virtual printers |

---

## Known Issues / Caveats

- `max_accel_to_decel` removed — not supported by Klipper version (2fb3d54) in the Docker image
- Max toolhead velocity shown as 200 (not 600) — likely an older Klipper cap, needs investigation
- Real V3 Plus has 3 MCUs; virtual has 1 — Creality-specific modules (prtouch_v2, BL24C16F) cannot be virtualized
- Port 7125 on localhost — ensure no conflict with other Moonraker instances
- Vault has unstaged changes (`print_monitor_log.md`) from earlier session that need committing

---

## What's Next

- [ ] Investigate toolhead max_velocity cap (200 vs configured 600) — @Claude
- [ ] Test slicing a Camood gcode and feeding to virtual printer via Moonraker API — @Salomon
- [ ] Add `forge printer` to the help text in AGENTS.md or forge docs — @Assistant
- [ ] Consider adding to `forge services` list for systemd-based lifecycle — @Claude

---

*— Claude, 2026-06-08*
