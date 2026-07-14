# OSINT — Intelligence Department Manual

**Workspace:** `djinn/workspaces/osint/`  
**Department Head:** Javier (DrManzo)  
**Status:** Active — Intelligence Operations  
**Created:** 2026-06-18  

---

## What This Department Does

The OSINT workspace is Djinn's dedicated open-source intelligence department. It owns the full lifecycle of passive and active intelligence gathering operations — from target profiling and social graph mapping to infrastructure footprinting, trend surveillance, and archived data recovery. Every operation is operator-initiated, vault-logged, and governed by the existing Djinn Gateway tier system.

This manual is the canonical reference for every agent operating inside this workspace. Read this first. Then read your individual agent brief.

---

## Department File Ownership

```
djinn/workspaces/osint/
├── OSINT-MANUAL.md                 ← You are here (read-only for agents)
├── TEAM.md                         ← Agent roster and routing
├── DEVLOG.md                       ← All work recorded here (append only)
├── targets/
│   ├── README.md                   ← How to create and manage target files
│   └── _template.md                ← Copy this to start a new target
├── reports/
│   ├── README.md                   ← Report format and naming conventions
│   └── _template.md                ← Copy this to start a new report
├── feeds/
│   ├── README.md                   ← Passive feed registry
│   └── feed-registry.md            ← Active feeds list
├── tools/
│   └── README.md                   ← Tool specs and build queue
└── agents/
    ├── RECON.md                    ← Web recon and passive footprinting
    ├── SOCIAL.md                   ← Social media and account enumeration
    ├── NETPROBE.md                 ← Network, domain, and IP analysis
    ├── ARCHIVE.md                  ← Cached data, Wayback, deleted content
    ├── TREND.md                    ← Trend surveillance and market intel
    ├── CORRELATOR.md               ← Cross-source correlation and synthesis
    ├── SCRIBE.md                   ← Operation logging and report assembly
    └── VISUAL.md                   ← Reverse image search and EXIF metadata
```

---

## Agent Roster Summary

| Agent Code | Name | Specialty | Priority |
|---|---|---|---|
| `RECON` | Web Recon Specialist | Passive footprinting, public records, site analysis | High |
| `SOCIAL` | Social Intelligence Agent | Account enumeration, handle lookup, social graph | High |
| `NETPROBE` | Network Probe Agent | Domain/IP/WHOIS/DNS, infrastructure mapping | High |
| `ARCHIVE` | Archive Recovery Agent | Wayback Machine, cached pages, deleted content | Medium |
| `TREND` | Trend Surveillance Agent | Market signals, community intel, keyword tracking | Medium |
| `CORRELATOR` | Cross-Source Correlator | Multi-source synthesis, entity linking, deconfliction | Critical |
| `SCRIBE` | OSINT Scribe | Operation logs, report assembly, vault entries | Always-on |
| `VISUAL` | Reverse Image Intelligence Agent | Reverse image search, EXIF metadata, photo attribution | High |

See `agents/` directory for full briefs.

---

## Gateway Tier Policy

All OSINT operations are subject to Djinn Gateway enforcement. No autonomous collection runs without operator confirmation at the appropriate tier.

| Operation Type | Gateway Tier | Approval Required |
|---|---|---|
| Passive web reads, public domain lookups | Tier 0–1 | Auto-approved |
| Social media scraping, public profile enumeration | Tier 2 | Auto-approved |
| Active port scanning, credential probing, account testing | Tier 3 | Operator `confirm` required |
| PII collection on real individuals | Tier 3–4 | Operator `confirm` required |
| Any output targeting a named real person | Tier 4 | Explicit written operator intent required |

All collected data routes through the existing encrypted SQLite pipeline. No raw PII is stored in plaintext vault files.

---

## Routing Rules

- **Public web presence, site structure, metadata** → `RECON`
- **Social accounts, handles, cross-platform identity** → `SOCIAL`
- **Domains, IPs, WHOIS, DNS, ASN, hosting** → `NETPROBE`
- **Deleted pages, cached versions, historical snapshots** → `ARCHIVE`
- **Community signals, market trends, keyword monitoring** → `TREND`
- **Linking entities across multiple sources** → `CORRELATOR`
- **All logging, report writing, vault entries** → `SCRIBE` (runs after every operation)
- **Photos, avatars, logos, reverse image search, EXIF metadata** → `VISUAL`

---

## Operation Protocol

Every OSINT operation in this workspace follows this protocol:

1. **Open** `targets/` — create a target file from `_template.md` or open existing target
2. **Define scope** — passive only or active enumeration? Set Gateway tier accordingly
3. **Assign agents** — pick the appropriate specialist agents for the operation
4. **Run** — execute queries, scrapes, and lookups through assigned agents
5. **Correlate** — route all findings through `CORRELATOR` before reporting
6. **Report** — `SCRIBE` assembles output to `reports/YYYY-MM-DD_<slug>.md`
7. **Log** — `SCRIBE` appends session to `DEVLOG.md`
8. **Commit** — `git commit -m "osint(<target-slug>): <summary>"`

---

## Tool Stack

No OSINT-specific tools currently exist. All five previously listed
(`djinn-bore-core`, `djinn-trend-agent`, `djinn-social-analyst`,
`djinn-style-scrape`, `djinn-vault-enrich`) turned out to be real Djinn
tools with unrelated actual purposes (3D-print STL prep, Djinn Media's
own trend/analytics/Discord ops, vault knowledge-curation) — see
`tools/README.md` for the full audit. Every agent currently runs on
manual web search/API calls until one of the tools below is built.

| Tool | Purpose | Status |
|---|---|---|
| `djinn-net-probe` | Domain/IP/WHOIS/DNS/ASN footprinting | Planned — see tools/README.md |
| `djinn-archive-fetch` | Wayback Machine and cached data recovery | Planned — see tools/README.md |
| `djinn-social-map` | Cross-platform social graph builder | Planned — see tools/README.md |

---

## Non-Negotiables

1. **Every operation has a target file.** No collection runs against unnamed subjects.
2. **Every session is logged.** SCRIBE writes it — no exceptions.
3. **Gateway tiers are enforced.** Active enumeration on real people requires operator `confirm`.
4. **PII routes to encrypted storage only.** No names, addresses, or identifiers in plaintext vault files.
5. **DEVLOG.md is truth.** If it's not in the devlog, the operation did not happen.
6. **Passive first.** Active techniques are escalation only — never the starting point.

---

*OSINT — part of the Djinn system*  
*Javier's personal AI operating system*
