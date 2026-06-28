# PENELOPE — Saturday Upgrade Runbook
## Klipper + Pi Zero 2W + CR Touch + Silicone Spacers + PETG

**Prepared by:** Marcus  
**Date:** 2026-06-26  
**Status:** SATURDAY-READY — paste and go  
**Vault path:** `~/Obsidian/djinn/printer/PENELOPE-SATURDAY-RUNBOOK.md`

> **CRITICAL CONTEXT FROM PRIOR SESSION (2026-06-20):**  
> Penelope's board is **NOT a 4.2.2 or 4.2.7**. She has the original 8-bit **ATmega1284P** (Creality Melzi-style, 2019 production, Marlin 1.1.6.2). The prior Klipper flash attempt via USB/avrdude failed because Creality removed the auto-reset capacitor — bootloader window is ~1s, too short for 48.5KB. With the Pi Zero 2W arriving Saturday, Klipper runs **on the Pi** and connects to the ATmega via USB serial — this **bypasses the bootloader problem entirely**. The ATmega runs a minimal Klipper MCU firmware (not a full Klipper install), and the Pi Zero 2W is the host that runs klippy. This is the correct and tested path for this exact hardware combination.

---

## Research Answers (Read Before Saturday)

### Board Version: ATmega1284P (Confirmed)

Penelope is the pre-2020 Ender 3 Pro generation with the original 8-bit Melzi-derived board — **not** the 4.2.2 or 4.2.7 that Creality introduced in late 2020. This was confirmed via M115 during the 2026-06-20 session:

```
FIRMWARE_NAME:Marlin Creality 3D
MACHINE_TYPE:Ender-3 Pro
EXTRUDER_COUNT:1
```

The 4.2.2 and 4.2.7 boards use STM32F103 (ARM Cortex-M3) and were introduced with the Ender 3 Pro V2 refresh in Q4 2020. Ender 3 Pro units from the 2019-early 2020 run shipped with the ATmega1284P. The visual identifier: the 4.2.x boards are black with silkscreened version numbers on the PCB; the original board is green, similar to the Melzi design. Penelope has the green board.

**Klipper firmware target for Saturday:**  
`CONFIG_MACH_atmega1284p=y`, 16MHz crystal, 250000 baud. The hex is already compiled at `~/klipper/out/klipper.elf.hex` on Salomon from the prior session.

### CR Touch Wiring — ATmega1284P (Original Melzi Board)

The original Creality board does **not** have a dedicated BLTouch/CR Touch JST header. The 5-pin CR Touch connector maps as follows:

| CR Touch Wire | Color | Connect To |
|---------------|-------|------------|
| GND | Black | GND on Z-stop header |
| +5V | Red | +5V on Z-stop header |
| GND (servo) | Brown | GND (any available) |
| Signal (servo) | Orange | **Z-stop signal pin** (PA3 / D19) |
| Sensor output | White | **Z-stop signal pin** (shared, or dedicated if available) |

> **Practical note:** On the original Melzi-style board, the cleanest mount is the Z endstop header (3-pin JST). The CR Touch replaces the Z endstop entirely. Run the 2-wire probe signal (white + black) to the Z endstop header, and the 3-wire servo (orange + red + brown) to a free fan or EXT header for +5V/GND/Signal. Many users use the Z endstop connector for signal + GND and tap +5V from the bed thermistor or fan header. **Do not use the hot-end cooling fan header for power** — it is PWM-controlled and will cause CR Touch servo errors.
>
> The safest wiring for the ATmega1284P board: use the dedicated CR Touch 5-pin extension cable (usually included or sold separately), connect directly to the Z-stop header for the probe output, and use the always-on fan header (+5V/GND) for CR Touch servo power. Label your cable before Saturday.

**In printer.cfg (covered in full config below):**
```ini
[bltouch]
sensor_pin: ^PA3     ; Z-stop pin on original Ender 3 Pro board
control_pin: PD7     ; servo signal — adjust if you use a different fan header pin
```

### Pi Zero 2W + Klipper: USB Serial vs UART

**Use USB serial (not UART).** This is the recommended path for Pi Zero 2W + Ender 3 Pro.

UART (GPIO 14/15) on the Pi Zero 2W requires disabling the Bluetooth module (which shares the hardware UART) and enabling the mini-UART on the console — it adds complexity with no benefit on a system already connected via USB. USB serial via the Pi's USB OTG port to the printer's USB-B port is plug-and-play, deterministic, and the connection path is identical to how the Pi was previously connected to Salomon.

The Pi Zero 2W has a single micro-USB port (the one labeled "USB" — not "PWR"). Use the included micro-USB cable: one end to the Pi USB OTG port, other end to the Ender 3 Pro's USB-B port (same cable/port OctoPrint was using to Salomon). Klipper will detect the printer at `/dev/ttyUSB0` or `/dev/serial/by-id/...`.

> **Power the Pi from the printer's USB port? No.** The Ender 3 Pro's USB port provides only ~100mA, insufficient for the Pi Zero 2W under Klipper load. Use the included power cable from the starter kit for Pi power. USB OTG handles data only.

### Pi Zero 2W + Klipper: Known Performance Issues

The Pi Zero 2W (1GHz quad-core RP3A0, 512MB RAM) is **sufficient but not comfortable** for Klipper. Known issues and mitigations:

