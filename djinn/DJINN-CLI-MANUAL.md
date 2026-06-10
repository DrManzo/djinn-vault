================================================================================
                          DJINN CLI MANUAL
             Every Command · Every Flag · Every Workflow
================================================================================
Version: 1.0 | Last updated: 2026-06-09 | Maintained by: Owner / Marcus

> Standalone CLI reference for the Djinn system. Covers every installed
> command, its flags, expected behavior, and common workflows. Anyone
> starting cold should be able to operate the full stack from this document.

================================================================================
TABLE OF CONTENTS
================================================================================

  1.  Installation Paths
  2.  Print Pipeline Commands
      2.1 djinn-print-consult
      2.2 djinn-model-slice
      2.3 djinn-confirm-print
      2.4 djinn-print-monitor
      2.5 djinn-print-quote
      2.6 djinn-force-cancel
      2.7 djinn-park-calc
  3.  Shop & Order Commands
      3.1 Owner Telegram Commands
      3.2 Owner Discord Commands
      3.3 Dashboard (localhost:5000)
  4.  Design Orchestrator
      4.1 djinn-design
  5.  Deployment
      5.1 djinn-shop-deploy
  6.  Common Workflows

================================================================================
1. INSTALLATION PATHS
================================================================================

All CLI tools install to:
  ~/.local/bin/

All shop data lives at:
  ~/.local/share/djinn-shop/
    shop.db         — Encrypted SQLite database
    exports/        — CSV + XLSX financial reports
    labels/         — Downloaded shipping label PDFs

All config lives at:
  ~/.config/djinn/
    easypost.env    — EasyPost API key  [REQUIRED for shipping]
    shop.json       — Shop address + config  [REQUIRED for labels]
  ~/.config/djinn-shop/
    secret.key      — Fernet encryption key  (chmod 600 — never commit)

All source lives at:
  ~/Obsidian/djinn/printer/

================================================================================
2. PRINT PIPELINE COMMANDS
================================================================================

--------------------------------------------------------------------------------
2.1 djinn-print-consult
--------------------------------------------------------------------------------

Purpose:
  Full pre-print analysis. Downloads/analyzes mesh, generates renders,
  dry-runs slicer for accurate time/material estimates, posts report.

Usage:
  djinn-print-consult <file.stl|file.3mf>
  djinn-print-consult <file> --profile <proto|standard|production>
  djinn-print-consult <file> --material <pla|petg|abs>
  djinn-print-consult <file> --no-render    # skip render generation
  djinn-print-consult <file> --json         # machine-readable output

What it does:
  1. Downloads file if URL provided, otherwise reads local path
  2. Analyzes mesh with trimesh: dimensions, volume, overhang detection
  3. Generates 3 renders: front, side, overhang map (red = needs support)
  4. Dry-runs Creality Print via Xvfb for real time + filament estimates
  5. Checks file hash against print history for prior notes
  6. Posts consult report to Discord channel + Telegram

Output format:
  File: <filename>
  Size: <X> × <Y> × <Z>mm  |  Volume: <V>cm³
  [WARNING if smoking accessory detected]

  Profiles:
    proto       ~<time>   ~<grams>g
    standard    ~<time>   ~<grams>g  ◄ recommended
    production  ~<time>   ~<grams>g

Notes:
  - Smoking accessory detection triggers PETG/ABS requirement warning
  - Prior print history shown if file hash matches previous job
  - Renders saved to /tmp/djinn-renders/ by default

--------------------------------------------------------------------------------
2.2 djinn-model-slice
--------------------------------------------------------------------------------

Purpose:
  Run Creality Print with exact user-specified settings to produce gcode.

Usage:
  djinn-model-slice <file.stl> --profile <proto|standard|production>
  djinn-model-slice <file.stl> --material petg --infill 20 --supports
  djinn-model-slice <file.stl> --output <path/to/output.gcode>

Flags:
  --profile     proto | standard | production
  --material    pla | petg | abs | tpu
  --infill      0–100 (percent)
  --supports    enable automatic support generation
  --no-supports force-disable supports
  --output      custom output path for gcode file

Notes:
  - Uses Creality Print as the slicer (OrcaSlicer and PrusaSlicer archived)
  - Runs headless via Xvfb
  - Output gcode is used directly by djinn-confirm-print

--------------------------------------------------------------------------------
2.3 djinn-confirm-print
--------------------------------------------------------------------------------

Purpose:
  Upload gcode to printer and start the print. The only way to start a print.

Usage:
  djinn-confirm-print <N>        # N = queue job number
  djinn-confirm-print <N> --dry-run   # validate without starting

