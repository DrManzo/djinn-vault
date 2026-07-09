"""
typography_utils.py — Adaptive letter geometry engine for FDM engraving.

Merged from typography_utils_marcus.py (physics foundation) and
typography_utils.py (PIL font measurement layer).

Pipeline:
  1. analyse_text()       — glyph difficulty table, min heights, stroke multipliers
  2. slope_projection()   — height/depth/spacing scale via 1/cos(θ), staircase risk
  3. curve_projection()   — arc length, sagitta, max chars, depth inner vs outer
  4. texture_correction() — layer line ridges, infill ghosting, wall flex buffers
  5. _measure_font_pil()  — OPTIONAL: real stroke widths from TTF via PIL (overrides table)
  6. build_advisory()     — assembles final CutAdvisory with mm values + brief
  7. full_typography_report() — master entry point, returns TypographyReport

All output in mm. No required external deps.
PIL (Pillow) used when available for real font measurements — falls back
to glyph table heuristics if PIL is unavailable or no font path given.

Machine: Calliope — Ender-3 V3 Plus
Nozzle: 0.4mm   Layer: 0.20mm std / 0.12mm acc
"""
from __future__ import annotations
import math
import pathlib
from dataclasses import dataclass, field
from typing import List, Optional

# ── Machine constants — import from geometry_utils, fall back inline ──────────
try:
    from .geometry_utils import (
        NOZZLE_DIA, LAYER_H_STD, LAYER_H_ACC,
        MIN_ENGRAVE_DEPTH, MIN_ENGRAVE_DEPTH_READABLE,
        MIN_LETTER_H, REC_LETTER_H, MIN_STROKE,
        OVERHANG_ANGLE_LIMIT,
        SurfaceGroup, WallProfile,
    )
except ImportError:
    NOZZLE_DIA                 = 0.4
    LAYER_H_STD                = 0.20
    LAYER_H_ACC                = 0.12
    MIN_ENGRAVE_DEPTH          = 0.5
    MIN_ENGRAVE_DEPTH_READABLE = 0.8
    MIN_LETTER_H               = 3.0
    REC_LETTER_H               = 5.0
    MIN_STROKE                 = 0.4
    OVERHANG_ANGLE_LIMIT       = 45.0
    SurfaceGroup               = object
    WallProfile                = object

# ── Research-backed sidewall constants ────────────────────────────────────────
# Source: 2023 HF study on 3D-printed type (Tandfonline) + 0.4mm nozzle community
# benchmarks (Prusa forum, MakerForums). Sidewall roughness (Ra ≈ layer_h × 0.55)
# means text needs extra height/stroke vs a top face to remain legible.
MIN_LETTER_H_SIDEWALL = 6.0    # hard minimum for FLAT_SIDE / CURVED_* surfaces
REC_LETTER_H_SIDEWALL = 8.0    # recommended — comfortable legibility on rough side
MIN_STROKE_SIDEWALL   = 0.6    # 1.5× nozzle — diagonal strokes below this get eaten by texture
REC_STROKE_SIDEWALL   = 0.9    # target stroke for reliable sidewall readability
MAX_ENGRAVE_DEPTH     = 1.4    # beyond this adds wall stress with no legibility gain
FRONT_ARC_DEG         = 120.0  # max reliable viewing arc on a cylinder (±60° from front)
# Lowercase glyphs with small counters that fail first on rough sidewalls
_RISKY_LOWERCASE      = set('egsaopqyb')

# PIL optional — used for real font metric extraction
try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL_OK = True
except ImportError:
    _PIL_OK = False


