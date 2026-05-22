---
subject: Djinn Operations
tags: [djinn, decisions, log]
created: 2026-05-19
---

# Decision Log

## 2026-05-19: Vault git initialized
- Repo: djinn-vault (private, GitHub)
- Remote: https://github.com/DrManzo/djinn-vault.git

## 2026-05-19: OpenCode configured with Ollama local
- Default model: qwen2.5:7b
- Provider: Ollama (http://localhost:11434/v1)

## 2026-05-19: Three-lane architecture adopted
- Live lane: Ollama qwen2.5:7b
- Dev lane: Claude (Pro subscription)
- Research: Perplexity → vault notes

## 2026-05-20: Claude Lane activated (Phase 5)
- Claude Code CLI installed on Salomon (`~/.local/bin/claude`)
- Claude identity document created: `djinn/Claude.md`
- CLAUDE.md config created at `~/.claude/CLAUDE.md`
- Agent topology updated: opencode (Salomon), opencode (Typhon), Claude (Salomon CLI)
- Signing convention established: `— Salomon`, `— Typhons Forge`, `— Claude`
- Auth: OAuth (Claude Pro) — requires interactive login via `claude` in terminal

## 2026-05-21: Phase 5 Complete — Claude Lane Fully Activated
- Claude.md created at `~/.openclaw/workspace/Claude.md` — defines role, 9-file context protocol, lane boundaries
- AGENTS.md routing table corrected — Role column added, duplicate deepseek row removed, Claude Code architecture row added
- opencode.json updated — temperature settings applied to all 6 models
- Ollama resource caps applied: 60% CPU, 20G RAM, no swap
- Ollama env vars set: MAX_LOADED_MODELS=2, KEEP_ALIVE=5m, GPU_MEMORY_FRACTION=0.80
- djinn-idle.timer active — nightly 22:00 model eviction (deepseek, phi4, coder)
- cpu-governor.service active — powersave enforced on boot (schedutil not available on AMD pstate)
- thermald skipped — Intel-only, AMD pstate handles thermals natively
- Typhon Claude setup: credentials transfer script at `djinn/scripts/typhon-claude-setup.sh`, background watcher running
- openclaw workspace versioned — initial git commit (13 files)
- Handoff package archived: `djinn/communications/djinn-handoff-package.md`

## 2026-05-22: Phase 9 — Printer Node architecture locked

- **Print server**: Creality Nebula pad running Klipper + Moonraker at `192.168.1.114:7125`
- **Decision**: Typhon KIAUH/Klipper install SKIPPED — Nebula pad is already a fully functional Moonraker node, reflashing MCU adds risk with zero benefit
- **Salomon** handles: modeling tools (FreeCAD, Blender, OpenSCAD), AI generation (Hunyuan3D-2), OrcaSlicer slicing, Claude lane work
- **Typhon** handles: Telegram bot daemon (always-on, lightweight, hits Moonraker over LAN)
- **PLR + thermal watchdog**: `plr.cfg` uploaded to Nebula pad — saves Z/layer at each layer change, polls every 5s for temp drops
- **Error logging**: `printer-error-logger.service` running on Salomon — polls Moonraker every 30s, logs to vault
- **idle_timeout**: Changed from 99999999 → 600s on Nebula pad — cat safety, turns off heaters + motors after 10 min idle
- **Printer IP**: Static-lease recommended at 192.168.1.114 — currently DHCP, changed once during this session (.113 → .114)
- **Vault schema**: `djinn/printer/{queue,active,completed,models,config}` active

---

*— Claude*
