---
title: TASK-059 — djinn-bughunter Monitoring Architecture
agent: marcus
date: 2026-06-01
tags: [research, monitoring, systemd, python, telegram, bughunter]
status: delivered
---

# TASK-059 — djinn-bughunter: Robust Local Error Monitoring

## Summary

`djinn-bughunter` currently catches clean service crashes via `OnFailure=` and lets scripts call `djinn-alert` directly. That covers the loudest failure class — but misses silent failures, stuck loops, empty-output runs, and resource saturation. This report maps every gap and gives a concrete implementation plan for `djinn-health` and hardened Python wrappers that catch the 80% that matters without adding maintenance overhead.

**Recommended action for Claude/Salomon:** Implement Section 6 architecture in order. Start with Section 2 (Python wrapper) since it retrofits existing scripts with zero per-script changes, then Section 5 (journald), then Section 1 additions (watchdog + timer audit), then Section 3 (`djinn-health`). Section 4 (bot heartbeat) is last — lowest risk, highest polish.

---

## Section 1 — Systemd `OnFailure` Coverage Gaps

### What `OnFailure=` Does and Does Not Catch

`OnFailure=` fires when a service unit enters the `failed` state: non-zero exit code, OOM kill, or abnormal signal termination. That covers the majority of crashing failures — but systemd has well-documented blind spots at scale.

**What it misses:**

| Failure Class | Why OnFailure Misses It | Detection Pattern |
|---|---|---|
| Timer exits 0 with no output | Service "succeeded" — no failure state | Output hash check in wrapper |
| Timer misconfigured / never fires | Unit never activates — no failure, just silence | `systemctl list-timers` audit cron |
| Silent no-op (wrong path, empty data) | Exit 0 with empty file or stale timestamp | File mtime check post-run |
| Restart loop (rapid cycling) | Each restart "succeeds" briefly | `StartLimitBurst` + rate alert |
| Service stuck / hung | Process alive, not making progress | `WatchdogSec=` in unit file |
| Timer enabled but wrong `WantedBy` | Never loaded into `timers.target` | Systemd timer dependency audit |

**Restart loops are particularly dangerous.** A service set to `Restart=always` without `StartLimitBurst` and `StartLimitIntervalSec` will restart indefinitely and silently — each restart resets the failure count, so `OnFailure` fires and then the service "recovers" before Javier sees a pattern. The HN discussion on this (2023) called it the canonical reason to monitor error *rates*, not just individual failure events. The winning pattern: add `StartLimitIntervalSec=300` and `StartLimitBurst=5` to prevent infinite silent churn.

**`systemd-watchdog` (`WatchdogSec=`)** is worth adding to any long-running daemon (gateways, watcher daemons). It requires the process to send `WATCHDOG=1` via `sd_notify()` (or the Python `sdnotify` library) at intervals of `WatchdogSec / 2`. If the process hangs without crashing — stuck in a poll loop, waiting on a dead socket — watchdog kills and restarts it. `OnFailure` alone does not catch a hung-but-alive process. Kubernetes adopted this pattern for kubelet in v1.32 with a 30s default — appropriate for Djinn's daemons too.

**Recommended additions to long-running service units:**
```ini
[Service]
WatchdogSec=120s
Restart=on-failure
RestartSec=10
StartLimitIntervalSec=300
StartLimitBurst=5
```

**Timer audit — detect timers that never fired:**
```bash
# Weekly cron — add to djinn-health or standalone:
systemctl --user list-timers --all --output=json \
  | python3 -c "
import json, sys, datetime
units = json.load(sys.stdin)
now = datetime.datetime.utcnow().timestamp()
for u in units:
    last = u.get('last_trigger_usec', 0)
    if last == 0:
        print(f'NEVER FIRED: {u[\"unit\"]}')
    elif (now - last/1e6) > 86400 * 2:  # >48h since last run
        name = u['unit']
        age_h = (now - last/1e6) / 3600
        print(f'STALE ({age_h:.0f}h): {name}')
" | while read line; do djinn-alert "$line"; done
```

