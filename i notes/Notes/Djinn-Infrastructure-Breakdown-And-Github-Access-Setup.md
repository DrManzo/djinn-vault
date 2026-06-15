---
tags:
  - technology/djinn-infrastructure/systems
  - technology/djinn-infrastructure/services
  - technology/djinn-infrastructure/cli-tools
  - 3d-printing/calibration/cube
---

---
subject: Technology/DjinnInfrastructure
tags:
  - technology/djinn-infrastructure/systems
  - technology/djinn-infrastructure/services
  - technology/djinn-infrastructure/cli-tools
created: 2026-06-14
source: Perplexity export

# Djinn Infrastructure Breakdown and GitHub Access Setup

## Summary
This note provides a detailed breakdown of the Djinn infrastructure, including its components, services, CLI tools, and current status. It also outlines steps to ensure another AI can understand and access the system via GitHub.

## Key Points
- **Topology**: 
  - Salomon (Omen): Heavy lifter with IP 192.168.1.225.
  - Typhon (MSI): Storage/sync with IP 192.168.1.113.
  - Calliope (Ender-3 V3 Plus): Printer with API at 192.168.1.114:7125.

- **Agents & Workspace**: 
  - 8 active systemd services for context assembly, gateway hybridization, auto-detection of 3D model URLs, Moonraker progress notifications, error logging, and voice dictation.
  - 14 OpenClaw agents covering content orchestration, media processing, design, and system management.

- **CLI Tools**: 
  - Print pipeline tools: `djinn-print-consult`, `djinn-model-slice`, `djinn-print-quote`, etc.
  - Media pipeline tools: `djinn-media-ingest`, `djinn-media-photo`, etc.
  - Design & 3D tools: `djinn-design`, `djinn-generate-3d`.
  - System management tools: `djinn-ctx-assembler`, `djinn-sync`.

- **Manufacturing Orchestrator**: 
  - 6 agents via `djinn-design` for design generation, editing, optimization, and more.

- **Typhon's Studio**: 
  - A streaming/post-production suite with 6 agents: Audio, Lighting, Music, Copilot, Stream, Post-Production (Whisper + phi4 show notes + ffmpeg clips).

- **Vault**: 
  - An Obsidian vault at `~/Obsidian/` synced to GitHub and GDrive as the single source of truth.

- **Current Projects**: 
  - No ongoing prints on Calliope; last prints were for Terp Tribe HQ cup and GoPro Tripod.

## Details
The Djinn infrastructure is a complex setup designed to manage various aspects of manufacturing, media processing, and system operations. It includes multiple agents, services, and CLI tools that work together to ensure seamless operation and management. The key components are:

- **Topology**: 
  - Salomon (Omen) acts as the heavy lifter with IP 192.168.1.225.
  - Typhon (MSI) serves as storage/sync with IP 192.168.1.113.
  - Calliope (Ender-3 V3 Plus) is the printer accessible via API at 192.168.1.114:7125.

- **Agents & Workspace**: 
  - The system runs eight active systemd services that handle context assembly, gateway hybridization, auto-detection of 3D model URLs, Moonraker progress notifications, error logging, and voice dictation.
  - There are 14 OpenClaw agents responsible for content orchestration, media processing, design, and system management.

- **CLI Tools**: 
  - The print pipeline includes tools like `djinn-print-consult`, `djinn-model-slice`, `djinn-print-quote`, etc., which manage the entire process from consultation to final printing.
  - Media pipeline tools such as `djinn-media-ingest`, `djinn-media-photo`, and others handle media ingestion, photo editing, captioning, thumbnail generation, and more.
  - Design & 3D tools like `djinn-design` and `djinn-generate-3d` facilitate the creation of designs and 3D models.
  - System management tools such as `djinn-ctx-assembler`, `djinn-sync`, etc., ensure that the system is well-managed.

- **Manufacturing Orchestrator**: 
  - The manufacturing orchestrator uses six agents via `djinn-design` for tasks like design generation, editing, optimization, and more.

- **Typhon's Studio**: 
  - This suite includes audio, lighting, music, copilot, stream, and post-production tools to manage streaming and post-production processes.

- **Vault**: 
  - The Obsidian vault at `~/Obsidian/` is synced to GitHub and GDrive as the single source of truth for all operations. It contains approximately 700 notes.

## References
- [https://github.com/DrManzo/djinn-vault.git](https://github.com/DrManzo/djinn-vault.git)
- [https://github.com/DrManzo/typhons-cyber-forge.git](https://github.com/DrManzo/typhons-cyber-forge.git)

## Related
- [[2026-06-01_github-look-into-the-djinn-vault-you-should-have-access-and-tell-me-wh]] — access-setup
- [[Djinn-3d-Printer-Overview-And-Puffco-Proxy-Quad]] — printer-overview
- [[35-Forge-Upgrades-For-Ender-3v3-Plus]] — printer-upgrades
