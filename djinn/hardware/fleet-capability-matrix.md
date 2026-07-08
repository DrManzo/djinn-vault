---
title: Fleet Capability Matrix
agent: Claude + Marcus
date: 2026-07-07
tags: [djinn, hardware, fleet, printers, capability]
---

# Djinn Fleet — Machine Capability Profiles

> **Enclosure note:** All FlashForge machines (Iris, Nemesis) are enclosed. Creality machines (Calliope, Penelope) are open frame.

---

## Quick-Reference Comparison Table

| | **Iris — AD5X** | **Nemesis — AD5M Pro** | **Calliope — E3V3+** | **Penelope — E3 Pro** |
|---|---|---|---|---|
| **Build Volume** | 220×220×220 mm | 220×220×220 mm | 300×300×330 mm | 220×220×250 mm |
| **Max Nozzle Temp** | 300°C | 280°C | 300°C | 260°C (Marlin soft cap) |
| **Max Bed Temp** | 110°C | 110°C | ~100°C | ~100°C |
| **Enclosure** | **Yes** | **Yes** (active HEPA) | No | No |
| **Extruder** | Direct drive | Direct drive | Direct drive (Sprite Pro) | Bowden (stock) |
| **Multi-material** | Yes — IFS 4-color | No | No | No |
| **Firmware** | Klipper (zmod/bambufy) | Klipper (zmod) | Klipper (Moonraker) | Klipper (Pi Zero 2W / ATmega1284P) |
| **Motion System** | CoreXY | CoreXY | CoreXZ | Cartesian (stock) |
| **Input Shaping** | Yes | Yes | Yes | Limited (ATmega cap) |
| **Best Role** | Multi-color display/detail | Engineering materials, enclosed single-color | Production workhorse, commissions | Detail/personal, experimental, PETG fine-tune |

---

## Iris — FlashForge AD5X

### Print Volume
220×220×220 mm. Square footprint — loses Calliope's Z height advantage. Good for multi-color display pieces, figurines, and smaller technical parts.

### Material Compatibility
- **Reliable:** PLA, PETG, TPU 95A (notably, multi-color TPU is a standout capability vs. competitors), PLA-CF, PETG-CF
- **Struggles:** ABS/ASA — enclosure helps but chamber temp is not independently controlled; warping risk on larger parts
- **Off-limits:** Nylon, PC, high-temp engineering resins without sustained chamber heat; CF blends accelerate nozzle wear (hardened steel stock helps)

### Safety Limits
- Max nozzle: 300°C
- Max bed: 110°C
- Enclosure: **Yes**
- Thermal runaway protection: Yes (CE/FCC/RoHS certified)
- **Known Klipper/bambufy issues:** `shoot_y_position=223` can cause "Move out of range" at Y=234.7 during long multi-color retractions — may need lowering to 218

### Multi-Material Capability
- **System:** IFS (Intelligent Filament System) — 4 spools, side-mounted, integrated cutter
- **Strengths:** Lower path resistance than AMS-style top-box; handles multi-color TPU better than Bambu AMS
- **Reliability notes:** Bambufy init issue on Klipper restart — `_START_BAMBUFY` must be triggered manually after restart. `min_version` mismatch fixed (1.2.2). Monitor first multi-color tool change.

### Known Struggles
- IFS purge waste accumulates — poop chute management required
- Bambufy + zmod stacked on Klipper = complex debugging surface
- 220mm Z is the smallest Z in the fleet
- Y-axis "Move out of range" bug during long multi-color retractions unresolved

### Best Use Case
Multi-color display pieces, figurines, props, any job requiring color changes. IFS handling multi-color TPU out-of-box is genuinely rare. Reserve for jobs where color separation matters more than build volume.

---

## Nemesis — FlashForge AD5M Pro

### Print Volume
220×220×220 mm. Enclosed chamber is the key differentiator from Iris.

### Material Compatibility
- **Reliable:** PLA, PETG, TPU (0.4mm nozzle); PLA-CF, PETG-CF (0.6mm nozzle recommended)
- **Capable with care:** ABS, ASA — enclosed chamber helps significantly; bed at 100–110°C + chamber temp from bed heat can sustain prints
- **Off-limits:** PC, Nylon without hotend upgrades (280°C max is below ideal for sustained PA/PC runs)
- **Active profile:** PETG at 240/235°C nozzle, 70°C bed, 30–50% fan, PA 0.035