`Persistent=true` in timer units ensures that if the machine was off at the scheduled time, the timer fires immediately on next boot — without it, missed runs are silently skipped.

---

## Section 2 — Python Script Error Capture Beyond systemd

### The Core Problem

Most Djinn scripts run via systemd timers and either: (a) exit 0 on partial failure because they caught exceptions internally, or (b) raise unhandled exceptions that go to journald but never trigger `djinn-alert` because the exit code bubbles up too late or is swallowed by a broad `except` block. The gap is **exit 0 + silent wrong output** — no failure state, no alert, wrong data written downstream.

### Pattern 1: Universal CLI Wrapper (Zero Per-Script Changes)

The cleanest approach for Djinn's architecture: a thin wrapper that any script can be called through. Add one line to the systemd unit:

```ini
# In the .service unit:
ExecStart=/home/drmanzo/.local/bin/djinn-run /home/drmanzo/.local/bin/djinn-trend-agent
```

`djinn-run` implementation:
```python
#!/usr/bin/env python3
"""Universal exception-catching wrapper for Djinn scripts."""
import sys, subprocess, os, datetime

def djinn_alert(msg):
    os.system(f'djinn-alert "{msg}"')

script = sys.argv[1:]
if not script:
    sys.exit(1)

result = subprocess.run(script, capture_output=False)
if result.returncode != 0:
    name = os.path.basename(script[0])
    djinn_alert(f"⚠️ {name} exited {result.returncode} at {datetime.datetime.now().strftime('%H:%M')}")
    sys.exit(result.returncode)
```

For Python scripts that you *can* modify, the `telegram-exception-alerts` library (PyPI) provides a zero-dependency decorator pattern — the recommended approach per the library docs:

```python
from telegram_exception_alerts import Alerter
tg_alert = Alerter.from_environment()  # reads ALERT_BOT_TOKEN + ALERT_CHAT_ID env vars

@tg_alert
def run_trend_agent():
    # ... full script logic
    pass
```

This sends the full traceback to Telegram on any unhandled exception with no additional error handling code required. It uses no external dependencies beyond the standard library.

### Pattern 2: Context Manager for Block-Level Coverage

```python
from contextlib import contextmanager
import subprocess, datetime

@contextmanager
def djinn_guard(label: str):
    try:
        yield
    except Exception as e:
        subprocess.run(['djinn-alert', f'⚠️ {label}: {type(e).__name__}: {e}'])
        raise

# Usage in any script:
with djinn_guard("djinn-trend-agent/ollama-synthesis"):
    result = call_ollama(prompt)
    parsed = json.loads(result)
```

### Pattern 3: Output Validation (Silent Success Detection)

The hardest case — the script runs, exits 0, but wrote empty or stale data. Add post-run validation to the timer service:

```ini
[Service]
ExecStart=/home/drmanzo/.local/bin/djinn-trend-agent
ExecStartPost=/home/drmanzo/.local/bin/djinn-validate-output trend-signal
```

`djinn-validate-output` checks the mtime and minimum size of the expected output file:
```python
#!/usr/bin/env python3
import sys, os, datetime, subprocess

CHECKS = {
    "trend-signal": ("~/Obsidian/djinn/social/TREND-SIGNAL.md", 200, 7200),  # path, min_bytes, max_age_s
    "heartbeat": ("~/Obsidian/djinn/communications/HEARTBEAT-typhon.md", 50, 600),
}
label = sys.argv[1]
path, min_bytes, max_age = CHECKS[label]
path = os.path.expanduser(path)
if not os.path.exists(path):
    subprocess.run(['djinn-alert', f'⚠️ {label}: output file missing: {path}'])
    sys.exit(1)
age = datetime.datetime.now().timestamp() - os.path.getmtime(path)
size = os.path.getsize(path)
if age > max_age or size < min_bytes:
    subprocess.run(['djinn-alert', f'⚠️ {label}: output stale ({age:.0f}s old, {size}B)'])
    sys.exit(1)
```

