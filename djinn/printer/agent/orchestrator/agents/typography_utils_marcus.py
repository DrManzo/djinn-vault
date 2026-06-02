"""
typography_utils_marcus.py — Adaptive letter geometry engine for FDM engraving.

Companion to geometry_utils.py. Where geometry_utils reads the SURFACE,
this module reads the TEXT and adapts every letter parameter to survive
that surface — slope, curvature, texture depth, wall thickness, and
nozzle physics — and returns exact cut advisories the engraver executes.

Pipeline (called by engrave.py after full_geometry_report()):
  1. analyse_text()         — parse the string, detect problem glyphs
  2. surface_compensation() — adjust depth/stroke per surface type
  3. slope_projection()     — recalculate height/spacing on slanted face
  4. curve_projection()     — wrap letters around cylindrical surface
  5. texture_correction()   — add depth buffer for rough/layered surfaces
  6. build_advisory()       — assemble final TypographyReport

All output is in mm. All decisions reference Calliope machine constants
imported from geometry_utils_marcus (falls back to inline constants).

No external dependencies. Pure Python 3.9+.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# ── Try to import machine constants from geometry_utils ───────────────────────
try:
    from .geometry_utils import (
        NOZZLE_DIA, LAYER_H_STD, LAYER_H_ACC,
        MIN_ENGRAVE_DEPTH, MIN_ENGRAVE_DEPTH_READABLE,
        MIN_LETTER_H, REC_LETTER_H, MIN_STROKE,
        OVERHANG_ANGLE_LIMIT,
        SurfaceGroup, WallProfile,
    )
except ImportError:
    # Standalone fallback — Calliope / Ender-3 V3 Plus
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


# ── Glyph difficulty table ─────────────────────────────────────────────────────
# Each entry: (min_height_mm, stroke_multiplier, notes)
# Glyphs that are hard to print cleanly get higher minimums.
_GLYPH_DIFFICULTY: dict[str, tuple[float, float, str]] = {
    # Ultra-thin serifs / enclosed counters
    'i': (3.5, 1.2, 'Thin vertical + dot — increase stroke, watch dot fill'),
    'j': (3.5, 1.2, 'Same as i + descender'),
    'l': (3.5, 1.1, 'Single stroke — clean but needs height'),
    '1': (3.5, 1.1, 'Single stroke numeral'),
    'I': (3.5, 1.0, 'Capital I — simplest glyph'),
    # Enclosed loops — hardest for FDM deboss
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
    # Diagonals — worst for FDM staircase on non-top surfaces
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
    # Punctuation / symbols — often omitted at scale
    "'": (5.0, 1.5, 'Apostrophe — single dot at small sizes, often unreadable below 6mm'),
    '"': (5.0, 1.5, 'Quote marks — unreadable below 6mm'),
    '.': (5.0, 2.0, 'Period — prints as blob below 5mm, omit or enlarge'),
    ',': (5.0, 2.0, 'Comma — same as period'),
    '!': (4.5, 1.5, 'Exclamation — bar + dot, dot unreliable below 5mm'),
    '?': (5.0, 1.4, 'Question mark — bowl + dot'),
    '@': (7.0, 1.5, 'At sign — never below 7mm on FDM'),
    '#': (6.0, 1.3, 'Hash — four strokes, needs 6mm+'),
    '%': (6.0, 1.4, 'Percent — two loops + diagonal'),
    '&': (6.0, 1.4, 'Ampersand — complex shape'),
}

_DEFAULT_GLYPH = (MIN_LETTER_H, 1.0, 'Standard glyph')


@dataclass
class GlyphAdvisory:
    char: str
    min_height_mm: float
    recommended_height_mm: float
    stroke_width_mm: float
    notes: str
    flag: bool   # True = this glyph needs special attention


@dataclass
class SlopeCompensation:
    surface_angle_deg: float    # angle of surface from horizontal
    height_scale: float         # multiply requested height by this
    depth_scale: float          # multiply requested depth by this
    spacing_scale: float        # multiply inter-letter spacing by this
    staircase_risk: str         # NONE / LOW / MEDIUM / HIGH
    advisory: str


@dataclass
class CurveCompensation:
    is_cylindrical: bool
    outer_radius_mm: float
    arc_length_per_char_mm: float   # how much arc each char occupies
    recommended_char_count: int     # max chars that fit cleanly
    wrap_direction: str             # HORIZONTAL / VERTICAL
    depth_inner_mm: float           # depth needed at inner arc edge
    depth_outer_mm: float           # depth at outer arc edge
    advisory: str


@dataclass
class TextureCorrection:
    surface_type: str           # SMOOTH / LAYER_LINES / ROUGH / TEXTURED
    layer_line_depth_mm: float  # estimated layer line ridge height
    depth_buffer_mm: float      # extra depth needed to punch through texture
    recommended_depth_mm: float # base depth + buffer
    stroke_buffer_mm: float     # extra stroke width for texture bite
    advisory: str


@dataclass
class CutAdvisory:
    """
    Final per-engraving cut instruction set.
    Everything the engraver needs — depth, width, height, spacing,
    style recommendation, and a plain-English brief.
    """
    content: str
    style: str                      # 'deboss' | 'emboss'
    final_depth_mm: float
    final_height_mm: float
    final_stroke_mm: float
    letter_spacing_mm: float
    word_spacing_mm: float
    orientation_deg: float
    arc_wrap: bool
    arc_radius_mm: float
    layer_profile: str              # 'standard_0.20' | 'accuracy_0.12'
    pass_count: int                 # recommended nozzle passes per stroke
    feed_rate_advisory: str         # 'normal' | 'slow_20pct' | 'slow_40pct'
    problem_glyphs: List[str]
    warnings: List[str]
    workarounds: List[str]
    brief: str                      # 1-paragraph human summary


@dataclass
class TypographyReport:
    content: str
    char_count: int
    glyph_advisories: List[GlyphAdvisory]
    slope_comp: SlopeCompensation
    curve_comp: Optional[CurveCompensation]
    texture_corr: TextureCorrection
    cut_advisory: CutAdvisory
    text_summary: str   # full human-readable block for LLM injection


# ── 1. Glyph analysis ─────────────────────────────────────────────────────────

def analyse_text(content: str, requested_height_mm: float = REC_LETTER_H) -> List[GlyphAdvisory]:
    """
    For every unique character in content, compute minimum viable height,
    recommended height, required stroke width, and whether it needs a flag.
    """
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
    """
    When a surface is tilted, letters appear compressed perpendicular
    to the slope direction. Compensate by scaling up.

    surface_angle_deg: angle from horizontal (0=flat top, 90=vertical wall)
    """
    rad = math.radians(surface_angle_deg)

    # Height compression: letters appear cos(angle) shorter across the slope
    # We need to print them 1/cos(angle) taller to look right
    if surface_angle_deg < 1:
        height_scale = 1.0
    else:
        height_scale = round(1.0 / max(math.cos(rad), 0.1), 3)

    # Depth scale: on a slope, the nozzle cuts at an angle.
    # Effective depth = requested_depth * cos(angle)
    # So we need to request depth / cos(angle) to get the desired effective depth
    depth_scale = round(1.0 / max(math.cos(rad), 0.1), 3)

    # Spacing: inter-letter gaps also compress on slope
    spacing_scale = round(1.0 / max(math.cos(rad), 0.1), 3)

    # Staircase risk by FDM layer lines
    if surface_angle_deg < 10:
        staircase = 'NONE'
        advisory = 'Surface nearly horizontal. No staircase. Standard parameters apply.'
    elif surface_angle_deg < 20:
        staircase = 'LOW'
        advisory = (
            f'Slope {surface_angle_deg:.0f}°. Minor staircase on diagonal strokes. '
            f'Scale height ×{height_scale:.2f}, depth ×{depth_scale:.2f}. '
            'Recommend sans-serif, bold weight.'
        )
    elif surface_angle_deg < 35:
        staircase = 'MEDIUM'
        advisory = (
            f'Slope {surface_angle_deg:.0f}°. Visible staircase on curves and diagonals. '
            f'Scale height ×{height_scale:.2f}, depth ×{depth_scale:.2f}, '
            f'spacing ×{spacing_scale:.2f}. '
            'Avoid S, s, O, o, e, g. Use block capitals only. Slow feed 20%.'
        )
    elif surface_angle_deg < OVERHANG_ANGLE_LIMIT:
        staircase = 'HIGH'
        advisory = (
            f'Slope {surface_angle_deg:.0f}°. Severe staircase. '
            f'Height ×{height_scale:.2f} ({height_scale:.2f}× requested). '
            f'Depth ×{depth_scale:.2f}. '
            'Only straight-stroke letters (I, H, T, L, E, F) will read cleanly. '
            'Slow feed 40%. Consider reorienting model (Workaround W1).'
        )
    else:
        staircase = 'HIGH'
        advisory = (
            f'Slope {surface_angle_deg:.0f}° exceeds FDM overhang limit ({OVERHANG_ANGLE_LIMIT}°). '
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
    """
    For cylindrical/curved surfaces: compute arc-wrap geometry.
    Determines how many chars fit, depth difference inner vs outer,
    and whether to wrap horizontally or stack vertically.
    """
    if not is_cylindrical or outer_radius_mm <= 0:
        return CurveCompensation(
            is_cylindrical=False,
            outer_radius_mm=outer_radius_mm,
            arc_length_per_char_mm=0,
            recommended_char_count=len(content),
            wrap_direction='HORIZONTAL',
            depth_inner_mm=MIN_ENGRAVE_DEPTH_READABLE,
            depth_outer_mm=MIN_ENGRAVE_DEPTH_READABLE,
            advisory='Surface is not cylindrical. Standard flat projection applies.'
        )

    # Approximate char width = 0.6 × char_height for proportional font
    char_width_mm = char_height_mm * 0.6
    spacing_mm = char_height_mm * 0.15  # inter-char gap
    arc_per_char = char_width_mm + spacing_mm

    # How many chars fit in 270° usable arc (leave 90° for seam/grip)
    usable_arc_deg = 270.0
    usable_arc_mm = 2 * math.pi * outer_radius_mm * (usable_arc_deg / 360.0)
    max_chars = int(usable_arc_mm / arc_per_char)

    # On a curve, the nozzle tip at the outer radius cuts shallower than
    # the inner radius because the surface curves away.
    # For a deboss: depth at the crest of each letter = nominal depth.
    # At the letter edges, effective depth is reduced by the sagitta:
    #   sagitta = r - sqrt(r² - (w/2)²)
    half_w = char_width_mm / 2
    sagitta = outer_radius_mm - math.sqrt(max(0, outer_radius_mm**2 - half_w**2))

    # To maintain MIN_ENGRAVE_DEPTH_READABLE at the edges, increase center depth
    depth_outer = round(MIN_ENGRAVE_DEPTH_READABLE + sagitta, 2)
    depth_inner = round(MIN_ENGRAVE_DEPTH_READABLE, 2)  # center of letter

    # Wrap direction: if radius > 20mm and char count > 4, wrap horizontally.
    # For small radii or short strings, vertical stacking is safer.
    wrap = 'HORIZONTAL' if outer_radius_mm >= 20 and len(content) <= max_chars else 'VERTICAL'

    too_many = len(content) > max_chars
    advisory_parts = [
        f'Cylindrical surface. Outer radius: {outer_radius_mm:.1f}mm.',
        f'Arc per character: {arc_per_char:.1f}mm.',
        f'Max characters in {usable_arc_deg:.0f}° usable arc: {max_chars}.',
    ]
    if too_many:
        advisory_parts.append(
            f'String "{content}" has {len(content)} chars — exceeds {max_chars} max. '
            'Abbreviate, reduce font size, or use two lines.'
        )
    advisory_parts.append(
        f'Sagitta at char edge: {sagitta:.3f}mm. '
        f'Recommended depth: {depth_outer:.2f}mm (center) to {depth_inner:.2f}mm (edge). '
        f'Nozzle must follow arc path — advise slicer to use cylindrical engraving mode.'
    )
    advisory_parts.append(f'Wrap direction: {wrap}.')

    return CurveCompensation(
        is_cylindrical=is_cylindrical,
        outer_radius_mm=outer_radius_mm,
        arc_length_per_char_mm=round(arc_per_char, 2),
        recommended_char_count=max_chars,
        wrap_direction=wrap,
        depth_inner_mm=depth_inner,
        depth_outer_mm=depth_outer,
        advisory=' '.join(advisory_parts),
    )


# ── 4. Texture correction ─────────────────────────────────────────────────────

def texture_correction(
    surface_angle_deg: float,
    layer_height_mm: float = LAYER_H_STD,
    surface_label: str = 'FLAT_TOP',
    infill_pct: int = 20,
    wall_count: int = 3,
) -> TextureCorrection:
    """
    FDM surfaces are not smooth. Layer lines, infill ghosting, and
    surface angle all create texture that fights engraving legibility.

    Returns depth buffer and stroke buffer needed to punch through the
    surface texture and produce clean readable cuts.

    surface_label: FLAT_TOP / FLAT_SIDE / FLAT_BOTTOM
    layer_height_mm: the actual layer height used for this print
    """
    # Layer line ridge height = ~50% of layer height on side surfaces,
    # ~20% on top (smoothed by nozzle wipe), ~0 on top with ironing.
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

    # Infill ghosting: high infill can cause ridges from pressure buildup.
    # Add buffer proportional to infill density above 40%.
    infill_buffer = max(0.0, (infill_pct - 40) / 100 * 0.1)

    # Wall count: fewer walls = more flex = engrave cuts shallower than requested.
    # Compensate: wall_count < 2 adds 0.2mm, wall_count 2-3 adds 0.1mm.
    wall_buffer = 0.20 if wall_count < 2 else (0.10 if wall_count < 4 else 0.0)

    depth_buffer = round(ridge_h + infill_buffer + wall_buffer, 3)
    rec_depth = round(MIN_ENGRAVE_DEPTH_READABLE + depth_buffer, 2)

    # Stroke buffer: on textured surfaces, strokes narrower than 2× nozzle
    # get partially filled by surface ridges. Buffer = 0.5× nozzle on sides.
    stroke_buffer = NOZZLE_DIA * 0.5 if surface_label == 'FLAT_SIDE' else 0.0

    advisory_parts = [
        f'Surface type: {stype}.',
        f'Layer line ridge height: {ridge_h:.3f}mm (at {layer_height_mm}mm layer height).',
        f'Depth buffer (ridge + infill + wall): {depth_buffer:.3f}mm.',
        f'Recommended minimum depth: {rec_depth:.2f}mm.',
    ]
    if stroke_buffer > 0:
        advisory_parts.append(
            f'Stroke buffer: +{stroke_buffer:.2f}mm on side surfaces — '
            f'minimum stroke {MIN_STROKE + stroke_buffer:.2f}mm.'
        )
    if infill_buffer > 0:
        advisory_parts.append(
            f'Infill ghosting risk (infill={infill_pct}%): +{infill_buffer:.3f}mm buffer applied.'
        )
    if wall_buffer > 0:
        advisory_parts.append(
            f'Low wall count ({wall_count} walls): +{wall_buffer:.2f}mm depth buffer for flex compensation.'
        )
    if rec_depth > 1.5:
        advisory_parts.append(
            'WARNING: recommended depth > 1.5mm. Check wall thickness — '
            'do not exceed 50% of wall thickness.'
        )

    return TextureCorrection(
        surface_type=stype,
        layer_line_depth_mm=round(ridge_h, 3),
        depth_buffer_mm=depth_buffer,
        recommended_depth_mm=rec_depth,
        stroke_buffer_mm=round(stroke_buffer, 2),
        advisory=' '.join(advisory_parts),
    )


# ── 5. Final cut advisory ─────────────────────────────────────────────────────

def build_advisory(
    content: str,
    surface_group,           # SurfaceGroup from geometry_utils
    wall_profile,            # WallProfile from geometry_utils (may be None)
    requested_height_mm: float = REC_LETTER_H,
    requested_depth_mm: float = MIN_ENGRAVE_DEPTH_READABLE,
    requested_stroke_mm: float = MIN_STROKE,
    style: str = 'deboss',
    layer_height_mm: float = LAYER_H_STD,
    infill_pct: int = 20,
    wall_count: int = 3,
) -> CutAdvisory:
    """
    Combines glyph analysis + slope + curve + texture into a single
    CutAdvisory with final mm values and a plain-English brief.
    """
    # ── Glyph pass ────────────────────────────────────────────────────────────
    glyphs = analyse_text(content, requested_height_mm)
    flagged = [g for g in glyphs if g.flag]
    max_stroke_needed = max((g.stroke_width_mm for g in glyphs), default=MIN_STROKE)
    max_min_height = max((g.min_height_mm for g in glyphs), default=MIN_LETTER_H)

    # ── Surface angle ─────────────────────────────────────────────────────────
    angle = getattr(surface_group, 'angle_from_vertical', 0.0)
    slope = slope_projection(angle)

    # ── Curve pass ────────────────────────────────────────────────────────────
    wp = wall_profile
    is_cyl = getattr(wp, 'is_cylindrical', False) if wp else False
    outer_r = getattr(wp, 'outer_r_max', 0.0) if wp else 0.0
    curve = curve_projection(outer_r, content, requested_height_mm, is_cyl)

    # ── Texture pass ──────────────────────────────────────────────────────────
    label = getattr(surface_group, 'label', 'FLAT_TOP')
    texture = texture_correction(angle, layer_height_mm, label, infill_pct, wall_count)

    # ── Compute final values ──────────────────────────────────────────────────
    # Height: max of requested, glyph minimum, slope-compensated
    base_height = max(requested_height_mm, max_min_height)
    final_height = round(base_height * slope.height_scale, 2)
    final_height = max(final_height, MIN_LETTER_H)

    # Depth: requested + texture buffer + slope scale
    base_depth = max(requested_depth_mm, texture.recommended_depth_mm)
    final_depth = round(base_depth * slope.depth_scale, 2)
    # Cap at 50% of wall thickness if wall profile available
    if wp and hasattr(wp, 'prime_zone_wall'):
        max_safe_depth = wp.prime_zone_wall * 0.50
        if final_depth > max_safe_depth:
            final_depth = round(max_safe_depth, 2)
            # Build warning handled below

    # Stroke: max of requested, glyph max, texture buffer
    final_stroke = round(
        max(requested_stroke_mm, max_stroke_needed, MIN_STROKE) + texture.stroke_buffer_mm,
        2
    )

    # Spacing
    letter_spacing = round(final_height * 0.12 * slope.spacing_scale, 2)
    word_spacing   = round(final_height * 0.60 * slope.spacing_scale, 2)

    # Arc wrap
    arc_wrap = curve.is_cylindrical and curve.outer_radius_mm > 0

    # Layer profile: use accuracy if depth ≤ 0.6mm (need fine resolution)
    layer_profile = 'accuracy_0.12' if final_depth <= 0.6 else 'standard_0.20'

    # Pass count: wider strokes benefit from 2 passes for clean walls
    pass_count = 2 if final_stroke >= NOZZLE_DIA * 1.5 else 1

    # Feed rate
    if slope.staircase_risk == 'HIGH':
        feed = 'slow_40pct'
    elif slope.staircase_risk == 'MEDIUM' or arc_wrap:
        feed = 'slow_20pct'
    else:
        feed = 'normal'

    # ── Warnings ──────────────────────────────────────────────────────────────
    warnings = []
    workarounds = []

    if flagged:
        for g in flagged:
            warnings.append(
                f'Glyph \'{g.char}\' needs ≥{g.min_height_mm}mm '
                f'(requested {requested_height_mm}mm): {g.notes}'
            )

    if slope.staircase_risk in ('MEDIUM', 'HIGH'):
        warnings.append(f'Staircase risk {slope.staircase_risk} at {angle:.0f}° slope. {slope.advisory}')
        if slope.staircase_risk == 'HIGH':
            workarounds.append('W1 — Reorient model so target surface faces up')

    if arc_wrap and len(content) > curve.recommended_char_count:
        warnings.append(
            f'Text too long for arc: {len(content)} chars, max {curve.recommended_char_count}. '
            'Abbreviate or reduce font size.'
        )
        workarounds.append('W5 — Line-wrap text along arc')

    if wp and hasattr(wp, 'prime_zone_wall'):
        max_safe = wp.prime_zone_wall * 0.50
        if requested_depth_mm > max_safe:
            warnings.append(
                f'Requested depth {requested_depth_mm}mm exceeds 50% of wall '
                f'({wp.prime_zone_wall}mm). Capped at {max_safe:.2f}mm.'
            )

    if texture.recommended_depth_mm > 1.5:
        warnings.append(
            'Surface texture requires depth > 1.5mm. Verify wall thickness before cutting.'
        )

    # ── Brief ─────────────────────────────────────────────────────────────────
    brief_parts = [
        f'Content: "{content}" ({len(content)} chars).',
        f'Surface: {label} at {angle:.0f}° from horizontal.',
        f'Final spec: {style} / depth {final_depth}mm / '
        f'height {final_height}mm / stroke {final_stroke}mm.',
        f'Letter spacing {letter_spacing}mm / word spacing {word_spacing}mm.',
    ]
    if arc_wrap:
        brief_parts.append(
            f'Arc wrap: radius {curve.outer_radius_mm:.1f}mm, '
            f'{curve.wrap_direction} direction, '
            f'depth {curve.depth_outer_mm}mm center / {curve.depth_inner_mm}mm edge.'
        )
    if slope.height_scale != 1.0 or slope.depth_scale != 1.0:
        brief_parts.append(
            f'Slope compensation applied: '
            f'height ×{slope.height_scale:.2f}, depth ×{slope.depth_scale:.2f}.'
        )
    brief_parts.append(
        f'Texture buffer: +{texture.depth_buffer_mm:.2f}mm depth '
        f'(layer lines + infill + wall flex).'
    )
    brief_parts.append(
        f'Layer profile: {layer_profile}. '
        f'Pass count: {pass_count}. Feed rate: {feed}.'
    )
    if warnings:
        brief_parts.append('WARNINGS: ' + ' | '.join(warnings))
    if workarounds:
        brief_parts.append('WORKAROUNDS: ' + ', '.join(workarounds))

    return CutAdvisory(
        content=content,
        style=style,
        final_depth_mm=final_depth,
        final_height_mm=final_height,
        final_stroke_mm=final_stroke,
        letter_spacing_mm=letter_spacing,
        word_spacing_mm=word_spacing,
        orientation_deg=0.0,
        arc_wrap=arc_wrap,
        arc_radius_mm=outer_r if arc_wrap else 0.0,
        layer_profile=layer_profile,
        pass_count=pass_count,
        feed_rate_advisory=feed,
        problem_glyphs=[g.char for g in flagged],
        warnings=warnings,
        workarounds=workarounds,
        brief=' '.join(brief_parts),
    )


# ── 6. Full typography report ─────────────────────────────────────────────────

def full_typography_report(
    content: str,
    surface_group,
    wall_profile=None,
    requested_height_mm: float = REC_LETTER_H,
    requested_depth_mm: float = MIN_ENGRAVE_DEPTH_READABLE,
    requested_stroke_mm: float = MIN_STROKE,
    style: str = 'deboss',
    layer_height_mm: float = LAYER_H_STD,
    infill_pct: int = 20,
    wall_count: int = 3,
) -> TypographyReport:
    """
    Master entry point. Returns TypographyReport with all compensations
    applied and a text_summary block ready for LLM injection.
    """
    glyphs = analyse_text(content, requested_height_mm)
    angle = getattr(surface_group, 'angle_from_vertical', 0.0)
    slope = slope_projection(angle)
    label = getattr(surface_group, 'label', 'FLAT_TOP')
    is_cyl = getattr(wall_profile, 'is_cylindrical', False) if wall_profile else False
    outer_r = getattr(wall_profile, 'outer_r_max', 0.0) if wall_profile else 0.0
    curve = curve_projection(outer_r, content, requested_height_mm, is_cyl)
    texture = texture_correction(angle, layer_height_mm, label, infill_pct, wall_count)
    cut = build_advisory(
        content, surface_group, wall_profile,
        requested_height_mm, requested_depth_mm, requested_stroke_mm,
        style, layer_height_mm, infill_pct, wall_count,
    )

    # Build text summary for LLM
    lines = [
        '=== TYPOGRAPHY ANALYSIS (typography_utils_marcus) ===',
        f'Content        : "{content}"',
        f'Char count     : {len(content)} (excl. spaces: {len(content.replace(" ", ""))})',
        f'Requested spec : height={requested_height_mm}mm  depth={requested_depth_mm}mm  '
        f'stroke={requested_stroke_mm}mm  style={style}',
        '',
        '--- GLYPH ANALYSIS ---',
    ]
    flagged_glyphs = [g for g in glyphs if g.flag]
    if flagged_glyphs:
        for g in flagged_glyphs:
            lines.append(f'  ⚠ \'{g.char}\' FLAG: min={g.min_height_mm}mm  stroke={g.stroke_width_mm}mm  {g.notes}')
    else:
        lines.append('  ✓ All glyphs viable at requested height.')
    lines.append('')
    lines.append('--- SLOPE COMPENSATION ---')
    lines.append(f'  Surface angle : {angle:.1f}° from horizontal')
    lines.append(f'  Staircase risk: {slope.staircase_risk}')
    lines.append(f'  Height scale  : ×{slope.height_scale:.3f}')
    lines.append(f'  Depth scale   : ×{slope.depth_scale:.3f}')
    lines.append(f'  Spacing scale : ×{slope.spacing_scale:.3f}')
    lines.append(f'  Advisory      : {slope.advisory}')
    lines.append('')
    lines.append('--- CURVE COMPENSATION ---')
    lines.append(f'  Cylindrical   : {curve.is_cylindrical}')
    if curve.is_cylindrical:
        lines.append(f'  Outer radius  : {curve.outer_radius_mm:.1f}mm')
        lines.append(f'  Arc/char      : {curve.arc_length_per_char_mm:.2f}mm')
        lines.append(f'  Max chars     : {curve.recommended_char_count}')
        lines.append(f'  Depth center  : {curve.depth_outer_mm:.2f}mm')
        lines.append(f'  Depth edge    : {curve.depth_inner_mm:.2f}mm')
        lines.append(f'  Wrap          : {curve.wrap_direction}')
    lines.append(f'  Advisory      : {curve.advisory}')
    lines.append('')
    lines.append('--- TEXTURE CORRECTION ---')
    lines.append(f'  Surface type  : {texture.surface_type}')
    lines.append(f'  Ridge height  : {texture.layer_line_depth_mm:.3f}mm')
    lines.append(f'  Depth buffer  : +{texture.depth_buffer_mm:.3f}mm')
    lines.append(f'  Stroke buffer : +{texture.stroke_buffer_mm:.2f}mm')
    lines.append(f'  Advisory      : {texture.advisory}')
    lines.append('')
    lines.append('--- FINAL CUT ADVISORY (send these values to the engraver) ---')
    lines.append(f'  Style         : {cut.style}')
    lines.append(f'  Depth         : {cut.final_depth_mm}mm  ← use this, not the requested value')
    lines.append(f'  Height        : {cut.final_height_mm}mm  ← use this')
    lines.append(f'  Stroke        : {cut.final_stroke_mm}mm  ← use this')
    lines.append(f'  Letter spacing: {cut.letter_spacing_mm}mm')
    lines.append(f'  Word spacing  : {cut.word_spacing_mm}mm')
    lines.append(f'  Arc wrap      : {cut.arc_wrap}  radius={cut.arc_radius_mm:.1f}mm')
    lines.append(f'  Layer profile : {cut.layer_profile}')
    lines.append(f'  Pass count    : {cut.pass_count}')
    lines.append(f'  Feed rate     : {cut.feed_rate_advisory}')
    if cut.problem_glyphs:
        lines.append(f'  Problem glyphs: {", ".join(cut.problem_glyphs)}')
    if cut.warnings:
        lines.append('  WARNINGS:')
        for w in cut.warnings:
            lines.append(f'    ⚠ {w}')
    if cut.workarounds:
        lines.append('  WORKAROUNDS:')
        for wa in cut.workarounds:
            lines.append(f'    🔧 {wa}')
    lines.append('')
    lines.append(f'  BRIEF: {cut.brief}')

    return TypographyReport(
        content=content,
        char_count=len(content),
        glyph_advisories=glyphs,
        slope_comp=slope,
        curve_comp=curve if curve.is_cylindrical else None,
        texture_corr=texture,
        cut_advisory=cut,
        text_summary='\n'.join(lines),
    )
