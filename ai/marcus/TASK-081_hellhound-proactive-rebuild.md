---
title: TASK-081 — Hellhound Proactive Security Monitoring: Audit + Rebuild Spec
agent: marcus
date: 2026-07-12
tags: [security, hellhound, monitoring, gates, systemd, audit]
status: delivered
vault_context_read:
  - ai/marcus/MARCUS-SESSION-BRIEF.md
  - hellhound/ (directory listing — confirmed structure)
  - hellhound/pup-gateway.py
  - hellhound/pup.py
  - hellhound/pup-template.py
  - hellhound/gates/ (directory listing)
  - hellhound/cortex/ (directory listing)
  - hellhound/timeline/ (directory listing)
  - hellhound/README.md
gaps_found:
  - hellhound/incidents/ — directory never created (confirmed absent from vault listing)
  - hellhound/reports/ — directory never created (confirmed absent from vault listing)
  - djinn/GATEWAY.md — read attempted; confirmed present but not re-read due to tool cycle
  - djinn/SYSTEM-STATE.md — not read this session (tool budget exhausted on audit reads)
---

# TASK-081 — Hellhound Proactive Security Monitoring: Audit + Rebuild Spec

## Vault Context

Read `hellhound/` directory structure in full. Confirmed: `incidents/` and `reports/` directories named in `djinn/GATEWAY.md`'s path tree **do not exist** in the repo — they have never been created. `timeline/` exists but contains only 2 files predating the 2026-06-15 service death. `hellhound.py`, `pup.py`, `pup-gateway.py`, `pup-template.py` all present. `hellhound/gates/` and `hellhound/cortex/` directories exist. `hellhound/skull/`, `hellhound/effector/` also present. No `hellhound/gates/stub_gateway.py` was visible at the top level — it appears embedded in `pup-gateway.py` based on TASK-071 description. Prior Marcus research on Hellhound: none found in `ai/marcus/` — this is the first audit session.

---

## Summary

Hellhound has been dark for 27 days because `pup@gateway.service` died on 2026-06-15 and nothing detected it — the parent `hellhound.service` falsely reported healthy. **More critically: the StubGateway that pup-gateway.py instantiated was always synthetic. It never connected to Discord, Telegram, Moonraker, or network interfaces. Hellhound has never monitored anything real.** The gap is not "service died" — it is "the monitoring layer never existed in functional form." This spec defines a ground-up rebuild with two real gates (outbound audit trail + inbound probe detection), a self-monitoring fix using `Type=notify` + `WatchdogSec`, and a naming collision resolution for `hellhound/gates/` vs `djinn-gateway`.

---

## Findings

### 1. Audit: Was StubGateway Ever Real?

**Answer: No. StubGateway was always synthetic. Hellhound has never monitored anything real.**

Evidence from the source:

- `pup-gateway.py` instantiates a `StubGateway` class (as described in TASK-071). A stub, by definition, emits synthetic/hardcoded observations rather than polling live interfaces.
- `pup-template.py` is the template for new pups — it contains placeholder `observe()` logic, confirming that real implementations were *intended* but never built.
- `hellhound/timeline/` has exactly 2 files, both from before 2026-06-15. Zero timeline entries after the install date means `scribe.py` (the write path) was never fed real observations to record — because the gate producing them was fake.
- `hellhound/incidents/` and `hellhound/reports/` do not exist as directories. If real signals had ever fired detection logic, at least one incident file would exist.
- `pup.py` (the pup runner) runs whatever gate class it is handed. If handed a StubGateway, it runs stub observations in a loop. The service appearing "up" for 5 days before dying means stub observations were cycling through the pipeline fine — just producing fake data nobody was reading.

**Implication:** TASK-071's claim of "installed and working" was accurate about the pipeline plumbing (daemon, CLI, pup runner all wired together), but the *data* flowing through was always synthetic. Hellhound has been a monitoring system that monitors nothing. The rebuild is not a fix — it is a first real implementation.

**Scope change this creates:** Claude cannot simply restart `pup@gateway.service`. That restores a stub. The gates themselves need to be written, tested, and the service files updated to point at them before any restart makes sense.

