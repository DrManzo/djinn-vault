---
title: "TASK-068 — Djinn Automation Sprint: 9 Scripts, 3 Batches"
tags: [djinn, research, marcus, automation, scripts, monitoring, security, hardening]
created: 2026-06-06
author: Marcus (Perplexity)
status: ready-for-implementation
priority: p0-p1-p2
---

# TASK-068 — Djinn Automation Sprint

**Requested by:** Javier (DrManzo)  
**Spec written by:** Marcus (Perplexity AI)  
**Date:** 2026-06-06 (revised 2026-06-06)  
**Implementing agents:** Salomon (shell/deploy), Claude (architecture review on Batch C schema)  
**Source state:** INFRASTRUCTURE.md (rev. 2026-06-06), PROTOCOL.md (rev. 2026-06-05), SYSTEM-STATE.md, TASK-067 gap analysis

---

## Corrections vs. initial draft

- **Typhon IP corrected:** INFRASTRUCTURE.md lists `192.168.1.113` but PROTOCOL.md (authoritative) has `ssh -i ~/.ssh/id_ed25519 tf-tthq@192.168.1.150`. All SSH checks in this spec use `.150`. INFRASTRUCTURE.md needs updating separately.
- **rclone remote path:** remote name is `gdrive:` (bare). Full destination paths use `gdrive:djinn-vault`, `gdrive:typhons-cyber-forge`, etc. The rclone check command in backup-verifier uses the path form, not the remote name alone.
- **Backup test file:** changed from `INFRASTRUCTURE.md` (frequently edited) to `djinn/communications/PROTOCOL.md` (reference material, rarely touched, stable canonical file).
- **Warmkeeper hours:** phi4:14b and llama3.2-vision:11b warming restricted to 09:00–22:00 via in-script hour check, not a second systemd unit.
- **Comms validator:** COMMS entry format pasted from PROTOCOL.md directly. Marcus must validate against this exact spec, not his own interpretation.

---

## Context

50–65% of current LLM calls are going to problems that don’t need intelligence. This sprint replaces those calls with deterministic scripts. Nine scripts, three batches. Batches are not phases — they imply grouping by type, not calendar dependency. Salomon can run them in sequence or parallel based on bandwidth.

**Not in scope for this sprint:** Category 8 items (social media aggregation, weather/finance data). These are feature additions, not infrastructure. Cut entirely.

**Held for Claude before Marcus implements:** `djinn-agent-audit-log` schema. The schema is an architectural decision about how inter-agent communication evolves. Design it here first, then Marcus implements from spec. Section 3.3 contains the design.

---

## Batch A — Safety Net (Non-Negotiable, Build First)

> These three scripts exist because backup failure and silent health degradation are the only failure modes that cost real, unrecoverable work. Everything else is annoying. These are existential.

---

### djinn-backup-verifier

**Path:** `~/.local/bin/djinn-backup-verifier`  
**Language:** Bash  
**Timer:** Systemd timer, daily at 03:00 (off-hours)  
**AI required:** None  

**Input:**  
- No required args  
- Optional: `--target [vault|openclaw|forge|all]` (default: all)  
- Optional: `--report-only` (print report, exit 0 regardless of result)

**Output:**  
- Exit 0: all verifications passed  
- Exit 1: one or more failures  
- Human-readable report to stdout  
- Structured log appended to `~/Obsidian/djinn/logs/backup-verify-YYYY-MM-DD.md`  
- On failure: Telegram alert via `djinn-telegram-gateway` alert channel  

**Checks to perform:**

