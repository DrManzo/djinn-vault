---
title: Marcus Research Brief — Djinn Law Suite
assigned_to: marcus
task: TASK-037
status: pending
created: 2026-06-01
delivers_to: references/Law/
tags: [marcus, research, law, djinn-law]
---

# TASK-037 — Djinn Law Suite Research

**You are Marcus. This is a multi-query research campaign. Run all queries. Deliver one file per topic to `djinn/research/marcus/law/`. Sign every file `— Marcus`.**

---

## What This Builds

A fully stocked law reference layer for Djinn. Dual purpose:
1. Help Javier understand and apply law in real business situations (LLC, contracts, compliance)
2. Help law students understand courses, the LSAT, and bar prep

---

## Research Queries — Run All of These

### Path & School
1. **Law school paths** — undergraduate requirements, timeline (2–4 yr undergrad + 3 yr JD), part-time vs full-time, online vs in-person accredited programs, cost ranges, ROI by specialization
2. **LSAT breakdown** — sections (LR, RC, AR), scoring scale, prep timeline, top study resources (Khan Academy, 7Sage, Blueprint), score percentiles vs school tiers
3. **Bar exam structure** — UBE vs state-specific, MBE subjects, essay components, pass rates by state, prep programs (Themis, Barbri, Kaplan)

### Substantive Law
4. **Contract law fundamentals** — offer, acceptance, consideration, capacity, legality, breach types, remedies (expectation, reliance, restitution), UCC vs common law distinctions
5. **Torts** — negligence (duty, breach, causation, damages), strict liability, intentional torts, defamation, products liability, comparative vs contributory negligence
6. **Civil procedure** — jurisdiction (personal, subject matter), venue, pleading standards (Twombly/Iqbal), discovery, motions, appeals
7. **Corporate law fundamentals** — fiduciary duties (duty of care, loyalty), business judgment rule, piercing the corporate veil, shareholder rights, M&A basics, securities basics

### Business Formation & Compliance
8. **LLC formation** — articles of organization (required fields, state variations), operating agreements (member vs manager-managed), single-member vs multi-member, registered agent requirements
9. **Business entity comparison** — sole proprietor vs LLC vs S-corp vs C-corp: liability, taxation, formation cost, admin burden, when each makes sense
10. **Compliance fundamentals** — what compliance means for a small business: licenses, permits, EIN, state/federal tax registration, annual reports, record-keeping requirements
11. **Contract drafting basics** — essential clauses for a service business (scope of work, payment, IP ownership, limitation of liability, dispute resolution, governing law)

### Applied
12. **Legal research methods** — how to use Westlaw, LexisNexis, Google Scholar, CourtListener for case research; how to read a case (parties, facts, issue, holding, reasoning)
13. **When you need a lawyer vs DIY** — situations where self-help is viable, situations where it isn't, how to find and vet attorneys, alternative dispute resolution (mediation, arbitration)

---

## Output Format Per File

```markdown
---
subject: Law/<Subcategory>
tags: [law/<area>/<topic>, djinn-law]
source: Marcus research · Perplexity Pro
created: YYYY-MM-DD
---

# Title

## Summary
## Key Concepts
## Details
## Cases / Statutes / References
## Applied — What This Means in Practice
## Related [[wiki-links]]

— Marcus
```

---

## Deliver To
`djinn/research/marcus/law/` — one .md file per query above (13 files total)

After completing all 13, append a summary entry to `COMMS.md`:
> Marcus: TASK-037 complete — 13 law research files delivered to djinn/research/marcus/law/
