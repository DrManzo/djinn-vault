# TASK-069 — Academic & School Writing Agent Suite
**Assigned to:** Marcus  
**Status:** done  
**Priority:** high  
**Created:** 2026-06-16 by Javier  
**Completed:** 2026-06-16 by Marcus (Perplexity)  
**Output:** Full research corpus for building academic writing agents that transform raw "word vomit" drafts into polished APA 7th and MLA 9th formatted papers — all bells and whistles. 15 sections covering both style guides, agent architecture, prompting strategies, citation generation, plagiarism detection, source integration, sentence restructuring, abstract writing, section scaffolding, and the complete pipeline design for Djinn.

---

## 1. The Core Problem — What the Agent Needs to Solve

### What "Word Vomit to Formatted Paper" Actually Means
The user dumps raw content: stream-of-consciousness arguments, bullet-point notes, half-finished paragraphs, copy-pasted facts with no sources, ideas in the wrong order. The agent must do all of the following in a single pipeline or as composable sub-agents:

1. **Understand intent** — extract the thesis/argument from unstructured text
2. **Impose structure** — identify what is intro, body, argument, evidence, conclusion
3. **Rewrite for academic register** — elevate language from casual to formal scholarly tone without losing the author's voice
4. **Insert in-text citations** — identify claims that need sourcing, attach properly formatted citations
5. **Generate a Works Cited / References page** — APA 7 or MLA 9, correct format, alphabetized
6. **Enforce style rules** — heading levels, running heads, page numbers, margins, font specs, line spacing
7. **Check for plagiarism signals** — flag overly verbatim passages that need paraphrasing
8. **Generate optional extras** — abstract, keywords, title page, annotated bibliography, outline

This is a **multi-stage NLP + formatting pipeline**, not a single prompt. Each of the above is a discrete agent task.

---

## 2. APA 7th Edition — Complete Specification

### What APA 7 Is
APA (American Psychological Association) 7th Edition (2020) is the dominant citation and style system for the social sciences, behavioral sciences, nursing, education, and business. GCU (Grand Canyon University) requires APA 7 for nearly all papers. San Bernardino Valley College courses in psychology, sociology, education, and many sciences use APA.

**Authoritative source:** *Publication Manual of the American Psychological Association, 7th Edition* (2020). ISBN: 978-1-4338-3215-4. Available at apastyle.apa.org.

### APA 7 Paper Structure
| Section | Required? | Notes |
|---------|-----------|-------|
| Title Page | Always | Title, author name, institutional affiliation, course, instructor, date |
| Abstract | Research papers | 150–250 words, no indent, Keywords line below |
| Body | Always | Introduction (unlabeled in APA), then labeled headings |
| References | Always | New page, centered "References" heading, hanging indent |
| Appendices | Optional | Label "Appendix A," "Appendix B," etc. |
| Footnotes | Optional | Content notes or copyright attribution only |
| Tables/Figures | Optional | Each on its own page or embedded |

### APA 7 Formatting Rules (The Machine Must Know All of These)

**Page Setup:**
- Margins: 1 inch on all sides
- Font: 12-pt Times New Roman OR 11-pt Calibri OR 11-pt Arial OR 10-pt Lucida Sans Unicode OR 11-pt Georgia
- Line spacing: Double-spaced throughout (including References)
- Paragraph indent: 0.5 inch first line (except abstract, block quotes, headings, title page, references)
- Page numbers: Top right header, starting from page 1 (title page = page 1)
- Running head: Required ONLY for manuscripts being submitted for publication — NOT required for student papers. Student papers do NOT need a running head.

**Title Page (Student Version):**
```
[Centered, bold]
Title of Paper: With Subtitle if Any

[Blank line]
Author First Last
Department of [Field], University Name
COURSE-NUMBER: Course Title
Instructor Name
Month Day, Year
```

**APA 7 Heading Levels:**
| Level | Format |
|-------|--------|
| Level 1 | **Bold, Centered, Title Case** |
| Level 2 | **Bold, Left-Aligned, Title Case** |
| Level 3 | **Bold, Italic, Left-Aligned, Title Case** |
| Level 4 | **Bold, Indented, Ends with Period.** Paragraph continues on same line. |
| Level 5 | **Bold, Italic, Indented, Ends with Period.** Paragraph continues on same line. |

**In-Text Citations:**
- Author-date system: (Smith, 2019) or Smith (2019)
- Direct quote: (Smith, 2019, p. 45) or (Smith, 2019, pp. 45–46)
- No author: Use abbreviated title in quotes ("Study Title," 2020)
- Two authors: (Smith & Jones, 2019) — always use ampersand in parentheses, "and" in prose
- Three or more authors: (Smith et al., 2019) — always use et al. from first mention in APA 7
- Organization as author: First citation (American Psychological Association [APA], 2020), subsequent (APA, 2020)
- No date: (Smith, n.d.)
- Multiple works in one citation: alphabetical by author, semicolons: (Jones, 2018; Smith, 2019)
- Secondary source (citing a source within a source): (Watson, 1929, as cited in Smith, 2019)

**Block Quotes (APA 7):**
- Use for direct quotes of 40+ words
- Indent entire block 0.5 inch from left margin
- No quotation marks
- Citation goes AFTER the final period: (Smith, 2019, p. 45)

### APA 7 Reference List Formats

