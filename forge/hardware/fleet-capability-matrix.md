---
title: Fleet Capability Matrix
agent: Claude + Marcus
date: 2026-07-07
tags: [djinn, hardware, fleet, printers, capability]
---

# Djinn Fleet — Machine Capability Profiles

Built from vault docs and current hardware research. Covers all four active machines plus the P1S expansion flag.

> **Enclosure note:** All FlashForge machines (Iris, Nemesis) are enclosed. Creality machines (Calliope, Penelope) are open frame.

---

## Quick-Reference Comparison Table

| | **Iris — AD5X** | **Nemesis — AD5M Pro** | **Calliope — E3V3+** | **Penelope — E3 Pro** |
|---|---|---|---|---|
| **Build Volume** | 220×220×220 mm | 220×220×220 mm | 300×300×330 mm | 220×220×250 mm |
| **Max Nozzle Temp** | 300°C | 280°C | 300°C | 260°C (Marlin soft cap) |
| **Max Bed Temp** | 110°C | 110°C | ~100°C | ~100°C |
| **Enclosure** | Yes (DIY, passive) | Yes (active HEPA) | No | No |
| **Extruder** | Direct drive | Direct drive | Direct drive (Sprite Pro) | Bowden (stock) |
| **Multi-material** | Yes — IFS 4-color | No | No | No |
| **Firmware** | Klipper (zmod/bambufy) | Klipper (zmod) | Klipper (Moonraker) | Klipper/OctoPrint (Pi Zero 2W / ATmega1284P) |
| **Slicer** | Bambu Studio (Typhon) | OrcaSlicer (Typhon) | OrcaSlicer or Creality Print (Typhon) | OrcaSlicer (Typhon) |
| **Motion System** | CoreXY | CoreXY | CoreXZ | Cartesian (stock) |
| **Input Shaping** | Yes | Yes | Yes | Limited (ATmega cap) |
| **Best Role** | Multi-color display/detail | Engineering materials, enclosed single-color | Production workhorse, commissions | Detail/personal, experimental, PETG fine-tune |

---

## Iris — FlashForge AD5X

### Print Volume

220×220×220 mm. Square footprint — loses Calliope's Z height advantage. Good for multi-color display pieces, figurines, and smaller technical parts.

### Material Compatibility

- **Reliable:** PLA, PETG, TPU 95A (notably, multi-color TPU is a standout capability vs. competitors), PLA-CF, PETG-CF
- **Struggles:** ABS/ASA — DIY enclosure helps over open-air but chamber temp is passive (bed/hotend heat only, no active heater); warping risk on larger parts; sealing quality depends on the build
- **Off-limits:** Nylon, PC, high-temp engineering resins — passive chamber can't sustain the temps required; CF blends technically supported but accelerate nozzle wear (hardened steel stock helps)

### Safety Limits

- Max nozzle: 300°C
- Max bed: 110°C
- Enclosure: **Yes (DIY, passive — no active filtration).** No HEPA/carbon filtering; ventilation or aftermarket filter (Nevermore, HEPA insert) recommended for ABS/ASA. Chamber temp from bed and hotend only — less stable than Nemesis's factory enclosure.
- Thermal runaway protection: Yes (certified CE/FCC/RoHS)
- **Bambufy/Klipper-specific:** Two open bugs in vault — `_START_BAMBUFY` delayed gcode doesn't auto-load on zmod restart (must trigger manually), and `shoot_y_position=223` can cause "Move out of range" at Y=234.7 during long multi-color retractions (may need lowering to 218)

### Multi-Material Capability

- **System:** IFS (Intelligent Filament System) — 4 spools, side-mounted, integrated cutter
- **How it works:** Side-mounted buffer/switcher with dedicated cutter; filament path designed for lower resistance than top-box AMS-style systems, enabling multi-color TPU
- **Reliability notes:** IFS generates purge waste ("poop") but achieves clean color transitions; community reports it handles TPU multi-color better than Bambu AMS which struggles with flexible filaments. `min_version` mismatch bug (1.2.3 vs 1.2.2) was fixed in vault. Bambufy init issue on restart remains open — monitor after every Klipper restart.

