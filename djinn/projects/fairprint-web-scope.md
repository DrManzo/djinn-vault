---
subject: FairPrintAgent Web UI — Scope Document
tags: [djinn, project, fairprint, typhons-forge, scope]
created: 2026-05-25
status: ready-to-build
owner: Claude + Javier
phase: scoped — waiting on audience validation signal
---

# FairPrintAgent Web UI — Scope

**Trigger:** When Instagram content builds enough audience that makers are asking about the pricing tool, this ships. Not before.

**Signal to start:** DMs asking "how do you price your prints?" or a post about pricing that gets 50+ saves/comments. That's demand validated.

---

## What It Does

A web form that does exactly what `djinn-print-quote --simple` does — no terminal required.

Input → three numbers.

---

## Form Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| Piece name | text | — | Used for library lookup + smoking detection |
| Weight (grams) | number | — | Finished part weight |
| Print time (hours) | number | — | Full print runtime |
| Spool cost ($/kg) | number | $22 | PLA default, user can override |
| Labor (minutes) | number | 20 | Hands-on prep + post-process |
| Size | radio: small / large / auto | auto | For smoking accessories — small=lower half comps, large=upper half |

**Optional (collapsed by default):**
- Hourly rate ($/hr) — default $20
- Design hours — 0 if using a library model
- Quantity — affects test-run fee (waived at 13+)

---

## Output

Three numbers, clearly labeled:

```
Cost floor:   $XX.XX  ← never go below this
Fair market:  $XX.XX  ← what to charge
Premium:      $XX.XX  ← rush/exclusive ceiling
```

Below the numbers: one-line breakdown showing material + machine + labor + test fee.

No login required for free tier.

---

## Tech Stack

**Option A — Recommended for MVP:**
- Static HTML/CSS/JS frontend (Cloudflare Pages or Netlify — free tier)
- Single Python serverless function (Cloudflare Workers with Python support, or Vercel)
- No database — stateless, each request is self-contained
- Cost: $0/month until significant traffic

**Option B — If market fetch is needed:**
- Same frontend
- Backend: FastAPI on Fly.io (free tier: 3 shared CPU, 256MB RAM)
- Adds DuckDuckGo market comp fetch — returns all three tiers (cost floor / fair market / premium)
- Cost: $0/month on free tier, ~$5/month if traffic grows

MVP ships as Option A (cost floor only, no live market comps). Upgrade to Option B if users want live Etsy comps.

---

## URL Structure

```
fairprintagent.com   (if domain purchased)
  OR
typhonsforge.com/price  (simpler — same brand)
```

Recommend subdomain of existing brand over new domain. Less friction, more trust from existing audience.

---

## Free vs Paid Tier

| Feature | Free | Paid ($5–10/mo) |
|---------|------|-----------------|
| Quotes per month | 5 | Unlimited |
| Market comp fetch (live Etsy data) | No | Yes |
| Quote history / price sheet export | No | Yes |
| Multi-material (resin, PETG) | No | Yes |

Free tier is enough to price 1–2 jobs. Most active sellers hit the cap quickly — natural conversion pressure.

**No login required for free tier** — just a session cookie counting quotes. Paid tier requires email only (no OAuth complexity for MVP).

---

## Build Sequence

```
1. Static form → calls local Python function → returns cost floor only    (~4 hrs)
2. Deploy to Cloudflare Pages + Workers                                   (~2 hrs)
3. Add smoking detection + size tier to output                            (~1 hr)
4. Add market comp fetch (Option B upgrade)                               (~4 hrs)
5. Add quote counter + paywall prompt at limit                            (~3 hrs)
6. Stripe integration for paid tier                                       (~4 hrs)
```

Total to MVP (steps 1–3): ~7 hours of build time.
Total to monetized product (steps 1–6): ~18 hours.

---

## What Claude Needs to Start

- Signal from Javier: "audience is ready, build it"
- Decision: typhonsforge.com/price OR standalone domain
- Decision: Option A (cost floor only) OR Option B (market comps) for v1

---

*— Claude, 2026-05-25*