### Self-Hosted Error Tracking (Optional — If You Want History)

**GlitchTip** is the practical self-hosted Sentry alternative for Djinn-scale systems. It requires only 4 Docker containers (backend + Celery worker + Redis + PostgreSQL) vs Sentry's 12+, uses ~50MB RAM per container, and is fully compatible with the Sentry Python SDK. Free tier: unlimited projects, up to 1,000 events/month (well within Djinn's volume). The `sentry-sdk` drop-in means any Python script gets error tracking with `sentry_sdk.init(dsn="http://...")`. At Djinn's scale, this is optional — the decorator pattern above is sufficient for reactive alerting.

---

## Section 3 — Disk and Resource Monitoring

### What Thresholds Matter for Salomon

| Resource | Djinn Risk | Recommended Threshold | Tool |
|---|---|---|---|
| `/mnt/storage` disk | Print queue, media pipeline, Ollama models — 870GB HDD | Alert at 85%, critical at 95% | `psutil.disk_usage()` |
| `/` SSD disk | OS + configs — 174GB free | Alert at 80% | `psutil.disk_usage()` |
| RAM | Ollama inference (phi4:14b needs ~10GB) — 32GB total | Alert at 90% used | `psutil.virtual_memory()` |
| GPU VRAM | RTX 5060 8GB — model loading | Alert if `nvidia-smi` shows >95% | `nvidia-smi` subprocess |
| Ollama process | If it crashes, all inference stops | Check `pgrep ollama` in health check | `pgrep` / `systemctl` |

**`psutil`** is the correct tool here — it's Python stdlib-adjacent, already installed in any scientific Python environment, and covers CPU/RAM/disk without any daemon. Using `psutil` + direct Telegram call (via `djinn-alert`) is the correct pattern for Djinn's architecture — no Prometheus, no Grafana, no Node Exporter.

```python
import psutil, subprocess

def check_resources():
    alerts = []
    disk_storage = psutil.disk_usage('/mnt/storage').percent
    disk_root = psutil.disk_usage('/').percent
    ram = psutil.virtual_memory().percent

    if disk_storage > 85:
        alerts.append(f"💾 /mnt/storage: {disk_storage:.0f}% full")
    if disk_root > 80:
        alerts.append(f"💾 / (SSD): {disk_root:.0f}% full")
    if ram > 90:
        alerts.append(f"🧠 RAM: {ram:.0f}% used")

    # Check Ollama running
    result = subprocess.run(['pgrep', '-x', 'ollama'], capture_output=True)
    if result.returncode != 0:
        alerts.append("🔴 Ollama process not running")

    for alert in alerts:
        subprocess.run(['djinn-alert', alert])
```

**Can systemd trigger disk pressure alerts natively?** Partially — `MemoryPressure=` and `CPUPressure=` directives (systemd 248+) can throttle units under pressure, but they don't send Telegram alerts. A cron-based `djinn-health` script running every 30 minutes is simpler and more transparent for Djinn's architecture than wiring into PSI (Pressure Stall Information) events.

**Netdata** (mentioned widely in the Linux admin community) is the right lightweight dashboard if Javier ever wants a visual — it auto-discovers services, has <1% CPU overhead, and exposes systemd unit failed states as built-in alerts. Install: `bash <(curl -Ss https://my-netdata.io/kickstart.sh)`. Dashboard at `:19999`. Optional addition — not a dependency.

---

## Section 4 — Telegram Bot Self-Monitoring

### The Failure Classes OnFailure Doesn't Catch

| Failure | systemd sees | Result |
|---|---|---|
| Bot process crashed | `failed` state → `OnFailure` fires ✅ | Caught |
| Telegram API unreachable (network) | Process alive, exit 0 errors | Silent ❌ |
| Poll loop silently stuck | Process alive, no exceptions | Silent ❌ |
| Messages arriving but not processed | Process alive, no failures | Silent ❌ |

### Pattern: Bot Self-Heartbeat

