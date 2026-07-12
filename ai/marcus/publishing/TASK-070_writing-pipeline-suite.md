# TASK-070 — Djinn Publishings: Writing Pipeline Suite Spec
**Assigned to:** Marcus
**Status:** done
**Priority:** high
**Created:** 2026-06-16 by Javier
**Completed:** 2026-06-16 by Marcus (Perplexity)
**Depends on:** TASK-069 (`djinn/research/marcus/publishing/TASK-069_djinn-publishings-research.md`)
**Vault path:** `djinn/research/marcus/publishing/TASK-070_writing-pipeline-suite.md`

---

## vault_context_read

```yaml
vault_context_read:
  - path: djinn/research/marcus/publishing/TASK-069_djinn-publishings-research.md
    reason: Establishes the canonical pipeline (DE → CE → proof → Atticus → KDP + IngramSpark + Draft2Digital) that all tools in this suite must align with
  - path: i notes/Notes/Summary-For-Chapter-3-Planning.md
    reason: Character roster — required for continuity checker and POV tracker default name lists
  - path: i notes/Notes/The-Story-So-Far-In-Pyraxis.md
    reason: Timeline and plot summary — required context for timeline contradiction detection
  - path: i notes/Topics/Creative Writing/Story-Critique/
    reason: Chapter planning structure — informs chapter splitter/merger directory conventions
  - path: i notes/Topics/Creative Writing/Book-Worldbuilding/
    reason: Worldbuilding vault — location/faction/term lists for continuity checker
```

---

## Overview

The `djinn-publish` pipeline is a suite of lightweight, CLI-first Python scripts that automate the mechanical, error-prone steps of moving a manuscript from raw draft to publish-ready file. The design philosophy is:

1. **Scripts first, AI second.** Every tool defaults to deterministic logic. An LLM is invoked only when the task is genuinely open-ended (e.g., "does this sentence read ambiguously?") or when pattern-matching alone would produce too many false positives.
2. **Markdown as the canonical source format.** Javier's writing workflow centers on Obsidian — the pipeline treats `.md` files as the single source of truth. Everything exports *from* Markdown.
3. **Minimal dependencies.** Python stdlib wherever possible. External libraries only where they provide irreplaceable value (e.g., `python-docx` for DOCX generation). No cloud dependencies for core tools.
4. **Idempotent.** Running any script twice on the same input produces the same output. No destructive edits to source files.
5. **Composable.** Tools are independent scripts that read from `stdin` or file paths and write to `stdout` or specified output paths. They can be chained in a `Makefile` or shell pipeline.

**Assumed manuscript structure:**

```
manuscript/
├── chapters/
│   ├── ch01_the-beginning.md
│   ├── ch02_pyraxis-wakes.md
│   └── ...
├── full_manuscript.md          # assembled by chapter-merger tool
├── style_guide.md              # character names, world terms, POV rules
├── arcs/                       # ARC exports
└── exports/
    ├── beta_reader_v1.docx
    ├── arc_v1.pdf
    └── atticus_ready/
```

---

## Group 1 — Manuscript Health Scripts

---

### Tool 1.1 — Word Count Tracker

**Description:** Per-chapter word count with running total, target vs. actual comparison, and projected finish date based on daily writing velocity.

**Input:**
- `manuscript/chapters/` directory (glob `*.md`)
- Optional: `--target 120000` (total word count target)
- Optional: `--start-date 2026-01-01` (when drafting began, for velocity calculation)

**Output:**
- Terminal table: chapter filename | word count | cumulative total | % of target
- Summary line: total words | target | delta | daily average | projected finish date
- Optional: `--json` flag emits machine-readable output for dashboard integration

**Logic:**
1. For each `.md` file, strip YAML frontmatter (anything between `---` fences at top of file)
2. Strip Markdown syntax (headers, bold, italics, links, code fences) using regex
3. Split on whitespace, count tokens
4. Sort chapters by filename (relies on numeric prefix convention: `ch01_`, `ch02_`, etc.)
5. Velocity: `total_words / days_since_start_date`; project: `(target - total_words) / velocity`

