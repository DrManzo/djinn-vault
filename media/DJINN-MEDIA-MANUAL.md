================================================================================
                    DJINN MEDIA — COMPLETE PIPELINE HANDBOOK
        Ingest → Edit → Caption → Publish → Analytics → Trend Loop
================================================================================
Version: 1.0 | Last updated: 2026-06-09 | Maintained by: DrManzo / Marcus

> Full standalone operator handbook for the Djinn Media pipeline.
> Absorbs MEDIA-STACK.md and DJINN-MEDIA-STATUS.md.
> An operator or agent who has never seen the system should be able to run,
> troubleshoot, and extend the full pipeline using only this document.

================================================================================
TABLE OF CONTENTS
================================================================================

  1.  What Djinn Media Is
  2.  Architecture Overview
      2.1  Two-Layer Design
      2.2  Full Pipeline Diagram
  3.  The 14-Agent Roster
  4.  CLI Command Reference
  5.  Telegram / Discord Triggers
  6.  LUT Color Grading System
  7.  Project Structure
  8.  Hashtag Bank
  9.  Reference Library & Vision QC
  10. Publish Output Format
  11. Instagram / Platform Specs
  12. Systemd Services & Timers
  13. Key File Paths & Config
  14. Meta API Credentials Setup
  15. Layer 1 — Intelligence Pipeline
      15.1  djinn-trend-agent (TASK-019)
      15.2  djinn-social-analyst
      15.3  djinn-meta-token-refresh
  16. Current Status & Outstanding Work
  17. Common Workflows (Step-by-Step)
  18. Troubleshooting
  19. Hard Rules

================================================================================
1. WHAT DJINN MEDIA IS
================================================================================

Djinn Media is the social production layer of Djinn OS. It takes raw footage
from Javier's iPhone, processes it through a multi-step automated pipeline,
and publishes finished Reels to Instagram and Facebook — fully automated.
No human steps are required between file drop and published post.

Two-sentence version:
  Drop raw footage into the inbox. The system handles color grading, captioning,
  thumbnail generation, QA, caption writing, hashtag selection, Drive upload,
  and direct Meta Graph API publishing — end to end.

Primary output: Instagram Reels + Facebook Reels for Typhon's Forge brand
  (gothic industrial 3D printing / cannabis accessories maker content).

The pipeline runs on Salomon (192.168.1.225). All tools are at ~/.local/bin/.
All models are local Ollama — no external AI API costs for production.

================================================================================
2. ARCHITECTURE OVERVIEW
================================================================================

────────────────────────────────────────────────────────────────────────────────
2.1  TWO-LAYER DESIGN
────────────────────────────────────────────────────────────────────────────────

  Layer 1 — INTELLIGENCE (runs on schedule, feeds into Layer 2)
    What it does: polls trends, manages hashtag bank, pulls own analytics,
    writes TREND-SIGNAL.md and HASHTAG-BANK.md.
    Why it matters: every caption and hashtag set is informed by what is
    actually performing — not static templates.

  Layer 2 — PRODUCTION (runs per job, triggered by Javier or inbox watcher)
    What it does: ingest → edit → caption → thumbnail → QA → publish-prep
    → Meta Graph API publish.
    Reads from: TREND-SIGNAL.md + HASHTAG-BANK.md (Layer 1 outputs).

────────────────────────────────────────────────────────────────────────────────
2.2  FULL PIPELINE DIAGRAM
────────────────────────────────────────────────────────────────────────────────

  iPhone footage
        │
        ▼
  gdrive:Typhons-Forge/inbox/
        │  (rclone sync every 5 min)
        ▼
  ~/djinn-media-inbox/
        │  (djinn-media-drop watcher — inotifywait / poll fallback)
        ▼
  djinn-media-ingest --job-name <slug>
        │  Creates project in ~/.local/share/djinn-media/projects/
        │  Writes manifest.json, stores --notes
        ▼
  ┌─────────────────────────┬──────────────────────────────────────┐
  │ LAYER 2 (per job)        │ LAYER 1 (scheduled, feeds captions)   │
  │                          │                                        │
  │  photo path:             │  djinn-trend-agent [TASK-019]          │
  │    djinn-media-photo     │  ← Firecrawl search/scrape             │
  │                          │  ← Printables RSS                      │
  │  video path:             │  ← Apify IG (optional)                 │
  │    djinn-media-reel      │  ← Ollama phi4:14b synthesis           │
  │    (--combine to concat  │  → TREND-SIGNAL.md (every 6h)          │
  │     multiple clips)      │  → HASHTAG-BANK.md (weekly)            │
  │                          │                                        │
  │  djinn-media-caption     │  djinn-social-analyst (daily 00:30 UTC)│
  │  (faster-whisper STT     │  ← Meta Graph API own post metrics     │
  │   → SRT → burn)          │  → analytics/YYYY-MM-DD.json           │
  │                          │  → TREND-SIGNAL.md (feedback loop)     │
  │  djinn-media-repurpose   │                                        │
  │  (long-form → clips)     │  djinn-meta-token-refresh (monthly)    │
  │                          │  ← exchanges page token (60-day)       │
  │  djinn-media-thumbnail   │  ← writes back to meta.env            │
  │  (vision frame scoring   │                                        │
  │   + compositing)         │                                        │
  │                          │                                        │
  │  djinn-media-qa          │                                        │
  │  (platform spec check)   │                                        │
  │                          │                                        │
  │  djinn-media-publish-prep│ ← reads TREND-SIGNAL.md [TASK-020]    │
  │  (caption gen, hashtags, │    + HASHTAG-BANK.md                   │
  │   GDrive upload,         │                                        │
  │   Discord notify)        │                                        │
  └─────────────────────────┴──────────────────────────────────────┘
        │
        ▼
  djinn-media-publish
        │  IG: create container → upload bytes → poll FINISHED → publish
        │  FB: init → upload → finish
        ▼
  Instagram Reel + Facebook Reel
        │
        ▼
  publish-log.json + Telegram notification

