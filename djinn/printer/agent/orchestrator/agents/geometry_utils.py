"""
geometry_utils.py — Pure-Python STL mesh geometry analysis.
No trimesh required. Reads binary or ASCII STL, returns structured
geometry data the engraving agent can reason over.

Machine profile: Calliope (Ender-3 V3 Plus)
  nozzle_dia   = 0.4mm
  layer_h      = 0.20mm (standard) / 0.12mm (accuracy)
  min_feature  = 0.4mm (1× nozzle)
  bed_x, bed_y = 300mm, 300mm
  bed_z        = 340mm
"""
from __future__ import annotations
import struct, math, pathlib
from dataclasses import dataclass, field
from typing import List, Tuple

# ── Machine constants ─────────────────────────────────────────────────────────
NOZZLE_DIA   = 0.4    # mm
LAYER_H_STD  = 0.20   # mm — standard profile
LAYER_H_ACC  = 0.12   # mm — accuracy profile
MIN_ENGRAVE_DEPTH  = 0.5   # mm — below this is invisible
MIN_ENGRAVE_DEPTH_READABLE = 0.8  # mm — safe for text readability
MIN_LETTER_H = 3.0   # mm absolute
REC_LETTER_H = 5.0   # mm recommended
MIN_STROKE   = NOZZLE_DIA  # 0.4mm
OVERHANG_ANGLE_LIMIT = 45.0  # degrees from vertical — FDM limit
BED_X, BED_Y, BED_Z = 300.0, 300.0, 340.0


@dataclass
class Face:
    normal: Tuple[float, float, float]
    v0: Tuple[float, float, float]
    v1: Tuple[float, float, float]
    v2: Tuple[float, float, float]

    @property
    def centroid(self) -> Tuple[float, float, float]:
        return (
            (self.v0[0] + self.v1[0] + self.v2[0]) / 3,
            (self.v0[1] + self.v1[1] + self.v2[1]) / 3,
            (self.v0[2] + self.v1[2] + self.v2[2]) / 3,
        )

    @property
    def area(self) -> float:
        ax = self.v1[0] - self.v0[0]; ay = self.v1[1] - self.v0[1]; az = self.v1[2] - self.v0[2]
        bx = self.v2[0] - self.v0[0]; by = self.v2[1] - self.v0[1]; bz = self.v2[2] - self.v0[2]
        cx = ay * bz - az * by; cy = az * bx - ax * bz; cz = ax * by - ay * bx
        return 0.5 * math.sqrt(cx*cx + cy*cy + cz*cz)


@dataclass
class SurfaceGroup:
    label: str              # FLAT_TOP / FLAT_SIDE / FLAT_BOTTOM / CURVED_CONVEX / STEEP_OVERHANG
    normal: Tuple[float, float, float]
    face_count: int
    total_area_mm2: float
    centroid: Tuple[float, float, float]
    engravability: float    # 0.0–1.0
    engrav_reason: str
    angle_from_vertical: float  # degrees


@dataclass
class GeometryReport:
    stl_path: str
    face_count: int
    bbox_x: float
    bbox_y: float
    bbox_z: float
    volume_cm3: float
    surface_groups: List[SurfaceGroup] = field(default_factory=list)
    engravable_groups: List[SurfaceGroup] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    text_summary: str = ""  # human-readable block for LLM consumption


def _normalize(v):
    m = math.sqrt(sum(x*x for x in v))
    if m < 1e-9:
        return (0.0, 0.0, 1.0)
    return tuple(x/m for x in v)


def _dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def _angle_from_up(normal):
    """Degrees from straight-up (0,0,1). 0=top, 90=side, 180=bottom."""
    up = (0.0, 0.0, 1.0)
    d = max(-1.0, min(1.0, _dot(normal, up)))
    return math.degrees(math.acos(d))


def _load_binary_stl(data: bytes) -> List[Face]:
    faces = []
    count = struct.unpack_from('<I', data, 80)[0]
    offset = 84
    for _ in range(count):
        vals = struct.unpack_from('<12f', data, offset)
        n = (vals[0], vals[1], vals[2])
        v0 = (vals[3], vals[4], vals[5])
        v1 = (vals[6], vals[7], vals[8])
        v2 = (vals[9], vals[10], vals[11])
        faces.append(Face(normal=_normalize(n), v0=v0, v1=v1, v2=v2))
        offset += 50
    return faces