### Known Struggles / Weak Points

- IFS purge waste accumulates — poop chute mod (FlashForge wiki) was designed for open-frame; confirm DIY enclosure accommodates the ejection path without obstruction; may need chute extended or repositioned
- Bambufy layer on top of zmod Klipper adds complexity: two stacked non-stock software systems means debugging is harder than on a standard printer
- 220×220×220 cubic volume is the smallest in the fleet — no Z height advantage
- Y-axis "Move out of range" bug during long multi-color retractions is unresolved

### Best Use Case

Multi-color display pieces, figurines, props, and any job requiring color changes with flexible TPU. The IFS system handling multi-color TPU out-of-box is genuinely rare. Best reserved for jobs where color separation matters more than build volume.

---

## Nemesis — FlashForge AD5M Pro

### Print Volume

220×220×220 mm. Identical footprint to Iris; enclosed chamber is the key differentiator.

### Material Compatibility

- **Reliable:** PLA, PETG, TPU (0.4mm nozzle); PLA-CF, PETG-CF (0.6mm nozzle recommended)
- **Capable with care:** ABS, ASA — enclosed chamber helps significantly; bed at 100–110°C + chamber temp from bed heat can sustain prints
- **Off-limits:** PC, Nylon without further hotend upgrades (max 280°C is below ideal for sustained PA/PC runs); fiber-reinforced on 0.4mm nozzle accelerates wear
- **Vault note:** Nemesis PETG profile is live at 240/235°C nozzle, 70°C bed, 30–50% fan, PA 0.035, with `SET_GCODE_OFFSET Z_ADJUST=0.03` in filament start gcode

### Safety Limits

- Max nozzle: **280°C** — lower than the rest of the fleet
- Max bed: 110°C
- Enclosure: Yes — active HEPA + activated carbon dual-layer filtration
- Thermal runaway: Yes
- **Known Klipper config issue:** `[probe]` is in `printer.base.cfg` (included file), meaning `SAVE_CONFIG` always fails for z_offset — must write z_offset manually to `/opt/config/printer.base.cfg` every time `PROBE_CALIBRATE` is run. This is a trap that will bite if forgotten.
- **Stock screen compatibility:** FlashForge touchscreen scans first ~200 lines of gcode for M104/M140; pure Klipper START_PRINT macro blocks the print — OrcaSlicer start gcode must include M140+M104 before START_PRINT

### Multi-Material Capability

Single material only. No multi-filament system.

### Known Struggles / Weak Points

- 280°C nozzle cap limits high-temp engineering runs (PC, high-temp Nylon)
- Bed physically tilted right-side-low (~1.3mm corner-to-corner variation); mesh compensates but manual re-tramming while warm is needed for best first-layer consistency
- z_offset SAVE_CONFIG conflict is a permanent workflow trap — every recalibration requires a manual SSH file edit
- 220mm Z height matches Iris, can't compete with Calliope's 330mm Z for tall parts
- zmod Klipper + stock FlashForge touchscreen creates a dual-system dependency; OrcaSlicer must be used (not FlashForge slicer) for proper Klipper compatibility

### Best Use Case

ABS/ASA prints requiring enclosure (functional parts, engineering prototypes), PETG that benefits from chamber temperature stability, and any job needing closed-chamber printing in the fleet. The enclosed chamber makes it the only machine currently capable of reliable ABS production.

---

## Calliope — Creality Ender-3 V3 Plus

### Print Volume

300×300×330 mm — **largest in the fleet.** The only machine that can handle oversized commissions and tall models.

### Material Compatibility

- **Reliable:** PLA (primary)
- **Capable:** PETG — but flagged "not at high temp" in machine roles doc; fan cap at S128 (50%) is system-wide to prevent EMI-induced nozzle_mcu dropout
- **Struggles:** ABS/ASA — open frame, no enclosure, warping risk on large parts; the 300×300 bed size makes warping worse at scale
- **Off-limits:** CF blends need caution — nozzle is tri-metal quick-swap but abrasive materials reduce longevity; no enclosure limits ABS reliability

