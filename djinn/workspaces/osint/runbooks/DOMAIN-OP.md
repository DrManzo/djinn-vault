# DOMAIN-OP — Domain/Infrastructure OSINT Runbook

> **Target type:** Domain name, IP address, or network infrastructure
> **Owned by:** NETPROBE (primary) → ARCHIVE → CORRELATOR → SCRIBE
> **Gateway entry tier:** Tier 1 (passive reads). Tier 3 for any active scanning.

---

## Phase 0 — Seed Data Collection

**Minimum viable seed (pick at least one):**
- Domain name (e.g., `example.com`)
- IP address or CIDR range
- ASN number
- SSL certificate SHA or fingerprint
- Hosting provider name

**Establish at seed stage:**
- Op objective: threat research? asset discovery? due diligence? attribution?
- Is active scanning authorized? (Default: NO — Tier 3 required)
- Known related domains / IPs to include in scope

---

## Phase 1 — WHOIS / RDAP

**Agent:** NETPROBE
**Gateway tier:** Tier 1
**Tools:** whois (CLI), RDAP, Whoxy, DomainTools (free tier)

### Steps

1. **Standard WHOIS:**
   ```bash
   whois <domain>
   ```
   Key fields: Registrar, Created, Updated, Expires, Name Servers, Registrant (often redacted post-GDPR)

2. **RDAP (structured, machine-readable WHOIS replacement):**
   ```bash
   curl https://rdap.org/domain/<domain>
   curl https://rdap.verisign.com/com/v1/domain/<domain>
   ```

3. **Historical WHOIS (registrant changes over time):**
   ```
   https://www.whoxy.com/<domain>
   https://whoishistory.com/<domain>
   ```
   > Historical WHOIS often reveals registrant email before privacy protection was added.

4. **Reverse WHOIS (find all domains registered by same email/org):**
   ```
   https://www.whoxy.com/reverse-whois/?email=<email>
   https://viewdns.info/reversewhois/?q=<email>
   ```

**Record at this step:**
- Registrar name and ID
- Registration date (domain age — old domains are less likely to be throwaway infra)
- Expiry date (is it about to expire? Signals abandonment or domain squatting risk)
- Registrant email (if visible — if not, note privacy proxy used)
- Name servers (reveals DNS host — Cloudflare, Route53, self-hosted, etc.)
- Any registrant identity recovered from historical WHOIS

---

## Phase 2 — DNS Full Record Set

**Agent:** NETPROBE
**Gateway tier:** Tier 1
**Tools:** dig, dnsx, SecurityTrails, MXToolbox

### Steps

1. **Full record sweep:**
   ```bash
   dig <domain> A        # IPv4 address(es)
   dig <domain> AAAA     # IPv6
   dig <domain> MX       # Mail servers
   dig <domain> NS       # Name servers
   dig <domain> TXT      # SPF, DMARC, verification tokens, Google/Microsoft ownership proofs
   dig <domain> CNAME    # Aliases
   dig <domain> SOA      # Zone authority — reveals DNS admin email
   dig <domain> CAA      # Which CAs are allowed to issue certs for this domain
   ```

2. **SPF analysis (email spoofing resistance):**
   ```bash
   dig TXT <domain> | grep spf
   ```
   - `~all` = soft fail (weak) — domain is spoofable
   - `-all` = hard fail (strong)
   - No SPF = fully spoofable

3. **DMARC analysis:**
   ```bash
   dig TXT _dmarc.<domain>
   ```
   - `p=none` = monitoring only (no enforcement)
   - `p=quarantine` or `p=reject` = enforced
   - No DMARC = high phishing risk

4. **DKIM selector discovery:**
   Common selectors to try:
   ```bash
   dig TXT google._domainkey.<domain>   # Google Workspace
   dig TXT selector1._domainkey.<domain> # Microsoft 365
   dig TXT default._domainkey.<domain>
   dig TXT mail._domainkey.<domain>
   ```

5. **Historical DNS (IP changes over time):**
   ```
   https://securitytrails.com/domain/<domain>/history/a
   ```