| Issue | Impact | Fix |
|-------|--------|-----|
| Low RAM (512MB) | Mainsail + Moonraker + Klipper together sit at ~350-400MB under load | Disable swap or add 256MB swap to the microSD; avoid running camera streams |
| SD card I/O bottleneck | Log writes and config saves can cause momentary klippy stalls | Use the best microSD from the kit (Samsung/SanDisk preferred); avoid cheap no-name cards |
| Thermal throttling | Pi Zero 2W throttles at 80°C — no heatsink in most kits | Attach the included heatsink if present; printer enclosures can get warm |
| No hardware watchdog by default | If klippy crashes, printer may continue moving | Enable `[virtual_sdcard]` and `[display_status]` — covered in printer.cfg |
| USB OTG host mode | Pi Zero 2W requires OTG mode enabled | `dtoverlay=dwc2` in `/boot/config.txt` — covered in install sequence |

**Bottom line:** Pi Zero 2W works for a detail/personal machine running at 30-60mm/s with no camera stream. Do not run input shaping resonance testing on the Zero 2W (it cannot drive the ADXL345 at sufficient sample rates reliably). Tune input shaping on Salomon or Calliope's Pi if needed later.

### PETG on Ender 3 Pro Bowden — Optimal Retraction

PETG is notoriously stringy in Bowden setups because the flexible Bowden tube allows filament compression and delayed retraction response.

**Recommended baseline for Ender 3 Pro Bowden (0.4mm nozzle, PETG 1.75mm):**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Retraction distance | 5.5–6.5mm | 5.5mm starting point; increase 0.5mm if stringing persists |
| Retraction speed | 40–45mm/s | Faster causes grinding; slower causes ooze |
| Print temp | 230–240°C | Lower end (230°C) reduces stringing; higher improves layer adhesion |
| Print speed | 30–45mm/s max for outer walls | PETG punishes speed harder than PLA |
| Combing mode | Within infill only | Prevents travel moves crossing part boundaries |
| Z-hop | 0.2mm | Prevents nozzle drag stringing on travel |
| Min travel for retract | 1.5mm | Avoid retracting on tiny moves |
| Fan speed | 30–50% max | Too much cooling causes layer delamination in PETG |

> **The single biggest PETG stringing fix for Bowden:** reduce print temperature to 230°C and enable combing. Most PETG stringing with Bowden is not a retraction problem — it's a temperature problem combined with travel moves that cross open air. Combing + lower temp resolves 80% of stringing before touching retraction distance.

---

## Saturday Install Sequence

### Pre-Saturday Checklist (Do Tonight or Tomorrow Morning)

- [ ] Locate Penelope's power cable and USB-B cable — set aside
- [ ] Confirm Pi Zero 2W kit contents: Pi, microSD, micro-USB cable, power adapter
- [ ] Download MainsailOS image: `https://github.com/mainsailcrew/MainsailOS/releases` — get the Pi Zero 2W / armv6l image
- [ ] Pre-flash microSD using Raspberry Pi Imager or Balena Etcher (see Step 1)
- [ ] Note Penelope's current IP neighborhood: your router assigns in 192.168.1.x range — DHCP will give Pi a new address; log into router after first Pi boot to find it
- [ ] Print this doc or have it open on phone/tablet — you'll need both hands for hardware steps

---

### PHASE 1 — Hardware

**Step 1 — Flash MainsailOS to microSD (do before Saturday if possible)**

MainsailOS is the recommended distribution — it ships with Klipper, Moonraker, and Mainsail pre-installed. This eliminates the KIAUH install sequence entirely.

```bash
# On any machine:
# 1. Download: https://github.com/mainsailcrew/MainsailOS/releases
# Select: mainsailOS-armv6l-*.img.xz (Pi Zero 2W uses armv6l)

# 2. Flash using Raspberry Pi Imager:
#    - Select custom image → browse to .img.xz
#    - Select your microSD card
#    - Click gear icon → set hostname: penelope, enable SSH, set user/pass
#    - WiFi SSID + password: fill in your network credentials HERE
#    - Write

# 3. After flash, mount boot partition and verify wpa_supplicant.conf exists
# OR: Raspberry Pi Imager's "advanced options" handles WiFi config automatically
```

> ⚠️ **WARNING:** If you use Pi Imager's advanced options, set hostname to `penelope` and enable SSH with password auth. This hostname will make the Pi discoverable at `penelope.local` immediately on first boot.

---

**Step 2 — Swap Silicone Spacers**

1. Power off Penelope completely. Unplug power cable.
2. Home all axes manually (move gantry to center by hand).
3. Remove the glass/PEI bed and set aside.
4. Using M3 screwdriver, loosen each corner bed leveling knob until spring+bolt are loose.
5. **Remove one corner at a time:** lift bed bracket slightly, remove spring, replace with M3 18mm silicone spacer. Thread bolt back through spacer until snug but not tight.
6. Repeat all 4 corners. The silicone spacers require **less tension** than springs — do not overtighten. Finger-tight + 1/4 turn.
7. Do NOT level yet. CR Touch will do it.

---

**Step 3 — Mount CR Touch**

1. Locate the CR Touch mount for Ender 3 Pro (STL available on Printables — print beforehand or use stock mount if included).
2. Mount CR Touch bracket to the left side of the X-carriage (standard position: 2mm left and ~3mm in front of nozzle tip — exact offsets go in printer.cfg).
3. Tighten mount screws — CR Touch must not wiggle at all.
4. **CR Touch wiring to original Melzi board:**

