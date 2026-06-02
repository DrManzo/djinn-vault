---
title: Contract Drafting Basics
task: TASK-061
created: 2026-06-01
tags: [law, contracts, drafting, IP, scope-of-work, limitation-of-liability]
related: [[llc-formation]] | [[when-you-need-a-lawyer]] | [[legal-research-methods]]
---

# Contract Drafting Basics

## Why Contracts Matter for a One-Person Operation

Contracts are not just for big companies. For a one-person 3D print shop or content studio, a contract does three things: (1) **defines what you agreed to do** so disputes about scope don't happen, (2) **allocates risk** so if something goes wrong, both parties know what the remedy is, and (3) **protects IP** so the design files, templates, and automation you build don't accidentally belong to someone else.

You don't need a lawyer to draft a serviceable contract — but you do need to understand what clauses do what.

---

## The Essential Clauses

### 1. Identification of Parties
Always state full legal names:
```
This Service Agreement is entered into as of [DATE] between
Typhon's Forge LLC, a California limited liability company
("Service Provider"), and [CLIENT LEGAL NAME] ("Client").
```
If you sign as "Javier" without your LLC, you may be contracting personally — not through your protected entity.

### 2. Scope of Work
The most-litigated clause in service contracts. Be specific:
- What you will do (deliverables, specs, dimensions, file formats)
- What you will NOT do (out of scope — list explicitly)
- Timeline and milestones
- What happens if the client changes the scope after agreement (change order process)

**Bad scope:** "Design and print custom accessories."
**Good scope:** "Design and print one (1) custom dry herb bowl, approximately 45mm diameter, in black PETG filament, delivered as physical product within 10 business days of approved 3D model. Revisions limited to two (2) rounds. Additional revisions billed at $[X]/hr."

### 3. Payment Terms
- Total price (or hourly rate + cap)
- Payment schedule (50% upfront, 50% on delivery is standard for custom work)
- Late payment: "Invoices unpaid after 30 days accrue 1.5% monthly interest."
- Payment method and currency
- What happens if client doesn't pay: your right to withhold delivery or retain deposit

### 4. Intellectual Property Ownership
This clause determines who owns the design files, molds, templates, and tools you create during the project. Default copyright rule: **the creator owns it** unless there is a written assignment.

Two common models:

**Work-for-hire (client owns everything):**
```
All deliverables created specifically for this project, including
3D model files, design files, and physical prototypes, are
assigned to Client upon receipt of full payment.
```

**License model (you keep IP, grant use rights):**
```
Service Provider retains ownership of all tools, templates,
pre-existing IP, and underlying design methodologies. Upon receipt
of full payment, Client is granted a non-exclusive, non-transferable
license to use the deliverables for [personal/commercial] purposes.
```

For Javier's situation: the **license model is almost always better**. You keep your design templates, printer configurations, workflow scripts, and AI tools. You grant the client the right to use the finished product. This is how studios and agencies operate.

IP clause should also cover:
- **Confidentiality**: client's design ideas are confidential; your underlying tools are confidential
- **Pre-existing IP**: explicitly carve out everything you brought to the project before it started
- **No reverse engineering**: client may not reverse-engineer your 3D designs or methods

### 5. Limitation of Liability
Without this clause, your liability for a breach could theoretically equal all damages the client suffered — including consequential damages (lost revenue, lost profits, etc.) that dwarf your contract price.

Standard clause:
```
In no event shall Service Provider's total liability to Client
exceed the total fees paid by Client under this Agreement.
Service Provider shall not be liable for any indirect,
incidental, special, or consequential damages, including
lost profits, even if advised of the possibility of such damages.
```

California enforces limitation of liability clauses in B2B contracts between sophisticated parties. They can be challenged if they're for **gross negligence or intentional misconduct** — but for normal business disputes, they hold.

### 6. Indemnification
Who defends and pays if a third party sues because of work done under this contract?

Mutual indemnification is fair:
```
Each party agrees to defend, indemnify, and hold harmless the other
party from claims arising out of its own negligence, breach of this
Agreement, or violation of applicable law.
```

