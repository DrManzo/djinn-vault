# Proxy Core — Pre-Sculpted Bowl Pipeline

Use this when the model already has a bowl/cup built into the geometry.
**No boring. No djinn-bore-core. No new holes.**

---

## When This Applies

- The model has a sculpted cavity that will serve as the Proxy bowl
- The cavity is open at the top, oriented upward when the model sits on the bed
- The model did NOT come from djinn-bore-core (no `_bored` suffix)

Proxy Core spec: **38.7mm dia × 44.6mm deep**

---

## Step 1 — Repair Non-Manifold Mesh

If the slicer throws Error 20 (non-manifold) or the mesh is not watertight:

```python
import trimesh, numpy as np, manifold3d

scene = trimesh.load('model.3mf')
raw = trimesh.util.concatenate([
    trimesh.Trimesh(vertices=g.vertices, faces=g.faces)
    for g in (scene.geometry.values() if hasattr(scene, 'geometry') else [scene])
])
mf = manifold3d.Manifold(mesh=manifold3d.Mesh(
    vert_properties=raw.vertices.astype(np.float32),
    tri_verts=raw.faces.astype(np.uint32),
))
mg = mf.to_mesh()
mesh = trimesh.Trimesh(vertices=np.array(mg.vert_properties), faces=np.array(mg.tri_verts))
mesh.export('model_repaired.stl')
```

> manifold3d is the only tool that reliably fixes dense organic sculpts.
> Blender voxel remesh, trimesh repair, and pymeshlab all fail on these meshes.

---

## Step 2 — Measure the Cup Diameter

Find the cup's inner diameter using cross-section circularity scanning:

```python
import trimesh, numpy as np

mesh = trimesh.load('model_repaired.stl', force='mesh')

for z in np.arange(5, mesh.bounds[1][2] * 0.7, 5):
    sl = mesh.section(plane_origin=[0,0,z], plane_normal=[0,0,1])
    if sl is None:
        continue
    p2d, _ = sl.to_planar()
    for path in p2d.polygons_closed:
        pts = np.array(path.exterior.coords)
        cx, cy = pts[:,0].mean(), pts[:,1].mean()
        r = np.sqrt(((pts - [cx,cy])**2).sum(axis=1))
        circularity = 1 - (r.std() / r.mean())
        if circularity > 0.85:
            print(f"Z={z:.0f}  dia={r.mean()*2:.1f}mm  circ={circularity:.2f}  center=({cx:.1f},{cy:.1f})")
```

Identify the largest circular feature — that is the cup opening. Note its diameter and XY center.

---

## Step 3 — Scale Uniformly to Proxy Spec

```python
TARGET_DIA = 38.7
measured_dia = <value from Step 2>
scale_factor = TARGET_DIA / measured_dia

mesh = trimesh.load('model_repaired.stl', force='mesh')
mesh.apply_scale(scale_factor)
mesh.export('model_scaled.stl')
```

Scale the whole model uniformly — do not scale axes independently.

---

## Step 4 — Find the Cup Floor Z

Ray-cast downward from inside the cup to find the actual floor surface:

```python
import trimesh, numpy as np

mesh = trimesh.load('model_scaled.stl', force='mesh')
CUP_CX, CUP_CY = <x from Step 2, scaled>, <y from Step 2, scaled>

ray_origin = np.array([[CUP_CX, CUP_CY, 30.0]])
ray_dir    = np.array([[0, 0, -1]])
locs, _, _ = mesh.ray.intersects_location(ray_origin, ray_dir)

locs_sorted = locs[np.argsort(locs[:,2])]
for loc in locs_sorted:
    print(f"Z={loc[2]:.2f}mm")
```

The **highest hit** is the inner cup floor surface. Use that Z as `FLOOR_Z`.

> The cup floor on sculpted models is often near Z=1-3mm — much lower than expected.
> Do not assume it matches the cross-section depth from Step 2.

---

## Step 5 — Apply Maker's Mark (Exterior Bottom)

```bash
djinn-model-mark model_scaled.stl --size 12 --depth 0.5 --output model_core.stl
```

Exterior bottom placement — `djinn-model-mark` handles it directly. No cutter manipulation needed.

---

## Output Files

| File | Contents |
|------|----------|
| `<name>_repaired.stl` | Watertight, unscaled |
| `<name>_scaled.stl` | Scaled to Proxy spec, no mark — save as `<name>_original.stl` |
| `<name>_core.stl` | Final — scaled + exterior bottom mark |

---

## What NOT To Do

- Do NOT run `djinn-bore-core` — that drills a new hole and destroys the sculpted cup
- Do NOT rely on `mesh.contains()` to find solid material on these meshes — it is unreliable on complex organic sculpts; use ray-casting instead

---

## Tools Required

- `manifold3d` — mesh repair
- `trimesh` — loading, ray-casting, export
- `djinn-model-mark` — exterior bottom mark

— Claude
