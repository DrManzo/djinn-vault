---
title: "TASK-067 — Djinn Vault System Gap Analysis & Improvement Recommendations"
tags: [djinn, research, marcus, architecture, security, observability, backup, scalability]
created: 2026-06-06
author: Marcus (Perplexity)
status: complete
---

# TASK-067 — Djinn Vault: Gap Analysis & Improvement Recommendations

**Requested by:** Hermes (via Salomon)  
**Completed by:** Marcus (Perplexity AI)  
**Date:** 2026-06-06  
**Source architecture reviewed:** INFRASTRUCTURE.md, SYSTEM-STATE.md, ROUTING.md, GATEWAY.md, djinn/ directory tree

---

## Executive Summary

The Djinn Vault is an architecturally sophisticated personal AI-agent ecosystem. It outperforms most personal knowledge base systems in agent specialization, hardware role clarity, and safety protocol rigor (especially around 3D printing). The primary gaps fall into **five categories**: secrets hygiene, observability, backup verification, headless agent reliability, and knowledge-graph coherence. All are addressable with existing tooling and modest additions.

---

## Part 1 — Comparative Analysis

### Djinn Vault vs. Comparable Systems

| Dimension | Djinn Vault | Typical Obsidian+AI Setup | Home Lab LLM Stack |
|-----------|-------------|--------------------------|-------------------|
| Agent role specialization | ✅ 14+ named agents with clear lanes | ❌ Single catch-all agent | ⚠️ 2–3 models, no routing |
| Hardware role separation | ✅ Salomon (ops) / Typhon (storage/stream) | ❌ Single machine | ✅ Often separated |
| Safety interlocks (print) | ✅ Hard-blocked cancel + PIN + confirm flow | N/A | N/A |
| Secrets management | ⚠️ Env files, chmod 600, no rotation policy | ❌ Often plaintext .env | ⚠️ Variable |
| Observability | ⚠️ djinn-agent-doctor (11 checks), no metrics store | ❌ None | ⚠️ Prometheus ad hoc |
| Backup verification | ⚠️ rclone + git push, no restore-test protocol | ❌ None | ⚠️ rsync only |
| Knowledge graph | ⚠️ ChromaDB embeddings (688 files) + manual links | ⚠️ Obsidian graph, no semantic layer | ❌ None |
| CI/CD for agent configs | ❌ Manual deploy | ❌ None | ❌ None |
| Headless agent execution | ⚠️ Known limitation — opencode text-only in headless | N/A | N/A |

**Verdict:** Djinn Vault is best-in-class for personal AI ecosystems in agent design and safety. The gaps are operational maturity items, not architectural flaws.

---

## Part 2 — Gap Analysis by Domain

### 2.1 System Architecture

**Identified Gaps:**
- The Orin machine referenced in the task brief does not appear in INFRASTRUCTURE.md or SYSTEM-STATE.md. If Orin is a planned third node (likely NVIDIA Orin SBC for large-model hosting), its role, routing rules, and vault-sync behavior need to be documented before it goes live.
- The known limitation — *"opencode in headless mode generates text responses but does not reliably execute shell tools"* — means COMMS.md tasks routed to @Salomon or @Typhon may silently fail. There is no retry logic or failure detection.
- Model routing in ROUTING.md is static. There is no dynamic fallback if Salomon's Ollama is overloaded or unreachable from Typhon.

**Recommendations:**
1. **Add circuit-breaker logic to comms-processor.** If opencode returns a response with no tool calls executed (detectable by checking for file writes or service state changes), log the failure to COMMS.md and optionally alert via Telegram.
2. **Document Orin's role now**, even if the machine isn't live. Establish lane boundaries, model assignments, and routing rules preemptively. Use the existing INFRASTRUCTURE.md format.
3. **Dynamic model fallback:** Add a health-check wrapper to `djinn-ctx-router` that pings `http://salomon:11434/api/tags` before routing. If unreachable, route to Typhon-local models (llama3.2:3b, qwen2.5:1.5b) with a degraded-mode flag.

---

### 2.2 Security & Credential Management

**Identified Gaps:**
- Secrets live in `~/.config/djinn/*.env` (chmod 600). This is correct practice for storage but there is **no rotation schedule or rotation tooling** documented.
- The Telegram bot token was already rotated once (noted: "new token 2026-05-23"). The rotation process appears to be manual and ad hoc. No audit trail of rotations exists.
- OpenClaw's 45-tool allowlist is a good attack-surface reduction, but it is stored in a file that is not in git (local only). If Salomon is rebuilt, this config must be manually recreated — a bootstrap gap.
- The SSH keypair (`~/.ssh/id_ed25519`) enabling passwordless Salomon→Typhon access is not mentioned in the bootstrap documentation. Loss of this key during a rebuild would require physical access to Typhon to re-authorize.

