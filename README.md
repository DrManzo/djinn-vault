# Djinn Vault

**Djinn** is a personal AI operating system — a coordinated stack of agents, automation pipelines, CLI tools, and hardware integrations that runs a real 3D print shop, a media production studio, and a home lab from a single knowledge base.

This vault is Djinn's memory: operational documentation, session history, research library, decision records, inter-agent communications, and deployment archive — all version-controlled, all committed after every session. No institutional knowledge is lost.

---

## What Djinn Is

Most AI setups are a single model in a single chat window. Djinn is something different: a multi-agent system where each agent has a defined lane, a defined output format, and a shared memory layer that persists across sessions and machines.

The goal is not to automate everything — it is to make the operator the decision-maker and the agents the execution layer. Djinn handles intake, analysis, quoting, printing, media production, and research. The operator approves, directs, and ships.

**Currently running:**

- **Typhon's Forge** — AI-automated 3D print commission shop. Discord intake → mesh analysis → fair-market quote → encrypted order flow → batch print → EasyPost ship. Operator touches each order twice.
- **Typhon's Studio** — Media production stack for Shorts, long-form video, music, and social content.
- **LBlack** — 8-stage AI-assisted video script pipeline (capture → draft → research → final).
- **Home infrastructure** — Unified dashboard, device monitoring, vault sync, system health automation.
- **Hellhound** — Security monitoring (2026-07-12). Deterministic detection (no model inference in the loop) for brute-force/reconnaissance against SSH and the Forge dashboard, auto-block via `ufw`, incident logging, Telegram alerts. AI is used only after the fact, for optional human-readable summaries — never for detection or blocking. See `hellhound/`.
- **Knowledge suites** — Structured research libraries across Law, Psychology, and Finance — built by Marcus (Perplexity) and indexed for semantic search.

---

## Hardware

| Machine | Role | Specs |
|---|---|---|
| **Salomon** | Primary orchestration node | HP Omen · RTX 5060 Laptop · 29GB RAM · Fedora Linux |
| **Typhon** | Shop machine (slicing/commissions/content/accounting) — reinstalled to Windows 2026-06-25, onboarding still incomplete | MSI · GTX 1650 4GB · 14GB RAM · Windows |
| **Orin** | Large-model host + always-on storage | iMac · Intel i7 8-core · 40GB RAM · 1.7TB free · macOS |
| **Calliope** | 3D printer | Ender-3 V3 Plus · Klipper + Moonraker |
| **Nemesis** | 3D printer | Flashforge AD5M Pro · Moonraker |
| **Iris** | 3D printer | Flashforge AD5X · Moonraker, multi-color (bambufy) |
| **Penelope** | 3D printer | Ender-3 Pro · OctoPrint (runs on Salomon, no independent IP) |

All machines share a local subnet. Ollama runs on Salomon (primary inference), Typhon (lightweight/relay), and Orin (large model CPU inference). The vault syncs to GitHub and Google Drive continuously.

---

## Agent Stack

Six agents operate in defined lanes. No agent owns the whole system — they feed each other.

| Agent | Platform | Lane |
|---|---|---|
| **Claude** | Anthropic API | Architecture, system design, cross-domain synthesis, vault-persistent session work |
| **Salomon** | Local Ollama (7 models) | Daily ops, Discord/Telegram gateways, print execution, deployment, media pipeline |
| **Typhon** | Local Ollama + storage | Backup, vault sync, Typhon's Studio, lightweight automation |
| **Marcus** | Perplexity AI | Deep research, multi-source synthesis, code audits, operator manuals, spec delivery |
| **Gemini** | Google AI Studio | Visual output, image generation, system diagrams, GDrive-native docs and media |
| **Assistant** | Hermes + local Ollama | Skill development, documentation, process engineering, bootstrapping |

All agents coordinate through `djinn/communications/COMMS.md` — an append-only message thread committed to GitHub after every session. Tasks are delegated via `djinn/communications/QUEUE.md`.

---

## Local Model Fleet

| Model | Salomon | Typhon | Orin | Role |
|---|---|---|---|---|
| qwen2.5:7b | ✓ | relay | — | Default — tool use, ops, daily tasks |
| deepseek-r1:7b | ✓ | relay | — | Reasoning, planning |
| phi4:14b | ✓ | relay | ✓ | Notes, captions, session reports |
| llama3.2-vision:11b | ✓ | relay | — | Mesh renders, visual QC |
| qwen2.5-coder:7b | ✓ | relay | — | Code generation |
| mistral:7b | ✓ | — | — | OpenClaw gateway relay |
| nomic-embed-text | ✓ | ✓ | ✓ | Embeddings, semantic search |
| llama3.3:70b | — | — | ✓ | Top-tier local inference (slow, high quality) |
| qwen2.5-coder:32b | — | — | ✓ | Large-context code tasks |
| llama3.2:3b | — | ✓ | — | Lightweight local only |
| qwen2.5:1.5b | — | ✓ | — | Lightweight automation |