The standard pattern from the Telegram bot monitoring community: the bot sends a heartbeat message to a private monitoring channel every N hours. If you don't see the heartbeat, the bot is stuck or dead.

```python
# Add to djinn-telegram-gateway — runs via APScheduler or asyncio periodic task
import datetime, asyncio

HEARTBEAT_INTERVAL_H = 6
HEARTBEAT_CHAT_ID = os.environ.get('DJINN_HEARTBEAT_CHAT_ID')  # separate monitoring chat

async def send_heartbeat(bot):
    if not HEARTBEAT_CHAT_ID:
        return
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    await bot.send_message(HEARTBEAT_CHAT_ID, f"💚 djinn-gateway alive — {ts}")

# In the Application's post_init or via JobQueue:
# application.job_queue.run_repeating(lambda ctx: send_heartbeat(ctx.bot),
#                                     interval=HEARTBEAT_INTERVAL_H * 3600)
```

The secondary monitor: add the bot's Telegram chat ID to a simple external ping check. If you have a second bot token (even a free one), it can message the primary bot and check for a response — this is the "dead man's switch" pattern. For single-person operations, the simpler version is: add a `djinn-gateway-watchdog` cron that checks the mtime of the last incoming message log file every 2 hours and alerts if it's stale beyond a threshold.

**python-telegram-bot v20+ (async):** The `JobQueue` API handles periodic tasks natively — no `APScheduler` required. `application.job_queue.run_repeating(callback, interval=21600)` schedules the heartbeat cleanly without a separate thread.

### Detecting Stuck Poll Loop

Add a `asyncio.wait_for()` timeout wrapper around the Telegram long-poll call, or use the `read_timeout` and `connect_timeout` parameters in `Application.builder()`:

```python
Application.builder() \
    .token(TOKEN) \
    .read_timeout(30) \
    .connect_timeout(10) \
    .build()
```

This ensures the bot raises a `NetworkError` (catchable) rather than hanging indefinitely on a dead connection. Combine with `Restart=on-failure` + `RestartSec=30` in the service unit.

---

## Section 5 — Local Log Persistence

### journald Persistent Logging

By default, systemd stores logs only in `/run/log/journal/` — lost on reboot. One command enables persistence:

```bash
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald
# OR set Storage=persistent in /etc/systemd/journald.conf
```

With persistent journald, all Djinn service output is queryable across reboots via `journalctl`. This is the recommended path for Djinn — it replaces ad-hoc `/tmp/` log files with a structured, indexed, automatically rotated store.

**Key journalctl queries for Djinn:**
```bash
# Last 24h failures across all Djinn units:
journalctl --user -p err --since "24h ago"

# How many times did djinn-trend-agent restart today:
journalctl --user -u djinn-trend-agent --since today | grep -c "Started\|Stopped"

# Show last run output of any timer:
journalctl --user -u djinn-morning --since "6h ago"

# Pattern: did this error appear 3+ times this hour:
journalctl --user -u djinn-telegram-gateway --since "1h ago" | grep -c "ERROR"
```

**journald vs flat log files:**

| | journald | Flat files in `~/Obsidian/djinn/logs/` |
|---|---|---|
| Query speed | Fast (indexed binary) | Slow (grep) |
| Multi-service aggregation | Built-in (`-u unit1 -u unit2`) | Manual |
| Automatic rotation | Yes (SystemMaxUse in journald.conf) | logrotate required |
| Human readable without tools | No (`journalctl` required) | Yes |
| Cross-reboot persistence | Yes (after enabling) | Yes (always) |
| Djinn vault integration | No | Yes (git-committed) |

**Recommended:** Use journald for operational logs (real-time service output), keep the existing Djinn vault flat files for agent-generated reports, session logs, and build log. Don't replace one with the other — they serve different query patterns.

**Log size management** — add to `/etc/systemd/journald.conf`:
```ini
[Journal]
Storage=persistent
SystemMaxUse=500M
SystemKeepFree=1G
MaxRetentionSec=30day
```

