---
title: Bug Report — render.py hardcoded PNG format ignores output extension
system: djinn-blender-render / typhons-forge
severity: medium
status: fixed
date: 2026-06-18
---

# Bug — render.py hardcoded PNG format ignores output extension

**System:** `~/typhons-forge/blender/scripts/render.py`
**Severity:** medium (file saved but with wrong format; wrapper check fails silently)
**Status:** fixed

## Root Cause

render.py hardcoded `file_format = 'PNG'` regardless of the `--out` extension:
```python
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = '/tmp/kraken_cover.jpg'
```

Blender saved `/tmp/kraken_cover.jpg` as a PNG file (wrong bytes, misleading extension). The wrapper then checked `os.path.exists(out_path)` — the file existed (as PNG data), so the file-exists check passed. But earlier in this session, before this bug was isolated, the wrapper was also checking the exit code and reporting failure.

## Symptom

Blender logs `Saved: '/tmp/kraken_cover.jpg'` (success), but the wrapper reports `✗ Render failed`. The file exists on disk but contains PNG data despite the `.jpg` extension.

## Fix

Detect format from output file extension:
```python
ext = os.path.splitext(out_path)[1].lower()
if ext in ('.jpg', '.jpeg'):
    scene.render.image_settings.file_format = 'JPEG'
    scene.render.image_settings.quality = 90
else:
    scene.render.image_settings.file_format = 'PNG'
```

## Rule Learned

Blender does NOT automatically infer output format from the file extension — it only writes what `file_format` says. Always set format explicitly from the caller's intended extension.

*— Claude, 2026-06-18*
