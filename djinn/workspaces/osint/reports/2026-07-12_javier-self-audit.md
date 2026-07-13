# Intelligence Report: Javier / DrManzo Self-Audit

**Report ID:** OSINT-RPT-2026-07-12-javier-self-audit
**Target:** [[2026-07-12_javier-self-audit]]
**Date:** 2026-07-12
**Assembled by:** SCRIBE (Claude)
**Reviewed by:** Javier (DrManzo)
**Status:** Final

---

## Executive Summary

First real operation run through the OSINT workspace since it was bootstrapped — a self-audit of Javier's public `DrManzo` GitHub identity, prompted by finding a live-but-dead API key hardcoded in the public `djinn-vault` repo earlier this session. Ran Tier 1 (passive infrastructure/repo audit), then escalated to Tier 2 (social/real-name cross-reference) at the operator's request. Tier 1 found one new piece of real exposure (a second real email, `djinnstudio@gmail.com`, leaked via git commit metadata), confirmed the already-fixed Penelope key is still physically present in git history, and confirmed the other 9 public repos on the account are clean. Tier 2's headline result is a **negative** (the good kind): no public link found anywhere between the operator's real name and the DrManzo/Djinn/Forge persona. Confidence: High. No action is urgent — everything found is low-severity — but several items are worth folding into the already-queued git-history purge (TASK-103), and a documented-tool-vs-reality gap was found in the SOCIAL agent's own tool stack.

---

## Methodology

| Agent | Techniques Used | Sources Queried |
|---|---|---|
| RECON | General web search, GitHub profile API | Google-indexed web, `api.github.com/users/DrManzo` |
| NETPROBE | GitHub code search (secret-pattern sweep), local git log analysis | `search/code` API scoped to `user:DrManzo`, `git log --all` on djinn-vault |
| SOCIAL | Real-name cross-reference search, Gravatar lookup (done manually — see tooling note below) | General web search, `gravatar.com/avatar/<md5>` |

ARCHIVE and TREND were not run — no target keywords or historical-snapshot need identified for this pass.

---

## Findings

### Identity & Profile

GitHub account `DrManzo`, created 2017-05-26, 11 followers, 10 public repos. Profile fields (`name`, `bio`, `company`, `location`, `email`, `blog`, `twitter_username`) are all empty — no PII surfaced from the profile page itself.

### Digital Footprint

`DrManzo` + `djinn-vault` does not appear in general web search results (Google-class indexing) — the repo is too new/low-traffic to be indexed yet. This is not real protection: GitHub's own search index found it instantly, and anyone with the direct handle or URL reaches it with zero friction.

Other public repos under the same account, none flagged by the secret-pattern sweep: `AI`, `faust`, `Faust_CLI`, `FinalProject`, `hypertrack-live-android`, `JourneyGame`, `sample-java-project`, `skadoosh`, `VLocksEnd`.

### Network & Infrastructure

