#!/usr/bin/env bash
# vault-restructure.sh — Djinn Vault Department Restructure
# Run from ~/Obsidian/
# Usage: bash djinn/migration/scripts/vault-restructure.sh [--dry-run]

set -euo pipefail
shopt -s nullglob

VAULT="$HOME/Obsidian"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

move() {
    local src="$1" dst="$2"
    if [[ ! -e "$VAULT/$src" ]]; then
        echo "  SKIP (not found): $src"
        return
    fi
    echo "  mv $src → $dst"
    if [[ "$DRY_RUN" == false ]]; then
        mkdir -p "$VAULT/$(dirname "$dst")"
        mv "$VAULT/$src" "$VAULT/$dst"
    fi
}

merge_dir() {
    local src="$1" dst="$2"
    if [[ ! -d "$VAULT/$src" ]]; then
        echo "  SKIP (not found): $src"
        return
    fi
    echo "  MERGE $src → $dst"
    if [[ "$DRY_RUN" == false ]]; then
        mkdir -p "$VAULT/$dst"
        find "$VAULT/$src" -mindepth 1 -maxdepth 1 | while read -r item; do
            name=$(basename "$item")
            if [[ -e "$VAULT/$dst/$name" ]]; then
                echo "    CONFLICT: $dst/$name exists — skipping $src/$name"
            else
                mv "$item" "$VAULT/$dst/$name"
            fi
        done
    fi
}

echo "=== Djinn Vault Restructure ==="
[[ "$DRY_RUN" == true ]] && echo "=== DRY RUN — no files will be moved ==="
echo ""

# ── PHASE 1: Create department roots ─────────────────────────────────────────
echo "Phase 1: Creating department roots"
for dept in forge ai media writing personal hellhound; do
    echo "  mkdir -p $dept"
    [[ "$DRY_RUN" == false ]] && mkdir -p "$VAULT/$dept"
done

# ── PHASE 2: djinn/printer/ subdirs → forge/ ─────────────────────────────────
echo ""
echo "Phase 2: djinn/printer/ subdirs → forge/"
for subdir in active agent archive backup calibration \
    calliope-config-backup-2026-06-05 commissions completed config \
    content design-process discord docs failures feedback finished-prints \
    forge-slicer library originals planning prints process queue shop \
    snapshots telegram tools traces-archive workflows; do
    move "djinn/printer/$subdir" "forge/$subdir"
done

# djinn/printer/forge/ conflicts with vault-root forge/ — rename
if [[ -d "$VAULT/djinn/printer/forge" ]]; then
    echo "  djinn/printer/forge/ → forge/_printer-forge/ (conflict avoidance)"
    [[ "$DRY_RUN" == false ]] && mv "$VAULT/djinn/printer/forge" "$VAULT/forge/_printer-forge"
fi

# ── PHASE 3: djinn/printer/ .md files → forge/ ───────────────────────────────
echo ""
echo "Phase 3: djinn/printer/ root .md files → forge/"
for f in "$VAULT/djinn/printer/"*.md; do
    [[ -f "$f" ]] || continue
    fname=$(basename "$f")
    if [[ -f "$VAULT/forge/$fname" ]]; then
        echo "  SKIP (exists in forge/): $fname"
    else
        echo "  mv djinn/printer/$fname → forge/$fname"
        [[ "$DRY_RUN" == false ]] && mv "$f" "$VAULT/forge/$fname"
    fi
done

# ── PHASE 4: djinn/hardware/ → forge/hardware/ ───────────────────────────────
echo ""
echo "Phase 4: djinn/hardware/ → forge/hardware/"
move "djinn/hardware" "forge/hardware"

# ── PHASE 5: djinn/finance/ → forge/finance/ ─────────────────────────────────
echo ""
echo "Phase 5: djinn/finance/ → forge/finance/"
move "djinn/finance" "forge/finance"

# ── PHASE 6: djinn/typhons-forge/ → forge/typhons-forge/ ─────────────────────
echo ""
echo "Phase 6: djinn/typhons-forge/ → forge/typhons-forge/"
move "djinn/typhons-forge" "forge/typhons-forge"

# ── PHASE 7: djinn/projects/ → forge/projects/ (merge) ──────────────────────
echo ""
echo "Phase 7: djinn/projects/ → forge/projects/"
if [[ -d "$VAULT/djinn/projects" ]] && [[ -d "$VAULT/forge/projects" ]]; then
    merge_dir "djinn/projects" "forge/projects"
    [[ "$DRY_RUN" == false ]] && rmdir "$VAULT/djinn/projects" 2>/dev/null || true
else
    move "djinn/projects" "forge/projects"
fi

# ── PHASE 8: vault-root forge/ conflict — rename media/ before media dept ────
echo ""
echo "Phase 8: forge/media/ → forge/_legacy-media/ (preserves new top-level media/)"
if [[ -d "$VAULT/forge/media" ]]; then
    echo "  mv forge/media → forge/_legacy-media"
    [[ "$DRY_RUN" == false ]] && mv "$VAULT/forge/media" "$VAULT/forge/_legacy-media"
