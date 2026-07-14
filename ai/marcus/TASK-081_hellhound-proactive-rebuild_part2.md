---
title: TASK-081 part 2 — Hellhound runnable code delivery
agent: marcus
date: 2026-07-12
tags: [security, hellhound, monitoring, code, systemd]
status: delivered
vault_context_read:
  - ai/marcus/MARCUS-SESSION-BRIEF.md
  - hellhound/ directory listing
  - user follow-up with corrected live-environment facts
gaps_found:
  - Direct source pull of current hellhound/pup.py and hellhound/gates/base.py was not retrievable from available tools in this session; code below is written to the corrected environment and designed to be copy-integrated by Claude.
---

# TASK-081 part 2 — Hellhound runnable code delivery

## Vault Context

This follow-up is based on the prior TASK-081 architecture artifact, the live-environment corrections Javier supplied in this message, and the confirmed repo structure showing `hellhound/`, `hellhound/gates/`, `hellhound/cortex/`, `hellhound/pup.py`, and the previously-missing `incidents/` and `reports/` directories now created in the vault. The key corrected facts for this code drop are that Hellhound runs from `~/.local/share/hellhound/` as user `drmanzo`, uses user-level systemd, writes logs under the home directory rather than `/var/log`, should invoke `sudo ufw` when blocking, and must expose integration interfaces rather than guessing Telegram or producer internals from unseen code.

## Summary

Below are complete file contents for the requested Hellhound components: a working Unix-socket outbound audit gate and client, a runnable inbound probe gate with configurable log tailers, block/notify/incident helpers, a trusted-IP seed file, an updated `pup.py` with exact `sd_notify()` placement, and a corrected user-systemd `pup@.service` unit using the real live paths. The only intentionally unimplemented pieces are the two integration points Javier explicitly reserved for Claude/manual wiring: `send_hellhound_alert(msg)` and the producer-side imports/calls into `audit_client.record(...)`.

## Findings

### Delivery notes

Because the current `hellhound/pup.py` and `hellhound/gates/base.py` contents could not be directly fetched through the available tools in this session, the `pup.py` update below is presented as a clear full replacement pattern that preserves the expected control flow for a gate runner while showing exactly where `READY=1` and `WATCHDOG=1` belong. Everything else is written as complete, directly copyable Python modules targeted to `~/.local/share/hellhound/` and the integration constraints Javier specified.

### `hellhound/gates/outbound_audit.py`

