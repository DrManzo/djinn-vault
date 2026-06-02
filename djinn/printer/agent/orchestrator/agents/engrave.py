"""
EngravingAgent — native surface geometry analysis and engraving placement
for the Djinn manufacturing orchestrator.

Pipeline:
  1. Load STL from state.source_stl (or accept path from brief)
  2. Run full geometry analysis via geometry_utils.full_geometry_report()
  3. Run full typography analysis via typography_utils.full_typography_report()
     — adapts letter height, depth, stroke, spacing, arc wrap, and texture
       buffer to the actual surface the text will land on
  4. Build a rich LLM prompt with ALL geometry AND typography data embedded
  5. LLM generates 3 ranked proposals using the pre-computed mm values
  6. Return proposals for Javier approval — nothing touches the model
  7. approve(state, N) — records choice, resolves exact placement coords
     via placement_resolver and stores in state.engraving_placement

Machine: Calliope — Ender-3 V3 Plus
Nozzle: 0.4mm  Layer: 0.20mm std / 0.12mm acc  Bed: 300×300×340mm
"""
from __future__ import annotations
import json, pathlib, re
from ..llm import LLM
from ..project_state import ProjectState
from . import geometry_utils as geo
from . import typography_utils as typo
from . import placement_resolver as placer

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM = """You are EngravingAgent, a specialist in 3D-surface geometry and FDM engraving placement.

Your ONLY job: given a geometry report, a typography analysis, and a human request,
produce exactly 3 ranked engraving proposals.

## CRITICAL RULE
The TYPOGRAPHY ANALYSIS section of the user message contains pre-computed values
for depth, height, stroke, spacing, feed rate, and pass count. These values have
already accounted for slope, surface texture, curve geometry, glyph difficulty,
and machine constraints.

YOU MUST USE THESE EXACT VALUES in your proposals. Do not substitute your own
guesses. The only field where you exercise judgment is position_description —
where on the surface the text goes. Everything else comes from the typography data.

## Geometry reasoning
- Face normals tell you which direction a surface faces. Normal ≈ (0,0,1) = top face.
- Engravability score 0.0–1.0: surfaces scored ≥ 0.7 are ideal, ≥ 0.5 are feasible.
- Surface centroid gives the physical center of a face group in model space (x,y,z mm).
- Bounding box tells you the total envelope.
- Wall profile tells you where material is thick enough to safely receive engraving.
  Never propose a depth that exceeds 50% of the wall thickness in the target zone.

## Proposal ranking logic
  Rank 1 — Best surface (highest engravability score) with typography values as-is.
  Rank 2 — Second-best surface or alternate position on same surface.
  Rank 3 — Creative or fallback: rotated orientation, abbreviated text, or workaround.

## Workaround tree
  W1 — Reorient print so target surface faces up
  W2 — Scale text up
  W3 — Reduce depth to 0.5mm minimum viable
  W4 — Switch emboss↔deboss
  W5 — Line-wrap text along curved surface
  W6 — Project onto tangent plane for compound curves
  W7 — Engrave on adjacent flat surface instead
  W8 — Flag for SLA print

## Output format — reply with EXACTLY this JSON, nothing before or after:

```json
{
  "request_understood": "one-sentence paraphrase",
  "geometry_notes": "2-3 sentence summary of surface geometry observed",
  "typography_notes": "1-2 sentence summary of key typography adjustments applied",
  "proposals": [
    {
      "rank": 1,
      "label": "Top surface — centered",
      "surface_group_index": 1,
      "surface_label": "FLAT_TOP",
      "engravability_score": 1.0,
      "position_description": "Centered on top face. Centroid at (X, Y, Z)mm. Clear of all edges by 3mm.",
      "content": "Typhon's Forge",
      "style": "deboss",
      "depth_mm": 0.84,
      "font_height_mm": 5.0,
      "stroke_width_mm": 0.56,
      "letter_spacing_mm": 0.60,
      "word_spacing_mm": 3.00,
      "orientation_deg": 0,
      "arc_wrap": false,
      "arc_radius_mm": 0.0,
      "layer_profile": "standard_0.20",
      "pass_count": 1,
      "feed_rate": "normal",
      "offset_from_edge_mm": 3.0,
      "rationale": "Best surface. Typography values taken directly from analysis.",
      "warnings": [],
      "workarounds_applied": []
    },
    {
      "rank": 2,
      "label": "Front side — base band",
      "surface_group_index": 2,
      "surface_label": "FLAT_SIDE",
      "engravability_score": 0.70,
      "position_description": "Lower third of front face, horizontal band.",
      "content": "Typhon's Forge",
      "style": "deboss",
      "depth_mm": 0.92,
      "font_height_mm": 5.4,
      "stroke_width_mm": 0.64,
      "letter_spacing_mm": 0.65,
      "word_spacing_mm": 3.20,
      "orientation_deg": 0,
      "arc_wrap": false,
      "arc_radius_mm": 0.0,
      "layer_profile": "standard_0.20",
      "pass_count": 2,
      "feed_rate": "normal",
      "offset_from_edge_mm": 3.0,
      "rationale": "Side surface. Slope and texture buffers applied per typography analysis.",
      "warnings": ["Layer lines horizontal — slight texture on letter edges."],
      "workarounds_applied": []
    },
    {
      "rank": 3,
      "label": "Cylindrical face — arc wrap",
      "surface_group_index": 3,
      "surface_label": "FLAT_SIDE",
      "engravability_score": 0.55,
      "position_description": "Wrapped around cylindrical surface at prime Z zone.",
      "content": "Typhon's Forge",
      "style": "deboss",
      "depth_mm": 0.96,
      "font_height_mm": 5.0,
      "stroke_width_mm": 0.56,
      "letter_spacing_mm": 0.60,
      "word_spacing_mm": 3.00,
      "orientation_deg": 0,
      "arc_wrap": true,
      "arc_radius_mm": 18.5,
      "layer_profile": "accuracy_0.12",
      "pass_count": 2,
      "feed_rate": "slow_20pct",
      "offset_from_edge_mm": 2.0,
      "rationale": "Arc wrap with curve-compensated depth. Slow feed for clean path.",
      "warnings": ["Confirm slicer supports cylindrical arc path for engraving."],
      "workarounds_applied": ["W5"]
    }
  ],
  "hard_blocks": [],
  "recommendation": "Proposal 1 for most use cases."
}
```

If the model has NO viable surface, fill hard_blocks and give 1 workaround proposal only.
Never hallucinate surfaces. Never override typography values with your own estimates.
"""


