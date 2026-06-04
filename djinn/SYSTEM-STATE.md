---
subject: Djinn Operations
tags: [djinn, system-state, operations]
created: 2026-05-20
updated: 2026-05-23T05:20
---

# SYSTEM-STATE.md — Djinn Operational State

Inter-machine operational state. Read before acting. Update when state changes.
**Related:** [[ROUTING]] | [[PROTOCOL]] | [[HEARTBEAT]] | [[HEARTBEAT-typhon]] | [[COMMS]]

---

## Machine Status

| Machine | Status | IP | User | Last Verified |
|---------|--------|----|------|--------------|
| Salomon | ✅ Online | 192.168.1.225 | `drmanzo` | 2026-05-23 |
| Typhon | ✅ Online | 192.168.1.113 | `tf-tthq` | 2026-05-23 |
| Claude | ✅ Online | — (API) | — | 2026-05-23 |

**Network:** Both machines on same subnet (192.168.1.x) as of 2026-05-23. SSH from Salomon→Typhon: `ssh -i ~/.ssh/id_ed25519 tf-tthq@192.168.1.113`. Passwordless via ed25519 key.

---

## Active Services — Salomon

| Service | Status | Notes |
|---------|--------|-------|
| OpenClaw gateway | ✅ Live | 127.0.0.1:18789, token auth. main=mistral:7b (gateway relay), coder=qwen2.5-coder:7b, law=deepseek-r1:7b. historyLimit=5 |
| Telegram @DjinnOCBot | ✅ Live | Polling, DMs locked to Javier. Bot: @DjinnOCBot (new token 2026-05-23) |
| Telegram printer bot | ✅ Live | djinn-printer-bot.service on **Typhon** |
| Ollama | ✅ Running | 0.0.0.0:11434 — **7 models** (qwen3.6 removed 2026-05-23) |
| comms-processor | ✅ Active | 3-min timer → routes @Clerk→djinn-clerk, @Slipbox→djinn-slipbox, @Salomon→opencode |
| djinn-clerk timer | ✅ Active | 1-hr timer → scans RAW/ for unprocessed Perplexity exports → i notes/Notes/ |
| Heartbeat timer | ✅ Active | 5-min → [[HEARTBEAT]] |
| Vault sync (GDrive) | ✅ Active | 2-min rclone |
| Vault sync (GitHub) | ✅ Active | git push after rclone |
| Forge sync | ✅ Active | 15-min → GDrive (~/forge/) |
| djinn-daily timer | ✅ Active | 8 AM → morning briefing via OpenClaw cron (qwen2.5:7b, 240s timeout) |
| djinn-weekly timer | ✅ Active | Sun 20:00 → weekly review |
| printer-error-logger | ✅ Active | Monitors Moonraker for errors |
| opencode | ✅ Available | ~/.opencode/bin/opencode v1.15.10 — use `--dangerously-skip-permissions` for headless |

---

## Active Services — Typhon

| Service | Status | Notes |
|---------|--------|-------|
| Ollama | ✅ Running | Local models + remote routing to Salomon:11434 |
| comms-processor | ✅ Active | 3-min systemd timer → scans COMMS.md → invokes opencode |
| Heartbeat timer | ✅ Active | 5-min → [[HEARTBEAT-typhon]] — now writes dynamic IP |
| Vault sync | ✅ Active | git pull 2-min |
| djinn-printer-bot | ✅ Live | python-telegram-bot, ~/.venvs/djinn-bot/, token in ~/.config/djinn/printer-bot.env |
| opencode | ✅ Available | Invoked via comms-processor — use `--dangerously-skip-permissions` for headless |

---

## Ollama Model Routing

| Model | Primary | Remote from Typhon | Role |
|-------|---------|-------------------|------|
| qwen2.5:7b | Both | Yes | Default — tool use + conversation |
| deepseek-r1:7b | Both | Yes | Deep reasoning |
| qwen2.5-coder:7b | Both | Yes | Code / dev |
| phi4:14b | Salomon | Yes | Notes / APA (on demand) |
| llama3.2-vision:11b | Salomon | Yes | Vision (on demand) |
| mistral:7b | Salomon | Yes | Creative writing |
| llama3.2:3b | Typhon | Local only | Lightweight admin |
| qwen2.5:1.5b | Typhon | Local only | Lightweight automation |
| nomic-embed-text | Both | Yes | Embeddings |

