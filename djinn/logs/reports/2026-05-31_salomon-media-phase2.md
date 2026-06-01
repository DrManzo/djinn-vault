---
title: Salomon — Phase 2 Djinn Media (TASK-016, 017, 018)
date: 2026-05-31
session_id: salomon-media-phase2
tags: [djinn, salomon, media, social, meta]
---

## Summary
Built and deployed 3 Djinn Media Phase 2 tools: Meta Graph API publishing, token refresh cron, and daily social analytics.

## What Was Built

### TASK-016 — `djinn-media-publish`
- **File:** `~/.local/bin/djinn-media-publish`
- Posts finished reel to Instagram (two-step: media → media_publish) and/or Facebook (single video POST)
- **Flow:** reads meta.env → loads manifest + caption + hashtags → uploads reel to GDrive for public URL → posts to IG and/or FB → writes `published` field to manifest + publish-log.json → Telegram notification
- IG gets full caption + all hashtags; FB gets first 2 sentences + 3 hashtags max
- `--dry-run` flag tested clean

### TASK-017 — `djinn-meta-token-refresh`
- **File:** `~/.local/bin/djinn-meta-token-refresh`
- **Systemd:** `djinn-meta-token-refresh.service` + `.timer` (monthly, 1st at 03:00, Persistent)
- Reads META_PAGE_TOKEN + META_APP_ID + META_APP_SECRET from meta.env
- Exchanges via `fb_exchange_token` grant → writes new token in-place → Telegram alert

### TASK-018 — `djinn-social-analyst`
- **File:** `~/.local/bin/djinn-social-analyst`
- **Systemd:** `djinn-social-analyst.service` + `.timer` (daily at 00:30 UTC, Persistent)
- Fetches recent IG media → per-post insights (reach, plays, saved, shares, comments, avg_watch_time) → ranks by saves+shares → writes analytics JSON + TREND-SIGNAL.md → git commit+push → Telegram
- Output dirs: `~/Obsidian/djinn/social/analytics/` and `~/Obsidian/djinn/social/TREND-SIGNAL.md`
- Empty-window case handled gracefully (no crash on zero posts)

## Also Done
- Installed `inotify-tools` via apt → djinn-media-drop.service now uses event-driven mode (was poll mode with 10s latency)
- Shipping cleanup already done by Claude (`djinn/shipping/` deleted, easypost_client bug moot)

## Files Created/Modified
- `~/.local/bin/djinn-media-publish` — new
- `~/.local/bin/djinn-meta-token-refresh` — new
- `~/.local/bin/djinn-social-analyst` — new
- `~/.config/systemd/user/djinn-meta-token-refresh.service` — new
- `~/.config/systemd/user/djinn-meta-token-refresh.timer` — new
- `~/.config/systemd/user/djinn-social-analyst.service` — new
- `~/.config/systemd/user/djinn-social-analyst.timer` — new
- `~/Obsidian/djinn/social/analytics/` — created
- `QUEUE.md` — TASK-016/017/018 marked done

## Tests & Validation
- `djinn-media-publish --dry-run` — verified all paths resolve correctly
- All 3 scripts: `python3 -m py_compile` — clean syntax
- Both systemd timers: enabled, listed in `systemctl --user list-timers`
- `djinn-media-drop` verified switching from poll to inotify mode

## Known Issues
- Real publish/analytics calls require `~/.config/djinn/meta.env` with valid Meta credentials — none available yet
- Token refresh timer won't fire until June 1st

## What's Next
- TASK-019 (Claude): build `djinn-trend-agent` — Firecrawl search/scrape + Printables RSS → phi4:14b → TREND-SIGNAL.md + HASHTAG-BANK.md every 6h
- TASK-020 (Claude): wire trend signal + hashtags into caption generation pipeline
- TASK-012 + TASK-015 (Marcus): research briefs — pending Javier trigger in Perplexity
