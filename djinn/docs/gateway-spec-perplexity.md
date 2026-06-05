<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# we also need a heavy handed routing system for all of the ai worl=king on djinn that will force them to use djinn to communicate while mainiting their functions the should be funneled into an single entress when accessing the github or djinn vault that restricts them from operating autonomusly unless given Dev options and doing all except doing anything that distrups poduction by asking before commiting to an act

Now I have the full picture. The structure is clear — COMMS.md is the existing hub , ROUTING.md defines the agent rules , the orchestrator is the runtime entry point . Here's the complete spec for the gateway system.

***

This is a **Djinn Gateway** — a single enforcement layer that every AI touching the vault or GitHub must pass through, with three modes and one rule: nothing irreversible happens without a checkpoint. Here's the full design.

***

## What This Is Not

This is not a firewall and not a permissions system in the OS sense. Every AI already has its tools. What's missing is **a behavioral contract enforced at runtime** — a wrapper that sits between the agent's intent and the action, classifies the action's risk tier, and routes accordingly. The orchestrator already does this partially for 3D jobs ; the gateway generalizes it to every AI action on the vault.

***

## The Three Access Modes

Every agent session starts in one of three modes. The mode is set in the session init, not per-action:


| Mode | Who Can Set It | What It Allows |
| :-- | :-- | :-- |
| **Standard** | Default for all sessions | Read anything, write COMMS, propose actions, ask before executing |
| **Dev** | Javier only, explicit flag | Full execution without approval gates, still logs everything |
| **Restricted** | Set automatically on production paths | Read-only + COMMS write; no file writes, no git commits, no shell execution |

The mode lives in a session context file — `~/.config/djinn/session.json` — set at session start. Any agent that can't read it defaults to **Restricted**.

***

## The Action Classification Table

Every discrete action an AI might take gets a risk tier. The gateway classifies before executing:


| Tier | Actions | Standard Mode | Dev Mode |
| :-- | :-- | :-- | :-- |
| **0 — Read** | Read any file, read COMMS, read git log, list directory | ✅ Auto-proceed | ✅ Auto-proceed |
| **1 — Log** | Write to COMMS.md, write session report, update HEARTBEAT | ✅ Auto-proceed | ✅ Auto-proceed |
| **2 — Propose** | Write to staging/, write to tmp/, create new branch | ✅ Auto-proceed + COMMS entry | ✅ Auto-proceed |
| **3 — Checkpoint** | Commit to git, push to GitHub, write to library/, overwrite existing STL, update queue | ⛔ **ASK FIRST** | ✅ Auto-proceed |
| **4 — Hard Stop** | Delete files, push to main directly, modify production shop data, modify ROUTING.md/PROTOCOL.md | ⛔ **BLOCKED — requires explicit Dev + confirm** | ⛔ **Requires double-confirm** |

Tier 3 is where "ask before committing to an act" lives. The gateway intercepts, posts a COMMS entry with the proposed action and a human-readable summary, sends a Telegram notification to Javier, and waits for a `Y` / `N` / `SKIP` reply before proceeding.

***

## The Single Entry Point: `djinn-gateway`

This is a Python module that wraps every tool call. Agents don't call `git commit` or `write_file()` directly — they call `djinn.gateway.execute(action, payload, context)`. The gateway classifies, checks mode, routes.

```
djinn/
└── gateway/
    ├── __init__.py
    ├── gateway.py          ← Main enforcement class
    ├── classifier.py       ← Action → Tier mapping
    ├── session.py          ← Session context loader (mode, agent_id, job_id)
    ├── checkpoint.py       ← Tier 3 ask-and-wait logic
    └── audit_log.py        ← Every action logged to djinn/logs/gateway/
```


### Core Interface

```python
from djinn.gateway import gateway

# Every AI action goes through this — no exceptions
result = gateway.execute(
    action="git_commit",
    payload={"files": [...], "message": "..."},
    context={"agent": "claude", "job_id": 42, "reason": "bore-core update"}
)
# Returns: {"status": "approved|pending|blocked", "result": ..., "checkpoint_id": ...}
```


### `gateway.py` — The Enforcer

```python
class DjinnGateway:
    def execute(self, action: str, payload: dict, context: dict) -> dict:
        tier = self.classifier.classify(action, payload)
        mode = self.session.mode           # standard | dev | restricted
        agent = context.get("agent", "unknown")

        # Tier 0–1: always pass
        if tier <= 1:
            result = self._run(action, payload)
            self.audit.log(tier, action, payload, context, "auto")
            return {"status": "approved", "result": result}

        # Tier 2: pass + COMMS entry
        if tier == 2:
            result = self._run(action, payload)
            self._comms_entry(tier, action, payload, context)
            self.audit.log(tier, action, payload, context, "auto")
            return {"status": "approved", "result": result}

        # Tier 3: checkpoint in Standard mode, auto in Dev
        if tier == 3:
            if mode == "dev":
                result = self._run(action, payload)
                self._comms_entry(tier, action, payload, context)
                self.audit.log(tier, action, payload, context, "dev_bypass")
                return {"status": "approved", "result": result}
            else:
                checkpoint_id = self.checkpoint.request(action, payload, context)
                # Blocks until Javier responds or timeout
                approved = self.checkpoint.wait(checkpoint_id, timeout_s=300)
                if approved:
                    result = self._run(action, payload)
                    self.audit.log(tier, action, payload, context, "approved")
                    return {"status": "approved", "result": result}
                else:
                    self.audit.log(tier, action, payload, context, "denied")
                    return {"status": "denied", "checkpoint_id": checkpoint_id}

        # Tier 4: hard block always
        if tier == 4:
            if mode == "dev":
                # Requires double-confirm — first approval creates a second checkpoint
                checkpoint_id = self.checkpoint.request(
                    action, payload, context,
                    message="⚠️ HARD STOP ACTION — confirm twice to proceed"
                )
                # ... double-confirm logic
            self.audit.log(tier, action, payload, context, "hard_blocked")
            return {"status": "blocked", "reason": f"Tier 4 action requires Dev mode + confirm"}
```


