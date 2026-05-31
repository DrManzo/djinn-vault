---
title: TASK-015 — DIY Trend Intelligence Stack Research
assigned_to: marcus
status: done
completed: 2026-05-31
tags: [djinn-media, trend-agent, scraping, instagram, reddit, youtube, apify, instaloader]
related: [[COMMS]] | [[TASK-012]] | [[TASK-016]] | [[TASK-018]]
---

# TASK-015 — DIY Zero-Cost Trend Intelligence Stack

> Can we replace Apify ($49/mo) + Flick ($30/mo) with a self-built, self-hosted stack that costs nothing to run and is maintained by us? Detailed analysis below.

---

## 1. Self-Hosted Instagram Scraping in 2026

### Current Library Status

| Library | Status (May 2026) | Reliability | Maintenance |
|---|---|---|---|
| **instaloader** | Active, healthy release cadence | Medium-Low | Weeks between breaks |
| **instagram-scraper** | Abandoned / unmaintained | Dead | N/A |
| **instagramy** | Unmaintained | Dead | N/A |
| **pyinstagram** | Unmaintained | Dead | N/A |
| **Playwright/Selenium headless** | Stable (browser-level) | Medium | Higher maintenance |

**Instaloader** is the only actively maintained pure-Python Instagram scraper as of May 2026. It has a healthy PyPI release cadence. However:

- It requires **authenticated sessions** (Firefox cookie import) to reliably pull hashtag data and avoid 429s
- Meta detects scripted access patterns and issues 429 rate limiting aggressively
- GitHub issues as of March 2026 confirm that **even authenticated sessions get detected reliably** when run continuously or at fixed intervals
- The library works best for one-off downloads, not a daemon polling every 6 hours

### Headless Browser Approach

Playwright (Python) is more stable than requests-based scrapers because it renders JavaScript and presents a real browser fingerprint. Tradeoffs:

- Higher memory usage (~300MB per browser instance)
- Slower per-query (3–8s vs <1s for requests)
- Still detectable via fingerprint if not rotated
- Requires a real or virtual display (Xvfb on Salomon)
- **No legitimate anti-bot workaround** — Meta's 2026 detection is at the account/session level, not just IP level

### Anti-Scraping Reality

Meta's anti-bot posture in 2026:

- **Rate limits:** 200 API calls/hour (official Graph API). Unofficial scraping limits are lower and undocumented.
- **CAPTCHA:** Triggered after pattern detection, not just volume
- **IP bans:** Datacenter IPs blocked immediately. Residential proxies work but cost $
- **Cookie requirements:** Unauthenticated scraping of hashtag pages returns minimal/no data
- **Account-level locks:** If the session account gets flagged, all scraping from that account stops until manual unlock

**Bottom line:** Self-hosted Instagram scraping is fragile, requires constant maintenance, and risks the shop's Instagram account if that account's session is used. **Not recommended as the primary trend data source.**

### Realistic Maintenance Burden

- Expected break frequency: every **2–6 weeks** when Meta updates frontend or detection patterns
- Time to fix per break: **1–4 hours** (identify change, update selectors or auth flow, test)
- Monthly maintenance estimate: **3–8 hours/month** just for Instagram scraping
- Failure mode: **silent** — scraper returns empty results without erroring, which is worse than a loud failure

---

## 2. Alternative Public Data Sources (Not Instagram)

### Reddit via PRAW — ✅ Recommended

Reddit's official API (PRAW) is free, stable, and does not require reverse engineering.

**Free tier limits (2026):** 100 requests/minute for OAuth apps. Djinn's use case (pull top 10 posts from 4 subreddits every 6 hours) = ~40 requests per poll. Well within limits.

**What we can extract:**
- Post title, score, upvote ratio, comment count, created timestamp
- Post velocity (new posts in last 24h with score > threshold)
- Flair ("DISCUSSION", "PRINT", "HELP" — useful for filtering to show-off content)
- Top comments (useful for detecting what questions/pain points are trending)

**Target subreddits for Djinn Media:**
- `r/3Dprinting` — primary maker signal
- `r/PrintedMinis` — niche, high-engagement community
- `r/glassheads` — cannabis accessory community
- `r/weed` — broad cannabis (use as signal, not content inspiration)
- `r/functionalart` — if exists; fallback to `r/crafts`