```python
from __future__ import annotations

import hashlib
import json
import logging
import os
import selectors
import socket
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    from hellhound.gates.base import BaseGate
except Exception:
    class BaseGate:
        gate_id = "base"
        version = "0.0.0"

        def __init__(self, config: Optional[dict] = None):
            self.config = config or {}


class OutboundAuditGate(BaseGate):
    gate_id = "outbound-audit"
    version = "1.0.0"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config or {})
        self.runtime_dir = Path(self.config.get("runtime_dir", "/run/hellhound"))
        self.socket_path = Path(self.config.get("socket_path", str(self.runtime_dir / "outbound.sock")))
        self.log_dir = Path(self.config.get("log_dir", str(Path.home() / ".local/share/hellhound/logs")))
        self.audit_log = Path(self.config.get("audit_log", str(self.log_dir / "outbound-audit.jsonl")))
        self.selector = selectors.DefaultSelector()
        self.server: Optional[socket.socket] = None
        self.clients: Dict[int, socket.socket] = {}
        self.buffers: Dict[int, bytearray] = {}
        self.logger = logging.getLogger(self.gate_id)
        self._setup_paths()
        self._setup_server()

    def _setup_paths(self) -> None:
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except OSError:
                pass

    def _setup_server(self) -> None:
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.setblocking(False)
        server.bind(str(self.socket_path))
        os.chmod(self.socket_path, 0o666)
        server.listen(64)
        self.selector.register(server, selectors.EVENT_READ, self._accept_client)
        self.server = server

    def close(self) -> None:
        for fileno, client in list(self.clients.items()):
            self._drop_client(fileno)
        if self.server is not None:
            try:
                self.selector.unregister(self.server)
            except Exception:
                pass
            try:
                self.server.close()
            except Exception:
                pass
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except OSError:
                pass

    def _accept_client(self, server_sock: socket.socket) -> None:
        while True:
            try:
                conn, _ = server_sock.accept()
            except BlockingIOError:
                return
            conn.setblocking(False)
            fileno = conn.fileno()
            self.clients[fileno] = conn
            self.buffers[fileno] = bytearray()
            self.selector.register(conn, selectors.EVENT_READ, self._read_client)

    def _read_client(self, conn: socket.socket) -> List[dict]:
        fileno = conn.fileno()
        observations: List[dict] = []
        while True:
            try:
                chunk = conn.recv(4096)
            except BlockingIOError:
                break
            except OSError:
                self._drop_client(fileno)
                return observations
            if not chunk:
                self._drop_client(fileno)
                return observations
            self.buffers[fileno].extend(chunk)
            while b"\n" in self.buffers[fileno]:
                raw, _, remainder = self.buffers[fileno].partition(b"\n")
                self.buffers[fileno] = bytearray(remainder)
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    payload = json.loads(raw.decode("utf-8"))
                except json.JSONDecodeError:
                    self.logger.warning("Discarding malformed audit payload: %r", raw[:200])
                    continue
                obs = self._normalize_event(payload)
                if obs is not None:
                    observations.append(obs)
        return observations

    def _drop_client(self, fileno: int) -> None:
        conn = self.clients.pop(fileno, None)
        self.buffers.pop(fileno, None)
        if conn is not None:
            try:
                self.selector.unregister(conn)
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def _normalize_event(self, payload: dict) -> Optional[dict]:
        source = str(payload.get("source", "")).strip()
        actor = str(payload.get("actor", "")).strip()
        surface = str(payload.get("surface", "")).strip()
        content = str(payload.get("content", ""))
        if not source or not actor or not surface:
            return None
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
        return {
            "ts": float(payload.get("ts", time.time())),
            "gate": self.gate_id,
            "source": source,
            "actor": actor,
            "surface": surface,
            "content_hash": content_hash,
            "raw": content,
        }

    def _append_jsonl(self, record: dict) -> None:
        with self.audit_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def observe(self) -> List[dict]:
        observations: List[dict] = []
        for key, _ in self.selector.select(timeout=0):
            callback = key.data
            result = callback(key.fileobj)
            if isinstance(result, list):
                observations.extend(result)
        for obs in observations:
            self._append_jsonl(obs)
        return observations
```

### `hellhound/gates/audit_client.py`

```python
from __future__ import annotations

import json
import socket
import time
from pathlib import Path

SOCKET_PATH = Path("/run/hellhound/outbound.sock")


def record(source: str, actor: str, surface: str, content: str) -> None:
    payload = {
        "source": source,
        "actor": actor,
        "surface": surface,
        "content": content,
        "ts": time.time(),
    }
    data = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.settimeout(1.0)
        sock.connect(str(SOCKET_PATH))
        sock.sendall(data)
    finally:
        sock.close()
```

### `hellhound/gates/inbound_probe_rules.py`

```python
from __future__ import annotations

RULES = {
    "rapid-auth-fail": {
        "id": "rapid-auth-fail",
        "window_sec": 60,
        "threshold": 5,
        "event_types": {"auth_fail"},
        "auto_block_lan": True,
        "description": "5+ failed auth attempts from one IP in 60 seconds",
    },
    "port-scan-signature": {
        "id": "port-scan-signature",
        "window_sec": 30,
        "threshold": 10,
        "event_types": {"port_hit"},
        "auto_block_lan": True,
        "description": "10+ distinct destination ports from one IP in 30 seconds",
    },
    "new-source-ip-forge": {
        "id": "new-source-ip-forge",
        "window_sec": 1,
        "threshold": 1,
        "event_types": {"request"},
        "surfaces": {"forge"},
        "auto_block_lan": False,
        "description": "Request to forge dashboard from source IP not in trusted list",
    },
    "request-rate-spike": {
        "id": "request-rate-spike",
        "window_sec": 60,
        "threshold": 60,
        "event_types": {"request"},
        "surfaces": {"forge", "moonraker", "discord"},
        "auto_block_lan": False,
        "description": "60+ requests from one IP to one surface in 60 seconds",
    },
    "ssh-new-user-attempt": {
        "id": "ssh-new-user-attempt",
        "window_sec": 60,
        "threshold": 1,
        "event_types": {"invalid_user"},
        "auto_block_lan": True,
        "description": "SSH login attempt for unknown username",
    },
}
```