def run(state: ProjectState, llm: LLM) -> ProjectState:
    """
    Run geometry + typography analysis, then call LLM with full data.
    Returns state with engraving_proposals populated.
    Approval happens in the calling interface (Telegram / CLI).
    """
    stl_path = state.source_stl or state.model_path
    if not stl_path or not pathlib.Path(stl_path).exists():
        state.status = 'engrave_error'
        state.note = f'EngravingAgent: STL not found at "{stl_path}". Provide source_stl in brief.'
        return state

    engrave_request = (
        state.engraving_request
        or state.brief.get('engraving_request')
        or state.brief.get('request', '')
    )

    # ── 1. Geometry ──────────────────────────────────────────────────────────
    print(f'  [EngravingAgent] Geometry: {stl_path}')
    try:
        geo_report = geo.full_geometry_report(stl_path)
    except Exception as e:
        state.status = 'engrave_error'
        state.note = f'EngravingAgent: geometry analysis failed — {e}'
        return state

    # Cache geo_report on state so approve() can use it without re-parsing
    state._geo_report = geo_report

    print(f'    bbox: {geo_report.bbox_x:.1f}×{geo_report.bbox_y:.1f}×{geo_report.bbox_z:.1f}mm  '
          f'faces: {geo_report.face_count}  groups: {len(geo_report.surface_groups)}')
    print(f'    engravable (score≥0.5): {len(geo_report.engravable_groups)}')
    if geo_report.warnings:
        for w in geo_report.warnings:
            print(f'    ⚠ {w}')

    # ── 2. Typography ─────────────────────────────────────────────────────────
    best_surface = (
        geo_report.engravable_groups[0]
        if geo_report.engravable_groups
        else (geo_report.surface_groups[0] if geo_report.surface_groups else None)
    )

    typo_report = None
    typo_block = '(Typography analysis: no engravable surface found — see geometry warnings.)'

    if best_surface:
        quoted = re.findall(r'["\u2018\u2019\u201c\u201d]([^"\u2018\u2019\u201c\u201d]+)["\u2018\u2019\u201c\u201d]', engrave_request)
        content_to_analyse = quoted[0] if quoted else engrave_request

        layer_h   = state.brief.get('layer_height_mm', geo.LAYER_H_STD)
        infill    = state.brief.get('infill_pct', 20)
        walls     = state.brief.get('wall_count', 3)
        req_h     = state.brief.get('font_height_mm', geo.REC_LETTER_H)
        req_d     = state.brief.get('engrave_depth_mm', geo.MIN_ENGRAVE_DEPTH_READABLE)
        req_s     = state.brief.get('stroke_width_mm', geo.MIN_STROKE)
        req_style = state.brief.get('engrave_style', 'deboss')

        print(f'  [EngravingAgent] Typography: "{content_to_analyse[:40]}" on {best_surface.label}')
        try:
            typo_report = typo.full_typography_report(
                content=content_to_analyse,
                surface_group=best_surface,
                wall_profile=geo_report.wall_profile,
                requested_height_mm=req_h,
                requested_depth_mm=req_d,
                requested_stroke_mm=req_s,
                style=req_style,
                layer_height_mm=layer_h,
                infill_pct=infill,
                wall_count=walls,
                font_path=state.brief.get('font_path'),
            )
            typo_block = typo_report.text_summary
            cut = typo_report.cut_advisory
            print(f'    depth={cut.final_depth_mm}mm  height={cut.final_height_mm}mm  '
                  f'stroke={cut.final_stroke_mm}mm  feed={cut.feed_rate_advisory}  '
                  f'passes={cut.pass_count}')
            if cut.warnings:
                for w in cut.warnings:
                    print(f'    ⚠ typo: {w}')
        except Exception as e:
            typo_block = f'(Typography analysis error: {e} — LLM will use geometry data only.)'
            print(f'    ⚠ typography error: {e}')

    # ── 3. LLM ────────────────────────────────────────────────────────────────
    user_msg = f"""=== ENGRAVING REQUEST ===
{engrave_request}

=== FULL GEOMETRY DATA (read every line before proposing anything) ===
{geo_report.text_summary}

=== TYPOGRAPHY ANALYSIS (USE THESE EXACT MM VALUES IN YOUR PROPOSALS) ===
{typo_block}

=== TASK ===
Propose exactly 3 ranked engraving options.
For depth_mm, font_height_mm, stroke_width_mm, letter_spacing_mm, word_spacing_mm,
layer_profile, pass_count, and feed_rate — use the values from the TYPOGRAPHY ANALYSIS
\u2018FINAL CUT ADVISORY\u2019 section above. Do not substitute your own estimates.
Return ONLY the JSON block. No prose before or after."""

    print(f'  [EngravingAgent] Sending to {llm.name} ...')
    reply = llm.chat(SYSTEM, [{'role': 'user', 'content': user_msg}], max_tokens=4000)

    # ── 4. Parse JSON ─────────────────────────────────────────────────────────
    proposals = {}
    m = re.search(r'```json\s*(.*?)\s*```', reply, re.DOTALL)
    if m:
        try:
            proposals = json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    if not proposals:
        m2 = re.search(r'\{.*\}', reply, re.DOTALL)
        if m2:
            try:
                proposals = json.loads(m2.group())
            except json.JSONDecodeError:
                pass

    if not proposals:
        state.status = 'engrave_error'
        state.note = 'EngravingAgent: LLM returned no valid JSON.'
        state.engraving_proposals = {'raw_reply': reply[:2000]}
        return state

    state.engraving_proposals = proposals
    state.engraving_request = engrave_request
    state.status = 'engrave_pending_approval'

    # ── 5. Store full context in state.mesh ───────────────────────────────────
    wp = geo_report.wall_profile
    state.mesh = {
        'bbox_x': geo_report.bbox_x,
        'bbox_y': geo_report.bbox_y,
        'bbox_z': geo_report.bbox_z,
        'volume_cm3': geo_report.volume_cm3,
        'face_count': geo_report.face_count,
        'surface_groups': [
            {
                'label': g.label,
                'engravability': g.engravability,
                'area_mm2': round(g.total_area_mm2, 2),
                'angle_deg': round(g.angle_from_vertical, 1),
                'centroid': [round(g.centroid[0],1), round(g.centroid[1],1), round(g.centroid[2],1)],
                'reason': g.engrav_reason,
            }
            for g in geo_report.surface_groups
        ],
        'wall_profile': {
            'is_cylindrical':      wp.is_cylindrical,
            'outer_r_min':         wp.outer_r_min,
            'outer_r_max':         wp.outer_r_max,
            'prime_zone_z_min':    wp.prime_zone_z_min,
            'prime_zone_z_max':    wp.prime_zone_z_max,
            'prime_zone_wall_mm':  wp.prime_zone_wall,
        } if wp else {},
        'typography': {
            'final_depth_mm':   typo_report.cut_advisory.final_depth_mm    if typo_report else None,
            'final_height_mm':  typo_report.cut_advisory.final_height_mm   if typo_report else None,
            'final_stroke_mm':  typo_report.cut_advisory.final_stroke_mm   if typo_report else None,
            'layer_profile':    typo_report.cut_advisory.layer_profile      if typo_report else None,
            'pass_count':       typo_report.cut_advisory.pass_count         if typo_report else None,
            'feed_rate':        typo_report.cut_advisory.feed_rate_advisory if typo_report else None,
            'arc_wrap':         typo_report.cut_advisory.arc_wrap           if typo_report else False,
            'arc_radius_mm':    typo_report.cut_advisory.arc_radius_mm      if typo_report else 0.0,
            'problem_glyphs':   typo_report.cut_advisory.problem_glyphs     if typo_report else [],
        },
    }

    _report_proposals(state)
    return state


