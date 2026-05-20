---
subject: Djinn Operations
tags: [djinn, system-state, operations]
created: 2026-05-20
updated: 2026-05-20
---

# SYSTEM-STATE.md — Djinn Operational State

This file tracks live system state across machines. Not identity (see ~/.openclaw/workspace/MEMORY.md). Read before acting. Update when state changes.

---

## System State

| Machine | Status | Last Seen | Notes |
|---------|--------|-----------|-------|
| Salomon | ✅ Online | 2026-05-20 | Primary workstation, all systems live |
| Typhon | ⚠️ Offline | 2026-05-20 | 192.168.50.113 — same router, different subnet. Static route added on Salomon. Will connect once Typhon boots. |
| Claude | ✅ Online | 2026-05-20 | Claude Code CLI active on Salomon, OAuth authenticated |

---

## Active Services (Salomon)

| Service | Status | Notes |
|---------|--------|-------|
| Ollama | ✅ Running | 0.0.0.0:11434 — 8 models, remote access enabled |
| Heartbeat timer | ✅ Active | 5-min systemd timer → HEARTBEAT.md |
| Vault sync | ✅ Active | 2-min vault-sync.timer → GitHub |
| Voice pipeline | ✅ Tested | voxtype STT + Piper TTS — PASS |
| Telegram bot | 🔑 Needs token | Script ready at ~/.local/bin/djinn-telegram-daily |

---

## Ollama Remote Routing

Typhon connects to Salomon's Ollama at `192.168.1.225:11434`.
Confirmed working: phi4:14b inference ran on Salomon GPU, streamed to Typhon.

| Model | Runs On | Available Remotely |
|-------|---------|-------------------|
| qwen2.5:7b | Both | Yes |
| deepseek-r1:7b | Both | Yes |
| qwen2.5-coder:7b | Both | Yes |
| phi4:14b | Salomon only | Yes |
| llama3.2-vision:11b | Salomon only | Yes |
| mistral:7b | Salomon only | Yes |
| llama3.2:3b | Typhon only | Local |
| nomic-embed-text | Both | Yes |

---

## Pending Tasks

### Typhon (queued — awaiting machine to come online)
- [ ] Pull `qwen2.5:1.5b`
- [ ] Re-verify Ollama remote routing after any config changes
- [ ] Set up 5-min heartbeat timer (systemd)
- [ ] Wire Telegram bot — needs token from @BotFather
- [ ] Git rebase: `git fetch origin && git reset --hard origin/main`

### Claude
- [ ] Phase 6 — build djinn-daily and djinn-sync skills on Salomon
- [ ] Confirm Typhon connectivity once it boots (static route already in place)

### Javier (requires human action)
- [ ] Boot Typhon
- [ ] Telegram bot token from @BotFather → `~/.config/djinn/telegram.conf`

---

## Key Decisions (summary — see decision-log.md for full history)

- **Vault** = single source of truth. GitHub + GDrive sync.
- **Three-lane architecture**: Ollama local (Salomon) → Ollama local (Typhon) → Claude API
- **Communication**: markdown files in `djinn/communications/` — append only, never overwrite
- **Signing**: always sign with `— <AgentName>`, git author set per agent

---

*— Claude*
