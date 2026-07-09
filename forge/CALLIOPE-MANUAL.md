================================================================================
                     CALLIOPE — COMPLETE USER MANUAL
              Djinn 3D Print Pipeline | Ender-3 V3 Plus
================================================================================
Version: 1.0 | Last updated: 2026-06-09 | Maintained by: DrManzo / Claude

> This document is a full standalone handoff. It absorbs PRINTER-MANUAL.md,
> SUPPORT-GUIDE.md, PRINT-PROFILES.md, and the pipeline quick-reference docs.
> A new operator who has never used the system should be able to go from zero
> to confirmed print using only this file.

================================================================================
TABLE OF CONTENTS
================================================================================

  1.  What Is This System?
  2.  Hardware & Infrastructure Reference
  3.  Before You Start — Preflight Checklist
  4.  The Full Print Workflow (Step-by-Step)
      4.1  Step 1 — Drop the File
      4.2  Step 2 — Read the Consult Report
      4.3  Step 3 — Choose Settings (slice command)
      4.4  Step 4 — Read the Slice Report
      4.5  Step 5 — Confirm to Print
      4.6  Step 6 — Monitor the Print
      4.7  Step 7 — Provide Feedback
  5.  Print Profiles — Full Reference
  6.  Materials Reference
  7.  Priority Modes
  8.  Support Settings — Full Guide
      8.1  When to Use Supports
      8.2  The Hollow Part Problem
      8.3  Making Supports Easier to Remove
  9.  The Maker's Mark (TF Anvil Engraving)
  10. Commission Quoting
  11. Job Statuses Reference
  12. Command Reference (All Commands)
  13. File & Directory Reference
  14. Services Reference
  15. Common Workflows (Step-by-Step)
      15.1  New Commission from Scratch
      15.2  Re-Printing a Known Model
      15.3  Quick Prototype / Fit Check
      15.4  Emergency Cancel of a Live Print
      15.5  Recovery After a Print Failure
  16. Troubleshooting (CAUSE + FIX)
  17. Technical Reference
      17.1  Slicer Stack
      17.2  Fan / EMI Hardware Constraint
      17.3  Failure Triage Protocol
      17.4  Service Architecture
      17.5  gcode Safety Layer
  18. FAQ

================================================================================
1. WHAT IS THIS SYSTEM?
================================================================================

Calliope is an Ender-3 V3 Plus 3D printer running Klipper firmware, managed
through a fully automated Discord/Telegram pipeline powered by Djinn — an AI
agent running on Salomon (the home server). The pipeline takes you from raw
model file to physical print in a structured, gated sequence: analyze → slice
→ review → confirm → print.

Nothing touches the printer without your explicit `confirm N` command. The
system is designed so you can manage a full print job from your phone over
Discord or Telegram without ever touching a desktop.

