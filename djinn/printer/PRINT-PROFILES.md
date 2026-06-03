# Print Profiles — Calliope (Ender-3 V3 Plus)

Profiles are suggestions, not law. Javier overrides any value at slice time.

---

## proto — Prototype / First-Look

**Purpose:** See if it fits, check the shape, test the design. Not a finished part.
**Priority:** Speed, material efficiency, easy cleanup.

| Setting | Value | Why |
|---|---|---|
| Infill | 8% | Just enough for structure |
| Infill pattern | Gyroid | Fast, omnidirectional, easy to break out |
| Layer height | 0.28mm | Faster, surface finish doesn't matter yet |
| Supports | Only if >60° | Aggressive threshold — reduce cleanup work |
| Brim | yes (3mm) | Adhesion without bulk |
| Raft | no | Unless piece is very small or unstable |
| Walls | 2 | Minimum shell |
| Bed temp | 55°C | Standard PLA |
| Hotend | 210°C | Standard PLA |

**Result:** Quick, cheap, easy to post-process. Expect rough surface. That's fine.

---

## standard — Working Part / Moderate Strength

**Purpose:** Functional part that needs to hold up. Not final production.

| Setting | Value | Why |
|---|---|---|
| Infill | 15% | Good strength/weight ratio |
| Infill pattern | Grid | Predictable, strong |
| Layer height | 0.20mm | Good balance |
| Supports | If >45° overhang | Standard threshold |
| Brim | yes (5mm) | Solid adhesion |
| Raft | no | |
| Walls | 3 | Solid shell |
| Bed temp | 60°C | Better adhesion for functional parts |
| Hotend | 210°C | |

---

## production — Final Piece / Full Strength

**Purpose:** Commission-ready or final-use part.

| Setting | Value | Why |
|---|---|---|
| Infill | 25% | High strength |
| Infill pattern | Gyroid | Best strength per gram |
| Layer height | 0.20mm | Clean finish |
| Supports | If >45° overhang | |
| Brim | yes (8mm) | Maximum adhesion |
| Raft | no | |
| Walls | 4 | Maximum shell thickness |
| Bed temp | 65°C | Best first-layer adhesion |
| Hotend | 210°C | |

---

## custom

Javier specifies everything. The slicer uses exactly what was said.
No defaults applied. No substitutions.

---

---

## Slicer Note (2026-06-03)

**Interactive slicing:** OrcaSlicer 2.3.2 — replaces PrusaSlicer for manual jobs.
**CLI pipeline** (`djinn-model-slice`, `djinn-model-combine`): PrusaSlicer — stays, unchanged.

Profile values above apply to both. Fan cap (`bridge_fan_speed=0` in OrcaSlicer, `50` in PrusaSlicer INI) is non-negotiable — hardware constraint on Calliope's Sprite Pro extruder.

*— Updated 2026-06-03 by Claude*