***

## The Checkpoint Flow (Tier 3)

When an agent hits a Tier 3 action, the flow is:

1. **Gateway posts to COMMS.md** — structured entry:

```
## CHECKPOINT-{id} | {timestamp} | {agent} | PENDING
**Action:** git_commit  
**Files:** djinn/printer/tools/djinn-bore-core.py  
**Message:** "Add auto-scale + wall thickness validation"  
**Reason:** bore-core v2 feature additions  
**Job:** #47  
→ Reply Y to approve, N to deny, SKIP to defer
```

2. **Marcus sends Telegram notification** — same summary, reply buttons Y / N
3. **Gateway blocks the calling agent** — it sleeps on a polling loop reading the checkpoint status from `~/.local/share/djinn/checkpoints/{id}.json`
4. **Javier replies** — Marcus writes the decision to the checkpoint file, updates the COMMS entry with `APPROVED` or `DENIED`
5. **Gateway resumes** — runs the action or returns the denial to the agent

Timeout default: **5 minutes**. On timeout, the action is **denied by default** — never auto-approved on timeout. Agent gets `{"status": "timeout_denied"}` and logs it in COMMS.

***

## GitHub-Specific Enforcement

The vault already has the GitHub token in the environment. Any agent that can write to GitHub (`git push`, API calls, PR creation) is already powerful. The gateway adds a git hook + a GitHub-side protection:

### Local Git Hook (`~/.config/djinn/hooks/pre-push`)

```bash
#!/bin/bash
# Every push runs through gateway classification
python3 -m djinn.gateway.git_hook --action pre_push \
  --remote "$1" --branch "$(git rev-parse --abbrev-ref HEAD)"
# Exit 1 = blocked by gateway
```

This installs via `djinn-gateway --install-hooks` and makes it impossible to bypass the gateway with a raw `git push` from any agent running under the djinn environment.

### GitHub Branch Protection (for the vault repo)

Set via GitHub API — protect `main` branch:

- Require PR for all pushes
- No direct push from any agent
- Only Javier's personal token (set with `DEV_OVERRIDE=1`) can bypass

This is the **hardware interlock** — even if an agent manages to get past the local gateway, main branch push fails at GitHub unless the PR was opened and approved through the COMMS checkpoint flow .

***

## Autonomous Operation Rules

Agents can work fully autonomously within these guardrails without asking for anything:

**Always autonomous (Tier 0–2):**

- Reading any file or directory in the vault
- Running analysis scripts (bore detection, surface scan, quote calculation)
- Writing to staging, tmp, or job directories
- Updating COMMS.md and session reports
- Creating new branches

**Never autonomous without checkpoint (Tier 3):**

- Committing to git (any branch)
- Pushing to GitHub
- Writing to `library/`, `queue/`, `originals/`
- Modifying shop DB or price data
- Sending Telegram messages to Javier (Marcus gate — not other agents)

**Never autonomous period (Tier 4):**

- Deleting any file (use archive/ instead)
- Modifying ROUTING.md, PROTOCOL.md, GATEWAY.md, Claude.md
- Pushing to main directly
- Modifying shop credentials or API keys

***

## Dev Mode Activation

```bash
# Javier activates Dev mode for a session
djinn-gateway --dev-session --duration 2h

# This writes:
# ~/.config/djinn/session.json
# {"mode": "dev", "activated_by": "javier", "expires": "2026-06-05T14:00:00"}

# All agents in this session skip Tier 3 checkpoints
# All actions still logged to gateway audit log
# Mode expires automatically — not sticky
```

Dev mode is **time-limited and session-scoped**. It never persists across reboots. When it expires, all agents revert to Standard automatically.

***

## What This Builds On (What Already Exists)

The infrastructure to make this work is already in the vault :


| Needed Component | Already Exists |
| :-- | :-- |
| COMMS write target | `COMMS.md` — all agents already append here |
| Telegram notification path | Marcus's Telegram bot — already wired for alerts |
| Checkpoint state storage | New: `~/.local/share/djinn/checkpoints/` |
| Audit log | New: `djinn/logs/gateway/YYYY-MM-DD.jsonl` |
| Agent identity in context | Already in orchestrator `run()` context |
| Mode config | New: `~/.config/djinn/session.json` |
| Git hook install point | New: `djinn-gateway --install-hooks` |

The orchestrator already implements the exact checkpoint pattern for engraving approval — `# Pause for approval — never auto-advance past engraving` . The gateway generalizes that single pause into a system-wide enforcement layer across every agent and every action class.

***

## New File to Create: `djinn/GATEWAY.md`

This is a Tier 4 protected file — no agent can modify it without Javier's double-confirm. It becomes the canonical rules document for the system, living alongside [ROUTING.md](https://github.com/DrManzo/djinn-vault/blob/main/djinn/ROUTING.md) and [PROTOCOL.md](https://github.com/DrManzo/djinn-vault/blob/main/djinn/communications/PROTOCOL.md).

Every agent's session-start prompt includes one line: **"Read GATEWAY.md before acting."** That's the enforcement hook for AI agents that aren't running Python (like Marcus operating through the web interface) — the behavioral contract is loaded at context initialization, not at runtime.

