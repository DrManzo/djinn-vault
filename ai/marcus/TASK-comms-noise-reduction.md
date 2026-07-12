# TASK — COMMS Noise Reduction

**Brief authored by:** Marcus  
**Date:** 2026-06-14  
**Assigned to:** Salomon  
**Output path:** `djinn/research/marcus/TASK-comms-noise-reduction.md`

---

## 1. Checkpoint Timeout Daemon — `djinn-checkpoint-cleanup`

### Problem

COMMS-2026-06.md contains ~60+ accumulated `PENDING` checkpoint entries (pattern: `CHECKPOINT-YYYYMMDD-HHMMSS | ... | unknown | PENDING`). Every one is `git push to origin (main)`, Tier 3 or 4, agent `unknown`, never resolved. These block signal visibility — a real agent message is buried under 10–20 consecutive checkpoint lines.

### Spec

**Script name:** `djinn-checkpoint-cleanup`  
**Install path:** `~/.local/bin/djinn-checkpoint-cleanup`  
**Vault path:** `automation/djinn-checkpoint-cleanup`  
**Trigger:** Run as part of the existing `comms-processor` cycle, NOT as a standalone daemon. Rationale: the comms-processor already reads COMMS.md on a timer; adding a second daemon that also reads/writes COMMS.md introduces a race condition. Embed cleanup as a pre-pass inside `comms_processor.py` (or the shell equivalent) before it processes new entries.

**Logic (pseudocode):**

```python
TIMEOUT_MINUTES = 5
COMMS_PATH = "djinn/communications/COMMS.md"

def cleanup_stale_checkpoints(comms_path):
    lines = read_file(comms_path)
    now = datetime.utcnow()
    output = []
    i = 0
    while i < len(lines):
        block_start = i
        # Detect checkpoint header: "### CHECKPOINT-YYYYMMDD-HHMMSS | ..."
        if re.match(r'^### CHECKPOINT-(\d{8}-\d{6})', lines[i]):
            ts_str = re.search(r'(\d{8}-\d{6})', lines[i]).group(1)
            checkpoint_time = datetime.strptime(ts_str, "%Y%m%d-%H%M%S")
            block = collect_block(lines, i)  # collect until next '---' or '###'
            age_minutes = (now - checkpoint_time).total_seconds() / 60
            is_pending = any("PENDING" in l for l in block)
            if is_pending and age_minutes > TIMEOUT_MINUTES:
                # Replace status line
                block = replace_status(block, "PENDING", "TIMEOUT_DENIED")
                block.append("→ Auto-resolved: exceeded 5-min window, no Javier response.\n")
            output.extend(block)
            i += len(block)
        else:
            output.append(lines[i])
            i += 1
    write_file(comms_path, output)
    append_cleanup_summary(comms_path, resolved_count)
```

**Cleanup entry format (appended once per run, not per checkpoint):**

```
### CLEANUP-{YYYYMMDD-HHMMSS} | djinn-checkpoint-cleanup | INFO
**Action:** Bulk timeout sweep
**Resolved:** {N} PENDING checkpoints → TIMEOUT_DENIED (age > 5 min)
**Range:** {oldest_id} → {newest_id}

— djinn-checkpoint-cleanup
```

**Integration point:** Add as `from automation.djinn_checkpoint_cleanup import run_cleanup` at the top of the comms-processor main loop, called before the entry dispatch switch. One function call, no subprocess, no new timer.

---

## 2. COMMS Three-Tier Split

### Problem

COMMS.md currently holds three distinct traffic types at equal visual weight:

1. **Agent coordination** — `@Claude → @All`, `@Salomon → @Marcus`, etc. — real signal
2. **Clerk→Slipbox per-note handoffs** — pipeline-internal routing noise, ~100 entries/session
3. **Checkpoint lifecycle** — gateway enforcement events, not conversation

### Design

| Tier | File | Writer | Reader | Retention |
|------|------|--------|--------|-----------|
| Agent coordination (signal) | `djinn/communications/COMMS.md` | All agents | All agents | Rotate at 50 KB |
| Clerk/Slipbox pipeline log | `djinn/communications/PIPELINE.md` | Clerk, Slipbox, Typhon session-end | Nobody (machine-only) | Batched daily summary only |
| Checkpoint lifecycle | `djinn/communications/CHECKPOINTS.md` | `djinn-gateway` pre-push hook | `djinn-checkpoint-cleanup` | Rotate weekly |

**COMMS.md rule going forward:** An entry belongs in COMMS.md if and only if it is agent-to-agent intentional communication — a decision, a status requiring human or agent action, a handoff of responsibility. Fully mechanical pipeline events (note processed, vault-sync push blocked, Clerk handed off file) do not qualify.

**PIPELINE.md format** — batched daily summary, not per-note:

```
### PIPELINE-SUMMARY-{YYYYMMDD} | Clerk | DAILY
**Notes processed:** {N}
**Slipbox runs:** {N}
**Typhon write requests fulfilled:** {N}
**Paths:** (list of note filenames, comma-separated, one line)

— Clerk
```

Clerk writes to `PIPELINE.md` once per day (driven by a `clerk.timer` equivalent), not on every note. The per-note `@Clerk → @Slipbox: New note ready for linking` entries that currently litter COMMS.md are **deleted from the Clerk output template** entirely — Slipbox reads a queue directory, not COMMS.

**CHECKPOINTS.md** takes over all `### CHECKPOINT-*` blocks from `djinn-gateway`'s pre-push hook. Change one line in the hook:

```bash
# Before:
COMMS_FILE="$VAULT/djinn/communications/COMMS.md"

# After:
COMMS_FILE="$VAULT/djinn/communications/CHECKPOINTS.md"
```

