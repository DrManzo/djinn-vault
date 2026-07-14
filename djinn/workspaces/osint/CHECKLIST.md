# OSINT OPERATION CHECKLISTS

> Three checklists. Run all three on every op. No skipping.

---

## PRE-OP CHECKLIST

*Complete before collecting a single data point.*

- [ ] Target file created from `targets/_template.md`
- [ ] Target slug is unique and follows naming convention (`YYYY-MM-DD_<slug>.md`)
- [ ] Operation purpose documented in target file (why are we collecting this?)
- [ ] Target type identified: Person / Organization / Domain / Mixed
- [ ] Operator name recorded in target file
- [ ] **Gateway tier set and written in target file** — do not proceed without this
- [ ] Appropriate runbook identified and open: PERSON-OP / ORG-OP / DOMAIN-OP
- [ ] Agents assigned (minimum: RECON + SCRIBE)
- [ ] Report file created from `reports/_template.md`
- [ ] DORK-BOOK.md open to correct category
- [ ] No authenticated sessions open in browser (passive-only ops stay logged out)
- [ ] Confirm: does this op require Tier 3+ approval? If yes — stop and get sign-off before proceeding

---

## DURING-OP CHECKPOINTS

*Run these as you move through each agent phase.*

### RECON Phase
- [ ] Minimum 3 dorks run from DORK-BOOK for target type
- [ ] All result URLs logged in target file (not just notes — actual URLs)
- [ ] No login walls crossed (Tier 0–1 boundary)
- [ ] New seed data identified and added to target file before moving on

### SOCIAL Phase
- [ ] Platforms enumerated via manual check (no OSINT enumeration tool exists yet — see `tools/README.md`)
- [ ] Handle variations logged (spaces, underscores, dots, numbers)
- [ ] All confirmed accounts tagged `[CONFIRMED]` in target file
- [ ] All unconfirmed accounts tagged `[CANDIDATE]` — do not treat as confirmed
- [ ] No account interactions (no follows, no DMs, no reactions) — Tier 2+ boundary

### NETPROBE Phase
- [ ] WHOIS/RDAP pulled and logged
- [ ] DNS records pulled: A, MX, TXT, NS, CNAME, SPF, DMARC, DKIM
- [ ] SSL cert history checked via crt.sh
- [ ] ASN and hosting provider identified
- [ ] Active scanning check: is anything in this phase sending packets to live infrastructure?
  - [ ] If yes — escalate to Tier 3 before continuing

### ARCHIVE Phase
- [ ] Wayback Machine CDX API queried for all known URLs
- [ ] Oldest and most recent snapshots logged
- [ ] Deleted content noted separately with `[ARCHIVED-ONLY]` tag
- [ ] No assumptions made from archived content without cross-validation

### TREND Phase
- [ ] Keyword searches run across configured feeds
- [ ] Date ranges noted for all results
- [ ] Signals tagged by type: news / hiring / legal / technical / social

### CORRELATOR Phase
- [ ] Correlator only runs after RECON + at least one other agent completes
- [ ] All entity links sourced — no inferred links without at least 2 independent sources
- [ ] Confidence score assigned to each link (High / Medium / Low)
- [ ] Contradictions flagged, not resolved by assumption

### SCRIBE (Ongoing)
- [ ] Report file updated after each agent phase
- [ ] No raw PII in report that isn't operationally necessary
- [ ] Source URLs cited for every claim in report

---

## POST-OP CHECKLIST

*Complete before committing anything to the vault.*

- [ ] All findings in report file, report status set to `COMPLETE` or `PARTIAL`
- [ ] Target file updated with final status and date
- [ ] **PII scrub check**: review all files for unnecessary PII (addresses, phone numbers, full DOB, SSN fragments) — remove anything not required for the stated op purpose
- [ ] **Gateway tier verification**: confirm no data was collected above the approved tier. If tier was exceeded, document why and get retroactive operator sign-off
- [ ] All source URLs still accessible? If any are 404, note as `[URL-DEAD]` with retrieval date
- [ ] Confidence scores assigned to all major findings
- [ ] Contradictions and gaps documented — do not present incomplete data as complete
- [ ] Report reviewed for accuracy — no typos in entity names, no transposed dates
- [ ] **DEVLOG entry appended** to `DEVLOG.md` with op summary, agents used, files changed
- [ ] Commit message written in format: `osint(<slug>): <one-line summary>`
- [ ] `git add djinn/workspaces/osint/` — confirm only OSINT files staged
- [ ] Push to remote: `git push`
- [ ] Confirm push succeeded before closing op

---

*CHECKLIST — OSINT / Djinn system — maintained by SCRIBE*
