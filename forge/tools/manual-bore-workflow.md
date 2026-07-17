---
title: Manual Bore Workflow — Standard Procedure
tags: [forge, tools, bore, workflow, standard-procedure]
status: standard — use this instead of djinn-bore-core's automation
established: 2026-07-17
related: [[2026-07-14_bug-djinn-bore-core-has-two-independent-silent-auto-scale-triggers-that-can-massively-corrupt-output-geometry-with-no-warning]] | [[2026-07-16_bug-djinn-bore-core-manual-mode-xy-centering-off-by-15mm]] | [[2026-07-16_bug-djinn-model-mark-filename-heuristic-false-positive-skip]] | [[2026-07-17_manual-bore-workflow-established]]
---

# Manual Bore Workflow — Standard Procedure

**Use this workflow for every proxy-accessory bore from now on. Do not rely on `djinn-bore-core`'s own targeting or centering decisions — only use it (or `manifold3d` directly) as the boolean-cutting engine.**

---

## Why This Exists

`djinn-bore-core` has three confirmed, independent defects, all found in the same 48-hour window (2026-07-14 to 2026-07-16), none of which fail loudly enough to catch before it's too late:

1. **Silent auto-scale corruption** — two separate internal safety-net triggers can rescale the *entire mesh* with no warning, up to 10.5x blowup in one observed case. `--target-height` only pins one of the two triggers; the second has no CLI flag at all. ([[2026-07-14_bug-djinn-bore-core-has-two-independent-silent-auto-scale-triggers-that-can-massively-corrupt-output-geometry-with-no-warning]])
2. **`--top-mode auto` targets the wrong feature on irregular geometry** — it found a small decorative dome cap instead of the real ~23mm cylindrical boss on one piece, and a mis-centered point on another. There is no way to visually confirm what it picked without independently checking.
3. **`--top-mode manual`'s own X/Y auto-centering can be off by 15mm+** from the true optimal center, with no CLI flag to override X/Y directly — only `--top-z` is exposed. ([[2026-07-16_bug-djinn-bore-core-manual-mode-xy-centering-off-by-15mm]])

A fourth, separate tool (`djinn-model-mark`) also has a false-positive bug that silently skips marking based on the input filename, not real geometry or the upstream tool's own report. ([[2026-07-16_bug-djinn-model-mark-filename-heuristic-false-positive-skip]])

None of the above are fixed at the source as of this writing. This workflow routes around all four.

---

## Prerequisites

```python
import trimesh
import numpy as np
import manifold3d as m3d
from shapely.ops import polylabel
```

Use the `djinn-orchestrator` venv, which has all of the above plus `shapely`:
```
/home/drmanzo/.venvs/djinn-orchestrator/bin/python3.11
```

---

## Step 1 — Isolate the real geometry

Export files (especially from 3D scans or some CAD-to-mesh pipelines) commonly carry microscopic debris fragments — sub-millimeter stray triangles — that make the whole file fail a `watertight` check even though the actual intended body is fine on its own.

```python
scene = trimesh.load('input.3mf')  # or .stl
mesh = list(scene.geometry.values())[0] if hasattr(scene, 'geometry') else scene
bodies = mesh.split(only_watertight=False)
main = sorted(bodies, key=lambda b: len(b.faces), reverse=True)[0]
print('watertight:', main.is_watertight, '| faces:', len(main.faces), '| extents:', main.extents.tolist())
```

If `len(bodies)` is large (dozens to hundreds) but one body has the overwhelming majority of faces and matches the file's overall bounding box, the rest are debris — discard them, keep only `main`.

---

## Step 2 — Find the true bore target by scanning, not guessing

Take horizontal cross-sections through the candidate region in small Z increments (0.5–1mm is usually enough resolution). **A genuine cylindrical boss shows a cross-sectional area that stays nearly constant over a real span of height.** A tapering point, dome cap, or organic curve will show area climbing or falling continuously instead.

```python
for z in np.arange(z_high, z_low, -1.0):
    sec = main.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        continue
    planar, T = sec.to_2D()
    polys = planar.polygons_full
    if len(polys) != 1:
        print(f'Z={z}: {len(polys)} polys (fragmented — likely past the isolated boss)')
        continue
    print(f'Z={z}: area={polys[0].area:.1f}mm2')
```

