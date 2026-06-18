---
title: Bug Report — BLENDER_EEVEE_NEXT not valid in snap Blender 5.1.2
system: djinn-blender-render / typhons-forge
severity: high
status: fixed
date: 2026-06-18
---

# Bug — BLENDER_EEVEE_NEXT not valid in snap Blender 5.1.2

**System:** `~/typhons-forge/blender/scripts/render.py`
**Severity:** high (render completely non-functional on first run)
**Status:** fixed

## Root Cause

render.py set the render engine as:
```python
scene.render.engine = 'BLENDER_EEVEE_NEXT'
```

This is the correct engine name in Blender 4.2+ in official builds, but the snap package of Blender 5.1.2 on Salomon still uses the legacy name `BLENDER_EEVEE`. The valid enum values in this build are:
```
('BLENDER_EEVEE', 'BLENDER_WORKBENCH', 'CYCLES')
```

## Symptom

```
TypeError: bpy_struct: item.attr = val: enum "BLENDER_EEVEE_NEXT" not found in ('BLENDER_EEVEE', 'BLENDER_WORKBENCH', 'CYCLES')
```

## Fix

```python
# Before
scene.render.engine = 'BLENDER_EEVEE_NEXT' if args.engine == 'eevee' else 'CYCLES'

# After
scene.render.engine = 'BLENDER_EEVEE' if args.engine == 'eevee' else 'CYCLES'
```

## Rule Learned

Snap packages can lag official release naming. When writing Blender Python API code, verify engine enum names against the actual installed binary — not documentation. Run `python -c "import bpy; print(bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items.keys())"` headless to get ground truth.

*— Claude, 2026-06-18*