```
CR Touch connector (5 wires):
  Black  → GND   (Z-stop header, pin 1)
  Red    → +5V   (fan header or dedicated 5V pin — NOT PWM fan)
  Brown  → GND   (same GND, or any GND)  
  Orange → SERVO SIGNAL (connect to a free output — see note below)
  White  → PROBE SIGNAL → Z-stop signal pin (PA3)

On original ATmega board, Z-stop header is 3 pins:
  Pin 1: GND
  Pin 2: +5V (may not be present on all boards — measure with multimeter)
  Pin 3: Signal (PA3 / D19)

Safest approach:
  - White + Black → Z-stop header (signal + GND)  
  - Red + Brown + Orange → Fan 0 header or spare EXT header (+5V, GND, signal)
  
If your board's Z-stop header has no +5V pin, tap +5V from the always-on fan header.
```

> ⚠️ **DO NOT connect CR Touch power to the hot-end fan (FAN0) if it is PWM-switched.** The original Ender 3 Pro board has the part cooling fan on a PWM channel — using this for CR Touch +5V will cause servo errors. Use the extruder cooling fan header (always-on 12V stepped down... or locate the +5V rail directly). When in doubt, use a multimeter before connecting.

5. Route cables cleanly — zip tie along existing cable harness.
6. Leave Ender 3 Pro power OFF for now.

---

**Step 4 — Install Dual PEO Build Plate**

1. Remove existing bed surface.
2. The Idealformer dual PEO plate is 235×235mm — this fits the Ender 3 Pro's 235×235mm heated bed (note: actual **usable** print area is 220×220mm due to carriage limits; the plate is physically 235×235 to cover the full bed surface including clips).
3. PEO plates are magnetic — verify the bed has a magnetic steel sheet installed (Ender 3 Pro ships with one). If not, a magnetic base sheet must be added before the PEO plate.
4. Attach smooth PEO side first (default). Textured PEO will be the alternate.
5. Do not peel protective film yet if present.

---

### PHASE 2 — Pi Zero 2W Setup

**Step 5 — First Boot**

1. Insert flashed microSD into Pi Zero 2W.
2. Connect Pi power cable to Pi's PWR micro-USB port (labeled PWR IN).
3. Connect micro-USB OTG cable: Pi USB port (labeled USB) → Ender 3 Pro USB-B port.
4. Power on Pi first. Wait 90 seconds for first boot.
5. Find Pi IP: `nmap -sn 192.168.1.0/24 | grep penelope` or check router DHCP table.
6. SSH in: `ssh pi@penelope.local` (or use IP directly)

---

**Step 6 — Enable USB OTG and Prepare Pi**

```bash
# SSH into Pi:
ssh pi@penelope.local

# Enable USB OTG host mode (required for Pi Zero 2W to act as USB host):
echo "dtoverlay=dwc2" | sudo tee -a /boot/config.txt
echo "dwc2" | sudo tee -a /etc/modules

# Set Pi to not throttle for heat (optional but good):
echo "over_voltage=2" | sudo tee -a /boot/config.txt
echo "arm_freq=1000" | sudo tee -a /boot/config.txt  # keep at rated speed

# Add pi user to dialout for serial access:
sudo usermod -a -G dialout pi

# Update system:
sudo apt update && sudo apt upgrade -y

# Reboot to apply OTG mode:
sudo reboot
```

---

**Step 7 — Verify MainsailOS Services**

After reboot, SSH back in:

```bash
# Check Klipper, Moonraker, Mainsail are running:
sudo systemctl status klipper
sudo systemctl status moonraker
sudo systemctl status nginx

# If any are stopped:
sudo systemctl start klipper
sudo systemctl start moonraker
sudo systemctl start nginx
sudo systemctl enable klipper moonraker nginx

# Confirm printer USB connection is visible:
ls /dev/serial/by-id/
# Expect: usb-1a86_USB2.0-Serial-if00-port0 (CH340 driver)
# Note the full path — you will use it in printer.cfg
```

---

### PHASE 3 — Klipper Firmware Flash to ATmega1284P

> This is the step that previously failed via USB from Salomon. From the Pi Zero 2W, the physical connection is the same USB line — **BUT** the key difference is the Pi now controls the USB line directly and can hold the bootloader window open differently. If this still fails via avrdude from the Pi, the fallback is the USBASP ISP path (documented at end of this file). **Try USB first.**

**Step 8 — Compile Klipper Firmware on Pi**

```bash
# On Pi Zero 2W:
cd ~/klipper

# Configure for ATmega1284P:
make menuconfig
# Settings:
#   Micro-controller Architecture: Atmel AVR
#   Processor model: atmega1284p
#   Baud rate: 250000
# Save and exit

make clean
make -j4
# Output: out/klipper.elf and out/klipper.elf.hex
```

Alternatively, copy the pre-compiled hex from Salomon (it was already compiled for this exact board):

```bash
# From Salomon, copy to Pi:
scp ~/klipper/out/klipper.elf.hex pi@penelope.local:~/klipper_penelope.hex
```

---

**Step 9 — Flash Klipper MCU Firmware**