**Journal Article:**
```
Author, A. A., & Author, B. B. (Year). Title of article with only first word capitalized and proper nouns. Journal Name in Italics, Volume(Issue), Page–Page. https://doi.org/xxxxx
```

**Book:**
```
Author, A. A. (Year). Title of book in italics: Subtitle. Publisher.
```

**Book Chapter (Edited):**
```
Author, A. A. (Year). Title of chapter. In E. E. Editor (Ed.), Title of book in italics (pp. xx–xx). Publisher.
```

**Website / Webpage:**
```
Author, A. A. (Year, Month Day). Title of page. Site Name. URL
```
Note: If no individual author, organization name goes first. If content is likely to change, include retrieval date.

**YouTube Video:**
```
Channel Name. (Year, Month Day). Title of video [Video]. YouTube. URL
```

**Report (Government or Organization):**
```
Organization Name. (Year). Title of report (Report No. xxx). Publisher. URL
```

**No Author:**
```
Title of work. (Year). Publisher.
```

**Key APA 7 Changes from 6th Edition (The Agent Must Know):**
- Three or more authors: now ALWAYS et al. from first mention (was "up to 5 listed first time" in 6th)
- DOI formatted as hyperlink: https://doi.org/xxxx (not "doi:" prefix)
- Running head: no longer required for student papers
- Publisher location: no longer included for books
- ISBN: not included in references
- Up to 20 authors listed in reference list (was 7 in 6th edition); for 21+ use first 19, ellipsis, last author

---

## 3. MLA 9th Edition — Complete Specification

### What MLA 9 Is
MLA (Modern Language Association) 9th Edition (2021) dominates the humanities: English, literature, language, cultural studies, media studies, and many history courses. If Javier takes English comp, literature, or communications courses at SBVC, those will be MLA.

**Authoritative source:** *MLA Handbook, 9th Edition* (2021). ISBN: 978-1-60329-286-7. Available at style.mla.org.

### MLA 9 Paper Structure
Unlike APA, MLA student papers do NOT have a separate title page by default. Instead:

**Header block (top-left, double spaced):**
```
First Last
Professor Name
Course Name and Number
Day Month Year
```

**Title:** Centered, standard title case, no bold/italic/underline (unless title contains a work that would normally be italicized).

**Running Header:** Author's Last Name + space + page number, top right. Example: `Manzo 3`

**Works Cited:** On a new page. Centered "Works Cited" heading. Hanging indent 0.5 inch. Alphabetical by first element.

### MLA 9 Formatting Rules
- Margins: 1 inch all sides
- Font: 12-pt Times New Roman (traditional standard; clean readable font)
- Line spacing: Double-spaced throughout, including Works Cited
- Paragraph indent: 0.5 inch first line
- No extra spacing between paragraphs
- Page numbers: Last Name + page number, top right (e.g., Manzo 3)
- NO title page for standard student papers
- NO abstract for standard student papers

### MLA 9 In-Text Citations
- Author-page system: (Smith 45) or Smith argues (45)
- No comma between author and page number
- No "p." before page numbers
- Block quotes (4+ lines of prose or 3+ lines of poetry): indent 0.5 inch, no quotation marks, citation AFTER final period
- No author: abbreviated title in quotes ("Article Title" 23)
- Multiple works in one citation: (Smith 45; Jones 89)

### MLA 9 Works Cited — The "Container" Model
MLA 9 uses a flexible "containers" framework. A source can be inside multiple containers (e.g., an article is in a journal, which is accessed through a database).

**Core elements (in order):**
1. Author.
2. *Title of Source.*
3. Title of Container,
4. Other contributors,
5. Version,
6. Number,
7. Publisher,
8. Publication date,
9. Location (page numbers, URL, DOI).

**Journal Article:**
```
Smith, Jane. "Article Title in Quotes." Journal Name in Italics, vol. 12, no. 3, 2020, pp. 45–67.
```

**Book:**
```
Smith, Jane. Book Title in Italics. Publisher, Year.
```

**Website:**
```
Smith, Jane. "Page Title." Website Name, Day Month Year, URL. Accessed Day Month Year.
```

**YouTube Video:**
```
Channel Name. "Video Title." YouTube, Day Month Year, URL.
```

**Essay in Edited Collection:**
```
Smith, Jane. "Essay Title." Collection Title, edited by John Doe, Publisher, Year, pp. 45–67.
```

**MLA 9 Key Changes from 8th Edition:**
- Inclusive language guidance updated
- "Accessed" date for URLs now strongly recommended
- In-text citation and Works Cited alignment tightened
- New guidance for live performances, social media, apps, and generative AI citation

### MLA 9 — Citing AI-Generated Content
MLA 9 added guidance (2023 update) for citing generative AI:
```
OpenAI. "[Description of query]." ChatGPT, version used, OpenAI, date of generation, URL.
```
For Djinn's outputs being used as sources: this applies. The agent should be aware of this edge case.

---

## 4. APA vs. MLA — Side-by-Side Decision Engine

