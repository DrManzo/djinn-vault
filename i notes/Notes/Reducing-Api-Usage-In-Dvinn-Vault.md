---
subject: Dvinn-Vault/Api-Usage-Reduction
tags:
  - business/process-efficiency/api-optimization
created: 2026-06-14
source: Perplexity export
---

# Reducing API Usage in Dvinn Vault

## Summary
Claude and Marcus analyzed the Dvinn Vault to identify changes that can significantly reduce API usage, focusing on mechanical file edits, COMMS.md management, and optimizing default settings.

## Key Points
- **Top 5 Immediate Changes:**
  - Any mechanical file edit or search-and-replace → QUEUE.md (Salomon)
  - COMMS.md entries → Salomon writes them after Claude delivers an artifact
  - Groq fallback is already built (llm.py) — wire it for burst tasks
  - Print pipeline ops (gcode, consult, upload) → Salomon/opencode owns this now
  - Compact COMMS.md via Salomon cron

- **Where Marcus Agrees:**
  - Timers firing unconditional git operations (288 pushes/day per machine)
  - COMMS-processor firing on empty COMMS.md
  - `max_tokens=2048` and `temperature=0.7` as universal defaults in `llm.py`

- **Where Claude Pushes Back:**
  - History limit setting (`historyLimit=5`)
  - Groq's `llama-3.3-70b` model
  - ChromaDB vault indexer running on 688 files
  - `djinn-ctx-router` firing every 5 minutes

- **What Marcus Found:**
  - Full re-indexing of `djinn-embed` without incremental mode
  - Fixed 16384 context window on qwen2.5:7b for all task types

## Details
The Dvinn Vault is more active than it appears, with daily commits from multiple agents and a complex inter-machine communication system. Claude identified several areas where API usage can be optimized:
- **Mechanical File Edits:** These tasks should be handled by Salomon to reduce unnecessary Claude invocations.
- **COMMS.md Management:** Entries should be added after Claude delivers an artifact, not during the session.
- **Groq Fallback:** The Groq model is already built and should be used for burst tasks.
- **Print Pipeline Operations:** These are now owned by Salomon/opencode.
- **Compact COMMS.md:** Regular cron jobs can manage this to reduce session bloat.

Claude also noted that the history limit setting might need a smarter context compression approach rather than just increasing it. Additionally, the ChromaDB indexer and `djinn-ctx-router` should be optimized for better performance.

## References
- [https://github.com/DrManzo/djinn-vault](https://github.com/DrManzo/djinn-vault)

## Related
- [[Process-Efficiency-Guidelines]] — General process optimization guidelines
- [[Claude-Session-Reports]] — Reports on Claude's sessions and tasks
- [[API-Optimization-Methods]] — Methods for optimizing API usage in complex systems

TAG RULES:
- topic MUST be one of: psychology, law, business, cs, personal, creative
- path: topic/context/relevant/commonality/specific-tag
- 2-4 tags per note, use hyphens not spaces
- You may create new nodes at context level and below
- Existing vault tags for reference: 1800s/literature/style, 3d-printing/automation, 3d-printing/bore-design, 3d-printing/calibration/cube, 3d-printing/filament/compatible, 3d-printing/filament/handling, 3d-printing/filament/preparation, 3d-printing/filament/recommendations, 3d-printing/filament/tracking, 3d-printing/filament/types, 3d-printing/glassware/attachment, 3d-printing/inventory-management, 3d-printing/models/benchmark, 3d-printing/models/benchmark-3343, 3d-printing/models/ender-3-v3-plus, 3d-printing/models/ender-3v3-plus, 3d-printing/models/ender-3v3-plus/upgrades, 3d-printing/models/puffco-proxy, 3d-printing/models/puffco-proxy/upgrade-script, 3d-printing/models/smoking-accessories, 3d-printing/printer-maintenance, 3d-printing/printer-models/ender-3-v3-plus, 3d-printing/printer-setup/beginner-guide, 3d-printing/printer-setup/preparation, 3d-printing/printer/subsystem, 3d-printing/quality/test, 3d-printing/subsystem, 3d-printing/tool-upgrades, 3d-printing/troubleshooting/mechanical-setup, 3d-printing/tuning/model, 3d-printing/virtual-setup, Creative/Aesthetic, Timers/Run, academic-writing/apa-style, academic-writing/study-strategies, accounting/cycle/close, accounting/principles/governance, accounting/ratios/performance-analysis, accounting/systems/adjusting-entries/supplies, accounting/systems/trial-balance/order-structure