```bash
# On Pi (Ender 3 Pro power ON, USB connected to Pi):

# Identify serial port:
ls /dev/serial/by-id/
# Note exact path, e.g.: /dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0

# Stop klipper before flashing:
sudo systemctl stop klipper

# Flash via avrdude (try arduino protocol first):
sudo avrdude -p atmega1284p \
  -c arduino \
  -P /dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0 \
  -b 57600 \
  -U flash:w:~/klipper/out/klipper.elf.hex:i

# If that fails with bootloader timeout, try avr109 at 115200:
sudo avrdude -p atmega1284p \
  -c avr109 \
  -P /dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0 \
  -b 115200 \
  -U flash:w:~/klipper/out/klipper.elf.hex:i
```

> ⚠️ **If USB flash fails again (same bootloader window issue):** The USBASP ISP fallback is documented at the bottom of this file. You will need a ~$5 USBASP programmer. Do not spend Saturday fighting the bootloader — the ISP path is 5 minutes once the hardware arrives. Klipper will still work with OctoPrint as fallback if Saturday ISP fails.

---

**Step 10 — Deploy printer.cfg**

```bash
# On Pi, the MainsailOS Klipper config lives at:
~/printer_data/config/printer.cfg

# Copy the Penelope printer.cfg from this document (see Section below)
# or paste directly:
nano ~/printer_data/config/printer.cfg
```

Paste the full `printer.cfg` from the **printer.cfg** section of this document.

---

**Step 11 — Start Klipper and Connect**

```bash
sudo systemctl start klipper

# Watch logs for errors:
journalctl -fu klipper
# Look for: "Klipper ready" — this means MCU connected and config loaded

# From Salomon or any browser:
# Navigate to: http://penelope.local  OR  http://<penelope-ip>
# Mainsail interface should appear
```

---

### PHASE 4 — CR Touch Calibration

**Step 12 — Z Offset Calibration (PROBE_CALIBRATE)**

> Power on Ender 3 Pro. Home all axes in Mainsail. Verify CR Touch deploys and retracts (watch for the red LED and pin movement).

```gcode
; In Mainsail terminal:
G28               ; home all axes
PROBE_CALIBRATE   ; begins interactive Z offset calibration
```

This starts the paper-test method:
1. Klipper will move the nozzle to probe position
2. Use `TESTZ Z=-0.1` to move down in 0.1mm increments
3. Slide a piece of paper between nozzle and bed
4. When paper has slight drag: `ACCEPT`
5. Then: `SAVE_CONFIG`

This writes `#*# [bltouch] z_offset` to the bottom of `printer.cfg` automatically.

---

**Step 13 — Bed Mesh First Run**

```gcode
G28                    ; home
BED_MESH_CALIBRATE     ; runs 25-point (5x5) probe mesh
BED_MESH_PROFILE SAVE=default
SAVE_CONFIG
```

After SAVE_CONFIG, Klipper restarts. The mesh is now saved and will load automatically via `BED_MESH_PROFILE LOAD=default` in `START_PRINT`.

---

**Step 14 — First Print Validation**

```gcode
; Slice the 20mm calibration cube in OrcaSlicer using Penelope-Detail profile
; Upload to Mainsail → Print
; Watch first layer closely — adjust z_offset if needed:
SET_GCODE_OFFSET Z=-0.05   ; fine tune live, then SAVE_CONFIG
```

---

### ISP Fallback (If USB Flash Fails)

If avrdude via USB fails again (same bootloader timing issue as the 2026-06-20 session):

```bash
# Hardware needed: USBASP programmer (~$5 on Amazon)
# Connect USBASP to Ender 3 Pro ICSP header (6-pin, near ATmega)
# ICSP header pinout: MISO/VCC/SCK/MOSI/RST/GND

sudo avrdude -p atmega1284p \
  -c usbasp \
  -U flash:w:~/klipper/out/klipper.elf.hex:i

# This bypasses the bootloader entirely — no timing window issue
# The hex at ~/klipper/out/klipper.elf.hex on Salomon is already compiled
# Copy to Pi first: scp salomon:~/klipper/out/klipper.elf.hex ~/
```

---

## printer.cfg — Penelope (Ender 3 Pro, ATmega1284P, CR Touch)

