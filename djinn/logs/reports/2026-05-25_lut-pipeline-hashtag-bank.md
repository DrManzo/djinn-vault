---
title: Session Report — LUT Color Pipeline, Hashtag Bank, Style Scraper
agent: Claude
date: 2026-05-25
tags: [djinn, report, media, lut, hashtag, photo-pipeline]
related: [[build-log]] | [[decision-log]] | [[MEDIA-STACK]]
---

# Session Report — LUT Color Pipeline, Hashtag Bank & Style Scraper

**Date:** 2026-05-25
**Agent:** Claude
**Session type:** Build
**Trigger:** Photo exports looked flat/convoluted; user wanted reference-driven aesthetic grading, trending hashtag research, and a scraper for style examples.

---

## Summary

Replaced ImageMagick curve-based photo editing with an ffmpeg + .cube LUT pipeline, giving photos and videos identical color science from the same files. Built a 236-tag hashtag bank (11 files, 9 categories) with a research agent and weekly systemd timer. Added `djinn-style-scrape` to auto-populate reference images from DuckDuckGo for vision QC. Multiple pipeline bug fixes: QA false positives on reel covers, feed manifest clobbering, Discord CloudFlare 403, hallucinated hashtags, caption voice drift.

---

## What Was Built or Changed

- **`djinn-lut-gen`** — generates `forge.cube`, `clean.cube`, `moody.cube` (33³ = 35937 points, 947KB each) to `~/.openclaw/workspace/media/shared/luts/`
- **`djinn-media-photo`** — rewritten: ffmpeg + LUT + `unsharp` sharpening, vision QC via llama3.2-vision, clean product name derivation from quoted notes text
- **`djinn-media-reel`** — LUT-based grading replaces inline curve strings; `--combine` flag for multi-clip concatenation
- **`djinn-style-scrape`** — DuckDuckGo image scraper, 8 default queries, downloads to `references/scraped/`; initial run pulled 32 images
- **Hashtag bank** — `~/Obsidian/djinn/media/hashtag-bank/` — 11 markdown files, 236 tags across 3d-printing (4 sub-categories), cannabis (4), brand (1), crossover (1), platform-rules (1)
- **`djinn-hashtag-update`** — `--report`, `--research` (phi4:14b trend research), `--add`, `--dump` modes; weekly systemd timer
- **`djinn-media-publish-prep`** — draft detection (quoted text in notes → polish mode), keyword-driven tag selection from bank, `clean_caption()` strips hallucinated tags, plain .txt exports, Drive upload includes `publish/` + `video/` + `feed/`, Discord posts plain text with Drive link
- **`djinn-media-qa`** — fixed `thumb_spec_for()` to correctly dispatch 1080×1920 spec for `reel_cover` variants
- **`djinn-media-ingest`** — `--notes` flag stores free-text in manifest
- **Reference folder** — `~/.openclaw/workspace/media/shared/references/{approved,scraped}/` with README
- **openclaw.json** — 14 agents total; added `style-scraper-agent` (14th), updated main agent routing for `style scrape` command and draft detection

---

## Technical Decisions

**LUT files over runtime curve math** — both photo and video tools now read the same .cube files, guaranteeing color consistency across exports. Previous approach: per-tool Python math that diverged silently. Rejected: inline ffmpeg `curves` filter (harder to tune visually).

**ffmpeg for photos, not ImageMagick** — `ffmpeg -frames:v 1` handles HEIC, WebP, and all common raw formats without extra dependencies. Also means `lut3d` filter works identically for stills and video.

**DuckDuckGo scraper over Instagram/Pinterest** — no API key required. Trade-off: results are noisier, need user curation. Mitigated by `approved/` folder for user's own trusted examples.

**draft-polish mode** — if user quotes text in their notes ("like this"), qwen2.5:7b polishes the draft. Cold-generate (no draft) falls back to phi4:14b. Reduces hallucination risk and respects user's intended voice.

