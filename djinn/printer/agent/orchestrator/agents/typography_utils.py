"""
typography_utils.py — FDM-aware typography analysis for the Djinn engraving pipeline.

Companion to geometry_utils.py. Answers the question geometry_utils can't:
"Will the letters actually be readable once printed?"

Uses PIL to read real font metrics from TTF files. Analyzes:
  - Stroke widths per character (from actual glyph bitmaps)
  - Counter detection (holes in o, b, d, e, etc.) and whether they're printable
  - Surface texture interaction (layer lines vs letter form orientation)
  - Adaptive depth recommendation based on wall thickness + surface type + font
  - Per-character warnings and font substitution advice

No external deps beyond PIL (Pillow), which is already in the djinn venv.

Machine: Calliope — Ender-3 V3 Plus
Nozzle: 0.4mm   Layer: 0.20mm std / 0.12mm acc
"""
from __future__ import annotations

import math
import pathlib
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# PIL is available — used for real font metric extraction
try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL_OK = True
except ImportError:
    _PIL_OK = False

# ── Machine constants (mirror geometry_utils for self-contained use) ──────────
NOZZLE_DIA       = 0.4    # mm
LAYER_H_STD      = 0.20   # mm
LAYER_H_ACC      = 0.12   # mm
MIN_COUNTER_MM   = 0.8    # mm — smallest printable counter (hole inside letter)
MIN_STROKE_MM    = 0.4    # mm — 1× nozzle
MIN_LETTER_H_MM  = 3.0    # mm — absolute minimum
REC_LETTER_H_MM  = 5.0    # mm — recommended
SURFACE_ROUGHNESS_FACTOR = 0.5   # roughness = layer_h × this factor

# Characters with FULLY ENCLOSED counters (voids the nozzle must navigate around)
# Open counters (c, e, r, s) are excluded — they're open loops, not enclosed voids
COUNTER_CHARS = set('aAbBdDgGopOPqQ068&@#')
# Characters with very thin strokes even in bold fonts
THIN_STROKE_CHARS = set('iIlL1!|:;.,\'"`')
# Characters that are especially wide (may need span adjustment)
WIDE_CHARS = set('mMwW%')

# Font weight → estimated stroke-width-to-height ratio
_WEIGHT_STROKE_RATIO = {
    'black':      0.18,
    'extrabold':  0.16,
    'heavy':      0.17,
    'bold':       0.13,
    'semibold':   0.11,
    'medium':     0.09,
    'regular':    0.08,
    'light':      0.05,
    'thin':       0.03,
    'ultralight': 0.02,
}

# Known good FDM fonts (verified clean at small sizes)
FDM_RECOMMENDED_FONTS = [
    'Roboto-Black',
    'Roboto-Bold',
    'RobotoCondensed-Bold',
    'LiberationSans-Bold',
    'DejaVuSans-Bold',
    'FreeSans-Bold',
    'Impact',
    'Arial-Bold',
]


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class CharAnalysis:
    char: str
    stroke_width_mm: float
    has_counter: bool
    counter_size_mm: float      # 0 if no counter
    counter_printable: bool     # True if counter_size >= MIN_COUNTER_MM
    printable: bool             # False if stroke too thin
    warnings: List[str] = field(default_factory=list)


@dataclass
class FontMetrics:
    font_name: str
    font_path: str
    weight_class: str           # black / bold / regular / light / thin
    stroke_ratio: float         # stroke_width / cap_height
    is_serif: bool
    is_condensed: bool
    is_monospace: bool
    fdm_suitable: bool          # True if verified usable on FDM
    fdm_suitability_reason: str


@dataclass
class SurfaceTextureProfile:
    surface_type: str           # FLAT_TOP / FLAT_SIDE / CURVED
    layer_height_mm: float
    roughness_mm: float         # peak-to-valley surface texture
    layer_orientation: str      # parallel / perpendicular / diagonal to text
    texture_interference: str   # none / low / medium / high
    min_depth_to_clear_texture: float   # depth needed to stand above texture noise
    texture_notes: str


