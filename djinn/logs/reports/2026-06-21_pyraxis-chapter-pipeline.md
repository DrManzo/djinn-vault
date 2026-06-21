---
title: Session Report — Dominion of Pyraxis Chapter Pipeline
date: 2026-06-21
agent: Claude
type: writing-pipeline
---

# Session Report — Dominion of Pyraxis Chapter Pipeline

## Summary

Ran all four available chapter files for *What the Empire Breeds* through the full writing/publishing pipeline. Source files were a mix of scanned PDFs (Prologue, Ch 1, Ch 2) and plain text (Ch 3). The PDFs were not machine-readable; Javier provided screenshots of Prologue and Ch 1 content directly in chat. All content has been transcribed, cleaned, and placed in the vault in properly formatted draft files. Full editorial and developmental notes have been written. CONTINUITY.md and CHARACTERS.md have been updated with new canon facts. Git commit and push to follow.

---

## What Was Built / Changed

### New Files Created

| File | Description |
|------|-------------|
| `Drafts/Prologue-The-Burning-Of-Sec-tra.md` | Clean draft of Prologue with typo fixes, [TBD] placeholders preserved, inline draft notes |
| `Drafts/Chapter-01-Javelin.md` | Cleaned draft of Ch 1 (Javelin POV) — voice-to-text artifacts removed, prose reconstructed; flagged for revision |
| `Drafts/Chapter-02-Raxz-The-Gala.md` | Full transcription of Ch 2 (Raxz POV) — near publication-ready prose, preserved faithfully |
| `Drafts/Chapter-03-Brax.md` | Full transcription of Ch 3 (Brax POV) — strong draft, preserved faithfully |
| `Editorial/PIPELINE-NOTES.md` | Full developmental + line edit pass: overall assessment, per-chapter notes (what's working/what needs work), cross-chapter consistency issues, character voice check, revision priorities, publishing pipeline recommendations |

### Files Updated

| File | Changes |
|------|---------|
| `CONTINUITY.md` | Added: Altonian Dynasty, Gallows Hills, Fields of Absolution, full location table, historical facts table, Faust established-facts table, corrected chapter numbering throughout story events section |
| `CHARACTERS.md` | Updated Faust profile with physical description and all Ch 1/Ch 3 facts; added Lord Theron of House Vandris as new character with flag about Nine Houses table |

---

## Technical Decisions

- **Chapter structure confirmed:** Prologue (Year 1 PR, 3 mystery figures) → Ch 1 (Javelin POV, training + Faust) → Ch 2 (Raxz POV, full gala day) → Ch 3 (Brax POV, damage control). Chapters 1 and 2 cover the same afternoon from different POVs.
- **PDFs were image-based, not machine-readable.** Screenshots were the only extraction method for Prologue and Ch 1; Ch 2 screenshots were sent as 17 images in chat. Ch 3 came as plain text.
- **Ch 2 is the strongest chapter by significant margin** — near publication-ready prose. Ch 3 is close behind. Ch 1 is an earlier draft and needs a full prose revision pass. Prologue needs structural rewrite of the opening paragraph + [TBD] resolution.
- **Lord Theron of House Vandris** was discovered in Ch 2 but does not appear in the Nine Houses table. Flagged for Javier to resolve: tenth house or replacement for an unnamed slot?
- **Faust is family to Brax** — established in Ch 3. This is significant unrevealed backstory and has been added to CONTINUITY.md and CHARACTERS.md.

---

## Files Created / Modified

```
djinn/workspaces/writing/projects/dominion-of-pyraxis/
  Drafts/
    Prologue-The-Burning-Of-Sec-tra.md   NEW
    Chapter-01-Javelin.md                NEW
    Chapter-02-Raxz-The-Gala.md         NEW
    Chapter-03-Brax.md                  NEW
  Editorial/
    PIPELINE-NOTES.md                   NEW
  CONTINUITY.md                         UPDATED (locations, history, Faust facts, chapter events)
  CHARACTERS.md                         UPDATED (Faust, Lord Theron)
djinn/logs/reports/
  2026-06-21_pyraxis-chapter-pipeline.md   THIS FILE
```

---

## Tests & Validation

- All draft files written with frontmatter (title, book, status, pov, date)
- Inline `<!-- DRAFT NOTES -->` blocks added to each chapter for quick reference without cluttering the manuscript view
- Cross-referenced each character appearance against CHARACTERS.md and CONTINUITY.md
- Verified internal timeline consistency: Brax 30 years of service, Faust holds over him 21 years → Brax ~9-10 when it started; Javelin 21 = full life under Faust's training; Raxz 21, wars 15 years ago → he was 6 = consistent with "before his father stopped smiling" memory
- Flagged Vandris as Nine Houses discrepancy — not resolved (requires Javier's input)
- Flagged blink sensory description inconsistency across chapters — "ripping noise," "faint squeak," "pop and whoosh" — needs standardization in revision pass

---

## Known Issues

- **[TBD] placeholders in Prologue:** World name for the people who formed the Altonian Dynasty is not established. The current vault has "Coravian" as the world name but the people's name in the Prologue context is blank.
- **House Vandris:** Not in the Nine Houses table. Either tenth house (breaks the established Nine structure) or one of the unnamed houses should be renamed.
- **What did Raxz do in the Arctus meeting?** The pre-gala meeting scene is intentionally elided from Ch 2 — but the author should decide privately what happened. Currently unknown even in the notes.
- **Bastyon meeting** (Ch 3): Set up but not executed on-page. Either needs a brief scene or a clear structural choice to defer it.
- **Mother/Empress absence:** Empty chair at the gala is noted but not explained. Should be locked in STORY-NOTES.md even if kept off-page.

---

## What's Next

### Immediate (before next writing session)
- Resolve [TBD] world name in Prologue
- Decide on House Vandris placement (tenth house vs. rename)
- Lock what happened in the Raxz-Arctus pre-gala meeting (even if off-page)
- Standardize blink sensory description across all chapters

### Writing Order
1. Revise Prologue (structural rewrite of opening + [TBD] resolution)
2. Revise Chapter 1 (full prose pass; expand intimate-tension scene; stabilize POV)
3. Chapter 4 — recommend: Javelin POV at the gala remaining with Millie after Raxz blinks away (one more beat of delay before the Emperor's office confrontation)
4. Chapter 5 — Emperor's office confrontation

— Claude
