# Typhon's Forge — Business Strategy
### Marketability · Profitability · Implementation · Promotion

**Version:** 1.0  
**Date:** 2026-05-31  
**Author:** Javier (DrManzo) — Analysis by Claude

---

## What This Is

Typhon's Forge is a fully-built, AI-powered 3D print commission shop operating system. Not a concept — deployed and running on Calliope right now. The complete pipeline:

```
Discord file drop → mesh analysis + renders → FairPrintAgent quote
→ customer ORDER → encrypted DM flow → payment confirm
→ plate batching → confirm print → Moonraker execution
→ progress monitoring → shipping label → tracking DM to customer
```

Every step is automated. The operator touches it twice: `paid ORD-XXXX` and `ship ORD-XXXX`.

---

## Library Inventory

| Category | Pieces |
|----------|--------|
| **Puffco/dab accessories** | Proxy tornado recycler, proxy core holster v9, Puffco cup, quad uptake recycler spec |
| **Decorative** | 6 vase styles, 3 skeleton hand/rose pieces, 2 spiral pots, tree flower pot |
| **Practical** | GoPro tripod, mic stand, GoPro/mic plate |
| **Custom/branded** | Typhon's Forge challenge coin, Javi vase, The Terp Tribe camood STL |

The Puffco accessories are the highest-value catalog. That's the primary niche.

---

## Marketability

### The Print Shop (Typhon's Forge)

**Why it's strong:**

1. **Smoking accessories are a proven Etsy category.** The system auto-applies a 35% market upcharge because DDG market research verified the market pays it. PLA is blocked for heat-exposed parts, PETG enforced — that's a real quality differentiator vs. casual sellers.

2. **"The Terp Tribe" branding** on the coin STL establishes a community angle. That's the target audience for the Puffco accessories — terp/dab collectors are buyers, not browsers.

3. **Batch printing is the profit lever.** 3 orders separately = 8h. Batched on one plate = 5h. Each customer is billed independently. That's the actual margin multiplier.

4. **Repeat design library = zero design cost on repeat orders.** The Forge coin at 3hr design time = $92.91 floor one-off. Same coin in batch = ~$8–10 floor. Volume turns into real profit fast.

### The System Itself (Future Product)

~50,000 active hobbyist print sellers on Etsy quote manually, track orders in spreadsheets, and do shipping through USPS.com. Djinn's print stack solves all of that. `djinn-shop-deploy` single-command installer already exists. Packaging estimate: 4–6 weeks to genericize config. Price point: $150–300 one-time or $30–50/month SaaS.

**Do not conflate these two revenue streams.** The shop is real money now. The software product is a future play after the shop proves the system works.

---

## Profitability

### Immediate — Shop Operation

| Product | Est. Fair Market Price | Notes |
|---------|------------------------|-------|
| Puffco proxy recycler | $45–65 | PETG + 35% smoking upcharge |
| Puffco cup attachment | $35–55 | same |
| Decorative vases | $15–30 | commodity_decor weights |
| Custom coin/badge | $60–90 first / $10–15 repeat batch | design cost amortizes fast |
| Custom part (client file) | $30–80 | depends on print time |

At 5–10 orders/month batched, projected $300–700/month gross on a printer with a $0.20/hr machine cost. The system enforces 30% minimum margin in code — impossible to accidentally under-price.

### The Key Numbers

| Metric | Value |
|--------|-------|
| Machine cost rate | ~$0.20/hr (electricity + depreciation + maintenance) |
| Minimum margin enforced | 30% |
| Smoking accessory upcharge | 35% |
| Express Print premium | 35% |
| Failure coverage built into floor | 8% (92% success rate assumption) |
| Batch efficiency gain | ~40% time savings vs separate prints |

### Longer-Term — Software Product

