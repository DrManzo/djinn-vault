"""
PlateNestAgent — arranges STL files onto a print plate.
Decimate high-poly STLs automatically. Arrange with trimesh. Export single merged plate STL.

Key constraint: PrusaSlicer silently drops objects when combined plate >~200MB.
Always decimate to <10MB per object before merging.
"""
import pathlib
from typing import Optional
import trimesh
import numpy as np

from ..project_state import ProjectState

BED_X, BED_Y   = 300, 300
MARGIN          = 10     # mm from bed edge
GAP             = 6      # mm gap between parts
MAX_MB          = 10     # per-object size limit before decimation
TARGET_FACES    = 15000  # decimation target (negligible visual loss at 0.2mm layer height)
QUEUE_DIR       = pathlib.Path.home() / "printer-files/queue"


def _decimate(stl_path: pathlib.Path) -> pathlib.Path:
    size_mb = stl_path.stat().st_size / (1024 * 1024)
    if size_mb <= MAX_MB:
        return stl_path

    print(f"    → decimating {stl_path.name} ({size_mb:.1f}MB)...")
    try:
        import pymeshlab
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(str(stl_path))
        ms.meshing_decimation_quadric_edge_collapse(targetfacenum=TARGET_FACES)
        out = stl_path.parent / (stl_path.stem + "_light.stl")
        ms.save_current_mesh(str(out))
        new_mb = out.stat().st_size / (1024 * 1024)
        print(f"      {size_mb:.1f}MB → {new_mb:.1f}MB ({TARGET_FACES} faces)")
        return out
    except Exception as e:
        print(f"      decimation failed ({e}) — using original")
        return stl_path


def _arrange(items: list[tuple[pathlib.Path, int]], job_id: int) -> pathlib.Path:
    """
    items: [(stl_path, quantity), ...]
    Fills plate row-by-row, left-to-right.
    """
    all_meshes = []
    cursor_x = MARGIN
    cursor_y = MARGIN
    row_height = 0.0

    for stl_path, qty in items:
        m_base = trimesh.load(str(stl_path), force="mesh")
        # Normalize to Z=0 origin
        m_base.apply_translation(-m_base.bounds[0])
        dims = m_base.bounding_box.extents  # [x, y, z]
        part_x, part_y = dims[0], dims[1]

        for _ in range(qty):
            if cursor_x + part_x > BED_X - MARGIN and cursor_x > MARGIN:
                cursor_x = MARGIN
                cursor_y += row_height + GAP
                row_height = 0.0

            if cursor_y + part_y > BED_Y - MARGIN:
                raise ValueError(
                    f"Parts don't fit on {BED_X}×{BED_Y}mm bed "
                    f"(ran out at Y={cursor_y:.0f}mm)"
                )

            m = m_base.copy()
            m.apply_translation([cursor_x, cursor_y, 0])
            all_meshes.append(m)

            cursor_x += part_x + GAP
            row_height = max(row_height, part_y)

    plate = trimesh.util.concatenate(all_meshes)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = QUEUE_DIR / f"plate_job{job_id}.stl"
    plate.export(str(out_path))
    return out_path


def run(state: ProjectState, items: Optional[list] = None) -> ProjectState:
    """
    items: [{"stl": "/path/to/file.stl", "qty": 1}, ...]
    If None: uses prototype variant STL with qty=1, or source_stl.
    """
    if items is None:
        stl = (state.variants.get("files", {}).get("prototype")
               or state.source_stl or "")
        if not stl:
            raise ValueError("No STL in project state — run ProtoOptAgent first or supply items=")
        items = [{"stl": stl, "qty": 1}]

    print(f"  [PlateNestAgent] {len(items)} item type(s)...")

    processed = []
    total_qty = 0
    for item in items:
        stl_path = pathlib.Path(item["stl"])
        if not stl_path.exists():
            raise FileNotFoundError(f"STL not found: {stl_path}")
        qty = int(item.get("qty", 1))
        total_qty += qty
        decimated = _decimate(stl_path)
        processed.append((decimated, qty))
        print(f"    {stl_path.name} × {qty}")

    plate_path = _arrange(processed, state.id)
    size_mb = plate_path.stat().st_size / (1024 * 1024)
    print(f"    → plate: {plate_path.name} ({total_qty} parts, {size_mb:.1f}MB)")

    state.plate_stl = str(plate_path)
    state.status = "priced"

    return state
