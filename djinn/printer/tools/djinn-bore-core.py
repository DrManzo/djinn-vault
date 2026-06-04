#!/usr/bin/env python3
"""
djinn-bore-core — Proxy core bore tool
Locates the top of a 3D STL object and subtracts a cylindrical bore
for the Puffco Proxy core seat.

Defaults (caliper-verified):
  diameter: 38.0mm + tolerance
  depth:    51.0mm
  tolerance: 0.3mm (range 0.2–0.4)

Usage:
  djinn-bore-core <input.stl> [options]

Place in ~/.local/bin/ and chmod +x for pipeline use.
Djinn calls this as a tool — no AI in the hot path.
"""

import argparse
import sys
import os
import json
from datetime import datetime, timezone
from pathlib import Path

COMMS_PATH = Path.home() / "Obsidian/djinn/communications/COMMS.md"
BORE_DIAMETER_DEFAULT = 38.0
BORE_DEPTH_DEFAULT    = 51.0
TOLERANCE_DEFAULT     = 0.3


def log(msg, quiet=False):
    if not quiet:
        print(msg)


def find_top_z_max(mesh):
    """Return (cx, cy, max_z) — centroid of highest-Z face group."""
    import numpy as np
    verts = mesh.vertices
    faces = mesh.faces
    face_centroids = verts[faces].mean(axis=1)
    top_idx = face_centroids[:, 2].argmax()
    top_z = verts[:, 2].max()
    cx = face_centroids[top_idx, 0]
    cy = face_centroids[top_idx, 1]
    return float(cx), float(cy), float(top_z)


def find_top_flat(mesh):
    """Return (cx, cy, max_z) — centroid of largest upward-facing flat region."""
    import numpy as np
    normals = mesh.face_normals
    areas   = mesh.area_faces
    # upward-facing: normal Z component > 0.9 (within ~25° of vertical)
    up_mask = normals[:, 2] > 0.9
    if not up_mask.any():
        log("  ⚠  No strongly upward faces found — falling back to z-max mode")
        return find_top_z_max(mesh)
    # bin by Z height (1mm buckets)
    verts = mesh.vertices
    faces = mesh.faces
    up_indices = np.where(up_mask)[0]
    face_centroids = verts[faces].mean(axis=1)
    up_centroids   = face_centroids[up_indices]
    up_areas       = areas[up_indices]
    # find Z bucket with most area
    z_vals = up_centroids[:, 2]
    z_max  = z_vals.max()
    # top 1mm band
    top_band = z_vals >= (z_max - 1.0)
    if top_band.sum() == 0:
        top_band = np.ones(len(z_vals), dtype=bool)
    cx = float(np.average(up_centroids[top_band, 0], weights=up_areas[top_band]))
    cy = float(np.average(up_centroids[top_band, 1], weights=up_areas[top_band]))
    return cx, cy, float(z_max)


def make_cylinder_mesh(diameter, depth, cx, cy, top_z, segments=64):
    """Return a trimesh cylinder positioned bore-down from top_z."""
    import trimesh
    import numpy as np
    radius = diameter / 2.0
    # cylinder origin at centroid, top face flush with top_z, extending down
    cyl = trimesh.creation.cylinder(radius=radius, height=depth, sections=segments)
    # by default cylinder is centered at origin — shift so top face = top_z
    cyl.apply_translation([cx, cy, top_z - depth / 2.0])
    return cyl


def repair_mesh(mesh):
    """Attempt basic repair via trimesh utilities."""
    import trimesh
    trimesh.repair.fix_winding(mesh)
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fill_holes(mesh)
    return mesh