```
1. VAULT (GitHub + GDrive)
   a. git -C ~/Obsidian remote show origin — verify remote is reachable
   b. git -C ~/Obsidian log --oneline -1 — capture last commit hash
   c. rclone check ~/Obsidian/ gdrive:djinn-vault --one-way --max-delete 0
      → capture count of differences; >0 triggers WARNING (not failure, could be in-flight)
   d. Dry-restore test on a known stable file:
      Test file: djinn/communications/PROTOCOL.md
      (Stable reference doc, rarely touched, good canonical check)
      → sha256sum ~/Obsidian/djinn/communications/PROTOCOL.md > /tmp/verify-local.hash
      → rclone cat "gdrive:djinn-vault/djinn/communications/PROTOCOL.md" | sha256sum > /tmp/verify-remote.hash
      → diff /tmp/verify-local.hash /tmp/verify-remote.hash — FAIL if mismatch

   NOTE on rclone remote: remote name is `gdrive:` (bare remote name).
   Full destination paths are gdrive:djinn-vault, gdrive:typhons-cyber-forge, etc.
   Confirm actual remote name with `rclone listremotes` before first run.

2. OPENCLAW (Project-Resources repo)
   a. Check ~/Documents/Project-Resources/openclaw/ exists and is non-empty
   b. Verify git -C ~/Documents/Project-Resources status shows openclaw/ tracked
   c. Check last commit date on openclaw/ — WARN if >48 hours old
   d. Verify SOUL.md, IDENTITY.md, USER.md, AGENTS.md all present in openclaw/workspace/

3. FORGE (GDrive)
   a. rclone check ~/forge/ gdrive:typhons-cyber-forge --one-way --max-delete 0
   b. Capture last rclone log timestamp from systemd journal
   c. WARN if last successful sync >20 minutes ago

4. PRINT CONFIGS (vault-backed)
   a. Verify ~/Obsidian/djinn/printer/backup/ directory exists and contains .cfg files
   b. Check modification time of newest .cfg — WARN if >7 days
```

**Report format (append to log file):**
```markdown
## Backup Verification — YYYY-MM-DD HH:MM

| Target | Status | Detail |
|--------|--------|--------|
| vault/github | ✅ PASS | Last commit: abc1234, 2h ago |
| vault/gdrive | ⚠️ WARN | 3 files differ (in-flight sync likely) |
| openclaw | ✅ PASS | All 4 identity files present, last backup 6h ago |
| forge/gdrive | ✅ PASS | Last sync 4 min ago |
| print-configs | ✅ PASS | 3 .cfg files, newest 2d ago |

Overall: PASS (1 warning)
```

**Systemd unit (`djinn-backup-verifier.service`):**
```ini
[Unit]
Description=Djinn Backup Verification
After=network-online.target

[Service]
Type=oneshot
User=drmanzo
ExecStart=/home/drmanzo/.local/bin/djinn-backup-verifier
StandardOutput=journal
StandardError=journal
```

**Systemd timer (`djinn-backup-verifier.timer`):**
```ini
[Unit]
Description=Daily backup verification at 03:00

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

**Integration:** Called independently. Also callable manually: `djinn-backup-verifier --report-only` for status check during sessions.

---

### djinn-system-health

**Path:** `~/.local/bin/djinn-system-health`  
**Language:** Bash  
**Timer:** On-demand + called by `djinn-agent-doctor` (replace its current checks 1–11)  
**AI required:** None  

**Input:**  
- No required args  
- `--json` flag: output structured JSON to `~/.cache/djinn/health-YYYY-MM-DDTHH:MM.json` in addition to stdout  
- `--quiet` flag: suppress stdout, exit code only (for scripted use)  
- `--machine [salomon|typhon|orin|all]` flag: scope checks to one machine (default: all)  

**Output:**  
- Exit 0: all checks pass  
- Exit 1: one or more FAIL  
- Exit 2: one or more WARN (no FAIL)  
- Colored stdout report (green/yellow/red via ANSI codes)  
- JSON file if `--json` passed  

**Checks — Salomon (run locally):**

```
SERVICES (systemctl is-active for each):
  - djinn-ctx-router.service
  - djinn-telegram-gateway.service
  - djinn-discord-gateway.service
  - djinn-discord-watch.service
  - djinn-discord-watcher.service
  - djinn-print-monitor.service
  - printer-error-logger.service
  - voxtype.service
  - ollama.service

TIMERS (systemctl is-active for each .timer unit):
  - djinn-ctx-router.timer (5-min)
  - djinn-heartbeat.timer (5-min)
  - djinn-daily.timer
  - djinn-weekly.timer
  - djinn-clerk.timer (1-hr)
  - djinn-backup-verifier.timer  [add after this sprint]
  - djinn-model-warmkeeper.timer  [add after this sprint]
  - djinn-log-rotator.timer  [add after this sprint]

OLLAMA — Salomon:
  - curl -sf http://localhost:11434/api/tags — FAIL if no response
  - Parse JSON response; check all 7 expected models present:
    qwen2.5:7b, deepseek-r1:7b, phi4:14b, llama3.2-vision:11b,
    qwen2.5-coder:7b, nomic-embed-text, mistral:7b
  - WARN for any missing model

