"""
MakersMark — stamps the TF anvil mark on the bottom face of the plate STL.
Must run after plate_nest, before slicing. No exceptions.

Uses manifold3d for boolean subtraction. Falls back to trimesh if manifold3d
reports an invalid mesh (common on non-watertight models).
"""
import pathlib
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
from trimesh.creation import extrude_polygon

from ..project_state import ProjectState

MARK_DEPTH_MM  = 0.40
MARK_SIZE_MM   = 20.0
MARK_SIZE_SM   = 15.0
MIN_FOOTPRINT  = 25.0  # below this, use small mark


def _build_cutter(size_mm: float, depth_mm: float) -> trimesh.Trimesh:
    S = size_mm
    W = S * 0.88
    H = S * 0.62
    hw, hh = W / 2, H / 2

    anvil_pts = [
        (-hw,        hh * 0.41), (-hw,        hh * 0.82),
        (-hw * 0.55, hh * 0.82), (-hw * 0.55, hh * 0.48),
        (-hw * 0.45, hh * 0.48), (-hw * 0.45, hh * 0.90),
        (0,          hh * 1.00),
        ( hw * 0.45, hh * 0.90), ( hw * 0.45, hh * 0.48),
        ( hw * 0.55, hh * 0.48), ( hw * 0.55, hh * 0.82),
        ( hw,        hh * 0.82), ( hw,        hh * 0.41),
        ( hw * 0.55, hh * 0.62), ( hw * 0.45, hh * 0.18),
        ( hw * 0.52,-hh * 0.55), ( hw * 0.52,-hh * 0.82),
        ( hw * 0.30,-hh * 1.00), (-hw * 0.30,-hh * 1.00),
        (-hw * 0.52,-hh * 0.82), (-hw * 0.52,-hh * 0.55),
        (-hw * 0.45, hh * 0.18), (-hw * 0.55, hh * 0.62),
    ]
    anvil = Polygon(anvil_pts).buffer(0)

    lh = H * 0.50
    lw = W * 0.36
    sw = lh * 0.20
    sh = lh * 0.12
    st = sw * 0.85
    lcy = (hh * 0.18 + hh * 0.90) / 2 - H * 0.04
    T_cx = -lw * 0.27
    F_cx =  lw * 0.27

    def slab_T(cx, cy, w, h):
        hw2, hh2 = w / 2, h / 2
        tbh = sw * 1.1
        return unary_union([
            Polygon([
                (cx-sw/2-sh, cy-hh2),    (cx+sw/2+sh, cy-hh2),
                (cx+sw/2+sh, cy-hh2+st), (cx+sw/2,    cy-hh2+st),
                (cx+sw/2,    cy+hh2-tbh),(cx+sw/2+sh, cy+hh2-tbh),
                (cx+sw/2+sh, cy+hh2-tbh+st),(cx-sw/2-sh, cy+hh2-tbh+st),
                (cx-sw/2-sh, cy+hh2-tbh),(cx-sw/2,    cy+hh2-tbh),
                (cx-sw/2,    cy-hh2+st), (cx-sw/2-sh, cy-hh2+st),
            ]).buffer(0),
            Polygon([
                (cx-hw2-sh, cy+hh2-tbh),(cx+hw2+sh, cy+hh2-tbh),
                (cx+hw2+sh, cy+hh2),    (cx-hw2-sh, cy+hh2),
            ]).buffer(0),
        ])

    def slab_F(cx, cy, w, h):
        hw2, hh2 = w / 2, h / 2
        bh = sw * 1.0
        sl = cx - hw2
        mid_w = w * 0.72
        mid_y = cy - hh2 * 0.08
        return unary_union([
            Polygon([(sl, cy-hh2),(sl+sw, cy-hh2),(sl+sw, cy+hh2),(sl, cy+hh2)]).buffer(0),
            Polygon([(sl-sh, cy-hh2),(sl+sw+sh, cy-hh2),(sl+sw+sh, cy-hh2+st),(sl-sh, cy-hh2+st)]).buffer(0),
            Polygon([(sl-sh, cy+hh2-bh),(cx+hw2+sh, cy+hh2-bh),(cx+hw2+sh, cy+hh2),(sl-sh, cy+hh2)]).buffer(0),
            Polygon([(sl-sh, mid_y),(sl+mid_w+sh, mid_y),(sl+mid_w+sh, mid_y+bh),(sl-sh, mid_y+bh)]).buffer(0),
        ])

    letters = unary_union([
        slab_T(T_cx, lcy, lw * 0.44, lh),
        slab_F(F_cx, lcy, lw * 0.44, lh),
    ]).buffer(0)

    mark = anvil.difference(letters).buffer(0)
    geoms = list(mark.geoms) if mark.geom_type == "MultiPolygon" else [mark]
    meshes = [extrude_polygon(g, height=depth_mm) for g in geoms if g.area > 0.01]
    return trimesh.util.concatenate(meshes)


def _boolean_subtract(mesh: trimesh.Trimesh, cutter: trimesh.Trimesh) -> trimesh.Trimesh:
    try:
        import manifold3d as m3d
        def to_m(tm):
            v = np.ascontiguousarray(tm.vertices, dtype=np.float32)
            f = np.ascontiguousarray(tm.faces, dtype=np.uint32).reshape(-1, 3)
            return m3d.Manifold(m3d.Mesh(vert_properties=v, tri_verts=f))
        def from_m(mf):
            mg = mf.to_mesh()
            return trimesh.Trimesh(vertices=np.array(mg.vert_properties),
                                   faces=np.array(mg.tri_verts))
        pm, cm = to_m(mesh), to_m(cutter)
        if pm.status() == m3d.Error.NoError and cm.status() == m3d.Error.NoError:
            return from_m(pm - cm)
    except Exception:
        pass
    # Fallback: trimesh boolean
    return mesh.difference(cutter)


def stamp(stl_path: pathlib.Path) -> pathlib.Path:
    """
    Add TF anvil mark to bottom of stl_path.
    Returns path to the marked STL (overwrites original with _marked suffix).
    """
    mesh = trimesh.load(str(stl_path), force="mesh")
    bounds = mesh.bounds
    bx = bounds[1][0] - bounds[0][0]
    by = bounds[1][1] - bounds[0][1]
    cx = (bounds[0][0] + bounds[1][0]) / 2
    cy = (bounds[0][1] + bounds[1][1]) / 2
    z_bottom = bounds[0][2]

    footprint = min(bx, by)
    size = MARK_SIZE_SM if footprint < MIN_FOOTPRINT * 2 else MARK_SIZE_MM
    # Auto-scale if mark is larger than footprint
    if size > footprint * 0.85:
        size = round(footprint * 0.80, 1)

    cutter = _build_cutter(size_mm=size, depth_mm=MARK_DEPTH_MM + 0.01)
    cutter.apply_translation([cx, cy, z_bottom - 0.01])

    result = _boolean_subtract(mesh, cutter)

    out = stl_path.parent / (stl_path.stem + "_marked.stl")
    result.export(str(out))
    return out


def run(state: ProjectState) -> ProjectState:
    plate = pathlib.Path(state.plate_stl)
    if not plate.exists():
        raise FileNotFoundError(f"plate_stl not found: {plate}")

    print(f"  [MakersMarkAgent] stamping {plate.name} ...")
    marked = stamp(plate)
    size_kb = marked.stat().st_size // 1024
    print(f"    → {marked.name} ({size_kb}KB)")

    state.plate_stl = str(marked)
    return state
