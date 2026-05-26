---
title: Session Report — Webcam Print Failure Monitor
agent: Claude
date: 2026-05-26
tags: [djinn, report, printer, webcam, calliope]
related: [[build-log]] [[decision-log]]
---

# Session Report — Webcam Print Failure Monitor

**Date:** 2026-05-26
**Agent:** Claude
**Session type:** Build
**Trigger:** Javier asked to use an unused webcam to monitor prints and automatically stop + save good pieces on failure.

---

## Summary

Built `djinn-webcam-monitor` — a frame-diff-based print failure detector for Calliope using the AKASO Brave 4 camera on `/dev/video2`. On confirmed failure: printer is paused via `DJINN_FAILURE_PARK` macro, a snapshot is sent to Telegram + Discord, continuous recording starts, and burst snapshots capture every 10 seconds. Smart recording runs 5-minute clips every 45 minutes during normal printing. Runs as a systemd user service with clean signal-based shutdown.

---

## What Was Built or Changed

- **`~/.local/bin/djinn-webcam-monitor`** (new) — Main monitoring daemon
  - AKASO discovery via udevadm scan (not hardcoded index)
  - `cv2.CAP_V4L2` explicit backend, 1.5s warmup delay, drain 5 stale frames on open
  - Frame diff: 22% pixel threshold, 3 consecutive confirmations before alerting
  - Smart recording: 45-min idle / 5-min scheduled clip / continuous on failure
  - Failure response: `DJINN_FAILURE_PARK` gcode, Telegram photo, Discord photo
  - Burst: 10-second snapshot interval during failure session
  - `/monitor status` state file at `~/.local/share/djinn/webcam-state.json`
  - Proper SIGTERM handler — releases camera device on exit

- **`~/.config/systemd/user/djinn-webcam-monitor.service`** (new) — Systemd service, auto-start, restart on failure

- **`~/.local/bin/djinn-discord-gateway`** (modified) — Added `handle_monitor_status` + `/monitor status` route in ROUTES_SYSTEM

- **`~/.local/bin/djinn-telegram-gateway`** (modified) — Same: `handle_monitor_status` + `/monitor status` route

- **`~/Obsidian/djinn/printer/klipper-macros-webcam.md`** (new) — Instructions for Javier to paste into printer.cfg: `DJINN_FAILURE_PARK` and `DJINN_RESUME_PRINT` macros

- **`~/Videos/print-monitor/`** — Created recording + snapshot directories

---

## Technical Decisions

1. **Custom detection vs Obico** — Built local frame-diff detection instead of Obico cloud service. Reasoning: Djinn stays fully self-hosted, no API keys, works offline. Obico can still be layered on top later (webhook → DJINN_FAILURE_PARK) if Javier wants cloud AI verification.

2. **OpenCV VideoWriter vs ffmpeg subprocess** — Used cv2.VideoWriter (mp4v codec) for recording. Avoids device conflict — same `cap` object serves both monitoring and recording. ffmpeg subprocess would need to re-open the same device, causing EBUSY.

3. **Device discovery by name** — Scanner checks udevadm `ID_MODEL` for "Brave" across /dev/video0–9 rather than hardcoding index 2. AKASO re-enumerates after reconnect; stable by-id path exists at `/dev/v4l/by-id/usb-AKASO_Brave_4_00.00.01-video-index0`.

4. **Warmup skip (5 min)** — First 5 minutes of print skipped for failure detection. Bed/brim/skirt phases have high frame diff naturally; false positives would be common without warmup.

5. **History-based comparison** — Frame compared to one from ~60 s ago (6 × 10-second checks) rather than a fixed baseline. A fixed baseline would misfire as print grows. Rolling 60-second window catches sudden catastrophic changes while tolerating gradual print growth.

---

## Files Created or Modified

| File | Action |
|------|--------|
| `~/.local/bin/djinn-webcam-monitor` | Created |
| `~/.config/systemd/user/djinn-webcam-monitor.service` | Created |
| `~/.local/bin/djinn-discord-gateway` | Modified — added monitor status handler |
| `~/.local/bin/djinn-telegram-gateway` | Modified — added monitor status handler |
| `~/Obsidian/djinn/printer/klipper-macros-webcam.md` | Created |
| `~/Videos/print-monitor/` | Created |

---

## Tests & Validation

- Camera opens cleanly (`cv2.VideoCapture(idx, cv2.CAP_V4L2)`, 640×480 @ 30fps confirmed)
- Service starts and runs without error: `Active: active (running)`
- Clean restart: previous process releases camera on SIGTERM before new process opens it
- Moonraker API verified at both ports 7125 and 4408 (both work; script uses 7125)
- `/monitor status` route added to Discord + Telegram (gateways restarted, all 3 services active)

---

## Known Issues

- **DJINN_FAILURE_PARK macro not yet installed** — Javier needs to paste it into printer.cfg via Fluidd UI (instructions at `djinn/printer/klipper-macros-webcam.md`). Until installed, failure response will still send alerts + start recording but the gcode call will return an error (non-fatal).
- **Discord holds /dev/video2** during video calls — if Javier does a Discord video call on Salomon, the monitor may contend for the camera. Both can hold it simultaneously (tested), but if Discord grabs it first and the monitor hasn't started yet, there could be a race. Long-term fix: run a shared MJPEG streamer.

---

## What's Next

1. **Javier: install Klipper macros** — Fluidd → printer.cfg → paste `DJINN_FAILURE_PARK`
2. **Typhon node setup** — second machine not yet participating as Djinn node
3. **Customer order intake** — no customer-facing ordering mechanism exists yet
4. **Daily briefing cron** — 8AM Telegram summary described in AGENTS.md, not yet wired

---

*— Claude*
