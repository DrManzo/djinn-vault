# OSINT — Agent Team Roster

**Department:** OSINT Intelligence  
**Last Updated:** 2026-06-18  

---

## Active Agents

### 1. RECON — Web Recon Specialist

**Role:** Passive open-web intelligence. Owns all surface-level footprinting of targets using publicly accessible information — no credentials, no active probing.

**Responsibilities:**
- Google/DuckDuckGo dork queries for target enumeration
- Site structure and metadata analysis (robots.txt, sitemaps, headers)
- Public records and government database lookups
- LinkedIn, GitHub, and professional profile harvesting
- Image reverse search and visual asset tracking
- News archive and press mention monitoring
- Job posting intelligence (reveals tech stack, team structure, expansion plans)

**Key Tools:**
- DuckDuckGo (already in Salomon's tool stack)
- Google dorks via Salomon search lane
- `djinn-style-scrape` for structured page extraction

**Escalation:** Domain/IP infrastructure hands off to `NETPROBE`. Social account enumeration hands off to `SOCIAL`.

---

### 2. SOCIAL — Social Intelligence Agent

**Role:** Cross-platform social media intelligence. Owns account enumeration, handle lookup, community monitoring, and social graph mapping.

**Responsibilities:**
- Username/handle enumeration across 200+ platforms via `djinn-bore-core`
- Twitter/X, Reddit, Discord, Telegram, Instagram public profile harvesting
- Community membership and group affiliation mapping
- Post history analysis and keyword extraction
- Follower/following graph analysis
- Cross-platform identity linkage (same person across handles)
- Real-time community signal monitoring via `djinn-social-analyst`

**Key Tools:**
- `djinn-bore-core` — handle enumeration
- `djinn-social-analyst` — social media analysis
- `djinn-discord-gateway` + `djinn-discord-watch` — Discord intel
- `djinn-social-map` (planned) — graph builder

**Escalation:** Social graph synthesis hands off to `CORRELATOR`. PII-level findings require operator Tier 3 confirm before storage.

---

### 3. NETPROBE — Network Probe Agent

**Role:** Infrastructure-level intelligence. Owns domain registration, DNS, IP allocation, ASN, hosting provider, and SSL certificate analysis.

**Responsibilities:**
- WHOIS lookups (domain registration, registrant history)
- DNS record enumeration (A, MX, TXT, NS, CNAME, SPF)
- IP geolocation and ASN/hosting provider identification
- SSL/TLS certificate transparency log analysis
- Reverse IP lookups (what else is on this server)
- Subdomain enumeration (passive only at Tier 1; active at Tier 3)
- Shodan and Censys public scan data review
- Email header analysis and MX record mapping

**Key Tools:**
- `djinn-net-probe` (planned — see tools/README.md)
- Public WHOIS APIs (RDAP)
- Certificate Transparency logs (crt.sh)
- Shodan public API

**Escalation:** Active port scanning requires operator Tier 3 confirm. Credential probing is prohibited without explicit Tier 4 authorization.

---

### 4. ARCHIVE — Archive Recovery Agent

**Role:** Historical and deleted content recovery. Owns Wayback Machine queries, Google cache, and other archival source extraction.

**Responsibilities:**
- Wayback Machine snapshot enumeration and download
- Google cache retrieval for recently deleted pages
- CommonCrawl index lookups
- Pastebin and similar paste site monitoring
- GitHub gist and deleted repo recovery (public forks, cached blobs)
- Archive.ph and Ghostarchive retrieval
- Historical WHOIS and DNS change tracking

**Key Tools:**
- `djinn-archive-fetch` (planned — see tools/README.md)
- Wayback Machine CDX API
- CommonCrawl index API

**Escalation:** Findings requiring active scraping or login hand off to `RECON` with Tier 2 escalation.

---

### 5. TREND — Trend Surveillance Agent

**Role:** Market signals, community intelligence, and keyword monitoring. Owns passive real-time feeds for topic and entity tracking.

**Responsibilities:**
- Google Trends analysis for target keywords and entity names
- Reddit and HackerNews community signal monitoring
- RSS feed registry management (`feeds/feed-registry.md`)
- Twitter/X trending topic correlation
- GitHub activity monitoring (stars, forks, issue volume) for tech targets
- Patent and trademark filing surveillance
- Job posting delta analysis (hiring surge = expansion signal)

**Key Tools:**
- `djinn-trend-agent` — existing tool
- `djinn-vault-enrich` — vault enrichment from feed outputs
- Google Trends public API

**Escalation:** Trend data requiring cross-source entity linking hands off to `CORRELATOR`.

---

### 6. CORRELATOR — Cross-Source Correlator

**Role:** The synthesis layer. Takes raw findings from all other agents and builds unified entity profiles, link maps, and confidence-scored conclusions.

**Responsibilities:**
- Entity deduplication across sources (same person/org appearing under different names)
- Link analysis — who connects to whom, how, via which platforms
- Timeline reconstruction from multi-source data
- Confidence scoring for unverified claims
- Contradiction flagging — when two sources conflict
- Final entity profile assembly before `SCRIBE` writes the report
- Pattern detection — repeated behaviors, network clusters, coordinated activity

**Key Tools:**
- Claude (correlation architecture — this is Claude's design lane)
- Obsidian graph view for visualization
- Custom correlation logic via `djinn-vault-enrich`

**Escalation:** Findings requiring legal or ethical review escalate to operator immediately. No autonomous action on flagged findings.

---

### 7. SCRIBE — OSINT Scribe (Always-On)

**Role:** The department's operational memory and report assembler. SCRIBE runs at the end of every operation and maintains the append-only log.

**Responsibilities:**

**Operation Logging:**
- Append every operation to `DEVLOG.md` with timestamp, target slug, agents used, tools run, and files changed
- Log format: `## YYYY-MM-DDTHH:MM:SSZ — <operation-name>` (matches MobileForge DEVLOG format)
- Record suggested commit message at end of every entry

**Report Assembly:**
- Take `CORRELATOR` output and format into `reports/YYYY-MM-DD_<slug>.md`
- Every report includes: target summary, methodology, sources used, findings, confidence level, and recommended next steps
- Flag any PII-sensitive content with `[ENCRYPTED — see vault db]` before writing to vault

**Vault Hygiene:**
- Ensure no plaintext PII appears in markdown files
- Verify Gateway tier was respected before logging the operation
- Archive completed target files to `targets/archived/` when a case is closed

**Escalation:** Never writes speculative conclusions. If evidence is insufficient, SCRIBE writes "Inconclusive — insufficient sourcing" rather than infer.

---

*OSINT Team Roster — part of the Djinn system*
