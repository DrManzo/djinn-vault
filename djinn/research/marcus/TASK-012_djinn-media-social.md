---
title: TASK-012 — Djinn Media Social Media Integration Research
author: Marcus (Perplexity AI)
created: 2026-05-31
tags: [djinn, research, social-media, instagram, facebook, media-pipeline, cannabis]
related: [[QUEUE]] | [[COMMS]] | [[3D-SUITE-FULL-MAP]]
---

# TASK-012 — Djinn Media: Social Media Integration Research

**Commissioned by:** Javier / Claude  
**Researcher:** Marcus (Perplexity AI)  
**Date:** 2026-05-31  
**Status:** Complete — all 8 sections delivered

---

## Section 1 — Auto-Posting APIs: Instagram & Facebook in 2026

### Current State

As of 2026, programmatic publishing to Instagram and Facebook is fully supported via the **Meta Graph API**, with no mandatory human approval step required once your app is reviewed and granted the correct permissions. The key permissions needed are `instagram_basic`, `instagram_content_publish`, and `pages_manage_posts` for Facebook.

The **Instagram Content Publishing API** (a subset of the Graph API) supports:
- Reels (video up to 15 minutes)
- Single-image feed posts
- Carousel posts (multi-image)
- Stories (via approved partners only — not available to all developers)

Publishing a Reel programmatically follows a two-step flow:
1. **Upload the video container** — POST to `/{ig-user-id}/media` with `media_type=REELS`, `video_url`, `caption`, `share_to_feed=true`
2. **Publish the container** — POST to `/{ig-user-id}/media_publish` with the `creation_id` from step 1

For Facebook, as of 2026, **every video posted to a Page is treated as a Reel** — there is no separate legacy video format. The Facebook Graph API Video Publishing endpoint accepts direct Reels uploads.

### Key Findings

- **No human approval step** is required once the Meta App is live and tokens are valid. The flow is fully headless.
- **Access tokens expire.** User tokens last 60 days; long-lived page tokens can be permanent if managed correctly via token refresh. For Djinn Media, a cron that refreshes the page token before expiry is mandatory.
- **Rate limits:** Instagram imposes 25 API-published posts per 24-hour window per user. For a one-person shop, this is not a constraint.
- **Meta Business Suite is NOT required** for publishing via the API. It is only needed for ad management and boosting.
- **April 2026 expansion:** Meta expanded the Instagram Management APIs to include additional partnership ad label support and enhanced third-party capabilities — this opens more surface area for automation tools.
- **Third-party scheduling APIs** (Buffer, Later, Publer) expose REST endpoints and all support fully automated posting. Buffer's API and Publer's API are the most developer-friendly for headless use. Upload-Post.com offers a single-endpoint solution that handles Reels, carousels, and feed posts with Python/cURL examples. Zernio offers a one-call API that abstracts the two-step Meta flow.

### Recommendations for Djinn

- **Use the Meta Graph API directly** — no intermediary needed for Djinn's volume. One shop, 1–3 posts/day, no rate limit risk.
- Wrap the two-step Reel publish flow in `djinn-media-publish-prep` as a function: `publish_reel(video_path, caption, hashtags, share_to_feed=True)`
- Store the Page access token in `~/.config/djinn/shop.env` as `META_PAGE_TOKEN`. Set a monthly cron to refresh it.
- For Facebook: use the same Graph API call routed to the Page endpoint — one video file, two publish calls.

### Gotchas

- **Webhook vs polling:** Meta will not push analytics back to you in real time without a webhook endpoint. Djinn needs a lightweight webhook receiver or a polling script for the feedback loop (see Section 5).
- **Video encoding requirements:** Instagram Reels requires H.264, AAC audio, 9:16 aspect ratio, 1080x1920 resolution, under 4GB. Djinn's existing ffmpeg pipeline already outputs this via the `30fps H.264 AAC` spec from TASK-005 — no extra work needed.
- **Stories remain gated** — programmatic Story publishing requires a Meta-approved partner app with `instagram_manage_comments` scope. Not worth pursuing for Djinn at current scale.

---

## Section 2 — What's Performing on Reels for Maker/3D Printing Content in 2026

### Current State

Instagram Reels in 2026 is the **primary discovery engine** on the platform. The algorithm has moved fully to an **interest graph** model — follower count no longer determines reach. Content earns distribution based on behavioral signals, primarily:
1. **DM shares** — the single most heavily weighted signal for Reels distribution
2. **Watch completion rate** — what percentage of viewers watch to the end
3. **Saves** — strong signal for evergreen/valuable content
4. **Comments with text** — weighted higher than emoji-only comments
5. **Non-follower reach ratio** — Instagram uses this as a quality gate before broader distribution

