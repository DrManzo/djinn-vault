---
title: Session Report — Djinn Media Phase 2 + Firecrawl Debloat Audit
agent: Claude
date: 2026-05-31
tags: [djinn-media, phase2, firecrawl, meta-api, shipping, report]
related: [[build-log]] | [[decision-log]] | [[COMMS]] | [[DJINN-MEDIA-STATUS]]
---

# Session Report — Djinn Media Phase 2 + Firecrawl Debloat Audit

**Date:** 2026-05-31  
**Agent:** Claude  
**Session type:** Build + Architecture  
**Trigger:** Phase 2 build (Salomon down 5h), shipping module cleanup, Firecrawl integration audit

---

## Summary

Built the complete Meta Graph API publishing layer for Djinn Media (Phase 2): `djinn-media-publish`, `djinn-meta-token-refresh`, and `djinn-social-analyst` with their systemd timers. Cleaned up a redundant `djinn/shipping/` module Marcus had pushed, pulling the useful address parser improvements into `shipping_agent.py` instead. Commissioned Marcus (TASK-015) to research whether Apify + Flick can be replaced with a zero-cost DIY stack — answer: yes, with Apify free tier + Firecrawl covering the scraping layer at $0. Installed Firecrawl key, wrote Phase 3 specs (TASK-019/020), and audited the codebase for fragile scraping that Firecrawl should replace.

---

## What Was Built or Changed

### Shipping cleanup
- **Pulled Marcus's address parser improvements** into `djinn/printer/shop/shipping_agent.py`: compiled `_ZIP_RE`, `_STATE_RE` (full state name matching), `_STREET_RE`; added `is_complete()` to `ParsedAddress`; city extraction uses `parts[-1]` (more accurate than first token).
- **Deleted `djinn/shipping/`** entirely (`git rm -r`): 5 files (`address_parser.py`, `easypost_client.py`, `db_schema.sql`, `README.md`, `__init__.py`) — redundant with `shipping_agent.py`, wrong DB path, not imported anywhere.

### Phase 2 — Meta publishing layer
- **`djinn-media-publish`** — full IG + FB Reels publish via Meta Graph API. IG: resumable upload (`rupload.facebook.com`) → poll FINISHED → publish. FB: `video_reels` init/upload/finish flow. Caption variants: IG = full + all hashtags, FB = 2 sentences + 3 hashtags. Writes back to manifest + `publish-log.json`. Telegram on success. `--dry-run` tested against 44.1MB project.
- **`djinn-meta-token-refresh`** — monthly systemd timer (Persistent=true). Exchanges page token via `fb_exchange_token` grant. Writes in-place, never overwrites on failure. Telegram success/fail.
- **`djinn-social-analyst`** — daily systemd timer (00:30 UTC). Pulls own IG post insights (reach, plays, saves, shares, avg_watch_ms). Writes `djinn/social/analytics/YYYY-MM-DD.json` + `TREND-SIGNAL.md` sorted by engagement. Commits vault + Telegram summary.

### Phase 3 specs
- **TASK-019** — full `djinn-trend-agent` spec: Firecrawl search/scrape + Printables RSS + Apify (optional) → Ollama phi4:14b → TREND-SIGNAL.md + HASHTAG-BANK.md every 6h. Updated from original Reddit/YouTube API deps after Firecrawl key was provided.
- **TASK-020** — `djinn-media-publish-prep` caption wiring spec: inject TREND-SIGNAL.md + HASHTAG-BANK.md into caption generation, write `job_hashtags` back to media-context.json.

### Firecrawl install + audit
- `~/.config/djinn/firecrawl.env` created (chmod 600) with key `fc-95272169bf4042b482f0e4a5a3ce5cda`
- `~/.config/djinn/apify.env` stub created (chmod 600), token pending
- Full sweep of `~/.local/bin/djinn-*` — found 2 fragile scraping targets for replacement

---

## Technical Decisions

**Resumable upload for IG video** — Meta's `upload_type=resumable` to `rupload.facebook.com` is the only path that doesn't require a publicly accessible URL. Alternative (GDrive share link) would require extra rclone steps and link expiry management. Resumable is cleaner.

**FB caption = 2 sentences + 3 hashtags** — Based on Marcus's TASK-012 research: Facebook's algorithm penalizes hashtag-heavy captions; IG rewards them. Platform-variant captions from a single source doc.