---

## Vault Structure

> **Note (2026-07-12):** the tree below predates a 2026-07-08 department restructure and is out of date — top-level layout is now `djinn/`, `forge/`, `media/`, `ai/`, `hellhound/`, `writing/`, `personal/`, `references/`, `RAW/`, `i notes/`. `djinn/GATEWAY.md` is the current authoritative structure reference; this section needs a full redraw, not attempted here since it wasn't part of today's change set.

```
djinn-vault/
├── README.md
│
├── djinn/                           ← Core operational memory
│   ├── DJINN-AGENTS-MANUAL.md       ← Agent roles, coordination, session discipline
│   ├── DJINN-CLI-MANUAL.md          ← Every CLI tool, flags, workflows
│   ├── GATEWAY.md                   ← Agent behavioral contract + enforcement tiers
│   ├── AGENTS.md                    ← Live agent registry and routing rules
│   ├── INFRASTRUCTURE.md            ← Machine topology, repos, services
│   ├── SYSTEM-STATE.md              ← Current operational state snapshot
│   ├── communications/
│   │   ├── COMMS.md                 ← Append-only inter-agent message thread
│   │   ├── QUEUE.md                 ← Task delegation queue
│   │   ├── HEARTBEAT.md             ← Salomon machine heartbeat
│   │   └── HEARTBEAT-typhon.md      ← Typhon machine heartbeat
│   ├── logs/
│   │   ├── build-log.md             ← Cumulative build history
│   │   ├── bugs.md                  ← Active bug index
│   │   ├── reports/                 ← Per-session reports (YYYY-MM-DD_slug.md)
│   │   └── gateway/                 ← Gateway action audit log (JSONL)
│   └── research/
│       └── marcus/                  ← Marcus research output (Law, Psych, Finance suites)
│
├── djinn/printer/                   ← Typhon's Forge 3D print shop
│   ├── FAIRPRINT-MANUAL.md          ← Complete operator handbook
│   ├── CALLIOPE-MANUAL.md           ← Printer hardware + Klipper reference
│   ├── PRINTER-MANUAL.md            ← Print process reference
│   ├── PRINT-PROFILES.md            ← Slicer profile reference
│   ├── commissions/                 ← FairPrintAgent pricing engine
│   ├── shop/                        ← Order management, accounting, shipping
│   └── agent/orchestrator/          ← 6-agent manufacturing pipeline (djinn-design)
│
├── djinn/media/                     ← Typhon's Studio media production
│   ├── DJINN-MEDIA-MANUAL.md        ← Complete media stack handbook
│   └── TYPHONS-STUDIO-MANUAL.txt    ← Studio system reference
│
├── scripts/                         ← LBlack video script pipeline
│   └── 01-prompt/ through 08-final/ ← 8-stage production workflow
│
├── references/                      ← Permanent knowledge library
└── inbox/                           ← Quick capture: raw ideas, voice memos
```

---

## Operator Manuals

Five complete standalone operator handbooks. Any agent or human starting cold can understand, operate, and troubleshoot the full relevant stack from these documents alone.

| Manual | Covers |
|---|---|
| `djinn/DJINN-AGENTS-MANUAL.md` | Agent roles, COMMS protocol, session discipline, coordination rules |
| `djinn/DJINN-CLI-MANUAL.md` | Every CLI tool, flags, usage, common workflows |
| `djinn/media/DJINN-MEDIA-MANUAL.md` | Typhon's Studio — full media production stack |
| `djinn/printer/FAIRPRINT-MANUAL.md` | Typhon's Forge — full print shop commission pipeline |
| `djinn/printer/CALLIOPE-MANUAL.md` | Calliope printer — Klipper/Moonraker setup and operation |

---

## Typhon's Forge — 3D Print Shop

A fully automated AI-mediated commission shop. Customer drops a file in Discord → the system analyzes the mesh, generates renders, quotes a fair-market price, collects payment details via encrypted DM, batches jobs by material and color, prints, and ships. The operator approves at two checkpoints.

**Full pipeline:**
```
Discord file drop
  → mesh analysis + renders (llama3.2-vision)
  → FairPrintAgent quote (material + machine + labor + market blend)
  → customer ORDER → encrypted DM flow → payment confirm
  → batch by material/color → operator confirm
  → Moonraker upload + print start
  → progress monitoring + notifications
  → EasyPost label purchase → tracking DM to customer
```

