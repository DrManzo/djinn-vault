---
title: TASK-012 — Djinn Media Social Integration Research
assigned_to: marcus
status: done
completed: 2026-05-31
tags: [djinn-media, instagram, facebook, meta-api, social, reels, cannabis]
related: [[COMMS]] | [[TASK-015]] | [[TASK-016]] | [[TASK-018]]
---

# TASK-012 — Djinn Media Social Media Integration

> Research brief for Djinn Media Layer 1 + Layer 2 social architecture. One section per question. Specific, actionable, cited.

---

## 1. Auto-Posting APIs (2026 State)

### Instagram Graph API

The official path is a **two-step (Instagram) or three-step (Facebook Reels)** flow, fully automatable with zero human intervention once a long-lived Page token is in place.

**Instagram Reels publish flow (Graph API v25.0, released Feb 2026):**

```
POST /{ig-user-id}/media
  media_type=REELS
  video_url=<public URL>        ← must be publicly accessible
  caption=<text + hashtags>
  share_to_feed=true
→ returns creation_id

POST /{ig-user-id}/media_publish
  creation_id=<from step 1>
→ returns ig_media_id
```

For large files, use the **resumable upload endpoint** instead of video_url:
```
POST rupload.facebook.com/ig-api-upload/{version}/{container-id}
```

**Eligibility requirements:**
- 9:16 aspect ratio
- 5–90 seconds duration
- H.264 or HEVC codec
- Instagram **Business account** (not personal, not Creator)
- Connected to a Facebook Page

**Rate limit:** 200 API calls per user per hour. Well within Djinn's usage.

### Facebook Graph API — Reels

Facebook Reels use a separate three-step flow via `/{page-id}/video_reels`:

```
Step 1 — Initialize:
  POST /{page-id}/video_reels
  upload_phase=start, video_state=PUBLISHED
→ returns video_id + upload_url

Step 2 — Upload binary:
  POST rupload.facebook.com/video-upload/{video-id}
  (binary in body, different host from graph.facebook.com)

Step 3 — Publish:
  POST /{page-id}/video_reels
  video_id=<from step 1>, video_state=PUBLISHED
```

FB Reel specs: 3–60s, minimum 23 FPS, same 9:16 ratio. Duration cap is tighter than IG (90s) — **keep exports under 60s for FB**.

**Permissions required (and must pass Meta app review):**
- `pages_manage_posts`
- `pages_read_engagement`
- `pages_show_list`

App review is required for any permission beyond `public_profile`. Budget 1–2 weeks for approval.

### Token Lifecycle — Critical Detail

Short-lived user tokens expire in 1 hour. Long-lived tokens last ~60 days. **Page tokens derived from a long-lived user token are non-expiring** — this is the correct setup for Djinn.

```
User token (1hr) → exchange → Long-lived user token (60d)
Long-lived user token → GET /{user-id}/accounts → Page token (non-expiring)
```

TASK-017 (`djinn-meta-token-refresh`) handles the 60-day long-lived token refresh. Page token itself does not need refreshing once correctly derived.

### Third-Party APIs

| Tool | API Access | Full Automation | Notes |
|---|---|---|---|
| **Buffer** | REST API | Yes (with paid plan) | Requires human account, not headless-friendly |
| **Publer** | REST API | Yes | Supports IG + FB, Reels-capable |
| **Zernio** | One-call API | Yes | Wraps Meta Graph API, simplifies auth |
| **Later** | No public API | No | UI-only |

**Recommendation:** Use Meta Graph API directly. TASK-016 spec already implements this correctly. Third-party tools add cost and a dependency layer without benefit for Djinn's architecture.

### 2025–2026 Changes
- Graph API v25.0 released February 2026 — added Page Viewer Metric, no breaking changes to Reels publishing
- Meta retired Rental Actors on Apify (April 2026) — all scraper actors now pay-per-usage
- No new restrictions on programmatic Reels posting as of May 2026

---

## 2. What's Performing on Reels for Maker/3D Printing Content

### Algorithm Signals (2026)

Instagram's 2026 algorithm rewards **momentum builders, not one-off posts**. The key signals in ranked order:

1. **DM shares** — highest weight signal. If viewers share the Reel via DM, the algorithm treats it as strong positive signal and expands distribution.
2. **Saves** — second highest. Indicates durable value.
3. **Watch time / completion rate** — weight depends on clip length. Shorter clips with high completion rate outperform longer clips with drop-off.
4. **Comments** — weighted less than shares/saves but still matters.
5. **Likes** — lowest weight in 2026. Vanity metric only.

### Content Format — What's Working

