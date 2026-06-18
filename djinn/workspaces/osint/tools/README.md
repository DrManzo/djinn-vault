# Tools — README

This directory tracks the OSINT tool build queue and existing tool inventory for the OSINT workspace.

---

## Existing Tools (in djinn-tools)

These tools already exist in the `djinn-tools` repo and are available to OSINT agents now:

| Tool | Location | Used By | Status |
|---|---|---|---|
| `djinn-bore-core` | djinn-tools | SOCIAL | Active |
| `djinn-trend-agent` | djinn-tools | TREND | Active |
| `djinn-social-analyst` | djinn-tools | SOCIAL | Active |
| `djinn-style-scrape` | djinn-tools | RECON | Active |
| `djinn-vault-enrich` | djinn-tools | CORRELATOR, TREND | Active |
| `djinn-discord-gateway` | djinn-tools | SOCIAL | Active |
| `djinn-discord-watch` | djinn-tools | SOCIAL | Active |

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
