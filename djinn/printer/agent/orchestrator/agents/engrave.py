"""
EngravingAgent — native surface geometry analysis and engraving placement
for the Djinn manufacturing orchestrator.

Pipeline:
  1. Load STL from state.source_stl (or accept path from brief)
  2. Run full geometry analysis via geometry_utils.full_geometry_report()
  3. Build a rich LLM prompt with ALL geometry data embedded
  4. LLM generates 3 ranked proposals (each with surface, position,
     depth, text/content, font-size, orientation, rationale, warnings)
  5. Return proposals for Javier approval — nothing touches the model

Machine: Calliope — Ender-3 V3 Plus
Nozzle: 0.4mm  Layer: 0.20mm std / 0.12mm acc  Bed: 300×300×340mm

This agent owns NO external deps beyond geometry_utils and the LLM.
It does NOT call djinn-model-text-engrave or djinn engrave-analyze —
it IS the authoritative engraving decision engine from here forward.
"""
from __future__ import annotations
import json, pathlib, re
from ..llm import LLM
from ..project_state import ProjectState
from . import geometry_utils as geo

# ── System prompt ─────────────────────────────────────────────────────────────
# Note: the full geometry report is injected at runtime into the user message.
# The system prompt establishes identity and reasoning rules only.

SYSTEM = """You are EngravingAgent, a specialist in 3D-surface geometry and FDM engraving placement.

Your ONLY job: given a geometry report and a human request, produce exactly 3 ranked
engraving proposals. You reason carefully about every layer, face normal, overhang angle,
and machine constraint before suggesting a position.

## You must understand and apply:

### Geometry reasoning
- Face normals tell you which direction a surface faces. Normal ≈ (0,0,1) = top face.
- Engravability score 0.0–1.0: surfaces scored ≥ 0.7 are ideal, ≥ 0.5 are feasible.
- Surface centroid gives the physical center of a face group in model space (x,y,z mm).
- Bounding box tells you the total envelope — use this to estimate relative positions.
  e.g. if bbox_z = 80mm and a centroid.z = 10mm, the surface is near the base.
- Multiple surface groups may exist. Rank them by engravability score FIRST, then by
  aesthetics and user intent.

### FDM constraint math
- Minimum visible depth: 0.5mm. Minimum recommended: 0.8mm.
- Minimum letter height: 3mm absolute. Use ≥ 5mm unless space demands 3mm.
- Minimum stroke width: 0.4mm (= 1 nozzle diameter). Bold or sans-serif fonts only.
- Overhang limit: 45° from vertical. Surfaces at >45° need reorientation or workaround.
- Slope warning: text on a slope ≥ 20° will exhibit staircase artifacts — note it.
- Curved surfaces: wrap text along the curve, project onto tangent plane.
- Deboss (carve inward) is easier to print on FDM than emboss (raised letters).
- Wall clearance: keep text ≥ 2mm from any edge to avoid thin-wall collapse.

### Workaround tree (use in order if preferred surface is problematic)
  W1 — Reorient print: rotate model so target surface faces up
  W2 — Scale text up: bigger text always easier than smaller
  W3 — Reduce depth to 0.5mm: minimum viable for tight spaces
  W4 — Switch emboss→deboss or deboss→emboss
  W5 — Line-wrap text along curved surface
  W6 — Project onto tangent plane for compound curves
  W7 — Engrave on adjacent flat surface instead
  W8 — Flag for SLA print (when no FDM surface is viable)

## Output format — reply with EXACTLY this JSON, nothing before or after:

```json
{
  "request_understood": "one-sentence paraphrase of what Javier asked",
  "geometry_notes": "2-3 sentence summary of what you observed in the geometry",
  "proposals": [
    {
      "rank": 1,
      "label": "Top surface — centered",
      "surface_group_index": 1,
      "surface_label": "FLAT_TOP",
      "engravability_score": 1.0,
      "position_description": "Centered on top face. Centroid at (X, Y, Z)mm.",
      "content": "Typhon's Forge",
      "style": "deboss",
      "depth_mm": 0.8,
      "font_height_mm": 5.0,
      "stroke_width_mm": 0.4,
      "orientation_deg": 0,
      "offset_from_edge_mm": 3.0,
      "rationale": "Best surface. Flat top means nozzle runs parallel to face. No overhang risk.",
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
      "depth_mm": 0.6,
      "font_height_mm": 4.0,
      "stroke_width_mm": 0.4,
      "orientation_deg": 0,
      "offset_from_edge_mm": 3.0,
      "rationale": "Side surface is printable with model in standard orientation.",
      "warnings": ["Layer lines will be horizontal — text reads well but slight texture."],
      "workarounds_applied": []
    },
    {
      "rank": 3,
      "label": "Side face — reoriented",
      "surface_group_index": 3,
      "surface_label": "FLAT_SIDE",
      "engravability_score": 0.55,
      "position_description": "Left face, center band.",
      "content": "Typhon's Forge",
      "style": "deboss",
      "depth_mm": 0.6,
      "font_height_mm": 4.0,
      "stroke_width_mm": 0.4,
      "orientation_deg": 90,
      "offset_from_edge_mm": 2.0,
      "rationale": "Requires rotating part 90° on bed. Adds print time but achieves the surface.",
      "warnings": ["Model must be reoriented in slicer — face W1 workaround."],
      "workarounds_applied": ["W1"]
    }
  ],
  "hard_blocks": [],
  "recommendation": "Proposal 1 for most use cases. Proposal 2 if top is functional and cannot be engraved."
}
```

If the model has NO viable surface for the request, fill hard_blocks with the reason
and include only 1 proposal: the best workaround. Never hallucinate a surface that
does not exist in the geometry report.
"""


