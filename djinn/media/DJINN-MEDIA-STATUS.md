---
title: Djinn Media — Full Stack Status
updated: 2026-05-31
agent: Claude
tags: [djinn-media, status, architecture, media-pipeline]
related: [[MEDIA-STACK]] | [[PLAN-djinn-media-architecture]] | [[build-log]] | [[COMMS]]
---

# Djinn Media — Full Stack Status

**Last updated:** 2026-05-31  
**Updated by:** Claude  
**Status:** Phase 2 complete. Phase 3 specced and queued.

---

## Overview

Djinn Media is the social production layer of Djinn OS. It takes raw footage from Javier's phone, processes it through a multi-step pipeline, and publishes finished Reels to Instagram and Facebook — fully automated, no human steps between drop and post.

The pipeline has two conceptual layers:

- **Layer 1 — Intelligence:** Trend polling, hashtag research, analytics feedback loop
- **Layer 2 — Production:** Ingest, edit, caption, kit, publish

---

## Current Architecture

```
iPhone footage
      │
      ▼
gdrive:Typhons-Forge/inbox/
      │  (rclone sync every 5 min)
      ▼
~/djinn-media-inbox/
      │  (djinn-media-drop watcher)
      ▼
djinn-media-ingest --job-name <slug>
      │  creates project in ~/.local/share/djinn-media/projects/
      ▼
┌─────────────────┬──────────────────────────────┐
│ Layer 2          │ Layer 1 (feeds into captions)  │
│                  │                                │
│ djinn-media-reel │ djinn-trend-agent [TASK-019]   │
│ djinn-media-photo│ ← Firecrawl search/scrape      │
│ djinn-media-kit  │ ← Printables RSS               │
│                  │ ← Apify IG (optional)          │
│                  │ ← Ollama phi4:14b synthesis    │
│                  │ → TREND-SIGNAL.md              │
│                  │ → HASHTAG-BANK.md              │
│                  │                                │
│ djinn-media-     │ ← reads TREND-SIGNAL.md        │
│   publish-prep   │    + HASHTAG-BANK.md           │
│ (captions,       │    [TASK-020]                  │
│  hashtags, kit)  │                                │
│                  │                                │
│ djinn-meta-      │ djinn-social-analyst           │
│   token-refresh  │ ← Meta Graph API own analytics │
│   (monthly cron) │ → analytics/YYYY-MM-DD.json   │
│                  │ → TREND-SIGNAL.md (feedback)   │
└─────────────────┴──────────────────────────────┘
      │
      ▼
djinn-media-publish
      │  IG: create container → upload → poll → publish
      │  FB: init → upload → finish
      ▼
Instagram Reel + Facebook Reel
      │
      ▼
publish-log.json + Telegram notification
```

---

## Scripts — Current State

| Script | Path | Status | What it does |
|--------|------|--------|--------------|
| `djinn-media-ingest` | `~/.local/bin/` | ✅ Live | Intake footage, create project manifest, job_slug support |
| `djinn-media-reel` | `~/.local/bin/` | ✅ Live | Export reel (30fps H.264 AAC, job-named output) |
| `djinn-media-photo` | `~/.local/bin/` | ✅ Live | Photo edit pipeline with LUT grading |
| `djinn-media-repurpose` | `~/.local/bin/` | ✅ Live | Clip cuts for repurposing (job-named) |
| `djinn-media-kit` | `~/.local/bin/` | ✅ Live | Stitch-kit/ builder + STITCH-ORDER.txt |
| `djinn-media-publish-prep` | `~/.local/bin/` | ✅ Live | Caption generation, hashtag validation, GDrive upload, Discord notify |
| `djinn-media-publish` | `~/.local/bin/` | ✅ Built | Meta Graph API publish (IG + FB) — awaiting meta.env credentials |
| `djinn-meta-token-refresh` | `~/.local/bin/` | ✅ Built | Monthly token refresh cron — awaiting meta.env app creds |
| `djinn-social-analyst` | `~/.local/bin/` | ✅ Built | Daily own-post analytics pull — awaiting meta.env credentials |
| `djinn-media-drop` | `~/.local/bin/` | ✅ Live | Inbox watcher daemon (inotifywait / poll fallback) |
| `djinn-style-scrape` | `~/.local/bin/` | ⚠️ Fragile | DuckDuckGo image reference scraper — Firecrawl replacement queued (TASK-021) |
| `djinn-trend-agent` | `~/.local/bin/` | 🔲 Pending | Multi-source trend poller — specced as TASK-019, queued for Salomon |

---

## Systemd Timers

| Timer | Schedule | Status |
|-------|----------|--------|
| `djinn-media-gdrive-sync.timer` | Every 5 min | ✅ Active |
| `djinn-media-drop.service` | Continuous daemon | ✅ Active |
| `djinn-meta-token-refresh.timer` | Monthly, 1st @ 03:00 | ✅ Active (awaiting creds) |
| `djinn-social-analyst.timer` | Daily @ 00:30 UTC | ✅ Active (awaiting creds) |
| `djinn-trend-agent.timer` | Every 6h | 🔲 Pending TASK-019 |

---

## Phase 2 — What Was Built (2026-05-31)

### djinn-media-publish
Full Meta Graph API publish script. Key design decisions:

- **Instagram resumable upload** — uses `rupload.facebook.com/video-upload/v19.0` (no public URL needed). Two-step: create container → upload bytes → poll status (`FINISHED`) → publish.
- **Facebook Reels** — `/{page_id}/video_reels` with `upload_phase=start/finish` pattern.
- **Caption variants** — IG gets full caption + all hashtags. FB gets first 2 sentences + 3 hashtags max (per Marcus TASK-012 findings).
- **Manifest write-back** — writes `published.instagram` + `published.facebook` with media IDs and timestamps.
- **Publish log** — appends to `~/.local/share/djinn-media/publish-log.json`.
- **Dry-run mode** — tested against `2026-05-24_inbound` (44.1MB reel). Prints full plan without API calls.

Config required (`~/.config/djinn/meta.env`, chmod 600):
```
META_PAGE_TOKEN=<long-lived page token>
IG_USER_ID=<instagram user id>
FB_PAGE_ID=<facebook page id>
META_APP_ID=<from Meta Developer Console>
META_APP_SECRET=<from Meta Developer Console>
```

### djinn-meta-token-refresh
Monthly cron (Persistent=true) that exchanges the current page token for a fresh 60-day token via `GET /v19.0/oauth/access_token?grant_type=fb_exchange_token`. Writes in-place to meta.env, never overwrites on failure. Telegram on success/failure.

### djinn-social-analyst
Daily cron at 00:30 UTC. Pulls last N days of own post metrics (reach, plays, saves, shares, avg_watch_ms) from Meta Graph API. Writes:
- `djinn/social/analytics/YYYY-MM-DD.json` — raw per-post data
- `djinn/social/TREND-SIGNAL.md` — sorted by saves+shares with signal deltas

This is the feedback loop that makes captions improve over time.

---

## Phase 3 — What's Queued

### TASK-019 — djinn-trend-agent (pending, Salomon)
Multi-source trend poller. Architecture:

| Source | Method | Cost | Maintenance |
|--------|--------|------|-------------|
| Reddit + YouTube signal | Firecrawl `fc.search()` | $0 (Firecrawl key set) | ~0h/mo |
| Makerworld + Printables pages | Firecrawl `fc.scrape_url()` | $0 | ~0h/mo |
| Printables RSS | Direct HTTP + XML parse | $0 | ~0h/mo (RSS is stable) |
| Apify Instagram scraper | Apify API | $0 (free tier, ~$3.60/mo usage) | 0h/mo (managed) |

Output: `djinn/social/TREND-SIGNAL.md` every 6h, `HASHTAG-BANK.md` weekly.

**Note:** Reddit and YouTube APIs are NOT needed. Firecrawl handles search across both platforms with a single key already installed.

### TASK-020 — Caption wiring (pending, Salomon)
Update `djinn-media-publish-prep` to inject TREND-SIGNAL.md + HASHTAG-BANK.md into the Ollama caption prompt before generation. Writes `job_hashtags[job_slug]` back to `media-context.json` so `djinn-media-publish` finds the right hashtags per job.

---

## Firecrawl Debloat Audit (2026-05-31)

Conducted a sweep of all `djinn-*` scripts for fragile web scraping. Findings:

### Replace with Firecrawl

**`djinn-style-scrape`** — currently uses a 2-step DuckDuckGo image search via raw urllib:
1. GET `duckduckgo.com/i.js?q=...&vqd=...` requires first extracting the `vqd` token from DDG HTML
2. Parses raw JSON response for image URLs

This is the canonical "breaks silently when DDG updates their frontend" pattern. Replace with `fc.search(query)` — single call, same output, Firecrawl-maintained. Queued as **TASK-021**.

**`djinn-model-fetch`** — has stable Printables GraphQL API (keep) but HTML parsing for Makerworld and Thingiverse (replace). Queued as **TASK-022**.

### Leave Alone

| Script | Reason |
|--------|--------|
| `djinn-hashtag-update` | Hits Ollama localhost only |
| `djinn-social-analyst` | Meta Graph API — structured JSON |
| `djinn-media-publish` | Meta Graph API — structured JSON |
| `djinn-meta-token-refresh` | Meta Graph API — structured JSON |
| All gateways | Telegram + Discord APIs |
| All shop scripts | Shippo + EasyPost APIs |

---

## Outstanding Before Live Publishing

1. **meta.env credentials** — fill in `META_PAGE_TOKEN`, `IG_USER_ID`, `FB_PAGE_ID`, `META_APP_ID`, `META_APP_SECRET` in `~/.config/djinn/meta.env`
2. **Apify account** — create free account at apify.com, get API token → `~/.config/djinn/apify.env`
3. **TASK-019** — Salomon builds djinn-trend-agent when ready
4. **TASK-020** — Salomon wires trend signal into caption generation
5. **TASK-021** — Salomon rewrites djinn-style-scrape with Firecrawl
6. **TASK-022** — Salomon replaces Makerworld/Thingiverse HTML scraping in djinn-model-fetch

---

## Key File Paths

```
~/.config/djinn/meta.env                   ← Meta credentials (chmod 600)
~/.config/djinn/firecrawl.env              ← Firecrawl API key (set)
~/.config/djinn/apify.env                  ← Apify token (stub, fill when ready)
~/.local/share/djinn-media/projects/       ← All project dirs
~/.local/share/djinn-media/media-context.json  ← Shared Layer 1→Layer 2 context
~/.local/share/djinn-media/publish-log.json    ← Post history
~/djinn-media-inbox/                       ← Drop folder (watched)
~/Obsidian/djinn/social/TREND-SIGNAL.md    ← Live trend context (Layer 1 output)
~/Obsidian/djinn/social/HASHTAG-BANK.md   ← Weekly hashtag audit
~/Obsidian/djinn/social/analytics/        ← Own post analytics (daily)
```

---

*— Claude, 2026-05-31*