### Safety Limits
- Max nozzle: **280°C** — lowest in the fleet
- Max bed: 110°C
- Enclosure: **Yes** — active HEPA + activated carbon dual-layer filtration
- **Config trap:** `[probe]` is in `printer.base.cfg` (included file) — `SAVE_CONFIG` always fails for z_offset; must write z_offset manually to `/opt/config/printer.base.cfg` every PROBE_CALIBRATE. Permanent fix: move `[probe]` to `printer.cfg`.
- **Stock screen:** FlashForge touchscreen scans first ~200 lines for M104/M140; OrcaSlicer start gcode must include M140+M104 before START_PRINT

### Multi-Material Capability
Single material only.

### Known Struggles
- 280°C nozzle cap limits PC/high-temp Nylon
- Bed physically tilted right-side-low (~1.3mm corner-to-corner); mesh compensates but manual re-tramming needed
- z_offset SAVE_CONFIG conflict is a permanent workflow trap without the probe section move
- 220mm Z — can't compete with Calliope's 330mm for tall parts

### Best Use Case
ABS/ASA prints requiring enclosure, PETG with chamber stability, engineering prototypes. The only machine currently capable of reliable ABS production in the fleet.

---

## Calliope — Creality Ender-3 V3 Plus

### Print Volume
300×300×330 mm — **largest in the fleet.** Only machine that can handle oversized commissions and tall models.

### Material Compatibility
- **Reliable:** PLA (primary)
- **Capable:** PETG — fan hard-capped at S128 (50%) system-wide to prevent EMI-induced nozzle_mcu dropout
- **Struggles:** ABS/ASA — open frame, no enclosure; warping risk worsens at 300×300 bed scale
- **Note:** CF blends need caution; no enclosure limits ABS reliability

### Safety Limits
- Max nozzle: 300°C
- Max bed: ~100°C
- Enclosure: **No**
- **Critical known issue (BUG-014):** nozzle_mcu UART cable harness — recurring key561 dropouts (bytes_invalid growing). Replacement cable on hand as of 2026-07-07; awaiting drag chain before install. Machine sidelined for long PETG runs until cable swap done.
- **Fan cap rule:** Hard cap at S128 (50%) system-wide — M106 S255 at bridge infill triggers EMI spike → instant nozzle_mcu dropout. Hardware constraint, not a preference.
- Thermal runaway: Yes (Klipper + PLR watchdog via plr.cfg)
- **Authorization rule:** NEVER start a print on Calliope without explicit per-job approval from Javier

### Multi-Material Capability
None.

### Known Struggles
- nozzle_mcu cable is the #1 reliability liability in the fleet right now
- CoreXZ motion — Z moves shared with one axis; can cause subtle quality degradation on very tall prints
- 300×300 bed takes longer to heat/cool; wide-bed motion is exactly what stresses the nozzle_mcu cable
- Fan cap at 50% limits bridging performance

### Best Use Case
Commission deliverables, production runs, oversized parts (>220mm in any axis), batch printing. Calliope makes money. Default routing target for all commission jobs in the Djinn Discord/Telegram pipeline.

---

## Penelope — Creality Ender-3 Pro (8-bit)

### Print Volume
220×220×250 mm. Slightly taller Z than Iris/Nemesis.

### Material Compatibility
- **Reliable:** PETG (primary), PLA (secondary)
- **Struggles:** ABS/ASA — no enclosure, Bowden path adds complexity; PETG stringing is the primary challenge (5.5–6.5mm retraction, combing, 230°C tuned baseline)
- **Off-limits:** CF blends and engineering materials — stock Bowden hotend, 260°C cap, 8-bit board speed limits

### Safety Limits
- Max nozzle: **~260°C** (Marlin 1.1.6 conservative cap on ATmega1284P)
- Max bed: ~100°C
- Enclosure: **No**
- **Pi Zero 2W caveat:** No hardware watchdog by default; Klipper on Pi handles thermal monitoring
- **Speeds capped at 40–60mm/s** — ATmega1284P cannot reliably process high-acceleration motion
- **USB flash broken** — Creality removed the auto-reset capacitor; future MCU firmware flashing requires USBASP ISP programmer (~$5) on ICSP header

### Multi-Material Capability
None.

### Known Struggles
- Bowden stringing on PETG — primary quality challenge; 5.5mm retraction at 45mm/s is tuned baseline
- 8-bit board speed ceiling — max ~9mm³/s volumetric, prints 2–3× slower than Calliope
- No reliable input shaping via ADXL345 on Pi Zero 2W — use manual ringing tower method
- Pi Zero 2W RAM pressure — 512MB total; sits at 350–400MB under load, no headroom for camera stream
- ATmega USB flash broken — ISP programmer required for MCU firmware updates

### Best Use Case
Personal projects, display pieces, fine surface quality (0.12–0.16mm layers, ironing, high wall count), PETG profile iteration. The detail machine. Never route commissions to Penelope.

---

## Penelope — 8-bit Board Deep Dive