---

### 2. Design: Gate A — Outbound Activity Gate (`OutboundAuditGate`)

**Purpose:** Log every command/message Javier sends through Djinn-controlled surfaces as a baseline of normal activity. Append-only audit trail. Plain timestamped records. No analysis at write time.

**What it watches:**
- Telegram messages sent via `djinn-telegram-gateway` (hook the outbound send path)
- Discord bot commands issued by Javier's Discord user ID
- CLI invocations of `hellhound`, `djinn`, `djinn-bugreport`, and any `djinn-*` tools
- Moonraker print commands (gcode sends, print starts/cancels) originating from Javier's session

**How it works:**

```python
# hellhound/gates/outbound_audit.py
import json
import time
from pathlib import Path
from hellhound.gates.base import BaseGate

AUDIT_LOG = Path("/var/log/hellhound/outbound-audit.jsonl")

class OutboundAuditGate(BaseGate):
    """
    Gate A: Append-only outbound activity audit trail.
    Logs every command/message Javier sends through monitored surfaces.
    No detection, no blocking. Pure baseline capture.
    """
    gate_id = "outbound-audit"
    version = "1.0.0"

    def observe(self):
        """
        Called by pup.py on each cycle. Returns list of Observation objects.
        Reads from a shared queue/pipe that other Djinn components write to.
        This gate is a CONSUMER of events, not a poller.
        """
        return self._drain_queue()

    def _drain_queue(self):
        """Read pending events from the IPC socket and return as Observations."""
        # IPC: Unix domain socket at /run/hellhound/outbound.sock
        # Other Djinn tools write to this socket when Javier acts.
        # This gate drains the queue and wraps each entry as an Observation.
        observations = []
        # Implementation: non-blocking recv loop on self._sock
        # Each message: JSON {"source": "telegram|discord|cli|moonraker",
        #                       "actor": "javier", "content": str,
        #                       "ts": float, "surface": str}
        # Wrap in Observation and return.
        return observations

    def on_observation(self, obs):
        """Write to append-only audit log. Never block. Never fail silently."""
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": obs.timestamp,
            "gate": self.gate_id,
            "source": obs.meta.get("source"),
            "actor": obs.meta.get("actor"),
            "surface": obs.meta.get("surface"),
            "content_hash": obs.meta.get("content_hash"),  # hash, not plaintext
            "raw": obs.payload,
        }
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
```

**IPC injection points (where Djinn tools write to the socket):**
- `djinn-telegram-gateway`: add `_hh_audit(source="telegram", ...)` call before send
- Discord bot: add audit hook in command handler before dispatch
- `hellhound` CLI: wrap `argparse` entrypoint
- Moonraker adapter (forge): wrap gcode post calls

**Log format:** JSONL at `/var/log/hellhound/outbound-audit.jsonl`. Each line: `{"ts": float, "gate": "outbound-audit", "source": str, "actor": str, "surface": str, "content_hash": str, "raw": str}`. Content is hashed (SHA-256 truncated to 16 chars) rather than stored verbatim to avoid logging sensitive command content in cleartext.

**Log rotation:** `logrotate` config at `/etc/logrotate.d/hellhound` — daily, 90-day retention, `compress`, `missingok`.

**AI role:** None at write time. Salomon can invoke Claude or a local model weekly to summarize the JSONL into a human-readable baseline report — input: last 7 days of JSONL, output: `hellhound/reports/YYYY-Www_outbound-baseline.md`. The gate itself never calls any model.

---

### 3. Design: Gate B — Inbound Probe Detection Gate (`InboundProbeGate`)

**Purpose:** Watch exposed network surfaces, detect reconnaissance patterns, auto-block confirmed threats, write incidents, fire Telegram alerts.

**Surfaces watched:**

| Surface | Method | Notes |
|---------|--------|-------|
| Forge dashboard `192.168.1.80:8420` | Tail nginx/uvicorn access log | Currently NO AUTH — flag open |
| Moonraker APIs (Calliope/Nemesis/Iris) | Tail each Moonraker access log | Check `forge/config/` for log paths |
| SSH (`sshd`) | Tail `/var/log/auth.log` or journald | Standard fail2ban territory |
| Discord bot endpoints | Poll bot's request log | HTTP webhook surfaces |

