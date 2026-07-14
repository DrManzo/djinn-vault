# Feed Registry

All active passive intelligence feeds. Managed by TREND agent. Updated by operator.

**Last Updated:** 2026-06-19
**Feed Count:** 14 active, 0 archived

---

## How to Use This Registry

- **Automated feeds** (RSS/API): poll via cron (`djinn-trend-agent` was
  previously suggested here but is Djinn Media's own hashtag/content poller,
  not built for external-target feeds — audited and removed 2026-07-13,
  see `tools/README.md`)
- **Manual feeds**: operator checks on a schedule; no automation
- **Keyword feeds**: replace `<KEYWORD>` with your target before querying
- Add new feeds by appending a row — never delete, archive instead

---

## Active Feeds

| Feed Name | Type | URL / Query | Target / Topic | Added | Status |
|---|---|---|---|---|---|
| HackerNews Stories (keyword) | API | `https://hn.algolia.com/api/v1/search?query=<KEYWORD>&tags=story&hitsPerPage=20` | Any keyword — replace `<KEYWORD>` | 2026-06-19 | Active |
| HackerNews Comments (keyword) | API | `https://hn.algolia.com/api/v1/search?query=<KEYWORD>&tags=comment&hitsPerPage=20` | Comment-level mentions | 2026-06-19 | Active |
| Reddit r/OSINT | RSS | `https://www.reddit.com/r/osint/.rss` | OSINT community news and techniques | 2026-06-19 | Active |
| Reddit r/netsec | RSS | `https://www.reddit.com/r/netsec/.rss` | Network security research and disclosures | 2026-06-19 | Active |
| Reddit r/opsec | RSS | `https://www.reddit.com/r/opsec/.rss` | Operational security topics | 2026-06-19 | Active |
| Reddit r/cybersecurity | RSS | `https://www.reddit.com/r/cybersecurity/.rss` | Broad security news | 2026-06-19 | Active |
| Exploit-DB | RSS | `https://www.exploit-db.com/rss.xml` | New public exploits and PoCs | 2026-06-19 | Active |
| NVD CVE Feed (recent) | API | `https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=20&startIndex=0` | All new CVEs — paginated JSON | 2026-06-19 | Active |
| NVD CVE Feed (keyword) | API | `https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=<KEYWORD>&resultsPerPage=20` | CVEs matching specific product/vendor | 2026-06-19 | Active |
| Have I Been Pwned — Latest Breaches | API | `https://haveibeenpwned.com/api/v3/latestbreach` | Most recent breach added to HIBP | 2026-06-19 | Active |
| Have I Been Pwned — All Breaches | API | `https://haveibeenpwned.com/api/v3/breaches` | Full breach list (poll for new entries) | 2026-06-19 | Active |
| GitHub Trending (public page) | Manual | `https://github.com/trending?since=daily` | Trending repos — check daily or weekly | 2026-06-19 | Manual |
| GitHub Search (keyword) | API | `https://api.github.com/search/repositories?q=<KEYWORD>&sort=updated&order=desc` | Repos matching keyword — replace `<KEYWORD>` | 2026-06-19 | Active |
| OSINT Framework | Manual | `https://osintframework.com` | Tool/resource updates — no RSS, check monthly | 2026-06-19 | Manual |

---

## Operator-Configured Feeds (Manual Setup Required)

These feeds require operator action to configure. Instructions below.

### Google Alerts
**What it does:** Email or RSS alerts when Google indexes new pages matching a keyword.
**Setup:**
1. Go to https://www.google.com/alerts
2. Enter your target keyword (name, handle, domain, company name)
3. Set: Sources = All, Language = All (or target language), Region = Any, How often = As-it-happens or Once a day
4. Delivery = RSS feed (not email — RSS is pipeable)
5. Copy the RSS URL Google generates
6. Add to this registry as a new row with Type = RSS and your keyword in Target/Topic

**Example RSS URL format:** `https://www.google.com/alerts/feeds/<id>/<token>`

### Shodan Monitor
**What it does:** Alerts when Shodan detects changes to your monitored IP ranges or domains.
**Setup:**
1. Requires Shodan account (free tier supports 1 monitor)
2. Go to https://monitor.shodan.io
3. Add your IP range or domain
4. Enable email or webhook alerts
5. Log the monitor ID here for reference — no RSS feed, webhook only

**Note:** Shodan Monitor is for **assets you own or have authorization to monitor.** Do not add third-party IPs without explicit authorization.

### SecurityTrails Domain Alerts
**What it does:** Alerts on DNS record changes for monitored domains.
**Setup:**
1. Requires SecurityTrails account (free tier: 50 queries/month)
2. API base: `https://api.securitytrails.com/v1/`
3. Set up domain monitoring via their dashboard or API
4. Log API key in Djinn secrets store (not here)

---

## Keyword Feed Templates

Copy these query templates and swap `<KEYWORD>` for your target before running.

```bash
# HackerNews — recent stories mentioning target
curl "https://hn.algolia.com/api/v1/search?query=<KEYWORD>&tags=story&hitsPerPage=10" | jq '.hits[] | {title, url, created_at}'

# NVD — CVEs for a specific product
curl "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=<KEYWORD>&resultsPerPage=10" | jq '.vulnerabilities[] | {id: .cve.id, published: .cve.published, description: .cve.descriptions[0].value}'

# GitHub repos updated recently matching keyword
curl "https://api.github.com/search/repositories?q=<KEYWORD>&sort=updated&order=desc&per_page=10" | jq '.items[] | {name: .full_name, updated: .updated_at, url: .html_url}'

# HIBP — check if a domain appears in breaches
curl "https://haveibeenpwned.com/api/v3/breacheddomain/<DOMAIN>" -H "hibp-api-key: <KEY>"
# Note: domain breach check requires paid HIBP API key ($3.50/month)
# Latest breach (no key required):
curl "https://haveibeenpwned.com/api/v3/latestbreach"
```

---

## Archived Feeds

| Feed Name | Type | Reason Archived | Archived Date |
|---|---|---|---|
| — | — | — | — |

---

*Feed Registry — OSINT / Djinn system — maintained by TREND agent*