Watch out for one-sided indemnification clauses in client paper that make you indemnify them for everything — common in corporate procurement agreements.

### 7. Termination
- Either party for convenience: "Either party may terminate with 14 days written notice."
- For cause: "Either party may terminate immediately upon material breach if not cured within 10 days of written notice."
- What happens to work in progress: does client pay for work completed? Do you deliver partial work?
- What happens to IP on termination without payment: you retain all files until paid in full

### 8. Dispute Resolution
Three tiers, from cheapest to most expensive:
1. **Negotiation** — parties attempt to resolve directly (30 days)
2. **Mediation** — neutral third party facilitates (non-binding, ~$500–$2,000)
3. **Arbitration or Litigation** — binding decision

For small business disputes in California under $12,500 (individuals) or $6,250 (businesses): **small claims court** is often the fastest, cheapest option. No lawyers allowed in court; $30–$100 filing fee; decision in 1–2 months.

Choice of law clause: `This Agreement shall be governed by the laws of the State of California.`
Venue clause: `Any disputes shall be resolved in San Bernardino County, California.`

### 9. Force Majeure
Excuses performance when events outside your control (pandemic, natural disaster, government shutdown) prevent delivery. Standard clause:
```
Neither party shall be liable for delays caused by circumstances
beyond their reasonable control, including acts of God, natural
disasters, government actions, or supply chain disruptions.
```

### 10. Entire Agreement / Integration Clause
```
This Agreement constitutes the entire agreement between the parties
and supersedes all prior negotiations, representations, and understandings.
No modification shall be binding unless in writing and signed by both parties.
```
This prevents a client from claiming a verbal promise made during negotiations binds you.

---

## Contract Anatomy — Quick Template Outline

```
1. Parties
2. Effective Date
3. Scope of Work / Deliverables
4. Payment Terms
5. Intellectual Property
6. Confidentiality
7. Limitation of Liability
8. Indemnification
9. Termination
10. Dispute Resolution
11. Governing Law and Venue
12. Force Majeure
13. Entire Agreement
14. Signatures
```

---

## Reading a Contract You Didn't Write

When a client or vendor sends you a contract:

1. **Find the IP clause first.** Does it claim ownership of your tools, templates, or pre-existing IP? If yes, negotiate that out before signing.
2. **Find the indemnification clause.** Is it mutual or one-sided? One-sided = negotiate.
3. **Find the limitation of liability clause.** Is there one? If not, you're exposed to unlimited damages — add one before signing.
4. **Find auto-renewal clauses.** Many vendor agreements auto-renew unless you send written notice 30–90 days before expiration.
5. **Find the governing law clause.** If it says Delaware courts, that's expensive for you. Push for California, San Bernardino County.

---

## Common Mistakes in Self-Drafted Contracts

1. **Vague scope** — "design work" without specs is the seed of every freelance dispute
2. **No payment schedule for custom work** — always get a deposit
3. **No IP clause at all** — the default is creator owns it; explicitly state your position
4. **No termination clause** — what if the project drags forever?
5. **Using "we agree" in body text instead of numbered, signed clauses** — email chains saying "sounds good" can be a contract but are hard to enforce
6. **Not signing as the LLC** — you're contracting personally, not through your protected entity

---

## Where to Get Templates
- **Docracy**: free open-source contracts
- **Law Insider**: real clauses from real corporate contracts (educational use)
- **LegalZoom / Rocket Lawyer**: paid templates ($5–$50), reasonable quality for small business
- **SCORE**: free business mentoring + contract templates via SBA partnership
- **GrandCanyon University Law Library**: check if your student access includes legal template databases

---

## Sources
- ECL Lewis Law (2025) — Essential Clauses Every Business Contract Needs
- Hutchings Law Group (2025) — Key Clauses to Protect Intellectual Property
- Sirion (2026) — Mastering Intellectual Property Clauses
- The Barrister Group (2026) — Ultimate Guide to Service Agreements
- California Courts Self-Help — Small Claims: https://selfhelp.courts.ca.gov/small-claims-california
