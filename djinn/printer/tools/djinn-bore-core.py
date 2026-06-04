#!/usr/bin/env python3
"""
djinn-bore-core v4 — Proxy core bore tool

Bores a core seat cavity into the top of any STL body for the Puffco Proxy.
v2: auto-scale recovery, wall thickness check, support column scan, Poisson repair.
v3: proportion-preserving scale, maker's mark on bore floor.
v4: 4-quadrant true-center detection, Z-level scan for best fit, wall auto-scale.

Defaults (caliper-verified):
  diameter: 38.0mm + tolerance
  depth:    51.0mm
  tolerance: 0.3mm (clamped 0.2–0.4)

Usage:
  djinn-bore-core <input.stl> [options]
"""

import argparse
import sys
import os
import json
import math
from datetime import datetime, timezone
from pathlib import Path

COMMS_PATH            = Path.home() / "Obsidian/djinn/communications/COMMS.md"
MARK_CONFIG_PATH      = Path.home() / ".config/djinn/makers-mark.json"
MARK_CONFIG_FALLBACK  = Path.home() / ".config/forge/makers-mark.json"

BORE_DIAMETER_DEFAULT = 38.0
BORE_DEPTH_DEFAULT    = 51.0
TOLERANCE_DEFAULT     = 0.3

WALL_HARD_FAIL    = 1.5   # mm — always a hard stop
WALL_WARN         = 3.0   # mm — warning; hard stop under --strict
COLUMN_FAIL_RATIO = 0.10  # < 10% bore area — hard stop under --strict
COLUMN_WARN_RATIO = 0.15  # 10–15% — warning


def log(msg, quiet=False):
    if not quiet:
        print(msg, flush=True)


# ── Feature map + proportion-preserving scale ─────────────────────────────────

def capture_feature_map(mesh):
    """
    Capture normalized vertex positions (0–1 in all axes) before any scaling.
    Returns dict with bbox_min, bbox_dims, norm_verts.
    """
    import numpy as np
    bbox_min  = mesh.bounds[0].copy()
    bbox_dims = (mesh.bounds[1] - mesh.bounds[0])
    safe_dims = np.where(bbox_dims > 0, bbox_dims, 1.0)
    return {
        "bbox_min":   bbox_min,
        "bbox_dims":  bbox_dims,
        "norm_verts": (mesh.vertices - bbox_min) / safe_dims,
    }


def proportional_scale(mesh, bore_depth, target_height):
    """
    Scale the body below the bore floor proportionally.
    Bore zone (top bore_depth mm) stays fixed in Z.
    XY scales uniformly with the below-bore Z scale to preserve proportions.
    Returns (new_mesh, scale_used, report_dict).
    """
    import numpy as np

    top_z       = float(mesh.vertices[:, 2].max())
    bore_floor  = top_z - bore_depth
    base_z      = float(mesh.vertices[:, 2].min())
    below_h     = bore_floor - base_z

    if below_h <= 0:
        return mesh, 1.0, {"note": "bore fills body — no below-bore zone to scale"}

    target_below = target_height - bore_depth
    if target_below <= 0:
        return mesh, 1.0, {"note": "target_height <= bore_depth — cannot scale"}

    z_scale  = target_below / below_h
    xy_scale = z_scale  # keep proportions: XY matches Z scale

    cx = float((mesh.bounds[0][0] + mesh.bounds[1][0]) / 2.0)
    cy = float((mesh.bounds[0][1] + mesh.bounds[1][1]) / 2.0)

    verts = mesh.vertices.copy()

    # XY: scale all vertices around center
    verts[:, 0] = cx + (verts[:, 0] - cx) * xy_scale
    verts[:, 1] = cy + (verts[:, 1] - cy) * xy_scale

    # Z: scale only below bore floor
    below = verts[:, 2] < bore_floor
    verts[below, 2] = base_z + (verts[below, 2] - base_z) * z_scale

    new_mesh          = mesh.copy()
    new_mesh.vertices = verts
    new_dims          = new_mesh.bounds[1] - new_mesh.bounds[0]

    report = {
        "bore_zone_mm":      round(bore_depth, 1),
        "body_below_before": round(below_h, 1),
        "body_below_after":  round(target_below, 1),
        "scale":             round(z_scale, 4),
        "width_before":      round(float(mesh.bounds[1][0] - mesh.bounds[0][0]), 1),
        "width_after":       round(float(new_dims[0]), 1),
        "total_height":      round(float(new_dims[2]), 1),
    }
    return new_mesh, z_scale, report


def print_proportion_report(report, quiet=False):
    if quiet or not report or "note" in report:
        return
    log("  Proportion map:", quiet)
    log(f"    Bore zone:    {report['bore_zone_mm']:.1f}mm → {report['bore_zone_mm']:.1f}mm  ✓ fixed (hardware spec)", quiet)
    log(f"    Body below:   {report['body_below_before']:.1f}mm → {report['body_below_after']:.1f}mm  ×{report['scale']:.4f}", quiet)
    log(f"    Object width: {report['width_before']:.1f}mm → {report['width_after']:.1f}mm  (XY matches body scale)", quiet)
    log(f"    Total height: {report['total_height']:.1f}mm", quiet)