**Recommendations:**
1. **Adopt a secrets rotation schedule.** Telegram bot tokens: rotate every 90 days. API keys: rotate on any suspected compromise or team member change. Log rotation events to `djinn/logs/security-log.md`.
2. **Back up the OpenClaw allowlist** (`~/.openclaw/` config) to `Project-Resources` repo under a `openclaw/` directory. It is currently marked "Local only" — this is a single point of failure.
3. **Add SSH key backup to bootstrap docs.** The `~/.ssh/id_ed25519.pub` should be stored in `Project-Resources` and the bootstrap script for Salomon should include the step to authorize it on Typhon.
4. **Consider HashiCorp Vault (local) or `pass` (GPG-based CLI)** for structured secrets management. `pass` is the lowest-friction option: it uses GPG encryption, integrates with shell scripts via `$(pass show djinn/telegram-token)`, and keeps a git history of secret metadata (not values).

**Tool Suggestion:** `pass` (passwordstore.org) — zero additional infra, GPG-backed, shell-native.

---

### 2.3 Monitoring & Observability

**Identified Gaps:**
- `djinn-agent-doctor` runs 11 health checks but appears to be invoked manually or on-demand. There is no continuous metrics collection or alerting threshold system.
- The heartbeat timer (5-min → HEARTBEAT.md) writes state to a markdown file but this data is not queryable or visualizable over time. You cannot ask "how many times did Salomon's Ollama go down in the past week?"
- There is no latency tracking for LLM inference calls. If phi4:14b starts timing out (noted in SYSTEM-STATE: "LLM timeout" fix from context window overflow), the only signal is a failed job — not a gradual degradation warning.
- No alerting for disk space. Both machines are at ~35–37% disk use now; with media pipelines and STL libraries growing, no threshold alert exists.

**Recommendations:**
1. **Add Prometheus + Grafana (lightweight).** The `prometheus-node-exporter` systemd service (single binary, ~10MB) exports CPU, RAM, disk, network metrics. Scrape from a Grafana instance on Typhon (it has headroom: 2.6Gi used of 14Gi). This gives you time-series data for both machines.
2. **Instrument Ollama inference latency.** Ollama exposes a `/api/generate` endpoint — wrap the call in `djinn-ctx-router` to record `(model, prompt_tokens, response_time_ms)` to a JSONL log at `~/Obsidian/djinn/logs/ollama-perf.jsonl`. Feed into Grafana.
3. **Add disk threshold alerts.** A simple cron: `df -h | awk '$5 > 80'` triggers a Telegram alert. Add to `djinn-agent-doctor` as check #12.
4. **Promote heartbeat data.** Instead of only writing to HEARTBEAT.md, write a structured JSON snapshot to `~/.local/share/djinn/heartbeat-history.jsonl` (append-only). This creates a queryable ops history without external infra.

**Tool Suggestions:**
- `prometheus-node-exporter` — system metrics
- `Grafana` (Docker on Typhon) — visualization
- `loki` (optional) — log aggregation if you want to go full observability stack

---

### 2.4 Disaster Recovery & Backup

**Identified Gaps:**
- The vault syncs to GDrive (rclone, 2-min) and GitHub (git push after rclone) from Salomon. Typhon only does `git pull`. This means **Typhon has no independent backup path** — if Salomon burns, the GDrive/GitHub copies are the only recovery point.
- There is no documented **restore procedure**. The bootstrap system provisions machines but the sequence for "restore vault from GDrive after total Salomon loss" is not written.
- No backup exists for `~/.openclaw/` (agent config, identity files, workspace). This is explicitly marked "Local only" and contains SOUL.md, IDENTITY.md, USER.md, AGENTS.md — the behavioral core of the system. Loss = full agent personality wipe.
- No RPO/RTO targets are defined. Without targets, you cannot know if the current 2-minute GDrive sync is adequate.
- Klipper/Moonraker printer config is noted as backed up in `djinn/printer/backup/` but no automated verification that the backup is current exists.

**Recommendations:**
1. **Define RPO/RTO targets explicitly.** Suggested:
   - Vault: RPO = 2 min (current GDrive sync), RTO = 30 min (git clone + bootstrap)
   - Agent configs (.openclaw): RPO = 24 hr, RTO = 1 hr
   - Print configs: RPO = after any config change, RTO = 2 hr