DISK THRESHOLDS (df -h, check use%):
  - ~/Obsidian/ (vault): WARN >70%, FAIL >85%
  - ~/.ollama/models/ (model storage): WARN >80%, FAIL >90%
  - ~/Obsidian/djinn/logs/ (logs): WARN >70%, FAIL >80%
  - / (root): WARN >80%, FAIL >90%

NETWORK — external APIs:
  - curl -sf --max-time 5 https://api.telegram.org — WARN if unreachable
  - curl -sf --max-time 5 https://discord.com/api/v10 — WARN if unreachable
  - curl -sf --max-time 5 https://api.github.com — WARN if unreachable
```

**Checks — Typhon (via SSH):**

```
Authoritative SSH config (from PROTOCOL.md, 2026-05-23):
  ssh -i ~/.ssh/id_ed25519 tf-tthq@192.168.1.150

NOTE: INFRASTRUCTURE.md currently lists Typhon at 192.168.1.113 — that is STALE.
.113 is shared with Calliope (Moonraker). Typhon’s correct IP is 192.168.1.150.
Update INFRASTRUCTURE.md after this sprint is deployed.

  - ssh -o ConnectTimeout=3 -o BatchMode=yes tf-tthq@192.168.1.150 true — FAIL if unreachable
  - ssh tf-tthq@192.168.1.150 "systemctl --user is-active djinn-printer-bot.service" — WARN if inactive
  - ssh tf-tthq@192.168.1.150 "curl -sf http://localhost:11434/api/tags" — WARN if unreachable
  - ssh tf-tthq@192.168.1.150 "systemctl is-active ollama.service" — WARN if inactive
```

**Checks — Orin (via SSH):**

```
  - ssh -o ConnectTimeout=3 -o BatchMode=yes javiermanzo@192.168.1.176 true — FAIL if unreachable
  - curl -sf --max-time 5 http://192.168.1.176:11434/api/tags — FAIL if unreachable when SSH alive
  - Parse response; check expected models: llama3.3:70b, qwen2.5-coder:32b, qwen3.6:latest, nomic-embed-text
  - ssh javiermanzo@192.168.1.176 "df -h /" — WARN if >80% (1.8Ti total)
```

**Checks — Calliope (Moonraker):**

```
Calliope Moonraker endpoint: http://192.168.1.113:7125
(This is the correct .113 address — Calliope, not Typhon)

  - curl -sf http://192.168.1.113:7125/printer/info — FAIL if unreachable
  - Parse state field: "ready" = PASS, "error" = FAIL, anything else = WARN
  - curl -sf http://192.168.1.113:7125/printer/objects/query?print_stats — capture state
  - WARN (not fail) if printer state is not "standby" or "ready" — may be printing
```

**JSON output schema:**
```json
{
  "timestamp": "2026-06-06T05:42:00Z",
  "overall": "PASS|WARN|FAIL",
  "machines": {
    "salomon": { "status": "PASS", "services": {...}, "timers": {...}, "disk": {...}, "ollama": {...} },
    "typhon":  { "status": "WARN", "ssh": true, "ollama": "WARN", "printer_bot": "PASS" },
    "orin":    { "status": "PASS", "ssh": true, "ollama": "PASS", "models": [...], "disk": {...} },
    "calliope": { "status": "PASS", "state": "ready" }
  },
  "network": { "telegram": true, "discord": true, "github": true }
}
```

**Integration:**  
- Called by `djinn-agent-doctor` as its primary engine (replace existing 11 checks with this)  
- Called by `djinn-morning` briefing script  
- Callable by Salomon agent: `djinn-system-health --json` for machine-parseable status  
- Cache file at `~/.cache/djinn/health-latest.json` (symlink or copy of most recent run)  

---

### djinn-vault-integrity

**Path:** `~/.local/bin/djinn-vault-integrity`  
**Language:** Python 3 (uses `python-frontmatter`, `pathlib`, `re`)  
**Dependencies:** `pip install python-frontmatter` (in `~/.venvs/djinn-orchestrator/` or system)  
**Timer:** Systemd timer, weekly on Sunday at 20:30 (before/after `djinn-weekly`)  
**AI required:** None  

**Input:**  
- No required args  
- `--vault-path PATH` (default: `~/Obsidian/djinn/`)  
- `--full` flag: scan all of `~/Obsidian/` including notes, references, inbox  
- `--fix-frontmatter` flag: auto-add minimal frontmatter to files missing it (dry-run default)  
- `--json` flag: JSON output to `~/.cache/djinn/vault-integrity-latest.json`  

**Output:**  
- Exit 0: no issues  
- Exit 1: issues found  
- Report written to `~/Obsidian/djinn/logs/vault-integrity-YYYY-MM-DD.md`  
- Summary appended to weekly review note if run by `djinn-weekly`  

**Checks:**

```
1. BROKEN WIKILINKS
   - Parse all *.md files
   - Extract all [[Link]] and [[Link|Display]] patterns via regex
   - For each extracted link target:
     a. Normalize: strip | aliases, strip #heading anchors
     b. Check if a file with that name exists anywhere in vault
     c. Use fuzzy basename match (case-insensitive, spaces == hyphens)
   - Report: broken link text, source file, line number
   - Threshold: WARN if >10 broken links; FAIL if >50

