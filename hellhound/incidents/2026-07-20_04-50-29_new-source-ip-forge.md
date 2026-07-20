---
ts: 2026-07-20T04:50:29.060509+00:00
rule_id: new-source-ip-forge
ip: 192.168.1.150
surface: forge
blocked: false
notified: true
---

# Incident: new-source-ip-forge — 2026-07-20 04:50 UTC

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
    "192.168.1.150 - - [19/Jul/2026 21:50:28] \"GET /login HTTP/1.1\" 200 -"
  ]
}
```

## Raw Events

```text
192.168.1.150 - - [19/Jul/2026 21:50:28] "GET /login HTTP/1.1" 200 -
```

## Notes

AI summary may be appended later by a separate report step. Detection, blocking, and notification are deterministic only.
