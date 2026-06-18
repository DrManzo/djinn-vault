# OSINT RESOURCES — Master Reference

> Every useful public OSINT source. For each: name, URL, purpose, free tier limits, owning agent.

---

## IDENTITY & SOCIAL

| Resource | URL | Purpose | Free Tier | Agent |
|---|---|---|---|---|
| **Have I Been Pwned** | https://haveibeenpwned.com | Email/phone breach lookup; check if identity appears in known breach datasets | Unlimited individual lookups; API requires key | SOCIAL |
| **Dehashed (public)** | https://dehashed.com | Breach database search by email, username, IP, name, address | Limited results without account; search is public | SOCIAL |
| **Hunter.io** | https://hunter.io | Email pattern discovery for organizations; validates email format (e.g., first.last@domain.com) | 25 searches/month free | RECON |
| **Maltego Community** | https://www.maltego.com/maltego-community/ | Visual link analysis and entity mapping; integrates many OSINT sources via transforms | Free community edition; limited transforms and result depth | CORRELATOR |
| **Intelligence X (intelx.io)** | https://intelx.io | Historical data, leaks, dark web indexing, document search | Limited free searches; full access paid | SOCIAL / RECON |
| **SpiderFoot (self-hosted)** | https://github.com/smicallef/spiderfoot | Automated OSINT collection across 200+ modules; self-hosted, no API limits | Fully free self-hosted; SpiderFoot HX is paid cloud | All agents |
| **Carrot2** | https://search.carrot2.org | Clustering search engine; groups results by topic; good for disambiguating common names | Free | RECON |

---

## DOMAIN & NETWORK

| Resource | URL | Purpose | Free Tier | Agent |
|---|---|---|---|---|
| **Shodan** | https://www.shodan.io | Internet-wide port scanning data; banner grabs, SSL certs, open services, CVE hits | 2 pages of results free; API key required for bulk; monitor is paid | NETPROBE |
| **Censys** | https://search.censys.io | Similar to Shodan; excellent for SSL cert search and host discovery | Free search with account; API rate-limited | NETPROBE |
| **crt.sh** | https://crt.sh | Certificate Transparency log search; reveals all SSL certs issued for a domain including subdomains | Completely free; no account | NETPROBE |
| **SecurityTrails** | https://securitytrails.com | Historical DNS records, subdomain enumeration, IP neighbor lookup | 50 API queries/month free with account | NETPROBE |
| **ViewDNS** | https://viewdns.info | Reverse IP lookup, DNS history, port scan, WHOIS, IP location; multi-tool | Free; some tools rate-limited | NETPROBE |
| **Whoxy** | https://www.whoxy.com | Historical WHOIS data; reverse WHOIS by email, name, or company | API credits required; very cheap; no meaningful free tier | NETPROBE |
| **RDAP** | https://lookup.icann.org / https://rdap.org | Modern WHOIS replacement; structured JSON output; registrant data | Completely free | NETPROBE |
| **Robtex** | https://www.robtex.com | DNS lookup, reverse DNS, AS/BGP data, shared hosting detection | Free | NETPROBE |
| **BGP.he.net** | https://bgp.he.net | ASN lookup, BGP routing data, IP block ownership, peering info | Completely free | NETPROBE |
| **BuiltWith** | https://builtwith.com | Technology stack fingerprinting from HTTP headers, scripts, cookies | Free individual lookups; bulk/API is paid | NETPROBE / RECON |
| **Spyse / Netlas** | https://netlas.io | Attack surface mapping, subdomain search, IP lookup, certificate data (Spyse rebranded to Netlas) | Limited free searches with account | NETPROBE |
| **VirusTotal** | https://www.virustotal.com | Domain/IP/hash reputation; passive DNS; file scanning; relationship graph | Free for manual lookups; API rate-limited | NETPROBE / TREND |
| **Wappalyzer** | https://www.wappalyzer.com | Browser extension + API for tech stack detection | Free extension; API is paid | NETPROBE |

---

## ARCHIVES & HISTORY

| Resource | URL | Purpose | Free Tier | Agent |
|---|---|---|---|---|
| **Wayback Machine CDX API** | https://web.archive.org/cdx/search/cdx | Programmatic access to Wayback Machine index; query all snapshots of a URL with dates, status codes, MIME types | Completely free; no rate limit documented but be courteous | ARCHIVE |
| **Wayback Machine (UI)** | https://web.archive.org | Human-readable historical snapshots of any indexed URL | Completely free | ARCHIVE |
| **CachedView** | https://cachedview.nl | Multi-source cached page viewer (Google cache, Wayback, Archive.is) | Free | ARCHIVE |
| **Archive.today** | https://archive.ph | On-demand page archiving; retrieve previous archives; useful for pages blocking Wayback | Free; some CAPTCHAs | ARCHIVE |
| **TimeTravel** | https://timetravel.mementoweb.org | Federated Memento API across multiple web archives | Free | ARCHIVE |