Not applicable this pass — `djinn-vault` has no custom domain, DNS, or hosting infrastructure of its own to probe (it's a GitHub-hosted repo, not a live service).

### Social Graph

Real name provided directly by the operator was cross-referenced against the DrManzo/Djinn/Forge/Hellhound persona — no public link found. The surname is common enough (dozens of unrelated "Manzo"/"Manzo-Ramos" people nationally, per aggregator sites) that name-only search is not a viable identification path either way; not pursued further to avoid misattributing strangers' data. Both known emails return 404 on Gravatar — no exposure there.

Operator also supplied a Pinterest handle (`boxingking1`) for a direct check. Its page title/meta description are fully public and search-indexed, and directly attribute the account to the operator's real name (more discoverable by real-name search than `djinn-vault` currently is). Content is unrelated hobby boards (hairstyle/facial-hair history, general art references) with no mention of Djinn, Forge, or the maker/cybersecurity persona; the handle isn't reused elsewhere in a way that bridges either. Net result stands: real-name and persona remain unlinked, but this account is a concrete example of how discoverable the real-name side already is.

Operator additionally confirmed ownership of two LinkedIn profiles surfaced by earlier name search. LinkedIn actively blocks unauthenticated access (HTTP 999 on all fetch attempts), so only the pre-indexed search-snippet headlines were available: one references a university student era, the other employment at a home-improvement company — neither connects to the Djinn/Forge persona. Compared to Pinterest, LinkedIn's access controls meaningfully reduce what's actually scrapable even though the account is real-name-confirmed.

Operator also supplied 14 additional personal email addresses/aliases directly and confirmed all as their own. None of the 14 had any prior independent public exposure, so — unlike every other identifier in this report — the raw addresses are withheld entirely rather than redacted-but-described; recording them here would make this audit the source of a new leak. Gravatar-checked all 14 (public, non-destructive): 13 clean, one resolved to an art image (not a personal photo) thematically consistent with the `boxingking1` Pinterest boards. One address sits at a custom domain that returned NXDOMAIN — not currently registered/resolving. Per-address breach exposure (HaveIBeenPwned) could not be checked — the v3 API requires a paid key not currently configured in this workspace; flagged as a real capability gap, not a clean result.

**Tier 3.** Operator confirmed escalation and supplied a headshot photo directly, requesting PimEyes facial recognition specifically. EXIF check (run first per protocol) came back clean — no GPS, device, or timestamp metadata. PimEyes itself, and even the lower-tier reverse-image engines (TinEye, Yandex, Google Images, Bing Visual), could not actually be executed — all require either public-hosting the photo first or an interactive anti-bot-protected browser session, neither of which was available/acceptable here. Confirmed via direct endpoint tests against TinEye and Yandex (405/400 rejections) rather than just assuming. The photo was used locally for the EXIF check only and was never uploaded or hosted anywhere.

The SOCIAL agent's documented tools (`djinn-bore-core`, `djinn-social-analyst`) turned out not to do handle enumeration at all — `djinn-bore-core` is a 3D-print geometry tool and `djinn-social-analyst` requires missing config; this pass substituted plain web search.

### Historical Record

The dead Penelope OctoPrint API key (redacted from the live file earlier this session, commit `bd2d6a3c`) is still present in 5 reachable commits in `djinn-vault`'s git history — `git filter-repo` was attempted but timed out on the repo's size; the purge is tracked as TASK-103 in QUEUE.md. Confirmed dead via a live 403 against the actual printer, so this is hygiene, not live exposure.

### Trend Signals

Not applicable — no market/community keyword tracking was in scope for a self-audit.

---

## Entity Link Map

Single entity (Javier / DrManzo) across two identifiers found: GitHub handle `DrManzo`, and two real email addresses — `typhonscyberforge@gmail.com` (already known) and `djinnstudio@gmail.com` (newly surfaced, via commit author metadata on `djinn-vault`, not the GitHub profile).

---

## Confidence Assessment

| Finding | Source Count | Confidence |
|---|---|---|
| `djinnstudio@gmail.com` exposed via commit metadata | 1 (direct `git log`) | High |
| Dead Penelope key still in git history | 2 (git log + `-S` pickaxe search) | High |
| Other 9 public repos clean of secret patterns | 1 (GitHub code search, 6 query patterns) | Medium — code search isn't exhaustive; a targeted manual review would raise confidence |
| Repo not yet indexed by general web search | 1 (WebSearch, 3 queries) | Medium — indexing lag, not a permanent property |
| No public link between real name and DrManzo persona | 1 (WebSearch, targeted cross-reference query) | Medium — absence-of-evidence, not proof; a determined search with different terms could still surface something |

---

## Recommended Next Steps

1. Decide whether `djinnstudio@gmail.com` should be public. If not, future commits should use the GitHub noreply email (already used inconsistently — some commits use it, some don't).
2. Fold the `djinnstudio@gmail.com` history exposure into TASK-103's git-history purge — same `filter-repo` operation would need to run either way, better to do both at once than run the heavy rewrite twice.
3. Consider this the template for a recurring quarterly self-audit rather than a one-off — the workspace was built for exactly this and has sat unused since 2026-06-18.
4. Fix `tools/README.md`/`TEAM.md`'s SOCIAL tool listing — `djinn-bore-core` and `djinn-social-analyst` are misattributed. Same class of drift as the VISUAL roster mismatch fixed earlier this session; worth a full pass over the tool inventory before it's trusted again.
5. `javier@typhonsforge.com`-pattern domain doesn't resolve — register it if it's meant to be live.
6. A real HaveIBeenPwned integration would raise confidence on future passes; currently only the keyless "latest breach" feed is wired.
7. VISUAL's Tier 3 (PimEyes/reverse-image) capability doesn't work autonomously from this environment — needs either operator-run manual searches or future tooling investment. `agents/VISUAL.md` should be updated to reflect this rather than presenting it as a straightforward escalation.

---

## PII Notice

Two real email addresses (`typhonscyberforge@gmail.com`, `djinnstudio@gmail.com`) are recorded in plaintext in the linked target file — both were already independently public before this audit (known public contact; git-history exposure respectively). A further 14 emails, two LinkedIn profile IDs, and the operator's real full name were all used as search inputs during this operation but are **deliberately withheld** from both this report and the target file, since none had independent prior exposure — writing them here, in a public repo, would make this audit the source of a new leak rather than a check against one. No third-party PII was retained.

---

*Report assembled by SCRIBE — part of the Djinn OSINT system*
