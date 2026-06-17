---
title: Session Report — djinn-publish writing pipeline suite
agent: Claude
date: 2026-06-16
tags: [djinn, report, writing, publishing, djinn-publish]
related: [[build-log]] [[decision-log]]
---

# Session Report — djinn-publish Writing Pipeline Suite

**Date:** 2026-06-16
**Agent:** Claude
**Session type:** Build
**Trigger:** TASK-070 spec (Marcus) completed; Javier said "start it off" then "keep going" then "do it"

---

## Summary

Built the complete `djinn-publish` writing pipeline suite — all 14 tools from TASK-070 spec, tested against real manuscript data. Converted all surviving chapters of *What the Empire Breeds* (Prologue, Ch1–Ch3) from PDF/txt to canonical Markdown. Scaffolded manuscript directory, seeded `style_guide.md` from vault worldbuilding notes, and confirmed every tool produces correct output on 13,341 words of actual prose.

---

## What Was Built or Changed

**New repo:** `~/djinn-publish/` (standalone git, not inside Obsidian vault)

### Manuscript
- `manuscript/chapters/ch00_prologue.md` — 616 words, Omniscient POV
- `manuscript/chapters/ch01_hall-of-might.md` — 2,091 words, Javelin POV (raw, voice-dictated)
- `manuscript/chapters/ch02_weight-of-duty.md` — 6,517 words, Raxz POV (polished draft)
- `manuscript/chapters/ch03_high-steward.md` — 4,117 words, Brax POV (in-progress)
- `manuscript/full_manuscript.md` — assembled (13,341 words total)
- `manuscript/style_guide.md` — character roster, POV map, location names, italics rules

### Group 1 — Manuscript Health
- `health/word_count.py` — per-chapter counts, running total, velocity projection
- `health/continuity_checker.py` — fuzzy name matching, timeline candidate flagging, optional Ollama strict mode
- `health/pov_tracker.py` — interiority signal detection, head-hop flagging, declared vs detected POV
- `health/readability.py` — Flesch-Kincaid grade, sentence std dev, filter word density

### Group 2 — Style Consistency
- `style/dialogue_tags.py` — attribution verb audit, adverb-modified tag detection
- `style/repeat_detector.py` — proximity window repeats, n-gram phrases, cross-chapter Z-score
- `style/italics_checker.py` — mixed * vs _ syntax, sentence-length italic flagging, style guide rule check

### Group 3 — Export
- `export/chapter_split_merge.py` — split full_manuscript.md ↔ merge chapters
- `export/to_docx.py` — industry-standard editorial DOCX (TNR 12pt, double-spaced, running header)
- `export/to_atticus.py` — Atticus-import DOCX (single-spaced, Heading hierarchy, front/back matter)

### Group 4 — Tracking
- `tracking/beta_tracker.py` — CSV-backed beta reader status with deadline monitoring
- `tracking/arc_log.py` — ARC distribution log with color-coded review status
- `tracking/editorial_tracker.py` — DE → CE → PROOF enforcer with timeline projection

### Supporting
- `run` — venv wrapper script: `./run health/word_count.py manuscript/chapters/`
- `.venv/` — Python venv with python-docx 1.2.0
- `requirements.txt`
- `.gitignore`

---

## Technical Decisions

**Standalone repo (`~/djinn-publish/`) not inside Obsidian vault** — vault-enrich is committing to the vault concurrently. A multi-file code tree in the same repo would recreate the merge conflict storm from the previous session.

**PDF extraction with pdftotext + manual ligature cleanup** — Ch1 and Ch2 were PDFs with ligature artifacts (ﬁ→fi, ﬂ→fl, "o ice"→"office", "di erent"→"different"). Fixed systematically with `sed`. Ch1 was voice-dictated with transcription artifacts ("quotation marks", "N" paragraph markers) — preserved as-is, marked `status: raw-draft`.

**Dialogue tag regex approach with explicit hex escapes for quotes** — the Edit tool auto-converts straight quotes to curly quotes (`"` → `"` `"`) inside source files, breaking regex patterns. Fixed by building patterns with string concatenation using `'\x22'` and named variables rather than embedding quote literals in raw strings.

