---
subject: Djinn Operations
tags: [djinn, system-state, operations]
created: 2026-05-20
updated: 2026-05-22
---

# SYSTEM-STATE.md — Djinn Operational State

Inter-machine operational state. Not identity (that lives in ~/.openclaw/workspace/MEMORY.md).
Read before acting. Update when state changes.

---

## Machine Status

| Machine | Status | Last Seen | Notes |
|---------|--------|-----------|-------|
| Salomon | ✅ Online | 2026-05-20 22:45 PDT | All systems live |
| Typhon | ✅ Online | 2026-05-21 | All services live. Claude Code authenticated. |
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
| qwen2.5:1.5b | Typhon | Local only | Lightweight automation |
| nomic-embed-text | Both | Yes | Embeddings |

---

## Active Services — Typhon

| Service | Status | Notes |
|---------|--------|-------|
| Ollama | ✅ Running | Local models + remote routing to Salomon:11434 |
| Heartbeat timer | ✅ Active | 5-min → HEARTBEAT-typhon.md |
| Vault sync | ✅ Active | 2-min → GitHub + GDrive |
| Vault git pull | ✅ Active | 2-min |
| Claude Code | ✅ Authenticated | OAuth, Claude lane active |
| Printer conf | ✅ Set | 192.168.1.113 → ~/.config/djinn/printer.conf |
| Ender-3 V3 Plus | ✅ Live | Moonraker at 192.168.1.113:7125 |

---

## Pending

### Voice pipeline — final wiring (Typhon lead)
- [ ] Wire `djinn-voice` → remote Salomon Ollama (phi4:14b) for inference
- [ ] Test full loop: speak → voxtype STT → remote Ollama → local Piper TTS → play
- [ ] Report results

### Nice-to-haves (no blockers)
- [ ] Fix Piper lib path on Salomon for local fallback (`libpiper_phonemize.so.1`)
- [ ] Upgrade whisper model on Typhon (base → small/medium)
- [ ] Printer auto-start systemd service

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