def boolean_subtract(body, cutter):
    """Subtract cutter from body. Tries manifold3d first, falls back to OpenSCAD."""
    # --- attempt 1: trimesh + manifold3d (fast, pure Python) ---
    try:
        import manifold3d  # noqa: F401
        result = body.difference(cutter, engine="manifold")
        if result is not None and len(result.faces) > 0:
            return result, "manifold3d"
    except Exception:
        pass

    # --- attempt 2: trimesh blender engine ---
    try:
        result = body.difference(cutter, engine="blender")
        if result is not None and len(result.faces) > 0:
            return result, "blender"
    except Exception:
        pass

    # --- attempt 3: OpenSCAD subprocess ---
    try:
        import subprocess, tempfile, trimesh
        with tempfile.TemporaryDirectory() as tmp:
            body_path   = os.path.join(tmp, "body.stl")
            cutter_path = os.path.join(tmp, "cutter.stl")
            out_path    = os.path.join(tmp, "result.stl")
            scad_path   = os.path.join(tmp, "bore.scad")
            body.export(body_path)
            cutter.export(cutter_path)
            scad = f'difference() {{ import("{body_path}"); import("{cutter_path}"); }}'
            with open(scad_path, "w") as f:
                f.write(scad)
            subprocess.run(
                ["openscad", "-o", out_path, scad_path],
                check=True, capture_output=True, timeout=120
            )
            result = trimesh.load(out_path)
            if result is not None and len(result.faces) > 0:
                return result, "openscad"
    except Exception:
        pass

    raise RuntimeError(
        "Boolean subtract failed — tried manifold3d, blender, and openscad. "
        "Ensure at least one backend is installed: pip install manifold3d  OR  apt install openscad"
    )


def append_comms(input_path, output_path, diameter, depth, cx, cy, top_z, top_mode, engine):
    """Append a COMMS.md entry per protocol."""
    if not COMMS_PATH.exists():
        return
    ts  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    msg = (
        f"\n---\n\n"
        f"### {ts} — @djinn-bore-core → @All: Bore complete\n\n"
        f"**What:** `{Path(output_path).name}` — "
        f"{diameter:.1f}mm bore × {depth:.1f}mm depth at Z={top_z:.1f}mm "
        f"(center XY={cx:.1f}, {cy:.1f})\n"
        f"**Top mode:** {top_mode} | **Engine:** {engine}\n"
        f"**Source:** `{Path(input_path).name}`\n"
        f"**Output:** `{output_path}`\n"
        f"**Action:** none — STL ready for slice\n\n"
        f"— djinn-bore-core\n"
    )
    with open(COMMS_PATH, "a") as f:
        f.write(msg)


def validate_bore_geometry(mesh, diameter, depth, cx, cy, top_z):
    """Raise descriptive errors before attempting boolean."""
    import numpy as np
    bounds = mesh.bounds  # [[xmin,ymin,zmin],[xmax,ymax,zmax]]
    body_height = bounds[1][2] - bounds[0][2]
    body_w = bounds[1][0] - bounds[0][0]
    body_d = bounds[1][1] - bounds[0][1]

    if depth > body_height:
        raise ValueError(
            f"Bore depth {depth}mm exceeds object height {body_height:.1f}mm. "
            "Reduce --depth or check your model."
        )
    if diameter > min(body_w, body_d):
        raise ValueError(
            f"Bore diameter {diameter}mm exceeds object footprint "
            f"({body_w:.1f} × {body_d:.1f}mm). "
            "Reduce --diameter or check your model."
        )