# ── Auto-scale recovery ───────────────────────────────────────────────────────

def auto_scale(mesh, depth, target_height=None, strict=False, preserve_proportions=True):
    """
    Detect wrong-unit scale and correct.
    Returns (mesh, scale_factor, rescaled, desc, prop_report).
    """
    import numpy as np
    bounds  = mesh.bounds
    dims    = bounds[1] - bounds[0]
    max_dim = float(dims.max())
    height  = float(dims[2])

    if height >= depth + 10.0 and max_dim >= 5.0:
        return mesh, 1.0, False, "no rescale needed", {}

    if strict:
        raise ValueError(
            f"Model height {height:.2f}mm < minimum {depth+10:.0f}mm "
            f"and --strict is set. Scale your model before running."
        )

    # Unit detection cascade
    if max_dim < 5.0:
        unit_scale  = 1000.0
        unit_reason = "sub-5mm → assuming meters exported as mm (×1000)"
    elif max_dim < 50.0:
        unit_scale  = 10.0
        unit_reason = "5–50mm → assuming cm exported as mm (×10)"
    elif max_dim > 500.0:
        unit_scale  = 0.0394
        unit_reason = ">500mm → assuming inches as mm (×0.0394)"
    else:
        unit_scale  = 1.0
        unit_reason = "dimensions within range, height too short"

    if unit_scale != 1.0:
        mesh = mesh.copy()
        mesh.apply_scale(unit_scale)

    new_height = float(mesh.bounds[1][2] - mesh.bounds[0][2])
    min_h      = target_height if target_height else (depth + 25.0)
    prop_report = {}
    h_scale     = 1.0

    needs_height_fix = (unit_scale != 1.0) or (new_height < min_h)
    if needs_height_fix and abs(new_height - min_h) / max(new_height, 0.001) > 0.05:
        if preserve_proportions:
            prop_mesh, z_scale, prop_report = proportional_scale(mesh, depth, min_h)
            # Verify bore will still fit after proportional XY shrink
            prop_dims = prop_mesh.bounds[1] - prop_mesh.bounds[0]
            min_footprint = min(float(prop_dims[0]), float(prop_dims[1]))
            if min_footprint >= depth + 10.0:  # bore_diameter is not known here; use depth as proxy check
                mesh    = prop_mesh
                h_scale = z_scale
                unit_reason += f"; proportional scale ×{z_scale:.4f} (body below bore)"
            else:
                # Proportional scale would make object too narrow — fall back to uniform
                prop_report = {"note": f"proportional would yield {min_footprint:.1f}mm footprint — fell back to uniform"}
                h_scale = min_h / new_height
                mesh.apply_scale(h_scale)
                unit_reason += f"; uniform scale ×{h_scale:.4f} (proportional footprint too narrow)"
        else:
            h_scale = min_h / new_height
            mesh.apply_scale(h_scale)
            unit_reason += f"; uniform scale ×{h_scale:.4f}"

    total = unit_scale * h_scale
    return mesh, total, True, unit_reason, prop_report


# ── True center — 4-quadrant top face analysis ───────────────────────────────