**Setup:**
```python
import praw
reddit = praw.Reddit(client_id=..., client_secret=..., user_agent="djinn-trend-agent/1.0")
subreddit = reddit.subreddit("3Dprinting")
top_posts = list(subreddit.top(time_filter="day", limit=10))
```

**Signal quality:** Good leading indicator for what's resonating in the maker community. Reddit trends often precede Instagram trends by 1–3 days.

### YouTube Data API v3 — ✅ Recommended

Free tier: **10,000 units/day**. A search query costs 100 units. That's 100 searches/day — Djinn needs ~8–16 per day (2–4 keywords × 4 polls). Comfortably within free tier.

**What we can extract:**
- Video title, description, view count, like count, comment count, publish date
- Tags (direct hashtag signal)
- Channel data (useful for identifying successful small creators in the niche)

**Query example:**
```python
from googleapiclient.discovery import build
youtube = build('youtube', 'v3', developerKey=API_KEY)
results = youtube.search().list(
    part='snippet',
    q='3D printing maker',
    type='video',
    videoDuration='short',  # YouTube Shorts proxy
    order='viewCount',
    publishedAfter='2026-05-30T00:00:00Z',
    maxResults=10
).execute()
```

**Signal quality:** YouTube Shorts trends are a **leading indicator** for Instagram Reels. Content formats that blow up on Shorts typically arrive on Reels within 1–2 weeks. This is the highest-quality free trend signal available.

**API key:** Free Google Cloud account, no credit card required for 10k units/day.

### Google Trends — ⚠️ Use Carefully

**pytrends (unofficial):** Still functional in 2026 but fragile — Google rate-limits it aggressively and has broken it multiple times. Not recommended for a cron job.

**Google Trends API (alpha):** Launched July 2025. Official, more stable, but still in alpha. No guaranteed SLA. Provides: consistently scaled interest data, time ranges, geographic data.

**Verdict:** Use the official alpha API if available. Fall back to manual Google Trends checks rather than pytrends in a daemon. Good for weekly keyword audits, not 6-hour polling.

**Useful keywords for Djinn:**
- `3D printed` — general interest
- `functional glass` — niche, cannabis-adjacent
- `puffco` — product-specific, peaks around drops
- `maker business` — entrepreneurship angle

### TikTok — ❌ Not Recommended for Djinn

TikTok's official API is available but requires a developer account and approval process that's uncertain for cannabis-adjacent content. Unofficial scrapers are fragile. TikTok's content policies are the strictest of all platforms for cannabis content — using TikTok as a data source when Djinn doesn't post there is low ROI.

**Exception:** If Javier decides to post on TikTok later, revisit. For now, skip.

### RSS / Web Scraping — ✅ Selective

| Source | What's Available | Stability |
|---|---|---|
| **Printables** (Prusa) | RSS feed for trending models | High |
| **Makerworld** (Bambu) | No RSS, scrapeable HTML | Medium |
| **Hackaday** | RSS feed | High |
| **Thingiverse** | RSS for popular items | Medium |

Printables and Hackaday RSS are stable, free, and provide signal about what physical objects are trending in the maker community. A trending model on Printables often becomes content inspiration within 1–2 weeks.

**Recommended addition to `djinn-trend-agent`:** Pull Printables RSS every 6 hours, extract top 5 trending model titles and categories. Add to TREND-SIGNAL.md.

---

## 3. Self-Hosted Hashtag Intelligence (Replacing Flick)

### What Flick Actually Does

Flick's core value props:
- Hashtag difficulty score (0–100)
- Estimated post volume per hashtag
- Average engagement per hashtag (average likes+comments on top posts using that tag)
- Hashtag grouping / saved collections

### Can We Build This?

**Partially, with caveats.**

The approach: scrape the top 9 posts for a given hashtag via Instaloader or Playwright, compute average likes+comments, use post count as volume proxy.

**Problems:**
- Meta blocks hashtag page scraping specifically and more aggressively than profile scraping
- Post count is no longer displayed on hashtag pages as of 2025 — Meta removed it
- Even when it works, data is delayed (cached pages) and inconsistent
- Silent failures (empty page returned, no error)

