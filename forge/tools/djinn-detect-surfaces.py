#!/usr/bin/env python3
"""
djinn-detect-surfaces

Pre-flight surface scanner for djinn-model-text-engrave.
Finds every engravable face on an STL via ray-cast and curvature analysis.
Outputs a surfaces.json file that djinn-model-text-engrave reads instead
of doing its own bounding-box surface detection.

Usage:
    djinn-detect-surfaces model.stl [--output surfaces.json] [--min-area 25] [--render]

Output:
    surfaces.json — all detected surfaces with positions, normals, bounds,
                    flatness scores, and engravability ratings.

Pass --surface-data surfaces.json --surface <id> to djinn-model-text-engrave
to use the pre-flight results instead of its bounding-box detection.
"""

import argparse
import json
import sys
import os
import numpy as np
from pathlib import Path

try:
    import trimesh
except ImportError:
    print("ERROR: trimesh is required. Install with: pip install trimesh")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RAY_GRID_N = 20                    # 20x20 grid per direction = 400 rays/face
FLATNESS_THRESHOLD_MM = 0.5        # std dev above this = curved, not flat
HIT_DENSITY_THRESHOLD = 0.70       # fraction of rays that must hit
CURVATURE_FLAT_THRESHOLD = 0.01    # |k| < this = flat vertex (rad/mm²)
MIN_FLAT_ZONE_AREA_MM2 = 25.0      # minimum flat zone to bother reporting
DEFAULT_MIN_AREA_MM2 = 25.0

DIRECTIONS = {
    "top":   np.array([0.0,  0.0, -1.0]),  # rays shoot down, hit top face
    "bottom": np.array([0.0, 0.0,  1.0]),  # rays shoot up, hit bottom face
    "front": np.array([0.0,  1.0,  0.0]),  # rays shoot +Y, hit front face
    "back":  np.array([0.0, -1.0,  0.0]),
    "left":  np.array([1.0,  0.0,  0.0]),
    "right": np.array([-1.0, 0.0,  0.0]),
}

# Normals expected for each direction (face pointing outward)
EXPECTED_NORMALS = {
    "top":    np.array([0.0,  0.0,  1.0]),
    "bottom": np.array([0.0,  0.0, -1.0]),
    "front":  np.array([0.0, -1.0,  0.0]),
    "back":   np.array([0.0,  1.0,  0.0]),
    "left":   np.array([-1.0, 0.0,  0.0]),
    "right":  np.array([1.0,  0.0,  0.0]),
}


# ---------------------------------------------------------------------------
# Mesh loading and repair
# ---------------------------------------------------------------------------

def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load_mesh(str(path))
    if isinstance(mesh, trimesh.Scene):
        meshes = list(mesh.geometry.values())
        mesh = trimesh.util.concatenate(meshes)
    if not mesh.is_watertight:
        trimesh.repair.fix_normals(mesh)
        trimesh.repair.fix_winding(mesh)
        trimesh.repair.fill_holes(mesh)
    return mesh


# ---------------------------------------------------------------------------
# Ray-cast surface detection
# ---------------------------------------------------------------------------