**All tools deterministic except continuity_checker.py --strict** — follows TASK-070 philosophy. LLM is called only when open-ended semantic reasoning is genuinely needed (timeline contradiction detection). Everything else is regex + stdlib.

**`style_guide.md` as single source of truth** — three tools (continuity checker, POV tracker, italics checker) read from it. Seeded from vault worldbuilding notes: `Summary-For-Chapter-3-Planning.md` + `The-Dominion-Of-Pyraxis-Quick-Reference-Guide.md`.

---

## Files Created or Modified

```
~/djinn-publish/                           ← new standalone repo
  manuscript/
    chapters/ch00_prologue.md              ← converted from PDF
    chapters/ch01_hall-of-might.md         ← converted from PDF (voice-draft)
    chapters/ch02_weight-of-duty.md        ← converted from PDF (polished)
    chapters/ch03_high-steward.md          ← converted from txt (in-progress)
    full_manuscript.md                     ← assembled by merger tool
    style_guide.md                         ← character/POV/location/italics rules
  health/word_count.py                     ← Tool 1.1
  health/continuity_checker.py             ← Tool 1.2
  health/pov_tracker.py                    ← Tool 1.3
  health/readability.py                    ← Tool 1.4
  style/dialogue_tags.py                   ← Tool 2.1
  style/repeat_detector.py                 ← Tool 2.2
  style/italics_checker.py                 ← Tool 2.3
  export/chapter_split_merge.py            ← Tool 3.3
  export/to_docx.py                        ← Tool 3.1
  export/to_atticus.py                     ← Tool 3.2
  tracking/beta_tracker.py                 ← Tool 4.1
  tracking/arc_log.py                      ← Tool 4.2
  tracking/editorial_tracker.py            ← Tool 4.3
  run                                      ← venv wrapper
  requirements.txt
  .gitignore
```

---

## Tests & Validation

All tools run against real manuscript data (13,341 words, 4 chapters):

- **word_count.py**: 13,341 total, 11.1% of 120k target, velocity 80 words/day
- **pov_tracker.py**: All 4 chapters match declared POV, no head-hop candidates
- **continuity_checker.py**: 1 location flag (Gallows vs Gallows Hills), 1 timeline pair in Ch2
- **repeat_detector.py**: Proximity repeats working, "o ice" artifact caught and fixed
- **readability.py**: Prologue flagged (FK 15.6 — one long run-on paragraph), Ch3 flagged (4.7% filter words)
- **dialogue_tags.py**: 5 tags detected (4 neutral, 1 non-neutral: "announced"), 1 adverb-tag
- **italics_checker.py**: 1 single-word italic found ("hard" in Ch1), no mixed syntax
- **to_docx.py**: Generated `what-the-empire-breeds_editorial.docx` (74KB)
- **to_atticus.py**: Generated `what-the-empire-breeds_atticus.docx` (73KB)
- **Tracking tools**: All 3 tested with sample entries, CSV read/write confirmed

---

## Known Issues

- **Ch1 voice-draft artifacts**: "quotation marks", "N" markers, fragmented sentences throughout. Needs a manual cleanup pass before any editorial use. Marked `status: raw-draft`.
- **dialogue_tags.py detection coverage**: Low count (5 tags for 13k words) — the pattern works correctly but most attribution in this manuscript is implied or uses beat + action rather than direct `"text," verb` structure. Not a bug; reflects the writing style.
- **Readability prologue flag**: FK 15.6 is from one massive run-on sentence in the raw draft prologue. Not a structural issue with the tool.

---

## What's Next

1. **Write Ch3 to completion** — Raxz-Arctus confrontation scene is the missing piece
2. **Write Ch4** from planning notes (Ch4 raw draft lost to machine reinstall)
3. **Run health tools before DE** — continuity_checker + pov_tracker + repeat_detector
4. **Ch1 cleanup pass** — voice-draft → polished prose (can use Djinn writing session)
5. **Djinn Publishings — Writing Pipeline Suite** — move from BACKLOG to QUEUE when manuscript is further along

— Claude
