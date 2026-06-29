---
subject: 3d-printing/models/ender-3-pro/shop-tools
tags:
  - business/finance/accounting
  - business/marketing/social-media
  - cs/bash-scripting
created: 2026-06-29
source: Perplexity export
---

# Typhon's Forge — Agent Reference

## Summary
This note outlines the structure and responsibilities of four key agents in a 3D printing operation, specifically focusing on financial tracking, inventory management, marketing, and accounting.

## Key Points
- **Bookkeeper (djinn-bookkeeper)**
  - Tracks income and expenses.
  - Logs transactions for commissions, shop sales, tips, filament, hardware, shipping supplies, platform fees.
  - Generates weekly profit & loss summaries.
  
- **Inventory Manager (djinn-inventory)**
  - Manages physical stock of filament, hardware, consumables.
  - Tracks filament by spool details and alerts when stocks drop below a threshold.

- **Marketing Agent (djinn-marketing)**
  - Handles Etsy listings, social media posts, hashtag management.
  - Schedules content for posting based on print metadata.

- **Accounting Agent (djinn-accounting)**
  - Provides higher-level financial analysis.
  - Generates monthly revenue vs expense reports with trend analysis.

## Details
The Typhon's Forge operation is a complex 3D printing setup running on a Djinn AI OS fleet. The agents are designed to run as standalone Python modules, register with the Djinn core via CLI commands, and communicate through Telegram/Discord gateways. Each agent has specific responsibilities that contribute to the overall financial and operational management of the shop.

### Bookkeeper (djinn-bookkeeper)
- **Responsibilities:**
  - Logs all income from commissions, shop sales, tips.
  - Tracks expenses for filament, hardware, shipping supplies, platform fees.
  - Calculates net profit per job, week, month.
  - Flags jobs with low cost margins.
  - Generates weekly P&L summaries.

- **Tool Integrations:**
  - Reads data from `djinn-print-quote` and `inventory`.
  - Writes to human-readable files and SQLite database.
  - Telegram commands for querying financial data.

### Inventory Manager (djinn-inventory)
- **Responsibilities:**
  - Tracks filament by spool details including material, color, brand, weight remaining, cost per kg, location.
  - Deducts filament after each print based on weight from `print tracker`.
  - Alerts when stock drops below a threshold.
  - Manages consumables and hardware orders.

- **Tool Integrations:**
  - Reads data from `djinn-print-track` for filament consumption.
  - Writes to inventory files and SQLite database.
  - Telegram commands for querying and managing inventory.

### Marketing Agent (djinn-marketing)
- **Responsibilities:**
  - Drafts Etsy product listings based on print metadata.
  - Schedules social media posts including Instagram/TikTok timelapses, finished prints, process shots.
  - Manages hashtag sets per product category.
  - Tracks which posts drive commission inquiries.

- **Tool Integrations:**
  - Reads data from `djinn-print-completed` for finished print metadata.
  - Uses media assets stored in `C:\Forge\content`.
  - Writes post drafts to marketing files.
  - Telegram commands for managing content scheduling and posting.

### Accounting Agent (djinn-accounting)
- **Responsibilities:**
  - Generates monthly revenue vs expense reports with trend analysis.
  - Calculates effective hourly rate for the operation.
  - Tracks platform fees per month.
  - Prepares tax documents by categorizing expenses and flagging deductibles.

## References
- [Perplexity Export](https://www.perplexity.ai/search/marcus-typhon-s-forge-full-age-hN5U5w4eTGyJAvvefsDqEQ)

## Related
- [[3d-printing/models/ender-3-pro]] — Ender 3 Pro printer details.
- [[3d-printing/shop-tools]] — General shop tools and processes.