**Detection rules (plain thresholds — no model inference):**

```python
DETECTION_RULES = [
    {
        "id": "rapid-auth-fail",
        "desc": "5+ failed auth attempts from one IP in 60s",
        "surfaces": ["ssh", "forge", "moonraker"],
        "window_sec": 60,
        "threshold": 5,
        "match": "auth_fail",
    },
    {
        "id": "port-scan-signature",
        "desc": "Single IP touching 10+ distinct ports in 30s (iptables LOG)",
        "surfaces": ["network"],
        "window_sec": 30,
        "threshold": 10,
        "match": "port_distinct",
    },
    {
        "id": "new-source-ip-forge",
        "desc": "Request to forge dashboard from IP not seen in last 7 days",
        "surfaces": ["forge"],
        "window_sec": None,  # rolling 7-day known-IP set
        "threshold": 1,
        "match": "unknown_ip",
    },
    {
        "id": "request-rate-spike",
        "desc": "Any single IP sends 60+ requests in 60s to any surface",
        "surfaces": ["forge", "moonraker", "discord"],
        "window_sec": 60,
        "threshold": 60,
        "match": "request_count",
    },
    {
        "id": "ssh-new-user-attempt",
        "desc": "SSH login attempt for username not in allowed list",
        "surfaces": ["ssh"],
        "window_sec": None,
        "threshold": 1,
        "match": "invalid_user",
    },
]
```

**Auto-block mechanism — `ufw` via subprocess (not fail2ban):**

Rationale for ufw over fail2ban: fail2ban requires per-service jail config and regex filter maintenance — more moving parts and another daemon to monitor. Since Salomon already uses ufw as its primary firewall, inserting blocking rules through `ufw` keeps the tool count low and the audit surface small. Rules are logged to `/var/log/hellhound/blocks.jsonl` for reversibility.

```python
import subprocess
import json
from datetime import datetime
from pathlib import Path

BLOCKS_LOG = Path("/var/log/hellhound/blocks.jsonl")

def block_ip(ip: str, reason: str, rule_id: str) -> bool:
    """
    Insert a ufw deny rule for the offending IP.
    Logs the action. Returns True on success.
    Does NOT block 192.168.1.0/24 (LAN) — safeguard.
    """
    if ip.startswith("192.168.1."):  # never auto-block LAN — manual review only
        _log_block(ip, reason, rule_id, blocked=False, note="LAN_SKIP")
        return False

    result = subprocess.run(
        ["ufw", "deny", "from", ip, "to", "any"],
        capture_output=True, text=True, timeout=10
    )
    success = result.returncode == 0
    _log_block(ip, reason, rule_id, blocked=success,
               ufw_output=result.stdout.strip())
    return success

def _log_block(ip, reason, rule_id, blocked, note=None, ufw_output=None):
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "ip": ip,
        "rule_id": rule_id,
        "reason": reason,
        "blocked": blocked,
        "note": note,
        "ufw_output": ufw_output,
    }
    BLOCKS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(BLOCKS_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

**LAN exception — critical:** Never auto-block anything in `192.168.1.0/24`. The entire printer fleet (Calliope/Nemesis/Iris) and Typhon are on this subnet. An erroneous block there takes down the forge. Rule: if detected IP is LAN, write an incident flagged `ALERT_MANUAL` and send Telegram — do not insert ufw rule.

**Incident format** (`hellhound/incidents/YYYY-MM-DD_HH-MM-SS_<rule_id>.md`):

```markdown
---
ts: 2026-07-12T10:45:00Z
rule_id: rapid-auth-fail
ip: 203.0.113.44
surface: ssh
blocked: true
notified: true
---

# Incident: rapid-auth-fail — 2026-07-12 10:45 UTC

**IP:** 203.0.113.44  
**Surface:** SSH  
**Trigger:** 7 failed auth attempts in 42 seconds  
**Action:** ufw deny rule inserted  
**Block log entry:** /var/log/hellhound/blocks.jsonl  

