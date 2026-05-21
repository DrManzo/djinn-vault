---
subject: Djinn Migration
tags: [djinn, migration, backup]
created: 2026-05-21
---

# Migration Manifest — What Lives Where

## Recoverable from Git (GitHub)

Everything in `~/Obsidian/` — vault notes, skills, workflows, comms, decisions, logs.

```bash
git clone https://github.com/DrManzo/djinn-vault.git ~/Obsidian
```

## Recoverable by Re-Running Bootstrap

All binaries, timers, and Ollama models can be reinstalled:

```bash
bash ~/Obsidian/djinn/migration/bootstrap.sh --machine salomon
```

## NOT in Git — Must Transfer Manually

These contain credentials and are intentionally excluded from version control.

| File | Contains | Recovery |
|------|----------|----------|
| `~/.claude/.credentials.json` | Claude Code OAuth tokens | `scp` from other machine, or `claude /login` |
| `~/.openclaw/openclaw.json` | Telegram botToken, Discord token, gateway auth | `scp` from Salomon only |
| `~/.config/djinn/telegram.conf` | BOT_TOKEN + CHAT_ID | Regenerate from openclaw.json (see bootstrap step 9c) |
| `~/.ssh/` | SSH keys | Generate new or restore from backup |
| `~/.openclaw/credentials/` | Pairing tokens | Regenerate via OpenClaw pairing flow |

## Passport Backup

External WD Passport backup of the full vault:

```bash
bash ~/.local/bin/vault-passport-backup
```

Backs up `~/Obsidian/` → `Passport/Obsidian-Backup/` via rsync.
Run before any major hardware change.

## GDrive Sync

Vault is also synced to Google Drive via `rclone bisync` every 2 minutes.
GDrive is a tertiary backup — primary is GitHub.

## Migration Checklist

Use this when moving Djinn to new hardware:

- [ ] Run `vault-passport-backup` on old machine
- [ ] Note current Ollama model list: `ollama list`
- [ ] Back up `~/.openclaw/openclaw.json` to Passport
- [ ] Back up `~/.claude/.credentials.json` to Passport
- [ ] On new machine: `bash ~/Obsidian/djinn/migration/bootstrap.sh`
- [ ] Copy credential files from Passport to new machine
- [ ] Verify: `ollama ps`, `systemctl --user list-timers`, `claude --version`
- [ ] Send test Telegram message: `bash ~/.local/bin/djinn-morning`
- [ ] Update machine IP in `HEARTBEAT.md` and `Djinns-Hub.md`
- [ ] Update `~/.claude/CLAUDE.md` with new machine topology if changed
- [ ] Run first weekly review: `bash ~/.local/bin/djinn-weekly`

## Recovery Time Estimate

| Step | Time |
|------|------|
| Bootstrap script (no models) | ~5 min |
| Ollama always-warm models (qwen2.5:7b + deepseek-r1:7b) | ~10 min |
| Credential file transfer | ~2 min |
| Verify + first heartbeat | ~2 min |
| **Total** | **~20 min** |

On-demand models (phi4:14b, vision) pull lazily on first use.

---

*— Claude*
