---
title: Machine — TF/TTHQ (Typhon)
tags: [djinn, machine, typhon, hardware, models]
created: 2026-05-22
updated: 2026-07-01
---

# Machine: TF/TTHQ — Typhon

**Callsign:** TF/TTHQ
**Network name:** Typhon (Windows hostname confirmed `Typhon` as of 2026-07-01)
**Role:** **Changed 2026-06-25** — dedicated shop machine (slicing, commissions, content, accounting). No longer storage/sync.
**OS:** Windows 11 Home
**IP:** LAN `192.168.1.113` (still shows `filtered` on all ports — Windows Firewall blocks unsolicited LAN); reachable **over Tailscale at `100.69.41.74`**, hostname `typhon` on tailnet
**Windows account:** `typhon` (renamed from typo'd `typho` 2026-07-01; profile folder is still physically `C:\Users\typho` — Windows doesn't rename that, harmless)
**SSH:** ✅ **Working** as of 2026-07-01, over Tailscale only (`ssh typhon@100.69.41.74`) — key-based via `administrators_authorized_keys`, delivered by USB (LAN port 22 still filtered)
**Claude Code:** ✅ **Live and authenticated** as of 2026-07-01 — Claude Desktop app installed, bundled CLI at
  `C:\Users\typho\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude-code\2.1.187\claude.exe`.
  Not on PATH. Credentials transferred from Salomon's `~/.claude/.credentials.json` (same Pro account) since the
  in-app login didn't carry over to non-interactive SSH sessions (DPAPI/credential-manager scoping). Verified with
  `claude -p "..."` over SSH — responds correctly.
**Related:** [[SYSTEM-STATE]] | [[ROUTING]] | [[HEARTBEAT-typhon]] | `djinn/workspaces/typhon-windows/setup-typhon.ps1`

Changes from this machine are signed: `— TF/TTHQ`

---

## ⚠️ Status: Native-Windows Onboarding Mostly Done — WSL2/Djinn-Stack Services Still Pending

This machine was reinstalled from Ubuntu to **Windows** around 2026-06-25 and repurposed
as Typhon's Forge shop machine. Everything below the "Old Ubuntu Setup" divider describes
the **old Ubuntu setup** and is kept for reference only — it does not reflect current reality.

**Decision made 2026-07-01:** rather than routing everything through WSL2 (per the original
`setup-typhon.ps1` plan), onboarding proceeded natively on Windows — Claude Code, git, and
all pipeline tools now run directly on Windows, driven remotely over SSH/Tailscale from
Salomon. WSL2 was never installed; this sidesteps the "needs a reboot the SSH session can't
survive" problem entirely for everything except Ollama's background service (see below).

**Confirmed working as of 2026-07-01:**
- **Network:** LAN (`192.168.1.113`) still shows every port `filtered` — Windows Firewall
  blocks unsolicited inbound despite `setup-typhon.ps1`'s firewall rules having been applied
  manually (see below). **Tailscale is the only working path**: `typhon` at `100.69.41.74`,
  pings and SSHes cleanly from Salomon.
- **SSH:** working over Tailscale, key-based via `administrators_authorized_keys` (pubkey
  delivered by physical USB drive, since no network path existed yet at the time).
- **Windows account:** renamed `typho` (typo) → `typhon`. Profile folder is still physically
  `C:\Users\typho` — Windows doesn't rename that, harmless.
