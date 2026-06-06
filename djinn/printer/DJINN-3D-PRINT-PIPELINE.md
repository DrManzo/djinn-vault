# Djinn 3D Print Pipeline
### Technical Overview — Typhon's Forge

**Version:** 1.0  
**Date:** 2026-05-31  
**Author:** Javier (DrManzo) — Architecture by Claude, Salomon, Marcus  
**Hardware:** Calliope (Ender-3 V3 Plus) at 192.168.1.113  
**Platform:** Fedora Linux / Salomon (HP Omen, RTX 5060, 29GB RAM)

---

## What It Is

A fully automated, AI-mediated 3D print shop operating system. A customer drops a file in Discord or describes what they want. The system analyzes it, generates renders, quotes the commission with live market research, collects payment, manages the print queue, batches compatible jobs, monitors the print, and generates a shipping label — all with minimal operator input.

**No spreadsheets. No manual quoting. No separate slicer GUI. No copy-pasting tracking numbers.**

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CUSTOMER LAYER                           │
│   Discord #3d-printing        Telegram DMs                      │
│   (file drop + ORDER)         (notifications)                   │
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
```

---

## The Full Workflow

### 1. File Intake
Customer drops `.stl` or `.3mf` in `#3d-printing` or describes what they want in plain text.

**If file:** `djinn-discord-watcher` detects within 20 seconds.  
**If text:** `intake_agent.py` parses via regex + qwen2.5:7b fallback → extracts piece name, quantity, material, customizations, smoking accessory flag.

### 2. Print Consult
`djinn-print-consult` runs automatically:
- Downloads and analyzes mesh (dimensions, volume, overhangs via trimesh)
- Generates 3 renders: front, side, overhang map (red = needs support) via PrusaSlicer + Xvfb
- Dry-runs PrusaSlicer to get real time and filament estimates
- Pulls prior print history for this model (keyed by file hash)
- Posts full consult report to Discord + Telegram

**Consult report includes:**
```
File: proxy_recycler_v2.stl
Size: 58.2 × 61.4 × 94.1mm  |  Volume: 38.4cm³
⚠️  Smoking accessory — PETG or ABS required

Profiles:
  proto       ~2h 10m   ~28g
  standard    ~3h 45m   ~44g  ◄ recommended
  production  ~5h 20m   ~62g
```

### 3. Quote Generation
`commissions/price.py` runs the pricing formula:

```
base_cost       = material + labor + depreciation + maintenance + electricity + extras
risk_adjusted   = base_cost / success_rate (0.92)
cost_floor      = risk_adjusted × (1 + minimum_margin 0.30)
fair_market     = wc×cost_floor + wm×market_median + wv×(cost_floor + value_premium)
```

**Job type weights:**
| Type | Cost | Market | Value |
|---|---|---|---|
| commodity_decor | 65% | 30% | 5% |
| functional_custom_part | 55% | 30% | 15% |
| design_heavy_oneoff | 40% | 25% | 35% |
| urgent_rush | 50% | 20% | 30% |

**Market search:** DuckDuckGo → Etsy/specialist retailers → true weighted median (not mean — outlier resistant). Auto-detects smoking accessories → category-specific queries → 35% upcharge applied.

**What the customer sees:**
```
🖨️  Puffco Proxy Recycler  ×2
     PETG · Logo engraving included

💰 Standard:      $51.34
⚡ Express Print: $69.31   (priority turnaround)

Reply ORDER or EXPRESS to confirm.
```

**What the owner sees (Telegram only):**
```
Cost floor:    $40.80   ← never quote below
Fair market:   $51.34   ← quoted to customer
Margin:        64.9%
Market comps:  4 listings (median $38.50)
🔥 Smoking accessory — +35% upcharge applied
```

### 4. Order Flow
Customer replies `ORDER` or `EXPRESS` in Discord.

Bot DMs customer:
- Payment instructions (Zelle + CashApp)
- Requests: name, shipping address, special notes
- 48-hour privacy cleanup notice

Customer info stored encrypted in `shop.db` (Fernet column-level encryption). Address never appears in any Discord channel. Owner notified via Telegram with full decrypted summary.

Owner confirms payment: `paid ORD-0001` → order advances → customer notified.