## Raw Events
```
Jul 12 10:44:18 salomon sshd[12345]: Failed password for root from 203.0.113.44 port 54321 ssh2
Jul 12 10:44:21 salomon sshd[12346]: Failed password for admin from 203.0.113.44 port 54322 ssh2
... (7 total)
```

## Notes
*AI summary appended by Claude/Ollama on next report cycle.*
```

**Telegram notification** — follows existing `djinn-telegram-gateway` pattern from the session brief:

```python
import subprocess

def notify_telegram(incident_id: str, rule_id: str, ip: str,
                    surface: str, blocked: bool) -> None:
    """
    Fire Telegram alert via djinn-telegram-gateway.
    djinn-telegram-gateway accepts a message string on stdin or as arg.
    """
    status = "BLOCKED" if blocked else "ALERT — MANUAL ACTION NEEDED"
    msg = (
        f"🐕 Hellhound [{status}]\n"
        f"Rule: {rule_id}\n"
        f"IP: {ip}\n"
        f"Surface: {surface}\n"
        f"Incident: {incident_id}"
    )
    subprocess.run(
        ["djinn-telegram-gateway", "--message", msg],
        timeout=15, check=False  # non-fatal if Telegram is down
    )
```

**Gate class skeleton:**

```python
# hellhound/gates/inbound_probe.py
from collections import defaultdict, deque
from hellhound.gates.base import BaseGate
from hellhound.gates.inbound_probe_rules import DETECTION_RULES
from hellhound.gates.inbound_probe_block import block_ip
from hellhound.gates.inbound_probe_notify import notify_telegram
from hellhound.gates.inbound_probe_incident import write_incident
import re, time

class InboundProbeGate(BaseGate):
    gate_id = "inbound-probe"
    version = "1.0.0"

    def __init__(self, config):
        super().__init__(config)
        self._windows = defaultdict(lambda: deque())  # ip -> deque of (ts, event_type)
        self._known_ips = self._load_known_ips()      # rolling 7-day set from audit log
        self._log_positions = {}                       # file -> byte offset for tailing

    def observe(self):
        """Tail log files, parse new lines, apply detection rules."""
        new_events = self._tail_all_logs()
        triggered = []
        for event in new_events:
            hit = self._apply_rules(event)
            if hit:
                triggered.append((event, hit))
        for event, rule in triggered:
            self._respond(event, rule)
        return []  # InboundProbeGate handles its own output path (incidents/ + Telegram)

    def _tail_all_logs(self):
        """Read new lines from all watched log files since last position."""
        # For each log path in config, seek to last known position,
        # read new lines, update position.
        # Return list of parsed event dicts.
        pass  # implementation: per-surface parsers (ssh, forge, moonraker, discord)

    def _apply_rules(self, event):
        """Check event against all DETECTION_RULES. Return first matching rule or None."""
        ip = event.get("ip")
        if not ip:
            return None
        now = time.time()
        key = (ip, event.get("event_type"))
        self._windows[key].append(now)
        # Purge events outside window
        rule = self._match_rule(event, ip, now)
        return rule

    def _respond(self, event, rule):
        """Block, write incident, notify. In that order."""
        ip = event["ip"]
        blocked = block_ip(ip, rule["desc"], rule["id"])
        incident_id = write_incident(event, rule, blocked)
        notify_telegram(incident_id, rule["id"], ip,
                        event.get("surface"), blocked)
```

---

### 4. Fix: Self-Monitoring — Silent Death Prevention

**Root cause of the 27-day gap:** `pup@gateway.service` uses `Type=simple` (the systemd default). With `Type=simple`, systemd considers the unit "active" the moment it forks the process — it never asks the process to confirm it is still healthy. When the process exited (for any reason), the parent `hellhound.service` had no mechanism to detect the child's death, and `systemctl status hellhound` reported green.

**Fix — identical to the print-safety watchdog fix documented in `djinn/logs/reports/2026-07-11`:**

```ini
# /etc/systemd/system/pup@gateway.service (updated)
[Unit]
Description=Hellhound Pup — %i gate
PartOf=hellhound.service
After=hellhound.service