**Manufacturing orchestrator — djinn-design (6-agent pipeline):**

| Agent | Function |
|---|---|
| DesignGenAgent | Brief → parametric OpenSCAD concept |
| DesignEditAgent | Modify existing design without rebuild |
| ProtoOptAgent | Render prototype + production STLs |
| DOEPrintOptAgent | Taguchi factor grid → optimal slicer profile, no test prints |
| PlateNestAgent | Decimate → arrange → export plate STL (handles >200MB meshes) |
| FairPrintAgent | Commission pricing: material + machine + labor + market blend |

**Pricing formula:**
```
material_cost  = spool_cost_per_gram × used_g × 1.10
machine_cost   = print_hours × ~$0.20/hr
labor_cost     = labor_minutes / 60 × $20.00/hr

base_cost      = material + machine + labor + extras
risk_adjusted  = base_cost / 0.92        (92% success rate assumption)
cost_floor     = risk_adjusted × 1.30    (30% minimum margin)

fair_market    = weighted blend of cost_floor, market_median, value_premium
smoking upcharge ×1.35 | express premium ×1.35
```

**Shop system:**
- Encrypted SQLite (Fernet column-level PII encryption)
- Full accounting: income statement, balance sheet, monthly reports, XLSX/CSV export
- Filament inventory with auto-deduction and low-stock alerts
- EasyPost integration (USPS / UPS / FedEx)
- Flask owner dashboard (localhost:5000)

**Print safety rules (non-negotiable):**
1. No autonomous print starts — operator `confirm N` required, gateway-enforced
2. No autonomous model orientation changes — operator owns orientation, always
3. No print cancels from agents — `djinn-force-cancel` requires owner PIN only
4. Customer PII stays out of Discord — encrypted DM flow only
5. Bot DM cleanup after 48 hours

---

## Typhon's Studio — Media Production

AI-assisted media stack for short-form video, long-form content, music production, and social posting.

- Shorts pipeline: script → voice → video assembly → upload
- Long-form YouTube video workflow
- Music generation and integration
- Social content scheduling and cross-posting
- Asset management (b-roll, overlays, audio stems)

See `djinn/media/DJINN-MEDIA-MANUAL.md` for the full operator reference.

---

## LBlack — Script Pipeline

8-stage structured workflow for AI-assisted video script production.

| Stage | Directory | Process |
|---|---|---|
| 1 | `inbox/` | Raw capture — ideas, voice memos |
| 2 | `scripts/01-prompt/` | Prompt engineering for Ollama |
| 3 | `scripts/02-draft/` | AI first-pass draft |
| 4 | `scripts/03-grammar-check/` | `script-check.sh` reports |
| 5 | `scripts/04-links/` | Reference URLs + source links |
| 6 | `scripts/05-resources/` | PDFs, images, benchmarks |
| 7 | `scripts/06-research/` | Pre-recording research notes |
| 8 | `scripts/07-review/` | Self-review checklists |
| Final | `scripts/08-final/video-name/` | `script.md` + `architecture.md` |

---

## Knowledge Suites

Marcus (Perplexity) has built three deep research libraries, indexed by domain and linked for semantic search via the Slipbox agent.

| Suite | Scope | Status |
|---|---|---|
| **Law** | LSAT, bar prep, contracts, torts, civil procedure, corporate law, LLC formation, CA compliance, legal research methods | Complete — 13 domains |
| **Psychology** | Behavioral/cognitive psych, Freud, Jung, shadow work, addiction, attachment, trauma, social psychology, EQ, personality frameworks | Complete — 14 domains |
| **Finance** | Budgeting, investing, stock analysis, crypto, federal/CA tax law, tax-advantaged accounts, self-employment, wealth building | Complete — 20 domains |

These are not chat summaries — they are structured reference documents with citations, key concepts, applied sections, and cross-links. They feed the OpenClaw law/psych/finance agents directly.

---

## The Gateway System

Djinn uses a tiered action classification system (`djinn-gateway`) to prevent agents from taking destructive or irreversible actions autonomously.

| Tier | Name | Examples | Standard Mode |
|---|---|---|---|
| 0 | Read | File reads, git log, directory listing | Auto |
| 1 | Log | COMMS.md writes, session reports, heartbeats | Auto |
| 2 | Propose | Write to staging/tmp, create branches | Auto + COMMS entry |
| 3 | Checkpoint | `git push`, write to library/, overwrite STLs, send Telegram | Log + allow |
| 4 | Hard Stop | `rm`, force push, modify GATEWAY.md or credentials | Blocked — dev mode + double-confirm required |