def main():
    parser = argparse.ArgumentParser(
        prog="djinn-bore-core",
        description="Bore a proxy core seat hole into the top of an STL object."
    )
    parser.add_argument("input", help="Path to input STL file")
    parser.add_argument("--diameter", type=float, default=BORE_DIAMETER_DEFAULT,
                        help=f"Bore diameter in mm (default: {BORE_DIAMETER_DEFAULT})")
    parser.add_argument("--depth", type=float, default=BORE_DEPTH_DEFAULT,
                        help=f"Bore depth in mm (default: {BORE_DEPTH_DEFAULT})")
    parser.add_argument("--tolerance", type=float, default=TOLERANCE_DEFAULT,
                        help=f"Added to diameter for fit clearance (default: {TOLERANCE_DEFAULT}, range 0.2–0.4)")
    parser.add_argument("--top-mode", choices=["z-max", "flat", "manual"], default="z-max",
                        help="Top face detection mode (default: z-max)")
    parser.add_argument("--top-z", type=float, default=None,
                        help="Manual Z height override (only used with --top-mode manual)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output STL path (default: <input>_bored.stl)")
    parser.add_argument("--no-comms", action="store_true",
                        help="Skip COMMS.md append (for testing)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would happen, write nothing")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress stdout except errors")
    parser.add_argument("--json", action="store_true",
                        help="Output result as JSON (for pipeline consumption)")

    args = parser.parse_args()

    # --- resolve paths ---
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"✗ STL not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
    else:
        output_path = input_path.with_name(input_path.stem + "_bored.stl")

    # --- effective diameter ---
    tol = max(0.2, min(0.4, args.tolerance))  # clamp to 0.2–0.4
    effective_diameter = args.diameter + tol

    log(f"  djinn-bore-core", args.quiet)
    log(f"  Input:      {input_path}", args.quiet)
    log(f"  Diameter:   {effective_diameter:.1f}mm ({args.diameter} + {tol} tolerance)", args.quiet)
    log(f"  Depth:      {args.depth}mm", args.quiet)
    log(f"  Top mode:   {args.top_mode}", args.quiet)

    # --- load mesh ---
    try:
        import trimesh
    except ImportError:
        print("✗ trimesh not installed. Run: pip install trimesh", file=sys.stderr)
        sys.exit(2)

    log("  Loading mesh...", args.quiet)
    mesh = trimesh.load(str(input_path), force="mesh")
    if mesh is None or not hasattr(mesh, "faces") or len(mesh.faces) == 0:
        print(f"✗ Failed to load mesh from {input_path}", file=sys.stderr)
        sys.exit(1)

    log(f"  Mesh: {len(mesh.faces)} faces, {len(mesh.vertices)} vertices", args.quiet)

    # --- repair if needed ---
    if not mesh.is_watertight:
        log("  ⚠  Mesh not watertight — attempting repair...", args.quiet)
        mesh = repair_mesh(mesh)
        if not mesh.is_watertight:
            log("  ⚠  Mesh still not watertight after repair — boolean may fail", args.quiet)

    # --- find top ---
    if args.top_mode == "z-max":
        cx, cy, top_z = find_top_z_max(mesh)
    elif args.top_mode == "flat":
        cx, cy, top_z = find_top_flat(mesh)
    elif args.top_mode == "manual":
        if args.top_z is None:
            print("✗ --top-mode manual requires --top-z <value>", file=sys.stderr)
            sys.exit(1)
        cx, cy, _ = find_top_z_max(mesh)  # still use centroid XY
        top_z = args.top_z
    else:
        print(f"✗ Unknown top mode: {args.top_mode}", file=sys.stderr)
        sys.exit(1)

    log(f"  Top face:   Z={top_z:.2f}mm  center XY=({cx:.2f}, {cy:.2f})", args.quiet)

    # --- validate ---
    try:
        validate_bore_geometry(mesh, effective_diameter, args.depth, cx, cy, top_z)
    except ValueError as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        log("\n  [DRY RUN] No files written.", args.quiet)
        log(f"  Would write: {output_path}", args.quiet)
        if args.json:
            print(json.dumps({
                "status": "dry_run",
                "output": str(output_path),
                "diameter": effective_diameter,
                "depth": args.depth,
                "top_z": top_z,
                "cx": cx,
                "cy": cy,
                "top_mode": args.top_mode,
            }))
        sys.exit(0)

    # --- build cylinder cutter ---
    log("  Building cutter cylinder...", args.quiet)
    cutter = make_cylinder_mesh(effective_diameter, args.depth, cx, cy, top_z)

    # --- boolean subtract ---
    log("  Running boolean subtract...", args.quiet)
    try:
        result, engine = boolean_subtract(mesh, cutter)
    except RuntimeError as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)

    log(f"  Boolean engine: {engine}", args.quiet)
    log(f"  Result: {len(result.faces)} faces", args.quiet)

    # --- export ---
    result.export(str(output_path))
    log(f"\n  ✓ {output_path.name} written", args.quiet)
    log(f"  ✓ Bore: {effective_diameter:.1f}mm × {args.depth:.1f}mm at Z={top_z:.2f}mm", args.quiet)

    # --- COMMS.md ---
    if not args.no_comms:
        try:
            append_comms(str(input_path), str(output_path),
                         effective_diameter, args.depth,
                         cx, cy, top_z, args.top_mode, engine)
            log("  ✓ COMMS.md appended", args.quiet)
        except Exception as e:
            log(f"  ⚠  COMMS.md append failed: {e}", args.quiet)

    if args.json:
        print(json.dumps({
            "status": "ok",
            "output": str(output_path),
            "diameter": effective_diameter,
            "depth": args.depth,
            "top_z": top_z,
            "cx": cx,
            "cy": cy,
            "top_mode": args.top_mode,
            "engine": engine,
        }))

    sys.exit(0)


if __name__ == "__main__":
    main()
