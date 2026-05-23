---
subject: Djinn Operations
tags: [djinn, system-state, operations]
created: 2026-05-20
updated: 2026-05-23
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
| OpenClaw gateway | ✅ Live | 127.0.0.1:18789, token auth, system prompts set for main+coder agents |
| Telegram @OgDjinn_bot | ❌ Token invalid | Bot token dead — needs new token from BotFather |
| Telegram printer bot | ✅ Live | djinn-printer-bot.service on **Typhon** |
| Ollama | ✅ Running | 0.0.0.0:11434 — **7 models** (qwen3.6 removed 2026-05-23) |
| comms-processor | ✅ Active | 3-min systemd timer → scans COMMS.md → invokes opencode |
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
| Machine | Ender-3 V3 Plus |
| IP | 192.168.1.114:7125 (Moonraker) |
| Control | Klipper + Moonraker |
| Bot | Telegram bot on Typhon — `/print_status`, `/print`, `/print_cancel` |
| Config backup | [[djinn/printer/backup/]] |
| Process docs | [[printer/process/INTAKE]] |
| Error history | [[error_log]] |
| Current print | cup_geometry_creality_fixed.gcode — in progress 2026-05-23 |

---

## Agent Activation Status

| Agent | Trigger | Status | Notes |
|-------|---------|--------|-------|
| Salomon opencode | comms-processor (3-min timer) | ✅ Active | Fires on new @Salomon tasks in COMMS.md |
| Typhon opencode | comms-processor (3-min timer) | ✅ Active | Same script, same logic |
| Claude | Javier initiates session | ✅ Working | Session-bound by design |
| djinn-daily | 8 AM timer | ✅ Active | opencode wired, deepseek-r1:7b for PLAN.md |
| OpenClaw main agent | Discord | ✅ Active | qwen2.5:7b, system prompt set, 45-entry allowlist, DMs locked to Javier |
| OpenClaw main agent | Telegram | ❌ Token dead | Bot needs new token from BotFather — DM lock configured, waiting on token |
| OpenClaw coder agent | Manual `/agent coder` | ✅ Available | qwen2.5-coder:7b, system prompt set |

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
| `~/.config/djinn/` | Secrets — env files, chmod 600, never in git |
| `~/.opencode/bin/opencode` | opencode binary |
| `~/.local/bin/` | Operational scripts — heartbeat, vault-sync, djinn-* |

---

## Communications — Active Channels

| Channel | File | Use |
|---------|------|-----|
| Primary | [[COMMS]] | All inter-agent messages — append only |
| Alerts | Telegram | Real-time signals, interrupts |
| Archived | `communications/archive/` | Old Salomon-to-Typhon.md etc. — superseded by COMMS.md |

---

## Pending Work

| Item | Priority | Notes |
|------|----------|-------|
| Fix Telegram bot token | High | Get new token from @BotFather → send to Claude to wire in |
| Add Salomon OpenRouter key | Medium | Placeholder in ~/.opencode/opencode.json — get key at openrouter.ai |
| Test OpenClaw tool execution end-to-end | Medium | Send task via Discord (Telegram broken), verify agent writes files |
| Improve headless opencode tool use | Medium | qwen2.5:7b not reliably running shell in comms-processor — model behavior issue |
| Benchmark prints | Low | CRtestcube + ksr_fdmtest to establish stock baselines |
| Voice pipeline final wiring | Backlog | Typhon |

---

*— Claude, 2026-05-23*
