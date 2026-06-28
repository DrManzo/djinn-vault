---
subject: 3d-printing/models/ender-3-pro/shop-tools
tags:
  - business/finance/accounting
  - business/marketing/research
  - cs/bash-scripting
created: 2026-06-28
source: Perplexity export

---

# Typhon's Forge — Agent Reference

## Summary
Typhon's Forge is a 3D printing operation with specific agents for financial tracking, inventory management, marketing, and accounting. Each agent is designed to run on the Djinn AI OS fleet and communicate through existing gateways.

## Key Points
- **Bookkeeper (djinn-bookkeeper)**: Tracks income, expenses, and generates financial reports.
- **Inventory Manager (djinn-inventory)**: Manages physical stock of filament, hardware, and consumables.
- **Marketing Agent (djinn-marketing)**: Handles shop listings, social media posts, and content scheduling.
- **Accounting Agent (djinn-accounting)**: Provides higher-level financial analysis.

## Details
### Bookkeeper (djinn-bookkeeper)
- **Responsibilities**:
  - Logs income and expenses.
  - Calculates net profit per job.
  - Tracks filament cost per gram.
  - Flags jobs with low margins.
  - Generates weekly P&L summaries.
- **Tool Integrations**:
  - Reads from `djinn-print-quote` output.
  - Reads from `inventory`.
  - Writes to `~/Obsidian/djinn/finance/forge-ledger.md` and SQLite DB.
- **Data Schema**:
  - `transactions`: id, date, type, category, amount, job_id, note
  - `jobs`: id, date, model, printer, filament_g, filament_cost, labor_min, platform_fee, total_charged, net

### Inventory Manager (djinn-inventory)
- **Responsibilities**:
  - Tracks filament by spool.
  - Alerts when stock drops below a threshold.
  - Manages consumables and hardware orders.
- **Tool Integrations**:
  - Reads from `djinn-print-track` output.
  - Reads `ORDER-LIST.md`.
  - Writes to `~/Obsidian/djinn/printer/inventory.md` and SQLite DB.
- **Data Schema**:
  - `spools`: id, material, color, brand, weight_total_g, weight_remaining_g, cost_per_kg, assigned_printer, status
  - `consumables`: id, item, quantity, unit, reorder_threshold, last_restocked

### Marketing Agent (djinn-marketing)
- **Responsibilities**:
  - Drafts Etsy product listings.
  - Schedules social media posts.
  - Tracks post performance.
  - Recommends models to list based on inventory and print time.
- **Tool Integrations**:
  - Reads from `~/Obsidian/djinn/printer/completed/`.
  - Reads from `C:\Forge\content\`.
  - Writes to `~/Obsidian/djinn/media/posts/`.

### Accounting Agent (djinn-accounting)
- **Responsibilities**:
  - Generates monthly financial reports.
  - Calculates effective hourly rate.
  - Tracks platform fees and tax preparation.

## References
- [Perplexity Export](https://www.perplexity.ai/search/marcus-typhon-s-forge-full-age-hN5U5w4eTGyJAvvefsDqEQ)

## Related
- [[3d-printing/models/ender-3-pro/shop-tools]] — Detailed breakdown of the shop tools.
- [[3d-printing/models/ender-3-pro/inventory-management]] — Inventory management specifics.