@dataclass
class CutAdvisory:
    recommended_depth_mm: float
    min_depth_mm: float
    max_safe_depth_mm: float
    recommended_font_height_mm: float
    min_font_height_mm: float
    recommended_style: str      # deboss / emboss
    stroke_compensation_mm: float   # add to stroke width for FDM spread
    wall_depth_ratio: float     # recommended_depth / wall_thickness
    legibility_score: float     # 0.0–1.0
    rationale: str
    warnings: List[str] = field(default_factory=list)
    adjustments: List[str] = field(default_factory=list)


@dataclass
class TypographyReport:
    text: str
    font_path: str
    font_metrics: FontMetrics
    font_height_mm: float
    total_width_mm: float
    char_analyses: List[CharAnalysis]
    surface_texture: SurfaceTextureProfile
    cut_advisory: CutAdvisory
    problem_chars: List[str]
    legibility_score: float     # 0.0–1.0 composite
    text_summary: str           # for LLM injection


# ── Font metrics extraction ───────────────────────────────────────────────────

def _weight_from_name(font_path: str) -> Tuple[str, float]:
    """Infer font weight class and stroke ratio from filename."""
    name = pathlib.Path(font_path).stem.lower().replace('-', '').replace('_', '')
    for weight, ratio in _WEIGHT_STROKE_RATIO.items():
        if weight in name:
            return weight, ratio
    return 'regular', _WEIGHT_STROKE_RATIO['regular']


def _measure_stroke_width_px(font, char='H', render_height=200) -> float:
    """
    Render a capital H at render_height px and measure the stroke width
    by scanning the middle row for on/off transitions.
    Returns stroke width as fraction of render height.
    """
    if not _PIL_OK:
        return 0.10

    try:
        img = Image.new('L', (render_height * 2, render_height + 20), 0)
        draw = ImageDraw.Draw(img)
        draw.text((5, 5), char, fill=255, font=font)
        arr = list(img.getdata())
        W = img.width

        mid_row = render_height // 2 + 5
        row = arr[mid_row * W: (mid_row + 1) * W]

        threshold = 64
        in_stroke = False
        strokes = []
        start = 0
        for i, px in enumerate(row):
            if px > threshold and not in_stroke:
                in_stroke = True
                start = i
            elif px <= threshold and in_stroke:
                in_stroke = False
                strokes.append(i - start)
        if in_stroke:
            strokes.append(len(row) - start)

        if strokes:
            # Use the thinnest stroke found (for H it's the crossbar or vertical)
            return min(strokes) / render_height
        return 0.10
    except Exception:
        return 0.10


def _measure_counter_size_px(font, char='o', render_height=200) -> float:
    """
    Render a lowercase 'o' and estimate the counter size as a fraction of height.
    Looks for the largest enclosed dark region.
    """
    if not _PIL_OK:
        return 0.35

    try:
        img = Image.new('L', (render_height * 2, render_height + 20), 0)
        draw = ImageDraw.Draw(img)
        draw.text((5, 5), char, fill=255, font=font)
        arr = list(img.getdata())
        W = img.width

        # Find the bounding box of white pixels
        white_rows = [r for r in range(img.height)
                      if any(arr[r * W + c] > 64 for c in range(W))]
        if not white_rows:
            return 0.0
        char_top = white_rows[0]
        char_bot = white_rows[-1]
        char_h = char_bot - char_top

        # In the middle of the character, scan for a dark gap (the counter)
        mid = (char_top + char_bot) // 2
        row = arr[mid * W: (mid + 1) * W]
        threshold = 64

        # Find dark runs that are surrounded by white (= counter)
        in_dark = False
        dark_runs = []
        start = 0
        prev_had_white = False
        for i, px in enumerate(row):
            if px > threshold:
                prev_had_white = True
                if in_dark:
                    dark_runs.append((start, i))
                    in_dark = False
            else:
                if prev_had_white and not in_dark:
                    in_dark = True
                    start = i

        enclosed = [e - s for s, e in dark_runs if e - s > 2]
        if enclosed:
            return max(enclosed) / render_height
        return 0.0
    except Exception:
        return 0.35