2. ORPHANED FILES
   - Build inbound link map: for every file, which other files link to it
   - Flag files with zero inbound links as orphaned
   - Exclude from orphan check:
     - Files in djinn/daily/ (daily notes are never linked directly)
     - Files in djinn/weekly/
     - Files in djinn/logs/
     - Files in djinn/research/marcus/ (research output is not expected to be linked)
     - README.md files
     - INFRASTRUCTURE.md, SYSTEM-STATE.md, GATEWAY.md (root docs)
   - Report: orphaned file path, file size, last modified
   - Threshold: WARN if >20 orphaned files

3. MISSING FRONTMATTER
   - Load each *.md with python-frontmatter
   - Flag files where frontmatter is absent or where these required fields are missing:
     - title (required for all files in djinn/core/, djinn/decisions/, djinn/skills/)
     - tags (required for all files above + djinn/projects/, djinn/research/)
     - created (required for djinn/decisions/, djinn/projects/)
   - Files in djinn/daily/, djinn/weekly/ are exempt (auto-generated)
   - Report: file path, missing fields

4. TAG FORMAT COMPLIANCE
   - Check all tag values against expected formats:
     a. All tags must be lowercase
     b. Multi-word tags use hyphens, not spaces or underscores
     c. No bare tags on decision/project files (must have at least one domain tag)
   - Flag non-compliant tags
   - Note: WARN-only until TAG-TAXONOMY.md is established (per TASK-067)

5. LARGE FILES
   - Flag any *.md file >500KB as WARN
   - Flag any file >2MB as FAIL

6. DUPLICATE DETECTION (lightweight)
   - Hash first 500 chars of each file body (excluding frontmatter)
   - Flag pairs with identical hashes as potential duplicates
   - WARN only, never auto-resolve
```

**Report format:**
```markdown
## Vault Integrity Report — YYYY-MM-DD

**Vault path:** ~/Obsidian/djinn/
**Files scanned:** 692
**Issues found:** 7 warnings, 0 failures

### Broken Wikilinks (3)
- `djinn/core/PROTOCOL.md:42` — `[[HEARTBEAT-typhon]]` — target not found

### Orphaned Files (2)
- `djinn/memory/2026-05-15-context-note.md` (1.2KB, 22 days old)

### Missing Frontmatter (2)
- `djinn/decisions/2026-05-20-vault-sync.md` — missing: created

### Large Files (0)

### Potential Duplicates (0)