What it does:
  1. Checks printer is idle (not already printing)
  2. Reads gcode bounding box to calculate safe park position
  3. Uploads gcode to Moonraker API
  4. Starts print job
  5. Registers park position in Klipper for failure handling

Safety:
  - Hard blocks if printer is already printing
  - No autonomous start — always requires explicit operator call
  - Park position calculation is mandatory before every job

--------------------------------------------------------------------------------
2.4 djinn-print-monitor
--------------------------------------------------------------------------------

Purpose:
  Poll Moonraker for print progress and post updates to Discord + Telegram.

Usage:
  djinn-print-monitor              # runs until print completes
  djinn-print-monitor --interval 30    # poll every 30 seconds (default: 60)
  djinn-print-monitor --silent         # no Discord/Telegram posts

Behavior:
  - Bootstrap mode (first 5 prints): updates every 10% complete
  - Normal mode: updates every 25% complete
  - 0% progress does NOT trigger failure — large files show 0% for hours
  - Completes automatically when Moonraker reports job done

Output example:
  🖨️ ORD-0001 | 50% | ~1h 20m remaining

--------------------------------------------------------------------------------
2.5 djinn-print-quote
--------------------------------------------------------------------------------

Purpose:
  CLI interface to FairPrintAgent pricing engine. Useful for manual quotes
  or testing pricing logic without going through Discord.

Usage:
  djinn-print-quote --file <file.stl> --material petg --qty 2
  djinn-print-quote --time 3.5 --grams 44 --material petg --type functional_custom_part
  djinn-print-quote --help

Flags:
  --file        STL/3MF file (for auto time/material estimate)
  --time        print time in hours (manual override)
  --grams       material used in grams (manual override)
  --material    pla | petg | abs | tpu
  --qty         quantity (default: 1)
  --type        job type: commodity_decor | functional_custom_part |
                          design_heavy_oneoff | urgent_rush
  --smoking     flag as smoking accessory (+35% upcharge)
  --express     flag as express order (+35% premium)

Output:
  Customer view: price tiers (standard + express)
  Owner view: cost floor, fair market, margin %, market comps

--------------------------------------------------------------------------------
2.6 djinn-force-cancel
--------------------------------------------------------------------------------

Purpose:
  Emergency stop for an active print. Requires owner PIN.

Usage:
  djinn-force-cancel
  [Prompts for PIN]

Behavior:
  - Sends emergency stop to Klipper
  - Moves toolhead to registered park position
  - Updates order status to cancelled
  - Posts notification to Telegram

Safety:
  - PIN-protected. No agent can call this without owner authorization.
  - `deny N` during a print routes to this command with PIN prompt.

--------------------------------------------------------------------------------
2.7 djinn-park-calc
--------------------------------------------------------------------------------

Purpose:
  Standalone park position calculator. Used internally by djinn-confirm-print
  but can also be called manually to verify park position before a job.

Usage:
  djinn-park-calc <file.gcode>

Output:
  Park X: <value>mm
  Park Y: <value>mm
  Park Z: <value>mm  (bounding box max + 10mm clearance)

================================================================================
3. SHOP & ORDER COMMANDS
================================================================================

--------------------------------------------------------------------------------
3.1 OWNER TELEGRAM COMMANDS
--------------------------------------------------------------------------------

These commands are issued by the owner in the Telegram bot DM.

  paid ORD-0001
    Mark ORD-0001 as payment received. Advances order to paid queue.

  ship ORD-0001
    Show carrier rate comparison for ORD-0001. No label purchased.

  ship ORD-0001 usps-priority
    Purchase USPS Priority label for ORD-0001. Downloads PDF to labels/.
    DMs tracking number to customer.

  batch ORD-0001 ORD-0003
    Merge ORD-0001 and ORD-0003 onto a single plate.
    PlateNestAgent runs. Combined gcode queued for confirm.

  inventory
    Show current filament spool inventory (material, color, brand, grams).

  low stock
    Show all spools below 150g threshold.

  add filament petg black 1000g $28
    Add a new spool to inventory. Format:
    add filament <material> <color> <weight>g $<cost>

  status
    Show current printer status (idle / printing / error) and active job.

  queue
    Show all paid, pending, and in-progress orders.

--------------------------------------------------------------------------------
3.2 OWNER DISCORD COMMANDS
--------------------------------------------------------------------------------

  confirm N
    Start print job N. Calls djinn-confirm-print internally.
    Hard-blocked if printer is already printing.

  deny N
    Cancel a queued job N (not yet printing).
    Blocked if job is currently printing — use force-cancel.

  quote <description>
    Manually trigger a FairPrint quote from a text description.
    Same as a customer typing in the channel but routed to owner view.