# ── Glyph difficulty table ────────────────────────────────────────────────────
# (min_height_mm, stroke_multiplier, notes)
_GLYPH_DIFFICULTY: dict[str, tuple[float, float, str]] = {
    'i': (3.5, 1.2, 'Thin vertical + dot — increase stroke, watch dot fill'),
    'j': (3.5, 1.2, 'Same as i + descender'),
    'l': (3.5, 1.1, 'Single stroke — clean but needs height'),
    '1': (3.5, 1.1, 'Single stroke numeral'),
    'I': (3.5, 1.0, 'Capital I — simplest glyph'),
    'o': (4.0, 1.3, 'Full loop — nozzle must complete closed path'),
    'O': (4.5, 1.3, 'Large loop — ensure wall clearance inside counter'),
    'e': (4.0, 1.4, 'Loop + crossbar — most failure-prone lowercase'),
    'E': (4.0, 1.2, 'Three crossbars — safe at 4mm+'),
    'a': (4.0, 1.3, 'Enclosed bowl + arm'),
    'g': (4.5, 1.4, 'Double-story g — avoid below 5mm'),
    'B': (4.5, 1.3, 'Double bowl — check counter fill at small sizes'),
    'R': (4.0, 1.2, 'Bowl + leg — good at 4mm+'),
    'S': (4.0, 1.3, 'S-curve — staircase risk on slopes'),
    's': (4.0, 1.4, 'Small s — most staircase-prone lowercase'),
    'W': (5.0, 1.2, 'Wide diagonal — needs full 5mm on side surfaces'),
    'w': (4.5, 1.2, 'Same — avoid on textured sides'),
    'M': (5.0, 1.2, 'Wide with diagonals'),
    'm': (4.5, 1.2, 'Three strokes — needs clean inter-stroke gap'),
    'X': (4.0, 1.3, 'Crossed diagonals — staircase on sides'),
    'x': (4.0, 1.3, 'Same'),
    'K': (4.0, 1.2, 'Diagonal arms'),
    'k': (4.0, 1.2, 'Diagonal arms'),
    'Z': (4.0, 1.2, 'Diagonal midbar'),
    'z': (4.0, 1.2, 'Same'),
    'N': (4.5, 1.2, 'Diagonal stroke'),
    'V': (4.0, 1.2, 'V-shape — needs full height'),
    'v': (4.0, 1.2, 'Same'),
    'A': (4.5, 1.2, 'Apex + crossbar'),
    "'": (5.0, 1.5, "Apostrophe — single dot at small sizes, often unreadable below 6mm"),
    '"': (5.0, 1.5, 'Quote marks — unreadable below 6mm'),
    '.': (5.0, 2.0, 'Period — prints as blob below 5mm'),
    ',': (5.0, 2.0, 'Comma — same as period'),
    '!': (4.5, 1.5, 'Exclamation — bar + dot, dot unreliable below 5mm'),
    '?': (5.0, 1.4, 'Question mark — bowl + dot'),
    '@': (7.0, 1.5, 'At sign — never below 7mm on FDM'),
    '#': (6.0, 1.3, 'Hash — four strokes, needs 6mm+'),
    '%': (6.0, 1.4, 'Percent — two loops + diagonal'),
    '&': (6.0, 1.4, 'Ampersand — complex shape'),
}
_DEFAULT_GLYPH = (MIN_LETTER_H, 1.0, 'Standard glyph')

# Font weight → stroke ratio (stroke_width / cap_height) — used when PIL unavailable
_WEIGHT_STROKE_RATIO = {
    'black': 0.18, 'extrabold': 0.16, 'heavy': 0.17, 'bold': 0.13,
    'semibold': 0.11, 'medium': 0.09, 'regular': 0.08,
    'light': 0.05, 'thin': 0.03, 'ultralight': 0.02,
}


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class GlyphAdvisory:
    char: str
    min_height_mm: float
    recommended_height_mm: float
    stroke_width_mm: float
    notes: str
    flag: bool
    measured_by_pil: bool = False   # True = stroke from real font measurement


@dataclass
class SlopeCompensation:
    surface_angle_deg: float
    height_scale: float
    depth_scale: float
    spacing_scale: float
    staircase_risk: str     # NONE / LOW / MEDIUM / HIGH
    advisory: str


@dataclass
class CurveCompensation:
    is_cylindrical: bool
    outer_radius_mm: float
    arc_length_per_char_mm: float
    recommended_char_count: int
    wrap_direction: str             # HORIZONTAL / VERTICAL
    depth_inner_mm: float
    depth_outer_mm: float
    advisory: str


@dataclass
class TextureCorrection:
    surface_type: str
    layer_line_depth_mm: float
    depth_buffer_mm: float
    recommended_depth_mm: float
    stroke_buffer_mm: float
    advisory: str


@dataclass
class FontProfile:
    """Real font metrics — populated by PIL measurement layer."""
    font_name: str
    font_path: str
    weight_class: str
    measured_stroke_ratio: float    # from real TTF, or heuristic
    is_serif: bool
    is_condensed: bool
    fdm_suitable: bool
    fdm_note: str
    pil_available: bool


@dataclass
class CutAdvisory:
    content: str
    style: str
    final_depth_mm: float
    final_height_mm: float
    final_stroke_mm: float
    letter_spacing_mm: float
    word_spacing_mm: float
    orientation_deg: float
    arc_wrap: bool
    arc_radius_mm: float
    layer_profile: str              # 'standard_0.20' | 'accuracy_0.12'
    pass_count: int
    feed_rate_advisory: str         # 'normal' | 'slow_20pct' | 'slow_40pct'
    problem_glyphs: List[str]
    warnings: List[str]
    workarounds: List[str]
    brief: str
    # Research-backed legibility gate fields
    risky_small_sidewall: bool = False   # True → Telegram must ask Javier to confirm
    case_style: str = 'Mixed'            # 'Mixed' | 'ALL_CAPS' | 'ALL_CAPS_RECOMMENDED'
    legibility_score: float = 1.0        # 0.0–1.0; < 0.6 triggers advisory


@dataclass
class TypographyReport:
    content: str
    char_count: int
    font_profile: Optional[FontProfile]
    glyph_advisories: List[GlyphAdvisory]
    slope_comp: SlopeCompensation
    curve_comp: Optional[CurveCompensation]
    texture_corr: TextureCorrection
    cut_advisory: CutAdvisory
    text_summary: str


# ── 1. Glyph analysis ─────────────────────────────────────────────────────────