**Lightweight pattern-alerting (no ELK):**
```bash
# Add to djinn-health or a 30-min cron:
ERROR_COUNT=$(journalctl --user --since "30min ago" -p err -q | wc -l)
if [ "$ERROR_COUNT" -gt 10 ]; then
    djinn-alert "⚠️ Journal: $ERROR_COUNT errors in last 30 min"
fi
```

---

## Section 6 — Build Recommendation

### The 20% That Catches 80% of Real Failures

In priority order — each builds on the previous:

**Sprint 1 — Retrofit (2–3 hours, zero per-script changes):**
1. Enable journald persistence (`mkdir -p /var/log/journal`)
2. Add `Restart=on-failure` + `StartLimitBurst=5` + `StartLimitIntervalSec=300` to all 7 core service units
3. Add `WatchdogSec=120s` to the two gateway daemons (telegram, discord)

**Sprint 2 — djinn-health script (3–4 hours):**
Build `djinn-health` at `~/.local/bin/djinn-health` — runs via 30-min systemd timer:

```python
#!/usr/bin/env python3
"""djinn-health — 30-minute system state check. Alerts on anything anomalous."""
import psutil, subprocess, datetime, os, pathlib

def alert(msg):
    subprocess.run(['djinn-alert', msg])

def check():
    alerts = []

    # 1. Disk (critical for print pipeline + Ollama models)
    for mount, threshold in [('/mnt/storage', 85), ('/', 80), ('/mnt/archive', 90)]:
        try:
            pct = psutil.disk_usage(mount).percent
            if pct > threshold:
                alerts.append(f"💾 {mount}: {pct:.0f}% full (threshold {threshold}%)")
        except FileNotFoundError:
            pass

    # 2. RAM
    ram = psutil.virtual_memory().percent
    if ram > 90:
        alerts.append(f"🧠 RAM: {ram:.0f}% used")

    # 3. Ollama process
    if subprocess.run(['pgrep', '-x', 'ollama'], capture_output=True).returncode != 0:
        alerts.append("🔴 Ollama not running — inference offline")

    # 4. Stale outputs (critical files not updated in expected window)
    stale_checks = [
        ('~/Obsidian/djinn/social/TREND-SIGNAL.md', 25200, 'trend-signal'),   # 7h
        ('~/Obsidian/djinn/communications/HEARTBEAT-typhon.md', 1800, 'typhon-heartbeat'),
    ]
    for path_str, max_age, label in stale_checks:
        path = pathlib.Path(os.path.expanduser(path_str))
        if path.exists():
            age = datetime.datetime.now().timestamp() - path.stat().st_mtime
            if age > max_age:
                alerts.append(f"⏰ {label} stale ({age/3600:.1f}h old)")

    # 5. Timer audit — timers not fired in >48h
    result = subprocess.run(
        ['systemctl', '--user', 'list-timers', '--all'],
        capture_output=True, text=True
    )
    # Parse for "n/a" in LAST column (never fired)
    for line in result.stdout.splitlines():
        if ' n/a ' in line and '.timer' in line:
            unit = [t for t in line.split() if '.timer' in t]
            if unit:
                alerts.append(f"🔇 Timer never fired: {unit[0]}")

    # 6. Journal error rate
    errors = subprocess.run(
        ['journalctl', '--user', '--since', '30min ago', '-p', 'err', '-q'],
        capture_output=True, text=True
    )
    error_count = len([l for l in errors.stdout.splitlines() if l.strip()])
    if error_count > 15:
        alerts.append(f"📋 Journal: {error_count} errors in last 30min")

    # 7. Restart loop detection
    for unit in ['djinn-telegram-gateway', 'djinn-trend-agent', 'djinn-morning']:
        restart_log = subprocess.run(
            ['journalctl', '--user', '-u', unit, '--since', '1h ago', '-q'],
            capture_output=True, text=True
        )
        restarts = restart_log.stdout.count('Started')
        if restarts > 5:
            alerts.append(f"🔄 Restart loop: {unit} restarted {restarts}x in last hour")

    if alerts:
        summary = '\n'.join(alerts)
        subprocess.run(['djinn-alert', f"djinn-health report:\n{summary}"])
    else:
        # Silent on clean run — only speak when something's wrong
        pass

if __name__ == '__main__':
    check()
```

