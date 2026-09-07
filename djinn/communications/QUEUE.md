---
title: Djinn Task Queue
updated: 2026-05-31
tags: [djinn, queue, delegation]
related: [[COMMS]] | [[PROTOCOL]] | [[build-log]]
---

# QUEUE — Djinn Task Queue

Claude, Marcus, or Javier writes tasks here. Salomon, Typhon, Marcus, and Claude pull and execute.

## Rules
- **Append only** — never delete entries. Mark `status: done` or `status: failed`.
- `trigger: auto` — runner picks up on next poll (cron every 5 min) — Salomon/Typhon only
- `trigger: manual` — Javier must send explicit signal — always used for Marcus and Claude tasks
- Runner: `djinn-queue-runner` on Salomon and Typhon
- On completion: runner calls `djinn-task-complete TASK-NNN "summary"` automatically (Salomon/Typhon); Marcus and Claude mark their own tasks done and append a COMMS entry

## Task Format — Salomon / Typhon

```
## TASK-NNN
- assigned_to: salomon | typhon
- status: done | in_progress | done | failed
- priority: critical | high | normal | low
- trigger: auto | manual
- created: YYYY-MM-DD by Claude|Javier|Marcus
- context: one-line description of what and why

**Commands:**
```bash
command one
command two
```
```

## Task Format — Marcus

```
## TASK-NNN
- assigned_to: marcus
- status: done | in_progress | done | failed
- priority: critical | high | normal | low
- trigger: manual
- created: YYYY-MM-DD by Claude|Javier
- context: one-line description

**Brief:**
[What to research or produce — specific questions, scope, required depth]

**Output expected:**
`djinn/research/marcus/TASK-NNN_slug.md`

**Deliver to:** Claude (reads via Read tool) | Javier (key findings in COMMS)
```

## Task Format — Claude

```
## TASK-NNN
- assigned_to: claude
- status: done | in_progress | done | failed
- priority: critical | high | normal | low
- trigger: manual
- created: YYYY-MM-DD by Marcus|Javier
- context: one-line description

**Brief:**
[What Claude needs to review, design, or decide — specific scope]

**Input:** `path/to/relevant/file` or COMMS context
**Output expected:** session report + COMMS entry + any file changes pushed
```

---

<!-- TASKS BELOW — oldest at top, newest at bottom -->

## TASK-001
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-05-31 by Salomon
- context: Deploy full shop system — gateways, dashboard, services, config stubs

**Commands:**
```bash
git -C ~/Obsidian pull
djinn-shop-deploy
```

**After completion, verify:**
```bash
curl -s http://localhost:5000/login | grep -q "Typhon" && echo "dashboard OK" || echo "dashboard FAILED"
systemctl --user is-active djinn-shop-dashboard.service
systemctl --user is-active djinn-dm-cleanup.timer
grep -q "SHOP_PATCH_APPLIED" ~/.local/bin/djinn-discord-gateway && echo "Discord patched OK" || echo "Discord NOT patched"
grep -q "SHOP_PATCH_APPLIED" ~/.local/bin/djinn-telegram-gateway && echo "Telegram patched OK" || echo "Telegram NOT patched"
```

**Report back:** Post djinn-shop-deploy output + verification results in COMMS.md.

---

## TASK-002
- assigned_to: salomon
- status: done
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-05-31 by Salomon
- context: Install cron for queue runner so TASK-NNN auto tasks execute every 5 min

**Commands:**
```bash
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/drmanzo/.local/bin/djinn-queue-runner >> /tmp/djinn-queue.log 2>&1") | crontab -
crontab -l | grep queue-runner
```

**Note:** Run after TASK-001 completes. Do not run before shop deploy is verified.

---

## TASK-003
- assigned_to: claude
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Salomon (per Javier)
- completed: 2026-05-31 by Claude
- context: Refactor shipping_agent.py — swap EasyPost SDK for Shippo, make provider configurable

**Commands:**
```bash
# Edit shipping_agent.py:
# 1. Add SHIPPING_PROVIDER=shippo|easypost config variable from shop.env
# 2. Add Shippo client implementation (rate lookup, label purchase, tracking)
# 3. Abstract to common interface
# 4. Test with SHIPPO_API_KEY from shop.env
```

**Note:** Shippo test key is in `~/.config/djinn/shop.env` as `SHIPPO_API_KEY`.

---

## TASK-004
- assigned_to: claude
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Salomon (per Javier)
- context: Fix maker's mark mirroring on bottom engraving + make it configurable

**Bug:** When the TF anvil STL (logo faces +Z) is boolean-subtracted from a vase bottom and viewed from below, the engraving reads reversed. Need to mirror X axis before subtract.

**Fix required in the workflow:**
1. Mirror maker's mark across X axis before boolean subtraction into bottom surfaces (`mirrored_verts[:, 0] = -mirrored_verts[:, 0]` + reverse face winding)
2. Make maker's mark a configurable variable — default `tf_anvil_traced_15mm.stl`, stored in `~/.config/djinn/makers-mark.json` with `{ "path": "...", "mirror_x": true }`
3. Document the rule so all agents know to mirror before engraving on bottom faces

**Files:**
- `/home/drmanzo/Downloads/files/tf_anvil_traced_15mm.stl` — default mark
- `~/.config/djinn/ender3-v3-plus.ini` — printer profile  
- `/home/drmanzo/.local/bin/djinn-print-consult` — consult script
- `/home/drmanzo/Obsidian/djinn/printer/SUPPORT-GUIDE.md` — workflow docs

**Report back:** Post fix summary in COMMS.md + update `build-log.md`.

---

## TASK-005
- assigned_to: claude
- status: done
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Media kit — update djinn-media-reel: force 30fps + job-name output filename

**Changes:**
1. Add `-r 30` to all ffmpeg export commands in `djinn-media-reel`
2. Read `job_slug` from `manifest["notes"]` field (fallback to project_id slug)
3. Rename output from `{project_id}_reel.mp4` → `{job_slug}_reel.mp4`
4. Same fix for cover frame filename

**File:** `/home/drmanzo/.local/bin/djinn-media-reel`

---

## TASK-006
- assigned_to: claude
- status: done
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Media kit — update djinn-media-repurpose: job-name clip naming

**Changes:**
1. Read `job_slug` from manifest notes (fallback to project_id slug)
2. Rename clip output from `clip_{n:02d}.mp4` → `{job_slug}_{n:02d}.mp4`

**File:** `/home/drmanzo/.local/bin/djinn-media-repurpose`

---

## TASK-007
- assigned_to: claude
- status: done
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Media kit — build djinn-media-kit: creates stitch-kit/ folder + STITCH-ORDER.txt

**What to build:**
- New script at `/home/drmanzo/.local/bin/djinn-media-kit`
- Reads all clips from `exports/reel/` in the project
- Creates `stitch-kit/` folder in project root
- Copies clips with job-named convention ({job_slug}_01.mp4 etc.)
- Writes `STITCH-ORDER.txt` (clip list, durations, notes from manifest)
- Updates manifest `status = "kit_ready"`
- Usage: `djinn-media-kit {project_id}`

**Spec:** See `~/Obsidian/djinn/projects/PLAN-media-kit-mobile.md`

---

## TASK-008
- assigned_to: claude
- status: done
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Media kit — update djinn-media-publish-prep: upload stitch-kit/ first, update Discord message

**Changes:**
1. Upload `stitch-kit/` to `gdrive:Typhons-Forge/posts/{project_id}/stitch-kit/` before other uploads
2. Discord `#post-ready` message leads with stitch-kit Drive link, not buried at the end

**File:** `/home/drmanzo/.local/bin/djinn-media-publish-prep`

---

## TASK-009
- assigned_to: claude
- status: done
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Media kit — update djinn-media-ingest: add --job-name flag

**Changes:**
1. Add `--job-name "slug"` CLI flag
2. Write `job_slug` field to manifest.json at ingest time
3. Fallback: derive from project_id if not provided

**File:** `/home/drmanzo/.local/bin/djinn-media-ingest`

---

## TASK-010
- assigned_to: salomon
- status: done
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- completed: 2026-05-31 by Salomon
- context: Media kit — deploy and test full updated pipeline with mini-vases-job4

**After Claude completes TASK-005 through 009:**
```bash
git -C ~/Obsidian pull
# Re-run mini-vases project through updated pipeline:
djinn-media-kit 2026-05-31_mini-vases-job4   # if project exists
# Or ingest fresh footage with job name:
djinn-media-ingest <footage_path> --job-name "mini-vases-job4"
djinn-media-reel 2026-05-31_mini-vases-job4
djinn-media-kit 2026-05-31_mini-vases-job4
```

**Verify:**
- stitch-kit/ folder exists with job-named clips
- STITCH-ORDER.txt has correct clip list
- Drive upload puts stitch-kit/ at top level
- Clips are 30fps H.264 AAC

**Report back:** COMMS.md + build-log.md

---

## TASK-011
- assigned_to: salomon
- status: done
- priority: low
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- completed: 2026-05-31 by Salomon
- context: Media kit — add "kit {project_id}" trigger to Discord + Telegram gateways

**After TASK-010 verified:**
Add `kit` command to both gateway scripts so Javier can trigger from phone:
- `kit {project_id}` → runs `djinn-media-kit {project_id}`
- Response: "Kit ready — {drive_link}"

**Files:** `djinn-discord-gateway`, `djinn-telegram-gateway`

---

## TASK-013
- assigned_to: claude
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Javier
- context: Build djinn-media-drop — personal footage intake watcher for fire testing the pipeline

**What to build:**

### 1. Drop folder
`~/djinn-media-inbox/` — local watched folder on Salomon

### 2. GDrive sync path (iPhone → Salomon)
`gdrive:Typhons-Forge/inbox/` → `~/djinn-media-inbox/`
Javier drops files from iPhone to Google Drive inbox folder. rclone syncs down every 5 min via systemd timer.

### 3. `djinn-media-drop` watcher daemon
- Watches `~/djinn-media-inbox/` with inotifywait (or poll fallback if inotify unavailable)
- When a new file lands and is fully written (not still copying):
  1. Derives job_slug from filename (strip extension, slugify)
  2. Runs `djinn-media-ingest <file> --job-name <job_slug>`
  3. Moves processed file to `~/djinn-media-inbox/processed/`
  4. Sends Telegram notification:
     ```
     📥 Djinn Media — intake received
     Job: {job_slug}
     Project: {project_id}
     Type: {video|photo}
     
     Send to start processing:
       reel {project_id}          ← export full reel
       reel {project_id} combine  ← combine multiple clips
       full {project_id}          ← run entire pipeline
     ```

### 4. systemd units (two)
- `djinn-media-drop.service` — the watcher daemon
- `djinn-media-gdrive-sync.timer` — rclone sync every 5 min
  `rclone copy gdrive:Typhons-Forge/inbox ~/djinn-media-inbox --ignore-existing`

**Files to create:**
- `/home/drmanzo/.local/bin/djinn-media-drop` — watcher script
- `~/.config/systemd/user/djinn-media-drop.service`
- `~/.config/systemd/user/djinn-media-gdrive-sync.timer`
- `~/.config/systemd/user/djinn-media-gdrive-sync.service`

**Note:** This is the fire-test intake path — Javier's own footage only. Completely separate from Discord capture (future). Lets him test the full pipeline with real footage immediately.

---

## TASK-014
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- completed: 2026-05-31 by Salomon
- context: Deploy djinn-media-drop watcher + gdrive sync timer after Claude builds TASK-013

**After Claude completes TASK-013:**
```bash
git -C ~/Obsidian pull
mkdir -p ~/djinn-media-inbox/processed
systemctl --user enable --now djinn-media-drop.service
systemctl --user enable --now djinn-media-gdrive-sync.timer
```

**Verify:**
```bash
systemctl --user status djinn-media-drop.service
systemctl --user status djinn-media-gdrive-sync.timer
# Drop a test file into ~/djinn-media-inbox/ and confirm Telegram notification fires
```

**Report back:** COMMS.md + build-log.md. Confirm Telegram intake notification works end to end.

---

## TASK-012
- assigned_to: marcus
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- completed: 2026-05-31 by Marcus
- context: Deep research brief — Djinn Media social media integration opportunities
- outcome: Full report at `djinn/research/marcus/TASK-012_djinn-media-social.md`. P0 blocker: Meta app review required for pages_manage_posts (1–2 week approval, must start now). Page token is non-expiring once correctly derived. FB Reels cap = 60s. 3–5 hashtags max.

**How to run:** Javier pastes the brief below directly into Perplexity. Marcus produces a research artifact. Javier relays output back to vault.

---

### Marcus Research Brief — Djinn Media

