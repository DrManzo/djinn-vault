---
subject: research/academic-writing-agent/apa-mla-formatter
tags:
  - academic/writing/formats/apa/mla
  - research/tools/academic-writing-agent
created: 2026-06-22
source: Perplexity export

---

# Academic Writing Agent for APA and MLA Formats

## Summary
The document details the comprehensive setup of an academic writing agent that automates APA and MLA formatting, including a detailed breakdown of rules, pipeline architecture, and implementation specifics.

## Key Points
- **Core Problem Spec**: Defines 8 discrete tasks from thesis extraction to abstract generation.
- **APA 7th Edition**: Includes title page structure, heading levels, in-text citation rules, reference list formats, and APA 7 changes from 6th edition.
- **MLA 9th Edition**: Covers the container model, Works Cited formats, in-text author-page citation rules, and AI citation guidance.
- **APA vs. MLA Decision Table**: A side-by-side table for discipline-specific citation systems.
- **Pipeline Architecture**:
  - Structure Analyzer
  - Register Rewriter
  - Citation Injector
  - Reference Builder
  - Format Enforcer
  - QA Checker
- **Bonus Modules**: Abstract Generator, Annotated Bibliography Generator, Outline Generator, Paraphrase Checker, Source Finder, Style Switcher.
- **Python Implementation Stack**: Uses `python-docx` for DOCX generation and Pandoc pipeline.
- **GCU and SBVC Specifics**: Details GCU's APA 7 deviations, SafeAssign integration, and free peer-reviewed source databases.

## Details
The document outlines a robust academic writing agent designed to handle the complexities of APA and MLA formatting. It begins by defining the core problem specification, which involves extracting key information from raw text and structuring it according to the specified citation styles. The agent is broken down into multiple stages: structure analysis, register rewriting, citation injection, reference building, format enforcement, and quality assurance checking.

The implementation uses Python with libraries like `python-docx` for generating DOCX files and Pandoc for converting Markdown to DOCX. The agent includes bonus modules such as an abstract generator, annotated bibliography creator, outline generator, paraphrase checker, source finder, and a style switcher between APA and MLA formats.

Additionally, the document covers specific requirements for institutions like GCU (George Mason University), including deviations from standard APA guidelines and integration with SafeAssign. It also provides details on free peer-reviewed source databases that students can access.

## References
- [TASK-069_academic-writing-agent.md](https://github.com/DrManzo/djinn-vault/blob/main/djinn/research/marcus/TASK-069_academic-writing-agent.md)

## Related
- [[djinn-production-system]] — Overview of the Djinn production system architecture.
- [[academic-writing-tools]] — Other tools and resources for academic writing.

---

This structured note captures the essential information from the provided content, ensuring it is organized and easily accessible within an Obsidian vault.