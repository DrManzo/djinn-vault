# Heartbeat — Tab S7 FE

**Last beat:** 2026-06-07 17:52:00 UTC  
**Machine:** Tab S7 FE (100.81.22.111)  
**Status:** Alive — bootstrapped this session

## System

- **Hardware:** Samsung Galaxy Tab S7 FE (SM-T738U)
- **OS:** Android 14 + Termux + Ubuntu 22.04 (proot-distro)
- **Arch:** aarch64
- **Tailscale IP:** 100.81.22.111
- **Tailscale hostname:** javiers-tab-s7-fe
- **SSH:** port 8022 (Termux sshd) — boot-persistent via ~/.termux/boot/start-sshd.sh

## Djinn Environment

- **Termux:** proot-distro, git, openssh, python, curl installed
- **Ubuntu (proot):** Ubuntu 22.04 aarch64 — git, curl, python3, build-essential, zsh, neovim, tmux, jq
- **Vault:** ~/Obsidian inside Ubuntu proot — cloned from bundle, remote → GitHub, credentials via ~/.git-credentials
- **Gateway mode:** Standard (no autonomous pushes to main)
- **Session.json:** present, mode=standard, agent=tablet

## Quick Access

```bash
# From Salomon:
ssh -p 8022 100.81.22.111

# Inside Termux:
proot-distro login ubuntu       # enter Ubuntu shell
vault                           # → cd ~/Obsidian + bash (alias)
ubuntu                          # → proot-distro login ubuntu (alias)

# Pull latest vault inside Ubuntu:
git -C ~/Obsidian pull origin main
```

## Bootstrapped

- **Date:** 2026-06-07
- **By:** Claude
- **Method:** ADB (USB) + Tailscale SSH
