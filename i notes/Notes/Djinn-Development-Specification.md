---
subject: ai/development/cli
tags:
  - cs/software-development
  - cs/orchestration-layer
  - personal/operating-system
  - business/executive-assistant
  - ai/models/integration
  - ai/development/cli
  - ai/development/faust/cli
created: 2026-05-23
source: Perplexity export
---

# Djinn Development Specification

## Summary
Djinn is a local-first, multi-domain personal operating system built on OpenClaw as the orchestration layer. It aims to act as an executive assistant, research engine, and voice-enabled interface for various professional domains.

## Key Points
- Djinn should be designed as a durable system that can reason over stored context.
- Core layers include Heart (identity), Mind (reasoning), Hands (action), Eyes and Ears (input), and All-I-do files (context).
- Design principles emphasize local-first data storage, model-agnostic orchestration, persistent memory, multi-channel interaction, trust ladder security, specialized sub-agents, and system architecture over novelty.

## Details
Djinn is intended to be a personal command center with the following roles:

### 1. Heart
- Contains Javier’s name, preferences, intellectual interests, constraints, values, emotional posture, tone, boundaries, and relationship model.
- Defines non-negotiable values such as truthfulness, privacy, security, local control, long-term thinking, and intellectual seriousness.

### 2. Mind
- Reasoning, planning, retrieval, domain frameworks, and task routing layer.
- Includes domain playbooks for finance, investing, law, psychology, cybersecurity, systems architecture, computer science, and business building.
- Features retrieval rules, research standards favoring primary or highly credible sources, and planning heuristics.

### 3. Hands
- Tools, automations, command execution, file manipulation, browser control, and API connectivity.
- Includes local shell and file operations, Git and GitHub workflows, note and document generation, research search/fetch functions, local development workflows, and communication channels like Telegram and Discord.

### 4. Eyes and Ears
- Multimodal intake including terminal, text chat interfaces, Telegram messages, voice memos, Discord channels, and voice-to-text via Whisper-based tooling.
- Also includes file/document ingestion from various sources such as PDFs, notes, markdown, screenshots, and structured data.

### 5. All-I-do files
- Explicit files capturing Javier’s total operating context: responsibilities, domains, workflows, goals, routines, projects, standards, and decision criteria.

## References
- [web:224]
- [page:1]

## Related
- [[Faust-Cli-Product-Overview]] — similarity 0.76
- [[Faust-Project-Setup-Architecture]] — similarity 0.75
