---
title: Session Report — FairPrintAgent Fixes + Price Sheet
agent: Claude
date: 2026-05-25
tags: [djinn, report, fairprint, typhons-forge, monetization]
related: [[build-log]] | [[typhons-forge-monetization]] | [[project_fairprint]]
---

# Session Report — FairPrintAgent Fixes + Price Sheet

**Date:** 2026-05-25
**Agent:** Claude
**Session type:** Build + Debug
**Trigger:** Context-continued from prior session — FairPrintAgent had TTY crash, cost inflation, wrong market comps for smoking pieces; Javier needed three prints priced.

---

## Summary

Carried forward from a prior session that hit context limit. Finished all outstanding FairPrintAgent fixes: TTY guard for `--quick` mode, correct machine/labor cost split, smoking category detection, size-tiered comp fetching, and Python 3.14 argparse unicode fix. Ran commission price quotes for Javier's three completed Puffco Proxy prints. Documented two-track monetization plan (content-first → FairPrintAgent web app) with platform-safe language rules for the smoking niche.

---

## What Was Built or Changed

- **`--quick` TTY guard** — added `sys.stdin.isatty()` check; exits with helpful error if piped, preventing the `ValueError: invalid literal for float` crash on Discord/Telegram
- **Machine vs labor cost split** — separated `machine_cost = print_hours * MACHINE_RATE_PER_HOUR (~$0.20/hr)` from `labor_cost = (labor_minutes / 60) * hourly_rate`; previously print time was billed at $20/hr labor which inflated Mario Pipe from $14 → $112
- **`MACHINE_RATE_PER_HOUR` constant** — `(180/1000 * 0.13) + (399/5000) + 0.10 ≈ $0.20/hr` (electricity + depreciation + maintenance)
- **Smoking keyword detection** — `is_smoking_item(piece_name)` checks against `SMOKING_KEYWORDS` set; routes market search to smoking-specific sources if match
- **`SMOKING_SOURCES` list** — 13 retailers/Etsy market URLs for smoking niche: kaydmayd.com, smok3designs.com, geewestglass.com, 420trinkets.com, etc.
- **`--size small|large` flag** — fetches 12 comps, sorts by price; `small` returns bottom half, `large` returns top half; applied in both CLI and JSON modes
- **`--labor` flag** — overrides default 20-min hands-on time
- **Python 3.14 argparse fix** — `≤` character in `--qty` help string caused `ValueError: unsupported format character`; replaced with `<=`
- **Platform content rules** — added to monetization doc: Etsy/Instagram/TikTok require "herb"/"tobacco" language, never "cannabis"/"weed"

---

## Technical Decisions

**Machine rate as constant, not flag** — The Ender-3 V3 Plus depreciation, electricity, and maintenance are fixed overhead. Having a flag for it would imply user-adjustable when the numbers are derived from known hardware specs. Hardcoded constant is correct.

**`--size` tier in simple mode only shows cost floor** — Simple mode doesn't fetch comps; size flag passes through to JSON mode only. Documented in TOOLS.md.

**Smoking detection by keyword, not category flag** — Piece names naturally contain the signal ("dab tray", "proxy bubbler", "puffco"). Keyword match is lower friction than requiring Javier to remember a `--category smoking` flag.

---

## Files Created or Modified

```
~/.local/bin/djinn-print-quote              ← TTY guard, machine/labor split, smoking detection, --size/--labor flags
~/Obsidian/djinn/SYSTEM-STATE.md            ← printer idle, FairPrintAgent formula corrected
~/.openclaw/workspace/TOOLS.md              ← formula, --quick TTY warning, Discord quote simple updated
~/.openclaw/workspace/PLAN.md               ← populated with carry-forward @Javier + @Claude actions
~/.openclaw/workspace/MEMORY.md             ← 5-day backfill (2026-05-22 to 2026-05-25)
~/Obsidian/djinn/projects/typhons-forge-monetization.md  ← two-track plan, platform content rules
~/Obsidian/djinn/TROUBLESHOOT.md            ← openclaw-gateway.service name corrected
~/Obsidian/djinn/logs/reports/2026-05-24_media-stack.md  ← service name corrected
```

---

## Tests & Validation

Three commission quotes run and validated:

| Piece | Specs | Mode | Ask |
|-------|-------|------|-----|
| Proxy Mario Pipe | 44g, 3.33h | `--simple --size small` | $14.88 |
| Proxy Toilet | 26.06g, 1.33h | `--simple --size small` | $13.06 |
| Proxy Bubbler | 35g, 13.7h | full JSON, size=large | $18.39 floor / $21.42 fair |

Mario Pipe: previously returned $112.77 due to print time billed at labor rate. Now $14.88. Correct.

Bubbler market comps note: auto-fetch returned dab mats/stands/travel cases, not actual 3D-printed bubblers. Market median $28.50 is wrong category. Real market for 13.7h recycler bubbler = $35–65+. Recommended list price $35–45.

---

## Known Issues / Caveats

- Bubbler market search accuracy: `fetch_market_comps()` for "proxy bubbler" returns accessories rather than bubblers. Full bubblers need manual comp injection or better search queries targeting "3d printed puffco proxy recycler" specifically.
- `--quick` mode: works in terminal only, must never be invoked from Discord/Telegram. OpenClaw `quick quote` hook already routes to `--simple` (fixed in prior session).
- Typhon heartbeat stale by 2 days — may be offline or sync issue.

---

## What's Next

**@Javier:**
- `systemctl --user restart openclaw-gateway.service` on Salomon (activates 14 agents)
- Run `djinn-print-quote` on every completed print — build full price sheet
- Film first "pricing a real print" Reel for Instagram (Mario Pipe quote is the example)
- Test media inbox: drop video/photo in #media-inbox → should auto-ingest

**@Claude:**
- Scope FairPrintAgent web UI (form: name, grams, hours, spool cost → three numbers)
- Wire `djinn-media-qa` and `djinn-media-publish-prep` to post results to #media-status and #post-ready
- Improve bubbler comp search: add "3d printed puffco proxy recycler" and "3d printed bubbler" as explicit search terms when "bubbler" is in piece name

---

*— Claude, 2026-05-25*