Scan a wide range first (coarse, e.g. every 2mm across the whole height) to find the *candidate* region, then re-scan that narrower band at finer resolution (0.5mm) to pin down the exact stable span and its boundaries.

**Do not trust `--top-mode auto`'s pick without doing this scan yourself first.** It has been wrong twice.

---

## Step 3 — Find the true center mathematically

Once the right Z-band is identified, compute the **pole of inaccessibility** (the point farthest from the polygon's boundary — equivalently, the center of the largest circle that fits entirely inside the cross-section). This is **not** the same as:
- the bounding-box center (can be off by a lot on asymmetric shapes)
- a simple vertex-mean centroid (frame-dependent, and skewed by uneven vertex density around the boundary)
- whatever `djinn-bore-core`'s internal manual-mode centering computes (confirmed off by 15mm+ on real geometry)

```python
poly = polys[0]
label = polylabel(poly, tolerance=0.05)
max_inscribed_radius = label.distance(poly.exterior)

# map the local 2D point back to absolute mesh coordinates
local_pt = np.array([[label.x, label.y, 0.0, 1.0]])
world_pt = local_pt @ T.T
cx, cy = world_pt[0][0], world_pt[0][1]
print(f'true center: ({cx:.2f}, {cy:.2f})  max safe diameter: {2*max_inscribed_radius:.2f}mm')
```

This also gives the bore-diameter sanity check for free: `2 * max_inscribed_radius` is the absolute largest bore that could fit at that exact point with zero wall margin. Any diameter spec must leave real margin below that number.

**If the file's coordinate system doesn't match what you expect** (e.g. slicer/bed-placement coordinates given to you verbally, vs. the raw file's own local coordinate space, which is usually centered near origin) — trust the geometry-derived local coordinates, not a verbally-given absolute position. Confirm the mismatch by checking the raw file's own bounding box first.

---

## Step 4 — Pick diameter and depth against spec, validated against real geometry

Standard proxy-accessory bore spec for this shop: **39.0mm diameter + 0.3mm tolerance (39.3mm actual cutter), 44.6mm depth.**

Before cutting, validate both against the actual piece:
- **Diameter** must leave real wall margin below the max-inscribed-circle diameter from Step 3 (aim for 3mm+ margin per side where possible; the piece's own design may force less — confirm with whoever owns the design intent if margin looks thin).
- **Depth** must leave real floor material: `piece_height - bore_start_z` should comfortably exceed the depth spec, with margin for the piece's base/support structure below the floor.

---

## Step 5 — Cut directly, bypass the tool's own decision-making

```python
diameter = 39.3
depth = 44.6
radius = diameter / 2.0
top_z = <confirmed Z from Step 2>

cutter = trimesh.creation.cylinder(radius=radius, height=depth, sections=64)
cutter.apply_translation([cx, cy, top_z - depth / 2.0])

mesh_m3d = m3d.Manifold(m3d.Mesh(
    vert_properties=main.vertices.astype(np.float32),
    tri_verts=main.faces.astype(np.uint32),
))
cutter_m3d = m3d.Manifold(m3d.Mesh(
    vert_properties=cutter.vertices.astype(np.float32),
    tri_verts=cutter.faces.astype(np.uint32),
))
result = mesh_m3d - cutter_m3d
result_data = result.to_mesh()
out = trimesh.Trimesh(vertices=result_data.vert_properties[:, :3], faces=result_data.tri_verts)
```

This uses the same `manifold3d` boolean engine `djinn-bore-core` uses internally — only the targeting decisions are replaced.

---

## Step 6 — Verify. All four checks below are required, none optional.

```python
print('watertight:', out.is_watertight)
print('extents unchanged:', out.extents.tolist(), 'vs original', main.extents.tolist())
print('volume removed:', (main.volume - out.volume) / 1000, 'cm3')
print('expected full cylinder:', 3.14159 * radius**2 * depth / 1000, 'cm3')
```

- **Scale unchanged** — extents before/after must match exactly (to floating-point noise). Any real drift means something silently rescaled and the result is not trustworthy.
- **Watertight** — must hold after the cut.
- **Volume removed ≈ theoretical cylinder volume** — if it's roughly half or less of theoretical, the cutter mostly missed real material (wrong position or the boss isn't fully solid); close to full theoretical volume confirms the cut landed cleanly in real material.
- **Cross-sections through the full cut depth show one consistent, fully-enclosed hole** — not a notch cut into an outer edge:

```python
for z in [<several Z values spanning top_z down to the floor>]:
    sec = out.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    planar, T = sec.to_2D()
    for p in planar.polygons_full:
        holes = [Polygon(h).area for h in p.interiors]
        print(f'Z={z}: exterior={p.area:.1f}mm2, holes={holes}')
```

A genuine bore shows the **same hole area at every depth checked**, always with `holes=1` (a real enclosed interior ring), never `holes=0` (which means either you're above/below the bore, or — if this happens *within* the expected depth range — the cut broke out to an edge instead of staying enclosed).

---

## Step 7 — Clearance check at the top (added 2026-07-17, after this exact failure mode was hit)

**Even a perfectly-centered, correctly-sized bore can still have a thin cap of material sitting over the opening**, if the piece's outer surface at that location isn't flat. This is easy to miss because the boolean cut itself reports success and the wall-thickness/hole checks above don't catch it — the bore is genuinely a clean hole, it's just sealed at the very top by a fraction of a millimeter of the original surface.

Ray-cast straight up from just below the cut's top face, sampling **multiple points across the full bore diameter, not just the center** — a real piece's rim can be uneven enough that the worst point is well off-axis (one observed case: the worst point was 10mm off-center on a 39mm bore).

```python
pts = [(cx, cy)]
for r in np.linspace(2, radius - 1, 6):
    for a in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))

max_roof = -1
worst_pt = None
for px, py in pts:
    origin = np.array([[px, py, top_z - 0.1]])
    direction = np.array([[0, 0, 1.0]])
    locations, _, _ = main.ray.intersects_location(origin, direction)  # check against the ORIGINAL uncut mesh
    if len(locations) == 0:
        continue
    lowest_hit = min(loc[2] for loc in locations)
    if lowest_hit > max_roof:
        max_roof, worst_pt = lowest_hit, (px, py)

clearance_needed = max_roof - top_z
print(f'clearance needed: {clearance_needed:.3f}mm at {worst_pt}')
```

**If `clearance_needed` is positive** (i.e., material remains above the cut), shift the *entire cutter's Z position* up by that amount plus a safety margin (round generously — e.g. if 0.42mm is needed, move up by ~1mm, not the bare minimum). **Diameter and depth stay exactly as specified — only position moves.** Re-cut with the new `top_z`, then re-run this same clearance check to confirm it now returns clear everywhere, and re-run all of Step 6's checks too since the cut changed.

---

## Step 8 — Mark separately, if at all

Apply `djinn-model-mark` as its own independent pass on the *bored* output — never rely on `djinn-bore-core`'s built-in marking (bugged, see above), and be aware `djinn-model-mark` itself has a filename-based false-positive skip (avoid input filenames ending in `_bored`).

**This step may legitimately produce nothing** if the piece's base is an open lattice/grid support structure rather than a solid slab — there's no flat surface to engrave into. Check `mark_size`/volume-removed in the tool's own output; if it's ~0, the mark didn't apply, and that's not necessarily a bug on this specific kind of piece — just note it and move on rather than fighting the tool.

---

## Step 9 — File hygiene

- **Copy the source before cutting — never overwrite it.**
- Keep a clearly-labeled original alongside every derived file (bored, marked, etc.) so there's always a way back to a known-good starting point.
- If a file's stated size doesn't match physical reference (a real print, a real measurement) — trust the physical reference over the file, flag the discrepancy clearly, and don't silently proceed on the file's numbers alone.

---

*Established 2026-07-17 after the Backpack Boyz Core bore — see [[2026-07-17_manual-bore-workflow-established]] for the full diagnostic session that led here.*
