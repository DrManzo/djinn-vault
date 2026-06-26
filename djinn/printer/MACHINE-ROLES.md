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
| IP | 192.168.1.XXX (assign DHCP reservation after Saturday) |
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
| IP | 192.168.1.114 (DHCP reserved) |
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
- Material is PETG at high temp

---

## Routing Logic — How Claude Should Decide

```
1. SIZE CHECK (hard constraint):
   - Model > 220mm in any axis → CALLIOPE only
   - Model ≤ 220×220×250mm → both eligible, continue

2. JOB TYPE:
   - Commission or deadline → CALLIOPE
   - Personal / experimental / detail → PENELOPE
   - Ambiguous → ask Javier

3. MATERIAL:
   - PETG → PENELOPE preferred
   - PLA, standard → CALLIOPE preferred
   - Experimental → PENELOPE only

4. QUALITY TARGET:
   - Layer height ≤ 0.16mm, ironing, detail mode → PENELOPE
   - Standard / production profile → CALLIOPE

5. QUEUE STATE:
   - Calliope printing commission → PENELOPE for personal jobs
   - Both idle → use above rules

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