### 5. Plate Batching
`batch_agent.py` scans paid queue before each print run:
- Groups jobs by material + color
- Checks if combined footprint fits on 220×220mm bed
- Proposes batch to owner: "ORD-0001 + ORD-0003 fit on one plate. Saves ~2h 40m."
- Owner approves: `batch ORD-0001 ORD-0003` → PlateNestAgent runs

### 6. Print Execution
`djinn-confirm-print N`:
1. Checks Calliope is not already printing
2. Calculates safe park position from gcode bounding box
3. Uploads gcode to Moonraker API
4. Starts print
5. Sets Klipper park position (used on failure)

`djinn-print-monitor` polls Moonraker every 60 seconds:
- Bootstrap mode (first 5 prints): updates every 10%
- Normal mode: updates every 25%
- Sends progress to Discord + Telegram

**Safety hard rules:**
- `deny N` is blocked while printing
- `force-cancel` requires PIN only the owner knows
- No autonomous orientation changes ever
- Nothing starts without explicit `confirm N`

### 7. Shipping
Owner sends: `ship ORD-0001 usps-priority` in Telegram.

`shipping_agent.py` via EasyPost SDK:
1. Decrypts customer address from shop.db
2. Estimates package weight (print grams + 85g packaging)
3. Gets rates from USPS / UPS / FedEx
4. Purchases label
5. Downloads PDF to `~/.local/share/djinn-shop/labels/`
6. Updates order to shipped
7. DMs customer with tracking number

If owner sends `ship ORD-0001` with no carrier: rate comparison shown first.

```
📦 Rates for ORD-0001
usps-groundadvantage      $4.89  3 days
usps-priority             $9.20  1–3 days  ← recommended
ups-ground               $11.45  3–7 days
```

---

## The Shop System

### Database (`shop.db`)
SQLite at `~/.local/share/djinn-shop/shop.db`.  
Encryption key at `~/.config/djinn-shop/secret.key` (Fernet, auto-generated, chmod 600).

**Encrypted fields:** customer name, shipping address, email, Discord contact.  
**Plaintext:** order IDs, amounts, dates, status, margins — all queryable.

**Tables:** `customers`, `orders`, `order_items`, `quotes`, `ledger`, `invoices`, `income_statements`, `balance_sheets`, `monthly_reports`, `dm_sessions`, `filament_inventory`, `filament_usage_log`, `shipments`, `tracking_events`

### Accounting (`accounting.py`)
Spec delivered by Marcus (Perplexity). Built by Claude.

**Income statement** — per period: gross revenue, COGS (material/machine/labor/design), gross profit, gross margin %, operating expenses, net income.

**Balance sheet** — snapshot: cash, accounts receivable, inventory value, equipment value (straight-line depreciation, 3yr useful life), accounts payable, owner's equity.

**Monthly report** — jobs completed/failed, failure rate, revenue, COGS, new/repeat customers, avg order value, filament used, machine hours.

**Export:** CSV + formatted XLSX (multi-sheet workbook). One click in dashboard.

### Dashboard (`dashboard/app.py`)
Flask web app, `http://localhost:5000`, password-gated, Bootstrap 5.

| Page | Shows |
|---|---|
| **Queue** (home) | All pending orders, confirm payment button, status badges |
| **Orders** | Full order history, filterable by status, click to expand |
| **Customers** | Ledger per customer, lifetime value, outstanding balance |
| **Finance** | Income statement + live balance sheet (editable cash/inventory inputs) |
| **Reports** | 6-month cards + XLSX/CSV export buttons |

### Filament Inventory (`inventory.py`)
- Tracks spools by material + color + brand
- Deducts grams after each print automatically
- Checks availability before quoting: "Only 120g of black PETG — job needs 150g"
- Low stock alerts at 150g threshold
- Feeds inventory value into balance sheet
- Commands: `add filament petg black 1000g $28`, `inventory`, `low stock`

---

## Agent Roles

| Agent | Platform | Lane |
|---|---|---|
| **Claude** | Anthropic API | Architecture, builds new components, session reports |
| **Salomon** | Local Ollama (qwen2.5:7b, deepseek-r1:7b) | Daily ops, Discord/Telegram gateways, print execution, deployment |
| **Typhon** | Local Ollama + storage | Backup, sync, Typhon's Studio |
| **Marcus** | Perplexity AI (Sonnet 4.6) | Research, code audits, spec delivery (accounting, EasyPost) |

