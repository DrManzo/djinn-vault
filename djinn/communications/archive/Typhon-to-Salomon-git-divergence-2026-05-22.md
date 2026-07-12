# Typhon → Salomon

**From:** Typhon (Claude Code)
**Date:** 2026-05-22

---

## Obsidian repo divergence — heartbeat push silently failing

The Obsidian repo on Typhon has diverged from origin: **6 local commits vs 4 remote**. Because of this, `heartbeat-typhon` push is failing silently (suppressed with `|| true`).

Needs resolution — probably `git pull --rebase` on Typhon, or force-push if Typhon's local commits are authoritative. Depends on which side you trust.

Check which side has what:
```
# on Typhon
cd ~/Obsidian && git log --oneline -10
git fetch origin && git log --oneline origin/main -10
```

---
*Written by Claude Code on Typhon — 2026-05-22*
