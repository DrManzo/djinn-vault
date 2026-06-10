================================================================================
                 FAIRPRINT / TYPHON'S FORGE — COMPLETE OPERATOR MANUAL
        Intake → Consult → Quote → Order → Batch → Print → Ship → Report
================================================================================
Version: 1.0 | Last updated: 2026-06-09 | Maintained by: Owner / Marcus

> Full standalone operator handbook for the Typhon's Forge / FairPrint system.
> Built from the deployed Djinn print-shop architecture and business strategy.
> An operator or agent who has never seen the stack should be able to understand,
> run, troubleshoot, and extend the commission workflow from this document alone.

================================================================================
TABLE OF CONTENTS
================================================================================

  1.  What FairPrint Is
  2.  System Overview
      2.1 Customer Promise
      2.2 Full Architecture
      2.3 End-to-End Workflow
  3.  Core Components
  4.  Pricing Logic
  5.  Order Flow
  6.  Batch & Print Execution
  7.  Shipping & Customer Handoff
  8.  Dashboard, Accounting, and Inventory
  9.  Product Library & Business Strategy
  10. Key Commands & Files
  11. Djinn Design Orchestrator (djinn-design)
  12. Safety Rules
  13. Troubleshooting
  14. Immediate Next Steps

================================================================================
1. WHAT FAIRPRINT IS
================================================================================

FairPrint is the commission pricing and fulfillment brain inside Typhon's Forge —
a fully automated, AI-mediated 3D print shop running on Calliope (Ender-3 V3 Plus)
orchestrated from the primary workstation.

Customers drop a file in Discord or describe a part in plain language. The system
analyzes the job, produces a consult report with renders, calculates a fair quote
using live market research, collects order data encrypted, manages the queue,
batches compatible jobs onto a single plate, monitors prints, and prepares shipping
— all with minimal operator input.

Operator involvement is intentionally reduced to two touches:
  1. Mark payment received (`paid ORD-XXXX`)
  2. Trigger shipping (`ship ORD-XXXX <carrier>`)

Everything else is automated.

Two business layers — do NOT conflate:
  1. Typhon's Forge — the live print shop making money now.
  2. djinn-shop-deploy — a future packaged product for other print sellers.

================================================================================
2. SYSTEM OVERVIEW
================================================================================

--------------------------------------------------------------------------------
2.1 CUSTOMER PROMISE
--------------------------------------------------------------------------------

Customer experience in one sentence:
  Drop a model or describe a part → receive a clear quote → confirm → get
  progress notifications and tracking with zero friction.

Owner experience in one sentence:
  Touch the order twice: mark payment received, then ship the finished piece.

--------------------------------------------------------------------------------
2.2 FULL ARCHITECTURE
--------------------------------------------------------------------------------

  ┌─────────────────────────────────────────────────────────────────┐
  │                        CUSTOMER LAYER                           │
  │   Discord #3d-printing          Telegram DMs                   │
  │   (file drop + ORDER)           (owner notifications)          │
  └────────────────────────────────┬────────────────────────────────┘
                                 │
  ┌────────────────────────────────▼────────────────────────────────┐
  │                     GATEWAY LAYER                               │
  │   djinn-discord-gateway      djinn-telegram-gateway             │
  │   djinn-discord-watcher      (owner commands + notifications)   │
  └────────────────────────────────┬────────────────────────────────┘
                                 │
  ┌────────────────────────────────▼────────────────────────────────┐
  │                    INTELLIGENCE LAYER                           │
  │  intake_agent.py        quote_formatter.py   batch_agent.py    │
  │  commissions/price.py   shop/db.py           shipping_agent.py  │
  │  customer_dm.py         accounting.py        inventory.py       │
  └────────────────────────────────┬────────────────────────────────┘
                                 │
  ┌────────────────────────────────▼────────────────────────────────┐
  │                    EXECUTION LAYER                              │
  │   djinn-print-consult    djinn-model-slice    djinn-confirm-print│
  │   djinn-print-monitor    djinn-park-calc      djinn-force-cancel │
  └────────────────────────────────┬────────────────────────────────┘
                                 │
  ┌────────────────────────────────▼────────────────────────────────┐
  │                    HARDWARE LAYER                               │
  │   Calliope (Ender-3 V3 Plus)                                    │
  │   Klipper + Moonraker at <printer-ip>:7125                      │
  └─────────────────────────────────────────────────────────────────┘