**Coordination:** All agents communicate via `~/Obsidian/djinn/communications/COMMS.md` (append-only message thread). Every build produces a session report in `djinn/logs/reports/`. Every bug logged in `bugs.md`. All committed and pushed to GitHub.

---

## Manufacturing Orchestrator (djinn-design)

Six-agent pipeline for original design work:

| Agent | Input | Output |
|---|---|---|
| **DesignGenAgent** | Brief (text) | Concept JSON + parametric OpenSCAD |
| **DesignEditAgent** | Existing SCAD + change request | Modified SCAD |
| **ProtoOptAgent** | SCAD | Prototype-light + production STLs |
| **DOEPrintOptAgent** | STL + optimization goal | Taguchi DOE grid → optimal slicer profile |
| **PlateNestAgent** | Multiple STLs | Decimated + arranged plate STL |
| **FairPrintAgent** | ProjectState | Commission quote → advances to `priced` |

DOEPrintOptAgent eliminates test prints — runs Taguchi factorial design to find optimal settings mathematically. Verified: -76% print time / -51% material vs standard settings for prototype-fast profile.

---

## Technology Stack

| Component | Technology |
|---|---|
| OS | Fedora Linux |
| Printer firmware | Klipper + Moonraker |
| Slicer | **Standard:** OrcaSlicer 2.3.2 — **CLI:** PrusaSlicer (legacy/diagnostic) |
| Local LLMs | Ollama (qwen2.5:7b, deepseek-r1:7b, phi4:14b, llama3.2-vision:11b) |
| Premium AI | Claude (Anthropic API), Perplexity (Marcus) |
| Database | SQLite + Fernet encryption |
| Web dashboard | Flask + Bootstrap 5 |
| Shipping | EasyPost SDK (USPS / UPS / FedEx) |
| Market data | DuckDuckGo Search (DDG) |
| 3D processing | trimesh, pymeshlab, OpenSCAD |
| Messaging | Discord (discord.py), Telegram (python-telegram-bot) |
| Vault/sync | Obsidian + git + rclone (GDrive) |
| Notifications | systemd timers + Telegram bot |

---

## File Structure

```
~/Obsidian/djinn/printer/
├── commissions/
│   ├── price.py          — Core pricing engine (DDG market search, smoking detection)
│   ├── brief.py          — Input validation + smoking routing
│   └── report.py         — Telegram / terminal / Markdown / JSON output
│
├── shop/
│   ├── db.py             — SQLite + Fernet encryption, all CRUD
│   ├── accounting.py     — Income statement, balance sheet, monthly reports, XLSX export
│   ├── quote_formatter.py— Customer view (clean) vs owner view (full)
│   ├── intake_agent.py   — Customer text → print brief (regex + qwen2.5:7b)
│   ├── customer_dm.py    — ORDER flow, DM collection, 48h cleanup
│   ├── batch_agent.py    — Queue batching by material + color
│   ├── inventory.py      — Filament spool tracking
│   ├── shipping_agent.py — EasyPost label purchase + tracking
│   └── dashboard/
│       ├── app.py        — Flask owner dashboard
│       └── templates/    — 5 pages (queue, orders, customers, finance, reports)
│
└── agent/orchestrator/
    ├── orchestrator.py
    └── agents/
        ├── design_gen.py, design_edit.py, proto_opt.py
        ├── doe_opt.py, plate_nest.py, price.py

~/.local/bin/
├── djinn-print-consult   — Mesh analysis + renders + dry-run slice
├── djinn-model-slice     — PrusaSlicer with exact user settings
├── djinn-confirm-print   — Park calc + Moonraker upload + start
├── djinn-print-monitor   — Progress polling + notifications
├── djinn-print-quote     — Commission pricing CLI
├── djinn-design          — 6-agent manufacturing orchestrator
└── djinn-shop-deploy     — Single-command full shop system installer

~/.local/share/djinn-shop/
├── shop.db               — Encrypted SQLite database
├── exports/              — CSV + XLSX financial reports
└── labels/               — Downloaded shipping label PDFs
```

