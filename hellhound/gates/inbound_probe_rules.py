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
        "window_sec": 3600,
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