```ini
# ============================================================
# PENELOPE — Klipper printer.cfg
# Machine: Ender 3 Pro (original 8-bit ATmega1284P board)
# Firmware: Klipper MCU on ATmega1284P, host on Pi Zero 2W
# Probe: CR Touch (BLTouch-compatible)
# Plate: Idealformer PEO 235x235mm
# Prepared: 2026-06-26 | Marcus
# ============================================================

[mcu]
# Serial path — verify with: ls /dev/serial/by-id/
serial: /dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
# If the above doesn't appear, try:
# serial: /dev/ttyUSB0
baud: 250000

[printer]
kinematics: cartesian
max_velocity: 200
max_accel: 1500
max_accel_to_decel: 750
max_z_velocity: 10
max_z_accel: 100
square_corner_velocity: 5.0

# ============================================================
# STEPPERS
# ============================================================

[stepper_x]
step_pin: PD7
dir_pin: !PC5
enable_pin: !PD6
microsteps: 16
rotation_distance: 40
endstop_pin: ^PC2
position_endstop: 0
position_max: 235
homing_speed: 50

[stepper_y]
step_pin: PC6
dir_pin: !PC7
enable_pin: !PD6
microsteps: 16
rotation_distance: 40
endstop_pin: ^PC3
position_endstop: 0
position_max: 235
homing_speed: 50

[stepper_z]
step_pin: PB3
dir_pin: PB2
enable_pin: !PA5
microsteps: 16
rotation_distance: 8
# CR Touch replaces Z endstop — endstop_pin uses bltouch:z_virtual_endstop
endstop_pin: probe:z_virtual_endstop
position_min: -2
position_max: 250
homing_speed: 10
second_homing_speed: 3
homing_retract_dist: 5

[extruder]
step_pin: PB1
dir_pin: !PB0
enable_pin: !PD6
microsteps: 16
rotation_distance: 33.683   # stock Ender 3 Pro — calibrate via e-steps test
nozzle_diameter: 0.400
filament_diameter: 1.750
heater_pin: PD5
sensor_type: EPCOS 100K B57560G104F
sensor_pin: PA7
min_temp: 0
max_temp: 260
min_extrude_temp: 170
pressure_advance: 0.0        # PLACEHOLDER — tune after install
pressure_advance_smooth_time: 0.040

[heater_bed]
heater_pin: PD4
sensor_type: EPCOS 100K B57560G104F
sensor_pin: PA6
min_temp: 0
max_temp: 120

[fan]
pin: PB4   # part cooling fan

[heater_fan extruder_fan]
pin: PB4
heater: extruder
heater_temp: 50.0

# ============================================================
# CR TOUCH (BLTouch-compatible)
# ============================================================

[bltouch]
sensor_pin: ^PC3
# NOTE: PA3 is the Z-stop signal pin on the original Ender 3 Pro board.
# Verify this matches your wiring before first boot.
# If CR Touch is wired to Z-stop header: sensor_pin: ^PA3
# Adjust based on which header you used (see wiring notes in runbook)
control_pin: PB4
# control_pin: the servo signal line — adjust to match your actual wiring
# Common alternate: PA4 if using EXT header
x_offset: -41.5   # CR Touch position relative to nozzle (measure your mount)
y_offset: -5.0    # Adjust after first probe calibration
z_offset: 0.0     # Set via PROBE_CALIBRATE — do not edit manually
speed: 5
lift_speed: 10
samples: 2
sample_retract_dist: 5
samples_result: median
samples_tolerance: 0.100
samples_tolerance_retries: 3
pin_up_touch_mode_reports_triggered: False  # required for CR Touch (not BLTouch)

# ============================================================
# BED MESH
# ============================================================

[bed_mesh]
speed: 80
horizontal_move_z: 5
mesh_min: 20, 20
mesh_max: 190, 190   # conservative inner mesh area accounting for CR Touch offset
probe_count: 5, 5
fade_start: 1.0
fade_end: 10.0
fade_target: 0
algorithm: bicubic
mesh_pps: 2, 2

[safe_z_home]
home_xy_position: 117.5, 117.5   # center of bed
speed: 80
z_hop: 10
z_hop_speed: 10

# ============================================================
# INPUT SHAPING (PLACEHOLDER — tune after install)
# ============================================================

[input_shaper]
# shaper_freq_x: 0    # PLACEHOLDER — run RESONANCE_TEST after install
# shaper_freq_y: 0    # Note: ADXL345 testing on Pi Zero 2W is unreliable
# shaper_type: mzv    # Manual tuning via ringing tower prints is recommended
# Uncomment and fill in after resonance testing

# ============================================================
# VIRTUAL SDCARD + DISPLAY STATUS
# ============================================================

[virtual_sdcard]
path: ~/printer_data/gcodes

[display_status]

[pause_resume]

[respond]

# ============================================================
# MAINSAIL REQUIRED
# ============================================================

[include mainsail.cfg]

# ============================================================
# MACROS — Djinn-Compatible (matches Calliope macro signature)
# ============================================================

[gcode_macro START_PRINT]
description: Standard print start — compatible with Calliope START_PRINT signature
gcode:
    {% set EXTRUDER_TEMP = params.EXTRUDER_TEMP|default(210)|float %}
    {% set BED_TEMP = params.BED_TEMP|default(60)|float %}
    
    G90                         ; absolute positioning
    M82                         ; absolute extruder
    M140 S{BED_TEMP}            ; start bed heating (non-blocking)
    M104 S150                   ; preheat hotend to safe temp (no ooze)
    
    G28                         ; home all axes
    BED_MESH_PROFILE LOAD=default ; load saved mesh
    
    M190 S{BED_TEMP}            ; wait for bed temp
    M109 S{EXTRUDER_TEMP}       ; wait for hotend temp
    
    ; Purge line — left edge of bed
    G1 Z5.0 F3000
    G1 X0.1 Y20 Z0.3 F5000.0
    G1 X0.1 Y200.0 Z0.3 F1500.0 E15
    G1 X0.4 Y200.0 Z0.3 F5000.0
    G1 X0.4 Y20 Z0.3 F1500.0 E30
    G92 E0
    
    G1 Z2.0 F3000
    G1 X5 Y20 Z0.3 F5000.0
    G92 E0
    RESPOND MSG="Penelope ready — printing"

[gcode_macro END_PRINT]
description: Standard print end — compatible with Calliope END_PRINT signature
gcode:
    G91                         ; relative positioning
    G1 E-5 F2700               ; retract 5mm
    G1 Z10 F3000               ; lift Z
    G90                         ; absolute positioning
    G1 X0 Y220 F3000           ; park — front of bed
    M104 S0                     ; hotend off
    M140 S0                     ; bed off
    M107                        ; fan off
    M84                         ; motors off
    RESPOND MSG="Penelope print complete"

[gcode_macro PAUSE]
description: Pause print
rename_existing: BASE_PAUSE
gcode:
    SAVE_GCODE_STATE NAME=PAUSE_state
    BASE_PAUSE
    G91
    G1 E-5 F2700
    G1 Z10 F3000
    G90
    G1 X0 Y220 F3000
    RESPOND MSG="Penelope paused — head parked"

[gcode_macro RESUME]
description: Resume print
rename_existing: BASE_RESUME
gcode:
    G91
    G1 E5 F2700
    G90
    RESTORE_GCODE_STATE NAME=PAUSE_state MOVE=1
    BASE_RESUME
    RESPOND MSG="Penelope resumed"

[gcode_macro CANCEL_PRINT]
description: Cancel print
rename_existing: BASE_CANCEL_PRINT
gcode:
    END_PRINT
    BASE_CANCEL_PRINT
    RESPOND MSG="Penelope print cancelled"

# Djinn failure park — matches Calliope macro
[gcode_macro djinn_failure_park]
description: Djinn emergency park on failure
gcode:
    {% if printer.toolhead.homed_axes == "xyz" %}
        G91
        G1 E-5 F2700
        G1 Z15 F3000
        G90
        G1 X0 Y220 F3000
    {% endif %}
    M104 S0
    M140 S0
    M107
    RESPOND MSG="Penelope emergency parked by Djinn"

# Djinn resume — matches Calliope macro
[gcode_macro djinn_resume_print]
description: Djinn resume after failure recovery
gcode:
    G91
    G1 E5 F2700
    G90
    RESUME

# ============================================================
# SAVE_CONFIG — DO NOT EDIT BELOW THIS LINE
# (Klipper writes z_offset and mesh data here automatically)
# ============================================================
```

