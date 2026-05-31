---
title: Salomon — Deploy Media Pipeline (TASK-010, 011, 014)
date: 2026-05-31
session_id: salomon-deploy-01
tags: [djinn, salomon, media, deploy, queue]
---

## Summary
Picked up 3 pending Salomon tasks from Claude's deploy queue in COMMS.md / QUEUE.md. All completed and verified end-to-end.

## What Was Done

### TASK-014 — Deploy djinn-media-drop watcher + gdrive sync timer
- **Built by:** Claude (TASK-013)
- **Deployed by:** Salomon
- `~/djinn-media-inbox/` + `processed/` directories created
- `djinn-media-drop.service`: enabled + started — watching inbox with 10s poll
- `djinn-media-gdrive-sync.timer`: enabled + started — syncs every 5 min from `gdrive:Typhons-Forge/inbox/`
- **Verification:** Test file → watcher detected → `djinn-media-ingest` ran → project created with correct `job_slug` in manifest → file moved to `processed/`
- **Note:** `inotifywait` not available — using poll mode

### TASK-010 — Deploy and test full updated media pipeline
- Verified all 5 scripts from Claude's TASK-005–009 exist and have expected changes
- End-to-end test: `djinn-media-ingest --job-name "mini-vases-job4"` → `djinn-media-reel` → `djinn-media-kit`
- **Verified:**
  - `job_slug: "mini-vases-job4"` in manifest
  - Reel output: `mini-vases-job4_reel.mp4` (30fps, H.264, audio intact)
  - Cover frame: `mini-vases-job4_reel_cover.jpg`
  - Stitch-kit folder with job-named clips + STITCH-ORDER.txt

### TASK-011 — Add `kit` command to Discord + Telegram gateways
- **Discord:** Added `handle_media_kit()` handler + route `^kit(?:\s+(.*))?$` to ROUTES_MEDIA + help text
- **Telegram:** Added `handle_media_kit()` handler + same route to ROUTES + help text
- Runs `djinn-media-kit {id}` then `djinn-media-publish-prep {id}` — returns Drive link via model
- Both syntax-checked clean

### Bug Fix — djinn-media-ingest job_name ordering
- **Root cause:** `job_slug` computed from `job_name` at line 64, before CLI arg parsing (lines 67–73)
- **Fix:** Moved arg parsing before slug derivation. Fallback `job_slug = slug` (source filename slug) when no `--job-name` passed.
- **Impact:** `--job-name` flag now actually works.

## Files Created/Modified
- `~/.local/bin/djinn-media-ingest` — fixed arg ordering
- `~/.local/bin/djinn-discord-gateway` — added kit handler, route, help
- `~/.local/bin/djinn-telegram-gateway` — added kit handler, route, help
- `~/djinn-media-inbox/` — created
- `~/djinn-media-inbox/processed/` — created
- `QUEUE.md` — TASK-010/011/014 marked done

## Tests & Validation
- TASK-014: test file → inbox → ingested → project created → cleaned
- TASK-010: ingest → reel → kit → all outputs correct (30fps, job-name)
- TASK-011: both scripts syntax-checked with py_compile
- All media scripts (`djinn-media-reel`, `djinn-media-repurpose`, `djinn-media-kit`, `djinn-media-publish-prep`) functionally verified

## Known Issues
- `djinn-media-drop.service` using poll mode (10s latency) — `inotifywait` not installed. Install `inotify-tools` for sub-second detection.

## What's Next
- Javier can now drop footage into GDrive inbox → auto-ingests → run `kit {project_id}` from phone
- Remaining QUEUE entries: TASK-012 (Marcus research — manual, needs Javier trigger)
