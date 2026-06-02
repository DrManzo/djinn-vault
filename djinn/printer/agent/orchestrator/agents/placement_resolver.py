"""
placement_resolver.py — Engraving placement bridge for Djinn.

Converts an approved engraving proposal (position_description string +
GeometryReport data) into a PlacementSpec with exact mm coordinates
ready to pass to djinn-model-text-engrave.

Entry point:
    resolve(spec, geo_report) -> PlacementSpec

If the position_description is too ambiguous to resolve,
returns PlacementSpec with resolved=False and a reason string.
Never raises — always degrades gracefully.

Machine: Calliope — Ender-3 V3 Plus
CLI target: djinn-model-text-engrave
  --x-offset, --y-offset, --z-depth, --text-width,
  --text-height, --rotation, --anchor
"""
from __future__ import annotations
import math
import re
from dataclasses import dataclass, field
from typing import Optional

# Minimum edge clearance enforced on all placements (mm)
EDGE_CLEARANCE_MM = 3.0

# Character aspect ratio used to estimate text block width
CHAR_ASPECT = 0.6


@dataclass
class PlacementSpec:
    """
    Fully resolved placement ready for djinn-model-text-engrave.

    All offsets are relative to the surface centroid unless
    anchor == 'TOP_LEFT', in which case they are from the
    bounding-box top-left corner of the surface.
    """
    resolved: bool
    reason: str                         # populated when resolved=False

    # Resolved coordinates
    x_offset_mm: float = 0.0
    y_offset_mm: float = 0.0
    z_surface_mm: float = 0.0          # Z of the target surface face
    width_mm: float = 0.0              # estimated text block width
    height_mm: float = 0.0             # font_height_mm from proposal
    rotation_deg: float = 0.0
    anchor: str = 'CENTER'             # 'CENTER' | 'TOP_LEFT'

    # Arc wrap (cylindrical surfaces)
    arc_wrap: bool = False
    arc_offset_deg: float = 0.0        # x_offset converted to degrees
    arc_radius_mm: float = 0.0

    # Ready-to-use CLI args dict
    modifier_args: dict = field(default_factory=dict)

    # Human-readable summary for Telegram confirmation
    text_summary: str = ''


def resolve(spec: dict, geo_report) -> PlacementSpec:
    """
    Main entry point.

    spec        — state.engraving_spec (the approved proposal dict)
    geo_report  — GeometryReport from geometry_utils.full_geometry_report()

    Returns PlacementSpec. Never raises.
    """
    try:
        return _resolve(spec, geo_report)
    except Exception as e:
        return PlacementSpec(
            resolved=False,
            reason=f'placement_resolver internal error: {e}',
        )