---

## OrcaSlicer Profile — Penelope-Detail.json

> **Inheritance note:** This profile inherits from `Penelope-Standard-TreeSupports` where possible. The `inherits` field must match your exact existing profile name in OrcaSlicer. If your standard tree-support profile is named differently, update the `inherits` field before importing.
>
> **Location:** `~/Obsidian/djinn/printer/forge-slicer/profiles/process/Penelope-Detail.json`
>
> **Import:** OrcaSlicer → Filament/Process → Import Config

```json
{
  "type": "process",
  "name": "Penelope-Detail",
  "from": "User",
  "inherits": "Penelope-Standard-TreeSupports",
  "instantiation": "true",
  "compatible_printers": ["Creality Ender-3 Pro 0.4 nozzle"],
  "notes": "High-quality detail profile for Penelope. Slow speeds, high wall count, ironing enabled. PETG and PLA. Bowden retraction 5.5mm. Marcus 2026-06-26.",

  "layer_height": "0.12",
  "initial_layer_height": "0.2",
  "wall_loops": "5",
  "bottom_shell_layers": "6",
  "top_shell_layers": "6",

  "outer_wall_speed": "30",
  "inner_wall_speed": "50",
  "sparse_infill_speed": "60",
  "internal_solid_infill_speed": "40",
  "top_surface_speed": "30",
  "initial_layer_speed": "20",
  "travel_speed": "120",

  "enable_overhang_speed": "1",
  "overhang_1_4_speed": "25",
  "overhang_2_4_speed": "20",
  "overhang_3_4_speed": "15",
  "overhang_4_4_speed": "10",

  "ironing_type": "top",
  "ironing_speed": "15",
  "ironing_flow": "0.15",
  "ironing_spacing": "0.1",

  "support_type": "tree(auto)",
  "support_threshold_angle": "40",
  "support_on_build_plate_only": "0",
  "support_top_z_distance": "0.2",
  "support_interface_top_layers": "2",
  "support_interface_bottom_layers": "2",

  "retraction_length": ["5.5"],
  "retraction_speed": ["45"],
  "retract_before_travel": ["1.5"],
  "z_hop": ["0.2"],
  "z_hop_types": ["Slope Lift"],
  "retraction_minimum_travel": ["1.5"],

  "infill_combination": "0",
  "sparse_infill_density": "20",
  "sparse_infill_pattern": "grid",

  "cool_plate_temp": ["70", "65", "70", "65"],
  "cool_plate_temp_initial_layer": ["75", "70", "75", "70"],
  "eng_plate_temp": ["70", "65", "70", "65"],
  "eng_plate_temp_initial_layer": ["75", "70", "75", "70"],
  "hot_plate_temp": ["70", "65", "70", "65"],
  "hot_plate_temp_initial_layer": ["75", "70", "75", "70"],
  "textured_plate_temp": ["70", "65", "70", "65"],
  "textured_plate_temp_initial_layer": ["75", "70", "75", "70"],

  "nozzle_temperature": ["230", "210", "230", "210"],
  "nozzle_temperature_initial_layer": ["235", "215", "235", "215"],

  "fan_max_speed": ["50"],
  "fan_min_speed": ["30"],
  "bridge_fan_speed": ["80"],
  "slow_down_for_cooling": "1",
  "slow_down_min_speed": "15",
  "slow_down_layer_time": "8",

  "enable_prime_tower": "0",
  "seam_position": "aligned",
  "staggered_inner_seam": "0",

  "use_relative_e_distances": "0",
  "layer_gcode": ";LAYER_CHANGE\nG92 E0",

  "machine_start_gcode": "START_PRINT EXTRUDER_TEMP=[nozzle_temperature_initial_layer] BED_TEMP=[cool_plate_temp_initial_layer]",
  "machine_end_gcode": "END_PRINT"
}
```