---

## Pricing Formula — Full Detail

```python
# Calliope (Ender-3 V3 Plus) defaults
machine_cost_per_hour = (180W/1000 × $0.13/kWh)    # electricity
                      + ($399 / 5000h)               # depreciation
                      + $0.10/h                      # maintenance
                      = ~$0.20/hr

# Per-job cost
material_cost    = (spool_cost / spool_weight_g) × used_g × 1.10 (waste buffer)
machine_cost     = print_hours × $0.20
labor_cost       = ((prep_min + postprocess_min + design_min) / 60) × $20/hr
extras           = packaging ($0.50) + hardware + shipping

base_cost        = material + machine + labor + extras
risk_adjusted    = base_cost / 0.92  (failure coverage)
cost_floor       = risk_adjusted × 1.30  (30% minimum margin)

market_median    = true weighted median of DDG-fetched Etsy listings
                   (sorted ascending, cumulative weight ≥ 50%)

fair_market      = wc×cost_floor + wm×market_median + wv×(cost_floor + value_premium)

if smoking_accessory:
    fair_market  *= 1.35  (35% upcharge)

express_price    = fair_market × 1.35  (urgent_rush tier)
premium_ceiling  = fair_market × 1.15
```

---

## Safety Architecture

| Rule | Implementation |
|---|---|
| No autonomous print start | `confirm N` required — hard gated |
| No cancel without PIN | `djinn-force-cancel` requires owner PIN |
| No autonomous orientation change | Hard rule in AGENTS.md — agents enforced |
| `deny N` blocked while printing | Gateway-level rejection |
| Safe park on failure | Park position calculated from gcode bounding box before every job |
| 0% progress ≠ failure | Byte-position tracking — large files show 0% for hours |
| Customer PII off Discord | Address collected in DM → encrypted DB → Telegram only |
| DM cleanup | Bot deletes its own messages after 48h |

---

## What's Deployed vs What's Next

### Deployed ✅
- Full print pipeline (consult → slice → confirm → monitor → complete)
- FairPrintAgent pricing (market search, smoking detection, job type weighting)
- Customer order flow (Discord ORDER → DM → payment → address → queue)
- Plate batching by material + color
- Filament inventory tracking
- Full accounting (income statement, balance sheet, monthly reports)
- Owner dashboard (localhost:5000)
- EasyPost shipping integration
- Encrypted SQLite database

### Immediate next steps
- EasyPost API key (free at easypost.com) → `~/.config/djinn/easypost.env`
- Real shop address → `~/.config/djinn/shop.json`
- Run first test order through full pipeline

### Packaging for other users
- `config.yaml` — all IPs, tokens, pricing config in one file
- `install.sh` — setup wizard → writes config → installs services
- Generic identity templates (remove personal data)
- Test on clean machine
- Estimated: 4–6 weeks additional work

---

## Key Numbers

| Metric | Value |
|---|---|
| Printer bed size | 220 × 220 × 250mm |
| Machine cost rate | ~$0.20/hr (electricity + depreciation + maintenance) |
| Default labor rate | $20.00/hr |
| Success rate assumption | 92% (8% failure coverage built into floor price) |
| Minimum margin | 30% |
| Smoking accessory upcharge | 35% |
| Express Print premium | 35% |
| Low stock alert threshold | 150g |
| DM privacy cleanup | 48 hours |
| Print monitor interval | 60 seconds |
| Dashboard URL | http://localhost:5000 |

---

## Inter-Agent Communication

All agents coordinate through `~/Obsidian/djinn/communications/COMMS.md` — an append-only message thread committed to GitHub after each session. Format: timestamp, from, to, subject, body, signature.

Every session produces:
- Session report at `djinn/logs/reports/YYYY-MM-DD_<slug>.md`
- Build log entry at `djinn/logs/build-log.md`
- Decision log entry (if architectural decision made)
- COMMS.md append
- `git push` to github.com/DrManzo/djinn-vault

No institutional knowledge is lost. Every decision, every bug, every build is documented.

---

*Built by Javier (DrManzo) with Claude (Anthropic), Salomon (local Ollama), and Marcus (Perplexity).*  
*Vault: github.com/DrManzo/djinn-vault*  
*— 2026-05-31*
