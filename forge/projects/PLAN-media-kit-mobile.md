---
title: Plan — Mobile Stitch Kit for Instagram & Facebook
tags: [djinn, media, plan, instagram, facebook, mobile]
created: 2026-05-31
status: planned
related: [[MEDIA-STACK]] | [[QUEUE]] | [[CONTENT-IDEAS]]
---

# Plan — Mobile Stitch Kit for IG/FB

**Goal:** Every print job produces a flat, phone-ready folder of named video clips that Javier can grab from Google Drive or Obsidian mobile and stitch directly in CapCut, Instagram editor, or any iPhone app — zero hunting, zero renaming.

---

## Platform Specs (Verified 2026-05-31)

| Platform | Format | Resolution | Codec | Audio | FPS | Max Duration | Max Size |
|----------|--------|-----------|-------|-------|-----|-------------|---------|
| Instagram Reels | MP4 | 1080×1920 (9:16) | H.264 | AAC | 30fps | 3 min | 1 GB |
| Instagram Feed video | MP4 | 1080×1350 (4:5) | H.264 | AAC | 30fps | 60s | — |
| Facebook Reels | MP4 | 1080×1920 (9:16) | H.264 | AAC | 30fps | No limit | 4 GB |
| Facebook Feed video | MP4 | 1080×1920 (9:16) | H.264 | AAC | 30fps | No limit | 4 GB |

**Key finding: Facebook and Instagram Reels are now the same spec.** As of June 2025, all Facebook videos post as Reels. One export covers both platforms.

**Current pipeline gap:** FPS is not forced — clips inherit source FPS. Everything else (H.264, AAC, 1080×1920, +faststart) is already correct.

---

## Naming Convention

Since only one print job runs at a time, the **print job name is the content identity**.

**Rule:** `{job_slug}_{nn}.mp4`

Examples:
```
mini-vases-job4_01.mp4
mini-vases-job4_02.mp4
mini-vases-job4_reel.mp4    ← full combined reel
puffco-proxy-v2_01.mp4
puffco-proxy-v2_reel.mp4
```

`job_slug` comes from the project manifest `notes` field (set at ingest time with `--notes "job_name"`), or falls back to the `project_id` slug.

---

## stitch-kit Folder Structure

Every project gets a `stitch-kit/` folder at the top level — flat, numbered, nothing buried:

```
stitch-kit/
├── {job_slug}_01.mp4         ← hook clip (0–30s)
├── {job_slug}_02.mp4         ← middle clip
├── {job_slug}_03.mp4         ← closer clip
├── {job_slug}_reel.mp4       ← full combined reel (if combined mode)
└── STITCH-ORDER.txt          ← clip list with durations + what's in each
```

**STITCH-ORDER.txt example:**
```
Project: mini-vases-job4
Generated: 2026-05-31

Clip 1 — mini-vases-job4_01.mp4  [0:00–0:30, 30s]
  Hook: printer reveal, vases starting to form

Clip 2 — mini-vases-job4_02.mp4  [0:30–1:00, 30s]
  Mid: layer detail, engraving close-up

Clip 3 — mini-vases-job4_03.mp4  [1:00–1:30, 30s]
  Closer: finished vases off the bed

Full Reel — mini-vases-job4_reel.mp4  [90s combined]

Platform: Instagram Reels + Facebook Reels (same spec)
Specs: 1080×1920, H.264, 30fps, AAC
Captions: see publish/POST.txt
```

---

## Google Drive Structure (Updated)

`stitch-kit/` becomes the **primary download target** — it's the first folder you see when you open the Drive link.

```
gdrive:Typhons-Forge/posts/{project_id}/
├── stitch-kit/         ← PRIMARY: grab these, stitch on iPhone
│   ├── {job_slug}_01.mp4
│   ├── {job_slug}_02.mp4
│   ├── {job_slug}_reel.mp4
│   └── STITCH-ORDER.txt
├── publish/            ← captions + hashtags (POST.txt, instagram_post.md)
├── video/              ← full processed reel (pipeline master)
└── feed/               ← feed photos (1080×1350, 1080×1080)
```

