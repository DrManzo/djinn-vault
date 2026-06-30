---
title: Typhon's Forge — Price Sheet
updated: 2026-06-29
tags: [djinn, pricing, shop, forge]
related: [[FAIRPRINT-MANUAL]] | [[inventory]]
---

# Typhon's Forge — Price Sheet

**Last updated:** 2026-06-29  
**Payment:** Zelle `typhonsforge@gmail.com` | CashApp `$TyphonsForge`

---

## Current Catalog

| Piece | Material | Base Price | Notes |
|-------|----------|-----------|-------|
| Camood TTHQ | PETG | **$20** | Terp Tribe branded proxy accessory |
| Proxy Core Holster | PLA | **$15** | Functional proxy core holder |
| Proxy Stand | PLA | **$15** | Puffco Proxy upright stand |

---

## Engraving / Emboss Upcharges

| Type | Upcharge |
|------|----------|
| Text only (name, initials) | +$5 |
| Logo / artwork engraving | +$8 |
| Deep emboss (raised design) | +$10–15 |
| Custom full wrap / redesign | +$15–20 |

**Standard upcharge for any engraving or emboss: +$8**

---

## Bundle

| Bundle | Price | Savings |
|--------|-------|---------|
| Camood + Holster + Stand | $45 | ~$5 off |

---

## Pricing Formula (FairPrintAgent)

`Ask = (material + machine + labor + test_run) ÷ 0.60`

- Material: spool cost per gram × grams used
- Machine: $0.20/hr depreciation + electricity
- Labor: $6.67 base hands-on floor
- Test run: 50% of print cost (qty 1–6), reduces at volume
- Margin: 40%
- Smoking/proxy accessory upcharge: +35% (applied automatically)

Run `djinn-print-quote --simple --name "X" --grams N --hours N` for any new piece.

---

*— Claude, 2026-06-29*
