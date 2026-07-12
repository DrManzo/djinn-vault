---
ts: 2026-07-12T15:16:19.267761+00:00
rule_id: ssh-new-user-attempt
ip: 192.168.1.154
surface: ssh
blocked: true
notified: true
---

# Incident: ssh-new-user-attempt — 2026-07-12 15:16 UTC

**IP:** 192.168.1.154  
**Surface:** ssh  
**Trigger:** SSH login attempt for unknown username  
**Action:** ufw deny inserted  
**Block note:** Rule added  

## Event

```json
{
  "ip": "192.168.1.154",
  "surface": "ssh",
  "event_type": "invalid_user",
  "raw_lines": [
    "Invalid user javier from 192.168.1.154 port 40128"
  ]
}
```

## Raw Events

```text
Invalid user javier from 192.168.1.154 port 40128
```

## Notes

AI summary may be appended later by a separate report step. Detection, blocking, and notification are deterministic only.
