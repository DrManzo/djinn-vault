# Skill: djinn-morning

**Owner:** Salomon (OpenClaw)  
**Purpose:** 8 AM Telegram prompt to Javier with carry-forward + system health  
**Status:** ⏳ Blocked — needs Telegram bot token  

## Triggers

- systemd timer: 8 AM daily (via OpenClaw native Telegram channel)
- Manual: `bash ~/.local/bin/djinn-morning`

## Inputs

- `~/.config/djinn/telegram.conf` — BOT_TOKEN + CHAT_ID
- `~/.openclaw/workspace/PLAN.md` — carry-forward items
- `~/Obsidian/djinn/communications/HEARTBEAT.md` — Salomon health
- `~/Obsidian/djinn/communications/HEARTBEAT-typhon.md` — Typhon health

## Steps

1. Read telegram.conf for BOT_TOKEN + CHAT_ID
2. Pull latest vault: `git -C ~/Obsidian pull --quiet`
3. Extract carry-forward items from OpenClaw PLAN.md
4. Extract Salomon/Typhon health from heartbeats
5. Build Markdown message with date, carry-forward, health status
6. Send via Telegram Bot API: `POST https://api.telegram.org/bot${TOKEN}/sendMessage`

## Outputs

- Telegram message sent to Javier
- stdout: success/failure

## Dependencies

- `curl` — Telegram Bot API call
- `~/.config/djinn/telegram.conf` — **blocked until Javier provides token**
- OpenClaw Telegram channel enabled (already done)

## Related

- OpenClaw handles native 8 AM Telegram prompt via built-in Telegram channel
- `djinn-morning` is a fallback/alternative path

---

*— Claude*