The pipeline handles:
  - Mesh analysis and 3-view renders
  - Automatic profile recommendation with dry-run time/filament estimates
  - Slicing via Creality Print CLI with your exact settings
  - gcode post-processing (fan cap, maker's mark if requested)
  - Moonraker upload and print start
  - Progress monitoring with milestone notifications
  - Feedback logging with per-model history lookup on future jobs
  - Commission pricing (material + machine + labor + test run)

================================================================================
2. HARDWARE & INFRASTRUCTURE REFERENCE
================================================================================

  Printer:          Calliope — Creality Ender-3 V3 Plus
  Printer IP:       192.168.1.113
  Firmware:         Klipper
  Interface layer:  Moonraker (REST API)
  Server:           Salomon (home server hosting all Djinn services)
  Agent:            Djinn (OgDjinn#9859 on Discord)
  Channels:         Discord #3d-printing | Telegram
  Extruder:         Sprite Pro (NOTE: nozzle_mcu board is EMI-sensitive — see §17.2)
  Slicer:           Creality Print (CLI + GUI)

Moonraker health check:
  curl http://192.168.1.113:7125/printer/info

Expected response: JSON with printer state. If this times out, the printer
is offline, Klipper crashed, or the network is down.

================================================================================
3. BEFORE YOU START — PREFLIGHT CHECKLIST
================================================================================

Before dropping a file, verify:

  [ ] Calliope is powered on
  [ ] Bed is clear of previous print material
  [ ] Filament is loaded and not tangled on the spool
  [ ] Moonraker responds: curl http://192.168.1.113:7125/printer/info
  [ ] Djinn services are running (see §14 for service names)
  [ ] No active print in queue: run `queue` in #3d-printing

If Djinn services are not responding:
  systemctl --user restart djinn-discord-gateway.service
  systemctl --user restart djinn-discord-watcher.service

================================================================================
4. THE FULL PRINT WORKFLOW (STEP-BY-STEP)
================================================================================

The pipeline always follows this flow. You cannot skip steps.

  DROP FILE → ANALYZE → CONSULT REPORT → slice N → SLICE REPORT → confirm N → PRINT
                                                                               ↓
                                                                  feedback N → STORED NOTES

------------------------------------------------------------------------
4.1 STEP 1 — DROP THE FILE
------------------------------------------------------------------------

Drop a .stl or .3mf file directly into Discord #3d-printing.

Djinn picks it up within 20 seconds and automatically:
  1. Downloads and analyzes the mesh
     - Dimensions (X × Y × Z mm)
     - Volume (cm³)
     - Overhang percentage and map
     - Bed fit check (300 × 300mm build area)
  2. Generates 3 renders: front view, side view, overhang map
     (red areas on overhang map = overhangs needing support consideration)
  3. Sends all three images to Discord and Telegram
  4. Runs a dry-run slice (Creality Print CLI) for real time and filament
  5. Posts the full consult report (see §4.2)

Supported input types:
  - Discord attachment (.stl or .3mf)
  - Direct .stl/.3mf URL
  - Printables URL (Djinn fetches the file)
  - Thingiverse URL (Djinn fetches the file)

If Djinn does not respond within 30 seconds:
  → Check: journalctl --user -u djinn-discord-watcher.service -n 20
  → The watcher polls every 20s — wait up to 30s total after the drop

------------------------------------------------------------------------
4.2 STEP 2 — READ THE CONSULT REPORT
------------------------------------------------------------------------

The consult report is everything you need to make a go/no-go decision
before committing to a slice. It contains:

  ┌─────────────────────────────────────────────────────────┐
  │ 🔍 Print Consult — Job #1                              │
  │ File: my_model.stl                                      │
  │ Size: 66.0×108.2×107.3mm  │  Volume: 248.85cm³         │
  │                                                         │
  │ ─── Prior print notes ──────────────────────────────   │
  │   [2026-05-28] production / pla / balanced              │
  │   → "slight warping on bottom-left corner, add brim"   │
  │                                                         │
  │ ─── My read ────────────────────────────────────────   │
  │   Overhangs at 11.7% — supports worth considering.     │
  │   Recommend standard: working part, not final.         │
  │                                                         │
  │ ─── Profiles ───────────────────────────────────────   │
  │  P · proto      8% gyroid  0.28mm  walls=2  ~3h 39m    │
  │  S · standard   15% grid   0.20mm  walls=3  ~6h 05m ◄  │
  │  P · production 25% gyroid 0.20mm  walls=4  ~9h 26m    │
  │  D · custom     you specify everything                  │
  │                                                         │
  │ ─── Still need from you ────────────────────────────   │
  │  • Profile  → proto / standard / production / custom   │
  │  • Supports → yes / no                                 │
  │  • Brim     → yes / no                                 │
  │  • Material → pla / petg / abs / tpu                   │
  │  • Priority → speed / balanced / accuracy              │
  └─────────────────────────────────────────────────────────┘

KEY FIELD: Prior print notes
  If this model has been printed before, the report shows the history.
  Read these notes first — they often tell you exactly what to adjust.

KEY FIELD: My read
  Djinn's interpretation of the geometry. Not a command — a recommendation.
  You can override any of it in your slice command.

Job is now in status: needs_review

------------------------------------------------------------------------
4.3 STEP 3 — CHOOSE SETTINGS (slice command)
------------------------------------------------------------------------

FULL FORMAT:
  slice N <profile> supports=yes/no brim=yes/no material=<mat> priority=<pri>

All parameters except the job number (N) and profile are optional.
Omitted parameters use the profile's defaults.

EXAMPLES:

  # Standard daily-use part, no fuss:
  slice 1 standard supports=no brim=yes material=pla priority=balanced

  # Commission part, strong, precise:
  slice 1 production supports=yes material=petg priority=accuracy

  # Quick fit check only:
  slice 1 proto material=pla priority=speed

  # Custom — full manual control:
  slice 1 supports=yes infill=20 brim=yes layer=0.20 material=pla priority=balanced

RULES:
  - No `/` prefix. Type directly in chat.
  - N = the job number from the consult report header
  - Profile names: proto, standard, production, custom
  - Custom mode lets you set: infill=%, layer=mm, walls=N, fan=%, temp_hotend=°C, temp_bed=°C

WHAT HAPPENS:
  Djinn slices the model using your exact settings via Creality Print CLI.
  Slicing takes 10–120 seconds depending on model complexity.
  Nothing is sent to the printer yet.

------------------------------------------------------------------------
4.4 STEP 4 — READ THE SLICE REPORT
------------------------------------------------------------------------

After slicing, Djinn sends:
  - 2 renders of the sliced model (front view + side view)
  - Support zone render (if supports=yes)
  - Full numeric slice report

SLICE REPORT FORMAT:

  ┌────────────────────────────────────────────────────────┐
  │ Calliope Job #1 — Sliced & Ready                      │
  │ File: my_model.stl                                     │
  │                                                        │
  │ Print time: 6h 5m                                      │
  │ Filament: 48125mm / 110.1g                             │
  │ Hotend: 210°C  Bed: 55°C                               │
  │ Layer height: 0.20mm                                   │
  │                                                        │
  │ Settings used:                                         │
  │   Profile: production   Supports: no                   │
  │   Infill: 25%   Brim: YES (8mm)   Walls: 4            │
  │   Material: PLA   Priority: balanced (100% speed)      │
  │                                                        │
  │ Commission estimate (qty 1):                           │
  │   Material:  $3.47                                     │
  │   Machine:   $1.79                                     │
  │   Labor:     $6.67                                     │
  │   Test run:  $2.63                                     │
  │   ─────────────                                        │
  │   Cost:      $14.56                                    │
  │   💰 Ask:    $24.26                                    │
  └────────────────────────────────────────────────────────┘

If something looks wrong — wrong time, wrong temperature, unexpected infill —
do NOT confirm yet. Run a new slice command with corrected settings.
Re-slicing is free. Wasted filament is not.

Job is now in status: pending

------------------------------------------------------------------------
4.5 STEP 5 — CONFIRM TO PRINT
------------------------------------------------------------------------

  confirm N

This is the ONLY command that actually starts the printer. Until you type
this, nothing physical has happened.

When you confirm, Djinn:
  1. Checks Calliope is not already printing (hard block if it is)
  2. Calculates a safe park position from the gcode bounding box
  3. Uploads the gcode file to Moonraker
  4. Starts the print via Moonraker API
  5. Sets the park position in Klipper (used if print fails mid-job)
  6. Sends a confirmation notification to Discord and Telegram

CALLIOPE WILL NOT START WITHOUT THIS COMMAND.

Job is now in status: printing

------------------------------------------------------------------------
4.6 STEP 6 — MONITOR THE PRINT
------------------------------------------------------------------------

Djinn monitors progress automatically and notifies you at:
  - Print started
  - Bootstrap mode (first 5 successful prints): every 10% progress
  - Normal mode (after 5 successes): every 25% progress
  - Pause detected
  - Error or cancellation
  - Print complete

Check status at any time:
  print status

Expected output:
  Calliope: PRINTING — Job #1 my_model.stl
  Progress: 47% (2h 53m remaining)
  Hotend: 210°C / 210°C  Bed: 55°C / 55°C
  Layer: 112 / 238

------------------------------------------------------------------------
4.7 STEP 7 — PROVIDE FEEDBACK
------------------------------------------------------------------------

  feedback N <what you observed>

Feedback is stored by file hash — the same model printed months later will
show this history in the consult report under "Prior print notes."

Be specific. The more detail you give, the better the next recommendation:

  # Good examples:
  feedback 1 first layer lifted on front edge, increase brim next time
  feedback 1 perfect, no issues — this profile + settings is the keeper
  feedback 1 surface rough on overhangs at accuracy priority, try 0.12mm
  feedback 1 warping on corners at 55°C bed, try 60°C for petg next time

  # Too vague (still acceptable, but less useful):
  feedback 1 ok
  feedback 1 failed

Feedback is optional but strongly recommended. It is the only way the
system gets smarter about your specific models and printer behavior.

Job is now in status: complete

================================================================================
5. PRINT PROFILES — FULL REFERENCE
================================================================================

  ┌────────────┬──────────────────────────┬────────┬─────────┬───────┬───────────┐
  │ Profile    │ Best Use                 │ Infill │ Layer   │ Walls │ Est. Time │
  ├────────────┼──────────────────────────┼────────┼─────────┼───────┼───────────┤
  │ proto      │ Fit checks, samples,     │ 8%     │ 0.28mm  │ 2     │ Fastest   │
  │            │ rapid concept prints     │ gyroid │         │       │           │
  ├────────────┼──────────────────────────┼────────┼─────────┼───────┼───────────┤
  │ standard   │ Working parts, daily use,│ 15%    │ 0.20mm  │ 3     │ Normal    │
  │            │ solid but not final      │ grid   │         │       │           │
  ├────────────┼──────────────────────────┼────────┼─────────┼───────┼───────────┤
  │ production │ Commissions, max strength│ 25%    │ 0.20mm  │ 4     │ Slow      │
  │            │ final deliverable parts  │ gyroid │         │       │           │
  ├────────────┼──────────────────────────┼────────┼─────────┼───────┼───────────┤
  │ custom     │ Full manual control      │ you set│ you set │ you   │ varies    │
  │            │ overrides all defaults   │        │         │ set   │           │
  └────────────┴──────────────────────────┴────────┴─────────┴───────┴───────────┘

PROFILE QUICK RULES:
  - proto: never use for commissions or functional parts
  - standard: default for anything you actually need to use
  - production: default for anything leaving your hands
  - custom: use when you know exactly what you need and why

PRE-SET RECIPES:

  Small decorative parts (vases, minis, trinkets):
    slice N proto supports=no brim=no material=pla priority=speed
    (or use standard if surface quality matters)

  Functional/structural parts (holsters, brackets, tools):
    slice N standard supports=yes brim=yes material=pla priority=balanced

  Commission-ready parts:
    slice N production supports=yes brim=yes material=pla priority=balanced

  Flexible parts:
    slice N standard supports=no material=tpu priority=balanced
    (TPU requires slow speed — balanced is the minimum, never speed)

================================================================================
6. MATERIALS REFERENCE
================================================================================

  ┌──────────┬──────────┬───────────┬────────────────────────────────────────────┐
  │ Material │ Bed Temp │ Hotend    │ Notes                                      │
  ├──────────┼──────────┼───────────┼────────────────────────────────────────────┤
  │ pla      │ 55°C     │ 210°C     │ Default. Easy, reliable, good surface.     │
  │          │          │           │ Use for almost everything.                 │
  ├──────────┼──────────┼───────────┼────────────────────────────────────────────┤
  │ petg     │ 70°C     │ 230°C     │ Stronger than PLA, slight stringing.       │
  │          │          │           │ Good for functional outdoor parts.         │
  ├──────────┼──────────┼───────────┼────────────────────────────────────────────┤
  │ abs      │ 100°C    │ 240°C     │ Warp risk. Needs enclosure or draft shield.│
  │          │          │           │ Use only when heat resistance required.    │
  ├──────────┼──────────┼───────────┼────────────────────────────────────────────┤
  │ tpu      │ 45°C     │ 220°C     │ Flexible. MUST use slow speed.             │
  │          │          │           │ Never use priority=speed with TPU.         │
  └──────────┴──────────┴───────────┴────────────────────────────────────────────┘

TEMPERATURE NOTES:
  - All temperatures above are baseline. Specific filament brands may vary ±5°C.
  - PETG at 55°C bed (PLA default) causes adhesion failures — always use 70°C.
  - ABS below 90°C bed will warp almost certainly.
  - TPU needs 45°C bed — higher causes stringing and oozing.

================================================================================
7. PRIORITY MODES
================================================================================

  ┌──────────┬──────────────┬──────────────┬──────────────────────────────────────┐
  │ Priority │ Speed Factor │ Layer Height │ Use When                             │
  ├──────────┼──────────────┼──────────────┼──────────────────────────────────────┤
  │ speed    │ 150%         │ 0.28mm       │ Fastest output, rougher surfaces.    │
  │          │              │              │ Prototypes only.                     │
  ├──────────┼──────────────┼──────────────┼──────────────────────────────────────┤
  │ balanced │ 100%         │ 0.20mm       │ Default. Best general tradeoff.      │
  │          │              │              │ Use for 90% of jobs.                 │
  ├──────────┼──────────────┼──────────────┼──────────────────────────────────────┤
  │ accuracy │ 60%          │ 0.12mm       │ Best surface finish. Much slower.    │
  │          │              │              │ Use for final commissions or display  │
  │          │              │              │ pieces where surface quality matters. │
  └──────────┴──────────────┴──────────────┴──────────────────────────────────────┘

ACCURACY MODE WARNING:
  A 6-hour balanced print becomes approximately 10 hours at accuracy priority.
  Only use accuracy when the surface quality difference is genuinely visible
  and worth it to the client or use case.

================================================================================
8. SUPPORT SETTINGS — FULL GUIDE
================================================================================

------------------------------------------------------------------------
8.1 WHEN TO USE SUPPORTS
------------------------------------------------------------------------

USE supports=yes:
  - Overhangs steeper than 45° from vertical (standard/production threshold)
  - Bridging spans longer than ~50mm with nothing below
  - Floating geometry — pieces of the model with no physical base underneath

SKIP supports=no:
  - Vases, cups, cylinders, bowls — any hollow part with narrow opening
    (see §8.2 for the hollow part problem — critical read)
  - Gradual curves with overhangs under ~20% — bridge cleanly at 0.20mm PLA
  - Parts where shoulder or taper is the only overhang geometry

DJINN'S THRESHOLD:
  - proto profile:              support threshold at 60° from vertical
  - standard / production:      support threshold at 45° from vertical
  - When in doubt, look at the overhang map render (red = needs support)

------------------------------------------------------------------------
8.2 THE HOLLOW PART PROBLEM
------------------------------------------------------------------------

This is the single most common support mistake. Read this.

When a vase or cylinder has an inward-curving shoulder or neck, the overhang
faces INTO the hollow interior. The slicer places supports directly below
that overhang — which is inside the part. You cannot reach inside to remove
them. There is no orientation you can rotate the model to that avoids this.

RULE: For any hollow part with a narrow opening, always use supports=no.

A gentle shoulder curve (5–15% overhang) will bridge cleanly at 0.20mm PLA.
The surface finish on the inside will be slightly rough — but nobody sees it.

HOW TO IDENTIFY THE HOLLOW PART PROBLEM:
  1. Look at the consult report overhang map (red areas)
  2. Ask: are those red areas on the inside of a hollow shell?
  3. If yes → supports=no regardless of what the slicer recommends
  4. If the red areas are on external geometry → use your judgment on supports

WILL THE SLICER FILL THE INSIDE?

  ┌─────────────────────────────┬──────────────────┬────────────────────┐
  │ Model Type                  │ Infill inside?   │ Supports inside?   │
  ├─────────────────────────────┼──────────────────┼────────────────────┤
  │ Solid cylinder/block        │ Yes — fills vol  │ Only if overhangs  │
  │                             │                  │ > threshold        │
  ├─────────────────────────────┼──────────────────┼────────────────────┤
  │ Hollow shell (vase, cup)    │ No — air stays   │ YES if shoulder or │
  │                             │                  │ neck overhangs     │
  ├─────────────────────────────┼──────────────────┼────────────────────┤
  │ Vase mode (spiral)          │ No               │ No — single wall,  │
  │                             │                  │ no roof possible   │
  └─────────────────────────────┴──────────────────┴────────────────────┘

------------------------------------------------------------------------
8.3 MAKING SUPPORTS EASIER TO REMOVE
------------------------------------------------------------------------

When supports ARE genuinely needed and you want clean removal:

  ┌───────────────────────────────────┬───────────────┬──────────────┬──────────────────────────────────────┐
  │ Setting                           │ Profile Default│ Easy-Remove  │ What It Does                         │
  ├───────────────────────────────────┼───────────────┼──────────────┼──────────────────────────────────────┤
  │ support_material_contact_distance │ 0.2mm         │ 0.25mm       │ Air gap between support top and model.│
  │                                   │               │              │ Larger = less fusing = cleaner break.│
  ├───────────────────────────────────┼───────────────┼──────────────┼──────────────────────────────────────┤
  │ support_material_interface_spacing│ 0mm (solid)   │ 0.2mm        │ Interface density. 0=solid sheet that │
  │                                   │               │              │ grips hard. 0.2=sparse grid, snaps.   │
  ├───────────────────────────────────┼───────────────┼──────────────┼──────────────────────────────────────┤
  │ support_material_interface_layers │ 2             │ 1            │ Dense interface layers at contact.    │
  │                                   │               │              │ Fewer = less bonded material.         │
  └───────────────────────────────────┴───────────────┴──────────────┴──────────────────────────────────────┘

To apply easy-remove settings on a specific job, tell Djinn when giving your
slice command:
  slice 1 standard supports=yes brim=yes material=pla easy_supports=yes

================================================================================
9. THE MAKER'S MARK (TF ANVIL ENGRAVING)
================================================================================

Every Typhon's Forge production print gets a TF anvil mark engraved into
the bottom face of the model. This is an identity mark, not decoration.

TOOL:
  djinn-model-mark <model.stl>

RULE: Mark always goes on the BOTTOM FACE (Z_min).
  Hidden on the shelf. Visible when flipped.

CRITICAL — MIRROR RULE (NON-NEGOTIABLE):
  The mark STL logo faces +Z. When boolean-subtracted into a bottom face
  and viewed from below (-Z), it reads reversed without a mirror.
  djinn-model-mark applies the mirror AUTOMATICALLY.
  DO NOT apply it manually — the tool handles it.

  - Built-in geometry (no --mark flag): mirror always applied.
  - External STL mark (--mark path/to/mark.stl): reads mirror_x from
    ~/.config/djinn/makers-mark.json. Default is true.
  - Pass --no-mirror ONLY if your STL was pre-mirrored.

CONFIG FILE:
  ~/.config/djinn/makers-mark.json

  {
    "path": "/home/drmanzo/Downloads/files/tf_anvil_traced_15mm.stl",
    "mirror_x": true,
    "size_mm": 15,
    "depth_mm": 0.5
  }

To change the default mark: update "path" in the config.
  mirror_x: true stays unless your new mark is pre-mirrored.

WARNING:
  NEVER subtract a mark STL into a bottom face without mirroring first.
  The config enforces this. If you bypass the tool, you own the result.

================================================================================
10. COMMISSION QUOTING
================================================================================

For client price estimates before committing to a print:

  quote <description>
  quick quote <args>

EXAMPLES:
  quote phone holster, PLA, production profile, qty 2
  quick quote production petg 110g 6h

The commission estimate in the slice report is the most accurate because it
uses actual sliced filament weight and time:

  ┌─────────────────────────────────────────────────────────────┐
  │ Commission Estimate Formula:                               │
  │                                                             │
  │   Material cost  = filament_grams × $0.0315/g (PLA rate)  │
  │   Machine time   = print_hours × $0.295/hr                │
  │   Labor          = fixed rate per job complexity tier      │
  │   Test run       = 18% of (material + machine + labor)     │
  │                                                             │
  │   Cost           = material + machine + labor + test       │
  │   Ask price      = Cost × 1.666 (standard markup)         │
  └─────────────────────────────────────────────────────────────┘

The "Ask" price in the slice report is what to charge the client.
Never quote less than "Cost" — that's break-even.

================================================================================
11. JOB STATUSES REFERENCE
================================================================================

  ┌──────────────────┬────────────────────────────────────────────────────────┐
  │ Status           │ Meaning                                                │
  ├──────────────────┼────────────────────────────────────────────────────────┤
  │ needs_settings   │ File analyzed. Waiting for your slice N command.       │
  ├──────────────────┼────────────────────────────────────────────────────────┤
  │ needs_review     │ Consult report sent. Settings not yet submitted.       │
  ├──────────────────┼────────────────────────────────────────────────────────┤
  │ pending          │ Sliced. gcode ready. Waiting for confirm N.            │
  ├──────────────────┼────────────────────────────────────────────────────────┤
  │ printing         │ Active print in progress on Calliope.                  │
  ├──────────────────┼────────────────────────────────────────────────────────┤
  │ complete         │ Print finished successfully.                           │
  ├──────────────────┼────────────────────────────────────────────────────────┤
  │ cancelled        │ Cancelled by user (deny N or force-cancel N).          │
  ├──────────────────┼────────────────────────────────────────────────────────┤
  │ failed           │ Print error detected by monitor service.               │
  └──────────────────┴────────────────────────────────────────────────────────┘

================================================================================
12. COMMAND REFERENCE (ALL COMMANDS)
================================================================================

  ┌───────────────────────────────────┬────────────────────────────────────────────┐
  │ Command                           │ What It Does                               │
  ├───────────────────────────────────┼────────────────────────────────────────────┤
  │ slice N <profile> [settings]      │ Submit settings and slice the model for job│
  │                                   │ N. Must be in needs_review status.         │
  ├───────────────────────────────────┼────────────────────────────────────────────┤
  │ confirm N                         │ Start the print for job N. IRREVERSIBLE.   │
  ├───────────────────────────────────┼────────────────────────────────────────────┤
  │ deny N                            │ Remove job N from queue. Blocked if        │
  │                                   │ Calliope is currently printing.            │
  ├───────────────────────────────────┼────────────────────────────────────────────┤
  │ force-cancel N "reason" <PIN>     │ Emergency cancel of live print. Moves head │
  │                                   │ to safe park. Requires PIN.                │
  ├───────────────────────────────────┼────────────────────────────────────────────┤
  │ queue                             │ Show all jobs and their current status.    │
  ├───────────────────────────────────┼────────────────────────────────────────────┤
  │ print status                      │ Live printer state, temps, and progress.   │
  ├───────────────────────────────────┼────────────────────────────────────────────┤
  │ feedback N <text>                 │ Log post-print notes for job N.            │
  │                                   │ Stored by file hash for future lookups.    │
  ├───────────────────────────────────┼────────────────────────────────────────────┤
  │ quote <description>               │ Commission price estimate from description.│
  ├───────────────────────────────────┼────────────────────────────────────────────┤
  │ quick quote <args>                │ Fast quote with known parameters.          │
  └───────────────────────────────────┴────────────────────────────────────────────┘

SLICE COMMAND PARAMETER REFERENCE:

  Parameter          Values               Default
  ─────────────────────────────────────────────────────────────────
  <profile>          proto, standard,     standard
                     production, custom
  supports=          yes, no              no
  brim=              yes, no              profile default
  material=          pla, petg, abs, tpu  pla
  priority=          speed, balanced,     balanced
                     accuracy
  infill=            integer (%)          profile default
  layer=             float (mm)           profile default
  walls=             integer              profile default
  easy_supports=     yes, no              no

================================================================================
13. FILE & DIRECTORY REFERENCE
================================================================================

  ┌──────────────────────────────────────┬──────────────────────────────────────────┐
  │ What                                 │ Where                                    │
  ├──────────────────────────────────────┼──────────────────────────────────────────┤
  │ Print queue                          │ ~/.local/share/djinn/print-queue.json    │
  ├──────────────────────────────────────┼──────────────────────────────────────────┤
  │ Staged gcode (ready to confirm)      │ ~/Obsidian/printer-files/queue/          │
  ├──────────────────────────────────────┼──────────────────────────────────────────┤
  │ Model library (past prints)          │ ~/Obsidian/printer-files/library/        │
  ├──────────────────────────────────────┼──────────────────────────────────────────┤
  │ Print feedback logs                  │ ~/Obsidian/djinn/printer/feedback/       │
  ├──────────────────────────────────────┼──────────────────────────────────────────┤
  │ Renders cache (consult images)       │ ~/.local/share/djinn/renders/            │
  ├──────────────────────────────────────┼──────────────────────────────────────────┤
  │ Failure log                          │ ~/Obsidian/djinn/printer/failures/       │
  │                                      │ FAILURE-LOG.md                           │
  ├──────────────────────────────────────┼──────────────────────────────────────────┤
  │ Recovery backups                     │ ~/Obsidian/printer-files/recovery/       │
  ├──────────────────────────────────────┼──────────────────────────────────────────┤
  │ Per-print vault notes                │ ~/Obsidian/djinn/printer/prints/         │
  ├──────────────────────────────────────┼──────────────────────────────────────────┤
  │ Slicer profile (Ender-3 V3 Plus)     │ ~/.config/djinn/ender3-v3-plus.ini       │
  ├──────────────────────────────────────┼──────────────────────────────────────────┤
  │ Maker's mark config                  │ ~/.config/djinn/makers-mark.json         │
  ├──────────────────────────────────────┼──────────────────────────────────────────┤
  │ Cube test gcode                      │ CRtestcube_Ender-3 V3 Plus_26m.gcode    │
  │                                      │ (always on printer, no upload needed)    │
  └──────────────────────────────────────┴──────────────────────────────────────────┘

================================================================================
14. SERVICES REFERENCE
================================================================================

All services run as systemd user services on Salomon.

  ┌────────────────────────────────┬──────────────────────────────────────────────┐
  │ Service                        │ Role                                         │
  ├────────────────────────────────┼──────────────────────────────────────────────┤
  │ djinn-discord-gateway          │ Receives commands from Discord, routes to    │
  │                                │ pipeline handlers                            │
  ├────────────────────────────────┼──────────────────────────────────────────────┤
  │ djinn-discord-watcher          │ Watches #3d-printing for STL/3MF attachments │
  ├────────────────────────────────┼──────────────────────────────────────────────┤
  │ djinn-discord-watch            │ Watches for model URLs in messages           │
  ├────────────────────────────────┼──────────────────────────────────────────────┤
  │ djinn-print-monitor            │ Tracks print progress, sends notifications   │
  ├────────────────────────────────┼──────────────────────────────────────────────┤
  │ djinn-print-monitor-v2.timer   │ Failure detection, runs every 60s            │
  ├────────────────────────────────┼──────────────────────────────────────────────┤
  │ djinn-telegram-gateway         │ Telegram bridge for notifications            │
  └────────────────────────────────┴──────────────────────────────────────────────┘

COMMON SERVICE COMMANDS:

  # Check service status:
  systemctl --user status djinn-discord-gateway.service

  # Restart a service:
  systemctl --user restart djinn-discord-gateway.service

  # View recent logs (last 20 lines):
  journalctl --user -u djinn-discord-watcher.service -n 20

  # Follow logs in real time:
  journalctl --user -u djinn-discord-watcher.service -f

  # Check all Djinn services at once:
  systemctl --user list-units 'djinn-*' --all

================================================================================
15. COMMON WORKFLOWS (STEP-BY-STEP)
================================================================================

------------------------------------------------------------------------
15.1 NEW COMMISSION FROM SCRATCH
------------------------------------------------------------------------

Scenario: Client sends you a model for a paid print.

  1. Receive the .stl file from client
  2. Drop file into Discord #3d-printing
  3. Wait for consult report (~20 seconds)
  4. Read consult report:
     - Check "Prior print notes" — any known issues with this model?
     - Check overhang map — are there supports needed?
     - Note Djinn's recommended profile
  5. Run djinn-model-mark on the file before slicing (commission rule):
     djinn-model-mark client_model.stl
  6. Reply with production profile:
     slice N production supports=<yes/no> brim=yes material=pla priority=balanced
  7. Read slice report — verify:
     - Print time matches your schedule
     - Commission estimate is at or above expected price point
     - Temps match loaded material
  8. If estimate is wrong or time too long, re-slice with adjusted settings
  9. When satisfied: confirm N
  10. Monitor with: print status
  11. After print: inspect output, then: feedback N <observation>
  12. Quote client using the "Ask" price from the slice report

------------------------------------------------------------------------
15.2 RE-PRINTING A KNOWN MODEL
------------------------------------------------------------------------

Scenario: You've printed this model before and have feedback history.

  1. Drop the same .stl file into #3d-printing
  2. Consult report will show "Prior print notes" with your previous feedback
  3. Read the notes — apply any corrections that were flagged
     Example: "warping, increase brim" → add brim=yes to slice command
  4. Slice with corrected settings based on prior feedback
  5. Confirm and print
  6. Provide updated feedback to overwrite or append to history

------------------------------------------------------------------------
15.3 QUICK PROTOTYPE / FIT CHECK
------------------------------------------------------------------------

Scenario: Fastest possible print to check dimensions or fit.

  1. Drop .stl into #3d-printing
  2. After consult report:
     slice N proto supports=no material=pla priority=speed
  3. Read slice report — confirm time is acceptable
  4. confirm N
  5. No feedback required (proto prints are not tracked for commission history)

------------------------------------------------------------------------
15.4 EMERGENCY CANCEL OF A LIVE PRINT
------------------------------------------------------------------------

Scenario: Print is running but something is wrong (layer shift, stringing,
layer separation visible through webcam or in person).

  SOFT CANCEL (via Discord/Telegram):
    force-cancel N "reason" <PIN>
    → Djinn moves the head to safe park position
    → Cancels the Moonraker job
    → Logs the cancellation with your reason

  HARD CANCEL (physical):
    → Use the touchscreen on Calliope directly
    → Djinn cannot override a physical cancel
    → After physical cancel, run: feedback N cancelled — reason here
       to keep the history accurate

  AFTER EITHER CANCEL:
    1. Inspect what went wrong
    2. Wait ≥ 2 minutes before restarting (nozzle_mcu stress protection)
    3. If EMI suspected: run tracer on next attempt:
       djinn-print-tracer --interval 5 &
    4. Assess and re-slice before confirming again

------------------------------------------------------------------------
15.5 RECOVERY AFTER A PRINT FAILURE
------------------------------------------------------------------------

Scenario: Print failed mid-job (klippy_shutdown, layer separation, disconnect).

  1. DO NOT immediately restart. Wait ≥ 2 minutes.
  2. Run the tracer on next attempt to capture diagnostic data:
     djinn-print-tracer --interval 5 &
  3. Check if failure was instant retransmit spike or gradual climb:
     - bytes_invalid > 0 at dropout → EMI → cap fan (bridge_fan_speed=0)
     - bytes_invalid = 0 → physical disconnect or power reset of nozzle_mcu
       → check connector and power trace physically
  4. Before ANY hardware diagnosis, run the cube test first:
     → The cube gcode (CRtestcube_Ender-3 V3 Plus_26m.gcode) is always
       on the printer — no upload needed
     → confirm the cube gcode to start it
     → Cube passes → problem is in the gcode, not hardware
     → Cube fails → hardware problem confirmed, then diagnose
  5. Consistent failure at same duration → gcode command, not hardware
  6. Random failure duration → hardware or EMI accumulation
  7. Log the failure: feedback N failed — [describe what was observed]

================================================================================
16. TROUBLESHOOTING (CAUSE + FIX)
================================================================================

  SYMPTOM: STL dropped but no response from Djinn after 30+ seconds
  CAUSE:   djinn-discord-watcher service is down or crashed
  FIX:     journalctl --user -u djinn-discord-watcher.service -n 20
           systemctl --user restart djinn-discord-watcher.service
           Watcher polls every 20s — allow up to 30s after restart
  ─────────────────────────────────────────────────────────────────────────
  SYMPTOM: slice command sent but nothing happened
  CAUSE:   Job is not in needs_review status, or command format is wrong
  FIX:     Run `queue` to check job status
           Verify format: slice N <profile> ... (no / prefix, no punctuation)
           If status is printing, you cannot re-slice — deny is blocked
  ─────────────────────────────────────────────────────────────────────────
  SYMPTOM: confirm N sent but printer did not start
  CAUSE 1: Moonraker unreachable or Klipper crashed
  FIX 1:   curl http://192.168.1.113:7125/printer/info
           If timeout → check Calliope is powered on and networked
           SSH to Salomon and check Klipper logs
  CAUSE 2: Calliope is already printing another job
  FIX 2:   print status → if printing, wait for completion or cancel first
  ─────────────────────────────────────────────────────────────────────────
  SYMPTOM: Renders missing from consult report
  CAUSE:   Xvfb not running in the watcher service cgroup
  FIX:     systemctl --user status djinn-discord-watcher.service
           Check for Xvfb errors in service logs
           journalctl --user -u djinn-discord-watcher.service -n 50
  ─────────────────────────────────────────────────────────────────────────
  SYMPTOM: Discord notifications not landing
  CAUSE:   Bot token expired or invalid
  FIX:     Check bot token in ~/.openclaw/openclaw.json is current
           All scripts use direct REST API — not OpenClaw relay
           Regenerate bot token in Discord Developer Portal if needed
  ─────────────────────────────────────────────────────────────────────────
  SYMPTOM: Print fails with klippy_shutdown or nozzle_mcu disconnect
  CAUSE:   EMI from fan at 100% (M106 S255) causing nozzle_mcu dropout
  FIX:     Re-slice with bridge_fan_speed=0 in Creality Print filament profile
           djinn-gcode-safety post-processes all gcode to cap M106 at S128
           For production profile: fan is already capped at 50%
           If problem persists: check nozzle_mcu connector physically
           Run tracer: djinn-print-tracer --interval 5 &
  ─────────────────────────────────────────────────────────────────────────
  SYMPTOM: Supports fused to model, impossible to remove
  CAUSE:   Default contact distance too tight for this filament or model
  FIX:     Re-slice with easy_supports=yes
           Or manually set: support_material_contact_distance=0.25mm
           And: support_material_interface_spacing=0.2mm
  ─────────────────────────────────────────────────────────────────────────
  SYMPTOM: First layer warping or not sticking
  CAUSE 1: Bed temp too low for material
  FIX 1:   PETG → ensure bed=70°C (not 55°C PLA default)
           ABS → ensure bed=100°C
  CAUSE 2: No brim on large flat-bottom parts
  FIX 2:   Re-slice with brim=yes
  CAUSE 3: Bed not level or Z offset wrong
  FIX 3:   Run bed leveling via Klipper: BED_MESH_CALIBRATE in console
  ─────────────────────────────────────────────────────────────────────────
  SYMPTOM: Stringing throughout the print
  CAUSE:   Hotend temperature too high, or retraction settings wrong
  FIX:     PETG stringing is normal — reduce temp by 5°C increments
           PLA stringing → check retraction is enabled in slicer profile
  ─────────────────────────────────────────────────────────────────────────
  SYMPTOM: maker's mark came out backwards / mirrored on bottom of print
  CAUSE:   djinn-model-mark was bypassed and mark was subtracted manually
  FIX:     ALWAYS use djinn-model-mark — it handles mirroring automatically
           If already printed, this is unfixable without reprinting
           To fix the STL: re-run djinn-model-mark on the original model

================================================================================
17. TECHNICAL REFERENCE
================================================================================

------------------------------------------------------------------------
17.1 SLICER STACK
------------------------------------------------------------------------

Creality Print is the SOLE active slicer. OrcaSlicer and PrusaSlicer
are archived and no longer used.

  ┌──────────────────┬────────┬───────────────────────────────────────────────┐
  │ Slicer           │ Role   │ How Invoked                                   │
  ├──────────────────┼────────┼───────────────────────────────────────────────┤
  │ Creality Print   │ ACTIVE │ GUI: flatpak run com.creality.CrealityPrint   │
  │                  │        │ CLI: Djinn calls headless for pipeline slicing │
  │                  │        │ Uploads directly to Calliope via Moonraker    │
  └──────────────────┴────────┴───────────────────────────────────────────────┘

------------------------------------------------------------------------
17.2 FAN / EMI HARDWARE CONSTRAINT
------------------------------------------------------------------------

CRITICAL — READ THIS BEFORE MODIFYING ANY FAN SETTINGS.

The nozzle_mcu board on the Sprite Pro extruder is EMI-sensitive.
100% fan speed (M106 S255) causes nozzle_mcu dropout mid-print.

RULES:
  - Creality Print: set bridge_fan_speed=0 in the filament profile
  - Production profile: fan capped at 50% — DO NOT override this
  - djinn-gcode-safety: post-processes ALL gcode files and caps M106
    at S128 max, regardless of what the slicer emitted
  - This is a hardware constraint, not a slicer preference

BRIDGE GEOMETRY WARNING:
  Engraved OR embossed text on a model creates bridge sections.
  Each letter groove or raised letter top is a bridging span.
  More text = more bridges = more fan-intensive spans = higher EMI risk.
  Check bridge count before printing text-heavy models. Consider
  using accuracy priority (slower print = less aggressive cooling needed).

DIAGNOSTIC TOOL:
  djinn-print-tracer --interval 5 &
  Run this before any print where EMI is suspected.
  Watch bytes_invalid at the moment of any dropout.

------------------------------------------------------------------------
17.3 FAILURE TRIAGE PROTOCOL
------------------------------------------------------------------------

Order matters. DO NOT touch hardware until the cube test passes.

  Step 1: Run tracer on next attempt:
          djinn-print-tracer --interval 5 &

  Step 2: Check bytes_invalid at moment of dropout:
          > 0  → EMI → cap fan (bridge_fan_speed=0). Retry.
          = 0  → physical disconnect or nozzle_mcu power reset
                 → check connector + power trace physically.
                 Fan cap will NOT fix this.

  Step 3: Check pattern:
          Gradual retransmit climb → print the cube test first:
            Cube passes → gcode problem (not hardware)
            Cube fails  → hardware problem confirmed → diagnose

  Step 4: Check timing consistency:
          Consistent failure at same layer/duration → gcode command
          Random failure duration                   → hardware or EMI

  Step 5: Wait ≥ 2 minutes between klippy_shutdown and next attempt.
          Rapid restart cycles stress the nozzle_mcu connector.

  Cube test gcode: CRtestcube_Ender-3 V3 Plus_26m.gcode
  Always resident on printer — no upload required.

------------------------------------------------------------------------
17.4 SERVICE ARCHITECTURE
------------------------------------------------------------------------

All services run as systemd user services on Salomon:

  djinn-discord-gateway.service
    → Entry point for all Discord commands
    → Routes to: print handler, queue handler, feedback handler
    → Communicates with: Moonraker API, Djinn AI layer

  djinn-discord-watcher.service
    → Polls #3d-printing for new attachments every 20 seconds
    → Downloads .stl/.3mf → triggers analyze → triggers consult report
    → Requires Xvfb in service cgroup for render generation

  djinn-discord-watch.service
    → Polls #3d-printing messages for Printables/Thingiverse URLs
    → Fetches file from URL → hands off to watcher pipeline

  djinn-print-monitor.service
    → Long-running Moonraker progress monitor
    → Sends percentage milestone notifications to Discord and Telegram
    → Bootstrap mode: every 10% (first 5 successful prints)
    → Normal mode: every 25% (thereafter)

  djinn-print-monitor-v2.timer
    → Systemd timer running every 60 seconds
    → Failure detection: checks for klippy_shutdown or stalled progress
    → Triggers notification and failure log entry on detection

  djinn-telegram-gateway.service
    → Mirrors Discord notifications to Telegram
    → Runs independently — Discord failure does not kill Telegram path

------------------------------------------------------------------------
17.5 GCODE SAFETY LAYER
------------------------------------------------------------------------

Tool: djinn-gcode-safety

All gcode generated by the slicer passes through djinn-gcode-safety
before being queued for Moonraker upload. It enforces:

  - M106 (fan speed) capped at S128 (50% max) regardless of slicer setting
  - No M106 S255 or higher is ever sent to Calliope
  - Applied automatically — operator does not need to invoke it manually

This is the last line of defense against EMI-induced nozzle_mcu failures.
Do not bypass it.

================================================================================
18. FAQ
================================================================================

Q: Can I start a print without going through the full pipeline?
A: Not through Djinn. The confirm command requires a pending job that was
   sliced through the pipeline. You can start a print directly via Moonraker
   web UI (http://192.168.1.113:7125) or Fluidd/Mainsail, but this bypasses
   gcode safety processing and feedback logging. Not recommended.

Q: What if I drop a file and immediately want to cancel before it analyzes?
A: Type `deny N` once the job number appears in the consult report.
   If you haven't seen a job number yet, wait for the consult — Djinn
   is already processing. Denying before analysis completes is not supported.

Q: Can I change settings after confirming?
A: No. confirm is irreversible. If you need different settings, you must
   force-cancel the job (if it's still in queue or just started) and
   re-slice with the correct settings.

Q: Why can't Djinn cancel a live print without my PIN?
A: Safety constraint. A pin-free cancel could be triggered accidentally.
   The physical touchscreen is always the fallback for emergencies.

Q: What is the maximum bed size?
A: Calliope's build volume is 300 × 300 × 300mm.
   The consult report will flag if the model doesn't fit.

Q: What if I want to print the same model with different settings later?
A: Drop the same file. Djinn identifies models by file hash. The consult
   will show prior print history. You then slice with new settings.
   The old feedback is preserved alongside the new run.

Q: Why is the production profile fan capped at 50%?
A: Hardware constraint — see §17.2. The nozzle_mcu board on the Sprite Pro
   is EMI-sensitive. 100% fan causes dropout. 50% is the tested safe cap.

Q: Can I use OrcaSlicer or PrusaSlicer?
A: Those slicers are archived. Creality Print is the only active slicer.
   It integrates directly with the CLI pipeline and Moonraker upload.
   Using a different slicer would bypass djinn-gcode-safety.

Q: How do I add a new filament type?
A: Edit ~/.config/djinn/ender3-v3-plus.ini with the material's temp profile.
   Then notify Djinn so it can be added to the material keyword list
   for the slice command parser.

Q: The commission estimate in the quote command differs from the slice report.
A: The quote command uses estimated parameters. The slice report uses actual
   sliced values (exact filament weight, exact print time). Always use the
   slice report estimate when pricing a commission — it's more accurate.

================================================================================
                              END OF MANUAL
================================================================================
*Document assembled by Claude — 2026-06-09*
*Source docs absorbed: PRINTER-MANUAL.md, SUPPORT-GUIDE.md, PRINT-PROFILES.md*
*See git history for change log.*
================================================================================
