#!/usr/bin/env python3
"""
djinn_terrarium_fit_agent.py

Booleans a parametric bayonet connector ring onto an arbitrary container
mesh (Meshy AI output, Blender sculpt, whatever) so it mates with the
Modular Terrarium Base System (see terrarium_base.scad).

Same pattern as djinn_makers_mark_agent.py: mesh in -> boolean op via
manifold3d -> validate -> mesh out. Ring geometry is the source of truth;
this script does NOT reinterpret bayonet spec, it just fits it to whatever
base diameter the input mesh actually has.

Usage:
    python djinn_terrarium_fit_agent.py \
        --input container_raw.stl \
        --output container_fitted.stl \
        --ring-scad terrarium_base.scad \
        --mode union \
        [--diameter-override 120] \
        [--openscad-bin openscad]

Pipeline stage: Meshy/Blender cleanup -> THIS SCRIPT -> validate_and_fix_engraving.py
(reuse the existing validator as a final manifold check before slicing)
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import trimesh
    import manifold3d as m3d
except ImportError as e:
    print(f"[FATAL] Missing dependency: {e}")
    print("        pip install trimesh manifold3d --break-system-packages")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Step 1: Load and sanity-check the input mesh (Meshy output is often non-
# manifold, so we don't trust it blindly -- same lesson as the cup fix).
# ---------------------------------------------------------------------------
def load_and_check(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, force="mesh")
    if not mesh.is_watertight:
        print(f"[WARN] Input mesh '{path.name}' is not watertight. "
              f"Attempting repair before boolean op.")
        mesh.fill_holes()
        mesh.remove_degenerate_faces()
        mesh.remove_duplicate_faces()
        mesh.merge_vertices()
    if not mesh.is_watertight:
        print(f"[WARN] Mesh still not watertight after repair. "
              f"Boolean op may fail or produce garbage -- inspect manually.")
    return mesh


# ---------------------------------------------------------------------------
# Step 2: Find the base diameter of the container so the ring can be
# generated to actually match it, instead of assuming a fixed size.
# ---------------------------------------------------------------------------
def detect_base_diameter(mesh: trimesh.Trimesh, z_slice_frac: float = 0.02) -> float:
    """
    Takes a thin horizontal slice near the bottom of the mesh (z_slice_frac
    of total height above the lowest point) and measures its bounding
    diameter. This is the diameter the connector ring needs to match.
    """
    z_min = mesh.bounds[0][2]
    z_max = mesh.bounds[1][2]
    height = z_max - z_min
    slice_z = z_min + height * z_slice_frac

    section = mesh.section(plane_origin=[0, 0, slice_z], plane_normal=[0, 0, 1])
    if section is None:
        raise RuntimeError(
            "Could not slice mesh near its base -- check that the mesh is "
            "oriented with Z-up and sits flat on the XY plane."
        )
    planar, _ = section.to_planar()
    diameter = planar.extents.max()
    print(f"[INFO] Detected base diameter: {diameter:.2f}mm "
          f"(measured at z={slice_z:.2f})")
    return diameter


# ---------------------------------------------------------------------------
# Step 3: Generate the ring geometry at the matched diameter via OpenSCAD,
# rather than hardcoding it here -- terrarium_base.scad stays the single
# source of truth for bayonet spec.
# ---------------------------------------------------------------------------
def generate_ring_stl(scad_path: Path, diameter: float, part: int,
                       openscad_bin: str, out_dir: Path) -> Path:
    out_stl = out_dir / f"ring_part{part}_{int(diameter)}mm.stl"
    cmd = [
        openscad_bin,
        "-o", str(out_stl),
        "-D", f"outer_diameter={diameter}",
        "-D", f"PART={part}",
        str(scad_path),
    ]
    print(f"[INFO] Generating ring geometry: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"OpenSCAD render failed:\n{result.stderr}")
    return out_stl


# ---------------------------------------------------------------------------
# Step 4: Boolean the ring onto the container mesh via manifold3d.
# Union by default (ring becomes part of the container's mounting base);
# subtract available if you want a female cavity cut instead.
# ---------------------------------------------------------------------------
def boolean_fit(container: trimesh.Trimesh, ring: trimesh.Trimesh,
                 mode: str) -> trimesh.Trimesh:
    c_manifold = m3d.Manifold(container.vertices, container.faces)
    r_manifold = m3d.Manifold(ring.vertices, ring.faces)

    if mode == "union":
        result = c_manifold + r_manifold
    elif mode == "subtract":
        result = c_manifold - r_manifold
    else:
        raise ValueError(f"Unknown mode '{mode}' -- use 'union' or 'subtract'")

    verts, faces = result.to_mesh().vert_properties, result.to_mesh().tri_verts
    fitted = trimesh.Trimesh(vertices=verts[:, :3], faces=faces)
    return fitted


# ---------------------------------------------------------------------------
# Step 5: Final validation before handing off to slicer. This mirrors
# validate_and_fix_engraving.py -- reuse that CLI directly if you'd rather
# not duplicate the logic; kept minimal here for a standalone sanity check.
# ---------------------------------------------------------------------------
def validate_output(mesh: trimesh.Trimesh) -> bool:
    ok = mesh.is_watertight and mesh.volume > 0
    if not ok:
        print("[FAIL] Output mesh failed validation "
              "(not watertight or zero/negative volume).")
        print("       Recommend running validate_and_fix_engraving.py on "
              "this file before slicing.")
    else:
        print(f"[OK] Output mesh is watertight. Volume: {mesh.volume:.2f}mm^3")
    return ok


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path,
                         help="Container mesh from Meshy/Blender (STL/OBJ)")
    parser.add_argument("--output", required=True, type=Path,
                         help="Path for the fitted output mesh")
    parser.add_argument("--ring-scad", required=True, type=Path,
                         help="Path to terrarium_base.scad")
    parser.add_argument("--part", type=int, default=1, choices=[1, 2, 3],
                         help="Which base part's ring to fit (default: 1, "
                              "since containers mate to Part 1's top ring)")
    parser.add_argument("--mode", default="union", choices=["union", "subtract"],
                         help="union = add ring as mounting base (default); "
                              "subtract = cut female cavity instead")
    parser.add_argument("--diameter-override", type=float, default=None,
                         help="Skip auto-detection and force a specific "
                              "diameter (mm)")
    parser.add_argument("--openscad-bin", default="openscad",
                         help="Path to openscad executable")
    args = parser.parse_args()

    container = load_and_check(args.input)

    diameter = args.diameter_override or detect_base_diameter(container)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        ring_stl = generate_ring_stl(
            args.ring_scad, diameter, args.part, args.openscad_bin, tmp_dir
        )
        ring_mesh = trimesh.load(ring_stl, force="mesh")

        fitted = boolean_fit(container, ring_mesh, args.mode)

        if not validate_output(fitted):
            print("[WARN] Writing output anyway -- inspect before printing.")

        fitted.export(args.output)
        print(f"[DONE] Wrote fitted mesh -> {args.output}")


if __name__ == "__main__":
    main()