def _resolve(spec: dict, geo_report) -> PlacementSpec:
    position_desc  = spec.get('position_description', '').lower()
    font_height    = float(spec.get('font_height_mm', 5.0))
    content        = spec.get('content', '')
    rotation_deg   = float(spec.get('orientation_deg', 0.0))
    arc_wrap       = bool(spec.get('arc_wrap', False))
    arc_radius     = float(spec.get('arc_radius_mm', 0.0))
    surface_label  = spec.get('surface_label', 'FLAT_TOP')
    surface_idx    = spec.get('surface_group_index', 1)

    # ── Locate the target surface group ──────────────────────────────────────
    surface_groups = getattr(geo_report, 'surface_groups', [])
    target_group   = None

    # Try by index first (1-based from LLM)
    if surface_groups and 1 <= surface_idx <= len(surface_groups):
        target_group = surface_groups[surface_idx - 1]

    # Fallback: match by label
    if target_group is None:
        for g in surface_groups:
            if getattr(g, 'label', '') == surface_label:
                target_group = g
                break

    # Last resort: use first group
    if target_group is None and surface_groups:
        target_group = surface_groups[0]

    if target_group is None:
        return PlacementSpec(
            resolved=False,
            reason='No surface groups found in GeometryReport. Run geometry analysis first.',
        )

    # ── Surface dimensions ───────────────────────────────────────────────────
    centroid      = getattr(target_group, 'centroid', (0.0, 0.0, 0.0))
    cx, cy, cz    = float(centroid[0]), float(centroid[1]), float(centroid[2])

    # Approximate surface face dimensions from bounding box + label
    bbox_x  = getattr(geo_report, 'bbox_x', 50.0)
    bbox_y  = getattr(geo_report, 'bbox_y', 50.0)
    bbox_z  = getattr(geo_report, 'bbox_z', 50.0)

    if surface_label == 'FLAT_TOP':
        surf_w, surf_h = bbox_x, bbox_y
        z_surface      = cz
    elif surface_label == 'FLAT_BOTTOM':
        surf_w, surf_h = bbox_x, bbox_y
        z_surface      = cz
    elif surface_label in ('FLAT_SIDE', 'CURVED_CONVEX', 'CURVED_CONCAVE'):
        surf_w  = bbox_x          # width along X
        surf_h  = bbox_z          # height along Z
        z_surface = cz
    else:
        surf_w, surf_h = bbox_x, bbox_z
        z_surface      = cz

    # Estimated text block dimensions
    n_chars    = len(content.replace(' ', ''))
    text_width = font_height * CHAR_ASPECT * max(n_chars, 1)

    # ── Usable area after edge clearance ────────────────────────────────────
    usable_w = surf_w - 2 * EDGE_CLEARANCE_MM
    usable_h = surf_h - 2 * EDGE_CLEARANCE_MM

    if usable_w <= 0 or usable_h <= 0:
        return PlacementSpec(
            resolved=False,
            reason=(
                f'Surface too small for edge clearance: '
                f'{surf_w:.1f}×{surf_h:.1f}mm with {EDGE_CLEARANCE_MM}mm clearance required.'
            ),
        )

    # Clamp text width to usable area
    if text_width > usable_w:
        text_width = usable_w

    # ── Parse position_description ───────────────────────────────────────────
    x_off = 0.0
    y_off = 0.0
    placement_token = 'centered'   # default

    desc = position_desc

    # Vertical position tokens
    if re.search(r'lower\s+third|bottom\s+third|base\s+band|lower\s+band', desc):
        y_off = -(usable_h * 0.33)
        placement_token = 'lower_third'
    elif re.search(r'upper\s+third|top\s+third|upper\s+band', desc):
        y_off = +(usable_h * 0.33)
        placement_token = 'upper_third'
    elif re.search(r'lower\s+half|bottom\s+half', desc):
        y_off = -(usable_h * 0.25)
        placement_token = 'lower_half'
    elif re.search(r'upper\s+half|top\s+half', desc):
        y_off = +(usable_h * 0.25)
        placement_token = 'upper_half'
    elif re.search(r'center(?:ed)?|middle', desc):
        y_off = 0.0
        placement_token = 'centered'

    # Horizontal position tokens
    if re.search(r'left\s+align|left\s+side|left\s+edge', desc):
        x_off = -(usable_w * 0.25)
        placement_token += '_left'
    elif re.search(r'right\s+align|right\s+side|right\s+edge', desc):
        x_off = +(usable_w * 0.25)
        placement_token += '_right'

    # Explicit centroid extraction  "centroid at (X, Y, Z)mm"
    m = re.search(r'centroid\s+at\s+\(([\d.\-]+),\s*([\d.\-]+),\s*([\d.\-]+)\)', desc)
    if m:
        # The LLM already gave us the absolute centroid — offsets are 0
        x_off = 0.0
        y_off = 0.0
        placement_token = 'centroid_explicit'

    # ── Wall profile Z clamping (prime zone) ─────────────────────────────────
    wall_profile = getattr(geo_report, 'wall_profile', None)
    pz_min = getattr(wall_profile, 'prime_zone_z_min', None)
    pz_max = getattr(wall_profile, 'prime_zone_z_max', None)
    # outer_r from wall profile — used as arc radius when spec value is absent
    wp_outer_r = getattr(wall_profile, 'outer_r_max', 0.0) or 0.0
    is_cyl     = getattr(wall_profile, 'is_cylindrical', False)

    is_side_surface = surface_label in ('FLAT_SIDE', 'CURVED_CONVEX', 'CURVED_CONCAVE') or arc_wrap or is_cyl

    if pz_min is not None and pz_max is not None:
        pz_center  = (pz_min + pz_max) / 2
        # Only override Z for side/cylindrical surfaces — top/bottom use their own centroid Z
        if is_side_surface:
            z_surface = pz_center
        if y_off != 0 and is_side_surface:
            half_pz    = (pz_max - pz_min) / 2
            y_off_clamped = max(-half_pz + EDGE_CLEARANCE_MM,
                                min(half_pz - EDGE_CLEARANCE_MM, y_off))
            if abs(y_off_clamped - y_off) > 0.5:
                y_off = y_off_clamped

    # ── Edge overflow guard ───────────────────────────────────────────────────
    max_x = (usable_w / 2) - (text_width / 2)
    x_off = max(-max_x, min(max_x, x_off))

    # ── Arc wrap: convert x_offset to degrees ────────────────────────────────
    # Use spec arc_radius if provided; fall back to wall_profile outer_r when arc_wrap requested
    effective_arc_r = arc_radius if arc_radius > 0 else (wp_outer_r if (arc_wrap or is_cyl) and wp_outer_r > 0 else 0.0)
    arc_offset_deg = 0.0
    if arc_wrap and effective_arc_r > 0:
        arc_offset_deg = math.degrees(x_off / effective_arc_r)

    # ── modifier_args dict ────────────────────────────────────────────────────
    modifier_args = {
        '--x-offset':    round(x_off, 3),
        '--y-offset':    round(y_off, 3),
        '--z-depth':     round(float(spec.get('depth_mm', 0.8)), 3),
        '--text-width':  round(text_width, 2),
        '--text-height': round(font_height, 2),
        '--rotation':    round(rotation_deg, 1),
        '--anchor':      'CENTER',
    }
    if arc_wrap or (is_cyl and is_side_surface):
        modifier_args['--arc-offset-deg'] = round(arc_offset_deg, 2)
        modifier_args['--arc-radius']     = round(effective_arc_r, 2)

    # ── Human-readable summary ────────────────────────────────────────────────
    lines = [
        '=== PLACEMENT RESOLVED ===',
        f'  Surface     : {surface_label} (group {surface_idx})',
        f'  Centroid    : ({cx:.1f}, {cy:.1f}, {cz:.1f}) mm',
        f'  Surface dim : {surf_w:.1f} × {surf_h:.1f} mm  usable: {usable_w:.1f} × {usable_h:.1f} mm',
        f'  Text block  : {text_width:.1f} × {font_height:.1f} mm  ({n_chars} chars)',
        f'  Token       : {placement_token}',
        f'  x_offset    : {x_off:.2f} mm',
        f'  y_offset    : {y_off:.2f} mm',
        f'  z_surface   : {z_surface:.2f} mm',
        f'  rotation    : {rotation_deg}°',
    ]
    if arc_wrap or (is_cyl and is_side_surface):
        lines.append(f'  Arc wrap    : r={effective_arc_r:.1f}mm  offset={arc_offset_deg:.2f}°'
                     + (f'  (radius from wall_profile)' if arc_radius == 0 and wp_outer_r > 0 else ''))
    if pz_min is not None and is_side_surface:
        lines.append(f'  Prime zone  : Z {pz_min:.1f}–{pz_max:.1f} mm (center {z_surface:.1f})')
    lines += [
        '',
        '  modifier_args:',
    ]
    for k, v in modifier_args.items():
        lines.append(f'    {k} {v}')
    lines += [
        '',
        '  ✓ Confirm to run djinn-model-text-engrave with these coordinates.',
        '    Reply: confirm engrave placement  |  cancel',
    ]

    return PlacementSpec(
        resolved=True,
        reason='',
        x_offset_mm=round(x_off, 3),
        y_offset_mm=round(y_off, 3),
        z_surface_mm=round(z_surface, 3),
        width_mm=round(text_width, 2),
        height_mm=round(font_height, 2),
        rotation_deg=rotation_deg,
        anchor='CENTER',
        arc_wrap=arc_wrap,
        arc_offset_deg=round(arc_offset_deg, 2),
        arc_radius_mm=effective_arc_r,
        modifier_args=modifier_args,
        text_summary='\n'.join(lines),
    )
