# DORK BOOK — OSINT Search Reference

> Organized by target type. Copy, modify slot, run. All dorks are passive (Tier 0–1) unless noted.
> Replace placeholders: `TARGET`, `DOMAIN`, `USERNAME`, `EMAIL`, `ORG`

---

## CATEGORY 1: Person

```
# Full name presence across web
"FIRSTNAME LASTNAME" -site:linkedin.com
# Finds mentions outside LinkedIn — news, forums, directories, breach dumps

# Email pattern discovery
"FIRSTNAME" "LASTNAME" site:DOMAIN email OR contact
# Finds email format used by org (e.g., f.lastname@ vs firstname@)

# Social handle discovery from name
"FIRSTNAME LASTNAME" site:twitter.com OR site:x.com
# Direct Twitter/X profile hits

"FIRSTNAME LASTNAME" site:github.com
# Developer identity, repos, commit emails

"FIRSTNAME LASTNAME" site:linkedin.com/in
# LinkedIn profile — confirms employment, connections, skills

# Resume / CV leaks
"FIRSTNAME LASTNAME" filetype:pdf (resume OR cv OR curriculum)
# PDFs self-published or indexed unintentionally

# Forum and community presence
"FIRSTNAME LASTNAME" site:reddit.com OR site:hackernews.com OR site:stackoverflow.com
# Developer/technical identity across communities

# Email address dorks (if email is known)
"target@domain.com" -site:domain.com
# Finds where this email was used outside the home domain

"target@domain.com" site:pastebin.com OR site:paste.ee OR site:ghostbin.com
# Breach dump or paste leak check

# Phone number (if known)
"555-867-5309" OR "5558675309"
# Any public registration, directory listing, or forum post containing the number

# Photo credit / byline search
"Photo by FIRSTNAME LASTNAME" OR "by FIRSTNAME LASTNAME"
# Finds journalist bylines, photography credits, publication attributions
```

---

## CATEGORY 2: Organization

```
# Employee directory exposure
site:DOMAIN "@DOMAIN" email
# Finds pages exposing internal email addresses

# Job postings for tech stack inference
site:linkedin.com/jobs OR site:indeed.com ORG (engineer OR developer OR "software")
# Job descriptions reveal stack, tooling, cloud provider, internal systems

# Document leaks (presentations, specs, contracts)
site:DOMAIN filetype:pdf OR filetype:pptx OR filetype:docx
# Indexed internal documents accidentally left public

# Staff list exposure
site:DOMAIN "team" OR "staff" OR "our people" OR "directory"
# Org pages with employee names and roles

# Exposed configuration or credentials
site:DOMAIN filetype:env OR filetype:config OR filetype:yml
# Accidentally indexed config files (Tier 1 — passive read only, do not interact)

# Technology stack from job posts
ORG ("we use" OR "our stack" OR "built with") site:news.ycombinator.com OR site:reddit.com
# HN/Reddit posts where company discusses internal tech

# Subsidiary and brand mapping
"ORG" ("subsidiary" OR "acquired" OR "division" OR "brand")
# Finds press coverage of corporate structure

# Legal and regulatory filings
"ORG" site:sec.gov OR site:courtlistener.com OR site:pacer.gov
# SEC filings, court cases, public legal exposure

# Partner and vendor exposure
site:DOMAIN ("powered by" OR "in partnership with" OR "our partners")
# Third-party relationships that expand attack surface or org graph

# Glassdoor / employee sentiment
site:glassdoor.com ORG
# Internal culture, tech debt signals, leadership names from reviews
```

---

## CATEGORY 3: Domain / Infrastructure

```
# Subdomain exposure via Google
site:DOMAIN -www
# Finds all indexed subdomains except www — reveals staging, admin, API endpoints

# Admin and login panel exposure
site:DOMAIN (intitle:"admin" OR intitle:"login" OR inurl:"admin" OR inurl:"wp-admin")
# Exposes CMS admin panels, custom admin paths

# Exposed directory listings
site:DOMAIN intitle:"index of"
# Open directory listings — can expose file trees, logs, backups

# robots.txt recon
site:DOMAIN inurl:robots.txt
# Disallowed paths in robots.txt reveal sensitive areas (not blocked, just unlisted)

# Exposed backup files
site:DOMAIN filetype:bak OR filetype:backup OR filetype:old OR filetype:zip
# Backup files left in web root — Tier 1, do not download without operator confirm

# Error pages leaking stack info
site:DOMAIN ("stack trace" OR "syntax error" OR "undefined index" OR "fatal error")
# Verbose error pages exposing server-side code and framework

# API endpoint exposure
site:DOMAIN inurl:"/api/" OR inurl:"/v1/" OR inurl:"/v2/"
# Indexed API endpoints — often undocumented

# Git exposure
site:DOMAIN inurl:"/.git" OR inurl:"/git"
# Exposed .git directories (critical misconfiguration — Tier 2 to access, Tier 3 to pull)

# Cache and CDN leaks
cache:DOMAIN
# Google cached version — may show older content or different state
```