---

## THREAT INTEL

| Resource | URL | Purpose | Free Tier | Agent |
|---|---|---|---|---|
| **GreyNoise** | https://www.greynoise.io | Distinguishes mass internet scanners from targeted activity; IP context | Free community tier with account; limited API | NETPROBE / TREND |
| **VirusTotal** | https://www.virustotal.com | Passive DNS, domain/IP/hash reputation, community comments | Free manual; API rate-limited (4 lookups/min public) | NETPROBE |
| **Shodan CVE Search** | https://www.shodan.io/search?query=vuln:CVE | Find hosts with known CVEs exposed to internet | Same as Shodan free tier | NETPROBE |
| **Exploit-DB** | https://www.exploit-db.com | Public exploit database; Google Hacking Database (GHDB) for dork reference | Completely free | RECON |
| **NVD (CVE Feed)** | https://services.nvd.nist.gov/rest/json/cves/2.0 | NIST National Vulnerability Database; CVE details JSON API | Completely free | TREND |
| **AlienVault OTX** | https://otx.alienvault.com | Threat intelligence pulses; IP/domain/hash indicators of compromise | Free with account | TREND / NETPROBE |

---

## PEOPLE & RECORDS

| Resource | URL | Purpose | Free Tier | Agent |
|---|---|---|---|---|
| **OSINT Framework** | https://osintframework.com | Categorized directory of OSINT tools and resources; visual tree navigation | Completely free; open source | All agents |
| **Spokeo** | https://www.spokeo.com | US people search: addresses, relatives, phone, email | Very limited free; mostly paid | SOCIAL / RECON |
| **FastPeopleSearch** | https://www.fastpeoplesearch.com | US public records aggregator; name, address, phone | Free (ad-supported) | SOCIAL |
| **OpenCorporates** | https://opencorporates.com | Global corporate registry data; subsidiaries, officers, addresses | Free search; bulk API is paid | RECON / CORRELATOR |
| **SEC EDGAR** | https://www.sec.gov/cgi-bin/browse-edgar | US public company filings: 10-K, 10-Q, 8-K, insider transactions | Completely free | TREND / FININT |
| **PACER** | https://pacer.gov | US federal court records | Free to register; $0.10/page to access documents | RECON |
| **CourtListener** | https://www.courtlistener.com | Free federal court record search; some PACER data mirrored | Free | RECON |

---

## VISUAL & IMAGE

| Resource | URL | Purpose | Free Tier | Agent |
|---|---|---|---|---|
| **TinEye** | https://tineye.com | Reverse image search; find where an image appears on the web; date of first appearance | 150 searches/month free | SOCIAL / IMINT |
| **PimEyes (public tier)** | https://pimeyes.com | Face recognition reverse search; finds public photos of a face | Very limited free; paid for meaningful results. **Tier 2 — operator confirm required.** | SOCIAL / IMINT |
| **Google Lens** | https://lens.google.com | Reverse image search with object recognition | Free | SOCIAL / IMINT |
| **Yandex Images** | https://yandex.com/images | Often finds faces and images missed by Google/TinEye; strong for Eastern European and Russian sources | Free | SOCIAL / IMINT |
| **SunCalc** | https://www.suncalc.org | Sun position calculator for photo geolocation (shadow angle analysis) | Free | IMINT |
| **GeoGuessr / Overpass Turbo** | https://overpass-turbo.eu | OSM data query; find specific infrastructure types by location for geolocation confirmation | Free | IMINT |

---

## AGGREGATORS

| Resource | URL | Purpose | Free Tier | Agent |
|---|---|---|---|---|
| **SpiderFoot (self-hosted)** | https://github.com/smicallef/spiderfoot | 200+ module OSINT automation; runs all collection disciplines from one tool | Fully free self-hosted | All agents |
| **Maltego Community** | https://www.maltego.com/maltego-community/ | Visual entity-relationship mapping; OSINT transform library | Free community; limited transforms | CORRELATOR |
| **OSINT Framework** | https://osintframework.com | Master directory of OSINT tools organized by target type | Free | All agents |
| **intelx.io** | https://intelx.io | Historical data aggregator: leaked databases, dark web, public web, documents | Limited free; paid for depth | RECON / SOCIAL |
| **Lampyre** | https://lampyre.io | Data analysis and OSINT aggregation with visualization | Paid; limited trial | CORRELATOR |

---

*RESOURCES — OSINT / Djinn system — maintained by SCRIBE. Verify URLs before use — services change.*
