---
title: session.json Schema
tags: [djinn, gateway, schema]
updated: 2026-06-05
---

# session.json Schema

File location: `~/.config/djinn/session.json`

This file is written by `djinn-gateway` and read by the Python enforcement module and the pre-push hook. It is machine-local — not committed to git.

---

## Current Schema (v2)

```json
{
  "mode": "standard",
  "activated_at": "2026-06-05T21:30:00+00:00",
  "expires_at": "2026-06-05T23:30:00+00:00",
  "duration_hours": 2,
  "activated_by": "javier",
  "machine": "salomon",
  "notes": ""
}
```

## Field Reference

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `mode` | string | yes | `"standard"` \| `"dev"` \| `"restricted"` |
| `activated_at` | ISO 8601 with UTC offset | yes | When mode was set. **Must include timezone offset** (e.g. `+00:00` or `-07:00`). |
| `expires_at` | ISO 8601 with UTC offset | yes for dev | When dev mode expires. Null for standard/restricted. **Must include timezone offset.** |
| `duration_hours` | number | no | Convenience field. Derived from activated_at → expires_at. |
| `activated_by` | string | yes | Always `"javier"` for dev mode. |
| `machine` | string | yes | `"salomon"` or `"typhon"` |
| `notes` | string | no | Optional context for the session. |

## Timezone Rule

**All timestamps must be timezone-aware ISO 8601 strings.** Never use naive datetime strings (no `Z`-less format, no timestamps without offset).

Correct: `"2026-06-05T21:30:00+00:00"`  
Correct: `"2026-06-05T14:30:00-07:00"`  
Wrong: `"2026-06-05T21:30:00"` ← naive, no offset — will be rejected by v2 reader

## Default (Standard Mode)

```json
{
  "mode": "standard",
  "activated_at": "2026-06-05T00:00:00+00:00",
  "expires_at": null,
  "duration_hours": null,
  "activated_by": "system",
  "machine": "salomon",
  "notes": ""
}
```

## Version History

| Version | Date | Change |
|---------|------|--------|
| v1 | 2026-06-05 | Initial schema — naive datetime strings |
| v2 | 2026-06-05 | Timezone-aware ISO 8601 required for activated_at and expires_at |

*— Marcus, 2026-06-05*