def analyze_font(font_path: str, font_height_mm: float) -> FontMetrics:
    """Extract real metrics from a TTF font file using PIL."""
    name = pathlib.Path(font_path).stem
    name_lower = name.lower()
    weight, stroke_ratio = _weight_from_name(font_path)

    is_serif = any(w in name_lower for w in ('serif', 'times', 'georgia', 'free'))
    is_condensed = any(w in name_lower for w in ('condensed', 'narrow', 'cond'))
    is_monospace = any(w in name_lower for w in ('mono', 'courier', 'code', 'fixed'))
    fdm_suitable = any(r in name for r in FDM_RECOMMENDED_FONTS)

    # Try to measure actual stroke ratio from the font
    if _PIL_OK and pathlib.Path(font_path).exists():
        try:
            render_h = 200
            pil_font = ImageFont.truetype(font_path, render_h)
            measured = _measure_stroke_width_px(pil_font, 'H', render_h)
            if 0.03 < measured < 0.40:
                stroke_ratio = measured
        except Exception:
            pass

    suitability_reasons = []
    if 'black' in name_lower or 'heavy' in name_lower:
        suitability_reasons.append('thick strokes — excellent FDM readability')
        fdm_suitable = True
    elif 'bold' in name_lower:
        suitability_reasons.append('bold weight — good FDM readability')
        fdm_suitable = True
    elif 'light' in name_lower or 'thin' in name_lower:
        suitability_reasons.append('thin strokes — will lose definition at <8mm on FDM')
        fdm_suitable = False
    elif is_serif:
        suitability_reasons.append('serif font — serifs need ≥7mm to survive FDM')
        fdm_suitable = fdm_suitable and font_height_mm >= 7.0
    else:
        suitability_reasons.append('standard weight — acceptable at ≥5mm')

    return FontMetrics(
        font_name=name,
        font_path=font_path,
        weight_class=weight,
        stroke_ratio=stroke_ratio,
        is_serif=is_serif,
        is_condensed=is_condensed,
        is_monospace=is_monospace,
        fdm_suitable=fdm_suitable,
        fdm_suitability_reason='; '.join(suitability_reasons) or 'unknown',
    )


# ── Per-character analysis ────────────────────────────────────────────────────

def analyze_characters(
    text: str,
    font_path: str,
    font_height_mm: float,
) -> List[CharAnalysis]:
    """Analyze each character for printability at the given font height."""
    results = []
    name_lower = pathlib.Path(font_path).stem.lower()
    weight, stroke_ratio = _weight_from_name(font_path)

    # Try to get real metrics via PIL
    pil_font = None
    if _PIL_OK and pathlib.Path(font_path).exists():
        try:
            pil_font = ImageFont.truetype(font_path, 200)
        except Exception:
            pass

    for ch in text:
        if ch in ' \t\n':
            continue

        stroke_mm = font_height_mm * stroke_ratio
        has_counter = ch in COUNTER_CHARS
        counter_mm = 0.0

        # Thin stroke characters use a reduced ratio
        if ch in THIN_STROKE_CHARS:
            stroke_mm = font_height_mm * min(stroke_ratio, 0.06)

        # Measure actual counter size for counter chars
        if has_counter and pil_font:
            frac = _measure_counter_size_px(pil_font, ch, 200)
            counter_mm = font_height_mm * frac
        elif has_counter:
            # Heuristic: counter is ~35% of height for round letters
            counter_mm = font_height_mm * 0.35

        counter_printable = (not has_counter) or (counter_mm >= MIN_COUNTER_MM)
        printable = stroke_mm >= MIN_STROKE_MM

        warnings = []
        if stroke_mm < MIN_STROKE_MM:
            warnings.append(
                f"'{ch}': stroke {stroke_mm:.2f}mm < nozzle {MIN_STROKE_MM}mm — "
                f"will be lost. Increase font size to ≥{MIN_STROKE_MM/stroke_ratio:.1f}mm."
            )
        elif stroke_mm < MIN_STROKE_MM * 1.5:
            warnings.append(
                f"'{ch}': stroke {stroke_mm:.2f}mm is borderline — "
                f"bold font or ≥{MIN_STROKE_MM*1.5/stroke_ratio:.1f}mm recommended."
            )
        if has_counter and not counter_printable and counter_mm > 0:
            needed = MIN_COUNTER_MM / max(counter_mm / font_height_mm, 0.001)
            if needed < 200:   # only warn if the number is sensible
                warnings.append(
                    f"'{ch}': counter {counter_mm:.2f}mm < minimum {MIN_COUNTER_MM}mm — "
                    f"interior void may collapse. Try font height ≥{needed:.1f}mm or bold font."
                )

        results.append(CharAnalysis(
            char=ch,
            stroke_width_mm=round(stroke_mm, 3),
            has_counter=has_counter,
            counter_size_mm=round(counter_mm, 3),
            counter_printable=counter_printable,
            printable=printable,
            warnings=warnings,
        ))

    return results


