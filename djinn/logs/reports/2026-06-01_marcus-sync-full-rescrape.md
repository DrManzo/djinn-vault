---
title: Session Report — djinn-marcus-sync full rescrape overhaul
agent: Claude
date: 2026-06-01
tags: [djinn, report, marcus, scraper]
related: [[build-log]] | [[decision-log]]
---

# Session Report — djinn-marcus-sync full rescrape overhaul

**Date:** 2026-06-01
**Agent:** Claude
**Session type:** Build
**Trigger:** Javier noted that Perplexity threads are reused/ongoing — current "skip seen URLs" logic was preventing updates to growing threads

---

## Summary

djinn-marcus-sync was treating seen URLs as permanently done, which meant ongoing Perplexity threads never got updated after first scrape. Overhauled the sync logic to re-scrape all visible threads every run, overwrite vault files in place using stable URL-derived filenames, and simplified content extraction to free `body.innerText` (no Gemini, no fragile CSS selectors).

---

## What Was Built or Changed

- **djinn-marcus-sync**: removed persistent `seen_urls` skip filter — `seen` is now within-run dedup only
- **djinn-marcus-sync**: state file now stores only `last_run` + `last_count` (no URL list)
- **djinn-marcus-sync**: removed `scan_raw_for_urls()` function (dedup no longer needed across runs)
- **djinn-marcus-sync**: added `scroll_to_load_full_thread()` — scrolls until `scrollHeight` stops growing, loads full lazy-loaded thread DOM before extraction
- **djinn-marcus-sync**: `extract_thread()` simplified to `document.body.innerText` — free, no selectors, no API
- **djinn-clerk `route_marcus_thread()`**: filename now derived from Perplexity thread UUID (`pplx_{thread_id}.md`) — stable across re-scrapes, always overwrites in place

---

## Technical Decisions

**body.innerText over Gemini extraction — Cost/principle**
Considered using Gemini Flash to clean page content. Rejected: 100 threads × hourly = ~$50-70/month, violates near-zero-cost principle. `body.innerText` is already structured (Q&A in order). djinn-clerk's existing `strip_nav_garbage` handles the nav chrome. Zero cost, zero API dependency.

**body.innerText over CSS selectors — Robustness**
Previous approach used `querySelectorAll('[class*="prose"]')` etc. Fragile — Perplexity can change class names any release. Plain `body.innerText` never breaks regardless of DOM changes.

**Stable filename from URL thread ID — Idempotency**
Previous: `{date}_{slug}.md` — new file every day, vault fills with duplicates. New: `pplx_{uuid}.md` — same thread always maps to same file, overwrite is safe.

**Scrolling before extraction — Completeness**
Perplexity lazy-loads older messages. Without scrolling, only the most recent exchange would be in the DOM. `scroll_to_load_full_thread()` repeats scroll until `scrollHeight` stabilizes, guaranteeing full thread in DOM before `innerText` grab.

---

## Files Created or Modified

```
~/.local/bin/djinn-marcus-sync    ← removed dedup filter, simplified extract_thread, added scroll helper
~/.local/bin/djinn-clerk          ← route_marcus_thread: stable pplx_{uuid}.md filename, always overwrite
```

---

## Dependencies Installed

None.

---

## Tests & Validation

Not run this session — changes are logic-only, timer will validate on next hourly fire. Manual test: `djinn-marcus-sync --dry-run` to verify thread list without writing files.

---

## Known Issues / Caveats

- Scraping ALL threads every hour means ~30-100 Firefox page loads per run. On a slow connection or with many threads, runs could exceed 1h and overlap with the next timer fire. Systemd `Type=oneshot` prevents overlap but the run could be long.
- `strip_nav_garbage` in clerk was built for Save my Chatbot export format. `body.innerText` includes slightly different nav chrome. May need minor pattern tuning after first real run.

---

## What's Next

- [ ] Monitor first live run output — `tail -f /tmp/djinn-marcus-sync.log` — @Javier
- [ ] Tune `strip_nav_garbage` patterns if nav chrome differs from extension format — @Claude

---

*— Claude, 2026-06-01*
