# Session Report — 2026-05-28 — Typhon's Studio Guardian Agent

**Agent:** Claude  
**Machine:** claude → Typhon (192.168.1.113)  
**Tags:** typhons-studio, guardian, watchdog, phase6

---

## Summary

Completed and deployed the Guardian Agent health watchdog for Typhon's Studio. The agent watches 5 services (OBS, Xvfb, MediaMTX, Redis, Studio Backend), polls every 30 seconds, auto-restarts critical restartable services with a 2-minute cooldown, and broadcasts real-time `guardian_status` WebSocket events to the UI. Added a Guardian tab to the studio frontend with live service cards, alert log, and manual restart buttons. Added a `🛡 OK/ALERT` status indicator to the header. All 5 services report `active` on first check.

---

## What Was Built / Changed

### Backend — New File
**`/home/tf-tthq/typhons-studio/backend/agents/guardian_agent.py`**
- `GuardianAgent` class — watches 5 services, polls every 30s
- `_watch_loop()` — async loop, 5s startup delay, runs `_check_all()` every 30s
- `_check_all()` — runs `_is_active()` for each service in thread pool, detects state changes, auto-restarts critical+restartable services, broadcasts on change
- `_is_active(name)` — `sudo systemctl is-active <name>` with 5s timeout → returns 'active' / 'inactive' / 'failed' / 'unknown'
- `_attempt_restart(svc, loop)` — respects 120s cooldown, runs `sudo systemctl restart <name>` in thread pool, broadcasts before and after
- `restart_service(name)` — manual restart from API, clears cooldown, delegates to `_attempt_restart`
- `health_check()` — on-demand full check, returns all service statuses, broadcasts
- `_broadcast_status()` — sends `guardian_status` WebSocket event: services list + last 5 alerts + healthy bool
- `status()` — snapshot for API: running, healthy, services, last 10 alerts
- Alert buffer: rolling 20 entries

### Backend — Updated
**`/home/tf-tthq/typhons-studio/backend/main.py`**
- Added `from agents.guardian_agent import GuardianAgent`
- Added `guardian_agent: GuardianAgent = None` global
- Lifespan: instantiates `GuardianAgent(broadcast)`, calls `await guardian_agent.start()`, calls `await guardian_agent.stop()` on shutdown
- Startup log updated: "Phase 6 + Guardian"
- New routes:
  - `GET /api/guardian/status` — cached status snapshot
  - `POST /api/guardian/health` — immediate full health check
  - `POST /api/guardian/restart/{service}` — manual service restart
- `/api/health` now reports `"guardian": true/false/null`

### Frontend — Updated
**`/home/tf-tthq/typhons-studio/frontend/js/app.js`**
- Added `'Guardian'` to tabs array (between Post and Copilot)
- Guardian state: `guardianServices`, `guardianAlerts`, `guardianHealthy`, `guardianRunning`, `guardianChecking`, `guardianRestarting`
- `handleGuardianStatus(data)` — handles `guardian_status` WebSocket event
- `guardianHealthCheck()` — calls `POST /api/guardian/health`
- `guardianRestart(name)` — calls `POST /api/guardian/restart/{name}`, per-service loading state
- `loadGuardianStatus()` — loads `GET /api/guardian/status` on startup
- `guardianStatusColor(status)` / `guardianStatusDot(status)` — helpers for service card display
- `_tsToTime(ts)` — converts Unix timestamp to locale time string
- `guardianBadge` computed — shows `!` badge on Guardian tab when `healthy === false`
- `loadStatus()` now calls `loadGuardianStatus()`
- WebSocket `guardian_status` handler added to `ws.onmessage`

**`/home/tf-tthq/typhons-studio/frontend/index.html`**
- Header: added `🛡 OK/ALERT/…` indicator — green when healthy, red+pulse when alert, clickable → jumps to Guardian tab
- Tabs: added Guardian badge `!` when `guardianBadge` is set
- Guardian tab panel:
  - Header row: overall status badge (ALL SYSTEMS GO / ALERT / INITIALISING) + CHECK NOW button
  - Service cards: one per watched service — icon, label, service name, critical/no-restart badges, last checked time, restart count, status badge (ACTIVE/FAILED/INACTIVE/UNKNOWN), RESTART button (restartable services only, disabled while restarting)
  - Alert log: scrollable, most recent first, timestamp + message

