================================================================================
                      DJINN BUGHUNTER MANUAL
          Proactive Vulnerability Scanner — Security Audit Tool
================================================================================
Version: 1.0 | Last updated: 2026-06-15 | Maintained by: Owner / Marcus

> Automated security scanner for the Djinn stack. Runs four distinct checks
> on a scheduled basis and deduplicates findings across runs. Findings land
> in djinn/logs/bugs.md.

================================================================================
TABLE OF CONTENTS
================================================================================

  1.  What It Scans
  2.  How to Run It
  3.  Findings — Format and Destination
  4.  Deduplication
  5.  Timer Schedule
  6.  Scope Reference

================================================================================
1. WHAT IT SCANS
================================================================================

Four checks run on every invocation:

  Check 1 — Bandit Static Analysis
    Scans djinn-* prefixed Python scripts in ~/.local/bin/.
    Reports CWE-mapped issues: injection flaws, insecure function use,
    hardcoded secrets in code, etc.
    Runs with -q flag to suppress Rich progress bar output (prevents JSON
    parse errors from stdout pollution — this was a confirmed bug, now fixed).

  Check 2 — pip-audit CVE Scan
    Scans all Python packages installed in the active environment.
    Reports CVEs with PURL identifiers, affected version, and fix version
    if available.
    Scope: full pip environment, not limited to djinn-* scripts.

  Check 3 — Secrets Regex
    Regex-based scan of all scripts under ~/.local/bin/.
    Targets: API keys, tokens, passwords, private key headers, bearer
    strings, and similar credential patterns.
    Scope: all scripts in ~/.local/bin/, not limited to djinn-* prefix.

  Check 4 — journald / /tmp Error Triage
    Pulls recent ERROR and CRITICAL entries from journald for
    djinn-related services.
    Also scans /tmp for crash files, core dumps, and error logs from
    the last run window.

================================================================================
2. HOW TO RUN IT
================================================================================

Run all four checks:
  djinn-bughunter

Run individual checks:
  djinn-bughunter --bandit       # bandit static analysis only
  djinn-bughunter --audit        # pip-audit CVE scan only
  djinn-bughunter --secrets      # secrets regex scan only
  djinn-bughunter --errlogs      # journald + /tmp triage only

Dry run (scan but do not write findings to bugs.md or update state):
  djinn-bughunter --dry-run
  djinn-bughunter --bandit --dry-run

Flags can be combined:
  djinn-bughunter --bandit --secrets      # run two checks only
  djinn-bughunter --audit --dry-run       # audit scan, no state write

================================================================================
3. FINDINGS — FORMAT AND DESTINATION
================================================================================

All findings append to:
  ~/djinn/logs/bugs.md

Each finding entry contains:
  - Timestamp of detection
  - Check type (bandit | pip-audit | secrets | errlogs)
  - Severity (if provided by source tool)
  - File path and line number (where applicable)
  - Finding description
  - SHA1 hash of the finding (used for deduplication — see Section 4)

Example entry:

  ## [2026-06-15T08:00:01] bandit | MEDIUM | B105
  File: ~/.local/bin/djinn-job-add
  Line: 42
  Issue: Possible hardcoded password string
  Hash: a3f1c2...

Duplicate findings (same SHA1 already in state file) are silently skipped.
Run with --dry-run to see what would be written without committing anything.

================================================================================
4. DEDUPLICATION
================================================================================

State file location:
  ~/.local/share/djinn/bughunter-state.json

How it works:
  Each finding is fingerprinted as a SHA1 hash over (check_type + file_path
  + line_number + finding_code). On every run, the hash is compared against
  the state file before writing to bugs.md. If the hash already exists, the
  finding is skipped — no duplicate entries accumulate in bugs.md.

  New findings (hash not in state) are written to bugs.md and the hash is
  added to the state file.

Resetting state (force re-report all findings):
  rm ~/.local/share/djinn/bughunter-state.json
  djinn-bughunter

Manual state inspection:
  cat ~/.local/share/djinn/bughunter-state.json | python3 -m json.tool

================================================================================
5. TIMER SCHEDULE
================================================================================

Unit files:
  djinn-bughunter.service   — oneshot service that runs the full scan
  djinn-bughunter.timer     — fires every hour on the hour

Check timer status:
  systemctl --user status djinn-bughunter.timer

Check last run:
  systemctl --user status djinn-bughunter.service

View logs from last run:
  journalctl --user -u djinn-bughunter.service -n 50

Force immediate run outside schedule:
  systemctl --user start djinn-bughunter.service

================================================================================
6. SCOPE REFERENCE
================================================================================

  Check          Target Scope
  ─────────────────────────────────────────────────────────────────────────
  bandit         djinn-* prefixed Python scripts in ~/.local/bin/ only.
                 Non-djinn binaries (e.g., Impacket tools) are excluded.
                 This is intentional — those tools generate false positives
                 that have nothing to do with the Djinn codebase.

  pip-audit      All installed Python packages in the active environment.
                 Scope is environment-wide — there is no per-tool filtering.

  secrets        All scripts under ~/.local/bin/ (no prefix filter).
                 Regex patterns are generic enough that any credential in
                 any script in that directory will be flagged.

  errlogs        journald entries for djinn-* services + /tmp scan.
                 Not scoped to Python files — catches runtime errors from
                 any part of the stack.

================================================================================
*— Marcus, 2026-06-15*
================================================================================
