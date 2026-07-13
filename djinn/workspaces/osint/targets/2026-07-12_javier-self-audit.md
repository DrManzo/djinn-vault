# Target: javier-self-audit

**Case Code:** OSINT-2026-07-12-javier-self-audit
**Opened:** 2026-07-12
**Status:** Closed
**Operator:** Javier (DrManzo)
**Gateway Tier:** [x] Tier 1 — Passive

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

**In Scope:**
GitHub profile metadata, public repo inventory, GitHub code search across all public repos under the account, git commit author metadata, general web search for handle/email reuse.

**Out of Scope:**
Real name/address discovery, any active probing, any third party, PimEyes/facial recognition, anything beyond Tier 1.

---

## Agent Assignments

| Agent | Task | Status |
|---|---|---|
| RECON | GitHub profile + general web search for handle/email | Done |
| NETPROBE | GitHub code search across all public repos for secret patterns; commit author metadata | Done |
| ARCHIVE | N/A this pass | Skipped |
| SOCIAL | N/A — no other platform handles seeded | Skipped |
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

### SOCIAL / ARCHIVE / TREND
Not run — no seed data (other platform handles, target keywords) provided for this pass. Would be natural follow-ups if this becomes a recurring self-audit.

---

## CORRELATOR Summary

Two real, low-severity findings and one confirmation of an already-known, already-mitigated issue:
1. `djinnstudio@gmail.com` is exposed via commit metadata — not discoverable from the GitHub profile alone, but trivially found by anyone who reads commit history (which is exactly what an OSINT pass does).
2. The dead Penelope OctoPrint key is still physically present in git history 5 commits deep — no live risk (key confirmed dead), but it's the kind of thing that should get cleaned up as part of TASK-103.
3. The other 9 public repos on the account show no secret-pattern hits — clean.

No PII beyond email addresses was collected. Nothing here rises above Tier 1/2.

---

## Confidence Level

- [x] High — Multiple independent sources corroborate (GitHub API, GitHub code search, local git log all agree)

---

## Recommended Next Steps

1. If `djinnstudio@gmail.com` is meant to be private, future commits to public repos should use the GitHub noreply address (`drmanzo@users.noreply.github.com`, already used in some commits) instead of a real Gmail address. Existing history can't be un-exposed without a history rewrite (same operation as TASK-103).
2. Complete TASK-103 (git-history purge of the dead Penelope key) during a deliberate off-hours pass — it would also be the natural point to scrub the `djinnstudio@gmail.com` commit-author exposure if desired, since both need the same `git filter-repo` + force-push operation. Worth doing together rather than twice.
3. If this self-audit is worth repeating periodically, next pass should add SOCIAL (handle reuse across platforms) and ARCHIVE (Wayback snapshots of the repo before today's cleanup) — skipped this time due to no seed handles beyond GitHub.

---

## Operation Timeline

| Date | Agent | Action |
|---|---|---|
| 2026-07-12 | SCRIBE | Target file created |
| 2026-07-12 | RECON | GitHub profile + web search complete |
| 2026-07-12 | NETPROBE | Code search + commit metadata audit complete |
| 2026-07-12 | SCRIBE | Report assembled, case closed |

---

*Case closed by SCRIBE. Tier 1 throughout — no operator confirm required.*