def find_true_center_top(mesh, bore_radius, wall_min=3.0, wall_tol=0.4):
    """
    Find the true center of the top face using 4-quadrant area-weighted analysis.
    Also checks if the object needs to be scaled up to meet minimum wall requirements.

    Steps:
    1. Extract all upward-facing faces within 2mm of max Z
    2. Compute initial centroid from those faces
    3. Divide into 4 quadrants around that centroid
    4. Area-weighted centroid per quadrant → average = refined true center
    5. Check min wall; if < wall_min + wall_tol, compute scale needed

    Returns (cx, cy, top_z, scale_needed, wall_mm, report_dict)
    """
    import numpy as np

    up_mask = mesh.face_normals[:, 2] > 0.9
    if not up_mask.any():
        # fall back to z-max
        fc = mesh.vertices[mesh.faces].mean(axis=1)
        i  = fc[:, 2].argmax()
        cx, cy = float(fc[i, 0]), float(fc[i, 1])
        top_z  = float(mesh.vertices[:, 2].max())
        return cx, cy, top_z, 1.0, None, {"method": "z-max fallback"}

    fc       = mesh.vertices[mesh.faces].mean(axis=1)
    up_fc    = fc[up_mask]
    up_area  = mesh.area_faces[up_mask]
    z_max    = float(up_fc[:, 2].max())
    top_band = up_fc[:, 2] >= (z_max - 2.0)

    if not top_band.any():
        top_band = np.ones(len(up_fc), dtype=bool)

    # Scan from top downward: find the HIGHEST Z level where a ±2mm window
    # of upward faces spans at least (bore_diameter + 2×wall_target) in both X and Y
    target_wall = wall_min + wall_tol
    # Scan threshold: bore must physically fit (diameter + 1mm clearance each side)
    # Wall adequacy is checked AFTER finding the level and handled by auto-scale
    min_span    = (bore_radius * 2) + 2.0  # bore diameter + 1mm each side minimum

    z_levels = sorted(set(float(round(z, 1)) for z in up_fc[:, 2]), reverse=True)
    best_z    = None
    best_band = None

    for z_candidate in z_levels:
        band = np.abs(up_fc[:, 2] - z_candidate) <= 2.0
        if band.sum() < 3:
            continue
        pts   = up_fc[band]
        span_x = pts[:, 0].max() - pts[:, 0].min()
        span_y = pts[:, 1].max() - pts[:, 1].min()
        if span_x >= min_span and span_y >= min_span:
            best_z    = z_candidate
            best_band = band
            break

    if best_z is None:
        # No level fits — use the widest upward face level
        best_z    = float(up_fc[up_area.argmax(), 2])
        best_band = np.abs(up_fc[:, 2] - best_z) <= 2.0

    top_band = best_band
    z_max    = best_z

    # Step 1: initial centroid
    init_cx = float(np.average(up_fc[top_band, 0], weights=up_area[top_band]))
    init_cy = float(np.average(up_fc[top_band, 1], weights=up_area[top_band]))

    # Step 2: 4-quadrant refinement
    pts  = up_fc[top_band]
    area = up_area[top_band]
    q_centroids = []
    for sx, sy in [(1,1),(-1,1),(1,-1),(-1,-1)]:
        qmask = ((pts[:,0] - init_cx) * sx >= 0) & ((pts[:,1] - init_cy) * sy >= 0)
        if qmask.sum() > 0:
            qcx = float(np.average(pts[qmask, 0], weights=area[qmask]))
            qcy = float(np.average(pts[qmask, 1], weights=area[qmask]))
            q_centroids.append((qcx, qcy))

    if q_centroids:
        cx = float(np.mean([q[0] for q in q_centroids]))
        cy = float(np.mean([q[1] for q in q_centroids]))
    else:
        cx, cy = init_cx, init_cy

    # Step 3: wall check — min distance from true center to top face boundary
    top_verts = mesh.vertices[mesh.faces[up_mask][top_band].flatten()]
    dist_x = min(abs(top_verts[:,0].max() - cx), abs(cx - top_verts[:,0].min()))
    dist_y = min(abs(top_verts[:,1].max() - cy), abs(cy - top_verts[:,1].min()))
    min_clearance = min(dist_x, dist_y)
    wall_mm       = min_clearance - bore_radius
    target_wall   = wall_min + wall_tol  # 3.0 + 0.4 = 3.4mm

    # Step 4: compute scale if wall is too thin
    scale_needed = 1.0
    if wall_mm < target_wall:
        # Scale object so min_clearance becomes bore_radius + target_wall
        scale_needed = (bore_radius + target_wall) / max(min_clearance, 0.001)

    report = {
        "method":        "4-quadrant face centroid",
        "init_center":   (round(init_cx, 2), round(init_cy, 2)),
        "true_center":   (round(cx, 2), round(cy, 2)),
        "quadrants":     len(q_centroids),
        "top_z":         round(z_max, 2),
        "wall_mm":       round(wall_mm, 2),
        "scale_needed":  round(scale_needed, 4),
        "top_span_mm":   (round(float(top_verts[:,0].max()-top_verts[:,0].min()),1),
                          round(float(top_verts[:,1].max()-top_verts[:,1].min()),1)),
    }
    return cx, cy, z_max, scale_needed, wall_mm, report


# ── Top detection (legacy modes) ─────────────────────────────────────────────

def find_top_z_max(mesh):
    import numpy as np
    fc = mesh.vertices[mesh.faces].mean(axis=1)
    i  = fc[:, 2].argmax()
    return float(fc[i, 0]), float(fc[i, 1]), float(mesh.vertices[:, 2].max())


def find_top_flat(mesh):
    import numpy as np
    up_mask = mesh.face_normals[:, 2] > 0.9
    if not up_mask.any():
        log("  ⚠  No upward faces — falling back to z-max")
        return find_top_z_max(mesh)
    fc      = mesh.vertices[mesh.faces].mean(axis=1)
    up_fc   = fc[up_mask]
    up_area = mesh.area_faces[up_mask]
    z_max   = up_fc[:, 2].max()
    band    = up_fc[:, 2] >= (z_max - 1.0)
    cx = float(np.average(up_fc[band, 0], weights=up_area[band]))
    cy = float(np.average(up_fc[band, 1], weights=up_area[band]))
    return cx, cy, float(z_max)


