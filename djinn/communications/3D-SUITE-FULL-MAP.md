---
title: 3D Suite — Full Architecture Map (Root to Leaf)
agent: Claude
date: 2026-05-31
tags: [djinn, architecture, 3d-printing, manufacturing, shop]
related: [[AGENT_STACK_SPEC]] | [[QUEUE]] | [[build-log]] | [[decision-log]]
---

# 3D Suite — Full Architecture Map

**Written:** 2026-05-31  
**Author:** Claude  
**Scope:** Every layer of the 3D printing system — entry points, agent pipeline, shop ops, data flow, file paths, and the glue between them. From root (CLI) to leaf (individual functions).

---

## System Overview

The 3D suite has two distinct layers that meet at the moment a model is ready to sell:

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: Manufacturing Pipeline                        │
│  Brief → Design → Edit → Optimize → DOE → Plate → Price│
└───────────────────────────┬─────────────────────────────┘
                            │ quote + plate STL
┌───────────────────────────▼─────────────────────────────┐
│  LAYER 2: Shop Operations                               │
│  Order intake → Customer DM → Batch → Ship → Accounting │
└─────────────────────────────────────────────────────────┘
```

Printer hardware: **Calliope** (Ender-3 V3 Plus), controlled via Klipper/Moonraker on Salomon.  
All code lives in: `~/Obsidian/djinn/printer/`  
Job persistence: `~/.local/share/djinn/print-queue.json`

---

## Root — Entry Points

### `djinn-design` (CLI)
**Path:** `~/.local/bin/djinn-design`  
**Source:** `djinn/printer/agent/orchestrator/cli.py`  
**Venv:** `~/.venvs/djinn-orchestrator` (Python 3.11)  
**Packages:** anthropic, pyDOE2, trimesh, pymeshlab, scipy, ollama

This is the single entry point for the entire manufacturing pipeline. It parses CLI args and routes to the appropriate agent or runs the full pipeline with `--full`.

**Commands:**
```bash
djinn-design "make a snap-fit enclosure, PETG, 80×60×30mm"     # new design
djinn-design --job 3 --edit "move holes 5mm inward"             # edit existing
djinn-design --job 3 --optimize                                  # generate variants
djinn-design --job 3 --doe prototype_fast                        # slicer optimization
djinn-design --job 3 --doe prototype_cheap
djinn-design --job 3 --doe balanced
djinn-design --job 3 --plate                                     # arrange plate
djinn-design --job 3 --plate --items '[{"stl":"a.stl","qty":2}]'
djinn-design --job 3 --full                                      # run full pipeline
djinn-design --status                                            # show queue
```

**Printer profile defaults (hardcoded):**
- Model: Ender-3 V3 Plus
- Enclosure: false (add `--enclosure` flag if box added)
- Hot-end sock: true (add `--no-sock` flag if removed)
- Bed insulated: false

---

## Layer 1: Manufacturing Pipeline

### Orchestrator
**Path:** `djinn/printer/agent/orchestrator/orchestrator.py`

The router. Classifies user intent into one of: `new_design | edit_design | optimize | doe | plate | price | status | unknown`. Classification uses an LLM prompt (minimal — just JSON, max 80 tokens). Routes to the correct agent. When `auto_advance=True` (from `--full`), runs the entire pipeline sequentially without stopping.

**Intent → Agent routing:**
```
new_design   → design_gen.run()
edit_design  → design_edit.run()
optimize     → proto_opt.run()
doe          → doe_opt.run()
plate        → plate_nest.run() → makers_mark.run()   (both run in the same "plate" step; see Agent 6)
price        → price.run()
engrave      → engrave.run()   (on-demand, any stage with an existing model — see On-Demand Agent below)
status       → _show_queue()
```

**Status machine (linear progression):**
```
design_gen → design_edit → proto_opt → doe_opt → plate_nest → priced → pending → printing
```
*(MakersMarkAgent runs inside the `plate_nest` step, before the status advances to `priced` — it does not get its own status value. EngravingAgent is intent-routed on demand and does not participate in this linear progression at all.)*

**Note (2026-07-13):** the routing table and status machine above were missing `makers_mark` and `engrave` entirely until this fix — both are real, currently-running pipeline stages, found via `djinn-doc-check`-style audit of the orchestrator code vs. this doc. See Agent 6 and the On-Demand Agent section below. This doc also still uses pre-restructure paths (`djinn/printer/...`) throughout, which is a separate staleness issue not addressed in this pass.

---

### ProjectState (Shared Data Object)
**Path:** `djinn/printer/agent/orchestrator/project_state.py`  
**Persisted to:** `~/.local/share/djinn/print-queue.json`

The spine of the pipeline. Every agent reads from it and writes back to it. One object travels through all six agents, accumulating data at each stage.

**Fields by phase:**

| Phase | Fields |
|-------|--------|
| Identity | `id`, `status`, `added`, `note` |
| Design | `brief`, `concept`, `source_scad`, `source_stl` |
| Edit | `edit_history` |
| Optimization | `variants` (prototype meta, production meta, file paths) |
| DOE | `doe_profile` (recommended profile, savings, tradeoffs, machine notes) |
| Plate | `plate_stl` |
| Pricing | `quote` (breakdown, market comps, confidence) |
| Queue compat | `url`, `model_path`, `gcode_path`, `infill`, `brim`, `supports_needed`, `mesh`, `stats` |

**Save strategy:** Merge on update — existing queue fields are preserved when design fields are added. A job at `status: printing` retains all its design-phase data.

---

### LLM Layer
**Path:** `djinn/printer/agent/orchestrator/llm.py`

Handles model routing transparently. If `ANTHROPIC_API_KEY` is set in `~/.config/djinn/claude.env`, uses Claude Sonnet 4.6. Otherwise falls back to `phi4:14b` via local Ollama. Agents call `llm.chat(system, messages, max_tokens)` and don't know which backend ran.

---

### On-Demand Agent — EngravingAgent

*(Missing from this map until 2026-07-13 — real, currently-running, ~490 lines. Not part of the numbered linear chain below — routed directly by intent classification, same tier as DesignEditAgent, callable at any stage where a model already exists.)*

**Path:** `forge/agent/orchestrator/agents/engrave.py`
**Triggered by:** intent classification on words like `"engrave", "add text", "put text", "write on", "mark", "stamp", "label"`
**Input:** `state.source_stl` (or a path passed in the brief) + operator's engraving request text
**Output:** 3 ranked placement proposals — nothing touches the model until one is approved
**LLM:** yes

Pipeline:
1. Load the source STL
2. Full geometry analysis (`geometry_utils.full_geometry_report()`) — surface curvature, flat regions, available area
3. Full typography analysis (`typography_utils.full_typography_report()`) — adapts letter height, depth, stroke width, spacing, arc wrap, and texture buffer to the actual surface the text will land on
4. LLM generates 3 ranked proposals using the precomputed geometry/typography values
5. Operator approves one via `approve(state, choice)`
6. `placement_resolver` converts the approved proposal into exact mm coordinates → `state.engraving_placement`

**Hard physical constraints in the system prompt** (Ender-3 V3 Plus / Calliope, 0.4mm nozzle, 0.20mm standard / 0.12mm accuracy layer height): engraved strokes below 0.6mm are unreliable on a sidewall, below 0.5mm unreliable anywhere, due to FDM layer-line roughness (~0.1mm at 0.2mm layers).

**Behavior:** always pauses for operator approval after generating proposals — never auto-advances, regardless of the `auto_advance` flag. This is deliberate: nothing is cut into the model without a human picking one of the 3 proposals first.

---

### Agent 1 — DesignGenAgent
**Path:** `djinn/printer/agent/orchestrator/agents/design_gen.py`  
**Input:** `brief` dict from ProjectState  
**Output:** concept JSON + `.scad` file  
**LLM:** yes (up to 6000 tokens — the only agent with a large generation budget)

Creates a parametric OpenSCAD design from a text brief. The system prompt enforces:
- All dimensions as named variables at the top — never magic numbers
- FDM-first rules: min 1.2mm walls (3× nozzle), +0.2mm hole clearance loose fit, +0.1mm press fit
- Overhangs minimized, supports flagged explicitly
- `$fn=64` for all circles
- Fillets on stress-risers (1.5–3mm)

**Output structure:** Two fenced blocks in the reply — `json` (concept metadata) + `openscad` (full parametric SCAD). Regex-parsed, saved to:
- `~/Obsidian/djinn/printer/models/job{N}_{name}.scad`

**What it writes to ProjectState:**
- `concept` — summary, key features, orientation, supports flag, time/material estimates, printability notes
- `source_scad` — path to SCAD file
- `status` → `"design_edit"`

---

### Agent 2 — DesignEditAgent
**Path:** `djinn/printer/agent/orchestrator/agents/design_edit.py`  
**Input:** existing SCAD + edit request string  
**Output:** modified SCAD  
**LLM:** yes

Reads the existing `.scad` file and applies targeted edits — parameter changes, geometry modifications, printability improvements. Does not rebuild from scratch. Appends to `edit_history` with timestamp and diff summary.

**What it writes to ProjectState:**
- Updated `source_scad` (overwrites file in place)
- `edit_history` entry
- `status` → `"proto_opt"`

---

### Agent 3 — ProtoOptAgent
**Path:** `djinn/printer/agent/orchestrator/agents/proto_opt.py`  
**Input:** SCAD file  
**Output:** two STL files (prototype-light, production-ready)  
**LLM:** yes

Generates two geometry variants from the SCAD source:
1. **Prototype-light** — reduced walls, infill, tolerances loosened. Prints faster and cheaper. For fit/form checks.
2. **Production-ready** — full walls, structural infill, tighter tolerances. For final use.

Calls OpenSCAD subprocess to render STLs. Stores both paths plus metadata (description, expected mass/time reduction %) in `state.variants`.

**What it writes to ProjectState:**
- `variants` — `{"prototype": {description, mass_reduction_pct, time_reduction_pct}, "production": {...}, "files": {"prototype": path, "production": path}}`
- `status` → `"doe_opt"`

---

### Agent 4 — DOEPrintOptAgent
**Path:** `djinn/printer/agent/orchestrator/agents/doe_opt.py`  
**Input:** ProjectState concept + supports flag + printer profile dict  
**Output:** optimal slicer settings  
**LLM:** no — pure deterministic Python

The most technically interesting agent. No LLM, no prints required. Uses a Taguchi-inspired factor grid with literature-calibrated prediction models to find the optimal slicer settings for a given optimization goal.

**Three optimization goals:**
- `prototype_fast` — weight: 60% time + 30% material - 10% strength. Min strength threshold: 0.22.
- `prototype_cheap` — weight: 20% time + 70% material - 10% strength. Min strength threshold: 0.22.
- `balanced` — weight: 40% time + 40% material - 20% strength. Min strength threshold: 0.85.

**Factor tables (baseline: 0.2mm / 60mm/s / 20% gyroid / 3 walls / 0.6mm support):**

| Factor | Range | Source |
|--------|-------|--------|
| Layer height | 0.12–0.36mm | 7 values |
| Print speed | 40–120mm/s | 6 values |
| Infill type + density | lightning/gyroid/cubic/grid/honeycomb × densities | 19 combinations |
| Wall count | 2–5 | 4 values |
| Support line width | 0.4mm / 0.6mm | Swansea 2023 (-31% polymer at 0.4mm) |

**Candidate grid:** Up to ~324 combinations evaluated per run. All candidates scored, sorted. Top 1 returned, top 5 alternatives included in output.

**Machine-level notes (from printer profile):**
- No enclosure → cardboard box tip (-15% power)
- No sock → install sock tip (-30–34% energy)
- Bed uninsulated → cork mat tip (-10–15% bed power)
- Supports on → 0.4mm line width tip (-31% support polymer)

**Literature baselines used:**
- Lightning infill vs 20% gyroid: -51% material, -38% time (Swansea 2023)
- Hot-end silicone sock: -30–34% energy loss reduction
- Full enclosure >2hr prints: -15–18% average power draw
- Support line width 0.6→0.4mm: -31% support polymer

**What it writes to ProjectState:**
- `doe_profile` — recommended_profile, predicted_factors, expected_savings_vs_standard, machine_notes, tradeoffs, confidence, candidates_total/passing, top_5_alternatives
- `status` → `"plate_nest"`

---

### Agent 5 — PlateNestAgent
**Path:** `djinn/printer/agent/orchestrator/agents/plate_nest.py`  
**Input:** list of `{stl, qty}` items (defaults to prototype variant if none)  
**Output:** single merged plate STL  
**LLM:** no — pure trimesh + pymeshlab

Packs STL files onto the bed. Handles the critical **>200MB STL bug** (large meshes silently drop objects during plate merging): every input STL is decimated to <10MB before merging.

**Bed dimensions:** 300×300mm (Ender-3 V3 Plus)  
**Margins:** 10mm from edge, 6mm gap between parts  
**Decimation target:** 15,000 faces (negligible visual loss at 0.2mm layer height)  
**Layout algorithm:** Row-by-row, left-to-right. New row when X overflows. Raises ValueError if Y overflows — no overflow to second plate (manual split required).

**What it writes to ProjectState:**
- `plate_stl` — path to `~/Obsidian/djinn/printer/queue/plate_job{N}.stl`
- `status` → `"priced"`

---

### Agent 6 — MakersMarkAgent

*(Missing from this map until 2026-07-13 — real, currently-running, added immediately after PlateNestAgent, before pricing/status advances.)*

**Path:** `forge/agent/orchestrator/agents/makers_mark.py`
**Input:** `state.plate_stl` (the merged plate STL PlateNestAgent just produced)
**Output:** same plate STL with the TF anvil mark boolean-subtracted into its bottom face
**LLM:** no — pure geometry (manifold3d, falls back to trimesh boolean if the mesh isn't manifold)

Stamps every plate unconditionally — there is no per-job opt-out. Mark size auto-scales down for small-footprint plates (`MARK_SIZE_SM` below `MIN_FOOTPRINT * 2`).

**Failure handling (fixed 2026-07-13):** on any failure (plate file missing, both boolean backends failing on a bad mesh, export failure), the orchestrator now halts and does **not** advance to pricing — same pattern as `ProtoOptAgent`'s render-failure handling: print the error, tell the operator the exact re-run command, `return state` without saving past the failure point. Previously, the failure was caught, printed as a soft warning, and the pipeline continued anyway with the **unmarked** plate silently written back to `state.plate_stl` — believed to be the actual cause of prior "missed maker's mark" incidents (memory: missed 3 times).

**What it writes to ProjectState:**
- `plate_stl` — overwritten with the marked version (`*_marked.stl`)
- `status` — unchanged; still transitions to `"priced"` as part of the same "plate" step

---

### Agent 7 — FairPrintAgent (price.py)
**Path:** `djinn/printer/agent/orchestrator/agents/price.py`  
**Also available as:** `djinn-print-quote` (standalone CLI)  
**Input:** ProjectState concept + DOE profile + brief  
**Output:** Quote dataclass → stored in ProjectState  
**LLM:** no — pure deterministic Python

Prices the job. Three-tier output: cost floor, fair market estimate, premium ceiling.

**Cost components:**
| Component | Formula |
|-----------|---------|
| Material | `(spool_cost / 1000g) × used_g × 1.10 waste buffer` |
| Electricity | `(180W / 1000) × print_hours × $0.13/kWh` |
| Depreciation | `($399 machine / 5000hr lifespan) × print_hours` |
| Maintenance | `$0.10/hr × print_hours` |
| Labor | `(prep_min + post_min + design_min) / 60 × $20/hr` |
| Packaging | `$0.50 flat` |

**Risk adjustment:** base cost ÷ 0.92 success rate  
**Cost floor:** risk_adjusted × 1.30 (30% margin)

**Market fetch:** Calls `fetch_market_comps(piece_name)` from `commissions/price.py` — live Etsy/market price search. `weighted_median()` of results. If <2 comps, falls back to concept's `market_price_estimate` or cost floor.

**Job type weights** (cost / market / value):
- `commodity_decor`: 0.65 / 0.30 / 0.05
- `functional_custom_part`: 0.55 / 0.30 / 0.15
- `design_heavy_oneoff`: 0.40 / 0.25 / 0.35
- `urgent_rush`: 0.50 / 0.20 / 0.30

**Smoking accessory upcharge:** Auto-detected from piece name. Upcharge applied silently to fair_market.

**Confidence:** high (≥2 market comps) / medium (design time logged) / low (neither)

**What it writes to ProjectState:**
- `quote` — `{piece_name, job_type, cost_floor, fair_market_estimate, premium_ceiling, confidence, breakdown, market, inputs, top_driver}`
- `status` → `"priced"`

---

## Layer 2: Shop Operations

**Root:** `djinn/printer/shop/`  
**Database:** `djinn/printer/shop/db.py` — SQLite at `~/.local/share/djinn-shop/shop.db`  
**Dashboard:** Flask app at `djinn/printer/shop/dashboard/app.py`, port 5000, systemd service `djinn-shop-dashboard`

### Module Map

**`intake_agent.py`**  
Receives commission requests from Discord/Telegram. Parses piece description, material, color, quantity, deadline from natural language. Creates an order record in SQLite. Generates an ORD-XXXX order ID. Routes to `quote_formatter.py` for pricing, then posts quote to the customer channel.

**`quote_formatter.py`**  
Takes a raw Quote object from FairPrintAgent and formats it for customer delivery — Discord embed or Telegram message. Shows fair_market as the offered price. Does not expose cost_floor. Adds turnaround estimate.

**`customer_dm.py`**  
Handles the full customer lifecycle after quote acceptance:
1. Sends payment instructions DM (PayPal/Venmo)
2. Collects shipping address via DM conversation
3. Parses address with `parse_address()` (usaddress library, 1.0 confidence on tested formats)
4. Notifies Javier via Telegram: order paid, address collected
5. Handles `paid ORD-XXXX` / `shipped ORD-XXXX` commands from Javier via Telegram
6. Sends shipping confirmation DM to customer
7. 48h cleanup timer: `djinn-dm-cleanup.timer` removes stale conversation contexts

**`batch_agent.py`**  
Groups pending orders into efficient print batches:
- Groups by material + color
- Checks each group against bed size (300×300mm)
- Calls PlateNestAgent to verify fit
- Sends batch proposal to Javier via Telegram: "3 orders ready — PETG black, 2hr est. Confirm?"
- Awaits `batch confirm` response before queuing the plate

**`inventory.py`**  
Filament spool tracking:
- `add filament petg black 1000g $28` — log new spool
- `deduct N g` — reduce stock after a print
- `check material color qty_needed` — availability check
- Low-stock alerts when spool < 100g
- Inventory value calculation for accounting (COGS)
- Discord/Telegram command parser built in

**`shipping_agent.py`**  
EasyPost integration:
- `parse_address(text) → ParsedAddress` — usaddress library, structured output
- `get_rates(from_addr, to_addr, weight_oz) → list[Rate]` — all carrier/service options
- `buy_label(rate_id) → Label` — purchase selected rate
- `download_label(label_url, order_id)` — saves PDF to `~/.local/share/djinn-shop/labels/`
- `track_shipment(tracking_code)` — returns current status
- Gateway command: `ship ORD-XXXX <carrier-service>` (e.g., `ship ORD-042 usps-first`)
- **EasyPost API key:** pending setup in `~/.config/djinn/shop.env`

**`accounting.py`**  
Revenue and cost tracking:
- Logs each completed order: revenue, material COGS, labor, shipping cost
- Monthly P&L summary
- Feeds the dashboard's financials tab

**`db.py`**  
SQLite schema. Tables:
- `orders` — order ID, customer, item, status, quote, timestamps
- `filament` — spool ID, material, color, weight_g, cost, remaining_g
- `transactions` — accounting entries (revenue, COGS, labor, shipping)

**`dashboard/`**  
Flask web app. Protected by `DJINN_DASH_PASSWORD` env var. Tabs:
- Orders — live order status, queue position
- Inventory — filament stock, low-stock highlights
- Financials — revenue, costs, margin
- Queue — active print queue from `print-queue.json`

Not yet deployed. Awaiting `DEPLOY: dashboard` trigger to Salomon.

---

## Supporting Infrastructure

### Print Queue
**File:** `~/.local/share/djinn/print-queue.json`  
**Schema:** `{next_id: N, jobs: [ProjectState...]}`  
All pipeline jobs and shop orders land here. Calliope reads job metadata from here via `djinn-confirm-print`.

### Print Control Scripts
| Script | Purpose |
|--------|---------|
| `djinn-confirm-print N` | Slices, sends to Calliope, calculates safe park, starts print |
| `djinn-deny-print N` | Removes job from queue (blocked while printing) |
| `djinn-print-consult N` | Analyzes model file, sends report, waits for Javier's settings |
| `djinn-print-monitor` | Watches Moonraker for print status, alerts on completion/failure |
| `djinn-force-cancel N PIN` | Emergency cancel (Javier only, PIN-gated) |

### Models / Files Directory Layout
```
~/Obsidian/djinn/printer/
├── models/          ← generated SCAD + STL files (DesignGenAgent output)
├── queue/           ← plate STLs ready for slicing (PlateNestAgent output)
├── active/          ← currently printing
├── completed/       ← finished jobs
├── failures/        ← failed prints with notes
├── commissions/     ← commission-specific files + price.py market fetcher
├── library/         ← reusable SCAD modules
└── originals/       ← source files uploaded by Javier
```

---

## Data Flow — Full Pipeline Run

```
djinn-design "brief text"
       │
       ▼
