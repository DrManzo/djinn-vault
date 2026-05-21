---
subject: Printer Config
tags: [djinn, printer, config]
created: 2026-05-21
---

# Printer Configuration

## Hardware

| Item | Value |
|------|-------|
| Model | Ender-3 V3 Plus |
| Firmware | Creality Nebula (Klipper-based) |
| Connection | Local WiFi only — Creality Cloud bypassed |
| Moonraker port | 7125 |
| Printer IP | 192.168.1.113 ✅ |
| Moonraker API | http://192.168.1.113:7125 ✅ Live |
| Location | TBD — needs enclosure (cat safety) |

## Network

```bash
PRINTER_IP=192.168.1.113
# Set in ~/.config/djinn/printer.conf on both Salomon and Typhon
```

## Profiles

| Profile | Material | Nozzle | Bed Temp | Hotend Temp |
|---------|----------|--------|----------|-------------|
| default | PLA | 0.4mm | 60°C | 215°C |
| draft | PLA | 0.4mm | 55°C | 210°C |
| quality | PLA | 0.4mm | 60°C | 215°C |

## Safety Notes

- Bed reaches 60–100°C — cat enclosure required before first print
- Hotend reaches 200°C+ — keep cats away during operation
- Never leave unattended for first 3 prints
- WiFi only — no USB cable needed, printer can be placed safely away from Typhon