### What the ATmega1284P Limits

| Constraint | Impact |
|---|---|
| Max volumetric speed ~9mm³/s | Hard cap on throughput |
| Speed ceiling 40–60mm/s outer walls | 2–3× slower than Calliope equivalent |
| No reliable input shaping via ADXL345 | Manual ringing tower calibration only |
| USB flash broken (no reset cap) | ISP programmer required for MCU firmware |

> **Note:** Klipper on the Pi Zero 2W already gives Penelope pressure advance and bed mesh despite the 8-bit MCU. ATmega just executes motion commands — all smart processing runs on the Pi. This is the correct architecture and is already in place.

### What a 32-bit Board Unlocks

Creality 4.2.7 with STM32F103 (~$30–45):
- Reliable ADXL345 input shaping — automated shaper freq detection
- Higher step rates — faster travel, less stutter on complex gcode
- Silent TMC2208/2209 drivers built in — significantly quieter than current A4988
- Direct USB DFU flashing — no ISP programmer needed for future updates
- Better microstepping — 256 vs. 16, smoother motion at low speeds

### Upgrade Priority Stack (Best ROI per Dollar)

1. **Hotend + extruder (~$25–50) — highest ROI:** Direct drive conversion (BMG/Orbiter + Dragon/Rapido) eliminates Bowden stringing entirely, brings retraction to 0.5–1mm, opens TPU. Biggest quality improvement available for Penelope.

2. **32-bit board 4.2.7 (~$35–45):** Silent drivers + reliable input shaping + easier firmware management. Most valuable if pushing speeds or running resonance calibration. Not required if Penelope stays slow/quality-focused.

3. **All-metal hotend (~$15–25):** If staying Bowden, removes PTFE from heat zone, enables ABS/ASA reliably. Lower ROI than direct drive but cheap.

4. **Linear rails X/Y (~$40–60):** Improves dimensional accuracy, reduces backlash. High-effort mod — do after hotend and board.

### Board Swap vs. Workhorse Verdict

Start with hotend/extruder, defer board swap. The Bowden extruder is the bottleneck for Penelope's current role, not the 8-bit board. Direct drive conversion gives better print quality immediately and costs less. Reassess board swap after direct drive is done.

---

## Expansion Flag — Bambu Lab P1S + AMS (×2, Under Consideration)

*Research only — no decision required.*

### Capability Summary

| Spec | Value |
|---|---|
| Build volume | 256×256×256 mm |
| Max nozzle temp | 300°C |
| Max bed temp | 100°C |
| Enclosure | Yes — active chamber fan + HEPA/carbon filter |
| Chamber temp control | Passive (bed-driven, no independent thermostat) |
| Max speed | 500mm/s, 20,000 mm/s² |
| Multi-material | AMS — 4 spools/unit, up to 4 units daisy-chained (16 colors) |
| Materials (ideal) | PLA, PETG, TPU, ABS, ASA, PVA, PET |
| Materials (with upgrades) | PA, PC — hardened nozzle required |
| CF/GF blends | Not recommended stock — hardened 0.6mm nozzle + extruder gear upgrade |

### AMS Failure Modes

- **TPU in AMS is poorly supported** — flexible filaments jam in the AMS buffer; most users bypass AMS for TPU (single spool direct)
- **Filament sensor failures** — high-frequency failure part; community reports frequent sensor replacement
- **Heat creep clogging** — enclosed chamber retains heat; PLA in AMS hub above chamber can soften and jam in hot environments; vented risers are common community mod
- **AMS feeding failures on long multi-color jobs** — PTFE path resistance and buffer tension cause mid-print jams; third-party filaments more prone

### Closed Ecosystem Constraints

- **Bambu Cloud dependency** — full feature set requires Bambu account + cloud. LAN-only mode exists but loses features.
- **No native Klipper** — proprietary firmware; community Klipper ports exist but unsupported/unstable. Djinn's Moonraker pipeline **cannot natively integrate the P1S** without custom bridge work.
- **Proprietary MQTT protocol** — community has reverse-engineered it (bambu-farm, etc.) but Djinn integration would require maintaining a custom API bridge vs. standard Moonraker REST used by all current machines.
- **Walled garden slicer** — Bambu Studio required for full AMS color workflow; OrcaSlicer has community P1S support but loses some AMS features.

### Fleet Integration Assessment

Two P1S units would add enclosed ABS/ASA production capacity and multi-color production scale, but introduce a split-pipeline problem. Every current Djinn machine runs Moonraker — one API, one CLI surface, one pipeline. P1S adds a second API paradigm, separate slicer workflows, and cloud dependency. Flag this before any purchase decision.

---

*— Claude + Marcus, 2026-07-07*
