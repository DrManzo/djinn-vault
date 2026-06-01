---
title: Session Report — TASK-029 djinn-marcus-sync initial build
agent: Claude
date: 2026-06-01
tags: [djinn, report, marcus, scraper, selenium]
related: [[build-log]] | [[decision-log]]
---

# Session Report — TASK-029 djinn-marcus-sync initial build

**Date:** 2026-06-01
**Agent:** Claude
**Session type:** Build
**Trigger:** Marcus pipeline automation — replace manual Perplexity export with hourly automated scrape

---

## Summary

Built djinn-marcus-sync from scratch: a Selenium + Xvfb scraper that polls the Perplexity Pro library, extracts thread content, and drops it into RAW/ with perplexity-pro frontmatter for djinn-clerk to route. Cloudflare bypassed via non-headless Firefox on a virtual display. djinn-clerk extended to detect and fast-route perplexity-pro files directly to djinn/research/marcus/threads/ without Ollama.

---

## What Was Built or Changed

- **`~/.local/bin/djinn-marcus-sync`** — NEW full Perplexity library scraper
  - Xvfb virtual display (:97) + non-headless Firefox to bypass Cloudflare fingerprinting
  - Copies cookies.sqlite from real Firefox snap profile to temp dir per-run (avoids lock conflicts)
  - `get_library_threads()` — scrolls /library 20x, extracts thread URLs + titles
  - `extract_thread()` — navigates to thread, extracts content, writes frontmatter with `source: perplexity-pro`
  - URL-based dedup (state file + scan_raw_for_urls for cross-run persistence)
  - Telegram notification on new threads
  - `--install` flag deploys systemd hourly timer with `loginctl enable-linger drmanzo`
- **`~/.local/bin/djinn-clerk`** — Extended for perplexity-pro routing
  - `read_frontmatter_field()` — extract YAML frontmatter fields
  - `route_marcus_thread()` — writes directly to djinn/research/marcus/threads/, no Ollama
  - Early return for `source: perplexity-pro` files before any Ollama path

---

## Technical Decisions

**Xvfb + non-headless Firefox over headless — Cloudflare bypass**
Headless Firefox triggers Cloudflare bot detection at browser fingerprint level regardless of valid session cookies. Virtual display with non-headless Firefox is identical to a real browser session from Cloudflare's perspective.

**requests library approach abandoned**
Tried requests with Firefox User-Agent + cookies first. Got HTTP 200 but page was a Next.js SPA shell — no thread data in HTML. Internal API endpoints returned 404/405. Selenium required.

**Temp profile copy (cookies only)**
Copying cookies.sqlite to a tmpdir avoids Firefox profile lock conflicts when the real browser is running. Only cookies needed — extensions, history, etc. excluded.

**No Ollama for perplexity-pro files**
Marcus threads are research deliveries, not raw exports needing cleanup. Routing them through qwen2.5:7b for summarization/tagging would degrade the content. Clerk detects source frontmatter and bypasses Ollama entirely.

---

## Files Created or Modified

```
~/.local/bin/djinn-marcus-sync              ← new — full scraper, Xvfb+Selenium, timer install
~/.local/bin/djinn-clerk                    ← extended — perplexity-pro fast-route to marcus/threads/
~/.config/systemd/user/djinn-marcus-sync.service  ← new — oneshot service
~/.config/systemd/user/djinn-marcus-sync.timer    ← new — hourly, Persistent=true
```

---

## Dependencies Installed

| Package | Method | Purpose |
|---------|--------|---------|
| selenium 4.44.0 | pip | Browser automation |
| geckodriver 0.36.0 | snap | Firefox WebDriver |
| Xvfb | apt (pre-installed) | Virtual display for non-headless Firefox |

---

## Tests & Validation

- First run: 20 threads found in library, all routed to djinn/research/marcus/threads/ via clerk
- Title extraction verified — titles came from `a.parentElement.innerText` not `a.innerText` (fixed UUID-as-title bug)
- Cloudflare bypass confirmed: non-headless Xvfb session returned library page, headless returned security block

---

## Known Issues / Caveats

- `loginctl enable-linger drmanzo` required — without it, systemd user timers don't fire without active login session

---

## What's Next

- [x] Wire djinn-clerk to auto-route perplexity-pro — done
- [x] Full rescrape overhaul (see 2026-06-01_marcus-sync-full-rescrape.md)

---

*— Claude, 2026-06-01*
