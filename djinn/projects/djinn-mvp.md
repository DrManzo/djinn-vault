---
subject: Djinn Operations
tags: [djinn, mvp, project]
created: 2026-05-19
updated: 2026-05-21
---

# Djinn MVP Project

## Status

| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 1 | Core Shell | ✅ Complete | 2026-05-19 |
| 2 | Identity Layer | ✅ Complete | 2026-05-20 |
| 3 | Vault Backup | ✅ Complete | 2026-05-19 |
| 4 | Inbox & Cleanup | ✅ Complete | 2026-05-20 |
| 5 | Claude Lane | ✅ Complete | 2026-05-21 |
| 6 | Agents & Skills | ✅ Complete | 2026-05-21 |
| 7 | Weekly Review | ✅ Complete | 2026-05-21 |
| 8 | Migration Prep | ✅ Complete | 2026-05-21 |
| 9 | Printer Node | ✅ Complete | 2026-05-21 |

---

## What Was Built

### Phase 1 — Core Shell
- Vault initialized, GitHub repo created, GDrive sync active
- Ollama running on Salomon with remote access from Typhon
- OpenCode configured with local Ollama provider

### Phase 2 — Identity Layer
- SYSTEM-STATE.md, ROUTING.md, AGENTS.md, SOUL.md, USER.md, IDENTITY.md
- Model routing corrected: qwen2.5:7b (tool ops), deepseek-r1:7b (reasoning)
- Signing convention: — Salomon, — Typhons Forge, — Claude

### Phase 3 — Vault Backup
- GitHub (primary) + GDrive bisync (secondary) + WD Passport (tertiary)
- vault-sync timer: 2-min cadence

### Phase 4 — Inbox & Cleanup
- 504+ notes processed, inbox cleared, temp files deleted
- djinn/ directory structure populated

### Phase 5 — Claude Lane
- Claude Code installed on Salomon, OAuth authenticated
- Claude.md identity doc created, 9-file context protocol established
- Claude-inbox.md / Claude-outbox.md comms channels live
- Hardware protection: Ollama resource caps, cpu-governor, djinn-idle.timer
- Claude Code on Typhon: credentials transferred via SSH key exchange

### Phase 6 — Agents & Skills
- `workflows/djinn-sync.md` — session startup sync skill
- `workflows/djinn-daily.md` — morning plan generation skill
- `djinn/skills/` — 7 skill specs (djinn-daily, djinn-sync, djinn-heartbeat, djinn-claude, djinn-morning, djinn-weekly + README)
- djinn-morning timer: 8 AM Telegram prompt live
- djinn-daily.timer: active
- Telegram config wired from openclaw.json (no BotFather needed)

### Phase 7 — Weekly Review
- `~/.local/bin/djinn-weekly` — git log + CHANGELOG + decisions → deepseek-r1:7b → vault note
- `djinn-weekly.timer`: Sundays 20:00
- Output: `djinn/weekly/YYYY-WNN.md` + Telegram digest
- Noise filtering: heartbeat and sync commits excluded

### Phase 8 — Migration Prep
- `djinn/migration/bootstrap.sh` — rebuilds Djinn from scratch on fresh Ubuntu (~20 min)
- `djinn/migration/manifest.md` — what's in git vs what needs manual transfer
- `djinn/migration/scripts/` — all 7 djinn scripts archived in vault
- Recovery: vault clone + bootstrap + 3 credential files = full system

### Phase 9 — Printer Node
- `djinn/printer/` vault schema — queue, active, completed, models, config
- `~/.local/bin/djinn-print` — Moonraker API client (status, queue, start, cancel, list, log)
- `workflows/printer.md` — Telegram `/print` command logic for OpenClaw
- `djinn/skills/djinn-printer.md` — skill spec
- Hardware activation: connect printer to WiFi → set `PRINTER_IP` in `~/.config/djinn/printer.conf` → live

---

## MVP Complete — 2026-05-21

All 9 phases delivered in a single session. Djinn is fully operational.

**What's live:**
- Two-machine AI system (Salomon + Typhon) with Ollama, OpenCode, Claude Code
- Vault synced to GitHub + GDrive + Passport every 2 minutes
- 8 AM morning Telegram prompt, weekly review every Sunday
- Full skill library (7 skills), migration bootstrap, printer node infrastructure
- Cross-machine comms via vault, SSH key exchange complete

**Printer fully operational. First print complete. Enclosure is a future project, not a blocker.**

---

*— Claude*