**Record at this step:**
- All IP addresses (current and historical)
- Mail provider (from MX records)
- Email security posture (SPF/DMARC/DKIM)
- DNS host
- Any TXT tokens that reveal third-party service usage (Stripe, Mailchimp, Salesforce ownership tokens)
- SOA admin email (often a real address)

---

## Phase 3 — Reverse IP & ASN

**Agent:** NETPROBE
**Gateway tier:** Tier 1
**Tools:** ViewDNS, BGP.he.net, ARIN/RIPE/APNIC RDAP, Shodan

### Steps

1. **Reverse IP — co-hosted domains:**
   ```
   https://viewdns.info/reverseip/?host=<ip>
   https://api.shodan.io/dns/reverse?ips=<ip>&key=<apikey>
   ```
   > Many domains on same IP = shared hosting (target has less control of infra).
   > Few or one domain = dedicated/cloud infra.

2. **IP geolocation (approximate — not legally precise):**
   ```
   https://ipinfo.io/<ip>
   ```

3. **ASN lookup:**
   ```bash
   whois -h whois.radb.net <ip>  # Returns ASN
   # Then:
   curl https://bgp.he.net/AS<asn>#_asinfo
   ```
   > ASN reveals the owning organization of the IP block. AWS = AS16509, Cloudflare = AS13335, etc.

4. **Full IP range for ASN (what else does this org own?):**
   ```
   https://bgp.he.net/AS<asn>#_prefixes
   ```

**Record at this step:**
- Hosting provider and ASN
- IP block size (large block = major org; /32 = single IP, likely cloud NAT)
- Co-hosted domains (signals shared hosting vs. dedicated)
- Physical datacenter region (approximate)

---

## Phase 4 — SSL Certificate History

**Agent:** NETPROBE
**Gateway tier:** Tier 1
**Tools:** crt.sh, Censys

### Steps

