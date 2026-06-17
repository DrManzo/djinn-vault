---
title: Session Report — djinn-paper Phase 1 MVP
agent: Claude
date: 2026-06-16
tags: [djinn, report, academic-writing, djinn-paper]
related: [[build-log]] [[decision-log]]
---

# Session Report — djinn-paper Phase 1 MVP

**Date:** 2026-06-16
**Agent:** Claude
**Session type:** Build
**Trigger:** TASK-069 research (Marcus) complete; Javier said "now" — build it immediately

---

## Summary

Built `djinn-paper`, the academic writing agent pipeline (Phase 1 MVP). Transforms raw draft text into formatted APA 7 or MLA 9 papers with deterministic Reference Builder and DOCX formatter plus an Ollama LLM rewrite pass. Reference Builder passes spec canonical test cases exactly. All deterministic paths verified end-to-end; LLM path ready but not tested with a real academic draft (no API key available, phi4 CPU-busy; defaults to qwen2.5:7b).

---

## What Was Built or Changed

**New repo:** `~/djinn-paper/` (standalone git, not inside Obsidian vault)

| File | Purpose |
|------|---------|
| `models.py` | Pydantic `SourceMetadata` schema — all source types (journal, book, chapter, website, YouTube, report, newspaper, dissertation, no-author, AI) |
| `references.py` | Rule-based Reference Builder — APA 7 + MLA 9 formatters for every source type; self-tests against spec's canonical examples |
| `prompts.py` | System prompt templates — master 7-step prompt + abstract generator |
| `docx_output.py` | Format Enforcer — `build_apa_docx()` and `build_mla_docx()`: title page, double-spacing, hanging-indent references, heading levels |
| `paper.py` | Main CLI — orchestrates load → LLM → rule-based references → DOCX → compliance report |
| `run` | venv wrapper script |
| `requirements.txt` | python-docx, pydantic, requests |

**Global CLI:** `~/.local/bin/djinn-paper` → wrapper to `~/djinn-paper/paper.py`

---

## Technical Decisions

**Standalone repo (not inside Obsidian vault)** — vault-enrich is concurrently committing during this build; same isolation pattern as djinn-publish.

**Reference Builder is deterministic Python, no LLM** — TASK-069 spec explicitly calls this out; rule-based formatters have deterministic correct outputs and self-test against spec's own examples.

**DOCX Format Enforcer is deterministic, no LLM** — same reasoning; python-docx handles all formatting mechanically.

**Default model: qwen2.5:7b** — No ANTHROPIC_API_KEY set; phi4:14b is CPU-bound running vault-enrich batch. qwen2.5:7b is lighter, available, and instruction-following capable. Override with `--model`.

**`--no-llm` flag** — allows testing and use of the deterministic path (reference building + DOCX) without an Ollama server; enables offline use and fast iteration.

**MLA double-period fix** — first-name initials like "Jean M." already end with "."; added `_mla_author_tag()` helper to avoid "Jean M.." in output.

**`_mla_author_tag()` helper** — strips/handles trailing period from author strings before formatting.

---

## Files Created or Modified

```
~/djinn-paper/                     ← new standalone git repo
  models.py                        ← Pydantic SourceMetadata schema
  references.py                    ← Rule-based APA7 + MLA9 reference builder
  prompts.py                       ← Master system prompt + abstract prompt
  docx_output.py                   ← DOCX format enforcer
  paper.py                         ← Main CLI
  requirements.txt
  run                              ← venv wrapper
  .gitignore
~/.local/bin/djinn-paper           ← global CLI wrapper
```

---

## Tests & Validation

**Reference Builder self-tests (Section 9 spec canonical examples):**
- APA 7 journal article: PASS — `Smith, J. (2019). Cognitive load in online learning. *Journal of Educational Psychology*, *112*(3), 445–467. https://doi.org/10.1037/edu0000412`
- MLA 9 journal article: PASS — `Smith, Jane. "Cognitive Load in Online Learning." *Journal of Educational Psychology*, vol. 112, no. 3, 2019, pp. 445–467.`

**End-to-end `--no-llm` test (APA 7):**
- 2 sources loaded (Twenge 2018 journal, Twenge 2017 book)
- Markdown output: correct title page header, correct reference entries, alphabetized
- DOCX: 19 paragraphs, correct structure (title page → body → References)
- QA: correctly flagged 2 uncited references (expected, since raw draft has no in-text citations)

**End-to-end `--no-llm` test (MLA 9):**
- Correct header block (author/instructor/course/date Day Month Year format)
- Works Cited with correct formatting, no double-period issue after initials

---

## Known Issues

- **Title case on unconventionally-cased proper nouns** — `iGen` becomes `IGen` via automated title case. No automatic fix; user should normalize source titles before passing to sources.json.
- **LLM path untested with real academic draft** — no API key, phi4 busy. The qwen2.5:7b path is wired correctly but needs a real use case to validate output quality.
- **APA sentence case doesn't preserve proper nouns** — algorithm lowercases all words except first word and post-colon first word; proper nouns must be manually corrected in the LLM output.
- **MLA "Accessed" date** — website entries require `access_date` field in source JSON; if absent, the date is silently omitted (correct per spec, but user may forget to include it).

---

## What's Next

1. **Test LLM path** — provide a real academic draft + source list, run with qwen2.5:7b, validate rewrite quality
2. **Phase 2** — break into 6 sub-agents, add CrossRef/Semantic Scholar source finder, annotated bibliography
3. **phi4 switch** — once vault-enrich batch completes, switch default to phi4:14b for better instruction following
4. **Pandoc template** — APA 7 Pandoc DOCX reference document for clean conversion from Markdown

— Claude