--------------------------------------------------------------------------------
3.3 DASHBOARD (localhost:5000)
--------------------------------------------------------------------------------

  URL:  http://localhost:5000
  Auth: Password-gated on first run.

  Pages:
    /           Queue — pending orders, confirm payment, status badges
    /orders     Full order history, filterable, expandable
    /customers  Per-customer ledger, lifetime value, balances
    /finance    Income statement + live balance sheet
    /reports    6-month summary cards + CSV/XLSX export

  Starting the dashboard manually:
    python3 ~/Obsidian/djinn/printer/shop/dashboard/app.py

  Starting via systemd (if configured):
    systemctl --user start djinn-dashboard

================================================================================
4. DESIGN ORCHESTRATOR
================================================================================

--------------------------------------------------------------------------------
4.1 djinn-design
--------------------------------------------------------------------------------

Purpose:
  Six-agent pipeline for original model creation: text brief → parametric
  OpenSCAD → prototype/production STLs → optimal slicer profile → plate → quote.

Usage:
  djinn-design --brief "<description>"
  djinn-design --brief "<description>" --output-dir <path>
  djinn-design --edit <existing.scad> --change "<modification request>"
  djinn-design --optimize <file.stl> --goal <time|material|strength>

Six-agent pipeline:

  1. DesignGenAgent
     Input:  Text brief
     Output: Concept JSON + parametric OpenSCAD file

  2. DesignEditAgent
     Input:  Existing .scad + change request
     Output: Modified .scad

  3. ProtoOptAgent
     Input:  .scad file
     Output: Prototype-light STL + production STL

  4. DOEPrintOptAgent
     Input:  STL + optimization goal (time | material | strength)
     Output: Taguchi DOE grid → optimal slicer profile
     Note:   Eliminates test prints via Taguchi factorial design.
             Verified result: -76% print time / -51% material vs standard.

  5. PlateNestAgent
     Input:  Multiple STLs
     Output: Decimated + arranged plate STL ready for slicing

  6. FairPrintAgent
     Input:  ProjectState (all prior outputs)
     Output: Commission quote → order status advances to `priced`

================================================================================
5. DEPLOYMENT
================================================================================

--------------------------------------------------------------------------------
5.1 djinn-shop-deploy
--------------------------------------------------------------------------------

Purpose:
  One-command installer for the full Djinn shop system. Sets up database,
  installs services, configures gateways, validates dependencies.

Usage:
  djinn-shop-deploy
  djinn-shop-deploy --check    # validate dependencies without installing
  djinn-shop-deploy --reset    # wipe shop.db and start fresh (DESTRUCTIVE)

What it installs:
  - shop.db with schema initialization
  - Fernet secret key generation (chmod 600)
  - Discord gateway service
  - Telegram gateway service
  - Dashboard service (optional)
  - systemd unit files
  - Required Python packages

Prerequisites (must exist before running):
  - ~/.config/djinn/easypost.env     (EasyPost API key)
  - ~/.config/djinn/shop.json        (shop address + config)
  - Discord bot token in environment
  - Telegram bot token in environment
  - Moonraker accessible on local network

================================================================================
6. COMMON WORKFLOWS
================================================================================

New commission from scratch:
  1. Customer drops file in Discord
  2. djinn-print-consult runs automatically
  3. FairPrintAgent quotes automatically
  4. Customer replies ORDER
  5. DM flow collects payment + address
  6. Owner: `paid ORD-XXXX`
  7. batch_agent checks for compatible queue jobs
  8. Owner: `confirm N`
  9. djinn-print-monitor runs automatically
  10. Owner: `ship ORD-XXXX usps-priority`

Manual quote from CLI:
  djinn-print-quote --file part.stl --material petg --type functional_custom_part

Check print status:
  djinn-print-monitor --silent   (shows status without posting)

Batch two paid orders:
  Owner Telegram: batch ORD-0001 ORD-0003
  Review proposed plate
  Owner Discord: confirm N

Add new filament spool:
  Owner Telegram: add filament petg black 1000g $28

Check low stock before accepting orders:
  Owner Telegram: low stock

Generate financial report:
  Open http://localhost:5000/reports
  Click Export XLSX or Export CSV

Design an original part:
  djinn-design --brief "wall-mounted mic stand arm, 200mm reach, fits 3/8 thread"

================================================================================
*— Marcus, 2026-06-09*
================================================================================