---

## Printer

| Field | Value |
|-------|-------|
| Machine | Ender-3 V3 Plus (Calliope) |
| IP | 192.168.1.113:7125 (Moonraker) |
| Control | Klipper + Moonraker |
| Bot | Telegram bot on Typhon — `/print_status`, `/print`, `/print_cancel` |
| Config backup | [[djinn/printer/backup/]] |
| Process docs | [[printer/process/INTAKE]] |
| Error history | [[error_log]] |
| Current print | None — idle |
| Queue | Job #1 (mario pipe + 4× coins) ✅ completed 2026-05-24 10:22 UTC. Job #2 (anybodywantcoffee) ✅ completed 2026-05-24 ~20:13 UTC. Queue empty. |
| Print agent stack | `djinn/printer/agent/orchestrator/` — 6-agent pipeline live |
| Commission pricing | `djinn-print-quote` — `~/.local/bin/djinn-print-quote` |
| Design CLI | `djinn-design` — `~/.local/bin/djinn-design` |

---

## Agent Activation Status

| Agent | Trigger | Status | Notes |
|-------|---------|--------|-------|
| Salomon opencode | comms-processor (3-min timer) | ✅ Active | Fires on new @Salomon tasks in COMMS.md |
| Typhon opencode | comms-processor (3-min timer) | ✅ Active | Same script, same logic |
| Claude | Javier initiates session | ✅ Working | Session-bound by design |
| djinn-daily | 8 AM timer | ✅ Active | opencode wired, deepseek-r1:7b for PLAN.md |
| OpenClaw main agent | Discord + Telegram | ✅ Active | mistral:7b (200k ctx, thin relay). Routes: note:/law:/code:/slipbox: prefixes |
| OpenClaw coder agent | `/agent coder` | ✅ Available | qwen2.5-coder:7b, shell + code tasks |
| OpenClaw law agent | `/agent law` | ✅ Available | deepseek-r1:7b, IRAC + LSAT study partner |
| Clerk | djinn-clerk timer (1-hr) + @Clerk in COMMS.md | ✅ Active | qwen2.5:7b — RAW/ → structured vault notes with hierarchical tags |
| Slipbox | @Slipbox in COMMS.md + djinn-slipbox --scan | ✅ Available | nomic-embed-text + qwen2.5:7b — semantic linking + hierarchical tags |
| DesignGenAgent | `djinn-design "<brief>"` or `design <brief>` in Discord/Telegram | ✅ Live | phi4:14b (local) → Claude if API key set. Outputs concept JSON + parametric OpenSCAD |
| DesignEditAgent | `djinn-design --job N --edit "<req>"` | ✅ Live | Modifies existing SCAD without rebuilding |
| ProtoOptAgent | `djinn-design --job N --optimize` | ✅ Live | Renders prototype-light + production-ready STLs |
| DOEPrintOptAgent | `djinn-design --job N --doe [fast\|cheap\|balanced]` | ✅ Live | Taguchi factor grid → slicer profile, no test prints needed |
| PlateNestAgent | `djinn-design --job N --plate` | ✅ Live | Decimate → arrange → export plate STL (auto-handles >200MB) |
| FairPrintAgent | `djinn-print-quote` / `quote <json>` Discord/Telegram | ✅ Live | Commission pricing: (material+machine+labor+design)/0.60 — machine runtime (~$0.20/hr) separate from labor. --quick requires TTY. |

**Known limitation:** opencode in headless mode (comms-processor) generates text responses but does not reliably execute shell tools — model treats tasks as conversation, not execution. Best for: summaries, file writes, status reports. For real shell execution: route to Claude or use direct SSH.

**OpenClaw tool execution:** 45 allowlist entries covering bash, git, python, node, npm, curl, jq, and all standard coreutils. Shell execution is enabled.

---

## Key Paths