--------------------------------------------------------------------------------
2.3 END-TO-END WORKFLOW
--------------------------------------------------------------------------------

   1. Customer uploads STL/3MF or describes a part in Discord #3d-printing.
   2. Intake parses the request into a structured print brief.
   3. djinn-print-consult downloads mesh, analyzes geometry, generates renders,
      dry-runs Creality Print for real time/material estimates.
   4. FairPrint runs pricing: cost floor + market research + job-type weighting.
   5. Customer receives clean quote; owner sees full cost breakdown via Telegram.
   6. Customer replies ORDER or EXPRESS.
   7. Bot DMs customer for payment + shipping address (encrypted DM flow).
   8. Owner confirms payment: `paid ORD-XXXX`.
   9. Paid queue scanned — compatible jobs batched onto one plate if possible.
  10. Owner starts print: `confirm N`. Monitor begins polling Moonraker.
  11. Progress reported to Discord and Telegram at regular intervals.
  12. Print completes → owner ships: `ship ORD-XXXX usps-priority`.
  13. Customer receives tracking DM. Accounting and reports auto-update.

================================================================================
3. CORE COMPONENTS
================================================================================

--------------------------------------------------------------------------------
djinn-print-consult
--------------------------------------------------------------------------------

  - Downloads and analyzes mesh geometry with trimesh.
  - Measures bounding box dimensions, volume, and overhang angles.
  - Generates three renders: front view, side view, overhang map (red = support).
  - Dry-runs Creality Print via Xvfb to get realistic time and filament numbers.
  - Pulls prior print history for this exact model (keyed by file hash).
  - Posts consult report to Discord channel and Telegram.

--------------------------------------------------------------------------------
commissions/price.py (FairPrintAgent)
--------------------------------------------------------------------------------

  - Calculates material, labor, machine, and extras cost.
  - Applies failure coverage and minimum margin floor.
  - Runs DuckDuckGo market search for comparable Etsy/specialist listings.
  - Uses true weighted median (not mean — outlier resistant).
  - Applies job-type weighting and smoking-accessory rules.
  - Applies Express upcharge for urgent_rush tier.

--------------------------------------------------------------------------------
customer_dm.py
--------------------------------------------------------------------------------

  - Sends payment instructions to customer via DM.
  - Collects name, shipping address, and special notes privately.
  - Stores all PII encrypted in shop.db with Fernet column-level encryption.
  - Customer address NEVER appears in any Discord channel.
  - Bot cleans up its own DM messages after 48 hours.

--------------------------------------------------------------------------------
batch_agent.py
--------------------------------------------------------------------------------

  - Scans paid queue for jobs with matching material and color.
  - Checks combined footprint against 220×220mm bed.
  - Proposes a batch to the owner with estimated time savings.
  - Owner approves with: `batch ORD-0001 ORD-0003`
  - PlateNestAgent arranges STLs on the plate.

--------------------------------------------------------------------------------
shipping_agent.py
--------------------------------------------------------------------------------

  - Decrypts customer address from shop.db.
  - Estimates package weight: print grams + 85g packaging allowance.
  - Fetches rates from USPS, UPS, and FedEx via EasyPost SDK.
  - If no carrier specified: returns comparison table first.
  - Purchases label, saves PDF to labels/, updates order to shipped.
  - DMs customer with tracking number.

--------------------------------------------------------------------------------
accounting.py / dashboard
--------------------------------------------------------------------------------

  - Income statement: revenue, COGS, gross profit, margin %, operating expenses, net.
  - Balance sheet: cash, receivables, inventory, equipment value, payables, equity.
  - Monthly report: jobs completed/failed, failure rate, revenue, COGS, repeat
    customers, avg order value, filament used, machine hours.
  - Export: CSV + formatted XLSX (multi-sheet workbook).
  - Dashboard at http://localhost:5000 — password-gated Flask + Bootstrap 5.

