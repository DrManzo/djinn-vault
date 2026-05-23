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
| OpenClaw gateway | ✅ Live | 127.0.0.1:18789, token auth |
| Telegram @OgDjinn_bot | ✅ Live | Polling, locked to Javier |
| Telegram printer bot | ✅ Live | djinn-printer-bot.service on **Typhon** |
| Ollama | ✅ Running | 0.0.0.0:11434 — 8 models, remote access enabled |
| Heartbeat timer | ✅ Active | 5-min → [[HEARTBEAT]] |
| Vault sync (GDrive) | ✅ Active | 2-min rclone |
| Vault sync (GitHub) | ✅ Active | git push after rclone |
| Forge sync | ✅ Active | 15-min → GDrive (~/forge/) |
| djinn-daily timer | ✅ Active | 8 AM → djinn-morning (bash only — opencode not yet wired) |
| djinn-weekly timer | ✅ Active | Sun 20:00 → weekly review |
| printer-error-logger | ✅ Active | Monitors Moonraker for errors |
| opencode | ✅ Available | ~/.opencode/bin/opencode — invoked manually or via triggers |

---

## Active Services — Typhon

| Service | Status | Notes |
|---------|--------|-------|
| Ollama | ✅ Running | Local models + remote routing to Salomon:11434 |
| Heartbeat timer | ✅ Active | 5-min → [[HEARTBEAT-typhon]] — now writes dynamic IP |
| Vault sync | ✅ Active | git pull 2-min |
| djinn-printer-bot | ✅ Live | python-telegram-bot, ~/.venvs/djinn-bot/, token in ~/.config/djinn/printer-bot.env |
| opencode | ✅ Available | Invoked manually — COMMS processor not yet deployed |

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

| Agent | Trigger | Status | Gap |
|-------|---------|--------|-----|
| Salomon opencode | Manual only | ⚠️ Partial | COMMS processor not deployed |
| Typhon opencode | Manual only | ⚠️ Partial | COMMS processor not deployed |
| Claude | Javier initiates session | ✅ Working | Session-bound by design |
| djinn-daily | 8 AM timer (bash) | ⚠️ Partial | Sends briefing but doesn't invoke opencode |
| COMMS→@Salomon | Not yet built | ❌ Missing | Phase 3 work |
| COMMS→@Typhon | Not yet built | ❌ Missing | Phase 3 work |

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

| Item | Phase | Owner |
|------|-------|-------|
| COMMS processor (Salomon) | Phase 3 | Claude builds, Salomon runs |
| COMMS processor (Typhon) | Phase 3 | Claude builds via SSH |
| Wire djinn-morning → opencode | Phase 4 | Claude |
| Typhon workspace parity | Phase 2 | Claude via SSH |
| Voice pipeline final wiring | Backlog | Typhon |

---

*— Claude, 2026-05-23*
