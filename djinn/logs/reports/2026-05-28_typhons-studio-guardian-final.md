---
title: Session Report — Typhon's Studio Guardian Agent (Complete)
agent: Claude
date: 2026-05-28
tags: [djinn, typhons-studio, guardian, watchdog, bugfix, vue3, phase6]
related: [[build-log]] | [[decision-log]] | [[2026-05-28_typhons-studio-phase6]] | [[2026-05-28_typhons-studio-guardian]]
---

# Session Report — Typhon's Studio: Guardian Agent + Bug Fix (Complete)

**Date:** 2026-05-28  
**Agent:** Claude  
**Session type:** Build + Debug  
**Trigger:** Guardian Agent was written but not deployed (carried over from Phase 6 session); "finish up" → deploy; browser reload loop discovered and fixed

---

## Summary

Completed the full deployment of the Guardian Agent watchdog for Typhon's Studio. Deployed `guardian_agent.py` to Typhon, wired it into `main.py`, added a Guardian tab and header status indicator to the frontend. Hit a browser-crashing bug immediately: Vue 3 silently strips properties starting with `_` from the template context, so `_tsToTime()` was invisible to the template, causing a runtime error that looped the page. Fixed by renaming to `fmtTs`. All 5 services confirmed active and Guardian tab confirmed working.

---

## What Was Built or Changed

### Guardian Agent — Backend

**`/home/tf-tthq/typhons-studio/backend/agents/guardian_agent.py`** (new)
- `GuardianAgent` class — monitors 5 services: `obs-headless`, `xvfb`, `mediamtx`, `redis-server`, `typhons-studio`
- `_watch_loop()` — async loop; 5s startup delay to let services settle, then polls every 30s
- `_check_all()` — checks all services in thread pool via `loop.run_in_executor()`, detects state transitions, auto-restarts critical+restartable services on failure, broadcasts on any change
- `_is_active(name)` — `sudo systemctl is-active <name>` with 5s timeout; returns `'active'` / `'inactive'` / `'failed'` / `'unknown'`
- `_attempt_restart(svc, loop)` — 120s cooldown between retries; runs `sudo systemctl restart <name>` in thread pool; broadcasts before and after; increments `restart_count`
- `restart_service(name)` — manual restart from API; clears cooldown (sets to 0) then delegates to `_attempt_restart`
- `health_check()` — on-demand full check; updates all states; broadcasts; returns full results dict
- `_broadcast_status()` — sends `guardian_status` WebSocket event: `{services, alerts, healthy}`
- `status()` — sync snapshot for REST: `{running, healthy, services, alerts[-10:]}`
- Alert buffer: rolling 20 entries; each entry is `{time: unix_ts, msg: str}`

**`/home/tf-tthq/typhons-studio/backend/main.py`** (updated)
- Added `from agents.guardian_agent import GuardianAgent`
- Added `guardian_agent: GuardianAgent = None` global
- Lifespan: instantiates `GuardianAgent(broadcast)`; calls `await guardian_agent.start()` on startup, `await guardian_agent.stop()` on shutdown
- Startup log: "Typhon Studio starting — Phase 6 + Guardian"
- Three new routes:
  - `GET /api/guardian/status` — returns cached status snapshot (sync, instant)
  - `POST /api/guardian/health` — runs immediate full check, returns results, broadcasts
  - `POST /api/guardian/restart/{service}` — manual restart; returns `{ok, error}`
- `/api/health` now includes `"guardian": true/false/null`

### Guardian Agent — Frontend

**`/home/tf-tthq/typhons-studio/frontend/js/app.js`** (updated)
- `tabs` array: added `'Guardian'` between `'Post'` and `'Copilot'`
- New refs: `guardianServices`, `guardianAlerts`, `guardianHealthy`, `guardianRunning`, `guardianChecking`, `guardianRestarting` (object keyed by service name)
- `handleGuardianStatus(data)` — handles `guardian_status` WebSocket event; updates all guardian refs
- `guardianHealthCheck()` — calls `POST /api/guardian/health`
- `guardianRestart(name)` — calls `POST /api/guardian/restart/{name}`; sets per-service restarting state
- `loadGuardianStatus()` — called on startup via `loadStatus()`; fetches `GET /api/guardian/status`
- `guardianBadge` computed — returns `'!'` when `guardianHealthy === false`
- `guardianStatusColor(status)` / `guardianStatusDot(status)` — helpers mapping status string → CSS class / icon
- `fmtTs(ts)` — converts Unix timestamp to locale time string (see bug section below)
- WebSocket: added `guardian_status` handler to `ws.onmessage`

**`/home/tf-tthq/typhons-studio/frontend/index.html`** (updated)
- Header: added `🛡 OK / ALERT / …` indicator after the TYPHON status chip; green = healthy, red + pulse = alert; click jumps to Guardian tab
- Tabs: Guardian gets a red `!` badge when `guardianBadge` is set
- Guardian tab panel:
  - Header row: overall status badge (`● ALL SYSTEMS GO` / `⚠ ALERT` / `◌ INITIALISING`) + `⟳ CHECK NOW` button
  - Service cards: icon, label, service name chip, CRITICAL badge, NO RESTART badge if applicable, last-checked time, restart count, last-restart time, status badge (colored), `↻ RESTART` button (restartable services only, disabled per-service while restarting)
  - Alert log: most-recent-first, timestamp + message

---

## Bug: Browser Reload Loop (Vue 3 Template Proxy)

### Symptom
Service restarted `active`. API routes all returned 200 OK. But the browser kept reconnecting every 1–2 seconds — WebSocket open → loadStatus calls → WebSocket close → repeat. Page never stabilized.

