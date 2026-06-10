# Djinn Vault

**Djinn** is a fully deployed, AI-mediated operating system for creative production, 3D print shop operations, and home infrastructure automation — built and maintained by Javier (DrManzo) with Claude (Anthropic), Salomon (local Ollama), and Marcus (Perplexity AI).

This vault is Djinn's memory, knowledge base, operational documentation, and deployment archive. Everything is committed and version-controlled. No institutional knowledge is lost.

---

## What Djinn Is

Djinn is not a single tool — it is a coordinated system of AI agents, CLI tools, automated pipelines, and hardware integrations running on a home lab. It currently operates:

- **Typhon's Forge** — A live AI-automated 3D print commission shop (Discord intake → consult → quote → order → print → ship)
- **LBlack** — A video script production pipeline (capture → AI draft → grammar check → research → final)
- **Typhon's Studio** — A media production stack for Shorts, long-form video, music, and social content
- **Home infrastructure** — Unified dashboard, device monitoring, system health automation

---

## Hardware

| Machine | Role | Specs |
|---|---|---|
| **Salomon** | Primary orchestration node | HP Omen · RTX 5060 · 29GB RAM · Fedora Linux |
| **Calliope** | 3D printer | Ender-3 V3 Plus · Klipper + Moonraker · 192.168.1.113 |
| **Typhon** | Local LLM + storage + media | Local Ollama host |

---

## Agent Roles

| Agent | Platform | Function |
|---|---|---|
| **Claude** | Anthropic API | Architecture, builds new components, session reports |
| **Salomon** | Local Ollama (qwen2.5:7b, deepseek-r1:7b) | Daily ops, Discord/Telegram gateways, print execution, deployment |
| **Typhon** | Local Ollama + storage | Backup, sync, Typhon's Studio operations |
| **Marcus** | Perplexity AI (Sonnet 4.6) | Research, code audits, spec delivery, operator manuals |

All agents coordinate through `djinn/communications/COMMS.md` — an append-only message thread committed to GitHub after each session.

---

## Vault Structure

```
djinn-vault/
├── README.md                        ← This file
│
├── djinn/                           ← Core operational memory
│   ├── communications/
│   │   └── COMMS.md                 ← Append-only inter-agent message thread
│   ├── decisions/                   ← Architecture Decision Records
│   ├── projects/                    ← Active project context and state
│   ├── research/                    ← Domain research notes
│   ├── people/                      ← Relationship context notes
│   ├── bugs.md                      ← Active bug log
│   └── logs/
│       ├── build-log.md             ← Cumulative build history
│       ├── reports/                 ← Per-session reports (YYYY-MM-DD_slug.md)
│       └── decisions/               ← Decision log entries
│
├── djinn/printer/                   ← Typhon's Forge 3D print shop
│   ├── FAIRPRINT-MANUAL.md          ← Complete operator handbook (Marcus)
│   ├── DJINN-3D-PRINT-PIPELINE.md   ← Full technical architecture
│   ├── TYPHONS-FORGE-STRATEGY.md    ← Business strategy + product library
│   ├── DJINN-CAPABILITIES.md        ← Capability-by-capability breakdown
│   ├── PRINT-PROFILES.md            ← Slicer profile reference
│   ├── PRINTER-MANUAL.md            ← Calliope hardware reference
│   ├── SUPPORT-GUIDE.md             ← Troubleshooting reference
│   ├── commissions/
│   │   ├── price.py                 ← Core pricing engine (FairPrintAgent)
│   │   ├── brief.py                 ← Input validation + smoking routing
│   │   └── report.py               ← Output formatter (Telegram/terminal/JSON)
│   ├── shop/
│   │   ├── db.py                    ← SQLite + Fernet encrypted storage
│   │   ├── accounting.py            ← Income statement, balance sheet, reports
│   │   ├── quote_formatter.py       ← Customer vs owner views
│   │   ├── intake_agent.py          ← Customer text → print brief
│   │   ├── customer_dm.py           ← ORDER flow + DM collection + cleanup
│   │   ├── batch_agent.py           ← Queue batching by material + color
│   │   ├── inventory.py             ← Filament spool tracking
│   │   ├── shipping_agent.py        ← EasyPost label purchase + tracking
│   │   └── dashboard/
│   │       ├── app.py               ← Flask owner dashboard (localhost:5000)
│   │       └── templates/           ← Queue, orders, customers, finance, reports
│   └── agent/orchestrator/
│       └── agents/                  ← 6-agent design pipeline (djinn-design)
│
├── djinn/media/                     ← Typhon's Studio media production
│   ├── DJINN-MEDIA-MANUAL.md        ← Complete media stack operator handbook (Marcus)
│   ├── TYPHONS-STUDIO-MANUAL.txt    ← Core studio system reference
│   └── [content pipeline files]
│
├── scripts/                         ← LBlack video script production pipeline
│   ├── 01-prompt/                   ← Prompts for Ollama drafting
│   ├── 02-draft/                    ← First-pass AI output
│   ├── 03-grammar-check/            ← script-check.sh reports
│   ├── 04-links/                    ← Reference URLs and source links
│   ├── 05-resources/                ← PDFs, images, benchmarks
│   ├── 06-research/                 ← Pre-recording research notes
│   ├── 07-review/                   ← Self-review checklists
│   └── 08-final/                    ← Ready-to-record scripts
│       └── video-name/
│           ├── script.md
│           └── architecture.md
│
├── inbox/                           ← Quick capture: raw ideas, voice memos
└── references/                      ← Permanent reference library
```

