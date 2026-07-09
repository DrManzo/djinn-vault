# Print Guardian — Research Brief for Claude & Salomon

**Purpose:** Technical depth brief for building and extending `djinn-print-guardian`.  
**Audience:** Claude (implementation), Salomon (COMMS integration)  
**Status:** v1 live — this doc covers the *why* and *next*.

---

## Background

Calliope (Ender 3 V3 Plus, Klipper/Moonraker) had two categories of failure
causing print abandonment despite the print being recoverable:

1. **BUG-014** — nozzle_mcu UART dropout at Z<10mm. **Hardware fix confirmed
   complete 2026-06-05** (connector reseated/replaced). Fan cap (S128) in
   `djinn-gcode-safety` removes the primary EMI trigger. Guardian handles any
   recurrence as a last-resort fallback.
2. **Setting drift** — FIRMWARE_RESTART wipes runtime velocity limits and
   pressure advance. Guardian injects these at every print start.

---

## Moonraker API: What the Guardian Uses

### State polling
```
GET /printer/objects/query?print_stats&toolhead&gcode_move&display_status
```
Returns:
- `print_stats.state` — standby / printing / paused / error / complete
- `toolhead.position[2]` — current Z in mm
- `gcode_move.speed_factor` — current speed multiplier (1.0 = 100%)
- `display_status.message` — current display message string

### GCode injection
```
POST /printer/gcode/script?script=<url-encoded-gcode>
```
Guardian uses this for:
- `SET_VELOCITY_LIMIT` — motion defaults
- `SET_PRESSURE_ADVANCE` — PA restore
- `M220 S100` — speed lock restore
- `FIRMWARE_RESTART` — recovery trigger
- `RESUME` — restart from PLR state
- `PAUSE` — hard stop when recovery exhausted

### Log access
```
GET /server/files/klippy.log?tail=80
```
Guardian scans for BUG-014 signatures:
- `"key561"` — Creality-specific UART error code
- `"nozzle_mcu"` — Klipper MCU identifier for hotend board
- `"Lost communication with MCU"` — generic Klipper MCU dropout

---

## Recovery Decision Tree

```
Printer → ERROR state
  ├── Scan klippy.log for dropout signature
  │     ├── Found AND in BUG-014 zone (Z<12mm) AND auto-resume ON AND attempts<3
  │     │     → FIRMWARE_RESTART → wait reconnect → inject defaults → RESUME
  │     ├── Found but NOT in danger zone or auto-resume OFF
  │     │     → Log only, no action
  │     └── Not found
  │           → Log only, no action
  └── attempts >= 3
        → PAUSE + log "check nozzle_mcu connector"
```

The 3-attempt cap is intentional. Three failed firmware restarts = hardware issue,
not software. Human required.

---

## Layer Relationship: Guardian vs gcode-safety

| Layer | Tool | What it does |
|---|---|---|
| Pre-flight | `djinn-gcode-safety` | Caps M106 at S128 before file hits Calliope |
| Runtime | `djinn-print-guardian` | Watches live state, injects fixes during print |

No overlap. Complementary layers.

---

## What Guardian Does NOT Handle (Future Scope)

| Failure | Reason Not In v1 | Proposed v2 |
|---|---|---|
| Thermal runaway | Cannot be safely auto-recovered | Log + notify only |
| Layer adhesion failure | No camera integration yet | Hook into djinn-vision |
| Clog (extruder skipping) | No extruder current/position sensor logic | Monitor e-steps vs expected |
| Network dropout | Already handled — retries silently | ✓ done |

---

## COMMS Integration (Salomon)

Guardian should write a COMMS entry on every recovery attempt and hard PAUSE.
Format:
```
CATEGORY: PRINT_GUARDIAN
EVENT: BUG014_RECOVERY_ATTEMPT_1
PRINT: <filename>
Z: <z_pos>mm
TIMESTAMP: <iso8601+tz>
RESULT: success | failed
NOTE: <log excerpt>
```

Wire into existing COMMS writer once guardian is deployed to Calliope's host.

---

## Deployment

```bash
chmod +x djinn/printer/tools/djinn-print-guardian

# Monitor only (no auto-resume)
djinn-print-guardian --host 192.168.1.X --interval 15

# Production (auto-recover, log to file)
djinn-print-guardian --host 192.168.1.X --auto-resume --log ~/djinn-guardian.log
```

### Systemd Unit
```ini
[Unit]
Description=djinn-print-guardian
After=moonraker.service
Requires=moonraker.service

[Service]
Type=simple
User=pi
ExecStart=/home/pi/djinn/printer/tools/djinn-print-guardian \
  --host 127.0.0.1 \
  --auto-resume \
  --log /home/pi/djinn-guardian.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Calliope-Specific Values

| Parameter | Value | Source |
|---|---|---|
| `ACCEL` | 2000 mm/s² | Proven profile — Camood, all shop pieces |
| `ACCEL_TO_DECEL` | 500 mm/s² | 25% of ACCEL per Klipper recommendation |
| `SQUARE_CORNER_VELOCITY` | 5 mm/s | Default, validated |
| `PRESSURE_ADVANCE` | 0.042 | Calibrated for Calliope + PETG |
| `BUG014_Z_THRESHOLD` | 12mm | All 11 dropouts at Z<10mm, +2mm margin |
| Max recovery attempts | 3 | Conservative — hardware fix confirmed |

---

*Research brief — djinn-vault 2026-06-05*