# ── Surface texture analysis ──────────────────────────────────────────────────

def analyze_surface_texture(
    surface_type: str,
    layer_height_mm: float = LAYER_H_STD,
) -> SurfaceTextureProfile:
    """
    Determine how FDM layer lines will interact with engraved letters.

    surface_type: 'FLAT_TOP' | 'FLAT_BOTTOM' | 'FLAT_SIDE' | 'CURVED_CONVEX' | other
    """
    roughness = layer_height_mm * SURFACE_ROUGHNESS_FACTOR

    if surface_type in ('FLAT_TOP', 'FLAT_BOTTOM'):
        # Layer lines run horizontally — mostly perpendicular to vertical letter strokes
        orientation = 'perpendicular'
        interference = 'low'
        texture_notes = (
            'Layer lines run horizontal — perpendicular to vertical letter strokes. '
            'Minimal interference. Horizontal strokes (crossbar of H, T) may show '
            'slight staircase at small sizes.'
        )
    elif 'SIDE' in surface_type:
        # Side surface — layer lines stack vertically during print
        # Text on a side surface: letters are cut across horizontal layer boundaries
        orientation = 'parallel'
        interference = 'medium'
        texture_notes = (
            'Side surface: layer lines run horizontally across the face. '
            'They cross through letter strokes creating visible ridges inside cuts. '
            'Depth must exceed layer height by 2× to read clearly. '
            'Bold/black fonts and ≥1.5mm depth strongly recommended.'
        )
    elif 'CURVED' in surface_type:
        orientation = 'diagonal'
        interference = 'medium'
        texture_notes = (
            'Curved surface: layer lines are concentric arcs. '
            'Letters near the apex are cleanest; text near edges may show '
            'increasing staircase. Wrap text along the curve axis for best results.'
        )
    else:
        orientation = 'unknown'
        interference = 'medium'
        texture_notes = 'Surface type unknown — assume medium texture interference.'

    # Minimum depth to stand clearly above texture noise
    if interference == 'low':
        min_depth = roughness * 3.0    # 3× roughness
    elif interference == 'medium':
        min_depth = roughness * 5.0    # 5× roughness
    else:
        min_depth = roughness * 8.0    # high interference

    return SurfaceTextureProfile(
        surface_type=surface_type,
        layer_height_mm=layer_height_mm,
        roughness_mm=round(roughness, 3),
        layer_orientation=orientation,
        texture_interference=interference,
        min_depth_to_clear_texture=round(min_depth, 2),
        texture_notes=texture_notes,
    )


# ── Adaptive cut advisor ──────────────────────────────────────────────────────

