# PERSON-OP — Person-Targeted OSINT Runbook

> **Target type:** Individual (real name, handle, email, or partial identity)
> **Owned by:** RECON → SOCIAL → VISUAL → NETPROBE → ARCHIVE → TREND → CORRELATOR → SCRIBE
> **Gateway entry tier:** Tier 1 (passive). Escalate to Tier 2 if PII aggregation begins. Tier 3 for any active enumeration.

---

## Phase 0 — Seed Data Collection

Before any agent runs, collect what you already know. Record in `targets/<slug>.md`.

**Minimum viable seed (pick at least one):**
- Full legal name
- Known username / handle
- Email address or pattern
- Phone number
- City / employer / institution
- Profile URL (any platform)

**Record at this step:**
- Seed data source (how did you get it?)
- Confidence level (HIGH / MEDIUM / LOW)
- Date of last known accuracy
- Any aliases or name variants

> If you have zero seed data, go to `QUICKSTART.md → Cold Start` before proceeding.

---

## Phase 1 — RECON (Passive Web Footprint)

**Agent:** RECON
**Gateway tier:** Tier 1
**Tools:** DuckDuckGo, Google dorks (see `DORK-BOOK.md → Person`), Bing, Yandex

### Steps

1. Run name dorks across all four engines — results differ significantly.
   ```
   "Firstname Lastname" site:linkedin.com
   "Firstname Lastname" filetype:pdf
   "Firstname Lastname" inurl:about OR inurl:profile
   ```
2. Run email dorks if email is known:
   ```
   "user@domain.com"
   "user@domain.com" -site:domain.com
   ```
3. Run employer/institution + name cross-query:
   ```
   "Firstname Lastname" "Company Name"
   "Firstname Lastname" site:company.com
   ```
4. Check Google cache for deleted pages: `cache:profileurl`
5. Run image reverse search if photo available → hand off to VISUAL agent.

**Record at this step:**
- All URLs found (even if not immediately useful)
- Platform presence confirmed (LinkedIn, Twitter/X, GitHub, etc.)
- Any additional aliases or email patterns surfaced
- Employer, location, or affiliation data found

---

## Phase 2 — SOCIAL (Handle Enumeration & Profile Mapping)

**Agent:** SOCIAL
**Gateway tier:** Tier 1 → escalate to Tier 2 if cross-platform aggregation reveals PII not already in seed
**Tools:** djinn-bore-core, Sherlock (local), WhatsMyName, manual platform checks

### Steps

1. Run `djinn-bore-core` on all known handles:
   ```
   djinn-bore-core --username <handle> --output targets/<slug>/social-map.json
   ```
2. For each confirmed platform, record:
   - Profile URL
   - Display name (may differ from handle)
   - Bio / description text
   - Location (stated)
   - Join date
   - Follower/following count (signals influence level)
   - Pinned content
   - External links in bio
3. Check for cross-platform username reuse — same handle on GitHub, Reddit, Steam, etc. is high-confidence same person.
4. Extract any email addresses visible in public bios or repos.
5. Extract any personal domains linked in bios → hand off to NETPROBE.

**Escalation trigger:** If aggregated social data produces home address, phone, or employer not already in seed — pause, verify Gateway tier with operator.

**Record at this step:**
- Full platform list with URLs
- Social graph sketch (who do they interact with most?)
- Any domains or emails surfaced
- Confidence score per platform (confirmed identity vs. probable same person)

---

## Phase 3 — NETPROBE (Personal Domain & Infrastructure)

**Agent:** NETPROBE
**Gateway tier:** Tier 1 (passive WHOIS/DNS). Tier 3 for any active port scan.
**Tools:** djinn-net-probe, RDAP, crt.sh, ViewDNS, SecurityTrails
**Run only if:** A personal domain, portfolio site, or self-hosted service was found in Phase 1 or 2.

### Steps

1. Run WHOIS/RDAP on any personal domains found:
   ```
   whois <domain>
   curl https://rdap.org/domain/<domain>
   ```
2. Check `crt.sh` for SSL cert history — often reveals additional subdomains and registration email:
   ```
   https://crt.sh/?q=<domain>
   ```
3. Run DNS full record set: A, MX, TXT, NS, CNAME, SPF, DMARC.
   ```
   dig <domain> ANY
   ```
4. Reverse IP lookup — who else is hosted on same IP? (signals shared hosting vs. dedicated)
5. Check BuiltWith / Wappalyzer for tech stack — can reveal CMS, hosting provider, email service.
6. Check Shodan for any exposed services on the IP (passive read only — Tier 1).

