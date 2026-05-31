---
title: Djinn Task Queue
updated: 2026-05-31
tags: [djinn, queue, delegation]
related: [[COMMS]] | [[PROTOCOL]] | [[build-log]]
---

# QUEUE — Djinn Task Queue

Claude (or Javier) writes tasks here. Salomon and Typhon pull and execute.

## Rules
- **Append only** — never delete entries. Mark `status: done` or `status: failed`.
- `trigger: auto` — runner picks up on next poll (cron every 5 min)
- `trigger: manual` — runner skips; Javier must send explicit signal
- Runner: `djinn-queue-runner` on Salomon and Typhon
- On completion: runner calls `djinn-task-complete TASK-NNN "summary"` automatically

## Task Format

```
## TASK-NNN
- assigned_to: salomon | typhon
- status: pending | in_progress | done | failed
- priority: critical | high | normal | low
- trigger: auto | manual
- created: YYYY-MM-DD by Claude|Javier
- context: one-line description of what and why

**Commands:**
```bash
command one
command two
```
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
- status: pending
- priority: high
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Deep research brief — Djinn Media social media integration opportunities

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
- status: pending
- priority: high
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Research — can we replace Apify + Flick with a self-built zero-cost trend intelligence stack? No subscriptions, Djinn maintains it.

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