### Root Cause
Vue 3's `PublicInstanceProxyHandlers` explicitly drops any property from `setup()`'s returned object whose key starts with `_` or `$`. These are treated as Vue internal / framework properties and are not forwarded to the template rendering context.

The Guardian tab template called `fmtTs(svc.last_check)` — originally named `_tsToTime`. Even though `_tsToTime` was listed in the `return {}` from `setup()`, Vue silently excluded it. The template hit a `ReferenceError: _tsToTime is not defined` at render time. Vue caught the error but the component threw, causing the page to remount → WebSocket reconnect → loadStatus() → reconnect loop.

No console error reached the user because the production Vue bundle (`vue.global.prod.js`) suppresses render errors to the console in certain environments.

### Fix
Renamed `_tsToTime` → `fmtTs` in both `app.js` (function declaration + `return {}`) and `index.html` (all 3 call sites). Redeployed. Reload loop stopped immediately.

### Rule Added
> **Never name a Vue `setup()` return property with a leading `_` or `$`.** Vue 3 treats these as framework-reserved and silently excludes them from the template proxy. The bug is silent in production — no console warning, just a broken render.

---

## Infrastructure (Pre-deployed, Confirmed Active)

**`/etc/sudoers.d/typhons-studio-guardian`** on Typhon — allows `tf-tthq` to run `systemctl is-active` and `systemctl restart` for the 5 watched services without a password. Required for the guardian to function under the `tf-tthq` service account.

---

## Files Created / Modified

| File | Status |
|------|--------|
| `/home/tf-tthq/typhons-studio/backend/agents/guardian_agent.py` | Created + Deployed |
| `/home/tf-tthq/typhons-studio/backend/main.py` | Updated — Guardian import, lifespan, 3 routes, health endpoint |
| `/home/tf-tthq/typhons-studio/frontend/js/app.js` | Updated — Guardian state, handlers, fmtTs fix |
| `/home/tf-tthq/typhons-studio/frontend/index.html` | Updated — Guardian tab, header indicator, fmtTs fix |
| `/etc/sudoers.d/typhons-studio-guardian` | Created (prior session) |

---

## Tests & Validation

| Test | Result |
|------|--------|
| `systemctl is-active typhons-studio` after deploy | ✅ `active` |
| `GET /api/health` | ✅ `{"phase": 6, "guardian": true, "status": "ok"}` |
| `GET /api/guardian/status` | ✅ All 5 services `active`, `healthy: true` |
| `POST /api/guardian/health` | ✅ `{"ok": true, "services": {obs-headless, xvfb, mediamtx, redis-server, typhons-studio}}` |
| WebSocket `guardian_status` on startup | ✅ 5 "recovered" alerts (unknown→active transition on first poll) |
| Browser UI after bug fix | ✅ No reload loop; Guardian tab renders with 5 green service cards |
| `🛡 OK` header indicator | ✅ Renders green; clicking navigates to Guardian tab |
| Manual restart button (UI) | ✅ Wired to `guardianRestart(name)` → `POST /api/guardian/restart/{name}` |

---

## Technical Decisions

1. **30s poll, broadcast only on change** — Keeps WebSocket traffic minimal. The UI reflects live state within 30s of any service failure without flooding the channel. On-demand `health_check()` always broadcasts for instant refresh.

2. **120s restart cooldown** — If a service is flapping, Guardian backs off automatically. Prevents a death-spiral where repeated fast restarts prevent the service from stabilizing. Manual API restarts bypass cooldown intentionally (operator knows what they're doing).

3. **Thread pool for all systemctl calls** — `loop.run_in_executor(None, ...)` keeps asyncio event loop unblocked during subprocess I/O. All 5 `is-active` checks run concurrently in the thread pool.

4. **`typhons-studio` marked `restartable: False`** — The studio backend cannot restart itself. If it crashes, systemd's `Restart=on-failure` directive in the unit file handles recovery. Having the process try to restart itself via systemctl while it's the one calling systemctl is undefined behavior.

5. **Guardian status in `/api/health`** — External uptime monitors (UptimeRobot, etc.) get a single endpoint that tells them if the watchdog is healthy. `null` = guardian not yet initialized, `true` = all critical services active, `false` = at least one critical service is down.

6. **`fmtTs` not `_tsToTime`** — Vue 3 template proxy drops `_`-prefixed properties. Named it without underscore to keep it visible to the template. The internal `_fmtTime` (Post tab) is called only from JS, not from templates — safe to keep as-is.

---

## Known Issues

- **First-poll "recovered" spam** — On every studio restart, all services transition from `unknown` to `active` and generate "recovered" alerts. These are accurate but cosmetically noisy. Can be suppressed with a `_first_poll` flag in a future update.
- **Cloudybay lights** — Still pending. Need Tuya IoT API key/secret from `iot.tuya.com` to retrieve local device keys via `tinytuya wizard`.
- **WHIP end-to-end test** — Not yet tested with a real device from Omen. Studio side is ready.

---

## What's Next

- [ ] Suppress first-poll "recovered" alerts — add `_first_poll` flag to `GuardianAgent.__init__` — @Claude
- [ ] Cloudybay lights — provide Tuya API credentials → run `tinytuya wizard` on Typhon — @Javier + @Claude
- [ ] WHIP end-to-end — open `https://192.168.1.113` on Omen, select AKASO Brave 4, click Connect — @Javier
- [ ] Automated report enforcement — see `djinn/logs/reports/2026-05-28_reporting-automation.md` — @Claude

---

*— Claude, 2026-05-28*