| Path | Purpose |
|------|---------|
| `~/Obsidian/` | Vault — single source of truth |
| `~/.openclaw/workspace/` | Djinn identity + agent config files |
| `~/Obsidian/djinn/workspace/` | Symlink → ~/.openclaw/workspace/ (Obsidian visibility) |
| `~/Obsidian/djinn/communications/` | Inter-agent comms — COMMS.md is active channel |
| `~/Obsidian/djinn/skills/` | Skill specs — [[skills/README]] |
| `~/Obsidian/djinn/printer/process/` | Print intake SOP, log, benchmarks, filament profiles |
| `~/Obsidian/djinn/printer/agent/` | Print agent stack — print_agent.py + orchestrator/ |
| `~/Obsidian/djinn/printer/agent/orchestrator/` | 6-agent manufacturing pipeline (DesignGen→Plate→Price) |
| `~/Obsidian/djinn/printer/commissions/` | FairPrintAgent pricing spec + quote history log |
| `~/Obsidian/djinn/printer/library/` | Model library — vault-backed, design-cost auto-detection |
| `~/.config/djinn/` | Secrets — env files, chmod 600, never in git |
| `~/.config/djinn/claude.env` | Anthropic API key (optional) — enables Claude routing in djinn-design |
| `~/.local/share/djinn/print-queue.json` | Print queue — extended with design/DOE/plate phase fields |
| `~/.venvs/djinn-orchestrator/` | Python 3.11 venv — anthropic, pyDOE2, trimesh, pymeshlab, scipy |
| `~/.opencode/bin/opencode` | opencode binary |
| `~/.local/bin/djinn-design` | Manufacturing orchestrator CLI |
| `~/.local/bin/djinn-print-quote` | Commission pricing CLI (FairPrintAgent) |
| `~/.local/bin/` | All operational scripts — heartbeat, vault-sync, djinn-* |

---

## Communications — Active Channels

| Channel | File | Use |
|---------|------|-----|
| Primary | [[COMMS]] | All inter-agent messages — append only |
| Alerts | Telegram | Real-time signals, interrupts |
| Archived | `communications/archive/` | Old Salomon-to-Typhon.md etc. — superseded by COMMS.md |

---

## Ollama Context Windows (Salomon)

Fixed 2026-05-23 — original 131072 num_ctx caused VRAM overflow (14GB KV cache) → LLM timeout.

| Model | num_ctx | VRAM est | Notes |
|-------|---------|----------|-------|
| qwen2.5:7b | 16384 | ~5.9GB | Main agent — fits with headroom |
| deepseek-r1:7b | 8192 | ~4.7GB | Reasoning |
| qwen2.5-coder:7b | 16384 | ~5.9GB | Coder agent |
| llama3.2-vision:11b | 4096 | ~8GB | Vision — tight, needs offload |
| phi4:14b | 16384 | 9.1GB+ | CPU offload required |

---

## Key Paths — Agent Scripts

| Path | Purpose |
|------|---------|
| `~/.local/bin/djinn-clerk` | Clerk — RAW/ Perplexity → structured vault note |
| `~/.local/bin/djinn-embed` | Embedding index builder (nomic-embed-text) |
| `~/.local/bin/djinn-slipbox` | Slipbox — semantic linking + hierarchical tags |
| `~/.djinn/embeddings/vault.json` | Embedding cache (incremental, auto-updated) |
| `~/.local/share/djinn/clerk-processed.json` | Clerk state — tracks processed RAW files |

## Pending Work

| Item | Priority | Notes |
|------|----------|-------|
| Add Anthropic API key | High | `~/.config/djinn/claude.env` — enables Claude routing in djinn-design (currently phi4:14b) |
| Add Salomon OpenRouter key | Medium | Placeholder in ~/.opencode/opencode.json — get key at openrouter.ai |
| Run djinn-embed --full after index completes | High | Initial build started 2026-05-23 — let it finish |
| Test Slipbox end-to-end after embed completes | High | Needs embedding cache to find similar notes |
| Benchmark prints | Low | CRtestcube + ksr_fdmtest to establish stock baselines |
| Voice pipeline final wiring | Backlog | Typhon |
| 1TB Passport SSD integration | Low | Javier mentioned it — available for large model/STL storage if needed |

---

*— Claude, 2026-05-23*
