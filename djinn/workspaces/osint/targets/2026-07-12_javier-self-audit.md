# Target: javier-self-audit

**Case Code:** OSINT-2026-07-12-javier-self-audit
**Opened:** 2026-07-12
**Status:** Closed
**Operator:** Javier (DrManzo)
**Gateway Tier:** [x] Tier 1 — Passive  [x] Tier 2 — Social

---

## Target Profile

| Field | Value |
|---|---|
| Name / Entity | Javier (operator, self-audit) |
| Type | Person (self) |
| Known Aliases | DrManzo |
| Known Domains | github.com/DrManzo/djinn-vault (public) |
| Known Social Handles | GitHub: DrManzo |
| Known Email Patterns | typhonscyberforge@gmail.com (known); djinnstudio@gmail.com (found in commit history — see NETPROBE/RECON) |
| Known Location | — (not searched, out of scope) |
| Associated Entities | Djinn AI OS, Forge (3D print/commission shop), Hellhound |

---

## Operation Scope

**Objective:**
Passive self-audit of Javier's public digital footprint via the `DrManzo` GitHub identity — specifically, what would an outside party with only public access (no vault/filesystem access) actually find. Prompted directly by discovering a live-but-dead API key hardcoded in the public `djinn-vault` repo earlier this session.

**In Scope (Tier 1):**
GitHub profile metadata, public repo inventory, GitHub code search across all public repos under the account, git commit author metadata, general web search for handle/email reuse.

**In Scope (Tier 2, added — operator provided real-name seed directly):**
General web search cross-referencing operator's real name against the `DrManzo`/Djinn/Forge online identity (checking for a public link, not building one); Gravatar lookup on both known emails.

**Out of Scope:**
Any active probing, any third party, PimEyes/facial recognition, anything beyond Tier 2. Operator's real full name is intentionally **not written in plaintext in this file** — see PII Notice below; recording it here would itself create the real-name↔persona link this audit exists to check for, in a public repo.

---

## Agent Assignments

| Agent | Task | Status |
|---|---|---|
| RECON | GitHub profile + general web search for handle/email | Done |
| NETPROBE | GitHub code search across all public repos for secret patterns; commit author metadata | Done |
| SOCIAL | Real-name-to-persona cross-reference search; Gravatar lookup | Done |
| ARCHIVE | N/A this pass | Skipped |
| TREND | N/A | Skipped |

---

## Findings Log

### RECON
- General web search for "DrManzo" + "djinn-vault" and for "typhonscyberforge" returns **no results** — the account/repo isn't indexed by mainstream search engines yet. This is low visibility, not real protection: anyone with the exact handle or a direct link finds it immediately via GitHub's own search/UI, which has a separate index from general web search.
- GitHub profile (`api.github.com/users/DrManzo`): `bio`, `company`, `location`, `email`, `blog`, `twitter_username` all null/empty. No PII on the profile itself. 11 followers. Account created 2017-05-26.

### NETPROBE
- **10 public repos** under DrManzo, not just `djinn-vault`: `AI` (2015, stale), `djinn-vault` (active), `faust` (2026-04), `Faust_CLI` (2026-05, "local command-line AI assistant"), `FinalProject` (2026-05), `hypertrack-live-android` (2017, stale), `JourneyGame` (2025), `sample-java-project` (2017, stale), `skadoosh` (2016, stale), `VLocksEnd` (2026-03).
- Ran GitHub code search (`secret`, `password`, `api_key`, `apikey`, `token`, `BEGIN PRIVATE KEY`) scoped to `user:DrManzo` across **all 10 repos**. Every hit returned was inside `djinn-vault`; none of the other 9 repos matched any pattern. Most `djinn-vault` hits are false positives (English-word matches in fiction/docs, e.g. `The-Masks-Of-Virellion.md`, or self-referential — the bug reports/logs *about* the Penelope key fix showing up because they contain the word "apikey"). No new live secret found beyond the one already fixed earlier this session.
- **New finding: a second real email is exposed via git commit metadata.** `git log --all --format='%an <%ae>'` on `djinn-vault` shows commit author `DrManzo <djinnstudio@gmail.com>` — a different address from the known `typhonscyberforge@gmail.com`. This is standard git behavior (author identity is baked into every commit) but it's real PII on a public repo that GitHub's profile page itself successfully hides.
- **Confirmed: the already-fixed Penelope API key is still reachable in git history.** `git log --all -S"<the old key>"` returns 5 commits. The key was redacted from the current file (this session, commit `bd2d6a3c`) but never purged from history — `git filter-repo` was attempted and timed out (see [[2026-07-12_bug-live-octoprint-api-key-hardcoded-in-public-penelope-manual-md]], TASK-103 in QUEUE.md). Confirmed the key itself is dead (403), so this is stale-secret hygiene, not a live exposure — but it means anyone who clones the repo and runs `git log -p` on the old commits still sees it.