def analyse_text(content: str, requested_height_mm: float = REC_LETTER_H) -> List[GlyphAdvisory]:
    advisories = []
    seen = set()
    for ch in content:
        if ch in seen or ch == ' ':
            continue
        seen.add(ch)
        min_h, stroke_mult, notes = _GLYPH_DIFFICULTY.get(ch, _DEFAULT_GLYPH)
        rec_h = max(min_h, requested_height_mm)
        stroke = round(NOZZLE_DIA * stroke_mult, 2)
        flag = requested_height_mm < min_h
        advisories.append(GlyphAdvisory(
            char=ch,
            min_height_mm=min_h,
            recommended_height_mm=rec_h,
            stroke_width_mm=stroke,
            notes=notes,
            flag=flag,
        ))
    return advisories


# ── 2. Slope compensation ─────────────────────────────────────────────────────

def slope_projection(surface_angle_deg: float) -> SlopeCompensation:
    rad = math.radians(surface_angle_deg)
    height_scale  = round(1.0 / max(math.cos(rad), 0.1), 3) if surface_angle_deg >= 1 else 1.0
    depth_scale   = round(1.0 / max(math.cos(rad), 0.1), 3)
    spacing_scale = round(1.0 / max(math.cos(rad), 0.1), 3)

    if surface_angle_deg < 10:
        staircase = 'NONE'
        advisory = 'Surface nearly horizontal. No staircase. Standard parameters apply.'
    elif surface_angle_deg < 20:
        staircase = 'LOW'
        advisory = (
            f'Slope {surface_angle_deg:.0f}°. Minor staircase on diagonal strokes. '
            f'Scale height ×{height_scale:.2f}, depth ×{depth_scale:.2f}. '
            'Recommend sans-serif bold.'
        )
    elif surface_angle_deg < 35:
        staircase = 'MEDIUM'
        advisory = (
            f'Slope {surface_angle_deg:.0f}°. Visible staircase on curves/diagonals. '
            f'Scale height ×{height_scale:.2f}, depth ×{depth_scale:.2f}, '
            f'spacing ×{spacing_scale:.2f}. '
            'Avoid S, s, O, o, e, g. Use block capitals. Slow feed 20%.'
        )
    elif surface_angle_deg < OVERHANG_ANGLE_LIMIT:
        staircase = 'HIGH'
        advisory = (
            f'Slope {surface_angle_deg:.0f}°. Severe staircase. '
            f'Height ×{height_scale:.2f}, depth ×{depth_scale:.2f}. '
            'Only straight-stroke letters (I, H, T, L, E, F) will read cleanly. '
            'Slow feed 40%. Consider W1 reorient.'
        )
    else:
        staircase = 'HIGH'
        advisory = (
            f'Slope {surface_angle_deg:.0f}° exceeds FDM limit ({OVERHANG_ANGLE_LIMIT}°). '
            'Engraving will fail. Apply W1 (reorient) or W8 (SLA).'
        )

    return SlopeCompensation(
        surface_angle_deg=surface_angle_deg,
        height_scale=height_scale,
        depth_scale=depth_scale,
        spacing_scale=spacing_scale,
        staircase_risk=staircase,
        advisory=advisory,
    )


# ── 3. Curve compensation ─────────────────────────────────────────────────────

def curve_projection(
    outer_radius_mm: float,
    content: str,
    char_height_mm: float,
    is_cylindrical: bool = True,
) -> CurveCompensation:
    if not is_cylindrical or outer_radius_mm <= 0:
        return CurveCompensation(
            is_cylindrical=False, outer_radius_mm=outer_radius_mm,
            arc_length_per_char_mm=0, recommended_char_count=len(content),
            wrap_direction='HORIZONTAL',
            depth_inner_mm=MIN_ENGRAVE_DEPTH_READABLE,
            depth_outer_mm=MIN_ENGRAVE_DEPTH_READABLE,
            advisory='Surface is not cylindrical. Standard flat projection applies.'
        )

    char_width_mm  = char_height_mm * 0.6
    spacing_mm     = char_height_mm * 0.15
    arc_per_char   = char_width_mm + spacing_mm

    # Use FRONT_ARC_DEG (120°) as the reliable viewing window — text beyond ±60° from
    # front foreshortens and counters collapse at arm's length viewing distance.
    usable_arc_mm  = 2 * math.pi * outer_radius_mm * (FRONT_ARC_DEG / 360.0)
    max_chars      = int(usable_arc_mm / arc_per_char)

    half_w  = char_width_mm / 2
    sagitta = outer_radius_mm - math.sqrt(max(0, outer_radius_mm**2 - half_w**2))

    depth_outer = round(MIN_ENGRAVE_DEPTH_READABLE + sagitta, 2)
    depth_inner = round(MIN_ENGRAVE_DEPTH_READABLE, 2)

    wrap = 'HORIZONTAL' if outer_radius_mm >= 20 and len(content) <= max_chars else 'VERTICAL'
    too_many = len(content) > max_chars

    parts = [
        f'Cylindrical. Outer radius: {outer_radius_mm:.1f}mm.',
        f'Arc/char: {arc_per_char:.1f}mm. Max chars in {FRONT_ARC_DEG:.0f}° front arc: {max_chars}.',
    ]
    if too_many:
        parts.append(
            f'"{content}" has {len(content)} chars — exceeds front-arc max ({max_chars}). '
            f'Text would extend beyond ±{FRONT_ARC_DEG/2:.0f}° and foreshorten at viewing angle. '
            'Abbreviate or reduce font size.'
        )
    parts.append(
        f'Sagitta: {sagitta:.3f}mm. Depth center: {depth_outer:.2f}mm / edge: {depth_inner:.2f}mm. '
        f'Wrap: {wrap}.'
    )

    return CurveCompensation(
        is_cylindrical=True, outer_radius_mm=outer_radius_mm,
        arc_length_per_char_mm=round(arc_per_char, 2),
        recommended_char_count=max_chars, wrap_direction=wrap,
        depth_inner_mm=depth_inner, depth_outer_mm=depth_outer,
        advisory=' '.join(parts),
    )