**Record at this step:**
- Registrar, registration date, expiry
- Registrant email (if not redacted — GDPR/privacy may hide this)
- Hosting provider and ASN
- Tech stack
- Any additional domains on same IP or same registrant email

---

## Phase 4 — ARCHIVE (Historical Profile Recovery)

**Agent:** ARCHIVE
**Gateway tier:** Tier 1
**Tools:** djinn-archive-fetch, Wayback Machine CDX API, CachedView, Google Cache

### Steps

1. Run Wayback CDX API on all known profile URLs and personal domains:
   ```
   https://web.archive.org/cdx/search/cdx?url=<profileurl>&output=json&limit=20&fl=timestamp,original,statuscode
   ```
2. Check earliest snapshot — what did the profile look like when first created?
3. Check snapshots around major life events (if known) — job changes, relocations, etc.
4. Look for deleted content: bios that have been scrubbed, old usernames, old email addresses.
5. Check CommonCrawl index for additional cached copies:
   ```
   https://index.commoncrawl.org/CC-MAIN-<year>-<week>-index?url=<domain>&output=json
   ```
6. Google Cache: `cache:<url>` for recently changed pages.

**Record at this step:**
- Earliest known web presence (date)
- Any previously used names, handles, or emails found in old snapshots
- Deleted content recovered
- Historical location or employer data

---

## Phase 5 — TREND (Name/Handle Keyword Monitoring)

**Agent:** TREND
**Gateway tier:** Tier 1
**Tools:** Google Alerts (manual), HackerNews Algolia API, Reddit search, GitHub search

### Steps

1. Search HackerNews for name/handle mentions:
   ```
   https://hn.algolia.com/api/v1/search?query=<name>&tags=comment,story
   ```
2. Search Reddit for username/name mentions across all subs.
3. Search GitHub for email or name in commits:
   ```
   https://github.com/search?q=<email>&type=commits
   ```
4. Check if name/handle appears in any public breach data (HIBP public breach list — no account lookup, just breach metadata).
5. If ongoing monitoring needed: add to `feeds/feed-registry.md` as a keyword-based Google Alert.

**Record at this step:**
- Any recent public mentions (news, forums, repos)
- Any breach associations (breach name only — not credential data)
- Volume trend (has this person's online presence grown or shrunk recently?)

---

## Phase 6 — CORRELATOR (Synthesis & Entity Resolution)

**Agent:** CORRELATOR
**Gateway tier:** Tier 2 (aggregated profile = PII)
**Tools:** Obsidian canvas (manual), link analysis notes, djinn-social-map (when available)

### Steps

1. Aggregate all findings from Phases 1–5 into `targets/<slug>.md`.
2. Build entity map: what identifiers are **confirmed** (same person, high confidence) vs. **probable** (likely same person) vs. **possible** (unverified)?
3. Resolve any conflicts: if two sources give different employers or locations, note discrepancy and assign confidence score.
4. Identify pivots: what new seed data emerged that could open new lines of inquiry?
5. Determine completeness:
   - **Complete profile:** Full name + current location + employer + 3+ platform presence + contact method confirmed
   - **Sufficient for purpose:** Depends on op objective — record explicitly what the op was trying to establish and whether it was established
6. Flag any Tier 3 escalation opportunities (active recon that *could* fill gaps) — do NOT run without operator confirm.

**Record at this step:**
- Confidence-scored entity map
- Open questions / unresolved conflicts
- Pivot opportunities
- Completeness assessment

---

## Phase 7 — SCRIBE (Report & Vault Commit)

**Agent:** SCRIBE
**Gateway tier:** Tier 2 (report contains aggregated PII)
**Tools:** Obsidian, git

### Steps

1. Copy `reports/_template.md` → `reports/YYYY-MM-DD_<slug>.md`
2. Fill all sections: objective, seed data, findings per phase, entity map, confidence scores, open questions, recommendations.
3. PII scrub check: does the report contain data that exceeds the op's stated purpose? Remove or redact if so.
4. Commit report and updated target file:
   ```
   git add djinn/workspaces/osint/ && git commit -m "osint(person): complete op — <slug>"
   ```
5. Append DEVLOG entry.
6. If case is closed: move `targets/<slug>.md` to `targets/archived/<slug>.md`.

---

## Gateway Escalation Reference

| Action | Tier | Requires |
|---|---|---|
| Passive web search, public profiles | 1 | Auto-approved |
| Cross-platform aggregation producing PII | 2 | Operator confirm |
| Active account probing, direct contact | 3 | Operator confirm + log |
| Credential lookup, breach data with passwords | 4 | Blocked — do not run |

---

*PERSON-OP Runbook — OSINT / Djinn system — maintained by SCRIBE*
