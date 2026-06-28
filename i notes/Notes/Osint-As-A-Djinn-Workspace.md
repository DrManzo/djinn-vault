---
subject: djinn/workspaces/osint
tags:
  - cs/security/oss/integration
  - djinn/workspaces/osint
created: 2026-06-28
source: Perplexity export
---

# OSINT as a Djinn Workspace

## Summary
Adding an OSINT workspace to the Djinn ecosystem is well-justified and fits seamlessly into the existing architecture.

## Key Points
- **Fit with Architecture**: The `djinn/workspaces/` directory already exists for domain-specific operational contexts.
- **Existing Tools**: Several tools in `djinn-tools` are partial OSINT implementations, such as `djinn-bore-core`, `djinn-trend-agent`, and `djinn-social-analyst`.
- **Passive vs. Active Operations**: Passive operations like domain lookups and public social scrapes are auto-approved (Tier 0–1). Active enumeration requires operator checkpoint (Tier 3).
- **PII Collection**: Any PII collection must route through the existing encrypted SQLite pipeline.
- **Workspace Structure**:
  - `OSINT-MANUAL.md`: Operator handbook
  - `targets/`: Named research subjects (Obsidian notes, not raw PII)
  - `reports/`: YYYY-MM-DD_slug.md (same format as existing logs)
  - `tools/`: New tools like `djinn-net-probe`, `djinn-archive-fetch`
  - `feeds/`: Passive intel feeds

## Details
The Djinn ecosystem is designed to grow without rewrites, making the addition of an OSINT workspace a natural fit. The architecture already includes agent lanes that map well onto OSINT research and tool execution.

### Why It Fits the Architecture
- **Marcus (Multi-source Web Synthesis)**: Perfect for OSINT research.
- **Salomon**: Tool execution and integration with `djinn-discord-gateway` and `djinn-discord-watch`.
- **Claude**: Correlation architecture and pipeline design.
- **qwen2.5:7b**: Default tool-use model, suitable for structured scraping tasks.

### What OSINT Would Actually Mean in Djinn
OSINT in Djinn isn't about running aggressive third-party toolkits but systematically enriching the information layer. Key implementations include:
- **Username/handle enumeration** using `djinn-bore-core`.
- **Discord community intel** with `djinn-discord-gateway` and `djinn-discord-watch`.
- **Trend & market intel** via `djinn-trend-agent`.
- **Deep person/entity research** in Marcus's research lane.
- **Domain/IP/infra footprint** using a new `djinn-net-probe`.
- **Social graph mapping** with an extended `djinn-social-analyst`.
- **Wayback/cached data pulls** through a new `djinn-archive-fetch`.

### What’s Already in Place
Several tools in `djinn-tools` are partial OSINT implementations:
- **`djinn-bore-core`**: Reconnaissance core.
- **`djinn-trend-agent`**: Market/community trend scraping.
- **`djinn-social-analyst`**: Social media analysis.
- **`djinn-style-scrape`**: Scraping infrastructure.
- **`djinn-vault-enrich`**: Vault enrichment from external sources.

### Gateway Compliance
The Gateway tiers already govern how an OSINT workspace must behave:
- Passive reads (Tier 0–1) are auto-approved.
- Active enumeration (Tier 3) requires operator checkpoint.
- PII collection must route through the existing encrypted SQLite pipeline.
- Storing OSINT outputs in `djinn/workspaces/osint/` as vault-indexed research.

### Recommended Workspace Structure
```
djinn/workspaces/osint/
├── OSINT-MANUAL.md ← Operator handbook (Marcus writes, Claude reviews)
├── targets/ ← Named research subjects (Obsidian notes, not raw PII)
├── reports/ ← YYYY-MM-DD_slug.md (same format as existing logs)
├── tools/ ← New djinn-tools: djinn-net-probe, djinn-archive-fetch
└── feeds/ ← Passive intel feeds (RSS, trend data, API outputs)
```

### Bottom Line
Adding OSINT to Djinn is a yes with no architectural debt. It fits the existing architecture, uses partially built tools, and respects the operator-controlled model.

## References
- [djinn-vault](https://github.com/DrManzo/djinn-vault)
- [djinn-tools](https://github.com/DrManzo/djinn-tools)

## Related
- [[djinn-research-request-pa-layer-redesign]] — Research request for PA Layer Redesign
- [[forge-slicer]] — Forge Slicer support prompt
- [[comms-noise-reduction]] — COMMS Noise Reduction session