# ── 4. Texture correction ─────────────────────────────────────────────────────

def texture_correction(
    surface_angle_deg: float,
    layer_height_mm: float = LAYER_H_STD,
    surface_label: str = 'FLAT_TOP',
    infill_pct: int = 20,
    wall_count: int = 3,
) -> TextureCorrection:
    if surface_label == 'FLAT_TOP':
        ridge_h = layer_height_mm * 0.20
        stype = 'LAYER_LINES_LIGHT'
    elif surface_label == 'FLAT_SIDE':
        ridge_h = layer_height_mm * 0.55
        stype = 'LAYER_LINES'
    elif surface_label == 'FLAT_BOTTOM':
        ridge_h = layer_height_mm * 0.30
        stype = 'LAYER_LINES_LIGHT'
    else:
        ridge_h = layer_height_mm * 0.60
        stype = 'ROUGH'

    infill_buffer = max(0.0, (infill_pct - 40) / 100 * 0.1)
    wall_buffer   = 0.20 if wall_count < 2 else (0.10 if wall_count < 4 else 0.0)
    depth_buffer  = round(ridge_h + infill_buffer + wall_buffer, 3)
    rec_depth     = round(MIN_ENGRAVE_DEPTH_READABLE + depth_buffer, 2)
    stroke_buffer = NOZZLE_DIA * 0.5 if surface_label == 'FLAT_SIDE' else 0.0

    parts = [
        f'Surface: {stype}. Layer ridge: {ridge_h:.3f}mm at {layer_height_mm}mm layer height.',
        f'Depth buffer (ridge+infill+wall): {depth_buffer:.3f}mm. Min depth: {rec_depth:.2f}mm.',
    ]
    if stroke_buffer > 0:
        parts.append(f'Stroke buffer: +{stroke_buffer:.2f}mm. Min stroke: {MIN_STROKE+stroke_buffer:.2f}mm.')
    if infill_buffer > 0:
        parts.append(f'Infill ghosting ({infill_pct}%): +{infill_buffer:.3f}mm.')
    if wall_buffer > 0:
        parts.append(f'Low wall count ({wall_count}): +{wall_buffer:.2f}mm flex compensation.')

    return TextureCorrection(
        surface_type=stype, layer_line_depth_mm=round(ridge_h, 3),
        depth_buffer_mm=depth_buffer, recommended_depth_mm=rec_depth,
        stroke_buffer_mm=round(stroke_buffer, 2), advisory=' '.join(parts),
    )


# ── 5. PIL font measurement layer ─────────────────────────────────────────────

def _resolve_font(font_path: str) -> str:
    if pathlib.Path(font_path).exists():
        return font_path
    for d in [
        pathlib.Path('/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF'),
        pathlib.Path('/usr/share/fonts/truetype/dejavu'),
        pathlib.Path('/usr/share/fonts/truetype/liberation'),
        pathlib.Path('/usr/share/fonts/truetype/freefont'),
    ]:
        c = d / pathlib.Path(font_path).name
        if c.exists():
            return str(c)
    return font_path


def _measure_stroke_ratio_pil(font_path: str, render_h: int = 200) -> float:
    """Render 'H' at render_h px and measure thinnest stroke as fraction of height."""
    try:
        pil_font = ImageFont.truetype(font_path, render_h)
        img = Image.new('L', (render_h * 2, render_h + 20), 0)
        ImageDraw.Draw(img).text((5, 5), 'H', fill=255, font=pil_font)
        W = img.width
        arr = list(img.getdata())
        mid = render_h // 2 + 5
        row = arr[mid * W: (mid + 1) * W]
        in_s, start, strokes = False, 0, []
        for i, px in enumerate(row):
            if px > 64 and not in_s:
                in_s, start = True, i
            elif px <= 64 and in_s:
                in_s = False
                strokes.append(i - start)
        if in_s:
            strokes.append(len(row) - start)
        if strokes:
            ratio = min(strokes) / render_h
            if 0.03 < ratio < 0.40:
                return ratio
    except Exception:
        pass
    return 0.0