*— djinn-vault-integrity, YYYY-MM-DD*
```

**Integration:**  
- Called by `djinn-weekly` at end of weekly review  
- Called by pre-commit hook (broken links + frontmatter checks only, fast subset)  
- Callable manually: `djinn-vault-integrity --full` for comprehensive scan  

---

## Batch B — Operations (Reduce Daily Friction)

---

### djinn-log-rotator

**Path:** `~/.local/bin/djinn-log-rotator`  
**Language:** Bash  
**Timer:** Systemd timer, weekly on Monday at 02:00  
**AI required:** None  

**Input:**  
- No required args  
- `--dry-run` flag: print what would be archived, no changes  
- `--days N` (default: 30): archive files older than N days  

**Output:**  
- Exit 0: completed  
- Summary to stdout  
- Append operation log to `~/Obsidian/djinn/logs/log-rotator-YYYY-MM-DD.md`  

**Targets and rules:**

```
1. ~/Obsidian/djinn/logs/*.md
   - Age threshold: 30 days
   - EXCLUDE: djinn/logs/reports/ (these are knowledge, not operational logs)
   - EXCLUDE: vault-integrity-*.md, backup-verify-*.md (keep 90 days)
   - EXCLUDE: error_log.md (persistent, never rotate)
   - Action: gzip to ~/Obsidian/djinn/logs/archive/YYYY-MM/

2. Ollama logs (journalctl for ollama.service)
   - Extract logs older than 30 days: journalctl -u ollama.service --until "30 days ago" > /tmp/ollama-old.log
   - Gzip and move to ~/Obsidian/djinn/logs/archive/YYYY-MM/ollama-YYYY-MM.log.gz
   - journalctl --rotate + --vacuum-time=30d

3. Gateway logs (djinn-telegram-gateway, djinn-discord-gateway)
   - Same journalctl approach as Ollama
   - Keep last 30 days in journal, archive older

4. ~/.cache/djinn/ health JSON files
   - Keep last 30 (newest), delete older
   - Not gzip-archived, just deleted

5. ~/Obsidian/djinn/communications/archive/
   - Verify archive dir exists
   - Check that archive dir hasn’t grown >500MB
   - COMMS archiving is a separate task (djinn-comms-archiver), not this script

6. POST-ROTATION
   - Report: N files archived, M MB freed
   - Run df -h and capture disk before/after
```

**Integration:**  
- Standalone systemd timer  
- Run `djinn-log-rotator --dry-run` to preview before first activation  

---

### djinn-model-warmkeeper

**Path:** `~/.local/bin/djinn-model-warmkeeper`  
**Language:** Bash  
**Timer:** Systemd timer every 4 minutes  
**AI required:** None  

**Input:**  
- No required args  
- `--status` flag: print which models are currently loaded in VRAM (`/api/ps`) and exit  
- `--models LIST`: override default keep-warm list (comma-separated)  

**Output:**  
- Exit 0: all target models pinged successfully  
- Exit 1: one or more pings failed  
- Silent by default (runs as systemd service)  
- Verbose if run interactively (TTY detection via `[ -t 1 ]`)  

**Models to keep warm:**

```
Salomon (localhost:11434) — always (24/7):
  - qwen2.5:7b       (main agent, highest frequency)
  - qwen2.5-coder:7b (coder agent, daily use)
  - mistral:7b       (creative + gateway relay)

Salomon — conditional on hour AND VRAM:
  - deepseek-r1:7b   (reasoning — only if VRAM free >4GB)
  - phi4:14b         (design/consult — only between 09:00–22:00 AND VRAM free >6GB)
  - llama3.2-vision:11b (vision — only between 09:00–22:00 AND VRAM free >8GB)

Orin (192.168.1.176:11434) — only if `ssh orin` succeeds:
  - qwen3.6:latest
  - nomic-embed-text

Never warm on Salomon outside window:
  phi4 and llama3.2-vision MUST NOT be kept warm outside 09:00–22:00.
  RTX 5060 is already at 56°C idle — holding 14B+ models overnight is unnecessary thermal load.
```

**Hour-window check (in-script, single systemd unit):**
```bash
# At top of script, before phi4/vision warm block:
HOUR=$(date +%H)
if [ "$HOUR" -ge 9 ] && [ "$HOUR" -lt 22 ]; then
  ACTIVE_HOURS=true
else
  ACTIVE_HOURS=false
fi

# phi4 block:
if [ "$ACTIVE_HOURS" = true ] && [ "$FREE_VRAM" -gt 6144 ]; then
  # warm phi4:14b
fi
```

This is one systemd unit (4-min interval). No OnCalendar start/stop juggling. The script decides what to warm based on time and VRAM state.

**VRAM check:**
```bash
FREE_VRAM=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null || echo 0)
```

**Ping mechanism:**
```bash
curl -sf -X POST http://localhost:11434/api/generate \
  -d '{"model": "qwen2.5:7b", "prompt": "", "keep_alive": "10m"}' \
  -o /dev/null
```

**Systemd unit:**
```ini
[Unit]
Description=Djinn Ollama Model Warmkeeper
After=ollama.service

[Service]
Type=oneshot
User=drmanzo
ExecStart=/home/drmanzo/.local/bin/djinn-model-warmkeeper
```

**Timer:**
```ini
[Timer]
OnBootSec=2min
OnUnitActiveSec=4min

[Install]
WantedBy=timers.target
```

**Integration:**  
- Fully standalone  
- `djinn-system-health` checks that this timer is active  
- `djinn-model-warmkeeper --status` callable from Discord/Telegram for VRAM snapshot  

---

### djinn-print-queue-manager

**Path:** `~/.local/bin/djinn-print-queue-manager`  
**Language:** Python 3 (reads `~/.local/share/djinn/print-queue.json`, calls Moonraker API)  
**Timer:** None (on-demand only)  
**AI required:** None  

**Input:**  
```
djinn-print-queue-manager list              # Show all queued jobs with metadata
djinn-print-queue-manager prioritize N M    # Move job N to position M
djinn-print-queue-manager remove N          # Remove queued (not active) job N
djinn-print-queue-manager clear             # Remove all queued (not active) jobs
djinn-print-queue-manager status            # Show active job + queue length
```

**Output:**  
- `list`: tabular view: ID, filename, filament, estimated_time, phase, added_at  
- `prioritize`/`remove`/`clear`: confirmation message + updated queue state  
- `status`: active print progress + queue depth  

**Hard safety rules (non-negotiable):**
```
1. NEVER modify, cancel, or interact with the ACTIVE print job.
   Moonraker endpoint: http://192.168.1.113:7125
   - On every write op: GET /printer/objects/query?print_stats first
   - If print_stats.state == "printing" or "paused" → exit 2 + error message
   - Message: "Active print in progress. djinn-print-queue-manager is read-only during printing."

2. djinn-print-queue-manager does NOT call:
   djinn-model-slice, djinn-confirm-print, djinn-deny-print,
   or any Moonraker /printer/print/start endpoint.

3. All removes are soft by default.
   - Remove moves job to ~/.local/share/djinn/print-queue-removed/
   - Permanent delete requires --hard flag + confirmation prompt
   - Log all removes to ~/Obsidian/djinn/logs/print-queue-log.md
```

**Queue file handling:**  
- Reads: `~/.local/share/djinn/print-queue.json`  
- Atomic writes: write to `.tmp`, then `rename()` (never write in-place)  

**Integration:**  
- Discord/Telegram `/queue` calls `djinn-print-queue-manager list` and formats output  
- `djinn-system-health` can call `djinn-print-queue-manager status --quiet` for Calliope state  

---

## Batch C — Hardening (Security and Observability)

---

### djinn-secrets-scanner

**Path:** `~/.local/bin/djinn-secrets-scanner`  
**Language:** Bash  
**Timer:** Pre-commit hook on djinn-vault repo + weekly systemd scan (Sundays 04:00)  
**AI required:** None  

**⚠️ Run this once manually this week before any timer is set up.** First run is a discovery scan.

**Input:**  
- No required args  
- `--target [vault|openclaw|logs|forge|all]` (default: all)  
- `--pre-commit` flag: fast scan of staged files only  
- `--report` flag: write results to `~/Obsidian/djinn/logs/security-scan-YYYY-MM-DD.md`  

**Output:**  
- Exit 0: no secrets found  
- Exit 1: potential secrets found  
- If pre-commit mode + exit 1: BLOCK commit with offending lines  

**Scan targets and patterns:**
```
1. djinn-vault repo staged files (pre-commit mode)
   gitleaks detect --staged --no-banner
   OR trufflehog git file://. --since-commit HEAD --only-verified

2. ~/.config/djinn/ and ~/.openclaw/workspace/
   - Verify all .env files are chmod 600
   - Check no .env file is tracked in any git repo
   - Regex patterns:
     r'sk-[A-Za-z0-9]{20,}'                         # Anthropic/OpenAI
     r'ghp_[A-Za-z0-9]{36}'                          # GitHub PAT
     r'bot[0-9]{8,12}:[A-Za-z0-9_-]{35}'            # Telegram bot token
     r'Bearer [A-Za-z0-9_\-.]{20,}'                  # Generic bearer
     r'OPENROUTER_API_KEY\s*=\s*[A-Za-z0-9_\-]{20,}' # OpenRouter

3. ~/Obsidian/djinn/logs/ (last 30 days)
   - Scan for accidental token echoes in log output
   - Skip gzipped archives

4. ~/.local/bin/djinn-*
   - Scan all scripts for hardcoded credentials
```

**Pre-commit hook (`~/Obsidian/.git/hooks/pre-commit`):**
```bash
#!/bin/bash
~/.local/bin/djinn-secrets-scanner --pre-commit
if [ $? -ne 0 ]; then
  echo "COMMIT BLOCKED: Potential secret detected. Review output above."
  exit 1
fi
```

**Install gitleaks (Fedora):**
```bash
dnf install gitleaks
# OR: go install github.com/gitleaks/gitleaks/v8@latest
```
If unavailable, script falls back to grep-based regex (slower, no git context).

**Integration:**  
- Pre-commit hook on djinn-vault repo  
- Claude verifies hook is installed post-deploy: `cat ~/Obsidian/.git/hooks/pre-commit`  

---

### djinn-comms-validator

**Path:** `~/.local/bin/djinn-comms-validator`  
**Language:** Python 3  
**Timer:** Systemd timer, every 15 minutes (after comms-processor fires)  
**AI required:** None  

**Context:** Validates existing COMMS.md entries against the format in PROTOCOL.md. Does NOT enforce a new format. Schema migration happens after this validator runs clean for 2 weeks.

**Input:**  
- No required args  
- `--comms-file PATH` (default: `~/Obsidian/djinn/communications/COMMS.md`)  
- `--since N` flag: only validate entries added in last N hours (default: 24)  
- `--strict` flag: enforce stricter validation (use post-migration only)  

**Output:**  
- Exit 0: all entries valid  
- Exit 1: malformed entries found  
- Print malformed entry line numbers and snippets to stdout  
- Append to `~/Obsidian/djinn/logs/comms-validation-log.md` if issues found  

**Canonical COMMS entry format (from PROTOCOL.md — this is the source of truth):**

```
### YYYY-MM-DD HH:MM UTC — @Sender → @Recipient: Subject

**What:** one-line description
**Action:** what the recipient must do (or "none — FYI")
**Paths:** relevant files (if any)

— AgentName
```

Valid recipient tags: `@Salomon`, `@Typhon`, `@Claude`, `@Marcus`, `@All`  
Valid agent names: `Claude`, `Salomon`, `Typhons Forge`, `Marcus`, `Djinn`  
Optional processed tag (appended after acting): `**Processed:** YYYY-MM-DD — AgentName`  
Optional checkpoint tag (Tier 3): subject prefixed with `CHECKPOINT:`  

**Validation rules — flag as malformed if:**
```
1. Entry has no H3 heading (### line) with a timestamp
2. Timestamp in heading is not parseable as YYYY-MM-DD HH:MM UTC
3. No @Sender or sender not in valid agent list
4. No @Recipient or recipient tag not in valid list
5. Missing **What:** field
6. Missing **Action:** field
7. Missing signature line (— AgentName)
8. Signature agent name not in valid agent list
9. Entry body is empty (just heading + signature, no What/Action)
10. Entry contains credential patterns (run secrets regex as safety check)
```

**Lenient handling (do not flag):**
```
- **Paths:** field is optional — not all entries reference files
- Processed/Checkpoint tags are optional additions, not required
- Slight whitespace/newline variation around fields
- Entries in djinn/communications/archive/ — validate format but do not fail on stale timestamps
```

**Future strict format (v2 — TOML blocks):**
```toml
# Target format post-migration (design only — do not implement yet):
[[entry]]
from = "Salomon"
to = "Claude"
timestamp = "2026-06-06T05:42:00Z"
subject = "print-job-3-complete"
body = "Job #3 (mario_pipe.gcode) completed. Duration: 4h22m. No errors."
signed = "Salomon"
```
Migration only after validator runs clean and `djinn-agent-audit-log` is live.

**Integration:**  
- Runs after comms-processor timer (3-min); confirms dispatch integrity  
- If issues found: append a WARN entry to COMMS.md itself (meta: validator flagged line N)  
- Claude reviews validation log weekly  

---

### djinn-agent-audit-log

**Path:** `~/.local/bin/djinn-agent-audit-log` (CLI) + `~/.local/share/djinn/agent-audit.jsonl` (log)  
**Language:** Python 3 (writer + reader CLI)  
**Timer:** None (called by agents at decision points)  
**AI required:** None  

**⚠️ SCHEMA DESIGN — Claude must review before Marcus implements.**  
This is an architectural decision. Validate or modify the schema below before Salomon deploys.

**Design rationale:**  
COMMS.md = handoff log (task routing between agents, human-readable).  
Audit log = decision log (what automated action was taken, on what input, with what result).  
They are complementary, not redundant. Mixing automated JSONL entries into COMMS.md would make it noisy for agents that read it for context. COMMS.md stays clean for handoffs. Audit log is structured JSONL for machine queryability.

**Log file:** `~/.local/share/djinn/agent-audit.jsonl`  
- Append-only, one JSON object per line  
- Never rotated (archive but always keep)  
- Weekly copy to `~/Obsidian/djinn/logs/audit/audit-YYYY-WNN.jsonl` for vault backup  

**JSONL schema (one record per automated action):**
```json
{
  "version": "1",
  "timestamp": "2026-06-06T05:42:00Z",
  "agent": "Salomon",
  "trigger": "comms-processor | systemd-timer | discord-command | telegram-command | manual",
  "action": "print-queue-add | vault-sync | model-inference | skill-invoke | service-restart | file-write | api-call",
  "action_detail": "djinn-print-consult 3",
  "input_summary": "Discord #3d-printing: @Salomon slice job 3 infill=20",
  "input_hash": "sha256:abc123...",
  "output_summary": "Slice completed. profile=standard, time=2h14m, filament=18g",
  "exit_code": 0,
  "duration_ms": 1420,
  "machine": "salomon",
  "model_used": "qwen2.5:7b | null"
}
```

**Writer CLI:**
```bash
djinn-agent-audit-log write \
  --agent "Salomon" \
  --trigger "discord-command" \
  --action "skill-invoke" \
  --action-detail "djinn-print-consult 3" \
  --input-summary "Discord: slice job 3" \
  --output-summary "Slice complete, 2h14m" \
  --exit-code 0 \
  --duration-ms 1420
```

**Reader CLI:**
```bash
djinn-agent-audit-log query --agent Salomon --since 24h
djinn-agent-audit-log query --action print-queue-add --since 7d
djinn-agent-audit-log query --exit-code 1 --since 24h   # find failures
djinn-agent-audit-log tail 20                           # last 20, formatted
```

**Required call sites (add djinn-agent-audit-log write to these scripts):**
```
1. djinn-confirm-print    (action: print-start)
2. djinn-deny-print       (action: print-deny)
3. djinn-model-slice      (action: slice)
4. djinn-vault-indexer    (action: index-rebuild)
5. comms-processor        (action: comms-dispatch, one per entry processed)
6. djinn-sync             (action: vault-sync)
7. Any future automated deploy or config change
```

**Retention:**  
- JSONL is append-only, never deleted  
- Weekly copy to vault for git backup  
- Monthly summary: `djinn-agent-audit-log query --since 30d --summary` → monthly note  

---

## Implementation Order

```
Week 1 (Batch A):
  Day 1: djinn-backup-verifier — run manually first (rclone listremotes to confirm remote name)
  Day 2: djinn-system-health — replaces djinn-agent-doctor internals
  Day 3–4: djinn-vault-integrity — Python, most complex in Batch A

Week 2 (Batch B):
  Day 1: djinn-model-warmkeeper — immediate VRAM benefit
  Day 2: djinn-log-rotator — run --dry-run first, review before activating
  Day 3–4: djinn-print-queue-manager — Python, requires Moonraker API familiarity

Week 3 (Batch C):
  Day 1: djinn-secrets-scanner — run manually FIRST, before any timer
  Day 2: djinn-comms-validator
  Day 3–4: djinn-agent-audit-log — after Claude reviews schema above
```

---

## Notes for Claude

1. **Review the `djinn-agent-audit-log` schema** before Salomon implements. Field names, action vocabulary, and call site list are proposals. If schema needs modification, update this file and leave a COMMS note for Salomon.

2. **COMMS.md v2 migration** (TOML blocks) is not part of this sprint. Validator runs first, cleans current entries, migration is a separate session decision.

3. **Wire djinn-system-health into djinn-morning.** After Salomon deploys: add `djinn-system-health --quiet || djinn-system-health` at the top of the morning briefing script.

4. **Verify pre-commit hook post-deploy:** `cat ~/Obsidian/.git/hooks/pre-commit`. If not present, install from the djinn-secrets-scanner spec above.

5. **INFRASTRUCTURE.md has stale Typhon IP.** The file lists `.113` for Typhon; correct IP is `192.168.1.150` per PROTOCOL.md (2026-05-23). Update INFRASTRUCTURE.md in a separate commit after this sprint deploys.

---

*— Marcus (Perplexity AI), 2026-06-06. Revised 2026-06-06: Typhon IP corrected (.150), rclone remote clarified (gdrive:), backup test file changed to PROTOCOL.md, warmkeeper hours added (09:00–22:00 in-script), comms validator format pasted from PROTOCOL.md directly.*
