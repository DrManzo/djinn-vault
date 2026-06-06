Heartbeat — Orin
Last beat: 2026-06-06 00:00 UTC — manually updated
Machine: Orin (192.168.1.176)
Status: Online — ethernet, Ollama live

Hardware:
  CPU: Intel 8-core
  RAM: 40GB
  Storage: 2TB
  GPU: Intel integrated (CPU inference only)
  OS: macOS

Ollama models (live):
  llama3.3:70b     — 42.5GB — primary, best local model in fleet
  phi4:14b         — 9.1GB  — reports, summaries
  nomic-embed-text — 0.3GB  — embeddings

Pulling (background):
  deepseek-r1:14b, qwen2.5:32b, qwen2.5-coder:7b

Notes: Always-on, ethernet, static IP 192.168.1.176. CPU inference only (no Metal on Intel).
Bootstrap doc: djinn/onboarding/orin-bootstrap.md