Enforced both mechanically (git pre-push hook) and behaviorally (agents read `GATEWAY.md` at session start and self-enforce). All actions are audit-logged to `djinn/logs/gateway/`.

Activate dev mode: `djinn-gateway dev` (2h default) | Check: `djinn-gateway status` | Reset: `djinn-gateway reset`

---

## Technology Stack

| Layer | Technology |
|---|---|
| OS (primary) | Fedora Linux |
| OS (large-model host) | macOS |
| Printer firmware | Klipper + Moonraker |
| Slicer | Creality Print (GUI via Xvfb) |
| Local LLMs | Ollama — 11 models across 3 machines |
| Premium AI | Claude (Anthropic API), Perplexity (Marcus), Gemini (Google AI Studio) |
| Database | SQLite + Fernet encryption |
| Web dashboard | Flask + Bootstrap 5 |
| Shipping | EasyPost SDK (USPS / UPS / FedEx) |
| 3D processing | trimesh, pymeshlab, OpenSCAD |
| Messaging | Discord (discord.py), Telegram (python-telegram-bot) |
| Search | DuckDuckGo (market data), semantic search via nomic-embed-text |
| Vault sync | Obsidian + git + rclone (GitHub + Google Drive) |
| Agent framework | OpenClaw (local), Claude Code (premium lane) |
| Notifications | systemd timers, Telegram bot |
| Security monitoring | Hellhound — deterministic Python (no model inference in the detection/blocking path), `ufw` for auto-block |

---

## Inter-Agent Coordination

Every session, every agent produces the same artifact set:

- **Session report** → `djinn/logs/reports/YYYY-MM-DD_<slug>.md`
- **Build log entry** → `djinn/logs/build-log.md`
- **Decision log entry** (if an architectural decision was made)
- **COMMS.md append** — signed entry in the shared message thread
- **git push** — vault committed and synced to GitHub

No knowledge is lost between sessions, machines, or agents. An agent starting cold reads the vault and has full context.

---

## Where Djinn Is Going

Djinn is designed to grow without rewrites. The architecture already supports what comes next.

**Near-term:**
- Orin large-model inference fully integrated — 70B-class tasks (deep reports, long-context analysis) running locally at near-zero cost
- Full semantic search across the vault — every note, research file, and decision linkable by meaning via nomic-embed-text + Slipbox
- Gemini visual lane active — product renders, architecture diagrams, and media-rich briefings generated and delivered to GDrive automatically
- Local session reporting — `djinn-local-report` generates session reports via phi4:14b; `djinn-comms-auto` routes COMMS entries to the right model by event type — reducing cloud dependency for routine documentation

**Medium-term:**
- Live law, psychology, and finance assistant lanes — structured research libraries feeding agent sessions for LSAT prep, shadow work, tax planning, and contract review
- Social media publishing pipeline — content calendar, cross-platform scheduling, performance analytics
- Original design catalog — custom 3D designs sold alongside commission work through Typhon's Forge
- Voice interface — Whisper + local TTS + command routing through the existing agent stack

**Longer-term:**
- Djinn as a replicable pattern — the architecture (vault-as-memory, tiered gateway, lane discipline, multi-agent coordination) is domain-agnostic. It works for research labs, small creative businesses, solo operators, and teams.
- Self-improving documentation — agents update their own manuals as the system changes; the vault always reflects current state
- Cross-vault federation — multiple Djinn instances sharing a research layer or production capacity across operators

The design principles that make this extensible: shared memory (the vault), lane discipline (agents don't step on each other), gateway enforcement (no destructive autonomy), and artifact-first sessions (every session produces durable, readable output).

---

## Naming Conventions

- **Manuals and specs:** `UPPER-KEBAB-CASE.md`
- **Notes:** `kebab-case.md`
- **Directories:** `kebab-case/`
- **Tags:** `#domain/subdomain` (e.g. `#psychology/shadow-work`, `#business/typhons-forge`)
- **Internal links:** `[[Note Title]]` (Obsidian wiki links)
- **Order IDs:** `ORD-XXXX` (zero-padded, sequential)
- **Session reports:** `YYYY-MM-DD_slug.md`
- **Task IDs:** `TASK-NNN` (sequential, QUEUE.md)

---

*Djinn is built and maintained by its operator with Claude (Anthropic), Salomon (local Ollama), Typhon (local Ollama), Marcus (Perplexity AI), and Gemini (Google AI Studio).*  
*— Partially updated 2026-07-12 (Hellhound, hardware table, department-restructure flag). Most recent full session record: `djinn/logs/reports/`. This file predates the 2026-07-08 department restructure in several sections not touched today — see the note under Vault Structure.*
