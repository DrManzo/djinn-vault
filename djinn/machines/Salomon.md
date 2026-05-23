---
title: Machine — Salomon
tags: [djinn, machine, salomon, hardware, models]
created: 2026-05-23
updated: 2026-05-23
---

# Machine: Salomon

**Callsign:** Salomon
**Network name:** Salomon
**Role:** Primary Djinn node — heavy compute, OpenClaw gateway, vault-sync lead
**SSH:** local (this machine — `drmanzo@192.168.1.225`)
**Related:** [[SYSTEM-STATE]] | [[ROUTING]] | [[HEARTBEAT]]

Changes from this machine are signed: `— Claude`

---

## Hardware

| Component | Spec |
|-----------|------|
| **CPU** | AMD Ryzen 9 8940HX @ up to 5.4GHz (16C/32T) |
| **RAM** | 30GB |
| **GPU** | NVIDIA GeForce RTX 5060 Laptop GPU — 8GB VRAM |
| **OS Drive** | 937GB NVMe SSD — `/` |
| **OS** | Ubuntu 26.04 LTS |

---

## Storage Layout

| Mount | Device | Size | Used | Contents |
|-------|--------|------|------|---------|
| `/` | nvme0n1p2 | 937G | 288G | OS, apps, configs, vault, models |

All repos and model files live on the NVMe — no secondary drive.

---

## Ollama Models

Ollama runs as system service, exposed on `0.0.0.0:11434` (reachable by Typhon via `ollama-salomon` provider).

| Model | Size | Role |
|-------|------|------|
| qwen2.5:7b | 4.7GB | Default — tool use, conversation |
| deepseek-r1:7b | ~4.7GB | Deep reasoning |
| qwen2.5-coder:7b | 4.7GB | Code / dev |
| phi4:14b | 9.1GB | Notes, APA, long-form (on demand) |
| llama3.2-vision:11b | 7.8GB | Vision (on demand) |
| mistral:7b | 4.1GB | Creative writing |
| llama3.2:3b | 2.0GB | Lightweight tasks |
| nomic-embed-text | 274MB | Embeddings |

**Remote access:** Typhon reaches Salomon's models via `ollama-salomon` provider at `http://192.168.1.225:11434/v1`

---

## OpenCode Config

**File:** `~/.opencode/opencode.json`
**Providers:**
- `ollama` — local (localhost:11434)
- `openrouter` — free tier (key: `PASTE_SALOMON_KEY_HERE` — not yet configured)

**Default model:** `ollama/qwen2.5:7b`

---

## OpenClaw Config

**File:** `~/.openclaw/openclaw.json`
**Gateway:** `127.0.0.1:18789`, token auth
**Agents:** `main` (qwen2.5:7b), `coder` (qwen2.5-coder:7b)
**Channels:**
- Telegram `@DjinnOCBot` — DM policy: allowlist (Javier only)
- Discord `@OgDjinn` — DM policy: allowlist (Javier only)

**Exec allowlist:** 45 entries covering bash, git, python, node, npm, curl, jq, coreutils

---

## Services

| Service | Status | Notes |
|---------|--------|-------|
| OpenClaw gateway | ✅ Live | systemd user service, port 18789 |
| Telegram @DjinnOCBot | ✅ Live | Polling connected, DMs locked to Javier |
| Discord @OgDjinn | ✅ Live | Connected, guild 1504308482575433788 |
| Ollama | ✅ Running | 0.0.0.0:11434, 8 models |
| comms-processor | ✅ Active | 3-min timer → scans COMMS.md → invokes opencode |
| Heartbeat | ✅ Active | 5-min → [[HEARTBEAT]] |
| Vault sync (GDrive) | ✅ Active | 2-min rclone |
| Vault sync (GitHub) | ✅ Active | git push via `gh auth` |
| djinn-daily | ✅ Active | 8 AM → morning briefing (qwen2.5:7b, 240s timeout) |
| djinn-weekly | ✅ Active | Sun 20:00 → weekly review |

---

## Git Auth

Uses `gh` CLI (`gh auth git-credential`) — no token baked into remote URLs.
Remote: `https://github.com/DrManzo/djinn-vault.git`

---

## Model Capacity Notes

With 30GB RAM and RTX 5060 8GB VRAM:
- **Runs well:** anything ≤14B parameters on GPU
- **Runs with offload:** 14–30B (CPU handles overflow)
- **Best use:** Heavy reasoning, vision, code generation, long-form writing

---

*— Claude, 2026-05-23*
