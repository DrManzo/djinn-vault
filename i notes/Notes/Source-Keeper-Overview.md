---
subject: business/project-management/modules/roles/faust/cli/core/adapters
tags:
  - cs/software-development
  - cs/notes-management
  - personal/productivity
  - business/research-tools
created: 2026-05-19
source: Perplexity export
---

# Source Keeper Overview

## Summary
Source Keeper is a lightweight capture tool designed for Windows that allows users to highlight text from any website, press Ctrl+Shift+S, and automatically save the highlighted content along with the full URL and timestamp into an organized markdown file. This tool supports custom “snippets” or collections such as "AI Research," "Design Ideas," and "Code Patterns," ensuring each capture is neatly formatted with source attribution.

## Key Points
- **Purpose**: Preserve sources while researching.
- **Platform**: Windows, local files, markdown output.
- **Features**:
  - Hotkey-triggered (Ctrl+Shift+S) for selective capturing.
  - URL-aware and timestamped captures.
  - Markdown format for portability across editors and version control systems.
- **Philosophy**: Local-first, privacy-respecting, and portable.

## Details
Source Keeper addresses the common issue of losing sources during research by providing a systematic way to capture and organize information. The tool is designed with content creators, builders, and researchers in mind who need to reference where they found their information. It ensures that each piece of captured data includes the exact source link for later reference.

The core functionality involves:
- **Hotkey Handler**: A system-level listener that captures highlighted text.
- **Clipboard Capture**: Extracts the highlighted text along with the current URL and timestamp.
- **File Structure**: Organizes snippets into custom collections, such as "AI Research," "Design Ideas," and "Code Patterns."
- **Markdown Template**: Ensures each capture is formatted consistently.

## References
- [Perplexity](https://www.perplexity.ai/search/7d8b6b49-bb3d-409a-95c2-903c960ab415)

## Related
- [[Source-Keeper-Project-Spec]] — similar functionality
- [[CiteAssist-and-GhostCite-Project]] — source management

## Summary
This document outlines the key system features, architecture, UI/UX considerations, and implementation milestones for developing Source Keeper, a portable, source-preserving, hotkey-triggered markdown capture tool.

## Key Points
- **Foundation Layer**: Hotkey handler, clipboard capture, file structure, markdown template.
- **Snippet Organization System**: User-defined collections for organizing captured content.
- **Implementation Roadmap**:
  - Phase 1: Architecture & Core Logic.
  - Phase 2: Snippet Organization System.

## Details
The build plan focuses on creating a functional and user-friendly product that aligns with the vision of Source Keeper. The tool will be developed in phases to ensure each component is thoroughly tested before integration.

### Phase 1: Architecture & Core Logic
- **Hotkey Handler**: Windows system-level listener using Python's `pynput` or a compiled executable wrapper.
- **Clipboard Capture**: Extracts highlighted text, current URL, and timestamp.
- **File Structure**: Defines where snippets live locally and how collections organize them.
- **Markdown Template**: Ensures consistent formatting for each capture.

### Phase 2: Snippet Organization System
- **User-Defined Collections**: Allows users to create custom collections such as "AI Research," "Design Ideas," and "Code Patterns."
- **UI/UX Considerations**: Design a user-friendly interface for managing snippets and collections.
- **Implementation Milestones**:
  - Define the file structure and directory layout.
  - Implement the hotkey handler and clipboard capture logic.
  - Develop the markdown template format.

## References
- [Perplexity](https://www.perplexity.ai/search/7d8b6b49-bb3d-409a-95c2-903c960ab415)

## Related
- [[Source-Keeper-Project-Spec]] — similar functionality
- [[CiteAssist-and-GhostCite-Project]] — source management