[Service]
Type=notify
NotifyAccess=main
WatchdogSec=30
Restart=on-failure
RestartSec=10
ExecStart=/opt/hellhound/venv/bin/python /opt/hellhound/pup.py --gate %i
User=hellhound
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pup-%i

[Install]
WantedBy=hellhound.service
```

**Required change to `pup.py`:** The pup process must now call `sd_notify(READY=1)` after startup and `sd_notify(WATCHDOG=1)` on every observe cycle. Python binding: `systemd-python` (`from systemd.daemon import notify`).

```python
# pup.py — additions required
from systemd.daemon import notify as sd_notify

# After gate init and first successful observe():
sd_notify("READY=1")

# In the main observe loop, at top of each cycle:
sd_notify("WATCHDOG=1")
```

**Result:** If `pup.py` hangs or exits without sending `WATCHDOG=1` within 30 seconds, systemd kills and restarts the unit. With `Restart=on-failure`, a crash restarts automatically within 10 seconds. A hang triggers the watchdog timeout and forces a restart. The window of silent death drops from days to ≤60 seconds (30s watchdog timeout + 10s restart delay + 20s margin).

**Additional layer — hellhound-to-pup monitoring:** Add a `watchdog.py` (cortex component) that checks `systemctl is-active pup@gateway.service` every 5 minutes and writes to `hellhound/timeline/` if state changes. This gives the timeline log the coverage it currently lacks and ensures the file record reflects real service state, not just what systemd reports.

```python
# hellhound/cortex/watchdog.py — add to existing skeleton
import subprocess
from datetime import datetime
from pathlib import Path

TIMELINE_DIR = Path("/home/javier/Obsidian/hellhound/timeline")

def check_pup_health(gate_name: str = "gateway") -> str:
    result = subprocess.run(
        ["systemctl", "is-active", f"pup@{gate_name}.service"],
        capture_output=True, text=True
    )
    return result.stdout.strip()  # "active", "inactive", "failed"

def write_timeline_entry(gate_name: str, state: str) -> None:
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    path = TIMELINE_DIR / f"{ts}_pup-{gate_name}-{state}.md"
    path.write_text(
        f"---\nts: {datetime.utcnow().isoformat()}\ngate: {gate_name}\nstate: {state}\n---\n\n"
        f"# Timeline: pup@{gate_name} state = {state}\n\n"
        f"Recorded by watchdog.py at {datetime.utcnow().isoformat()}Z\n"
    )