def _load_ascii_stl(text: str) -> List[Face]:
    import re
    faces = []
    token_re = re.compile(
        r'facet normal\s+([\d.eE+\-]+)\s+([\d.eE+\-]+)\s+([\d.eE+\-]+)'
        r'.*?vertex\s+([\d.eE+\-]+)\s+([\d.eE+\-]+)\s+([\d.eE+\-]+)'
        r'\s+vertex\s+([\d.eE+\-]+)\s+([\d.eE+\-]+)\s+([\d.eE+\-]+)'
        r'\s+vertex\s+([\d.eE+\-]+)\s+([\d.eE+\-]+)\s+([\d.eE+\-]+)',
        re.DOTALL
    )
    for m in token_re.finditer(text):
        vals = [float(x) for x in m.groups()]
        n = _normalize((vals[0], vals[1], vals[2]))
        faces.append(Face(
            normal=n,
            v0=(vals[3], vals[4], vals[5]),
            v1=(vals[6], vals[7], vals[8]),
            v2=(vals[9], vals[10], vals[11]),
        ))
    return faces


def load_stl(path: str) -> List[Face]:
    data = pathlib.Path(path).read_bytes()
    try:
        header = data[:80].decode('ascii', errors='replace')
    except Exception:
        header = ''
    if b'solid' in data[:256] and b'facet normal' in data[:512]:
        return _load_ascii_stl(data.decode('ascii', errors='replace'))
    return _load_binary_stl(data)


def _classify_label(angle: float) -> str:
    if angle < 20:
        return 'FLAT_TOP'
    elif angle < 70:
        return 'FLAT_SIDE'
    elif angle < 110:
        return 'FLAT_SIDE'
    elif angle < 160:
        return 'FLAT_BOTTOM'
    else:
        return 'FLAT_BOTTOM'


def _engravability(angle: float) -> Tuple[float, str]:
    """Score 0.0–1.0 and reason string."""
    if angle < 15:
        return 1.0, 'Flat top surface — ideal for FDM engraving. Nozzle tracks with gravity.'
    elif angle < 45:
        return 0.85, 'Slightly angled top — excellent. Minor layer staircase on slope edge.'
    elif angle < 75:
        return 0.70, 'Side surface — good with print orientation adjustment. Check overhang.'
    elif angle < 90:
        return 0.55, 'Near-vertical side — feasible but watch for layer line interference.'
    elif angle < 110:
        return 0.40, 'Shallow bottom-facing — requires support or reorientation. Hard on FDM.'
    elif angle < 135:
        return 0.15, 'Overhanging surface — very difficult. Recommend workaround: reorient or skip.'
    else:
        return 0.0, 'Bottom-facing overhang — not engravable without supports. Use top surface.'


def classify_surfaces(
    faces: List[Face],
    angle_thresh: float = 15.0,
) -> List[SurfaceGroup]:
    """
    Group faces by normal direction (within angle_thresh degrees) and
    classify engravability. Returns groups sorted by engravability desc.
    """
    groups: list[dict] = []

    for face in faces:
        angle = _angle_from_up(face.normal)
        placed = False
        for g in groups:
            ref_angle = _angle_from_up(g['normal'])
            if abs(angle - ref_angle) < angle_thresh:
                # Check normal dot product similarity
                if _dot(face.normal, g['normal']) > math.cos(math.radians(angle_thresh)):
                    g['faces'].append(face)
                    g['area'] += face.area
                    # running centroid average
                    c = face.centroid
                    n = len(g['faces'])
                    prev = g['centroid']
                    g['centroid'] = (
                        prev[0] + (c[0]-prev[0])/n,
                        prev[1] + (c[1]-prev[1])/n,
                        prev[2] + (c[2]-prev[2])/n,
                    )
                    placed = True
                    break
        if not placed:
            groups.append({
                'normal': face.normal,
                'faces': [face],
                'area': face.area,
                'centroid': face.centroid,
            })

    result = []
    for g in groups:
        if len(g['faces']) < 1:
            continue
        angle = _angle_from_up(g['normal'])
        label = _classify_label(angle)
        score, reason = _engravability(angle)
        result.append(SurfaceGroup(
            label=label,
            normal=g['normal'],
            face_count=len(g['faces']),
            total_area_mm2=g['area'],
            centroid=g['centroid'],
            engravability=score,
            engrav_reason=reason,
            angle_from_vertical=angle,
        ))

    result.sort(key=lambda s: s.engravability, reverse=True)
    return result


def _bounding_box(faces: List[Face]):
    xs, ys, zs = [], [], []
    for f in faces:
        for v in (f.v0, f.v1, f.v2):
            xs.append(v[0]); ys.append(v[1]); zs.append(v[2])
    return (
        max(xs)-min(xs),
        max(ys)-min(ys),
        max(zs)-min(zs),
    )