def approve(state: ProjectState, choice: int) -> ProjectState:
    """
    Record Javier's approval of proposal 1, 2, or 3.

    1. Writes engraving_spec to state.
    2. Runs placement_resolver.resolve() to convert position_description
       into exact x/y/z offsets + modifier_args.
    3. Stores PlacementSpec in state.engraving_placement.
    4. Prints resolved coordinates for Telegram confirmation.
    """
    proposals = state.engraving_proposals.get('proposals', [])
    if not proposals or choice < 1 or choice > len(proposals):
        state.note = f'EngravingAgent approve: choice {choice} out of range (have {len(proposals)})'
        return state

    chosen = proposals[choice - 1]
    state.engraving_approved = choice
    state.engraving_spec     = chosen
    state.status             = 'engrave_approved'
    state.note = f'Engraving approved: {chosen.get("label", "")} — {chosen.get("content", "")}'
    print(f'  [EngravingAgent] Approved proposal {choice}: {state.note}')

    # ── Resolve placement coordinates ─────────────────────────────────────────
    geo_report = getattr(state, '_geo_report', None)
    if geo_report is None:
        print('  [EngravingAgent] ⚠ No cached geo_report — re-running geometry analysis.')
        stl_path = state.source_stl or state.model_path
        if stl_path and pathlib.Path(stl_path).exists():
            try:
                geo_report = geo.full_geometry_report(stl_path)
                state._geo_report = geo_report
            except Exception as e:
                print(f'  [EngravingAgent] ⚠ geometry re-run failed: {e}')

    placement = placer.resolve(chosen, geo_report) if geo_report else placer.PlacementSpec(
        resolved=False,
        reason='geo_report unavailable — re-run engrave analysis before approving.',
    )

    state.engraving_placement = {
        'resolved':         placement.resolved,
        'reason':           placement.reason,
        'x_offset_mm':      placement.x_offset_mm,
        'y_offset_mm':      placement.y_offset_mm,
        'z_surface_mm':     placement.z_surface_mm,
        'width_mm':         placement.width_mm,
        'height_mm':        placement.height_mm,
        'rotation_deg':     placement.rotation_deg,
        'anchor':           placement.anchor,
        'arc_wrap':         placement.arc_wrap,
        'arc_offset_deg':   placement.arc_offset_deg,
        'arc_radius_mm':    placement.arc_radius_mm,
        'modifier_args':    placement.modifier_args,
    }

    # Print for Telegram / console confirmation
    print()
    print(placement.text_summary)

    return state


