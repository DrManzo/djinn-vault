---
title: Support Settings — Djinn Fleet
agent: Marcus
date: 2026-07-07
tags: [djinn, printer, supports, settings, iris, nemesis, calliope, penelope]
related: [[PRINT-PROFILES]] | [[MACHINE-ROLES]]
---

# Support Settings — Djinn Fleet

Last updated: 2026-07-07  
Scope: All 4 active machines — Iris, Nemesis, Calliope, Penelope

---

## The Core Strategy

**The best support is one that doesn't bond to the part.** Every machine in the fleet has a different tool available:

| Machine | Best Support Strategy | Why |
|---|---|---|
| **Iris** (AD5X) | PLA interface layers via IFS (T2/T3) + PETG/PLA body | Different materials = near-zero adhesion at interface |
| **Nemesis** (AD5M Pro) | Dense interface, low temp, max Z-gap | Single material — optimize gap and density to minimize bonding |
| **Calliope** (E3V3+) | Dense interface, low temp, max Z-gap | Same as Nemesis — single material PLA workhorse |
| **Penelope** (E3 Pro) | Dense interface, low temp, max Z-gap + PETG-aware settings | Bowden adds stringing risk on supports — managed via retraction |

---

## Iris — FlashForge AD5X (Multi-Material Support Strategy)

### Why Iris Has the Fleet's Best Support Capability

Iris's IFS system can assign different filaments to different roles. Assigning PLA as the support interface material while printing the part body in PETG (or vice versa) creates a **dissimilar-material interface** — PLA and PETG don't bond well at contact temperatures, so supports pop off with minimal force and leave a clean surface.

This is the same principle used by water-soluble PVA supports, but achievable with standard materials already on-hand.

### Material Assignment in Bambu Studio / OrcaSlicer (Iris)

```
T1 = Part body material (PETG or PLA — whichever is the print material)
T2 = Support interface material (PLA if body is PETG; PETG if body is PLA)
T3 = Support body material (same as T1, or match T2 for full dissimilar supports)
```

**Recommended assignment for PETG parts:**
- Body: T1 = PETG
- Support interface: T2 = PLA (210°C, 55°C bed)
- Support body: T3 = PLA (same as interface — reduces filament swaps)

**Recommended assignment for PLA parts:**
- Body: T1 = PLA
- Support interface: T2 = PETG (240°C, 70°C bed)
- Support body: T3 = PLA (reduces swaps, PETG interface is sufficient)

### Support Settings — Iris (OrcaSlicer / Bambu Studio)

| Setting | Value | Notes |
|---|---|---|
| Support type | Normal (not tree for interface layer work) | Tree supports are harder to control at interface |
| Support threshold angle | 40° | More aggressive than default; IFS handles cleanup |
| Support top Z distance | 0.15mm | Reduced from default 0.2mm — dissimilar materials allow this |
| Support bottom Z distance | 0.15mm | |
| Support interface layers (top) | 3 | 3 layers of PLA interface on top of supports |
| Support interface layers (bottom) | 2 | Fewer needed on bottom |
| Interface pattern | Rectilinear | Maximizes contact area; breaks cleanly due to material mismatch |
| Interface line width | 0.4mm | Standard |
| Interface spacing | 0.2mm | Dense — relies on material mismatch not gap for release |
| Support body density | 10–15% | Sparse body saves material; interface is where quality matters |
| Support body pattern | Zigzag | Fast, easy to break |
| Support speed | 150 mm/s | |
| Support interface speed | 80 mm/s | Slow down on interface for adhesion accuracy |
| Support fan speed | 100% | Full cooling on PLA interface layers |

### Iris Support — Key Rules

