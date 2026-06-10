================================================================================
                 FAIRPRINT / TYPHON'S FORGE — COMPLETE OPERATOR MANUAL
        Intake → Consult → Quote → Order → Batch → Print → Ship → Report
================================================================================
Version: 1.0 | Last updated: 2026-06-09 | Maintained by: DrManzo / Marcus

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
orchestrated from Salomon (HP Omen, RTX 5060, 29GB RAM, 192.168.1.225).

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
  │   Discord #3d-printing        Telegram DMs                      │
  │   (file drop + ORDER)         (owner notifications)            │
  └──────────────────┬──────────────────────────────────────────────┘
                     │
  ┌──────────────────▼──────────────────────────────────────────────┐
  │                     GATEWAY LAYER (Salomon)                     │
  │   djinn-discord-gateway       djinn-telegram-gateway            │
  │   djinn-discord-watcher       (owner commands + notifications)  │
  └──────────────────┬──────────────────────────────────────────────┘
                     │
  ┌──────────────────▼──────────────────────────────────────────────┐
  │                    INTELLIGENCE LAYER                           │
  │                                                                 │
  │  intake_agent.py        quote_formatter.py   batch_agent.py    │
  │  (text → brief)         (customer vs owner)  (plate grouping)  │
  │                                                                 │
  │  commissions/           shop/                shipping_agent.py  │
  │   price.py              db.py                (EasyPost labels)  │
  │   brief.py              accounting.py                           │
  │   report.py             customer_dm.py                          │
  │                         inventory.py                            │
  └──────────────────┬──────────────────────────────────────────────┘
                     │
  ┌──────────────────▼──────────────────────────────────────────────┐
  │                    EXECUTION LAYER                              │
  │   djinn-print-consult    djinn-model-slice    djinn-confirm-print│
  │   djinn-print-monitor    djinn-park-calc      djinn-force-cancel │
  └──────────────────┬──────────────────────────────────────────────┘
                     │
  ┌──────────────────▼──────────────────────────────────────────────┐
  │                    HARDWARE LAYER                               │
  │   Calliope (Ender-3 V3 Plus)                                    │
  │   Klipper + Moonraker at 192.168.1.113:7125                     │
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

  Example report format:

    File: proxy_recycler_v2.stl
    Size: 58.2 × 61.4 × 94.1mm  |  Volume: 38.4cm³
    ⚠️  Smoking accessory — PETG or ABS required

    Profiles:
      proto       ~2h 10m   ~28g
      standard    ~3h 45m   ~44g  ◄ recommended
      production  ~5h 20m   ~62g

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

FairPrint is built to prevent undercharging. The engine combines real cost, risk
coverage, enforced minimum margin, and market context.

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
      fair_market *= 1.35                      (35% upcharge)

  express_price  = fair_market × 1.35          (urgent_rush tier)

Machine economics defaults:
  Machine cost rate:        ~$0.20/hr (electricity + depreciation + maintenance)
  Electricity component:     180W/1000 × $0.13/kWh
  Depreciation:              $399 / 5000hr estimated life
  Maintenance:               $0.10/hr

Job-type weighting table:

  ┌─────────────────────────────┬────────┬────────┬────────┐
  │ Job type                    │  Cost  │ Market │  Value │
  ├─────────────────────────────┼────────┼────────┼────────┤
  │ commodity_decor             │  65%   │  30%   │   5%   │
  │ functional_custom_part      │  55%   │  30%   │  15%   │
  │ design_heavy_oneoff         │  40%   │  25%   │  35%   │
  │ urgent_rush                 │  50%   │  20%   │  30%   │
  └─────────────────────────────┴────────┴────────┴────────┘

Customer-facing quote example:

  🖨️  Puffco Proxy Recycler ×2
       PETG · Logo engraving included

  💰 Standard:      $51.34
  ⚡ Express Print: $69.31   (priority turnaround)

  Reply ORDER or EXPRESS to confirm.

Owner-facing Telegram breakdown:

  Cost floor:    $40.80   ← never quote below
  Fair market:   $51.34   ← quoted to customer
  Margin:        64.9%
  Market comps:  4 listings (median $38.50)
  🔥 Smoking accessory — +35% upcharge applied

================================================================================
5. ORDER FLOW
================================================================================

Trigger words:
  ORDER    = standard fulfillment
  EXPRESS  = priority turnaround (× 1.35 pricing)

Order sequence:
  1. Customer confirms quote in Discord.
  2. Bot opens DM: sends payment instructions (Zelle / CashApp).
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
  - Plaintext only: order IDs, amounts, dates, status, margins.

