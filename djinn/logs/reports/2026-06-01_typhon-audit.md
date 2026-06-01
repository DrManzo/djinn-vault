---
title: TASK-045 — Typhon Full System Audit
date: 2026-06-01
author: Claude
tags: [typhon, audit, maintenance, TASK-045]
status: complete
---

# TASK-045 — Typhon System Audit

**Executed:** 2026-06-01 ~01:10 UTC  
**SSH:** `tf-tthq@192.168.1.113` (ed25519 key)  
**IMPORTANT:** Typhon IP in CLAUDE.md (`192.168.50.113`) is wrong — correct IP is `192.168.1.113`

---

## Disk State

| Mount | Device | Size | Used | Free | Use% |
|-------|--------|------|------|------|------|
| `/` | nvme0n1p2 | 233G | 33G | 185G | 17% |
| `/mnt/storage` | sda1 | 916G | 319G | 552G | 37% |
| `/run/media/tf-tthq/Extreme SSD` | sdb1 | 1.9T | 275G | 1.6T | 15% |
| `/run/media/tf-tthq/The Library` | sdc1 | 4.6T | 334G | 4.3T | 8% |

**After log cleanup:** `/` went from 36G → 33G used (freed 3.8GB).

---

## What Was Cleaned

### Journal Vacuum (done this session)
- Freed **3.8GB** from `/var/log/journal` using `sudo journalctl --vacuum-size=200M`
- Root cause: vault-sync.service was failing every 2 minutes, flooding the journal

---

## Issues Found

### 🔴 TASK-044 Not Executed
**Extreme SSD (`/dev/sdb1`) is still mounted raw at `/run/media/tf-tthq/Extreme SSD`.**  
Typhon did not execute TASK-044 despite the COMMS.md directive. This is a manual execution task — needs Javier to trigger on Typhon directly or run djinn-queue-runner manually.

### 🔴 vault-sync Broken Bisync State (FIXED: timer stopped)
vault-sync.service was failing every 2 minutes with:
```
ERROR: Bisync critical error: cannot find prior Path1 or Path2 listings
ERROR: Bisync aborted. Must run --resync to recover.
```
**Action taken:** `systemctl --user stop vault-sync.timer && systemctl --user disable vault-sync.timer`

**Javier must run to recover:**
```bash
# 1. Run one-time resync to rebuild bisync state
ssh -i ~/.ssh/id_ed25519 tf-tthq@192.168.1.113 \
  "rclone bisync ~/Obsidian/ gdrive:Obsidian/ \
    --backup-dir gdrive:Obsidian_archive \
    --exclude 'RAW/**' \
    --exclude '.obsidian/workspace*' \
    --resync --verbose 2>&1"

# 2. Re-enable the timer
ssh -i ~/.ssh/id_ed25519 tf-tthq@192.168.1.113 \
  "systemctl --user enable --now vault-sync.timer"
```
*Note: `--resync` rebuilds bisync state database. Does NOT delete files. Safe to run.*

### 🟡 Snap Bloat
3.4GB in `/var/lib/snapd/snaps`. Desktop apps present: Discord, Firefox, 1Password, GNOME apps.  
If Typhon is running headless, several can be removed. **Low priority — machine has 185GB free.**

### 🟡 Syslog Still Bloated
- `/var/log/syslog.1`: 985MB
- `/var/log/syslog`: 221MB
- `/var/log/kern.log.1`: 206MB

These need sudo logrotate but `/var/log` had insecure permissions (world-writable) when attempted.  
Fix when convenient: `sudo chmod 755 /var/log && sudo logrotate -f /etc/logrotate.conf`

### 🟡 Stray Session File
`/home/tf-tthq/session-ses_1bb0.md` (136KB) — random file in home root. Can likely be deleted.

---

## Home Directory Breakdown (6.7GB total)

| Path | Size | Notes |
|------|------|-------|
| `~/printer-files/` | 1.6G | Rsync target from Salomon — expected |
| `~/snap/` | 888M | Snap user data |
| `~/typhons-studio/` | 499M | Unknown project — review needed |
| `~/djinn-bot-venv/` | 37M | Python venv for djinn bots |
| `~/typhons-studio-savepoint/` | 312K | Savepoint of above |
| `~/session-ses_1bb0.md` | 136K | Stray file — can delete |

---

## Ollama Models

No models found in `~/.ollama/models/`. The 53GB Ollama model footprint previously noted has been cleared (or never fully migrated to Typhon). **Build gate condition: Typhon audit complete — ✅ Ollama bloat resolved.**

---

## System Health

- **Memory:** 2.4GB/14GB used (healthy)
- **Uptime:** 4 days, 44 min
- **Failed services:** None (`systemctl --failed` clean)
- **Load average:** 0.69, 1.48, 1.63 (mild — likely from vault-sync failure loop)
- **Docker:** Not installed

---

## Build Gate Status

| Condition | Status |
|-----------|--------|
| Typhon audit complete | ✅ Done |
| Ollama bloat resolved | ✅ (no models present) |
| TASK-044 (Extreme SSD reformat) | ❌ Not executed |
| vault-sync recovery | ❌ Needs `--resync` by Javier |

**Interpretation:** TASK-045 audit is done. TASK-044 still needs execution. Build gate can proceed for Marcus research (PHASE-2) — it was gated on audit completion + model bloat, not on TASK-044 format. TASK-044 can proceed in parallel.

---

## Pending Actions (for Javier)

1. **Run vault-sync --resync** (see command above) then re-enable timer
2. **Trigger TASK-044** on Typhon — either SSH and run commands manually, or send via Typhon's terminal
3. **Review `~/typhons-studio/`** — 499MB, unknown project
4. **Optional syslog cleanup** — `sudo chmod 755 /var/log && sudo logrotate -f /etc/logrotate.conf`

---

— Claude