| Feature | APA 7 | MLA 9 |
|---------|-------|-------|
| Disciplines | Psychology, social sciences, education, nursing, business | English, humanities, literature, language arts |
| Citation system | Author-date: (Smith, 2019) | Author-page: (Smith 45) |
| Reference list title | **References** | **Works Cited** |
| Title page | Yes (student version) | No (header block only) |
| Abstract | Yes (150–250 words) | No |
| Running head | No (student papers) | Yes (Last Name + page #) |
| Heading levels | 5 levels, bold/italic system | No formal heading system |
| Three+ authors | et al. from first mention | All authors listed (up to a point) |
| Page numbers in citations | Yes (p. 45) | No "p." prefix: (Smith 45) |
| DOI/URL format | https://doi.org/xxx | Full URL or DOI |

**Agent decision logic:** When Javier passes in a paper, the agent should check the course/professor instructions or ask: "Is this psychology/social science (APA) or English/humanities (MLA)?" Make this a required input before formatting.

---

## 5. Agent Architecture — The Writing Pipeline

### Recommended Multi-Agent Pipeline Design

For the Djinn ecosystem, the academic writing agent should be designed as a **pipeline of specialist sub-agents**, not one monolithic prompt. This maps to how Djinn's agent-specialist pattern already works.

```
Input: Raw Draft (word vomit)
       |
       v
[AGENT 1: Intake & Structure Analyzer]
 - Extract thesis
 - Identify argument structure
 - Tag each paragraph: intro / claim / evidence / transition / conclusion
 - Flag missing sections
       |
       v
[AGENT 2: Academic Register Rewriter]
 - Elevate informal language to formal scholarly tone
 - Remove first-person unless required (discipline-dependent)
 - Fix grammar, syntax, wordiness
 - Preserve Javier's core argument and voice
       |
       v
[AGENT 3: Citation Injector]
 - Identify all factual claims requiring citations
 - Accept source list from user OR search for sources via API
 - Insert in-text citations (APA or MLA format)
       |
       v
[AGENT 4: Reference Builder]
 - Take all sources cited
 - Generate fully formatted References (APA) or Works Cited (MLA) page
 - Sort alphabetically
 - Apply hanging indent markup
       |
       v
[AGENT 5: Format Enforcer]
 - Apply title page (APA) or header block (MLA)
 - Apply heading levels
 - Apply running header, page numbers
 - Ensure margins, font, spacing in output format (DOCX, Markdown, LaTeX)
       |
       v
[AGENT 6: QA & Compliance Checker]
 - Verify every in-text citation has a reference entry
 - Verify every reference entry has at least one in-text citation
 - Flag orphaned citations or references
 - Check word count, abstract length
 - Generate compliance report
       |
       v
Output: Formatted Academic Paper
        + Compliance Report
        + Optional: Abstract, Keywords, Outline, Annotated Bibliography
```

### System Prompt Requirements for Each Sub-Agent

Every sub-agent in this pipeline needs a system prompt that includes:
- Which style guide is active (APA 7 or MLA 9)
- The academic level (undergraduate, graduate)
- The institution (GCU requires APA 7; certain SBVC classes may specify MLA)
- The discipline
- The output format (Markdown → DOCX, raw text, LaTeX)
- Preservation instructions: "Maintain the author's core arguments; do not fabricate claims"

---

## 6. Agent 1 — Intake and Structure Analyzer

### What It Must Do
This is the most critical agent because the entire pipeline depends on understanding the raw input correctly.

**Tasks:**
1. **Thesis extraction** — identify the central claim(s). If none is clear, flag for user input.
2. **Argument mapping** — identify supporting points, counterarguments, evidence passages.
3. **Section tagging** — label each paragraph or cluster as: title claim, background, literature review, methodology, argument, evidence, analysis, counterargument, rebuttal, conclusion.
4. **Gap detection** — identify what's missing. "This paper has no concluding paragraph." "No evidence is cited for Claim 2."
5. **Outline generation** — produce a structured outline from the raw material.

**System Prompt Template — Agent 1:**
```
You are an academic writing structure analyst. You will receive unstructured draft text.

Your job is:
1. Extract the central thesis or argument.
2. Identify each distinct idea or claim.
3. Map the logical flow: which ideas support the thesis, which are tangential, which are missing.
4. Tag each paragraph with its function: [INTRO], [BACKGROUND], [CLAIM], [EVIDENCE], [ANALYSIS], [COUNTERARGUMENT], [REBUTTAL], [TRANSITION], [CONCLUSION].
5. List any critical missing components.
6. Produce a structured outline.

Style guide active: {APA_7 | MLA_9}
Academic level: {undergraduate | graduate}
Discipline: {user_input}

Do NOT rewrite the text. Only analyze and map it.
Do NOT add information that is not in the draft.
Do NOT fabricate sources.
```

---

## 7. Agent 2 — Academic Register Rewriter

### What "Academic Register" Means
Register = the level and style of language appropriate to a context. Academic register in English is characterized by:
- Formal vocabulary ("demonstrate" not "show"; "utilize" not "use" — though "use" is now preferred in APA style over "utilize")
- Complex but clear sentence structure
- Hedged language for claims with uncertain evidence: "suggests," "may indicate," "evidence supports"
- Passive voice used selectively (more common in science writing; APA actually encourages active voice now)
- No contractions, slang, or colloquialisms
- Precise terminology from the discipline
- Logical transitions between ideas

### What to Rewrite vs. Preserve
**Rewrite:**
- Contractions ("it's" → "it is")
- Slang ("super important" → "critically significant")
- Run-on sentences
- Missing transitions
- Unsupported absolute claims ("always," "never") → hedge appropriately
- First-person casual usage (context-dependent; APA 7 now encourages "I" in appropriate contexts)

**Preserve:**
- Core argument and thesis — do NOT change what the author is arguing
- Discipline-specific jargon used correctly
- Specific examples or case studies provided by the author
- The author's organizational choices (unless they violate the style guide)

**System Prompt Template — Agent 2:**
```
You are an academic writing editor specializing in {APA_7 | MLA_9} style.
You will receive tagged draft text from the structure analyzer.

Your job:
1. Rewrite each tagged section to meet formal academic register standards.
2. Fix grammar, punctuation, and syntax errors.
3. Eliminate contractions, slang, and informal language.
4. Improve transitions between paragraphs and sections.
5. Ensure the introduction ends with a clear thesis statement.
6. Ensure the conclusion restates the thesis and synthesizes (does not merely summarize).
7. Use hedged language for uncertain claims.
8. Preserve the author's core argument exactly — do not change what they are arguing.
9. Do NOT add new claims, evidence, or sources.
10. Flag any passage that is ambiguous enough that rewriting risks distorting meaning — return those to the user for clarification.

Style rules:
- {APA}: Use active voice where possible. Use "I" only in appropriate reflexive contexts. Avoid editorial "we."
- {MLA}: Third-person preferred for literary analysis. Use present tense for discussing texts.
- Both: No contractions. No first-person unless discipline/instructor requires it.
```

---

## 8. Agent 3 — Citation Injector

### The Hardest Part of the Pipeline
The citation injector is the most technically complex component because it must:
1. Identify which claims in the paper require citations
2. Match claims to sources the user has provided
3. Format the in-text citation correctly
4. Handle cases where the user has NOT provided a source (flag, don't fabricate)

### Citation Need Detection — Heuristics
The agent should flag for citation any sentence that:
- Makes a statistical claim ("X% of people...")
- Attributes an idea to a theory, study, or school of thought
- States a historical fact that is not common knowledge
- Makes a causal claim ("research shows that X causes Y")
- Quotes or paraphrases another author's specific words or ideas
- Defines a technical term in a way attributed to a specific source

Sentences that do NOT need citations:
- Common knowledge ("The Earth orbits the Sun")
- The author's own analysis or argument
- Logical conclusions drawn from already-cited evidence
- Definitions in a general dictionary (though discipline-specific definitions still need sources)

### Citation Matching System
The agent should accept sources in two ways:
1. **User-provided source list** — user gives a list of sources (title, author, year, URL/DOI) and the agent matches each claim to the most relevant source.
2. **AI-assisted source suggestion** — agent flags uncited claims and suggests what type of source is needed: "This claim about cognitive dissonance needs a primary psychology study — please provide a source or I can suggest search terms."

**Do NOT fabricate sources.** This is non-negotiable and must be hardcoded into the system prompt. Hallucinated citations are academically catastrophic.

**System Prompt Template — Agent 3:**
```
You are an academic citation specialist for {APA_7 | MLA_9}.
You will receive rewritten academic text and a list of sources provided by the user.

Your job:
1. Identify every claim that requires a citation (statistical, theoretical, quoted, paraphrased, attributed).
2. For each claim that needs a citation, match it to the most appropriate source from the provided source list.
3. Insert correctly formatted in-text citations.
4. For claims with no matching source, insert [CITATION NEEDED: describe what type of source is needed].
5. Format block quotes correctly for passages 40+ words (APA) or 4+ lines (MLA).
6. Do NOT fabricate any source, author name, title, date, page number, DOI, or URL.
7. Do NOT remove a claim because it lacks a citation — flag it instead.

Source list provided by user:
{user_source_list}

Format: {APA_7 | MLA_9}
```

---

## 9. Agent 4 — Reference Page Builder

### What It Must Generate
The reference page builder takes all cited sources and produces a perfectly formatted References (APA) or Works Cited (MLA) page.

**Input:** List of source metadata objects:
```json
{
  "author_last": "Smith",
  "author_first": "Jane",
  "year": 2019,
  "title": "Cognitive Load in Online Learning",
  "source_type": "journal_article",
  "journal": "Journal of Educational Psychology",
  "volume": 112,
  "issue": 3,
  "pages": "445-467",
  "doi": "10.1037/edu0000412"
}
```

**Output (APA 7):**
```
Smith, J. (2019). Cognitive load in online learning. Journal of Educational Psychology, 112(3), 445–467. https://doi.org/10.1037/edu0000412
```

**Output (MLA 9):**
```
Smith, Jane. "Cognitive Load in Online Learning." Journal of Educational Psychology, vol. 112, no. 3, 2019, pp. 445–467.
```

### Source Type Coverage — The Agent Must Handle All of These

| Source Type | APA 7 Pattern | MLA 9 Pattern |
|-------------|--------------|---------------|
| Journal article (with DOI) | Author, A. (Year). Title. Journal, Vol(Iss), pp. DOI | Author. "Title." Journal, vol., no., year, pp. |
| Journal article (no DOI, with URL) | Author, A. (Year). Title. Journal, Vol(Iss), pp. URL | Author. "Title." Journal, vol., no., year, pp. URL. |
| Book | Author, A. (Year). Title. Publisher. | Author. Title. Publisher, Year. |
| Book chapter (edited) | Author, A. (Year). Chapter. In Ed (Ed.), Book (pp.). Publisher. | Author. "Chapter." Book, edited by Ed, Publisher, Year, pp. |
| Website | Author. (Year, Month Day). Title. Site. URL | Author. "Title." Site, Date, URL. Accessed Date. |
| YouTube video | Channel. (Year, Month Day). Title [Video]. YouTube. URL | Channel. "Title." YouTube, Date, URL. |
| Government report | Agency. (Year). Title (Report No.). URL | Agency. Title. Year, URL. |
| Newspaper article | Author. (Year, Month Day). Title. Paper. URL | Author. "Title." Newspaper, Date, URL. |
| Dissertation | Author. (Year). Title [Doctoral dissertation, University]. Database. | Author. Title. Year, University, database or URL. |
| No author | Title. (Year). Publisher. | Title. Publisher, Year. |
| No date (APA) | Author. (n.d.). Title. Publisher. | N/A — MLA uses full date |
| AI-generated content | See APA AI citation guidance | See MLA AI citation guidance |

### Sorting and Hanging Indent
- Sort alphabetically by first author's last name
- If same author: sort by year, earliest first
- If same author AND same year (APA): add a, b, c suffixes: (Smith, 2019a), (Smith, 2019b)
- **Hanging indent:** First line flush left, all subsequent lines indented 0.5 inch. This must be in the output format (DOCX paragraph formatting, LaTeX `\bibitem`, or Markdown with `   ` continuation indent).

---

## 10. Agent 5 — Format Enforcer

### What Format Enforcement Means
Formatting is the last stage — after content is correct, citations are in, references are built. The format enforcer applies the visual and structural rules.

### APA 7 Student Paper Checklist (What the Agent Enforces)
- [ ] Title page with title (bold, centered), author, affiliation, course number, instructor, date
- [ ] Abstract page (if required): "Abstract" heading (bold, centered), 150–250 words, Keywords line
- [ ] Body begins on new page, introduction text begins immediately (no "Introduction" heading in APA)
- [ ] Headings: Level 1 bold centered, Level 2 bold left, Level 3 bold italic left
- [ ] In-text citations: author-date format throughout
- [ ] No extra spacing between paragraphs
- [ ] References on a new page, "References" heading bold centered
- [ ] References double-spaced, hanging indent
- [ ] Page numbers top right from page 1
- [ ] Font and size consistent throughout
- [ ] 1-inch margins all sides

### MLA 9 Student Paper Checklist
- [ ] Header block top-left: student name, professor, course, date (Day Month Year)
- [ ] Title centered, no special formatting
- [ ] Running header: Last Name + page number, top right
- [ ] Body text double-spaced, 0.5 indent
- [ ] Works Cited on new page, "Works Cited" centered
- [ ] Works Cited alphabetical, hanging indent
- [ ] Consistent font
- [ ] 1-inch margins

### Output Formats the Agent Should Support

| Format | Tool/Method | Notes |
|--------|------------|-------|
| **DOCX** | Python `python-docx` library | Full formatting support: margins, font, heading styles, headers/footers, hanging indent |
| **Markdown** | Standard Markdown + Pandoc | Good for vault storage; convert to DOCX/PDF via Pandoc with custom template |
| **LaTeX** | Custom .tex template | Best for math-heavy papers; BibTeX for references |
| **PDF** | Pandoc or WeasyPrint | Convert from DOCX or LaTeX; final submission format |
| **Google Docs** | Google Docs API | For cloud-based workflow |

**Recommended for Djinn:** Markdown as working format + Pandoc to DOCX for submission. This keeps everything in the vault as readable text and produces clean Word documents.

---

## 11. Agent 6 — QA and Compliance Checker

### What the QA Agent Verifies

**Citation-Reference Parity:**
- Every (Author, Year) or (Author page) in the body must have a matching entry in References/Works Cited
- Every entry in References/Works Cited must be cited at least once in the body
- Mismatches are flagged with line numbers

**APA-Specific Checks:**
- et al. rule: 3+ authors → et al. in ALL in-text citations
- Ampersand in parenthetical citations: (Smith & Jones, 2019) — never "and"
- "and" in prose: Smith and Jones (2019) argue — never "&"
- No "ibid." or "op. cit." — repeat full citation each time in APA
- Abstract is 150–250 words (flag if outside range)
- Running head absent (student papers)

**MLA-Specific Checks:**
- No comma between author and page in parenthetical: (Smith 45) not (Smith, 45)
- No "p." before page numbers in parenthetical
- Works Cited (not "Bibliography" or "References") is the correct title
- Works Cited is alphabetical
- "Accessed" date included for URLs

**General Academic Writing Quality Checks:**
- Paragraph length (flag paragraphs under 3 sentences or over 15 sentences)
- Transition words present between major sections
- Conclusion does not introduce new claims or evidence
- Introduction ends with a thesis statement (agent identifies and confirms this)
- No direct quotes exceeding 10% of total word count (academic guideline)

**Compliance Report Output Format:**
```markdown
## Compliance Report — [Paper Title]
**Style Guide:** APA 7 / MLA 9  
**Date:** YYYY-MM-DD  

### PASSED
- [x] Title page present and correctly formatted
- [x] Abstract: 203 words (within 150–250 range)
- [x] All in-text citations have matching reference entries

### WARNINGS
- [ ] Paragraph 4 (Body Section 2): No in-text citation for statistical claim on line 47
- [ ] Reference #3 (Johnson, 2021): No in-text citation found
- [ ] Abstract: 267 words (exceeds 250-word limit)

### ERRORS
- [!] In-text citation (Smith & Jones, 2019) — Reference list shows "Smith and Jones" — fix to "Smith & Jones"

### SUGGESTIONS
- Conclusion paragraph introduces new evidence (last paragraph). Consider moving to body.
- 3 block quotes present. Ensure no more than 1–2 per paper for original analysis priority.
```

---

## 12. Bonus Modules — Bells and Whistles

### 12.1 Abstract Generator
For APA papers requiring an abstract:
- Input: completed paper body
- Output: 150–250 word abstract summarizing purpose, method (if applicable), findings, and implications
- APA abstract structure: Background → Purpose → Method/Approach → Results/Main Points → Conclusion/Implications
- No citations in abstract
- No first-person in abstract
- Keywords line: 3–5 keywords, lowercase (except proper nouns), separated by commas

**System Prompt Template — Abstract Generator:**
```
You are an APA 7 abstract writer. You will receive a completed academic paper.
Write an abstract of 150–250 words that:
1. States the purpose of the paper in the first sentence
2. Describes the approach or argument
3. Summarizes the main findings or claims
4. States the implications or conclusions
Do NOT include citations in the abstract.
Do NOT use first-person pronouns.
Do NOT copy entire sentences verbatim from the paper.
After the abstract, write a Keywords line: 3–5 keywords, lowercase, comma-separated.
Format: Keywords: keyword one, keyword two, keyword three
```

### 12.2 Annotated Bibliography Generator
An annotated bibliography combines the reference entry with a brief (150–200 word) annotation describing:
- The source's main argument or content
- The methodology (for empirical sources)
- How it relates to the paper's topic
- Any limitations or biases

**Format (APA 7 Annotated):**
```
Smith, J. (2019). Cognitive load in online learning. Journal of Educational Psychology, 112(3), 445–467. https://doi.org/10.1037/edu0000412

   This study examines the relationship between cognitive load theory and student 
   performance in asynchronous online learning environments. Smith employs a 
   randomized controlled trial with 240 undergraduate participants across three 
   course formats. The findings indicate that segmented video content significantly 
   reduces extraneous cognitive load (p < .001). This source directly supports the 
   paper's argument that instructional design choices affect learning outcomes. 
   Limitations include a single-institution sample that may limit generalizability.
```

### 12.3 Outline Generator
The outline agent takes the structured analysis from Agent 1 and produces a formal academic outline:

**APA-style outline format:**
```
I. Introduction
   A. Background on [topic]
   B. Problem statement
   C. Thesis: [exact thesis statement]

II. [First Major Section Title]
   A. [Subtopic 1]
      1. [Supporting point]
      2. [Supporting point]
   B. [Subtopic 2]
...

IV. Conclusion
   A. Restatement of thesis
   B. Synthesis of findings
   C. Implications for future research/practice
```

### 12.4 Paraphrase Checker (Anti-Plagiarism Module)
This module scans the paper for passages that are too close to source material:
- Input: paper text + source texts (if available)
- Flags passages that share more than 5 consecutive words with a source
- Suggests paraphrase rewrites
- Notes: this is a local heuristic check, not a full plagiarism database check. For institutional submission, tools like Turnitin or iThenticate are the standard. This agent module is for pre-submission self-review.

**Integration note:** If Javier wants full plagiarism detection, the agent can be connected to the Copyleaks API or PlagiarismCheck API, both of which have Python SDKs and reasonable pricing.

### 12.5 Source Finder Module
For claims flagged as [CITATION NEEDED], an optional source-finder module can:
1. Take the claim text
2. Generate a search query for Google Scholar, Semantic Scholar, or PubMed
3. Return candidate sources with title, author, year, abstract snippet
4. Let Javier select which source to use
5. Feed the selected source into the Reference Builder

**APIs to use:**
- **Semantic Scholar API** — free, no key required for basic use, returns structured metadata including DOI, authors, year, abstract. URL: `https://api.semanticscholar.org/graph/v1/paper/search`
- **PubMed E-utilities** — free, for medical/science sources. `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- **CrossRef API** — free, returns DOI-linked metadata. `https://api.crossref.org/works?query=`
- **Google Scholar** — no official API; use `scholarly` Python library for limited scraping

### 12.6 Style Guide Switcher
The agent should be able to convert a fully formatted APA paper to MLA or vice versa:
- Convert in-text citations from author-date to author-page (requires page number data — flag if missing)
- Reformat reference list to alternate style
- Swap title page for header block (or vice versa)
- Remove/add abstract
- Adjust heading structure

This is a power feature for when a student submits the same paper to a class that uses a different style guide.

---

## 13. Technical Implementation — Python Stack

### Core Libraries

| Library | Purpose | Install |
|---------|---------|--------|
| `python-docx` | Generate and format DOCX files | `pip install python-docx` |
| `pypandoc` | Convert Markdown/DOCX/LaTeX/PDF | `pip install pypandoc` + Pandoc binary |
| `bibtexparser` | Parse and generate BibTeX for LaTeX | `pip install bibtexparser` |
| `habanero` | CrossRef API client for DOI lookup | `pip install habanero` |
| `scholarly` | Google Scholar search (unofficial) | `pip install scholarly` |
| `pyalex` | OpenAlex API (free, comprehensive academic metadata) | `pip install pyalex` |
| `requests` | Semantic Scholar and CrossRef API calls | Standard library |
| `langchain` | LLM pipeline orchestration | `pip install langchain` |
| `ollama` (Python) | Local model calls for Javier's Ollama setup | `pip install ollama` |
| `pydantic` | Schema validation for source metadata objects | `pip install pydantic` |
| `jinja2` | Template rendering for reference formats | `pip install jinja2` |

### Recommended Architecture Pattern for Djinn

```python
# Pseudocode — Djinn Academic Writing Agent

class AcademicWritingAgent:
    def __init__(self, style: Literal["APA7", "MLA9"], model: str):
        self.style = style
        self.model = model  # e.g., "llama3.1", "gemma3", "claude-3-5-sonnet"
        self.agents = [
            StructureAnalyzerAgent(style, model),
            RegisterRewriterAgent(style, model),
            CitationInjectorAgent(style, model),
            ReferenceBuilderAgent(style),  # Rule-based, no LLM needed
            FormatEnforcerAgent(style),    # Rule-based
            QACheckerAgent(style, model),
        ]

    def run(self, raw_draft: str, sources: list[SourceMetadata]) -> PaperOutput:
        result = raw_draft
        for agent in self.agents:
            result = agent.process(result, sources)
        return result
```

**Key design decision:** The Reference Builder and Format Enforcer should be **rule-based, not LLM-based**. These have deterministic correct outputs — using an LLM for them introduces hallucination risk. Use Python string templates and python-docx formatting calls instead.

The LLM is appropriate for:
- Structure analysis (judgment call)
- Register rewriting (generative)
- Citation injection (matching/judgment)
- QA compliance check (judgment)
- Abstract generation (generative)

### DOCX Generation with python-docx — Key Patterns

```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Set margins (APA: 1 inch all sides)
section = doc.sections[0]
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(1)
section.right_margin = Inches(1)

# Set default font (Times New Roman 12pt)
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Add title page
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("Paper Title Here")
run.bold = True
run.font.name = 'Times New Roman'
run.font.size = Pt(12)

# Add page break
doc.add_page_break()

# Add References heading
ref_heading = doc.add_paragraph("References")
ref_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
ref_heading.runs[0].bold = True

# Add reference entry with hanging indent
para = doc.add_paragraph()
para.paragraph_format.left_indent = Inches(0.5)
para.paragraph_format.first_line_indent = Inches(-0.5)  # Hanging indent
para.paragraph_format.space_after = Pt(0)
para.add_run("Smith, J. (2019). ...")

doc.save("paper_output.docx")
```

### Pandoc Command for Converting Markdown to Formatted DOCX
```bash
pandoc input.md \
  --reference-doc=apa7_template.docx \
  -o output.docx \
  --metadata title="Paper Title"
```
Create `apa7_template.docx` once with all correct APA styles set, then Pandoc applies them to any Markdown input.

---

## 14. GCU and SBVC Specific Notes

### Grand Canyon University (GCU) — APA Requirements
GCU uses APA 7th Edition for virtually all undergraduate and graduate papers. GCU-specific deviations and requirements:
- **GCU Style Guide** supplements APA 7 — available at library.gcu.edu. Some assignments have GCU-specific title page formatting.
- GCU title page typically requires: paper title, student name, course number and name, instructor name, university, and date — centered and double-spaced.
- GCU assignments often require a **minimum number of peer-reviewed sources** — this should be a QA check in the agent.
- GCU uses **SafeAssign** (Blackboard's plagiarism checker) for submission — the paraphrase checker module is directly relevant for pre-submission checking.
- **GCU writing center:** writingcenter.gcu.edu — resource for templates and style guides.

### San Bernardino Valley College (SBVC) — Style Variation
- SBVC English composition courses (ENGL 101, 102) typically use MLA 9.
- SBVC psychology courses typically use APA 7.
- SBVC does not have a single mandated style — the agent must ask the instructor's requirement as a first input.
- Many SBVC instructors provide their own formatting preference that may differ slightly from the official APA/MLA standard. The agent should accept "instructor override" parameters.

### Peer-Reviewed Sources — Where to Find Them (Free, for Students)
| Resource | Coverage | Access |
|----------|---------|--------|
| Google Scholar | Broad; links to free PDFs | scholar.google.com |
| PubMed | Medical, psychology, biology | pubmed.ncbi.nlm.nih.gov |
| ERIC | Education research | eric.ed.gov |
| JSTOR | Humanities and social sciences | jstor.org (limited free access) |
| OpenAlex | Comprehensive open metadata | openalex.org |
| Semantic Scholar | CS, medicine, science | semanticscholar.org |
| PsycINFO | Psychology (via SBVC library proxy) | Through SBVC library |
| SBVC Library databases | All disciplines | Through SBVC student login |
| GCU Library databases | All disciplines | Through GCU student login |

---

## 15. Prompt Engineering — System Prompts for the Full Agent

### Master System Prompt (For a Single-Agent "Do Everything" Version)
If the Djinn implementation needs a simpler one-shot approach before the full pipeline is built, use this master prompt:

```
You are an expert academic writing agent specializing in APA 7th Edition and MLA 9th Edition formatting.

You will receive a raw draft from the user. Your job is to transform it into a properly formatted academic paper.

FOLLOW THESE STEPS IN ORDER:

STEP 1 — ANALYZE: Read the draft. Identify the thesis, supporting arguments, and any missing structural components. Report your analysis briefly.

STEP 2 — RESTRUCTURE: Reorder content into proper academic structure: Introduction (with thesis), Body (organized by argument), Conclusion.

STEP 3 — REWRITE: Elevate language to formal academic register. Eliminate contractions, slang, and informal phrasing. Fix grammar. Preserve the author's core argument.

STEP 4 — CITATIONS: Identify all claims requiring citations. Insert [CITATION NEEDED: claim type] for any unsourced factual claims. If the user has provided a source list, insert correctly formatted in-text citations.

STEP 5 — REFERENCES: Build a complete, alphabetized, correctly formatted References (APA) or Works Cited (MLA) page from all cited sources.

STEP 6 — FORMAT: Apply correct title page / header block, headings, running header, page number notation in comments, abstract (APA only, if required).

STEP 7 — QA REPORT: End with a compliance report noting any remaining issues.

STYLE GUIDE: {APA_7 | MLA_9}  
INSTITUTION: {GCU | SBVC | Other}  
COURSE: {course name/number}  
INSTRUCTOR REQUIREMENTS: {any special instructions}  

NEVER fabricate sources, authors, page numbers, DOIs, or dates.  
NEVER change the author's core argument.  
ALWAYS flag uncertainty rather than guessing.
```

### Parameters the Agent Should Always Request Before Starting
```yaml
required_inputs:
  - style_guide: "APA 7" | "MLA 9"
  - paper_type: "argumentative" | "research" | "literature_review" | "case_study" | "reflection"
  - academic_level: "undergraduate" | "graduate"
  - institution: "GCU" | "SBVC" | "other"
  - course: "[course name and number]"
  - instructor: "[instructor name]"
  - abstract_required: true | false
  - word_count_target: [number]
  - sources_provided: true | false
  - source_list: [list of source metadata]

optional_inputs:
  - instructor_special_requirements: "[any deviations from standard APA/MLA]"
  - minimum_peer_reviewed_sources: [number]
  - output_format: "docx" | "markdown" | "pdf" | "latex"
  - include_outline: true | false
  - include_annotated_bibliography: true | false
  - include_abstract: true | false (override for papers that don't normally need one)
```

---

## 16. Implementation Roadmap for Djinn

### Phase 1 — MVP (Single Agent, One-Shot)
- One system prompt handles the full pipeline
- Accepts raw text input + optional source list
- Outputs formatted Markdown with APA or MLA applied
- QA report at end
- Model: Use Claude 3.5 Sonnet or Gemini 1.5 Pro for best instruction-following on formatting rules
- **Timeline: 1–2 sessions to implement**

### Phase 2 — Pipeline (Multi-Agent)
- Break into 6 sub-agents as described in Section 5
- Add DOCX output via python-docx
- Add source metadata schema (Pydantic models)
- Add Reference Builder as rule-based Python (no LLM)
- Add Format Enforcer as rule-based Python
- **Timeline: 1–2 weeks**

### Phase 3 — Full Suite
- Source Finder module (Semantic Scholar / CrossRef API)
- Paraphrase Checker
- Style Switcher (APA ↔ MLA conversion)
- Annotated Bibliography Generator
- Outline Generator
- Integration with Djinn personal layer (knows Javier's GCU courses, enrolled classes, default style)
- **Timeline: 2–4 weeks**

### Phase 4 — Integrations
- Connect to GCU Blackboard (if API available) for direct submission check
- Connect to SBVC library database APIs for source retrieval
- Pandoc template library (one template per style guide + institution combo)
- Voice input support via Whisper: Javier talks through his argument, agent transcribes + formats
- **Timeline: 1–2 months**

---

## Sources and References

- American Psychological Association. (2020). *Publication manual of the American Psychological Association* (7th ed.). https://doi.org/10.1037/0000165-000  
- Modern Language Association. (2021). *MLA handbook* (9th ed.). MLA. https://style.mla.org  
- Purdue Online Writing Lab. (2026). APA style guide. Purdue University. https://owl.purdue.edu/owl/research_and_citation/apa_style/  
- Purdue Online Writing Lab. (2026). MLA style guide. Purdue University. https://owl.purdue.edu/owl/research_and_citation/mla_style/  
- Grand Canyon University. (2026). GCU academic writing style guide. https://library.gcu.edu  
- Semantic Scholar API. (2026). Semantic Scholar open research API. Allen Institute for AI. https://api.semanticscholar.org  
- CrossRef. (2026). CrossRef REST API. CrossRef. https://api.crossref.org  
- OpenAlex. (2026). OpenAlex: Open catalog of scholarly papers. OurResearch. https://openalex.org  

---

*Marcus — Perplexity AI research agent*  
*Completed: 2026-06-16 8:17 PM PDT*  
*Task: TASK-069 | Suite: Djinn Academic Writing Suite | Sections: 16*  
*Vault path: djinn/research/marcus/TASK-069_academic-writing-agent.md*
