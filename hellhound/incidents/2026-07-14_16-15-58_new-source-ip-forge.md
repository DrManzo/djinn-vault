---
ts: 2026-07-14T16:15:58.345890+00:00
rule_id: new-source-ip-forge
ip: 127.0.0.1
surface: forge
blocked: true
notified: true
---

# Incident: new-source-ip-forge — 2026-07-14 16:15 UTC

**IP:** 127.0.0.1  
**Surface:** forge  
**Trigger:** Request to forge dashboard from source IP not in trusted list  
**Action:** ufw deny inserted  
**Block note:** Rule added  

## Event

```json
{
  "ip": "127.0.0.1",
  "surface": "forge",
  "event_type": "request",
  "raw_lines": [
    "127.0.0.1 - - [14/Jul/2026 09:15:57] \"POST /login HTTP/1.1\" 200 -"
  ]
}
```

## Raw Events

```text
127.0.0.1 - - [14/Jul/2026 09:15:57] "POST /login HTTP/1.1" 200 -
```

## Notes

AI summary may be appended later by a separate report step. Detection, blocking, and notification are deterministic only.