---

## CATEGORY 4: Username Enumeration

```
# Cross-platform presence
"USERNAME" site:twitter.com OR site:x.com OR site:instagram.com OR site:tiktok.com

"USERNAME" site:github.com OR site:gitlab.com OR site:bitbucket.org

"USERNAME" site:reddit.com/user

"USERNAME" site:keybase.io OR site:gravatar.com
# Cryptographic identity anchors — often link multiple platforms

"USERNAME" site:twitch.tv OR site:youtube.com OR site:kick.com
# Streaming/content platform presence

"USERNAME" site:medium.com OR site:substack.com OR site:dev.to
# Writing / publishing presence

"USERNAME" site:steamcommunity.com OR site:chess.com OR site:lichess.org
# Gaming / hobby community presence

# Username variation sweep
"USERNAME" OR "USERNAME_" OR "USERNAME." OR "x_USERNAME" OR "USERNAME_x"
# Common variation patterns across platforms
```

> **No automated tool for this yet.** `djinn-bore-core` was previously
> listed here for multi-platform username enumeration — it's actually a
> 3D-print STL tool, not an OSINT tool. Audited and removed 2026-07-13,
> see `tools/README.md`. Use [WhatsMyName](https://whatsmyname.app/) or
> the manual dorks above until a real tool exists.

---

## CATEGORY 5: Leak / Paste Dorks

```
# Pastebin and paste sites
"TARGET" site:pastebin.com
"TARGET" site:paste.ee
"TARGET" site:rentry.co

# GitHub code leaks
"TARGET" site:github.com (password OR secret OR apikey OR token OR credential)
# Source code leaks, hardcoded credentials containing target references

"DOMAIN" site:github.com (password OR secret OR key)
# Broader org/domain leak in public repos

# Document dumps
"TARGET" site:scribd.com OR site:slideshare.net OR site:issuu.com
# Uploaded documents mentioning target

# Breach mention check
"TARGET" "breach" OR "leak" OR "dump" OR "database"
# News coverage or community discussion of target being in a breach

# Darkweb indexers (public-facing only — Tier 1)
"TARGET" site:intelx.io OR site:dehashed.com
# Public index pages only — do not authenticate without Tier 2 approval
```

---

## DuckDuckGo Equivalents

DuckDuckGo supports most Google syntax. Key differences:

| Google | DuckDuckGo | Notes |
|---|---|---|
| `site:domain.com` | `site:domain.com` | Works identically |
| `filetype:pdf` | `filetype:pdf` | Works identically |
| `intitle:"text"` | `intitle:"text"` | Works identically |
| `inurl:"path"` | `inurl:"path"` | Works identically |
| `cache:url` | Not supported | Use Wayback Machine instead |
| `-site:` exclusion | `-site:` | Works identically |

DDG advantage: does not personalize results, so queries return less biased index. Use DDG as a secondary check on all major RECON dorks.

---

## Shodan Search Syntax (Infrastructure Targets)

```
# Org/ASN lookup
org:"ORG NAME"
as:ASNUMBER
# All Shodan-indexed hosts belonging to an org or ASN

# Domain and hostname
hostname:DOMAIN
hostname:.DOMAIN
# All hosts with matching hostname (wildcard on second)

# Technology/product fingerprint
product:"Apache httpd" org:"ORG"
server:"nginx" hostname:DOMAIN
# Identify specific server software on target infrastructure

# Open ports
port:22 org:"ORG"
port:3389 hostname:DOMAIN
# Exposed SSH or RDP — Tier 1 to view, Tier 3 to interact

# SSL cert subject
ssl.cert.subject.cn:DOMAIN
ssl.cert.subject.o:"ORG NAME"
# Find all IPs with certs issued to a domain or org — great for subdomain mapping

# Default credentials / exposed panels
http.title:"admin" org:"ORG"
http.title:"Dashboard" hostname:DOMAIN
# Exposed admin UIs — Tier 1 view, Tier 3+ to probe

# Banner grabbing
banner:"SSH" org:"ORG"
banner:"220" port:21 hostname:DOMAIN
# FTP/SSH banners often reveal OS and software versions

# Vuln search (Shodan CVE)
vuln:CVE-XXXX-XXXXX
# Hosts with known CVEs — Tier 1 to identify, Tier 3+ to validate
```

> **Note:** Shodan queries are passive reads (Tier 1). Shodan is showing you what it already scanned. You are not scanning the target. No tier escalation for lookups.

---

*DORK-BOOK — OSINT / Djinn system — maintained by RECON agent*
