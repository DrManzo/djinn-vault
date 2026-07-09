# Djinn 3D Print Pipeline — Capabilities

**What this system can do that nothing else does.**

---

## Core Capability: Zero-Touch Order Fulfillment

A customer drops a 3D model file in Discord. Without any operator input, the system:

1. Analyzes the mesh — dimensions, volume, overhangs, bed fit
2. Generates 3 photorealistic renders (front, side, overhang map)
3. Runs a real slicer dry-run to get exact time and filament estimates
4. Searches the live market (Etsy + specialist retailers) for comparable prices
5. Generates a commission quote using a weighted formula (cost + market + value)
6. Posts the quote to Discord — clean retail format for the customer

The operator never touched the computer.

---

## Capability: Market-Aware Commission Pricing

Not flat rates. Not guesswork.

- Searches DuckDuckGo for live Etsy listings of comparable items
- Computes a **true weighted median** (not a mean — outlier resistant)
- Blends cost-floor, market median, and value premium by job type
- Automatically detects smoking accessories (puffco, dab, rig, bong, terp...) → applies 35% market upcharge — because the market pays it
- Library check: if the design already exists in vault → design cost = $0
- Shows customer: item, price, Express option — nothing else
- Shows owner: full cost breakdown, margin %, market comps, smoking flag — everything hidden from customer

**Example output for a Puffco Proxy Recycler:**
```
Customer sees:          Owner sees:
$51.34 standard         Cost floor:    $40.80
$69.31 express          Margin:        64.9%
                        Market comps:  4 listings ($38.50 median)
                        🔥 +35% smoking upcharge applied
```

---

## Capability: Intelligent Intake

Customers don't need to fill out a form. They just talk.

> "I want a puffco attachment like a water recycler, 3 of them, with my logo"

The system extracts: item type, quantity (3), customization (logo engraving), job type (functional_custom_part), material enforcement (PETG — smoking item), calculates logo design time, adds it to the quote. Asks one clarifying question if needed (logo file or design work?).

Smoking keywords are detected automatically. PETG/ABS is enforced — PLA is blocked for heat-exposed parts.

---

## Capability: Full Order Flow Without Operator Presence

When a customer says ORDER:

1. Bot DMs the customer privately — payment instructions (Zelle + CashApp)
2. Collects: name, shipping address, special requests — all in the DM
3. Stores everything encrypted in the local database (AES-256 equivalent) — address never touches a Discord channel
4. Operator gets a Telegram notification with the full decrypted summary
5. Operator confirms payment received with one message: `paid ORD-0001`
6. Customer is automatically notified. Order advances.
7. DM conversation auto-deletes after 48 hours for customer privacy.

---

## Capability: Plate Batching by Material and Color

Before starting any print run, the system scans the queue for compatible jobs.

If two paid orders use the same material and color and their parts fit on the 220×220mm bed together — the system proposes a batch:

> "ORD-0001 + ORD-0003 fit on one plate — PETG Black, 4 parts. Saves ~2h 40m vs printing separately."

Each customer still has their own order record, their own price, their own tracking number. The batching is purely operational efficiency for the operator. Accepting a batch triggers the PlateNestAgent — which decimates, arranges, and exports the combined plate STL automatically.

---

## Capability: Print Safety Architecture

The system enforces hard rules that cannot be overridden by any agent:

- **Nothing prints without `confirm N`** — explicit operator approval required every time
- **No autonomous cancellation** — `force-cancel` requires a PIN only the operator knows
- **No orientation changes** — the operator owns model orientation. Always.
- **0% progress ≠ failure** — large gcode files legitimately show 0% for hours (byte-position tracking). The system will not cancel based on progress alone.
- **Safe park on failure** — park position is calculated from the gcode bounding box before every job, set in Klipper before the first layer

The physical touchscreen on the printer is always the highest authority. Nothing the software does can override it.

---

## Capability: One-Command Shipping Labels

Print completes. Operator sends one Telegram message:

`ship ORD-0001 usps-priority`

The system:
- Decrypts the customer's address from the database
- Estimates package weight (print grams + packaging)
- Purchases a USPS Priority label via EasyPost
- Downloads the PDF label to the local drive
- Updates the order to shipped
- DMs the customer their tracking number automatically

If the operator wants to compare carriers first — `ship ORD-0001` with no service shows a rate table:
```
usps-groundadvantage   $4.89   3 days
usps-priority          $9.20   1–3 days  ← recommended
ups-ground            $11.45   3–7 days
fedex-home            $13.20   1–5 days
```