================================================================================
3. THE 14-AGENT ROSTER
================================================================================

  ┌──────────────────────────────┬──────────────────┬──────────────────────────────────────┐
  │ Agent                        │ Model            │ Role                                  │
  ├──────────────────────────────┼──────────────────┼──────────────────────────────────────┤
  │ content-orchestrator         │ qwen2.5:7b       │ Routes jobs to specialist agents      │
  │ ingest-agent                 │ qwen2.5:7b       │ Creates project structure + manifest  │
  │ video-edit-agent             │ qwen2.5:7b       │ ffmpeg Reel export, LUT grade, combine│
  │ photo-edit-agent             │ qwen2.5:7b       │ ffmpeg + LUT photo edit, vision QC    │
  │ caption-agent                │ qwen2.5:7b       │ faster-whisper STT → SRT → burn       │
  │ repurpose-agent              │ qwen2.5:7b       │ Long-form → Reel clips                │
  │ thumbnail-agent              │ qwen2.5:7b       │ Frame scoring + cover compositing     │
  │ publish-prep-agent           │ qwen2.5:7b /     │ Captions, hashtags, Drive upload,     │
  │                              │ phi4:14b         │ Discord notify                        │
  │ qa-agent                     │ qwen2.5:7b       │ Platform spec compliance gate         │
  │ hashtag-agent                │ phi4:14b         │ Hashtag bank management + research    │
  │ style-scraper-agent          │ qwen2.5:7b       │ DuckDuckGo aesthetic reference scraper│
  │ main                         │ qwen2.5:7b       │ General purpose                       │
  │ law                          │ qwen2.5:7b       │ General purpose                       │
  │ coder                        │ qwen2.5:7b       │ General purpose                       │
  └──────────────────────────────┴──────────────────┴──────────────────────────────────────┘

  Vision QC: llama3.2-vision:11b called via REST from photo-edit + thumbnail
  agents for frame scoring. On demand — not always warm.

  Caption model routing logic:
    Draft present (quoted text in --notes, e.g. --notes ""like this""):
      → qwen2.5:7b polish pass
    No draft:
      → phi4:14b cold generation

================================================================================
4. CLI COMMAND REFERENCE
================================================================================

All tools at ~/.local/bin/ — pre-approved for all OpenClaw agents.

────────────────────────────────────────────────────────────────────────────────
INGEST
────────────────────────────────────────────────────────────────────────────────

  djinn-media-ingest <path> [--notes "text"] [--job-name <slug>]

    Creates a new project from a file or folder.
    Writes manifest.json, creates project directory structure.
    --notes: optional context passed into caption generation
    --job-name: custom slug for the project ID

  Example:
    djinn-media-ingest ~/Videos/forge-session.mp4 --notes "new filament spool reveal" --job-name forge-spool-01

────────────────────────────────────────────────────────────────────────────────
PHOTO EDITING
────────────────────────────────────────────────────────────────────────────────

  djinn-media-photo <project_id> [--style forge|clean|moody|raw] [--format feed|story|both]

    Applies LUT color grading to photos.
    Exports feed (1080×1080 and 1080×1350) and/or story (1080×1920).
    Runs vision QC scoring after export.
    Default style: forge. Default format: both.

  Example:
    djinn-media-photo forge-spool-01 --style forge --format feed

────────────────────────────────────────────────────────────────────────────────
VIDEO / REEL
────────────────────────────────────────────────────────────────────────────────

  djinn-media-reel <project_id> [--style forge|clean|moody|raw] [--combine] [--duration 90] [--start 0]

    Exports a 9:16 Reel (1080×1920, H.264+AAC, ≤90s).
    Applies LUT color grading via ffmpeg lut3d filter.
    --combine: concatenate all raw clips in upload order before grading
    --duration: max clip length in seconds (default 90)
    --start: trim start offset in seconds
    Default style: forge.

  Example:
    djinn-media-reel forge-spool-01 --style forge --combine