def _approx_volume(faces: List[Face]) -> float:
    """Signed volume via divergence theorem."""
    total = 0.0
    for f in faces:
        v0, v1, v2 = f.v0, f.v1, f.v2
        total += (v0[0]*(v1[1]*v2[2]-v1[2]*v2[1])
                 -v0[1]*(v1[0]*v2[2]-v1[2]*v2[0])
                 +v0[2]*(v1[0]*v2[1]-v1[1]*v2[0]))
    return abs(total) / 6.0 / 1000.0  # mm³ → cm³


def full_geometry_report(stl_path: str) -> GeometryReport:
    faces = load_stl(stl_path)
    if not faces:
        raise ValueError(f"No faces found in {stl_path}")

    bbox_x, bbox_y, bbox_z = _bounding_box(faces)
    vol = _approx_volume(faces)
    groups = classify_surfaces(faces)
    engravable = [g for g in groups if g.engravability >= 0.5]
    warnings = []

    if bbox_x > BED_X or bbox_y > BED_Y or bbox_z > BED_Z:
        warnings.append(
            f'Model {bbox_x:.1f}×{bbox_y:.1f}×{bbox_z:.1f}mm may exceed '
            f'Ender-3 V3 Plus bed ({BED_X}×{BED_Y}×{BED_Z}mm). Check orientation.'
        )
    if not engravable:
        warnings.append('No flat surfaces scored ≥0.5. All engraving requires reorientation or workaround.')

    # Build human-readable text summary for LLM
    lines = [
        f'=== GEOMETRY REPORT: {pathlib.Path(stl_path).name} ===',
        f'Bounding box : {bbox_x:.1f} × {bbox_y:.1f} × {bbox_z:.1f} mm (X×Y×Z)',
        f'Volume       : {vol:.2f} cm³',
        f'Face count   : {len(faces)}',
        f'Surface groups found: {len(groups)}',
        '',
        '--- MACHINE CONSTRAINTS (Ender-3 V3 Plus / Calliope) ---',
        f'  Nozzle dia     : {NOZZLE_DIA}mm',
        f'  Layer height   : {LAYER_H_STD}mm std / {LAYER_H_ACC}mm accuracy',
        f'  Min engrave depth : {MIN_ENGRAVE_DEPTH}mm (invisible below this)',
        f'  Readable depth    : {MIN_ENGRAVE_DEPTH_READABLE}mm recommended',
        f'  Min letter height : {MIN_LETTER_H}mm absolute / {REC_LETTER_H}mm recommended',
        f'  Min stroke width  : {MIN_STROKE}mm (= 1× nozzle)',
        f'  Overhang limit    : {OVERHANG_ANGLE_LIMIT}° from vertical',
        f'  Bed size          : {BED_X}×{BED_Y}×{BED_Z}mm',
        '',
        '--- SURFACE GROUPS (sorted best → worst for engraving) ---',
    ]
    for i, g in enumerate(groups):
        lines.append(
            f'  [{i+1}] {g.label}  score={g.engravability:.2f}'
            f'  area={g.total_area_mm2:.1f}mm²'
            f'  angle={g.angle_from_vertical:.1f}°'
            f'  faces={g.face_count}'
            f'  centroid=({g.centroid[0]:.1f},{g.centroid[1]:.1f},{g.centroid[2]:.1f})'
        )
        lines.append(f'       → {g.engrav_reason}')

    if warnings:
        lines.append('')
        lines.append('--- WARNINGS ---')
        for w in warnings:
            lines.append(f'  ⚠ {w}')

    lines.append('')
    lines.append('--- FDM ENGRAVING RULES (apply to every proposal) ---')
    lines.append('  1. Depth must be ≥ 0.5mm to be visible (≥ 0.8mm recommended).')
    lines.append('  2. Text height must be ≥ 3mm absolute (≥ 5mm recommended).')
    lines.append('  3. Stroke width must be ≥ 0.4mm (1× nozzle). Bold fonts preferred.')
    lines.append('  4. Deboss (inward carve) is easier to print than emboss (raised).')
    lines.append('  5. Text on a slope ≥ 20° will show staircase artifacts — warn the user.')
    lines.append('  6. Curved surfaces: project text onto tangent plane. Wrap text along arc.')
    lines.append('  7. Overhangs >45° need supports or reorientation — never silently accept.')
    lines.append('  8. If nothing viable, state clearly and propose: (a) reorient, (b) SLA.')

    report = GeometryReport(
        stl_path=stl_path,
        face_count=len(faces),
        bbox_x=bbox_x,
        bbox_y=bbox_y,
        bbox_z=bbox_z,
        volume_cm3=vol,
        surface_groups=groups,
        engravable_groups=engravable,
        warnings=warnings,
        text_summary='\n'.join(lines),
    )
    return report