1. **Always assign support interface to the opposite material from the part body.** PLA part → PETG interface. PETG part → PLA interface. This is non-negotiable for clean removal.
2. **In Bambu Studio:** go to `Filament` tab → assign support/interface extruder to T2 separately from object extruder T1.
3. **In OrcaSlicer with Iris:** Use "Support" filament assignment in the multi-material panel. Set "Support interface filament" to the alternate material slot.
4. **Purge volume between T1↔T2 transitions:** Keep at ~60–80mm³ — PLA/PETG are adjacent enough that full purge isn't needed. Bambufy will route excess into infill/supports automatically.
5. **Enclosure note:** Iris has a DIY enclosure (passive, no active filtration). For PLA interfaces on PETG parts, the enclosure helps PETG body but may slightly over-retain heat for PLA interface layers. If PLA interface is stringing, crack the enclosure door 2–3cm during the print.

---

## Nemesis — FlashForge AD5M Pro (Single-Material Support)

### Strategy

Nemesis is single-material — no dissimilar interface trick. The goal is maximum Z-gap and minimum interface density to reduce adhesion while keeping the support structurally sound enough to not collapse.

Nemesis's enclosed chamber is an advantage: consistent temperature = consistent support behavior. No warping mid-print that shifts support contact.

### Support Settings — Nemesis (OrcaSlicer)

#### PLA Supports (on PLA parts)

| Setting | Value | Notes |
|---|---|---|
| Support type | Tree (auto) | Best for PLA — minimal contact points |
| Threshold angle | 45° | Standard |
| Top Z distance | 0.20mm | Full gap — same material needs air gap |
| Bottom Z distance | 0.20mm | |
| Interface layers (top) | 2 | |
| Interface layers (bottom) | 1 | |
| Interface pattern | Rectilinear | |
| Interface density | 80% | Dense but not solid |
| Interface line width | 0.4mm | |
| Support body density | 10% | Sparse |
| Support body pattern | Zigzag | |
| Support speed | 150 mm/s | |
| Interface speed | 80 mm/s | |
| Fan speed on supports | 100% | Full cooling for clean layers |

#### PETG Supports (on PETG parts)

| Setting | Value | Notes |
|---|---|---|
| Support type | Normal | Tree supports with PETG can flex and fail mid-print |
| Threshold angle | 50° | Less aggressive — PETG supports bond harder, reduce count |
| Top Z distance | 0.25mm | Extra gap — PETG bonds more than PLA |
| Bottom Z distance | 0.20mm | |
| Interface layers (top) | 2 | |
| Interface layers (bottom) | 1 | |
| Interface pattern | Rectilinear | |
| Interface density | 60% | Less dense — relies on Z-gap for release |
| Interface line width | 0.4mm | |
| Support body density | 8% | Even sparser |
| Support speed | 120 mm/s | Slightly slower — PETG stringing risk |
| Interface speed | 60 mm/s | |
| Fan speed on supports | 60% | Don't over-cool PETG — delamination risk |

#### ABS Supports (on ABS parts — Nemesis only, enclosed)

| Setting | Value | Notes |
|---|---|---|
| Support type | Normal | ABS warps — tree supports risk detachment |
| Threshold angle | 50° | |
| Top Z distance | 0.25mm | ABS bonds aggressively at interface |
| Bottom Z distance | 0.25mm | |
| Interface layers (top) | 2 | |
| Interface layers (bottom) | 1 | |
| Interface pattern | Rectilinear | |
| Interface density | 50% | Sparse — ABS to ABS interface will still bond at lower density |
| Support body density | 8% | |
| Support speed | 80 mm/s | Slow down — ABS needs thermal stability |
| Interface speed | 50 mm/s | |
| Fan speed on supports | 0–20% | Minimal fan — ABS warps with cooling |

### Nemesis Support — Key Rules

1. **For PETG and ABS — increase Z-gap before increasing interface sparsity.** More gap = cleaner release. Sparser interface = weaker support.
2. **z_offset SAVE_CONFIG trap:** After any recalibration on Nemesis, z_offset must be written manually to `/opt/config/printer.base.cfg` via SSH. If Z-gap appears wrong after a recalibration, this is why.
3. **Enclosed chamber advantage:** Nemesis supports don't shift mid-print due to drafts. You can run supports closer (lower Z-gap) than you could on an open-frame machine.

