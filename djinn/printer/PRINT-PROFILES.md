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

## Slicer Note (2026-06-08)
**Slicer:** Creality Print — handles all slicing (interactive and CLI pipeline). OrcaSlicer and PrusaSlicer are archived.

ALL gcode passes through `djinn-gcode-safety` which caps M106 fan speed to S128 max — hardware constraint on Calliope's nozzle_mcu UART.

*— Updated 2026-06-08 by Claude*

---

# Print Profiles — Penelope (Ender 3 Pro)

**Build volume: 220×220×250mm** — 36% smaller than Calliope. Check fit before routing a job here.
**Control:** OctoPrint on Salomon at `http://localhost:5001` — `djinn-penelope upload <file>` then `djinn-penelope print <file>`
**Fan constraint:** None (stock 8-bit board, no nozzle_mcu UART issue)

Same profile structure as Calliope. Javier overrides any value.

## proto

| Setting | Value |
|---|---|
| Infill | 8% gyroid |
| Layer height | 0.28mm |
| Walls | 2 |
| Supports | Only if >60° |
| Brim | yes (3mm) |
| Bed temp | 55°C |
| Hotend | 210°C |

## standard

| Setting | Value |
|---|---|
| Infill | 15% grid |
| Layer height | 0.20mm |
| Walls | 3 |
| Supports | If >45° overhang |
| Brim | yes (5mm) |
| Bed temp | 60°C |
| Hotend | 210°C |

## production

| Setting | Value |
|---|---|
| Infill | 25% gyroid |
| Layer height | 0.20mm |
| Walls | 4 |
| Supports | If >45° overhang |
| Brim | yes (8mm) |
| Bed temp | 65°C |
| Hotend | 210°C |

## Routing Note
If a model exceeds 220×220×250mm on any axis → route to Calliope only.
If a model fits within 220×220×250mm → either printer works; default to Calliope unless specified.

*— Added 2026-06-20 by Claude*
