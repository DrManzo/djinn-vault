---
title: Machine — TF/TTHQ (Typhon)
tags: [djinn, machine, typhon, hardware, models]
created: 2026-05-22
updated: 2026-07-01
---

# Machine: TF/TTHQ — Typhon

**Callsign:** TF/TTHQ
**Network name:** Typhon (Windows hostname currently reports `Typhon-4`, pending rename to `typhon` — see Status below)
**Role:** **Changed 2026-06-25** — dedicated shop machine (slicing, commissions, content, accounting). No longer storage/sync.
**IP:** 192.168.1.113 (host is up, all tested ports `filtered` as of 2026-07-01)
**SSH:** Broken — old key auth (`tf-tthq@192.168.1.113`) no longer applies, machine was wiped
**Related:** [[SYSTEM-STATE]] | [[ROUTING]] | [[HEARTBEAT-typhon]] | `djinn/workspaces/typhon-windows/setup-typhon.ps1`

Changes from this machine are signed: `— TF/TTHQ`

---

## ⚠️ Status: Mid-Migration, Onboarding Incomplete

This machine was reinstalled from Ubuntu to **Windows** around 2026-06-25 and repurposed
as Typhon's Forge shop machine. Everything below the divider describes the **old Ubuntu
setup** and is kept for reference only — it does not reflect current reality.

**What's confirmed as of 2026-07-01:**
- Host is up and answering ARP/port probes at 192.168.1.113, but every checked port
  (22, 3389, 445, 139, 5985, 11434) is `filtered` — no services exposed yet.
- Hostname still resolves as `Typhon-4.lan`, meaning `Rename-Computer -NewName "typhon"`
  in the setup script hasn't taken effect — the script likely hasn't been run (or completed
  + rebooted) on this box yet.
- No heartbeat since 2026-06-23 13:40 UTC (the old Linux heartbeat timer no longer exists
  on Windows; nothing has replaced it).
- Not present in the Tailscale tailnet yet.
- The setup script's post-reboot instructions call
  `curl https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/scripts/bootstrap-node.sh | bash`
  inside WSL2 Ubuntu — **this file does not exist anywhere in the vault or git history.**
  This blocks the WSL2-side Djinn install (Ollama, Claude Code, comms-processor, heartbeat)
  even once the ps1 script runs successfully.

**Onboarding checklist (what's left):**
1. Run/re-run `djinn/workspaces/typhon-windows/setup-typhon.ps1` as Administrator on the
   physical machine (debloat, OpenSSH, WSL2, winget installs, `C:\Forge\*`, firewall, rename, reboot).
2. Write the missing `djinn/scripts/bootstrap-node.sh` (WSL2/Windows-adapted version of
   `djinn/migration/bootstrap.sh`) before step 3 below can work.
3. Inside WSL2 Ubuntu, run the bootstrap script to install Ollama/Claude Code/vault clone/djinn scripts.
4. Paste Salomon's SSH pubkey into `C:\ProgramData\ssh\administrators_authorized_keys`.
5. Join Tailscale.
6. Import OrcaSlicer profiles from `Z:\forge\slicer-profiles` (verify the `Z:` share target
   IP is actually correct — the script maps to `\\192.168.1.176\storage`, which does not
   match a currently-live host on the LAN as of 2026-07-01).
7. Stand up a Windows/WSL2-appropriate heartbeat + comms-processor equivalent — the old
   systemd timers don't exist on this OS.

---

## Old Ubuntu Setup (superseded — reference only)

**SSH (dead):** `ssh -i ~/.ssh/id_ed25519 tf-tthq@192.168.1.113`

## Hardware

| Component | Spec |
|-----------|------|
| **CPU** | 11th Gen Intel Core i5-11400H @ 2.70GHz (6C/12T, up to 4.5GHz) |
| **RAM** | 14GB |
| **GPU** | NVIDIA GeForce GTX 1650 Max-Q — 4GB VRAM |
| **OS Drive** | 250GB NVMe SSD (KINGSTON) — `/` |
| **Bulk Storage** | 1TB HDD (WDC WD10SPZX) — `/mnt/storage` |
| **OS** | ~~Ubuntu 26.04 LTS~~ → Windows (as of 2026-06-25) |

---

## Storage Layout (Ubuntu — no longer applies)

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

## Ollama Models (Ubuntu — needs reinstall inside WSL2 or native Windows Ollama)

Ollama ran as system service (`ollama` user). Models stored at `/mnt/storage/ollama-system/models/` (symlinked from `/usr/share/ollama/.ollama`).

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

## OpenCode Config (Ubuntu — needs reinstall)

**File:** `~/.opencode/opencode.json`
**Providers:**
- `ollama` — local (localhost:11434)
- `ollama-salomon` — remote (192.168.1.225:11434)
- `openrouter` — free tier (API key configured)

**Default model:** `ollama/qwen2.5:7b`

---

## Services (Ubuntu — none of these exist on Windows yet)

| Service | Status | Notes |
|---------|--------|-------|
| Ollama | ❌ Gone with reinstall | Needs Windows/WSL2 reinstall |
| comms-processor | ❌ Gone with reinstall | 3-min timer, scans COMMS.md for @Typhon tasks |
| vault-sync | ❌ Gone with reinstall | 15-min timer via rclone → gdrive |
| djinn-printer-bot | ❌ Gone with reinstall | Telegram bot, token was in `~/.config/djinn/printer-bot.env` |
| heartbeat | ❌ Gone with reinstall | 5-min → `djinn/communications/HEARTBEAT-typhon.md` |

---

## Installed Apps (Ubuntu — no longer applies)

| App | Method | Notes |
|-----|--------|-------|
| 1Password | snap | v8.11.14 |
| Discord | snap | v1.0.139 |
| rclone | apt | gdrive remote configured and working |

## Git Auth (Ubuntu — credentials gone with reinstall, must be reprovisioned)

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
- **Best use:** Lightweight admin, quick queries, printer bot, storage ops (pre-Windows-migration usage — role has since changed to shop machine)

---

*— Claude, 2026-05-23. Updated 2026-07-01 for Windows migration/onboarding status.*
