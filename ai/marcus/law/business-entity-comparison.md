---
title: Business Entity Comparison
task: TASK-061
created: 2026-06-01
tags: [law, business, entity, LLC, corporation, sole-proprietorship]
related: [[llc-formation]] | [[compliance-fundamentals]]
---

# Business Entity Comparison

## Overview

Choosing a business entity is one of the most consequential legal decisions a founder makes. It determines personal liability exposure, how profits are taxed, how the business is governed, and what investors or partners can participate. In California, the main options are sole proprietorship, LLC, S-corp, and C-corp — plus partnership structures for multi-owner arrangements.

For most one-person operations like Typhon's Forge or Terp Tribe Clouds, the decision reduces to: **sole proprietorship vs. single-member LLC**, with an S-corp election as a future tax optimization once profits exceed ~$60–80k/year.

---

## Side-by-Side Comparison

| Feature | Sole Proprietorship | Single-Member LLC | S-Corp (via LLC election) | C-Corp |
|---|---|---|---|---|
| **Formation cost (CA)** | ~$0–$26 (DBA filing) | $70 + $20 SOI | $70 LLC + $0 IRS election | $100–$150 |
| **Annual CA franchise tax** | $0 | $800 minimum | $800 minimum | $800 minimum |
| **Personal liability** | Unlimited | Protected (with formalities) | Protected | Protected |
| **Tax treatment** | Schedule C (pass-through) | Schedule C (disregarded entity) | W-2 salary + K-1 distributions | Corporate tax + dividend tax (double) |
| **Self-employment tax** | 15.3% on all net profit | 15.3% on all net profit | 15.3% on salary only, not distributions | N/A — owner is employee |
| **Investors** | Not practical | Limited (no stock) | Limited (100 shareholders max, US only) | Unlimited, any investor type |
| **Complexity** | Minimal | Low | Medium (payroll required) | High |
| **Best for** | Testing an idea, under $20k/yr | Most small businesses | Profitable solo businesses, $60k+/yr net | Venture-backed startups, stock options |

---

## Sole Proprietorship

### What it is
The default. If you start selling something without forming any entity, you are a sole proprietor. No filing required unless using a trade name (DBA).

### DBA (Doing Business As / Fictitious Business Name)
- Required if operating under a name other than your own legal name
- Filed with the county clerk where your business is located
- San Bernardino County: ~$26 filing fee
- Must be published in a local newspaper (Cal. Bus. & Prof. Code § 17900)
- Does NOT provide liability protection — it's only a name registration

### Liability
Unlimited personal liability. A customer who sues Typhon's Forge as a sole proprietorship can reach your personal bank account, car, and other assets.

### Tax
Schedule C attached to your Form 1040. Net profit is subject to self-employment tax (15.3%) plus income tax. Straightforward — one tax return.

### When it makes sense
- Side hustle under $15–20k/year with low liability risk
- Testing a business idea before committing to formation costs
- Service businesses with professional liability insurance as an alternative shield

---

## Single-Member LLC (Recommended Starting Structure)

### What it is
A separate legal entity that provides liability protection while maintaining the tax simplicity of a sole proprietorship. The IRS "disregards" a single-member LLC for tax purposes — you still file Schedule C — but California treats it as a real entity with the $800 minimum franchise tax.

### Liability shield
Your personal assets are protected from business debts and lawsuits — as long as you:
1. Keep separate bank accounts (no commingling)
2. Sign contracts as the LLC, not personally
3. Maintain the Operating Agreement
4. Don't commit fraud through the LLC

This protection is called avoiding **veil piercing** — courts will "pierce the corporate veil" and hold members personally liable if the LLC isn't treated as a real entity.

### Tax
- Default: disregarded entity → Schedule C (same as sole proprietor)
- Optional: elect S-corp status (see below)
- Optional: elect partnership tax status (requires at least 2 members)

### When it makes sense
- Any business with real liability exposure (physical products, client services, manufacturing)
- Revenue above $20k/year where the $800/yr franchise tax is worth the liability protection
- Cannabis-adjacent products especially — one lawsuit could wipe out everything if unprotected

