---
subject: Typhon's Forge — Monetization Plan
tags: [djinn, project, active, typhons-forge, fairprint, marketing]
created: 2026-05-25
status: active
owner: Claude + Javier
phase: content-first
---

# Project: Typhon's Forge Monetization

Two-track strategy: build the brand through content first, convert audience into product revenue second. Both tracks run on the same story — Javier built AI tooling to run his print operation and price commissions without guessing.

---

## The Story

*"I built an AI pricing tool so I'd stop underselling my prints."*

That's the hook. Not a tech tutorial. Not a print showcase. The story of a maker who built systems around the craft — and what those systems actually do for the business of making.

The differentiator: Javier combines psychological self-awareness, systems thinking, and AI tooling in a way most maker-content creators don't. The content isn't just "here's a cool print" — it's "here's how I think about this."

---

## Track 1 — Brand (Content First)

**Goal:** Build an audience on Typhon's Forge that trusts Javier as someone who takes the business of making seriously.

**Platform priority:** Instagram (already active since 2026-05-24) → YouTube Shorts → YouTube long-form

**Content angle:**
- Shift from pure print showcase to "print + the numbers behind it"
- Show FairPrintAgent running on real jobs: cost floor, fair market, live Etsy comps
- Explain each line in plain language — makers feel the pain point immediately because they've all undercharged
- The "never go below this" cost floor is the visual anchor for every pricing post

**Content formats:**
- Reel/Short: start a print → run the quote while it's printing → show the three numbers → explain them
- Carousel: breakdown of a specific job (material + machine + labor + margin = what to charge)
- Educational posts: the formula itself — why 40% margin, why machine time ≠ labor time

**Niche:** Business of making. Less competition than pure print content. Makers who want to go from hobby to income.

---

## Track 2 — Product (After Audience Exists)

**Goal:** Turn FairPrintAgent into a web tool accessible to makers without terminal skills.

**Current state:** Python CLI — requires terminal comfort. Not marketable to most makers.

**Required before launch:**
- Web form UI: piece name, grams, hours, spool cost → outputs the three numbers
- No login required for free tier
- Hosted (minimal infra — static + serverless function is enough)

**Business model:** $5–10/month SaaS, free tier with limited quotes/month.

**Target customers:** Etsy sellers, small print shops, hobbyists doing commissions.

**Launch strategy:** Warm audience from Track 1 → announce web version → free tier drives signups → convert to paid.

---

## Sequence

```
Now          → Test FairPrintAgent on every completed print. Build price sheet.
Now          → Shift Instagram content toward pricing/business angle.
+2–4 weeks   → Consistent content cadence established, audience growing.
+4–8 weeks   → Build web version of FairPrintAgent.
+8–12 weeks  → Launch web tool to existing audience.
```

---

## Assets Already Built

| Asset | Status | Notes |
|-------|--------|-------|
| FairPrintAgent CLI | ✅ Working | `djinn-print-quote`, validated on Mario Pipe + coin |
| Instagram | ✅ Active | @typhonsforge, posting since 2026-05-24 |
| 9-agent media stack | ✅ Built | Needs OpenClaw restart to activate |
| Print queue + history | ✅ Running | `quote-history.jsonl` logs every quote |
| YouTube pipeline | ✅ Built | 8-stage script production workflow ready |

---

## Open Questions

- [ ] What's the Instagram handle / exact URL? — @Javier to confirm
- [ ] Web version: build in-house or use a no-code form tool first to validate demand?
- [ ] Pricing model: per-quote vs subscription vs one-time?

---

## Next Actions

- [ ] Run `djinn-print-quote` on every completed print — build a real price sheet — @Javier
- [ ] Film first "pricing a real print" Reel on Instagram — @Javier
- [ ] `systemctl --user restart openclaw-gateway.service` on Salomon to activate media agents — @Javier
- [ ] Scope web version UI (form fields, output display) — @Claude when ready

---

*— Claude, 2026-05-25*