cli.py → orchestrator.run()
       │
       ▼
orchestrator.classify() ──LLM──→ {"intent": "new_design"}
       │
       ▼
ProjectState.new(brief) → print-queue.json (id=N, status=design_gen)
       │
       ▼
design_gen.run(state, llm)
  ├── LLM generates: concept JSON + OpenSCAD
  ├── saves: models/jobN_name.scad
  └── state: concept, source_scad, status=design_edit
       │
       ▼  (--full only, otherwise stops here)
design_edit.run(state, llm)        ← or manual: --edit "request"
  └── state: updated scad, edit_history, status=proto_opt
       │
       ▼
proto_opt.run(state, llm)
  ├── renders: prototype_light.stl, production.stl via OpenSCAD subprocess
  └── state: variants dict with paths + metadata, status=doe_opt
       │
       ▼
doe_opt.run(state, goal, printer)  ← no LLM — pure math
  ├── builds ~324 candidate profiles
  ├── scores against goal weights
  ├── reads printer dict for machine-specific tips
  └── state: doe_profile, status=plate_nest
       │
       ▼
plate_nest.run(state, items)       ← no LLM — trimesh + pymeshlab
  ├── decimates each STL to <10MB (pymeshlab)
  ├── arranges row-by-row on 300×300mm bed (trimesh)
  ├── exports: queue/plate_jobN.stl
  └── state: plate_stl, status=priced
       │
       ▼
