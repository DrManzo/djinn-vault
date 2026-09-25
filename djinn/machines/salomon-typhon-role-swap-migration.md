---
title: Migration Plan — Salomon/Typhon Role Swap
tags: [djinn, machines, architecture, migration, in-progress]
created: 2026-09-07
status: sequenced
related: [[Salomon]] | [[TF-TTHQ]] | [[GATEWAY]]
---

# Salomon/Typhon Role Swap — Migration Plan

**Status: SEQUENCED, awaiting Phase 1 — no destructive action taken yet. Inventory and sequencing plan complete; next step is Javier's physical wipe of Typhon.**

## The decision (2026-09-07, Javier + Claude)

Typhon's Windows reprovisioning has been incomplete since the 2026-06-25 wipe — over two months of `djinn-penelope-usbip-watch.service` and `forge-printer-files-backup.service` permanently failing because Typhon is unreachable for what they need, `HEARTBEAT-typhon.md` frozen since 2026-06-23, onboarding flagged incomplete in vault docs the whole time. Rather than keep nursing that half-finished state:

- **Typhon** gets wiped clean and rebuilt as **Ubuntu 26.04.1 LTS Server** (headless), becoming the new command-center — takes over everything Salomon currently runs for Djinn automation.
- **Salomon** gets repurposed to **Windows**, to run the heavy AutoCAD/Adobe/3D professional software cluster (see `machines/Alexandria` context) that needs its stronger hardware (16-core Ryzen 9, 8GB RTX 5060, 29GB RAM vs Typhon's 6-core i5, 4GB GTX 1650, 16GB RAM).
- Alexandria (SanDisk Extreme SSD) stays physically attached to whichever machine ends up needing it most — likely new-Typhon, as an always-on drive.

**Physical constraint:** Claude has no remote-KVM/out-of-band access to either machine's BIOS/boot process. The actual OS wipe+install on Typhon requires Javier physically present with a USB boot drive. Claude's SSH access to Typhon dies the moment its current Windows install is wiped, and resumes once the new Ubuntu install is up and reachable.

## Progress so far

- [x] Ubuntu 26.04.1 Server ISO downloaded to `D:\iso\ubuntu-26.04.1-live-server-amd64.iso` on Typhon (2026-09-07). SHA256 verified: `cc8a95cde20f6ced61a322420de00f10cc3c90ced545daa46cb9c1a117f1d927` — matches `releases.ubuntu.com/26.04/SHA256SUMS` exactly.
- [x] Full inventory of what must migrate (below)
- [x] Safe migration sequencing plan + shop-downtime decision (below) — 2026-09-10
- [x] Javier: physically wiped Typhon, installed Ubuntu 26.04.1 Server — 2026-09-25
- [x] Bootstrap script run on new-Typhon (piecemeal, not via the script directly -- see Known Issues) — all runtime deps verified matching Salomon: pyenv 2.6.31 + Python 3.11.11, Node v22.22.3, Docker 29.8.1, rclone v1.60.1-DEV, openclaw@2026.5.22 (exact pin)
- [ ] Rebuild the actual djinn-*/forge-*/studio-* stack on new-Typhon (Phase 2 proper -- this was just runtime setup)

**New-Typhon connection details (2026-09-25):** LAN IP `192.168.1.113` (same as before the wipe -- DHCP reservation tied to the NIC's MAC address, 04:7c:16:2f:62:9a), username `drmanzo`. Salomon's SSH key is authorized -- passwordless `BatchMode=yes` access confirmed working. Not yet on Tailscale (fresh OS, never authenticated) -- LAN IP is the only path in for now, fine for same-network work, will need Tailscale re-auth before remote-from-elsewhere access matters.

**Known issues hit during bootstrap, both real bugs, not user error:**
1. The Ubuntu Server installer's own netplan config for `enp3s0` had no `dhcp4: true` at all -- interface came up, got IPv6 via kernel-level SLAAC automatically, but never requested an IPv4 lease. Explains ~30 min of "why can't we find it on the network" -- it had no IPv4 address to find. Fixed by adding `dhcp4: true` and re-applying.
2. `typhon-bootstrap.sh`'s Docker GPG key setup (`gpg --dearmor`) produced a binary keyring that this apt/gpg version rejected as "unsupported filetype." Diffed against Salomon's own *working* `/etc/apt/keyrings/docker.asc` and found it's actually still plain ASCII-armored text, never dearmored at all -- despite Docker's own install docs recommending the dearmor step. This apt version apparently accepts (or specifically wants) the armored form via `signed-by=`. Script needs fixing to skip dearmoring, or this needs re-verifying against whatever the "correct" modern behavior actually is before trusting it blanket for future installs.
3. Running `typhon-bootstrap.sh` directly over SSH failed entirely -- its internal `sudo` calls need a real TTY on this system's sudo policy, and a backgrounded SSH session can't allocate one. Worked around by running every sudo-requiring step individually with the password piped fresh each time (`echo PASSWORD | sudo -S ...`), rather than relying on a cached credential. Offered Javier the alternative of a NOPASSWD sudoers rule matching Salomon's own setup, but that specific action was blocked by the platform's own safety classifier when Claude tried it directly -- Javier would need to add that himself if wanted for future convenience.
- [ ] Decide + execute Salomon's Windows path (full wipe / dual-boot / VM)
- [ ] Move the Alexandria software cluster to its final home

**Note (2026-09-10):** As of this update, Typhon has been unreachable (Tailscale: offline, last seen ~1d ago, still tagged "windows") for about a day, for an unconfirmed reason — may or may not already be mid-wipe. Not assumed either way; confirm actual state before starting Phase 1 below.

**2026-09-10 side-fix, unrelated to sequencing but found while checking current state:** the checkpoint-gate auto-exempt built 2026-09-06 never covered `vault-sync:` commits, only `heartbeat:`/`review: weekly review`. Since vault-sync interleaves with heartbeat constantly, this caused 3 days of accumulated unpushed commits (83 total, all verified clean) and `heartbeat.service`/`djinn-gcode-sync.service` showing failed. Backlog pushed, gap fixed — Javier explicitly chose to auto-exempt `vault-sync:` too, with the tradeoff (its `git add -A` is broad, message alone doesn't prove content-safety the way it does for heartbeat/weekly) documented inline in the hook source.

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

## Sequencing plan (decided 2026-09-10)

### The core tension

Whichever machine gets wiped first, its current role goes dark, and the *other* machine can't immediately absorb it — different OS, different software already installed. There's no zero-downtime path between exactly two machines swapping roles; some gap is unavoidable. The two candidate gaps aren't equally costly:

- **Command-center gap** (heartbeat, gateways, checkpoint system, all Djinn automation) — already tolerating an informal version of this right now (Typhon's been offline a day with no ill effect beyond some failed timers). Low real-world cost.
- **Shop-machine gap** (Typhon's *current* Windows job: slicing, commissions, content pipeline) — customer/business-facing. Neither machine can cover this mid-transition: new-Typhon-as-Linux can't run Windows slicers, and Salomon isn't Windows yet.

**Decision: accept the shop-machine gap. Pause new commission intake for the duration.** This fixes the order: Typhon gets wiped and rebuilt as command center *first*; Salomon converts to Windows *after* new-Typhon is proven stable. Pausing commissions is Javier's own action (business-facing), not something Claude does.

### Phase 0 — Pre-flight (remote, before any physical step)

- [ ] Resolve remaining open questions below that affect what gets rebuilt (Ollama's new home, the penelope-usbip-watch/gcode-sync topology rework, the duplicate morning timer)
- [x] Bootstrap script written: `djinn/migration/scripts/typhon-bootstrap.sh` — pyenv 2.6.31 + Python 3.11.11, nvm v0.40.4 + Node v22.22.3, Docker CE (official repo, matching Salomon exactly, not Ubuntu's docker.io), rclone, openclaw pinned to @2026.5.22 (Salomon's actual running version, not latest @2026.9.3 — caught this discrepancy while writing it). All versions/methods checked live against Salomon, not assumed. Syntax-checked (`bash -n`), not yet run (Typhon doesn't exist as Linux yet). NOT installing Ollama — still an open decision.
- [ ] Confirm Typhon's actual current state (online/offline, wiped or not) before Javier starts Phase 1 — don't assume from a stale note
- [ ] Javier: pause new commission intake

### Phase 1 — Wipe Typhon, install Ubuntu Server (Javier physical + Claude remote once reachable)

- [ ] Javier: boot from the already-staged USB (built from `D:\iso\ubuntu-26.04.1-live-server-amd64.iso`), wipe, install Ubuntu 26.04.1 Server, enable SSH, get it back on Tailscale
- [ ] Claude: once reachable, verify base OS, run the Phase 0 bootstrap script

### Phase 2 — Rebuild the command-center stack on new-Typhon (Claude remote, Javier available for secrets/decisions)

- [x] **2026-09-25:** Re-surveyed live state directly (`systemctl --user list-unit-files`) rather than trusting this doc's 2026-09-07 inventory as current — real drift found. Live enabled set is 23 timers + 15 services = 38 units (doc's 27+18 estimate was close but not exact; several `djinn-*`/`forge-*`/`studio-*` naming-family duplicates exist on Salomon, disabled, and were correctly left behind, not migrated).
- [x] Transfer the 7 credential/secret files securely — done, byte-verified identical on both sides, `chmod 600` confirmed, `printer-bot.env` symlink recreated.
- [x] `~/.local/bin` synced (317 files) — excluded 4 desktop-only GUI tools nothing in the automation stack references (`OrcaSlicer.AppImage`, `altserver-linux`, `weylus`, `ldid`, ~220MB, not needed on a headless box).
- [x] Vault git checkout cloned fresh on new-Typhon via HTTPS (anonymous, read-only so far), `git pull --ff-only` verified working. **Push is not yet set up** — `gh auth` needs a token, and piping it host-to-host was correctly blocked by the platform's own safety classifier (looks like credential exfiltration even though it's Javier's own token between his own two machines). Javier needs to run one of these himself: `gh auth token | ssh drmanzo@192.168.1.113 "gh auth login --with-token"` (from Salomon), or `ssh drmanzo@192.168.1.113` then `gh auth login` interactively (device-code flow).
- [x] Recreated 21 of the 23 uncontested timers + all 15 always-on services (systemd unit files copied, `daemon-reload`'d, verified loading with no parse errors) — excluded `djinn-penelope-usbip-watch` and `djinn-gcode-sync` pending the topology-rework decision (unchanged open question, see below).
- [x] Updated hardcoded machine-identity strings: `heartbeat` script + unit (`Salomon (192.168.1.225)` → `Typhon (192.168.1.113)`), `comms-processor.service`'s `DJINN_AGENT=Salomon` → `DJINN_AGENT=Typhon`. Confirmed via source read that `comms-processor` is fully parameterized off this one env var — no code fork needed, no other script has an identity-specific branch.
- [x] Minimal Python deps installed on new-Typhon's pyenv 3.11.11, pinned to Salomon's exact versions: `flask==3.1.3`, `requests==2.34.2`, `discord.py==2.7.1`, `easypost==10.6.0`, `opencv-python-headless==4.13.0.92`. Deliberately did **not** blanket-copy Salomon's full ~140-package pip freeze — most of it (chromadb, playwright, selenium, faster-whisper, google-genai, trimesh, etc.) belongs to unrelated tools, not the migrating automation stack. Verified the real need by grepping actual `import`/`from` lines in every migrating script rather than assuming.
- [x] `~/virtual-printer` compose setup copied (compose files, config, scripts) — deliberately excluded `printer_data/logs` (230MB of regeneratable runtime logs) and `gcodes`/`database`/`certs` (fresh container state, not meant to travel).
- [x] **Bug found + fixed (both machines):** `djinn-virtual-printer.service` declared `Requires=docker.service`/`After=docker.service` — a *system*-level unit name, which a `systemd --user` manager can never resolve (separate namespace). This has silently never worked on **Salomon either** — not something the migration broke, a pre-existing latent bug only surfaced by actually trying to start it today. Fixed on both machines: dropped the cross-manager dependency lines, added an `ExecStartPre` docker-readiness poll instead. Full writeup: `logs/reports/2026-09-25_bug-djinn-virtual-printer-service-can-t-start-user-level-unit-referencing-system-level-docker-service-by-requires-after.md`.
- [x] **Second bug found (new-Typhon only):** the persistent `systemd --user` manager was spawned *before* the bootstrap script's `usermod -aG docker` ran, so it kept stale group membership — `docker` commands worked over a fresh SSH login but failed with permission-denied from inside a `systemd --user` unit. Fixed with one reboot (no disk encryption on this box, confirmed safe to do remotely, came back in ~30s). Logged in the same bug report as above.
- [x] **First real live-fire verification:** `djinn-virtual-printer.service` started successfully on new-Typhon after both fixes — `v3plus-virtual` container up, ports 7125/8110 bound, enabled for boot. This is the first migrated unit actually proven working end-to-end, not just "installed."
- [ ] **Deliberately NOT started yet — real collision risk, not an oversight:** `heartbeat`, `vault-sync`, `comms-processor`, `djinn-weekly`, `djinn-checkpoints-rotate`, `djinn-dm-cleanup` all write to the shared vault git repo (commit/push) or shared state — enabling their timers on new-Typhon *right now*, while Salomon's identical copies are still live, would cause real double-fires (duplicate/conflicting heartbeat commits, competing pushes, possible push races) — exactly what Phase 3 already warns about, just discovered to apply earlier than expected (Phase 2 verification, not just cutover). Similarly, `djinn-telegram-gateway` and `djinn-discord-gateway` both long-poll the *same bot tokens* — running both machines' copies simultaneously would cause Telegram/Discord API conflicts (409-style errors) or duplicate message delivery, not a clean A/B comparison. **Recommendation:** verify these either one at a time with Salomon's matching timer briefly paused, or hold all of them for the actual Phase 3 cutover window where Salomon's copy gets disabled first by design anyway.
- [ ] Migrate real data: `shop.db`, hellhound state — take a final snapshot of each on old-Salomon right before cutover so nothing written in the gap is lost. Not started — no urgency yet since old-Salomon is still the live system of record.
- [ ] `djinn-penelope-usbip-watch` / `djinn-gcode-sync` — still blocked on the same open topology question as before, unchanged this session.

### Phase 3 — Cutover

- [ ] Stop + disable (not delete yet) each service/timer on Salomon only once its new-Typhon counterpart has been verified actually firing correctly on its own
- [ ] Confirm nothing double-fires during the transition (e.g. both machines pushing heartbeats at once)
- [ ] New-Typhon becomes sole command center

### Phase 4 — Convert Salomon to Windows (Javier physical)

- [ ] Resolve task #12 (full wipe / dual-boot / VM) — still open, needs Javier's call
- [ ] Javier: physically execute whichever path is chosen
- [ ] Move the needed Alexandria software cluster (task #13, the 81GB AutoCAD/Adobe/course set) to new-Salomon

### Phase 5 — Resume shop operations

- [ ] Once new-Salomon has the needed software working, Javier resumes commission intake
- [ ] Decide Alexandria's final physical placement — likely stays attached to new-Typhon as "always on" per the original intent, separate from the software cluster itself (which should live on new-Salomon's own disk, not require Alexandria to stay plugged into whichever machine needs to run it)

### Phase 6 — Cleanup

- [ ] Once confident nothing needs rollback, remove the disabled-but-not-deleted Salomon-side command-center units from Phase 3
- [ ] Update this doc's status to "complete" and close out the open tasks

---

## Open questions still needing a decision (not yet resolved)

1. **`djinn-penelope-usbip-watch` and `djinn-gcode-sync`** — both currently exist specifically because *old* Typhon does Windows slicing and Penelope's USB needed sharing from it. Once Typhon is Linux and Salomon is Windows, the actual topology these scripts assume may be inverted or obsolete. Needs fresh thinking, not a blind migrate.
2. **Ollama / local LLM serving** — does new-Typhon keep this role, move to Salomon-as-Windows (awkward, Windows Ollama support exists but changes the automation model), or move somewhere else entirely (Orion already hosts larger models per existing fleet docs)?
3. **Confirmed duplicate, not just a naming coincidence:** `djinn-daily` fires `~/.local/bin/djinn-morning` at 08:00, and `djinn-morning` fires the *same script* again at 08:30 — the exact same morning-briefing script running twice, 30 minutes apart, every day. This should almost certainly be one timer, not two, on new-Typhon. Worth asking Javier whether this was ever deliberate (e.g., a retry-safety-net pattern) before dropping one, but it reads as accidental duplication.
4. **Alexandria's final resting place** — likely new-Typhon as "always on," per Javier's stated intent, but not yet physically decided/executed.
5. **Salomon's Windows path** — full wipe vs dual-boot vs VM-for-just-the-heavy-software. Affects whether any of Salomon's current Linux capabilities (games, Ollama, dev tools) survive in any form.

---

*— Claude, 2026-09-07, scoping phase, no destructive action taken*
