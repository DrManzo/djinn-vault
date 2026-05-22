# Printer Profile — Ender-3 V3 Plus

## Hardware

| Item | Value |
|------|-------|
| Build volume | 300 × 300 × 330mm |
| Bed | PEI flex plate (textured, magnetic) |
| Probe | CR Touch (auto bed leveling) |
| Extruder | Direct drive (Sprite) |
| Nozzle | 0.4mm hardened steel |
| Connectivity | WiFi — Creality Nebula pad (bypasses Creality Cloud) |
| Print server | Klipper + Moonraker on Nebula pad |
| API endpoint | `http://192.168.1.114:7125` |

## Default Print Settings — PLA

| Parameter | Value |
|-----------|-------|
| Nozzle temp | 220°C |
| Bed temp | 55°C |
| Layer height | 0.2mm |
| First layer height | 0.3mm |
| Infill | 15% (functional parts: 40%+) |
| Print speed | 150 mm/s |
| First layer speed | 30 mm/s |
| Supports | Auto |
| Retraction | 0.5mm @ 35 mm/s |
| Fan | Off first layer, 100% from layer 2 |

## Measured Performance Baseline

From Rose_Decor_fixed.gcode run (2026-05-22):

| Metric | Value |
|--------|-------|
| Hotend stability | ±0.32°C from target |
| Bed stability | ±0.01°C from target |
| Hotend range | 219.6–220.5°C |
| Anomalies | None detected post cable-reseat |

## Safety Systems

- **idle_timeout**: 600s — cuts heaters + motors after 10 min idle (cat safety)
- **PLR**: Active via `plr.cfg` — saves Z/layer at each layer change, pauses on temp drop
- **Thermal watchdog**: Polls every 5s — pauses print if hotend drops >15°C below target
- **verify_heater extruder**: `check_gain_time:30, max_error:120` (restored to stock after cable fix)

## Hardware Notes

- **nozzle_mcu**: GD32F303CBT6 on `/dev/ttyS1` @ 230400 baud — cable reseated 2026-05-22, retransmit_seq dropped from 4289 → 2
- **Printer IP**: DHCP at 192.168.1.114 — recommend static lease via router to prevent future address changes
- **Cat safety**: Printer must be enclosed or placed out of reach — bed reaches 55-60°C, hotend 220°C+

## Software Stack (Salomon)

| Tool | Role |
|------|------|
| OrcaSlicer | STL → G-code slicing, Moonraker upload |
| FreeCAD | Parametric modeling (functional parts) |
| Blender | Organic modeling, mesh repair |
| OpenSCAD | Scripted/Djinn-generated parts |
| Hunyuan3D-2 | Text → 3D mesh (AI generation, pending install) |

## Workflow

```
Prompt → Hunyuan3D-2 (or FreeCAD/OpenSCAD)
  → STL in djinn/printer/queue/
  → OrcaSlicer headless slice
  → Moonraker upload + print start
  → printer-error-logger monitors
  → Job logged to djinn/printer/completed/
```

## Telegram Commands (Typhon bot)

| Command | Action |
|---------|--------|
| `/print <filename>` | Start named file from Moonraker gcodes |
| `/print_status` | Current state, progress, temps |
| `/print_cancel` | Cancel active print |
| `/print_queue` | List files available on printer |
| `/print_log` | Last 5 completed/failed jobs |
