# Djinn 3D Print Pipeline — Instruction Manual

**Printer:** Calliope (Ender-3 V3 Plus) at `192.168.1.113`
**Interface:** Discord `#3d-printing` or Telegram
**Agent:** Djinn (OgDjinn#9859) — powered by Salomon / deepseek-r1:7b
**Last updated:** 2026-05-30

---

## Overview

The pipeline is fully automated from file drop to print start. You drop a model file, Djinn analyzes it, asks for your settings, slices it, shows you the result, and waits for your go-ahead before touching the printer. Nothing starts without `confirm N`.

```
DROP FILE → ANALYZE → CONSULT REPORT → slice N → SLICE REPORT → confirm N → PRINT
                                                                           ↓
                                                              feedback N → NOTES FOR NEXT TIME
```

---

## Step 1 — Drop the File

Drop a `.stl` or `.3mf` file directly into `#3d-printing`.

Djinn picks it up within 20 seconds and:
- Downloads and analyzes the mesh (dimensions, volume, overhangs, bed fit)
- Generates 3 renders: front view, side view, overhang map (red = needs support)
- Sends all three images to Discord and Telegram
- Runs a dry-run slice to get real time and filament estimates (PrusaSlicer CLI)
- Posts the full consult report

**Supported sources:** Discord attachment, direct `.stl`/`.3mf` URL, Printables, Thingiverse URL

---

## Step 2 — Read the Consult Report

The report contains everything you need to make a decision:

```
🔍 Print Consult — Job #1
File: my_model.stl
Size: 66.0x108.2x107.3mm  │  Volume: 248.85cm³

─── Prior print notes ────────────────────   ← shows if model was printed before
  [2026-05-28] production / pla / balanced
    → "slight warping on bottom-left corner, increase brim"

─── My read ──────────────────────────────
  Overhangs at 11.7% — supports worth considering. Check the angles.
  Recommend standard: working part — solid, not final

─── Profiles ─────────────────────────────
  P · proto       infill= 8% gyroid  layer=0.28mm  walls=2  ~3h 39m  ~60g
  S · standard    infill=15% grid    layer=0.20mm  walls=3  ~6h 05m  ~110g ◄
  P · production  infill=25% gyroid  layer=0.20mm  walls=4  ~9h 26m  ~167g
  D · custom      you specify everything

─── Still need from you ──────────────────
• Profile   →  A (proto) / B (standard) / C (production) / D (custom)
• Supports  →  yes/no
• Brim      →  yes/no
• Material  →  pla / petg / abs / tpu
• Priority  →  speed / balanced / accuracy
```

**Profiles:**
| Profile | Use case | Infill | Layer | Walls | Speed |
|---------|----------|--------|-------|-------|-------|
| proto | Fast look, fit check, sample | 8% gyroid | 0.28mm | 2 | Fast |
| standard | Working part, solid daily use | 15% grid | 0.20mm | 3 | Normal |
| production | Commission-ready, max strength | 25% gyroid | 0.20mm | 4 | Normal |
| custom | Full control | you set | you set | you set | you set |

**Materials:**
| Material | Bed | Hotend | Notes |
|----------|-----|--------|-------|
| pla | 55°C | 210°C | Default. Easy, reliable |
| petg | 70°C | 230°C | Stronger, slight stringing |
| abs | 100°C | 240°C | Warp risk, needs enclosure |
| tpu | 45°C | 220°C | Flexible, slow required |

**Priority:**
| Priority | Speed factor | Layer height | Use when |
|----------|-------------|-------------|---------|
| speed | 150% | 0.28mm | Fastest, rougher surface |
| balanced | 100% | 0.20mm | Default |
| accuracy | 60% | 0.12mm | Best surface finish, slowest |

---

## Step 3 — Reply with Settings (slice command)

```
slice N <profile> supports=yes/no brim=yes/no material=pla priority=balanced
```

**Examples:**

```
slice 1 standard supports=no brim=yes material=pla priority=balanced
slice 1 production supports=yes material=petg priority=accuracy
slice 1 proto material=pla priority=speed
slice 1 supports=yes infill=20 brim=yes layer=0.20 material=pla priority=balanced
```

No `/` prefix needed. Reply exactly like the examples in the report.

**What happens:** Djinn slices the model using your exact settings (PrusaSlicer CLI pipeline). Takes 10–120 seconds depending on model size.

---

## Step 4 — Read the Slice Report

After slicing, Djinn sends:
- 2 renders of the sliced model (front + side)
- Support zone render (if supports enabled)
- Full slice report with exact settings, time, filament, temps, commission estimate

```
*Calliope Job #1 — Sliced & Ready*
File: my_model.stl

Print time: 6h 5m
Filament: 48125mm / 110.1g
Hotend: 210°C  Bed: 55°C
Layer height: 0.20mm

Settings used:
  Profile: production   Supports: no
  Infill: 25%
  Brim: YES (8mm)
  Walls: 4
  Material: PLA
  Priority: balanced (speed factor 100%)

Commission estimate (qty 1):
  Material:  $3.47
  Machine:   $1.79
  Labor:     $6.67
  Test run:  $2.63
  ─────────────
  Cost:      $14.56
  💰 Ask:    $24.26
```

Review it. If something looks wrong, reply with a new `slice N` command with different settings — it will re-slice. Nothing has been sent to the printer yet.

---

## Step 5 — Confirm to Print

```
confirm N
```

This is the only command that actually starts the printer. Djinn:
1. Checks Calliope is not already printing
2. Calculates a safe park position from the gcode bounding box
3. Uploads the gcode to Moonraker
4. Starts the print
5. Sets the park position in Klipper (used if print fails)

**Calliope will not start without this command.**

---

## During the Print

Djinn monitors the print and notifies you at:
- Print started
- Every 10% progress (bootstrap mode: every print until 5 successes)
- Every 25% progress (normal mode: after 5 successful prints)
- Pause, error, cancellation, completion

**Check status anytime:**
```
print status
```

---

## Step 6 — After the Print

When the print finishes (or fails), Djinn asks for feedback:

```
feedback N <what you observed>
```

**Examples:**
```
feedback 1 first layer lifted on the front edge, increase brim next time
feedback 1 perfect, no issues
feedback 1 surface was rough on overhangs, try accuracy priority
feedback 1 warping on corners, bed was 55°C, try 60°C for petg next time
```

Notes are stored by file hash — the same model printed again weeks later will show this history in the consult report. This is how the system learns your preferences and gets closer to perfect each run.

---

## Cancellation & Safety

### Cancel a pending job (not yet started)
```
deny N
```
Removes from queue. Blocked if Calliope is currently printing.

### Emergency cancel (live print)
```
force-cancel N "reason" <PIN>
```
Requires your PIN. Moves head to safe park position. Cannot be triggered without PIN.

**Djinn cannot cancel a live print without your PIN.** The only soft override is the physical touchscreen on Calliope.

### Print lock
`deny N` is hard-blocked while printing. The system will reject it and tell you.

### Safe park
Every confirmed print calculates a park position from the gcode bounding box before the job starts. If the print fails, Klipper parks the head clear of the model.

---

## Other Commands

| Command | What it does |
|---------|-------------|
| `queue` | Show all jobs and their status |
| `print status` | Live printer state, temps, progress |
| `quote <description>` | Commission price estimate |
| `quick quote <args>` | Fast quote with known params |
| `feedback N <text>` | Log post-print notes |
| `deny N` | Remove pending job from queue |
| `confirm N` | Start print job N |

---

## Job Statuses

| Status | Meaning |
|--------|---------|
| `needs_settings` | Consult ran, waiting for your `slice N` reply |
| `needs_review` | Consult report sent, awaiting settings confirmation |
| `pending` | Sliced, gcode ready, waiting for `confirm N` |
| `printing` | Active print in progress |
| `complete` | Print finished successfully |
| `cancelled` | Cancelled by user |
| `failed` | Print error detected |

---

## Print Profiles Reference

Defined in `~/Obsidian/djinn/printer/PRINT-PROFILES.md`

**Small decorative parts** (vases, minis, trinkets):
- proto profile + raft + 55°C + 0% infill + no supports

**Functional/structural parts** (holsters, brackets, tools):
- standard or production + supports + 65°C + infill

---

## File Locations

| What | Where |
|------|-------|
| Print queue | `~/.local/share/djinn/print-queue.json` |
| Staged gcode | `~/Obsidian/printer-files/queue/` |
| Model library | `~/Obsidian/printer-files/library/` |
| Print feedback | `~/Obsidian/djinn/printer/feedback/` |
| Renders cache | `~/.local/share/djinn/renders/` |
| Failure log | `~/Obsidian/djinn/printer/failures/FAILURE-LOG.md` |
| Recovery backups | `~/Obsidian/printer-files/recovery/` |
| Print vault notes | `~/Obsidian/djinn/printer/prints/` |
| Slicer profile | `~/.config/djinn/ender3-v3-plus.ini` |

---

## Services

All run as systemd user services on Salomon.

| Service | Role |
|---------|------|
| `djinn-discord-gateway` | Receives commands from Discord, routes to handlers |
| `djinn-discord-watcher` | Watches #3d-printing for STL/3MF attachments |
| `djinn-discord-watch` | Watches for model URLs in messages |
| `djinn-print-monitor` | Tracks print progress, sends notifications |
| `djinn-print-monitor-v2.timer` | Failure detection, runs every 60s |
| `djinn-telegram-gateway` | Telegram notifications |

**Restart a service:**
```bash
systemctl --user restart djinn-discord-gateway.service
```

---

## Troubleshooting

**STL dropped but no response:**
- Check `journalctl --user -u djinn-discord-watcher.service -n 20`
- Watcher polls every 20s — wait up to 30s after drop

**slice command did nothing:**
- Make sure job status is `needs_review` (run `queue`)
- Command format: `slice N <profile> ...` — no extra punctuation

**confirm did nothing:**
- Check Moonraker is reachable: `curl http://192.168.1.113:7125/printer/info`
- Check Calliope isn't already printing: `print status`

**Renders missing from report:**
- Xvfb must be running in the watcher service cgroup — check service status

**Discord sends not landing:**
- All scripts now use direct REST API (not openclaw)
- Check bot token in `~/.openclaw/openclaw.json` is valid

---

*Last updated by Claude — 2026-05-30*
*See `logs/reports/2026-05-30_3dprint-pipeline-overhaul.md` for full change history.*