Supports USPS, UPS, FedEx, DHL through one API key.

---

## Capability: Real Business Accounting

Not a spreadsheet. A proper accounting system.

**Income Statement** — per period: revenue, COGS broken out by material/machine/labor/design, gross profit, gross margin %, platform fees, supply expense, net income.

**Balance Sheet** — snapshot: cash on hand, accounts receivable, filament inventory value, printer book value (straight-line depreciation, 3-year life), accounts payable, owner's equity.

**Monthly Report** — jobs completed, failure rate, revenue, avg order value, new/repeat customers, filament consumed, machine hours.

All of this exports to a formatted Excel workbook (multi-sheet) or CSV with one click on the dashboard.

---

## Capability: Filament Inventory Awareness

The system tracks every spool.

- Log a new spool: `add filament petg black 1000g $28`
- Grams are deducted automatically after each print
- Before quoting, the system checks if the job can be fulfilled: "Only 120g of black PETG on hand — job needs 150g"
- Customers see available colors when ordering
- Low-stock alerts fire automatically at 150g threshold
- Inventory value feeds directly into the balance sheet

---

## Capability: Original Design Pipeline

For customers who don't have a file — the system can generate the design.

Six agents in sequence:

| Step | What happens |
|---|---|
| **DesignGen** | Interview → concept JSON → parametric OpenSCAD generated by AI |
| **DesignEdit** | Modify existing design without rebuilding from scratch |
| **ProtoOpt** | Renders prototype-light and production-ready STLs |
| **DOEPrintOpt** | Taguchi factorial design → optimal slicer profile **without test prints** |
| **PlateNest** | Decimate + arrange multiple parts → single plate STL |
| **FairPrint** | Reads all prior data → generates commission quote |

The DOEPrintOptAgent eliminates test prints entirely. It runs a mathematical optimization across layer height, infill, speed, and temperature to find the optimal settings before a single gram of filament is used.

---

## Capability: Institutional Memory

The system remembers every print.

Each model is identified by file hash. Every piece of feedback the operator logs after a print:

> `feedback 1 slight warping on bottom-left corner, increase brim next time`

...is stored and surfaced the next time that exact model is printed:

```
─── Prior print notes ────────────────────
[2026-05-28] production / petg / balanced
  → "slight warping on bottom-left corner, increase brim"
```

Over time this builds a tuned knowledge base per model. No print shop — manual or automated — has this. Every repeat job gets smarter.

---

## Capability: Multi-Agent Coordination

Four agents with defined lanes, one shared communication channel.

| Agent | Role |
|---|---|
| **Claude** (Anthropic) | Architecture, complex builds, session reports |
| **Salomon** (local Ollama) | Daily ops, Discord/Telegram, print execution |
| **Typhon** (storage node) | Backup, sync, studio pipeline |
| **Marcus** (Perplexity) | Research, code audits, spec delivery |

All coordination happens through a shared message thread (`COMMS.md`) committed to GitHub. Every session produces a written report. Every bug is logged. No institutional knowledge is ever lost.

---

## What This Replaces

| Before | After |
|---|---|
| Open slicer, set settings manually, estimate time | Drop file → consult report auto-generated |
| Google "what should I charge for this" | Market search runs automatically, margin calculated |
| Copy-paste customer address into USPS.com | One Telegram command → label downloaded |
| Excel spreadsheet for orders | SQLite database, full accounting, XLSX export |
| Remember last print settings for this file | Prior notes shown in every future consult |
| Check Discord DMs, check Telegram, check printer | One dashboard at localhost:5000 |
| Four separate tools | One system |

---

## Numbers

| Metric | Value |
|---|---|
| Time from file drop to consult report | < 60 seconds |
| Minimum margin enforced | 30% |
| Smoking accessory upcharge | 35% |
| Market comparable sources | Etsy + 7 specialist retailers |
| Pricing formula inputs | 12 variables (material, time, labor, market, risk, job type...) |
| DM privacy cleanup | 48 hours |
| Shipping carriers supported | USPS, UPS, FedEx, DHL (100+ via EasyPost) |
| Database encryption | AES-128 (Fernet) on all PII fields |
| Printer failure coverage | 8% built into every quote |

---

*Typhon's Forge — Javier (DrManzo)*  
*github.com/DrManzo/djinn-vault*