**Firecrawl over Reddit + YouTube APIs** — TASK-019 originally required `reddit.env` + `youtube.env` credentials. Firecrawl's `fc.search()` covers both platforms with the existing key. One credential, maintained externally. Marcus's research confirmed Reddit PRAW is still viable as a direct alternative, but Firecrawl is simpler.

**Don't build a self-hosted Instagram scraper** — Marcus's TASK-015 research: 3–8h/month maintenance, silent failure mode, account-flag risk. Apify free tier covers Djinn's actual volume ($3.60/mo usage within the $5 free tier). Zero maintenance.

**`djinn-style-scrape` DDG vqd scraping** — The `vqd` token is extracted from raw DuckDuckGo HTML before the image search can fire. This pattern breaks silently whenever DDG updates their frontend. Firecrawl `fc.search()` is a direct replacement with zero maintenance.

---

## Files Created or Modified

```
~/.local/bin/djinn-media-publish              ← new — IG + FB Reels publisher
~/.local/bin/djinn-meta-token-refresh         ← new — monthly Meta token refresh
~/.local/bin/djinn-social-analyst             ← new — daily own-post analytics pull
~/.config/systemd/user/djinn-meta-token-refresh.service  ← new
~/.config/systemd/user/djinn-meta-token-refresh.timer    ← new (monthly)
~/.config/systemd/user/djinn-social-analyst.service      ← new
~/.config/systemd/user/djinn-social-analyst.timer        ← new (daily 00:30)
~/.config/djinn/firecrawl.env                 ← new (chmod 600)
~/.config/djinn/apify.env                     ← new stub (chmod 600)
djinn/printer/shop/shipping_agent.py          ← address parser improvements merged
djinn/shipping/                               ← deleted (git rm -r, 5 files)
djinn/communications/QUEUE.md                 ← TASK-015 (done), TASK-016-020 added
djinn/media/DJINN-MEDIA-STATUS.md             ← new — full stack status document
~/.openclaw/workspace/AGENTS.md               ← Build Delegation Protocol added (local, not git)
```

---

## Dependencies Installed

| Package | Method | Purpose |
|---------|--------|---------|
| `firecrawl-py` | pip (pending TASK-019) | Firecrawl SDK for trend agent |

---

## Tests & Validation

- `djinn-media-publish 2026-05-24_inbound --dry-run` — printed platform targets, reel path, caption preview, hashtag count. No errors.
- `python3 -m py_compile ~/.local/bin/djinn-media-publish` → OK
- `python3 -m py_compile ~/.local/bin/djinn-meta-token-refresh` → OK
- `python3 -m py_compile ~/.local/bin/djinn-social-analyst` → OK
- `systemctl --user list-timers | grep meta-token` → confirmed active (Javier enabled)
- `systemctl --user list-timers | grep social-analyst` → confirmed active (Javier enabled)

---

## Known Issues / Caveats

- **meta.env is empty** — all Phase 2 scripts are built and syntax-checked but cannot make live API calls until Javier fills in `META_PAGE_TOKEN`, `IG_USER_ID`, `FB_PAGE_ID`, `META_APP_ID`, `META_APP_SECRET`.
- **Apify key missing** — `apify.env` is a stub. TASK-019 spec handles this gracefully (skips Apify source silently if key not set).
- **djinn-style-scrape still uses DDG vqd** — fragile, will break silently. TASK-021 queued for replacement.
- **Git conflict on Phase 2 push** — Marcus pushed TASK-015 while build was in progress. Resolved with `git stash && git pull --rebase && git stash pop && git push`.

---

## What's Next

- [ ] Fill meta.env credentials (META_PAGE_TOKEN, IG_USER_ID, FB_PAGE_ID, META_APP_ID, META_APP_SECRET) — @Javier
- [ ] Create Apify account, get token → apify.env — @Javier
- [ ] TASK-019: Build djinn-trend-agent — @Salomon
- [ ] TASK-020: Wire trend signal into caption generation — @Salomon
- [ ] TASK-021: Rewrite djinn-style-scrape with Firecrawl — @Salomon
- [ ] TASK-022: Replace Makerworld/Thingiverse HTML scraping in djinn-model-fetch — @Salomon

---

*— Claude, 2026-05-31*
