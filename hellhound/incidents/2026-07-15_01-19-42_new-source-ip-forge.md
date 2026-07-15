---
ts: 2026-07-15T01:19:42.054029+00:00
rule_id: new-source-ip-forge
ip: 127.0.0.1
surface: forge
blocked: true
notified: true
---

# Incident: new-source-ip-forge — 2026-07-15 01:19 UTC

**IP:** 127.0.0.1  
**Surface:** forge  
**Trigger:** Request to forge dashboard from source IP not in trusted list  
**Action:** ufw deny inserted  
**Block note:** Skipping adding existing rule  

## Event

```json
{
  "ip": "127.0.0.1",
  "surface": "forge",
  "event_type": "request",
  "raw_lines": [
    "127.0.0.1 - - [14/Jul/2026 18:19:41] \"GET / HTTP/1.1\" 200 -"
  ]
}
```

## Raw Events

```text
127.0.0.1 - - [14/Jul/2026 18:19:41] "GET / HTTP/1.1" 200 -
```

## Notes

AI summary may be appended later by a separate report step. Detection, blocking, and notification are deterministic only.
