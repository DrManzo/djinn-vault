---
title: Bug Report — pyembree hasattr false positive raises on access
system: djinn-finalize / TASK-080
severity: medium
status: fixed
date: 2026-06-18
---

# Bug — pyembree hasattr false positive raises on access

**System:** TASK-080 Kraken pipe diagnostic script (`finalize_kraken_pipe.py`)
**Severity:** medium
**Status:** fixed

## Root Cause

`hasattr(trimesh.ray, "ray_pyembree")` returned `True` even though the module is not installed. The attribute exists on the namespace but accessing it triggers a deferred import that raises `ModuleNotFoundError: No module named 'embreex'`. `hasattr()` only catches `AttributeError`, not import errors, so the check was meaningless.

## Symptom

```
ModuleNotFoundError: No module named 'embreex'
  at: trimesh.ray.ray_pyembree.RayMeshIntersector(mesh)
```

## Fix

Replaced `hasattr` guard with `try/except`:

```python
# Before
if hasattr(trimesh.ray, "ray_pyembree"):
    intersector = trimesh.ray.ray_pyembree.RayMeshIntersector(mesh)
else:
    intersector = mesh.ray

# After
try:
    intersector = trimesh.ray.ray_pyembree.RayMeshIntersector(mesh)
except Exception:
    intersector = mesh.ray
```

## Rule Learned

`hasattr()` only catches `AttributeError`. For lazy-import modules (common in scientific Python: trimesh, Open3D, etc.), always guard with `try/except ImportError` or `try/except Exception`. `hasattr` is not safe for import-gated attributes.

*— Claude, 2026-06-18*