---

## Calliope — Creality Ender-3 V3 Plus (Production Support)

### Strategy

Calliope is the production machine — supports must be reliable, fast to print, and clean enough for commission-quality output. PLA is the primary material. Tree supports are preferred for surface quality on organic shapes; normal supports for flat overhangs.

**Fan cap constraint:** `M106 S128` max system-wide (nozzle_mcu UART hardware bug). Support fan speed must not exceed 50% in any profile — all support settings below respect this limit.

### Support Settings — Calliope (OrcaSlicer / Creality Print)

#### PLA Supports (primary)

| Setting | Value | Notes |
|---|---|---|
| Support type | Tree (auto) | Best surface quality for commissions |
| Threshold angle | 45° | |
| Top Z distance | 0.20mm | |
| Bottom Z distance | 0.15mm | |
| Interface layers (top) | 3 | Extra interface for commission-quality surface |
| Interface layers (bottom) | 1 | |
| Interface pattern | Rectilinear | |
| Interface density | 80% | Dense for smooth supported surface |
| Interface line width | 0.42mm | Matches Calliope outer wall line width |
| Support body density | 12% | |
| Support body pattern | Zigzag | Fast |
| Support speed | 150 mm/s | |
| Interface speed | 80 mm/s | |
| **Fan speed — HARD CAP** | **S128 (50%)** | **NEVER exceed — nozzle_mcu dropout risk** |
| Brim on supports | No | Adds cleanup time on commissions |

#### PETG Supports (avoid if possible — route to Penelope)

Calliope is not the preferred machine for PETG. If a commission requires PETG supports, route to Penelope or Nemesis. If Calliope must run PETG supports:

| Setting | Value |
|---|---|
| Threshold angle | 52° | Push high — avoid supports where possible |
| Top Z distance | 0.28mm | Maximum gap |
| Interface density | 50% | |
| Fan speed | S64 (25%) max | Even lower than PLA cap |

### Calliope Support — Key Rules

1. **Fan cap is absolute.** Any profile with M106 S255 at bridge/support infill will cause `nozzle_mcu` dropout. The `djinn-gcode-safety` script caps all M106 to S128 at gcode post-processing. Verify it runs before every commission print.
2. **nozzle_mcu cable status:** As of 2026-07-05, cable replacement is pending (BUG-014). Avoid long PETG support prints until new cable is installed. PLA support prints are lower risk.
3. **Tree supports on large plates:** Calliope's 300×300 bed means support trees can span long distances. If a tree support looks unstable in the slicer preview (thin column, long reach), switch to Normal supports for that job.

---

## Penelope — Creality Ender-3 Pro (Bowden-Aware Support)

### Strategy

Penelope's Bowden path (5.5mm retraction) creates a stringing risk on supports specifically — every time the nozzle travels across a support gap, there's potential for a string. Z-hop and careful retraction settings are critical. PETG is the primary material; supports in PETG on a Bowden machine require extra care.

### Support Settings — Penelope (OrcaSlicer)

#### PETG Supports (primary — Bowden-tuned)

| Setting | Value | Notes |
|---|---|---|
| Support type | Normal | Tree supports with Bowden PETG = stringing nightmare |
| Threshold angle | 52° | Higher threshold — avoid supports where possible |
| Top Z distance | 0.25mm | Extra gap for PETG release |
| Bottom Z distance | 0.20mm | |
| Interface layers (top) | 2 | |
| Interface layers (bottom) | 1 | |
| Interface pattern | Rectilinear | |
| Interface density | 60% | |
| Interface line width | 0.42mm | |
| Support body density | 8% | Sparse — less material = less stringing |
| Support body pattern | Zigzag | |
| Support speed | 40 mm/s | Match Penelope's outer wall speed cap |
| Interface speed | 30 mm/s | Slow — precision on interface matters |
| Fan speed | 50% | PETG cooling balance |
| **Retraction on support travel** | 5.5mm @ 45mm/s | Match Penelope's calibrated Bowden retraction |
| Z-hop on support travel | 0.20mm | Lift over support structures to prevent nozzle drag |
| Combing mode | Within infill | Keep nozzle inside perimeters — reduces travel across gaps |

