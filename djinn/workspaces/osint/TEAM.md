# OSINT — Agent Team Roster

**Department:** OSINT Intelligence
**Last Updated:** 2026-06-19

---

## Active Agents

### 1. RECON — Web Recon Specialist

**Role:** Passive open-web intelligence. Owns all surface-level footprinting of targets using publicly accessible information — no credentials, no active probing.

**Responsibilities:**
- Google/DuckDuckGo dork queries for target enumeration
- Site structure and metadata analysis (robots.txt, sitemaps, headers)
- Public records and government database lookups
- LinkedIn, GitHub, and professional profile harvesting
- News archive and press mention monitoring
- Job posting intelligence (reveals tech stack, team structure, expansion plans)

**Key Tools:**
- DuckDuckGo (already in Salomon's tool stack)
- Google dorks via Salomon search lane
- No dedicated OSINT scraping tool yet — `djinn-style-scrape` was previously
  listed here but is actually a Djinn Media aesthetic-reference finder, not
  a target-recon tool; removed 2026-07-13, see `tools/README.md`

**Escalation:** Domain/IP infrastructure hands off to `NETPROBE`. Social account enumeration hands off to `SOCIAL`. Visual assets (photos, avatars) hand off to `VISUAL`.

---

### 2. SOCIAL — Social Intelligence Agent

**Role:** Cross-platform social media intelligence. Owns account enumeration, handle lookup, community monitoring, and social graph mapping.

**Responsibilities:**
- Username/handle enumeration across 200+ platforms — currently manual (see note below)
- Twitter/X, Reddit, Discord, Telegram, Instagram public profile harvesting
- Community membership and group affiliation mapping
- Post history analysis and keyword extraction
- Follower/following graph analysis
- Cross-platform identity linkage (same person across handles)
- Real-time community signal monitoring — currently manual (see note below)

**Key Tools:**
- No dedicated OSINT tool yet. `djinn-bore-core`, `djinn-social-analyst`,
  `djinn-discord-gateway`, and `djinn-discord-watch` were previously listed
  here but are a 3D-print tool and Javier's own Discord/Meta-analytics ops
  tools, respectively — none do third-party account enumeration or
  monitoring. Removed 2026-07-13, see `tools/README.md`.
- `djinn-social-map` (planned) — graph builder, not yet built

**Escalation:** Social graph synthesis hands off to `CORRELATOR`. PII-level findings require operator Tier 3 confirm before storage. Profile photos hand off to `VISUAL`.

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
- No dedicated OSINT tool yet. `djinn-trend-agent` and `djinn-vault-enrich`
  were previously listed here but are Djinn Media's own hashtag/content-trend
  poller and the vault knowledge-curation pipeline, respectively — neither
  monitors external targets/keywords. Removed 2026-07-13, see `tools/README.md`.
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
- No dedicated correlation tool yet. `djinn-vault-enrich` was previously
  listed here but is the general vault knowledge-curation pipeline (RAW →
  `i notes/` → `references/`), not cross-source entity correlation.
  Removed 2026-07-13, see `tools/README.md`.

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

### 8. VISUAL — Reverse Image Intelligence Agent

**Role:** Visual asset intelligence. Owns reverse image search, EXIF/XMP/IPTC metadata extraction, photo-based entity attribution, and cross-platform image tracking. Runs when any photo, avatar, logo, or image asset is part of the seed data or discovered during an op.

**Responsibilities:**
- Profile photo reverse search across TinEye, Yandex, Google Images, and Bing Visual Search
- EXIF metadata extraction via ExifTool (device model, timestamps, GPS — GPS is Tier 3)
- Visual asset cross-platform tracking (same avatar across accounts = high-confidence same-person signal)
- Logo and brand image matching for ORG-OP targets
- Deleted image recovery via Wayback Machine and Google cache
- PimEyes facial recognition (Tier 3 only — explicit operator confirm required, never autonomous)

**Key Tools:**
- TinEye — exact/near-duplicate image matching
- Yandex Images — best free face matching
- Google Images reverse search
- Bing Visual Search
- ExifTool (local CLI) — full metadata extraction
- PimEyes — Tier 3 facial recognition, operator confirm required
- No dedicated tool for image harvesting from profile URLs. `djinn-style-scrape`
  was previously listed here with a fabricated `--images` flag — audited
  2026-07-13, see `tools/README.md`. Download images manually until a real
  tool exists.

**Gateway tier:** Entry at Tier 2. GPS EXIF → Tier 3 hard stop. Facial recognition → Tier 3 explicit confirm. Home address from visual → Tier 4 stop.

**Integration:**
- Receives handoff from PERSON-OP Phase 1 and SOCIAL when photo seed exists
- Feeds confirmed platform matches back to SOCIAL for account enumeration
- Feeds new domains/URLs discovered in results back to NETPROBE
- All findings tagged `[VISUAL-CONFIRMED]` or `[VISUAL-CANDIDATE]` for SCRIBE

**Escalation:** No autonomous facial recognition. GPS coordinates withheld until Tier 3 operator confirm. Subject is a minor → all visual ops stop immediately.

---

*OSINT Team Roster — part of the Djinn system*
