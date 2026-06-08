---
subject: Agent Task Queue
updated: 2026-06-07
---

# QUEUE.md — Djinn Task Queue

Active tasks pending assignment or completion.
Agents append to this file. Javier sets priorities.

## Format

    TASK-NNN | [lane] | [agent] | [priority] | description

## Active Queue

- [ ] TASK-001 | all-lanes | all | HIGH | API reduction: implement top 20 script replacements (session 2026-06-07)

- [ ] TASK-005 | mobile | Javier | MEDIUM | Create iPhone Shortcut "Send to Djinn" — Share Sheet trigger, asks session name + agent, POSTs to Salomon Flask endpoint (port 8765) via Tailscale/local network.

- [ ] TASK-006 | desktop | Javier | MEDIUM | Add iMac Safari/Chrome bookmarklet — grabs page innerText, prompts session + agent, POSTs to Salomon Flask endpoint. One drag to bookmarks bar.

- [ ] TASK-007 | gemini-lane | Gemini | MEDIUM | Establish Gemini session-end GDrive write convention — at end of each session Gemini writes summary Doc to Typhons-Forge/gemini/reports/gemini-session-YYYY-MM-DD.md. Salomon rclone picks up on 2-min cycle.

- [ ] TASK-008 | infra | Salomon | LOW | Wire Firefox AI Chat Exporter output folder to ~/djinn-inbox/ drop target via SSH/SFTP mount or Tailscale file drop. Laptop-only, lowest priority since Flask endpoint covers all devices.

- [ ] TASK-009 | architecture | Claude | HIGH | Design bug hunter agent for Djinn — spec a proactive, automated vulnerability detection pipeline to sit alongside the existing djinn-bugreport CLI. Must include: (1) Python static analysis via bandit on every commit, (2) dependency audit via pip-audit on cron, (3) secrets scanning on staged files pre-push, (4) known-error regex triage replacing LLM error log reads (feeds into API reduction TASK-001), (5) structured output to djinn/logs/bugs.md and Telegram alert. Claude owns architecture. Salomon deploys. No LLM in the detection path — pure deterministic scanning. Marcus note: vault currently has zero automated scanning. djinn-bugreport is manual-only. This is a real gap.

## Completed

- [x] TASK-002 | infra | Salomon | 2026-06-07 | Flask inbox endpoint DEPLOYED — djinn-flask-inbox running on 0.0.0.0:8765, confirmed active by Salomon.
- [x] TASK-003 | infra | Salomon | 2026-06-07 | inbox-watcher.service DEPLOYED — inotifywait loop active, fires marcus-sync.py on file drops, confirmed active by Salomon.
- [x] TASK-004 | infra | Salomon | 2026-06-07 | marcus-sync.py DEPLOYED — script at ~/.local/bin/marcus-sync.py, confirmed active by Salomon.