────────────────────────────────────────────────────────────────────────────────
CAPS / SUBTITLES
────────────────────────────────────────────────────────────────────────────────

  djinn-media-caption <project_id> [--model medium|large-v3] [--burn]

    Transcribes audio using faster-whisper → writes SRT to captions/.
    --burn: burns subtitles directly into the video export
    Default model: medium (faster). Use large-v3 for accuracy-critical content.

  Example:
    djinn-media-caption forge-spool-01 --model medium --burn

────────────────────────────────────────────────────────────────────────────────
REPURPOSE
────────────────────────────────────────────────────────────────────────────────

  djinn-media-repurpose <project_id> [--clips 5]

    Slices long-form content (>3 min) into 3–10 Reel-ready clips.
    --clips: target number of output clips (default 5)

  Example:
    djinn-media-repurpose forge-workshop-vod --clips 6

────────────────────────────────────────────────────────────────────────────────
THUMBNAIL
────────────────────────────────────────────────────────────────────────────────

  djinn-media-thumbnail <project_id> [--text "title"] [--style bold|band]

    Uses llama3.2-vision to score frames (1–10).
    Composites best frame + optional text overlay.
    Exports: 1280×720, 1080×1080, 1080×1920.
    --style bold: large centered text. --style band: text band at bottom.

  Example:
    djinn-media-thumbnail forge-spool-01 --text "New filament drop" --style band

────────────────────────────────────────────────────────────────────────────────
QA GATE
────────────────────────────────────────────────────────────────────────────────

  djinn-media-qa <project_id>

    Checks all exports against platform specs:
    resolution, codec, duration, file size, aspect ratio.
    Fails loudly — does not allow publish-prep on a failed QA.

────────────────────────────────────────────────────────────────────────────────
PUBLISH PREP
────────────────────────────────────────────────────────────────────────────────

  djinn-media-publish-prep <project_id>

    Generates caption (draft polish or cold generate via phi4:14b).
    Validates and selects hashtags from bank (strips hallucinated tags).
    Uploads to Google Drive: gdrive:Typhons-Forge/posts/<project_id>/
    Posts Discord notification to #media-status and #post-ready.
    Writes: caption_feed.txt, caption_reel.txt, POST.txt, instagram_post.md

────────────────────────────────────────────────────────────────────────────────
PUBLISH (META GRAPH API)
────────────────────────────────────────────────────────────────────────────────

  djinn-media-publish <project_id> [--dry-run]

    Publishes directly to Instagram and Facebook via Meta Graph API.
    Instagram: resumable upload → create container → poll FINISHED → publish
    Facebook:  init → upload → finish
    --dry-run: prints full plan, makes no API calls.
    Requires: ~/.config/djinn/meta.env (see §14)

  Caption variants:
    Instagram: full caption + all hashtags
    Facebook:  first 2 sentences + 3 hashtags max

  After publish:
    Writes published.instagram + published.facebook to manifest
    Appends to ~/.local/share/djinn-media/publish-log.json
    Sends Telegram notification

────────────────────────────────────────────────────────────────────────────────
FULL PIPELINE (END-TO-END)
────────────────────────────────────────────────────────────────────────────────

  djinn-media-ingest <path> --job-name <slug>
  djinn-media-reel <slug> --style forge --combine
  djinn-media-caption <slug> --burn
  djinn-media-thumbnail <slug>
  djinn-media-qa <slug>
  djinn-media-publish-prep <slug>
  djinn-media-publish <slug>

  Or trigger end-to-end from Discord/Telegram:
    media full <path>

────────────────────────────────────────────────────────────────────────────────
LUT MANAGEMENT
────────────────────────────────────────────────────────────────────────────────

  djinn-lut-gen
    Regenerates forge/clean/moody/raw .cube LUT files.
    Output: ~/.openclaw/workspace/media/shared/luts/
    Run after any style adjustment.

