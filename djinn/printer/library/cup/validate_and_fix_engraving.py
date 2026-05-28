#!/usr/bin/env python3
"""
validate_and_fix_engraving.py
─────────────────────────────
Checks an engraved cup STL for letter-depth issues and broken boolean geometry,
then auto-fixes into a single-component slicer-ready mesh.

Usage:
    python3 validate_and_fix_engraving.py input.stl [--min-depth 1.5] [--output fixed.stl]

Requirements:
    pip install trimesh numpy manifold3d rtree
"""

import sys
import argparse
import numpy as np
import trimesh
import manifold3d as m3d

# ─────────────────────────────────────────────────────────────
# MANIFOLD HELPERS
# ─────────────────────────────────────────────────────────────

def to_manifold(tm):
    v = np.ascontiguousarray(tm.vertices, dtype=np.float32)
    f = np.ascontiguousarray(tm.faces,    dtype=np.uint32).reshape(-1, 3)
    return m3d.Manifold(m3d.Mesh(vert_properties=v, tri_verts=f))

def from_manifold(mf):
    mg = mf.to_mesh()
    return trimesh.Trimesh(
        vertices=np.array(mg.vert_properties),
        faces=np.array(mg.tri_verts)
    )

def cup_surface_y(x, R):
    return float(np.sqrt(max(0.0, R**2 - x**2)))


# ─────────────────────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────────────────────

def analyze(stl_path, min_depth=1.5):
    print(f"\n📂  Loading: {stl_path}")
    mesh = trimesh.load(stl_path)
    comps = sorted(mesh.split(only_watertight=False),
                   key=lambda c: len(c.vertices), reverse=True)

    cup_body = comps[0]
    letters  = comps[1:]

    R = float(cup_body.vertices[:, 1].max())
    print(f"    Cup radius:      {R:.2f} mm")
    print(f"    Components:      {len(comps)}  {'⚠️  fragmented — will rebuild' if len(comps) > 1 else '✅ single mesh'}")
    print(f"    Watertight:      {mesh.is_watertight}")

    if not letters:
        print("    No letter components found.")
        return None

    all_letter_verts = np.vstack([c.vertices for c in letters])
    y_max = all_letter_verts[:, 1].max()
    y_min = all_letter_verts[:, 1].min()
    print(f"    Letter slab Y:   [{y_min:.3f}, {y_max:.3f}]")

    issues = []
    worst_shortfall = 0.0

    print(f"\n  {'#':>3}  {'X':>7}  {'CupSurf':>9}  {'Depth':>8}  Status")
    print("  " + "─"*44)
    for i, lm in enumerate(letters):
        cx    = float(lm.vertices[:, 0].mean())
        surf  = cup_surface_y(cx, R)
        depth = surf - y_max
        ok    = depth >= min_depth
        print(f"  {i+1:>3}  {cx:>+7.1f}  {surf:>9.3f}  {depth:>7.2f}mm  {'✅' if ok else '❌ SHALLOW'}")
        if not ok:
            shortfall = min_depth - depth
            worst_shortfall = max(worst_shortfall, shortfall)
            issues.append((i+1, cx, depth))

    fragmented = len(comps) > 1
    ok_depths  = len(issues) == 0

    if ok_depths and not fragmented:
        print(f"\n  ✅  File is clean — no fix needed.")
    else:
        if not ok_depths:
            print(f"\n  ⚠️   {len(issues)} shallow letter(s). Need {worst_shortfall:.2f}mm more depth.")
        if fragmented:
            print(f"  ⚠️   {len(comps)} components — slicer will ignore letter shells.")

    return {
        "ok":            ok_depths and not fragmented,
        "R":             R,
        "y_max":         y_max,
        "y_min":         y_min,
        "components":    comps,
        "letters":       letters,
        "issues":        issues,
        "needed_shift":  -worst_shortfall,
        "fragmented":    fragmented,
    }


# ─────────────────────────────────────────────────────────────
# FIX
# ─────────────────────────────────────────────────────────────

def fix(info, output_path):
    shift    = info["needed_shift"]
    cup_body = info["components"][0]
    letters  = info["letters"]
    R        = info["R"]

    print(f"\n🔧  Rebuilding as single mesh (shift={shift:.3f}mm) …")

    cup_m = to_manifold(cup_body)
    if cup_m.status() != m3d.Error.NoError:
        print(f"  ❌  Cup body not valid: {cup_m.status()}")
        sys.exit(1)

    for i, lm in enumerate(letters):
        # Shift vertices inward
        new_verts = lm.vertices.copy()
        new_verts[:, 1] += shift

        # Extend cutter outward past cup surface so boolean cuts real faces
        cx       = float(new_verts[:, 0].mean())
        surf_y   = cup_surface_y(cx, R)
        y_top    = new_verts[:, 1].max()
        y_bot    = new_verts[:, 1].min()
        extend   = max(0.0, surf_y + 2.0 - y_top)     # ensure 2mm past surface
        t        = (new_verts[:, 1] - y_bot) / max(y_top - y_bot, 1e-9)
        new_verts[:, 1] = y_bot + t * (y_top + extend - y_bot)

        # Letters come out inverted from boolean — flip winding
        cutter = trimesh.Trimesh(
            vertices=new_verts,
            faces=lm.faces[:, ::-1].copy(),
            process=False
        )
        cm = to_manifold(cutter)
        if cm.status() != m3d.Error.NoError:
            # try without flip
            cutter2 = trimesh.Trimesh(vertices=new_verts, faces=lm.faces.copy(), process=False)
            cm = to_manifold(cutter2)
        if cm.status() == m3d.Error.NoError:
            cup_m = cup_m - cm
            print(f"  Letter {i+1:>2}: ✅  ({cup_m.num_vert()} verts)")
        else:
            print(f"  Letter {i+1:>2}: ⚠️  skipped ({cm.status()})")

    result = from_manifold(cup_m)
    result_comps = result.split(only_watertight=False)
    print(f"\n  Result:     {len(result.vertices)} verts, {len(result.faces)} faces")
    print(f"  Components: {len(result_comps)}  {'✅' if len(result_comps)==1 else '❌'}")
    print(f"  Watertight: {result.is_watertight}")
    print(f"  Volume:     {result.volume/1000:.2f} cm³")

    result.export(output_path)
    print(f"\n💾  Saved: {output_path}")
    return result


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Validate & fix engraved cup STL for slicing")
    ap.add_argument("input")
    ap.add_argument("--min-depth", type=float, default=1.5)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    info = analyze(args.input, args.min_depth)
    if info is None or info["ok"]:
        sys.exit(0)

    out = args.output or args.input.replace(".stl", "_fixed.stl")
    fix(info, out)

    print("\n🔁  Re-validating …")
    check = analyze(out, args.min_depth)
    if check and check["ok"]:
        print("\n🎉  Fix confirmed — ready to slice.")
        sys.exit(0)
    else:
        print("\n❌  Fix incomplete — manual check needed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
