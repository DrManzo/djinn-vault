---
title: PLAN — Penelope Integration (Ender 3 Pro)
agent: Claude
date: 2026-06-20
tags: [djinn, plan, printer, penelope, architecture]
related: [[SYSTEM-STATE]] | [[INFRASTRUCTURE]] | [[PRINT-PROFILES]] | [[CALLIOPE-MANUAL]]
---

# PLAN — Penelope Integration (Ender 3 Pro)

**Date:** 2026-06-20
**Status:** SPEC — awaiting Javier decision on hosting + board confirmation

---

## What We Found

### Penelope (Ender 3 Pro)
| Field | Value |
|-------|-------|
| Connection | USB to Salomon — `/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0` → `/dev/ttyUSB0` |
| USB chip | CH340 (1a86:7523) — used on both 8-bit and 32-bit Creality boards |
| Firmware (current) | Stock Marlin — serial-only, no network API |
| Build volume | 220×220×250mm |
| Mainboard | **UNKNOWN — Javier must confirm** (see §Decision 1) |
| Klipper on Salomon | Not installed |

### Calliope (Ender-3 V3 Plus) — pre-existing state
| Field | Value |
|-------|-------|
| Actual IP | **192.168.1.114** (not .113 as documented) |
| Hostname | `Ender-3.lan` |
| Firmware | Klipper + Moonraker — fully operational |
| Djinn macros | Installed (`djinn_failure_park`, `djinn_resume_print`) |
| Scripts at .113 | **15 scripts still point to old IP** — see §Pre-existing Bug |

---

## Decision Required from Javier

### Decision 1 — Penelope's Mainboard (MUST ANSWER FIRST)

The CH340 chip tells us nothing about the CPU. Two very different flash paths:

| Board | CPU | How to identify | Klipper flash method |
|-------|-----|----------------|---------------------|
| 4.2.2 "silent" | STM32F103 | "4.2.2" silkscreened on PCB | DFU via USB (no jumper needed on most) |
| 4.2.7 "silent" | STM32F103 | "4.2.7" silkscreened on PCB | DFU via USB |
| Old V1 (pre-2020) | ATmega1284P | Blue Melzi-style board | avrdude via CH340 |

**Action: look at the mainboard label or run `! sudo python3 -c "import serial,time; s=serial.Serial('/dev/ttyUSB0',115200,timeout=3); time.sleep(2); s.write(b'M115\n'); time.sleep(2); print(s.read(1024).decode(errors='replace'))"` to get Marlin's firmware string.**

The M115 response will include `FIRMWARE_INFO` with the board name.

### Decision 2 — How Should Penelope Be Hosted?

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **A: Klipper on Salomon via USB** | Same pipeline as Calliope, no new hardware, Moonraker at port 7126 | Penelope physically tethered to Salomon, 2nd Moonraker instance to manage | **Recommended** |
| **B: Dedicated Raspberry Pi** | Penelope self-contained, can move | Costs money, more hardware to manage | Good if you want independence |
| **C: Manual/SD alongside Calliope** | No install, zero setup | Not in queue, no Djinn automation | Stop-gap only |

**Recommendation: Option A.** Salomon is always on, Penelope is already plugged in, and a second Moonraker instance at `:7126` is a well-trodden pattern. All the Djinn tooling is already on Salomon.

### Decision 3 — Job Routing Logic

Calliope: 300×300×330mm. Penelope: 220×220×250mm.

| Option | Behavior |
|--------|---------|
| **Manual per-job** | `slice N --printer penelope` — Javier picks explicitly every time |
| **Auto-route by fit** | If model ≤ 220×220×250 → offer both; if larger → Calliope only |
| **Manual default, auto-warn** | Default routes to Calliope; system warns "Penelope can also handle this" for small jobs |

**Recommendation: Manual default with auto-warn.** Keeps Javier in control (consistent with existing print-orientation rule) while surfacing Penelope as an option for small jobs.

---

## Pre-existing Bug: Calliope IP Drift (.113 → .114)

**This is separate from the Penelope integration and should be fixed first.**

Calliope's actual IP is 192.168.1.114. Fifteen scripts still point to 192.168.1.113:

```
djinn-agent-doctor          → 192.168.1.113
djinn-ctx-router            → 192.168.1.113
djinn-force-cancel          → 192.168.1.113
djinn-deny-print            → 192.168.1.113
djinn-discord-gateway       → 192.168.1.113
djinn-printer-files-backup  → 192.168.1.113 (this is Typhon SSH, not Moonraker — separate)
djinn-print-recover         → 192.168.1.113
djinn-queue-reset           → uses $DJINN_MOONRAKER (env var) with 113 default
djinn-terp-tribe-track      → 192.168.1.113
djinn-print-safety          → 192.168.1.113 (via $DJINN_MOONRAKER env)
djinn-print-tracer          → 192.168.1.113
djinn-telegram-gateway      → 192.168.1.113
djinn-setup-channels        → 192.168.1.113
djinn-model-fetch           → 192.168.1.113
djinn-print-monitor         → 192.168.1.113
```

