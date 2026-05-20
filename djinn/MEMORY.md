---
subject: Djinn Operations
tags: [djinn, memory, agents]
created: 2026-05-20
updated: 2026-05-20
---

# MEMORY.md — Djinn Shared Agent Memory

This file is the shared memory index for all Djinn agents. Read it before acting. Update it when state changes.

---

## System State

| Machine | Status | Last Seen | Notes |
|---------|--------|-----------|-------|
| Salomon | ✅ Online | 2026-05-20 | Primary workstation, all systems live |
| Typhon | ⚠️ Unreachable | 2026-05-20 | 192.168.50.113 — ping fails from Salomon. Subnet mismatch under investigation. |
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
- [ ] Phase 6 — Agents & Skills definitions
- [ ] Investigate Typhon subnet gap (192.168.50.x vs 192.168.1.x)

### Javier (requires human action)
- [ ] Get Telegram bot token from @BotFather → add to `~/.config/djinn/telegram.conf`
- [ ] Verify Typhon is online and confirm its current IP/network interface

---

## Key Decisions (summary — see decision-log.md for full history)

- **Vault** = single source of truth. GitHub + GDrive sync.
- **Three-lane architecture**: Ollama local (Salomon) → Ollama local (Typhon) → Claude API
- **Communication**: markdown files in `djinn/communications/` — append only, never overwrite
- **Signing**: always sign with `— <AgentName>`, git author set per agent

---

*— Claude*
