---
title: Virtual Ender-3 V3 Plus
tags: [djinn, printer, virtual, docker, klipper, testing]
created: 2026-06-08
updated: 2026-06-08
---

# Virtual Ender-3 V3 Plus

A software-accurate simulation of Calliope running inside Docker via SimulAVR + real Klipper + Moonraker. Use it to test gcode, macros, slicer profiles, and API scripts without touching the real printer.

## What It Is

- **Base image:** `ghcr.io/mainsail-crew/virtual-klipper-printer:latest` (mainsail-crew)
- **MCU:** SimulAVR emulating ATmega644p (real Klipper firmware, not a stub)
- **API:** Full Moonraker REST + WebSocket on port 7125 — same interface as Calliope
- **Location:** `~/virtual-printer/` on Salomon

## Accurate Specs

| Setting | Value |
|---------|-------|
| Kinematics | CoreXZ |
| Build volume | 300 × 300 × 330 mm |
| Bed mesh | 6×6 (bicubic) |
| Pressure advance | 0.04 |
| Input shaper | EI type, X=78Hz Y=58Hz |
| Extruder | Direct drive, rotation_distance=6.9 |
| Filament sensor | Not modeled (SimulAVR limitation) |
| Temps | Simulated constants (not real PID) |
| Velocity (sim) | 200 mm/s max (physical: 600) — SimulAVR limitation |
| Acceleration (sim) | 3000 mm/s² (physical: 20000) — SimulAVR limitation |

> **Note on velocity/accel:** The real V3 Plus does 600mm/s and 20000mm/s². SimulAVR runs at 2MHz instead of 20MHz, so timing blows up at real speeds. The sim values are set for stability. Macro logic, gcode parsing, API behavior, and mesh/PA all work identically — only motion timing differs.

## Access

- **Moonraker API:** `http://localhost:7125` (or `http://192.168.1.225:7125` from other machines)
- **Mainsail web UI:** Open `https://my.mainsail.xyz` → Add Printer → `192.168.1.225:7125`
- **Fake webcam:** `http://localhost:8110`

## Forge CLI Commands

```bash
forge printer start       # start container
forge printer stop        # stop container
forge printer status      # check state + temps
forge printer logs        # tail Klipper/Moonraker logs
forge printer shell       # bash into container
forge printer restart     # stop + start
forge printer update      # pull latest image, restart
```

## Systemd Auto-Start

The service starts automatically on user login:

```bash
systemctl --user status djinn-virtual-printer   # check
systemctl --user start djinn-virtual-printer    # manual start
systemctl --user stop djinn-virtual-printer     # manual stop
```

## Testing Workflows

### Upload and run a gcode file

```bash
# Upload via Moonraker API
curl -X POST "http://localhost:7125/server/files/upload" \
  -F "file=@/path/to/test.gcode" \
  -F "root=gcodes"

# Start print
curl -X POST "http://localhost:7125/printer/print/start" \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.gcode"}'
```

### Test a macro

```bash
curl -X POST "http://localhost:7125/printer/gcode/script" \
  -H "Content-Type: application/json" \
  -d '{"script": "PRINT_START BED_TEMP=60 EXTRUDER_TEMP=210"}'
```

### Query printer state

```bash
curl -sf "http://localhost:7125/printer/objects/query?heater_bed&extruder&toolhead&print_stats" | python3 -m json.tool
```

### Check gcode console

```bash
curl -sf "http://localhost:7125/server/gcode_store?count=20" | python3 -m json.tool
```

## What You Can Test

- Macro logic (PRINT_START, PRINT_END, CANCEL_PRINT)
- Gcode file parsing and execution
- Moonraker API calls (same as used by djinn-print scripts)
- Bed mesh configuration changes
- Pressure advance values
- Slicer output — does the gcode parse cleanly?
- API scripts before deploying against Calliope

## What You Cannot Test

- Real temperatures (both heaters report 103.26°C constant — SimulAVR artifact)
- Actual motion at print speed (sim runs 3-10× slower)
- Hardware faults (nozzle_mcu disconnect, etc.)
- Filament runout
- Z-offset calibration (no real probe)

## Config Files

- `~/virtual-printer/printer_data/config/printer.cfg` — main config
- `~/virtual-printer/printer_data/config/moonraker.conf` — Moonraker config
- `~/virtual-printer/.env` — port config
- `~/virtual-printer/docker-compose.yml` — compose definition

## Troubleshooting

**"Timer too close" shutdown:** Velocity/accel too high for SimulAVR. Keep `max_velocity ≤ 200` and `max_accel ≤ 3000` in the virtual config.

**Klippy in Error state after restart:** Check logs with `forge printer logs`. Most common cause is a config syntax error. The container maps `~/virtual-printer/printer_data/` directly, so edit files on the host and restart.

**Port conflict:** If something else uses 7125, set `VIRTUAL_PRINTER_PORT=7126` in `~/virtual-printer/.env` before starting.

---

*— Claude, 2026-06-08*