================================================================================
6. BATCH & PRINT EXECUTION
================================================================================

Batching is the primary profit multiplier. The system checks for compatible paid
orders and presents a merge recommendation before committing.

Batch logic:
  - Match material and color across paid queue.
  - Check combined STL footprint against 220×220mm bed.
  - Calculate time savings vs separate prints.
  - Present to owner: "ORD-0001 + ORD-0003 fit one plate. Saves ~2h 40m."
  - Owner approves: `batch ORD-0001 ORD-0003`
  - PlateNestAgent runs: decimates, arranges, produces plate STL.

Print start — `djinn-confirm-print N`:
  1. Check Calliope is idle (not already printing).
  2. Calculate safe park position from gcode bounding box.
  3. Upload gcode to Moonraker via API.
  4. Start print.
  5. Set Klipper park position for use on failure.

Monitoring — `djinn-print-monitor`:
  - Polls Moonraker every 60 seconds.
  - Bootstrap mode (first 5 prints): updates every 10% complete.
  - Normal mode: updates every 25% complete.
  - Progress posted to Discord and Telegram.
  - 0% for a long time ≠ failure on large files (byte-position tracking lag).

================================================================================
7. SHIPPING & CUSTOMER HANDOFF
================================================================================

Trigger in Telegram:
  ship ORD-0001 usps-priority

If carrier is omitted:
  ship ORD-0001   →   shows rate comparison, no label purchased yet.

Example rate comparison:

  📦 Rates for ORD-0001
  usps-groundadvantage      $4.89   3 days
  usps-priority             $9.20   1–3 days  ← recommended
  ups-ground               $11.45   3–7 days

Shipping sequence:
  1. Decrypt customer address from shop.db.
  2. Estimate weight: print grams + 85g packaging.
  3. Fetch USPS / UPS / FedEx rates via EasyPost SDK.
  4. Purchase label.
  5. Save PDF to `~/.local/share/djinn-shop/labels/`.
  6. Mark order shipped in DB.
  7. DM customer with tracking number.
  8. Accounting updates automatically.

================================================================================
8. DASHBOARD, ACCOUNTING, AND INVENTORY
================================================================================

--------------------------------------------------------------------------------
Dashboard
--------------------------------------------------------------------------------

  URL: http://localhost:5000
  Auth: password-gated (set on first run)

  ┌──────────────┬────────────────────────────────────────────────────────────┐
  │ Page         │ Contents                                                   │
  ├──────────────┼────────────────────────────────────────────────────────────┤
  │ Queue (home) │ All pending orders, confirm payment button, status badges  │
  │ Orders       │ Full history, filterable by status, click to expand        │
  │ Customers    │ Ledger per customer, lifetime value, outstanding balance    │
  │ Finance      │ Income statement + live balance sheet (editable inputs)     │
  │ Reports      │ 6-month summary cards + XLSX/CSV export buttons            │
  └──────────────┴────────────────────────────────────────────────────────────┘

--------------------------------------------------------------------------------
Accounting outputs
--------------------------------------------------------------------------------

  Income statement:
    Gross revenue, COGS (material/machine/labor/design), gross profit,
    gross margin %, operating expenses, net income.

  Balance sheet:
    Cash, accounts receivable, inventory value, equipment value
    (straight-line depreciation, 3yr useful life), accounts payable, owner equity.

  Monthly report:
    Jobs completed / failed, failure rate, revenue, COGS, new/repeat customers,
    avg order value, filament used, machine hours.

  Export: CSV and formatted XLSX (multi-sheet workbook) from Reports page.

--------------------------------------------------------------------------------
Inventory tracking
--------------------------------------------------------------------------------

  - Tracks spools by material, color, and brand.
  - Deducts grams automatically after each completed print.
  - Blocks or warns quotes if required grams exceed available stock.
  - Low-stock alert fires at 150g threshold.
  - Inventory value feeds the balance sheet.

  Commands:
    add filament petg black 1000g $28
    inventory
    low stock

================================================================================
9. PRODUCT LIBRARY & BUSINESS STRATEGY
================================================================================

The Puffco and dab accessories are the highest-value catalog items — the primary
niche. The smoking-accessory category auto-applies a 35% upcharge because DDG
market research confirmed the market pays it. PLA is hard-blocked for heat-exposed
parts; PETG enforced — a real differentiator vs. casual sellers.

