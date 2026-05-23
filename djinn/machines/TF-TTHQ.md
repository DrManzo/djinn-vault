---
title: Machine — TF/TTHQ (Typhon)
tags: [djinn, machine, typhon, hardware, models]
created: 2026-05-22
updated: 2026-05-23
---

# Machine: TF/TTHQ — Typhon

**Callsign:** TF/TTHQ
**Network name:** Typhon
**Role:** Storage node, printer bot host, secondary Djinn agent
**SSH:** `ssh -i ~/.ssh/id_ed25519 tf-tthq@192.168.1.113`
**Related:** [[SYSTEM-STATE]] | [[ROUTING]] | [[HEARTBEAT-typhon]]

Changes from this machine are signed: `— TF/TTHQ`

---

## Hardware

| Component | Spec |
|-----------|------|
| **CPU** | 11th Gen Intel Core i5-11400H @ 2.70GHz (6C/12T, up to 4.5GHz) |
| **RAM** | 14GB |
| **GPU** | NVIDIA GeForce GTX 1650 Max-Q — 4GB VRAM |
| **OS Drive** | 250GB NVMe SSD (KINGSTON) — `/` |
| **Bulk Storage** | 1TB HDD (WDC WD10SPZX) — `/mnt/storage` |
| **OS** | Ubuntu 26.04 LTS |

---

## Storage Layout

| Mount | Device | Size | Used | Contents |
|-------|--------|------|------|---------|
| `/` | nvme0n1p2 | 233G | 55G | OS, apps, configs |
| `/mnt/storage` | sda1 | 916G | ~35G | Ollama models (33G), Obsidian, forge, Project-Resources |

**Disk allocation:**
- `/mnt/storage/ollama-system/` — Ollama model files (symlinked from `/usr/share/ollama/.ollama`)
- `/mnt/storage/Obsidian/` — vault (symlinked from `~/Obsidian`)
- `/mnt/storage/forge/` — forge repo (symlinked from `~/forge`)
- `/mnt/storage/Project-Resources/` — resources repo

---

## Ollama Models

Ollama runs as system service (`ollama` user). Models stored at `/mnt/storage/ollama-system/models/` (symlinked from `/usr/share/ollama/.ollama`).

| Model | Size | Can Run Locally? | Notes |
|-------|------|-----------------|-------|
| qwen2.5:7b | 4.7GB | ✅ Yes | Default — tool use, general |
| deepseek-r1:8b | 5.2GB | ✅ Yes | Reasoning (note: :8b not :7b) |
| qwen2.5-coder:7b | 4.7GB | ✅ Yes | Code |
| qwen2.5:1.5b | 986MB | ✅ Yes | Ultralight admin |
| llama3.2:3b | 2.0GB | ✅ Yes | Lightweight tasks |
| phi4:14b | 9.1GB | ⚠️ Limited | Needs CPU offload (14GB RAM) |
| llama3.2-vision:11b | 7.8GB | ⚠️ Limited | Vision — needs offload |
| nomic-embed-text | 274MB | ✅ Yes | Embeddings |

**Remote access:** Typhon's opencode can reach Salomon's models via `ollama-salomon` provider at `http://192.168.1.225:11434/v1`

---

## OpenCode Config

**File:** `~/.opencode/opencode.json`
**Providers:**
- `ollama` — local (localhost:11434)
- `ollama-salomon` — remote (192.168.1.225:11434)
- `openrouter` — free tier (API key configured)

**Default model:** `ollama/qwen2.5:7b`

---

## Services

| Service | Status | Notes |
|---------|--------|-------|
| Ollama | ✅ Running | System service, models on 1TB |
| comms-processor | ✅ Active | 3-min timer, scans COMMS.md for @Typhon tasks |
| vault-sync | ✅ Active | 15-min timer via rclone → gdrive |
| djinn-printer-bot | ✅ Live | Telegram bot, token in `~/.config/djinn/printer-bot.env` |
| heartbeat | ✅ Active | 5-min → `djinn/communications/HEARTBEAT-typhon.md` |

---

## Installed Apps

| App | Method | Notes |
|-----|--------|-------|
| 1Password | snap | v8.11.14 |
| Discord | snap | v1.0.139 |
| rclone | apt | gdrive remote configured and working |

## Git Auth

All repos use HTTPS with fine-grained PAT:
- Stored: `~/.config/djinn/github.env` (chmod 600) + `~/.git-credentials`
- Repos: `djinn-vault`, `typhons-cyber-forge`, `Project-Resources`
- Rotate at: github.com/settings/tokens (fine-grained)

---

## Model Capacity Notes

With 14GB RAM and GTX 1650 4GB VRAM:
- **Runs well:** anything ≤8B parameters
- **Runs with offload:** 8–14B (slower, CPU handles overflow)
- **Cannot run locally:** >14B — route to Salomon via `ollama-salomon`
- **Best use:** Lightweight admin, quick queries, printer bot, storage ops

---

*— Claude, 2026-05-23*
