---
job_id: 2
date: 2026-05-30
source: https://cdn.discordapp.com/attachments/1507882513891065876/1510327301026615336/cup_engraved_FINAL.stl?ex=6a1c6969&is=6a1b17e9&hm=a1190ccdd8ec42f9245c87fc9b1e20d79b4005ede9d980d187906e986cea8d37&
model: /home/drmanzo/Obsidian/djinn/printer/library/10327301026615336_cup_engraved_FINAL_stl/model.stl
gcode: /home/drmanzo/Obsidian/djinn/printer/queue/model_job2.gcode
status: complete
profile: production
supports: False
infill: 15%
brim: True
layer_height: 0.2mm
walls: 4
---

# Print Job #2 — model

## Slice Report

*Calliope Job #2 — Sliced & Ready*
File: `model.stl`
Integrity: 🔒 `4db8b0f30ba6e47351b1f03f77a1b8d3…`
Dims: 66.0x108.2x107.3mm | Volume: 248.85cm³

*Print time:* 6h 27m 15s
*Filament:* 41101mm / 122.6g
*Hotend:* 220°C  *Bed:* 55°C
*Layer height:* 0.2mm

*Settings used:*
  Profile: *production*  Supports: no
  Infill: 15%
  Brim: YES (5mm)
  Walls: 4
  Layer: 0.2mm
  Raft: no

*Commission estimate (qty 1):*
  Material:  $2.97
  Machine:   $1.31
  Labor:     $6.67
  Design:    $0.00
  Test run:  $2.14  ← Test run 50% of print cost (single/small run qty 1–6) — $2.14.
  ─────────────────
  Cost:      $13.08  (÷ 0.60)
  💰 Ask:    $21.81
  Design found in library (BambuLab-Filament-Display-Model-Fake-Vase-Mode_stls.zip) — not charged.

Reply `confirm 2` to send to Calliope.
Reply `deny 2` to remove from queue.
Calliope will NOT start automatically.

## Progress Log

| Time | Event |
|------|-------|
| 2026-05-30 17:02 UTC | Sliced — waiting for confirm |

| 2026-05-30 17:03 UTC | Print started |
| 2026-05-30 17:47 UTC | 10.1% complete |
| 2026-05-30 18:12 UTC | 20.0% complete |
| 2026-05-30 18:35 UTC | 30.1% complete |
| 2026-05-30 18:59 UTC | 40.1% complete |
| 2026-05-30 19:27 UTC | 50.0% complete |
| 2026-05-30 19:59 UTC | 60.0% complete |
| 2026-05-30 20:32 UTC | 70.1% complete |
| 2026-05-30 21:04 UTC | 80.0% complete |
| 2026-05-30 21:35 UTC | 90.0% complete |
| 2026-05-30 22:18 UTC | Completed in 5h 6m |

## Post-Print Notes

**Engraving quality:**
- `T` in "Terp" — messy at the top crossbar and right side of the stem (viewed left to right). Boolean depth likely insufficient at that letter; surface curvature of the cup means the right edge of T sits shallower than center.
- `e` in "Tribe" — curve incomplete on the left-hand side. The curved counter of the 'e' didn't cut cleanly, likely a manifold issue with that letter component or insufficient intersection depth at that X position.

**Support:**
- Under the tank (base overhang on sides) — 0.45–0.5mm overhang printed rough on the underside. **Supports required here on next print.** No other areas need support. Everything else came out clean.

**Action items for reprint:**
- [ ] Enable supports, targeted at underside of tank only
- [ ] Increase engrave depth by ~0.5mm at edges to compensate for cup curvature (especially T and curved letters)
- [ ] Verify 'e' component boolean succeeded during slicing prep
