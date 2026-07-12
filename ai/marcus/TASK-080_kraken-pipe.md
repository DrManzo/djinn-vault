# TASK-080 — Kraken Proxy Pipe Finalization Diagnostic

**Model:** `/home/drmanzo/Downloads/kraken-typhons-forge/Kraken_pipe.stl`
**Python:** `/home/drmanzo/.venvs/djinn-orchestrator/bin/python3.11`
**Script name:** `finalize_kraken_pipe.py`

---

## Diagnostic Approach

### Check 1 — Mouthpiece Opening (Mantle Tip)

The Kraken's mantle tip is the topmost point of the model (maximum Z). We fire a single ray **downward** (direction `[0, 0, -1]`) from a point slightly above the tip, aimed at the XY centroid of the tip area. If the ray's **first intersection** with the mesh is within a small epsilon of the top-most Z, the tip is **capped** (the first thing the ray hits is a roof face). If the ray passes through open air before hitting an interior wall, or hits nothing at all, the tip is **OPEN**. We report the Z coordinate of the first hit for context.

We also fire a **second ray upward** (`[0, 0, +1]`) from just inside the cup floor (cup center XY, Z = cup_floor + 1mm). If that ray exits through the top without hitting a face, the channel is unobstructed from below upward.

### Check 2 — Vapor Path Continuity

A functional vapor path requires unobstructed void space connecting the cup interior (Z ≈ 1.69mm) to the mouthpiece opening at the top. We use a **vertical ray fan**: fire N rays upward from points arranged on a small circle (r = 5mm) around the cup center XY, originating at `Z = cup_floor + 2mm`. For each ray, we count mesh intersections. An **even** intersection count means the ray exits the mesh (open path). An **odd** count means the ray terminates inside a wall (blocked). We report the fraction of rays that are clear and flag BLOCKED with the Z of first blockage if any ray terminates inside.

We also fire a **single axial ray** straight up from cup center. This is the primary vapor axis; if it's clear, path is functionally open.

### Check 3 — Wall Thickness at Cup Zone (Z = 0–10mm)

We sample cross-section slices at several Z heights in the cup zone (Z = 1, 3, 5, 7, 10mm). For each slice, `trimesh.intersections.mesh_plane()` returns line segments (the mesh/plane intersection). We reconstruct the polygons with Shapely. For each polygon ring, wall thickness is estimated by computing the **minimum distance between the outer boundary and any inner boundary** (if a hollow section exists), or by comparing the polygon to the expected 38.7mm circle and estimating the thinnest cross-section using the inscribed-circle approach: for each boundary point, find the nearest point on any other boundary and record the distance. We report the global minimum wall thickness and its XYZ location.

---

## Script