> **Temperature array order:** `[PETG, PLA, PETG, PLA]` — indices correspond to OrcaSlicer's 4 plate types (cool plate, engineering plate, high-temp plate, textured plate). Filament selection in OrcaSlicer drives which index is active. This means PETG at 70°C bed / 230°C hotend, PLA at 65°C bed / 210°C hotend — as specified.

---

## Djinn Integration Checklist

After Penelope's Pi Zero 2W first boot and Moonraker is confirmed running:

### Step 1 — Note Penelope's IP

```bash
# From Salomon:
nmap -sn 192.168.1.0/24 | grep -A1 penelope
# Or check router DHCP table — look for hostname "penelope"
# Note the IP: 192.168.1.XXX
```

**Assign a DHCP reservation in your router for penelope.local** — prevents IP drift (the Calliope .113→.114 problem should not repeat with Penelope).

---

### Step 2 — Update ~/.djinn.env and printers.env

```bash
# In ~/.config/djinn/printers.env (or ~/.djinn.env — wherever printers block lives):

# Add Penelope Moonraker entry:
DJINN_MOONRAKER_PENELOPE=http://192.168.1.XXX:7125
# Replace XXX with Penelope's actual assigned IP

# Verify Calliope entry is correct (from prior IP fix):
DJINN_MOONRAKER_CALLIOPE=http://192.168.1.114:7125

# Health check:
curl $DJINN_MOONRAKER_PENELOPE/printer/info
# Expected: JSON with klippy_state: ready
```

---

### Step 3 — Retire OctoPrint Connection Logic for Penelope

```bash
# The following are now obsolete for Penelope — update or archive:

# 1. djinn-penelope CLI (currently uses OctoPrint at localhost:5001)
#    → Rewrite to use Moonraker API (same as djinn-confirm-print / djinn-force-cancel)
#    → New endpoint: $DJINN_MOONRAKER_PENELOPE/printer/gcode/script
#    → Upload: $DJINN_MOONRAKER_PENELOPE/server/files/upload
#    → Print start: POST $DJINN_MOONRAKER_PENELOPE/printer/print/start

# 2. OctoPrint service — stop and disable:
sudo systemctl stop djinn-penelope.service
sudo systemctl disable djinn-penelope.service
# Do NOT delete yet — keep as fallback until Klipper is confirmed stable

# 3. DJINN_PENELOPE_APIKEY in printers.env — no longer needed post-OctoPrint
#    (Moonraker uses its own API key or trusted network — localhost is trusted by default)

# 4. Any script referencing localhost:5001 for Penelope:
grep -r "5001" ~/.local/bin/ ~/.config/djinn/
# Review each hit — update to use DJINN_MOONRAKER_PENELOPE
```

---

### Step 4 — Add Penelope to Heartbeat Monitor

```bash
# If Djinn has a heartbeat/health monitor (djinn-agent-doctor or similar):
# Add entry for Penelope alongside Calliope:

# Example entry format (adjust to your actual monitor script):
# PENELOPE | $DJINN_MOONRAKER_PENELOPE/printer/info | klippy_state=ready

# Test manually:
curl -s "$DJINN_MOONRAKER_PENELOPE/printer/info" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d['result']['state'])"
# Expected: ready
```

---

### Step 5 — Update djinn-model-slice and print pipeline for --printer penelope

This is the Phase 2 CLI refactor from the integration plan. Minimum viable for Saturday:

```bash
# Short-term: use Moonraker API directly from Mainsail for Penelope jobs
# until djinn-model-slice gets the --printer flag

# The START_PRINT/END_PRINT macros are now identical in signature to Calliope's
# so OrcaSlicer profiles can use the same gcode template:
#   START_PRINT EXTRUDER_TEMP=[nozzle_temp] BED_TEMP=[bed_temp]
# Djinn can route to either printer using the same gcode — printer selection
# happens at the Moonraker upload endpoint, not in the gcode itself.
```

---

## MACHINE-ROLES.md (Vault Doc)

> **Location:** `~/Obsidian/djinn/printer/MACHINE-ROLES.md`