**Sprint 3 — Python exception wrapper (1–2 hours):**
- Add `telegram-exception-alerts` decorator to the 5 most critical scripts (trend-agent, morning, social-analyst, media-publish, queue-runner)
- Or deploy `djinn-run` wrapper and update service ExecStart lines to route through it

**Sprint 4 — Bot heartbeat (1 hour):**
- Add 6-hour heartbeat to `djinn-telegram-gateway` via `JobQueue`
- Create a separate `DJINN_HEARTBEAT_CHAT_ID` env var in `telegram.env`

**Sprint 5 — Output validation (2 hours):**
- Build `djinn-validate-output` and wire as `ExecStartPost=` on the 3 most critical timers

### Estimated Build Times and Maintenance Cost

| Component | Build | Maintenance | Failure mode if it breaks |
|---|---|---|---|
| journald persistence | 5 min | Zero | Logs go to /run (lost on reboot) |
| Restart/watchdog unit tweaks | 30 min | Zero | Noisy restart loops |
| `djinn-health` 30-min cron | 3-4 h | Low (update thresholds) | No proactive alerts |
| Exception decorator | 1-2 h/script | Zero | Exceptions go to journal only |
| `djinn-run` wrapper | 1 h | Near zero | Same as decorator fallback |
| Bot heartbeat | 1 h | Zero | No alive-proof for gateway |
| Output validation | 2 h | Low (new scripts need entries) | Silent stale outputs undetected |

**Total Sprint 1–4:** ~12–15 hours build, <1 hr/month maintenance.

**High-maintenance components to avoid:**
- Self-hosted Sentry (too heavy for one machine)
- Custom log aggregation daemons (journald + `journalctl` queries are sufficient)
- Prometheus + Grafana stack (massive overkill — `psutil` + `djinn-health` covers all the real thresholds)
- Self-built Instagram scraper patterns applied to monitoring (anything that requires browser automation to monitor itself is a trap)

**GlitchTip** is the one optional addition worth considering if Javier wants error history and grouping rather than just live alerts. Free tier (1,000 events/month), Sentry SDK compatible, 4 Docker containers. Add only if the decorator approach generates too much noise without context.

---

## Sources

- Lennart Poettering, "systemd for Administrators Part XV — Watchdog Support": http://0pointer.de/blog/projects/watchdog.html
- Kubernetes systemd watchdog integration (v1.32 beta): https://kubernetes.io/docs/reference/node/systemd-watchdog/
- `telegram-exception-alerts` PyPI package: https://pypi.org/project/telegram-exception-alerts/
- GlitchTip self-hosted error tracking: https://glitchtip.com
- systemd/Timers — ArchWiki: https://wiki.archlinux.org/title/Systemd/Timers
- journald persistent logging — Red Hat KB: https://access.redhat.com/solutions/696893
- systemd restart loop discussion — HN 2023: https://news.ycombinator.com/item?id=36952867
- systemd service reliability patterns 2026: https://www.devopsness.com/blog/systemd-service-reliability-patterns
- Lightweight system monitoring with psutil + Telegram: https://medium.com/@kunalsharma1601/telegram-integrated-system-monitor-on-aws-ec2
- Exception logging decorator patterns: https://www.blog.pythonlibrary.org/2016/06/09/python-how-to-create-an-exception-logging-decorator/
- Netdata lightweight monitoring: https://dev.to/yash_step2dev/how-to-set-up-linux-server-monitoring-in-10-minutes-free-1715
- GlitchTip vs Sentry self-hosted 2026: https://danubedata.ro/blog/self-host-sentry-glitchtip-error-tracking-2026

— Marcus, 2026-06-01