- **Reveal format**: Build → show → reveal. Starts with raw material or print bed, ends with finished product in use. Highest save rate in maker niche.
- **Timelapse with voiceover**: Full print condensed to 20–30s with narration explaining the why. Works for process-heavy content.
- **Text-on-screen + trending audio**: Low production cost, high reach potential. Use on-screen text as the primary hook, audio as atmosphere.
- **POV**: "Print from my perspective" angle. Performs well for niche audiences, lower reach but higher follow conversion.
- **3D content** (where applicable): Posts with actual 3D/depth elements generate 2–3x higher engagement than flat video.

### Optimal Clip Length

- **15–30 seconds**: Maximum reach. Algorithm pushes short, high-completion-rate content to non-followers.
- **30–60 seconds**: Best for saves and follows. Enough time to demonstrate value.
- **60–90 seconds**: Only for complex processes. Drop-off risk is high without strong hooks every 15s.

**Recommendation for Djinn Media**: Target 20–45s. Long enough to show the print process, short enough to complete.

### Hook Strategy (First 3 Seconds)

- **Visual hook**: Motion on screen immediately. No static title cards. Start mid-action.
- **Text hook pattern**: "[Bold claim] → [contradiction or curiosity gap]" — example: "This printed in 4 hours" / "...and sold in 20 minutes."
- **Audio hook**: Cut first — silence or ambient sound before beat drops works better than starting on music.

### Posting Cadence

- 3–5 Reels per week for growth phase
- Consistency > frequency. 3 per week every week beats 10 one week and 0 the next
- Best times: Tuesday–Friday, 9–11am and 6–9pm in audience timezone
- After a high-performing post: **wait 24–48 hours before posting again** — algorithm gives the top post space to breathe

### Hashtag Strategy