#### PLA Supports (secondary)

| Setting | Value | Notes |
|---|---|---|
| Support type | Tree (auto) | PLA handles tree supports better than PETG on Bowden |
| Threshold angle | 45° | |
| Top Z distance | 0.20mm | |
| Bottom Z distance | 0.15mm | |
| Interface layers (top) | 3 | Penelope is the detail machine — extra interface |
| Interface layers (bottom) | 1 | |
| Interface pattern | Rectilinear | |
| Interface density | 80% | |
| Support speed | 50 mm/s | |
| Interface speed | 35 mm/s | |
| Fan speed | 100% | Full cooling — PLA on Penelope benefits from max fan |
| Retraction | 5.5mm @ 45mm/s | Same Bowden retraction |
| Z-hop | 0.15mm | |

### Penelope Support — Key Rules

1. **Never use Tree supports with PETG on Penelope.** The long travel paths between tree branches cross open air — every crossing is a potential string with 5.5mm Bowden retraction. Normal supports only for PETG.
2. **If support surfaces are rough after removal:** Increase top Z distance by 0.05mm increments. Penelope's Bowden can over-extrude slightly at support interface transitions.
3. **Combing is your friend.** Setting combing to "Within Infill" keeps the nozzle inside perimeters during support travel. This is the single most impactful setting for reducing PETG stringing on supports in Bowden machines.
4. **Speed cap:** Penelope's 8-bit board runs at 40–60mm/s max for outer walls. Support speed must not exceed the machine's reliable ceiling. 40mm/s support / 30mm/s interface is conservative and correct.

---

## Quick-Reference: Support Settings by Machine

| Setting | Iris (PETG+PLA interface) | Nemesis PLA | Nemesis PETG | Calliope PLA | Penelope PETG |
|---|---|---|---|---|---|
| Support type | Normal | Tree | Normal | Tree | Normal |
| Threshold angle | 40° | 45° | 50° | 45° | 52° |
| Top Z distance | 0.15mm | 0.20mm | 0.25mm | 0.20mm | 0.25mm |
| Interface layers (top) | 3 | 2 | 2 | 3 | 2 |
| Interface density | 0.2mm spacing | 80% | 60% | 80% | 60% |
| Interface speed | 80 mm/s | 80 mm/s | 60 mm/s | 80 mm/s | 30 mm/s |
| Support speed | 150 mm/s | 150 mm/s | 120 mm/s | 150 mm/s | 40 mm/s |
| Fan speed | 100% | 100% | 60% | **S128 max** | 50% |
| Interface material | PLA (T2) | same | same | same | same |

---

## Why PLA-as-Interface Works (The Physics)

PLA and PETG have different surface energies and crystalline structures. When a PLA interface layer is deposited on top of a PETG support body (or vice versa), the two materials cool and solidify with very low inter-layer adhesion — they don't chemically bond the way same-material layers do. The result is a support that:

- Prints reliably (PLA and PETG are both stable at standard temps)
- Holds the overhanging geometry in place during printing
- Releases cleanly with finger pressure or light pliers after the print
- Leaves a smooth surface on the part face — comparable to PVA supports without the water-soluble overhead

This is why Iris should be the default machine for any print where support surface quality matters.

---

*— Marcus (Perplexity), 2026-07-07*  
*Iris enclosure: DIY, passive (no active filtration) — confirmed 2026-07-07*
