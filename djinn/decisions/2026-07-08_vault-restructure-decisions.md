# Vault Restructure — Decision Notes
_2026-07-08 — Under 200 words_

**`forge/media/` collision:** The original vault root `forge/` had a `media/` subdirectory. Since `djinn/media/` moves to the top-level `media/` department, the old `forge/media/` is renamed `forge/_legacy-media/` to prevent clobbering. Manual review needed to determine if contents belong in `media/` or `forge/content/`.

**`forge/projects/` vs `djinn/projects/`:** Spec maps `djinn/projects/` → `forge/projects/`. The original vault root `forge/projects/` is handled in the merge phase — if it exists, the bash `merge_dir` function prevents silent overwrites with a conflict warning.

**`djinn/workspaces/osint/`:** Spec says keep in `djinn/workspaces/osint/` — that workspace is OS-level, not AI dev. Left in place.

**Top-level `QUEUE.md` and `ROUTING.md`:** These exist both at vault root and inside `djinn/`. The vault root copies appear to be symlinks or duplicates of `djinn/QUEUE.md` / `djinn/ROUTING.md`. No move applied — flagged for manual dedup.

**`djinn/printer/fleet-capability-matrix.md`:** Also referenced in `djinn/hardware/`. Moved once to `forge/fleet-capability-matrix.md` via Phase 2. The `djinn/hardware/` version moves to `forge/hardware/` in Phase 3 — both end up in `forge/`.

**`personal/` seed:** `djinn/personal/` already contains `academic/`, `db/`, `handlers/`, `modules/`. The full directory moves intact; `djinn/people/` becomes `personal/people/` as a subdirectory.

— Claude
