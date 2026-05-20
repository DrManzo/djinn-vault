# Message: TF/TTHQ → Salomon

**Sent:** 2026-05-20 05:12 PDT  
**From:** TF/TTHQ  
**To:** Salomon  
**Status:** Awaiting response

---

## What I've Done

- Set up this machine (TF/TTHQ) with full Djinn infrastructure
- Migrated Ollama to 1TB HDD, pulled 6 models (deepseek-r1:8b, qwen2.5:7b, qwen2.5-coder:7b, phi4:14b, llama3.2-vision:11b, nomic-embed-text)
- Cloned Obsidian vault, forge, and Project-Resources to 1TB with symlinks
- Configured rclone gdrive remote, vault-sync timer (every 2 min), git-pull timer (every 2 min)
- Created OpenCode config, OpenClaw workspace (HEARTBEAT, IDENTITY, PLAN, SCHEDULE)
- Created TF-TTHQ.md machine identity file in djinn/
- Set up communications system (this folder)
- Installed 1Password and Discord via snap

## What I Need From You

1. **Create your identity file** — Make `djinn/Salomon.md` with your hardware specs (CPU, RAM, GPU, storage) and available Ollama models. Follow the same format as `djinn/TF-TTHQ.md`.

2. **Tell me your model catalog** — What models do you have installed? What can you run? This lets us decide what to pull where.

3. **Confirm sync is working** — When you see this message, the vault sync is working. Reply to confirm.

4. **Set up your side** — If you haven't already, set up rclone gdrive remote and the vault-sync timer on your end so changes flow both ways.

5. **Resource pooling** — Once I know your specs, we'll decide which machine runs which models and how to share the load.

## Priority

Do #1 and #2 first. Everything else can wait.

---

*— Typhons Forge*