Scripts already on .114 (recently updated): `djinn-confirm-print`, `djinn-print-monitor-v2`, `djinn-print-track`, `djinn-webcam-monitor`.

**Fix:** Set `DJINN_MOONRAKER_CALLIOPE=http://192.168.1.114:7125` in `~/.config/djinn/printers.env` and update all scripts to source it instead of hardcoding. This also sets up the env-var pattern needed for multi-printer support.

---

## Full Integration Scope (Post-Decision)

### Phase 0 — Pre-work (do first, independent of Penelope)
- [ ] Fix Calliope IP across 15 scripts (replace 192.168.1.113 with 192.168.1.114)
- [ ] Create `~/.config/djinn/printers.env` with DJINN_MOONRAKER_CALLIOPE and (eventually) DJINN_MOONRAKER_PENELOPE
- [ ] Update vault docs: SYSTEM-STATE.md, INFRASTRUCTURE.md, CALLIOPE-MANUAL.md with correct IP

### Phase 1 — Identify & Flash Penelope (once Decision 1 answered)
- [ ] Run M115 to get board string
- [ ] Install Klipper on Salomon: `git clone https://github.com/Klipper3d/klipper ~/klipper`
- [ ] Compile firmware for Penelope's board (config depends on board type)
- [ ] Flash via USB (board-dependent method)
- [ ] Install Moonraker as second instance at port 7126 with its own data dir (`~/printer_data_penelope/`)
- [ ] Write `printer.cfg` for Penelope (220×220×250, Ender 3 Pro profile)
- [ ] Install Djinn Klipper macros (`djinn_failure_park`, `djinn_resume_print`) in Penelope's printer.cfg

### Phase 2 — CLI Tool Refactor (multi-printer support)
Add `--printer <calliope|penelope>` flag to all print pipeline tools:
- `djinn-print-consult`
- `djinn-model-slice`
- `djinn-confirm-print`
- `djinn-deny-print`
- `djinn-force-cancel`
- `djinn-print-monitor` / `djinn-print-monitor-v2`
- `djinn-print-track`
- `djinn-gcode-safety` (fan cap S128 — verify if Penelope has same constraint)
- `djinn-webcam-monitor`

Queue schema: add `"printer": "calliope"` field to every job entry in `~/.local/share/djinn/print-queue.json`.

### Phase 3 — Bot Commands
- Discord/Telegram: `slice N --printer penelope` syntax
- `djinn-print-consult`: add build-fit check vs. 220×220×250, warn if job exceeds Penelope's volume
- Auto-warn logic in consult report: "Penelope can also handle this (fits in 220×220×250)"

### Phase 4 — Vault Docs
- [ ] Create `~/Obsidian/djinn/printer/PENELOPE-MANUAL.md`
- [ ] Create `~/Obsidian/djinn/printer/PENELOPE-PROFILES.md` (same profiles, Ender 3 Pro defaults)
- [ ] Add Penelope to PRINT-PROFILES.md header (dual-printer section)
- [ ] Update SYSTEM-STATE.md printer table
- [ ] Update INFRASTRUCTURE.md topology section
- [ ] Update AGENTS.md print workflow section

---

## Penelope Hardware Spec (to document once board is confirmed)

| Field | Value |
|-------|-------|
| Name | Penelope |
| Machine | Ender 3 Pro |
| Build volume | 220×220×250mm |
| Nozzle | 0.4mm |
| Extruder | Bowden (stock) |
| Heated bed | Yes |
| Auto-leveling | CR Touch / BLTouch IF installed — **confirm with Javier** |
| Mainboard | **TBD — read M115** |
| USB device | `/dev/ttyUSB0` on Salomon |
| Moonraker (target) | `http://localhost:7126` (Klipper on Salomon) |
| Fan constraint | TBD — check nozzle_mcu presence (Ender 3 Pro is stock single-MCU, likely no S128 cap) |

---

## Recommended First Actions

1. **Javier reads the board label** or runs the M115 command (needs sudo)
2. **Fix Calliope IP first** — isolated, low-risk, unblocks any print pipeline work
3. **Javier decides hosting option** (A/B/C above)
4. Then Phase 1 begins

*— Claude, 2026-06-20*