1. **Certificate transparency log search:**
   ```
   https://crt.sh/?q=<domain>&output=json
   https://crt.sh/?q=%.<domain>&output=json   # All subdomains
   ```
   > Every SSL cert issued is logged publicly. This reveals:
   > - All subdomains (including internal/staging ones accidentally cert'd)
   > - Historical cert issuance (when did HTTPS begin?)
   > - Which CA is used (Let's Encrypt = low-cost/automated; DigiCert = enterprise)
   > - SANs (Subject Alternative Names) — other domains on same cert

2. **Censys cert search:**
   ```
   https://search.censys.io/search?resource=certificates&q=parsed.names%3A<domain>
   ```

3. **Extract all subdomains from crt.sh:**
   ```bash
   curl -s "https://crt.sh/?q=%25.<domain>&output=json" | jq -r '.[].name_value' | sort -u
   ```

**Record at this step:**
- Full subdomain list (passive — no brute force)
- First cert issuance date
- CA used
- Any SANs revealing related domains
- Internal/staging subdomains accidentally exposed

---

## Phase 5 — Tech Stack Fingerprinting

**Agent:** NETPROBE
**Gateway tier:** Tier 1 (passive fingerprinting only)
**Tools:** BuiltWith, Wappalyzer (browser extension), Shodan, WhatRuns

### Steps

1. **BuiltWith full tech profile:**
   ```
   https://builtwith.com/<domain>
   ```
   Reveals: CMS, analytics, CDN, hosting, frameworks, ad tech, email platform, payment processor.

2. **Shodan banner data (passive read of existing scan data — NOT active scanning):**
   ```
   hostname:<domain>
   ssl:<domain>
   ```
   Shodan scans the internet continuously — reading their data is passive Tier 1. Running your own scan is Tier 3.

3. **HTTP headers (passive — check archive snapshots, not live requests unless authorized):**
   Key headers to look for in archived responses:
   - `Server:` — web server and version
   - `X-Powered-By:` — framework
   - `X-Generator:` — CMS
   - `Set-Cookie:` — session tech, CDN cookies

**Record at this step:**
- Full tech stack
- CDN presence (and whether it masks real IP)
- Known CVEs for detected software versions (note — do NOT test, just research)
- Email platform (relevant for social engineering resistance assessment)

---

## Phase 6 — Shodan Banner Data

**Agent:** NETPROBE
**Gateway tier:** Tier 1 (reading Shodan's existing data). Tier 3 for live scanning.
**Tools:** Shodan web UI or API

### Steps

1. **Search by hostname:**
   ```
   hostname:<domain>
   ```
2. **Search by org name:**
   ```
   org:"<Organization Name>"
   ```
3. **Search by IP or CIDR:**
   ```
   net:<ip>/<cidr>
   ```
4. **Search for specific exposed services:**
   ```
   hostname:<domain> port:22    # SSH
   hostname:<domain> port:3389  # RDP
   hostname:<domain> port:27017 # MongoDB
   hostname:<domain> port:9200  # Elasticsearch
   ```
5. **SSL cert search:**
   ```
   ssl.cert.subject.cn:<domain>
   ```

**Record at this step:**
- Open ports visible to internet
- Service banners (version strings)
- Any exposed databases, admin panels, or development services
- Last scan timestamp (Shodan data can be months old — note this)

> **CRITICAL:** Recording what Shodan already knows is Tier 1 passive. Connecting to any discovered service — even just a banner grab — is active and requires Tier 3 operator confirm.

---

## Phase 7 — ARCHIVE (Historical Pages on Domain)

**Agent:** ARCHIVE
**Gateway tier:** Tier 1
**Tools:** djinn-archive-fetch, Wayback CDX API

### Steps

1. **CDX full crawl of domain:**
   ```
   https://web.archive.org/cdx/search/cdx?url=<domain>/*&output=json&fl=timestamp,original,statuscode&collapse=urlkey&limit=100
   ```
2. **Pull snapshots for:**
   - `/admin`, `/wp-admin`, `/login` — were admin paths ever exposed?
   - `/robots.txt` — historical disallow rules reveal hidden paths
   - `/sitemap.xml` — historical page inventory
   - `/.env`, `/config`, `/backup` — any accidental exposure now deleted?
3. **Check for old software versions in archived pages** — old version strings in page source may reveal CVEs.

**Record at this step:**
- Historical paths of interest
- Any previously exposed sensitive paths (now deleted)
- Tech stack version history
- Domain age and evolution

---

## Phase 8 — CORRELATOR (Link to Org/Person Entities)

**Agent:** CORRELATOR
**Gateway tier:** Tier 1–2 depending on what's linked

### Steps

1. **Map domain to organization:** Does WHOIS registrant, cert SAN, or Shodan org field link this domain to a known org? → Cross-reference with any existing ORG-OP.
2. **Map domain to person:** Does historical WHOIS registrant email link to a known individual? → Cross-reference with any existing PERSON-OP or create new one.
3. **Map infrastructure relationships:** Same ASN as other known domains? Same SSL cert? Same hosting account (reverse IP)? Build the infrastructure cluster.
4. **Flag exposure risk:** Exposed services + tech stack CVEs + weak email security = risk summary for report.

---

## Phase 9 — SCRIBE (Report & Vault Commit)

Use `reports/_template.md`. Domain reports should include:
- Infrastructure summary table: domain → IPs → ASN → hosting provider → CDN
- DNS record table: type / value / notes
- Subdomain inventory (from crt.sh)
- Tech stack table
- Exposure risk summary
- Attribution links (org / person connections)

---

## Gateway Escalation Reference

| Action | Tier | Requires |
|---|---|---|
| WHOIS, RDAP, DNS queries | 1 | Auto-approved |
| Reading Shodan existing data | 1 | Auto-approved |
| Cert transparency queries | 1 | Auto-approved |
| BuiltWith / Wappalyzer fingerprinting | 1 | Auto-approved |
| Connecting to any live service (even curl) | 3 | Operator confirm + log |
| Active port scanning | 3 | Operator confirm + log |
| Vulnerability testing | 4 | Blocked — out of scope |

---

*DOMAIN-OP Runbook — OSINT / Djinn system — maintained by SCRIBE*