### Safety Limits

- Max nozzle: 300°C
- Max bed: ~100°C
- Enclosure: No
- **Critical known electrical issue:** nozzle_mcu UART cable harness (BUG-014) — recurring key561 dropouts (bytes_invalid growing = intermittent partial-wire contact). Replacement cable on hand as of 2026-07-07; awaiting drag chain before install. History: originally fixed 2026-06-03 (reseat), recurred 2026-06-28, fully diagnosed 2026-07-05 as degraded cable.
- **Fan cap rule:** Hard cap at S128 (50%) system-wide — M106 S255 at bridge infill creates EMI spike → instant nozzle_mcu dropout. This is a hardware constraint, not a preference.
- Thermal runaway: Yes (Klipper + PLR watchdog via plr.cfg)
- **Authorization rule:** NEVER start a print on Calliope without explicit per-job approval from Javier

### Multi-Material Capability

Single material. No multi-filament system.

### Known Struggles / Weak Points

- nozzle_mcu cable is a chronic failure point — the #1 reliability liability in the fleet right now; cable replacement + service loop + stepper wire separation is the required fix
- CoreXZ motion (not CoreXY) — Z moves are shared with one axis; can cause subtle quality degradation on very tall prints compared to true CoreXY
- 300×300 bed takes longer to heat and cool; PEI surface care is more critical at this scale
- Wide-bed operations (multi-object plates, full mesh probing) are exactly the motion profile that stresses the nozzle_mcu cable — avoid until cable replaced
- Fan cap at 50% limits bridging performance on some materials

### Best Use Case

Commission deliverables, production runs, oversized parts (>220mm in any axis), and batch printing. Calliope makes money. She is fully automated in the Djinn Discord/Telegram pipeline and is the default routing target for all commission jobs.

---

## Penelope — Creality Ender-3 Pro

### Print Volume

220×220×250 mm. Slightly taller Z than Iris/Nemesis due to stock Ender-3 Pro frame geometry.

### Material Compatibility

- **Reliable:** PETG (primary), PLA (secondary)
- **Struggles:** ABS/ASA — no enclosure, Bowden path adds complexity; PETG stringing is the known challenge with Bowden (5.5–6.5mm retraction, combing, 230°C is the calibrated baseline)
- **Off-limits:** CF blends and engineering materials — stock Bowden hotend, 260°C Marlin soft cap, 8-bit board speed limits make these impractical

### Safety Limits

- Max nozzle: ~260°C (Marlin 1.1.6 on ATmega1284P; hardware may support higher but firmware conservative cap)
- Max bed: ~100°C
- Enclosure: No
- **8-bit board thermal runaway:** Marlin 1.1.6 has basic thermal runaway but lacks the sophisticated watchdog of Klipper. With the Pi Zero 2W + Klipper now installed as host, Klipper's thermal monitoring runs on the Pi — this is substantially safer
- **Pi Zero 2W caveat:** No hardware watchdog by default; if klippy crashes, printer may continue moving until `[display_status]` + `[virtual_sdcard]` catch it (configured in printer.cfg)
- Speeds capped at 40/50/60mm/s max — 8-bit ATmega1284P cannot reliably process high-acceleration motion commands

### Multi-Material Capability

None. Single material, Bowden.

### Known Struggles / Weak Points

- Bowden stringing on PETG — the primary quality challenge; 5.5mm retraction at 45mm/s is the tuned baseline but requires ongoing attention
- 8-bit board speed ceiling — max volumetric throughput ~9mm³/s, prints run at 40–60mm/s
- ATmega1284P USB bootloader flash is permanently broken — Creality removed the auto-reset capacitor; any future firmware flashing requires a USBASP ISP programmer (~$5) connected to the ICSP header
- Pi Zero 2W RAM pressure — 512MB total; Mainsail + Moonraker + Klipper sit at 350–400MB under load; no camera stream, no swap bloat
- Input shaping unreliable on Pi Zero 2W — ADXL345 sample rate insufficient at this CPU; manual ringing tower method is the recommended calibration path
- OctoPrint 1.11.x global API key deprecated for write operations — user-specific key in `~/.config/djinn/printers.env` is the workaround (already implemented)

