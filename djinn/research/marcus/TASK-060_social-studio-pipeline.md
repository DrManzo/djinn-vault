# TASK-060 — Automated Social Media Content Studio Pipeline
**Assigned to:** Marcus
**Status:** done
**Completed:** 2026-06-01
**Priority:** critical
**Context:** Full-stack research — automated social media content studio pipeline for two brands (Typhon's Forge + Terp Tribe Clouds). Season/episode/weekly cadence. Apple ecosystem priority. Near-studio-staff automation level.

---

## Table of Contents
1. [iCloud Access from Linux in 2026](#1-icloud-access-from-linux-in-2026)
2. [Apple Ecosystem Media Formats — HEIC, HEVC, ProRes](#2-apple-ecosystem-media-formats--heic-hevc-prores)
3. [Platform Format Specs — Current 2026 Requirements](#3-platform-format-specs--current-2026-requirements)
4. [YouTube Shorts + X Publishing APIs](#4-youtube-shorts--x-publishing-apis)
5. [Per-Day Content Templates and Seasonal Naming Automation](#5-per-day-content-templates-and-seasonal-naming-automation)
6. [Caption and Description Generation — Per Platform, Per Brand, Per Theme](#6-caption-and-description-generation--per-platform-per-brand-per-theme)
7. [Transcription Pipeline for Video Content](#7-transcription-pipeline-for-video-content)
8. [Multi-Brand Architecture — Keeping Typhon and Terp Tribe Separate](#8-multi-brand-architecture--keeping-typhon-and-terp-tribe-separate)
9. [Scheduling and Publishing Automation](#9-scheduling-and-publishing-automation)
10. [Storage and Archival for Season-Based Content](#10-storage-and-archival-for-season-based-content)

---

## 1. iCloud Access from Linux in 2026

### Current State
There are two credible Python-based options and one recommended hybrid path. There is no official Apple iCloud API for Linux — all approaches simulate the iCloud.com web session.

### Option A — `icloudpd` (iCloud Photos Downloader)
- **Project:** `icloud-photos-downloader.github.io/icloud_photos_downloader`
- **What it does:** Downloads the full iCloud Photo Library to a local directory. Watches for new photos, supports original quality, live photo pairs, HEIC, HEVC.
- **Auth:** Apple ID + password. 2FA is mandatory for all new accounts. icloudpd supports MFA via console prompt or a WebUI endpoint on a configurable port — the WebUI mode is the correct choice for a headless server.
- **2FA re-auth cadence:** Apple sets trust tokens to expire after approximately **2 months**. icloudpd can send an SMTP email notification when the token expires. This means Javier must reauthenticate every ~60 days. There is no workaround — this is Apple enforcing human-in-the-loop.
- **Critical blocker — Advanced Data Protection (ADP):** If Javier has ADP enabled on his Apple ID (Settings → iCloud → Advanced Data Protection), `icloudpd` **cannot access his library**. ADP uses end-to-end encryption with no server-side key, which disables iCloud.com web access entirely. ADP must be **disabled** for icloudpd to function. This is a hard, Apple-enforced limitation — not a bug in icloudpd.

### Option B — `pyicloud` (PyPI)
- **Project:** `pypi.org/project/pyicloud`
- **Lower-level:** pyicloud is the underlying library that icloudpd is built on. It exposes iCloud Drive, Photos, Contacts, Find My, etc. as Python objects.
- **Use case:** If Djinn needs to pull from iCloud Drive (not just Photos), pyicloud is the right layer. icloudpd only pulls Photos.
- **Same ADP blocker applies.**

### Option C — Recommended: iPhone iOS Shortcut → iCloud Drive → rclone pull (Hybrid Path)
Given that Djinn already has rclone + GDrive configured, this is the lowest-friction, most reliable approach:

1. **On iPhone:** Create an iOS Shortcut (Shortcuts app) that runs via automation (e.g., "When I arrive home" or "Every day at 23:00"):
   - `Get Latest Photos/Videos from Camera Roll` (last N items or since last run)
   - `Save File` → iCloud Drive → `Djinn/inbox/`
2. **On Salomon:** rclone sync `icloud-drive:Djinn/inbox/` → `~/djinn-media-inbox/` on a 5-min timer (same pattern as existing gdrive sync).

**Why this beats icloudpd for Djinn's use case:**
- No ADP conflict — the Shortcut copies files to a standard iCloud Drive folder, not Photo Library
- No 60-day re-auth loop on a server
- Works with or without ADP
- Javier controls what gets pushed (intentional, not everything in camera roll)
- rclone already has the iCloud Drive remote configured or can be configured with `rclone config` → "iCloud" → WebDAV backend → `https://idmsa.apple.com` (requires App-Specific Password)

**Important iOS limitation:** iOS Shortcuts cannot directly write to Google Drive folders via Files app — this is a known iOS restriction as of 2025/2026. The correct flow is **iCloud Drive → rclone** (not GDrive → rclone). Set up rclone's `icloud` remote using the WebDAV protocol.

### rclone iCloud Drive Configuration
```bash
rclone config
# Name: icloud
# Type: webdav
# URL: https://idmsa.apple.com  (rclone handles the iCloud WebDAV discovery)
# vendor: other
# user: <apple-id-email>
# pass: <app-specific-password>  # REQUIRED — regular password doesn't work headlessly
```
App-Specific Password: Generate at `appleid.apple.com` → Sign-In & Security → App-Specific Passwords.

### Realistic Failure Modes
| Approach | Failure Mode | Severity | Maintenance |
|----------|-------------|----------|-------------|
| icloudpd | 2FA token expiry every 60 days (requires manual re-auth) | Medium | 15 min/re-auth, 6x/year |
| icloudpd + ADP enabled | Silent — no photos downloaded, no error | **Critical** | Must disable ADP |
| iOS Shortcut + rclone iCloud | Shortcut won't run if iPhone is off; rclone sync needs app-specific password refresh | Low | Annual password refresh |
| iOS Shortcut → iCloud → rclone | iCloud WebDAV rate limits on large syncs | Low | Mitigated by incremental sync |

### Recommendation
**Use the iOS Shortcut → iCloud Drive → rclone path for Djinn.** Run the Shortcut nightly or when charging. Set rclone iCloud sync every 5 min on Salomon. Keep icloudpd available as a fallback if Javier wants full library sync.

**Blocker for Javier:** Must create an App-Specific Password at appleid.apple.com and add `ICLOUD_APP_PASSWORD` to `~/.config/djinn/icloud.env`.

---

## 2. Apple Ecosystem Media Formats — HEIC, HEVC, ProRes

### HEIC Still Images on Linux
`ffmpeg` in its default Ubuntu/Debian build **does not** decode HEIC because of H.265 patent licensing. The correct tool is `libheif`:

```bash
sudo apt install libheif-examples  # provides heif-convert, heif-dec
```

Convert in the pipeline:
```bash
heif-convert input.heic output.jpg
# Or batch:
for f in *.heic; do heif-convert "$f" "${f%.heic}.jpg"; done
```

For Ubuntu 22.04+, `libheif1` alone is not enough — you specifically need `libheif-examples` which ships `heif-convert`.

As of ffmpeg 6.1+ (static builds from johnvansickle.com or built from source), ffmpeg **can** decode HEIC/HEIF natively. But the Ubuntu/Debian package manager version is often older. Test with:
```bash
ffmpeg -i test.heic test.jpg 2>&1 | grep -i "heif\|hevc\|no such"
```
If it errors, fall back to `heif-convert`.

### HEVC (H.265) Video on Linux
iPhone video files are `.MOV` containers with HEVC encoding. ffmpeg decodes HEVC by default on Ubuntu via `libde265` or software decoder. No special packages needed.

Transcode HEVC → H.264 for all platforms:
```bash
ffmpeg -i input.mov -c:v libx264 -preset fast -crf 18 \
  -c:a aac -b:a 192k -movflags +faststart output.mp4
```
`crf 18` = near-lossless. Use `crf 23` for smaller files where quality matters less.

For 9:16 vertical and scaling:
```bash
ffmpeg -i input.mov -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -preset fast -crf 20 -c:a aac -b:a 192k output_9x16.mp4
```

### ProRes from iPhone
iPhone 15 Pro and later can shoot ProRes 422 LT. Apple's official position is that ffmpeg's ProRes implementation is "unauthorized" — but in practice, ffmpeg decodes ProRes 422 and ProRes 422 HQ without issue on Linux. **ProRes RAW** is not supported by ffmpeg. ProRes 4444 XQ is also unsupported for encoding but decodes.

For the Djinn pipeline, ProRes is just an input format — you're decoding it (reading it), not encoding it. Decoding works fine:
```bash
ffmpeg -i iphone_prores.mov -c:v libx264 -crf 18 -c:a aac output.mp4
```

If the file won't open, it's likely ProRes RAW (`.mov` + `.raw` pair) which ffmpeg cannot handle. Workaround: use iPhone setting to shoot HEVC instead of ProRes, or use the QuickTime conversion path on a Mac as a preprocessing step before sending to Salomon.

### Live Photos
An iPhone Live Photo is a `.HEIC` still + a `.MOV` (1–3 second clip) paired by filename. For social media:
- **Feed post:** use the `.HEIC` (still) — convert to `.jpg`
- **Reels/Stories:** use the `.MOV` (motion clip) — transcode to H.264
- **Best practice for Djinn:** ingest both, auto-detect the pair by filename, prefer `.MOV` for video projects and `.HEIC` for photo-only projects.

### Quality Recommendations for Cannabis Accessory + Maker Content
Macro shots and smoke effects have high-frequency detail that compression destroys. Use:
- **Export bitrate:** `crf 18` for H.264 (near-lossless). Target ~15–25 Mbps for 1080p vertical.
- **Two-pass VBR** if upload time allows: `-b:v 16M -maxrate 25M -bufsize 50M`
- **Frame rate:** Lock to 30fps (`-r 30`). Existing pipeline already does this.
- **Avoid upscaling** — if source is <1080p, letterbox/pillarbox rather than upscale.

---

## 3. Platform Format Specs — Current 2026 Requirements

### Master Table

| Platform | Resolution | Aspect Ratio | Duration | Max Size | Codec | Recommended Bitrate | Hashtags |
|----------|-----------|--------------|----------|----------|-------|--------------------|----|
| **Instagram Reels** | 1080×1920 | 9:16 | 3–180s | 4GB | H.264 + AAC | 15–25 Mbps | 3–5 |
| **Instagram Feed** | 1080×1350 | 4:5 | up to 60s | 4GB | H.264 + AAC | 15–25 Mbps | 3–5 |
| **Facebook Reels** | 1080×1920 | 9:16 | No limit (9:16 recommended) | 1GB | H.264 + AAC | 15–25 Mbps | 2–3 |
| **Facebook Feed** | 1080×1920 | 9:16 or any | No limit (June 2025: all videos = Reels) | 1GB | H.264 + AAC | 8–15 Mbps | 2–3 |
| **YouTube Shorts** | 1080×1920 | 9:16 | up to 180s | 256GB | H.264 + AAC | 8–15 Mbps | 3–5 |
| **X (Twitter) video** | 1080×1920 | 9:16 | up to 140s | 512MB | H.264 + AAC | 5–8 Mbps | 1–2 |

### Key 2025–2026 Changes
- **Instagram Reels:** Maximum extended from 90s to **3 minutes (180s)** — January 2025.
- **Instagram Feed:** A new **3:4 ratio (1080×1440)** was added in May 2025 as a supported portrait option.
- **Facebook:** As of **June 2025, ALL Facebook videos are now Reels** — no separate video vs. Reels distinction. No duration cap. 9:16 still recommended for best reach.
- **YouTube Shorts:** Extended from 60s to **3 minutes (180s)** in October 2024.
- **X video:** 140 second max. No recent format changes.

### Can One Master Export Serve All Platforms?
**Yes, with minor caveats.** A single `1080×1920 H.264 AAC, 15–25 Mbps, 30fps, under 90 seconds` export plays on all five platforms without rejection. Specific notes:
- X has a 512MB file size cap — at 25 Mbps, a 90s video is ~280MB. Safe.
- FB will accept any bitrate up to 1GB.
- IG will re-encode anything you send — export clean and high-bitrate to minimize IG's compression artifacts.
- YouTube Shorts: same specs, no issues.

**The exception:** X/Twitter captions must be separate (280 chars max). IG and FB captions are different lengths. You still need 4 caption variants, but one video file serves all platforms.

### Thumbnail Requirements
- Instagram: auto-generated from video. Can set a custom cover via the Graph API `cover_url` param.
- Facebook: same as IG — `thumb_url` param on video upload.
- YouTube: required separate upload via `thumbnails.set` API endpoint. `1280×720`, JPEG or PNG, max 2MB.
- X: auto-generated. No custom thumbnail API.

**Pipeline implication:** `djinn-media-reel` already generates a cover frame. That frame can be uploaded to IG/FB as the cover and to YouTube as the thumbnail.

---

## 4. YouTube Shorts + X Publishing APIs

### YouTube Data API v3 — Uploading Shorts

**How to upload:**
1. Create a Google Cloud Project → Enable YouTube Data API v3
2. Create OAuth 2.0 credentials (type: "Web application" or "Desktop app")
3. Do the one-time browser-based OAuth dance → get a refresh token
4. Store refresh token in `~/.config/djinn/youtube.env`
5. All future uploads use the refresh token to silently mint new access tokens

**Critical: No Service Accounts.** YouTube Data API explicitly does not support service account auth. The `NoLinkedYouTubeAccount` error will always appear if you try. The refresh token path is the only headless option.

**Upload flow:**
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds = Credentials(
    token=None,
    refresh_token=REFRESH_TOKEN,
    token_uri='https://oauth2.googleapis.com/token',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
youtube = build('youtube', 'v3', credentials=creds)

body = {
    'snippet': {
        'title': title,          # SEO title
        'description': description,
        'tags': tags_list,
        'categoryId': '26'       # How-to & Style — closest for maker
    },
    'status': {
        'privacyStatus': 'public',
        'selfDeclaredMadeForKids': False
    }
}
media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)
request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
response = None
while response is None:
    status, response = request.next_chunk()
```

**Quota:** `videos.insert` costs **1600 units** per upload. Default quota is **10,000 units/day**. That's 6 uploads/day before hitting the cap. For 7 posts/brand/week = 1 upload/day per brand = 2 uploads/day total. Well within limits.

**Thumbnail upload:**
```python
youtube.thumbnails().set(
    videoId=video_id,
    media_body=MediaFileUpload(cover_path, mimetype='image/jpeg')
).execute()
```

**Making a video a Short:** It's automatic. If the video is 9:16 and ≤ 3 minutes, YouTube classifies it as a Short. No special API flag needed.

**Gotcha — cannabis content:** YouTube's cannabis policy bans monetization for drug-related content but does **not** ban uploads. Glass accessories and functional art 3D prints are generally fine. Avoid explicit drug use language in titles/descriptions. "Functional art," "maker," "artisan glass" language is preferred. The channel will not qualify for monetization on these videos, but they will stay up.

### X (Twitter) API v2 — Video Upload

**Tier reality in 2026:**
- **Free tier:** Allows 500 posts/month at app level via OAuth 2.0. Media upload endpoint (`POST /2/media/upload`) is available on Free but has been inconsistently documented. Community testing shows it's possible with OAuth 2.0 but erratic.
- **Basic tier:** $200/month ($175/year). 3,000 posts/month at user level, 50,000 at app level. Clean access to media upload endpoints.
- **Cost verdict:** For 7 posts/week × 2 brands = 60 posts/month — Free tier is technically sufficient on volume, but media upload reliability at Free is a known pain point. **Recommend: start with Free, upgrade to Basic only if media uploads fail consistently.**

**Video upload flow (v1.1 media endpoint, required for video):**
```python
import tweepy
# OAuth 1.0a is required for media uploads (v1.1 endpoint)
auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret,
    access_token, access_token_secret
)
api = tweepy.API(auth)

# Step 1 — upload video (chunked for files >5MB)
media = api.media_upload(
    filename=video_path,
    media_category='tweet_video'  # required for video
)
# Step 2 — poll until processing complete
while True:
    status = api.get_media_upload_status(media.media_id)
    if status.processing_info['state'] == 'succeeded':
        break
    time.sleep(status.processing_info.get('check_after_secs', 5))

# Step 3 — post tweet with media
client = tweepy.Client(consumer_key=..., consumer_secret=..., ...)
client.create_tweet(text=caption, media_ids=[media.media_id])
```

**Note:** The v1.1 media upload deprecation warning that appeared in 2025 was clarified — video uploads remain on the v1.1 endpoint. The deprecated endpoint was for image uploads only, and even that was extended. Use `tweepy` v4.x which handles both.

**X cannabis policy:** X is significantly less restrictive than IG/Meta on cannabis-adjacent content. "Functional glass," pipe accessories, and 3D printed smoking accessories are not actively policed. Standard NSFW flag is not required for product photography. Use normal product language.

---

## 5. Per-Day Content Templates and Seasonal Naming Automation

### Episode and Week Numbering Convention
For Terp Tribe Clouds Season 6, the recommended convention:
- **Season (S):** Global counter, increments when Javier declares a new season. Current: 6.
- **Week (W):** Week number within the current season. Starts at 1 on the first Monday of the season, increments every 7 days.
- **Episode (E):** Total number of pieces of content published (cumulative within the season, not per-week). E1 = first content day of S6, E2 = second, etc.

This gives filenames like `S6_E14_W2_Wax-Wednesday` (Season 6, 14th piece of content, 2nd week of season, Wednesday's theme).

**Alternate simpler approach:** If week-within-season tracking is too complex, use day-of-week ordinal within season: E = (week_number - 1) × 7 + day_index. This makes E completely derivable without a separate episode counter.

### Storage Architecture
```python
# Recommended: SQLite per brand
# ~/.local/share/djinn/brands/terp-tribe.db
# ~/.local/share/djinn/brands/typhon-forge.db

CREATE TABLE content_days (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,           -- 'terp-tribe' | 'typhon-forge'
    season INTEGER NOT NULL,
    week_in_season INTEGER NOT NULL,
    episode INTEGER NOT NULL,       -- auto-incremented per brand per season
    content_day TEXT NOT NULL,      -- 'monday' ... 'sunday'
    theme_name TEXT NOT NULL,       -- 'Wax Wednesday', 'Network Monday', etc.
    folder_slug TEXT NOT NULL,      -- 'S6_E14_W2_Wax-Wednesday'
    project_id TEXT,                -- links to djinn-media manifest
    status TEXT DEFAULT 'pending',  -- pending | in_progress | done | published
    created_at TEXT DEFAULT (datetime('now'))
);
```

### Auto-Folder Creation on Ingest
Add a `djinn-content-day-init` command (or integrate into `djinn-media-ingest`):

```bash
djinn-content-day-init --brand terp-tribe --date 2026-06-04
# → Looks up Wednesday theme for Terp Tribe
# → Queries DB for current season/week/episode counters
# → Creates: ~/Terp\ Tribe/Wednesday/S6_E14_W2_Wax-Wednesday/
# → Creates subfolders: videos/ pics/ done/
# → Writes brand_context.json to done/ (used by caption agent)
# → Inserts row into content_days table
# → Prints: "S6_E14_W2_Wax-Wednesday ready at ~/Terp Tribe/Wednesday/S6_E14_W2_Wax-Wednesday/"
```

### Brand Config Files (per-brand, not per-instance)
```json
// ~/.config/djinn/brands/terp-tribe.json
{
  "brand_name": "Terp Tribe Clouds",
  "brand_slug": "terp-tribe",
  "season": 6,
  "season_start_date": "2026-01-06",
  "base_folder": "~/Terp Tribe",
  "telegram_bot": "@djinn_terptribeclouds_bot",
  "content_schedule": {
    "monday":    { "theme": "Network Monday",      "tone": "community" },
    "tuesday":   { "theme": "Eve Life Tuesday",    "tone": "lifestyle" },
    "wednesday": { "theme": "Wax Wednesday",       "tone": "product-focused" },
    "thursday":  { "theme": "Terpy Disposables",  "tone": "product-focused" },
    "friday":    { "theme": "Flower Friday",       "tone": "chill" },
    "saturday":  { "theme": "Sesh Out Saturday",   "tone": "community" },
    "sunday":    { "theme": "Slow-Mo Sundays",     "tone": "cinematic" }
  },
  "platform_credentials": "~/.config/djinn/meta-terp-tribe.env",
  "caption_persona": "Terp Tribe voice: cannabis community, stoner culture, lifestyle. Warm, inclusive, slightly irreverent. Never clinical. 420-safe hashtags only.",
  "db_path": "~/.local/share/djinn/brands/terp-tribe.db"
}
```

```json
// ~/.config/djinn/brands/typhon-forge.json
{
  "brand_name": "Typhon's Forge",
  "brand_slug": "typhon-forge",
  "season": 1,
  "season_start_date": "2026-01-01",
  "base_folder": "~/Typhon's Forge",
  "telegram_bot": "@djinn_bughunter_bot",
  "content_schedule": {
    "monday":    { "theme": "Maker Monday",    "tone": "process" },
    "tuesday":   { "theme": "Tech Tuesday",    "tone": "technical" },
    "wednesday": { "theme": "Weld Wednesday",  "tone": "craft" },
    "thursday":  { "theme": "Print Thursday",  "tone": "product-reveal" },
    "friday":    { "theme": "Forge Friday",    "tone": "satisfying-process" },
    "saturday":  { "theme": "Shop Saturday",   "tone": "behind-scenes" },
    "sunday":    { "theme": "Silent Sunday",   "tone": "cinematic" }
  },
  "platform_credentials": "~/.config/djinn/meta-typhon.env",
  "caption_persona": "Typhon's Forge voice: dark maker aesthetic, precision craft, functional art. Direct. Technical but accessible. No filler.",
  "db_path": "~/.local/share/djinn/brands/typhon-forge.db"
}
```

### `done/` Folder Population Sequence
Steps that can run in parallel vs must be sequential:

```
1. djinn-media-ingest [SEQUENTIAL — must run first to create manifest]
2. djinn-media-reel [SEQUENTIAL — needs ingested files]
3. [PARALLEL block]
   3a. djinn-media-publish-prep [generates captions, reads TREND-SIGNAL.md]
   3b. faster-whisper transcription [reads reel output]
   3c. cover frame extraction [ffmpeg from reel]
4. [SEQUENTIAL — needs 3a complete]
   djinn-media-publish [posts to Meta]
5. [SEQUENTIAL — needs 3b complete]
   subtitle burn-in (optional)
6. [SEQUENTIAL — needs 3a + YouTube credentials]
   youtube upload
7. [SEQUENTIAL — needs 3a + X credentials]
   x post
```

The `done/` folder is fully populated after steps 3a–3c and before publishing. Publishing runs separately.

---

## 6. Caption and Description Generation — Per Platform, Per Brand, Per Theme

### Prompt Engineering Pattern for Platform Variants
The caption agent should generate all four variants in one LLM call (more efficient, better cross-platform coherence):

```python
prompt = f"""
You are the caption writer for {brand_name}. Brand voice: {brand_config['caption_persona']}

Content context:
- Theme: {theme_name} ({tone})
- Transcript: {transcript_text[:500]}
- Trending topics: {trend_signal['trending_topics']}
- Hook style: {trend_signal['recommended_hook_style']}
- Hashtag bank: {hashtag_bank[-20:]}

Rules:
- NEVER use #weed #cannabis #420 #marijuana or any variant
- Use cannabis-safe language: "botanical", "herb", "flower", "terp", "dab", "concentrate", "functional art"
- Instagram: 150–220 words, 3–5 hashtags from bank
- Facebook: first 2 sentences of IG caption + max 3 hashtags
- YouTube: Title (under 70 chars, SEO-optimized) + Description (first 125 chars = hook visible before "more") + Tags list (10–15 keywords)
- X/Twitter: under 280 chars including 1–2 hashtags, punchy, no filler

Respond ONLY with valid JSON:
{{
  "ig": "full caption with hashtags",
  "fb": "shortened caption with 2-3 hashtags",
  "yt_title": "YouTube title",
  "yt_description": "YouTube description (multi-line, includes CTA)",
  "yt_tags": ["tag1", "tag2", ...],
  "x": "tweet text under 280 chars"
}}
"""
```

### Per-Theme Tone Injection
Each content day has a defined tone (in `content_schedule`). Inject it directly:

| Theme | Tone Descriptor | Caption Opening Pattern |
|-------|----------------|------------------------|
| Network Monday | Community-first, call to action | "Who in the tribe is doing this…" |
| Wax Wednesday | Product-focused, sensory | "When the dab hits just right…" |
| Slow-Mo Sundays | Cinematic, no text wall | Single evocative sentence + 2 tags |
| Flower Friday | Chill, relatable | Short, lowercase-aesthetic, emoji-light |
| Forge Friday | Process satisfaction | "From raw filament to this in 4 hours." |
| Print Thursday | Product reveal | Lead with the product name + spec |

These patterns live in the brand config as `opening_pattern` per day. The caption prompt injects them as "Suggested opening: [pattern]" — the model can use or ignore, but it calibrates tone immediately.

### YouTube Description Structure
```
[TITLE — repeat keyword-rich version]

[Hook paragraph — 1–2 sentences visible before "more"]

[3–5 sentence body — what the video shows, why it matters]

🔗 Shop: [link]
📸 Instagram: @[handle]

Chapters:
00:00 Intro
[auto-generated from transcript if multiple segments]

Tags: 3d printing, functional art, [day theme keyword], [brand keyword], ...
```

### X/Twitter 280-Char Compression
The best pattern for auto-generating punchy X captions from longer IG captions:
```python
# After generating IG caption, pass to a compression prompt:
x_prompt = f"""
Compress this Instagram caption to under 250 characters for X/Twitter.
Keep the most compelling idea. Remove hashtags except 1–2 maximum.
Original: {ig_caption}
Respond with ONLY the compressed tweet text.
"""
```
Use a smaller/faster model for this step (qwen2.5:7b is fine — it's a compression task, not a creative one).

---

## 7. Transcription Pipeline for Video Content

### Recommended Model Size for Short-Form Social Content
For clips under 90 seconds on Salomon hardware (local CPU, no dedicated GPU for transcription):

| Model | Size | CPU Speed (60s clip) | Accuracy | Recommendation |
|-------|------|---------------------|----------|----------------|
| `tiny` | 75MB | ~10s | 85% | Too low accuracy |
| `base` | 142MB | ~15s | 90% | Acceptable for hashtag extraction |
| `small` | 466MB | ~30s | 94% | **Recommended for Djinn** |
| `medium` | 1.5GB | ~45s | 96% | Use for hero content needing high accuracy |
| `large-v3-turbo` | 1.6GB | ~19s on GPU | 98% | Use if Salomon has VRAM to spare |

For 60–90 second social clips where Ollama phi4:14b is already running in memory: use `small` to avoid RAM contention. Switch to `medium` for any piece you're burning subtitles into (quality matters for burn-in).

**faster-whisper command:**
```python
from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(video_path, beam_size=5, language="en")
```

### Output to `done/` Folder
Write both:
```
done/transcription.txt     ← plain text, full transcript, one line per segment
done/transcription.srt     ← SRT file for subtitle burn-in or IG caption overlay
```

SRT format:
```
1
00:00:00,000 --> 00:00:03,450
This is the first line of text.

2
00:00:03,500 --> 00:00:07,200
And this is the second.
```

### Should Transcription Feed Caption Generation?
**Yes — include it.** Pass the first 500 characters of `transcription.txt` into the caption prompt as "Transcript snippet." This grounds the caption in the actual content rather than just the job metadata. It dramatically improves specificity on product demos and process videos.

### Auto-Subtitle Burn-In (9:16 Reels Style)
Best practice for vertical short-form: **centered, lower-third position**, large readable font, bold + shadow:

```bash
ffmpeg -i reel.mp4 \
  -vf "subtitles=done/transcription.srt:force_style='FontSize=28,Fontname=Arial,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,Alignment=2,MarginV=120'" \
  -c:v libx264 -preset fast -crf 20 -c:a copy \
  done/reel_subtitled.mp4
```

Parameters:
- `Alignment=2` = centered bottom
- `MarginV=120` = 120px from bottom (avoids IG/TikTok UI overlap)
- `FontSize=28` = readable on mobile
- White text, black outline for readability over any background

**For smoke/dark backgrounds:** add `BackColour=&H40000000,BorderStyle=4` to add a semi-transparent background box behind text.

The subtitle burn-in version goes into `done/reel_subtitled.mp4`. The standard `reel.mp4` stays clean. Javier decides which version to post.

---

## 8. Multi-Brand Architecture — Keeping Typhon and Terp Tribe Separate

### Single Backend, Brand-Aware Routing
The correct pattern is **one pipeline with brand-aware routing via config**, not two pipeline instances. This prevents code drift between brands and makes adding a third brand trivial.

Every `djinn-media-*` command that needs brand-specific behavior takes a `--brand <slug>` flag:
```bash
djinn-content-day-init --brand terp-tribe --date 2026-06-04
djinn-media-publish-prep <project_id> --brand terp-tribe
djinn-media-publish <project_id> --brand terp-tribe --platform ig
```

The brand flag causes the script to load `~/.config/djinn/brands/{brand}.json` and use that brand's credentials, voice, folder, and DB.

### Credential Isolation
Each brand has its own credential file. **Never mix credentials between brands.**

```
~/.config/djinn/meta-terp-tribe.env    (chmod 600)
  META_PAGE_TOKEN_TT=<terp-tribe page token>
  IG_USER_ID_TT=<terp tribe IG user ID>
  FB_PAGE_ID_TT=<terp tribe FB page ID>
  YT_REFRESH_TOKEN_TT=<terp tribe YT refresh token>
  X_ACCESS_TOKEN_TT=<terp tribe X token>
  X_ACCESS_SECRET_TT=<terp tribe X secret>

~/.config/djinn/meta-typhon.env        (chmod 600)
  META_PAGE_TOKEN_TF=<typhon page token>
  IG_USER_ID_TF=<typhon IG user ID>
  FB_PAGE_ID_TF=<typhon FB page ID>
  YT_REFRESH_TOKEN_TF=<typhon YT refresh token>
  X_ACCESS_TOKEN_TF=<typhon X token>
  X_ACCESS_SECRET_TF=<typhon X secret>
```

The publish script loads the right env file based on `brand_config['platform_credentials']`.

### Adding a Third Brand
To add Brand 3:
1. Create `~/.config/djinn/brands/brand3.json` (copy template, fill fields)
2. Create `~/.config/djinn/meta-brand3.env` (fill credentials)
3. Run `djinn-content-day-init --brand brand3 --setup` (creates DB, base folder)

No code changes. Zero downtime for existing brands.

### Folder Tree
```
~/Terp Tribe/
  Monday/S6_E1_W1_Network-Monday/
    videos/
    pics/
    done/
      reel.mp4
      cover.jpg
      caption_ig.txt
      caption_fb.txt
      caption_yt.txt
      caption_x.txt
      transcription.txt
      transcription.srt
      brand_context.json   ← brand name, theme, season/episode/week slugs
  Wednesday/S6_E3_W1_Wax-Wednesday/
    ...

~/Typhon's Forge/
  Monday/S1_E1_W1_Maker-Monday/
    ...
```

### Trend Signals Per Brand
`TREND-SIGNAL.md` is currently global (one file for all Djinn). For two brands with different niches (cannabis lifestyle vs maker), consider writing brand-scoped trend signals:
- `djinn/social/TREND-SIGNAL-terp-tribe.md`
- `djinn/social/TREND-SIGNAL-typhon.md`

`djinn-trend-agent` gets a `--brand` flag that queries brand-appropriate keywords and writes the brand-scoped signal file. Each caption agent reads its own brand's signal.

---

## 9. Scheduling and Publishing Automation

### Optimal Posting Times in 2026

**Instagram (based on Buffer analysis of 9.6M posts, May 2026):**
- Best overall: **Thursday 9am, Wednesday 12pm, Wednesday 6pm**
- For cannabis/maker niche specifically: **Tuesday–Thursday, 11am–2pm local time** performs well for product + process content
- Weekends remain viable but lower peak engagement
- Consistency > perfect timing — daily posts at any reasonable hour outperform sporadic posts at optimal times

**Facebook:** Mirrors Instagram cadence but 30–60 min later tends to catch secondary waves.

**YouTube Shorts:** Algorithm is less time-dependent — Shorts circulate in the feed for days. Post within the 8am–6pm window for initial push, but day-of-week matters less than IG.

**X/Twitter:** 8am–10am local time for maker/craft content. X cannabis-adjacent accounts see evening engagement (8pm–10pm) from recreational audience.

### Does Scheduling via Third-Party Penalize Reach?
Meta (IG/FB) has explicitly stated that third-party API posts are treated identically to native posts since 2022. This holds in 2026. **No penalty for API-posted content.** The persistent myth is debunked.

YouTube's algorithm does not penalize scheduled uploads vs instant uploads.

X: No known scheduling penalty.

### Third-Party Schedulers vs. DIY Cron

**Publer (recommended if budget exists):**
- **Free tier:** 3 social accounts (not enough for 2 brands × 4 platforms = 8 accounts)
- **Professional:** $5/account/month (~$40/month for 8 accounts annual)
- **Business:** $10/account/month for analytics + best-time features
- **Has a REST API** (`publer.com/help/en/article/publer-api-for-marketers`) — can be triggered programmatically to schedule posts from Djinn
- **Supports:** IG, FB, YouTube, X + 9 other platforms
- **Verdict for 2 brands:** ~$40–80/month for full scheduling + analytics

**DIY cron scheduler in Djinn (recommended for zero cost):**
Build `djinn-publish-scheduler` — reads `done/` folders across both brands, finds unpublished content with `status = "kit_ready"`, checks configured post time per brand per day, queues and fires `djinn-media-publish` at the right moment.

```python
# ~/.config/djinn/publish-schedule.json
{
  "terp-tribe": {
    "monday":    "10:30",
    "wednesday": "11:00",
    "friday":    "10:00"
    // ... etc
  },
  "typhon-forge": {
    "monday":    "11:00",
    "thursday":  "12:00"
  }
}
```

Timer: `djinn-publish-scheduler.timer` — runs every 15 minutes, checks if any brand/day has content ready to post at the current time. If yes, fires the publish chain.

**Recommendation:** Build the DIY scheduler first. It costs nothing and keeps the system self-contained. Switch to Publer if/when the analytics and auto-scheduling features justify the cost.

---

## 10. Storage and Archival for Season-Based Content

### Volume Estimate
Full season:
- 7 content days/week × 10 weeks = 70 pieces of content
- Per piece: ~1 raw video (500MB–2GB HEVC), ~1 reel.mp4 (~150MB H.264), captions, thumbnails
- Rough total: **50–200GB per brand per season of raw + processed content**

Salomon's `/mnt/archive` (Extreme SSD reformatted to ext4, post-TASK-044) is the Tier 2 cold archive. Local SSD (Salomon home drive) is Tier 1 working storage.

### Tiering Strategy

| Tier | Location | Content | Retention |
|------|---------|---------|-----------|
| **Tier 1** | `~/Terp Tribe/` (Salomon home) | Current season active content | Until kit_ready + published |
| **Tier 2** | `/mnt/archive/media-files/terp-tribe/S6/` | Published content, raw footage | 2 seasons rolling |
| **Tier 3** | `gdrive:Typhons-Forge/archive/terp-tribe/S6/` | All seasons, permanent | Forever |

Archive script: `djinn-content-archive --brand terp-tribe --season 6` — moves `done/` folders from Tier 1 → Tier 2, syncs Tier 2 → Tier 3 via rclone.

### Queryable Archive with SQLite Index
Instead of XMP sidecars (video XMP support in Linux tools is inconsistent), use the brand SQLite DB as the queryable index:

```sql
-- Find all Wax Wednesday content from Season 6
SELECT folder_slug, project_id, status, created_at
FROM content_days
WHERE brand = 'terp-tribe'
  AND season = 6
  AND content_day = 'wednesday'
ORDER BY episode ASC;
```

Add `archive_path` and `gdrive_url` columns to the `content_days` table so any piece of content is resolvable in < 1 second without scanning the filesystem.

XMP sidecars are still worth writing for photo files (`.HEIC` → `.HEIC.xmp`) because tools like Lightroom and digiKam will read them. Use `exiftool` for writing:
```bash
exiftool -Title="S6_E3_W1_Wax-Wednesday" \
         -Keywords="terp-tribe,season-6,wax-wednesday" \
         -Description="Wax Wednesday S6E3" \
         done/cover.jpg
```

### Finding Content Without a Full Media Server
The folder naming convention is the index. Add one helper command:
```bash
djinn-content-find --brand terp-tribe --theme "wax" --season 6
# Queries SQLite, prints matching folder_slug + archive_path
```

No Plex, no Jellyfin, no media server needed. The DB is the catalog.

---

## Open Build Questions for Claude
1. **iCloud intake blocker:** Javier must create an App-Specific Password and configure rclone's iCloud WebDAV remote. Cannot build the iOS Shortcut → Salomon sync path without this credential in place.
2. **HEIC conversion dependency:** `sudo apt install libheif-examples` must be run on Salomon before the pipeline handles iPhone photos.
3. **YouTube one-time OAuth:** Must be done in a browser once. After that, refresh token is permanent until revoked. Add `YT_REFRESH_TOKEN` to brand credential files.
4. **X API media upload reliability:** Test on Free tier first. Budget $200/month for Basic only if Free media uploads fail.
5. **ProRes handling:** Advise Javier to shoot HEVC instead of ProRes for Djinn-destined content. ProRes RAW from iPhone cannot be decoded by ffmpeg.
6. **Brand schedule for Typhon's Forge:** The config template above uses placeholder theme names. Javier to confirm actual day themes before `djinn-content-day-init` is built.
7. **Terp Tribe Season 6 start date:** Used to compute week_in_season. Confirm date.
8. **AA safe language confirmation:** Cannabis-safe language list in brand configs — confirm "terp", "dab", "concentrate", "functional art", "botanical", "herb", "flower" are all approved for use. Confirm what words to never use.

---

*Researched and written by Marcus | 2026-06-01 | Task: TASK-060*
*Claude builds from this document. Do not paste into chat.*