def _build_font_profile(font_path: str, font_height_mm: float) -> Optional[FontProfile]:
    """Build FontProfile using PIL if available, else return None."""
    if not font_path:
        return None

    font_path = _resolve_font(font_path)
    name      = pathlib.Path(font_path).stem
    nl        = name.lower().replace('-', '').replace('_', '')

    weight = 'regular'
    for w in _WEIGHT_STROKE_RATIO:
        if w in nl:
            weight = w
            break

    is_serif     = any(w in nl for w in ('serif', 'times', 'georgia', 'free'))
    is_condensed = any(w in nl for w in ('condensed', 'narrow', 'cond'))
    fdm_suitable = any(w in nl for w in ('black', 'heavy', 'extrabold', 'bold'))

    if is_serif:
        fdm_note = f'Serif font — needs ≥7mm to preserve serifs on FDM'
        fdm_suitable = fdm_suitable and font_height_mm >= 7.0
    elif any(w in nl for w in ('light', 'thin', 'ultralight')):
        fdm_note = f'Light/thin weight — strokes will be lost at <8mm'
        fdm_suitable = False
    else:
        fdm_note = f'Sans-serif {"bold/black" if fdm_suitable else "regular"} — '
        fdm_note += 'FDM suitable' if fdm_suitable else 'acceptable at ≥5mm'

    # Measure real stroke ratio if PIL available
    measured = 0.0
    pil_ok = False
    if _PIL_OK and pathlib.Path(font_path).exists():
        measured = _measure_stroke_ratio_pil(font_path)
        pil_ok = measured > 0

    stroke_ratio = measured if pil_ok else _WEIGHT_STROKE_RATIO.get(weight, 0.09)

    return FontProfile(
        font_name=name, font_path=font_path, weight_class=weight,
        measured_stroke_ratio=stroke_ratio,
        is_serif=is_serif, is_condensed=is_condensed,
        fdm_suitable=fdm_suitable, fdm_note=fdm_note,
        pil_available=pil_ok,
    )


def _apply_font_to_glyphs(
    glyphs: List[GlyphAdvisory],
    font_profile: FontProfile,
    font_height_mm: float,
) -> List[GlyphAdvisory]:
    """
    Override glyph stroke_width_mm with real measured values from PIL.
    This supersedes the table multipliers for accurate per-font advice.
    """
    if not font_profile or not font_profile.pil_available:
        return glyphs

    ratio = font_profile.measured_stroke_ratio
    updated = []
    for g in glyphs:
        _, table_mult, _ = _GLYPH_DIFFICULTY.get(g.char, _DEFAULT_GLYPH)
        # Use measured ratio × table multiplier (thin chars still get their penalty)
        real_stroke = round(font_height_mm * ratio * table_mult, 3)
        updated.append(GlyphAdvisory(
            char=g.char,
            min_height_mm=g.min_height_mm,
            recommended_height_mm=g.recommended_height_mm,
            stroke_width_mm=real_stroke,
            notes=g.notes,
            flag=g.flag or (real_stroke < MIN_STROKE),
            measured_by_pil=True,
        ))
    return updated


# ── 6. Legibility score ───────────────────────────────────────────────────────

def _legibility_score(
    height_mm: float,
    stroke_mm: float,
    depth_mm: float,
    is_sidewall: bool,
    n_problem_glyphs: int,
    surface_angle_deg: float,
) -> float:
    """
    0.0–1.0 estimate of likely print legibility.
    < 0.6 → advisory warning to Javier before committing to print.
    """
    score = 1.0
    min_h = MIN_LETTER_H_SIDEWALL if is_sidewall else MIN_LETTER_H
    rec_h = REC_LETTER_H_SIDEWALL if is_sidewall else REC_LETTER_H
    min_s = MIN_STROKE_SIDEWALL   if is_sidewall else MIN_STROKE

    if height_mm < min_h:
        score -= 0.40
    elif height_mm < rec_h:
        score -= 0.15

    if stroke_mm < min_s:
        score -= 0.30
    elif stroke_mm < min_s * 1.4:
        score -= 0.10

    if depth_mm < MIN_ENGRAVE_DEPTH:
        score -= 0.25
    elif depth_mm < MIN_ENGRAVE_DEPTH_READABLE:
        score -= 0.10

    if is_sidewall:
        score -= 0.08           # sidewall texture always costs something

    score -= n_problem_glyphs * 0.04

    if surface_angle_deg > 70:  # steep side or overhang
        score -= 0.12

    return round(max(0.0, min(1.0, score)), 2)


# ── 7. Final cut advisory ─────────────────────────────────────────────────────