### Best Use Case

Personal projects, display pieces, fine surface quality work (0.12–0.16mm layers, ironing, high wall count), PETG profile iteration. The detail machine — use when quality matters more than time. Never route commissions to Penelope.

---

## Penelope — 8-bit Board Deep Dive

### What the ATmega1284P Limits Right Now

| Constraint | Impact |
|---|---|
| Max volumetric speed ~9mm³/s | Hard cap on throughput — can't push high-flow nozzles or fast infill speeds |
| Speed ceiling 40–60mm/s outer walls | Prints take ~2–3× longer than Calliope equivalent |
| No reliable input shaping via ADXL345 | Can tune resonance manually (ringing tower), but no automated shaper freq detection |
| No pressure advance in Marlin 1.1.6 | Solved — Klipper on Pi Zero 2W handles PA via the host; ATmega only executes movement |
| USB flash broken (no reset cap) | ISP programmer required for any future MCU firmware update |

> **Important clarification:** Klipper running on the Pi Zero 2W as host already gives Penelope pressure advance and bed mesh compensation despite the 8-bit MCU. The ATmega just executes motion commands; all the smart stuff runs on the Pi. This is the correct architecture and is already implemented.

### What a 32-bit Board Unlocks

A drop-in 32-bit board (Creality 4.2.7 with STM32F103, ~$30–45) would unlock:

- Reliable ADXL345 input shaping — USB serial fast enough for resonance testing; proper automated shaper frequencies instead of manual ringing towers
- Higher step rates — faster travel, less stuttering on complex gcode segments
- Silent TMC2208/2209 drivers built in (4.2.7) — significantly quieter operation vs. current A4988 steppers
- Direct USB DFU flashing — no ISP programmer needed for future firmware updates
- Better stepper microstepping — 256 microsteps vs. 16, smoother motion at low speeds

### Upgrade Priority Stack (Best ROI per Dollar)

1. **Hotend + extruder (highest ROI, ~$25–50):** A Sprite-style direct drive or even a BMG/Orbiter clone + Dragon/Rapido hotend eliminates Bowden stringing entirely, brings retraction down to 0.5–1mm like Calliope, and opens TPU. This is the single biggest quality improvement available. If Penelope stays PETG-primary, this is the right first spend.

2. **32-bit board — 4.2.7 (~$35–45):** Get silent drivers + reliable input shaping + easier firmware management. Most valuable if you want to push speeds or run resonance calibration properly. Not required if Penelope stays slow/quality-focused.

3. **All-metal hotend upgrade (~$15–25):** If staying Bowden, a Micro Swiss all-metal or similar removes the PTFE from the heat zone, enabling higher-temp materials (ASA, ABS) reliably. Lower ROI than direct drive conversion but cheap.

4. **Linear rails (X/Y, ~$40–60):** Improves dimensional accuracy and reduces backlash on detail prints. High-effort mod (requires reprinting/remounting carriages), justified only after hotend and board are done.

### Board Swap vs. Workhorse Strategy

**Verdict: Start with hotend/extruder, defer board swap.**

Penelope's current role is detail/personal/PETG. The 8-bit board isn't the bottleneck for that role — the Bowden extruder is. A direct drive conversion gives you better print quality immediately and costs less. The board swap makes sense only if you want to push speeds or need reliable automated input shaping, which Penelope's current role doesn't demand. Run Penelope as a quality-focused Bowden machine until the direct drive mod is done, then reassess whether the 4.2.7 board is worth the additional step.

---

---

## The Sisters — Bambu Fleet (Incoming)

> All sisters run Bambu Studio on Typhon (Windows). Same slicer family as Iris.