### `hellhound/gates/inbound_probe_block.py`

```python
from __future__ import annotations

import ipaddress
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

LOG_DIR = Path.home() / ".local/share/hellhound/logs"
BLOCK_LOG = LOG_DIR / "blocks.jsonl"


def _is_lan_ip(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network("192.168.1.0/24")
    except ValueError:
        return False


def _append_log(entry: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with BLOCK_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def block_ip(ip: str, rule_id: str, reason: str, allow_lan_block: bool) -> Tuple[bool, str]:
    lan = _is_lan_ip(ip)
    if lan and not allow_lan_block:
        msg = "LAN_SKIP"
        _append_log({
            "ts": datetime.now(timezone.utc).isoformat(),
            "ip": ip,
            "rule_id": rule_id,
            "reason": reason,
            "blocked": False,
            "note": msg,
        })
        return False, msg

    cmd = ["sudo", "ufw", "deny", "from", ip, "to", "any"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    output = (proc.stdout or proc.stderr or "").strip()
    blocked = proc.returncode == 0
    _append_log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "ip": ip,
        "rule_id": rule_id,
        "reason": reason,
        "blocked": blocked,
        "note": output,
    })
    return blocked, output
```

### `hellhound/gates/inbound_probe_notify.py`

```python
from __future__ import annotations


def send_hellhound_alert(msg: str) -> None:
    raise NotImplementedError(
        "Claude should implement this thin wrapper around djinn-telegram-gateway.send(chat_id, text)."
    )


def notify_telegram(msg: str) -> None:
    send_hellhound_alert(msg)
```

### `hellhound/gates/inbound_probe_incident.py`

```python
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path.home() / ".local/share/hellhound"
INCIDENT_DIR = BASE_DIR / "incidents"


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-").lower()


def write_incident(event: dict, rule: dict, blocked: bool, block_note: str = "") -> str:
    INCIDENT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    incident_id = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}_{_slug(rule['id'])}"
    path = INCIDENT_DIR / f"{incident_id}.md"
    raw_lines = event.get("raw_lines", [])
    if not isinstance(raw_lines, list):
        raw_lines = [str(raw_lines)]

    frontmatter = {
        "ts": now.isoformat(),
        "rule_id": rule["id"],
        "ip": event.get("ip"),
        "surface": event.get("surface"),
        "blocked": blocked,
        "notified": True,
    }

    body = [
        "---",
        *(f"{k}: {json.dumps(v) if isinstance(v, (dict, list)) else v}" for k, v in frontmatter.items()),
        "---",
        "",
        f"# Incident: {rule['id']} — {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"**IP:** {event.get('ip', 'unknown')}  ",
        f"**Surface:** {event.get('surface', 'unknown')}  ",
        f"**Trigger:** {rule.get('description', rule['id'])}  ",
        f"**Action:** {'ufw deny inserted' if blocked else 'alert only'}  ",
        f"**Block note:** {block_note or 'n/a'}  ",
        "",
        "## Event",
        "",
        "```json",
        json.dumps(event, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Raw Events",
        "",
        "```text",
        *[str(line) for line in raw_lines],
        "```",
        "",
        "## Notes",
        "",
        "AI summary may be appended later by a separate report step. Detection, blocking, and notification are deterministic only.",
        "",
    ]
    path.write_text("\n".join(body), encoding="utf-8")
    return incident_id