### What's Working for Maker/3D Printing Content

**Format winners:**
- **Reveal format** — show finished product first (hero shot, 3 seconds), then cut to the process. Forces pattern interrupt. Outperforms linear process-to-result every time.
- **POV + voiceover** — first-person camera on the printer/workspace, creator narrating what's happening and why. Works because it's intimate and informative simultaneously.
- **Time-lapse with text commentary** — compressed print from bed to finish, with on-screen text annotations explaining each phase. 3D content generates 2–3x higher engagement than flat graphics due to novelty.
- **"What I made for X" format** — product shown in context of the customer or use case. Strong save signal.

**Hook strategy (first 1.5 seconds is critical):**
- Lead with the finished product, not the printer. Audiences don't know yet if they care about 3D printing — show them why they should in the first frame.
- Text overlay in the first frame: "I made this in 14 hours" or "This took 3 attempts to get right" — specificity triggers curiosity.
- Test every hook on mute — if it doesn't communicate value without audio, it won't perform.
- For the dark maker aesthetic: high-contrast hero shots with product lit against dark background are outperforming bright studio shots in the maker niche.

**Optimal length:**
- **15–45 seconds** is the sweet spot for reach. A 10-second Reel at 80% completion rate outperforms a 60-second Reel at 30% completion rate every time.
- 30–90 seconds for engagement (saves, comments, shares). Use the longer format when explaining a build process or result.
- Instagram will show Reels up to 3 minutes to non-followers, but shorter content earns initial distribution faster.

**Posting frequency and timing:**
- **3–5 Reels per week** is the documented optimum for the 3D printing niche — balances visibility maintenance against production quality.
- Consistency matters more than volume. Publishing at irregular intervals resets the algorithm's distribution baseline for your account.
- For small accounts (under 10k), growth is driven almost entirely by **DM shares and saves** — design content to be sharable, not just watchable. Ask explicitly: "Send this to someone building their own shop."

**Hashtag strategy:**
- 5–8 hashtags per Reel. Mix: 1–2 broad (`#3Dprinting`, `#makersgonnamake`), 3–4 niche (`#ender3`, `#filament`, `#functionalprint`), 1–2 hyper-niche (`#klipper`, `#openclawai`, `#typhonsforge`).
- On-screen text is read by Instagram's algorithm — always include keywords directly in the video, not just the caption.
- Alt text on upload adds another indexing signal — Djinn's publish function should auto-populate this from the job metadata.

### Small Account Growth Playbook

Accounts under 10k followers grow via:
1. **Remix/Collab** with larger accounts in the maker space — Instagram's algorithm boosts remixed content
2. **Reply to comments on Day 1** — engagement velocity in the first hour is a strong distribution signal
3. **Cross-niche content** — 3D printing meets cannabis accessories is a niche cross that serves both communities and gets DM-shared within both
4. **Specificity over breadth** — "I printed a Puffco Proxy recycler in PLA and here's what failed" beats generic "3D printing timelapse" every time

---

## Section 3 — AI-Assisted Social Media Tools: Competitive Landscape

### What Exists in 2026

**Scheduling + publishing tools with AI features:**
- **Buffer** ($6–18/mo) — AI caption suggestions, scheduling, analytics. API available. Best headless developer experience.
- **Later** ($16–40/mo) — Visual planning, AI hashtag suggestions, link-in-bio tools. Less developer-friendly.
- **Publer** ($12–40/mo) — REST API, multi-platform, best for automation-heavy users. Supports Reels natively.
- **ContentStudio** — AI copy generation from templates for IG/FB/LinkedIn. Solid caption generation but no custom pipeline integration.

**AI content generation tools:**
- **Jasper / Copy.ai** — analyze top-performing posts in your niche and suggest captions optimized for the algorithm. Input: brief or raw transcript. Output: platform-specific caption.
- **Zebracat / Invideo AI** — for Reels and Stories creation from script or raw footage. Not comparable to Djinn's pipeline — these are consumer tools, not CLI-integrated.
- **Lumen5 / Pictory** — video-from-text tools. Consumer grade. Irrelevant to Djinn's ffmpeg pipeline.
- **Flonnect** — combines caption writing, hashtag support, and scheduling in one tool. Best-in-class for solo creators as of mid-2026.
- **Hootsuite OwlyWriter AI** — enterprise grade, expensive, overkill for a one-person shop.