def build_advisory(
    content: str,
    surface_group,
    wall_profile,
    requested_height_mm: float = REC_LETTER_H,
    requested_depth_mm: float  = MIN_ENGRAVE_DEPTH_READABLE,
    requested_stroke_mm: float = MIN_STROKE,
    style: str = 'deboss',
    layer_height_mm: float = LAYER_H_STD,
    infill_pct: int = 20,
    wall_count: int = 3,
    font_profile: Optional[FontProfile] = None,
) -> CutAdvisory:
    glyphs = analyse_text(content, requested_height_mm)
    if font_profile:
        glyphs = _apply_font_to_glyphs(glyphs, font_profile, requested_height_mm)

    flagged          = [g for g in glyphs if g.flag]
    max_stroke_needed = max((g.stroke_width_mm for g in glyphs), default=MIN_STROKE)
    max_min_height   = max((g.min_height_mm for g in glyphs), default=MIN_LETTER_H)

    angle   = getattr(surface_group, 'angle_from_vertical', 0.0)
    label   = getattr(surface_group, 'label', 'FLAT_TOP')
    slope   = slope_projection(angle)

    is_cyl  = getattr(wall_profile, 'is_cylindrical', False) if wall_profile else False
    outer_r = getattr(wall_profile, 'outer_r_max', 0.0) if wall_profile else 0.0
    curve   = curve_projection(outer_r, content, requested_height_mm, is_cyl)

    texture = texture_correction(angle, layer_height_mm, label, infill_pct, wall_count)

    # Height
    base_height  = max(requested_height_mm, max_min_height)
    final_height = round(base_height * slope.height_scale, 2)
    final_height = max(final_height, MIN_LETTER_H)

    # Depth
    base_depth  = max(requested_depth_mm, texture.recommended_depth_mm)
    final_depth = round(base_depth * slope.depth_scale, 2)
    if wall_profile and hasattr(wall_profile, 'prime_zone_wall'):
        max_safe = wall_profile.prime_zone_wall * 0.50
        if final_depth > max_safe:
            final_depth = round(max_safe, 2)

    # Stroke — use PIL-measured value if available, else table
    final_stroke = round(
        max(requested_stroke_mm, max_stroke_needed, MIN_STROKE) + texture.stroke_buffer_mm,
        2,
    )

    # If font profile says font is unsuitable, add warning
    warnings   = []
    workarounds = []

    if font_profile and not font_profile.fdm_suitable:
        warnings.append(
            f'Font {font_profile.font_name} not ideal for FDM: {font_profile.fdm_note}. '
            f'Recommend Roboto-Black or DejaVuSans-Bold.'
        )

    for g in flagged:
        warnings.append(
            f"Glyph '{g.char}' needs ≥{g.min_height_mm}mm "
            f"(requested {requested_height_mm}mm): {g.notes}"
            + (' [PIL-measured]' if g.measured_by_pil else '')
        )

    # ── Sidewall hard rules (research-backed) ────────────────────────────────
    is_sidewall          = label in ('FLAT_SIDE', 'CURVED_CONVEX', 'CURVED_CONCAVE')
    risky_small_sidewall = False
    case_style           = 'ALL_CAPS' if content == content.upper() and content.strip() else 'Mixed'
    leg_score            = 1.0  # computed below

    if is_sidewall:
        # Height gate
        if final_height < MIN_LETTER_H_SIDEWALL:
            risky_small_sidewall = True
            warnings.append(
                f'HEIGHT RISK: {final_height}mm < sidewall minimum {MIN_LETTER_H_SIDEWALL}mm. '
                f'Layer texture (~{LAYER_H_STD*0.55:.2f}mm ridge) will fragment strokes. '
                f'Upgrade to ≥{REC_LETTER_H_SIDEWALL}mm for reliable result.'
            )
            final_height = max(final_height, MIN_LETTER_H_SIDEWALL)
        elif final_height < REC_LETTER_H_SIDEWALL:
            warnings.append(
                f'Height {final_height}mm is marginal for sidewall. '
                f'≥{REC_LETTER_H_SIDEWALL}mm recommended. Proceed with care.'
            )

        # Stroke gate
        if final_stroke < MIN_STROKE_SIDEWALL:
            risky_small_sidewall = True
            warnings.append(
                f'STROKE RISK: {final_stroke}mm < sidewall minimum {MIN_STROKE_SIDEWALL}mm. '
                f'Diagonal strokes get chewed by 0.2mm layer ridges. '
                f'Target ≥{REC_STROKE_SIDEWALL}mm.'
            )
            final_stroke = max(final_stroke, MIN_STROKE_SIDEWALL)

        # Depth cap — beyond MAX_ENGRAVE_DEPTH adds wall stress, not readability
        if final_depth > MAX_ENGRAVE_DEPTH:
            warnings.append(
                f'Depth capped {final_depth}mm → {MAX_ENGRAVE_DEPTH}mm. '
                f'Beyond {MAX_ENGRAVE_DEPTH}mm adds wall stress without legibility gain.'
            )
            final_depth = MAX_ENGRAVE_DEPTH

        # Case style recommendation
        risky_chars = sorted(set(ch for ch in content if ch in _RISKY_LOWERCASE))
        if risky_chars:
            case_style = 'ALL_CAPS_RECOMMENDED'
            warnings.append(
                f'CASE RISK: lowercase {risky_chars} have small counters that fail on rough sidewalls '
                f'(e/g/s/a/o/p/q/y/b). Strongly recommend ALL CAPS to remove these glyphs.'
            )
        elif content == content.upper():
            case_style = 'ALL_CAPS'

    # ── Legibility score (computed for all surfaces, used as safety gate) ───────
    leg_score = _legibility_score(
        final_height, final_stroke, final_depth,
        is_sidewall, len(flagged), angle,
    )
    if leg_score < 0.6 and not risky_small_sidewall:
        risky_small_sidewall = True
        warnings.append(
            f'LEGIBILITY SCORE {leg_score:.2f} < 0.60. Combined glyph/size/stroke risk '
            f'is high. Confirm with Javier before printing.'
        )

    if slope.staircase_risk in ('MEDIUM', 'HIGH'):
        warnings.append(f'Staircase {slope.staircase_risk} at {angle:.0f}°. {slope.advisory}')
        if slope.staircase_risk == 'HIGH':
            workarounds.append('W1 — Reorient model so target surface faces up')

    if is_cyl and len(content) > curve.recommended_char_count:
        warnings.append(
            f'Text too long for arc: {len(content)} chars, max {curve.recommended_char_count}. '
            'Abbreviate or reduce font size.'
        )
        workarounds.append('W5 — Line-wrap text along arc')

    if wall_profile and hasattr(wall_profile, 'prime_zone_wall'):
        max_safe = wall_profile.prime_zone_wall * 0.50
        if requested_depth_mm > max_safe:
            warnings.append(
                f'Requested depth {requested_depth_mm}mm exceeds 50% of wall '
                f'({wall_profile.prime_zone_wall}mm). Capped at {max_safe:.2f}mm.'
            )

    letter_spacing = round(final_height * 0.12 * slope.spacing_scale, 2)
    word_spacing   = round(final_height * 0.60 * slope.spacing_scale, 2)
    arc_wrap       = is_cyl and outer_r > 0
    layer_profile  = 'accuracy_0.12' if final_depth <= 0.6 else 'standard_0.20'
    pass_count     = 2 if final_stroke >= NOZZLE_DIA * 1.5 else 1
    feed           = ('slow_40pct' if slope.staircase_risk == 'HIGH'
                      else 'slow_20pct' if slope.staircase_risk == 'MEDIUM' or arc_wrap
                      else 'normal')

    brief_parts = [
        f'Content: "{content}" ({len(content)} chars).',
        f'Surface: {label} at {angle:.0f}° from horizontal.',
        f'Final spec: {style} / depth {final_depth}mm / height {final_height}mm / stroke {final_stroke}mm.',
        f'Spacing: letter {letter_spacing}mm / word {word_spacing}mm.',
    ]
    if arc_wrap:
        brief_parts.append(
            f'Arc wrap: r={curve.outer_radius_mm:.1f}mm, {curve.wrap_direction}, '
            f'depth {curve.depth_outer_mm}mm center / {curve.depth_inner_mm}mm edge.'
        )
    if slope.height_scale != 1.0 or slope.depth_scale != 1.0:
        brief_parts.append(
            f'Slope compensation: height ×{slope.height_scale:.2f}, depth ×{slope.depth_scale:.2f}.'
        )
    brief_parts.append(
        f'Texture buffer: +{texture.depth_buffer_mm:.2f}mm. '
        f'Layer: {layer_profile}. Passes: {pass_count}. Feed: {feed}.'
    )
    if font_profile:
        src = 'PIL-measured' if font_profile.pil_available else 'table-estimated'
        brief_parts.append(
            f'Font {font_profile.font_name} ({font_profile.weight_class}): '
            f'stroke ratio {font_profile.measured_stroke_ratio:.2f} [{src}].'
        )
    if warnings:
        brief_parts.append('WARNINGS: ' + ' | '.join(warnings))
    if workarounds:
        brief_parts.append('WORKAROUNDS: ' + ', '.join(workarounds))

    return CutAdvisory(
        content=content, style=style,
        final_depth_mm=final_depth, final_height_mm=final_height,
        final_stroke_mm=final_stroke,
        letter_spacing_mm=letter_spacing, word_spacing_mm=word_spacing,
        orientation_deg=0.0, arc_wrap=arc_wrap,
        arc_radius_mm=outer_r if arc_wrap else 0.0,
        layer_profile=layer_profile, pass_count=pass_count,
        feed_rate_advisory=feed,
        problem_glyphs=[g.char for g in flagged],
        warnings=warnings, workarounds=workarounds,
        brief=' '.join(brief_parts),
        risky_small_sidewall=risky_small_sidewall,
        case_style=case_style,
        legibility_score=leg_score,
    )


