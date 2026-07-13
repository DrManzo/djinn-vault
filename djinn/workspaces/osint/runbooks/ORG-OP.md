# ORG-OP — Organization-Targeted OSINT Runbook

> **Target type:** Company, nonprofit, government body, or other organizational entity
> **Owned by:** RECON → VISUAL → NETPROBE → SOCIAL → ARCHIVE → TREND → CORRELATOR → SCRIBE
> **Gateway entry tier:** Tier 1 (passive). Escalate to Tier 2 for employee PII aggregation. Tier 3 for active scanning.

---

## Phase 0 — Seed Data Collection

**Minimum viable seed (pick at least one):**
- Legal company name
- Primary domain
- Known subsidiaries or brands
- HQ location
- Industry / SIC / NAICS code
- LinkedIn company page URL
- Key personnel names (optional — improves Phase 3 yield)

**Record in:** `targets/<slug>.md`

**Also establish at seed stage:**
- Op objective (competitive intel? due diligence? security assessment? public research?)
- Known subsidiaries to include in scope
- Out-of-scope entities (if subsidiary X is explicitly excluded, note it)

---

## Phase 1 — RECON (Org Web Presence & Job Posting Intel)

**Agent:** RECON
**Gateway tier:** Tier 1
**Tools:** Google dorks (see `DORK-BOOK.md → Organization`), Bing, LinkedIn public search

### Steps

1. Run org name dorks:
   ```
   site:<domain> filetype:pdf
   site:<domain> filetype:xlsx OR filetype:docx
   "<Company Name>" "annual report" OR "press release"
   "<Company Name>" inurl:investor OR inurl:careers
   ```
2. Extract job postings — goldmine for tech stack, team structure, and growth signals:
   ```
   site:linkedin.com/jobs "<Company Name>"
   site:greenhouse.io OR site:lever.co OR site:workday.com "<Company Name>"
   ```
   > Job postings reveal: tech stack ("experience with AWS, Terraform, Go"), team structure ("join our 5-person security team"), strategic direction, and hiring velocity.
3. Find public org chart signals:
   ```
   site:linkedin.com "<Company Name>" "VP of" OR "Head of" OR "Director of"
   ```
4. Search for public documents: whitepapers, SEC filings, court records, regulatory filings.
5. Check Crunchbase, PitchBook (public tier), AngelList for funding history and investor list.
6. Capture the official logo and any executive headshots surfaced → hand off to `VISUAL` for reverse image search (impersonator/counterfeit account detection) and EXIF extraction.

**Record at this step:**
- Primary and secondary domains confirmed
- Subsidiary / brand list
- Estimated headcount
- Tech stack hints from job postings
- Key executive names surfaced
- Funding stage and investors (if relevant)
- Logo/photo assets handed to VISUAL, if any

---

## Phase 2 — NETPROBE (Full Domain/IP/ASN Sweep)

**Agent:** NETPROBE
**Gateway tier:** Tier 1 (passive). Tier 3 for active scanning.
**Tools:** djinn-net-probe, crt.sh, SecurityTrails, Shodan, Censys, BuiltWith, BGP.he.net

### Steps

1. **Certificate transparency — subdomain enumeration (passive):**
   ```
   https://crt.sh/?q=<domain>&output=json
   https://crt.sh/?q=%.<domain>&output=json
   ```
2. **DNS full record set:**
   ```
   dig <domain> ANY
   # Key records: A (IPs), MX (email provider), TXT (SPF/DMARC/verification tokens), NS (DNS host)
   ```
3. **Reverse IP — who shares their infrastructure?**
   ```
   https://viewdns.info/reverseip/?host=<ip>&apikey=<key>
   ```
4. **ASN lookup — full IP range owned by org:**
   ```
   https://bgp.he.net/AS<asn>
   # Find ASN first: whois <ip> | grep -i "asn\|origin"
   ```
5. **Shodan org search (passive read):**
   ```
   org:"<Company Name>"
   ssl:"<domain>" port:443
   ```
6. **Censys org search:**
   ```
   https://search.censys.io/search?resource=hosts&q=<domain>
   ```
7. **BuiltWith technology profile:**
   ```
   https://builtwith.com/<domain>
   ```
8. **Email security posture (reveals mail provider and hygiene):**
   - SPF record: `dig TXT <domain>` → look for `v=spf1`
   - DMARC: `dig TXT _dmarc.<domain>`
   - DKIM: check known selectors — `dig TXT google._domainkey.<domain>`

**Record at this step:**
- Full subdomain list from cert transparency
- IP ranges and ASN
- Hosting provider(s) — AWS/GCP/Azure/on-prem mix
- CDN provider (Cloudflare, Fastly, Akamai — affects what Shodan can see)
- Tech stack from BuiltWith
- Email provider and security posture
- Any exposed admin or staging subdomains (note — do NOT access, just record existence)

**Tier 3 escalation:** Active port scanning of discovered IPs requires operator confirm.

---

## Phase 3 — SOCIAL (Official Accounts & Employee Enumeration)

**Agent:** SOCIAL
**Gateway tier:** Tier 1 for official accounts. Tier 2 for employee PII aggregation.
**Tools:** djinn-bore-core (org handle), LinkedIn public search, Twitter/X advanced search

### Steps

1. **Official social account inventory:**
   - LinkedIn company page: follower count, employee count, recent posts
   - Twitter/X: `@handle` presence, follower count, post frequency
   - GitHub org: `github.com/<org>` — public repos, contributor list
   - YouTube, Facebook, Instagram (industry-dependent)
