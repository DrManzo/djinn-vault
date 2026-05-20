---
subject: Djinn Operations
tags: [djinn, system-state, operations]
created: 2026-05-20
updated: 2026-05-20
---

# SYSTEM-STATE.md — Djinn Operational State

Inter-machine operational state. Not identity (that lives in ~/.openclaw/workspace/MEMORY.md).
Read before acting. Update when state changes.

---

## Machine Status

| Machine | Status | Last Seen | Notes |
|---------|--------|-----------|-------|
| Salomon | ✅ Online | 2026-05-20 22:45 PDT | All systems live |
| Typhon | ⏳ Offline | 2026-05-20 | Boot + sync-up instructions queued in Salomon-to-Typhon.md |
| Claude | ✅ Online | 2026-05-20 | Claude Code CLI active, OAuth authenticated |

---

## Active Services — Salomon

| Service | Status | Notes |
|---------|--------|-------|
| OpenClaw gateway | ✅ Live | 127.0.0.1:18789, token auth |
| Telegram @OgDjinn_bot | ✅ Live | Polling, locked to Javier (7620067588) |
| Discord @OgDjinn | ✅ Live | Djinn OC guild, inbound/outbound |
| 8 AM cron | ✅ Fixed | id: 25a700db — was failing (Telegram disabled), now live |
| Ollama | ✅ Running | 0.0.0.0:11434 — 8 models, remote access enabled |
| Heartbeat timer | ✅ Active | 5-min → HEARTBEAT.md |
| Vault sync | ✅ Active | 2-min → GitHub + GDrive |
| Forge sync | ✅ Active | 15-min → GDrive |
| Voice pipeline | ✅ Tested | voxtype STT + Piper TTS (en_GB-alba-medium) |

---

## Ollama Model Routing

| Model | Runs On | Remote From Typhon | Role |
|-------|---------|-------------------|------|
| qwen2.5:7b | Both | Yes | Default — tool use + conversation |
| deepseek-r1:7b | Both | Yes | Deep reasoning |
| qwen2.5-coder:7b | Both | Yes | Code / dev |
| phi4:14b | Salomon | Yes | Notes / APA (on demand) |
| llama3.2-vision:11b | Salomon | Yes | Vision (on demand) |
| mistral:7b | Salomon | Yes | Creative writing |
| llama3.2:3b | Typhon | Local only | Lightweight admin |
| qwen2.5:1.5b | Typhon (pending pull) | — | Lightweight automation |
| nomic-embed-text | Both | Yes | Embeddings |

---

## Pending

### Typhon (offline — instructions queued)
- [ ] Boot machine
- [ ] Git rebase (file renames)
- [ ] Pull qwen2.5:1.5b
- [ ] Verify Ollama remote routing
- [ ] Set up heartbeat-typhon timer → HEARTBEAT-typhon.md
- [ ] Verify vault-sync at 2-min
- [ ] Report network interfaces + SSH status
- [ ] Respond in Typhon-to-Salomon.md

### Javier
- [ ] Boot Typhon
- [ ] Test Telegram: message @OgDjinn_bot

---

## Communication Channels

| From → To | File |
|-----------|------|
| Salomon → Typhon | `djinn/communications/Salomon-to-Typhon.md` |
| Typhon → Salomon | `djinn/communications/Typhon-to-Salomon.md` |
| Any → Claude | `djinn/communications/Claude-inbox.md` |
| Claude → All | `djinn/communications/Claude-outbox.md` |

---

## Key Decisions

- Vault = single source of truth. GitHub primary, GDrive backup.
- Three-lane architecture: Ollama (Salomon) + Ollama (Typhon) + Claude API
- Communication: markdown files in djinn/communications/ — append only, never overwrite
- Signing: `— <AgentName>`, git author set per agent
- OpenClaw workspace files (~/.openclaw/workspace/) = Djinn identity layer (do not rename)
- Vault djinn/ files = inter-machine ops layer (SYSTEM-STATE, ROUTING, HEARTBEAT, comms)

---

*— Claude*