---

## S-Corp Election on an LLC

### What it is
A **tax election**, not a separate entity. You form an LLC, then file IRS Form 2553 to elect S-corp tax treatment. The LLC still exists and is governed by LLC rules (Operating Agreement, members, etc.) — only the tax treatment changes.

### The tax savings mechanism
Without S-corp: 100% of net profit is subject to 15.3% self-employment tax.
With S-corp: you pay yourself a "reasonable salary" (W-2), which is subject to payroll taxes. The remaining profit passes through as a K-1 distribution, which is **not** subject to self-employment tax.

**Example (net $100k/year):**
- Without S-corp: $100k × 15.3% SE tax = $15,300
- With S-corp: $60k salary × 15.3% = $9,180 + $0 SE on $40k distribution = **$6,120 saved**

Actual savings depend on reasonable compensation standards. The IRS requires S-corp owner-employees to pay themselves a salary comparable to what they'd pay someone else to do their job.

### Additional complexity and cost
- Must run payroll (QuickBooks Payroll, Gusto, etc.) — adds ~$50–$100/month
- Must file Form 1120-S annually (S-corp tax return) — CPA cost ~$500–$1,500/year
- Stricter rules: max 100 shareholders, US residents/citizens only, one class of stock

### When it makes sense
- Net profit consistently above $60–80k/year
- When payroll + CPA costs are less than the SE tax savings
- Not worth it below ~$40–50k net profit — the compliance cost exceeds the savings

---

## C-Corp

### What it is
The default corporation structure. Taxed at the corporate level (21% federal rate) AND again when profits are distributed as dividends (qualified dividend rate, ~15–20%). This **double taxation** makes C-corps unattractive for small businesses.

### When it makes sense
- You're seeking venture capital (VCs require C-corps, typically Delaware C-corps)
- You want to issue stock options to employees (ISO and NSO programs require C-corp structure)
- You plan to have foreign investors (S-corps are US-only)
- Exit via IPO is a realistic long-term goal

### Almost certainly NOT the right choice for Javier
Unless Typhon's Forge scales into a funded startup with employees and institutional investors, the $800/yr minimum franchise tax + double taxation + compliance complexity make a C-corp counterproductive.

---

## Multi-Member Considerations

If Terp Tribe Clouds has co-founders or business partners, the entity selection changes:

- **Multi-member LLC**: default tax treatment is a **partnership** (Form 1065 + K-1s). Profits pass through proportionally. Requires a comprehensive Operating Agreement addressing profit sharing, decision authority, exit/buyout, member removal.
- **Partnership (General)**: avoid — general partners have unlimited personal liability
- **LLC with S-corp election**: still possible with multiple members; all must be US individuals; one class of membership interest only

Key principle: **document the ownership split before money is on the table.** Handshake deals about equity become lawsuits when revenue arrives.

---

## Decision Framework for Javier

```
Are you making $0 now or testing an idea?
  → Sole proprietor with DBA, zero formation cost

Are you selling physical products or anything with liability exposure?
  → Single-member LLC immediately. $90 in, $800/yr, done.

Are you netting $60k+ consistently?
  → Talk to a CPA about S-corp election. Math it out.

Do you have a co-founder on Terp Tribe Clouds?
  → Multi-member LLC with a real Operating Agreement BEFORE you split profits.

Are you pursuing institutional funding or IPO?
  → Delaware C-corp at that point. Not now.
```

---

## Sources
- California Secretary of State — Business Entity Types: https://www.sos.ca.gov/business-programs/business-entities/starting-business/types
- IRS — LLC tax treatment options: https://www.irs.gov/businesses/small-businesses-self-employed/single-member-limited-liability-companies
- Wolters Kluwer — LLC vs S-Corp vs C-Corp: https://www.wolterskluwer.com/en/expert-insights/compare-types-of-businesses-c-corp-s-corp-llc-and-dba
- LinkedIn (Czaplak, 2026) — LLC vs S-Corp 2026 breakdown