# ── Mesh operations ───────────────────────────────────────────────────────────

def make_cylinder_mesh(diameter, depth, cx, cy, top_z, segments=64):
    import trimesh
    cyl = trimesh.creation.cylinder(radius=diameter / 2.0, height=depth, sections=segments)
    cyl.apply_translation([cx, cy, top_z - depth / 2.0])
    return cyl


def repair_mesh(mesh):
    import trimesh
    trimesh.repair.fix_winding(mesh)
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fill_holes(mesh)
    return mesh, "trimesh"


def repair_mesh_heavy(mesh):
    import trimesh, tempfile, os
    try:
        import pymeshlab
    except ImportError:
        return None, "pymeshlab not installed"
    tmp_in = tmp_out = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
            tmp_in = f.name
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
            tmp_out = f.name
        mesh.export(tmp_in)
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(tmp_in)
        ms.compute_normal_for_point_clouds()
        ms.generate_surface_reconstruction_screened_poisson(depth=8)
        ms.save_current_mesh(tmp_out)
        result = trimesh.load(tmp_out, force="mesh")
        trimesh.repair.fix_winding(result)
        trimesh.repair.fix_normals(result)
        return result, "poisson"
    except Exception as e:
        return None, str(e)
    finally:
        for p in (tmp_in, tmp_out):
            if p:
                try:
                    os.unlink(p)
                except Exception:
                    pass


def boolean_subtract(body, cutter):
    try:
        import manifold3d  # noqa
        r = body.difference(cutter, engine="manifold")
        if r is not None and len(r.faces) > 0:
            return r, "manifold3d"
    except Exception:
        pass
    try:
        r = body.difference(cutter, engine="blender")
        if r is not None and len(r.faces) > 0:
            return r, "blender"
    except Exception:
        pass
    try:
        import subprocess, tempfile, trimesh
        with tempfile.TemporaryDirectory() as tmp:
            bp = os.path.join(tmp, "body.stl")
            cp = os.path.join(tmp, "cutter.stl")
            op = os.path.join(tmp, "result.stl")
            sp = os.path.join(tmp, "bore.scad")
            body.export(bp)
            cutter.export(cp)
            open(sp, "w").write(f'difference(){{import("{bp}");import("{cp}");}}')
            subprocess.run(["openscad", "-o", op, sp],
                           check=True, capture_output=True, timeout=120)
            r = trimesh.load(op)
            if r is not None and len(r.faces) > 0:
                return r, "openscad"
    except Exception:
        pass
    raise RuntimeError(
        "Boolean subtract failed — tried manifold3d, blender, openscad. "
        "Ensure at least one backend is available."
    )


# ── Maker's mark on bore floor ────────────────────────────────────────────────

def load_mark_config():
    for p in (MARK_CONFIG_PATH, MARK_CONFIG_FALLBACK):
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                pass
    return {}


def engrave_mark_on_bore_floor(bored_mesh, cx, cy, top_z, bore_depth, effective_diam, quiet=False):
    """
    Engrave maker's mark on bore floor centered at (cx, cy).
    Bore floor is at top_z - bore_depth. Mark recesses into body below the floor.
    Mirror is NOT applied (bore floor is viewed from above, natural orientation).
    Returns (result_mesh, mark_size_used, error_str_or_None).
    """
    import trimesh

    cfg = load_mark_config()
    mark_stl_path = cfg.get("path")
    if not mark_stl_path or not Path(mark_stl_path).exists():
        return bored_mesh, 0.0, f"mark STL not found: {mark_stl_path}"

    depth_mm     = float(cfg.get("depth_mm", 0.5))
    config_size  = float(cfg.get("size_mm", 15.0))

    # Max mark diameter: bore_diam - 6mm (3mm margin each side)
    max_size = effective_diam - 6.0
    mark_size = min(config_size, max_size)
    if mark_size < 3.0:
        return bored_mesh, 0.0, f"bore too small for mark (max={max_size:.1f}mm < 3mm)"

    log(f"  Engraving mark on bore floor ({mark_size:.1f}mm, {depth_mm}mm deep)...", quiet)

    mark = trimesh.load(str(mark_stl_path), process=True)

    # Scale to mark_size based on X extent
    x_ext = mark.bounds[1][0] - mark.bounds[0][0]
    if x_ext > 0:
        mark.apply_scale(mark_size / x_ext)

    # NO mirror — bore floor is viewed from above (+Z), natural orientation reads correctly
    # (contrast with bottom face mark which IS mirrored for below-Z viewing)

    # Flatten Z to depth_mm
    z_ext = mark.bounds[1][2] - mark.bounds[0][2]
    if z_ext > 0:
        mark.vertices[:, 2] = (
            (mark.vertices[:, 2] - mark.bounds[0][2]) / z_ext * depth_mm
        )

    trimesh.repair.fix_normals(mark, multibody=True)

    # Position: center at (cx, cy), cutter top overlaps bore floor by 0.01mm
    bore_floor_z = top_z - bore_depth
    mb = mark.bounds
    mark.apply_translation([
        cx - (mb[0][0] + mb[1][0]) / 2.0,
        cy - (mb[0][1] + mb[1][1]) / 2.0,
        bore_floor_z - depth_mm + 0.01,
    ])

    try:
        result, _ = boolean_subtract(bored_mesh, mark)
        return result, mark_size, None
    except Exception as e:
        return bored_mesh, 0.0, f"mark boolean failed: {e}"


