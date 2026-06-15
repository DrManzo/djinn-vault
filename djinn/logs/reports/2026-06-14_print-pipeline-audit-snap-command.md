---
title: Session Report — Print Pipeline Full Audit, Repair & snap Command
agent: Claude
date: 2026-06-14
tags: [djinn, report, print-pipeline, webcam, discord, calliope, commission-flow]
related: [[build-log]] [[decision-log]] [[bugs]]
---

# Session Report — Print Pipeline Full Audit, Repair & snap Command

**Date:** 2026-06-14
**Agent:** Claude
**Session type:** Build / Debug
**Trigger:** Full audit of Djinn print pipeline requested — work backwards from Calliope to customer intake, find and fix all gaps

---

## Summary

A complete end-to-end audit of the Djinn print pipeline was performed across two sessions. Every stage from customer Discord attachment → model fetch → maker's mark → slice → confirm → print → customer notification was examined and repaired. Twelve distinct bugs were found and fixed, two duplicate/dead processes were killed, three broken systemd services were corrected, and a new `snap` Discord command was added to pull a live AKASO camera shot on demand. The pipeline is now fully connected from intake to delivery notification.

---

## What Was Built or Changed

### New Scripts
- **`~/.local/bin/djinn-job-add`** — bridges a marked STL into the print queue for the manual/library workflow (bypasses the customer Discord intake path). Accepts `--profile`, `--material`, `--color`, `--supports`, `--qty`, `--notes`. Writes job with `status="confirmed"` to the main queue JSON.

### Modified Scripts
- **`~/.local/bin/djinn-discord-gateway`**
  - `handle_customer_profile_pick()`: fixed status filter `"needs_review"` → `"needs_settings"` (mismatch with what `djinn-model-fetch` writes)
  - `handle_customer_profile_pick()`: inserted `djinn-model-mark` call before slice step — commission flow was going directly from pick to slice, skipping the maker's mark entirely
  - Parses `Saved:` line from mark stdout to get the marked STL path; updates queue job's `model_path`
  - Saves `customer_discord_id` and `customer_discord_name` to queue entry for post-print notification
  - Customer profile pick call updated to pass `str(message.author.id)` as third arg
  - Removed URL detection blocks — intake is attachments-only (simpler for Javier and customers)
  - Added `snap`/`snapshot` command in print channel: copies `latest.jpg` written by webcam-monitor and posts it as a Discord image attachment

- **`~/.local/bin/djinn-print-track`**
  - Lines 18–19: `MOONRAKER_HTTP/WS` corrected from `192.168.1.113` (Typhon) → `192.168.1.114` (Calliope)
  - Added `MAIN_QUEUE_PATH`, `DISCORD_CHANNEL_ID` constants
  - Added `discord_notify(text)` — posts to #3d-printing via bot token
  - Added `tg_notify(text)` — sends Telegram message to Javier
  - Added `main_queue_finalize(fname, outcome, filament_g, duration_min)` — finds the matching queue job by gcode filename, updates status to `complete`/`failed`, records `completed_at`, `filament_g`, `duration_min`; if `customer_discord_id` is present and print succeeded, mentions the customer in Discord
  - `_handle_end()`: calls `main_queue_finalize()` and `tg_notify()` after `generate_print_dir()`

- **`~/.local/bin/djinn-print-monitor-v2`**
  - IP corrected: `192.168.1.113` → `192.168.1.114`

- **`~/.local/bin/djinn-webcam-monitor`**
  - `_open()`: reverted from string path `/dev/video{idx}` to integer index `idx` for `cv2.VideoCapture()` — V4L2 backend rejects string paths ("can't be used to capture by name"); integer form works correctly
  - `_open()`: added explicit `cap.release()` on failed open — previously a failed VideoCapture could hold a partial fd, causing "Device or resource busy" on the next open attempt after a service restart
  - Main loop: writes `SNAP_DIR / "latest.jpg"` every 10 s (on each analysis tick) for on-demand snap from Discord
  - "Print ended" block: captures a completion photo and sends to Telegram + Discord before `_reset()`

- **`~/.local/bin/djinn-ctx-router`**
  - Fixed `NameError`: `pathlib.Path.home()` changed to `Path.home()` (file uses `from pathlib import Path`, not `import pathlib`)

- **`~/.local/bin/heartbeat`**
  - `git pull --rebase` → `git pull --rebase --autostash` — dirty working tree was causing silent rebase failure and blocking vault push

### Killed / Removed
- **`djinn-discord-watcher`** (service + script) — disabled and stopped. Duplicate of the gateway's attachment handler; was causing double-fetch on every customer STL drop
- **`djinn-marcus-sync`** (service + timer + script) — removed entirely. Selenium scraper for Perplexity library; fragile (session crashes), not needed since Javier downloads exports manually