**Verdict:** Hashtag page scraping from Instagram is **not stable enough** for automated weekly audits. Too much maintenance, too much risk of silent failure.

### Alternative: Build HASHTAG-BANK.md from Other Signals

Instead of scraping Instagram for hashtag data, derive hashtag intelligence from:

1. **Extract hashtags from top Reddit posts** — titles and comments often contain Instagram hashtag candidates
2. **Extract tags from top YouTube videos** in the niche — these map closely to effective Instagram hashtags
3. **Monitor which hashtags appear in captions of posts that outperform** in `djinn-social-analyst` analytics — this is the highest-quality signal and is already in TASK-018
4. **Manual seed list** — curate 30–50 known-good hashtags, audit monthly with Flick's free trial or manually

**This approach is more durable than scraping Instagram directly.** The HASHTAG-BANK.md doesn't need to be perfect — it needs to be safe (no banned tags) and directionally correct.

---

## 4. Realistic Maintenance Burden

### Self-Built Instagram Scraper

| Factor | Detail |
|---|---|
| Break frequency | Every 2–6 weeks |
| Fix time per break | 1–4 hours |
| Monthly maintenance | 3–8 hours |
| Failure mode | **Silent** — returns empty data, no alert |
| Risk | Account-level flag if session account is the shop's main IG account |

**The silent failure problem is critical.** If the scraper breaks and returns empty trend data, `djinn-trend-agent` writes an empty TREND-SIGNAL.md, the caption agent generates generic captions, and Javier doesn't know for days or weeks. A monitoring layer would be required (check if TREND-SIGNAL.md was updated in last 12h, Telegram alert if not).

### Apify (Managed)

| Factor | Detail |
|---|---|
| Break frequency | Rare — Apify maintains the actor |
| Fix time per break | 0 — Apify handles it |
| Monthly maintenance | ~0 hours |
| Failure mode | Loud — Apify returns error codes |
| Cost | Free tier ($5 credits/mo) for Djinn's volume |

**The X vs. $0 calculation:**
- Self-built: $0/mo + 3–8 hours/month maintenance
- Apify free tier: $0/mo + 0 hours/month maintenance
- Apify paid: $29/mo (Starter plan, if free tier runs out) + 0 hours/month

At Javier's hourly value, even 2 hours/month of maintenance time makes Apify's free tier the better choice.

---

## 5. Apify Free Tier Analysis

**Free tier (2026):** $5/month in platform credits, 25 concurrent runs, 8 GB RAM per actor, 5 datacenter proxy IPs, no credit card required.

**Djinn's usage calculation:**
- Polling cadence: 4x/day = 120 runs/month
- Apify's Instagram Hashtag Scraper: ~$0.02–0.05 per run for small queries (10 posts per hashtag, 3 hashtags)
- Estimated monthly cost: 120 × $0.03 = **$3.60/month**
- **Fits in the $5 free tier.** ✅

**Important note (April 2026):** Apify retired the Rental Actor pricing model. All actors are now pay-per-usage. This is better for Djinn — no monthly actor rental fee on top of platform credits. The $5 free credits cover compute only.

**Hybrid recommendation:** Use Apify free tier as the primary Instagram data source. Build Reddit + YouTube + Printables RSS as free, self-maintained secondary sources. If Apify free tier runs out, the secondary sources still run.

---

## 6. Build Recommendation

### Optimal Zero-Cost Stack

