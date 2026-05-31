---
title: Djinn Media — System Architecture
tags: [djinn, media, architecture, plan, instagram, facebook, discord]
created: 2026-05-31
status: planned
related: [[MEDIA-STACK]] | [[PLAN-media-kit-mobile]] | [[QUEUE]] | [[CONTENT-IDEAS]]
---

# Djinn Media — System Architecture

**What it is:** The social media production layer of Djinn. Takes raw input (now: Discord clips; later: Javier's own footage) and produces platform-ready posts automatically — right format, right style, right tags, right caption.

**Brand:** Djinn Media (sub-brand of Djinn OS, separate from Typhon's Forge shop ops)

---

## Two-Layer Architecture

```
┌─────────────────────────────────────────────────────┐
│               LAYER 1 — INTELLIGENCE                │
│                                                     │
│  trend-agent       hashtag-agent    style-agent     │
│  (what's hot now)  (job-relevant    (what filters   │
│                     tags, live)      are working)   │
│                                                     │
│  Runs on schedule. Writes to shared context.        │
│  Output: media-context.json (per-job, auto-updated) │
└──────────────────────┬──────────────────────────────┘
                       │ feeds
┌──────────────────────▼──────────────────────────────┐
│               LAYER 2 — PRODUCTION                  │
│                                                     │
│  clip-agent        caption-agent    export-agent    │
│  (applies LUT,     (writes copy     (formats for    │
│   cuts, pacing)     from context)    IG + FB)       │
│                                                     │
│  Triggered per job. Reads context. Outputs kit.     │
│  Output: stitch-kit/ → Google Drive → Discord       │
└─────────────────────────────────────────────────────┘
```

Layer 1 is always running (scheduled). Layer 2 fires per job when input arrives.

---

## Layer 1 — Intelligence Agents

### trend-agent
- **What it does:** Monitors what content formats, topics, and styles are gaining traction in maker/3D printing/cannabis niches on IG and FB
- **Runs:** Daily or on-demand
- **Output:** `media-context.json` → `trending_formats`, `trending_topics`, `recommended_hook_style`
- **Data sources:** TBD by Marcus research (TASK-012) — IG Graph API, third-party trend APIs, scraping

### hashtag-agent (extends existing `djinn-hashtag-update`)
- **What it does:** Pulls hashtags relevant to the *specific job* being posted — not just brand tags, but what's trending for that content type right now
- **Inputs:** Job name, print type (vase, functional, cannabis accessory, etc.), current trending topics
- **Runs:** Per job, at publish-prep time
- **Output:** `media-context.json` → `job_hashtags[]` — ranked by relevance + current performance
- **Current state:** `djinn-hashtag-update --research` already exists (phi4:14b, weekly). This agent replaces the static bank with live + job-aware selection.

### style-agent
- **What it does:** Monitors what visual styles, color grades, pacing, and effects are performing in the target niche. Recommends which LUT to apply, optimal clip pacing, whether text-on-screen is working right now.
- **Runs:** Weekly or on-demand
- **Output:** `media-context.json` → `recommended_lut`, `recommended_pacing`, `hook_format`
- **Data sources:** TBD by Marcus — scraping top-performing content, platform analytics API

---

## Layer 2 — Production Agents

Read from `media-context.json` written by Layer 1. No manual input required.

### clip-agent (extends `djinn-media-reel` + `djinn-media-kit`)
- Applies recommended LUT from style-agent (not hardcoded `forge`)
- Cuts clips to recommended pacing
- Names clips by print job: `{job_slug}_{nn}.mp4`
- Outputs to `stitch-kit/` — flat, numbered, phone-ready

### caption-agent (extends `djinn-media-publish-prep`)
- Reads job context + trending topics from Layer 1
- Writes caption in brand voice with current hook style
- Pulls `job_hashtags[]` from hashtag-agent (live, job-specific)
- Outputs `POST.txt`, `caption_feed.txt`, `caption_reel.txt`

### export-agent (extends `djinn-media-reel` + publish-prep)
- Forces platform specs: 1080×1920, H.264, AAC, 30fps, +faststart
- Packages `stitch-kit/` for Drive upload
- Posts to Discord `#post-ready` with Drive link + captions

---

## Personal Footage Intake — Fire Test Path (TASK-013/014)

Before Discord capture is built, Javier can test the full pipeline with his own footage:

```
iPhone → Google Drive (gdrive:Typhons-Forge/inbox/)
  ↓ rclone sync every 5 min (djinn-media-gdrive-sync.timer)
~/djinn-media-inbox/
  ↓ djinn-media-drop watcher (inotifywait daemon)
djinn-media-ingest --job-name {derived from filename}
  ↓
Telegram: "📥 Ingested: {project_id} — send reel/full to process"
  ↓
Javier sends: full {project_id}
  ↓
Layer 1 + Layer 2 pipeline → stitch-kit/ → Drive → #post-ready
```

**Drop folder:** `~/djinn-media-inbox/`
**GDrive inbox:** `gdrive:Typhons-Forge/inbox/`
**Processed files moved to:** `~/djinn-media-inbox/processed/`

This path is intentionally separate from Discord capture. It's the manual "I shot this, run it" path that will exist permanently even after full automation.

---

## Current Scope — Discord Only

**Right now Djinn Media runs on Discord channel content only.**

Input pipeline (to be built — see discord capture plan):
```
Discord channel activity
  → djinn-discord-capture (clips/screenshots of channel)
  → djinn-media-ingest --job-name "{print_job}"
  → Layer 1 (trend + hashtag + style context)
  → Layer 2 (grade → caption → kit → Drive)
  → Discord #post-ready
```

This covers the content ideas already documented — the bot demo, renders dropping, the customer flow, agent conversations. That's the raw material. Djinn Media makes it postable automatically.

---

## Future Scope — Javier's Own Footage

When the shop grows and Javier starts filming:

```
Javier shoots on iPhone → AirDrops to Mac / uploads to Drive
  → djinn-media-ingest <path> --job-name "{print_job}"
  → same Layer 1 + Layer 2 pipeline
  → stitch-kit/ ready on Drive within minutes
  → Javier opens Drive on iPhone, stitches in CapCut, posts
```

Javier's only job: shoot and upload. Djinn Media handles everything else — color, captions, tags, formatting, distribution.

---

## The shared context file

`media-context.json` — written by Layer 1, read by Layer 2. Lives at:
`~/.local/share/djinn-media/media-context.json`

```json
{
  "updated_at": "2026-05-31T...",
  "trending_formats": ["POV timelapse", "before/after reveal", "text-on-screen tutorial"],
  "trending_topics": ["AI automation", "custom 3d print", "maker shop"],
  "recommended_hook_style": "POV reveal — first 3s shows finished product, then process",
  "recommended_lut": "forge",
  "recommended_pacing": "cut every 2-3s for first 15s, slower after",
  "job_hashtags": {
    "mini-vases-job4": ["#3dprinting", "#makersmark", "#smallbatch", ...],
    "puffco-proxy-v2": ["#3dprinting", "#puffco", "#customaccessory", ...]
  },
  "platform_notes": {
    "instagram": "Reels under 30s getting strong reach this week",
    "facebook": "Same spec as IG Reels — one export covers both"
  }
}
```

---

## What Marcus Needs to Find (TASK-012 addition)

Added to research brief as Question 8:
- What data sources exist for programmatically querying trending hashtags, content formats, and style trends for IG/FB in 2026?
- Is the IG Graph API useful for this or is third-party the only real option?
- What trend APIs (RapidAPI, Apify, etc.) are reliable and affordable for a one-person operation?
- How do you detect what visual styles/filters are performing without scraping — is there a signal available?

---

## Build Order

| Phase | What | Who |
|-------|------|-----|
| **Phase 0 (now)** | Marcus research → TASK-012 | Marcus / Javier |
| **Phase 1** | Mobile stitch kit (TASK-005–011) | Claude + Salomon |
| **Phase 2** | Discord capture agent | Claude + Salomon |
| **Phase 3** | Layer 1 agents (trend, hashtag live, style) | Claude (spec) + Salomon (deploy) |
| **Phase 4** | Layer 1 → Layer 2 wiring (media-context.json) | Claude + Salomon |
| **Phase 5** | Full Discord → post pipeline live | Salomon ops |
| **Future** | Javier footage input path | As needed |

Phase 1 is already queued and ready to build. Phases 2–4 wait for Marcus research results.

---

*— Claude, 2026-05-31*