Discord `#post-ready` message is updated to lead with the `stitch-kit/` Drive link.

---

## Obsidian Mobile Access

Obsidian vault syncs via git. The stitch-kit folder will also be written inside the vault project:

```
~/Obsidian/djinn/media/posts/{project_id}/stitch-kit/
```

If rclone/Drive isn't available, open Obsidian mobile → media/posts → project → stitch-kit. Files are there directly.

**Note:** Large video files may be excluded from the git-tracked vault to avoid bloating the repo. If so, Drive is the primary mobile access point and Obsidian mobile has the text files (STITCH-ORDER.txt, POST.txt, captions) only.

---

## What Changes in Code

### 1. `djinn-media-reel` — 2 fixes
- Add `-r 30` to all ffmpeg export commands (force 30fps)
- Read `job_slug` from manifest notes field; rename output from `{project_id}_reel.mp4` → `{job_slug}_reel.mp4`

### 2. `djinn-media-repurpose` — 1 fix
- Rename clip output from `clip_{n:02d}.mp4` → `{job_slug}_{n:02d}.mp4`
- Read `job_slug` from manifest

### 3. New: `djinn-media-kit` — new script (~80 lines)
- Reads all clips from `exports/reel/`
- Creates `stitch-kit/` folder in project root
- Copies clips with job-name convention
- Writes `STITCH-ORDER.txt` with durations + notes from manifest
- Updates manifest `status = "kit_ready"`
- Run automatically after `djinn-media-repurpose` or `djinn-media-reel`
- Trigger: `djinn-media-kit {project_id}`
- Discord/Telegram trigger: `kit {project_id}`

### 4. `djinn-media-publish-prep` — 1 change
- Upload `stitch-kit/` to Drive first, before `publish/` and `video/`
- Discord `#post-ready` message leads with stitch-kit Drive link

### 5. `djinn-media-ingest` — 1 addition
- Add `--job-name "slug"` flag that writes `job_slug` to manifest
- Fallback: use project_id slug if not provided

---

## Updated Full Pipeline (with kit step)

```
djinn-media-ingest <path> --job-name "mini-vases-job4"
  → creates project, stores job_slug in manifest

djinn-media-reel <id> [--combine]
  → exports {job_slug}_reel.mp4 at 30fps

djinn-media-repurpose <id> [--clips N]
  → exports {job_slug}_01.mp4, _02.mp4...

djinn-media-thumbnail <id>
djinn-media-qa <id>

djinn-media-kit <id>          ← NEW STEP
  → creates stitch-kit/, writes STITCH-ORDER.txt

djinn-media-publish-prep <id>
  → uploads stitch-kit/ to Drive (primary link)
  → posts to Discord #post-ready with kit link
```

---

## Delegation

| Task | Who | What |
|------|-----|------|
| TASK-005 | **Claude** | Update `djinn-media-reel`: force 30fps, job-name output |
| TASK-006 | **Claude** | Update `djinn-media-repurpose`: job-name clip naming |
| TASK-007 | **Claude** | Build `djinn-media-kit`: stitch-kit folder + STITCH-ORDER.txt |
| TASK-008 | **Claude** | Update `djinn-media-publish-prep`: upload stitch-kit/ first, new Discord message format |
| TASK-009 | **Claude** | Update `djinn-media-ingest`: add `--job-name` flag |
| TASK-010 | **Salomon** | Deploy + test full pipeline with `mini-vases-job4` project |
| TASK-011 | **Salomon** | Add `kit {project_id}` trigger to Discord + Telegram gateways |

**Build order:** TASK-005 → 006 → 007 → 008 → 009 (all Claude, can do in one session) → TASK-010 → 011 (Salomon after Claude done)

---

## What Marcus Does NOT Need To Do

Platform specs are confirmed from live sources (2026-05-31). No Marcus research needed for this task. Marcus-lane work only if deeper algorithm/engagement research is needed later.

---

*— Claude, 2026-05-31*