---

## Operator Manuals

Five complete standalone operator handbooks live in the vault. Any agent or human starting cold can understand, run, and troubleshoot the full relevant stack from these documents alone.

| Manual | Location | Covers |
|---|---|---|
| **DJINN-AGENTS-MANUAL.md** | `djinn/` | Agent roles, COMMS protocol, session discipline, coordination rules |
| **DJINN-CLI-MANUAL.md** | `djinn/` | Every CLI tool, flags, usage, common workflows |
| **DJINN-INFRA-MANUAL.md** | `djinn/` | Hardware, networking, systemd services, home dashboard |
| **DJINN-MEDIA-MANUAL.md** | `djinn/media/` | Typhon's Studio full media production stack |
| **FAIRPRINT-MANUAL.md** | `djinn/printer/` | Typhon's Forge full print shop commission pipeline |

---

## Typhon's Forge — 3D Print Shop

A fully automated AI-mediated commission shop. Customer drops a file in Discord → system analyzes, quotes, collects payment, batches, prints, ships. Operator touches the order twice.

**Full pipeline:**
```
Discord file drop → mesh analysis + renders → FairPrintAgent quote
→ customer ORDER → encrypted DM flow → payment confirm
→ plate batching → confirm print → Moonraker execution
→ progress monitoring → EasyPost shipping label → tracking DM to customer
```

**Key numbers:**

| Metric | Value |
|---|---|
| Printer bed | 220 × 220 × 250mm |
| Machine cost rate | ~$0.20/hr |
| Labor rate | $20.00/hr |
| Success rate assumption | 92% |
| Minimum enforced margin | 30% |
| Smoking accessory upcharge | 35% |
| Express premium | 35% |
| Low stock alert | 150g |
| Dashboard | http://localhost:5000 |

**CLI tools:**

| Command | Function |
|---|---|
| `djinn-print-consult` | Mesh analysis + 3 renders + dry-run slice |
| `djinn-model-slice` | Exact slice with chosen settings |
| `djinn-confirm-print` | Park calc + Moonraker upload + start |
| `djinn-print-monitor` | Progress polling + notifications |
| `djinn-print-quote` | Commission pricing CLI |
| `djinn-design` | 6-agent manufacturing orchestrator |
| `djinn-shop-deploy` | One-command full shop installer |

**Pricing formula (FairPrintAgent):**
```
material_cost  = spool_cost_per_gram × used_g × 1.10
machine_cost   = print_hours × ~$0.20/hr
labor_cost     = labor_minutes / 60 × $20/hr

base_cost      = material + machine + labor + extras
risk_adjusted  = base_cost / 0.92
cost_floor     = risk_adjusted × 1.30

fair_market    = wc×cost_floor + wm×market_median + wv×(cost_floor + value_premium)

if smoking_accessory: fair_market *= 1.35
express_price  = fair_market × 1.35
```

