#!/usr/bin/env python3
"""
djinn-bore-core v2 — Proxy core bore tool

Bores a core seat cavity into the top of any STL body for the Puffco Proxy.
v2: auto-scale recovery, wall thickness check, support column scan.

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
BORE_DIAMETER_DEFAULT = 38.0
BORE_DEPTH_DEFAULT    = 51.0
TOLERANCE_DEFAULT     = 0.3

WALL_HARD_FAIL   = 1.5   # mm — always a hard stop
WALL_WARN        = 3.0   # mm — warning; hard stop under --strict
COLUMN_FAIL_RATIO = 0.10  # < 10% bore area — hard stop under --strict
COLUMN_WARN_RATIO = 0.15  # 10–15% — warning


def log(msg, quiet=False):
    if not quiet:
        print(msg, flush=True)


# ── Auto-scale recovery ───────────────────────────────────────────────────────

def auto_scale(mesh, depth, target_height=None, strict=False):
    """
    Detect wrong-unit scale and correct. Returns (mesh, scale_factor, rescaled, desc).
    Trigger: height < depth+10mm OR any dimension < 5mm.
    """
    bounds  = mesh.bounds
    dims    = bounds[1] - bounds[0]
    max_dim = float(dims.max())
    height  = float(dims[2])

    if height >= depth + 10.0 and max_dim >= 5.0:
        return mesh, 1.0, False, "no rescale needed"

    if strict:
        raise ValueError(
            f"Model height {height:.2f}mm < minimum {depth+10:.0f}mm "
            f"and --strict is set. Scale your model before running."
        )

    # Unit detection cascade
    if max_dim < 5.0:
        unit_scale = 1000.0
        unit_reason = "sub-5mm → assuming meters exported as mm (×1000)"
    elif max_dim < 50.0:
        unit_scale = 10.0
        unit_reason = "5–50mm → assuming cm exported as mm (×10)"
    elif max_dim > 500.0:
        unit_scale = 0.0394
        unit_reason = ">500mm → assuming inches as mm (×0.0394)"
    else:
        unit_scale = 1.0
        unit_reason = "dimensions within range, height too short"

    if unit_scale != 1.0:
        mesh = mesh.copy()
        mesh.apply_scale(unit_scale)

    new_height = float(mesh.bounds[1][2] - mesh.bounds[0][2])
    min_h      = target_height if target_height else (depth + 25.0)
    h_scale    = 1.0

    # After a unit correction, always scale to target — the original scale was wrong
    # so we have no reason to trust the resulting size. Scale up OR down to target.
    # Without a unit correction, only scale up (model is legitimately large if > min_h).
    needs_scale = (unit_scale != 1.0) or (new_height < min_h)
    if needs_scale and abs(new_height - min_h) / max(new_height, 0.001) > 0.05:
        h_scale = min_h / new_height
        mesh.apply_scale(h_scale)

    total = unit_scale * h_scale
    desc  = unit_reason
    if h_scale != 1.0:
        desc += f"; height-scaled ×{h_scale:.2f} to {min_h:.1f}mm"

    return mesh, total, True, desc


# ── Top detection ─────────────────────────────────────────────────────────────

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
    """Fast repair — fixes winding/normals/holes in-place. Returns (mesh, method)."""
    import trimesh
    trimesh.repair.fix_winding(mesh)
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fill_holes(mesh)
    return mesh, "trimesh"


def repair_mesh_heavy(mesh):
    """Poisson surface reconstruction via pymeshlab. Returns a new watertight mesh."""
    import trimesh, tempfile, os
    try:
        import pymeshlab
    except ImportError:
        return None, "pymeshlab not installed"

    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
        tmp_in = f.name
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
        tmp_out = f.name
    try:
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


# ── Structural checks ─────────────────────────────────────────────────────────

def check_wall_thickness(bored_mesh, cx, cy, top_z, bore_radius, depth,
                          n_z=6, n_angles=12):
    """
    Cast inward rays at multiple Z levels within the bore.
    Returns minimum wall thickness in mm, or None if measurement failed.
    """
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
    """
    Scan Z slices below the bore floor for thin support columns.
    Returns (issues_list, worst_issue_or_None).
    """
    import numpy as np
    bore_area  = math.pi * bore_radius ** 2
    base_z     = float(mesh.bounds[0][2])
    floor_z    = top_z - bore_depth

    if floor_z <= base_z + 2.0:
        return [], None  # bore goes to base — nothing to check below

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
            f"({w:.1f} × {d:.1f}mm)."
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
                 wall_mm, col_worst, material):
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

    msg = (
        f"\n---\n\n"
        f"### {ts} — @djinn-bore-core → @All: Bore complete\n\n"
        f"**Source:** `{Path(input_path).name}`\n"
        f"**Output:** `{output_path}`\n"
        f"**Bore:** {diameter:.1f}mm ⌀ × {depth:.1f}mm depth — "
        f"top Z={top_z:.1f}mm, center ({cx:.1f}, {cy:.1f})\n"
        f"**Top mode:** {top_mode} | **Engine:** {engine}\n"
        f"**Scale:** {scale_line}\n"
        f"**Wall:** {wall_status_str(wall_mm)}\n"
        f"**Columns:** {col_line}\n"
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
    parser.add_argument("--diameter",      type=float, default=BORE_DIAMETER_DEFAULT,
                        help=f"Bore diameter mm (default {BORE_DIAMETER_DEFAULT})")
    parser.add_argument("--depth",         type=float, default=BORE_DEPTH_DEFAULT,
                        help=f"Bore depth mm (default {BORE_DEPTH_DEFAULT})")
    parser.add_argument("--tolerance",     type=float, default=TOLERANCE_DEFAULT,
                        help="Added to diameter for fit clearance, clamped 0.2–0.4 (default 0.3)")
    parser.add_argument("--top-mode",      choices=["z-max", "flat", "manual"], default="z-max")
    parser.add_argument("--top-z",         type=float, default=None,
                        help="Manual Z override (requires --top-mode manual)")
    parser.add_argument("--output",        type=str, default=None,
                        help="Output path (default: <input>_bored.stl)")
    parser.add_argument("--target-height", type=float, default=None,
                        help="Target height mm after auto-scale (default: depth+25mm)")
    parser.add_argument("--material",      default="pla",
                        choices=["pla", "petg", "abs", "asa"],
                        help="Material for COMMS warning (default: pla)")
    parser.add_argument("--strict",        action="store_true",
                        help="Escalate all warnings to hard stops")
    parser.add_argument("--no-comms",      action="store_true",
                        help="Skip COMMS.md append")
    parser.add_argument("--dry-run",       action="store_true",
                        help="Print plan, write nothing")
    parser.add_argument("--quiet",         action="store_true")
    parser.add_argument("--json",          action="store_true",
                        help="Output result as JSON for pipeline use")
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

    log(f"  djinn-bore-core v2", args.quiet)
    log(f"  Input:    {input_path}", args.quiet)
    log(f"  Diameter: {effective_diam:.1f}mm ({args.diameter} + {tol} tol)", args.quiet)
    log(f"  Depth:    {args.depth}mm", args.quiet)
    log(f"  Top mode: {args.top_mode}", args.quiet)
    log(f"  Material: {args.material.upper()} {'(prototype)' if args.material == 'pla' else ''}", args.quiet)
    if args.strict:
        log(f"  Mode:     STRICT — all warnings are hard stops", args.quiet)

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

    # ── auto-scale ────────────────────────────────────────────────────────────
    scale_factor = 1.0
    scale_desc   = "no rescale needed"
    rescaled     = False
    try:
        mesh, scale_factor, rescaled, scale_desc = auto_scale(
            mesh, args.depth,
            target_height=args.target_height,
            strict=args.strict,
        )
    except ValueError as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)

    if rescaled:
        dims = mesh.bounds[1] - mesh.bounds[0]
        log(f"  ⚠  Auto-scaled ×{scale_factor:.3f}: {scale_desc}", args.quiet)
        log(f"     New size: {dims[0]:.1f} × {dims[1]:.1f} × {dims[2]:.1f}mm", args.quiet)

    # ── repair ───────────────────────────────────────────────────────────────
    repair_method = "none"
    if not mesh.is_volume:
        log("  ⚠  Mesh not a solid volume — attempting fast repair...", args.quiet)
        mesh, repair_method = repair_mesh(mesh)
        if not mesh.is_volume:
            log("  ⚠  Fast repair insufficient — running Poisson reconstruction...", args.quiet)
            heavy, method = repair_mesh_heavy(mesh)
            if heavy is not None and heavy.is_volume:
                mesh = heavy
                repair_method = method
                log(f"  ✓ Poisson reconstruction succeeded ({len(mesh.faces)} faces)", args.quiet)
            else:
                log(f"  ⚠  Poisson failed ({method}) — boolean may produce artifacts", args.quiet)
                repair_method = f"failed ({method})"

    # ── support column check (on original geometry, pre-bore) ─────────────────
    col_issues, col_worst = [], None
    if mesh.bounds[1][2] - args.depth > mesh.bounds[0][2] + 2.0:
        log("  Checking support columns below bore floor...", args.quiet)
        col_issues, col_worst = check_support_columns(
            mesh, float(mesh.bounds[1][2]), args.depth, bore_radius
        )
        if col_worst:
            label = "CRITICAL" if col_worst["critical"] else "WARNING"
            log(f"  ⚠  Column {label}: {col_worst['area']:.1f}mm² "
                f"({col_worst['ratio']*100:.1f}% of bore area) at Z={col_worst['z']}mm",
                args.quiet)
            if args.strict and col_worst["critical"]:
                print("✗ Support column below minimum under --strict", file=sys.stderr)
                sys.exit(1)
        else:
            log("  ✓ Support columns OK", args.quiet)

    # ── find top ─────────────────────────────────────────────────────────────
    if args.top_mode == "z-max":
        cx, cy, top_z = find_top_z_max(mesh)
    elif args.top_mode == "flat":
        cx, cy, top_z = find_top_flat(mesh)
    else:
        if args.top_z is None:
            print("✗ --top-mode manual requires --top-z <value>", file=sys.stderr)
            sys.exit(1)
        cx, cy, _ = find_top_z_max(mesh)
        top_z = args.top_z

    log(f"  Top: Z={top_z:.2f}mm  center ({cx:.2f}, {cy:.2f})", args.quiet)

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
        if col_worst:
            log(f"  ⚠  Column warning would appear in COMMS", args.quiet)
        if args.json:
            print(json.dumps({
                "status":       "dry_run",
                "output":       str(output_path),
                "diameter":     effective_diam,
                "depth":        args.depth,
                "top_z":        top_z,
                "cx":           cx,
                "cy":           cy,
                "scale_factor": scale_factor,
                "top_mode":     args.top_mode,
                "col_worst":    col_worst,
            }))
        sys.exit(0)

    # ── boolean subtract ──────────────────────────────────────────────────────
    log("  Building cutter cylinder...", args.quiet)
    cutter = make_cylinder_mesh(effective_diam, args.depth, cx, cy, top_z)

    log("  Boolean subtract...", args.quiet)
    try:
        result, engine = boolean_subtract(mesh, cutter)
    except RuntimeError as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)
    log(f"  Engine: {engine} | {len(result.faces)} faces out", args.quiet)

    # ── wall thickness check (on bored result) ────────────────────────────────
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
            )
            log("  ✓ COMMS.md appended", args.quiet)
        except Exception as e:
            log(f"  ⚠  COMMS append failed: {e}", args.quiet)

    if args.json:
        print(json.dumps({
            "status":       "ok",
            "output":       str(output_path),
            "diameter":     effective_diam,
            "depth":        args.depth,
            "top_z":        top_z,
            "cx":           cx,
            "cy":           cy,
            "scale_factor": scale_factor,
            "top_mode":     args.top_mode,
            "engine":       engine,
            "wall_mm":      wall_mm,
            "col_worst":    col_worst,
        }))

    sys.exit(0)


if __name__ == "__main__":
    main()
