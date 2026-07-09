# Typhon's Forge — Content Ideas

**Premise:** You built an AI-powered 3D print shop OS from scratch. Multi-agent, self-documenting, fully automated from order intake to shipping label. Nobody else has this. The build process is the content.

---

## Series: "I Built an AI Print Shop"

Each episode is one piece of the build. The git history, COMMS.md agent conversations, and real Discord bot interactions are your raw footage.

### Episode List

**EP 01 — The Problem**
"Why I stopped taking 3D print commissions"
- Manual quoting, manual slicing, manual updates, manual shipping — all separate tools
- The decision to build one system that handles everything
- Show the chaos before: Discord DMs, separate slicer, no pricing formula
- Hook: "What if you could drop a file in Discord and have an AI quote it, slice it, and track it?"

**EP 02 — The First Agent (Print Consult)**
"AI that reads your 3D model before you even ask"
- Drop an STL → renders appear → consult report with real estimates
- Show the overhang map, the profile comparison, the prior print history
- The feedback loop: same model printed again → "last time you said increase brim"
- Hook: "It remembers every print you've ever done"

**EP 03 — The Pricing Engine**
"How I stopped guessing what to charge"
- The FairPrintAgent formula: cost floor + market median + job type weighting
- Live demo: drop a Puffco attachment → it searches Etsy → returns market-aware price
- The smoking accessory upcharge and why it exists
- Hook: "The market doesn't care what it cost you to make it"

**EP 04 — The Puffco Build**
"Designing and pricing a 3D printed Puffco accessory with AI"
- Full product story: quad uptake recycler, technical spec, PETG requirement
- Marcus (Perplexity) writes the product spec
- Pipeline: design → consult → quote → print → ship
- Standalone video, targets the Puffco/dab community directly
- Hook: "Custom 3D printed Puffco attachments — here's what goes into making one"

**EP 05 — Four Agents, One System**
"Meet the team: Claude, Salomon, Typhon, Marcus"
- Pull up COMMS.md — show the actual agent-to-agent conversations
- Claude designs, Marcus researches, Salomon deploys, Typhon stores
- The moment Marcus delivered the EasyPost spec and Claude built it
- Hook: "I run a print shop with four AI agents that talk to each other"

**EP 06 — The Customer Flow**
"What your customers see vs what you see"
- Customer side: drop file → renders → clean quote → ORDER → DM with payment details
- Owner side: full cost breakdown, margin, smoking flag, market comps — all hidden from customer
- Show both views side by side
- Hook: "Professional quoting system. Built in Discord."

**EP 07 — Batch Printing**
"How I print 3 orders at once and charge each separately"
- Plate batching: same material + color → one plate → 40% time savings
- Each customer still has their own order, their own price, their own tracking
- The operational math: 3 orders separately = 8h. Batched = 5h.
- Hook: "Why printing multiple orders together makes your shop more profitable"

**EP 08 — The Accounting System**
"Running a real business, not a hobby"
- Show the dashboard: queue, orders, customers, P&L, balance sheet
- Income statement, accounts receivable, monthly reports
- Exporting to XLSX for taxes
- Marcus's spec → Claude's implementation in one session
- Hook: "This is what a real print shop's books look like"

**EP 09 — One Command to Ship**
"From print complete to label in 30 seconds"
- `ship ORD-0001 usps-priority` in Telegram
- EasyPost fetches USPS/UPS/FedEx rates, shows comparison
- Owner picks, label downloads, customer gets tracking automatically
- Hook: "The most annoying part of running a print shop, automated"

**EP 10 — Packaging It for Others**
"Can I turn my personal AI system into something anyone can run?"
- The config.yaml work — pulling 47 hardcoded IPs/paths into one file
- The install.sh — one command setup
- Testing on a clean machine
- Hook: "If it takes more than 10 minutes to set up, nobody will use it"

---

## Standalone Videos (algorithm bait)

**"I automated my 3D print shop with AI"**
— 8 min overview of the full system. Drop a file, show everything that happens automatically. No explanation of the code. Pure demo. This is the main channel trailer.

**"This AI quotes my 3D prints better than I can"**
— Focus entirely on FairPrintAgent. Show it searching Etsy, finding market comps, applying job type weighting. Compare to how most people quote (guessing).

**"3D printed Puffco proxy attachment — from idea to product listing"**
— Product video. Technical but accessible. Shows the spec, the print profile, the final result. Targets cannabis accessory community.

**"Discord bot that runs my print shop"**
— Screen recording of the full customer flow from Discord. No code, no explanation — just the experience. Most shareable format.

**"I asked four AIs to build me a business"**
— The agent architecture story. Claude, Salomon, Marcus, Typhon. The COMMS.md conversations as a narrative. Wild angle that nobody is covering.

---

## Short-form / Clips

- The moment renders appear in Discord after an STL drop — 30 sec
- The Telegram rate comparison before buying a label — 15 sec
- COMMS.md showing Claude giving orders to Salomon — 20 sec
- The batch suggestion with time savings — 15 sec
- Dashboard showing margin on a completed order — 20 sec

---

## Platform Notes

**YouTube** — Series format. EP01-10 as a playlist. Standalone demos as individual videos. SEO targets: "3D print shop automation", "AI 3D printing business", "Puffco 3D print".

**TikTok / Reels** — Clips only. The Discord bot demo is the strongest. Visual, fast, no explanation needed.

**Reddit** — r/3Dprinting, r/Entrepreneur, r/SideProject. Text post with one demo video. "I built an AI print shop OS — here's what it can do." No pitch, just show the thing.

**Twitter/X** — Thread format. "I automated my 3D print shop. Here's the stack: [thread]". Show COMMS.md screenshot — the inter-agent conversations are genuinely novel content.

---

## The Narrative Hook That Lands

Not "I built a bot." Not "AI automation." 

**"I replaced the 6 most annoying parts of running a print shop with one system that talks to itself."**

The talking-to-itself angle (COMMS.md, four agents, Marcus delivering specs to Claude) is what nobody else has. Lean into it.

---

*— Claude, 2026-05-31*
