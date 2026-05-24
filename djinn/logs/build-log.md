---
subject: Djinn Operations
tags: [djinn, build-log]
created: 2026-05-19
---

# Build Log

## 2026-05-19: MVP Build Day 1
- OpenCode configured with Ollama local provider
- Vault backed up, git initialized, pushed to GitHub
- vault-sync systemd timer created (15-min GDrive sync)
- vault-passport-backup script created
- Inbox processed (9 notes moved to proper locations)
- djinn/ directories populated with operational notes
- 504 note vault now backed up to GitHub + local tarball

## 2026-05-21: MVP Phase 5 Complete — Claude Lane + Hardware Protection
- Salomon: routing config applied (opencode.json temperatures), resource caps active (60% CPU / 20G RAM)
- Salomon: djinn-idle.timer wired — evicts deepseek, phi4, coder at 22:00 nightly
- Salomon: cpu-governor.service active, powersave enforced on boot
- Salomon: AGENTS.md routing corrected, Claude.md identity doc created
- Salomon: openclaw workspace versioned (initial commit, 13 files)
- Typhon: setup script ready (`djinn/scripts/typhon-claude-setup.sh`), pending Typhon coming online
- Claude lane: active on Salomon, Claude.md created, 9-file context protocol established
- Both machines communicating through vault (vault-sync + HEARTBEAT.md)
- Phase 6 (Agents & Skills) ready to begin when Typhon is confirmed

## 2026-05-22: Phase 9 — Printer Node (Ender-3 V3 Plus) — In Progress

- Klipper + Moonraker: already live on Nebula pad (`192.168.1.114:7125`) — no Typhon install needed
- `plr.cfg` uploaded to printer: Power Loss Recovery + thermal watchdog (5s poll, saves Z+layer, pauses on temp drop)
- `printer-error-logger.service` active on Salomon: polls Moonraker every 30s, logs errors + monitor rows to vault
- Printer vault structure live: `djinn/printer/{queue,active,completed,models,config}`
- Print baseline captured: Rose_Decor_fixed.gcode — hotend ±0.32°C, bed ±0.01°C, no anomalies
- idle_timeout: updated to 600s on Nebula pad (was 99999999), cat safety active
- OrcaSlicer: installed (AppImage), Ender-3 V3 Plus profile configured
- FreeCAD + Blender + OpenSCAD: installing (P9-JOB 2)
- Telegram bot: instructions written to COMMS.md for Typhon (P9-JOB 5)
- Hunyuan3D-2: pending pyenv Python 3.11 install (P9-JOB 3)

---

*— Claude*

## 2026-05-24: Manufacturing Orchestrator + Coin + FairPrintAgent

**Typhon's Forge Challenge Coin (2026-05-23)**
- 38mm × 4.5mm challenge coin designed from PNG logo
- Pipeline: PNG → PBM (ImageMagick) → SVG (potrace) → OpenSCAD parts → trimesh merge
- Final: LOGO_SCALE=0.0448 (20% reduction to stop corner text clipping), text size=3.8
- Key discoveries: OpenSCAD CGAL union() silently fails on 1M-face meshes; SVG center must be measured from rendered STL not SVG header
- Build report: `djinn/printer/library/typhons-forge-coin/COIN_BUILD_REPORT.md`

**FairPrintAgent / djinn-print-quote (2026-05-23)**
- Commission pricing CLI: `(material + time + design) / 0.60`
- Library auto-detect: design cost → $0 if piece name matches library folder
- Market fetch: ddgs DuckDuckGo/Etsy search
- Full agent mode: weighted cost+market blend, 4 job types
- OpenClaw: `quote`, `quick quote` command handlers added

**Print Job #1 — mario pipe + 4 coins (2026-05-24)**
- Combined plate: proxy_parts_mario_pipe + 4× Typhon's Forge coins
- PrusaSlicer silently dropped pipe when combined STL exceeded ~200MB
- Fix: decimate coins to 15k faces with pymeshlab → plate = 3.3MB → sliced correctly
- 3h 20m / 59.8g — started 2026-05-24

**Six-Agent Manufacturing Orchestrator (2026-05-24)**
- Package: `djinn/printer/agent/orchestrator/`
- Agents: DesignGenAgent, DesignEditAgent, ProtoOptAgent, DOEPrintOptAgent, PlateNestAgent (all live)
- CLI: `djinn-design` at `~/.local/bin/djinn-design`
- Venv: `~/.venvs/djinn-orchestrator/` (Python 3.11 — anthropic, pyDOE2, trimesh, pymeshlab, scipy)
- DOE engine verified: -76% time / -51% material for prototype_fast vs standard settings
- OpenClaw: `design`, `design edit`, `design optimize`, `design doe`, `design plate`, `design status` handlers

*— Claude*