================================================================================
4. PRICING LOGIC
================================================================================

  material_cost  = spool_cost_per_gram × used_g × 1.10   (10% waste buffer)
  machine_cost   = print_hours × ~$0.20/hr
  labor_cost     = total_labor_min / 60 × $20/hr
  extras         = packaging ($0.50) + hardware + shipping add-ons

  base_cost      = material + machine + labor + extras
  risk_adjusted  = base_cost / 0.92           (92% success rate assumption)
  cost_floor     = risk_adjusted × 1.30        (30% minimum margin)

  market_median  = true weighted median of DDG-fetched Etsy/specialist listings

  fair_market    = wc×cost_floor + wm×market_median + wv×(cost_floor + value_premium)

  if smoking_accessory:
      fair_market *= 1.35

  express_price  = fair_market × 1.35

Machine economics defaults:
  Machine cost rate:   ~$0.20/hr (electricity + depreciation + maintenance)
  Electricity:          180W/1000 × local kWh rate
  Depreciation:         printer_cost / 5000hr estimated life
  Maintenance:          $0.10/hr

Job-type weighting table:

  ┌─────────────────────────────┬────────┬────────┬────────┐
  │ Job type                    │  Cost  │ Market │  Value │
  ├─────────────────────────────┼────────┼────────┼────────┤
  │ commodity_decor             │  65%   │  30%   │   5%   │
  │ functional_custom_part      │  55%   │  30%   │  15%   │
  │ design_heavy_oneoff         │  40%   │  25%   │  35%   │
  │ urgent_rush                 │  50%   │  20%   │  30%   │
  └─────────────────────────────┴────────┴────────┴────────┘

================================================================================
5. ORDER FLOW
================================================================================

  ORDER    = standard fulfillment
  EXPRESS  = priority turnaround (× 1.35 pricing)

Order sequence:
  1. Customer confirms quote in Discord.
  2. Bot opens DM: sends payment instructions.
  3. Bot collects name, shipping address, and notes via DM.
  4. Data encrypted into shop.db. Address NEVER in Discord channels.
  5. Owner receives decrypted Telegram summary.
  6. Owner confirms payment: `paid ORD-XXXX`
  7. Order enters paid queue → batchable and printable.

Privacy implementation:
  - shop.db at `~/.local/share/djinn-shop/shop.db`
  - Fernet column-level encryption for: name, shipping address, email, contact.
  - Encryption key: `~/.config/djinn-shop/secret.key` (chmod 600, auto-generated)
  - Bot DMs deleted after 48 hours.

================================================================================
6. BATCH & PRINT EXECUTION
================================================================================

Batch logic:
  - Match material and color across paid queue.
  - Check combined STL footprint against 220×220mm bed.
  - Present to owner with time savings estimate.
  - Owner approves: `batch ORD-0001 ORD-0003`

Print start — `djinn-confirm-print N`:
  1. Check printer is idle.
  2. Calculate safe park position from gcode bounding box.
  3. Upload gcode to Moonraker.
  4. Start print.
  5. Register park position for failure handling.

Monitoring:
  - Bootstrap mode (first 5 prints): updates every 10%.
  - Normal mode: updates every 25%.
  - 0% for a long time ≠ failure on large files.

================================================================================
7. SHIPPING & CUSTOMER HANDOFF
================================================================================

  ship ORD-0001 usps-priority
  ship ORD-0001              (shows rate comparison first)

Sequence:
  1. Decrypt customer address.
  2. Estimate weight: print grams + 85g packaging.
  3. Fetch USPS / UPS / FedEx rates via EasyPost.
  4. Purchase label, save PDF.
  5. Mark order shipped, DM customer tracking.

================================================================================
8. DASHBOARD, ACCOUNTING, AND INVENTORY
================================================================================

  Dashboard: http://localhost:5000 (password-gated)

  Pages: Queue · Orders · Customers · Finance · Reports

  Accounting: Income statement · Balance sheet · Monthly reports · XLSX/CSV export

  Inventory commands:
    add filament petg black 1000g $28
    inventory
    low stock

  Low-stock alert threshold: 150g

