---
subject: Business
tags:
  - business
created: 2026-05-19
source: 2026-05-18_20-19-33_Perplexity
---

```markdown
subject: Business
tags:
  - business
  - business/software
  - business/career-factors/productivity
  - cs/software-engineering
  - cs/nlp
  - personal/learning-tools
created: 2026-05-19
source: 2026-05-18_20-19-33_Perplexity; Perplexity export

# CiteAssist and GhostCite — Project Plan

## Summary
GhostCite is a Word add-in (C#, VSTO-based) that serves as a personal citation tool, enabling users to load a small set of sources, insert in-text citations on command, and auto-generate formatted references/bibliography lists. CiteAssist represents the future paid version with publisher catalog integration and cloud collaboration capabilities. The core citation engine is designed as a reusable library for later integration into Notation Clark's document/report modules.

## Key Points
- Word add-in task pane with dropdown of loaded sources.
- "Insert Citation" button drops (Author, Year) at cursor, marks source as used.
- "Generate References" button creates formatted APA/MLA list of only used sources.
- MVP is manual-triggered, no AI, no automatic detection — simple and local.
- Free/local version: user supplies own PDFs, all processing on-device.
- Paid version (CiteAssist): publisher catalogs, cloud storage, cross-device sync, team collaboration.
- Core citation logic extracted as reusable C# library for Notation Clark integration.
- Build approach: Visual Studio Word Add-in template, one feature at a time.
- Tech stack: C#, VSTO or Office.js, hardcoded JSON for v0 sources.

## Details
The development philosophy is "ugly but lethal" — get a working MVP first, iterate with community feedback, then add polish and monetization. The MVP scope is deliberately narrow: load sources manually, insert citations on user command, generate references when triggered by typing "References" or "Bibliography." No PDF parsing, no AI, no system-wide detection. 

CiteAssist enhances the writing process by integrating seamlessly with Microsoft Word. Students load their PDF textbooks and scholarly articles into CiteAssist, which then monitors their typing to suggest precise quotes and citations. The tool automatically formats these citations in APA or MLA style and manages the reference list at the end of the essay.

### Workflow
1. **Loading Sources**: Users upload their PDFs.
2. **Real-Time Suggestions**: As they type, CiteAssist suggests relevant passages.
3. **Insertion**: Users can confirm and insert chosen text with proper citations.
4. **Reference Management**: The tool updates the reference list automatically.

The long-term vision positions GhostCite as a building block within the larger M Systems ecosystem, with the citation engine serving HR/legal/medical case file documentation through Notation Clark.

## References
- Microsoft Word VSTO add-in development.
- Office.js API for modern Word add-ins.
- APA and MLA citation formatting standards.
- [Perplexity](https://www.perplexity.ai/search/753313ea-7908-4600-8f47-721253322200)

## Related
- [[Meanas-and-M-Systems-Business-Vision]]
- [[Source-Keeper-Project-Spec]]
- [[APA Formatted Posts]]
- [[Scrambled-Notes-to-APA-Essay-Converter]]
- [[California-LLC-Formation-Software-Company]]
- [[CiteAssist-and-GhostCite-Project]] — integration
```

This updated reference note integrates the new source content into the existing structure, expanding on details and key points without duplicating or removing correct information.