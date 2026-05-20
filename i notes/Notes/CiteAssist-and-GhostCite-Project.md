---
subject: Business/M-Systems
tags: [citeassist, ghostcite, word-addin, citation-tool, m-systems, student-tools]
created: 2026-05-19
source: 2026-05-18_20-19-33_Perplexity
---

# CiteAssist and GhostCite — Project Plan

## Summary
GhostCite is a Word add-in (C#, VSTO-based) that serves as a personal citation tool — loading a small set of sources, inserting in-text citations on command, and auto-generating formatted references/bibliography lists. CiteAssist is the future paid version with publisher catalog integration and cloud collaboration. The core citation engine is designed as a reusable library for later integration into Notation Clark's document/report modules.

## Key Points
- Word add-in task pane with dropdown of loaded sources
- "Insert Citation" button drops (Author, Year) at cursor, marks source as used
- "Generate References" button creates formatted APA/MLA list of only used sources
- MVP is manual-triggered, no AI, no automatic detection — simple and local
- Free/local version: user supplies own PDFs, all processing on-device
- Paid version (CiteAssist): publisher catalogs, cloud storage, cross-device sync, team collaboration
- Core citation logic extracted as reusable C# library for Notation Clark integration
- Build approach: Visual Studio Word Add-in template, one feature at a time
- Tech stack: C#, VSTO or Office.js, hardcoded JSON for v0 sources

## Details
The development philosophy is "ugly but lethal" — get a working MVP first, iterate with community feedback, then add polish and monetization. The MVP scope is deliberately narrow: load sources manually, insert citations on user command, generate references when triggered by typing "References" or "Bibliography." No PDF parsing, no AI, no system-wide detection. The long-term vision positions GhostCite as a building block within the larger M Systems ecosystem, with the citation engine serving HR/legal/medical case file documentation through Notation Clark.

## References
- Microsoft Word VSTO add-in development
- Office.js API for modern Word add-ins
- APA and MLA citation formatting standards

## Related
- [[Meanas-and-M-Systems-Business-Vision]]
- [[Source-Keeper-Project-Spec]]
- [[APA Formatted Posts]]
- [[Scrambled-Notes-to-APA-Essay-Converter]]
- [[California-LLC-Formation-Software-Company]]
