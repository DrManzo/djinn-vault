---
title: Typhon — Machine Profile
tags: [djinn, machine, typhon, hardware]
updated: 2026-05-23
---

# Typhon — Machine Profile (Djinn's Hub)

**Host:** Typhon (tf-tthq) — 192.168.1.113
**Role:** Storage, sync, printer bot, lightweight inference node
**Related:** [[SYSTEM-STATE]] | [[Salomon]] | [[HEARTBEAT-typhon]] | [[ROUTING]] | [[COMMS]]

**Introduced:** 2026-05-20
**Host:** typhon (Typhons Forge)
**Role:** Primary workstation / Djinn host / Storage & Sync node  
**Kernel:** 7.0.0-15-generic

---

## Hardware

| Component | Spec |
|-----------|------|
| **CPU** | 11th Gen Intel Core i5-11400H @ 2.70GHz |
| **RAM** | 14 GB DDR4 |
| **GPU** | NVIDIA GeForce GTX 1650 (Max-Q) — 4 GB VRAM |
| **GPU Driver** | NVIDIA 595.71.05 |
| **Storage (OS)** | 250GB NVMe SSD (KINGSTON OM8PDP3256B-AI1) — 174 GB free |
| **Storage (Bulk)** | 1TB HDD (WDC WD10SPZX) mounted at `/mnt/storage` — 870 GB free |
| **Swap** | 4 GB |

---

## Models Currently Stored (on 1TB HDD)

| Model | Size | Can Run Here? | Notes |
|-------|------|---------------|-------|
| deepseek-r1:8b | 5.2 GB | Yes | Deep reasoning |
| qwen2.5:7b | 4.7 GB | Yes | Default — live lane |
| qwen2.5-coder:7b | 4.7 GB | Yes | Code / dev |
| phi4:14b | 9.1 GB | Limited (CPU offload) | Notes / APA format |
| llama3.2-vision:11b-instruct-q4_K_M | 7.8 GB | Stretch (CPU offload) | Image / vision |
| nomic-embed-text:latest | 274 MB | Yes | Embeddings |
| llama3.2:3b | 2.0 GB | Yes — GPU native | Lightweight admin tasks |
| `qwen2.5:1.5b` | 1.0 GB | Yes — GPU native | Tiny, perfect for automation scripts |

**Total stored:** ~34.8 GB

---

## Capacity Notes

- **Max model this machine can run comfortably on GPU alone:** ~7B-8B parameter
- **Larger models (11B-14B):** Run with CPU offloading — slower but functional
- **Storage available:** ~870 GB free on 1TB HDD — can download any model size
- **SSD space:** 174 GB free for OS, configs, apps

---

## Installed Tools

- Ollama (local LLM runtime)
- OpenCode (coding agent)
- rclone (Google Drive sync — remote: `gdrive`)
- Git
- 1Password (snap)
- Discord (snap)

---

## Recommended Models to Pull (by Use Case)

### 🎛 Admin / Automation (lightweight, fast, CPU-only friendly)

| Model | Size | Why |
|-------|------|-----|
| `llama3.2:3b` | ~2 GB | Already stored — GPU native, fast admin tasks |
| `qwen2.5:1.5b` | ~1 GB | Tiny, perfect for automation scripts |
| `phi3:3.8b` | ~2.3 GB | Microsoft's efficient model — good reasoning for size |
| `deepseek-r1:1.5b` | ~1 GB | Lightweight reasoning, fast responses |

### ✍️ Screenwriting / Creative Writing

| Model | Size | Why |
|-------|------|-----|
| `mistral:7b` | ~4.1 GB | Excellent prose quality, strong creative writing |
| `dolphin-mistral:7b` | ~4.1 GB | Creative fine-tune, uncensored, good for dialogue |
| `qwen2.5:7b` | 4.7 GB | Already stored — solid all-round writer |
| `phi4:14b` | 9.1 GB | Already stored — structured / academic writing |

### 🖼 Photo / Video Understanding

| Model | Size | Why |
|-------|------|-----|
| `llama3.2-vision:11b` | 7.8 GB | Already stored — image analysis, frame-by-frame |
| `llava:7b` | ~4.7 GB | Dedicated vision model — good for photo analysis |
| `llava-llama3:8b` | ~5.5 GB | Strong vision + reasoning combo |

### 💪 Heavy Lifting (needs more GPU / multi-machine)

| Model | Size | Why |
|-------|------|-----|
| `mixtral:8x7b` | ~26 GB | MoE — powerful but needs 20+ GB RAM |
| `qwen2.5:72b` | ~40 GB | Top-tier, requires beefy machine |
| `llama3.1:70b` | ~39 GB | Large context, needs serious hardware |
| `deepseek-r1:671b` | ~400 GB | Massive — cluster only |

---

## Resource Pooling Plan

### Current State
- **Djinns Hub (Typhon)** — i5-11400H, 14 GB RAM, GTX 1650 4GB, 1TB HDD + 250GB SSD
- **Salomon** — Ryzen 9 8940HX, 32 GB RAM, RTX 5060 8GB, 1TB NVMe
- **Claude** — Anthropic API (Pro subscription), Claude Code CLI on Salomon

### Agent Topology

| Agent | Machine | Role | Provider |
|-------|---------|------|----------|
| opencode | Salomon | Live lane, daily ops, automation | Ollama local |
| opencode | Typhon | Storage/sync, lightweight tasks | Ollama local |
| Claude | Salomon (CLI) | Architecture, cross-domain synthesis | Claude API (Pro) |

### Ollama Remote Server — ACTIVE ✅
- **Status:** Live since 2026-05-20 06:42 PDT
- **Salomon IP:** 192.168.1.225:11434
- **Connection:** `OLLAMA_HOST=192.168.1.225:11434`
- **Test:** phi4:14b remote inference confirmed — haiku generated on Salomon GPU, streamed to Typhon
- **Models available remotely:** qwen2.5:7b, deepseek-r1:7b, qwen2.5-coder:7b, mistral:7b, phi4:14b, llama3.2-vision:11b, nomic-embed-text, qwen3.6:latest (36B)

### Heartbeat Timer — ACTIVE ✅
- **Status:** Live since 2026-05-21 07:47 UTC
- **Interval:** 5 minutes via systemd timer (`heartbeat-typhon.timer`)
- **Output:** `djinn/communications/HEARTBEAT-typhon.md`
- **Includes:** uptime, GPU stats, Ollama model count, disk, RAM

### Strategy Options

1. ~~**Ollama Remote Server**~~ — DONE, active and tested
2. **SSH Tunnel** — backup if direct connection fails
3. **Shared Model Cache** — if both machines access the same 1TB drive (via network mount), they share one model directory
4. **OpenCode Multi-Machine** — configure each OpenCode instance to route to whichever machine has the GPU power for the target model

### Model Distribution Plan
- Small/medium models (1-8B): run on either machine
- Large models (11-14B): run on Salomon (8GB VRAM + 32GB RAM) — accessed via remote Ollama
- Heavy models (70B+): run on Salomon, accessed remotely from Typhon
- Vision models: run on Salomon (more VRAM) — accessed via remote Ollama
- Typhon handles: lightweight tasks, storage, backup, GDrive sync, local inference (<8B)

---

*— Typhons Forge*