2. **Back up `~/.openclaw/` to Project-Resources repo.** Add a systemd timer: `djinn-openclaw-backup.service` runs daily, `rsync ~/.openclaw/ ~/Documents/Project-Resources/openclaw/`, then `git commit + push`.
3. **Write a restore runbook.** Create `djinn/docs/RESTORE-RUNBOOK.md` with step-by-step instructions for: (a) total Salomon rebuild from zero, (b) Typhon rebuild, (c) vault restore from GDrive. This document should be tested annually (fire drill).
4. **Add backup integrity check.** After each rclone sync, run `rclone check ~/Obsidian/ gdrive:djinn-vault --one-way` and log the result. A mismatch triggers Telegram alert.
5. **Consider a third backup destination.** GDrive + GitHub are both cloud. For geo-distribution, the 1TB Passport SSD (noted in Pending Work) should be added as a local encrypted backup target via `rclone crypt`.

---

### 2.5 Workflow Optimization & CI/CD

**Identified Gaps:**
- Agent skill files in `djinn/skills/` are deployed manually. There is no validation step — a malformed skill spec could silently break an agent.
- No automated testing for CLI tools (`djinn-print-consult`, `djinn-model-slice`, etc.). These are shell scripts with significant logic; regressions go undetected until a job fails.
- The changelog (`djinn-changelog.md`) is manually maintained. Entries can be missed or written inconsistently.
- No staging environment. Config changes go directly to production (Salomon's live services). A bad systemd unit file can break Telegram notifications mid-print.

**Recommendations:**
1. **Add a pre-commit hook** to the djinn-vault repo that validates frontmatter YAML on all `.md` files using `python-frontmatter`. Catches malformed tags before they break the vault indexer.
2. **Create a `djinn-test` script** that runs smoke tests for the 5 most-critical CLI tools:
   - `djinn-print-consult --dry-run` (no printer needed)
   - `djinn-model-slice --validate` (validate profile exists)
   - `djinn-agent-doctor` (existing — make it exit non-zero on failures)
   - `djinn-vault-indexer --count` (verify chunk count matches last known)
   - `djinn-ctx-router --test` (verify context assembly produces non-empty output)
3. **Automate changelog entries.** Add to the existing session report protocol: any agent that deploys a change must append a `djinn-changelog.md` entry using a standard template. Claude is best positioned to enforce this.
4. **Use a `.env.example` file** in Project-Resources to document all required environment variables without values. This prevents the "what env vars do I need?" problem during rebuilds.

---

### 2.6 Scalability & Performance

**Identified Gaps:**
- The RTX 5060 Laptop (Salomon) is the sole LLM host for both machines. All Typhon model requests remote-route to Salomon. This is a single point of contention — if Salomon is running phi4:14b for a design job while Typhon's comms-processor fires, the 7B request queues behind a 14B load.
- Context window sizes were already tuned once (noted: overflow fix). But the current config is static — no dynamic context scaling based on available VRAM.
- The ChromaDB index (688 files, 8,284 chunks) is rebuilt via `djinn-vault-indexer`. There is no incremental update strategy documented — only "run --full after index completes." Large vaults will make full rebuilds increasingly slow.
- Ollama is bound to `0.0.0.0:11434` — accessible to any device on the LAN without authentication.

**Recommendations:**
1. **Implement Ollama request queue prioritization.** Use Ollama's concurrency settings: set `OLLAMA_NUM_PARALLEL=2` and `OLLAMA_MAX_QUEUE=4` in the Ollama systemd environment. This prevents a phi4 job from blocking all 7B requests indefinitely.
2. **Add Ollama authentication.** Bind Ollama to `127.0.0.1:11434` on Salomon and use SSH port forwarding for Typhon (`ssh -L 11434:localhost:11434 salomon`). This eliminates LAN exposure. Alternatively, set `OLLAMA_HOST` with a bearer token (Ollama 0.2+ supports this).
3. **ChromaDB incremental indexing.** The `djinn-vault-indexer` should track file modification timestamps (stored in `~/.djinn/embeddings/vault.json`) and only re-embed files whose mtime has changed since last run. This is the standard approach — check if this is already implemented; if not, it's a ~20-line addition.
4. **Typhon local model expansion.** For low-stakes automation tasks (comms-processor admin summaries, heartbeat writes), configure Typhon's comms-processor to prefer local models (llama3.2:3b, qwen2.5:1.5b) before routing to Salomon. This reduces Salomon's load by ~30% for trivial tasks.

---

### 2.7 Knowledge Management

**Identified Gaps:**
- The vault has specialized directories (`daily/`, `weekly/`, `research/`, `decisions/`, `memory/`, `skills/`, etc.) but no documented **ontology** — the canonical tag hierarchy. Tags like `[djinn, infrastructure, architecture, onboarding]` are applied inconsistently across files.
- Orphaned documents (files with no inbound links in Obsidian) are not detected or reported. As the vault grows, islands of disconnected knowledge accumulate.
- The Slipbox agent uses semantic similarity for linking, but there is no scheduled review process for *rejecting* low-quality links that the agent proposes.
- The `i notes/` directory appears to be a processing inbox (Perplexity exports → Clerk → structured notes). The pipeline is documented but the quality gate between "raw" and "structured" is the Clerk LLM (qwen2.5:7b) — no human review step is specified.
- Research tasks are numbered but there is no index linking them to decisions or projects. TASK-037 (law), TASK-038 (psyc), TASK-039 (cash) have no visible parent linkage in the research-index.

**Recommendations:**
1. **Create a canonical tag taxonomy** at `djinn/core/TAG-TAXONOMY.md`. Define 3-level hierarchy: `domain/subdomain/specificity` (e.g., `djinn/infrastructure/networking`). Enforce via pre-commit hook or Clerk post-processing rule.
2. **Add orphan detection to djinn-agent-doctor** (check #13): run `grep -rL '\[\[' ~/Obsidian/djinn/ --include='*.md'` to find files with no wikilinks. Report count and list in weekly digest.
3. **Link research tasks to decision records.** Update `djinn/decisions/` entries to include a `research_refs:` field listing TASK IDs that informed the decision. Backward-link from TASK files to decisions using a `decisions:` frontmatter field.
4. **Weekly Slipbox review ritual.** Add a step to the Sunday `djinn-weekly` workflow: output the top 10 new semantic links proposed by the Slipbox agent and prompt Javier to accept/reject. This keeps the knowledge graph curated rather than auto-polluted.
5. **Knowledge graph export.** Use the Obsidian Dataview plugin or a Python script against the vault to export a `graph.json` (nodes = files, edges = wikilinks + semantic links). Periodically visualize to detect clusters and gaps. Store snapshots in `djinn/media/` for longitudinal comparison.

---

## Part 3 — Implementation Roadmap

### Priority Matrix

| Recommendation | Effort | Impact | Priority |
|----------------|--------|--------|----------|
| Back up `~/.openclaw/` to Project-Resources | Low (1hr) | Critical (agent personality loss risk) | 🔴 P0 |
| Write restore runbook | Low (2hr) | Critical (RTO undefined) | 🔴 P0 |
| Add SSH key to bootstrap docs | Low (30min) | High (rebuild blocker) | 🔴 P0 |
| Ollama authentication (bind to localhost) | Low (30min) | High (LAN exposure) | 🔴 P0 |
| comms-processor failure detection | Medium (3hr) | High (silent failures) | 🟠 P1 |
| `pass` secrets manager adoption | Medium (4hr) | High (rotation + audit trail) | 🟠 P1 |
| Disk space alert in djinn-agent-doctor | Low (1hr) | High (no current disk alerting) | 🟠 P1 |
| Ollama NUMA/queue config tuning | Low (1hr) | Medium (reduces contention) | 🟠 P1 |
| Pre-commit YAML validation hook | Low (2hr) | Medium (vault integrity) | 🟡 P2 |
| Heartbeat JSONL history logging | Low (1hr) | Medium (ops history) | 🟡 P2 |
| Canonical TAG-TAXONOMY.md | Medium (3hr) | Medium (knowledge coherence) | 🟡 P2 |
| Research → decisions cross-linking | Medium (4hr) | Medium (knowledge graph) | 🟡 P2 |
| Prometheus + Grafana (Typhon) | High (8hr) | Medium (metrics over time) | 🟢 P3 |
| Ollama inference latency logging | Medium (3hr) | Medium (performance visibility) | 🟢 P3 |
| ChromaDB incremental indexing | Medium (4hr) | Medium (vault scale) | 🟢 P3 |
| Third backup destination (Passport SSD) | Medium (3hr) | Low (nice-to-have geo-redundancy) | 🟢 P3 |
| `djinn-test` smoke test suite | High (6hr) | Medium (regression prevention) | 🟢 P3 |

### Suggested Sprint Order

**Week 1 (P0 — Immediate):**
- Back up `.openclaw/` → Project-Resources
- Add SSH key to bootstrap
- Bind Ollama to localhost
- Write minimal restore runbook

**Week 2 (P1 — Operational Hardening):**
- Add comms-processor failure detection
- Adopt `pass` for secrets
- Add disk alert to agent-doctor

**Week 3–4 (P2 — Knowledge & Workflow):**
- TAG-TAXONOMY.md
- Pre-commit YAML hook
- Cross-link research → decisions
- Heartbeat JSONL logging

**Backlog (P3 — Enhancement):**
- Grafana/Prometheus
- Latency logging
- Smoke tests
- Incremental ChromaDB

---

## Part 4 — Risk Assessment

| Change | Risk | Mitigation |
|--------|------|------------|
| Binding Ollama to localhost | Breaks Typhon remote routing if not using SSH tunnel | Set up SSH tunnel *before* changing bind address; test Typhon→Salomon model call |
| `pass` adoption | Breaks existing scripts that source `.env` files directly | Migrate one credential at a time; keep `.env` files as fallback initially |
| Prometheus on Typhon | Adds ~100MB RAM overhead | Typhon has 11.4GB headroom; negligible |
| Pre-commit hook | Blocks commits if YAML is malformed | Add `--no-verify` escape hatch; document in README |
| comms-processor failure detection | Could generate noise alerts | Tune detection threshold — only alert if *two consecutive* cycles show no tool execution |
| `.openclaw/` in git | Identity files (SOUL.md, USER.md) contain personal data | Ensure Project-Resources repo is private (it is); add `openclaw/` to `.gitignore` of any public forks |

---

## Part 5 — Validation Methods

For each major change, verify as follows:

**Ollama localhost binding:**
```bash
# From Typhon, verify remote routing still works
curl http://192.168.1.225:11434/api/tags  # Should fail (bound to localhost)
ssh -L 11434:localhost:11434 drmanzo@192.168.1.225 -N &
curl http://localhost:11434/api/tags  # Should succeed via tunnel
```

**`.openclaw/` backup:**
```bash
# Verify all identity files present in Project-Resources
ls ~/Documents/Project-Resources/openclaw/workspace/ | grep -E 'SOUL|IDENTITY|USER|AGENTS'
# Verify git history tracks the backup
git -C ~/Documents/Project-Resources log --oneline openclaw/
```

**Restore runbook:**
- Annual drill: provision a fresh VM (Fedora), follow the runbook from zero, verify vault is accessible and all services start cleanly. Record time-to-operational as the measured RTO.

**comms-processor failure detection:**
```bash
# Send a test task to COMMS.md that requires shell execution
echo "@Salomon — test: echo 'hello' > /tmp/comms-test.txt" >> ~/Obsidian/djinn/communications/COMMS.md
# Wait 3 minutes, check if file was created
ls /tmp/comms-test.txt && echo "PASS" || echo "FAIL — failure detection should have triggered"
```

**Disk alert:**
```bash
# Simulate alert condition
df -h | awk '$5+0 > 70 {print "ALERT:", $0}'  # Adjust threshold for test
```

**TAG-TAXONOMY compliance:**
```bash
# Check for files missing taxonomy-compliant tags (post-implementation)
python3 -c "
import frontmatter, glob
for f in glob.glob('/home/drmanzo/Obsidian/djinn/**/*.md', recursive=True):
    post = frontmatter.load(f)
    tags = post.get('tags', [])
    if not any('/' in t for t in tags):
        print(f'Non-hierarchical tags: {f}')
"
```

---

## Appendix — Tool Reference

| Tool | Purpose | Install |
|------|---------|---------|
| `pass` | GPG-backed secrets manager | `dnf install pass` |
| `prometheus-node-exporter` | System metrics export | `dnf install golang-github-prometheus-node-exporter` |
| `grafana` | Metrics visualization | Docker: `docker run -d -p 3000:3000 grafana/grafana` |
| `python-frontmatter` | YAML frontmatter validation | `pip install python-frontmatter` |
| `rclone check` | Backup integrity verification | Built into existing rclone install |
| Obsidian Dataview | Vault graph/query | Obsidian plugin (already in .obsidian/) |

---

*— Marcus (Perplexity AI), 2026-06-06. Research conducted against live vault state as of commit 23633b4 on DrManzo/djinn-vault.*  
*Reviewed architecture: INFRASTRUCTURE.md, SYSTEM-STATE.md, ROUTING.md, GATEWAY.md, djinn/ directory tree.*