price.run(state)                   ← no LLM — deterministic Python
  ├── calculates cost components from state data
  ├── fetch_market_comps(piece_name) → live market search
  ├── weighted_median() → market price
  ├── applies job_type weights
  ├── smoking upcharge if applicable
  └── state: quote dict, status=priced
       │
       ▼
print-queue.json (status=priced) ── Javier reviews ──→ djinn-confirm-print N
```

---

## What's Deployed vs Pending

| Component | Status |
|-----------|--------|
| `djinn-design` CLI | ✅ Live |
| DesignGenAgent | ✅ Live |
| DesignEditAgent | ✅ Live |
| ProtoOptAgent | ✅ Live |
| DOEPrintOptAgent | ✅ Live |
| PlateNestAgent | ✅ Live |
| MakersMarkAgent | ✅ Live (missing from this doc until 2026-07-13; failure-handling bug fixed same day, see Known Gaps) |
| EngravingAgent | ✅ Live (missing from this doc until 2026-07-13) |
| FairPrintAgent / `djinn-print-quote` | ✅ Live |
| `db.py` + SQLite schema | ✅ Built |
| `intake_agent.py` | ✅ Built |
| `quote_formatter.py` | ✅ Built |
| `batch_agent.py` | ✅ Built |
| `inventory.py` | ✅ Built |
| `customer_dm.py` | ✅ Built |
| `shipping_agent.py` | ✅ Built (EasyPost key pending) |
| `accounting.py` | ✅ Built |
| `dashboard/` Flask app | ✅ Built — **pending deploy** |
| Gateway wiring (Discord + Telegram) | **Pending deploy** |
| EasyPost API key in shop.env | **Pending Javier** |
| `djinn-shop-dashboard` systemd service | **Pending deploy** |

---

## Known Gaps and Risks

**No second-plate overflow in PlateNestAgent.** If items don't fit on one 300×300 plate, it raises ValueError. Multi-plate batching is not implemented. Large orders require manual splitting.

**DOE factor tables are static.** The prediction models are literature-calibrated but not empirically tuned to Calliope specifically. Real print times may vary ±15–20% from predictions until field data is collected and factors are updated.

**OpenSCAD subprocess dependency.** ProtoOptAgent calls `openscad` as a subprocess. If it's not installed or the SCAD has errors, the STL render fails silently or produces an empty file. No validation of the rendered STL exists currently.

**Market comp fetch depends on external service.** `fetch_market_comps()` hits a live market API. If the service is down or rate-limited, pricing falls back to concept estimate — which may be stale or absent for new designs.

**Shop deploy is in QUEUE.md, not yet triggered.** The dashboard, gateway wiring, and shipping agent are built but not running. All four shop deploy tasks are in QUEUE.md awaiting `trigger: manual` signals from Javier.

**(Fixed 2026-07-13) MakersMarkAgent used to silently continue on stamp failure.** The orchestrator caught any exception from `makers_mark.run()`, printed a soft warning, and proceeded straight to pricing anyway — with the plate STL overwritten by the *unmarked* version under a false assumption of success. Believed to be the actual cause of prior missed-maker's-mark incidents (memory: missed 3 times). Now matches `ProtoOptAgent`'s render-failure pattern: on any stamp failure, the pipeline halts and does not advance to pricing until the operator fixes the issue and re-runs.

---

*— Claude, 2026-05-31*
*Amended 2026-07-13 — added MakersMarkAgent and EngravingAgent (both real, previously undocumented), fixed the MakersMark silent-failure bug above. See `djinn/logs/build-log.md` for the session that found this via `djinn-doc-check`-style audit.*