────────────────────────────────────────────────────────────────────────────────
HASHTAG BANK
────────────────────────────────────────────────────────────────────────────────

  djinn-hashtag-update [--report] [--research] [--add #tag --category cat --tier mid] [--dump]

    --report:    audit all tags in bank
    --research:  run phi4:14b trend research pass
    --add:       add a new tag to bank
    --dump:      print full bank to stdout

────────────────────────────────────────────────────────────────────────────────
STYLE SCRAPER
────────────────────────────────────────────────────────────────────────────────

  djinn-style-scrape [--query "text"] [--max N]

    Scrapes aesthetic reference images via DuckDuckGo.
    ⚠️ Fragile — Firecrawl replacement queued as TASK-021.
    Output: ~/.openclaw/workspace/media/shared/references/scraped/

================================================================================
5. TELEGRAM / DISCORD TRIGGERS
================================================================================

All commands work in @DjinnOCBot (Telegram) or #media-inbox (Discord).

  ┌──────────────────────────────────┬────────────────────────────────────────┐
  │ Command                          │ What it does                           │
  ├──────────────────────────────────┼────────────────────────────────────────┤
  │ media <path>                     │ Ingest a file or folder                │
  │ photo <project_id>               │ Edit photos with LUT grading           │
  │ reel <project_id>                │ Export 9:16 Reel                       │
  │ reel <project_id> combine        │ Concat all raw clips, then export      │
  │ caption <project_id>             │ Transcribe + generate captions         │
  │ repurpose <project_id>           │ Slice into Reel clips                  │
  │ thumbnail <project_id> [text]    │ Generate cover thumbnails              │
  │ qa <project_id>                  │ Run platform compliance check          │
  │ publish <project_id>             │ Caption package + Drive + Discord      │
  │ media full <path>                │ Run entire pipeline end-to-end         │
  │ media status                     │ List all projects + their status       │
  │ style scrape                     │ Trigger djinn-style-scrape (all queries│
  │ style scrape <query>             │ Targeted aesthetic reference scrape    │
  └──────────────────────────────────┴────────────────────────────────────────┘

================================================================================
6. LUT COLOR GRADING SYSTEM
================================================================================

LUT files: ~/.openclaw/workspace/media/shared/luts/
Generated by: djinn-lut-gen
Applied via: ffmpeg lut3d filter (same .cube files for both photo and video)
Result: identical look across every export format — feed, reel, story.

  ┌──────────┬───────────────────────────────────────────────────────┬───────────────────────────────────────┐
  │ Preset   │ Description                                           │ Use When                              │
  ├──────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────┤
  │ forge    │ Warm tungsten (3900K), copper shadows, S-curve,       │ DEFAULT — dark maker / gothic brand    │
  │          │ 15% desaturation                                      │ aesthetic                             │
  ├──────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────┤
  │ clean    │ Cool daylight (5600K), +10% saturation, gentle        │ Product detail shots where clarity    │
  │          │ contrast                                              │ matters more than mood               │
  ├──────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────┤
  │ moody    │ Teal shadows, blue push, 25% desaturation, cinematic  │ Atmospheric, slow, vibe content       │
  ├──────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────┤
  │ raw      │ Resize / crop only — no color changes                 │ Neutral baseline, A/B testing         │
  └──────────┴───────────────────────────────────────────────────────┴───────────────────────────────────────┘

To regenerate LUTs after any style adjustment:
  djinn-lut-gen

================================================================================
7. PROJECT STRUCTURE
================================================================================

Every project lives at:
  ~/.local/share/djinn-media/projects/<project_id>/

And is mirrored in vault at:
  ~/Obsidian/djinn/media/posts/<project_id>/

Directory layout:

  <project_id>/
  ├── manifest.json           ← job metadata, notes, published timestamps
  ├── raw/                    ← ORIGINAL FILES — NEVER MODIFIED
  ├── selects/
  ├── edits/
  ├── exports/
  │   ├── feed/               ← 1080×1080 (1:1) + 1080×1350 (4:5) JPEG
  │   ├── reel/               ← 1080×1920 H.264+AAC ≤90s
  │   ├── story/              ← 1080×1920
  │   └── thumbnail/          ← 1280×720 (16:9), 1080×1080 (1:1), 1080×1920 (9:16)
  ├── captions/               ← SRT files + transcript.txt
  └── publish/
      ├── instagram_post.md   ← Obsidian-readable full package
      ├── caption_feed.txt    ← Feed caption, plain text, phone-ready
      ├── caption_reel.txt    ← Reel caption, plain text
      └── POST.txt            ← Everything in one file: captions + hashtags + checklist

Google Drive layout (uploaded by publish-prep):
  gdrive:Typhons-Forge/posts/<project_id>/
  ├── publish/                ← all .txt + .md files
  ├── video/                  ← final reel .mp4
  └── feed/                   ← JPEG exports

================================================================================
8. HASHTAG BANK
================================================================================

Location: ~/Obsidian/djinn/media/hashtag-bank/
Size: 11 files, 236 tags, 3 tiers (broad / mid / micro)

Directory structure:

  hashtag-bank/
  ├── 3d-printing/
  │   ├── general.md          (13 tags)
  │   ├── materials.md        (20 tags)
  │   ├── tools.md            (23 tags)
  │   └── community.md        (16 tags)
  ├── cannabis/
  │   ├── general.md          (26 tags)
  │   ├── culture.md          (18 tags)
  │   ├── education.md        (21 tags)
  │   └── industry.md         (19 tags)
  ├── typhons-forge/
  │   └── brand.md            (27 tags)
  ├── crossover/
  │   └── maker-culture.md    (36 tags)
  └── platform-rules/
      └── instagram.md        ← shadowban guidance + rotation strategy

How publish-prep picks tags:
  Keywords from project notes + manifest are matched against tag slugs.
  Only tags that exist in the bank are used — hallucinated tags stripped.

Manage the bank:
  djinn-hashtag-update --report              # full audit
  djinn-hashtag-update --research            # phi4:14b trend pass
  djinn-hashtag-update --add #tagname --category cannabis/culture --tier mid

Weekly research timer:
  systemctl --user status djinn-hashtag-research.timer

================================================================================
9. REFERENCE LIBRARY & VISION QC
================================================================================

Location: ~/.openclaw/workspace/media/shared/references/

  references/
  ├── approved/     ← YOUR ground truth. Drop JPEG/PNG examples here manually.
  └── scraped/      ← Auto-populated by djinn-style-scrape (currently 32 images)

How vision QC works:
  djinn-media-photo scores every export against:
    - All images in approved/
    - First 3 images in scraped/
  Uses llama3.2-vision (on demand, loaded via REST).
  Score 1–10 printed at export time.
  Score < 6: manual review warning printed. Export still proceeds.

To add your own reference images:
  cp your-image.jpg ~/.openclaw/workspace/media/shared/references/approved/

To trigger a reference rescrape:
  djinn-style-scrape                          # all 8 default queries
  djinn-style-scrape --query "your search"   # specific query
  # or from bot: style scrape

Default scrape queries (8):
  dark industrial 3d printing
  gothic maker workshop
  3d printed cannabis accessories dark
  industrial forge metal
  dark moody product photography
  typhons forge dark craft
  cannabis accessories custom 3d print
  dark maker studio

================================================================================
10. PUBLISH OUTPUT FORMAT
================================================================================

After djinn-media-publish-prep, the publish/ folder contains:

  instagram_post.md     Obsidian-formatted full package (for vault reference)
  caption_feed.txt      Feed caption — plain text, paste into IG app directly
  caption_reel.txt      Reel caption — plain text
  POST.txt              Single file with: both captions + full hashtag set
                        + posting checklist

Discord notifications sent to:
  #media-status    pipeline summary + Drive link
  #post-ready      full posting package (plain text) + Drive link

Caption variant logic (platform-specific):
  Instagram: full caption + all selected hashtags
  Facebook:  first 2 sentences only + 3 hashtags max
  (Per Marcus TASK-012 research findings — FB penalizes hashtag overload)

================================================================================
11. INSTAGRAM / PLATFORM SPECS
================================================================================

  ┌────────────────────┬──────────────┬──────────┬────────────────┬────────────────────────┐
  │ Format             │ Resolution   │ Max Size │ Codec          │ Notes                  │
  ├────────────────────┼──────────────┼──────────┼────────────────┼────────────────────────┤
  │ Feed photo 4:5     │ 1080×1350    │ 8MB      │ JPEG           │ Primary crop           │
  │ Feed photo 1:1     │ 1080×1080    │ 8MB      │ JPEG           │ Square fallback        │
  │ Reel               │ 1080×1920    │ 3.6GB    │ H.264 + AAC    │ ≤90s                   │
  │ Story              │ 1080×1920    │ 4GB      │ H.264 + AAC    │ ≤60s                   │
  │ Reel cover (thumb) │ 1080×1920    │ 8MB      │ JPEG           │                        │
  │ Thumbnail 16:9     │ 1280×720     │ 8MB      │ JPEG           │ YouTube-style cover    │
  └────────────────────┴──────────────┴──────────┴────────────────┴────────────────────────┘

All specs enforced by djinn-media-qa before publish-prep is allowed to run.

================================================================================
12. SYSTEMD SERVICES & TIMERS
================================================================================

  ┌────────────────────────────────────────┬──────────────────────────┬────────────────────────────────────┐
  │ Unit                                   │ Schedule                 │ Status / Notes                     │
  ├────────────────────────────────────────┼──────────────────────────┼────────────────────────────────────┤
  │ djinn-media-gdrive-sync.timer          │ Every 5 min              │ ✅ Active                          │
  │ djinn-media-drop.service               │ Continuous daemon        │ ✅ Active (inotifywait watcher)    │
  │ djinn-meta-token-refresh.timer         │ Monthly, 1st @ 03:00     │ ✅ Active (awaiting meta.env creds)│
  │ djinn-social-analyst.timer             │ Daily @ 00:30 UTC        │ ✅ Active (awaiting meta.env creds)│
  │ djinn-hashtag-research.timer           │ Weekly                   │ ✅ Active                          │
  │ djinn-trend-agent.timer                │ Every 6h                 │ 🔲 Pending — TASK-019              │
  └────────────────────────────────────────┴──────────────────────────┴────────────────────────────────────┘

Manage services:
  systemctl --user status djinn-media-drop.service
  systemctl --user restart djinn-media-drop.service
  journalctl --user -u djinn-media-drop.service -n 50

  systemctl --user status djinn-media-gdrive-sync.timer
  systemctl --user list-timers --user        # all timers + next run time

================================================================================
13. KEY FILE PATHS & CONFIG
================================================================================

  CREDENTIALS (keep chmod 600):
    ~/.config/djinn/meta.env              ← Meta Graph API credentials
    ~/.config/djinn/firecrawl.env         ← Firecrawl API key (set)
    ~/.config/djinn/apify.env             ← Apify token (stub — fill when ready)

  RUNTIME STATE:
    ~/.local/share/djinn-media/projects/       ← all project directories
    ~/.local/share/djinn-media/media-context.json  ← Layer 1 → Layer 2 context
    ~/.local/share/djinn-media/publish-log.json    ← post history

  INBOX (watched by djinn-media-drop):
    ~/djinn-media-inbox/                   ← drop files here from GDrive sync

  GDRIVE INBOX (synced every 5 min):
    gdrive:Typhons-Forge/inbox/            ← drop from iPhone here

  MEDIA ASSETS:
    ~/.openclaw/workspace/media/shared/luts/          ← .cube LUT files
    ~/.openclaw/workspace/media/shared/references/    ← vision QC references

  LAYER 1 OUTPUT:
    ~/Obsidian/djinn/social/TREND-SIGNAL.md       ← live trend context (every 6h)
    ~/Obsidian/djinn/social/HASHTAG-BANK.md       ← weekly hashtag audit
    ~/Obsidian/djinn/social/analytics/            ← own post analytics (daily JSON)

  HASHTAG BANK:
    ~/Obsidian/djinn/media/hashtag-bank/

  VAULT MEDIA:
    ~/Obsidian/djinn/media/posts/<project_id>/    ← vault mirror of project

================================================================================
14. META API CREDENTIALS SETUP
================================================================================

Djinn Media can do everything up to publish-prep without credentials.
To enable live publishing and analytics, fill in:

  ~/.config/djinn/meta.env  (chmod 600)

  META_PAGE_TOKEN=<long-lived page token>
  IG_USER_ID=<instagram user id>
  FB_PAGE_ID=<facebook page id>
  META_APP_ID=<from Meta Developer Console>
  META_APP_SECRET=<from Meta Developer Console>

Where to get these:
  - Meta App: developers.facebook.com → My Apps → your app
  - Page Token: Graph API Explorer → generate with pages_manage_posts +
    instagram_basic + instagram_content_publish scopes
  - IG User ID: Graph API → /{page-id}?fields=instagram_business_account
  - FB Page ID: facebook.com/your-page → About → Page ID

Once meta.env is filled:
  djinn-media-publish <project_id> --dry-run    # verify plan before going live
  djinn-media-publish <project_id>              # publish for real

Optional — Apify (for IG trend scraping via djinn-trend-agent):
  ~/.config/djinn/apify.env
  APIFY_TOKEN=<from apify.com → Settings → Integrations>

================================================================================
15. LAYER 1 — INTELLIGENCE PIPELINE
================================================================================

────────────────────────────────────────────────────────────────────────────────
15.1  djinn-trend-agent (TASK-019 — PENDING)
────────────────────────────────────────────────────────────────────────────────

  Scheduled: every 6h via djinn-trend-agent.timer (timer exists, script pending)
  Status: specced, queued for Salomon to build

  What it does:
    - Polls multiple trend sources
    - Runs phi4:14b synthesis pass
    - Writes TREND-SIGNAL.md (sorted by engagement signal)
    - Writes HASHTAG-BANK.md (weekly)

  Sources:
    ┌──────────────────────────────┬──────────────────────────┬──────────┬──────────────┐
    │ Source                       │ Method                   │ Cost     │ Maintenance  │
    ├──────────────────────────────┼──────────────────────────┼──────────┼──────────────┤
    │ Reddit + YouTube signal      │ Firecrawl fc.search()    │ $0       │ ~0h/mo       │
    │ Makerworld + Printables pages│ Firecrawl fc.scrape_url()│ $0       │ ~0h/mo       │
    │ Printables RSS               │ Direct HTTP + XML parse  │ $0       │ ~0h/mo       │
    │ Apify Instagram scraper      │ Apify API                │ ~$3.60/mo│ 0h (managed) │
    └──────────────────────────────┴──────────────────────────┴──────────┴──────────────┘

  Note: Reddit and YouTube APIs are NOT needed. Firecrawl handles both
  platforms with the single key already installed at ~/.config/djinn/firecrawl.env.

────────────────────────────────────────────────────────────────────────────────
15.2  djinn-social-analyst
────────────────────────────────────────────────────────────────────────────────

  Scheduled: daily @ 00:30 UTC via djinn-social-analyst.timer
  Status: built, active, awaiting meta.env credentials

  What it does:
    - Pulls last N days of own post metrics from Meta Graph API
      (reach, plays, saves, shares, avg_watch_ms)
    - Writes: djinn/social/analytics/YYYY-MM-DD.json (raw per-post data)
    - Writes: djinn/social/TREND-SIGNAL.md (sorted by saves+shares, with deltas)

  This is the feedback loop:
    Own analytics → TREND-SIGNAL.md → publish-prep-agent reads it →
    caption + hashtag selection informed by what actually performed.

────────────────────────────────────────────────────────────────────────────────
15.3  djinn-meta-token-refresh
────────────────────────────────────────────────────────────────────────────────

  Scheduled: monthly, 1st @ 03:00 via djinn-meta-token-refresh.timer
  Status: built, active, awaiting meta.env credentials

  What it does:
    - Exchanges current page token for a fresh 60-day long-lived token
      via GET /v19.0/oauth/access_token?grant_type=fb_exchange_token
    - Writes new token in-place to meta.env (never overwrites on failure)
    - Sends Telegram notification on success or failure

  You never need to manually refresh the token — this runs automatically.

================================================================================
16. CURRENT STATUS & OUTSTANDING WORK
================================================================================

As of 2026-05-31 — Phase 2 complete, Phase 3 queued.

  ┌───────────────────────────────────┬───────────────────────────────────────────────────────────┐
  │ Script                            │ Status                                                    │
  ├───────────────────────────────────┼───────────────────────────────────────────────────────────┤
  │ djinn-media-ingest                │ ✅ Live                                                   │
  │ djinn-media-reel                  │ ✅ Live                                                   │
  │ djinn-media-photo                 │ ✅ Live                                                   │
  │ djinn-media-repurpose             │ ✅ Live                                                   │
  │ djinn-media-kit                   │ ✅ Live                                                   │
  │ djinn-media-publish-prep          │ ✅ Live                                                   │
  │ djinn-media-publish               │ ✅ Built — awaiting meta.env credentials                  │
  │ djinn-meta-token-refresh          │ ✅ Built — awaiting meta.env credentials                  │
  │ djinn-social-analyst              │ ✅ Built — awaiting meta.env credentials                  │
  │ djinn-media-drop                  │ ✅ Live                                                   │
  │ djinn-style-scrape                │ ⚠️ Fragile — Firecrawl rewrite queued (TASK-021)          │
  │ djinn-trend-agent                 │ 🔲 Pending — queued as TASK-019                           │
  └───────────────────────────────────┴───────────────────────────────────────────────────────────┘

OUTSTANDING BEFORE LIVE PUBLISHING:
  1. meta.env credentials — fill META_PAGE_TOKEN, IG_USER_ID, FB_PAGE_ID,
     META_APP_ID, META_APP_SECRET in ~/.config/djinn/meta.env
  2. Apify account — apify.com → free account → API token → ~/.config/djinn/apify.env
  3. TASK-019 — Salomon builds djinn-trend-agent
  4. TASK-020 — Salomon wires TREND-SIGNAL.md into caption prompt in publish-prep
  5. TASK-021 — Salomon rewrites djinn-style-scrape with Firecrawl
  6. TASK-022 — Salomon replaces Makerworld/Thingiverse HTML scraping in djinn-model-fetch

================================================================================
17. COMMON WORKFLOWS (STEP-BY-STEP)
================================================================================

────────────────────────────────────────────────────────────────────────────────
WORKFLOW A — Full Reel from iPhone footage
────────────────────────────────────────────────────────────────────────────────

  1. Drop footage to GDrive:
       Shoot → Google Photos auto-sync → Typhons-Forge/inbox/

  2. Wait for sync (up to 5 min) or confirm:
       ls ~/djinn-media-inbox/

  3. Ingest:
       djinn-media-ingest ~/djinn-media-inbox/forge-session.mp4 \
         --job-name forge-session-01 \
         --notes "new PETG spool reveal, dark workshop setup"

  4. Edit reel (combine clips if multiple):
       djinn-media-reel forge-session-01 --style forge --combine

  5. Caption (transcribe + burn):
       djinn-media-caption forge-session-01 --burn

  6. Thumbnail:
       djinn-media-thumbnail forge-session-01 --text "New PETG Drop" --style band

  7. QA gate:
       djinn-media-qa forge-session-01
       # Fix any failures before continuing

  8. Publish prep (generates captions, picks hashtags, uploads to Drive):
       djinn-media-publish-prep forge-session-01
       # Check #post-ready in Discord for the full package

  9. Publish live (requires meta.env):
       djinn-media-publish forge-session-01 --dry-run    # verify first
       djinn-media-publish forge-session-01

────────────────────────────────────────────────────────────────────────────────
WORKFLOW B — Full pipeline from Telegram/Discord
────────────────────────────────────────────────────────────────────────────────

  After footage is in inbox:
    Telegram: media full ~/djinn-media-inbox/forge-session.mp4

  Or step by step from Telegram:
    media ~/djinn-media-inbox/forge-session.mp4
    reel forge-session-01
    caption forge-session-01
    thumbnail forge-session-01 New PETG Drop
    qa forge-session-01
    publish forge-session-01

────────────────────────────────────────────────────────────────────────────────
WORKFLOW C — Repurpose a long recording into clips
────────────────────────────────────────────────────────────────────────────────

  1. Ingest the full recording:
       djinn-media-ingest ~/Videos/workshop-vod.mp4 --job-name workshop-vod-01

  2. Slice into clips:
       djinn-media-repurpose workshop-vod-01 --clips 6

  3. Each clip becomes its own sub-project.
     Repeat Workflow A for each clip from step 4 onward.

────────────────────────────────────────────────────────────────────────────────
WORKFLOW D — Add new hashtags to the bank
────────────────────────────────────────────────────────────────────────────────

  1. Check current state:
       djinn-hashtag-update --report

  2. Add a new tag:
       djinn-hashtag-update --add #resinprinting --category 3d-printing/materials --tier mid

  3. Run a research pass (phi4:14b identifies trending tags):
       djinn-hashtag-update --research

────────────────────────────────────────────────────────────────────────────────
WORKFLOW E — Update aesthetic reference images
────────────────────────────────────────────────────────────────────────────────

  1. Trigger rescrape:
       djinn-style-scrape
       # or: style scrape (Telegram/Discord)

  2. Add your own approved ground truth:
       cp my-reference.jpg ~/.openclaw/workspace/media/shared/references/approved/

  3. Next photo export will score against your new references automatically.

================================================================================
18. TROUBLESHOOTING
================================================================================

  SYMPTOM: Inbox files not being picked up automatically
  CAUSE:   djinn-media-drop.service is not running, or inotifywait is broken
  FIX:
    systemctl --user status djinn-media-drop.service
    journalctl --user -u djinn-media-drop.service -n 30
    # If crashed: systemctl --user restart djinn-media-drop.service
    # If inotifywait missing: install inotify-tools; service falls back to polling

  SYMPTOM: GDrive inbox not syncing from iPhone
  CAUSE:   djinn-media-gdrive-sync.timer missed or rclone config broken
  FIX:
    systemctl --user status djinn-media-gdrive-sync.timer
    rclone lsd gdrive:Typhons-Forge/inbox/     # test rclone connection
    systemctl --user restart djinn-media-gdrive-sync.timer

  SYMPTOM: djinn-media-qa fails with codec error
  CAUSE:   Source file is not H.264 — iPhone HEVC/H.265 files need transcoding
  FIX:    djinn-media-reel handles transcoding automatically via ffmpeg.
           If running manually: ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4

  SYMPTOM: djinn-media-caption produces blank transcript
  CAUSE:   Audio track missing or faster-whisper not installed in pyenv 3.11
  FIX:
    python3 -c "import faster_whisper"    # if ImportError:
    pyenv shell 3.11
    pip install faster-whisper

  SYMPTOM: Vision QC score is always low (< 6)
  CAUSE:   approved/ folder is empty — scoring against scraped/ only
  FIX:    Add your own reference images to:
           ~/.openclaw/workspace/media/shared/references/approved/

  SYMPTOM: djinn-media-publish fails with token expired
  CAUSE:   meta.env page token is >60 days old
  FIX:    djinn-meta-token-refresh runs monthly automatically.
           To force a manual refresh:
           djinn-meta-token-refresh
           # Or re-generate from Graph API Explorer (see §14)

  SYMPTOM: djinn-style-scrape fails or returns no images
  CAUSE:   DuckDuckGo frontend change broke the vqd token extraction
  STATUS:  Known fragile — Firecrawl rewrite queued as TASK-021
  FIX:    Add reference images manually to approved/ for now.

  SYMPTOM: publish-prep produces wrong hashtags
  CAUSE:   Project notes don't have enough keywords for bank matching
  FIX:    Re-run ingest with richer --notes:
           djinn-media-ingest <path> --job-name <same-id> --notes "better keywords"
           djinn-media-publish-prep <id>   # regenerate

  SYMPTOM: Discord notification not sent after publish-prep
  CAUSE:   Discord bot offline or #media-status / #post-ready channel missing
  FIX:
    journalctl --user -u openclaw-gateway.service -n 20
    Check Discord bot status in #bot-status

================================================================================
19. HARD RULES
================================================================================

  1. raw/ is READ ONLY. Originals are never modified. Always work on copies.

  2. Never run djinn-media-publish without a --dry-run check first.
     Verify the caption and hashtag output before committing to Meta API.

  3. Never store Meta credentials in git. meta.env is in ~/.config/djinn/,
     chmod 600, and explicitly gitignored.

  4. Never cancel a running pipeline mid-job without checking what files
     are in progress. Partial exports may corrupt the project manifest.
     If interrupted: djinn-media-ingest to re-initialize, then re-run from
     the failed step.

  5. Hashtag bank is the only source of truth for tags.
     Publish-prep strips any tag not in the bank. Do not bypass this.
     Add new tags properly with djinn-hashtag-update --add.

  6. djinn-media-qa must pass before publish-prep.
     Do not skip the QA gate. Platform rejections waste the publish slot.

  7. GDrive is the canonical store for all media exports.
     GitHub never receives binary files, video, or images.

  8. The feedback loop matters:
     After any published post — check djinn-social-analyst output the next
     morning. High-performing tags and hooks feed the next caption generation.

================================================================================
SOURCE DOCUMENTS ABSORBED
================================================================================

  djinn/media/MEDIA-STACK.md          — architecture, agents, CLI, LUTs, hashtag bank
  djinn/media/DJINN-MEDIA-STATUS.md   — phase status, script table, Layer 1 spec,
                                         outstanding tasks, key file paths

================================================================================
*— Marcus, 2026-06-09*
================================================================================
