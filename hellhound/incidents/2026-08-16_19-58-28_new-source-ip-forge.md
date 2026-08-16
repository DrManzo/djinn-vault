---
ts: 2026-08-16T19:58:28.928931+00:00
rule_id: new-source-ip-forge
ip: 192.168.1.150
surface: forge
blocked: false
notified: true
---

# Incident: new-source-ip-forge — 2026-08-16 19:58 UTC

**IP:** 192.168.1.150  
**Surface:** forge  
**Trigger:** Request to forge dashboard from source IP not in trusted list  
**Action:** alert only  
**Block note:** LAN_SKIP  

## Event

```json
{
  "ip": "192.168.1.150",
  "surface": "forge",
  "event_type": "request",
  "raw_lines": [
    "192.168.1.150 - - [16/Aug/2026 12:58:28] \"GET /api/status HTTP/1.1\" 200 -"
  ]
}
```

## Raw Events

```text
192.168.1.150 - - [16/Aug/2026 12:58:28] "GET /api/status HTTP/1.1" 200 -
```

## Notes

AI summary may be appended later by a separate report step. Detection, blocking, and notification are deterministic only.
