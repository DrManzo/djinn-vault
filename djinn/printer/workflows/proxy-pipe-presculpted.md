# Proxy Pipe — Pre-Sculpted Bowl Pipeline

Use this when the model already has a sculpted cup/bowl that will serve as the Proxy receiver.
Companion to [[proxy-core-presculpted-bowl]] — run both when making a matched core + pipe set.

---

## What's Automated vs Human-Directed

| Step | Who |
|------|-----|
| Mesh repair | Automated |
| Cup diameter measurement | Automated |
| Uniform scale to Proxy spec | Automated |
| Save clean reference (`_original.stl`) | Automated |
| Mouthpiece position, radius, depth | **Javier** |
| Vapor channel route and taper Z | **Javier** |
| Cup entry angle and radius | **Javier** |
| Maker's mark (exterior bottom) | Automated |

The boring decisions stay manual because they are model-specific — the mantle tip location, body geometry, and cup orientation differ per sculpt.

---

## Steps 1–3 — Repair, Measure, Scale

Same as [[proxy-core-presculpted-bowl]] Steps 1–3. Run those first.
Output: `<name>_original.stl` — clean, scaled, watertight, no modifications.

---

## Step 4 — Get Tip Centroid (for mouthpiece placement)

```python
import trimesh, numpy as np

mesh  = trimesh.load('<name>_original.stl', force='mesh')
z_top = float(mesh.bounds[1][2])

tip_verts = mesh.vertices[mesh.vertices[:, 2] >= z_top - 5.0]
tip_cx = float(tip_verts[:, 0].mean())
tip_cy = float(tip_verts[:, 1].mean())
print(f"Tip centroid: ({tip_cx:.2f}, {tip_cy:.2f})  Z_top={z_top:.2f}mm")
```

Report to Javier. He confirms or adjusts the mouthpiece XY.

---

## Step 5 — Human Direction: Boring Parameters

Ask Javier for:

| Parameter | Kraken values | Description |
|-----------|--------------|-------------|
| `MP_R` | 4.0mm | Mouthpiece radius |
| `MP_DEPTH` | 22mm | Mouthpiece depth from tip |
| `VAPOR_R` | 5.0mm | Vapor channel radius (vertical section) |
| `TAPER_Z` | 80.0mm | Z height where channel bends toward cup |
| `CUP_ENTRY_R` | 4.0mm | Radius of bore entering the cup |
| `CUP_ENTRY_Z` | FLOOR_Z + 18mm | Z of cup entry point |

---

## Step 6 — Bore the Pipe

