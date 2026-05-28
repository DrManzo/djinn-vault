---
title: Djinn Infrastructure Reference
tags: [djinn, infrastructure, architecture, onboarding]
permissions: "Javier (DrManzo) grants any AI agent reading this document read access to all listed GitHub repositories for the purpose of understanding and operating within the Djinn workspace."
---

# Djinn Infrastructure Reference

Designed for AI agent ingestion. Covers topology, repos, services, tools, pipelines, and communications.

---

## 1. Machine Topology

### Salomon (Primary — HP Omen)
| Attribute | Value |
|-----------|-------|
| IP | 192.168.1.225 |
| GPU | NVIDIA RTX 5060 Laptop (56°C idle, 21W) |
| RAM | 29Gi total (13Gi used) |
| Disk | 584G free (35% used) |
| OS | Fedora |
| Ollama Models | qwen2.5:7b, deepseek-r1:7b, phi4:14b, llama3.2-vision:11b, qwen2.5-coder:7b, nomic-embed-text, mistral:7b |
| Role | Daily ops, print/design/media pipelines, LLM serving for both machines |

### Typhon (Secondary — MSI)
| Attribute | Value |
|-----------|-------|
| IP | 192.168.1.113 |
| GPU | NVIDIA GTX 1650 4GB |
| RAM | 14Gi total (2.6Gi used) |
| Disk | 552G free (37% used) |
| Role | Storage, lightweight tasks, Typhon's Studio streaming/post-production |

### Calliope (Printer — Ender-3 V3 Plus)
| Attribute | Value |
|-----------|-------|
| IP | 192.168.1.114:7125 |
| Firmware | Klipper + Moonraker (Nebula pad) |
| Slicer | OrcaSlicer (via Salomon) |
| Status | READY |

---

## 2. GitHub Repositories