### SOCIAL
- Cross-referenced operator's real name against "3D printing", "cybersecurity", and "Djinn" — **zero results connecting the real name to the `DrManzo`/Djinn/Forge/Hellhound persona.** This is the key Tier 2 finding: as far as general web search can tell, the operator's public-facing 3D-print/AI-ops identity and real legal name are not linked anywhere indexed. Good separation.
- Real name (surname shared with "Manzo-Ramos"/"Manzo") is common enough that name-only search returns dozens of unrelated people — LinkedIn profiles, a Spokeo aggregator page (86 matches nationally), a trucking company, an MLB player, none confirmably the operator. Deliberately did not pull any of these threads further — attributing a stranger's public records to the operator would be a real OSINT error, not a finding. If a positive link is ever needed, it requires operator-supplied disambiguators (city, employer, DOB range), not blind name search.
- Gravatar lookup on both known emails (`typhonscyberforge@gmail.com`, `djinnstudio@gmail.com`): both return 404 (no avatar registered) — no exposure via Gravatar.
- **Tooling note:** `djinn/workspaces/osint/tools/README.md` and `TEAM.md` list `djinn-bore-core` and `djinn-social-analyst` as "Active" tools used by SOCIAL for handle enumeration. Neither does that: `djinn-bore-core` is actually a 3D-print STL geometry tool (bores a proxy core seat — unrelated to OSINT), and `djinn-social-analyst` errors on a missing config file (`~/.config/djinn/meta.env`) and appears scoped to the Forge shop's own social analytics, not third-party handle enumeration. This SOCIAL pass was done manually via web search instead. Same class of doc/reality drift as the VISUAL roster mismatch fixed earlier — worth a follow-up audit of the whole `tools/README.md` inventory before trusting it again.

### ARCHIVE / TREND
Not run — no target keywords or historical-snapshot need identified for this pass.

---

## CORRELATOR Summary

Tier 1: two real, low-severity findings and one confirmation of an already-known, already-mitigated issue:
1. `djinnstudio@gmail.com` is exposed via commit metadata — not discoverable from the GitHub profile alone, but trivially found by anyone who reads commit history (which is exactly what an OSINT pass does).
2. The dead Penelope OctoPrint key is still physically present in git history 5 commits deep — no live risk (key confirmed dead), but it's the kind of thing that should get cleaned up as part of TASK-103.
3. The other 9 public repos on the account show no secret-pattern hits — clean.

Tier 2 (real name provided by operator): the headline result is a **negative** — no public link found between the operator's real name and the DrManzo/Djinn/Forge persona. That's the good outcome for an OPSEC audit. Secondary finding: the SOCIAL agent's documented tool stack (`djinn-bore-core`, `djinn-social-analyst`) doesn't actually do what `tools/README.md` claims — this pass was done manually instead.

No PII beyond email addresses and a name-search (no third party data retained) was collected. Nothing here rises above Tier 2.

---

## Confidence Level

- [x] High — Multiple independent sources corroborate (GitHub API, GitHub code search, local git log all agree)

---

## Recommended Next Steps

1. If `djinnstudio@gmail.com` is meant to be private, future commits to public repos should use the GitHub noreply address (`drmanzo@users.noreply.github.com`, already used in some commits) instead of a real Gmail address. Existing history can't be un-exposed without a history rewrite (same operation as TASK-103).
2. Complete TASK-103 (git-history purge of the dead Penelope key) during a deliberate off-hours pass — it would also be the natural point to scrub the `djinnstudio@gmail.com` commit-author exposure if desired, since both need the same `git filter-repo` + force-push operation. Worth doing together rather than twice.
3. Audit `djinn/workspaces/osint/tools/README.md` and `TEAM.md`'s tool inventory against what actually exists/works — `djinn-bore-core` and `djinn-social-analyst` are both misattributed to OSINT/SOCIAL use. Same class of drift as the VISUAL roster mismatch fixed earlier this session.
4. If a real handle-enumeration tool is wanted for future SOCIAL passes, that's the `djinn-social-map` "planned" tool in `tools/README.md`, not the two currently listed as "Active" — it doesn't exist yet either, so this pass used plain web search as a substitute.

---

## Operation Timeline

| Date | Agent | Action |
|---|---|---|
| 2026-07-12 | SCRIBE | Target file created |
| 2026-07-12 | RECON | GitHub profile + web search complete |
| 2026-07-12 | NETPROBE | Code search + commit metadata audit complete |
| 2026-07-12 | SCRIBE | Report assembled, case closed (Tier 1) |
| 2026-07-12 | Operator | Provided real-name seed directly, requested Tier 2 escalation |
| 2026-07-12 | SOCIAL | Real-name/persona cross-reference + Gravatar check complete |
| 2026-07-12 | SCRIBE | Report updated, case re-closed (Tier 2) |

---

## PII Notice

Operator's real full name was provided verbally during this session and used as a search seed, but is **intentionally not recorded in plaintext** anywhere in this file or the linked report — this is a public repo, and writing the real name here would itself create the exact real-name-to-persona link this audit confirmed does not currently exist. No encrypted-DB pipeline was available to store it more safely, so the safest option was simply not writing it to the vault at all. Two real email addresses (already known to the operator) remain recorded in plaintext per the operator's own explicit self-audit request.

---

*Case closed by SCRIBE. Tier 2 — auto-approved per workspace Gateway policy, no operator confirm beyond the escalation request itself required.*