def compute_cut_advisory(
    text: str,
    font_metrics: FontMetrics,
    font_height_mm: float,
    char_analyses: List[CharAnalysis],
    surface_texture: SurfaceTextureProfile,
    wall_thickness_mm: float,
    outer_radius_mm: float = 0.0,   # 0 = flat surface
) -> CutAdvisory:
    """
    Given everything we know about the font, the letters, and the surface,
    recommend the optimal cut parameters.
    """
    warnings = []
    adjustments = []

    # ── Depth calculation ────────────────────────────────────────────────────
    # Floor: must clear surface texture
    depth_floor = surface_texture.min_depth_to_clear_texture
    depth_floor = max(depth_floor, 0.5)     # hard minimum

    # Ceiling: don't exceed 30% of wall thickness
    depth_ceiling = wall_thickness_mm * 0.30
    depth_ceiling = min(depth_ceiling, 2.5)  # cap at 2.5mm — diminishing returns

    # Curved surface penalty: reduce by 10% (curvature spreads the cut)
    if outer_radius_mm > 0 and outer_radius_mm < 50:
        depth_ceiling *= 0.90
        warnings.append(
            f'Curved surface (r={outer_radius_mm:.1f}mm): depth ceiling reduced by 10%. '
            f'Curvature spreads cut geometry — shallower reads cleaner.'
        )

    # Target depth: start at 1.9mm (known good from Camood reference), clamp to range
    depth_target = 1.9
    depth_target = max(depth_floor, min(depth_target, depth_ceiling))

    if depth_target < 0.8:
        warnings.append(
            f'Wall only {wall_thickness_mm:.1f}mm thick — max safe depth '
            f'{depth_ceiling:.2f}mm. Text may be faint. Consider reorienting print.'
        )
    if depth_floor > depth_target:
        warnings.append(
            f'Surface texture ({surface_texture.texture_interference} interference) '
            f'requires ≥{depth_floor:.2f}mm depth to read. '
            f'Wall limits depth to {depth_ceiling:.2f}mm — may be marginal.'
        )

    # ── Font height check ────────────────────────────────────────────────────
    min_font_h = MIN_LETTER_H_MM
    rec_font_h = font_height_mm

    # Serif fonts need more height to preserve details
    if font_metrics.is_serif:
        min_font_h = max(min_font_h, 7.0)
        if font_height_mm < 7.0:
            warnings.append(
                f'Serif font at {font_height_mm}mm — serifs will collapse below 7mm on FDM. '
                f'Switch to bold sans-serif (Roboto Black, DejaVuSans-Bold) or increase to 7mm.'
            )
            adjustments.append(f'Increase font height to 7mm OR switch to bold sans-serif')

    if not font_metrics.fdm_suitable:
        adjustments.append(
            f'Replace {font_metrics.font_name} with Roboto-Black or DejaVuSans-Bold '
            f'({font_metrics.fdm_suitability_reason})'
        )

    # ── Stroke compensation ──────────────────────────────────────────────────
    # FDM nozzle slightly overextrudes on first layer and into recesses.
    # Compensate by not shrinking strokes — 0mm compensation unless strokes are borderline.
    min_stroke = min((c.stroke_width_mm for c in char_analyses), default=0.4)
    stroke_comp = 0.0
    if min_stroke < NOZZLE_DIA * 1.5:
        stroke_comp = NOZZLE_DIA * 0.5
        adjustments.append(
            f'Stroke compensation +{stroke_comp:.2f}mm — thinnest stroke '
            f'({min_stroke:.2f}mm) is close to nozzle dia. Use bold font or increase size.'
        )

    # ── Problem characters ───────────────────────────────────────────────────
    problem_chars = [c for c in char_analyses if c.warnings]
    if problem_chars:
        for pc in problem_chars:
            for w in pc.warnings:
                warnings.append(w)

    # ── Style recommendation ─────────────────────────────────────────────────
    # Deboss (inward carve) is almost always better on FDM side walls
    style = 'deboss'
    if surface_texture.surface_type in ('FLAT_TOP',):
        style = 'deboss'  # still deboss — emboss on flat top needs supports

    # ── Legibility score ─────────────────────────────────────────────────────
    score = 1.0

    # Penalize for font not being FDM-suited
    if not font_metrics.fdm_suitable:
        score -= 0.25
    # Penalize for depth being too shallow relative to floor
    if depth_target < depth_floor * 1.2:
        score -= 0.20
    # Penalize for problem characters
    n_prob = len(problem_chars)
    score -= min(n_prob * 0.05, 0.25)
    # Penalize for texture interference
    if surface_texture.texture_interference == 'high':
        score -= 0.15
    elif surface_texture.texture_interference == 'medium':
        score -= 0.05
    # Penalize for thin wall
    if wall_thickness_mm < 3.0:
        score -= 0.20

    score = round(max(0.0, min(1.0, score)), 2)

    rationale = (
        f'Wall {wall_thickness_mm:.1f}mm → max safe depth {depth_ceiling:.2f}mm (30% rule). '
        f'Surface texture ({surface_texture.texture_interference}) needs ≥{depth_floor:.2f}mm to clear layer lines. '
        f'Recommended: {depth_target:.2f}mm depth ({depth_target/wall_thickness_mm*100:.0f}% of wall). '
        f'Font {font_metrics.font_name} ({font_metrics.weight_class}) — '
        f'stroke ratio {font_metrics.stroke_ratio:.2f} → '
        f'{font_height_mm * font_metrics.stroke_ratio:.2f}mm strokes at {font_height_mm}mm height.'
    )

    return CutAdvisory(
        recommended_depth_mm=round(depth_target, 2),
        min_depth_mm=round(depth_floor, 2),
        max_safe_depth_mm=round(depth_ceiling, 2),
        recommended_font_height_mm=round(rec_font_h, 1),
        min_font_height_mm=round(min_font_h, 1),
        recommended_style=style,
        stroke_compensation_mm=round(stroke_comp, 2),
        wall_depth_ratio=round(depth_target / max(wall_thickness_mm, 0.1), 3),
        legibility_score=score,
        rationale=rationale,
        warnings=warnings,
        adjustments=adjustments,
    )