| | **Clotho** | **Lachesis** | **Atropos** |
|---|---|---|---|
| **Model** | Bambu P1S + AMS | Bambu P1S + AMS | TBD |
| **Role** | Fast enclosed production, multi-color at scale | Fast enclosed production, multi-color at scale | TBD — name reserved |
| **Slicer** | Bambu Studio (Typhon) | Bambu Studio (Typhon) | Bambu Studio (Typhon) |
| **Status** | Planned | Planned | Incoming |

**Name origin:** The three Fates (Moirai) — Clotho spins the thread, Lachesis measures it, Atropos cuts it. Filament as thread. Chosen to complete the mythological fleet naming convention.

---

## ⚑ Expansion Reference — Bambu Lab P1S + AMS

*Clotho and Lachesis confirmed as P1S + AMS. Atropos model TBD.*

### Capability Summary

- **Build volume:** 256×256×256 mm
- **Max nozzle temp:** 300°C
- **Max bed temp:** 100°C
- **Enclosure:** Yes — fully enclosed with active chamber temperature regulation fan and activated carbon HEPA filter
- **Max chamber temp:** Passive (bed-driven, not independently controlled) — chamber rises with bed temp; no precision thermostat
- **Speed:** 500mm/s max toolhead, 20,000 mm/s²
- **Multi-material:** AMS (Automatic Material System) — 4 spools per unit, up to 4 AMS units daisy-chained for 16 colors
- **Materials (ideal):** PLA, PETG, TPU, ABS, ASA, PVA, PET
- **Materials (capable with upgrades):** PA, PC — require hardened nozzle
- **CF/GF blends:** Not recommended on stock hardware — hardened 0.6mm nozzle + extruder gear upgrade required

### AMS Reliability & Failure Modes

The AMS is the P1S's most powerful feature and its most common complaint source:

- **TPU in AMS is poorly supported** — flexible filaments jam in the AMS buffer and filament path; most users run TPU bypassing the AMS entirely (single spool direct)
- **Filament sensor failures** — the AMS filament sensor is a high-frequency failure part; community reports sensor replacement as a common fix for feeding failures
- **Heat creep clogging** — the enclosed chamber retains heat; PLA in the AMS hub above the chamber can soften and jam, especially in hot environments. Vented risers are a popular community mod.
- **AMS feeding failures during multi-color** — PTFE path resistance and buffer tension issues cause mid-print jams on long multi-color jobs; third-party filaments sometimes more prone than Bambu house brand

### Closed Ecosystem Constraints

This is the most significant fleet consideration:

- **Bambu Studio / Bambu Cloud dependency** — the full feature set (AMS color management, timelapse, remote monitoring, push-to-print) requires Bambu account and cloud connectivity. LAN-only mode exists but loses features.
- **No native Klipper** — P1S runs proprietary firmware; the community has partial Klipper ports but it's not a supported or stable path. This means Djinn's Moonraker/OctoPrint pipeline **cannot natively integrate the P1S** without significant custom work.
- **Walled garden slicer** — Bambu Studio is required for full AMS color workflow; OrcaSlicer has community P1S support but loses some AMS-specific features. Standard gcode from third-party slicers is accepted but with limited AMS coordination.
- **Proprietary communication protocol** — Bambu uses MQTT over LAN; the community has reverse-engineered it (bambu-farm, etc.), but any Djinn integration would require maintaining a custom API bridge rather than the standard Moonraker REST that Calliope, Nemesis, and Penelope use.

### Fleet Integration Assessment

Two P1S units would add enclosed ABS/ASA production capacity and true multi-color production scale, but the closed ecosystem creates a split-pipeline problem. Every current Djinn machine (Calliope, Nemesis, Penelope, Iris) runs Moonraker — one API, one CLI surface, one pipeline. Adding P1S introduces a second API paradigm, separate slicer workflows, and cloud dependency. Worth flagging before any purchase decision.

---

*— Claude + Marcus, 2026-07-07*