# ── Structural checks ─────────────────────────────────────────────────────────

def check_wall_thickness(bored_mesh, cx, cy, top_z, bore_radius, depth,
                          n_z=6, n_angles=12):
    import numpy as np
    FAR   = 400.0
    min_w = float("inf")

    z_lo = top_z - 3.0
    z_hi = top_z - depth + 3.0
    if z_hi >= z_lo:
        z_hi = top_z - depth * 0.5
    z_levels = np.linspace(z_lo, z_hi, max(n_z, 2))
    angles   = np.linspace(0, 2 * math.pi, n_angles, endpoint=False)

    for z in z_levels:
        for angle in angles:
            dx, dy = math.cos(angle), math.sin(angle)
            origin = np.array([[cx + dx * FAR, cy + dy * FAR, z]])
            direc  = np.array([[-dx, -dy, 0.0]])
            try:
                locs, _, _ = bored_mesh.ray.intersects_location(
                    ray_origins=origin, ray_directions=direc
                )
            except Exception:
                continue
            if len(locs) < 2:
                continue
            inward = np.array([-dx, -dy, 0.0])
            t = np.sort(np.dot(locs - origin[0], inward))
            for i in range(len(t) - 1):
                gap = t[i + 1] - t[i]
                if gap > 0.5:
                    min_w = min(min_w, gap)
                    break

    return min_w if min_w != float("inf") else None


def _polygon_area(pts):
    import numpy as np
    x, y = pts[:, 0], pts[:, 1]
    n = len(x)
    return abs(sum(x[i] * y[(i + 1) % n] - x[(i + 1) % n] * y[i]
                   for i in range(n))) / 2.0


def check_support_columns(mesh, top_z, bore_depth, bore_radius):
    import numpy as np
    bore_area = math.pi * bore_radius ** 2
    base_z    = float(mesh.bounds[0][2])
    floor_z   = top_z - bore_depth

    if floor_z <= base_z + 2.0:
        return [], None

    issues = []
    for z in np.arange(floor_z - 3.0, base_z + 2.0, -3.0):
        if not (base_z < z < floor_z):
            continue
        try:
            sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        except Exception:
            continue
        if sec is None:
            continue

        total = 0.0
        try:
            for ent in sec.entities:
                pts = sec.vertices[ent.points]
                if len(pts) >= 3:
                    total += _polygon_area(pts)
        except Exception:
            continue

        if 0 < total < bore_area * COLUMN_WARN_RATIO:
            issues.append({
                "z":        round(float(z), 1),
                "area":     round(total, 1),
                "ratio":    round(total / bore_area, 3),
                "critical": total < bore_area * COLUMN_FAIL_RATIO,
            })

    worst = min(issues, key=lambda x: x["ratio"]) if issues else None
    return issues, worst


# ── Validation ────────────────────────────────────────────────────────────────

def validate_bore_geometry(mesh, diameter, depth, cx, cy, top_z):
    bounds = mesh.bounds
    h = bounds[1][2] - bounds[0][2]
    w = bounds[1][0] - bounds[0][0]
    d = bounds[1][1] - bounds[0][1]
    if depth > h:
        raise ValueError(
            f"Bore depth {depth}mm exceeds object height {h:.1f}mm. "
            "Reduce --depth or use --target-height."
        )
    if diameter > min(w, d):
        raise ValueError(
            f"Bore diameter {diameter}mm exceeds object footprint "
            f"({w:.1f} × {d:.1f}mm). Use --no-proportional or increase --target-height."
        )


def wall_status_str(wall):
    if wall is None:
        return "⚠  measurement unavailable"
    if wall < WALL_HARD_FAIL:
        return f"✗ FAIL {wall:.1f}mm — too thin, bore punches through"
    if wall < WALL_WARN:
        return f"⚠  WARN {wall:.1f}mm — structurally marginal (< {WALL_WARN}mm)"
    if wall < 6.0:
        return f"✓ OK {wall:.1f}mm"
    return f"✓ IDEAL {wall:.1f}mm"


# ── COMMS ─────────────────────────────────────────────────────────────────────