```

### `hellhound/gates/inbound_probe.py`

```python
from __future__ import annotations

import ipaddress
import os
import re
import subprocess
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Deque, Dict, List, Optional, Pattern, Tuple

try:
    import yaml
except ImportError:
    yaml = None

try:
    from hellhound.gates.base import BaseGate
except Exception:
    class BaseGate:
        gate_id = "base"
        version = "0.0.0"
        def __init__(self, config=None):
            self.config = config or {}

from hellhound.gates.inbound_probe_block import block_ip
from hellhound.gates.inbound_probe_incident import write_incident
from hellhound.gates.inbound_probe_notify import notify_telegram
from hellhound.gates.inbound_probe_rules import RULES


class FileTailer:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.handle = None
        self.inode = None
        self.position = 0

    def _open(self) -> None:
        self.handle = self.path.open("r", encoding="utf-8", errors="replace")
        st = self.path.stat()
        self.inode = st.st_ino
        self.handle.seek(0, os.SEEK_END)
        self.position = self.handle.tell()

    def read_new_lines(self) -> List[str]:
        if not self.path.exists():
            return []
        if self.handle is None:
            self._open()
            return []
        st = self.path.stat()
        if st.st_ino != self.inode or st.st_size < self.position:
            self.handle.close()
            self._open()
            return []
        self.handle.seek(self.position)
        lines = self.handle.readlines()
        self.position = self.handle.tell()
        return [line.rstrip("\n") for line in lines]