================================================================================
9. PRODUCT LIBRARY & BUSINESS STRATEGY
================================================================================

Highest-value niche: Puffco/dab accessories.
Smoking accessories auto-apply 35% upcharge. PLA hard-blocked for heat-exposed parts.

Current library:
  Puffco/dab    — Proxy tornado recycler, proxy core holster, Puffco cup,
                   quad uptake recycler
  Decorative    — Vase styles, skeleton pieces, spiral pots, flower pot
  Practical     — GoPro tripod, mic stand, GoPro/mic plate
  Custom        — Challenge coin, branded vases, community STLs

Batch efficiency: ~40% time savings vs separate prints. Primary margin multiplier.
Projected: $300–700/month gross at 5–10 orders/month batched.

================================================================================
10. KEY COMMANDS & FILES
================================================================================

  paid ORD-0001
  batch ORD-0001 ORD-0003
  confirm N
  ship ORD-0001 usps-priority
  inventory  /  low stock  /  add filament petg black 1000g $28

Key paths:
  ~/Obsidian/djinn/printer/commissions/price.py
  ~/Obsidian/djinn/printer/shop/db.py
  ~/.local/share/djinn-shop/shop.db
  ~/.config/djinn-shop/secret.key          (chmod 600 — never commit)
  ~/.config/djinn/easypost.env
  ~/.config/djinn/shop.json

================================================================================
11. DJINN DESIGN ORCHESTRATOR
================================================================================

  DesignGenAgent   → Brief → Concept JSON + OpenSCAD
  DesignEditAgent  → SCAD + change → Modified SCAD
  ProtoOptAgent    → SCAD → Proto-light + production STLs
  DOEPrintOptAgent → STL + goal → Taguchi DOE → optimal slicer profile
  PlateNestAgent   → Multiple STLs → Arranged plate STL
  FairPrintAgent   → ProjectState → Commission quote → priced

DOE verified: -76% print time / -51% material vs standard for prototype-fast.

================================================================================
12. SAFETY RULES
================================================================================

  1. No autonomous print starts. `confirm N` always required.
  2. No autonomous orientation changes.
  3. `deny N` blocked while printing.
  4. `djinn-force-cancel` requires owner PIN.
  5. Safe park position calculated before every print.
  6. 0% progress ≠ failure on large files.
  7. Customer PII never in Discord channels.
  8. Do not bypass the DM flow.

================================================================================
13. TROUBLESHOOTING
================================================================================

  SYMPTOM: Quote too low
  FIX:     Re-run with correct job type and richer brief.

  SYMPTOM: Address in channel
  FIX:     Halt order. Purge text. Restart with customer_dm.py only.

  SYMPTOM: Insufficient stock
  FIX:     Check `inventory`, restock, or offer alt material.

  SYMPTOM: No batch proposal
  FIX:     Confirm material+color match and plate area fit.

  SYMPTOM: 0% progress too long
  FIX:     Check Moonraker job state. Do not cancel prematurely.

  SYMPTOM: Ship command fails
  FIX:     Fill `~/.config/djinn/easypost.env` and `~/.config/djinn/shop.json`.

  SYMPTOM: Dashboard won’t load
  FIX:     python3 ~/Obsidian/djinn/printer/shop/dashboard/app.py

================================================================================
14. IMMEDIATE NEXT STEPS
================================================================================

  1. EasyPost API key → `~/.config/djinn/easypost.env`
  2. Shop address → `~/.config/djinn/shop.json`
  3. Run one complete test order end-to-end.
  4. Publish Etsy listings using consult renders as product photos.
  5. Formalize payment beyond current method when ready.

Future packaging path:
  - config.yaml — all IPs/tokens/paths in one file
  - install.sh — guided setup wizard
  - Clean-machine install test (release gate)
  - Target: Etsy 3D print sellers, hobbyist print shop operators

================================================================================
*— Marcus, 2026-06-09*
================================================================================