def run(state: ProjectState, llm: LLM) -> ProjectState:
    """
    Run engraving analysis on state.source_stl.
    Embeds full geometry report in the LLM prompt.
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

    print(f'  [EngravingAgent] Analyzing geometry: {stl_path}')
    try:
        report = geo.full_geometry_report(stl_path)
    except Exception as e:
        state.status = 'engrave_error'
        state.note = f'EngravingAgent: geometry analysis failed — {e}'
        return state

    print(f'    bbox: {report.bbox_x:.1f}×{report.bbox_y:.1f}×{report.bbox_z:.1f}mm  '
          f'faces: {report.face_count}  groups: {len(report.surface_groups)}')
    print(f'    engravable groups (score≥0.5): {len(report.engravable_groups)}')

    if report.warnings:
        for w in report.warnings:
            print(f'    ⚠ {w}')

    # Build the full prompt — geometry data embedded verbatim
    user_msg = f"""=== ENGRAVING REQUEST ===
{engrave_request}

=== FULL GEOMETRY DATA (read every line before proposing anything) ===
{report.text_summary}

=== TASK ===
Propose exactly 3 ranked engraving options for this STL and this request.
Apply every constraint and every workaround from your system prompt.
Return ONLY the JSON block. No prose before or after."""

    print(f'  [EngravingAgent] Sending to {llm.name} ...')
    reply = llm.chat(SYSTEM, [{'role': 'user', 'content': user_msg}], max_tokens=4000)

    # Parse JSON from reply
    proposals = {}
    m = re.search(r'```json\s*(.*?)\s*```', reply, re.DOTALL)
    if m:
        try:
            proposals = json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    if not proposals:
        # Try bare JSON
        m2 = re.search(r'\{.*\}', reply, re.DOTALL)
        if m2:
            try:
                proposals = json.loads(m2.group())
            except json.JSONDecodeError:
                pass

    if not proposals:
        state.status = 'engrave_error'
        state.note = 'EngravingAgent: LLM did not return valid JSON. Raw reply saved to engraving_proposals.'
        state.engraving_proposals = {'raw_reply': reply[:2000]}
        return state

    state.engraving_proposals = proposals
    state.engraving_request = engrave_request
    state.status = 'engrave_pending_approval'

    # Store geometry summary in state for downstream use
    state.mesh = {
        'bbox_x': report.bbox_x,
        'bbox_y': report.bbox_y,
        'bbox_z': report.bbox_z,
        'volume_cm3': report.volume_cm3,
        'face_count': report.face_count,
        'surface_groups': [
            {
                'label': g.label,
                'engravability': g.engravability,
                'area_mm2': round(g.total_area_mm2, 2),
                'angle_deg': round(g.angle_from_vertical, 1),
                'centroid': [round(g.centroid[0],1), round(g.centroid[1],1), round(g.centroid[2],1)],
                'reason': g.engrav_reason,
            }
            for g in report.surface_groups
        ],
    }

    _report_proposals(state)
    return state


def approve(state: ProjectState, choice: int) -> ProjectState:
    """
    Record Javier's approval of proposal 1, 2, or 3.
    Writes engraving_spec to state for the downstream modifier.
    """
    proposals = state.engraving_proposals.get('proposals', [])
    if not proposals or choice < 1 or choice > len(proposals):
        state.note = f'EngravingAgent approve: choice {choice} out of range (have {len(proposals)})'
        return state

    chosen = proposals[choice - 1]
    state.engraving_approved = choice
    state.engraving_spec = chosen
    state.status = 'engrave_approved'
    state.note = f'Engraving approved: {chosen.get("label", "")} — {chosen.get("content", "")}'
    print(f'  [EngravingAgent] Approved proposal {choice}: {state.note}')
    return state


def _report_proposals(state: ProjectState):
    p = state.engraving_proposals
    print(f'\n  EngravingAgent — {p.get("request_understood", "")}')
    print(f'  Geometry: {p.get("geometry_notes", "")}')
    for prop in p.get('proposals', []):
        print(f'\n  [{prop["rank"]}] {prop["label"]} (score={prop["engravability_score"]})')
        print(f'      Surface  : {prop["surface_label"]} — group {prop["surface_group_index"]}')
        print(f'      Position : {prop["position_description"]}')
        print(f'      Spec     : {prop["style"]} / depth={prop["depth_mm"]}mm / '
              f'font={prop["font_height_mm"]}mm / stroke={prop["stroke_width_mm"]}mm')
        print(f'      Rationale: {prop["rationale"]}')
        for w in prop.get('warnings', []):
            print(f'      ⚠ {w}')
        for wa in prop.get('workarounds_applied', []):
            print(f'      🔧 Workaround {wa} applied')
    if p.get('hard_blocks'):
        print(f'\n  HARD BLOCKS:')
        for b in p['hard_blocks']:
            print(f'    ✗ {b}')
    print(f'\n  Recommendation: {p.get("recommendation", "")}')
    print('\n  → Reply: approve engrave 1  /  approve engrave 2  /  approve engrave 3')