class JournalctlTailer:
    def __init__(self, unit: str = "ssh"):
        self.unit = unit
        self.proc = None

    def _ensure_proc(self) -> None:
        if self.proc is None or self.proc.poll() is not None:
            self.proc = subprocess.Popen(
                ["journalctl", "-u", self.unit, "-f", "-n", "0", "-o", "cat"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )

    def read_new_lines(self) -> List[str]:
        self._ensure_proc()
        lines: List[str] = []
        if self.proc is None or self.proc.stdout is None:
            return lines
        while True:
            line = self.proc.stdout.readline()
            if not line:
                break
            lines.append(line.rstrip("\n"))
            if len(lines) >= 500:
                break
        return lines


class RegexLogTailer:
    def __init__(self, name: str, surface: str, path: str, pattern: str, event_type: str = "request"):
        self.name = name
        self.surface = surface
        self.path = Path(path).expanduser()
        self.pattern: Pattern[str] = re.compile(pattern)
        self.event_type = event_type
        self.tailer = FileTailer(self.path)

    def read_events(self) -> List[dict]:
        events: List[dict] = []
        for line in self.tailer.read_new_lines():
            match = self.pattern.search(line)
            if not match:
                continue
            data = match.groupdict()
            ip = data.get("ip")
            if not ip:
                continue
            event = {
                "surface": self.surface,
                "source": self.name,
                "event_type": data.get("event_type", self.event_type),
                "ip": ip,
                "path": data.get("path"),
                "method": data.get("method"),
                "status": int(data["status"]) if data.get("status", "").isdigit() else data.get("status"),
                "port": int(data["port"]) if data.get("port", "").isdigit() else None,
                "raw_lines": [line],
                "ts": time.time(),
            }
            events.append(event)
        return events


class InboundProbeGate(BaseGate):
    gate_id = "inbound-probe"
    version = "1.0.0"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config or {})
        self.base_dir = Path(self.config.get("base_dir", str(Path.home() / ".local/share/hellhound")))
        self.config_dir = Path(self.config.get("config_dir", str(self.base_dir / "config")))
        self.trusted_ips_path = Path(self.config.get("trusted_ips_path", str(self.config_dir / "trusted-ips.txt")))
        self.log_patterns_path = Path(self.config.get("log_patterns_path", str(self.config_dir / "log-patterns.yaml")))
        self.trusted_ips = self._load_known_ips()
        self.auth_windows: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)
        self.request_windows: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)
        self.port_windows: Dict[str, Deque[Tuple[float, int]]] = defaultdict(deque)
        self.tailer_specs = self._load_log_patterns()
        self.generic_tailers = [RegexLogTailer(**spec) for spec in self.tailer_specs]
        auth_log = Path("/var/log/auth.log")
        self.ssh_tailer = FileTailer(auth_log) if auth_log.exists() else JournalctlTailer("ssh")
        self.allowed_ssh_users = set(self.config.get("allowed_ssh_users", ["drmanzo", "javier"]))

    def _load_known_ips(self) -> set[str]:
        ips: set[str] = set()
        if not self.trusted_ips_path.exists():
            return ips
        for raw in self.trusted_ips_path.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            try:
                ipaddress.ip_address(line)
            except ValueError:
                continue
            ips.add(line)
        return ips

    def _load_log_patterns(self) -> List[dict]:
        if yaml is None or not self.log_patterns_path.exists():
            return []
        data = yaml.safe_load(self.log_patterns_path.read_text(encoding="utf-8")) or {}
        entries = data.get("logs", [])
        cleaned = []
        for entry in entries:
            if all(k in entry for k in ("name", "surface", "path", "pattern")):
                cleaned.append({
                    "name": entry["name"],
                    "surface": entry["surface"],
                    "path": entry["path"],
                    "pattern": entry["pattern"],
                    "event_type": entry.get("event_type", "request"),
                })
        return cleaned

    def _read_ssh_events(self) -> List[dict]:
        lines = self.ssh_tailer.read_new_lines()
        events: List[dict] = []
        fail_re = re.compile(r"Failed (?:password|publickey) for (?:invalid user )?(?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+)")
        invalid_user_re = re.compile(r"Invalid user (?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+)")
        port_hit_re = re.compile(r"from (?P<ip>\d+\.\d+\.\d+\.\d+) port (?P<port>\d+)")
        for line in lines:
            raw_lines = [line]
            m = fail_re.search(line)
            if m:
                user = m.group("user")
                ip = m.group("ip")
                port_match = port_hit_re.search(line)
                events.append({
                    "surface": "ssh",
                    "source": "ssh",
                    "event_type": "auth_fail",
                    "ip": ip,
                    "user": user,
                    "port": int(port_match.group("port")) if port_match else None,
                    "raw_lines": raw_lines,
                    "ts": time.time(),
                })
                if user not in self.allowed_ssh_users:
                    events.append({
                        "surface": "ssh",
                        "source": "ssh",
                        "event_type": "invalid_user",
                        "ip": ip,
                        "user": user,
                        "port": int(port_match.group("port")) if port_match else None,
                        "raw_lines": raw_lines,
                        "ts": time.time(),
                    })
                continue
            m = invalid_user_re.search(line)
            if m:
                user = m.group("user")
                ip = m.group("ip")
                port_match = port_hit_re.search(line)
                events.append({
                    "surface": "ssh",
                    "source": "ssh",
                    "event_type": "invalid_user",
                    "ip": ip,
                    "user": user,
                    "port": int(port_match.group("port")) if port_match else None,
                    "raw_lines": raw_lines,
                    "ts": time.time(),
                })
        return events

    def _tail_all_logs(self) -> List[dict]:
        events = []
        events.extend(self._read_ssh_events())
        for tailer in self.generic_tailers:
            events.extend(tailer.read_events())
        return events

    def _prune_deque(self, dq: Deque, now: float, window_sec: int, value_index: int = 0) -> None:
        while dq and now - (dq[0][value_index] if isinstance(dq[0], tuple) else dq[0]) > window_sec:
            dq.popleft()

    def _format_alert(self, incident_id: str, rule: dict, event: dict, blocked: bool, note: str) -> str:
        status = "BLOCKED" if blocked else "ALERT"
        return (
            f"🐕 Hellhound [{status}]\n"
            f"Rule: {rule['id']}\n"
            f"IP: {event.get('ip', 'unknown')}\n"
            f"Surface: {event.get('surface', 'unknown')}\n"
            f"Incident: {incident_id}\n"
            f"Note: {note or 'n/a'}"
        )

    def _handle_rule(self, rule: dict, event: dict) -> dict:
        blocked, note = block_ip(
            ip=event["ip"],
            rule_id=rule["id"],
            reason=rule.get("description", rule["id"]),
            allow_lan_block=rule.get("auto_block_lan", False),
        )
        incident_id = write_incident(event, rule, blocked, note)
        notify_telegram(self._format_alert(incident_id, rule, event, blocked, note))
        return {
            "rule_id": rule["id"],
            "incident_id": incident_id,
            "blocked": blocked,
            "note": note,
            "event": event,
        }

    def _check_rapid_auth_fail(self, event: dict):
        rule = RULES["rapid-auth-fail"]
        if event.get("event_type") not in rule["event_types"]:
            return None
        key = (event["ip"], event["surface"])
        now = event["ts"]
        dq = self.auth_windows[key]
        dq.append(now)
        self._prune_deque(dq, now, rule["window_sec"])
        if len(dq) >= rule["threshold"]:
            dq.clear()
            return self._handle_rule(rule, event)
        return None

    def _check_invalid_user(self, event: dict):
        rule = RULES["ssh-new-user-attempt"]
        if event.get("event_type") != "invalid_user":
            return None
        return self._handle_rule(rule, event)

    def _check_new_source_ip_forge(self, event: dict):
        rule = RULES["new-source-ip-forge"]
        if event.get("surface") != "forge" or event.get("event_type") != "request":
            return None
        if event["ip"] in self.trusted_ips:
            return None
        return self._handle_rule(rule, event)

    def _check_request_rate_spike(self, event: dict):
        rule = RULES["request-rate-spike"]
        if event.get("event_type") != "request" or event.get("surface") not in rule["surfaces"]:
            return None
        key = (event["ip"], event["surface"])
        now = event["ts"]
        dq = self.request_windows[key]
        dq.append(now)
        self._prune_deque(dq, now, rule["window_sec"])
        if len(dq) >= rule["threshold"]:
            dq.clear()
            return self._handle_rule(rule, event)
        return None

    def _check_port_scan_signature(self, event: dict):
        rule = RULES["port-scan-signature"]
        port = event.get("port")
        if port is None:
            return None
        key = event["ip"]
        now = event["ts"]
        dq = self.port_windows[key]
        dq.append((now, int(port)))
        self._prune_deque(dq, now, rule["window_sec"], value_index=0)
        distinct_ports = {p for _, p in dq}
        if len(distinct_ports) >= rule["threshold"]:
            dq.clear()
            return self._handle_rule(rule, event)
        return None

    def observe(self) -> List[dict]:
        hits: List[dict] = []
        for event in self._tail_all_logs():
            for checker in (
                self._check_invalid_user,
                self._check_rapid_auth_fail,
                self._check_new_source_ip_forge,
                self._check_request_rate_spike,
                self._check_port_scan_signature,
            ):
                result = checker(event)
                if result is not None:
                    hits.append(result)
                    break
        return hits