**Who you are answering for:**
Javier runs a one-person 3D print shop (Typhon's Forge) with a fully automated AI backend — multi-agent system (Claude, local Ollama, Perplexity) handling quoting, slicing, printing, shipping, and accounting. He is now building a social media production layer called **Djinn Media** on top of this system.

The existing media pipeline already handles: video ingest → color grading → caption generation → hashtag selection → Google Drive upload → Discord notification. All local, all automated, CLI-driven on a Linux machine with ffmpeg, faster-whisper, Ollama (phi4:14b, llama3.2-vision), rclone.

**Target platforms:** Instagram Reels, Instagram Feed, Facebook Reels, Facebook Feed. Possibly TikTok later.

**Content type:** Short-form video (15–90s) of 3D printing process, product reveals, AI shop automation demos. Dark maker aesthetic. Cannabis accessories in the mix.

---

**Research questions — go deep on each:**

1. **Auto-posting APIs**
   What are the current (2026) options for programmatically publishing to Instagram and Facebook without manual intervention? Specifically:
   - Instagram Graph API — current capabilities, what requires Meta Business Suite, what can be fully automated vs what still requires human action
   - Facebook Graph API for video/Reels posting
   - Third-party scheduling APIs (Buffer, Later, Publer, etc.) that expose REST APIs — which ones allow full automation without a human approval step?
   - Any new Meta features in 2025–2026 that opened up or closed off auto-posting?

2. **What's actually performing on Reels for maker/3D printing content in 2026**
   - What content formats are the algorithm rewarding right now (POV, voiceover, text-on-screen, timelapse, reveal format)?
   - Optimal clip length for reach vs engagement tradeoff
   - What hook styles (first 3 seconds) are working in the maker/DIY/craft niche
   - Any data on posting frequency, timing, consistency patterns that matter
   - How do successful small maker accounts (under 10k followers) grow vs larger ones

3. **AI-assisted social media tools for creators — competitive landscape**
   - What tools exist in 2026 for AI-assisted caption writing, hashtag research, content scheduling for small creators?
   - Any tools that do what Djinn Media is building (auto-generate content from raw footage + metadata)?
   - What's the gap — what are these tools missing that a custom pipeline could do better?

4. **Cross-platform content repurposing**
   - Best practices for repurposing one piece of content across IG, FB, and TikTok without getting penalized for duplicate content
   - Watermark detection — does Instagram or FB actually suppress content with TikTok watermarks in 2026?
   - How to format one video file to perform optimally on all three without separate exports

5. **Analytics and feedback loops**
   - What analytics are available via the Instagram/Facebook Graph API (not just the app — the actual API)?
   - Can you pull reach, saves, shares, watch time, retention data programmatically?
   - Are there open-source or lightweight tools for aggregating this data locally?

6. **Cannabis content and platform policies in 2026**
   - What is Instagram's current enforcement stance on cannabis accessory content (not drug use — 3D printed accessories, pipes, etc.)?
   - What hashtag categories are getting shadowbanned vs tolerated?
   - Any workarounds successful cannabis-adjacent accounts are using?
   - Facebook's policy vs Instagram's policy — are they different?

7. **Djinn Media as a product**
   - If this pipeline were packaged as a tool for other small shop owners / makers — what would be the most valuable features to emphasize?
   - Who is the target user (maker, Etsy seller, print shop, cannabis brand)?
   - What's the competitive positioning vs existing tools?

---

8. **Live trend and hashtag data sources (NEW — critical for Djinn Media Layer 1)**
   Djinn Media has a two-layer architecture: Layer 1 (intelligence agents) feeds Layer 2 (production agents). Layer 1 needs live data to work:
   - What APIs or data sources can programmatically return trending hashtags for a given niche (maker, 3D printing, cannabis accessory) on Instagram and Facebook in 2026?
   - Is the Instagram Graph API useful for trend data or is it limited to your own account analytics?
   - What third-party options exist (RapidAPI hashtag tools, Apify scrapers, Iconosquare API, etc.) — which are reliable and affordable for a one-person operation?
   - How do you detect what visual styles/filters/formats are performing without manual scraping? Is there a signal available via any API?
   - What does a viable "trend polling agent" look like — how often should it run, what does it query, what does it return?

**Output format requested:**
Structured report with one section per question. For each section: current state, key findings, specific recommendations or integrations to pursue, and any warnings/gotchas. Cite sources. Flag anything time-sensitive (API changes, policy updates).

**Deliver as:** Write markdown artifact directly to `djinn/research/marcus/TASK-012_djinn-media-social.md` in `github.com/DrManzo/djinn-vault` and commit. Fallback: write to `gdrive:Typhons-Forge/research/marcus/TASK-012_djinn-media-social.md`. Claude reads on demand — do NOT paste into chat.

---

## TASK-015
- assigned_to: marcus
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- completed: 2026-05-31 by Marcus
- context: Research — can we replace Apify + Flick with a self-built zero-cost trend intelligence stack? No subscriptions, Djinn maintains it.
- outcome: Yes. Apify free tier ($3.60/mo usage within $5 free credit) + Firecrawl + Printables RSS. No self-hosted IG scraper (3–8h/mo maintenance, silent failures). Full report: `djinn/research/marcus/TASK-015_diy-trend-stack.md`

**How to run:** Javier pastes the brief below into Perplexity. Marcus writes output to `djinn/research/marcus/TASK-015_diy-trend-stack.md` in GitHub vault and commits. Do NOT paste into chat.

---

### Marcus Research Brief — DIY Trend Intelligence Stack

**Context:**
TASK-012 recommended Apify ($49/mo) + Flick ($30/mo) = $79/mo to power Djinn Media's Layer 1 trend intelligence. Javier wants to know if we can replace all of that with a self-built, self-hosted stack that costs nothing to run and is maintained by us — no third-party subscriptions.

The system is `djinn-trend-agent`: a daemon running every 6 hours on Salomon (Linux, Python, Ollama available), writing to `djinn/social/TREND-SIGNAL.md` and `djinn/social/HASHTAG-BANK.md`, which the Layer 2 caption agent reads before generating post content.

The question: **can a custom Python scraper + free public data sources replace Apify's Instagram scraper and Flick's hashtag tool entirely, with acceptable reliability and reasonable maintenance burden?**

---

**Research questions — go deep on each:**

1. **Self-hosted Instagram scraping in 2026**
   - What open-source Python libraries can scrape Instagram public data (hashtag pages, trending Reels by keyword, post engagement) without an official API key?
   - Current state of: `instaloader`, `instagramy`, `instagram-scraper`, `pyinstagram`, and any 2025–2026 forks or replacements
   - Which can reliably extract: top posts for a given hashtag, engagement metrics (likes/comments/saves where visible), video metadata, caption text?
   - How often do these break when Meta updates its frontend? Realistic maintenance cadence — days, weeks, or months between fixes?
   - Anti-scraping posture of Instagram in 2026 — rate limits, CAPTCHA, IP bans, cookie requirements. What does a responsible scraping setup look like?
   - Is a headless-browser approach (Playwright, Selenium) more stable than requests-based scrapers?

2. **Alternative public data sources for trend signal — not Instagram**
   - Can we get equivalent trend signal from platforms that are more scrape-friendly?
   - **Reddit** — r/3Dprinting, r/PrintedMinis, r/weed, r/glassheads: Reddit's official API (PRAW) — what's accessible free in 2026? Post velocity, upvote ratio, comment velocity as trend signal.
   - **YouTube Data API** (free tier: 10,000 units/day) — can we pull trending shorts/videos by keyword ("3D printing", "functional art", "maker")? Is this a useful proxy for what Instagram will boost next?
   - **TikTok** — usable public API or scraper for trending content by keyword in 2026? Is TikTok trend signal a leading indicator for Instagram performance?
   - **Google Trends** — `pytrends` library: keyword velocity for "3D printed", "functional glass", "puffco" etc. How reliable in 2026?
   - **RSS / web scraping** — Hackaday, Printables, Makerworld trending: do these expose trend data via RSS or scrapeable HTML?
   - Which combination of these sources gives signal quality equivalent to Apify's Instagram scraper?

3. **Self-hosted hashtag intelligence — replacing Flick**
   - Flick's core value: hashtag difficulty, volume estimate, average engagement per hashtag. Can we build this?
   - From Instagram public data: can we infer hashtag volume and engagement by scraping the hashtag page's top posts and computing average likes/comments?
   - Is this stable enough for a weekly hashtag audit, or does Meta block hashtag page scraping specifically?
   - Any open-source hashtag analytics tools that already do this?

4. **Realistic maintenance burden**
   - For a self-built Instagram scraper: what's the realistic failure rate? Hours/month to maintain against Meta's anti-bot updates?
   - Compare: Apify handles all maintenance for $49/mo vs self-built at $0/mo but X hours/month. What is X, realistically?
   - What's the failure mode — silent (worse) or loud with clear errors?
   - Hybrid option: thin wrapper around Apify's free tier (1,000 actor calls/mo). Does Djinn's actual query volume (4 runs/day × 30 days = 120 runs/month) fit in the free tier?

5. **Apify free tier analysis**
   - What does Apify's free tier actually include in 2026?
   - Does 120 runs/month fit? If yes, is the answer simply: use Apify free tier + self-maintain a fallback scraper?

6. **Build recommendation**
   - Optimal zero-cost, self-maintained trend stack for Djinn Media Layer 1
   - Concrete architecture: which sources, which libraries, query cadence, output format
   - Realistic risks and mitigations
   - Estimated build time (hours) and ongoing maintenance time per month

**Output format:**
Structured report, one section per question. Be specific — name actual library versions, actual API endpoints, actual free tier limits. Flag anything likely to change in the next 6 months. Cite sources.

**Deliver as:** Write markdown artifact directly to `djinn/research/marcus/TASK-015_diy-trend-stack.md` in `github.com/DrManzo/djinn-vault` and commit. Fallback: `gdrive:Typhons-Forge/research/marcus/TASK-015_diy-trend-stack.md`. Claude reads on demand — do NOT paste into chat.

---

## TASK-016
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-05-31 by Salomon
- completed: 2026-05-31 by Claude

**Goal:** Build `djinn-media-publish` — posts a finished reel to Instagram and/or Facebook via Meta Graph API. Zero human steps after the command fires.

**File:** `/home/drmanzo/.local/bin/djinn-media-publish`

**Interface:**
```
djinn-media-publish <project_id> [--platform ig|fb|both] [--dry-run]
```
- `--platform` defaults to `both`
- `--dry-run` prints what would happen, makes no API calls

**Config file:** `~/.config/djinn/meta.env` (chmod 600, never git-tracked)
```
META_PAGE_TOKEN=<long-lived page token>
IG_USER_ID=<instagram user id>
FB_PAGE_ID=<facebook page id>
```

**Inputs (read from project manifest.json):**
- `exports/reel/{job_slug}_reel.mp4` — the video to upload (must exist)
- `captions/caption_reel.txt` — caption text (fallback: manifest `notes` field)
- `~/.local/share/djinn-media/media-context.json` → `job_hashtags[job_slug]` — hashtag list (fallback: empty)

**Instagram publish flow (two-step per Meta Graph API):**
1. POST `https://graph.facebook.com/v19.0/{IG_USER_ID}/media`
   - `media_type=REELS`, `video_url=<public URL or upload>`, `caption=<caption + hashtags>`, `share_to_feed=true`
   - Returns `creation_id`
2. POST `https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish`
   - `creation_id=<from step 1>`
   - Returns `ig_media_id`

**Note on video delivery:** Meta requires a publicly accessible URL for the video, not a local path. Use rclone to push the reel to `gdrive:Typhons-Forge/posts/{project_id}/` first, then generate a public link — OR use Meta's resumable upload endpoint. Simpler path: upload to a temporary public URL via rclone + GDrive share link. Document whichever approach works.

**Facebook publish flow:**
- POST `https://graph.facebook.com/v19.0/{FB_PAGE_ID}/videos`
  - `file_url=<same public URL>`, `description=<fb_caption>` (shorter, 2–3 hashtags only per Marcus Section 4)
  - Returns `fb_post_id`

**Caption handling:**
- IG caption = full caption + all hashtags from `job_hashtags`
- FB caption = first 2 sentences of caption + 2–3 hashtags max (strip the rest)
- If `captions/caption_reel.txt` missing → use manifest `notes` field as caption

**Outputs — write back to manifest.json:**
```json
"published": {
  "instagram": { "media_id": "...", "published_at": "ISO8601" },
  "facebook":  { "post_id":  "...", "published_at": "ISO8601" }
}
```
- Update manifest `status = "published"`
- Append entry to `~/.local/share/djinn-media/publish-log.json`

**Error handling:**
- Any API error → print error + exit 1. Do NOT retry automatically.
- Missing config → print which key is missing + exit 1 with setup instructions
- Missing reel file → exit 1 with the expected path

**Telegram notification on success:**
```
✅ Djinn Media — posted
Job: {job_slug}
IG: {ig_media_id}
FB: {fb_post_id}
```

**Success criteria:**
```bash
# Dry run (no credentials needed to test logic):
djinn-media-publish 2026-05-31_mini-vases-job4 --dry-run
# Should print: platform targets, reel path, caption preview, hashtag count

# Syntax check:
python3 -m py_compile ~/.local/bin/djinn-media-publish && echo OK
```

**Report back:** COMMS.md — confirm dry-run output looks correct. Real publish test happens when Javier has Meta credentials in meta.env.

---

## TASK-017
- assigned_to: salomon
- status: done
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-05-31 by Salomon
- completed: 2026-05-31 by Claude

**Goal:** Build `djinn-meta-token-refresh` — keeps the Meta Page access token alive. Tokens expire; a silent expiry breaks all publishing. This cron prevents that.

**Files:**
- `/home/drmanzo/.local/bin/djinn-meta-token-refresh`
- `~/.config/systemd/user/djinn-meta-token-refresh.service`
- `~/.config/systemd/user/djinn-meta-token-refresh.timer` (monthly, 1st of each month, 03:00)

**Interface:** `djinn-meta-token-refresh` (no args — reads and writes meta.env in place)

**Logic:**
1. Read `META_PAGE_TOKEN` from `~/.config/djinn/meta.env`
2. Call `GET https://graph.facebook.com/v19.0/oauth/access_token` with:
   - `grant_type=fb_exchange_token`
   - `client_id={APP_ID}` (read from meta.env as `META_APP_ID`)
   - `client_secret={APP_SECRET}` (read from meta.env as `META_APP_SECRET`)
   - `fb_exchange_token={current token}`
3. On success: overwrite `META_PAGE_TOKEN=<new_token>` in meta.env (preserve all other lines)
4. Send Telegram: `✅ Meta token refreshed — expires in 60 days`
5. On failure: send Telegram alert + exit 1, do NOT overwrite the existing token

**Config added to `~/.config/djinn/meta.env`:**
```
META_APP_ID=<from Meta Developer Console>
META_APP_SECRET=<from Meta Developer Console>
```

**Success criteria:**
```bash
python3 -m py_compile ~/.local/bin/djinn-meta-token-refresh && echo OK
systemctl --user list-timers | grep meta-token
```

**Report back:** COMMS.md — confirm timer is active. Real token exchange test happens when Javier has app credentials.

---

## TASK-018
- assigned_to: salomon
- status: done
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-05-31 by Salomon
- completed: 2026-05-31 by Claude

**Goal:** Build `djinn-social-analyst` — daily analytics pull from Meta Graph API. Measures what's working. Feeds the feedback loop that improves future captions and hashtags.

**Files:**
- `/home/drmanzo/.local/bin/djinn-social-analyst`
- `~/.config/systemd/user/djinn-social-analyst.service`
- `~/.config/systemd/user/djinn-social-analyst.timer` (daily at 00:30 UTC)

**Interface:** `djinn-social-analyst [--days 7]` (default: last 7 days of posts)

**Config:** reads `~/.config/djinn/meta.env` (IG_USER_ID, META_PAGE_TOKEN)

**Logic:**
1. Call `GET /{IG_USER_ID}/media?fields=id,timestamp,caption&limit=20` → get list of recent post IDs
2. For each post in the last `--days` days, call `GET /{media_id}/insights?metric=reach,plays,saved,shares,comments,ig_reels_avg_watch_time`
3. Build a record per post: `{media_id, timestamp, caption_preview (first 60 chars), reach, plays, saved, shares, comments, avg_watch_ms}`
4. Write full record to `~/Obsidian/djinn/social/analytics/YYYY-MM-DD.json`
5. Sort posts by `(saved + shares)` descending
6. Write `~/Obsidian/djinn/social/TREND-SIGNAL.md`:

```markdown
# Trend Signal — {YYYY-MM-DD}
_Updated by djinn-social-analyst_

## Top performers (last 7 days, by saves + shares)
| Post | Reach | Saves | Shares | Watch time |
...

## Bottom performers
...

## Signal deltas
- Avg watch time this week vs last week: X ms
- Top hashtag pattern: [inferred from top post captions]
- Recommended caption length: X chars (median of top 3)
```

6. `git -C ~/Obsidian add djinn/social/ && git commit -m "social: analyst {date}" && git push`
7. Telegram: `📊 Social report ready — {date}. Top post: {caption_preview} ({saves} saves, {shares} shares)`

**Output files:**
- `~/Obsidian/djinn/social/analytics/YYYY-MM-DD.json` — raw per-post metrics
- `~/Obsidian/djinn/social/TREND-SIGNAL.md` — human + agent readable summary

**Error handling:** If API returns no data (no posts yet) → write empty analytics file + log "no posts in window" to Telegram. Do not crash.

**Success criteria:**
```bash
python3 -m py_compile ~/.local/bin/djinn-social-analyst && echo OK
systemctl --user list-timers | grep social-analyst
# Create the output dirs:
mkdir -p ~/Obsidian/djinn/social/analytics
```

**Report back:** COMMS.md — confirm timer active, dirs created, dry-run or syntax check passes.

---

## TASK-019
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-05-31 by Claude
- deployed: 2026-05-31 by Salomon (timer enabled, firecrawl-py installed)
- context: Phase 3 — build djinn-trend-agent: multi-source trend poller → TREND-SIGNAL.md + HASHTAG-BANK.md
- outcome: Built with Firecrawl search/scrape + Printables RSS (Apify dropped — Firecrawl covers all sources). Salomon: enable timer (see deploy note below).

**Goal:** Poll 4 sources every 6 hours. Feed raw results to Ollama phi4:14b. Write synthesized trend signal that Layer 2 caption agent reads before generating content.

**Updated architecture — Firecrawl as primary scraping engine:**
Firecrawl (`fc-...`, already saved to `~/.config/djinn/firecrawl.env`) replaces the need for separate Reddit and YouTube API credentials. One key covers web search + URL scraping across all platforms.

**Files:**
- `/home/drmanzo/.local/bin/djinn-trend-agent`
- `~/.config/systemd/user/djinn-trend-agent.service`
- `~/.config/systemd/user/djinn-trend-agent.timer` (every 6h: `OnCalendar=*-*-* 00,06,12,18:05:00`)

**Config files:**
- `~/.config/djinn/firecrawl.env` → `FIRECRAWL_API_KEY=fc-...` ✅ already set
- `~/.config/djinn/apify.env` → `APIFY_API_TOKEN=` (create stub, fill when Javier has key)

**Output files:**
- `~/Obsidian/djinn/social/TREND-SIGNAL.md` — written every 6h run
- `~/Obsidian/djinn/social/HASHTAG-BANK.md` — written on Sunday runs only (weekly deep audit)
- `~/.local/share/djinn-media/media-context.json` — updated with `trending_topics`, `recommended_hook_style`, `hashtag_candidates`, `format_signals`

**Dependencies (pip install):** `firecrawl-py`, `requests` (already present)

---

**Source 1 — Firecrawl web search (Reddit + YouTube + maker sites):**
```python
from firecrawl import FirecrawlApp
fc = FirecrawlApp(api_key=FIRECRAWL_KEY)

searches = [
    "reddit r/3Dprinting top posts today 3D printing maker",
    "reddit r/glassheads top posts today functional glass art",
    "youtube shorts trending 3D printing maker 2026",
    "makerworld bambu trending models 3D printing",
]
results = []
for query in searches:
    r = fc.search(query, limit=5)
    results.extend(r.get("data", []))
# Each result has: url, title, description, markdown content
```
Extract: titles, descriptions, any hashtags or tags mentioned.
If `FIRECRAWL_API_KEY` is empty → skip silently.

**Source 2 — Firecrawl scrape (Makerworld + Printables trending pages):**
```python
pages = [
    "https://makerworld.com/en/models?sort=trending",
    "https://www.printables.com/model?sort=trending",
]
for url in pages:
    result = fc.scrape_url(url, formats=["markdown"])
    # result["markdown"] is clean text of the page
    # extract: model names, categories, like counts where visible
```
Fallback if scrape fails: skip that page silently.

**Source 3 — Printables RSS (always runs, no key needed):**
```python
import xml.etree.ElementTree as ET
r = requests.get("https://www.printables.com/rss", timeout=15)
root = ET.fromstring(r.content)
items = root.findall(".//item")[:10]
# extract: title, description, category
```
No credentials. Always runs. Floor-level signal even if all other sources fail.

**Source 4 — Apify Instagram scraper (optional, fill key when available):**
```python
# Only runs if APIFY_API_TOKEN is set in ~/.config/djinn/apify.env
url = "https://api.apify.com/v2/acts/apify~instagram-hashtag-scraper/run-sync-get-dataset-items"
payload = {"hashtags": ["3dprinting", "functionalart", "makersmark"], "resultsLimit": 9}
r = requests.post(url, json=payload, headers={"Authorization": f"Bearer {APIFY_TOKEN}"}, timeout=120)
# Returns: caption, likesCount, commentsCount, hashtags[]
```
If `APIFY_API_TOKEN` is empty → skip silently. Firecrawl covers maker trend signal in the interim.

---

**Ollama synthesis layer:**

After collecting raw data from all sources, build a context string and call Ollama:

```python
import subprocess, json

prompt = f"""You are the trend intelligence layer for Djinn Media, a 3D print shop social media pipeline (Typhon's Forge).

Raw trend data collected {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}:

{combined_raw_text}

Extract the following and respond ONLY with valid JSON — no explanation, no markdown, just the JSON object:
{{
  "trending_topics": ["<3-5 themes resonating in maker/3D printing/cannabis accessory communities>"],
  "recommended_hook_style": "<one sentence: what hook format is working right now>",
  "hashtag_candidates": ["<10-15 Instagram-safe hashtags — NEVER include #weed #cannabis #420 #marijuana>"],
  "format_signals": "<what visual format is performing: timelapse, reveal, POV, text-on-screen, etc.>",
  "platform_notes": "<any specific IG or FB observations this week>"
}}"""

result = subprocess.run(
    ["ollama", "run", "phi4:14b", prompt],
    capture_output=True, text=True, timeout=120
)
# Parse JSON from result.stdout, strip any surrounding text
```

If Ollama fails or JSON parse fails → keep previous TREND-SIGNAL.md unchanged, send Telegram alert, exit 0 (don't kill the timer).

---

**TREND-SIGNAL.md format** (overwrite every run):
```markdown
# Trend Signal — {YYYY-MM-DD HH:MM UTC}
_Updated by djinn-trend-agent — sources: {which sources ran}_

## Trending Topics
{trending_topics as bullet list}

## Hook Style
{recommended_hook_style}

## Format Signal
{format_signals}

## Hashtag Candidates
{hashtag_candidates as space-separated line — safe to paste into caption}

## Platform Notes
{platform_notes}

---
_Layer 2 caption and hashtag agents read this file before generating content._
```

**HASHTAG-BANK.md** (Sunday runs only — append/overwrite weekly section):
Write a dated section with the full hashtag_candidates list + source attribution. Accumulates over time as a historical record of what was trending each week.

**media-context.json** — merge the Ollama output into the existing file:
```python
ctx = {}
if CONTEXT_JSON.exists():
    ctx = json.loads(CONTEXT_JSON.read_text())
ctx.update({
    "updated_at": now_iso,
    "trending_topics": result["trending_topics"],
    "recommended_hook_style": result["recommended_hook_style"],
    "recommended_format": result["format_signals"],
    "platform_notes": result["platform_notes"],
})
# NOTE: do NOT overwrite job_hashtags — that's written by caption agent per job
CONTEXT_JSON.write_text(json.dumps(ctx, indent=2))
```

**Monitoring — stale signal detection:**
After writing TREND-SIGNAL.md, check if `djinn-social-analyst` has also written analytics recently (check mtime of `djinn/social/analytics/` newest file). If newest analytics file is > 48h old, append a warning line to TREND-SIGNAL.md: `⚠️ Own analytics stale — djinn-social-analyst may not have run.`

**Git + Telegram:**
```bash
git -C ~/Obsidian add djinn/social/TREND-SIGNAL.md djinn/social/HASHTAG-BANK.md
git -C ~/Obsidian commit -m "trend: signal update {date} {HH:MM}"
git -C ~/Obsidian push
```
Telegram: `🔮 Trend signal updated — {n} sources, {len(topics)} topics, {len(hashtags)} hashtag candidates`

**Graceful degradation:** If ALL sources fail (no API keys set, all network errors) → do not overwrite TREND-SIGNAL.md. Send Telegram: `⚠️ djinn-trend-agent: all sources failed — signal unchanged`. Exit 0.

**Success criteria:**
```bash
# Install deps
pip install praw google-api-python-client --quiet

# Create config stubs
for f in apify.env reddit.env youtube.env; do
  touch ~/.config/djinn/$f && chmod 600 ~/.config/djinn/$f
done

# Syntax check
python3 -m py_compile ~/.local/bin/djinn-trend-agent && echo OK

# Printables RSS runs without any API key — smoke test:
djinn-trend-agent --sources printables --dry-run
# Should print extracted Printables titles and exit 0

# Timer active:
systemctl --user list-timers | grep trend-agent
```

Add `--sources` flag: comma-separated list of `apify,reddit,youtube,printables` (default: all). `--dry-run`: collect data, print synthesis input, skip Ollama and file writes.

**Report back:** COMMS.md — sources that ran successfully, sample trending_topics extracted, Printables smoke test output, timer status.

---

## TASK-020
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-05-31 by Claude
- context: Phase 3 — wire TREND-SIGNAL.md + HASHTAG-BANK.md into djinn-media-publish-prep caption generation
- outcome: Wired. Trend signal injected into both prompt paths. job_hashtags written to media-context.json per job. Graceful when no signal file exists.

**Goal:** The caption agent in `djinn-media-publish-prep` currently generates captions without knowing what's trending. Wire in TREND-SIGNAL.md and HASHTAG-BANK.md so captions reflect current hooks, formats, and hashtags.

**File:** `/home/drmanzo/.local/bin/djinn-media-publish-prep` (modify existing)

**What to find in the file:** The section that calls Ollama to generate a caption. It currently passes job metadata (project_id, notes, media_type) to the model. Find that call.

**Changes:**

1. Before the Ollama caption call, read context:
```python
TREND_FILE   = Path.home() / "Obsidian/djinn/social/TREND-SIGNAL.md"
HASHTAG_BANK = Path.home() / "Obsidian/djinn/social/HASHTAG-BANK.md"
CONTEXT_JSON = Path.home() / ".local/share/djinn-media/media-context.json"

trend_context = TREND_FILE.read_text() if TREND_FILE.exists() else "No trend signal available."
hashtag_section = ""
if HASHTAG_BANK.exists():
    # pull only the most recent weekly section (last 30 lines)
    lines = HASHTAG_BANK.read_text().splitlines()
    hashtag_section = "\n".join(lines[-30:])
```

2. Inject into the Ollama prompt as a context block:
```
## Current Trend Signal
{trend_context[:800]}  ← truncate to keep prompt lean

## Recent Hashtag Bank
{hashtag_section[:400]}
```

3. Update the system prompt instruction to use this context:
```
Use the hook style and format from the trend signal above.
Select hashtags from the hashtag bank that are relevant to this job.
Do NOT use #weed #cannabis #420 #marijuana or any variant.
```

4. Also write `job_hashtags` into media-context.json after caption generation:
```python
# After Ollama returns hashtags for this job:
ctx = {}
if CONTEXT_JSON.exists():
    try: ctx = json.loads(CONTEXT_JSON.read_text())
    except: pass
ctx.setdefault("job_hashtags", {})[job_slug] = selected_hashtags
CONTEXT_JSON.write_text(json.dumps(ctx, indent=2))
```
This makes `djinn-media-publish` find the right hashtags in media-context.json.

**If TREND-SIGNAL.md doesn't exist yet** (trend agent not run yet): proceed normally with generic caption — do not crash. Log: `[publish-prep] No trend signal — generating generic caption`.

**Success criteria:**
```bash
python3 -m py_compile ~/.local/bin/djinn-media-publish-prep && echo OK
# Then: djinn-media-publish-prep {any_project_id} --dry-run
# Output should include "trend signal loaded" or "no trend signal" line
```

**Report back:** COMMS.md — confirm caption generation now references trend signal, show sample prompt snippet with context injected.

---

## TASK-021
- assigned_to: salomon
- status: done
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-05-31 by Salomon
- context: Firecrawl debloat — rewrite djinn-style-scrape: replace fragile DDG vqd token scraping with fc.search()

**Goal:** Replace the 2-step DuckDuckGo image search (extract vqd token from HTML → query /i.js) with a single `fc.search()` call. The vqd pattern breaks silently whenever DDG changes their frontend.

**File:** `/home/drmanzo/.local/bin/djinn-style-scrape`

**Current pattern (fragile):**
```python
# Step 1 — extract vqd token from DDG HTML
r = urllib.request.urlopen(f"https://duckduckgo.com/?q={q}&iax=images&ia=images")
vqd = re.search(r'vqd="([^"]+)"', html).group(1)
# Step 2 — query image results
r = urllib.request.urlopen(f"https://duckduckgo.com/i.js?q={q}&vqd={vqd}&...")
```

**Replacement:**
```python
from firecrawl import FirecrawlApp
import os, json
from pathlib import Path

key = open(Path.home() / ".config/djinn/firecrawl.env").read()
# parse FIRECRAWL_API_KEY=... line
FIRECRAWL_KEY = dict(l.split("=",1) for l in key.splitlines() if "=" in l).get("FIRECRAWL_API_KEY","")

fc = FirecrawlApp(api_key=FIRECRAWL_KEY)

for query in QUERIES:
    results = fc.search(query, limit=8)
    for item in results.get("data", []):
        # item has: url, title, description, markdown
        # save to references/scraped/ as before
```

**Preserve:**
- Same output folder: `references/scraped/`
- Same query list (8 aesthetic queries)
- Same file-per-query output structure
- `--dry-run` flag if it exists

**Success criteria:**
```bash
python3 -m py_compile ~/.local/bin/djinn-style-scrape && echo OK
djinn-style-scrape --dry-run   # or djinn-style-scrape (first query only, limit 3)
```

**Report back:** COMMS.md — confirm first search returns results, no urllib.request import remaining.

---

## TASK-022
- assigned_to: salomon
- status: done
- priority: low
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-05-31 by Claude
- context: Firecrawl debloat — replace Makerworld + Thingiverse HTML scraping in djinn-model-fetch with fc.scrape_url()
- outcome: _scrape_links() replaced. Firecrawl scrape first (extracts markdown links via regex), HTMLParser fallback if key not set. MakerWorld handler unchanged (raises login error — correct). Printables GraphQL unchanged.

**Goal:** `djinn-model-fetch` currently scrapes Makerworld and Thingiverse with raw HTMLParser. These sites change their markup; the scraping breaks silently. Replace with `fc.scrape_url(url, formats=["markdown"])` which returns clean parsed markdown.

**File:** `/home/drmanzo/.local/bin/djinn-model-fetch`

**Keep as-is:** Printables GraphQL API (stable, structured JSON — no change needed)

**Replace:**
- Makerworld HTML parsing section → `fc.scrape_url("https://makerworld.com/en/models/{id}", formats=["markdown"])`
- Thingiverse HTML parsing section → `fc.scrape_url("https://www.thingiverse.com/thing:{id}", formats=["markdown"])`
- Extract model name, description, tags from `result["markdown"]` using regex on clean text (much simpler than HTMLParser)

**Note:** Only do this if Makerworld/Thingiverse scraping is actively broken or causes issues. This is a "next time you're in the file" fix — not urgent. Do TASK-019, 020, 021 first.

**Report back:** COMMS.md — confirm scrape returns expected fields for one Makerworld model ID.

---

## TASK-023
- assigned_to: claude
- status: done
- completed: 2026-06-01 by Claude
- priority: normal
- trigger: manual
- created: 2026-05-31 by Javier
- context: PHASE-4: Build — Wire Rabbit R1 as mobile Telegram terminal for Djinn commands
- output: djinn-telegram-gateway updated — incoming voice message transcription (Groq Whisper), /r1 command (compact text + auto-voice), R1 mode persists for session

## TASK-024
- assigned_to: salomon
- status: done
- priority: low
- trigger: manual
- created: 2026-05-31 by Claude
- context: SUPERSEDED by TASK-044 + TASK-042 — no action needed — Mount extra HDD on Typhon as Tier 2 cold archive storage

## TASK-025
- assigned_to: claude
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-05-31 by Claude
- context: Build djinn-marcus — Perplexity CLI research agent (vault-integrated, topic threads, QUEUE.md-aware)
- output: ~/.local/bin/djinn-marcus — stdlib Python, sonar-pro default, 7 commands, git auto-commit on writes

## TASK-026
- assigned_to: claude
- status: done
- completed: 2026-06-01 by Claude
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude
- context: PHASE-3: Infrastructure — run anytime, no dependency — Fix gdrive-backup-manifest rotation — runs hourly, should be weekly, keeps all timestamped files indefinitely (bloat)

## TASK-027
- assigned_to: javier
- status: done
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude
- context: JAVIER: Fill Shippo key when ready — no phase dependency — Fill SHIPPO_API_KEY in ~/.config/djinn/shop.env — last remaining shop variable, activates live shipping rates and label purchase

## TASK-028
- assigned_to: javier
- status: done
- priority: low
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-06-01 by Javier
- context: Keeping Perplexity Pro as-is — student discount applied, Marcus lane stays active

## TASK-029
- assigned_to: claude
- status: done
- completed: 2026-06-01 by Claude
- priority: normal
- trigger: manual
- created: 2026-05-31 by Javier
- context: PHASE-4: Build — djinn-marcus-sync — Perplexity Pro library scraper
- output: ~/.local/bin/djinn-marcus-sync — Xvfb+Firefox bypasses Cloudflare, extracts cookies from snap profile, diffs against state file + RAW/, saves new threads with frontmatter to RAW/, Telegram notification, git auto-commit. Hourly systemd timer installed (active). 20 threads detected on first dry-run. Run djinn-marcus-sync to do first full sync, --full to resync all.

## TASK-030
- assigned_to: claude
- status: done
- priority: normal
- trigger: manual
- created: 2026-06-01 by Javier
- completed: 2026-06-01 by Claude
- context: PHASE-3: Infrastructure — run anytime, no dependency — COMMS.md rotation — archive entries older than 30 days to djinn/communications/archive/COMMS-YYYY-MM.md, keep COMMS.md lean and fast to scan

## TASK-031
- assigned_to: claude
- status: done
- completed: 2026-06-01 by Claude
- priority: normal
- trigger: manual
- created: 2026-06-01 by Javier
- context: PHASE-3: Infrastructure — run anytime, no dependency — Djinn conversation log — both gateways (Telegram + Discord) write daily exchange summary to djinn/logs/conversations/YYYY-MM-DD.md so key decisions made between Javier and Djinn are vault-persistent

## TASK-032
- assigned_to: claude
- status: done
- priority: high
- trigger: manual
- created: 2026-06-01 by Javier
- completed: 2026-06-01 by Claude
- context: PHASE-3: Quick fix — run anytime, no dependency — Claude queue alert — Djinn checks QUEUE.md for assigned_to:claude + status:pending at gateway startup and pings Javier via Telegram so pending Claude tasks don't silently pile up

## TASK-033
- assigned_to: claude
- status: done
- completed: 2026-06-01 by Claude
- priority: normal
- trigger: manual
- created: 2026-06-01 by Javier
- context: PHASE-3: Infrastructure — run anytime, no dependency — Typhon heartbeat staleness alert — if HEARTBEAT-typhon.md last beat is >24h old, Djinn alerts Javier on next Telegram message

## TASK-034
- assigned_to: claude
- status: done
- priority: high
- trigger: manual
- created: 2026-06-01 by Javier
- completed: 2026-06-01 by Claude
- context: PHASE-3: Quick fix — run anytime, no dependency — Fix djinn-printer-files-backup exit code — rsync transfers successfully but set -euo pipefail causes exit 1. Add || true to rsync pipe.

## TASK-035
- assigned_to: claude
- status: done
- priority: normal
- trigger: manual
- created: 2026-06-01 by Javier
- completed: 2026-06-01 by Claude
- context: PHASE-3: Infrastructure — run anytime, no dependency — Diagnose djinn-print-monitor-v2 — timer active but service dies immediately. v1 is covering but v2 should replace it.

## TASK-036
- assigned_to: claude
- status: done
- priority: normal
- trigger: manual
- created: 2026-06-01 by Javier
- completed: 2026-06-01 by Claude
- context: PHASE-3: Infrastructure — run anytime, no dependency — forge-sync still hitting GDrive rateLimitExceeded — further stagger or backoff needed

## TASK-037
- assigned_to: marcus
- status: done
- note: research delivered in two passes. Part 1 (825 lines): domains 1-7 (Law School, LSAT, CA Bar, Contracts, Torts, Civil Procedure, Corporate Law). Part 2 (808 lines): domains 8-13 (LLC Formation, CA Business Compliance, Contract Drafting, Cannabis-Adjacent Business, Legal Research Methods, Self-Study Path). Both vaulted in djinn/research/marcus/law/. RESEARCH GATE LIFTED — all three suites (Law, Psych, Finance) now complete. PHASE-4 builds can begin.
- priority: high
- trigger: manual
- created: 2026-06-01 by Javier
- context: PHASE-2: Research gate — run after TASK-045. No suite builds until all three Marcus tasks complete — Djinn Law Suite — 13 research queries covering law school paths, LSAT, bar prep, contracts, torts, civil procedure, corporate law, LLC formation, compliance, contract drafting, legal research methods
- brief: djinn/research/marcus/TASK-037_djinn-law-research.md
- output: djinn/research/marcus/law/TASK-037_djinn-law-research-output.md (partial)

## TASK-038
- assigned_to: marcus
- status: done
- note: research delivered 2026-06-01 as single combined file (759 lines, all 14 domains covered with citations). Saved to djinn/research/marcus/psychology/TASK-038_djinn-psyc-research-output.md
- priority: high
- trigger: manual
- created: 2026-06-01 by Javier
- context: PHASE-2: Research gate — run after TASK-045. No suite builds until all three Marcus tasks complete — Djinn Psyc Suite — 14 research queries covering behavioral/cognitive psych, Freud, Jung, shadow work, Jordan Peterson, addiction, attachment, trauma, social psychology, EQ, personality frameworks
- brief: djinn/research/marcus/TASK-038_djinn-psyc-research.md
- output: djinn/research/marcus/psychology/ (14 files)

## TASK-039
- assigned_to: marcus
- status: done
- note: research delivered 2026-06-01 as single combined file (923 lines, all 20 domains covered with real citations). Saved to djinn/research/marcus/finance/TASK-039_djinn-cash-research-output.md
- priority: high
- trigger: manual
- created: 2026-06-01 by Javier
- context: PHASE-2: Research gate — run after TASK-045. No suite builds until all three Marcus tasks complete — Djinn Cash Suite — 20 research queries covering budgeting, investing, stock analysis, 7-day speculation framework, market indicators, crypto, federal/CA tax law, tax-advantaged accounts, self-employment taxes, wealth building. All outputs must note legal compliance constraints.
- brief: djinn/research/marcus/TASK-039_djinn-cash-research.md
- output: djinn/research/marcus/finance/ (20 files)

## TASK-040
- assigned_to: claude
- status: done
- completed: 2026-06-01 by Claude
- priority: normal
- trigger: manual
- created: 2026-06-01 by Javier
- context: PHASE-4: Build — gated on TASK-037/038/039 research complete — Build djinn-gemini — Gemini AI Studio API integration. Lane: Drive document reading, YouTube video analysis/transcription, long-context document processing, image batch QC for media pipeline. Follows djinn-marcus pattern — vault-persistent outputs, topic threads, git auto-commit.
- ready: API key stored ~/.config/djinn/gemini.env ✓ | google-genai SDK installed ✓ | gemini-2.5-flash confirmed live ✓ | models available: gemini-2.5-pro, gemini-2.5-flash, deep-research-max-preview

## TASK-041
- assigned_to: javier
- status: done
- priority: low
- trigger: manual
- created: 2026-06-01 by Claude
- context: SUPERSEDED — drive contents audited manually 2026-06-01 — Audit Typhon drives before archive setup — check what is on Extreme SSD (sdb, 275GB used, NTFS) and The Library (sdc, 334GB used, exFAT). Decide: reformat to ext4 for cold archive use, or keep existing content and partition. Do NOT reformat without knowing what is on them.

## TASK-042
- assigned_to: claude
- status: done
- priority: high
- trigger: manual
- created: 2026-06-01 by Claude
- completed: 2026-06-01 by Claude (done as part of TASK-044 execution)
- context: PHASE-3: Run after TASK-044/045 complete — Set up Typhon cold archive structure — once TASK-041 confirmed, format target drive to ext4, create /mnt/archive/ directory tree (printer-files/, media-files/, vault-snapshots/), wire into storage protocol as Tier 2. Auto-mount via /etc/fstab.

## TASK-043
- assigned_to: claude
- status: done
- completed: 2026-06-01 by Claude
- priority: normal
- trigger: manual
- created: 2026-06-01 by Claude
- context: PHASE-4: Build — gated on TASK-037/038/039 research complete — Gemini TTS — wire gemini-2.5-flash-tts into Djinn. Djinn gets a voice: Telegram voice message responses for conversational exchanges. Optional --voice flag on gateway. Also explore native audio (gemini-2.5-flash-native-audio) for voice message INPUT from phone.

## TASK-044
- assigned_to: typhon
- status: done
- priority: critical
- trigger: manual
- created: 2026-06-01 by Claude
- completed: 2026-06-01 by Claude (executed via SSH)
- context: PHASE-1: Run now — gates all builds — Copy Extreme SSD → /mnt/storage, then reformat to ext4 as djinn-archive cold storage. 552GB free on storage, 275GB to copy — fits. NOTE: Library-Backup (271GB on Extreme SSD) may duplicate library-rescue (263GB already on storage) — verify before copying, skip if identical.

**Commands:**
```bash
# Step 1 — check if Library-Backup duplicates library-rescue (compare sizes)
SSD_SIZE=$(du -sb "/run/media/tf-tthq/Extreme SSD/Library-Backup" 2>/dev/null | cut -f1)
STG_SIZE=$(du -sb /mnt/storage/library-rescue 2>/dev/null | cut -f1)
echo "SSD Library-Backup: $SSD_SIZE bytes"
echo "Storage library-rescue: $STG_SIZE bytes"
# If within 5% of each other — skip Library-Backup in rsync (add --exclude='Library-Backup')

# Step 2 — copy (exclude Library-Backup if duplicate confirmed above)
rsync -av --progress \
  --exclude='Library-Backup' \
  --exclude='System Volume Information' \
  "/run/media/tf-tthq/Extreme SSD/" /mnt/storage/extreme-ssd-backup/

# Step 3 — hard verify: abort if copied size is less than 3GB (means something went wrong)
COPIED=$(du -sb /mnt/storage/extreme-ssd-backup/ | cut -f1)
echo "Copied: $COPIED bytes"
[ "$COPIED" -gt 3000000000 ] || { echo "ABORT: copy too small, not formatting"; exit 1; }

# Step 4 — unmount
udisksctl unmount -b /dev/sdb1
sleep 2

# Step 5 — reformat to ext4
sudo mkfs.ext4 -L "djinn-archive" /dev/sdb1

# Step 6 — mount + persist
sudo mkdir -p /mnt/archive
UUID=$(sudo blkid -s UUID -o value /dev/sdb1)
echo "UUID=$UUID /mnt/archive ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo mount /mnt/archive

# Step 7 — create archive directory structure
mkdir -p /mnt/archive/{printer-files,media-files,vault-snapshots,library-rescue}

# Step 8 — final report
echo "=== TASK-044 COMPLETE ===" 
df -h /mnt/archive
echo "UUID: $UUID"
echo "Structure:"; ls /mnt/archive/
```

**Abort condition:** Step 3 will hard-stop before any format if the copy looks wrong. Safe to run autonomously.
**Report back:** paste Step 8 output into COMMS.md, mark TASK-044 done

## TASK-045
- assigned_to: claude
- status: done
- priority: critical
- trigger: manual
- created: 2026-06-01 by Claude
- completed: 2026-06-01 by Claude
- context: PHASE-1: Run after TASK-044 completes — gates all builds — Full Typhon system audit — snap bloat, log sizes, home directory, duplicate data (library-rescue vs Library-Backup), ollama-system (53GB of models — which are still needed?), running services health check, disk cleanup. Report what can be safely removed.

## TASK-052
- assigned_to: claude
- status: done
- completed: 2026-06-01 by Claude
- priority: normal
- trigger: manual
- created: 2026-06-01 by Javier
- context: PHASE-4: Build — Wire djinn-gemini into Telegram gateway
- output: djinn-telegram-gateway updated — /gemini <cmd> <args> routes to djinn-gemini CLI (ask, youtube, url, doc, research). ANSI codes stripped, header/path lines filtered, 3800-char truncation for Telegram limit, 180s timeout for long analyses. /help updated.

## TASK-054
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-06-01 by Claude
- completed: 2026-06-01 by Claude
- context: PHASE-ALPHA Sprint 1 — djinn-personal-db SQLite library + CLI

**Goal:** Create the single source of truth for Javier's personal state — sobriety, habits, streaks, people, deadlines, Black Book log.

**File:** `~/.local/bin/djinn-personal-db` (Python, chmod +x)

**Schema:** See `djinn/research/architecture/PHASE-ALPHA-PERSONAL-LAYER.md` — tables: habits, completions, streaks, sobriety, people, deadlines, black_book_log

**Seed on first run (if DB empty):**
- sobriety: start_date='2026-03-01', substance='alcohol', active=1
- habits: writing (daily), black_book (daily), exercise (daily)
- people: Mira (role='partner', archive_threshold_days=14), Craig (role='sponsor', archive_threshold_days=9999)

**CLI interface:**
```
djinn-personal-db habit done <name>           → mark complete today, update streak
djinn-personal-db habit check                 → print all streaks (name, current, longest, last done)
djinn-personal-db sobriety                    → print "Day N" from 2026-03-01 to today
djinn-personal-db deadline add <title> <YYYY-MM-DD> <domain>
djinn-personal-db deadline check              → print deadlines within 72h, JSON output
djinn-personal-db people mention <name>       → set last_mentioned = today
djinn-personal-db people check                → print name, role, days_since_mention, archived
djinn-personal-db blackbook log               → insert today's date into black_book_log (idempotent)
djinn-personal-db briefing                    → JSON: {sobriety_day, streaks{}, deadlines_72h[], blackbook_yesterday, meeting_today}
```

**DB path:** `~/.local/share/djinn/personal.db`

**Success criteria:**
```bash
djinn-personal-db sobriety          # → "Day 92." (or current count from 2026-03-01)
djinn-personal-db habit done writing
djinn-personal-db habit check       # → shows writing streak = 1
djinn-personal-db briefing | python3 -m json.tool  # → valid JSON
```

**Report back:** paste output of success criteria in COMMS.md

## TASK-055
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-06-01 by Claude
- context: PHASE-ALPHA Sprint 1 — djinn-morning rewrite, conciliary-aware briefing

**Goal:** Rewrite djinn-morning so it knows Javier, not just the system. Under 90 words. One action item. Inline buttons for habit logging.

**Depends on:** TASK-054 complete

**File:** `~/.local/bin/djinn-morning` (replace existing)

**Logic:**
1. Call `djinn-personal-db briefing` → parse JSON
2. Compose message using this template (fill from data):

```
Day {sobriety_day} sober.
{writing_line}
{one_thing}
{optional_context_line}
```

Writing line logic:
- streak > 0: "Writing: {streak} day streak."
- streak = 0 AND yesterday done: "Write today — keep the streak."
- streak = 0: "Write today."

One thing priority (pick highest):
1. Deadline in next 24h → "PSY 320 paper due TOMORROW."
2. AA meeting today → "Meeting tonight at {time}."
3. Black Book not done yesterday → "The book waited for you. Still is."
4. Creative target → "Aethoria today — 30 minutes."

Optional context line (only if something notable):
- If deadline in 48-72h: "{title} due in 2 days."
- If sobriety is a milestone (30, 60, 90, 100, 365 days): short acknowledgment

**Inline buttons (Telegram keyboard):**
```python
InlineKeyboardMarkup([[
    InlineKeyboardButton("✓ Writing", callback_data="habit_done:writing"),
    InlineKeyboardButton("✓ Black Book", callback_data="habit_done:black_book"),
    InlineKeyboardButton("✓ Exercise", callback_data="habit_done:exercise"),
    InlineKeyboardButton("Skip", callback_data="habit_skip"),
]])
```

**Tone rules:**
- Never start with "Good morning" or any greeting
- Opens with sobriety day — always, no exception
- Direct. Warm but not soft. Not clinical.
- If Black Book missed: "The book waited for you. Still is." — not "You didn't journal yesterday."
- No bullet lists. Prose only.

**Timer:** keep existing 08:00 systemd timer — but also trigger on first incoming Telegram message if before 10am and morning brief not yet sent today (flag in `/tmp/djinn-morning-{date}.sent`)

**Success criteria:**
```bash
djinn-morning   # → sends Telegram message with inline buttons, under 90 words, no errors
```

**Report back:** paste the actual Telegram message text + confirm buttons sent

## TASK-056
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-06-01 by Claude
- context: PHASE-ALPHA Sprint 1+2 — Personal commands in Telegram gateway

**Goal:** Wire personal commands and inline button handlers into existing djinn-telegram-gateway.

**Depends on:** TASK-054 complete

**File:** `~/.local/bin/djinn-telegram-gateway` (modify existing)

**Commands to add (add to dispatch table):**

```python
# /sober → sobriety day
r'/sober': handle_sober   # calls djinn-personal-db sobriety, returns "Day N."

# /done [habit]
r'/done(?:\s+(.+))?': handle_done  # calls djinn-personal-db habit done <name>
                                    # if no arg: show inline buttons for each active habit

# /check → streak status
r'/check': handle_check   # calls djinn-personal-db habit check, formats as short list

# /reflect → Black Book one-question
r'/reflect': handle_reflect  # load latest black-book entry, local Ollama, return ONE question

# /stuck → Socratic question for academic work
r'/stuck': handle_stuck   # local Ollama: given no context, return one Socratic question
                          # to surface what's blocking the user. No answer, no suggestions.

# /meeting → next AA meeting
r'/meeting': handle_meeting   # print next AA meeting from hardcoded schedule

# /craig(?:\s+(.+))? → draft message to Craig
r'/craig(?:\s+(.+))?': handle_craig  # /craig alone: prompt for message
                                      # /craig <msg>: show draft + confirm button
```

**Inline button callback handler (add to callback_query handler):**
```python
if data.startswith("habit_done:"):
    habit = data.split(":")[1]
    run_shell(f"djinn-personal-db habit done {habit}")
    answer_callback(f"✓ {habit} logged")
elif data == "habit_skip":
    answer_callback("Noted.")
```

**handle_reflect logic:**
```python
def handle_reflect(match, _raw):
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    # Try today's entry, fall back to yesterday's
    for d in [today, yesterday]:
        path = Path.home() / f"Obsidian/personal/black-book/{d}.md"
        if path.exists():
            content = path.read_text()[:3000]
            # Strip names for privacy before Ollama
            for name in ["Mira", "Craig"]:
                content = content.replace(name, "[person]")
            prompt = f"Read this journal entry. Ask ONE question about it. Do not interpret. Do not summarize. Do not offer insight. ONE question only:\n\n{content}"
            out, _, _ = run_shell(f'ollama run qwen2.5:7b "{prompt}"', timeout=60)
            run_shell("djinn-personal-db blackbook log")
            return out.strip() + "\n— Djinn"
    return "No entry found for today or yesterday. Write it first."
```

**handle_craig logic:**
```python
def handle_craig(match, _raw):
    msg = (match.group(1) or "").strip()
    if not msg:
        return "What do you want to say to Craig?\n/craig <your message>"
    # Show draft, ask confirm
    # Store draft in memory/tmp, return with confirm button
    draft_path = Path("/tmp/djinn-craig-draft.txt")
    draft_path.write_text(msg)
    return f"Draft to Craig:\n\n\"{msg}\"\n\nSend it? /craig confirm | /craig cancel"
```

**AA meeting schedule (hardcode, update when Javier provides actual times):**
```python
AA_MEETINGS = []  # Javier to fill: [{"day": "monday", "time": "19:00", "link": "..."}]
```

**Success criteria:**
- `/sober` returns current day count
- `/done writing` logs completion, returns confirmation
- `/reflect` with a Black Book entry present returns a single question (not an analysis)
- `/check` returns current streaks
- Inline buttons from morning briefing log correctly when tapped

**Report back:** test each command, paste outputs in COMMS.md

## TASK-057
- assigned_to: salomon
- status: done
- priority: normal
- trigger: manual
- created: 2026-06-01 by Claude
- completed: 2026-06-02 by Salomon
- context: PHASE-ALPHA Sprint 2 — AA meeting reminders + Craig contact

**Goal:** AA meeting reminders in morning briefing and /meeting command. Craig draft-and-confirm flow.

**Depends on:** TASK-056 complete

**What to build:**

1. AA schedule config file: `~/.config/djinn/aa-meetings.json`
   Format: `[{"day": "monday", "time": "19:00", "type": "online", "platform": "Discord", "link": ""}]`
   Javier fills this — ship the empty config with a placeholder.

2. `djinn-morning` reads `aa-meetings.json` — if meeting today, include in briefing context line.

3. `/meeting` command: reads the schedule, finds next upcoming meeting, prints:
   "Next meeting: {day} at {time} on {platform}. {link}"
   If Javier hasn't provided the schedule: "Set your meeting schedule in ~/.config/djinn/aa-meetings.json"

4. Craig contact: add Craig to `people` table with role='sponsor'. `/craig` command drafts a message and shows it. Actual send mechanism: Javier pastes it wherever Craig is (SMS, Telegram, etc.) — we don't automate send without knowing Craig's channel. Confirm flow: `/craig confirm` just confirms "drafted — ready to send" and clears tmp file.

**Success criteria:**
```bash
cat ~/.config/djinn/aa-meetings.json  # → valid JSON, empty array or placeholder
/meeting                               # → "Add your schedule to aa-meetings.json" OR meeting info
```

## TASK-058
- assigned_to: salomon
- status: done
- priority: normal
- trigger: manual
- created: 2026-06-01 by Claude
- context: PHASE-ALPHA Sprint 2 — Mira context tracking

**Goal:** Passive listener in Telegram gateway that tracks last mention of Mira (and Mira). Weekly auto-archive if not mentioned.

**Depends on:** TASK-054, TASK-056 complete

**File:** `~/.local/bin/djinn-telegram-gateway` (modify)

**Logic — add to message processing loop (after auth check, before dispatch):**

```python
TRACKED_PEOPLE = {
    "mira": "Mira",
}

def scan_for_people_mentions(text):
    if not text:
        return
    lower = text.lower()
    mentioned = set()
    for keyword, canonical in TRACKED_PEOPLE.items():
        if keyword in lower:
            mentioned.add(canonical)
    for name in mentioned:
        run_shell(f"djinn-personal-db people mention '{name}'")
```

Call `scan_for_people_mentions(text)` on every incoming message from Javier.

**Weekly archive check (add to djinn-weekly or a new Sunday cron):**

```python
# Run Sunday morning
out, _, _ = run_shell("djinn-personal-db people check")
# Parse output: if any person has days_since_mention > archive_threshold AND not archived
# Send Telegram message: "{name} hasn't come up in {N} days. Archiving her context for now
#   — say her name to bring it back."
# Then: run_shell(f"djinn-personal-db people archive '{name}'")
```

Restore: when mention is detected for an archived person → `run_shell(f"djinn-personal-db people restore '{name}'")`

**Success criteria:**
- Send a test message containing "Mira" → `djinn-personal-db people check` shows last_mentioned = today
- `djinn-personal-db people check` prints correctly

**Report back:** paste people check output after test mention

## TASK-059
- assigned_to: marcus
- status: done
- priority: high
- trigger: manual
- completed: 2026-06-01 by Marcus
- created: 2026-06-01 by Claude (per Javier)
- context: Research — what does djinn-bughunter need to run robustly as a local error reporter on Salomon? What monitoring infrastructure belongs in a self-hosted systemd/Python environment?

**Brief:**

Djinn just added `@djinn_bughunter_bot` (Telegram) + `djinn-alert` (notifier script) for failure reporting. It currently catches systemd `OnFailure` events for 7 core services and lets scripts call `djinn-alert "message"` directly. This is functional but minimal. Javier wants to know what else is needed to make this bulletproof and what patterns exist for local error monitoring at this scale.

**Who this is for:**
One-person shop. Linux (Ubuntu/Debian). Python scripts, systemd services and timers, Telegram bots. No cloud monitoring budget. Djinn is the infrastructure — needs to monitor itself.

**Research questions:**

1. **Systemd failure coverage gaps**
   - `OnFailure` only fires on clean service failure (exit 1, OOM, etc.). What does it miss?
   - What about: timer units that run but exit 0 with no output (silent no-ops), timers that never fire (misconfigured OnCalendar), services that "succeed" but produce empty/wrong output, services stuck in a restart loop?
   - What are the standard patterns for catching these in a self-hosted systemd environment?
   - Is `systemd-watchdog` (WatchdogSec=) worth adding to long-running services? What does it catch vs OnFailure?

2. **Python script error capture — beyond systemd**
   - Many Djinn scripts run via timers and swallow exceptions silently. What patterns (decorators, context managers, wrapper functions) let a script report its own failures to djinn-alert without changing every error path?
   - Is there a lightweight local equivalent of Sentry for Python that works offline? (e.g. Sentry's self-hosted, Rollbar alternatives, etc.)
   - What's the simplest pattern for "wrap any CLI script so unhandled exceptions go to Telegram"?

3. **Disk and resource monitoring**
   - What are the standard lightweight tools for monitoring disk usage, RAM, and CPU on a single Linux machine and alerting when thresholds are crossed?
   - Specifically: Salomon has a print queue, media pipeline, and Ollama models (heavy disk/RAM). What thresholds matter and what tools can alert on them without a full Prometheus/Grafana stack?
   - Can systemd itself trigger alerts on disk pressure? Or is a small cron check simpler?

4. **Telegram bot failure self-monitoring**
   - The bots themselves (djinn-personal-gateway, djinn-telegram-gateway) could crash or lose network. SystemD catches the crash — but what about: bot running but Telegram API unreachable, bot running but poll loop silently stuck, bot running but messages not being received?
   - What heartbeat or watchdog patterns exist specifically for Telegram bot processes?
   - Is there a pattern where the bot pings itself or sends a heartbeat to a secondary channel every N hours to prove it's alive?

5. **Local log aggregation — what's realistic**
   - Currently logs go to `/tmp/` and are lost on reboot. What's the minimal viable log persistence setup for a Djinn-scale system (7–10 systemd services, a dozen cron scripts)?
   - `journald` persistent logging vs flat log files — which is easier to query and alert on?
   - Any lightweight local log analysis tools that can catch patterns (e.g., "this error appeared 3 times in the last hour") without a full ELK stack?

6. **Build recommendation**
   - What's the 20% of monitoring that catches 80% of real failures in a system like Djinn?
   - Concrete architecture: what to add to `djinn-alert` and what to add to individual services
   - What should be in a `djinn-health` script that runs every 30 minutes and reports system state?
   - Estimated build time for each piece

**Output format:** Structured report, one section per question. Be specific — name actual tools, patterns, systemd directives. Flag anything with high maintenance cost (we want durable, low-touch monitoring).

**Deliver to:** `djinn/research/marcus/TASK-059_bughunter-monitoring.md` — commit to vault. Claude reads on demand.

---

## TASK-060
- assigned_to: marcus
- status: done
- completed: 2026-06-01 by Marcus
- priority: critical
- trigger: manual
- created: 2026-06-01 by Claude (per Javier)
- context: Full-stack research — automated social media content studio pipeline for two brands (Typhon's Forge + Terp Tribe Clouds). Season/episode/weekly cadence. Apple ecosystem priority. Near-studio-staff automation level.

**Brief:**

Javier is building an automated social media content studio on top of the existing Djinn media pipeline. Two separate brands, two separate Telegram bots, one shared backend. The system takes raw footage (photos + video) from iCloud or Google Drive, processes it into platform-ready content, and outputs a `DONE/` folder per content day — fully labeled, transcribed, captioned, and tagged, ready to copy-paste or schedule.

**What Djinn already has (do not re-research, build on it):**
- `djinn-media-ingest` — intake, manifest creation
- `djinn-media-reel` — ffmpeg reel assembly, 30fps H.264
- `djinn-media-repurpose` — clip segmentation
- `djinn-media-kit` — stitch-kit folder + STITCH-ORDER.txt
- `djinn-media-publish-prep` — Ollama caption gen, hashtag selection (reads TREND-SIGNAL.md)
- `djinn-media-publish` — Meta Graph API publish (IG + FB)
- `djinn-trend-agent` — 6-hour trend polling (Firecrawl + Printables RSS → Ollama phi4:14b)
- `djinn-social-analyst` — daily Meta analytics pull
- `ffmpeg`, `faster-whisper`, Ollama (`phi4:14b`, `llama3.2-vision`), `rclone` (GDrive configured)
- Two social Telegram bots registered: `@djinn_bughunter_bot` (Typhon's Forge), `@djinn_terptribeclouds_bot` (Terp Tribe Clouds)

**Brand 1 — Terp Tribe Clouds**
Co-founder project. Currently in **Season 6**. Fixed weekly content schedule:
| Day | Content Theme |
|-----|---------------|
| Monday | Network Monday |
| Tuesday | Eve Life Tuesday |
| Wednesday | Wax Wednesday |
| Thursday | Terpy Disposables |
| Friday | Flower Friday |
| Saturday | Sesh Out Saturday |
| Sunday | Slow-Mo Sundays |

**Brand 2 — Typhon's Forge**
Javier's own shop. Weekly day names TBD — same pipeline, different brand identity. 3D printing, functional art, maker content.

**Target platforms for both brands:**
Instagram Reels + Feed, Facebook Reels + Feed, YouTube Shorts, X (Twitter) video.

**Output folder structure (per brand):**
```
Terp Tribe/
└── Monday/
    └── S6_E1_W1_Network-Monday/
        ├── videos/          ← raw clips
        ├── pics/            ← raw photos
        └── done/
            ├── reel.mp4             ← final assembled reel
            ├── cover.jpg            ← thumbnail
            ├── caption_ig.txt       ← IG caption + hashtags, copy-paste ready
            ├── caption_fb.txt       ← FB version (shorter, 2–3 hashtags)
            ├── caption_yt.txt       ← YouTube title + description + tags
            ├── caption_x.txt        ← X/Twitter version (280 chars)
            └── transcription.txt    ← full audio transcription
```

File naming convention: `S{season}_E{episode}_W{week}_{content-day-slug}`

**Research questions — go deep on each:**

1. **iCloud access from Linux in 2026**
   - What are the current options for syncing iCloud Photo Library or iCloud Drive to a Linux machine (Salomon, Ubuntu)?
   - `icloudpd` (iCloud Photos Downloader) — current state, auth method, reliability, Apple ID 2FA handling
   - Any alternatives: `pyicloud`, direct iCloud Drive API, Shortcuts automation on iPhone to push to GDrive first?
   - Apple's stance on third-party iCloud access in 2026 — has it gotten more or less open?
   - **Recommended path:** given Djinn already has rclone + GDrive, is the best flow iPhone → iCloud → GDrive (via iOS Shortcuts) → rclone pull? Or is direct iCloudpd more reliable?
   - Realistic failure modes and maintenance burden for each approach

2. **Apple ecosystem media formats — handling HEIC, HEVC, ProRes**
   - iPhone shoots HEIC photos and HEVC (H.265) or ProRes video. What does ffmpeg need to handle these on Linux?
   - `heif-gdk-pixbuf`, `libheif`, ffmpeg HEVC decoding — what packages are required?
   - ProRes RAW / ProRes 422 from iPhone 15 Pro — can ffmpeg transcode these without Apple hardware? What are the limitations?
   - Live Photos — `.HEIC` + `.MOV` pair — should we extract the still, the video, or both? Best practice for social media?
   - Optimal transcode settings: HEIC → JPEG (for thumbnails/IG feed), HEVC → H.264 (for all platforms), ProRes → H.264 (same pipeline)
   - Any quality/compression tradeoffs to be aware of for cannabis accessory + maker content (macro shots, smoke effects, detail shots)

3. **Platform format specs — current 2026 requirements**
   For each platform (Instagram Reels, IG Feed, Facebook Reels, FB Feed, YouTube Shorts, X video):
   - Optimal resolution and aspect ratio (9:16, 1:1, 16:9?)
   - Max file size and duration limits
   - Recommended codec and bitrate for best quality vs upload speed
   - Caption length limits and hashtag best practices per platform
   - Thumbnail requirements
   - Any 2025–2026 changes to specs that the existing djinn-media-reel pipeline needs to account for
   - Can one master export serve all platforms, or do we need per-platform encodes?

4. **YouTube Shorts + X publishing APIs**
   The existing pipeline only publishes to Meta (IG + FB). What's needed to add YouTube Shorts and X:
   - YouTube Data API v3 — uploading Shorts (9:16 under 60s), required scopes, OAuth flow for headless/server use, quota limits
   - X (Twitter) API v2 video upload — current status (has Elon's API pricing affected automated video posting?), free vs paid tiers, what you get at each tier
   - Best library for each: `google-api-python-client` for YouTube, `tweepy` or direct requests for X?
   - Any gotchas specific to cannabis-adjacent content on YouTube vs X (policy enforcement differences)
   - Realistic automation level: can both be fully headless, or does one require manual steps?

5. **Per-day content templates and seasonal naming automation**
   - How to build a content calendar engine that knows: today is Wednesday Season 6, therefore this is "Wax Wednesday" S6_E{N}_W{week_of_season}
   - Episode numbering across 7 days/week: does E1 = first piece of content ever, or first of the season, or first of the week?
   - Recommended episode/week counter storage (SQLite? JSON file per brand?)
   - How to generate the folder structure automatically on ingest — script creates `S6_E1_W1_Wax-Wednesday/` before any content lands
   - Content day templates: per-theme prompt injection for the caption agent. "Wax Wednesday" content should prompt differently than "Slow-Mo Sundays." How to store and inject these per brand, per day.
   - How the `done/` folder gets populated — what runs in sequence, what can run in parallel?

6. **Caption and description generation — per platform, per brand, per content theme**
   - The existing caption agent (Ollama phi4:14b, reads TREND-SIGNAL.md) generates one IG caption. Now we need 4 platform variants + brand voice differentiation.
   - What prompt engineering patterns work for generating platform-appropriate caption variants from one piece of content?
   - How to encode brand voice: Terp Tribe (cannabis community, lifestyle, stoner culture) vs Typhon's Forge (maker, precision craft, dark aesthetic). Both need cannabis-safe language.
   - Per-content-theme tone injection: "Slow-Mo Sundays" should read differently than "Wax Wednesday." How to structure this as a reusable config per brand?
   - X/Twitter 280-char constraint — best approach for auto-generating punchy short-form from a longer caption?
   - YouTube description structure: title (SEO), description (first 125 chars show before "more"), chapters if applicable, end-screen CTA, tags list

7. **Transcription pipeline for video content**
   - `faster-whisper` is already installed. What's the current recommended model size for short-form social content (under 60s) on Salomon hardware?
   - How to integrate transcription output into the done/ folder: `.srt` subtitles for burn-in, `.txt` for copy-paste, both?
   - Should the transcription feed into caption generation (give the model the transcript as context)?
   - Auto-subtitle burn-in with ffmpeg — current best practice for vertical (9:16) Reels-style content

8. **Multi-brand architecture — keeping Typhon and Terp Tribe completely separate**
   - Single backend (Djinn on Salomon), two brand configs, two Telegram bots, two folder trees, two sets of captions/hashtags/brand voices, two social platform credentials
   - How to structure brand config files so adding a third brand later is just adding a new config file
   - Credential isolation: each brand has its own Meta Page token, IG user ID, YT channel, X account. How to store and load per-brand without risk of cross-posting
   - Should each brand have its own media pipeline instance, or one pipeline with brand-aware routing?

9. **Scheduling and publishing automation**
   - Best practices for scheduling social posts for optimal reach in 2026 (time-of-day, day-of-week for cannabis/maker niches)
   - Does any platform still penalize third-party scheduled posts vs native posting?
   - Buffer, Later, Publer API tiers — if we want scheduled publishing without building it ourselves, what's the most cost-effective option for 2 brands, 4 platforms, 7 posts/week each?
   - Alternatively: can we build a lightweight cron-based scheduler in Djinn that posts at a configured time per brand per day without a third-party service?

10. **Storage and archival for season-based content**
    - A full season of content (7 content days/week × ~10 weeks) is potentially 70+ reel files + raw footage. What's the recommended storage architecture?
    - Salomon local SSD → Typhon cold archive (already set up at `/mnt/archive`) → GDrive as offsite backup. How should the done/ folders be tiered?
    - Naming and search: how to find "all Wax Wednesday content from Season 6" in a folder tree efficiently
    - Any metadata tagging approach (XMP sidecar files, SQLite index) that makes the archive queryable without a full media server

**Output format:** Structured report, one section per research question. For each: current state, specific tools/libraries to use, integration path with existing Djinn stack, warnings/gotchas, estimated build complexity. Flag anything that requires Javier's Apple ID credentials or platform account setup — those are blockers.

**Deliver to:** `djinn/research/marcus/TASK-060_social-studio-pipeline.md` — commit to vault. Claude reads and builds from it.



## TASK-061
- assigned_to: marcus
- status: done
- priority: high
- trigger: manual
- created: 2026-06-01 by Claude
- completed: 2026-06-01 by Marcus
- context: Complete TASK-037 — 6 missing law topics. Perplexity hit output limit on first run, domains 8-13 were cut off.

**Brief:**
Deliver the following 6 topics to `djinn/research/marcus/law/` as individual .md files. Use the same format as the existing 7 files in that directory (subject/tags/source frontmatter, Summary/Key Concepts/Details/Cases/Applied/Related sections, sign — Marcus).

1. **llc-formation.md** — Articles of organization (required fields, CA vs other states), operating agreements (member vs manager-managed), single-member vs multi-member, registered agent requirements, CA $800 franchise tax, EIN, annual report schedule
2. **business-entity-comparison.md** — Sole prop vs LLC vs S-corp vs C-corp: liability exposure, taxation (pass-through vs double), formation cost, admin burden, when each makes sense for a small shop/freelancer
3. **compliance-fundamentals.md** — What compliance means for a small business: business licenses, seller's permit, EIN, state/federal tax registration, CA FTB requirements, annual reports, record-keeping requirements, OSHA basics
4. **contract-drafting-basics.md** — Essential clauses for a service business: scope of work, payment terms, IP ownership, limitation of liability, dispute resolution (arbitration vs mediation), governing law, indemnification, force majeure — with plain-English explanation of each
5. **legal-research-methods.md** — How to use Westlaw, LexisNexis, Google Scholar, CourtListener, Fastcase; how to read a case (caption, parties, facts, issue, holding, reasoning, dicta); primary vs secondary sources; shepardizing/KeyCiting
6. **when-you-need-a-lawyer.md** — Situations where self-help is viable (small claims, simple contracts, LLC formation), situations where it isn't (litigation, complex IP, criminal), how to find and vet attorneys (State Bar referral, Avvo, flat-fee vs hourly), mediation vs arbitration vs litigation cost comparison

After all 6 files are written, append to COMMS.md:
> Marcus: TASK-061 complete — 6 missing law topics delivered, TASK-037 now fully covered.

**Output:** `djinn/research/marcus/law/` — 6 .md files

## TASK-062
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-06-01 by Claude
- context: Deploy Discord gateway overhaul after Claude completes build — restart djinn-discord-gateway service

**Commands:**
```bash
git -C ~/Obsidian pull
systemctl --user restart djinn-discord-gateway.service
systemctl --user status djinn-discord-gateway.service
```

**Verify:**
- Service is active
- Bot responds in Discord print channel
- Test: drop a file and confirm customer sees clean profile picker, not the technical report

**Report back:** COMMS.md — confirm service restarted and bot is live

---

## TASK-063
**title:** Social studio first-run setup
**assigned:** Javier (manual steps only — cannot be automated)
**trigger:** manual
**priority:** high
**status:** pending
**created:** 2026-06-01 by Claude

### Steps
1. Install cloudflared: `curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cloudflared.deb && sudo dpkg -i /tmp/cloudflared.deb`
2. `cloudflared tunnel login` (browser required once)
3. `cloudflared tunnel create djinn-media`
4. `cloudflared tunnel route dns djinn-media media.<yourdomain>.com`
5. Update `~/.config/djinn/hosting.env` — set `DJINN_MEDIA_BASE_URL=https://media.<yourdomain>.com`
6. Enable tunnel service: `systemctl --user enable --now djinn-cf-tunnel.service`
7. Fill `~/.config/djinn/meta-terp-tribe.env` with IG/FB/YT/X credentials (see `configs/meta.env.example`)
8. `chmod 600 ~/.config/djinn/meta-terp-tribe.env`
9. Confirm Typhon's Forge weekly day names → Claude updates `typhon-forge.json`
10. Confirm Terp Tribe Season 6 actual start date → Claude updates `terp-tribe.json`
11. First dry run: `djinn-media-ingest --brand terp-tribe --setup`
12. YouTube one-time OAuth: `cd ~/projects/djinn-social && .venv/bin/python scripts/youtube_oauth_setup.py --brand terp-tribe --client-secrets ~/google-client-secrets.json`

### Notes
Meta App Review: apply at developers.facebook.com → Business → Instagram → content_publish permissions. Start now — takes 2–4 weeks. Dev mode works for Javier's own accounts without review.

---

## TASK-064
- assigned_to: salomon
- status: done
- completed: 2026-06-02 by Claude (superseded)
- priority: high
- trigger: manual
- created: 2026-06-02 by Claude
- context: Proxy Stand v22 — PRINT THIS. Final engraving: TYPHONS FORGE, ALL CAPS, 8mm Liberation Bold, 1.4mm depth, bore expanded to 42.4mm for 42mm glass cylinder fit.

**File:** `/home/drmanzo/printer-files/queue/Proxy_Stand_job5_v22_pla.stl`
**Material:** PLA
**Slicer settings:** 0.15mm layers (NOT 0.2mm — reduces sidewall roughness, improves engraving legibility), standard PLA temps, no supports needed

**Geometry verified:**
- Outer diameter: 62mm (engraving on outer wall intact)
- Inner bore: 42.39mm diameter (designed 42.4mm — prints ~42.1mm, snug fit for 42mm glass)
- Watertight, 1 component

**After slicing:** Post gcode to Calliope queue and confirm in COMMS.md.

— Claude

---
## PRINT JOB — 2026-06-02 — Proxy Stand Pair
**To:** Salomon  
**Priority:** Normal

Slice and print both in a single plate job on Calliope (Ender-3 V3 Plus).

**Files (both marked, watertight, single component):**
- `/home/drmanzo/printer-files/queue/Proxy_Stand_typhons_forge_final.stl` — engraved "Typhons Forge", opening expanded +0.3mm
- `/home/drmanzo/printer-files/queue/Proxy_Stand_terp_tribe_hq_final.stl` — embossed "Terp Tribe HQ"

**Slice settings:**
- Layer: 0.20mm
- Walls: 3
- Infill: 15%
- Supports: tree (auto), text faces are on the side wall — supports needed for upper overhangs only
- **Brim: NO**
- Nozzle: 215°C / Bed: 60°C

**Plating:** place side by side on the 300×300 bed, text faces forward, flat bases down. Both models are 62mm wide so they fit with room to spare.

**Maker's mark:** ✅ stamped on bottom of both (15mm, 0.5mm deep)

— Claude
---

## TASK-065
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-06-02 by Claude
- context: Wire automated print failure triage into djinn-print-monitor — cube-first diagnostic protocol

**Goal:** When a print failure is detected, Djinn automatically runs the triage protocol instead of waiting for Javier to diagnose manually.

**File:** `/home/drmanzo/.local/bin/djinn-print-monitor-v2` (modify existing failure handler)

**Current behavior:** On failure detection, logs to FAILURE-LOG.md and sends Telegram alert.

**New behavior — add after failure is logged:**

### 1. Check if tracer data exists for the failed job
```python
TRACE_DIR = Path.home() / "Obsidian/djinn/printer/active"
traces = list(TRACE_DIR.glob("TRACE-*.md"))
latest_trace = max(traces, key=lambda p: p.stat().st_mtime) if traces else None
```

### 2. Analyze tracer data if available
```python
# Read trace, find rows with 100% retransmit
# Check if the spike was instant (0→100% in one interval) or gradual (climbing over many rows)
# INSTANT: two consecutive rows where retx% jumps from <5% to >90%
# GRADUAL: retx% climbs across 5+ rows

if instant_spike:
    # Grep M106 in the failed gcode at the failure Z height
    failed_gcode = Path.home() / f"printer-files/queue/{failed_filename}"
    # if file exists locally, grep for M106 near failure layer
    # Send Telegram: "⚡ EMI spike detected at Z={z}. Check M106 in gcode near that layer. Suggest: cap M106 S255→S128"
    msg = f"⚡ Instant nozzle_mcu spike at Z={failure_z} X={failure_x} Y={failure_y}\nLikely cause: M106 fan command\nRun: grep M106 {failed_filename}\nFix: cap S255→S128"
elif gradual_climb:
    msg = f"📈 Gradual nozzle_mcu degradation — possible hardware\nQueuing calibration cube..."
    # Queue the cube (step 3)
else:
    msg = "⚠️ Print failed — no tracer data. Start djinn-print-tracer before next attempt."
```

### 3. Auto-queue calibration cube on gradual failure (or no tracer data)
```python
CUBE_FILE = "CRtestcube_Ender-3 V3 Plus_26m.gcode"
# POST to Moonraker job queue
requests.post(f"{MOONRAKER}/server/job_queue/job", json={"filename": CUBE_FILE})
# Send Telegram: "🧊 Calibration cube queued as next job — hardware baseline test. If it passes, problem is in the failed gcode."
```

### 4. Telegram alert format on failure
```
🔴 Print failed: {filename}
Duration: {duration}s ({duration/60:.1f}min)
State: {state}

🔬 Tracer analysis: {instant_spike | gradual_climb | no_data}
{diagnostic_message}

Next: {cube_queued | check_gcode_M106 | start_tracer}
```

**Config needed:**
```python
CUBE_GCODE = "CRtestcube_Ender-3 V3 Plus_26m.gcode"  # hardcode, always on printer
MOONRAKER = "http://192.168.1.113:7125"
TRACE_DIR = Path.home() / "Obsidian/djinn/printer/active"
```

**Dependencies:** `requests` (already installed), `pathlib` (stdlib)

**Success criteria:**
```bash
# Simulate a failure: temporarily rename state file to force failure detection
# Confirm Telegram message arrives with correct triage analysis
# Confirm cube is queued in Moonraker job queue on gradual/no-data path
python3 -m py_compile ~/.local/bin/djinn-print-monitor-v2 && echo OK
systemctl --user status djinn-print-monitor.timer
```

**Report back:** COMMS.md — paste sample Telegram message output and confirm cube queues correctly on test failure.

---

### JOB-8 — Camood TTHQ × 4 PLA — UPLOAD + PRINT [print_approved=true]

**For:** Salomon
**Priority:** normal
**Status:** gcode ready, Calliope unreachable from Claude machine

**Action needed:**
1. Upload gcode to Calliope Moonraker: `http://192.168.1.114:7125`
   - File: `/home/drmanzo/.local/share/forge/gcode/Camood_TTHQ_engraved_job8.gcode`
   - If path not shared: scp from Salomon or re-slice with `djinn slice 8`
2. Start print — **Javier has given explicit approval**

**Job details:**
- STL: `~/printer-files/library/engraved/terp-tribe/Camood_TTHQ_engraved.stl`
- Qty: 4 (2×2 on one plate)
- Material: PLA · 215°C nozzle · 60°C bed
- Layer: 0.2mm · 3 walls · 15% infill
- Supports: **buildplate-only** — tank underside junction ONLY, top edge NO support, round body NO support
- Brim: none
- Print time: 29h 59m · 497.6g PLA

*— Claude, 2026-06-04*

---

## 2026-06-04 — OpenClaw bootstrap fix (Claude → verified, no handoff needed)

No tasks queued for Salomon or Typhon from this session. The fix was config-only on Salomon (openclaw.json). Gateway already restarted.

Test action for Javier: `openclaw tui` → ask "who am I?" — should get a Djinn response that knows Javier.

*— Claude, 2026-06-04*

---

## 2026-06-05 — Print Queue Reset

**Closed by Claude — per Javier request 2026-06-05**

The following print items are now closed. No prints are pending, queued, or on hold.

| Item | Status | Reason |
|------|--------|--------|
| JOB-8 — Camood TTHQ × 4 | **cancelled** | Superseded by Job 9 → Job 10. All Camood jobs concluded. |
| PRINT JOB — 2026-06-02 — Proxy Stand Pair | **cancelled** | Superseded by Job 6 (ProxyStand_TTHQ). Closed. |
| TASK-065 — djinn-print-monitor triage | **superseded** | Replaced by `djinn-print-safety` daemon (built 2026-06-05). Triage logic lives there now. |
| TASK-063 — Social studio first-run setup | **pending — non-print** | Retained. No print dependency. Javier's own setup steps. |

**Printer state as of 2026-06-05:**
- Moonraker queue: empty, idle
- Print history: cleared (71 entries)
- Active traces: archived to `djinn/printer/traces-archive/`
- No prints approved, running, or waiting

*— Claude, 2026-06-05*

---

## TASK-067
- assigned_to: salomon
- status: done
- priority: high
- trigger: auto
- created: 2026-06-05 by Claude
- spec_source: djinn/research/marcus/TASK-066_claude-dependency-migration.md#SPEC-1

**Goal:** Upgrade `djinn-session-end` to build a real commit message from git state + COMMS context — zero LLM, eliminates the need to keep Claude open just to close a session.

**File:** `~/.local/bin/djinn-session-end` (extend existing)

**Interface:**
```
djinn-session-end <topic>              # stage all, build message, push
djinn-session-end <topic> --no-push   # build message, commit, don't push
djinn-session-end --push-only         # push what's already staged
```

**Key logic:**
- Stage: `git add -A` (skip if `--push-only`)
- Diff summary: `git diff --cached --stat` — top 10 files, used in commit body
- COMMS scrape: read last 5 entries from COMMS.md (lines since last `---` separator), extract the subject line from each `### ...` header
- Commit message template (deterministic, no LLM):
  ```
  <topic>: <first changed file or "multiple files"> — <file count> file(s)

  Changed:
  <git diff --stat top 10>

  Session context:
  <last 3 COMMS entry subjects, one per line>

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  ```
- COMMS append: one Tier 1 entry with commit SHA, timestamp, topic
- Gateway: check `djinn-gateway status`; if Standard mode, `--push-only` and pushes will hit the pre-push hook (correct behavior — don't bypass)

**Success criteria:**
- `djinn-session-end test-topic` produces a commit with a human-readable message containing actual file list
- COMMS entry is written with correct SHA
- `djinn-session-end --push-only` works without re-staging
- Zero LLM calls (no ollama, no API)
- Test: run after making a test file change, verify commit message and COMMS entry

**Report back:** COMMS entry with: diff of old vs new script, test output showing commit message, confirmation zero LLM calls.

---

## TASK-068
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-06-05 by Claude
- depends_on: TASK-067 (stable first)
- spec_source: djinn/research/marcus/TASK-066_claude-dependency-migration.md#SPEC-2

**Goal:** New tool `djinn-local-report` — sends structured context to phi4:14b and gets back a properly formatted 6-section session report. Session reports no longer require Claude.

**File:** `~/.local/bin/djinn-local-report` (new)

**Interface:**
```
djinn-local-report --topic "gateway-phase1"
djinn-local-report --topic "gateway-phase1" --since "2026-06-05T18:00:00"
djinn-local-report --topic "gateway-phase1" --no-commit   # write file, don't commit
djinn-local-report --topic "gateway-phase1" --upgrade     # use Claude API instead of phi4
```

**Key logic:**
1. Context assembly (no LLM):
   - `git log --oneline --since=<session-start>` — commits this session
   - `git diff --stat HEAD~N HEAD` — files changed
   - Last 5 COMMS entries since `--since` timestamp
   - QUEUE tasks matching today's date with status `done` or `in-progress`
2. Ollama call to phi4:14b (`http://localhost:11434/api/generate`):
   - System: "You are a technical writer for Djinn AI OS. Write a session report in the exact format below. Be factual. Do not invent details not in the context."
   - Required sections: Summary, Work Completed, Files Changed, Decisions Made, Open Issues, Next Steps
   - Temperature: 0.3 (factual, not creative)
3. Validation: check all 6 section headers are present using regex; if any missing, re-prompt with missing section list (max 1 retry)
4. Fallback: if phi4 unavailable, retry with qwen2.5:7b
5. Save: `~/Obsidian/djinn/logs/reports/YYYY-MM-DD_<topic>.md`
6. COMMS entry: Tier 1, notes report was auto-generated by phi4:14b

**Success criteria:**
- Report has all 6 sections
- Summary matches actual git log (no hallucinated file names)
- Completes in < 90 seconds on phi4:14b
- Works without Claude open
- `--upgrade` flag falls back gracefully if API key not set

**Report back:** COMMS entry with: sample report output (first 20 lines), wall-clock time, which model was used.

---

## TASK-069
- assigned_to: salomon
- status: done
- priority: normal
- trigger: manual
- created: 2026-06-05 by Claude
- depends_on: TASK-067 (session-end v2 must be stable)
- spec_source: djinn/research/marcus/TASK-066_claude-dependency-migration.md#SPEC-3

**Goal:** New tool `djinn-comms-auto` — routes COMMS entry generation to the right local model by event type. Fills the dead time between Claude sessions.

**File:** `~/.local/bin/djinn-comms-auto` (new)

**Interface:**
```
djinn-comms-auto --event task-complete --task TASK-067
djinn-comms-auto --event build --file djinn-session-end --summary "v2: auto commit msg"
djinn-comms-auto --event bug --exit-code 1 --script djinn-bore-core --context "..."
djinn-comms-auto --session-end --topic "gateway-phase1"
```

**Key logic — model routing by event type:**
| Event | Model | Notes |
|-------|-------|-------|
| `task-complete` | qwen2.5:7b | Mechanical, structured |
| `build` | phi4:14b | Needs context about what changed |
| `bug` | deepseek-r1:7b | Reasoning model for root cause |
| `session-end` | phi4:14b | Substantive summary |

- Each event type has a fixed prompt template (see SPEC-3 in Marcus's doc)
- COMMS write guard: use file lock (`fcntl.flock`) to prevent concurrent writes
- Idempotent: generate a hash from (event type + timestamp + script name); skip if that hash already appears in today's COMMS entries
- Validate output: regex check against COMMS entry schema (`### YYYY-MM-DD...` header present)
- If validation fails: log to stderr, write raw context as fallback entry marked `[AUTO-UNVALIDATED]`

**Success criteria:**
- All 4 event types produce correctly formatted COMMS entries
- No duplicate entries on repeated calls with same event
- Works without Claude open
- File lock prevents race conditions when Salomon and Typhon both write simultaneously

**Report back:** COMMS entry with test output for all 4 event types, confirmation of idempotency check.

---

## TASK-070
- assigned_to: marcus
- status: done
- completed: 2026-06-08 by Claude (audit — fixes 2/3/4 already applied; fix 1 noted in COMMS for Salomon)
- fix1_applied: 2026-06-10 by Claude — djinn-route Typhon .113→.150 AND Orion .176→.177 both corrected
- priority: high
- trigger: manual
- created: 2026-06-06 by Claude
- context: Four bug fixes across automation/ scripts and djinn-route — caught during post-merge code review

**Fixes required:**

### Fix 1 — djinn-route: wrong Typhon IP (critical)
**File:** `~/.local/bin/djinn-route` on Salomon (NOT in vault — local file only)
**Line 31:** `TYPHON_URL="http://192.168.1.113:11434"` → `"http://192.168.1.150:11434"`

`.113` is Calliope (Klipper/Moonraker). Typhon is `.150` (confirmed in `~/.ssh/config`). Any script using `djinn-route lightweight` currently hits Calliope's port 11434 which doesn't run Ollama. Since djinn-route is not vault-tracked, note this fix in your COMMS entry so Salomon applies it locally — or propose adding djinn-route to the vault so it's version-controlled.

### Fix 2 — djinn-system-health: wrong VAULT_PATH default
**File:** `automation/djinn-system-health`
**Line 27:** `VAULT_PATH="${VAULT_PATH:-$HOME/djinn-vault}"` → `"${VAULT_PATH:-$HOME/Obsidian}"`

The vault lives at `~/Obsidian`, not `~/djinn-vault`. If run without VAULT_PATH set, the disk check silently looks at a path that doesn't exist.

### Fix 3 — djinn-backup-verifier: same VAULT_PATH default bug
**File:** `automation/djinn-backup-verifier`
**Line 38:** `VAULT_PATH="${VAULT_PATH:-$HOME/djinn-vault}"` → `"${VAULT_PATH:-$HOME/Obsidian}"`

Same root cause as Fix 2.

### Fix 4 — djinn-vault-integrity: frontmatter warnings should not raise exit 1
**File:** `automation/djinn-vault-integrity`
**Current behavior:** `has_issues = bool(broken or fm_warnings)` — exits 1 on frontmatter warnings alone.
**Correct behavior:** Only exit 1 on broken links. Frontmatter warnings stay in the report but don't change the exit code (they're noise-level, not actionable failures).

Change:
```python
# Before:
has_issues = bool(broken or fm_warnings)

# After:
has_issues = bool(broken)
```

The status line in the report and log can still show "ISSUES FOUND" if there are frontmatter warnings — just don't let that alone trigger exit 1 (and by extension, Telegram alerts).

---

**Deliver:** Push fixes 2, 3, 4 to vault via commit. For fix 1 (djinn-route), write a COMMS entry addressed to @Salomon with the exact sed command or note so Salomon applies it locally.

**Report back:** COMMS entry confirming all four fixes committed/noted.

---

## TASK-071
- assigned_to: salomon
- status: done
- priority: normal
- trigger: manual
- created: 2026-06-10 by Claude
- context: Install Hellhound v1 runtime on Salomon from DrManzo/djinn-vault main (commit e35832a)

**Commands:**
```bash
# 1. Pull latest vault (Hellhound files are now in djinn-vault main)
cd ~/Obsidian && git pull

# 2. Copy runtime files to install location
mkdir -p ~/.local/share/hellhound/
cp ~/Obsidian/hellhound/hellhound.py \
   ~/Obsidian/hellhound/pup.py \
   ~/Obsidian/hellhound/pup-template.py \
   ~/Obsidian/hellhound/pup-gateway.py \
   ~/.local/share/hellhound/

# 3. Install CLI
cp ~/Obsidian/hellhound/bin/hellhound ~/.local/bin/ && chmod +x ~/.local/bin/hellhound

# 4. Install systemd units
cp ~/Obsidian/hellhound/skull/*.service \
   ~/Obsidian/hellhound/skull/*.socket \
   ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now hellhound.socket hellhound.service

# 5. Provision gateway pup and start it
hellhound pup new gateway
systemctl --user start pup@gateway

# 6. Verify StubGateway is producing observations (10s interval)
hellhound log --tail 20
```

**Success criteria:** `hellhound status` shows hellhound running + gateway pup connected; `hellhound log --tail 20` shows synthetic observations from StubGateway every ~10s; SQLite and vault timeline receiving entries.

**Report back:** COMMS entry confirming install complete or any errors hit.

---

## ~~TASK — Camood Diagnostic Review~~

**Status:** CLOSED — 2026-06-07 — dropped by Javier. Project done.


## TASK-072
- assigned_to: typhon
- status: done
- priority: normal
- trigger: auto
- created: 2026-06-15 by Claude
- context: Install Orca Slicer v2.3.2 on Typhon — distributed slicing node

**Commands:**
```bash
wget -q https://github.com/SoftFever/OrcaSlicer/releases/download/v2.3.2/OrcaSlicer_Linux_V2.3.2.AppImage -O /tmp/OrcaSlicer.AppImage
chmod +x /tmp/OrcaSlicer.AppImage
sudo mkdir -p /opt/orca-slicer
cd /tmp && /tmp/OrcaSlicer.AppImage --appimage-extract
sudo cp -r squashfs-root/* /opt/orca-slicer/
rm -rf /tmp/squashfs-root /tmp/OrcaSlicer.AppImage
sudo ln -sf /opt/orca-slicer/AppRun /usr/local/bin/orca-slicer
orca-slicer --help | head -3
```

## TASK-073
- assigned_to: orin
- status: done
- priority: normal
- trigger: auto
- created: 2026-06-15 by Claude
- context: Install Orca Slicer v2.3.2 on Orion — distributed slicing node (iMac, Intel 8-core)

**Commands:**
```bash
wget -q https://github.com/SoftFever/OrcaSlicer/releases/download/v2.3.2/OrcaSlicer_Linux_V2.3.2.AppImage -O /tmp/OrcaSlicer.AppImage
chmod +x /tmp/OrcaSlicer.AppImage
sudo mkdir -p /opt/orca-slicer
cd /tmp && /tmp/OrcaSlicer.AppImage --appimage-extract
sudo cp -r squashfs-root/* /opt/orca-slicer/
rm -rf /tmp/squashfs-root /tmp/OrcaSlicer.AppImage
sudo ln -sf /opt/orca-slicer/AppRun /usr/local/bin/orca-slicer
orca-slicer --help | head -3
```

## TASK-074
- assigned_to: claude
- status: future
- priority: low
- trigger: manual
- created: 2026-06-15 by Claude
- context: Wire hellhound observations into existing gateways for real traffic monitoring

**Scope:**
1. Add `hh_observe()` calls into djinn-discord-gateway (order received, command routed, customer message)
2. Add `hh_observe()` calls into djinn-telegram-gateway (confirm/deny, operator commands)
3. Add `hh_observe()` calls into djinn-webcam-monitor (print start, milestone, failure, complete)
4. Build report generator: hellhound reads SQLite timeline → assembles daily/on-demand summary → sends to Telegram
5. Replace StubGateway in pup-gateway.py with real observer (fed by gateways, not replacing them)

**Not doing yet:** gateway pup does not replace djinn-discord-gateway — observe-only pattern.

## TASK-075
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-06-15 by Claude
- completed: 2026-06-15 by Claude (built directly after 3 failed Salomon attempts — see COMMS)
- spec_source: djinn/research/marcus/TASK-PA-REDESIGN_personal-layer.md#SPEC-PA-01

**Goal:** Surface the single most time-sensitive academic item in the morning briefing. GCU's 8-week courses run a predictable weekly rhythm (DQ1 due Wed, DQ2 due Fri, all assignments due Sun 11:59PM AZT) — currently invisible to Djinn.

**File:** `~/.local/bin/djinn-personal-db` (extend schema + commands), `~/.local/bin/djinn-morning` (briefing line)

**Interface:**
```
djinn-personal-db academic add <course> <task_type> <due_date> [due_time] [--recurring weekly --day wed]
djinn-personal-db academic check          — JSON list of open items, soonest first
djinn-personal-db academic done <id>
```
Telegram: `/school` — full weekly view across all active courses (not just the urgent one)

**Key logic:**
- New table: `academic_deadlines(id, course, task_type, due_date, due_time, due_tz, completed, recurring, recur_day_of_week)`
- Recurring weekly deadlines (DQ1/DQ2/Sunday-due) seeded per active course — Javier provides course list + recurrence pattern once per 8-week term, not per assignment
- Priority algorithm: CRITICAL if due ≤ 1 day, ELEVATED if due ≤ 3 days, else background (on-demand only via `/school`)
- Morning brief shows only the single most urgent item: `📚 [Course] — [Task] due [day].`
- This REPLACES the existing generic `deadlines` table usage in `djinn-morning`'s "one thing" logic — academic items now take priority in that slot when CRITICAL

**Success criteria:**
- `djinn-personal-db academic add "FIN-202" "DQ1" 2026-06-17 --recurring weekly --day wednesday` registers correctly
- Morning brief shows the academic item when one is CRITICAL/ELEVATED and nothing else outranks it
- `/school` in Telegram returns full weekly view
- Zero missed deadlines test: seed a full week of fake GCU deadlines, verify briefing surfaces the right one each day

**Report back:** Schema diff, test output of the seeded-week scenario, confirmation `/school` works end to end in Telegram.

**Done — actual implementation notes:** Built directly into the three live files (`djinn-personal-db`, `djinn-personal-gateway`, `djinn-morning`), not as a separate vault module. Interface differs from the original spec: `academic add <course> <label> <date> [type]` (label before date, no `--recurring` flag) and a separate `academic seed-gcu <course> <monday> <start> <end>` command that inserts DQ1/DQ2/Assignments for one week at a time, instead of a generic recurrence engine. `/school` shows 7-day view with tier tags. Briefing JSON now includes `academic_item` (single highest-priority CRITICAL/ELEVATED line); `djinn-morning`'s `compose()` puts it first in the "one thing" slot, ahead of the legacy `deadlines` table. Tested live against `~/.local/share/djinn/personal.db` — schema migrated cleanly, no data loss, `briefing` JSON still parses. Vault mirror at `djinn/personal/academic/status.md` synced via `djinn-personal-db sync`.

## TASK-076
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-06-15 by Claude
- completed: 2026-06-15 by Claude
- spec_source: djinn/research/marcus/TASK-PA-REDESIGN_personal-layer.md#SPEC-PA-06

**Goal:** Fix the Black Book cold-start problem. Zero entries exist because the 5-entry/day goal and the `/reflect`-only flow create too high an activation bar. Replace with a zero-friction capture command.

**File:** `~/.local/bin/djinn-personal-gateway` (new route), `~/.local/bin/djinn-personal-db` (extend blackbook commands)

**Interface:**
```
djinn-personal-db blackbook log [--source manual|reflect]
djinn-personal-db blackbook count          — total entries logged
```
Telegram: `/log [text]` — if text present, immediate capture, no prompt, no Ollama call. If no text, bot replies "What's on your mind?" and captures the next message as the entry.

**Key logic:**
- Entry text is appended to `~/Obsidian/personal/black-book/{today}.md` (create if missing) — this file already gitignored, confirm it stays that way
- `black_book_log` table gets an `entry_source` column ('manual' | 'reflect')
- `/reflect` stays exactly as built, but only activates once 3+ entries exist total — below that, `/reflect` replies "Write a couple entries first — `/log` works for that."
- At exactly 3 entries logged (lifetime), send one-time message: "📓 You have 3 entries. /reflect is live."
- Drop the 5-entry daily goal entirely — it does not appear anywhere, not in briefing, not in `/check`. Replace with: 1 entry/day is "done", 3+ is shown as a bonus note, never as a requirement.

**Success criteria:**
- `/log "rough day"` writes to today's Black Book file and confirms with entry count, no Ollama call in the path
- At 3rd lifetime entry, the unlock message fires once
- `/reflect` before 3 entries gives the redirect message instead of erroring
- AI never reads Black Book content except inside `/reflect`'s existing local-Ollama-only flow — confirm no regression there

**Report back:** Confirm gitignore still covers `personal/`, confirm `/reflect` gate works, paste a sample `/log` exchange.

**Done — actual implementation notes:** Live `black_book_log` table (one row per day, used by `/reflect`'s existing logging) was left as-is; added a separate `black_book_entries(id, entry_date, logged_at)` table for the lifetime entry count instead of adding an `entry_source` column to `black_book_log` — simpler, no migration of existing rows needed. Entry text is written only to `~/Obsidian/personal/black-book/{date}.md` (append-only), never stored in SQLite — kept the original Phase Alpha principle that raw journal text lives in the vault file, not the DB. `/log` with no args sets a pending-state flag per chat_id and captures the next plain-text message (mirrors the existing `_craig_draft` pattern). `/reflect` gates at 3 lifetime entries, redirects below that. Tested live: `/log`, `/log <text>`, and the 3-entry gate message all confirmed via direct dispatch test, then cleaned from the DB/vault.

## TASK-077
- assigned_to: salomon
- status: done
- priority: normal
- trigger: manual
- created: 2026-06-15 by Claude
- completed: 2026-06-15 by Claude
- spec_source: djinn/research/marcus/TASK-PA-REDESIGN_personal-layer.md#SPEC-PA-07

**Goal:** Stop the morning brief from generating false-guilt pressure on colitis flare days. One toggle suppresses the action item and pauses streaks for the day.

**File:** `~/.local/bin/djinn-personal-db` (new table + commands), `~/.local/bin/djinn-morning` (flare check before composing)

**Interface:**
```
djinn-personal-db flare on
djinn-personal-db flare clear
djinn-personal-db flare status        — prints "active" or "clear"
```
Telegram: `/flare` (toggle on), `/flare clear` (manual clear)

**Key logic:**
- New table: `health_flags(flag_date, flag_type, auto_cleared)` — `flag_type` always 'colitis' for now, structured for future flag types
- Auto-clears at midnight local time (check `flag_date != today` on read, treat as inactive)
- `djinn-morning`: if flare active today, skip normal `compose()` entirely, send instead: "Day [N] sober.\nRest day — system in quiet mode." plus the softest possible action item only if a CRITICAL academic deadline exists (depends on TASK-075 landing first — if not yet built, omit that line entirely)
- Streak `_recalc_streak` logic: a flare day should not break any streak — treat flare days as "skip, no penalty" for habit streak calculation (don't require completion, don't reset streak to 0 either)

**Success criteria:**
- `/flare` then triggering `djinn-morning --force` produces the quiet-mode message, not the normal briefing
- A flare day with no habit completions does not reset the writing/exercise streak the next day
- `/flare clear` or midnight rollover restores normal briefing behavior

**Report back:** Confirm streak-pause behavior with a test sequence (log streak, flare a day, skip habits, confirm streak intact next day).

**Done — actual implementation notes:** `health_flags` table, `flare on/clear/status` commands, `/flare`/`/flare clear` Telegram routes, and `djinn-morning`'s flare quiet-mode branch (`compose_flare()`, no habit keyboard) all built and tested live. Streak-pause implemented by changing `_recalc_streak()`'s date-walk to skip any date present in `health_flags` (flag_type='flare') without breaking the streak. Tested live with a real sequence: completion 2 days ago → flare flagged yesterday → completed today → streak correctly came out to 2 (flare day bridged, not counted, not broken). Test data cleaned from the live DB after verification.

## TASK-078
- assigned_to: salomon
- status: done
- priority: normal
- trigger: manual
- created: 2026-06-15 by Claude
- completed: 2026-06-15 by Claude
- spec_source: djinn/research/marcus/TASK-PA-REDESIGN_personal-layer.md#SPEC-PA-03,04,05

**Goal:** Recovery cluster — step work tracking, craving log, and meeting attendance logging. Bundled together since all three are local-only, Ollama-only, and share the same "no surveillance, no encouragement text" design constraint.

**File:** `~/.local/bin/djinn-personal-db` (3 new tables + commands), `~/.local/bin/djinn-personal-gateway` (3 new routes)

**Interface:**
```
djinn-personal-db step status
djinn-personal-db step done
djinn-personal-db sponsor-contact [note]
djinn-personal-db craving <1-10> [tag]
djinn-personal-db craving week              — Ollama-generated pattern note, local only
djinn-personal-db meeting attended [name]
djinn-personal-db meeting missed
djinn-personal-db meetings week
```
Telegram: `/step`, `/step done`, `/sponsor-contact [note]`, `/craving [1-10] [tag]`, `/craving week`, `/meeting attended`, `/meeting missed`, `/meetings week`

**Key logic:**
- `step_work(id, step_number, status, started_date, completed_date, notes)` — `/step` prints "Step [N]: [status]. Started [X] days ago." No encouragement text, no commentary.
- `sponsor_contacts(id, contact_date, brief_note)` — just a timestamp + optional note, no scheduling logic, no "you haven't contacted Craig" nagging
- `craving_log(id, logged_at, severity, tag, sobriety_day)` — `/craving 7 work-stress` replies only "Logged. Day [N] sober." `/craving week` pulls the week's entries, sends to local Ollama (qwen2.5:7b) with prompt "Identify one pattern in this data, state it as fact, no advice" — output only, no cloud LLM
- `meeting_attendance(id, meeting_date, meeting_type, meeting_name, attended, notes)` — ties into existing AA schedule from `aa-meetings.json` for `meeting_name` lookup where possible
- Morning brief: add at most one quiet line if 5+ days since last logged meeting attendance — "5 days since last meeting logged." No nagging tone, no streak language.

**Success criteria:**
- All four commands log correctly and round-trip through `briefing` JSON where relevant
- `/craving week` produces a single Ollama-generated line, confirmed no cloud API call in the code path
- 5-day-since-meeting line appears in briefing only when threshold crossed, never otherwise

**Report back:** Sample output of all new commands, confirm Ollama-only path for craving pattern note (grep for any non-local LLM call).

**Done — actual implementation notes:** All commands built directly into `djinn-personal-db` (`step status/start/done`, `sponsor`, `craving`/`craving week`, `meeting`/`meeting missed`/`meeting week`/`meeting nudge`) and corresponding `/step`, `/sponsor-contact`, `/craving`, `/meeting attended|missed|week` Telegram routes. Note: bare `/meeting` was already taken by the existing AA-schedule lookup (handle_meeting) — disambiguated by matching `/meeting (attended|missed|week)` as a separate, more specific route checked before the bare `/meeting$` pattern, so both features coexist without collision. `craving log` fixed the sobriety-table bug found in the prior Salomon attempts (queried nonexistent `sobriety_log`; now reads the live `sobriety` table directly). `craving week` confirmed Ollama-only — single `subprocess.run(["ollama","run","qwen2.5:7b",...])` call, no cloud client. `meeting_nudge` wired into `briefing` JSON and into `djinn-morning`'s priority chain. Tested live via direct dispatch calls; test rows cleaned from DB after verification.

## TASK-079
- assigned_to: salomon
- status: done
- priority: low
- trigger: manual
- created: 2026-06-15 by Claude
- completed: 2026-06-15 by Claude
- spec_source: djinn/research/marcus/TASK-PA-REDESIGN_personal-layer.md#SPEC-PA-08,09

**Goal:** Minimum-viable tracking for Aethoria writing sessions and gym sessions — lowest complexity of the Phase Beta set, single-tap logging only.

**File:** `~/.local/bin/djinn-personal-db` (2 new tables + commands), `~/.local/bin/djinn-personal-gateway` (new routes)

**Interface:**
```
djinn-personal-db write <minutes> [scene_note]
djinn-personal-db aethoria status            — streak + weekly session count
djinn-personal-db aethoria-goal <text>
djinn-personal-db gym                        — logs today, prints monthly count
```
Telegram: `/write [minutes] [scene note]`, `/aethoria`, `/aethoria-goal [text]`, `/gym`

**Key logic:**
- `writing_sessions(id, session_date, duration_minutes, scene_note, word_count)` — word_count optional, leave null if not provided
- `gym_sessions(id, session_date)` — that's it, no sets/reps/weight tracking, just presence
- Morning brief Aethoria line: show only if no writing session logged today AND no CRITICAL academic deadline active (depends on TASK-075's CRITICAL flag — if not built yet, just check "no session today")
- After 3+ consecutive missed writing days: "Aethoria dark — 3 days. Just open the doc." — stated as fact, no guilt framing
- Gym: briefing never mentions it unless the month ends at 0/3 sessions — that line only fires once, at month-end check

**Success criteria:**
- `/write 30 "Faust chapter 4"` logs correctly, streak visible via `/aethoria`
- `/gym` logs and shows correct monthly count, capped reporting (no daily nagging)
- 3-consecutive-miss dark-streak line fires correctly in a test sequence

**Report back:** Sample `/write`, `/aethoria`, `/gym` output. Confirm briefing suppression logic works (log a session, verify Aethoria line disappears that day).

**Done — actual implementation notes:** `write`, `aethoria status/goal`, `gym` commands and matching `/write`, `/aethoria [goal ...]`, `/gym` Telegram routes built directly into the live files. `aethoria_line` in briefing JSON fires at 3+ days since last writing session with the spec's exact "Aethoria dark — N days. Just open the doc." wording, and is suppressed automatically once a session is logged today (days_since resets to 0). Added `gym_month_end_line`: fires only on the 1st of the month, checking the prior month's session count, true to the "fires once, at month-end" requirement — verified via `briefing` JSON output (field present, null outside the trigger window). Priority order in `djinn-morning` is academic > legacy deadlines > meeting nudge > meeting tonight > black book > aethoria > gym month-end > generic fallback.

---

## TASK-080
- assigned_to: marcus
- status: pending
- priority: high
- trigger: manual
- created: 2026-06-17 by Claude
- context: Typhon's Forge — Kraken Proxy pipe finalization script

**How to run:** Paste this brief into Perplexity (Marcus). Output goes to `djinn/research/marcus/TASK-080_kraken-pipe.md` in the vault. Claude reads and implements.

---

### Marcus Brief — Kraken Proxy Pipe Finalization

**What this is:**
Typhon's Forge (Javier's 3D print shop) builds Puffco Proxy accessories. The Proxy is a modular concentrate vaporizer. Accessories come in two types:
- **Core** — holds the Proxy bowl insert. Has a 38.7mm × 44.6mm deep bore.
- **Pipe** — the body/water attachment the core sits in. The core drops into the pipe from the top. The pipe delivers vapor from the core to the mouthpiece.

**The model:**
`/home/drmanzo/Downloads/kraken-typhons-forge/Kraken_pipe.stl`

A sculpted Kraken (octopus-like creature) 3D model — 78.9 × 92.7 × 97.4mm, watertight, already repaired with manifold3d, uniformly scaled so the sculpted cup in the model = 38.7mm diameter (matching Proxy Core spec).

Key geometry facts confirmed by Claude:
- The sculpted cup (the bowl the kraken holds) is the Core receiver — 38.7mm dia, already sized correctly
- Mantle tip (top of the model) = mouthpiece
- Proxy connection = bottom of the model
- No new bores needed — the sculpted geometry already provides the cup
- Model is a shell (not solid) — watertight shell mesh, not infilled solid

**What a Proxy pipe needs to function:**
1. The Core receiver cup (38.7mm dia) — ✅ already sculpted in
2. A vapor path from the cup floor up through the model body to the mouthpiece at the top
3. The mouthpiece opening must be open (not capped) so vapor exits
4. The base must be stable (flat enough to sit on a surface or fit a standard joint)
5. Wall thickness sufficient for FFF printing in ASA — minimum 1.2mm walls

**The question:**
Write a Python script (`finalize_kraken_pipe.py`) that:

1. **Checks the mouthpiece (mantle tip) opening** — fire a ray from outside the model downward into the tip area. If there's no opening (the tip is solid/capped), report it. Do NOT automatically cut it — just diagnose.

2. **Checks the vapor path** — fire rays from inside the cup upward through the model body toward the mouthpiece. Determine if there is a continuous open channel (void space) connecting the cup interior to the mouthpiece opening. Report: connected or blocked.

3. **Checks wall thickness** at the cup area (Z=0–10mm) — sample points around the 38.7mm cup perimeter and check that wall thickness is ≥ 1.2mm. Report min wall thickness found.

4. **Reports findings** as a clean summary:
```
Mouthpiece: OPEN | CAPPED (at Z=Xmm)
Vapor path: CLEAR | BLOCKED (at Z=Xmm)
Min wall thickness: X.Xmm at (x, y, z)
Action required: [none | list specific fixes]
```

**Tools available on this machine:**
- `trimesh` (ray casting, mesh loading, cross-sections)
- `manifold3d` (boolean ops if needed)
- `numpy`
- `shapely`
- Python 3.11 venv at `/home/drmanzo/.venvs/djinn-orchestrator/bin/python3.11`

**Constraints:**
- Do NOT apply any modifications in this script — diagnosis only
- Do NOT re-scale the model — it is already at final scale
- Script must run in under 60 seconds on a model with ~867K faces
- Use ray casting, not `mesh.contains()` — contains() is unreliable on complex organic shell meshes (confirmed this session)

**Reference:**
- Proxy Core spec: `~/Obsidian/djinn/printer/puffco_proxy_quad_uptake_recycler_specs.md`
- Pre-sculpted bowl workflow: `~/Obsidian/djinn/printer/workflows/proxy-core-presculpted-bowl.md`
- Cup center XY (after scaling): approximately (-1.2, -8.9)
- Cup floor Z (after scaling): approximately 1.69mm

**Output:**
Write the complete script to `djinn/research/marcus/TASK-080_kraken-pipe.md` as a fenced Python code block, preceded by a short explanation of the diagnostic approach for each check. Claude runs it and reports findings back.

**Deliver to:** Claude (reads via Read tool)

---

## TASK-103
- assigned_to: claude
- status: backlog
- priority: low
- trigger: manual
- created: 2026-06-18 by Javier
- context: Restart djinn-vault-enrich on Orin — stopped mid-run on 2026-06-16, last processed letter C (main run) and restarted from A (v2). 382 notes total, ~52 written so far. Check for resume/checkpoint mechanism before relaunching to avoid duplicating already-processed notes.

**When picked up:**
- SSH to 192.168.1.176
- Check script for checkpoint/resume logic
- If resume supported: restart from last written note
- If not: audit already-written notes in references/ to skip duplicates
- Monitor first 10 notes to confirm no duplication before leaving it running

## TASK-081
- assigned_to: salomon
- status: pending
- priority: high
- trigger: manual
- created: 2026-06-18 by Claude
- context: Phase C — Build djinn-blender-repair CLI wrapper

**Goal:** Wrap `blender/scripts/repair.py` as a first-class djinn CLI tool at `~/.local/bin/djinn-blender-repair`.

**File:** `~/.local/bin/djinn-blender-repair` (new, chmod +x)

**Interface:**
```
djinn-blender-repair <input.stl> [--out output.stl] [--report] [--timeout 120]
```
- `--out` defaults to `{input_stem}_repaired.stl` in same directory
- `--report` prints verbose face/issue summary to stdout
- `--timeout` seconds before killing Blender process (default 120)

**Key logic:**
1. Resolve script path: `~/typhons-forge/blender/scripts/repair.py` (git pull first if older than 24h — check mtime, skip if recent)
2. Call: `/snap/bin/blender --background --python {script} -- --input {input} --out {out}`
3. Capture stdout/stderr, pass through to caller
4. On exit code 0: print `✓ Repair complete: {out}` — done
5. On exit code 1: print `✗ Repair failed — non-manifold edges remain. See output above.` — exit 1
6. On timeout: kill process, print `✗ Blender repair timed out after {timeout}s` — exit 1
7. On Blender not found (`/snap/bin/blender` missing): print `✗ Blender not installed (snap). Run: sudo snap install blender` — exit 1

**Success criteria:**
```bash
djinn-blender-repair ~/Downloads/kraken-typhons-forge/Kraken_pipe.stl
# → should complete in < 120s, print repair summary, exit 0
python3 -m py_compile ~/.local/bin/djinn-blender-repair && echo OK
```

**Report back:** COMMS.md — paste repair output on Kraken_pipe.stl, confirm exit 0.

---

## TASK-082
- assigned_to: salomon
- status: pending
- priority: high
- trigger: manual
- created: 2026-06-18 by Claude
- context: Phase C — Build djinn-blender-render CLI wrapper
- depends_on: TASK-081 pattern (same structure, different script)

**Goal:** Wrap `blender/scripts/render.py` as `~/.local/bin/djinn-blender-render`.

**File:** `~/.local/bin/djinn-blender-render` (new, chmod +x)

**Interface:**
```
djinn-blender-render <input.stl> [--out cover.jpg] [--brand typhon|terp-tribe] [--engine eevee|cycles] [--size 1080] [--timeout 300]
```
- `--out` defaults to `{input_stem}_render.jpg` in same directory
- `--brand` defaults to `typhon`
- `--engine` defaults to `eevee`
- `--size` defaults to 1080
- `--timeout` defaults to 300 (Cycles needs more time)

**Key logic:**
1. Resolve script path: `~/typhons-forge/blender/scripts/render.py`
2. Resolve scenes dir: `~/typhons-forge/blender/scenes/`
3. Call: `/snap/bin/blender --background --python {script} -- --input {input} --out {out} --brand {brand} --engine {engine} --size {size}`
4. On exit 0: print `✓ Render complete: {out}` — done
5. On exit non-zero or timeout: print error, exit 1
6. If `--out` path ends in `.jpg`: ensure render.py gets the right file format (pass `--format jpg`)

**Success criteria:**
```bash
djinn-blender-render ~/Downloads/kraken-typhons-forge/Kraken_pipe.stl --out /tmp/kraken_test.jpg
# → /tmp/kraken_test.jpg exists, > 50KB, exit 0
ls -lh /tmp/kraken_test.jpg
```

**Report back:** COMMS.md — confirm render output exists and open it briefly to verify it's not black/blank (check file size as proxy).

---

## TASK-083
- assigned_to: salomon
- status: pending
- priority: high
- trigger: manual
- created: 2026-06-18 by Claude
- depends_on: TASK-081 complete and verified
- context: Phase C — Wire djinn-blender-repair into djinn-bore-core pre-flight

**Goal:** Meshy AI sculpts automatically get cleaned before boring. Zero new commands for Javier.

**File:** `~/.local/bin/djinn-bore-core` (modify existing)

**What to find:** The section near the top where the input STL is validated/loaded. Look for where the file path is read and where the mesh is first opened.

**Changes — add a pre-flight repair block after input validation, before any bore/mark operations:**

```python
import subprocess, os, re

def _should_repair(stl_path: str) -> bool:
    """Auto-repair if filename starts with Meshy_ or FORCE_BLENDER_REPAIR env is set."""
    basename = os.path.basename(stl_path)
    return basename.startswith("Meshy_") or os.environ.get("FORCE_BLENDER_REPAIR") == "1"

def _blender_repair(stl_path: str) -> str:
    """Run djinn-blender-repair, return path to repaired STL. Raises on failure."""
    repaired = stl_path.replace(".stl", "_repaired.stl")
    result = subprocess.run(
        ["djinn-blender-repair", stl_path, "--out", repaired],
        capture_output=True, text=True, timeout=150
    )
    if result.returncode != 0:
        raise RuntimeError(f"Blender repair failed:\n{result.stdout}\n{result.stderr}")
    print(f"[bore-core] Repair complete: {repaired}")
    return repaired
```

Then in the main flow, before the mesh is loaded for boring:
```python
if _should_repair(input_stl):
    print(f"[bore-core] Meshy source detected — running Blender repair pass...")
    input_stl = _blender_repair(input_stl)
```

**Behavior:**
- Meshy files (`Meshy_*.stl`) → auto-repair → use repaired file for boring
- All other files → no change, same as before
- If Blender repair fails → print warning, fall back to original file (don't block the bore)
- Set `FORCE_BLENDER_REPAIR=1` to trigger repair on any file for testing

**Success criteria:**
```bash
# Test with Kraken (not Meshy, use env var):
FORCE_BLENDER_REPAIR=1 djinn-bore-core Kraken_pipe.stl ...
# → should print "[bore-core] running Blender repair pass..." before boring begins
python3 -m py_compile ~/.local/bin/djinn-bore-core && echo OK
```

**Report back:** COMMS.md — show the `[bore-core] Repair complete` line from a test run.

---

## TASK-084
- assigned_to: salomon
- status: pending
- priority: high
- trigger: manual
- created: 2026-06-18 by Claude
- depends_on: TASK-082 complete and verified
- context: Phase C — Wire djinn-blender-render into djinn-media-ingest for auto cover.jpg

**Goal:** Every ingested project that has an STL source automatically gets a branded product render as its cover image. Zero new commands.

**File:** `~/.local/bin/djinn-media-ingest` (modify existing)

**What to find:** The section where the manifest is written and where `cover.jpg` is handled (or where the post-ingest steps run).

**Changes — add a render step after manifest creation:**

```python
import subprocess, os

def _render_cover(stl_path: str, project_dir: str, brand: str = "typhon") -> bool:
    """Render cover.jpg for the project. Returns True on success."""
    cover_path = os.path.join(project_dir, "done", "cover.jpg")
    os.makedirs(os.path.join(project_dir, "done"), exist_ok=True)
    result = subprocess.run(
        ["djinn-blender-render", stl_path, "--out", cover_path, "--brand", brand],
        capture_output=True, text=True, timeout=360
    )
    if result.returncode == 0:
        print(f"[ingest] Cover render: {cover_path}")
        return True
    else:
        print(f"[ingest] Render failed (non-blocking): {result.stderr.strip()}")
        return False
```

**Where to call it:**
- After manifest is written, check manifest for `stl_source` field (the path to the original STL)
- If `stl_source` exists and the file is accessible: call `_render_cover(stl_source, project_dir, brand)`
- Brand: read from manifest `brand` field if present, default `"typhon"`
- Non-blocking: render failure prints warning but does NOT fail the ingest
- Skip if `done/cover.jpg` already exists (don't overwrite existing covers)

**Add `--stl-source` flag to ingest CLI** so Javier can specify STL at ingest time:
```
djinn-media-ingest <footage_path> --job-name slug [--stl-source /path/to/model.stl] [--brand typhon|terp-tribe]
```
If `--stl-source` is passed: write it to manifest `stl_source` field + trigger render.
If not passed: check if a `.stl` file exists alongside the footage (same directory) — use it if found.

**Success criteria:**
```bash
# Ingest with explicit STL source:
djinn-media-ingest /some/footage.mp4 --job-name kraken-test --stl-source ~/Downloads/kraken-typhons-forge/Kraken_pipe.stl
# After ingest: ls {project_dir}/done/cover.jpg → file exists, > 50KB
python3 -m py_compile ~/.local/bin/djinn-media-ingest && echo OK
```

**Report back:** COMMS.md — show cover.jpg file size after a test ingest with --stl-source.

## TASK-085
- assigned_to: salomon
- status: pending
- priority: high
- trigger: manual
- created: 2026-06-18 by Claude
- context: Fix gateway — add QUEUE-aware "build TASK-NNN" command to Discord + Telegram gateways

**Problem:** `build TASK-081 TASK-082` sent to Discord routed to a generic Ollama model with no QUEUE context. Bot hallucinated completely wrong task descriptions. Any "build TASK-NNN" command needs to read the actual spec from QUEUE.md and pass it to opencode.

**Files:** `~/.local/bin/djinn-discord-gateway`, `~/.local/bin/djinn-telegram-gateway` (modify both)

**What to add — a `build` command handler:**

```python
import re, subprocess
from pathlib import Path

QUEUE_FILE = Path.home() / "Obsidian/djinn/communications/QUEUE.md"

def extract_task_spec(task_id: str) -> str | None:
    """Pull a single TASK-NNN block from QUEUE.md."""
    content = QUEUE_FILE.read_text()
    pattern = rf"(## {re.escape(task_id)}\n.*?)(?=\n## TASK-|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else None

def handle_build(match, raw):
    # Parse: "build TASK-081 TASK-082" or "build TASK-081"
    ids = re.findall(r"TASK-\d+", raw, re.IGNORECASE)
    if not ids:
        return "Usage: build TASK-NNN [TASK-NNN ...]"

    responses = []
    for task_id in ids:
        task_id = task_id.upper()
        spec = extract_task_spec(task_id)
        if not spec:
            responses.append(f"✗ {task_id} not found in QUEUE.md")
            continue

        prompt = f"Read this task spec and build it exactly as described. Do not ask questions — just build it.\n\n{spec}"
        result = subprocess.run(
            ["opencode", prompt],
            capture_output=True, text=True, timeout=600
        )
        if result.returncode == 0:
            responses.append(f"✓ {task_id}: build complete")
        else:
            responses.append(f"✗ {task_id}: opencode failed\n{result.stderr[:200]}")

    return "\n".join(responses)
```

Add to dispatch table in both gateways:
```python
r'build\s+(TASK-\d+(?:\s+TASK-\d+)*)': handle_build,
```

**This must be checked BEFORE the generic fallback LLM handler** — otherwise the regex never fires.

**Success criteria:**
```bash
# In Discord or Telegram:
build TASK-083
# → should print spec-matching output, not hallucinated content
# → opencode should actually build the djinn-bore-core wire
```

**Report back:** COMMS.md — show the Discord response to a `build TASK-083` test after this is deployed.

### TASK-085 — Blocker note (2026-06-18)
Gateway `build TASK-NNN` handler is wired and reads QUEUE.md correctly. Blocked by opencode startup context overflowing Groq llama-3.3-70b token limit. Fix: configure opencode to use a local Ollama model (qwen2.5:7b or deepseek-r1:7b) for headless `run` calls, or set `--model ollama/qwen2.5:7b` flag. Parked until model routing is resolved.

---

## TASK-086
- assigned_to: marcus
- status: done
- priority: high
- trigger: manual
- created: 2026-06-19 by Claude
- context: Blender addon A-2 — non-manifold edge detector operator

**Goal:** Add a `non_manifold_check.py` operator to the Typhon's Forge Blender addon that detects and highlights non-manifold edges/vertices in the active mesh and reports results to the user.

**File:** `~/typhons-forge/blender/addon/typhons_forge/operators/non_manifold_check.py`

**Spec:**
- Class name: `TF_OT_NonManifoldCheck`
- bl_idname: `tf.non_manifold_check`
- bl_label: `Check Non-Manifold`
- bl_description: `Select and highlight all non-manifold edges and vertices`

**What the operator does:**
1. Switch to Edit Mode on the active object.
2. Deselect all, then run `bpy.ops.mesh.select_non_manifold()`.
3. Count selected edges and vertices (use `bmesh` — iterate `bm.edges` / `bm.verts` where `e.select`).
4. Stay in Edit Mode so Javier can see what's highlighted (do NOT return to Object Mode).
5. Report via `self.report({'INFO'}, ...)`:
   - If 0 issues: `"✓ Manifold — no issues found"`
   - If issues: `"✗ Non-manifold: {n_edges} edges, {n_verts} verts — highlighted in viewport"`
6. Return `{'FINISHED'}`.

**Error handling:**
- If no active object: `self.report({'WARNING'}, "No active mesh selected")` → `{'CANCELLED'}`
- If active object is not a mesh: same warning.

**Panel wire-up:**
In `~/typhons-forge/blender/addon/typhons_forge/panels/main_panel.py`, add a button in the existing "Repair" or "QA" section:
```python
layout.operator("tf.non_manifold_check", icon='MESH_DATA')
```
If there is no Repair/QA section yet, create one with `layout.label(text="QA Checks:")`.

**Register:** Add to `operators/__init__.py` imports and register list.

**Test:**
```python
# From Blender scripting console, with a non-manifold mesh active:
bpy.ops.tf.non_manifold_check()
# Should select bad geometry and report the count
```

**Commit:** `git commit -m "feat: add non-manifold check operator (TF-A2)"` in typhons-forge repo.
**Report:** COMMS.md entry confirming operator works in viewport.

---

## TASK-087
- assigned_to: marcus
- status: done
- priority: high
- trigger: manual
- created: 2026-06-19 by Claude
- context: Blender addon A-2 — mesh cleanup operator (merge by distance + fill holes + remove loose)
- depends_on: TASK-086 pattern established

**Goal:** Add a `mesh_cleanup.py` operator that runs three standard mesh repair operations in sequence on the active object: merge by distance, fill holes, remove loose geometry.

**File:** `~/typhons-forge/blender/addon/typhons_forge/operators/mesh_cleanup.py`

**Class:** `TF_OT_MeshCleanup`
- bl_idname: `tf.mesh_cleanup`
- bl_label: `Clean Mesh`
- bl_description: `Merge doubles, fill holes, remove loose — repair pass for imported STLs`

**Properties (user-adjustable in operator redo panel):**
```python
merge_threshold: bpy.props.FloatProperty(name="Merge Distance", default=0.001, min=0.0001, max=1.0, unit='LENGTH')
fill_sides: bpy.props.IntProperty(name="Max Hole Sides", default=4, min=3, max=100)
```

**What the operator does:**
1. Switch to Edit Mode.
2. Select all (`bpy.ops.mesh.select_all(action='SELECT')`).
3. `bpy.ops.mesh.remove_doubles(threshold=self.merge_threshold)` → capture `info` for count.
4. `bpy.ops.mesh.fill_holes(sides=self.fill_sides)`.
5. Back to Object Mode.
6. Remove loose geometry: enter Edit Mode, `bpy.ops.mesh.select_all(action='DESELECT')`, `bpy.ops.mesh.select_loose()`, `bpy.ops.mesh.delete(type='VERT')`.
7. Return to Object Mode.
8. Record vertex/face counts before and after (use `len(obj.data.vertices)` / `len(obj.data.polygons)` before entering Edit Mode and after returning).
9. `self.report({'INFO'}, f"Cleanup done — {verts_removed} verts merged, holes filled, loose removed. Faces: {faces_before}→{faces_after}")`.

**Error handling:** Same guard as TASK-086 — no active mesh → cancel.

**Also update `blender/scripts/repair.py`:**
Add `remove_doubles` call if not already present, and expose the merge threshold as a `--merge-threshold` CLI arg (default 0.001). This keeps addon and headless behavior in sync.

**Panel wire-up:** Add button in the same Repair/QA section from TASK-086:
```python
layout.operator("tf.mesh_cleanup", icon='BRUSH_DATA')
```

**Register in `operators/__init__.py`.**

**Commit:** `git commit -m "feat: add mesh cleanup operator — merge/fill/loose (TF-A2)"` in typhons-forge.
**Report:** COMMS.md.

---

## TASK-088
- assigned_to: marcus
- status: done
- priority: high
- trigger: manual
- created: 2026-06-19 by Claude
- context: Blender addon A-2 — auto-center and bed-drop operator
- depends_on: TASK-086 pattern

**Goal:** Add an `align_to_bed.py` operator that centers the active object on the XY origin and drops it to Z=0 (bottom face touching the bed). One-click print prep.

**File:** `~/typhons-forge/blender/addon/typhons_forge/operators/align_to_bed.py`

**Class:** `TF_OT_AlignToBed`
- bl_idname: `tf.align_to_bed`
- bl_label: `Align to Bed`
- bl_description: `Center on X/Y origin and drop to Z=0 for print prep`

**What the operator does:**
1. Get `obj = context.active_object`. Guard for None/non-mesh.
2. Apply any pending transforms: `bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)`.
3. Get bounding box world-space min/max using `obj.bound_box` with `obj.matrix_world`:
   ```python
   import mathutils
   corners = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
   min_x = min(c.x for c in corners); max_x = max(c.x for c in corners)
   min_y = min(c.y for c in corners); max_y = max(c.y for c in corners)
   min_z = min(c.z for c in corners)
   ```
4. Center XY: `obj.location.x -= (min_x + max_x) / 2`, `obj.location.y -= (min_y + max_y) / 2`.
5. Drop to bed: `obj.location.z -= min_z`.
6. `self.report({'INFO'}, "Aligned to bed — centered XY, Z=0")`.

**Panel wire-up:** Add button in a "Print Prep" section:
```python
layout.label(text="Print Prep:")
layout.operator("tf.align_to_bed", icon='ANCHOR_BOTTOM')
```

**Register in `operators/__init__.py`.**

**Commit:** `git commit -m "feat: add align-to-bed operator (TF-A2)"` in typhons-forge.
**Report:** COMMS.md.

---

## TASK-089
- assigned_to: marcus
- status: done
- priority: high
- trigger: manual
- created: 2026-06-19 by Claude
- context: Blender addon A-2 — bounding box + volume/weight info panel widget

**Goal:** Add a panel section that displays live bounding box dimensions, mesh volume, and rough material weight estimate for the active object.

**File:** `~/typhons-forge/blender/addon/typhons_forge/panels/main_panel.py` (add new section)

**Display these values in the N-panel (draw logic reading from selected object):**
```
─── Mesh Info ───────────────────────
Bounds:   X: 45.3mm  Y: 30.1mm  Z: 22.8mm
Volume:   ~12,400 mm³
Material: PLA  [dropdown]
Weight:   ~15.4 g  (estimate — slicer overrides)
Faces:    18,432
```

**Implementation:**
1. In `draw(self, context)`, get `obj = context.active_object`. If None or not mesh, show "No mesh selected."
2. Use `obj.bound_box` + `obj.matrix_world` to compute dimensions (same math as TASK-088).
3. Use `obj.data.calc_volume()` for mesh volume in scene units. Check `context.scene.unit_settings.scale_length` — if scene uses meters (default), multiply mm³ result by `(1/scale_length)^3 * 1000^3`.
4. Register an EnumProperty on Scene for material selection:
   ```python
   bpy.types.Scene.tf_material = bpy.props.EnumProperty(
       name="Material",
       items=[('PLA','PLA',''),('PETG','PETG',''),('ASA','ASA',''),('TPU','TPU','')],
       default='PLA'
   )
   ```
5. Density map: `{'PLA': 1.24, 'PETG': 1.27, 'ASA': 1.07, 'TPU': 1.21}` g/cm³.
6. Compute: `weight_g = (volume_mm3 / 1000) * density`.
7. Show: `layout.label(text=f"~{weight_g:.1f} g")` + `layout.label(text="estimate — slicer overrides", icon='INFO')`.
8. Show face count: `len(obj.data.polygons)`.

Unregister `tf_material` scene prop on addon disable.

**Commit:** `git commit -m "feat: mesh info panel — bounds, volume, weight estimate (TF-A2)"` in typhons-forge.
**Report:** COMMS.md with sample output on a test STL.

---

## TASK-090
- assigned_to: marcus
- status: done
- priority: medium
- trigger: manual
- created: 2026-06-19 by Claude
- context: Blender addon A-2 — rename / version stamp operator

**Goal:** Add a `rename_object.py` operator that renames the active object and mesh data block in a consistent Typhon's Forge production naming format.

**File:** `~/typhons-forge/blender/addon/typhons_forge/operators/rename_object.py`

**Class:** `TF_OT_RenameObject`
- bl_idname: `tf.rename_object`
- bl_label: `Stamp Name / Version`
- bl_description: `Rename object with brand prefix, product name, and version tag`
- bl_options: `{'REGISTER', 'UNDO'}`

**Properties (shown in operator popup):**
```python
brand:   EnumProperty(items=[('tf','TF','Typhon Forge'),('tt','TT','Terp Tribe')], default='tf')
name:    StringProperty(name="Product Name", default="")
version: StringProperty(name="Version", default="v1")
```

**What the operator does:**
1. Guard: no active object → cancel with warning.
2. Build slug: `f"{self.brand}_{self.name.lower().replace(' ','_')}_{self.version}"` → e.g. `tf_kraken_pipe_v1`.
3. `obj.name = slug`
4. `obj.data.name = slug`
5. `self.report({'INFO'}, f"Renamed → {slug}")`.

**Invoke with dialog:** Override `invoke`:
```python
def invoke(self, context, event):
    return context.window_manager.invoke_props_dialog(self)
```

**Panel wire-up:** Add in Print Prep section:
```python
layout.operator("tf.rename_object", icon='FONT_DATA')
```

**Register in `operators/__init__.py`.**

**Commit:** `git commit -m "feat: rename/version stamp operator (TF-A2)"` in typhons-forge.
**Report:** COMMS.md.

---

## TASK-091
- assigned_to: marcus
- status: done
- priority: high
- trigger: manual
- created: 2026-06-19 by Claude
- context: Build djinn-blender-qa — headless QA script with three-class severity model

**Goal:** Create `~/typhons-forge/blender/scripts/qa_check.py` and the `djinn-blender-qa` CLI wrapper.

**Files:**
- `~/typhons-forge/blender/scripts/qa_check.py`
- `~/djinn-tools/djinn-blender-qa` (wrapper, same pattern as `djinn-blender-repair`)

---

### qa_check.py spec

**Usage (headless):**
```
blender --background --python qa_check.py -- --input model.stl [--printer ender3_v3_plus] [--material PLA] [--out report.json]
```

**Severity model — three classes:**

| Class | Meaning | Pipeline behavior |
|---|---|---|
| `critical` | Print will fail or part is defective | Exit 1, block slice |
| `warning` | Print may succeed but result degrades | Exit 0 with warnings, user decides |
| `info` | Informational only | Exit 0, included in report |

**Checks to implement:**

Critical:
- Non-manifold edges: use bmesh `select_non_manifold()`, count > 0 → critical
- Build volume exceeded: bounding box > printer envelope. Ender-3 V3 Plus = 300×300×300mm
- Zero volume: `mesh.calc_volume() == 0` → flat or inverted → critical

Warning:
- Wall thickness < threshold: sample at 50 random interior points with ray pair (cast in, measure depth to back face). Median < 1.2mm (PETG/ASA) or < 0.8mm (PLA) → warning
- High overhang: downward-facing faces (normal.z < -0.5) > 15% of total face count → warning
- High face count: > 500,000 faces → warning
- Trapped internal volume: detect closed interior shells via bmesh connected components on boundary

Info (always emit):
- Bounding box dimensions (X/Y/Z mm)
- Mesh volume mm³
- Face count
- Estimated weight g (volume × density, provisional)
- Non-manifold edge count (0 = pass)

**Output JSON:**
```json
{
  "file": "model.stl",
  "printer": "ender3_v3_plus",
  "material": "PLA",
  "passed": true,
  "exit_code": 0,
  "critical": [],
  "warnings": [
    {"code": "THIN_WALL", "message": "Median wall 0.9mm < 1.2mm", "threshold_mm": 1.2, "measured_mm": 0.9}
  ],
  "info": {
    "dimensions": {"x": 45.3, "y": 30.1, "z": 22.8},
    "volume_mm3": 12400,
    "face_count": 18432,
    "estimated_weight_g": 15.4,
    "non_manifold_edges": 0
  }
}
```

`passed` = true only if `critical` list is empty. Exit code 1 if any critical issue.

### djinn-blender-qa wrapper spec

Same pattern as `djinn-blender-repair`:
```
djinn-blender-qa <input.stl> [--printer ender3_v3_plus] [--material PLA] [--out report.json] [--timeout 120]
```

- Resolves script: `~/typhons-forge/blender/scripts/qa_check.py`
- Exit 1 on critical: print `✗ QA FAILED: {issues}`
- Exit 0 with warnings: print `⚠ QA passed with warnings`
- Clean pass: print `✓ QA passed`
- Install to `~/djinn-tools/djinn-blender-qa` and `~/.local/bin/djinn-blender-qa`

**Update `~/typhons-forge/blender/README.md` Build Status table:**
```
| B-3 | djinn-blender-qa | done |
```

**Commit:** `git commit -m "feat: djinn-blender-qa — three-class QA script (B-3)"` in both repos.
**Report:** COMMS.md with sample output from a test STL.

---
**TASK:** Save Penelope Z offset to EEPROM
**FOR:** Javier (manual — OctoPrint terminal)
**DATE:** 2026-06-29
**ACTION:** Open OctoPrint terminal → run `M851 Z-0.599` then `M500`. Current babystep is RAM only and resets on power cycle.

**TASK:** Approve and print Camood_TerpTribeHq_union.stl
**FOR:** Javier
**DATE:** 2026-06-29
**FILE:** ~/Desktop/Review/Camood_TerpTribeHq_union.stl
**ACTION:** Review, approve, send to Calliope via Creality on-device slicer. Single body, boolean-unioned, ready to slice.

**TASK:** Replace nozzle_mcu cable harness on Calliope
**FOR:** Javier (hardware)
**DATE:** 2026-06-29
**ACTION:** Reseat is not permanent. Order or source replacement cable/connector for nozzle_mcu UART on Ender-3 V3 Plus.

---
**TASK:** ~~Typhon Windows onboarding — physical/RDP steps~~ SUPERSEDED — see below
**STATUS:** done — SSH/Tailscale access established, remote onboarding completed, see [[2026-07-01_typhon-windows-remote-onboarding]]

---
**TASK:** Typhon Windows onboarding — one interactive/RDP session needed to finish
**FOR:** Javier (manual — needs an interactive login at the machine, not SSH)
**DATE:** 2026-07-01
**CONTEXT:** Full remote setup is done (SSH over Tailscale, Claude Code authenticated, repos cloned, ~18 pipeline apps installed — see `machines/TF-TTHQ.md`). Two things are stuck because Windows blocks GUI/service init over non-interactive SSH (Session 0 isolation — see [[2026-07-01_bug-typhon-session0-noninteractive-hangs]]).
**ACTION:**
1. Log in to Typhon interactively (physically or via RDP, not SSH). Run:
   `"C:\Users\typho\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude-code\2.1.187\claude.exe" --dangerously-skip-permissions`
   and click through the disclaimer/theme prompts once. This unlocks `--bg` (background agent) mode for future unattended automation.
2. Start Ollama once from that same interactive session (Start Menu or `ollama serve` in a terminal) and confirm it stays running (check `http://localhost:11434` responds). Once it's stable, pull the model set from the old Ollama Models table in `machines/TF-TTHQ.md` (qwen2.5:7b, qwen2.5:1.5b, llama3.2:3b, nomic-embed-text at minimum).
3. Retry the 1Password install (`winget install --id AgileBits.1Password`) — it failed twice with a SID-mapping error, possibly tied to the recent account rename; a reboot may clear it.
4. Confirm the real current IP of the Oroborus/Library storage share — `setup-typhon.ps1` maps `Z:` to `\\192.168.1.176\storage`, which wasn't a live host on the LAN during recent scans.
5. Decide (with Claude): stick with the native-Windows approach used for this onboarding, or still pursue WSL2 for closer parity with old Typhon's service model — see decision-log 2026-07-01 entry.
5. Join Tailscale.

---

## TASK-092 — Typhon: Unlock SSH + Import slicer profiles
- assigned_to: typhon (Javier — needs interactive session)
- status: pending
- priority: high
- trigger: manual
- created: 2026-07-03 by Claude
- context: Typhon SSH is locked behind Windows firewall/Session 0 isolation. `typhon-unlock.ps1` on USB needs to run as Admin interactively. After unlock, import `bambufy-template-bambustudio.3mf` as default Iris profile and `orca-profiles/` JSONs for Nemesis.

**Actions (after SSH unlock):**
1. Run `typhon-unlock.ps1` as Admin on Typhon to configure SSH key auth + firewall
2. Open `bambufy-template-bambustudio.3mf` (on USB) in Bambu Studio → save as default Iris profile
3. Import `orca-profiles/Iris-AD5X-0.4mm-Bambufy.json` and `orca-profiles/Nemesis-AD5M-Pro-0.4mm.json` into OrcaSlicer

---

## TASK-093 — Iris: Test first multi-color print
- assigned_to: javier
- status: pending
- priority: high
- trigger: manual
- created: 2026-07-03 by Claude
- context: Bambufy is live on Iris but untested with an actual multi-color print. After slicer profiles are on Typhon, slice a small 2-color test and print.

**Pre-flight check:**
1. If Iris Klipper was restarted since setup: run `SET_GCODE_VARIABLE MACRO=_IFS_VARS VARIABLE=init VALUE=1` in the console first
2. Slice a small 2-color model using Bambu Studio with the Iris profile
3. Send to Iris and observe filament changes

---

## TASK-094 — Iris: Fix `_START_BAMBUFY` delayed gcode auto-init
- assigned_to: claude
- status: pending
- priority: normal
- trigger: manual
- created: 2026-07-03 by Claude
- context: bambufy's `_START_BAMBUFY` delayed gcode doesn't auto-load on zmod Klipper. After every restart, user must manually trigger init. Need to find a workaround (Klipper delayed_gcode vs STARTUP vs moonraker startup script).

**Approach:** Research and implement one of:
1. Add `_START_BAMBUFY` init to a RESTART gcode macro override
2. Use Moonraker's `[power]` or `[button]` startup automation
3. Inject `_IFS_VARS.init=1` via moonraker.conf on_connect handler

---
**QUEUED:** 2026-07-03
**FOR:** Salomon
**FROM:** Claude
**TASK:** Install OrcaSlicer + Bambu Studio on Typhon

After Typhon SSH is unlocked (run djinn/ssh-recovery/typhon-unlock.ps1 from USB as Admin on Typhon):

```bash
~/forge/slicer-setup/djinn-typhon-slicers.sh
```

This pushes both installers from ~/forge/slicers/ and runs silent installs on Typhon. Full step-by-step also in Typhon USB at djinn/OPENCODE-PROMPT.md.

**ALSO:** After OrcaSlicer is on Typhon and connected to Iris (192.168.1.50:7125), run in Iris Klipper console (http://192.168.1.50):
```
ENABLE_PLUGIN name=bambufy
```

---
**QUEUED:** 2026-07-05
**FOR:** Javier (physical)
**FROM:** Claude
**TASK:** Nemesis bed re-tramming

Right side of Nemesis bed is physically low by ~0.6mm (mesh shows -2.82 at right vs -1.53 at left). Needs manual corner screw adjustment while bed is warm (70°C). Raise right side and re-run BED_MESH_CALIBRATE after.

---
**QUEUED:** 2026-07-05
**FOR:** Javier (physical) + Claude (config)
**FROM:** Claude
**TASK:** Calliope replacement cable install

When new toolhead cable arrives:
1. Install with 40–50mm service loop at toolhead connector
2. Route separately from stepper motor wires (opposite sides of cable chain)
3. Anchor cable to X carriage body with zip tie — force goes to tie, not connector
4. Reseat or replace JST connector on nozzle board (fretting wear likely)
5. After install: run `G28` → `PROBE_CALIBRATE` → `ACCEPT` → write z_offset to printer.cfg → `BED_MESH_CALIBRATE` → `SAVE_CONFIG`
6. Tag @Claude to verify config after install

---
**QUEUED:** 2026-07-05
**FOR:** Claude
**FROM:** Claude
**TASK:** Nemesis — move [probe] section to printer.cfg for SAVE_CONFIG compatibility

Currently `[probe]` with z_offset is in `/opt/config/printer.base.cfg` (included file). This means SAVE_CONFIG always fails for z_offset with "conflicts with included value". Fix: move the entire `[probe]` section from printer.base.cfg into printer.cfg directly. After that, PROBE_CALIBRATE + SAVE_CONFIG will work normally. Do this when Nemesis is not mid-print.

**RESOLVED — 2026-07-09 by Claude.** Verified via SSH: `[probe]` now lives directly in `printer.cfg` (not printer.base.cfg), so `SAVE_CONFIG` no longer conflicts. Current z_offset (0.071) and bed mesh differ from the 7/5 calibration (-0.401, 1.3mm variation) — confirmed with Javier this is expected, not data loss: he physically relocated Nemesis and recalibrated it himself around 7/8, hence the new numbers. No further action needed.

---

**QUEUED:** 2026-07-06
**FOR:** Javier
**FROM:** Claude
**TASK:** Iris — monitor first multi-color tool change

Watch the first filament change on any Iris multi-color print. Confirm `_GOTO_TRASH` fires (toolhead moves to trash bucket at Y≈210), filament purges, `_SBROS_TRASH` fires, and print resumes. If the trash position is wrong, tune `shoot_y_position` via: `SET_GCODE_VARIABLE MACRO=_IFS_VARS VARIABLE=shoot_y_position VALUE=<new>` + `SAVE_VARIABLE`.

---

**QUEUED:** 2026-07-06
**FOR:** Javier
**FROM:** Claude
**TASK:** Calliope cable — install when parts arrive

Service loop 40–50mm at toolhead connector. Route nozzle_mcu cable separately from stepper wires (EMI). Anchor to X carriage with zip tie so pulling force goes to anchor, not connector. After install: PROBE_CALIBRATE → BED_MESH_CALIBRATE → test PETG print.

---

## Calliope Bring-Up — $(date +%Y-%m-%d) → Tomorrow

### Physical (Javier)
- [ ] Install replacement nozzle_mcu UART cable (service loop 40–50mm, anchor to X carriage)
- [ ] Separate cable from stepper wires (EMI isolation)
- [ ] Route drag chain
- [ ] Level the drawer Calliope sits on
- [ ] Power on and confirm no key561 / bytes_invalid errors in Fluidd console

### Software (Claude via SSH once Calliope is online at 192.168.1.114)
- [ ] SSH into Calliope host at `192.168.1.114`
- [ ] Copy `~/Obsidian/djinn/printer/config/fan-cap-calliope.cfg` to Calliope config directory
- [ ] Add `[include fan-cap-calliope.cfg]` to `printer.cfg`
- [ ] `FIRMWARE_RESTART`
- [ ] Test: send `M106 S255` from Fluidd console — confirm log shows `M106 capped: S255 -> S128 (BUG-014 fan cap)`
- [ ] Test: send `M106 S0` — confirm fan turns off cleanly (no cap log)
- [ ] Test: send `M106 S64` — confirm passes through unchanged (no cap log)
- [ ] Run a short PLA test print and verify fan never exceeds 50%

### Before first commission print
- [ ] Confirm `djinn-print-safety` is running with `DJINN_MOONRAKER=http://192.168.1.114:7125`
- [ ] Re-level bed and run `BED_MESH_CALIBRATE`
- [ ] Verify `djinn-gcode-safety` situation (source missing — check if fan-cap macro makes it redundant)

— Claude, 2026-07-07

**CORRECTION — 2026-07-09 by Claude.** Skip the entire "Software" fan-cap block above (lines re: `fan-cap-calliope.cfg`, `M106` cap tests). BUG-014's root cause was reinvestigated and confirmed on 2026-06-29 (see `logs/bugs.md`): the dropouts are the toolhead cable pulling to its stress point during engraved/embossed toolpaths, not EMI from fan PWM. The fan cap (and thermal soak, 3x3 mesh, TRSYNC) were all tried and reverted as ineffective — stock config is correct. Installing the fan cap again would be reintroducing a dead-end fix. `~/Obsidian/forge/config/fan-cap-calliope.cfg` also moved under the 7/8 department restructure — the path referenced above (`djinn/printer/config/`) no longer exists. Post-cable-install steps are just: PROBE_CALIBRATE → BED_MESH_CALIBRATE → test print with single-merged-body geometry (no separate engrave/emboss shells) and gyroid infill, per the validated Calliope print rules in bugs.md. (Also: the "$(date +%Y-%m-%d)" in the section header above is an unexpanded shell variable, not a real date — this checklist was written 2026-07-07.)

## TASK-095 — Oroborus: Check /mnt/archive drive + create marcus structure
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-07-08 by Claude
- closed: 2026-07-08 by Claude
- context: RESOLVED — djinn-archive SSD (/dev/sdb1, 1.8TB) is physically connected to Salomon, not Oroborus. Mounted at /mnt/alexandria. Marcus structure created directly on Salomon. Oroborus /mnt/archive I/O errors irrelevant — that drive is separate.

**Resolution:**
- SSD label: djinn-archive
- Mount: /mnt/alexandria/
- Marcus structure created: _inbox/ _processed/ _index/
- README written to drive
- Vault INDEX.md updated with correct path
- No Oroborus action needed for marcus

## TASK-096 — Salomon idle: Marcus research pass-through agent
- assigned_to: salomon
- status: pending
- priority: low
- trigger: manual — run only when Salomon is idle (Javier not actively using it)
- created: 2026-07-08 by Claude
- context: Slow background pass-through of Marcus research exports on Oroborus. For each folder in /mnt/archive/marcus/_inbox/, read the content, extract key insights, write a consolidated summary to _index/<topic>.md, move the source folder to _processed/. Do NOT delete originals — _processed/ is the permanent record. Update ai/marcus/INDEX.md in vault with each new entry and commit.

**Logic (no djinn tool yet — run manually or write djinn-marcus-index):**
```bash
# For each unprocessed session in _inbox/
for dir in /mnt/archive/marcus/_inbox/*/; do
    topic=$(basename "$dir")
    echo "Processing: $topic"
    
    # Use Salomon's local model (phi4:14b or qwen2.5:7b) to summarize
    # Feed all .md files in the dir as context
    # Write output to /mnt/archive/marcus/_index/${topic}_summary.md
    
    # Move to processed
    mv "$dir" /mnt/archive/marcus/_processed/
    
    # Update vault index
    # Append row to ~/Obsidian/ai/marcus/INDEX.md
    echo "| $(date +%Y-%m-%d) | $topic | _processed/$topic | summarized |" >> ~/Obsidian/ai/marcus/INDEX.md
done

# Commit index update
cd ~/Obsidian && git add ai/marcus/INDEX.md && git commit -m "ai: marcus index updated by idle agent" && git push
```
**Note:** Write this as a proper djinn-marcus-index tool once TASK-008 confirms Oroborus is healthy.

## TASK-097 — Salomon: Move ~/Games to Alexandria
- assigned_to: claude
- status: pending
- priority: normal
- trigger: manual
- created: 2026-07-12 by Claude
- context: ~/Games/epic-games-store/ (3.3GB) still on Salomon. Move to /run/media/drmanzo/alexandria/games/ to clear Salomon. Confirm games still launch after move (symlink if needed).

## TASK-098 — Salomon: Clean stale /mnt/ subdirs
- assigned_to: claude
- status: pending
- priority: low
- trigger: manual
- created: 2026-07-12 by Claude
- context: /mnt/ has leftover empty dirs from old manual mounts: iris-usb, penelope-sd, piboot, piroot, typhon-usb, winiso, winusb. Verify all are empty/stale then rmdir.

## TASK-099 — Oroborus: forge/forge commit (actionable) + djinn-core status (Javier's call)
- assigned_to: oroborus (local opencode agent executes the forge/forge part;
  if a Claude session on Oroborus is invoked, its job is to supervise/verify
  only, not run the commands itself — deterministic git ops don't need
  Claude-tier reasoning or its token cost. Report back in COMMS.md when done.)
- status: **Part A done 2026-07-18 by Claude (Oroborus)** — delegated to local
  opencode, verified diff/commit before reporting. Commit `768ceb9`, no push
  (no remote configured, correctly left alone). Diff turned out bigger than
  this task's original description — see 2026-07-18 COMMS entry, flagged to
  Javier, not silently committed as a footnote. **Part B (djinn-core) still
  pending — still needs Javier's call, not actioned.**
- status (superseded): pending — corrected 2026-07-12 by Claude (Salomon). Original task
  description was wrong on both repos; re-verified directly via SSH before
  rewriting. `git` is now installed on Oroborus (wasn't earlier today —
  confirmed progress from whoever/whatever ran `apt install git`).
- priority: normal
- trigger: manual
- created: 2026-07-12 by Claude

**Part A — `~/code/forge/forge` (actionable now, do this):**

Confirmed real, legitimate uncommitted work — not noise. Two files:
- `forge/discord/watcher.py` — real feature change: adds `JAVIER_CHAT_ID`
  and `load_tg_token()` reading `~/.config/djinn/ops-tg.env`'s
  `DJINN_TG_TOKEN` — looks like Telegram notification wiring for the
  Discord watcher, same credential pattern used elsewhere in Djinn.
- `forge/shop/__pycache__/customer_dm.cpython-311.pyc` — stale tracked
  bytecode from before `.gitignore` (which already correctly excludes
  `__pycache__/` and `*.pyc`) was added in a later commit. Never
  retroactively untracked.

Steps:
1. `cd ~/code/forge/forge`
2. `git rm --cached forge/shop/__pycache__/customer_dm.cpython-311.pyc` — stop tracking it (already gitignored, this just fixes the pre-existing leftover)
3. `git add forge/discord/watcher.py`
4. `git commit -m "discord watcher: wire Telegram notifications via ops-tg.env"` (or a better message once you've read the full diff — this is a summary from a partial diff view, verify before committing)
5. No `git push` — this repo has **no remote configured at all** (checked: `git remote -v` returns nothing), only 2 commits total in its history. Looks like local-only development that was never meant to go to GitHub yet, not a broken/missing remote. Don't invent one — just commit locally and report.

**Part B — `~/code/djinn/djinn-core` (NOT actionable — needs Javier, don't guess):**

This is not a "commit uncommitted changes" situation. There is **no `.git` directory here at all** — confirmed directly. It has a `.gitignore` and `README.md` (files you'd expect in a repo) but no git metadata — it was never actually version-controlled at this location. There's also no `DrManzo/djinn-core` repository on GitHub (checked via `gh repo view` — doesn't exist).

Do not `git init` this and start committing — that would create a brand-new, disconnected repo with no history, silently, which could be the wrong move depending on what Javier actually wants. Open questions only Javier can answer:
- Was djinn-core previously version-controlled somewhere else (a different path on Salomon, or folded into another repo) before this rsync migration, and did the `.git` just fail to copy over?
- Should this become its own real GitHub repo now, or is it meant to be untracked deployed code (like some other `~/.local/bin/` tools that were never in djinn-tools either)?

Flag this in COMMS.md and stop there — don't take any git action on djinn-core until Javier weighs in.

## TASK-100 — Penelope: Investigate offline status
- assigned_to: javier
- status: resolved — premise was wrong
- priority: normal
- trigger: manual
- created: 2026-07-12 by Claude
- closed: 2026-07-12 by Claude
- context: RESOLVED — original task incorrectly described Penelope as a networked device at 192.168.1.150. Penelope has no independent IP — it's an Ender 3 Pro connected via USB, run through OctoPrint hosted on Salomon (`http://localhost:5001`, per `forge/config/fleet-registry.json`). Confirmed live 2026-07-12: OctoPrint is up and responding (HTTP 302 on :5001, real process listening). Nothing was actually offline; the task was chasing a network address that was never Penelope's in the first place.

## TASK-101 — Typhon: Power on + mount as network share
- assigned_to: javier
- status: pending
- priority: high
- trigger: manual
- created: 2026-07-12 by Claude
- context: Typhon (192.168.1.113) offline. Once powered on: mount SMB shares from Salomon at /run/media/drmanzo/typhon, configure Bambu Studio + OrcaSlicer for Iris/Nemesis access. Also run chkdsk on the USB stick (currently dirty NTFS).

## TASK-102 — Filament: Update inventory to current stock
- assigned_to: javier+claude
- status: in-progress
- priority: high
- trigger: manual
- created: 2026-07-12 by Claude
- context: filament-inventory.json last updated 2026-06-08, only 3 spools (stale). Needs full physical count of current spools: material, color, brand, weight remaining, which printer loaded. Javier provides count, Claude updates file.

## TASK-103
- assigned_to: claude
- status: in_progress
- priority: low
- trigger: manual
- created: 2026-07-12 by Claude
- context: purge dead OctoPrint key (KOYv4Nj2...) from djinn-vault git history

**Brief:**
git filter-repo --replace-text run against ~/Obsidian timed out at 394MB repo size
(2-min window, several stray worktree branches). No corruption (git fsck clean,
vault-sync.timer restarted). Key is already confirmed dead so no live exposure —
this is hygiene only, not urgent. Redo as a deliberate off-hours pass: pause
vault-sync.timer, run filter-repo with a long/background timeout, verify with
git fsck --full, force-push, restart timer. Consider pruning stray
worktree-* branches first to speed up the rewrite.

**Input:** [[2026-07-12_bug-live-octoprint-api-key-hardcoded-in-public-penelope-manual-md]]

## TASK-104
- assigned_to: marcus
- status: pending
- priority: normal
- trigger: manual
- created: 2026-07-14 by Claude (per Javier)
- context: Personal CFO cash-flow modeling. Javier provided 7 raw financial source documents (Chase checking/savings activity, J.P. Morgan brokerage positions/tax lots, EAI report, 2 brokerage statement PDFs) covering Mar 2025–Jul 2026. Raw documents contain account numbers and transaction-level detail and are intentionally kept out of git (archived locally, gitignored, at `personal/finance/raw/2026-07-14/`). Claude extracted and aggregated the numbers into a summary with no account numbers, no raw transaction rows, and no third-party full names.

**Brief:** Read `ai/marcus/finance/briefs/2026-07-14_cashflow-summary.md` for income streams, categorized outflows, monthly net trend, and current cash/brokerage position. Section 5 of that file (risk tolerance, time horizon, hard rules) is intentionally blank — Javier will supply that context directly in the Perplexity session, it's not derivable from documents. Use this to build/refine the cash-flow model and stress-test discussed in TASK-039 (`ai/marcus/finance/TASK-039_djinn-cash-research-output.md`).

**Output expected:** `ai/marcus/finance/TASK-104_cashflow-model.md`

**Deliver to:** Javier (COMMS summary) + Claude (reads via GitHub, integrates if needed)

## ~~TASK-105~~ — RESOLVED 2026-08-24
- assigned_to: claude
- status: resolved (2026-08-24, by Claude, folded into the same pass as the djinn/personal/* git-history purge)
- priority: was high
- trigger: manual
- created: 2026-07-15 by Claude (per Javier)
- context: 8 raw Marcus threads (djinn-vault) with genuinely personal content — AA/recovery disclosure, a raw "Wounded Healer and The Fool" relationship/promiscuity self-analysis thread, and (found on a second, broader pass using the new djinn-clerk sensitivity filter, not the initial manual grep) a thread discussing a partner's active addiction and an "I love you" exchange — were sitting in ai/marcus/threads/, which is publicly tracked (not gitignored like RAW/ and personal/). Removed from current tracking 2026-07-15 (commits aba1ee01 + follow-up), content preserved at RAW/marcus-personal-recovered/ (gitignored). Full git history purge intentionally deferred — other background jobs had active worktree branches at the time, and a filter-repo history rewrite mid-session risks breaking their in-progress work far worse than a normal push conflict would. Same deferral pattern as TASK-103 (dead OctoPrint key), but higher priority — this is live personal content, not a dead credential. Root cause fixed going forward: djinn-clerk (~/.local/bin, not git-tracked) now runs a content-sensitivity filter before routing any perplexity-pro thread to the public ai/marcus/threads/ path — flagged threads go to personal/marcus-threads/ (gitignored) instead. Filter combines a keyword list (recovery, therapy, mental health, relationship terms) with names dynamically loaded from personal/people/relationship-map.md, so it stays current without code edits. Before re-running djinn-clerk over any backlog, double-check whether more than these 8 files need the same treatment — this filter is new and wasn't in place when the original 59 threads were written.

**Update 2026-07-16:** Scope expanded significantly — a second, much larger exposure found in the same sweep: djinn-vault-enrich and djinn-clerk's general (non-Marcus) note path had the identical zero-filtering gap, affecting the publicly-tracked `references/` and `i notes/Notes/` (not just `ai/marcus/threads/`). 59 more files removed across three passes (30 + 12 + 17, the last 17 being a self-inflicted reprocessing duplicate caught and fixed in the same pass — see the 2026-07-16 bug report). Root cause now fixed at the source in both tools, same pattern as the Marcus fix. This task's scope is now the full combined list below, not just the original 8.

**Brief:** Do this as a deliberate off-hours pass when no other background jobs/worktrees are active: `git worktree list` should show only the main checkout. Pause `vault-sync.timer` on Salomon first (`systemctl --user stop vault-sync.timer`). Run `git filter-repo --path <each filename below> --invert-paths` (scoped path removal should be much faster than the earlier --replace-text run that timed out on this 394MB repo — this targets specific file paths, not a full-content text scan). Files (ai/marcus/threads/ — original 8):
  - ai/marcus/threads/2026-06-01_marcus-og.md
  - ai/marcus/threads/pplx_1f4c8eb0-5172-4725-bbc7-4dac61542052.md
  - ai/marcus/threads/2026-06-01_so-marcus-you-there.md
  - ai/marcus/threads/2026-06-01_so-marcus-you-there-ou_there.md
  - ai/marcus/threads/pplx_c9de8f2c-6946-4a5e-868d-83765376984b.md
  - ai/marcus/threads/pplx_320bbe04-b875-4ad6-9a41-c1daa4a40cab.md
  - ai/marcus/threads/2026-06-01_you-are-marcus-read-this-httpsgithubcomdrmanzodjinn-vault.md
  - ai/marcus/threads/pplx_19eddb5a-76ce-425c-b75a-d78a4aa15ad0.md

Files (references/ + i notes/Notes/ — 2026-07-16 addition): every path touched by commits `8617c8c1`, `89d6e6ae`, and `a6287a2b` on this repo — use `git log --diff-filter=D --name-only 8617c8c1^..a6287a2b` to generate the exact list at purge time rather than hand-copying it here (safer than risking a stale/incomplete manual list for a destructive history op). Also redact-only (don't remove the whole file, just the 33 rows already stripped by commit `8617c8c1`) in `references/Source-Inventory-Raw-Files.md`'s history if `filter-repo --replace-text` is used for that one file specifically.

Verify with `git fsck --full` before force-pushing. Force-push, then restart `vault-sync.timer`. Other machines with existing clones (Oroborus, Typhon, any worktrees) will need `git fetch && git reset --hard origin/main` afterward, not a fresh clone (would lose gitignored local-only content).

**Input:** [[2026-07-15_bug-djinn-clerk-s-marcus-dir-hardcoded-to-dead-pre-restructure-path-would-have-silently-misfiled-real-marcus-threads]], [[2026-07-16_bug-djinn-vault-enrich-and-djinn-clerk-s-general-note-path-had-the-same-zero-filtering-gap-as-the-marcus-path-59-files-exposed-in-public-references-and-i-notes-notes-since-2026-05-19]]

**Resolved 2026-08-24:** Executed via `git filter-repo` in one combined pass alongside the separate djinn/personal/* history purge (see that closure note above, near the top of this file). Exact scope used: the original 8 `ai/marcus/threads/` files by literal path, all 50 files from `git log --diff-filter=D --name-only 8617c8c1^..a6287a2b` (generated fresh at purge time, per this task's own instruction, not hand-copied), plus a `--replace-text` pass redacting the 33 raw-filename rows in `references/Source-Inventory-Raw-Files.md`'s history (the file itself, not removed — only those 33 identifying rows). `git fsck --full` clean before push. Checked all other locally-registered branches/worktrees first (`git worktree list` showed 6 stale worktrees from past sessions — none active, none containing any of the purged paths on their already-pushed remote counterparts) before touching the shared object database, since this task's own brief warned against a mid-session rewrite when other worktrees are live. Force-pushed `main` only — commit count went from 7710 to 7707 on that branch (3 commits pruned as degenerate-empty once their sole content was purged paths); every other branch left untouched. Verified post-push: `origin/main` has zero trace of any purged path. Full report: `logs/reports/2026-08-24_vault-history-purge-personal-and-task105.md`.

Per Javier's 2026-08-24 instruction, Oroborus is being retired (Typhon + Salomon only going forward) — its clone does not need `git fetch && git reset --hard`. **Typhon still does**, whenever its vault clone is next reprovisioned/back online.

## TASK-106
- assigned_to: marcus
- status: pending
- priority: normal
- trigger: manual
- created: 2026-07-15 by Claude (per Javier)
- context: Javier wants the recovered personal Marcus threads (recovery/relationship content, see TASK-105) worked directly by Marcus going forward, not by Claude — this is squarely Marcus's lane (you already have native conversational continuity with these threads from the live Perplexity sessions; Claude does not and shouldn't be the one processing this content further). Claude's role here was privacy remediation only (getting the content off the public repo path and building the filter that prevents recurrence) — see the two 2026-07-15 bug reports on djinn-clerk for that work. Extraction/synthesis of the actual personal content is handed off to you.

**Brief:** The recovered/preserved files are gitignored, not linked here directly since this file is public — read them from:
  - `RAW/marcus-personal-recovered/` (8 files, the originals that were removed from the public ai/marcus/threads/ path)
  - `personal/marcus-threads/` (where djinn-clerk now correctly routes anything it flags as personal/sensitive going forward, including one new continuation Javier pasted directly 2026-07-15)

Continue this work using your existing personal-layer infrastructure (`personal/modules/recovery.py`, `personal/README.md`'s TASK-078 step-work/recovery tracking, `/reflect`, `/step`, `/sponsor_contact` etc.) rather than starting fresh — extract whatever's useful to Javier's ongoing recovery/personal-growth work and continue the thread naturally, same as any other live Marcus session would.

**Output expected:** Whatever form makes sense for continuing this with Javier directly (Telegram via djinn-personal-gateway, or a session note) — this isn't a technical deliverable like other TASK entries, it's picking the conversation back up.

**Deliver to:** Javier directly.

---

## ~~Find and fix PA-layer dashboard sync writing to djinn/personal/ instead of personal/~~ — RESOLVED same session

- status: resolved (2026-08-19, same session, by Claude — closing out before Salomon picked it up)
- priority: was high
- context: `djinn/personal/recovery.md`, `sobriety.md`, `health.md`, `habits.md`, `aethoria.md`, `academic/status.md` were dashboard-sync output with zero gitignore coverage, one push away from public exposure.
- **Root cause found:** `/home/drmanzo/.local/bin/djinn-personal-db`, function `cmd_vault_sync()` (invoked via `djinn-personal-db sync`, and automatically after most commands), line 894, hardcoded `vault = Path.home() / "Obsidian/djinn/personal"` — should have been `Path.home() / "Obsidian/personal"` (the actual private, gitignored tree; see `personal/README.md`). Simple wrong-path typo, not a Salomon-side script — `~/.local/bin` isn't a git repo, so no vault commit needed for this file itself.
- **Fix applied:** corrected the path, ran `djinn-personal-db sync` to regenerate the 6 mirror files at the correct `personal/` location, deleted the stale copies at `djinn/personal/` (now removed entirely, was DB-derived and gitignored anyway — no data loss, SQLite remains the source of truth).
- **Verified:** `ls ~/Obsidian/personal/*.md` shows fresh `_Last synced_` timestamps at the new path; `djinn/personal/` no longer exists.
- **Correction, 2026-08-24:** "No further action needed" was wrong — it covered the live files and the sync-script bug, not the git history. Those 6 files sat in ~27 unpushed local commits (2026-07-23 through 2026-08-19) on a public GitHub repo for a month before this was caught during an unrelated vault cleanup pass. Purged via `git filter-repo` + verified force-push on 2026-08-24, combined with the TASK-105 purge in the same operation. See that task's resolution note and `logs/reports/2026-08-24_vault-history-purge-personal-and-task105.md` for full detail. The `.gitignore` rule itself remains correct and harmless to leave in place.

---

## Check djinn-penelope-usbip-watch.service once Typhon is back online

- status: pending — blocked on external dependency (Typhon), not a code bug
- priority: low
- created: 2026-09-06 by Claude (per Javier)
- context: `djinn-penelope-usbip-watch.service` keeps Penelope's USB (shared from Typhon via usbipd-win) attached over Tailscale. It's been failing every 5-minute timer fire since Typhon's Windows reinstall (2026-06-25) left it unreachable for this purpose — confirmed again 2026-09-06 (`ssh typhon@100.69.41.74 usbip attach -r 100.69.41.74 -b 2-4` fails, `Active: failed` in `systemctl --user status`). This is expected/known, not something to fix on the Salomon side — see [[machines/TF-TTHQ]] for Typhon's onboarding status.
- **Next step:** once Typhon's reprovisioning is far enough along that its usbipd-win share for Penelope's USB is actually live again, re-check this service: `systemctl --user status djinn-penelope-usbip-watch.service` and `systemctl --user list-units --failed`. If it still fails at that point, it's a real bug worth diagnosing properly rather than the expected external-dependency block it is right now.