```python
#!/usr/bin/env python3.11
"""
finalize_kraken_pipe.py
TASK-080 — Kraken Proxy Pipe Diagnostic
Diagnosis only — no modifications applied.
Run with: /home/drmanzo/.venvs/djinn-orchestrator/bin/python3.11 finalize_kraken_pipe.py
"""

import numpy as np
import trimesh
import sys
import time
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
STL_PATH = Path("/home/drmanzo/Downloads/kraken-typhons-forge/Kraken_pipe.stl")
CUP_CENTER_XY = np.array([-1.2, -8.9])
CUP_FLOOR_Z = 1.69
MIN_WALL_MM = 1.2
CUP_DIAMETER = 38.7

# ── Load ─────────────────────────────────────────────────────────────────────
t0 = time.time()
print(f"[INFO] Loading mesh: {STL_PATH}")
mesh = trimesh.load(str(STL_PATH), force="mesh")
print(f"[INFO] Mesh loaded: {len(mesh.faces):,} faces, {len(mesh.vertices):,} vertices")
print(f"[INFO] Bounds: {mesh.bounds}")

bounds_min, bounds_max = mesh.bounds
model_top_z = bounds_max[2]
model_bot_z = bounds_min[2]

# Build ray intersector once (BVH — fast for organic meshes)
intersector = trimesh.ray.ray_pyembree.RayMeshIntersector(mesh) \
    if hasattr(trimesh.ray, "ray_pyembree") else mesh.ray

print(f"[INFO] Mesh top Z = {model_top_z:.3f}mm, bottom Z = {model_bot_z:.3f}mm")

# ════════════════════════════════════════════════════════════════════════════
# CHECK 1 — MOUTHPIECE OPENING
# ════════════════════════════════════════════════════════════════════════════
print("\n── CHECK 1: Mouthpiece (mantle tip) ──────────────────────────────────")

# Identify tip centroid XY: use the top 2mm of the mesh
tip_mask = mesh.vertices[:, 2] > (model_top_z - 2.0)
tip_verts = mesh.vertices[tip_mask]
tip_xy = tip_verts[:, :2].mean(axis=0) if len(tip_verts) > 0 else np.array([0.0, 0.0])
tip_z = model_top_z

print(f"[INFO] Tip centroid XY estimated: ({tip_xy[0]:.2f}, {tip_xy[1]:.2f}), Z = {tip_z:.3f}mm")

# Ray: from above, fire downward into tip
ray_origin_top = np.array([[tip_xy[0], tip_xy[1], tip_z + 5.0]])
ray_dir_down = np.array([[0.0, 0.0, -1.0]])

locs_top, ray_idx_top, face_idx_top = intersector.intersects_location(
    ray_origin_top, ray_dir_down, multiple_hits=True
)

mouthpiece_status = "UNKNOWN"
mouthpiece_z = None

if len(locs_top) == 0:
    mouthpiece_status = "OPEN"
    mouthpiece_z = tip_z
    print(f"[RESULT] No mesh hit from above — tip area appears OPEN")
else:
    # Sort hits by Z descending (highest first = closest to our ray origin)
    sorted_hits = locs_top[np.argsort(locs_top[:, 2])[::-1]]
    first_hit_z = sorted_hits[0, 2]
    gap = tip_z - first_hit_z

    if gap < 0.5:
        # First hit is very close to the top surface — likely a cap face
        mouthpiece_status = "CAPPED"
        mouthpiece_z = first_hit_z
        print(f"[RESULT] First hit at Z={first_hit_z:.3f}mm (gap={gap:.3f}mm) — tip appears CAPPED")
    else:
        mouthpiece_status = "OPEN"
        mouthpiece_z = first_hit_z
        print(f"[RESULT] First interior hit at Z={first_hit_z:.3f}mm — tip appears OPEN (gap={gap:.3f}mm)")

# Secondary check: ray upward from cup floor toward tip
ray_origin_cup = np.array([[CUP_CENTER_XY[0], CUP_CENTER_XY[1], CUP_FLOOR_Z + 1.0]])
ray_dir_up = np.array([[0.0, 0.0, 1.0]])

locs_up, _, _ = intersector.intersects_location(
    ray_origin_cup, ray_dir_up, multiple_hits=True
)
if len(locs_up) == 0:
    print(f"[INFO] Upward axial ray from cup: no hits (fully open channel toward top)")
else:
    hits_z = sorted(locs_up[:, 2].tolist())
    print(f"[INFO] Upward axial ray intersections at Z = {[f'{z:.2f}' for z in hits_z]}")

# ════════════════════════════════════════════════════════════════════════════
# CHECK 2 — VAPOR PATH CONTINUITY
# ════════════════════════════════════════════════════════════════════════════
print("\n── CHECK 2: Vapor path (cup → mouthpiece) ────────────────────────────")

N_RAYS = 16
angles = np.linspace(0, 2 * np.pi, N_RAYS, endpoint=False)
fan_radius = 5.0  # mm, within cup interior
ray_start_z = CUP_FLOOR_Z + 2.0

fan_origins = np.column_stack([
    CUP_CENTER_XY[0] + fan_radius * np.cos(angles),
    CUP_CENTER_XY[1] + fan_radius * np.sin(angles),
    np.full(N_RAYS, ray_start_z)
])
fan_dirs = np.tile([0.0, 0.0, 1.0], (N_RAYS, 1))

blocked_rays = []
clear_rays = []
first_blockage_z = None

for i in range(N_RAYS):
    locs_i, _, _ = intersector.intersects_location(
        fan_origins[i:i+1], fan_dirs[i:i+1], multiple_hits=True
    )
    n_hits = len(locs_i)
    # Even hits = ray exits mesh (open). Odd hits = ray ends inside mesh (blocked).
    if n_hits % 2 == 1:
        block_z = float(locs_i[np.argsort(locs_i[:, 2])[0], 2])
        blocked_rays.append((i, block_z))
        if first_blockage_z is None or block_z < first_blockage_z:
            first_blockage_z = block_z
    else:
        clear_rays.append(i)

# Also check center axial ray for path
locs_axial, _, _ = intersector.intersects_location(
    ray_origin_cup, ray_dir_up, multiple_hits=True
)
axial_hits = len(locs_axial)
axial_clear = (axial_hits % 2 == 0)

print(f"[INFO] Fan rays: {len(clear_rays)}/{N_RAYS} clear, {len(blocked_rays)}/{N_RAYS} blocked")
print(f"[INFO] Axial center ray: {'CLEAR' if axial_clear else 'BLOCKED'} ({axial_hits} intersections)")

if len(blocked_rays) == 0 and axial_clear:
    vapor_status = "CLEAR"
    vapor_blockage_z = None
    print(f"[RESULT] All fan rays clear — vapor path CLEAR")
elif axial_clear and len(blocked_rays) <= N_RAYS // 4:
    vapor_status = "CLEAR"
    vapor_blockage_z = first_blockage_z
    print(f"[RESULT] Center axial clear; {len(blocked_rays)} peripheral rays blocked near Z={first_blockage_z:.2f}mm — vapor path functionally CLEAR")
else:
    vapor_status = "BLOCKED"
    vapor_blockage_z = first_blockage_z
    print(f"[RESULT] Vapor path BLOCKED — first blockage at Z={vapor_blockage_z:.2f}mm")

# ════════════════════════════════════════════════════════════════════════════
# CHECK 3 — WALL THICKNESS AT CUP ZONE (Z = 0–10mm)
# ════════════════════════════════════════════════════════════════════════════
print("\n── CHECK 3: Wall thickness at cup zone (Z=0–10mm) ───────────────────")

try:
    from shapely.geometry import MultiLineString, Polygon, MultiPolygon
    from shapely.ops import unary_union, polygonize
    shapely_ok = True
except ImportError:
    shapely_ok = False
    print("[WARN] Shapely not available — using fallback thickness estimate")

sample_zs = [1.0, 3.0, 5.0, 7.0, 10.0]
global_min_thickness = float("inf")
global_min_location = None

for z_slice in sample_zs:
    if z_slice < model_bot_z or z_slice > model_top_z:
        continue

    plane_origin = np.array([0.0, 0.0, z_slice])
    plane_normal = np.array([0.0, 0.0, 1.0])

    try:
        lines = trimesh.intersections.mesh_plane(mesh, plane_normal, plane_origin)
    except Exception as e:
        print(f"[WARN] Slice at Z={z_slice} failed: {e}")
        continue

    if lines is None or len(lines) == 0:
        print(f"[INFO] Z={z_slice}mm: no cross-section found")
        continue

    if shapely_ok:
        try:
            mls = MultiLineString([tuple(map(tuple, seg)) for seg in lines])
            polys = list(polygonize(mls))
            if not polys:
                print(f"[INFO] Z={z_slice}mm: could not polygonize cross-section")
                continue

            # For each polygon, estimate min wall thickness:
            # outer boundary vs interior voids, or pair of adjacent rings
            all_rings = []
            for poly in polys:
                all_rings.append(poly.exterior)
                for interior in poly.interiors:
                    all_rings.append(interior)

            if len(all_rings) < 2:
                # Single solid polygon — estimate thickness from area/perimeter
                p = polys[0]
                approx_thickness = p.area / p.length * 2.0
                print(f"[INFO] Z={z_slice}mm: single polygon, approx wall ~{approx_thickness:.2f}mm")
                if approx_thickness < global_min_thickness:
                    global_min_thickness = approx_thickness
                    cx, cy = p.centroid.x, p.centroid.y
                    global_min_location = (cx, cy, z_slice)
                continue

            # Sample points on each ring, find nearest other-ring point distance
            min_t_slice = float("inf")
            min_xy_slice = None

            for ri, ring_a in enumerate(all_rings):
                pts_a = np.array(ring_a.coords)
                # Subsample for speed on large rings
                step = max(1, len(pts_a) // 64)
                pts_a = pts_a[::step]
                for rj, ring_b in enumerate(all_rings):
                    if ri >= rj:
                        continue
                    pts_b = np.array(ring_b.coords)
                    # Vectorized nearest-neighbor distance
                    diffs = pts_a[:, np.newaxis, :] - pts_b[np.newaxis, :, :]
                    dists = np.sqrt((diffs ** 2).sum(axis=2))
                    idx_flat = np.argmin(dists)
                    ia, ib = np.unravel_index(idx_flat, dists.shape)
                    min_d = dists[ia, ib]
                    if min_d < min_t_slice:
                        min_t_slice = min_d
                        min_xy_slice = pts_a[ia]

            if min_t_slice < global_min_thickness:
                global_min_thickness = min_t_slice
                global_min_location = (float(min_xy_slice[0]), float(min_xy_slice[1]), z_slice)

            print(f"[INFO] Z={z_slice}mm: min wall thickness ≈ {min_t_slice:.2f}mm")

        except Exception as e:
            print(f"[WARN] Shapely error at Z={z_slice}: {e}")
    else:
        # Fallback: use segment lengths as rough proxy
        seg_lengths = np.linalg.norm(lines[:, 1] - lines[:, 0], axis=1)
        rough_t = float(np.min(seg_lengths))
        print(f"[INFO] Z={z_slice}mm: min segment length (rough) ≈ {rough_t:.2f}mm")
        if rough_t < global_min_thickness:
            global_min_thickness = rough_t
            mid_pts = (lines[:, 0] + lines[:, 1]) / 2
            idx_min = np.argmin(seg_lengths)
            global_min_location = tuple(mid_pts[idx_min])

# ════════════════════════════════════════════════════════════════════════════
# FINAL REPORT
# ════════════════════════════════════════════════════════════════════════════
elapsed = time.time() - t0
print(f"\n{'═'*60}")
print(f"  KRAKEN PIPE DIAGNOSTIC REPORT")
print(f"  Elapsed: {elapsed:.1f}s")
print(f"{'═'*60}")

if mouthpiece_z is not None:
    print(f"  Mouthpiece:        {mouthpiece_status} (at Z={mouthpiece_z:.2f}mm)")
else:
    print(f"  Mouthpiece:        {mouthpiece_status}")

if vapor_blockage_z is not None:
    print(f"  Vapor path:        {vapor_status} (first issue near Z={vapor_blockage_z:.2f}mm)")
else:
    print(f"  Vapor path:        {vapor_status}")

if global_min_location:
    x, y, z = global_min_location
    print(f"  Min wall thickness: {global_min_thickness:.2f}mm at ({x:.1f}, {y:.1f}, {z:.1f})")
else:
    print(f"  Min wall thickness: measurement unavailable")

print(f"{'─'*60}")

# Action required logic
actions = []
if mouthpiece_status == "CAPPED":
    actions.append(f"CUT mouthpiece opening at Z={mouthpiece_z:.2f}mm (boolean subtract or open-face delete)")
if vapor_status == "BLOCKED":
    actions.append(f"DRILL/BORE vapor channel — blockage detected near Z={vapor_blockage_z:.2f}mm")
if global_min_thickness < MIN_WALL_MM:
    actions.append(f"THICKEN walls in cup zone — min {global_min_thickness:.2f}mm < {MIN_WALL_MM}mm threshold")

if actions:
    print(f"  Action required:")
    for a in actions:
        print(f"    - {a}")
else:
    print(f"  Action required:   none — model passes all checks")

print(f"{'═'*60}\n")
```

---

## Notes for Claude

- Run with: `/home/drmanzo/.venvs/djinn-orchestrator/bin/python3.11 finalize_kraken_pipe.py`
- The script uses `trimesh.ray.ray_pyembree` if available (fastest BVH); falls back to the pure-Python intersector gracefully.
- Shapely is used for polygon wall-thickness estimation; if absent, a segment-length fallback activates.
- **Do NOT modify the mesh** based on this output — diagnosis only. All edits are a separate task.
- If mouthpiece reports CAPPED, the fix is a boolean subtract of a small cylinder at tip XY centered on `tip_xy` computed inside the script.
- If vapor path reports BLOCKED, cross-reference the blockage Z with the mesh in Blender/MeshLab to identify the internal wall causing obstruction.