def _report_proposals(state: ProjectState):
    p = state.engraving_proposals
    print(f'\n  EngravingAgent — {p.get("request_understood", "")}')
    print(f'  Geometry  : {p.get("geometry_notes", "")}')
    print(f'  Typography: {p.get("typography_notes", "")}')
    for prop in p.get('proposals', []):
        print(f'\n  [{prop["rank"]}] {prop["label"]}  (engravability={prop["engravability_score"]})')
        print(f'      Surface  : {prop["surface_label"]} — group {prop["surface_group_index"]}')
        print(f'      Position : {prop["position_description"]}')
        print(
            f'      Spec     : {prop["style"]}  depth={prop["depth_mm"]}mm  '
            f'h={prop["font_height_mm"]}mm  stroke={prop["stroke_width_mm"]}mm  '
            f'ls={prop.get("letter_spacing_mm","?")}mm  '
            f'feed={prop.get("feed_rate","?")}  passes={prop.get("pass_count","?")}'
        )
        if prop.get('arc_wrap'):
            print(
                f'      Arc wrap : radius={prop.get("arc_radius_mm",0):.1f}mm  '
                f'profile={prop.get("layer_profile","?")}'
            )
        print(f'      Rationale: {prop["rationale"]}')
        for w in prop.get('warnings', []):
            print(f'      ⚠ {w}')
        for wa in prop.get('workarounds_applied', []):
            print(f'      🔧 {wa}')
    if p.get('hard_blocks'):
        print('\n  HARD BLOCKS:')
        for b in p['hard_blocks']:
            print(f'    ✗ {b}')
    print(f'\n  Recommendation: {p.get("recommendation", "")}')
    print('\n  → approve engrave 1  /  approve engrave 2  /  approve engrave 3')
