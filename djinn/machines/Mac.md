---
title: Machine — Mac
tags: [djinn, machine, mac, hardware]
created: 2026-06-02
updated: 2026-06-02
---

# Machine: Mac

**Callsign:** Mac  
**Network name:** Mac  
**Role:** Daily driver — Claude Code lane, architecture decisions, vault-persistent work, cross-domain synthesis  
**IP:** (local network — check router / `ipconfig getifaddr en0`)  
**Related:** [[Salomon]] | [[HEARTBEAT]] | [[COMMS]]

Changes from this machine are signed: `— Claude`

---

## Hardware

| Component | Spec |
|-----------|------|
| **CPU** | Apple Silicon (M-series) |
| **OS** | macOS |
| **Shell** | zsh |

> Update this table with actual specs once known.

---

## Role in Djinn

This machine is the **Claude Code / premium dev lane**. It does NOT run:
- Ollama locally (connects to Salomon's Ollama at `http://192.168.1.225:11434`)
- OpenClaw gateway
- Telegram/Discord bots (those run on Salomon/Typhon)
- systemd services (macOS uses launchd — automate only what's needed)

It DOES handle:
- Architecture decisions and complex builds via Claude Code
- Vault reads/writes and git push
- djinn-marcus, djinn-gemini, djinn-personal-db CLI tools
- Session reports, build-log, COMMS entries
- End-to-end testing of Claude API integrations (llm.py, djinn-social)

---

## Setup

### Core tools
```bash
brew install git gh python3 jq trash
```

### Vault
```bash
gh auth login
git clone https://github.com/DrManzo/djinn-vault.git ~/Obsidian
```

### Claude Code config
```bash
cp ~/Obsidian/djinn/Claude.md ~/.claude/CLAUDE.md
mkdir -p ~/.openclaw && ln -s ~/Obsidian/djinn/workspace ~/.openclaw/workspace
```

### Config
```bash
mkdir -p ~/.config/djinn
# claude.env, gemini.env, perplexity.env — chmod 600, never git-tracked
echo 'source ~/.config/djinn/claude.env' >> ~/.zshrc
echo 'export OLLAMA_HOST=http://192.168.1.225:11434' >> ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### Python tools
```bash
pip3 install anthropic google-genai requests firecrawl-py
# Pull tools from Salomon:
for tool in djinn-marcus djinn-gemini djinn-personal-db djinn-bugreport djinn-claude; do
  scp drmanzo@192.168.1.225:~/.local/bin/$tool ~/.local/bin/$tool && chmod +x ~/.local/bin/$tool
done
```

---

## Remote Ollama

Salomon exposes Ollama on `0.0.0.0:11434`. Mac connects directly:
```bash
curl http://192.168.1.225:11434/api/tags
```

Set `OLLAMA_HOST=http://192.168.1.225:11434` in shell profile — all Djinn tools respect this env var.

---

## Vault Sync

Same git workflow as Salomon:
```bash
git -C ~/Obsidian pull
git -C ~/Obsidian add -A && git commit -m "..." && git push
```

No rclone GDrive sync needed on Mac — Salomon owns that.

---

## What's NOT Available on Mac

| Feature | Why | Workaround |
|---------|-----|-----------|
| Printer tools | Klipper/Moonraker on local LAN | Send via Telegram/Discord to Salomon |
| Ollama local | Not installed | Remote via `OLLAMA_HOST` |
| systemd timers | macOS uses launchd | Manual runs or launchd agents if needed |
| Discord/Telegram bots | Hosted on Salomon/Typhon | Control via Discord/Telegram as user |

---

*— Claude, 2026-06-02*