2. **Employee enumeration from LinkedIn (public, no auth required):**
   ```
   site:linkedin.com/in "<Company Name>"
   site:linkedin.com/in "<Company Name>" "security" OR "engineer" OR "developer"
   ```
   > This surfaces current employees by title. Collect: name, title, tenure, location.
   > **Escalation:** Aggregating >10 employee records constitutes PII collection → Tier 2 confirm.
3. **GitHub contributor analysis:**
   - Enumerate public repos: `https://api.github.com/orgs/<org>/repos`
   - List contributors: `https://api.github.com/repos/<org>/<repo>/contributors`
   - Contributor GitHub profiles often contain personal email, website, location
4. **Email pattern inference:**
   - Use Hunter.io public search: `https://hunter.io/domain-search?domain=<domain>`
   - Confirms format: `firstname.lastname@company.com` vs `f.lastname@` etc.
   - Cross-validate with emails found in GitHub commits

**Record at this step:**
- Official social account URLs and metrics
- Inferred email format
- Key personnel list (name + title + LinkedIn URL)
- GitHub org presence and public repo list
- Engineering stack hints from GitHub repos

---

## Phase 4 — ARCHIVE (Historical Web Presence)

**Agent:** ARCHIVE
**Gateway tier:** Tier 1
**Tools:** djinn-archive-fetch, Wayback Machine CDX API, CommonCrawl

### Steps

1. **Wayback CDX sweep on primary domain:**
   ```
   https://web.archive.org/cdx/search/cdx?url=<domain>/*&output=json&limit=50&fl=timestamp,original,statuscode&collapse=urlkey
   ```
2. **Key historical snapshots to pull:**
   - Earliest snapshot (founding era tech stack, original team)
   - Pre-acquisition snapshots (if org was acquired — what did it look like before?)
   - Old `/team` or `/about` pages (historical leadership)
   - Old `/careers` pages (historical tech stack from job postings)
   - Old press releases and blog posts
3. **Defunct subsidiary domains:** Run Wayback on any subsidiaries that no longer have active sites.
4. **Historical DNS:** SecurityTrails free tier shows historical A records — when did IP change? Reveals infrastructure migrations.

**Record at this step:**
- Founding date (first Wayback snapshot)
- Historical leadership (old team pages)
- Past tech stack vs. current (migration signals)
- Acquired or defunct subsidiaries
- Any removed content (legal notices, old product pages)

---

## Phase 5 — TREND (News Volume, Patent Filings, Hiring Signals)

**Agent:** TREND
**Gateway tier:** Tier 1
**Tools:** Google News, HackerNews Algolia, Reddit search, USPTO (patents), SEC EDGAR (public filings)

### Steps

1. **News volume and sentiment:**
   ```
   https://hn.algolia.com/api/v1/search?query=<Company Name>&tags=story
   site:news.ycombinator.com "<Company Name>"
   ```
2. **Patent filings (innovation signal):**
   ```
   https://patents.google.com/?assignee=<Company Name>
   https://www.uspto.gov/patents/search
   ```
3. **SEC EDGAR (for public companies):**
   ```
   https://www.sec.gov/cgi-bin/browse-edgar?company=<name>&action=getcompany
   ```
   > 10-K, 10-Q filings reveal financials, risk factors, key personnel, litigation.
4. **Hiring velocity (growth/contraction signal):**
   - Compare current job posting count vs. 90 days ago
   - Sudden spike = expansion or new product
   - Sudden drop = layoffs or pivot
5. **Reddit community presence:**
   ```
   https://www.reddit.com/search/?q=<Company Name>&sort=new
   ```

**Record at this step:**
- Recent news events (funding, acquisition, controversy, product launch)
- Patent filing activity (R&D focus areas)
- Hiring trend direction
- Public sentiment (HN/Reddit tone)

---

## Phase 6 — CORRELATOR (Org Graph & Subsidiary Mapping)

**Agent:** CORRELATOR
**Gateway tier:** Tier 2
**Tools:** Obsidian canvas, djinn-social-map (when available), manual link analysis

### Steps

1. **Build org graph:**
   - Parent company → subsidiaries → brands
   - Key personnel → their other board seats / affiliations (via LinkedIn, Crunchbase)
   - Investor → portfolio companies (are there strategic relationships with competitors?)
2. **Infrastructure graph:**
   - Primary domain → subdomains → IPs → ASN → hosting provider
   - Email domains → mail provider → security posture
3. **Resolve conflicts:**
   - LinkedIn says 500 employees; job postings suggest 50-person engineering team — flag discrepancy
   - Two different founding dates in different sources — note and assign confidence
4. **Pivot opportunities:**
   - Key personnel found → run PERSON-OP on high-value individuals
   - Subsidiary domain found → run DOMAIN-OP on it
   - Investor found → are they also invested in a competitor?

**Record at this step:**
- Org graph (text or canvas)
- Infrastructure map
- Confidence-scored key findings
- Recommended pivot ops

---

## Phase 7 — SCRIBE (Report & Vault Commit)

Same as PERSON-OP Phase 7. Use `reports/_template.md`. Org reports tend to be longer — consider splitting into: Executive Summary + Full Findings appendix.

**Additional org-specific report sections:**
- Org structure diagram
- Infrastructure summary table
- Key personnel table (name / title / LinkedIn / confidence)
- Tech stack table
- Risk/exposure notes (exposed subdomains, weak email security, etc.)

---

*ORG-OP Runbook — OSINT / Djinn system — maintained by SCRIBE*