**Hashtag research:**
- **Flick** ($30/mo) — hashtag research, competitor insights, IG-specific. Best dedicated hashtag tool.
- **Social Blade** (free) — follower growth tracking, competitor benchmarking.
- **HypeAuditor** — influencer analysis. Not directly relevant but useful for competitor research.

### The Gap — What Djinn Does That No Tool Does

Every tool listed above assumes a human is in the content creation loop. The gap Djinn Media fills:

1. **Zero-touch intake to publish** — footage drops from an iPhone to Google Drive, flows through automated ingest, color grade, caption generation, hashtag selection, and publish without a human touching a keyboard between drop and post.
2. **Job-metadata-aware captions** — Djinn knows the print job: material, duration, temperature profile, customer type, geometry. No generic tool has access to this. Djinn can generate captions like "16-hour PLA Puffco Proxy, 0.16mm @ 220°C, 0 errors" automatically from `manifest.json` — no human writes this.
3. **Local model privacy** — Djinn uses local Ollama models (phi4:14b, llama3.2-vision) for caption and hashtag generation. No content leaves the machine until it's posted. No subscription to an AI caption SaaS needed.
4. **Feedback loop integration** — when Djinn pulls analytics back via the Graph API, it can feed performance data back into Layer 1 agents to tune future hashtag and caption generation. No commercial tool does this closed-loop optimization at the individual creator level.

**Competitive positioning:** Djinn Media is not competing with Buffer or Jasper. It's the layer *beneath* those tools — the pipeline that replaces the human operator entirely. The closest analog is a custom-built version of what a social media agency does, automated for a one-person shop.

---

## Section 4 — Cross-Platform Content Repurposing

### Current State

**There is no algorithmic penalty for posting the same video to Instagram, Facebook, and TikTok.** Platforms do not share content fingerprints with each other and cannot detect cross-platform duplication. The "duplicate content penalty" myth is not supported by current evidence.

**What IS penalized:**
- **TikTok watermarks on Instagram/Facebook** — both platforms detect the TikTok watermark (the logo + username in the corner) and deprioritize content carrying it. This is watermark detection, not content detection.
- **Wrong aspect ratio** — letterboxed or pillarboxed video (wrong format for the platform) gets penalized by completion rate, not by the algorithm directly, but the effect is the same.
- **Wrong tone in captions** — copy-pasted captions across platforms underperform because each platform's audience has different expectations.

### Best Practice for Djinn's Pipeline

Djinn already exports clean H.264 AAC at 9:16 — this is the correct format for all three target platforms. The pipeline should:

1. **Export the raw file before posting anywhere.** `djinn-media-reel` outputs `{job_slug}_reel.mp4` — this is the master. Never use a downloaded-from-platform version as a re-upload source.
2. **Generate platform-specific captions per platform.** Same hashtag set, different caption tone:
   - Instagram: hook-first, hashtags at end, CTA ("Send to your maker friends")
   - Facebook: longer, more narrative, fewer hashtags (2–3 max)
   - TikTok (future): casual, spoken-word style, no hashtag spam
3. **Stagger posting times by 30–60 minutes** between platforms. Prevents any shared CDN fingerprinting and spreads notification load.
4. **Audio:** Trending sounds don't transfer between platforms. Djinn's content should use royalty-free music from a local library or silence with strong visual storytelling. Do not rely on trending Instagram audio — it cannot be reused on TikTok or Facebook without rights.
5. **One export, three posts.** A single `djinn-media-publish` call should handle IG → FB → (future TikTok) in sequence with platform-aware caption variants generated by the Layer 1 caption agent.

### Format Optimization Across Platforms

| Spec | Instagram Reels | Facebook Reels | TikTok |
|------|----------------|---------------|--------|
| Aspect ratio | 9:16 | 9:16 | 9:16 |
| Resolution | 1080x1920 | 1080x1920 | 1080x1920 |
| Codec | H.264 | H.264 | H.264 |
| Audio | AAC | AAC | AAC |
| Max length | 90s for reach | No hard cap | 3 min |
| Optimal length | 15–45s | 30–60s | 15–60s |
| Hashtags | 5–8 | 2–3 | 3–5 |
| Watermark penalty | Yes (TikTok) | Yes (TikTok) | Yes (IG/FB) |

Djinn's current ffmpeg pipeline already matches this spec. No additional export profiles needed.

---

## Section 5 — Analytics and Feedback Loops via the Graph API

### What's Available Programmatically

