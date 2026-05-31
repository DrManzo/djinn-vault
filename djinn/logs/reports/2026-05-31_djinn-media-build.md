---
title: Session Report — Djinn Media Build (TASK-004 through 013)
agent: Claude
date: 2026-05-31
tags: [djinn, report, media, build]
related: [[build-log]] | [[QUEUE]] | [[PLAN-djinn-media-architecture]]
---

# Session Report — Djinn Media Build

**Date:** 2026-05-31
**Agent:** Claude
**Session type:** Build
**Tasks completed:** TASK-004, 005, 006, 007, 008, 009, 013

---

## Summary

Built the Djinn Media production pipeline updates and the personal footage intake system. Seven tasks completed in one session. Salomon now has four deploy tasks ready (TASK-010, 011, 014) plus Marcus research (TASK-012) pending Javier's trigger.

---

## What Was Built or Changed

### TASK-004 — Maker's mark configurable + STL support
- **`djinn-model-mark`**: Added `--mark <stl>` flag, `--no-mirror` flag, `load_mark_config()`, `build_cutter_from_stl()`. External STL marks auto-mirror X axis by default (reads from config). Built-in geometry unchanged and always mirrors.
- **`~/.config/djinn/makers-mark.json`**: Created. Points to `tf_anvil_traced_15mm.stl`, `mirror_x: true`, `size_mm: 15`, `depth_mm: 0.5`.
- **`SUPPORT-GUIDE.md`**: Added Maker's Mark section — rule documented, config format shown, "never bypass" stated explicitly.

### TASK-005 — `djinn-media-reel`: 30fps + job-name output
- Added `-r 30` to both single-clip and normalize_clip ffmpeg commands
- Output filename: `{job_slug}_reel.mp4` (reads `job_slug` from manifest, falls back to notes slug, then project_id)
- Cover frame filename updated to match

### TASK-006 — `djinn-media-repurpose`: job-name clips
- Clip output renamed from `clip_{n:02d}.mp4` → `{job_slug}_{n:02d}.mp4`
- Same job_slug derivation logic as TASK-005

### TASK-007 — New: `djinn-media-kit`
- New script at `/home/drmanzo/.local/bin/djinn-media-kit`
- Creates `stitch-kit/` in project root — flat, named clips ready for iPhone
- Writes `STITCH-ORDER.txt` with clip list, durations, platform specs
- Updates manifest `status = "kit_ready"`, writes `stitch_kit` metadata block
- Usage: `djinn-media-kit {project_id}`

### TASK-008 — `djinn-media-publish-prep`: stitch-kit Drive upload
- `_upload_to_gdrive()` now uploads `stitch-kit/` first, gets a direct shareable link for it
- Returns `(folder_link, kit_link)` tuple
- Discord `#media-status` and `#post-ready` messages now lead with stitch-kit link
- `#post-ready` message format: `Grab clips (stitch-kit): {link}` at the top

### TASK-009 — `djinn-media-ingest`: `--job-name` flag
- Added `--job-name "slug"` CLI flag
- Writes `job_slug` field to `manifest.json`
- Falls back to empty string if not provided (reel/repurpose derive from notes)
- Updated usage line

### TASK-013 — `djinn-media-drop`: intake watcher + systemd units
- New script at `/home/drmanzo/.local/bin/djinn-media-drop`
- Watches `~/djinn-media-inbox/` — inotifywait (event-driven) with poll fallback
- On new file: stability check → `djinn-media-ingest` → move to `processed/` → Telegram notification with project_id + processing commands
- Inbox: `~/djinn-media-inbox/`  Processed: `~/djinn-media-inbox/processed/`
- Three systemd units written: `djinn-media-drop.service`, `djinn-media-gdrive-sync.service`, `djinn-media-gdrive-sync.timer`
- GDrive sync: `gdrive:Typhons-Forge/inbox` → `~/djinn-media-inbox` every 5 min

---

## Technical Decisions

- **job_slug derivation order:** `manifest["job_slug"]` (set by `--job-name`) → slugify(notes) → project_id slug. Same logic in all three tools (reel, repurpose, kit) so they're always consistent.
- **Mirror in djinn-model-mark:** Built-in Shapely geometry already mirrored — left unchanged. New `build_cutter_from_stl()` mirrors the external STL vertices + reverses face winding. `mirror_x` default is `True` unless config says otherwise or `--no-mirror` passed.
- **inotifywait with poll fallback:** Salomon may or may not have inotify-tools installed. Poll at 10s is good enough for a manual drop workflow.
- **stitch-kit Drive as primary link:** Kit link is a direct link to the `stitch-kit/` subfolder, not the project root — one tap to the clips on mobile.

---

## Files Created or Modified

```
~/.local/bin/djinn-model-mark              ← added --mark, --no-mirror, STL support
~/.local/bin/djinn-media-reel              ← 30fps, job_slug output names
~/.local/bin/djinn-media-repurpose         ← job_slug clip names
~/.local/bin/djinn-media-kit               ← NEW — stitch-kit builder
~/.local/bin/djinn-media-publish-prep      ← stitch-kit Drive upload, new Discord msg
~/.local/bin/djinn-media-ingest            ← --job-name flag, job_slug in manifest
~/.local/bin/djinn-media-drop              ← NEW — inbox watcher daemon
~/.config/djinn/makers-mark.json           ← NEW — mark config
~/.config/systemd/user/djinn-media-drop.service
~/.config/systemd/user/djinn-media-gdrive-sync.service
~/.config/systemd/user/djinn-media-gdrive-sync.timer
~/djinn-media-inbox/                       ← NEW — drop folder
~/djinn-media-inbox/processed/             ← NEW — processed files land here
Obsidian/djinn/printer/SUPPORT-GUIDE.md   ← maker's mark rule added
Obsidian/djinn/communications/QUEUE.md    ← TASK-004–009, 013 marked done
```

---

## Tests & Validation

Not deployed/tested yet — Salomon handles TASK-010 (deploy + test) and TASK-014 (deploy drop watcher). Scripts are syntax-clean Python.

---

## Known Issues / Caveats

- `djinn-media-drop` uses `/usr/bin/rclone` hardcoded in systemd unit — Salomon should verify rclone path with `which rclone` before enabling timer.
- `djinn-media-kit` assumes clips in `exports/reel/` are already processed. If called before `djinn-media-reel`, it exits cleanly with an error message.
- The `_upload_to_gdrive()` return signature changed from `str` to `(str, str)` tuple — only `djinn-media-publish-prep` calls it internally, so no external breakage.

---

## What's Next

- TASK-010: Salomon deploys + tests full updated pipeline
- TASK-011: Salomon adds `kit` trigger to Discord/Telegram gateways
- TASK-014: Salomon enables `djinn-media-drop.service` + `djinn-media-gdrive-sync.timer`
- TASK-012: Javier triggers Marcus research (Perplexity), saves to `research/marcus/TASK-012_djinn-media-social.md`

---

*— Claude, 2026-05-31*
