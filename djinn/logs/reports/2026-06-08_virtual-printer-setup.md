---
title: Session Report — Virtual Ender-3 V3 Plus Setup
agent: Claude
date: 2026-06-08
tags: [djinn, report, printer, virtual, docker, klipper]
related: [[VIRTUAL-PRINTER]] | [[build-log]] | [[decision-log]]
---

# Session Report — Virtual Ender-3 V3 Plus Setup

**Date:** 2026-06-08
**Agent:** Claude
**Session type:** Build
**Trigger:** Javier requested a virtual copy of the Ender-3 V3 Plus for testing, usable globally across Djinn — not tied to any single agent or purpose.

---

## Summary

Built a fully operational virtual Ender-3 V3 Plus using the mainsail-crew/virtual-klipper-printer Docker image (real Klipper + Moonraker via SimulAVR). The virtual printer runs on Salomon at `localhost:7125`, exposes the full Moonraker API, accepts gcode, and responds to macro calls. It is wired into Typhon's Forge via `forge printer [start|stop|status|...]` and auto-starts on user login via systemd. Documentation is in `djinn/printer/VIRTUAL-PRINTER.md`.

---

## What Was Built or Changed

- **Virtual printer container** (`ghcr.io/mainsail-crew/virtual-klipper-printer:latest`) running as `v3plus-virtual` on Docker
- **`~/virtual-printer/printer_data/config/printer.cfg`** — Full Ender-3 V3 Plus config: CoreXZ kinematics, 300×300×330mm build volume, 6×6 bed mesh, pressure advance=0.04, input shaper (EI), PRINT_START/END/CANCEL macros, direct drive extruder matching real specs
- **`~/virtual-printer/docker-compose.yml`** — Compose file with port mapping (7125, 8110) and named container `v3plus-virtual`
- **`~/virtual-printer/virtual-printer.sh`** — Control script: start/stop/restart/status/logs/shell/update
- **`~/.local/bin/forge`** — Added `printer` subcommand and status dashboard entry for virtual printer
- **`~/.config/systemd/user/djinn-virtual-printer.service`** — Systemd user service for auto-start on login
- **`~/Obsidian/djinn/printer/VIRTUAL-PRINTER.md`** — Full usage doc: specs, API examples, test workflows, troubleshooting

---

## Technical Decisions

**SimulAVR velocity limits (200mm/s, 3000mm/s²) — Why:** The ATmega644p SimulAVR runs at 2MHz vs 20MHz on real hardware. Real V3 Plus settings (600mm/s, 20000mm/s²) cause "Timer too close" MCU shutdown within seconds. Sim values keep the virtual MCU stable. Motion timing is wrong; everything else (macro logic, API, gcode parsing, mesh, PA) is identical to the real printer.

**Single MCU config (no stepper_z1 conflict) — Why:** Original config duplicated PC1 between stepper_z1 and the filament runout sensor. Moved stepper_z1 to PA0/PA1 (unused pins on the sim MCU) and removed the runout sensor (not testable on SimulAVR anyway).

**Dropped `resonance_tester` / `adxl345` — Why:** SimulAVR doesn't expose an ADXL345 chip. The section caused a config error on startup. Input shaper values are hardcoded in the config instead; they can be tuned on the real printer and updated here.

**Dropped `temperature_fan soc_fan` — Why:** `temperature_mcu` sensor type is not supported on atmega644p in SimulAVR. Removed to prevent config error.

**Dropped `max_accel_to_decel` — Why:** Deprecated in modern Klipper; replaced by `minimum_cruise_ratio`. Removed.

**Port 7125 for virtual printer — Why:** Matches Calliope's Moonraker port. Any script or tool targeting `$MOONRAKER_HOST:7125` works against either printer by changing only the host.

---

## Files Created or Modified

```
~/virtual-printer/printer_data/config/printer.cfg    ← V3 Plus config (overwrite from generic SimulAVR default)
~/virtual-printer/docker-compose.yml                  ← Named container, .env-driven ports
~/virtual-printer/virtual-printer.sh                  ← Control script
~/virtual-printer/.env                                 ← Port config
~/.local/bin/forge                                     ← Added printer subcommand + status entry
~/.config/systemd/user/djinn-virtual-printer.service  ← Auto-start service
~/Obsidian/djinn/printer/VIRTUAL-PRINTER.md           ← Usage documentation
```

---

## Dependencies Installed

| Package | Method | Purpose |
|---------|--------|---------|
| ghcr.io/mainsail-crew/virtual-klipper-printer | docker pull | SimulAVR + Klipper + Moonraker base image |

Docker was already installed on Salomon (v29.5.3).

---

## Tests & Validation

- `forge printer status` → `Virtual Ender-3 V3 Plus: RUNNING` + Operational state ✓
- `curl http://localhost:7125/printer/info` → `state: ready` / `Printer is ready` ✓
- `curl .../printer/objects/query?toolhead` → X: -4–304, Y: -3–305, Z: -5–335, PA=0.04 ✓
- `POST /printer/gcode/script` with `M115` → `FIRMWARE_NAME:Klipper FIRMWARE_VERSION:2fb3d54` ✓
- Systemd service enabled: `default.target.wants/djinn-virtual-printer.service` symlink created ✓

---

## Known Issues / Caveats

- Both heaters report a constant `103.26°C` — SimulAVR artifact, not a real temperature. Macros that wait on `M190`/`M109` will either stall or need a workaround in sim context.
- Motion velocity is artificially throttled (200mm/s / 3000mm/s²) to keep SimulAVR stable. Real print timing will differ.
- Filament runout sensor not modeled — virtual printer will never trigger runout.
- The virtual printer is not accessible remotely by default — port 7125 is bound to `0.0.0.0` on Salomon, so other machines on the LAN can reach it at `192.168.1.225:7125`.

---

## What's Next

- [ ] Test uploading a real gcode file (e.g., KSR slice) and verify parse + execute — @Javier
- [ ] Add `djinn-virtual-printer` wrapper to PATH as a standalone tool if needed — @Salomon
- [ ] Consider `VIRTUAL_PRINTER_URL` env var in djinn-print scripts for routing API calls to virtual printer during dev — @Claude

---

*— Claude, 2026-06-08*