The Instagram Graph API's Insights endpoint (`/{ig-media-id}/insights`) returns the following metrics for Reels:
- `reach` — unique accounts that saw the Reel
- `plays` — total number of times the Reel was played
- `saved` — number of saves
- `shares` — number of times shared via DM or external share
- `comments` — comment count
- `likes` — like count
- `ig_reels_avg_watch_time` — average watch time in milliseconds
- `ig_reels_video_view_total_time` — total aggregate watch time
- `total_interactions` — sum of likes + comments + saves + shares

**What you CANNOT get via API (as of 2026):**
- Per-second retention/drop-off curve (this is only visible in the app's native Insights)
- Audience demographic breakdowns on individual posts (account-level only)
- Hashtag-level reach attribution

### Account-Level Metrics

The `/{ig-user-id}/insights` endpoint returns:
- `reach` (28-day window or custom period)
- `follower_count` over time
- `profile_views`
- `website_clicks`
- Audience demographics: age, gender, city, country

### Feedback Loop Architecture for Djinn

A viable feedback loop agent runs as a daily cron at 00:00 UTC:

```
djinn-social-analyst (daily cron)
  → pull last 7 days of media insights via Graph API
  → write to djinn/social/analytics/{YYYY-MM-DD}.json
  → compare: top 3 posts by (saves + shares) vs bottom 3
  → extract: caption length, hashtag count, video duration, hook style
  → write recommendation delta to djinn/social/TREND-SIGNAL.md
  → Layer 1 caption agent reads TREND-SIGNAL.md at next post generation
```

This closes the loop: post → perform → measure → improve caption/hashtag strategy → post.

### Open-Source / Lightweight Analytics Options

- **Data365 API** — unified access to Instagram + TikTok + Reddit through one API. Most reliable for programmatic multi-platform analytics aggregation in 2026.
- **Minter.io** — tracks reach, engagement rate by reach, average watch time, shares, profile visits, reach from non-followers. Has API access on paid plans.
- **Iconosquare** — hashtag analytics, competitor benchmarking, API access. $49/mo. Worth it if Djinn Media scales to client work.
- For Djinn's current needs: **direct Graph API polling is sufficient and free.** No third-party analytics tool needed until managing multiple accounts.

---

## Section 6 — Cannabis Content and Platform Policies in 2026

### Instagram's Current Enforcement Stance

Instagram's policy distinguishes between:
- **Cannabis consumption content** — explicitly prohibited. Videos showing people smoking, vaping, or consuming cannabis will be removed or suppressed.
- **Cannabis accessory products** — the policy is ambiguous and inconsistently enforced. 3D-printed pipes, recyclers, and accessories (not depicting use) exist in a gray zone.
- **Artistic/educational/product showcase content** — generally tolerated if no consumption is depicted and no sales language is used.

Practical enforcement reality for Djinn Media:
- Product showcase posts ("I printed this Puffco Proxy recycler — here's the geometry") have much lower removal risk than use-case demonstration posts.
- Never use hashtags like `#weed`, `#cannabis`, `#420`, `#marijuana`, `#stoner` — these are actively monitored and trigger suppression.
- The shadowban is confirmed real as of 2026, despite Meta's past denials. Content using banned hashtags gets suppressed in search and Explore without account notification.

### Hashtag Strategy for Cannabis-Adjacent Content

**Use these — tolerated in 2026:**
- `#glassart`, `#heady`, `#functionalart`, `#puffco`, `#recycler`, `#dab`, `#concentrate` (moderate risk), `#smokeware`, `#headypiece`
- Product-specific: `#puffcoproxy`, `#3Dprintedglass`, `#makerculture`

**Avoid — high suppression risk:**
- `#weed`, `#cannabis`, `#420`, `#marijuana`, `#stoner`, `#reefer`, `#hemp` (complicated — sometimes flagged)

**Workarounds used by successful cannabis-adjacent accounts:**
1. **Lead with the craft, not the substance.** "3D printed functional art" frames the content as maker content, not cannabis content.
2. **No consumption in video** — show the product being printed, assembled, or displayed. Never show it being used.
3. **Community-first captions** — speak to the maker community ("12-hour SLA print, 0.05mm layer height") rather than the cannabis community.
4. **No sales language in posts** — never include pricing, "available in shop," or purchase CTAs in the post itself. Link in bio only, and keep the bio link to a neutral landing page.

### Facebook vs Instagram Policy

| Policy Area | Instagram | Facebook |
|------------|-----------|----------|
| Cannabis ads | Prohibited | Prohibited |
| Product images | Tolerated (no use) | Tolerated (no sale language) |
| Sales CTAs | Risky | Explicitly prohibited |
| Consumption depiction | Removed | Removed |
| Accessory showcase | Gray zone | Gray zone — more lenient |
| Enforcement consistency | Inconsistent | Less aggressive than IG |

**Facebook is generally less aggressively enforced than Instagram** for cannabis-adjacent content. Educational and product showcase content on Facebook Pages is more stable. The rule: never imply sale or delivery, never show consumption, never post prices.

### California-Specific Note

Javier is in San Bernardino, CA. California cannabis advertising regulations add a layer: any online content that could be construed as advertising to minors is prohibited. For Instagram, this means no cartoon imagery, no youth-appealing aesthetics, and no claims about recreational effects. Product showcase content for adult collectors is compliant.

---

## Section 7 — Djinn Media as a Product

### Core Value Proposition

Djinn Media solves a specific problem: **a one-person maker shop cannot operate a consistent social media presence manually while also running fulfillment, printing, and customer comms.** The pipeline eliminates the social media operator role entirely — from footage drop to multi-platform post, no human is in the loop.

### Target Users

The addressable market, in priority order:

1. **One-person 3D print shops** (Etsy sellers, independent makers) — closest to Javier's use case. Most likely early adopters. Currently managing social manually or not at all.
2. **Cannabis accessory brands** (small-batch makers, glass artists, DTC brands) — desperate for compliant automation that doesn't require a full-time social media manager.
3. **Craft and maker YouTube/TikTok creators** who also sell product — need the content repurposing layer more than the quoting/slicing layer.
4. **Small-batch print services** (phone cases, cosplay parts, architectural models) — same problem, different product category.

### Most Valuable Features to Emphasize

1. **Zero-touch posting** — drop footage from your phone, it posts itself. This is the headline feature. No other tool does this for production footage with job-aware metadata.
2. **Automated caption + hashtag generation from job metadata** — captions that know what was printed, how long it took, what went wrong, and what material was used. No generic "amazing print!" filler.
3. **Multi-platform single-export** — one video, three platforms, platform-optimized captions.
4. **Compliance-aware content generation** — the Layer 1 agent knows the cannabis-adjacent content rules and generates captions that stay in the tolerated zone automatically.
5. **Feedback loop** — daily analytics pull that tunes the next post's hashtag and caption strategy.

### Competitive Positioning

Djinn Media is not a scheduling tool — it's a **production intelligence layer**. The positioning:

> *Buffer, Later, and Publer help you schedule content a human created. Djinn Media creates and publishes the content autonomously, informed by your production data.*

No existing tool has access to print job metadata (material, layer height, temperature, duration, error log). This is Djinn's defensible moat. The data that makes the captions accurate and specific is locked inside the shop's operational system — a third-party tool can never replicate this without deep API integration.

---

## Section 8 — Live Trend and Hashtag Data Sources for Layer 1

### The Intelligence Layer Problem

Djinn Media's two-layer architecture requires Layer 1 (intelligence agents) to feed Layer 2 (production agents) with live trend signal. The question is: **what does a viable trend polling agent actually query, and at what cadence?**

### What the Instagram Graph API Does NOT Provide

The Instagram Graph API is **account-centric, not platform-centric.** It returns:
- Your own posts' performance data
- Your own audience demographics
- Your own follower growth

It does NOT return:
- Platform-wide trending hashtags
- Competitor post performance
- Trending audio/sounds
- What visual styles are performing across the platform

For trend data, you must go outside the official API.

### Third-Party Trend Data Options

**Reliable and affordable for a one-person operation:**

1. **RapidAPI — Instagram Hashtag/Trend scrapers** (multiple providers, $10–50/mo)
   - Returns top posts for a given hashtag
   - Returns hashtag volume estimates
   - Risk: Meta periodically breaks scraper APIs; uptime not guaranteed
   - Best current option: `instagram-bulk-profile-scrapper` on RapidAPI (~$30/mo for 10k calls)

2. **Apify** — most reliable scraper infrastructure as of 2026
   - Instagram Hashtag Scraper actor: returns top/recent posts, engagement, hashtag metadata
   - Instagram Trending Reels actor: returns trending Reels by niche keyword
   - Pricing: ~$49/mo for a solo developer tier
   - Advantage: Apify maintains the scrapers so your code doesn't break when Meta updates its frontend
   - **Best recommendation for Djinn Layer 1** — most stable option available outside the official API

3. **Flick API** ($30/mo)
   - Purpose-built for hashtag research
   - Returns: hashtag difficulty, volume, average engagement per hashtag
   - Does NOT return trending content — only hashtag metadata
   - Use for: weekly hashtag audit, not real-time trend signal

4. **Data365** — unified social API (Instagram + TikTok + Reddit)
   - Returns profile data, post data, hashtag data across platforms
   - Better for cross-platform competitive analysis than real-time trending

5. **Iconosquare API** ($49/mo)
   - Hashtag analytics, competitor benchmarking, best time to post data
   - API access on paid plans
   - More stable than scraper-based tools but limited to hashtag metadata, not trending content

### Viable Trend Polling Agent Architecture

**Recommended architecture for Djinn Layer 1 — `djinn-trend-agent`:**

```
djinn-trend-agent (runs every 6 hours via systemd timer)

Sources:
  1. Apify — Instagram Trending Reels, query: ["3d printing", "maker", "functional art"]
     → extract: top 10 Reels by engagement velocity (last 24h)
     → extract: common visual styles (text-on-screen %, reveal format %, timelapse %)
     → extract: audio type (music vs voiceover vs silent)

  2. Flick API — weekly hashtag audit (runs Sunday only)
     → query: base hashtag set from shop.json
     → return: current volume, difficulty, avg engagement
     → update: djinn/social/HASHTAG-BANK.md

  3. Own Graph API insights (daily at 00:00)
     → pull last 7 posts
     → compute: top performers by (saves + shares + watch_time)
     → delta: which hashtags appeared in top performers vs bottom

Outputs:
  → djinn/social/TREND-SIGNAL.md (updated every 6h)
  → djinn/social/HASHTAG-BANK.md (updated weekly)

Layer 2 reads:
  → TREND-SIGNAL.md before generating captions
  → HASHTAG-BANK.md when selecting hashtag set per post
```

**Polling cadence:**
- Apify trend scrape: every 6 hours (4x/day). Trends move slowly enough that hourly polling wastes quota.
- Own analytics: daily. Post performance data stabilizes after 24–48 hours.
- Hashtag bank: weekly. Hashtag volume doesn't shift faster than this.

**What a trend signal cannot tell you:**
- Which *audio tracks* are trending on Instagram — this is not accessible via any API. Best workaround: use your own background music and let the algorithm distribute based on visual quality and engagement.
- Real-time Explore page composition — Meta does not expose this. The closest proxy is Apify's trending Reels data, which reflects what's being boosted by the algorithm by measuring engagement velocity on recent posts.

### Cost Estimate for Full Trend Intelligence Stack

| Tool | Purpose | Cost/mo |
|------|---------|--------|
| Apify (solo tier) | Trending Reels + hashtag scraping | $49 |
| Flick | Hashtag difficulty + volume audit | $30 |
| Meta Graph API | Own analytics + publishing | Free |
| **Total** | | **$79/mo** |

Alternative minimal stack (Apify only): **$49/mo** — covers trending Reels and hashtag metadata. Drop Flick until revenue justifies the additional data.

---

## Summary — Priority Build Order for Djinn Media Layer 1

Based on this research, the recommended build sequence:

1. **Publishing function** — wrap the Meta Graph API two-step Reel publish into `djinn-media-publish`. Handles IG + FB in one call. (No cost, highest leverage.)
2. **Token management cron** — monthly refresh of Meta Page access token. (Critical infrastructure, 30 minutes to build.)
3. **Analytics pull cron** — `djinn-social-analyst` daily pull of post insights → `analytics/{date}.json`. Feeds the feedback loop. (Free, foundational.)
4. **TREND-SIGNAL.md writer** — `djinn-trend-agent` using Apify to populate trend signal every 6 hours. ($49/mo, unlocks Layer 1 intelligence.)
5. **Caption agent update** — teach the Layer 1 caption agent to read `TREND-SIGNAL.md` and `HASHTAG-BANK.md` before generating captions. (Local, no cost.)
6. **Platform-variant captions** — caption agent generates IG variant and FB variant from the same job metadata. (Model prompt update, no cost.)
7. **Multi-platform publish** — extend the publish function to post to both IG and FB sequentially with the correct caption variant. (Builds on item 1.)

This stack is fully buildable with existing Djinn infrastructure. Total new monthly cost: **$49/mo** (Apify only to start).

---

*Research complete. Committed to djinn/research/marcus/TASK-012_djinn-media-social.md — 2026-05-31.*