```python
import trimesh, numpy as np, manifold3d

SRC = '<name>_original.stl'
OUT = '<name>_pipe.stl'

mesh  = trimesh.load(SRC, force='mesh')
z_top = float(mesh.bounds[1][2])

# Values from Step 4 + Javier direction
TIP_CX, TIP_CY = <tip_cx>, <tip_cy>
CUP_CX, CUP_CY = <cup_cx>, <cup_cy>     # from core workflow
FLOOR_Z    = <floor_z>                    # from core workflow
MP_R       = 4.0
MP_DEPTH   = 22.0
VAPOR_R    = 5.0
TAPER_Z    = 80.0
CUP_ENTRY_R = 4.0
CUP_ENTRY_Z = FLOOR_Z + 18.0


def cylinder_between(p1, p2, radius, sections=64):
    p1, p2 = np.array(p1, dtype=float), np.array(p2, dtype=float)
    vec = p2 - p1
    length = np.linalg.norm(vec)
    if length < 0.1:
        return None
    d = vec / length
    z = np.array([0., 0., 1.])
    axis = np.cross(z, d)
    ax_len = np.linalg.norm(axis)
    if ax_len > 1e-6:
        axis /= ax_len
        R = trimesh.transformations.rotation_matrix(np.arccos(np.clip(np.dot(z, d), -1, 1)), axis)
    else:
        R = np.eye(4) if np.dot(z, d) > 0 else trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    cyl = trimesh.creation.cylinder(radius=radius, height=length, sections=sections)
    cyl.apply_transform(trimesh.transformations.translation_matrix((p1 + p2) / 2) @ R)
    return cyl


def to_mf(m):
    return manifold3d.Manifold(mesh=manifold3d.Mesh(
        vert_properties=np.ascontiguousarray(m.vertices, dtype=np.float32),
        tri_verts=np.ascontiguousarray(m.faces, dtype=np.uint32),
    ))

def from_mf(mf):
    mg = mf.to_mesh()
    return trimesh.Trimesh(vertices=np.array(mg.vert_properties), faces=np.array(mg.tri_verts))


body = to_mf(mesh)

# 1. Mouthpiece
body = body - to_mf(cylinder_between(
    [TIP_CX, TIP_CY, z_top + 1],
    [TIP_CX, TIP_CY, z_top - MP_DEPTH],
    MP_R,
))

# 2. Vertical vapor channel
body = body - to_mf(cylinder_between(
    [TIP_CX, TIP_CY, z_top - MP_DEPTH + 2],
    [TIP_CX, TIP_CY, TAPER_Z],
    VAPOR_R,
))

# 3. Junction sphere (smooths the bend)
junc = trimesh.creation.icosphere(subdivisions=4, radius=VAPOR_R)
junc.apply_translation([TIP_CX, TIP_CY, TAPER_Z])
body = body - to_mf(junc)

# 4. Angled bore into cup
angle_end = np.array([CUP_CX, CUP_CY, CUP_ENTRY_Z])
body = body - to_mf(cylinder_between(
    [TIP_CX, TIP_CY, TAPER_Z],
    angle_end,
    CUP_ENTRY_R,
))

# 5. Entry sphere at cup terminus (clean hole)
entry = trimesh.creation.icosphere(subdivisions=4, radius=CUP_ENTRY_R * 1.2)
entry.apply_translation(angle_end)
body = body - to_mf(entry)

result = from_mf(body)
print(f"Face delta: {len(result.faces) - len(mesh.faces):+,}  watertight: {result.is_watertight}")
result.export(OUT)
```

Expected: face delta non-zero, watertight = True.

---

## Step 7 — Maker's Mark (Exterior Bottom)

```bash
djinn-model-mark <name>_pipe.stl --size 12 --depth 0.5 --output <name>_pipe.stl
```

Exterior bottom placement — `djinn-model-mark` handles it directly.
Do NOT use the un-mirror method here — that is only for interior cup floor marks (core workflow).

---

## Output Files

| File | Contents |
|------|----------|
| `<name>_original.stl` | Clean scaled reference, no modifications |
| `<name>_core.stl` | Core — mark on cup floor (see [[proxy-core-presculpted-bowl]]) |
| `<name>_pipe.stl` | Pipe — bored + exterior bottom mark |

---

## Boring Parameters — Kraken Reference Values

| Parameter | Value | Notes |
|-----------|-------|-------|
| Mouthpiece XY | (0.05, 31.37) | Mantle tip centroid |
| Z_top | 97.36mm | |
| MP_R | 4.0mm | 8mm dia opening |
| MP_DEPTH | 22mm | |
| VAPOR_R | 5.0mm | Vertical section |
| TAPER_Z | 80.0mm | Where channel bends |
| CUP_ENTRY_R | 4.0mm | Matches cup back hole |
| CUP_ENTRY_Z | 19.69mm | FLOOR_Z (1.69) + 18mm |
| Cup XY | (-1.2, -8.9) | |
| Cup floor Z | 1.69mm | |

---

## What NOT To Do

- Do NOT run `djinn-bore-core` — destroys the sculpted cup
- Do NOT use interior cup floor mark for the pipe — exterior bottom only
- Do NOT use `mesh.contains()` for geometry checks — unreliable on organic sculpts; use ray casting
- Do NOT bore the vapor channel as a single straight vertical — it must angle into the cup, not through the floor

— Claude
