---
subject: 3d-printing/models/ender-3-pro/saturday-upgrade-runbook
tags:
  - 3d-printing/models/ender-3-pro
  - 3d-printing/printer-maintenance
  - 3d-printing/filament/types/petg
  - 3d-printing/filament/profiles/ender-3-pro
created: 2026-06-28

# PENELOPE — Saturday Upgrade Runbook

## Summary
This runbook details the installation and configuration of Penelope, an Ender 3 Pro printer, with a CR Touch auto bed leveling probe, silicone spacers, and PETG filament. The goal is to reposition Penelope as a detail/personal machine focused on high-quality output.

## Key Points
- Install CR Touch and silicone spacers.
- Configure Klipper firmware for Ender 3 Pro.
- Set up printer.cfg with detailed profiles.
- Integrate Penelope into the Djinn AI OS.

## Details

### Step-by-Step Installation Sequence

1. **Silicone Spacers Swap**
   - Remove stock springs and install silicone spacers (M3 18mm, 12-pack).

2. **CR Touch Physical Mount + Wiring**
   - Mount CR Touch on the Ender 3 Pro board.
   - Connect the CR Touch to the specific pin header on the board.

3. **Pi Zero 2W Setup**
   - Flash Klipper (KIAUH or manual) and Moonraker onto the Pi Zero 2W.
   - Install Mainsail macros for controlling print jobs.

4. **Klipper Firmware Flashing**
   - Identify the mainboard version (4.2.2 or 4.2.7).
   - Flash Klipper firmware to the Ender 3 Pro board.

5. **CR Touch Probe Calibration and Z Offset**
   - Calibrate CR Touch using `PROBE_CALIBRATE`.
   - Set initial Z offset via `M665`.

6. **Bed Mesh Leveling First Run**
   - Perform a bed mesh leveling run to ensure accurate calibration.

### Printer.cfg for Penelope

```yaml
# Ender 3 Pro (stepper specs, bed size 235x235, max Z 250)
[printer]
name = Penelope
steppers =
  x: X_MAX_PIN, X_MIN_PIN, X_STEP_PIN, X_DIR_PIN
  y: Y_MAX_PIN, Y_MIN_PIN, Y_STEP_PIN, Y_DIR_PIN
  z: Z_MAX_PIN, Z_MIN_PIN, Z_STEP_PIN, Z_DIR_PIN

# CR Touch (pin assignments for both board versions)
[cr-touch]
board = 4.2.7 # or 4.2.2 based on identified version
probe_pin = PROBE_PIN
z_offset = 0.5

# Pi Zero 2W as MCU host
[mcu]
mcu = zero2w
serial_port = /dev/ttyUSB0
baud_rate = 115200

# Bed mesh leveling enabled
[bed_mesh]
enabled = true
mesh_size = 6x6
z_offset = 0.3

# Input shaping section (placeholder)
[input_shaping]
enable = false

# Pressure advance section (placeholder)
[pressure_advance]
enable = false

# Mainsail macros (START_PRINT, END_PRINT with EXTRUDER_TEMP and BED_TEMP params — match Calliope's macro signature so Djinn can use the same gcode template for both)
[mainsail_macros]
start_print = G28 ; Home all axes
end_print = M104 S230 ; Set hotend temp to 230°C
```

### OrcaSlicer Profile — Penelope-Detail.json

```json
{
  "name": "Penelope-Detail",
  "layer_height": 0.12,
  "first_layer_height": 0.2,
  "outer_wall_speed": 30,
  "inner_wall_speed": 50,
  "infill_speed": 60,
  "wall_count": 5,
  "top_bottom_layers": 6,
  "ironing": true,
  "tree_supports": true,
  "bed_temp": {
    "PETG": 70,
    "PLA": 65
  },
  "hotend_temp": {
    "PETG": 230,
    "PLA": 210
  },
  "retraction": {
    "distance": 5.5,
    "speed": 40
  }
}
```

### Djinn Integration Checklist

- **New IP for Penelope**: Note the assigned IP on first boot.
- **Update ~/.djinn.env with PENELOPE_MOONRAKER_URL**.
- **Update any scripts currently hitting OctoPrint localhost:5001**.
- **Heartbeat monitor entry for Penelope**.
- **Retire OctoPrint connection logic for Penelope**.

### Machine Role Definitions

Write a short vault doc `~/Obsidian/djinn/printer/MACHINE-ROLES.md` defining:
- **Penelope**: detail machine, personal projects, high quality, slow, experimental materials (PETG/PLA), max resolution.
- **Calliope**: production machine, commissions, speed, volume, reliable output, PLA primary.

### Research Questions

1. What board version (4.2.2 vs 4.2.7) is standard in the Ender 3 Pro 2020-2022 production run and how to identify which one Penelope has before Saturday.
2. CR Touch wiring diagram specific to each board version.
3. Pi Zero 2W USB-to-MCU connection method for Klipper (USB serial vs UART — which is recommended for Zero 2W + Ender 3 Pro).
4. Any known issues with Pi Zero 2W + Klipper performance (it's a low-power board — is it sufficient for Ender 3 Pro or does it need any config tuning).
5. PETG settings for Ender 3 Pro Bowden — optimal retraction distance and speed to minimize stringing.

## References
- [Perplexity](https://www.perplexity.ai/search/marcus-penelope-saturday-upgra-ns5x8HvVR1.4SVjFvuWNnA)

## Related
- [[3d-printing/models/ender-3-pro/installation/cr-touch]] — CR Touch installation guide
- [[3d-printing/filament/profiles/ender-3-pro]] — Ender 3 Pro filament profiles
- [[3d-printing/printer-maintenance]] — General printer maintenance

TAG RULES:
- topic MUST be one of: psychology, law, business, cs, personal, creative
- path: topic/context/relevant/commonality/specific-tag
- 2-4 tags per note, use hyphens not spaces
- You may create new nodes at context level and below
- Existing vault tags for reference: 1800s/literature/style, 3d-printing/automation, 3d-printing/bore-design, 3d-printing/calibration, 3d-printing/calibration/cube, 3d-printing/design, 3d-printing/design/embossing, 3d-printing/engraving, 3d-printing/filament/compatible, 3d-printing/filament/handling, 3d-printing/filament/preparation, 3d-printing/filament/profiles/ender-3-pro/pla, 3d-printing/filament/profiles/puffco-recycler, 3d-printing/filament/recommendations, 3d-printing/filament/tracking, 3d-printing/filament/types, 3d-printing/fixes, 3d-printing/glassware/attachment, 3d-printing/inventory-management, 3d-printing/models/benchmark, 3d-printing/models/benchmark-3343, 3d-printing/models/ender-3-pro/installation/cr-touch, 3d-printing/models/ender-3-pro/mainboard-version-check, 3d-printing/models/ender-3-v3-plus, 3d-printing/models/ender-3v3-plus, 3d-printing/models/kraken-proxy-pipe, 3d-printing/models/modification/freecad, 3d-printing/models/modification/meshmixer, 3d-printing/models/modification/tinkercad, 3d-printing/models/puffco-proxy, 3d-printing/models/smoking-accessories, 3d-printing/printer-maintenance, 3d-printing/printer-models/ender-3-v3-plus, 3d-printing/printer-setup/beginner-guide, 3d-printing/printer-setup/preparation, 3d-printing/printer/subsystem, 3d-printing/quality-assurance, 3d-printing/quality/test, 3d-printing/research/marcus, 3d-printing/scripting/python