def raycast_face(mesh: trimesh.Trimesh, direction_name: str) -> dict | None:
    """
    Cast a 20x20 grid of rays from outside the mesh toward the face
    indicated by direction_name. Returns surface data dict or None.
    """
    ray_dir = DIRECTIONS[direction_name]      # direction rays travel
    face_axis = int(np.argmax(np.abs(ray_dir)))  # which axis is the face on

    bounds = mesh.bounds  # [[xmin,ymin,zmin],[xmax,ymax,zmax]]
    bmin, bmax = bounds[0], bounds[1]
    dims = bmax - bmin

    # Build grid in the two axes perpendicular to ray direction
    axes = [i for i in range(3) if i != face_axis]
    u_vals = np.linspace(bmin[axes[0]] + dims[axes[0]] * 0.05,
                         bmax[axes[0]] - dims[axes[0]] * 0.05, RAY_GRID_N)
    v_vals = np.linspace(bmin[axes[1]] + dims[axes[1]] * 0.05,
                         bmax[axes[1]] - dims[axes[1]] * 0.05, RAY_GRID_N)

    uu, vv = np.meshgrid(u_vals, v_vals)
    n_rays = RAY_GRID_N * RAY_GRID_N

    origins = np.zeros((n_rays, 3))
    origins[:, axes[0]] = uu.flatten()
    origins[:, axes[1]] = vv.flatten()

    # Place ray origins well outside the mesh on the far side
    if ray_dir[face_axis] < 0:
        origins[:, face_axis] = bmax[face_axis] + dims[face_axis] * 0.5
    else:
        origins[:, face_axis] = bmin[face_axis] - dims[face_axis] * 0.5

    directions = np.tile(ray_dir, (n_rays, 1))

    # Fire rays
    try:
        locations, index_ray, _ = mesh.ray.intersects_location(
            ray_origins=origins,
            ray_directions=directions,
        )
    except Exception:
        return None

    if len(locations) == 0:
        return None

    hit_density = len(set(index_ray)) / n_rays
    if hit_density < HIT_DENSITY_THRESHOLD:
        return None

    # Median hit position on the face axis = actual face position
    face_hits = locations[:, face_axis]
    median_pos = float(np.median(face_hits))
    std_pos = float(np.std(face_hits))

    # Engravable bounds (projected to face plane)
    u_hits = locations[:, axes[0]]
    v_hits = locations[:, axes[1]]

    # Remove outliers (>2σ)
    u_clean = u_hits[np.abs(u_hits - np.mean(u_hits)) < 2 * np.std(u_hits)]
    v_clean = v_hits[np.abs(v_hits - np.mean(v_hits)) < 2 * np.std(v_hits)]

    width = float(u_clean.max() - u_clean.min()) if len(u_clean) > 1 else 0.0
    height = float(v_clean.max() - v_clean.min()) if len(v_clean) > 1 else 0.0
    area = width * height

    is_flat = std_pos < FLATNESS_THRESHOLD_MM
    engravability = _score_surface(direction_name, area, hit_density, is_flat, std_pos)

    normal = EXPECTED_NORMALS[direction_name].tolist()
    face_position = {"axis": ["x", "y", "z"][face_axis], "value_mm": round(median_pos, 3)}
    bounds_2d = {
        f"{['x','y','z'][axes[0]]}_min": round(float(u_clean.min()) if len(u_clean) else 0, 2),
        f"{['x','y','z'][axes[0]]}_max": round(float(u_clean.max()) if len(u_clean) else 0, 2),
        f"{['x','y','z'][axes[1]]}_min": round(float(v_clean.min()) if len(v_clean) else 0, 2),
        f"{['x','y','z'][axes[1]]}_max": round(float(v_clean.max()) if len(v_clean) else 0, 2),
    }

    warnings = []
    if std_pos > FLATNESS_THRESHOLD_MM:
        warnings.append(f"Surface not flat (std={std_pos:.2f}mm) — text may not engrave cleanly")
    if area < 100:
        warnings.append(f"Small surface area ({area:.1f}mm²) — text size will be limited")
    if direction_name == "bottom":
        warnings.append("Bottom face — text will not be visible in normal orientation")

    return {
        "id": f"{direction_name}_raycast",
        "label": _label(direction_name),
        "detection_method": "raycast",
        "normal": normal,
        "face_position_mm": face_position,
        "engravable_bounds": bounds_2d,
        "area_mm2": round(area, 1),
        "width_mm": round(width, 1),
        "height_mm": round(height, 1),
        "flatness_std_mm": round(std_pos, 3),
        "hit_density": round(hit_density, 3),
        "is_flat": is_flat,
        "engravable": engravability > 0.3,
        "engravability_score": round(engravability, 3),
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Curvature-based zone detection
# ---------------------------------------------------------------------------

def curvature_zones(mesh: trimesh.Trimesh, min_area: float) -> list[dict]:
    """
    For surfaces that failed the flatness test, find flat zones via
    Gaussian curvature (vertex_defects). Returns engravable zone dicts.
    """
    zones = []
    try:
        k = mesh.vertex_defects()   # per-vertex Gaussian curvature, 0=flat
    except Exception:
        return zones

    flat_mask = np.abs(k) < CURVATURE_FLAT_THRESHOLD
    flat_indices = np.where(flat_mask)[0]

    if len(flat_indices) < 10:
        return zones

    flat_verts = mesh.vertices[flat_indices]   # Nx3

    # Cluster by vertex normal direction (group faces pointing same way)
    flat_normals = mesh.vertex_normals[flat_indices]

    # Simple clustering: bin normals into 6 cardinal buckets
    buckets: dict[str, list] = {d: [] for d in DIRECTIONS}
    for i, (vert, norm) in enumerate(zip(flat_verts, flat_normals)):
        best_dir = max(EXPECTED_NORMALS.keys(),
                       key=lambda d: float(np.dot(norm, EXPECTED_NORMALS[d])))
        buckets[best_dir].append(vert)

    for direction_name, verts in buckets.items():
        if len(verts) < 5:
            continue
        verts_arr = np.array(verts)
        centroid = verts_arr.mean(axis=0)

        # Estimate area of this flat zone
        u_span = verts_arr[:, 0].max() - verts_arr[:, 0].min()
        v_span = verts_arr[:, 1].max() - verts_arr[:, 1].min()
        w_span = verts_arr[:, 2].max() - verts_arr[:, 2].min()
        axes_spans = sorted([u_span, v_span, w_span])
        approx_area = axes_spans[2] * axes_spans[1]   # two largest

        if approx_area < min_area:
            continue

        # Try to compute local curvature radius
        # mean curvature H ≈ 0 for flat, curvature_radius = 1/|H|
        flat_k_vals = k[flat_indices[
            np.where(flat_mask)[0][:len(flat_indices)]
        ][:len(verts)]]
        mean_k = float(np.mean(np.abs(flat_k_vals))) if len(flat_k_vals) else 0.0
        curvature_radius = round(1.0 / mean_k, 1) if mean_k > 1e-6 else None

        warnings = []
        if curvature_radius and curvature_radius < 50:
            warnings.append(
                f"Curved surface (radius={curvature_radius}mm) — "
                "text >15mm wide will distort at edges"
            )

        zones.append({
            "id": f"{direction_name}_curvature",
            "label": f"Curved flat zone — {_label(direction_name)}",
            "detection_method": "curvature",
            "normal": EXPECTED_NORMALS[direction_name].tolist(),
            "flat_zone_centroid_mm": [
                round(float(centroid[0]), 2),
                round(float(centroid[1]), 2),
                round(float(centroid[2]), 2),
            ],
            "flat_zone_area_mm2": round(approx_area, 1),
            "curvature_radius_mm": curvature_radius,
            "engravable": approx_area >= min_area,
            "engravability_score": round(0.45 if approx_area >= 100 else 0.30, 3),
            "warnings": warnings,
        })

    return zones


# ---------------------------------------------------------------------------
# Scoring and labeling helpers
# ---------------------------------------------------------------------------

def _score_surface(direction: str, area: float, hit_density: float,
                   is_flat: bool, std_mm: float) -> float:
    base = {
        "top": 1.0, "front": 0.80, "back": 0.75,
        "left": 0.70, "right": 0.70, "bottom": 0.55,
    }.get(direction, 0.5)

    if not is_flat:
        base *= 0.5
    if area < 25:
        base *= 0.3
    elif area < 100:
        base *= 0.7

    base *= min(hit_density / HIT_DENSITY_THRESHOLD, 1.0)
    return round(min(base, 1.0), 3)


def _label(direction: str) -> str:
    return {
        "top": "Top face",
        "bottom": "Bottom base",
        "front": "Front wall",
        "back": "Back wall",
        "left": "Left wall",
        "right": "Right wall",
    }.get(direction, direction)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def detect_surfaces(stl_path: Path, min_area: float = DEFAULT_MIN_AREA_MM2,
                    output_path: Path | None = None) -> dict:
    print(f"djinn-detect-surfaces")
    print(f"  Input:   {stl_path}")

    mesh = load_mesh(stl_path)
    bounds = mesh.bounds
    dims = bounds[1] - bounds[0]

    print(f"  Mesh:    {len(mesh.faces)} faces, {len(mesh.vertices)} vertices")
    print(f"  Size:    {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm")
    print(f"  Watertight: {mesh.is_watertight}")
    print()

    surfaces = []
    
    # ── Phase 1: Ray-cast all 6 directions ──────────────────────────────────
    print("  Phase 1: Ray-cast surface detection...")
    flat_directions_found = set()
    for dir_name in DIRECTIONS:
        result = raycast_face(mesh, dir_name)
        if result and result["area_mm2"] >= min_area:
            surfaces.append(result)
            if result["is_flat"]:
                flat_directions_found.add(dir_name)
            status = "✓" if result["engravable"] else "⚠"
            print(f"    {status} {dir_name:6s} → {result['area_mm2']:6.1f}mm²  "
                  f"flat={result['is_flat']}  score={result['engravability_score']}")

    # ── Phase 2: Curvature zones for non-flat faces ──────────────────────────
    print()
    print("  Phase 2: Curvature-based zone detection...")
    missed = [d for d in DIRECTIONS if d not in flat_directions_found]
    if missed:
        print(f"    Scanning curved zones for: {', '.join(missed)}")

        # Downsample large meshes for curvature pass
        analysis_mesh = mesh
        if len(mesh.faces) > 100_000:
            print(f"    Downsampling {len(mesh.faces)} → 50000 faces for curvature analysis...")
            try:
                analysis_mesh = mesh.simplify_quadratic_decimation(50_000)
            except Exception:
                analysis_mesh = mesh

        zones = curvature_zones(analysis_mesh, min_area)
        curved_added = 0
        for zone in zones:
            dir_base = zone["id"].replace("_curvature", "")
            if dir_base not in flat_directions_found:
                surfaces.append(zone)
                curved_added += 1
                print(f"    ✓ {zone['label'][:40]:40s} area≈{zone['flat_zone_area_mm2']:.1f}mm²")
        if curved_added == 0:
            print("    No additional curved zones found.")
    else:
        print("    All directions covered by raycast — skipping curvature pass.")

    # ── Sort by score ────────────────────────────────────────────────────────
    surfaces.sort(key=lambda s: s["engravability_score"], reverse=True)

    result = {
        "file": stl_path.name,
        "dimensions_mm": {
            "x": round(float(dims[0]), 2),
            "y": round(float(dims[1]), 2),
            "z": round(float(dims[2]), 2),
        },
        "bounding_box": {
            "min": [round(float(v), 2) for v in bounds[0]],
            "max": [round(float(v), 2) for v in bounds[1]],
        },
        "face_count": len(mesh.faces),
        "watertight": bool(mesh.is_watertight),
        "surfaces_found": len(surfaces),
        "surfaces": surfaces,
        "note": (
            "Pass --surface-data <this file> --surface <id> to djinn-model-text-engrave "
            "to use detected surface positions instead of bounding-box guessing."
        ),
    }

    # ── Write output ────────────────────────────────────────────────────────
    if output_path is None:
        output_path = stl_path.with_suffix(".surfaces.json")

    output_path.write_text(json.dumps(result, indent=2))

    print()
    print(f"  Found {len(surfaces)} engravable surface(s).")
    print(f"  Output: {output_path}")
    print()

    # Print summary table
    engravable = [s for s in surfaces if s.get("engravable")]
    print(f"  {'ID':<30} {'Score':>6}  {'Area':>8}  {'Method'}")
    print(f"  {'-'*30} {'------':>6}  {'--------':>8}  {'--------'}")
    for s in engravable:
        area_str = f"{s.get('area_mm2', s.get('flat_zone_area_mm2', 0)):.1f}mm²"
        print(f"  {s['id']:<30} {s['engravability_score']:>6.3f}  {area_str:>8}  {s['detection_method']}")
        for w in s.get("warnings", []):
            print(f"  {'':30}   ⚠ {w}")

    print()
    print("  ✓ djinn-detect-surfaces complete")
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Pre-flight surface scanner for djinn-model-text-engrave."
    )
    parser.add_argument("stl", help="Path to input STL file")
    parser.add_argument("--output", "-o", help="Output JSON path (default: <model>.surfaces.json)")
    parser.add_argument("--min-area", type=float, default=DEFAULT_MIN_AREA_MM2,
                        help=f"Minimum surface area in mm² (default: {DEFAULT_MIN_AREA_MM2})")
    args = parser.parse_args()

    stl_path = Path(args.stl)
    if not stl_path.exists():
        print(f"ERROR: File not found: {stl_path}")
        sys.exit(1)

    output_path = Path(args.output) if args.output else None
    detect_surfaces(stl_path, min_area=args.min_area, output_path=output_path)


if __name__ == "__main__":
    main()
