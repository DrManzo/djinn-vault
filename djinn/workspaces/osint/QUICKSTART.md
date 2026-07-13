# OSINT QUICKSTART — First 15 Minutes

> Read this before any operation. This is your ignition sequence.

---

## Standard Start (You Have a Target)

1. **Open a target file**
   - Copy `targets/_template.md` → `targets/YYYY-MM-DD_<slug>.md`
   - Fill in: target name, seed data you already have, operation purpose, and operator name
   - Save before doing anything else — this is your evidence anchor

2. **Classify your target type**
   - Person → run `runbooks/PERSON-OP.md`
   - Organization → run `runbooks/ORG-OP.md`
   - Domain / Infrastructure → run `runbooks/DOMAIN-OP.md`
   - Mixed → start with the primary entity, pivot as you go

3. **Set your Gateway tier before collecting**
   - Tier 0–1: Passive reads, public lookups, search engines — auto-approved
   - Tier 2: Enumeration, account probing (non-authenticated) — operator confirm
   - Tier 3: Active scanning, anything touching live infrastructure — explicit checkpoint
   - Tier 4: PII collection, credential-adjacent data — hard stop, operator sign-off required
   - Write the tier in your target file under `gateway_tier:` before you run anything

4. **Assign agents** — pick only what the target warrants
   - Always start: RECON + SCRIBE (every op, no exceptions)
   - Add per need: SOCIAL (handles/accounts), NETPROBE (domains/IPs), ARCHIVE (historical), TREND (signals), CORRELATOR (synthesis only after data exists)

5. **Run RECON first** — always
   - Pull `DORK-BOOK.md`, select the category matching your target type
   - Run 3–5 dorks, record every result URL in the target file
   - Do not click through to anything that requires login — that's Tier 2+

6. **Open a report file**
   - Copy `reports/_template.md` → `reports/YYYY-MM-DD_<slug>.md`
   - SCRIBE logs findings continuously — do not wait until the end

7. **Run agents in order** (per the appropriate runbook)
   - RECON → SOCIAL → VISUAL → NETPROBE → ARCHIVE → TREND → CORRELATOR → SCRIBE
   - Skip agents that don't apply — do not run NETPROBE if there's no domain seed, skip VISUAL if there's no photo/logo seed

8. **Checkpoint at 15 minutes**
   - If you have fewer than 3 confirmed data points: escalate to cold start protocol below
   - If you have 3+ data points: continue through the runbook
   - If you've hit Tier 3 material: stop, flag in target file, get operator confirm

9. **Commit when complete**
   - Run Post-Op checklist (`CHECKLIST.md`)
   - Append DEVLOG entry
   - `git add djinn/workspaces/osint/ && git commit -m "osint(<slug>): <one-line summary>" && git push`

---

## Cold Start (You Know Almost Nothing)

Use when seed data is a single name, handle, email, or domain with no confirmed context.

1. **Lock in what you have** — write it in the target file exactly as given, no assumptions
2. **Run name/handle/domain through a search engine first** — plain query, no dorks yet
   - Goal: establish whether the entity has any public web presence at all
   - Record: top 5 results, any associated platforms, any secondary names found
3. **Identify the entity type from results** — is this a person, org, or infrastructure target?
4. **Pick one pivot** — the single strongest signal from step 2 (e.g., a LinkedIn URL, a GitHub handle, a domain registration)
5. **Run RECON dorks on that pivot only** — do not broaden until the pivot confirms or denies
6. **If pivot confirms**: you now have seed data — continue with standard start from step 2
7. **If pivot denies** (no results, dead ends): try alternate spellings, common username patterns, associated emails
8. **If still nothing after 3 pivot attempts**: document in target file as `low-signal target`, flag for operator review before investing more time

---

## Agent Triage Quick Reference

| What you have | Agents to assign |
|---|---|
| Full name only | RECON, SOCIAL |
| Email address | RECON, SOCIAL, NETPROBE (domain part) |
| Username / handle | SOCIAL, RECON, ARCHIVE |
| Domain name | NETPROBE, RECON, ARCHIVE |
| Company name | RECON, NETPROBE, SOCIAL, TREND |
| IP address | NETPROBE, CORRELATOR |
| Phone number | RECON (dorks), CORRELATOR |
| Photo | VISUAL (TinEye / PimEyes — Tier 2, operator confirm) |

---

*QUICKSTART — OSINT / Djinn system — maintained by SCRIBE*