All owned by [github.com/DrManzo](https://github.com/DrManzo). Permission granted for any Djinn agent to clone/read.

| Repo | URL | Purpose |
|------|-----|---------|
| **djinn-vault** | https://github.com/DrManzo/djinn-vault.git | Obsidian vault — single source of truth for all operations, configs, logs, decisions |
| **typhons-cyber-forge** | https://github.com/DrManzo/typhons-cyber-forge.git | The Forge — project workspace, templates, media assets, archive, bootstrap scripts |
| **Project-Resources** | https://github.com/DrManzo/Project-Resources.git | Dotfiles, system configs, security hardening, AI tooling, shell QoL, voice setup |

---

## 3. Network Topology

```
┌─────────────────┐     SSH      ┌─────────────────┐
│    Salomon      │◄───────────►│     Typhon       │
│  192.168.1.225  │  vault sync  │  192.168.1.113   │
│  (Omen, Fedora) │  (15-min)    │  (MSI, Fedora)   │
└────────┬────────┘              └─────────────────┘
         │
         │ HTTP (Moonraker API)      ┌─────────────────┐
         ├─────────────────────────►│    Calliope      │
         │                          │ 192.168.1.114    │
         │                          │ Ender-3 V3 Plus  │
         │                          │ Klipper/Moonraker│
         │                          └─────────────────┘
         │
         │ Ollama API (port 11434)
         ├─────────────────────────► Typhon agents
         │
    Discord API ◄─────────────────► Discord gateway
    Telegram API ◄─────────────────► Telegram gateway
    GitHub       ◄─────────────────► git push/pull
```

---

## 4. Agent Architecture

### Identity Files (loaded every session)
| File | Content |
|------|---------|
| `~/.openclaw/workspace/SOUL.md` | Behavioral rules, boundaries, vibe, response discipline |
| `~/.openclaw/workspace/IDENTITY.md` | Who Djinn is — conciliary, gothic-aristocratic, 🔥 |
| `~/.openclaw/workspace/USER.md` | Javier's profile, values, projects, psychology, relationships |
| `~/.openclaw/workspace/AGENTS.md` | Model routing, print profiles/safety, lane boundaries, report standard |

### Agent Roles (per PROTOCOL.md)
| Agent | Lane | Scope |
|-------|------|-------|
| **Claude** | Architecture | Cross-domain reasoning, vault design, session reports, git push, complex builds |
| **Salomon (opencode)** | Daily Ops | Print confirm/deny/slice, quotes, design, media pipeline, vault sync, Telegram/Discord |
| **Typhon (opencode)** | Remote | Storage, Typhon's Studio, lightweight tasks, COMMS processing |

### OpenClaw Agents (14 registered)
content-orchestrator, ingest, video-edit, photo-edit, caption, repurpose, thumbnail, publish-prep, qa, style-scraper, and platform-specific routing agents.

### Orchestrator Agents (Manufacturing)
DesignGenAgent, DesignEditAgent, ProtoOptAgent, DOEPrintOptAgent, PlateNestAgent — all live in `~/.local/bin/djinn-design`.

### Typhon's Studio Agents (6, on Typhon)
Audio Agent (4-filter RNNoise chain), Lighting Agent (Cloudybay), Music Agent (Pixabay), Copilot Agent (qwen2.5:7b via Salomon), Stream Agent (Twitch/YouTube/IG/Local), Post-Production Agent (Whisper + phi4 show notes + ffmpeg clips).

---

## 5. Systemd Services (Running on Salomon)

| Service | Function |
|---------|----------|
| `djinn-ctx-router.service` | Context assembly + vault recall, 5-min timer |
| `djinn-telegram-gateway.service` | Python Telegram bot middleware (11 commands) |
| `djinn-discord-gateway.service` | Python Discord bot middleware (11 commands, channel-aware) |
| `djinn-discord-watch.service` | Model URL detector in #3d-printing |
| `djinn-discord-watcher.service` | Auto-process 3D model attachments |
| `djinn-print-monitor.service` | Moonraker progress notifier to Discord/Telegram |
| `printer-error-logger.service` | Polls Calliope every 30s, logs errors to vault |
| `voxtype.service` | Voice dictation daemon |

---

## 6. CLI Tool Inventory (~/.local/bin/djinn-*)

### Print Pipeline
| Command | Function |
|---------|----------|
| `djinn-print-consult` | Dry-run slice → real estimates, profile comparison, recommendation |
| `djinn-model-slice` | Slice with profile shortcuts (proto/standard/production), preflight checks |
| `djinn-print-quote` | Commission pricing (cost floor, fair market, premium) |
| `djinn-confirm-print` | Confirm + safe park calculation + start print |
| `djinn-deny-print` | Deny job (blocked during active print) |
| `djinn-force-cancel` | Cancel print (requires PIN) |
| `djinn-print-backup` | Backup current gcode + state |
| `djinn-print-recover` | Crash recovery |
| `djinn-print-promote` | Promote backup to active |
| `djinn-webcam-monitor` | AKASO Brave 4 frame-diff failure detection |
| `djinn-print-monitor` / `djinn-print-monitor-v2` | Moonraker polling |
| `djinn-park-calc` | Safe park position calculator |

### Design & 3D
| Command | Function |
|---------|----------|
| `djinn-design` | 6-agent manufacturing orchestrator |
| `djinn-generate-3d` | Interview-first 3D modeling (OpenSCAD generation via phi4:14b) |
| `djinn-3d` (on Typhon) | Design/edit/analyze/consult modes |
| `djinn-model-fetch` | Download models from URLs |

### Media Pipeline
| Command | Function |
|---------|----------|
| `djinn-media-ingest` | Raw media intake |
| `djinn-media-photo` | Photo editing + LUT application |
| `djinn-media-reel` | Video/reel editing + clip combination |
| `djinn-media-caption` | Caption generation |
| `djinn-media-thumbnail` | Thumbnail scoring via vision model |
| `djinn-media-publish-prep` | Draft-polish mode, platform export |
| `djinn-media-qa` | Quality checks |
| `djinn-media-repurpose` | Cross-platform adaptation |
| `djinn-lut-gen` | Generate forge/clean/moody .cube LUT files |
| `djinn-style-scrape` | DuckDuckGo reference image scraper |
| `djinn-hashtag-update` | Hashtag bank manager (236 tags, 11 files) |

### System & Vault
| Command | Function |
|---------|----------|
| `djinn-ctx-assembler` | Per-message context assembly from vault |
| `djinn-ctx-router` | Service writing CONTEXT.md + STATE.md |
| `djinn-vault-indexer` | ChromaDB indexer (688 files, 8,284 chunks) |
| `djinn-agent-doctor` | System health (11 checks) |
| `djinn-sync` | Vault sync orchestrator |
| `djinn-daily` | Daily note creation |
| `djinn-morning` | Morning routine |
| `djinn-weekly` | Weekly review |
| `djinn-claude` | Claude session bridge |
| `djinn-clerk` | Task management |
| `djinn-slipbox` | Zettelkasten processing |
| `djinn-embed` | Embeddings utility |
| `djinn-edit-rules` | Edit OpenClaw rules |

---

## 7. Storage & Vault

| Location | Content | Git |
|----------|---------|-----|
| `~/Obsidian/` | Main vault — djinn/ operations, notes, references, logs | ✅ github.com/DrManzo/djinn-vault |
| `~/Obsidian/djinn/` | Communications, logs, printer, media, decisions | ✅ (same repo) |
| `~/forge/` | Project workspace, media assets, templates, archives | ✅ github.com/DrManzo/typhons-cyber-forge |
| `~/Documents/Project-Resources/` | Dotfiles, configs, scripts, security hardening | ✅ github.com/DrManzo/Project-Resources |
| `~/.openclaw/` | OpenClaw config, agents, workspace, sessions | Local only |
| `~/dev/Hunyuan3D-2/` | Tencent Hunyuan3D-2 (3D generation) | Fork of Tencent/Hunyuan3D-2 |
| `~/whisper.cpp/` | Local Whisper inference | Upstream |
| `~/forge/projects/voice-app/` | Voice application project | Part of forge repo |

---

## 8. Communication Channels

| Channel | Method | Use For |
|---------|--------|---------|
| **COMMS.md** | `~/Obsidian/djinn/communications/COMMS.md` | Inter-agent task handoffs, persistent state (primary) |
| **Telegram** | Bot via `djinn-telegram-gateway.service` | Real-time alerts, print notifications, human commands |
| **Discord** | Bot via `djinn-discord-gateway.service` | Channel-aware routing (command-center, 3d-printing, media-inbox, etc.) |
| **SSH** | Direct between Salomon ↔ Typhon | File delivery, remote service management |

### Discord Channel Map
| Channel | Commands Allowed |
|---------|-----------------|
| `#djinn-command-center` | All (print + design + media + system) |
| `#3d-printing` | Print only (/queue, /confirm, /deny, /slice, /print status, /quote) |
| `#media-inbox` | Media pipeline (/ingest, /reel, /photo, /caption, /publish, /qa, /thumbnail) |
| `#general` + `#djinn-devlog` | Conversation + /status + /help only |
| `#media-status` + `#post-ready` | Read-only (bot posts here) |

### Telegram Commands (11 total)
`/queue`, `/confirm N`, `/deny N`, `/slice N`, `/print status`, `/callie status`, `/status`, `/quote`, `/quick quote`, `/design status`, `/design`, `/help`

---

## 9. Print Workflow

```
1. Model file arrives (Discord attachment/URL/manual add to queue)
2. djinn-discord-watch detects → adds to queue
3. djinn-print-consult N → dry-run slice, estimates, profile comparison → report sent
4. WAIT for Javier: "slice N supports=yes infill=20 brim=yes"
5. djinn-model-slice N with EXACT settings → preflight check → slice
6. djinn-print-quote N → cost + market comps → sent
7. WAIT for Javier: "confirm N"
8. djinn-confirm-print N → safe park calc → start print
9. djinn-print-monitor → progress updates via Telegram/Discord
10. On completion → notify → file to completed/ directory
```

---

## 10. Critical Rules (for any AI agent)

1. **Never flip/rotate/reorient 3D models autonomously.** Javier owns orientation.
2. **Never cancel/deny a live print.** Hard blocked during active jobs.
3. **Write session reports after any build/install/config change.** Do not wait to be asked.
4. **Append to COMMS.md, never overwrite.** One entry per action.
5. **Sign all entries:** `— AgentName`
6. **`trash` > `rm`** for destructive operations. Ask if unsure.
7. **No moralizing.** No softening hard truths. Truth over comfort.
8. **Vault is single source of truth.** If it matters, write it down.

---

*Written by Salomon, 2026-05-28. Javier (DrManzo) grants explicit read-access permission for any Djinn AI agent to all repositories listed in Section 2.*