Current library inventory:

  ┌──────────────────┬─────────────────────────────────────────────────────────┐
  │ Category         │ Items                                                   │
  ├──────────────────┼─────────────────────────────────────────────────────────┤
  │ Puffco/dab       │ Proxy tornado recycler, proxy core holster v9,          │
  │                  │ Puffco cup, quad uptake recycler spec                   │
  │ Decorative       │ 6 vase styles, 3 skeleton hand/rose pieces,             │
  │                  │ 2 spiral pots, tree flower pot                          │
  │ Practical        │ GoPro tripod, mic stand, GoPro/mic plate                │
  │ Custom/branded   │ Typhon's Forge challenge coin, Javi vase,               │
  │                  │ The Terp Tribe camood STL                               │
  └──────────────────┴─────────────────────────────────────────────────────────┘

Illustrative price bands:

  ┌──────────────────────────────┬─────────────────────┬──────────────────────┐
  │ Product                      │ Est. fair market    │ Notes                │
  ├──────────────────────────────┼─────────────────────┼──────────────────────┤
  │ Puffco proxy recycler        │ $45–65              │ PETG + 35% upcharge  │
  │ Puffco cup attachment        │ $35–55              │ same category        │
  │ Decorative vases             │ $15–30              │ commodity_decor      │
  │ Custom coin/badge            │ $60–90 first        │ design amortizes     │
  │                              │ $10–15 batch repeat │ fast on repeat       │
  │ Custom client file           │ $30–80              │ time/material depend │
  └──────────────────────────────┴─────────────────────┴──────────────────────┘

Batch efficiency:
  3 orders separately ≈ 8h machine time.
  Same 3 orders batched ≈ 5h. Each customer billed independently.
  That ~40% time savings is the real margin multiplier.

Projected revenue at 5–10 orders/month batched: $300–700/month gross.
The 30% minimum margin is enforced in code — impossible to accidentally underprice.

Promotion strategy:
  1. Reddit — r/3Dprinting, r/SideProject, r/Entrepreneur (zero cost, immediate)
  2. TikTok / Reels — Discord demo: file drop → renders → quote in 30 seconds
  3. YouTube — "I Built an AI Print Shop" series (long-term SEO)
  4. Puffco / terp community — r/puffco, Puffco Discord servers

Content assets already available:
  - Git history of the full build
  - COMMS.md inter-agent conversation thread
  - Real Discord bot interaction recordings
  - djinn-print-consult renders (front, side, overhang map)
  - Dashboard screenshots (queue, orders, finance)
  - Batch proposal messages with time savings calculations

================================================================================
10. KEY COMMANDS & FILES
================================================================================

Owner Telegram/Discord commands:
  paid ORD-0001
  batch ORD-0001 ORD-0003
  confirm N
  ship ORD-0001 usps-priority
  ship ORD-0001                  (shows rate comparison first)
  inventory
  low stock
  add filament petg black 1000g $28

CLI tools at ~/.local/bin/:
  djinn-print-consult            mesh analysis + renders + dry-run slice
  djinn-model-slice              exact slice run with user settings
  djinn-confirm-print            park calc + Moonraker upload + start
  djinn-print-monitor            progress polling + notifications
  djinn-print-quote              pricing CLI
  djinn-design                   six-agent design/manufacturing orchestrator
  djinn-shop-deploy              one-command full shop installer

Key file paths:
  ~/Obsidian/djinn/printer/commissions/price.py
  ~/Obsidian/djinn/printer/shop/db.py
  ~/Obsidian/djinn/printer/shop/accounting.py
  ~/Obsidian/djinn/printer/shop/dashboard/app.py
  ~/.local/share/djinn-shop/shop.db
  ~/.config/djinn-shop/secret.key              (chmod 600 — never commit)
  ~/.local/share/djinn-shop/exports/
  ~/.local/share/djinn-shop/labels/
  ~/.config/djinn/easypost.env
  ~/.config/djinn/shop.json                    (shop address + config)

Database tables:
  customers, orders, order_items, quotes, ledger, invoices,
  income_statements, balance_sheets, monthly_reports, dm_sessions,
  filament_inventory, filament_usage_log, shipments, tracking_events

================================================================================
11. DJINN DESIGN ORCHESTRATOR (djinn-design)
================================================================================

For original model work, djinn-design runs a six-agent pipeline.

  ┌───────────────────┬────────────────────────────┬────────────────────────────┐
  │ Agent             │ Input                      │ Output                     │
  ├───────────────────┼────────────────────────────┼────────────────────────────┤
  │ DesignGenAgent    │ Brief (text)               │ Concept JSON + OpenSCAD    │
  │ DesignEditAgent   │ Existing SCAD + change req │ Modified SCAD              │
  │ ProtoOptAgent     │ SCAD                       │ Proto-light + production   │
  │ DOEPrintOptAgent  │ STL + optimization goal    │ Taguchi DOE → optimal      │
  │                   │                            │ slicer profile             │
  │ PlateNestAgent    │ Multiple STLs              │ Arranged plate STL         │
  │ FairPrintAgent    │ ProjectState               │ Commission quote → priced  │
  └───────────────────┴────────────────────────────┴────────────────────────────┘