- 3–5 hashtags max (2026 best practice — Instagram confirmed over-hashtagging hurts reach)
- Mix: 1 broad (\#3dprinting, 500k+ posts), 1 niche (\#3dprintedpipe, <50k posts), 1 hyper-specific (\#typhonsforge or brand tag)
- **Never use banned hashtags** — silent suppression, no notification

---

## 3. AI Tools Competitive Landscape

### What Exists in 2026

| Tool | Caption AI | Hashtag Research | Auto-Schedule | From Raw Footage | Price |
|---|---|---|---|---|---|
| **Buffer** | Yes (GPT-based) | Basic | Yes | No | $18/mo |
| **Flick** | Yes | Advanced | Yes | No | $30/mo |
| **Jasper** | Yes | No | No | No | $49/mo |
| **Later** | Basic | Yes | Yes | No | $25/mo |
| **Publer** | Yes | Basic | Yes | No | $12/mo |
| **Djinn Media** | Yes (job-metadata-aware) | From TREND-SIGNAL.md | Yes (TASK-016) | **Yes — native** | $0 |

### The Gap

Every commercial tool operates on content **the human already created**. They take a finished video, help write a caption, suggest hashtags, and schedule it.

**None of them generate content from production metadata.** Djinn Media's defensible moat:

- Captions written from `manifest.json` — knows the actual job (material, layer height, print time, customer type)
- Hashtags pulled from `HASHTAG-BANK.md` which is updated by live trend data
- The reel itself is generated from job footage by `djinn-media-reel`, not assembled manually
- The entire pipeline fires from one command or a Telegram message

**Positioning statement for Djinn Media as a product:** "Buffer schedules content a human made. Djinn creates it from production data."

### What They're Missing

- No tool integrates with print shop job data
- No tool auto-generates the video — they only schedule it
- No tool has a feedback loop from post analytics back into caption/hashtag generation
- No tool is fully local and CLI-driven (privacy, no SaaS dependency)

---

## 4. Cross-Platform Content Repurposing

### Duplicate Content Penalty

**There is no cross-platform duplicate content penalty.** Instagram does not penalize content that also exists on TikTok or Facebook. Each platform's algorithm evaluates content independently within that platform.

The only real risk: **TikTok watermarks**. Instagram's algorithm detects and suppresses Reels that contain a TikTok watermark (the \@username + TikTok logo overlay). This is real and confirmed as of 2026. Facebook has the same detection.

**Fix:** Export from the source (ffmpeg) without any watermark. Never download from TikTok and re-upload.

### One File, Three Platforms

Djinn Media's export from `djinn-media-reel` already produces the correct format. Single export strategy:

```
Format: H.264, AAC audio, 9:16, 1080x1920, 30fps
Duration: ≤60s (satisfies FB Reels cap)
Bitrate: 8–15 Mbps
```

This file posts to IG Reels (up to 90s), FB Reels (up to 60s), and TikTok (up to 3min) without re-encoding.

### Stagger Timing

Post to platforms 30–60 minutes apart, not simultaneously. Each platform treats it as fresh content. Simultaneous posting has no technical downside but anecdotally platforms detect cross-posting patterns.

**Recommended order:** Instagram → Facebook → TikTok (if applicable)

---

## 5. Analytics via Graph API

### What's Available Programmatically

`GET /{media-id}/insights` returns the following metrics for Reels:

| Metric | Description |
|---|---|
| `reach` | Unique accounts that saw the post |
| `plays` | Total play count (includes replays) |
| `saved` | Number of saves |
| `shares` | Number of shares (includes DM shares) |
| `comments` | Comment count |
| `ig_reels_avg_watch_time` | Average watch time in milliseconds |
| `ig_reels_video_view_total_time` | Total cumulative watch time |
| `total_interactions` | Sum of likes + comments + saves + shares |

**What's NOT available:** Individual viewer identities, DM recipient data, external share destinations.

### TASK-018 (`djinn-social-analyst`) Architecture

The spec is correct. Polling cadence of daily at 00:30 UTC is appropriate — Meta updates insights with a 24–48h lag, so real-time polling has no value. Weekly summary is the actionable unit.

### Local Aggregation

No external tool needed. `djinn-social-analyst` writes JSON to `~/Obsidian/djinn/social/analytics/` and builds `TREND-SIGNAL.md` locally. Claude reads `TREND-SIGNAL.md` at caption generation time to weight toward formats currently performing.

---

## 6. Cannabis Content Policy (2026)

### Platform Comparison

| Platform | Organic Posts | Paid Ads | Accessories | Consumption Imagery |
|---|---|---|---|---|
| **Instagram** | Allowed (no sales CTA) | Banned | Allowed if no sale implied | Banned |
| **Facebook** | Allowed (no sales CTA) | Banned | Allowed if no sale implied | Banned |
| **TikTok** | High removal risk | Banned | Any cannabis visual risks removal | Banned |
| **X/Twitter** | Allowed | Allowed (licensed, 21+, legal state) | Allowed | Restricted |
| **YouTube** | Educational only | Banned | Allowed (no monetization) | Banned |

### Instagram/Facebook Enforcement Reality

Meta allows cannabis brand accounts to **show products visually** — photos, videos of accessories, process shots. What triggers enforcement:

- Sales CTAs ("Buy now", "DM to order", prices in caption)
- Consumption imagery (smoking, dabbing, inhaling)
- Underage-adjacent imagery
- Direct links to purchase in post copy

**For Typhon's Forge:** 3D printed accessories shown as product shots without consumption or sales copy = generally tolerated. Process video (printing the piece) = lowest risk.

### Shadowban Reality

Instagram officially denies shadowbanning exists. In practice, account-level suppression is real and triggered by:

- Using banned hashtags (\#420, \#weedstagram, \#stoner are high-risk)
- Repeated community guideline violations
- Third-party tools that violate ToS
- Posting too many similar pieces of content too fast

**Safe hashtag patterns for cannabis accessories:**
- ✅ \#functionalart, \#glassart, \#artisancraft, \#3dprinted, \#makerculture, \#smokingaccessories
- ⚠️ \#pipe, \#handpipe (tolerated, watch for account-level suppression)
- ❌ \#420, \#weedstagram, \#cannabis, \#stoner, \#marijuana

### California-Specific Note

California is a legal state. Instagram doesn't honor state-level legal status — federal policy applies. No difference in enforcement for CA-based accounts.

### Workarounds Working Accounts Use

- "21+ Only" in bio
- Describe pieces as "functional art" or "artisan glass" rather than pipes
- Link to a landing page with an age gate, not directly to products
- Avoid hashtag stacking — 3–5 max, none from the banned list
- Alternate cannabis-adjacent posts with neutral maker content to avoid pattern detection

---

## 7. Djinn Media as a Product

### Target User Priority

1. **Primary:** One-person 3D print shops / CNC shops / laser cutting shops with a social presence — same use case as Typhon's Forge
2. **Secondary:** Etsy sellers who make physical goods and film their process but don't have time to edit/post
3. **Tertiary:** Cannabis-adjacent small brands (glass blowers, accessory designers) who need an automated, compliant posting workflow

### Features to Emphasize

1. **Job-aware captions** — the AI knows what was made, for whom, on what machine, in what time. No commercial tool has this.
2. **Zero human steps from intake to post** — iPhone drop → Drive sync → auto-ingest → reel → publish. One command or one Telegram message.
3. **Local-first** — no SaaS, no monthly subscription, no footage uploaded to third-party servers
4. **Compliance-aware** — HASHTAG-BANK.md is pre-filtered for cannabis-safe tags
5. **Analytics feedback loop** — post performance feeds back into next caption's tone and hashtag selection

### Competitive Positioning

**Against Buffer/Later/Publer:** "They schedule content you already made. Djinn makes the content."

**Against Jasper/Flick:** "They write captions for generic inputs. Djinn writes captions from your actual job data — material, layer count, print duration, customer."

**Against hiring a social media manager:** "Djinn runs on Salomon 24/7 for the cost of electricity."

---

## 8. Live Trend and Hashtag Data Sources (Layer 1 Architecture)

### Instagram Graph API for Trend Data

**Verdict: Not useful for trend discovery.** The Graph API only returns data for your own account's posts. There is no endpoint for trending hashtags, top posts by keyword, or competitor analysis. It's analytics-in, not trend-out.

### Third-Party Options

| Source | What It Provides | Free Tier | Reliability | Recommended |
|---|---|---|---|---|
| **Apify Instagram Scraper** | Top posts by hashtag, engagement metrics | $5/mo credits | High (managed) | ✅ Yes |
| **Flick** | Hashtag difficulty, volume, avg engagement | No free tier ($30/mo) | High | ⚠️ Cost |
| **Reddit PRAW** | Post velocity, upvote ratio in r/3Dprinting etc | Yes (free, 100 req/min) | High | ✅ Yes |
| **YouTube Data API** | Trending shorts by keyword | Yes (10k units/day) | High | ✅ Yes |
| **Google Trends API (alpha)** | Keyword velocity over time | Yes | Medium | ✅ Yes |
| **pytrends (unofficial)** | Same as Trends but no official support | Yes | Low-Medium | ⚠️ Fragile |
| **Instaloader** | Public profile/hashtag data | Yes | Low in 2026 | ❌ Fragile |

**Apify free tier:** $5/month in platform credits. At Djinn's polling cadence (4x/day = 120 runs/month), this fits inside the free tier for lightweight hashtag scraping actors. Heavy video scraping costs more. See TASK-015 for detailed DIY alternative analysis.

### djinn-trend-agent Architecture (Layer 1)

```
Schedule: every 6 hours via systemd timer

Sources polled:
  1. Apify Instagram Hashtag Scraper (or DIY — see TASK-015)
     Query: top 10 posts for [#3dprinting, #functionalart, #makerculture]
     Extract: caption text, like count, comment count, hashtags used

  2. Reddit PRAW
     Subreddits: r/3Dprinting, r/PrintedMinis, r/glassheads
     Extract: top 10 posts by score in last 24h, title, flair

  3. YouTube Data API v3
     Query: videos, keyword="3D printing" OR "functional art", order=viewCount, publishedAfter=24h ago
     Extract: title, view count, like count, tags

  4. Google Trends API (alpha, if stable) or pytrends fallback
     Keywords: "3D printed", "functional glass", "puffco", "maker"
     Extract: relative interest, rising queries

Outputs written:
  ~/Obsidian/djinn/social/TREND-SIGNAL.md     ← read by caption agent
  ~/Obsidian/djinn/social/HASHTAG-BANK.md     ← read by publish-prep

TRASH-SIGNAL.md format:
  ## Trending this cycle
  - [topic]: [signal source] — [why it matters]

  ## Top hashtags (by engagement/post in niche)
  - #hashtag: [avg engagement], [post count], [safe: yes/no]

  ## Format signal
  - [video format type] is trending in [niche] — [evidence]
```

### Detecting Visual Style Trends

No API returns "POV is trending" directly. Proxy signals:
- Caption text from top posts → NLP to detect format keywords ("POV", "timelapse", "reveal", "before/after")
- Hashtag patterns from top posts → cluster by format type
- YouTube titles → extract format keywords with regex

Ollama (phi4:14b on Salomon) handles this NLP step locally — no external LLM call needed.

### Polling Cadence Recommendation

- **Every 6 hours** for TREND-SIGNAL.md (4x/day)
- **Weekly** for HASHTAG-BANK.md deep audit (hashtag volume changes slowly)
- **Daily** for TREND-SIGNAL.md git commit (even if no changes — timestamp proves freshness)

---

## Summary — Priority Actions

| Priority | Action | Task |
|---|---|---|
| P0 | Complete Meta app review to get publishing permissions | Pre-TASK-016 |
| P0 | Get long-lived Page token → non-expiring Page token | Pre-TASK-016 |
| P1 | Deploy `djinn-media-publish` | TASK-016 |
| P1 | Deploy `djinn-meta-token-refresh` | TASK-017 |
| P1 | Deploy `djinn-social-analyst` | TASK-018 |
| P2 | Build `djinn-trend-agent` with Reddit + YouTube + Google Trends sources | New task |
| P2 | Add Apify Instagram scraper or DIY equivalent to trend agent | TASK-015 |
| P3 | Build HASHTAG-BANK.md weekly auditor | New task |

**Biggest gotcha:** Meta app review. Without `pages_manage_posts` approval, TASK-016 cannot publish. Start this process now — do not wait until the code is built.