- **Claude Code:** live and authenticated, from the Claude Desktop app's bundled CLI at
  `C:\Users\typho\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude-code\2.1.187\claude.exe`
  (not on PATH). Credentials transferred from Salomon's `~/.claude/.credentials.json` (same
  Pro account) since the in-app interactive login didn't carry over to non-interactive SSH
  sessions (DPAPI/credential-manager scoping). The interactive first-run wizard (theme +
  login-method picker) could not be scripted over SSH — it also triggered a fresh browser
  OAuth flow that failed non-interactively — so the credential-file-copy approach was used
  instead of the wizard. **`claude --bg` (background agent mode) still needs one interactive
  disclaimer acceptance** — attempted via `settings.json` (`dangerouslySkipPermissions: true`,
  copied from Salomon's) but that alone wasn't sufficient; needs a human at the machine once.
- **Git:** installed (winget), configured with a GitHub PAT (same token as Salomon's `gh auth
  token`) embedded directly in clone URLs — the default Git Credential Manager (`manager`,
  set at system config level) fails non-interactively over SSH even after resetting the
  global helper to `store`; embedding the token in the URL sidestepped it entirely.
- **Vault + repos cloned:** `C:\Users\typho\Obsidian` (djinn-vault), `C:\Users\typho\forge`
  (typhons-cyber-forge), `C:\Users\typho\Documents\Project-Resources`.
- **`C:\Forge\*` directory structure** built (queue, models, gcode/{penelope,calliope},
  completed, content/{photos,videos,reels}, accounting, shop, tools).
- **Firewall rules** opened for 22/8080/4455/8554/8889/6379/11434 (still doesn't explain the
  LAN `filtered` result on port 22 specifically — SSH only works over Tailscale, LAN access
  is unexplained and untested further).
- **Power settings** applied (no sleep/hibernate on AC).
- **Software installed via winget:** Git, Ollama, Obsidian, Python 3.12, OBS Studio,
  Notepad++, JetBrains Mono Nerd Font, 7-Zip, Rustup, Microsoft 365 Apps (Office), Blender
  5.1.2, Creality Print 7.1.1, FFmpeg 8.1.1, rclone, Discord, **1Password** (installed
  successfully after a reboot — confirmed the earlier `0x80070534` SID mapping failures were
  caused by the account rename, cleared once the machine rebooted). Windows Terminal was
  already present.
- **Debloat + reboot completed 2026-07-01:** ran the `setup-typhon.ps1` debloat section
  (Bing/Xbox/Solitaire/Zune/etc apps removed, Cortana/telemetry/OneDrive-autostart/Game DVR
  disabled, non-djinn startup entries cleaned) via a script file over SSH — the original
  script's own `Remove-AppxPackage -Package $pkg.PackageFullName` line has a pre-existing bug
  where it fails on packages with multiple installed instances (array-to-string binding
  error); a handful of packages hit this and may not have actually been removed despite the
  script printing "Removed". Rebooted afterward (`shutdown /r`) — came back cleanly, `sshd`/
  `Tailscale` auto-started as configured, hostname/account survived intact.
- **OrcaSlicer:** the pinned URL in `setup-typhon.ps1` (v2.3.0) 404'd — upstream moved orgs
  (`SoftFever/OrcaSlicer` → `OrcaSlicer/OrcaSlicer`) and versioned up to v2.4.1. Running the
  installer via `Start-Process -Wait` over SSH hung indefinitely (GUI installer stuck in a
  non-interactive Session 0 — same class of problem as the Claude Code wizard). Fixed by
  downloading the installer and extracting it directly with 7-Zip (`7z x`) instead of running
  it — NSIS installers unpack cleanly this way. Binary now at `C:\Forge\tools\OrcaSlicer\orca-slicer.exe`.
- **OpenCode:** not on winget/no Windows install script path (the official installer is a
  bash script assuming WSL/Unix) — downloaded the release zip directly
  (`anomalyco/opencode`, `opencode-windows-x64.zip`, v1.17.13) and extracted to
  `C:\Users\typho\.opencode\bin\opencode.exe`. Config written at
  `C:\Users\typho\.opencode\opencode.json`, mirroring Salomon's local+remote Ollama provider
  pattern — but **no models have been pulled yet**, and see below re: Ollama itself.
- **Ollama:** binary installed, but **the background server does not survive a non-interactive
  launch** — `ollama.exe serve` started via SSH crashes within ~3 seconds
  (`app.log`: "Failed to start: Unable to init instance: Unspecified error"), same Session-0
  class of issue as the GUI installers. Needs to be started once from an interactive/RDP
  session; after that it may register properly and survive future headless restarts.

**What's still actually blocking full parity with the original plan:**
- WSL2 was deliberately skipped — if it's wanted later for `bootstrap-node.sh`-style parity
  with old Typhon (systemd timers, native Linux tooling), that decision needs revisiting.
  `djinn/scripts/bootstrap-node.sh` (referenced in the original ps1 post-reboot instructions)
  still does not exist anywhere in the vault or git history — moot unless WSL2 gets installed.
- No heartbeat since 2026-06-23 13:40 UTC — nothing has replaced the old Linux timer; would
  need a Windows Task Scheduler job or an OpenCode/Claude Code cron-equivalent.
- No comms-processor equivalent — Typhon does not currently poll COMMS.md/QUEUE.md for tasks.
- `Z:` drive mapping to `\\192.168.1.176\storage` (Oroborus/Library) not attempted — that IP
  wasn't confirmed live on the LAN during this session's scans.
- Ollama server and OpenCode's local models not yet actually running — **confirmed post-reboot
  that this is tied to the SSH session type itself (Session 0), not any persistent OS state**:
  same crash (`Unable to init instance: Unspecified error`) recurred immediately after reboot
  when launched over SSH again. A reboot alone will not fix this — needs an actual interactive
  session.
- `claude --bg` disclaimer not accepted — same, needs one interactive session.

**Next physical/interactive session at the machine should:**
1. Run `claude --dangerously-skip-permissions` once interactively, click through, confirm the
   disclaimer — unlocks `claude --bg` for future headless automation.
2. Start `ollama serve` once interactively (or check if it needs a full GUI login rather than
   RDP — Session 0 vs Session 1 distinction may matter) — then `ollama pull` the model set
   from the old TF-TTHQ Ollama Models table below.
3. Decide whether WSL2 is still wanted for this machine's role, or whether native-Windows is
   the permanent path going forward.

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