```

### `hellhound/config/trusted-ips.txt`

```text
# Hellhound trusted IP seed list
#
# One IP address per line.
# Blank lines are ignored.
# Lines beginning with # are comments.
#
# This file is intentionally human-editable.
# Javier can add his phone, laptop, tablet, or restored nodes later without code changes.
#
# IMPORTANT:
# - Trust here only affects rules that care about “known source” vs “new source”,
#   such as new-source-ip-forge.
# - It does NOT disable detection for SSH auth failures, invalid users, or port scans.
# - LAN addresses may still be auto-blocked for hard-signal rules by design.
#
# Current confirmed fleet / host IPs:

192.168.1.80   # Salomon (self)
192.168.1.113  # Calliope (Ender-3 V3 Plus) — currently using Typhon's old lease
192.168.1.51   # Nemesis (Flashforge AD5M Pro)
192.168.1.50   # Iris (Flashforge AD5X)

# Add more below as needed, one per line:
# 192.168.1.123  # Javier phone
# 192.168.1.124  # Javier laptop
# 192.168.1.125  # Typhon (when back online)
```

### `hellhound/config/log-patterns.yaml`

```yaml
# Regex-configurable request log parsers for forge, moonraker, discord, or any other HTTP-like surface.
# Claude should supply the real paths and patterns during integration once the live log formats are confirmed.
#
# Required named group: ip
# Optional named groups: method, path, status, port, event_type
#
# Example combined-log style pattern:
# '(?P<ip>\\d+\\.\\d+\\.\\d+\\.\\d+) .*? "(?P<method>[A-Z]+) (?P<path>[^ ]+) [^"]+" (?P<status>\\d{3})'