**Dependencies:** Python stdlib only (`pathlib`, `re`, `datetime`, `argparse`)

**Complexity:** Simple

**LLM needed:** No — pure arithmetic and string processing

**Priority:** Must-have before publish

**Notes:** Add `--exclude-frontmatter` flag to skip any chapter with `status: outline` in frontmatter, so placeholder chapters don't inflate page count.

---

### Tool 1.2 — Continuity Checker

**Description:** Flags potential continuity errors across the full manuscript: character name inconsistencies, location name variations, and timeline markers that appear out of order.

**Input:**
- `manuscript/chapters/` directory
- `style_guide.md` — canonical names list in a defined section (`## Characters`, `## Locations`, `## Factions`) — one canonical name per line, with optional aliases in parentheses: `Kael Vrayne (Kael, the Vrayne boy)`
- Optional: `--strict` mode adds LLM pass for semantic contradictions

**Output:**
- Flagged list per category: character name variant | chapter file | line number | canonical name
- Location variant flags: same structure
- Timeline contradiction candidates: pairs of sentences containing temporal language that may conflict (e.g., "three days later" appearing after "a week had passed" within the same scene block)

**Logic:**
1. Parse `style_guide.md` to build canonical name dict: `{alias → canonical}`
2. For each chapter, scan every paragraph for any token that fuzzy-matches a known alias but doesn't match the canonical form (use `difflib.SequenceMatcher` for fuzzy matching, threshold 0.85)
3. Timeline markers: extract sentences containing keywords (`["days later", "that morning", "the next", "hours ago", "weeks since"]`), group by chapter, flag pairs within the same scene where the temporal language is internally contradictory
4. Location scanner: same alias-dict approach as character names

**LLM pass (optional `--strict`):** Send flagged timeline sentence pairs to the model with prompt: *"Do these two sentences, appearing in the same scene, contradict each other temporally? Answer YES or NO with brief reason."* Use only for pairs where deterministic detection is ambiguous. Cache results by sentence hash to avoid re-querying.

**Dependencies:** `difflib` (stdlib), `re`, `pathlib`. Optional LLM: any Ollama-compatible model via subprocess call or `requests` to local endpoint.

**Complexity:** Medium

**LLM needed:** Optional (strict mode only)

**Priority:** Must-have before DE submission

---

### Tool 1.3 — POV Tracker

**Description:** Identifies which POV character holds each chapter and each scene break, and flags mid-scene POV breaks (head-hopping).

**Input:**
- `manuscript/chapters/` directory
- `style_guide.md` — POV character list under `## POV Characters` section: one name per line
- POV chapters may declare their POV character in frontmatter: `pov: Kael`

**Output:**
- Per-chapter POV assignment table: chapter | declared POV | detected POV | match Y/N
- Flagged head-hops: chapter | scene (by `---` scene break delimiter) | line number | suspected POV shift (name of second character appearing with interiority markers)
- Summary: POV distribution across manuscript (which character has the most chapters)

**Logic:**
1. **Declared POV:** Read frontmatter `pov:` field if present.
2. **Detected POV:** Within each scene (delimited by `---` or `* * *` horizontal rules), count first-person interiority signals attached to named characters:
   - Patterns: `[Name] thought`, `[Name] felt`, `[Name] realized`, `[Name] noticed`, `[Name] wondered`, `[Name]'s heart`, `[Name]'s stomach`, `in [Name]'s mind`
   - The character with the highest interiority signal count in a scene = detected POV holder
3. **Head-hop detection:** If a scene contains interiority signals for 2+ characters, flag it. If one character has ≥3 signals and a second character has ≥2, escalate to warning.
4. **Conflict detection:** If declared POV ≠ detected POV, flag mismatch for review.

**Dependencies:** `re`, `pathlib`, `collections.Counter` (all stdlib)