### Infrastructure (previous session, confirmed active)
**`/etc/sudoers.d/typhons-studio-guardian`** on Typhon
- Allows `tf-tthq` to run `systemctl restart/is-active` on watched services without password

---

## Technical Decisions

1. **Poll + WebSocket broadcast** — Guardian polls systemctl every 30s and only broadcasts on state change. On-demand `health_check()` always broadcasts. Keeps WebSocket traffic low while ensuring UI is always current.

2. **Thread pool for systemctl calls** — `loop.run_in_executor(None, self._is_active, name)` keeps the asyncio event loop unblocked for all 5 simultaneous checks.

3. **120s restart cooldown** — Prevents restart storms. If a service fails repeatedly, guardian backs off automatically. Manual restarts from the API bypass the cooldown (cooldown reset to 0).

4. **typhons-studio marked `restartable: False`** — The studio can't restart itself. A crashed backend would need systemd to recover it via `Restart=on-failure` in the unit file, not self-triggered.

5. **First-check "recovered" alerts** — On first poll, all services transition from "unknown" to their actual state. If all are active, this generates 5 "recovered" alerts which correctly show up in the log as the initial state establishment.

6. **Guardian status in `/api/health`** — Added `"guardian": true/false/null` so any external monitoring tool or uptime checker can see guardian health at a glance.

---

## Files Created / Modified

| File | Status |
|------|--------|
| `/home/tf-tthq/typhons-studio/backend/agents/guardian_agent.py` | Created + Deployed |
| `/home/tf-tthq/typhons-studio/backend/main.py` | Updated (Guardian routes + lifespan) |
| `/home/tf-tthq/typhons-studio/frontend/js/app.js` | Updated (Guardian state + handlers) |
| `/home/tf-tthq/typhons-studio/frontend/index.html` | Updated (Guardian tab + header indicator) |
| `/etc/sudoers.d/typhons-studio-guardian` | Created (previous session) |

---

## Tests & Validation

| Test | Result |
|------|--------|
| `guardian_agent.py` import | ✅ Clean — no errors on service restart |
| `systemctl restart typhons-studio` | ✅ `active (running)` |
| `GET /api/health` | ✅ `{"phase": 6, "guardian": true, "status": "ok"}` |
| `GET /api/guardian/status` | ✅ All 5 services `active`, `healthy: true`, 5 alerts in log |
| `POST /api/guardian/health` | ✅ `{"ok": true, "services": {...}}` |
| Guardian WebSocket broadcast | ✅ 5 "recovered" alerts on first check (unknown→active transitions) |
| Header `🛡 OK` indicator | ✅ Rendered green in header |
| Guardian tab | ✅ Service cards, alert log, CHECK NOW button functional |

---

## Known Issues

- **First-check "recovered" spam** — On every service restart, all 5 services generate "recovered" alerts since they transition from "unknown". Cosmetic only; could be filtered in a future update by skipping alerts on the first poll cycle.
- **Cloudybay lights** — Still pending. Need Tuya IoT API credentials (iot.tuya.com) to fetch local device keys. UDP discovery from wired→WiFi may also be blocked by router; needs testing with lights powered on.
- **WHIP end-to-end** — Not yet tested with real device from Omen. Ready to test: open `https://192.168.1.113` in Chrome on Omen, accept cert, select AKASO Brave 4, click Connect.

---

## What's Next

- **Cloudybay lights** — Get Tuya IoT API key/secret from iot.tuya.com, run `tinytuya wizard`, paste device IDs into lighting agent config
- **WHIP end-to-end test** — Live test from Omen with AKASO Brave 4 camera
- **Guardian cooldown display** — Show remaining cooldown time in UI for services currently in cooldown
- **Suppress first-poll alerts** — Add a `_first_poll` flag to skip "recovered" alerts on init
- **Redis pub/sub between agents** — Currently agents communicate via direct Python calls; Redis could decouple them for future multi-process deployment

---

*— Claude*