Once the shop runs live orders and the margin is proven, the packaging path:
- `config.yaml` — all machine IPs, tokens, pricing config in one file
- `install.sh` — guided setup wizard
- Test on a clean machine (this is the gate)
- Landing page + GitHub release
- Target: Etsy 3D print sellers, hobbyist print shop operators

---

## Implementation — What's Blocking Revenue

### Immediate (This Week)

1. **EasyPost API key** — free at easypost.com → `~/.config/djinn/easypost.env`
2. **Real shop address** → `~/.config/djinn/shop.json`
3. **Run one test order** through the full pipeline end-to-end
4. **Etsy shop listing** for the Puffco pieces already in library — use renders from `djinn-print-consult` as product photos

### Near-Term (2–4 Weeks)

5. **Payment formalization** — Zelle/CashApp works but Stripe integration unlocks lower friction and potential Etsy-native payment
6. **Instagram/TikTok** for Puffco accessories — the terp/dab community buys custom accessories heavily; visual product content
7. **First Reddit post** to r/3Dprinting and r/SideProject — "here's what I built," not a pitch

### Software Product Path (4–8 Weeks)

8. `config.yaml` — pull all hardcoded IPs/tokens/paths into one file
9. `install.sh` — guided setup wizard writes config, installs services
10. Clean-machine test (this is the gate — if it doesn't install cleanly, it's not a product)
11. Landing page + GitHub release

---

## Promotion

### The Hook That Lands

> **"I replaced the 6 most annoying parts of running a print shop with one system that talks to itself."**

The COMMS.md screenshots — Claude giving architecture specs to Salomon, Marcus delivering accounting code — are content nobody else is making. The inter-agent conversation thread is genuinely novel. Lean into it.

### Platform Priority

**1. Reddit** (zero cost, immediate reach)
- r/3Dprinting, r/SideProject, r/Entrepreneur
- Text post + one demo video
- "I automated my print shop" posts reliably perform
- No pitch — just show the thing

**2. TikTok / Reels** (most shareable format)
- The Discord demo clip: file drop → renders appear → quote posted — 30 seconds, no explanation needed
- This is the strongest top-of-funnel piece
- See `CONTENT-IDEAS.md` for full clip list

**3. YouTube Series** (long-term SEO)
- "I Built an AI Print Shop" — EP01–10 playlist
- Low competition keywords: "AI 3D printing business", "3D print shop automation"
- See `CONTENT-IDEAS.md` for full episode list

**4. Puffco / Terp Community** (targeted conversion)
- r/puffco, Puffco Discord servers, terp collector groups
- Show the product, not the system
- Custom accessories sell here; community has high willingness to pay

### Content Assets Already Available

- Git history of the full build
- COMMS.md inter-agent conversation thread
- Real Discord bot interaction recordings
- `djinn-print-consult` renders (front, side, overhang map)
- Dashboard screenshots (queue, orders, finance pages)
- Batch proposal messages with time savings calculations

---

## What This Replaces

| Before | After |
|--------|-------|
| Google "what should I charge" | Market search runs automatically, margin calculated |
| Open slicer, set settings manually | Drop file → consult report auto-generated |
| Copy-paste address into USPS.com | One Telegram command → label downloaded |
| Excel spreadsheet for orders | SQLite DB, full accounting, XLSX export |
| Remember last print settings for this file | Prior notes shown in every future consult |
| Check Discord + Telegram + printer separately | One dashboard at localhost:5000 |
| 6 separate tools | One system |

---

## Related Documents

- [[DJINN-3D-PRINT-PIPELINE]] — full technical architecture
- [[DJINN-CAPABILITIES]] — capability-by-capability breakdown
- [[CONTENT-IDEAS]] — full video series and promotion plan
- `commissions/PRICING_SPEC.md` — FairPrintAgent formula detail
- `agent/AGENT_STACK_SPEC.md` — six-agent design pipeline

---

*Typhon's Forge — Javier (DrManzo)*  
*Analysis: Claude, 2026-05-31*  
*— Claude*