# ── 7. Master entry point ─────────────────────────────────────────────────────

def full_typography_report(
    content: str,
    surface_group,
    wall_profile=None,
    requested_height_mm: float = REC_LETTER_H,
    requested_depth_mm: float  = MIN_ENGRAVE_DEPTH_READABLE,
    requested_stroke_mm: float = MIN_STROKE,
    style: str = 'deboss',
    layer_height_mm: float = LAYER_H_STD,
    infill_pct: int = 20,
    wall_count: int = 3,
    font_path: str = None,
) -> TypographyReport:
    """
    Master entry point. Accepts surface_group and wall_profile from geometry_utils.
    Optional font_path enables real PIL font measurement.
    """
    font_profile = _build_font_profile(font_path, requested_height_mm) if font_path else None

    glyphs  = analyse_text(content, requested_height_mm)
    if font_profile:
        glyphs = _apply_font_to_glyphs(glyphs, font_profile, requested_height_mm)

    angle   = getattr(surface_group, 'angle_from_vertical', 0.0)
    label   = getattr(surface_group, 'label', 'FLAT_TOP')
    is_cyl  = getattr(wall_profile, 'is_cylindrical', False) if wall_profile else False
    outer_r = getattr(wall_profile, 'outer_r_max', 0.0) if wall_profile else 0.0

    slope   = slope_projection(angle)
    curve   = curve_projection(outer_r, content, requested_height_mm, is_cyl)
    texture = texture_correction(angle, layer_height_mm, label, infill_pct, wall_count)
    cut     = build_advisory(
        content, surface_group, wall_profile,
        requested_height_mm, requested_depth_mm, requested_stroke_mm,
        style, layer_height_mm, infill_pct, wall_count, font_profile,
    )

    lines = [
        '=== TYPOGRAPHY ANALYSIS ===',
        f'Content        : "{content}"',
        f'Char count     : {len(content)} (non-space: {len(content.replace(" ",""))})',
        f'Requested spec : height={requested_height_mm}mm  depth={requested_depth_mm}mm  '
        f'stroke={requested_stroke_mm}mm  style={style}',
    ]

    if font_profile:
        src = 'PIL-measured' if font_profile.pil_available else 'table-estimated'
        lines += [
            '',
            '--- FONT PROFILE ---',
            f'  Font       : {font_profile.font_name} ({font_profile.weight_class})',
            f'  FDM suited : {"YES" if font_profile.fdm_suitable else "NO — " + font_profile.fdm_note}',
            f'  Stroke ratio: {font_profile.measured_stroke_ratio:.3f} [{src}]'
            f' → {requested_height_mm * font_profile.measured_stroke_ratio:.2f}mm strokes at {requested_height_mm}mm',
        ]

    flagged = [g for g in glyphs if g.flag]
    lines += ['', '--- GLYPH ANALYSIS ---']
    if flagged:
        for g in flagged:
            src = ' [PIL]' if g.measured_by_pil else ''
            lines.append(
                f"  ⚠ '{g.char}' FLAG: min={g.min_height_mm}mm  "
                f"stroke={g.stroke_width_mm}mm{src}  {g.notes}"
            )
    else:
        lines.append('  ✓ All glyphs viable at requested height.')

    lines += [
        '', '--- SLOPE COMPENSATION ---',
        f'  Angle       : {angle:.1f}° from horizontal',
        f'  Staircase   : {slope.staircase_risk}',
        f'  Scales      : height ×{slope.height_scale:.3f}  depth ×{slope.depth_scale:.3f}  '
        f'spacing ×{slope.spacing_scale:.3f}',
        f'  Advisory    : {slope.advisory}',
        '', '--- CURVE COMPENSATION ---',
        f'  Cylindrical : {curve.is_cylindrical}',
    ]
    if curve.is_cylindrical:
        lines += [
            f'  Outer radius: {curve.outer_radius_mm:.1f}mm',
            f'  Arc/char    : {curve.arc_length_per_char_mm:.2f}mm',
            f'  Max chars   : {curve.recommended_char_count}',
            f'  Depth center: {curve.depth_outer_mm:.2f}mm / edge: {curve.depth_inner_mm:.2f}mm',
            f'  Wrap        : {curve.wrap_direction}',
        ]
    lines.append(f'  Advisory    : {curve.advisory}')

    lines += [
        '', '--- TEXTURE CORRECTION ---',
        f'  Type        : {texture.surface_type}',
        f'  Ridge height: {texture.layer_line_depth_mm:.3f}mm',
        f'  Depth buffer: +{texture.depth_buffer_mm:.3f}mm',
        f'  Stroke buf  : +{texture.stroke_buffer_mm:.2f}mm',
        f'  Advisory    : {texture.advisory}',
        '',
        '--- FINAL CUT ADVISORY (use these values — do not substitute) ---',
        f'  Style       : {cut.style}',
        f'  Depth       : {cut.final_depth_mm}mm',
        f'  Height      : {cut.final_height_mm}mm',
        f'  Stroke      : {cut.final_stroke_mm}mm',
        f'  Spacing     : letter {cut.letter_spacing_mm}mm / word {cut.word_spacing_mm}mm',
        f'  Arc wrap    : {cut.arc_wrap}  r={cut.arc_radius_mm:.1f}mm',
        f'  Layer       : {cut.layer_profile}',
        f'  Passes      : {cut.pass_count}',
        f'  Feed        : {cut.feed_rate_advisory}',
    ]
    if cut.problem_glyphs:
        lines.append(f'  Problems    : {", ".join(cut.problem_glyphs)}')
    lines.append(f'  Legibility  : {cut.legibility_score:.2f}/1.00'
                 + ('  ⚠ RISKY — confirm with Javier' if cut.risky_small_sidewall else '  ✓'))
    lines.append(f'  Case style  : {cut.case_style}')
    if cut.warnings:
        lines.append('  WARNINGS:')
        for w in cut.warnings:
            lines.append(f'    ⚠ {w}')
    if cut.workarounds:
        lines.append('  WORKAROUNDS:')
        for wa in cut.workarounds:
            lines.append(f'    🔧 {wa}')
    lines += ['', f'  BRIEF: {cut.brief}']

    return TypographyReport(
        content=content,
        char_count=len(content),
        font_profile=font_profile,
        glyph_advisories=glyphs,
        slope_comp=slope,
        curve_comp=curve if curve.is_cylindrical else None,
        texture_corr=texture,
        cut_advisory=cut,
        text_summary='\n'.join(lines),
    )