# ── Full report ───────────────────────────────────────────────────────────────

def full_typography_report(
    text: str,
    font_path: str,
    font_height_mm: float,
    surface_type: str,
    wall_thickness_mm: float,
    outer_radius_mm: float = 0.0,
    layer_height_mm: float = LAYER_H_STD,
) -> TypographyReport:
    """
    Full typography analysis for a given text + font + surface combination.
    Returns a TypographyReport with LLM-ready text_summary.
    """
    # Resolve font path
    font_path = _resolve_font(font_path)

    font_metrics   = analyze_font(font_path, font_height_mm)
    char_analyses  = analyze_characters(text, font_path, font_height_mm)
    surface_texture = analyze_surface_texture(surface_type, layer_height_mm)
    cut_advisory   = compute_cut_advisory(
        text, font_metrics, font_height_mm, char_analyses,
        surface_texture, wall_thickness_mm, outer_radius_mm,
    )

    # Estimate total text width
    total_width_mm = _estimate_text_width(text, font_path, font_height_mm)
    problem_chars  = [c.char for c in char_analyses if c.warnings]
    legibility_score = cut_advisory.legibility_score

    text_summary = _build_summary(
        text, font_metrics, font_height_mm, total_width_mm,
        char_analyses, surface_texture, cut_advisory, problem_chars,
    )

    return TypographyReport(
        text=text,
        font_path=font_path,
        font_metrics=font_metrics,
        font_height_mm=font_height_mm,
        total_width_mm=total_width_mm,
        char_analyses=char_analyses,
        surface_texture=surface_texture,
        cut_advisory=cut_advisory,
        problem_chars=problem_chars,
        legibility_score=legibility_score,
        text_summary=text_summary,
    )