**Complexity:** Medium

**LLM needed:** No — the interiority-signal pattern list is sufficient for deterministic detection at this granularity. A false-positive rate of ~15% is acceptable (writer reviews flags, not auto-corrects).

**Priority:** Must-have before DE submission

---

### Tool 1.4 — Readability Pass

**Description:** Calculates Flesch-Kincaid grade level, sentence length variance, and filter word density per chapter and across the full manuscript.

**Input:**
- `manuscript/chapters/` directory or single file path
- Optional: `--filter-words path/to/custom_list.txt` (augments default filter word list)

**Output:**
- Per-chapter table: FK grade level | avg sentence length | sentence length std dev | filter word count | filter word % of total words
- Full-manuscript aggregate row
- Filter word breakdown: which filter words appear most frequently, top 10 per chapter
- Flagged chapters: FK grade > 12 (too dense), sentence length std dev < 5 (monotonous rhythm), filter word % > 4% (over-reliance)

**Default filter word list:**
```
was, were, had, felt, seemed, appeared, noticed, saw, heard, watched, looked,
realized, thought, knew, found, began, started, just, suddenly, very, quite,
rather, somewhat, almost, nearly, really, actually, basically, literally
```

**Logic:**
1. Split chapter text into sentences (use `re.split(r'(?<=[.!?])\s+', text)`)
2. FK Grade: `0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59`. Syllable count via regex vowel-cluster approximation (stdlib-only method; accuracy ~85%, sufficient for pass/fail flagging).
3. Sentence length std dev: standard deviation of word counts per sentence.
4. Filter word scan: case-insensitive token match against filter list, count and percentage.

**Dependencies:** `re`, `statistics`, `pathlib`, `argparse` (all stdlib)

**Complexity:** Simple

**LLM needed:** No

**Priority:** Nice-to-have (run before copy edit, not before DE)

---

## Group 2 — Style Consistency Tools

---

### Tool 2.1 — Dialogue Tag Audit

**Description:** Flags overuse of non-`said`/`asked` dialogue tags and adverb-modified tags. Provides per-chapter and manuscript-wide frequency tables.

**Input:**
- `manuscript/chapters/` directory or single file
- Optional: `--threshold 10` (flag chapters where non-said tags exceed N% of all dialogue tags)

**Output:**
- Per-chapter table: total dialogue tags | `said`/`asked` count | non-said count | top 5 non-said tags with counts
- Manuscript-wide aggregate
- Flagged lines: chapter | line number | the full dialogue line with the problematic tag highlighted

**Non-said tag detection logic:**
1. Dialogue pattern: `"[text]" [verb] [character]` or `[character] [verb] "[text]"`
2. Extract the attribution verb. If it is not in `{said, asked, replied, answered}`, flag it.
3. Adverb-modified tag: tag + word ending in `-ly` within 3 tokens → secondary flag.

**Common non-said tags to track:** `exclaimed, shouted, whispered, hissed, snapped, breathed, laughed, smiled, frowned, huffed, growled, murmured, declared, announced, insisted, demanded, protested`

**Dependencies:** `re`, `collections.Counter`, `pathlib` (stdlib)

**Complexity:** Simple

**LLM needed:** No

**Priority:** Nice-to-have (run before copy edit)

---

### Tool 2.2 — Repeated Word/Phrase Detector

**Description:** Identifies words and phrases that repeat within close proximity (same paragraph or within N sentences) and across the full manuscript at abnormally high frequency.

**Input:**
- `manuscript/chapters/` directory or single file
- `--window 5` (sentence window for proximity detection, default 5)
- `--top 20` (report top N most-frequent words per chapter, default 20)
- Optional: `--stopwords path/to/stopwords.txt` (augments default English stopwords)

**Output:**
- Proximity flags: chapter | paragraph | the repeated word/phrase | distance between occurrences (in sentences)
- Frequency report: per chapter top-N non-stopword tokens with counts
- Cross-manuscript frequency: words that appear in unusually high density across the full text (Z-score > 2.0 relative to a baseline of expected English prose frequency)
- Phrase detector: 2–4 word n-grams appearing ≥5 times per chapter

