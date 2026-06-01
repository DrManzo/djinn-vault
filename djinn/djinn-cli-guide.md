# Djinn CLI Guide

## Quick Start

### Talk to Djinn (main model — qwen3.6:latest)
```bash
openclaw agent --agent main -m "your message here"
```

### Talk to Coder agent (qwen2.5-coder:7b)
```bash
openclaw agent --agent coder -m "write a script that..."
```

### Interactive terminal UI
```bash
openclaw tui
```

### Web Dashboard
Open Firefox → `http://127.0.0.1:18789/`

Token: `[rotated — see openclaw.json]`

---

## Gateway Management

```bash
# Status
systemctl --user status openclaw-gateway

# Restart
systemctl --user restart openclaw-gateway

# Stop
systemctl --user stop openclaw-gateway

# Start
systemctl --user start openclaw-gateway

# Logs (live)
journalctl --user -u openclaw-gateway -f
```

---

## Devices & Approvals

```bash
# List paired devices
openclaw devices list

# Approve a new browser/device
openclaw devices approve <request-id>
```

---

## Status & Diagnostics

```bash
# Full gateway status
openclaw status

# Quick health check
curl http://127.0.0.1:18789/health
```

---

## Docker (Djinn container)

```bash
# Start
bash ~/forge/projects/djinn-core/scripts/start.sh

# Stop
bash ~/forge/projects/djinn-core/scripts/stop.sh

# Attach (interactive terminal inside container)
bash ~/forge/projects/djinn-core/scripts/attach.sh

# Logs
docker logs -f djinn
```

---

## Cache & Sessions

```bash
# Clear chat history
rm -f ~/.openclaw/agents/main/sessions/*

# Clear all caches
rm -rf ~/.openclaw/sessions ~/.openclaw/tasks ~/.openclaw/tui ~/.openclaw/logs/*
```

---

## Config File

Location: `~/.openclaw/openclaw.json`

```bash
# View current config
openclaw config list

# Set a config value
openclaw config set <path> <value>
```