**Shop system:**
- Encrypted SQLite database (Fernet column-level PII encryption)
- Full accounting: income statement, balance sheet, monthly reports
- XLSX/CSV financial exports
- Filament inventory with auto-deduction and low-stock alerts
- EasyPost shipping integration (USPS / UPS / FedEx)
- Flask owner dashboard at localhost:5000

---

## Typhon's Studio — Media Production

AI-assisted media stack for short-form video, long-form content, music production, and social posting.

**Capabilities:**
- Shorts pipeline: script → voice → video assembly → upload
- Long-form YouTube video workflow
- Music generation and integration
- Social content scheduling and cross-posting
- Asset management (b-roll, overlays, audio stems)

See `djinn/media/DJINN-MEDIA-MANUAL.md` for the complete operator reference.

---

## LBlack — Script Pipeline

Structured 8-stage workflow for video script production with AI drafting, grammar checking, research integration, and final packaging.

**Stages:**
1. **Capture** → `inbox/`
2. **Prompt** → `scripts/01-prompt/`
3. **Draft** → `scripts/02-draft/` (Ollama)
4. **Check** → `scripts/03-grammar-check/` (`script-check.sh`)
5. **Links** → `scripts/04-links/`
6. **Resources** → `scripts/05-resources/`
7. **Research** → `scripts/06-research/`
8. **Review** → `scripts/07-review/`
9. **Final** → `scripts/08-final/video-name/`

---

## Technology Stack

| Layer | Technology |
|---|---|
| OS | Fedora Linux |
| Printer firmware | Klipper + Moonraker |
| Slicer | Creality Print (GUI via Xvfb) |
| Local LLMs | Ollama (qwen2.5:7b, deepseek-r1:7b, phi4:14b, llama3.2-vision:11b) |
| Premium AI | Claude (Anthropic API), Perplexity (Marcus) |
| Database | SQLite + Fernet encryption |
| Web dashboard | Flask + Bootstrap 5 |
| Shipping | EasyPost SDK (USPS / UPS / FedEx) |
| Market data | DuckDuckGo Search |
| 3D processing | trimesh, pymeshlab, OpenSCAD |
| Messaging | Discord (discord.py), Telegram (python-telegram-bot) |
| Vault sync | Obsidian + git + rclone (Google Drive) |
| Notifications | systemd timers + Telegram bot |

---

## Inter-Agent Coordination

All agents communicate via `djinn/communications/COMMS.md` — append-only, committed to GitHub after each session.

Every session produces:
- Session report → `djinn/logs/reports/YYYY-MM-DD_<slug>.md`
- Build log entry → `djinn/logs/build-log.md`
- Decision log entry (if architectural decision made)
- COMMS.md append
- `git push` to github.com/DrManzo/djinn-vault

No knowledge is lost. Every decision, bug, and build is documented.

---

## Naming Conventions

- **Files:** `UPPER-KEBAB-CASE.md` for manuals and specs; `kebab-case.md` for notes
- **Directories:** `kebab-case/`
- **Tags:** `#domain/subdomain` (e.g., `#psychology/shadow-work`, `#business/typhons-forge`)
- **Links:** `[[Internal Link]]` for Obsidian cross-references
- **Order IDs:** `ORD-XXXX` (zero-padded, sequential)
- **Session reports:** `YYYY-MM-DD_slug.md`

---

## Safety Rules (Print Shop)

1. No autonomous print starts — `confirm N` required, hard gated
2. No autonomous model orientation changes — hard rule enforced in agents
3. `deny N` blocked while printing — gateway-level rejection
4. `djinn-force-cancel` requires owner PIN only
5. Safe park position calculated before every print job
6. Customer PII never in Discord channels — encrypted DM flow only
7. Bot DM cleanup after 48 hours

---

*Built by Javier (DrManzo) with Claude (Anthropic), Salomon (local Ollama), Typhon (local), and Marcus (Perplexity AI).*  
*Vault: github.com/DrManzo/djinn-vault*  
*— 2026-06-09*