else
    echo "  SKIP (forge/media/ not found)"
fi

# ── PHASE 9: djinn/media/ → media/ ──────────────────────────────────────────
echo ""
echo "Phase 9: djinn/media/ → media/"
for subdir in hashtag-bank logos posts projects; do
    move "djinn/media/$subdir" "media/$subdir"
done
for f in "$VAULT/djinn/media/"*.md; do
    fname=$(basename "$f")
    echo "  mv djinn/media/$fname → media/$fname"
    [[ "$DRY_RUN" == false ]] && mv "$f" "$VAULT/media/$fname"
done

# ── PHASE 10: djinn/social/ → media/analytics/ ───────────────────────────────
echo ""
echo "Phase 10: djinn/social/ → media/analytics/"
move "djinn/social" "media/analytics"

# ── PHASE 11: djinn/research/ → ai/ ──────────────────────────────────────────
echo ""
echo "Phase 11: djinn/research/ → ai/"
for subdir in architecture claude gemini marcus; do
    move "djinn/research/$subdir" "ai/$subdir"
done
for f in "$VAULT/djinn/research/"*.md; do
    fname=$(basename "$f")
    echo "  mv djinn/research/$fname → ai/$fname"
    [[ "$DRY_RUN" == false ]] && mv "$f" "$VAULT/ai/$fname"
done

# ── PHASE 12: djinn/workspaces/ splits ───────────────────────────────────────
echo ""
echo "Phase 12: djinn/workspaces/ → ai/workspaces/"
move "djinn/workspaces/mobile-forge"   "ai/workspaces/mobile-forge"
move "djinn/workspaces/typhon-windows" "ai/workspaces/typhon-windows"
# writing/ handled in Phase 14 | osint/ STAYS per decisions doc

# ── PHASE 13: djinn/hellhound/ → hellhound/ (merge) ─────────────────────────
echo ""
echo "Phase 13: djinn/hellhound/ → hellhound/ (merge)"
for subdir in gates incidents reports timeline; do
    move "djinn/hellhound/$subdir" "hellhound/$subdir"
done
for f in "$VAULT/djinn/hellhound/"*.md; do
    fname=$(basename "$f")
    echo "  mv djinn/hellhound/$fname → hellhound/$fname"
    [[ "$DRY_RUN" == false ]] && mv "$f" "$VAULT/hellhound/$fname"
done

# ── PHASE 14: djinn/writing/ → writing/ ──────────────────────────────────────
echo ""
echo "Phase 14: djinn/writing/ → writing/"
for subdir in drafts notes outlines research; do
    move "djinn/writing/$subdir" "writing/$subdir"
done
for f in "$VAULT/djinn/writing/"*.md; do
    fname=$(basename "$f")
    echo "  mv djinn/writing/$fname → writing/$fname"
    [[ "$DRY_RUN" == false ]] && mv "$f" "$VAULT/writing/$fname"
done

# ── PHASE 15: djinn/workspaces/writing/ → writing/workspace/ ────────────────
echo ""
echo "Phase 15: djinn/workspaces/writing/ → writing/workspace/"
move "djinn/workspaces/writing" "writing/workspace"

# ── PHASE 16: djinn/personal/ → personal/ ────────────────────────────────────
echo ""
echo "Phase 16: djinn/personal/ → personal/"
move "djinn/personal" "personal"

# ── PHASE 17: djinn/people/ → personal/people/ ───────────────────────────────
echo ""
echo "Phase 17: djinn/people/ → personal/people/"
move "djinn/people" "personal/people"

# ── PHASE 18: Stray printer manuals at djinn/ root ───────────────────────────
echo ""
echo "Phase 18: djinn/ root printer manuals → forge/"
for f in PENELOPE-MANUAL.md PENELOPE-SATURDAY-RUNBOOK.md; do
    if [[ -f "$VAULT/djinn/$f" ]]; then
        if [[ -f "$VAULT/forge/$f" ]]; then
            echo "  SKIP djinn/$f (already in forge/)"
        else
            echo "  mv djinn/$f → forge/$f"
            [[ "$DRY_RUN" == false ]] && mv "$VAULT/djinn/$f" "$VAULT/forge/$f"
        fi
    fi
done

# ── PHASE 19: Prune now-empty djinn/ subdirs ──────────────────────────────────
echo ""
echo "Phase 19: Pruning empty djinn/ subdirs"
for subdir in printer hardware finance typhons-forge projects media social \
    research hellhound writing personal people; do
    if [[ -d "$VAULT/djinn/$subdir" ]]; then
        if [[ "$DRY_RUN" == false ]]; then
            rmdir "$VAULT/djinn/$subdir" 2>/dev/null \
                && echo "  Pruned: djinn/$subdir" \
                || echo "  KEPT (not empty): djinn/$subdir — check manually"
        else
            echo "  Would prune (if empty): djinn/$subdir"
        fi
    fi
done

echo ""
echo "=== DONE ==="
[[ "$DRY_RUN" == true ]] && echo "=== DRY RUN complete. Run without --dry-run to apply. ===" || echo "Next: run update-links.py --dry-run"
