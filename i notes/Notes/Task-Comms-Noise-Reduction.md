---
subject: cs/comms/noise-reduction
tags:
  - cs/comms/noise-reduction/checkpoint-cleanup
  - cs/comms/noise-reduction/three-tier-split
  - cs/comms/noise-reduction/agent-coordination
  - cs/comms/noise-reduction/pipeline-log
created: 2026-06-28

# TASK — COMMS Noise Reduction

## Summary
The task involves addressing noise in the Djinn's communication system by implementing a checkpoint timeout daemon and splitting the `COMMS.md` file into three tiers to better manage different types of traffic.

## Key Points
- **Checkpoint Timeout Daemon**
  - Script name: `djinn-checkpoint-cleanup`
  - Install path: `~/.local/bin/djinn-checkpoint-cleanup`
  - Vault path: `automation/djinn-checkpoint-cleanup`
  - Trigger: Part of the existing `comms-processor` cycle
  - Logic:
    - Detect and mark `PENDING` checkpoints older than 5 minutes as `TIMEOUT_DENIED`

- **COMMS Three-Tier Split**
  - Tier 1: Agent coordination (signal)
    - File: `djinn/communications/COMMS.md`
    - Writers: All agents
    - Readers: All agents
    - Retention: Rotate at 50 KB

  - Tier 2: Clerk/Slipbox pipeline log
    - File: `djinn/communications/PIPELINE.md`
    - Writers: Clerk, Slipbox, Typhon session-end
    - Readers: Machine-only
    - Retention: Batched daily summary only

## Details
The primary issues with the current COMMS system are:
- Accumulated PENDING checkpoints that block signal visibility.
- Mixed traffic types in `COMMS.md`, leading to clutter.

To address these, a checkpoint timeout daemon will be implemented as part of the existing comms-processor cycle. This script will mark old PENDING checkpoints as TIMEOUT_DENIED and append cleanup entries for clarity. Additionally, the `COMMS.md` file will be split into three tiers: agent coordination, Clerk/Slipbox pipeline log, and checkpoint lifecycle.

## References
- [Perplexity Export](https://www.perplexity.ai/search/750f5ffc-7dc7-464c-9670-6c1c876181a4)

## Related
- [[djinn-checkpoint-cleanup]] — Implementation details of the checkpoint timeout daemon.
- [[comms-three-tier-split]] — Design and rationale for splitting COMMS.md into three tiers.

---