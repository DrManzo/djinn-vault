---
title: Printer Clean-Queue Snapshot
date: 2026-06-05
agent: Claude
tags: [djinn, printer, snapshot, calliope]
---

# Printer State Snapshot — Clean Queue
**Date:** 2026-06-05  
**Printer:** Calliope (Ender-3 V3 Plus) @ 192.168.1.113:7125

This snapshot captures the clean-queue state. Run `djinn-queue-reset` to restore this state at any time.

---

## Queue State
- Moonraker job queue: **empty**
- Queue mode: **idle (paused with no jobs)** — correct state, jobs require explicit approval to start
- Print history: **cleared**
- Active traces: **none** (archived to `djinn/printer/traces-archive/`)

---

## Active Fixes & Modifications (preserved — do not touch)

### Slicer Profiles
| File | Change |
|------|--------|
| `~/.config/forge/ender3-v3-plus.ini` (symlinked to `~/.config/djinn/`) | `max_fan_speed=50`, `bridge_fan_speed=50` — EMI fix |
| `~/.config/forge/ender3-v3-plus.ini` | `post_process = djinn-gcode-safety` — auto safety injection |
| `~/.config/forge/ender3-v3-plus.ini` | `label_objects = 1` — per-object cancel support |
| `~/.config/OrcaSlicer/user/default/filament/Calliope PLA @Ender-3V3-all.json` | Fan capped 50%, 210°C/60°C nozzle/bed |

### Safety Scripts
| Script | Purpose |
|--------|---------|
| `~/.local/bin/djinn-gcode-safety` | Post-processor: injects M220 S53 + M204 S800 at Z≥90mm (Marcus 80mm/s cap), PAUSE_PRINT at Z≥104mm |
| `~/.local/bin/djinn-print-safety` | Runtime daemon: polls MCU stats, computes failure probability, alerts Telegram, auto-pause + 3min hold + speed ramp on resume |
| `~/.config/systemd/user/djinn-print-safety.service` | Systemd unit for the daemon |

### Library
| Path | Contents |
|------|---------|
| `~/printer-files/library/engraved/terp-tribe/` | Camood_TTHQ_engraved.stl, ProxyStand_TTHQ_cursive_centered.stl |
| `~/printer-files/library/cored/external/apple/` | Apple_bored.stl (38mm Proxy core, uniform scale) |
| `~/printer-files/library/engraved/terp-tribe/Camood_print_config.json` | Print config for Camood |

### Known Issues (hardware — not fixed by software)
- Calliope nozzle_mcu cable has a physical stress point at ~Z=106mm toolhead height
- Manifests as instant retransmit spike (bytes_invalid=0) — physical disconnect
- Mitigation: djinn-gcode-safety pauses at Z=104mm for inspection
- Permanent fix required: inspect/rereoute cable or replace connector

---

## How to Restore This State

Run: `djinn-queue-reset`

Or manually:
```bash
# Clear Moonraker history
curl -X DELETE "http://192.168.1.113:7125/server/history/job?all=true"

# Verify queue empty
curl -s "http://192.168.1.113:7125/server/job_queue/status"

# Archive any stale traces
mv ~/Obsidian/djinn/printer/active/TRACE-*.md ~/Obsidian/djinn/printer/traces-archive/ 2>/dev/null
```

*— Claude, 2026-06-05*