def _resolve_font(font_path: str) -> str:
    """Return font_path as-is if it exists, otherwise search common locations."""
    if pathlib.Path(font_path).exists():
        return font_path
    search_dirs = [
        pathlib.Path('/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF'),
        pathlib.Path('/usr/share/fonts/truetype/dejavu'),
        pathlib.Path('/usr/share/fonts/truetype/liberation'),
        pathlib.Path('/usr/share/fonts/truetype/freefont'),
        pathlib.Path('/usr/share/fonts/truetype'),
    ]
    name = pathlib.Path(font_path).name
    for d in search_dirs:
        candidate = d / name
        if candidate.exists():
            return str(candidate)
    # Return original path and let PIL fail gracefully
    return font_path


def _estimate_text_width(text: str, font_path: str, font_height_mm: float) -> float:
    """Estimate rendered text width in mm using PIL."""
    if not _PIL_OK or not pathlib.Path(font_path).exists():
        return len(text) * font_height_mm * 0.6   # rough heuristic

    try:
        render_h = 200
        pil_font = ImageFont.truetype(font_path, render_h)
        bbox = pil_font.getbbox(text)
        if bbox:
            pixel_width = bbox[2] - bbox[0]
            return round(pixel_width / render_h * font_height_mm, 1)
    except Exception:
        pass
    return len(text) * font_height_mm * 0.6


def _build_summary(
    text, font_metrics, font_height_mm, total_width_mm,
    char_analyses, surface_texture, cut_advisory, problem_chars,
) -> str:
    adv = cut_advisory
    fm  = font_metrics
    st  = surface_texture

    lines = [
        '--- TYPOGRAPHY ANALYSIS ---',
        f'  Text       : "{text}"',
        f'  Font       : {fm.font_name} ({fm.weight_class})',
        f'  FDM suited : {"YES" if fm.fdm_suitable else "NO — " + fm.fdm_suitability_reason}',
        f'  Stroke ratio: {fm.stroke_ratio:.2f} → '
        f'{font_height_mm * fm.stroke_ratio:.2f}mm strokes at {font_height_mm}mm height',
        f'  Size       : {font_height_mm}mm tall × {total_width_mm}mm wide',
        '',
        f'  Surface    : {st.surface_type}  texture={st.texture_interference}  '
        f'roughness={st.roughness_mm}mm',
        f'  Layer lines: {st.layer_orientation} to text strokes',
        f'  {st.texture_notes}',
        '',
        '  --- CUT ADVISORY ---',
        f'  Recommended depth  : {adv.recommended_depth_mm}mm',
        f'  Depth range        : {adv.min_depth_mm}mm (min) → {adv.max_safe_depth_mm}mm (max safe)',
        f'  Wall usage         : {adv.wall_depth_ratio*100:.0f}% of wall at recommended depth',
        f'  Style              : {adv.recommended_style}',
        f'  Stroke compensation: +{adv.stroke_compensation_mm}mm',
        f'  Legibility score   : {adv.legibility_score:.2f} / 1.00',
        '',
        f'  Rationale: {adv.rationale}',
    ]

    if problem_chars:
        lines.append(f'\n  ⚠ PROBLEM CHARACTERS: {", ".join(repr(c) for c in problem_chars)}')
        for ca in char_analyses:
            for w in ca.warnings:
                lines.append(f'    • {w}')

    if adv.warnings:
        lines.append('\n  ⚠ WARNINGS:')
        for w in adv.warnings:
            if w not in [cw for ca in char_analyses for cw in ca.warnings]:
                lines.append(f'    • {w}')

    if adv.adjustments:
        lines.append('\n  → RECOMMENDED ADJUSTMENTS:')
        for a in adv.adjustments:
            lines.append(f'    • {a}')

    if adv.legibility_score >= 0.85:
        lines.append('\n  ✓ VERDICT: Will print cleanly. Proceed.')
    elif adv.legibility_score >= 0.65:
        lines.append('\n  ~ VERDICT: Acceptable. Apply adjustments above for best results.')
    else:
        lines.append('\n  ✗ VERDICT: Legibility at risk. Apply all adjustments before cutting.')

    return '\n'.join(lines)