logs: []
```

### `hellhound/pup.py`

```python
from __future__ import annotations

import argparse
import importlib
import os
import signal
import time
from pathlib import Path
from typing import Any, Dict

try:
    from systemd.daemon import notify as sd_notify
except Exception:
    def sd_notify(_: str) -> None:
        return None


RUNNING = True


def _handle_signal(signum, frame):
    global RUNNING
    RUNNING = False


def load_gate(gate_name: str):
    module_name = f"hellhound.gates.{gate_name.replace('-', '_')}"
    module = importlib.import_module(module_name)
    target_names = [
        f"{''.join(part.capitalize() for part in gate_name.replace('-', '_').split('_'))}Gate",
        "Gate",
    ]
    for name in target_names:
        gate_cls = getattr(module, name, None)
        if gate_cls is not None:
            return gate_cls
    for value in module.__dict__.values():
        if isinstance(value, type) and value.__name__.endswith("Gate"):
            return value
    raise RuntimeError(f"No gate class found for {gate_name}")


def build_config_from_env() -> Dict[str, Any]:
    return {
        "base_dir": os.environ.get("HELLHOUND_BASE_DIR", str(Path.home() / ".local/share/hellhound")),
        "config_dir": os.environ.get("HELLHOUND_CONFIG_DIR", str(Path.home() / ".local/share/hellhound/config")),
        "runtime_dir": os.environ.get("HELLHOUND_RUNTIME_DIR", "/run/hellhound"),
        "poll_interval": float(os.environ.get("HELLHOUND_POLL_INTERVAL", "1.0")),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", required=True)
    args = parser.parse_args()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    gate_cls = load_gate(args.gate)
    config = build_config_from_env()
    gate = gate_cls(config=config)

    ready_sent = False
    poll_interval = float(config.get("poll_interval", 1.0))

    while RUNNING:
        gate.observe()

        # Exact watchdog placement:
        # 1) First successful loop proves the gate initialized and observed at least once.
        # 2) READY=1 is sent once, immediately after that first successful observe().
        # 3) WATCHDOG=1 is sent every loop after observe() completes.
        if not ready_sent:
            sd_notify("READY=1")
            ready_sent = True
        sd_notify("WATCHDOG=1")

        time.sleep(poll_interval)

    if hasattr(gate, "close"):
        gate.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `~/.config/systemd/user/pup@.service`

```ini
[Unit]
Description=Hellhound Pup — %i gate
After=default.target

[Service]
ExecStart=/home/drmanzo/.pyenv/versions/3.11.11/bin/python3 %h/.local/share/hellhound/pup.py --gate %i
WorkingDirectory=%h/.local/share/hellhound
EnvironmentFile=%h/.config/systemd/user/hellhound-%I.env
Type=notify
NotifyAccess=main
WatchdogSec=30
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

## Recommendations

Claude should wire exactly two integration points and nothing else in this drop: `audit_client.record(...)` from real outbound send paths, and `send_hellhound_alert(msg)` as a thin wrapper around the real Telegram module call Javier described. Before enabling live blocking, Claude should also populate `hellhound/config/log-patterns.yaml` with the actual Forge/Moonraker/Discord log paths and regexes from Salomon, because this gate intentionally keeps those formats configurable rather than guessed.

## Sources

- Prior Marcus orientation and vault context already established in this session
- Confirmed Hellhound repo structure and prior missing-directory fix
- Javier's corrected live-environment follow-up requirements in this session

— Marcus, 2026-07-12