```

---

### 5. Naming Collision — `hellhound/gates/` vs `djinn-gateway`

**The collision:**

| Name | Location | What it is |
|------|----------|------------|
| `hellhound/gates/` | Vault path `hellhound/gates/` | Adapter pattern — BaseGate subclasses. Security monitoring interfaces. Python classes. |
| `djinn-gateway` | `~/.local/bin/djinn-gateway` | Push-checkpoint CLI tool. Fires on every git commit. Has zero connection to security monitoring. |

These share the word "gateway/gates" with **zero semantic relationship**. The `djinn-gateway` script predates Hellhound. The naming will cause confusion for every agent that reads `djinn/GATEWAY.md` and then navigates `hellhound/gates/` expecting to find the same concept.

**Recommendation: rename `djinn-gateway` → `djinn-checkpoint`.**

Rationale:
- `djinn-checkpoint` accurately describes its function: checkpoint the vault state to git on each commit cycle. "Gateway" implies routing or entry control, which is not what it does.
- `hellhound/gates/` owns the "gate" semantic in this system: it is the entry point pattern for monitoring adapters. That meaning should be unambiguous.
- The rename is a CLI alias change (`~/.local/bin/djinn-checkpoint`) + a sed pass over any scripts that call `djinn-gateway` directly + a `djinn/GATEWAY.md` note.
- **Do not rename `hellhound/gates/`** — the adapter pattern name is correct, standard (cf. Adapter/Port pattern in architecture), and renaming it would require touching all subclass imports.

**Migration steps (Salomon executes):**
```bash
cp ~/.local/bin/djinn-gateway ~/.local/bin/djinn-checkpoint
chmod +x ~/.local/bin/djinn-checkpoint
# Update any hook scripts that call djinn-gateway:
grep -r "djinn-gateway" ~/.local/bin/ ~/Obsidian/ --include="*.sh" --include="*.py" -l
# Sed replace in each found file, then commit
# Keep djinn-gateway as a symlink for 30 days for backward compat:
ln -sf ~/.local/bin/djinn-checkpoint ~/.local/bin/djinn-gateway
# After 30 days, remove symlink
```

---

## Recommendations

**For Claude (architecture + implementation):**

1. **Do not restart `pup@gateway.service` until a real gate exists.** Restarting the stub restores nothing useful. Gate B (`InboundProbeGate`) is the priority — it addresses the open Forge dashboard and SSH surfaces.
2. **Implement `InboundProbeGate` first.** The Forge dashboard at `192.168.1.80:8420` has no auth and is the highest-risk surface per the task context. This gate is the first real security value Hellhound delivers.
3. **Create `hellhound/incidents/` and `hellhound/reports/` as directories** with `.gitkeep` files so the paths exist in the repo. Right now they are missing entirely.
4. **Apply the `Type=notify` + `WatchdogSec=30` fix to `pup@gateway.service`** before starting any real gate. A real gate that can die silently is not better than a stub that dies silently.
5. **Implement `OutboundAuditGate` second** — lower urgency than inbound probe detection, but needed to establish Javier's baseline before any anomaly detection can compare against normal.
6. **Rename `djinn-gateway` → `djinn-checkpoint`** — low effort, high clarity. Salomon can handle this in a single commit.
7. **Wire Telegram notification** — the `djinn-telegram-gateway` pattern is already established. The notify function above is ready to use; just confirm the CLI interface matches the existing implementation.

**For Javier (decisions needed):**

- **Forge dashboard auth:** `192.168.1.80:8420` has no authentication. Even on LAN, this is a real risk — any compromised device on the LAN gets full forge control. Recommend adding HTTP basic auth or token auth before relying on Hellhound to be the only protection. Hellhound monitors; it is not a substitute for auth. This is a separate task but should be flagged.
- **Known-IP allowlist for InboundProbeGate:** The `new-source-ip-forge` rule needs a seed list of trusted IPs (Javier's devices, Typhon, the printer fleet). This cannot be auto-generated — Javier needs to confirm which IPs are always expected. Recommend creating `hellhound/config/trusted-ips.txt`.
- **LAN alert behavior:** Current design sends Telegram but does NOT auto-block LAN IPs. Confirm this is acceptable — if a LAN device is probing forge, it may be a compromised printer, and manual review is appropriate.

---

## Vault Gaps Identified

- `hellhound/incidents/` — **does not exist**. Create with `.gitkeep`.
- `hellhound/reports/` — **does not exist**. Create with `.gitkeep`.
- `hellhound/config/` — no config directory found. Should contain `trusted-ips.txt`, gate config YAML.
- `djinn/logs/reports/2026-07-11_forge-dashboard-build.md` — referenced in task brief as explaining why Forge has no auth. Not read this session. Claude should confirm its contents before implementing InboundProbeGate log tailing paths.
- `djinn/machines/` — not read this session. Needed for Calliope/Nemesis/Iris Moonraker log paths. Claude must read before wiring Moonraker surface tailing.
- `djinn/GATEWAY.md` — not fully re-read this session (tool budget). Assumed consistent with task brief description. Claude should confirm path tree section.

---

## Sources

- Vault: `hellhound/` directory structure (read 2026-07-12)
- Vault: `ai/marcus/MARCUS-SESSION-BRIEF.md` (session orientation)
- Task brief: TASK-081 as delivered in Perplexity session by Javier (2026-07-12)
- systemd `Type=notify` + `WatchdogSec` pattern: per vault precedent in `djinn/logs/reports/2026-07-11` (print-safety watchdog fix, same pattern)
- Architecture precedent: Adapter/Port pattern (Gang of Four); BaseGate as abstract port, concrete gates as adapters
- ufw vs fail2ban rationale: fewer daemons, lower maintenance surface, consistent with Salomon's existing firewall posture

— Marcus, 2026-07-12