**Logic:**
1. Tokenize using `re.findall(r'\b[a-zA-Z]+\b', text)` after lowercasing
2. Proximity: for each token, record its sentence index; if the same token appears within `--window` sentences, flag it
3. N-gram phrases: sliding window of size 2, 3, 4; count frequency; report phrases exceeding threshold
4. Z-score normalization: compare chapter token frequency to manuscript-wide frequency distribution using `statistics.stdev`

**Dependencies:** `re`, `collections.Counter`, `statistics`, `pathlib` (stdlib)

**Complexity:** Simple-Medium

**LLM needed:** No

**Priority:** Must-have before copy edit

---

### Tool 2.3 — Italics Consistency Checker

**Description:** Audits the use of italics (`*word*` or `_word_`) throughout the manuscript, ensuring internal thought formatting is uniform and that italics are not used inconsistently for other purposes (foreign words, titles, emphasis).

**Input:**
- `manuscript/chapters/` directory
- `style_guide.md` — `## Italics Rules` section: one rule per line, e.g.:
  - `internal_thought: single_word_italics` or `internal_thought: full_sentence_italics`
  - `foreign_terms: italicized`
  - `book_titles: italicized`

**Output:**
- Internal thought candidates: all italicized text that is a complete sentence or clause (≥4 words), listed by chapter and line
- Single-word italics inventory: frequency table of all italicized single words across manuscript
- Formatting inconsistency flag: if both `*word*` and `_word_` Markdown italics syntax are used within the same chapter, flag for normalization
- Rule violation candidates: if style guide says `internal_thought: single_word_italics` but full sentence italics appear, flag them (and vice versa)

**Logic:**
1. Extract all italic spans using `re.findall(r'\*([^*]+)\*|_([^_]+)_', text)`
2. Classify by length: 1 word = single-word, ≥4 words = phrase/sentence, 2–3 = ambiguous
3. Check for mixed syntax (`*` vs `_`) within same chapter
4. Cross-reference against style guide rules

**Dependencies:** `re`, `pathlib`, `collections.Counter` (stdlib)

**Complexity:** Simple

**LLM needed:** No — rule-based classification is sufficient

**Priority:** Nice-to-have (run during copy edit phase)

---

## Group 3 — Export and Formatting Scripts

---

### Tool 3.1 — Markdown → DOCX Exporter

