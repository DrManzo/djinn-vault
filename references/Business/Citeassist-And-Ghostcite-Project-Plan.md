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
- **Word Add-in Interface**: Features a task pane with a dropdown of loaded sources.
- **Citation Insertion**: "Insert Citation" button allows users to insert (Author, Year) at the cursor and marks the source as used.
- **Reference Generation**: "Generate References" button creates formatted APA/MLA lists for only the used sources.
- **MVP Characteristics**: The MVP is manual-triggered with no AI or automatic detection; it operates simply and locally.
- **Free Version**: Users supply their own PDFs, and all processing occurs on-device.
- **Paid Version (CiteAssist)**: Includes publisher catalogs, cloud storage, cross-device sync, and team collaboration features. Runs alongside Microsoft Word, loads PDFs as a closed corpus, suggests quotes and in-text citations, and manages reference lists/bibliographies.
- **Core Citation Logic**: Extracted as a reusable C# library for integration with Notation Clark.
- **Build Approach**: Utilizes the Visual Studio Word Add-in template, developing one feature at a time.
- **Tech Stack**: Employs C#, VSTO or Office.js, with hardcoded JSON for version 0 sources.

## Details
The development philosophy is "ugly but lethal," focusing on creating a working MVP first and iterating based on community feedback before adding polish and monetization. The MVP scope is deliberately narrow: users manually load sources, insert citations on command, and generate references when prompted by typing "References" or "Bibliography." There is no PDF parsing, AI, or system-wide detection involved.

CiteAssist enhances the writing process by integrating seamlessly with Microsoft Word. Students load their PDF textbooks and scholarly articles into CiteAssist, which then monitors their typing to suggest precise quotes and citations. The tool automatically formats these citations in APA or MLA style and manages the reference list at the end of the essay.

### Workflow
1. **Loading Sources**: Users upload their PDFs.
2. **Real-Time Suggestions**: As they type, CiteAssist suggests relevant passages.
3. **Insertion**: Students can confirm and insert chosen text with proper citations.
4. **Reference Management**: The tool updates the reference list automatically.

The long-term vision positions GhostCite as a foundational component within the larger M Systems ecosystem, with the citation engine supporting HR/legal/medical case file documentation through Notation Clark.

## References
- Microsoft Word VSTO add-in development
- Office.js API for modern Word add-ins
- APA and MLA citation formatting standards
- [Perplexity](https://www.perplexity.ai/search/753313ea-7908-4600-8f47-721253322200)

## Related
- [[Meanas-and-M-Systems-Business-Vision]]
- [[Source-Keeper-Project-Spec]]
- [[APA Formatted Posts]]
- [[Scrambled-Notes-to-APA-Essay-Converter]]
- [[California-LLC-Formation-Software-Company]]
- [[CiteAssist-and-GhostCite-Project]] — integration
```

This updated reference note integrates new information from the source content, expanding on CiteAssist's features and workflow while maintaining existing details about GhostCite.