DOEPrintOptAgent eliminates test prints. It runs Taguchi factorial design to find
optimal settings mathematically. Verified result: -76% print time / -51% material
vs standard settings for prototype-fast profile.

================================================================================
12. SAFETY RULES
================================================================================

  1. No autonomous print starts. `confirm N` is always required — hard gated.

  2. No autonomous orientation changes. Agents are forbidden from changing model
     orientation without explicit owner instruction.

  3. `deny N` is blocked while printing. Gateway-level rejection.

  4. `djinn-force-cancel` requires owner PIN only. No agent can bypass.

  5. Safe park position must be calculated from gcode bounds before every job.

  6. 0% progress ≠ failure. Byte-position tracking means large files can show
     0% for hours. Confirm Moonraker job state before treating as stuck.

  7. Customer PII off Discord. Address collected via DM → encrypted DB.
     Never log, echo, or post address to any Discord channel.

  8. Do not bypass the DM flow. Manual address collection outside customer_dm.py
     is a privacy violation. Stop and restart properly if this happens.

================================================================================
13. TROUBLESHOOTING
================================================================================

  SYMPTOM: Quote looks too low
  CAUSE:   Wrong job type, missing market comps, or underspecified labor/design
  FIX:     Re-run quote with corrected classification and richer brief.
           Check owner Telegram output for cost floor vs fair market gap.

  SYMPTOM: Customer address appeared in channel
  CAUSE:   DM flow was bypassed
  FIX:     Halt the order. Purge exposed text. Restart with customer_dm.py only.

  SYMPTOM: Quote blocked — insufficient stock
  CAUSE:   Required grams exceed available spool inventory
  FIX:     Check `inventory` and restock. Offer alt material/color if possible.

  SYMPTOM: Batch proposal never appears
  CAUSE:   Orders differ by material/color, or combined footprint exceeds bed
  FIX:     Confirm material+color match in paid queue. Check plate area estimate.

  SYMPTOM: Large print shows 0% for extended period
  CAUSE:   Byte-position tracking lag for large gcode files
  FIX:     Check Moonraker job state directly. Do not assume failure prematurely.

  SYMPTOM: Ship command fails
  CAUSE:   EasyPost API key or shop address missing
  FIX:     Fill `~/.config/djinn/easypost.env` and `~/.config/djinn/shop.json`

  SYMPTOM: Customer tracking DM not sent
  CAUSE:   Label purchase succeeded but notification failed
  FIX:     Confirm order status in DB. Check bot health. Resend tracking manually.

  SYMPTOM: Dashboard won't load
  CAUSE:   Flask app not running
  FIX:     python3 ~/Obsidian/djinn/printer/shop/dashboard/app.py

  SYMPTOM: XLSX export fails or produces blank file
  CAUSE:   No orders in date range, or openpyxl not installed
  FIX:     Confirm order data exists. pip install openpyxl if missing.

================================================================================
14. IMMEDIATE NEXT STEPS
================================================================================

Required before fully live operation:

  1. EasyPost API key → `~/.config/djinn/easypost.env`
     (free account at easypost.com → API key)

  2. Shop address → `~/.config/djinn/shop.json`
     (return address used on all shipping labels)

  3. Run one complete test order through the full pipeline end-to-end.

  4. Publish Etsy listings for existing Puffco pieces.
     Use renders from djinn-print-consult as product photos.

  5. Payment formalization — Zelle/CashApp works today. Stripe unlocks lower
     friction and potential Etsy-native payment later.

Future: software product packaging path
  - Pull all hardcoded IPs/tokens/paths into `config.yaml`
  - Write guided `install.sh` setup wizard
  - Test on a clean machine (this is the release gate)
  - Landing page + GitHub release
  - Target: Etsy 3D print sellers, hobbyist print shop operators
  - Estimated: 4–6 weeks to genericize from current state

================================================================================
SOURCE DOCUMENTS ABSORBED
================================================================================

  djinn/printer/DJINN-3D-PRINT-PIPELINE.md   — full technical architecture,
                                               pricing formula, workflow, safety
  djinn/printer/TYPHONS-FORGE-STRATEGY.md    — product library, profitability,
                                               promotion strategy, next steps

================================================================================
*— Marcus, 2026-06-09*
================================================================================
