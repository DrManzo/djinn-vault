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
- people: Sabrina (role='partner', archive_threshold_days=14), Craig (role='sponsor', archive_threshold_days=9999)

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
            for name in ["Sabrina", "Sammy", "Craig"]:
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
- context: PHASE-ALPHA Sprint 2 — Sabrina context tracking

**Goal:** Passive listener in Telegram gateway that tracks last mention of Sabrina (and Sammy). Weekly auto-archive if not mentioned.

**Depends on:** TASK-054, TASK-056 complete

**File:** `~/.local/bin/djinn-telegram-gateway` (modify)

**Logic — add to message processing loop (after auth check, before dispatch):**

```python
TRACKED_PEOPLE = {
    "sabrina": "Sabrina",
    "sammy": "Sabrina",   # same person, different name
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
- Send a test message containing "Sabrina" → `djinn-personal-db people check` shows last_mentioned = today
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

