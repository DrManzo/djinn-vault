# Tools — README

This directory tracks the OSINT tool build queue and existing tool inventory for the OSINT workspace.

---

## Existing Tools (in djinn-tools)

**None, as of 2026-07-13.** This table previously listed 7 tools (`djinn-bore-core`,
`djinn-trend-agent`, `djinn-social-analyst`, `djinn-style-scrape`,
`djinn-vault-enrich`, `djinn-discord-gateway`, `djinn-discord-watch`) as
"Active" for OSINT use. Audited via `djinn-doc-check` + manual inspection —
every one of them is a real, working tool elsewhere in Djinn (3D-print
STL prep, Djinn Media's own trend/analytics/Discord ops, vault
knowledge-curation), but none of them do third-party OSINT collection.
They were cross-listed by loose name association (SOCIAL↔"social",
TREND↔"trend") rather than actual capability review. Until one of the
Planned tools below is built, every OSINT agent runs on manual web
search/API calls — see `djinn/workspaces/osint/targets/2026-07-12_javier-self-audit.md`
for what that actually looked like in practice.

---

## Planned Tools (build queue)

These tools need to be built and added to `djinn-tools` to complete the OSINT stack:

### 1. `djinn-net-probe`

**Owner:** NETPROBE agent  
**Priority:** High  
**Purpose:** Domain/IP/WHOIS/DNS/ASN/SSL footprinting in a single unified tool  
**Inputs:** Domain name, IP address, or ASN number  
**Outputs:** Structured JSON with WHOIS, DNS records, IP geo, ASN, SSL cert info, reverse IP neighbors  
**APIs to integrate:** RDAP, crt.sh, ip-api.com, Shodan public API  
**Estimated build:** Medium — 3–5 Python modules, ~300 LOC  

---

### 2. `djinn-archive-fetch`

**Owner:** ARCHIVE agent  
**Priority:** Medium  
**Purpose:** Retrieve historical snapshots and deleted content from archival sources  
**Inputs:** URL, domain, or keyword  
**Outputs:** List of snapshots with timestamps, raw HTML dumps, extracted text  
**APIs to integrate:** Wayback Machine CDX API, CommonCrawl index, archive.ph  
**Estimated build:** Medium — 2–3 Python modules, ~200 LOC  

---

### 3. `djinn-social-map`

**Owner:** SOCIAL agent  
**Priority:** Medium  
**Purpose:** Build cross-platform social graph from enumerated accounts  
**Inputs:** List of confirmed account URLs/handles  
**Outputs:** Graph JSON (nodes = accounts, edges = confirmed connections), Obsidian-compatible MD link map  
**APIs to integrate:** Public platform APIs (Twitter v2 public, Reddit API, GitHub API)  
**Estimated build:** High — graph data model + 4–5 platform adapters, ~500 LOC  

---

## Tool Build Protocol

When building a new OSINT tool:

1. Create the tool in `djinn-tools` following existing tool structure
2. Update this file — move tool from Planned to Existing
3. Update `TEAM.md` agent brief to reference the new tool
4. Commit to both repos:
   - `djinn-tools`: `feat(osint): add djinn-net-probe tool`
   - `djinn-vault`: `docs(osint): update tools/README.md — djinn-net-probe active`

---

*Tools Registry — OSINT / Djinn system*