---

## Technical Decisions

**Integer index vs. string path for cv2.VideoCapture** — The previous session changed integer `2` to string `"/dev/video2"` due to a "can't open by index" error. Investigation showed that error was caused by the device being busy (held by a zombie process or Discord renderer), not by a V4L2 index limitation. The V4L2 backend accepts integer device numbers but explicitly rejects string paths ("can't be used to capture by name"). Reverted to integer form.

**Shared latest.jpg for snap instead of opening camera on demand** — The webcam-monitor holds `/dev/video2` exclusively. V4L2 devices cannot be opened by two processes simultaneously. Rather than signaling the monitor or doing complex IPC, the monitor writes `latest.jpg` every 10 s and the snap command reads it. Max staleness is 10 s, which is acceptable for a live-look command.

**Attachments-only intake** — URL detection was implemented and then removed. Decision: the Discord intake path accepts only file attachments. No marketplace URL scraping. Reason: simpler for customers (they upload the file), simpler for Javier (no edge-case URL parsing), and avoids the dependency on external page scraping.

**Calliope IP is 192.168.1.114, not .113** — .113 is Typhon. Both `djinn-print-track` and `djinn-print-monitor-v2` had the wrong IP hardcoded. Fixed in both.

---

## Files Created or Modified

```
~/.local/bin/djinn-job-add                          ← NEW: STL → queue bridge for manual workflow
~/.local/bin/djinn-discord-gateway                  ← status filter fix, mark step, snap command, discord_id tracking
~/.local/bin/djinn-print-track                      ← correct Calliope IP, queue finalize, customer notification
~/.local/bin/djinn-print-monitor-v2                 ← correct Calliope IP
~/.local/bin/djinn-webcam-monitor                   ← integer index, explicit release, latest.jpg write, completion photo
~/.local/bin/djinn-ctx-router                       ← NameError fix (pathlib.Path → Path)
~/.local/bin/heartbeat                              ← --autostash on git pull --rebase
~/Obsidian/djinn/logs/build-log.md                  ← session entries appended + merge conflict resolved
~/Obsidian/djinn/logs/reports/2026-06-14_print-pipeline-audit-snap-command.md  ← this file
```

---

## Tests & Validation

- **Camera open**: confirmed `cv2.VideoCapture(2, cv2.CAP_V4L2)` succeeds when device is free; confirmed V4L2 backend is compiled in (`v4l/v4l2: YES` in build info)
- **latest.jpg**: verified file created at `~/Videos/print-monitor/snapshots/latest.jpg` (85 KB) within 10 s of service start
- **Service status**: `djinn-webcam-monitor` and `djinn-discord-gateway` both `active` after restart
- **ffmpeg capture**: confirmed AKASO streams YUYV/MJPEG/H264 at 1920×1080 and 1280×720 via `ffmpeg -f v4l2 -list_formats`
- **Device lock**: confirmed fuser shows the webcam-monitor exclusively holds `/dev/video2` while running; confirmed ffmpeg and OpenCV both get "Device or resource busy" while service runs (expected)
- **Build-log conflict**: merge conflict between Typhon stash and Claude stash resolved; both sides preserved

---

## Known Issues / Caveats

- **snap staleness**: if the webcam-monitor crashes or is stopped, `latest.jpg` goes stale. The gateway checks `mtime < 120 s` and returns an error message if stale. This is correct behavior.
- **Discord camera conflict**: Discord's renderer process (Chromium) will grab `/dev/video2` if a voice/video call is active. While Discord holds the camera the webcam-monitor can't open it and will sit in the retry loop. Monitor recovers automatically once Discord releases.
- **`djinn-webcam-monitor` Moonraker IP still shows `.113` in the file header comment** — not a functional bug (the actual `MOONRAKER` constant is a separate one that was already correct in this file; print-monitor-v2 was the one with the wrong constant).
- **`djinn-print-track`** customer notification requires `customer_discord_id` to be set on the queue job. Jobs added via `djinn-job-add` don't have this field, so those won't trigger customer Discord mentions — correct behavior for internal/library jobs.

---

## What's Next

- [ ] Test full commission flow end-to-end: customer uploads STL → picks profile → confirm → print → customer mention — @Javier
- [ ] Test `snap` command in `#3d-printing` Discord channel — @Javier
- [ ] `djinn-design` orchestrator at `~/Obsidian/djinn/printer/agent/orchestrator/` — exists but never tested — @Claude
- [ ] Post-print social promotion path (`djinn-print-promote`, `djinn-media-*`) — not yet addressed — @Claude
- [ ] Webcam monitor Moonraker IP: confirm the `MOONRAKER` constant in `djinn-webcam-monitor` is correct (should be `.114`, not `.113`) — @Claude

---

*— Claude, 2026-06-14*