**Description:** Converts the assembled manuscript (or individual chapters) from Markdown to a clean `.docx` file formatted for editorial submission. Follows industry standard manuscript format (Times New Roman 12pt, double-spaced, 1" margins, header with author/title/page number).

**Input:**
- `manuscript/full_manuscript.md` or chapter directory
- `--title "What the Empire Breeds"`
- `--author "Javier [surname]"`
- `--contact "djinnpublishings@[domain].com"`
- Optional: `--style editorial` (default, industry standard) or `--style beta` (more readable, slightly larger font)

**Output:**
- `exports/[title]_v[version]_editorial.docx`

**Industry standard manuscript format applied:**
- Font: Times New Roman 12pt body
- Double-spaced throughout
- 1" margins all sides
- Header: `[Author Last Name] / [Title Keyword] / [Page Number]` (right-aligned, from page 2)
- Title page: title (centered, 1/3 down page), author name, contact, word count
- Chapter breaks: new page per chapter, chapter title centered, 3 blank lines before chapter text begins
- Scene breaks: `#` rendered as `* * *` (standard manuscript format for scene breaks)

**Logic:**
1. Parse Markdown: strip frontmatter, extract chapter titles from `#` and `##` headings, split on horizontal rules for scene breaks
2. Build DOCX structure using `python-docx`: set styles, apply paragraph formatting, build header, insert page breaks between chapters
3. Scene breaks: replace `---` or `* * *` Markdown dividers with centered `* * *` paragraph in normal (non-heading) style

**Dependencies:** `python-docx` (external, pip installable), `re`, `pathlib`

**Complexity:** Medium

**LLM needed:** No

**Priority:** Must-have (needed for DE and beta reader submission per TASK-069 pipeline)

---

### Tool 3.2 — Markdown → Atticus-Ready Formatter

**Description:** Prepares the manuscript Markdown for clean import into Atticus (the chosen formatter per TASK-069). Atticus imports DOCX — this tool produces a specifically structured DOCX optimized for Atticus import rather than editorial submission.

**Input:**
- `manuscript/full_manuscript.md`
- `--title`, `--author`, `--series-title "The Dominion's Rise"`, `--series-number 1`
- `--trim 6x9` (validates target trim size is supported)

**Output:**
- `exports/atticus_ready/[title]_atticus_import.docx`

**Key differences from editorial DOCX:**
- Single-spaced (Atticus re-flows with its own leading settings)
- No manuscript header (Atticus generates its own)
- Clean heading hierarchy: `Heading 1` = chapter title, `Heading 2` = scene heading if used
- Emphasis styles preserved: bold (`**`), italic (`*`) mapped to DOCX character styles
- Horizontal rules preserved as distinct paragraph style (Atticus uses them for scene break ornament placement)
- Front matter sections clearly labeled: title page, copyright, dedication, TOC placeholder, chapter 1 start
- Back matter sections: author bio, series note, acknowledgments

**Atticus import notes:**
- Atticus reads DOCX heading styles to auto-detect chapter structure
- Paragraph breaks must be single returns (not double) — Atticus handles spacing via its own paragraph styles
- Footnotes not supported in Atticus for novels — flag any footnotes in the source with a warning

**Dependencies:** `python-docx`, `re`, `pathlib`

**Complexity:** Medium

**LLM needed:** No

**Priority:** Must-have (direct pipeline step per TASK-069 Section 2.1)

---

### Tool 3.3 — Chapter Splitter/Merger

**Description:** Two inverse operations in one script. Split mode: takes `full_manuscript.md` and produces individual chapter files. Merge mode: takes `manuscript/chapters/*.md` and assembles them into `full_manuscript.md` in correct order.

**Input (split mode):**
- `--input full_manuscript.md --mode split --output-dir chapters/`
- Chapter detection: any line matching `^# Chapter` or `^# [A-Z]` at the start of a line after the first page

**Input (merge mode):**
- `--input-dir chapters/ --mode merge --output full_manuscript.md`
- Merge order: alphanumeric sort on filename (relies on `ch01_`, `ch02_` prefix convention)

**Output:**
- Split: `chapters/ch01_[slug].md`, `ch02_[slug].md`, etc. (slug = lowercased chapter title, spaces → hyphens)
- Merge: single `full_manuscript.md` with chapter titles as `# Heading` dividers

**Logic:**
1. **Split:** Read full file; scan for chapter heading pattern; on each match, write buffer to new file named by chapter number (auto-incremented) + title slug; reset buffer
2. **Merge:** Glob `chapters/*.md`, sort, read each file, append to output buffer with a newline separator between files; preserve frontmatter from individual chapters in a preamble comment block (stripped from assembled output)
3. Frontmatter handling: strip YAML frontmatter (`---` blocks) from individual chapter files before merging; write a `## FRONTMATTER STRIPPED FROM [filename]` comment block to a sidecar log for reference

**Dependencies:** `pathlib`, `re`, `argparse` (stdlib)

**Complexity:** Simple

**LLM needed:** No

**Priority:** Must-have (core workflow tool — Javier writes in individual chapter files per Obsidian structure; merger assembles for export)

---

### Tool 3.4 — ARC PDF Generator

**Description:** Produces a clean, reader-ready ARC PDF from the assembled manuscript. Includes cover page with ARC disclaimer, chapter breaks with page numbers, and metadata footer. This is the EPUB-alternative for direct PDF distribution per TASK-069 Section 3.3.

**Note:** EPUB is the recommended ARC format per TASK-069 (more universal). This tool produces a PDF ARC for recipients who prefer PDF or for direct/personal distribution.

**Input:**
- `manuscript/full_manuscript.md`
- `assets/cover.jpg` (optional — if present, inserts as cover page)
- `--title`, `--author`, `--series`, `--version "ARC v1 — Not for Sale"`
- `--pub-date "Fall 2026"` (for ARC cover page)

**Output:**
- `arcs/[title]_ARC_v[N].pdf`

**PDF structure:**
1. Cover page: cover image (if available) or styled title card
2. ARC disclaimer page: "This is an Advance Reader Copy of [Title] by [Author], published by Djinn Publishings. It is not for sale or distribution. Please request permission before quoting. Publication date: [date]. Thank you for reading."
3. Body: Garamond 12pt (or closest available), 1.1 line spacing, chapter breaks, running header (title + author), page numbers (footer, centered)
4. Back matter: author bio, series note, contact information for Djinn Publishings

**Generation approach:** Use `reportlab` (external library) for direct PDF generation. Markdown → intermediate text structure → ReportLab canvas. Alternatively, generate DOCX via Tool 3.1 then convert to PDF using `libreoffice --headless --convert-to pdf` shell call (requires LibreOffice installed, which is standard on Fedora/Ubuntu).

**Recommended approach:** LibreOffice headless conversion is faster to implement and more accurate for typography. ReportLab gives more control but requires building a layout engine.

**Dependencies:** `subprocess` (stdlib for LibreOffice call) OR `reportlab` (external). `pathlib`, `re`.

**Complexity:** Medium (LibreOffice approach) / Complex (ReportLab approach)

**LLM needed:** No

**Priority:** Nice-to-have (EPUB is the primary ARC format; PDF is secondary)

---

## Group 4 — Submission and Tracking Tools

---

### Tool 4.1 — Beta Reader Tracker

**Description:** Lightweight CSV-backed tracker for beta reader status. No database — pure CSV file, edited manually or via script commands.

**Input/Storage:** `tracking/beta_readers.csv`

**CSV schema:**
```
name, email, chapter_range, date_sent, deadline, status, feedback_received, notes
```

Status values: `pending | sent | reading | submitted | complete | dropped`

**CLI commands:**
- `python beta_tracker.py add --name "Jane" --email "..." --chapters "1-12" --deadline "2026-08-01"`
- `python beta_tracker.py update --name "Jane" --status reading`
- `python beta_tracker.py status` — prints current table, sorted by deadline
- `python beta_tracker.py overdue` — lists readers past deadline with status != complete
- `python beta_tracker.py report` — summary: total sent, % submitted, % complete, avg feedback time

**Output:** Terminal table (formatted with `str.ljust` column alignment, no external table library needed)

**Dependencies:** `csv`, `datetime`, `argparse`, `pathlib` (stdlib)

**Complexity:** Simple

**LLM needed:** No

**Priority:** Must-have before beta reading begins

---

### Tool 4.2 — ARC Distribution Log

**Description:** Tracks every ARC recipient across all platforms (NetGalley, StoryOrigin, direct email). Records send date, review status, and review link.

**Input/Storage:** `tracking/arc_log.csv`

**CSV schema:**
```
name, platform, email_or_handle, date_sent, arc_version, review_posted, review_link, notes
```

Platform values: `netgalley | storyorigin | direct | booksirenreads | other`

**CLI commands:**
- `python arc_log.py add --name "..." --platform storyorigin --date 2026-09-01 --version "ARC v1"`
- `python arc_log.py mark-reviewed --name "..." --link "https://goodreads.com/..."`
- `python arc_log.py status` — full table with color-coded review status (ANSI escape codes: green = reviewed, yellow = pending, red = overdue)
- `python arc_log.py summary` — total sent | total reviewed | % review rate | platforms breakdown

**ANSI color output:**
```python
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
```

**Dependencies:** `csv`, `datetime`, `argparse` (stdlib)

**Complexity:** Simple

**LLM needed:** No

**Priority:** Must-have before ARC distribution (6–8 weeks before pub date per TASK-069 Section 4.3)

---

### Tool 4.3 — Editorial Revision Tracker

**Description:** Tracks the editorial pipeline across all three rounds (DE → CE → proof), file handoffs, deadlines, and revision notes.

**Input/Storage:** `tracking/editorial_log.csv`

**CSV schema:**
```
round, editor_name, editor_email, file_sent, date_sent, date_due, date_received, file_received, status, notes
```

Round values: `DE | CE | PROOF`
Status values: `not_started | file_sent | in_progress | received | revising | complete`

**CLI commands:**
- `python editorial_tracker.py add --round DE --editor "Name" --email "..." --file-sent "exports/manuscript_v1.docx" --date-due "2026-10-01"`
- `python editorial_tracker.py update --round DE --status received --file-received "exports/manuscript_v1_DE_edits.docx"`
- `python editorial_tracker.py status` — full pipeline view, all rounds
- `python editorial_tracker.py timeline` — calculates elapsed time per round, total editorial timeline, projected completion

**Timeline reporting:**
- Calculates days elapsed per round (date_received − date_sent)
- Flags rounds where no file has been received past the due date
- Projects total editorial timeline: sum of elapsed + estimated remaining (user provides estimates via `--estimate-days N`)

**Dependencies:** `csv`, `datetime`, `argparse` (stdlib)

**Complexity:** Simple

**LLM needed:** No

**Priority:** Must-have before hiring DE (first editorial handoff per TASK-069 Section 3.1)

---

## Priority Matrix

| Tool | Group | Priority | Complexity | LLM | Depends On |
|------|-------|----------|------------|-----|------------|
| 1.1 Word Count Tracker | Manuscript Health | **Must-have** | Simple | No | None |
| 1.2 Continuity Checker | Manuscript Health | **Must-have** | Medium | Optional | style_guide.md |
| 1.3 POV Tracker | Manuscript Health | **Must-have** | Medium | No | style_guide.md |
| 1.4 Readability Pass | Manuscript Health | Nice-to-have | Simple | No | None |
| 2.1 Dialogue Tag Audit | Style Consistency | Nice-to-have | Simple | No | None |
| 2.2 Repeated Word Detector | Style Consistency | **Must-have** | Simple-Med | No | None |
| 2.3 Italics Checker | Style Consistency | Nice-to-have | Simple | No | style_guide.md |
| 3.1 Markdown → DOCX | Export/Format | **Must-have** | Medium | No | python-docx |
| 3.2 Atticus-Ready Export | Export/Format | **Must-have** | Medium | No | python-docx |
| 3.3 Chapter Splitter/Merger | Export/Format | **Must-have** | Simple | No | None |
| 3.4 ARC PDF Generator | Export/Format | Nice-to-have | Medium | No | LibreOffice or reportlab |
| 4.1 Beta Reader Tracker | Tracking | **Must-have** | Simple | No | None |
| 4.2 ARC Distribution Log | Tracking | **Must-have** | Simple | No | None |
| 4.3 Editorial Revision Tracker | Tracking | **Must-have** | Simple | No | None |

**Build order recommendation:**

Phase 1 (before beta reading):
- 3.3 Chapter Splitter/Merger → 1.1 Word Count → 4.1 Beta Reader Tracker → 3.1 DOCX Exporter

Phase 2 (before DE submission):
- 1.2 Continuity Checker → 1.3 POV Tracker → 2.2 Repeated Word Detector → 4.3 Editorial Tracker

Phase 3 (before ARC distribution):
- 3.2 Atticus-Ready Export → 4.2 ARC Log → 1.4 Readability Pass

Phase 4 (polish):
- 2.1 Dialogue Tag Audit → 2.3 Italics Checker → 3.4 ARC PDF Generator

---

## Dependency Installation

```bash
# Required external dependencies (all others are stdlib)
pip install python-docx          # Tools 3.1, 3.2
pip install reportlab            # Tool 3.4 (optional — LibreOffice approach preferred)

# LibreOffice headless (Fedora/Ubuntu — for Tool 3.4 PDF generation)
# Fedora:
sudo dnf install libreoffice-headless
# Ubuntu:
sudo apt install libreoffice
```

---

## Repository Structure Recommendation

```
djinn-publish/
├── README.md
├── requirements.txt              # python-docx only; reportlab optional
├── style_guide_template.md       # blank template for Javier to fill
├── tracking/
│   ├── beta_readers.csv          # auto-created on first run
│   ├── arc_log.csv
│   └── editorial_log.csv
├── health/
│   ├── word_count.py             # Tool 1.1
│   ├── continuity_checker.py     # Tool 1.2
│   ├── pov_tracker.py            # Tool 1.3
│   └── readability.py            # Tool 1.4
├── style/
│   ├── dialogue_tags.py          # Tool 2.1
│   ├── repeat_detector.py        # Tool 2.2
│   └── italics_checker.py        # Tool 2.3
├── export/
│   ├── to_docx.py                # Tool 3.1
│   ├── to_atticus.py             # Tool 3.2
│   ├── chapter_split_merge.py    # Tool 3.3
│   └── arc_pdf.py                # Tool 3.4
└── tracking/
    ├── beta_tracker.py           # Tool 4.1
    ├── arc_log.py                # Tool 4.2
    └── editorial_tracker.py      # Tool 4.3
```

---

## Alignment Notes — TASK-069 Cross-Reference

| TASK-069 Decision | djinn-publish Tool That Serves It |
|-------------------|----------------------------------|
| Manuscript to beta readers → `.docx` | Tool 3.1 (Markdown → editorial DOCX) |
| Manuscript to Atticus for formatting | Tool 3.2 (Atticus-ready DOCX) |
| EPUB as primary ARC format | Not scripted — Atticus handles EPUB export; Tool 3.4 covers PDF ARC only |
| DE → CE → proof sequence | Tool 4.3 (editorial revision tracker) enforces this sequence |
| Beta reader process (4–6 weeks, 5–10 readers) | Tool 4.1 (beta reader tracker with deadline monitoring) |
| ARC distribution 6–8 weeks before pub date | Tool 4.2 (ARC log with date tracking) |
| Continuity/POV issues flagged before DE | Tools 1.2 and 1.3 (run manuscript health checks before sending to DE) |
| Copy edit targets word-level consistency | Tools 2.1, 2.2, 2.3 (run before or alongside CE to pre-flag obvious issues) |

---

## Notes on LLM Integration

Only Tools 1.2 (strict mode) invokes an LLM. All other tools are deterministic. This is intentional:

- **Deterministic tools are cheaper to run.** No API cost, no latency, no hallucination risk.
- **The writer should make judgment calls.** These tools produce a list of *candidates* for review, not automatic corrections. The flag is the output; the decision belongs to Javier.
- **LLM calls are reserved for genuine ambiguity.** The continuity checker's `--strict` mode is the only case where open-ended reasoning (semantic temporal contradiction) is genuinely required. Even then, results are cached by hash to avoid re-querying.
- **Future LLM integration hooks:** Tool 1.4 (readability) could optionally pipe flagged sentences to a model asking for alternative phrasing suggestions. Tool 2.2 (repeat detector) could optionally suggest synonyms. These are not specced here — they are Phase 2 enhancements, not MVP scope.

---

*Marcus — Perplexity AI research agent*
*Completed: 2026-06-16 20:00 PDT*
*Task: TASK-070 | Suite: Djinn Publishings Research | Queries: 4 research inputs read*
*Vault path: djinn/research/marcus/publishing/TASK-070_writing-pipeline-suite.md*
