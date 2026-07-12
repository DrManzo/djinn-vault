from __future__ import annotations

import ipaddress
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

LOG_DIR = Path.home() / ".local/share/hellhound/logs"
BLOCK_LOG = LOG_DIR / "blocks.jsonl"

LAN_NETWORK = ipaddress.ip_network("192.168.1.0/24")


def _is_lan_ip(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip) in LAN_NETWORK
    except ValueError:
        return False


def _append_log(entry: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with BLOCK_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def block_ip(ip: str, rule_id: str, reason: str, allow_lan_block: bool) -> Tuple[bool, str]:
    """
    Insert a ufw deny rule for the offending IP via passwordless sudo.
    Never blocks 192.168.1.0/24 unless the rule explicitly allows it
    (rapid-auth-fail, port-scan-signature, ssh-new-user-attempt only —
    see inbound_probe_rules.py). Logs every decision, blocked or not.
    """
    lan = _is_lan_ip(ip)
    if lan and not allow_lan_block:
        _append_log({
            "ts": datetime.now(timezone.utc).isoformat(),
            "ip": ip,
            "rule_id": rule_id,
            "reason": reason,
            "blocked": False,
            "note": "LAN_SKIP",
        })
        return False, "LAN_SKIP"

    cmd = ["sudo", "-n", "ufw", "deny", "from", ip, "to", "any"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = (proc.stdout or proc.stderr or "").strip()
        blocked = proc.returncode == 0
    except (subprocess.TimeoutExpired, OSError) as exc:
        output = str(exc)
        blocked = False

    _append_log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "ip": ip,
        "rule_id": rule_id,
        "reason": reason,
        "blocked": blocked,
        "note": output,
    })
    return blocked, output