`djinn-checkpoint-cleanup` scans `CHECKPOINTS.md` instead of `COMMS.md`.

---

## 3. Agent Tag Fix — Who Is Writing `agent: unknown`

### Root Cause

From COMMS.md evidence, all `unknown` checkpoints are written by the **`djinn-gateway` pre-push Git hook** (`djinn/hooks/pre-push` or `~/.git/hooks/pre-push`). The hook calls `djinn-gateway checkpoint` (or writes the COMMS block directly via shell heredoc), but it does not know which agent initiated the push — it only sees the Git process.

The hook runs as the OS user (`drmanzo`), not as an agent session. It has no `$DJINN_AGENT` environment variable set, so it defaults to `unknown`.

### Fix

**Step 1:** Agents that trigger a vault push must export their identity before calling `git push`:

```bash
# In any agent script that calls git push:
export DJINN_AGENT="@Salomon"  # or @Typhon, @Claude, etc.
git push origin main
```

**Step 2:** The pre-push hook reads the variable:

```bash
# In pre-push hook, replace hardcoded "unknown":
AGENT="${DJINN_AGENT:-unknown}"

# Write checkpoint block:
cat >> "$COMMS_FILE" <<EOF
### CHECKPOINT-${TIMESTAMP} | ${TIMESTAMP_HUMAN} | ${AGENT} | PENDING
**Action:** git push to origin (${BRANCH})
...
EOF
```

**Step 3:** Identify the two callers that need tagging:

- `djinn-vault-sync` (Typhon's vault sync timer) → add `export DJINN_AGENT="@Typhon"` before its `git push` call
- `djinn-session-end` (session close script) → add `export DJINN_AGENT="@Salomon"` or detect agent from session.json `agent` field and export dynamically

**Patch locations:**
- `~/.local/bin/djinn-vault-sync` — line containing `git push`
- `~/.local/bin/djinn-session-end` — same
- `djinn/hooks/pre-push` — read `$DJINN_AGENT`

No other callers appear in the COMMS log based on pattern analysis (all PENDING checkpoints are vault-sync or session-end pushes, not interactive agent commands).

---

## 4. Rotation Strategy — Pipeline Log Files

### Rotation Plan

| File | Trigger | Archive name | Max live size |
|------|---------|--------------|---------------|
| `COMMS.md` | File reaches **50 KB** | `COMMS-archive-{YYYY-MM}.md` | 50 KB |
| `CHECKPOINTS.md` | **Weekly** (Sunday 03:00 UTC) | `CHECKPOINTS-archive-{YYYY-WNN}.md` | ~40 KB est. |
| `PIPELINE.md` | **Monthly** (1st of month, 03:00 UTC) | `PIPELINE-archive-{YYYY-MM}.md` | ~30 KB est. |

**All archives land in:** `djinn/communications/archive/`

**Rotation logic (shared helper):** `automation/djinn-comms-rotate`

```bash
#!/usr/bin/env bash
# Usage: djinn-comms-rotate <file> <archive-name>
FILE="$1"
ARCHIVE="$2"
ARCHIVE_DIR="$(dirname "$FILE")/archive"

mkdir -p "$ARCHIVE_DIR"
cp "$FILE" "$ARCHIVE_DIR/$ARCHIVE"
# Preserve last 3 lines as continuity header in new live file
tail -3 "$FILE" > "${FILE}.tmp"
echo "" >> "${FILE}.tmp"
echo "<!-- rotated $(date -u +%Y-%m-%dT%H:%M:%SZ) — archive: archive/$ARCHIVE -->" >> "${FILE}.tmp"
mv "${FILE}.tmp" "$FILE"
```

**Rotation size estimates (based on observed COMMS-2026-06.md = ~114 KB over ~10 days):**

- `COMMS.md` at 50 KB cap: rotates roughly every **4–5 days** during active development
- `CHECKPOINTS.md` weekly: at ~10–15 checkpoints/hour during active sessions, expect **~500–800 entries/week**, yielding archive files of **~60–80 KB**
- `PIPELINE.md` monthly: at ~100 Clerk/Slipbox entries/session, 2–3 sessions/day, expect **~5,000–9,000 entries/month** if not batched, or **~30 daily-summary entries** if the batching fix (Section 2) is applied — archive files then ~**8–15 KB/month**

**Systemd timer for CHECKPOINTS rotation:**

```ini
# /etc/systemd/user/djinn-checkpoints-rotate.timer
[Timer]
OnCalendar=Sun 03:00 UTC
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/user/djinn-checkpoints-rotate.service
[Service]
ExecStart=/home/drmanzo/.local/bin/djinn-comms-rotate \
  /home/drmanzo/Obsidian/djinn/communications/CHECKPOINTS.md \
  CHECKPOINTS-archive-%Y-W%V.md
```

COMMS.md size-based rotation is best handled inside `djinn-comms-rotate` called by `comms-processor` after each write — check `wc -c COMMS.md`, rotate if > 51200 bytes. No separate timer needed.

---

## Implementation Order

1. **Pre-push hook patch** (Section 3) — 10 min, immediate noise reduction on future checkpoints
2. **CHECKPOINTS.md split** (Section 2, checkpoint tier only) — change one variable in pre-push hook
3. **Clerk batching** (Section 2, pipeline tier) — edit Clerk output template to suppress per-note COMMS writes; create PIPELINE.md target
4. **`djinn-checkpoint-cleanup`** (Section 1) — embed in comms-processor, cleans up the existing ~60 stale PENDING entries in one pass
5. **Rotation timers** (Section 4) — wire systemd timers after new files exist
