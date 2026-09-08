---
title: Migration Plan — Salomon/Typhon Role Swap
tags: [djinn, machines, architecture, migration, in-progress]
created: 2026-09-07
status: scoping
related: [[Salomon]] | [[TF-TTHQ]] | [[GATEWAY]]
---

# Salomon/Typhon Role Swap — Migration Plan

**Status: SCOPING — no destructive action taken yet. This document is the inventory phase.**

## The decision (2026-09-07, Javier + Claude)

Typhon's Windows reprovisioning has been incomplete since the 2026-06-25 wipe — over two months of `djinn-penelope-usbip-watch.service` and `forge-printer-files-backup.service` permanently failing because Typhon is unreachable for what they need, `HEARTBEAT-typhon.md` frozen since 2026-06-23, onboarding flagged incomplete in vault docs the whole time. Rather than keep nursing that half-finished state:

- **Typhon** gets wiped clean and rebuilt as **Ubuntu 26.04.1 LTS Server** (headless), becoming the new command-center — takes over everything Salomon currently runs for Djinn automation.
- **Salomon** gets repurposed to **Windows**, to run the heavy AutoCAD/Adobe/3D professional software cluster (see `machines/Alexandria` context) that needs its stronger hardware (16-core Ryzen 9, 8GB RTX 5060, 29GB RAM vs Typhon's 6-core i5, 4GB GTX 1650, 16GB RAM).
- Alexandria (SanDisk Extreme SSD) stays physically attached to whichever machine ends up needing it most — likely new-Typhon, as an always-on drive.

**Physical constraint:** Claude has no remote-KVM/out-of-band access to either machine's BIOS/boot process. The actual OS wipe+install on Typhon requires Javier physically present with a USB boot drive. Claude's SSH access to Typhon dies the moment its current Windows install is wiped, and resumes once the new Ubuntu install is up and reachable.

## Progress so far

- [x] Ubuntu 26.04.1 Server ISO downloaded to `D:\iso\ubuntu-26.04.1-live-server-amd64.iso` on Typhon (2026-09-07). SHA256 verified: `cc8a95cde20f6ced61a322420de00f10cc3c90ced545daa46cb9c1a117f1d927` — matches `releases.ubuntu.com/26.04/SHA256SUMS` exactly.
- [ ] Full inventory of what must migrate (this document, in progress)
- [ ] Safe migration sequencing plan
- [ ] Javier: physically wipe Typhon, install Ubuntu Server
- [ ] Rebuild the stack on new-Typhon
- [ ] Decide + execute Salomon's Windows path (full wipe / dual-boot / VM)
- [ ] Move the Alexandria software cluster to its final home

---

## Full inventory: Salomon's current command-center stack

### Timers (27 total; excluding pure-Ubuntu-system ones: `snap.firmware-updater`, `launchpadlib-cache-clean`, `ubuntu-insights-upload`, `ubuntu-insights-collect` — those are OS-level, not Djinn, and will exist natively on any fresh Ubuntu install)

| Timer | Script | Notes |
|---|---|---|
| `comms-processor` | `~/.local/bin/comms-processor` | `DJINN_AGENT=Salomon` env — **must become `DJINN_AGENT=Typhon` on migration** |
| `djinn-iris-address-watch` | `~/.local/bin/djinn-iris-address-watch` | |
| `forge-print-complete-watcher` | `~/.local/bin/djinn-print-complete-watcher` | |
| `forge-print-monitor-v2` | `~/.local/bin/djinn-print-monitor-v2` | |
| `djinn-penelope-usbip-watch` | `~/.local/bin/djinn-penelope-usbip-watch` | Currently fails — was trying to reach *old* Typhon for Penelope's USB. Logic needs review once roles flip: Penelope is USB-attached to Salomon per SYSTEM-STATE.md, so this whole unit's *purpose* (share Penelope's USB FROM Typhon) may not even make sense anymore post-swap — flag for a real decision, not a blind migrate. |
| `gdrive-sync` | `~/.local/bin/gdrive-sync` + `~/.local/bin/gdrive-backup-manifest` | Fixed today (rate-limit + resync). Depends on `~/.config/rclone/rclone.conf` |
| `djinn-gcode-sync` | `~/.local/bin/djinn-gcode-sync` | Pulls sliced gcode FROM Typhon today — direction flips or becomes irrelevant post-swap since Typhon won't be doing Windows slicing anymore |
| `forge-sync` | `~/.local/bin/forge-sync` | |
| `heartbeat` | `~/.local/bin/heartbeat` | Fixed today (scoped `git add`). Writes `HEARTBEAT.md`, hardcodes "Salomon" in output — **needs machine-name update** |
| `forge-printer-log-sync` | `~/.local/bin/djinn-printer-log-sync` | |
| `studio-trend-agent` | `~/.local/bin/djinn-trend-agent` | |
| `djinn-bughunter` | `~/.local/bin/djinn-bughunter` | |
| `djinn-dm-cleanup` | inline python importing `forge/shop/customer_dm.py` | Fixed today (path). Needs `requests` in whatever Python migrates with it |
| `comms-compact` | `~/.local/bin/djinn-comms-compact` | |
| `djinn-daily` | `~/.local/bin/djinn-morning` | |
| `djinn-morning` | `~/.local/bin/djinn-morning` | (same script as djinn-daily — check if intentional dup or one is stale) |
| `djinn-budget-paycheck` | `~/.local/bin/djinn-budget-alert paycheck` | |
| `djinn-checkpoints-rotate` | `~/.local/bin/djinn-comms-rotate` via bash -c | Fixed today (date specifier bug) |
| `studio-hashtag-research` | `~/.local/bin/djinn-hashtag-update --research` | |
| `djinn-weekly` | `~/.local/bin/djinn-weekly` | Verified working today (checkpoint-gate fix held under real conditions) |
| `forge-printer-files-backup` | `~/.local/bin/djinn-printer-files-backup` | Fixed today (env var names). Currently backs up TO Typhon — direction flips or becomes irrelevant post-swap |
| `djinn-budget-weekly` | `~/.local/bin/djinn-budget-alert weekly` | |
| `vault-sync` | `~/.local/bin/vault-sync` | Rate-limit fix applied today, not yet fully verified end-to-end (see today's earlier report) |

### Always-on services (18, excluding desktop-session plumbing — see "Does NOT migrate" below)

| Service | Script | Notes |
|---|---|---|
| `djinn-clerk` | `~/.local/bin/djinn-clerk-watch` | Watches RAW/, sensitivity-filters into personal/ or public paths |
| `djinn-ctx-router` | `~/.local/bin/djinn-ctx-router` | |
| `djinn-discord-gateway` | `~/.local/bin/djinn-discord-gateway` | `EnvironmentFile=~/.djinn.env` — needs the real secret |
| `djinn-hound` | `~/.local/bin/djinn-hound` | |
| `djinn-inbox` | `~/.local/bin/djinn-flask-inbox` | Port 8765 |
| `djinn-personal-gateway` | `~/.local/bin/djinn-personal-gateway` | |
| `djinn-print-track` | `~/.local/bin/djinn-print-track start` | |
| `djinn-shop-dashboard` | `~/.pyenv/shims/python3 ~/Obsidian/forge/shop/dashboard/app.py` | Port 8420. **3 env files**: `~/.config/forge/shop.env`, `~/.config/forge/easypost.env`, `~/.config/djinn/printers.env`. Real business DB at `~/.local/share/djinn-shop/shop.db` (135KB, live orders/customers/inventory) — this is real data, not just config, needs an actual data migration not just a code copy |
| `djinn-telegram-gateway` | `~/.local/bin/djinn-telegram-gateway` | `EnvironmentFile=~/.djinn.env` |
| `djinn-virtual-printer` | `docker compose up -d` | **Needs Docker installed on new-Typhon** + the compose file (`~/virtual-printer/docker-compose.yml`) + its images (see Docker section below) |
| `forge-webcam-monitor` | `~/.local/bin/djinn-webcam-monitor` | |
| `hellhound` | `~/.pyenv/versions/3.11.11/bin/python3 ~/.local/share/hellhound/hellhound.py` | Security monitoring — has its own data dir at `~/.local/share/hellhound/` that needs to move, not just the script |
| `inbox-watcher` | `~/.local/bin/inbox-watcher` | |
| `openclaw-gateway` | Node v22.22.3 via nvm, `openclaw` npm package | Port 18789. Has its own `OPENCLAW_WINDOWS_TASK_NAME` env — suggests openclaw itself has some cross-platform awareness already, worth checking its docs |
| `printer-error-logger` | `~/.local/bin/printer-error-logger` | |
| `studio-media-drop` | `~/.local/bin/djinn-media-drop` | |

### Does NOT migrate — tied to Salomon being an interactive Linux desktop, not headless automation

| Service | Why it can't move to headless Ubuntu Server |
|---|---|
| `voxtype` | Voice-to-text daemon — requires `DISPLAY=:0` / `WAYLAND_DISPLAY` (an active GUI session). No display on a headless server. This capability is lost in the swap unless replaced some other way — flag to Javier, don't silently drop it without him knowing. |
| `filter-chain` | PipeWire audio filter chain — desktop audio infrastructure, meaningless without a desktop session. |

(Standard desktop-session plumbing not listed as its own inventory row either, for the same reason: `gnome-keyring-daemon`, `pipewire`/`pipewire-pulse`/`wireplumber`, `spice-vdagent`, `mpris-proxy`, `obex`, `xdg-desktop-portal-*`, `IBus`, `gcr-ssh-agent`, `ydotool` — all GUI-session infrastructure that a headless server doesn't need at all.)

---

## Cross-cutting dependencies

### Secrets / credential files that must transfer securely (not committed to git, per [[feedback-secrets]])
- `~/.djinn.env` — shared master secrets (Discord + Telegram gateway tokens, per today's `djinn-gateway` source reading)
- `~/.config/forge/shop.env`
- `~/.config/forge/easypost.env`
- `~/.config/djinn/printers.env`
- `~/.config/djinn/telegram.conf`
- `~/.config/forge/printer-bot.env` (symlinked from `~/.config/djinn/printer-bot.env`)
- `~/.config/rclone/rclone.conf` (GDrive OAuth token)

### Real data (not just config/code) that must migrate
- `~/.local/share/djinn-shop/shop.db` — live business database (orders, customers, inventory, ledger)
- `~/.local/share/hellhound/` — security monitoring data/state
- `~/Obsidian` itself — the vault git checkout (though this is trivially re-clonable from GitHub; the concern is any *uncommitted* local state at migration time)

### Runtime dependencies to install fresh on new-Typhon
- pyenv + Python 3.11.11 (used directly by `hellhound`, via shims by `djinn-shop-dashboard`/`djinn-dm-cleanup`)
- Node v22.22.3 via nvm (for `openclaw-gateway`)
- Docker (for `djinn-virtual-printer` — compose file at `~/virtual-printer/docker-compose.yml`, images: `dadoum/anisette-v3-server`, `djinn-core-djinn`, `forge-slicer`, `ghcr.io/mainsail-crew/virtual-klipper-printer`)
- Ollama (for the 7 local models Salomon currently serves — only relevant if new-Typhon is meant to keep serving local LLM inference; needs a decision, since Typhon's weaker GPU may not be the right host for this either)
- rclone

### Machine-identity strings that need updating, not just copy-pasted
Several scripts hardcode "Salomon" in their output/logic (`heartbeat`'s `**Machine:** Salomon (192.168.1.225)` line, `comms-processor`'s `DJINN_AGENT=Salomon` env, likely others not yet audited) — these need actual updates to reflect the new machine identity, not a blind file copy.

---

## Open questions still needing a decision (not yet resolved)

1. **`djinn-penelope-usbip-watch` and `djinn-gcode-sync`** — both currently exist specifically because *old* Typhon does Windows slicing and Penelope's USB needed sharing from it. Once Typhon is Linux and Salomon is Windows, the actual topology these scripts assume may be inverted or obsolete. Needs fresh thinking, not a blind migrate.
2. **Ollama / local LLM serving** — does new-Typhon keep this role, move to Salomon-as-Windows (awkward, Windows Ollama support exists but changes the automation model), or move somewhere else entirely (Orion already hosts larger models per existing fleet docs)?
3. **Confirmed duplicate, not just a naming coincidence:** `djinn-daily` fires `~/.local/bin/djinn-morning` at 08:00, and `djinn-morning` fires the *same script* again at 08:30 — the exact same morning-briefing script running twice, 30 minutes apart, every day. This should almost certainly be one timer, not two, on new-Typhon. Worth asking Javier whether this was ever deliberate (e.g., a retry-safety-net pattern) before dropping one, but it reads as accidental duplication.
4. **Alexandria's final resting place** — likely new-Typhon as "always on," per Javier's stated intent, but not yet physically decided/executed.
5. **Salomon's Windows path** — full wipe vs dual-boot vs VM-for-just-the-heavy-software. Affects whether any of Salomon's current Linux capabilities (games, Ollama, dev tools) survive in any form.

---

*— Claude, 2026-09-07, scoping phase, no destructive action taken*
