---
subject: Creative Writing/Fantasy-Worldbuilding
tags: [fantasy, worldbuilding, dark-fantasy, creative-writing, djinn, openclaw, agent-system, personal-os, architecture]
created: 2026-05-19
source: Technical Specification
type: technical-spec
---

# Djinn Development Specification

## Summary
Djinn is a local-first, multi-domain, multi-agent personal operating system built on OpenClaw as the harness/orchestration layer, combining cloud and local models to serve as a deeply personalized executive assistant, research engine, systems operator, strategist, and voice-enabled interface across finance, law, psychology, cybersecurity, computer science, and business building.

## Key Points
- OpenClaw serves as the harness around a model, supplying tools, memory, permissions, channels, and workflows that let the brain act in the world
- Djinn is designed as a personal command center and digital operator, not just a chatbot — a durable system that reasons over stored context, spawns sub-agents, and operates continuously
- Design principles: local-first where possible, model-agnostic orchestration, persistent memory, multi-channel interaction, trust ladder security, specialized sub-agents, and system architecture over novelty
- Heart layer contains enduring identity, principles, motivations, values, emotional posture, tone, boundaries, and relationship model with files including identity.md, user.md, memory.md, and soul.md
- Mind layer handles reasoning, planning, retrieval, domain frameworks, and task routing with domain playbooks for finance, investing, law, psychology, cybersecurity, systems architecture, computer science, and business building
- Hands layer includes local shell and file operations, Git and GitHub workflows, note generation, research functions, local development workflows, and communication channels
- Eyes and ears provide multimodal intake through terminal, Telegram, Discord, voice-to-text via Whisper, and file/document ingestion
- Required file architecture includes root-level files (README, identity, user, memory, soul, agents, tools, heartbeat, security, models, voice, workflows, repos, roadmap) plus organized directories for heart, mind, all-i-do, skills, channels, and vault
- Ten sub-agents defined: djinn-core, djinn-research, djinn-finance, djinn-legal, djinn-psych, djinn-cyber, djinn-dev, djinn-business, djinn-voice, and djinn-operator
- Eight essential repos: djinn-core, djinn-skills, djinn-memory, djinn-voice, djinn-infra, djinn-workflows, djinn-ui, and djinn-docs
- Voice stack uses Whisper/Whisper.cpp for STT and Piper for offline TTS, with push-to-talk and dictation behavior
- Communication channels: Telegram for mobile access and voice memos, Discord for parallel multi-agent workflows with separate channels by domain
- Security specification includes no plain-text secrets, separate trust tiers (read-only through high-risk with explicit confirmation), daily backups, audit logs, and rollback plans
- Trust ladder: Tier 0 (read only), Tier 1 (local file creation), Tier 2 (repo branch changes), Tier 3 (outbound communications with approval), Tier 4 (high-risk actions with per-action confirmation)
- Development proceeds in six phases: core identity scaffolding, runtime setup, memory and retrieval, voice, domain skills, and infrastructure and automation

## Details
The Djinn specification represents a comprehensive architecture for a personal AI operator system. The Heart/Mind/Hands metaphor provides a clear organizational structure: Heart defines who Djinn is and how it relates to the user, Mind handles reasoning and domain expertise, and Hands execute actions in the environment. The trust ladder security model is critical — progressively granting permissions rather than full autonomy prevents catastrophic errors. The multi-repo approach keeps the system maintainable long-term, with djinn-core as the central configuration and supporting repos for skills, memory, voice, infrastructure, and workflows. The sub-agent architecture allows specialized work without forcing one session to hold all threads. The vault/Obsidian-style knowledge base provides durable context that accumulates over time. The specification acknowledges missing user-specific details that must be filled in before implementation: exact personality, values, goals, task automation boundaries, model preferences, and repo visibility.

## References
No external references.

## Related
- [[Fantasy-Worldbuilding-Hub]]
- [[Story-Critique-Hub]]
- [[Aethoria-Religion-And-Pantheon]]
- [[Aethoria-Magic-And-Technology]]
- [[Djinn-OC]]
