Heartbeat — Orin
Last beat: 2026-06-06 02:00 UTC — manually updated
Machine: Orin (192.168.1.176)
Status: Online — ethernet, Ollama live, vault cloned, djinn tools installed

Hardware:
  CPU: Intel 8-core
  RAM: 40GB
  Storage: 2TB
  GPU: Intel integrated (CPU inference only)
  OS: macOS 15.7.8

Ollama models (live):
  llama3.3:70b          — 42.5GB — best local model in fleet
  qwen2.5-coder:32b     — 19.9GB — large coder model
  phi4:14b              — 9.1GB  — reports, summaries
  nomic-embed-text      — 0.3GB  — embeddings

Djinn tools installed:
  ~/.local/bin/djinn-local-report
  ~/.local/bin/djinn-comms-auto

Vault: ~/Obsidian (cloned, hourly cron pull)
Git user: Orin <orin@djinn.local>
OLLAMA_HOST: http://localhost:11434 (local)
Remote access: SSH enabled (javiermanzo@192.168.1.176)

Notes: Always-on, ethernet, static IP 192.168.1.176. CPU inference only (no Metal on Intel).
Bootstrap doc: djinn/onboarding/orin-bootstrap.md