def append_comms(input_path, output_path, diameter, depth,
                 cx, cy, top_z, top_mode, engine,
                 scale_factor, scale_desc,
                 wall_mm, col_worst, material,
                 prop_report=None, mark_size=0.0):
    if not COMMS_PATH.exists():
        return
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    col_line = (
        "✓ no column issues" if col_worst is None else
        f"{'✗ CRITICAL' if col_worst['critical'] else '⚠  WARN'} "
        f"narrowest column {col_worst['area']:.1f}mm² "
        f"({col_worst['ratio']*100:.1f}% of bore area) at Z={col_worst['z']}mm"
    )
    scale_line = (
        "✓ no rescale" if scale_factor == 1.0
        else f"⚠  auto-scaled ×{scale_factor:.3f} — {scale_desc}"
    )
    mat_warn = {
        "pla":  "⚠  PLA (prototype) — PETG min, ABS/ASA recommended for production",
        "petg": "⚠  PETG — marginal for long-term heat exposure; ABS/ASA preferred",
        "abs":  "✓ ABS — suitable for heat exposure",
        "asa":  "✓ ASA — optimal for heat exposure",
    }.get(material.lower(), "")

    prop_line = ""
    if prop_report and "note" not in prop_report:
        prop_line = (
            f"**Proportion:** body-below ×{prop_report['scale']:.4f} "
            f"({prop_report['body_below_before']:.1f}mm → {prop_report['body_below_after']:.1f}mm) | "
            f"bore zone {prop_report['bore_zone_mm']:.1f}mm fixed\n"
        )

    mark_line = (
        f"**Mark:** ✓ bore floor engraved — {mark_size:.1f}mm @ {load_mark_config().get('depth_mm', 0.5)}mm depth, mirror=off (viewed from above)\n"
        if mark_size > 0 else
        "**Mark:** none\n"
    )

    msg = (
        f"\n---\n\n"
        f"### {ts} — @djinn-bore-core → @All: Bore complete\n\n"
        f"**Source:** `{Path(input_path).name}`\n"
        f"**Output:** `{output_path}`\n"
        f"**Bore:** {diameter:.1f}mm ⌀ × {depth:.1f}mm depth — "
        f"top Z={top_z:.1f}mm, center ({cx:.1f}, {cy:.1f})\n"
        f"**Top mode:** {top_mode} | **Engine:** {engine}\n"
        f"**Scale:** {scale_line}\n"
        + prop_line +
        f"**Wall:** {wall_status_str(wall_mm)}\n"
        f"**Columns:** {col_line}\n"
        + mark_line
    )
    if mat_warn:
        msg += f"**Material:** {mat_warn}\n"
    msg += f"**Action:** none — STL ready for slice\n\n— djinn-bore-core\n"

    with open(COMMS_PATH, "a") as f:
        f.write(msg)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="djinn-bore-core",
        description="Bore a proxy core seat into the top of an STL object."
    )
    parser.add_argument("input",
                        help="Path to input STL")
    parser.add_argument("--diameter",          type=float, default=BORE_DIAMETER_DEFAULT)
    parser.add_argument("--depth",             type=float, default=BORE_DEPTH_DEFAULT)
    parser.add_argument("--tolerance",         type=float, default=TOLERANCE_DEFAULT,
                        help="Added to diameter, clamped 0.2–0.4 (default 0.3)")
    parser.add_argument("--top-mode",          choices=["auto", "z-max", "flat", "manual"], default="auto",
                        help="Top detection: auto=4-quadrant true center (default), z-max, flat, manual")
    parser.add_argument("--top-z",             type=float, default=None)
    parser.add_argument("--output",            type=str,   default=None)
    parser.add_argument("--target-height",     type=float, default=None,
                        help="Target height mm after auto-scale (default: depth+25mm)")
    parser.add_argument("--material",          default="pla",
                        choices=["pla", "petg", "abs", "asa"])
    parser.add_argument("--strict",            action="store_true",
                        help="Escalate all warnings to hard stops")
    parser.add_argument("--no-proportional",   action="store_true",
                        help="Use uniform scale instead of proportion-preserving scale")
    parser.add_argument("--no-mark",           action="store_true",
                        help="Skip maker's mark on bore floor")
    parser.add_argument("--no-comms",          action="store_true")
    parser.add_argument("--dry-run",           action="store_true")
    parser.add_argument("--quiet",             action="store_true")
    parser.add_argument("--json",              action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"✗ STL not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_path.with_name(input_path.stem + "_bored.stl")
    )

    tol            = max(0.2, min(0.4, args.tolerance))
    effective_diam = args.diameter + tol
    bore_radius    = effective_diam / 2.0

    log(f"  djinn-bore-core v4", args.quiet)
    log(f"  Input:    {input_path}", args.quiet)
    log(f"  Diameter: {effective_diam:.1f}mm ({args.diameter} + {tol} tol)", args.quiet)
    log(f"  Depth:    {args.depth}mm", args.quiet)
    log(f"  Top mode: {args.top_mode}", args.quiet)
    log(f"  Material: {args.material.upper()} {'(prototype)' if args.material == 'pla' else ''}", args.quiet)
    flags = []
    if args.strict:           flags.append("STRICT")
    if args.no_proportional:  flags.append("no-proportional")
    if args.no_mark:          flags.append("no-mark")
    if flags:
        log(f"  Flags:    {', '.join(flags)}", args.quiet)

    try:
        import trimesh
    except ImportError:
        print("✗ trimesh not installed: pip install trimesh", file=sys.stderr)
        sys.exit(2)

    # ── load ─────────────────────────────────────────────────────────────────
    log("  Loading mesh...", args.quiet)
    mesh = trimesh.load(str(input_path), force="mesh")
    if mesh is None or not hasattr(mesh, "faces") or len(mesh.faces) == 0:
        print(f"✗ Failed to load mesh from {input_path}", file=sys.stderr)
        sys.exit(1)
    log(f"  Mesh: {len(mesh.faces)} faces, watertight={mesh.is_watertight}", args.quiet)

    # Capture feature map before any scaling
    feature_map = capture_feature_map(mesh)

    # ── auto-scale ────────────────────────────────────────────────────────────
    scale_factor = 1.0
    scale_desc   = "no rescale needed"
    rescaled     = False
    prop_report  = {}
    try:
        mesh, scale_factor, rescaled, scale_desc, prop_report = auto_scale(
            mesh, args.depth,
            target_height=args.target_height,
            strict=args.strict,
            preserve_proportions=not args.no_proportional,
        )
    except ValueError as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)

    if rescaled:
        dims = mesh.bounds[1] - mesh.bounds[0]
        log(f"  ⚠  Auto-scaled ×{scale_factor:.3f}: {scale_desc}", args.quiet)
        log(f"     New size: {dims[0]:.1f} × {dims[1]:.1f} × {dims[2]:.1f}mm", args.quiet)
        print_proportion_report(prop_report, args.quiet)

    # ── repair ───────────────────────────────────────────────────────────────
    repair_method = "none"
    if not mesh.is_volume:
        log("  ⚠  Mesh not a solid volume — attempting fast repair...", args.quiet)
        mesh, repair_method = repair_mesh(mesh)
        if not mesh.is_volume:
            log("  ⚠  Fast repair insufficient — running Poisson reconstruction...", args.quiet)
            heavy, method = repair_mesh_heavy(mesh)
            if heavy is not None and heavy.is_volume:
                mesh          = heavy
                repair_method = method
                log(f"  ✓ Poisson reconstruction succeeded ({len(mesh.faces)} faces)", args.quiet)
            else:
                log(f"  ⚠  Poisson failed ({method}) — boolean may produce artifacts", args.quiet)
                repair_method = f"failed ({method})"

    # ── support column check ──────────────────────────────────────────────────
    col_issues, col_worst = [], None
    if mesh.bounds[1][2] - args.depth > mesh.bounds[0][2] + 2.0:
        log("  Checking support columns below bore floor...", args.quiet)
        col_issues, col_worst = check_support_columns(
            mesh, float(mesh.bounds[1][2]), args.depth, bore_radius
        )
        if col_worst:
            label = "CRITICAL" if col_worst["critical"] else "WARNING"
            log(f"  ⚠  Column {label}: {col_worst['area']:.1f}mm² "
                f"({col_worst['ratio']*100:.1f}%) at Z={col_worst['z']}mm", args.quiet)
            if args.strict and col_worst["critical"]:
                print("✗ Support column below minimum under --strict", file=sys.stderr)
                sys.exit(1)
        else:
            log("  ✓ Support columns OK", args.quiet)

    # ── find top — 4-quadrant true center by default ─────────────────────────
    if args.top_mode == "manual":
        if args.top_z is None:
            print("✗ --top-mode manual requires --top-z <value>", file=sys.stderr)
            sys.exit(1)
        cx, cy, _ = find_top_z_max(mesh)
        top_z = args.top_z
        log(f"  Top: Z={top_z:.2f}mm  center ({cx:.2f}, {cy:.2f}) [manual]", args.quiet)
    elif args.top_mode in ("z-max", "flat"):
        if args.top_mode == "z-max":
            cx, cy, top_z = find_top_z_max(mesh)
        else:
            cx, cy, top_z = find_top_flat(mesh)
        log(f"  Top: Z={top_z:.2f}mm  center ({cx:.2f}, {cy:.2f}) [{args.top_mode}]", args.quiet)
    else:  # "auto" — 4-quadrant true center (default)
        cx, cy, top_z, scale_for_wall, wall_pre, center_report = find_true_center_top(
            mesh, bore_radius, wall_min=WALL_WARN, wall_tol=0.4
        )
        log(f"  Top: Z={top_z:.2f}mm  true center ({cx:.2f}, {cy:.2f})  "
            f"[4-quadrant, {center_report['quadrants']} quads]", args.quiet)
        log(f"  Top span: {center_report['top_span_mm'][0]}×{center_report['top_span_mm'][1]}mm  "
            f"wall={center_report['wall_mm']:.1f}mm", args.quiet)

        # Auto-scale to meet wall requirement if needed
        if scale_for_wall > 1.01:
            log(f"  ⚠  Wall {center_report['wall_mm']:.1f}mm < {WALL_WARN+0.4:.1f}mm — "
                f"scaling ×{scale_for_wall:.3f} to meet minimum", args.quiet)
            mesh.apply_scale(scale_for_wall)
            scale_factor *= scale_for_wall
            # Re-run center after scale
            cx, cy, top_z, _, _, _ = find_true_center_top(mesh, bore_radius)
            log(f"  Rescaled top: Z={top_z:.2f}mm  center ({cx:.2f}, {cy:.2f})", args.quiet)

    # ── validate bore geometry ────────────────────────────────────────────────
    try:
        validate_bore_geometry(mesh, effective_diam, args.depth, cx, cy, top_z)
    except ValueError as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)

    # ── dry-run exit ──────────────────────────────────────────────────────────
    if args.dry_run:
        log("\n  [DRY RUN] No files written.", args.quiet)
        log(f"  Would write: {output_path}", args.quiet)
        if args.json:
            print(json.dumps({
                "status": "dry_run", "output": str(output_path),
                "diameter": effective_diam, "depth": args.depth,
                "top_z": top_z, "cx": cx, "cy": cy,
                "scale_factor": scale_factor, "top_mode": args.top_mode,
            }))
        sys.exit(0)

    # ── boolean subtract (bore) ───────────────────────────────────────────────
    log("  Building cutter cylinder...", args.quiet)
    cutter = make_cylinder_mesh(effective_diam, args.depth, cx, cy, top_z)

    log("  Boolean subtract...", args.quiet)
    try:
        result, engine = boolean_subtract(mesh, cutter)
    except RuntimeError as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)
    log(f"  Engine: {engine} | {len(result.faces)} faces out", args.quiet)

    # ── wall thickness check ──────────────────────────────────────────────────
    log("  Checking wall thickness...", args.quiet)
    wall_mm = check_wall_thickness(result, cx, cy, top_z, bore_radius, args.depth)
    log(f"  Wall: {wall_status_str(wall_mm)}", args.quiet)

    if wall_mm is not None and wall_mm < WALL_HARD_FAIL:
        print(f"✗ Wall {wall_mm:.1f}mm < {WALL_HARD_FAIL}mm — bore punches through",
              file=sys.stderr)
        sys.exit(1)
    if wall_mm is not None and wall_mm < WALL_WARN and args.strict:
        print(f"✗ Wall {wall_mm:.1f}mm < {WALL_WARN}mm under --strict", file=sys.stderr)
        sys.exit(1)

    # ── maker's mark on bore floor ────────────────────────────────────────────
    mark_size = 0.0
    if not args.no_mark:
        result, mark_size, mark_err = engrave_mark_on_bore_floor(
            result, cx, cy, top_z, args.depth, effective_diam, args.quiet
        )
        if mark_err:
            log(f"  ⚠  Mark skipped: {mark_err}", args.quiet)
        else:
            log(f"  ✓ Mark engraved ({mark_size:.1f}mm, bore floor)", args.quiet)

    # ── export ────────────────────────────────────────────────────────────────
    result.export(str(output_path))
    log(f"\n  ✓ {output_path.name} written", args.quiet)
    log(f"  ✓ Bore: {effective_diam:.1f}mm × {args.depth:.1f}mm at Z={top_z:.2f}mm", args.quiet)
    if args.material.lower() in ("pla", "petg"):
        log(f"  ⚠  {args.material.upper()} — PETG min, ABS/ASA recommended for production",
            args.quiet)

    # ── COMMS ─────────────────────────────────────────────────────────────────
    if not args.no_comms:
        try:
            append_comms(
                str(input_path), str(output_path),
                effective_diam, args.depth,
                cx, cy, top_z, args.top_mode, engine,
                scale_factor, scale_desc,
                wall_mm, col_worst, args.material,
                prop_report=prop_report, mark_size=mark_size,
            )
            log("  ✓ COMMS.md appended", args.quiet)
        except Exception as e:
            log(f"  ⚠  COMMS append failed: {e}", args.quiet)

    if args.json:
        print(json.dumps({
            "status": "ok", "output": str(output_path),
            "diameter": effective_diam, "depth": args.depth,
            "top_z": top_z, "cx": cx, "cy": cy,
            "scale_factor": scale_factor, "top_mode": args.top_mode,
            "engine": engine, "wall_mm": wall_mm,
            "col_worst": col_worst, "mark_size": mark_size,
        }))

    sys.exit(0)


if __name__ == "__main__":
    main()
