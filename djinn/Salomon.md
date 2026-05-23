---
title: Salomon — Machine Profile
tags: [djinn, machine, salomon, hardware]
updated: 2026-05-23
---

# Salomon — Machine Profile

**Host:** Salomon (drmanzo) — 192.168.1.225
**Role:** Heavy lifter — primary dev, Ollama hub, Claude Code lane
**Related:** [[SYSTEM-STATE]] | [[Djinns-Hub]] | [[HEARTBEAT]] | [[ROUTING]] | [[COMMS]]

**Introduced:** 2026-05-20
**Host:** Djinn
**Role:** Primary workstation / Djinn host / Dev machine
**Kernel:** 7.0.0-15-generic

---

## Hardware

| Component | Spec |
|-----------|------|
| **CPU** | AMD Ryzen 9 8940HX with Radeon Graphics |
| **RAM** | 32 GB DDR5 |
| **GPU** | NVIDIA GeForce RTX 5060 Laptop GPU — 8 GB VRAM |
| **GPU Driver** | NVIDIA (proprietary) |
| **Storage** | 1TB NVMe SSD (SK hynix PVC10 HFS001TEM9X173N) |
| **Swap** | 8 GB |

---

## Models Currently Stored

| Model | Size | Can Run Here? | Notes |
|-------|------|---------------|-------|
| qwen3.6:latest | 23 GB | Limited (CPU offload) | Retired — too heavy for daily use |
| qwen2.5:7b | 4.7 GB | Yes — GPU native | Default — live lane |
| phi4:14b | 9.1 GB | Yes — partial GPU offload | Notes / APA format |
| llama3.2-vision:11b-instruct-q4_K_M | 7.8 GB | Yes — GPU native | Image / vision |
| nomic-embed-text:latest | 274 MB | Yes | Embeddings |
| qwen2.5-coder:7b | 4.7 GB | Yes — GPU native | Code / dev |
| deepseek-r1:7b | 4.7 GB | Yes — GPU native | Deep reasoning |
| mistral:7b | 4.1 GB | Yes — GPU native | Creative writing / prose |

**Total stored:** ~58 GB

---

## Capacity Notes

- **Max model this machine can run comfortably on GPU alone:** ~8B-11B parameter
- **14B models:** Run with partial GPU offload — functional, ~5-10 tok/s
- **23B models (qwen3.6):** Heavy CPU offload — slow, usable for async tasks only
- **32B+ models:** Not practical without significant slowdown
- **Storage:** 1TB NVMe — fast model loads, no HDD bottleneck
- **RAM:** 32GB — can run multiple models simultaneously

---

## Installed Tools

- Ollama (local LLM runtime)
- OpenCode (coding agent / execution shell)
- OpenClaw (agent orchestration)
- Docker (Djinn container)
- rclone (Google Drive sync — remote: `gdrive`)
- Git (GitHub authenticated: DrManzo)
- 1Password
- Discord
- voxtype (STT — compiled, push-to-talk whisper daemon)
- Piper TTS (UK Alba voice)
- Postman, Burp Suite, Kali tools (cybersecurity stack)

---

## Recommended Models to Pull (by Use Case)

### 🎛 Admin / Automation (lightweight, fast)

| Model | Size | Why |
|-------|------|-----|
| `llama3.2:3b` | ~2 GB | Meta's small model — fast, good for quick tasks |
| `qwen2.5:1.5b` | ~1 GB | Tiny, perfect for automation scripts |
| `phi3:3.8b` | ~2.3 GB | Microsoft's efficient model — good reasoning for size |

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

---

## Resource Pooling Plan (fill when Typhon comes online)

### Current State
- **Salomon** — Ryzen 9 8940HX, 32 GB RAM, RTX 5060 8GB, 1TB NVMe
- **Typhon** — i5-11400H, 14 GB RAM, GTX 1650 4GB, 1TB HDD + 250GB SSD

### Strategy Options

1. **Ollama Remote Server** — run Ollama on Salomon with `OLLAMA_HOST=0.0.0.0`, Typhon connects via `OLLAMA_BASE_URL=http://salomon:11434`
2. **SSH Tunnel** — forward Ollama API port between machines
3. **Shared Model Cache** — if both machines access the same network mount, they share one model directory
4. **OpenCode Multi-Machine** — configure each OpenCode instance to route to whichever machine has the GPU power for the target model

### Model Distribution Plan
- Small/medium models (1-8B): run on either machine
- Large models (11-14B): run on Salomon (8GB VRAM + 32GB RAM)
- Heavy models (70B+): run on Salomon, accessed remotely from Typhon
- Vision models: run on Salomon (more VRAM)
- Typhon handles: lightweight tasks, storage, backup, GDrive sync

---

*— Salomon*
