# Runbooks

Step-by-step operational playbooks for each primary target type.

| Runbook | Target Type | Primary Agent | Avg Phases |
|---|---|---|---|
| [PERSON-OP.md](PERSON-OP.md) | Individual person | RECON → SOCIAL → VISUAL → NETPROBE → ARCHIVE → TREND → CORRELATOR | 7 |
| [ORG-OP.md](ORG-OP.md) | Organization / company | RECON → VISUAL → NETPROBE → SOCIAL → ARCHIVE → TREND → CORRELATOR | 7 |
| [DOMAIN-OP.md](DOMAIN-OP.md) | Domain / IP / infrastructure | NETPROBE (primary) → ARCHIVE → CORRELATOR | 9 |

## How to Use

1. Identify your target type
2. Open the corresponding runbook
3. Start at Phase 0 — collect seed data first, always
4. Follow phases in order — each phase informs the next
5. Record findings at each phase checkpoint in `targets/<slug>.md`
6. Run SCRIBE at the end to produce the final report

## Gateway Tier Reminder

Every runbook entry-point is **Tier 1 (passive)**. Escalation triggers are documented within each runbook phase. When in doubt, stop and confirm with operator before proceeding.

---

*Runbooks — OSINT / Djinn system*