**Tag validation in `clean_caption()`** — strips any hashtag not in the bank before writing publish files. Eliminates hallucinated or typo'd tags. Down-side: new legitimate tags silently dropped until added to bank via `djinn-hashtag-update --add`.

**Manifest merge with `dict.fromkeys(existing + new)`** — each tool only writes its own export type, never touching other tools' entries. Prior bug: photo tool replaced entire exports dict on each run.

---

## Files Created or Modified

```
~/.local/bin/djinn-lut-gen                    ← NEW: generates forge/clean/moody .cube LUTs
~/.local/bin/djinn-media-photo                ← REWRITTEN: ffmpeg + LUT + vision QC
~/.local/bin/djinn-media-reel                 ← UPDATED: lut_filter(), --combine flag
~/.local/bin/djinn-style-scrape               ← NEW: DuckDuckGo reference scraper
~/.local/bin/djinn-media-publish-prep         ← UPDATED: draft mode, tag filter, txt exports, Drive
~/.local/bin/djinn-media-qa                   ← UPDATED: per-variant thumbnail spec dispatch
~/.local/bin/djinn-media-ingest               ← UPDATED: --notes flag
~/.local/bin/djinn-hashtag-update             ← NEW: hashtag bank manager + research
~/.openclaw/workspace/media/shared/luts/forge.cube   ← NEW: 947KB
~/.openclaw/workspace/media/shared/luts/clean.cube   ← NEW: 947KB
~/.openclaw/workspace/media/shared/luts/moody.cube   ← NEW: 947KB
~/.openclaw/workspace/media/shared/references/README.md  ← NEW: approved/ + scraped/ instructions
~/.openclaw/workspace/media/shared/references/scraped/   ← NEW: 32 auto-scraped images
~/.openclaw/openclaw.json                     ← UPDATED: 14 agents, style-scraper-agent added
~/Obsidian/djinn/media/hashtag-bank/          ← NEW: 11 files, 236 tags
```

---

## Dependencies Installed

None new. All tools use ffmpeg (already present), Python stdlib, and existing Ollama models.

---

## Tests & Validation

- `djinn-lut-gen` — ran successfully, 3 × 947KB .cube files generated
- `djinn-style-scrape` — initial run: 32 images downloaded across 8 queries
- LUT files verified to load in ffmpeg (`lut3d` filter applied to test frame)
- `openclaw-gateway.service` restarted, 14 agents active
- 2026-05-24_inbound (Proxy Time Mug): 5-clip combine reel (49.7s), forge graded, Drive uploaded, Discord posted
- QA fix verified: reel_cover no longer false-positives on 16:9 spec
- Tag filter verified: hallucinated tags stripped before writing POST.txt

---

## Known Issues / Caveats

- Vision QC (`score_against_references`) requires Ollama + llama3.2-vision running. If model not loaded, QC is skipped silently.
- `djinn-style-scrape` DuckDuckGo vqd token may break if DDG changes their HTML structure.
- Scraped images in `references/scraped/` are noisy — user should review and move good examples to `approved/`.
- Tags stripped by `clean_caption()` are silently dropped; no warning yet. Use `djinn-hashtag-update --add` to grow the bank.
- `djinn-media-photo` HEIC support depends on ffmpeg having `hevc` decoder. Most distros do.

---

## What's Next

- [ ] Drop your own photo examples in `~/.openclaw/workspace/media/shared/references/approved/` — @Javier
- [ ] Review scraped/ folder, move best refs to approved/ — @Javier
- [ ] Run `djinn-media-photo <project> --style forge` on real content to evaluate forge LUT visually — @Javier
- [ ] Wire `djinn-media-qa` to post completion summary to #media-status — @Claude
- [ ] `djinn-hashtag-update --research` monthly to keep tags fresh — @Salomon cron

---

*— Claude, 2026-05-25*
