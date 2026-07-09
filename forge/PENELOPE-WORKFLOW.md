---
title: Penelope Print Workflow — Standard Process
tags: [djinn, penelope, printer, workflow]
updated: 2026-06-20
---

# Penelope Print Workflow — Standard

This is the standard process for every Penelope print job. Follow in order.

---

## 1. Apply Maker's Mark

Every final print gets the mark before slicing.

```bash
djinn-model-mark /path/to/file.stl --output /path/to/file-marked.stl
```

**Hollow models:** check inner radius first, adjust `--size` and/or `--x`/`--y` offset so the mark lands on wall material. Use the preview render to confirm before proceeding.

Default: `--size 20 --depth 0.5` centered (no offset) works for solid-bottom models.

---

## 2. Slice with OrcaSlicer

```bash
MACHINE="Creality Ender-3 Pro 0.4 nozzle"
OUTPUT_DIR="$HOME/.local/share/forge/gcode"

/opt/orca-slicer/AppRun \
    --load-settings \
        "/opt/orca-slicer/resources/profiles/Creality/machine/${MACHINE}.json;${HOME}/Obsidian/djinn/printer/forge-slicer/profiles/process/Penelope-Standard.json" \
    --load-filaments "${HOME}/Obsidian/djinn/printer/forge-slicer/profiles/filament/Penelope-PLA.json" \
    --slice 0 \
    --outputdir "$OUTPUT_DIR" \
    /path/to/file-marked.stl
```

**With supports:**
```bash
    # Add before --slice:
    --load-settings "...machine.json;.../Penelope-Standard-Supports.json" \
```

**Multiple copies:** pass the STL multiple times: `file.stl file.stl file.stl`

Output lands at `~/.local/share/forge/gcode/plate_1.gcode`

---

## 3. Upload and Print

```bash
cp ~/.local/share/forge/gcode/plate_1.gcode \
   ~/.local/share/forge/gcode/penelope-<jobname>.gcode

djinn-penelope upload ~/.local/share/forge/gcode/penelope-<jobname>.gcode
djinn-penelope print penelope-<jobname>.gcode
```

---

## 4. Monitor

```bash
djinn-penelope status     # state, temps, progress
djinn-penelope files      # what's on the printer
djinn-penelope cancel     # stop if needed
```

OctoPrint web UI: `http://localhost:5001` (user: `djinn`, pass: `djinnprint`)

---

## Profile Reference

| Profile | Use |
|---------|-----|
| `Penelope-Standard` | Default — 0.2mm, 20% grid, 3 walls, no brim |
| `Penelope-Standard-Supports` | Same + supports enabled (45° threshold) |
| `Penelope-Production` | 0.2mm, 25% gyroid, 4 walls, 8mm brim |
| `Penelope-PLA` | Filament — 210°C, 60°C bed, 5.5mm retraction (Bowden) |

**Key constraints:**
- Build volume: 220×220×250mm — check fit before routing
- Bowden extruder: retraction 5.5mm (profiles handle this automatically)
- 8-bit board: speeds capped at 40/50/60mm/s — do not port Calliope speeds
- No pressure advance, no input shaping

---

*— Claude, 2026-06-20*