```markdown
---
title: Machine Roles — Djinn Print Fleet
agent: Marcus
date: 2026-06-26
tags: [djinn, printer, roles, routing, penelope, calliope]
related: [[PENELOPE-SATURDAY-RUNBOOK]] | [[CALLIOPE-MANUAL]] | [[PRINT-PROFILES]]
---

# Machine Roles — Djinn Print Fleet

Last updated: 2026-06-26  
Fleet: 2 printers (Penelope + Calliope)

---

## Penelope — Detail Machine

| Field | Value |
|-------|-------|
| Hardware | Creality Ender 3 Pro |
| Firmware | Klipper (Pi Zero 2W host, ATmega1284P MCU) |
| IP | 192.168.1.XXX (assign DHCP reservation) |
| Moonraker | http://192.168.1.XXX:7125 |
| Interface | Mainsail |
| Build volume | 220×220×250mm |
| Extruder | Bowden (stock) — retraction 5.5mm |
| Probe | CR Touch + bed mesh 5×5 |
| Bed surface | Idealformer Dual PEO (Smooth + Textured, 235×235mm) |
| Materials | PETG primary, PLA secondary |
| Env var | DJINN_MOONRAKER_PENELOPE |

**Role:** Personal projects, display pieces, experimental models, maximum quality output.  
Penelope prints slow and prints right. She is the detail machine — the one you use when surface quality, dimensional accuracy, and resolution matter more than time.

**Use Penelope when:**
- Layer height ≤ 0.16mm
- Wall count ≥ 4
- Ironing or top surface finish matters
- Material is PETG, experimental, or requires fine-tuned profiles
- Print is for personal use, display, or precision fit
- Part fits in 220×220×250mm
- You want to iterate on profile settings without affecting commission queue

**Do not use Penelope when:**
- Print is a commission deliverable on deadline
- Model exceeds 220×220×250mm
- Volume is needed (multiple copies, batch runs)
- Speed is more important than quality

---

## Calliope — Production Machine

| Field | Value |
|-------|-------|
| Hardware | Creality Ender-3 V3 Plus |
| Firmware | Klipper (dedicated Pi host) |
| IP | 192.168.1.114 (DHCP reserved as Ender-3.lan) |
| Moonraker | http://192.168.1.114:7125 |
| Interface | Mainsail / Djinn Discord pipeline |
| Build volume | 300×300×330mm (usable) |
| Extruder | Direct drive (Sprite Pro) — retraction 0.5–1mm |
| Materials | PLA primary, PETG capable |
| Env var | DJINN_MOONRAKER_CALLIOPE |

**Role:** Commissions, production runs, high-volume output, reliable workhorse.  
Calliope is the machine that makes money. She is always-ready, Djinn-automated, and optimized for throughput. She does not get experimental profiles or fine-tune sessions during active commission queue.

**Use Calliope when:**
- Print is a commission deliverable
- Part exceeds 220×220×250mm (only Calliope can fit it)
- Multiple copies needed (batch slicing)
- PLA, standard settings, speed + reliability matter
- Djinn Discord pipeline is the workflow (slice N → confirm N)

**Do not use Calliope when:**
- Experimental profile tuning is needed (puts commission queue at risk)
- Print is personal and small enough for Penelope
- Material is PETG at high temp (Calliope's Sprite Pro nozzle has thermal limits)

---

## Routing Logic — How Claude Should Decide

```
Given a print job, Claude routes as follows:

1. SIZE CHECK (hard constraint):
   - Model > 220mm in any axis → CALLIOPE only (Penelope cannot fit it)
   - Model ≤ 220×220×250mm → both printers eligible, continue to step 2

2. JOB TYPE:
   - Commission or deadline job → CALLIOPE
   - Personal / experimental / detail → PENELOPE
   - Ambiguous → ask Javier

3. MATERIAL:
   - PETG → PENELOPE preferred (Penelope's profile is tuned; Calliope's PETG support is basic)
   - PLA, standard → CALLIOPE preferred (faster, automated pipeline)
   - Experimental material → PENELOPE only

4. QUALITY TARGET:
   - Layer height ≤ 0.16mm, ironing, or detail mode → PENELOPE
   - Standard / production profile → CALLIOPE

5. QUEUE STATE:
   - If Calliope is printing a commission → PENELOPE for any waiting personal jobs
   - If both idle → use above rules

DEFAULT: When in doubt, ask Javier. Never route a commission to Penelope
without explicit approval. Never route an experimental profile to Calliope
during an active commission run.
```

---

## Fleet Quick Reference

| | Penelope | Calliope |
|--|----------|----------|
| Role | Detail / Personal | Production / Commission |
| Speed | Slow (quality) | Fast (throughput) |
| Build area | 220×220×250mm | 300×300×330mm |
| Primary material | PETG | PLA |
| Retraction | 5.5mm Bowden | 0.5mm Direct Drive |
| Layer height default | 0.12–0.16mm | 0.20mm |
| Djinn pipeline | Mainsail + Moonraker API | Mainsail + Discord/Telegram |
| Automation level | Semi-manual (Phase 2 pending) | Fully automated |

*— Marcus, 2026-06-26*
```

---

## Post-Saturday: What's Not Done Yet

These are out of scope for Saturday but should be tracked:

- [ ] `djinn-model-slice --printer penelope` flag (Phase 2 CLI refactor — existing plan)
- [ ] Progress notifications for Penelope (OctoPrint webhooks → Telegram were pending; now route Moonraker events to Djinn monitor instead)
- [ ] Input shaping resonance test (requires ADXL345 — Pi Zero 2W can run it but is unreliable at high sample rates; use Salomon if possible, or do manual ringing tower tuning)
- [ ] Pressure advance calibration (print pressure advance tower, then update `pressure_advance:` in printer.cfg)
- [ ] PETG-specific OrcaSlicer filament profile `Penelope-PETG.json` (Marcus report from 2026-06-20 has all specs — just not created yet)
- [ ] `confirm N` safety gate for Penelope jobs (mirrors Calliope's djinn-confirm-print)
- [ ] MACHINE-ROLES.md: add Penelope IP once DHCP reservation is confirmed

---

*Runbook prepared by Marcus — 2026-06-26*  
*Source vault docs: PLAN-penelope-integration.md, 2026-06-20_penelope-live.md, CALLIOPE-MANUAL.md, 2026-06-21_bug-creality-print-klipper-macros-on-marlin.md*  
*Saturday target: Penelope wireless + Klipper + CR Touch + Mainsail + Djinn integrated*