```
djinn-trend-agent — runs every 6 hours via systemd timer

Source 1: Apify Instagram Hashtag Scraper (FREE TIER)
  - Actor: apify/instagram-hashtag-scraper
  - Query: top 9 posts for 3 hashtags per poll
  - Cost: ~$3.60/mo (within $5 free tier)
  - Maintenance: 0 hours (Apify manages)
  - Output: top post captions, hashtag lists, engagement counts

Source 2: Reddit PRAW (FREE, official API)
  - Query: top 10 posts/day from r/3Dprinting, r/glassheads, r/PrintedMinis
  - Cost: $0
  - Maintenance: ~0 hours (official API, stable)
  - Output: trending topics, titles, flair, score

Source 3: YouTube Data API v3 (FREE, 10k units/day)
  - Query: top 10 Shorts by keyword per poll (2 keywords × 4 polls = 800 units/day, well within limit)
  - Cost: $0
  - Maintenance: ~0 hours (official API, stable)
  - Output: trending video titles, tags, view velocity

Source 4: Printables RSS (FREE, stable)
  - Query: https://www.printables.com/rss — top models feed
  - Cost: $0
  - Maintenance: ~0 hours (RSS, extremely stable)
  - Output: trending model names, categories

Source 5: Google Trends API alpha (FREE, if stable)
  - Query: weekly keyword interest for 5 core terms
  - Cost: $0
  - Maintenance: low (alpha — monitor for deprecation)
  - Output: rising search terms, geographic peaks

Local NLP (Ollama phi4:14b on Salomon)
  - Takes raw data from all 5 sources
  - Extracts: trending topics, format signals, hashtag candidates
  - Writes: TREND-SIGNAL.md + HASHTAG-BANK.md
  - Cost: $0 (already running)
```

### Architecture Diagram

```
[systemd timer — every 6h]
        │
        ▼
[djinn-trend-agent]
        │
    ┌───┼───────────────────┬─────────────────┬──────────────┐
    │   │                   │                 │              │
    ▼   ▼                   ▼                 ▼              ▼
 Apify Reddit            YouTube          Printables    Google Trends
  IG    PRAW             Data API           RSS           API alpha
 scraper                 v3 free
    │   │                   │                 │              │
    └───┴───────────────────┴─────────────────┴──────────────┘
                            │
                            ▼
               [Ollama phi4:14b — local NLP]
                            │
              ┌─────────────┴──────────────┐
              ▼                            ▼
     TREND-SIGNAL.md               HASHTAG-BANK.md
     (every 6h update)             (weekly deep audit)
              │                            │
              ▼                            ▼
    [djinn-caption-agent]       [djinn-media-publish]
    reads before generating      reads for hashtag selection
```

### Build Time Estimate

| Component | Hours |
|---|---|
| Apify integration (API call + parse) | 2h |
| Reddit PRAW integration | 1h |
| YouTube API integration | 1.5h |
| Printables RSS parser | 1h |
| Google Trends integration | 1h |
| Ollama NLP processing layer | 3h |
| TREND-SIGNAL.md + HASHTAG-BANK.md writer | 2h |
| systemd timer + monitoring | 1h |
| Testing + first run verification | 2h |
| **Total** | **~14h** |

### Ongoing Maintenance

| Component | Hours/Month |
|---|---|
| Apify (managed) | 0 |
| Reddit PRAW | ~0 (official API) |
| YouTube API | ~0 (official API) |
| Printables RSS | ~0 |
| Google Trends alpha | ~0.5 (watch for deprecation) |
| Ollama NLP prompts | ~1 (tune as content evolves) |
| **Total** | **~1–2h/month** |

Compare to self-built Instagram scraper alone: 3–8h/month. The full diversified stack costs less maintenance than a single fragile scraper.

### Risks and Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Apify free tier credits run out | Low | Monitor usage, $29/mo Starter plan as fallback |
| Google Trends API exits alpha with breaking changes | Medium | Fall back to pytrends or manual quarterly audits |
| Reddit API changes pricing | Low | PRAW is stable; 100 req/min free tier confirmed through 2026 |
| YouTube API quota changes | Low | Currently 10k units/day — well above Djinn's needs |
| Apify actor breaks for Instagram | Very Low | Apify maintains actors; silent failure very rare |
| TREND-SIGNAL.md goes stale (any source fails) | Medium | Add monitoring: Telegram alert if file not updated in 8h |

### Final Recommendation

**Do not build a self-hosted Instagram scraper.** The maintenance burden (3–8h/month), silent failure risk, and account-flag risk outweigh the $0 cost benefit when Apify's free tier covers Djinn's actual usage volume at no cost.

**Build the diversified stack:** Apify (IG data) + Reddit PRAW + YouTube Data API + Printables RSS. Total cost: $0/month. Total maintenance: 1–2h/month. Total build time: ~14 hours.

This stack is more robust than Apify alone because it has multiple independent sources — if any one fails, the others continue producing trend signal.
