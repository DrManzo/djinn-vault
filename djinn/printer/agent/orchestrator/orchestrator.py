"""
Djinn Manufacturing Orchestrator — intent parser and agent router.
Entry point for the full DesignGen → Edit → ProtoOpt → DOE → PlateNest → Price pipeline.
"""
import json, re
from .project_state import ProjectState, _load_queue
from .llm import LLM
from .agents import design_gen, design_edit, proto_opt, doe_opt, plate_nest

INTENT_SYSTEM = """You are a manufacturing pipeline router for a 3D printing system.

Classify the user input into ONE intent:
  new_design   — create a new part from scratch
  edit_design  — modify an existing design
  optimize     — generate prototype/production geometry variants
  doe          — optimize slicer/process parameters
  plate        — arrange parts on a print plate
  price        — get a cost quote
  status       — show job queue status
  unknown      — none of the above

Reply with ONLY valid JSON: {"intent": "...", "job_id": null}
"""


def classify(text: str, llm: LLM) -> dict:
    reply = llm.chat(INTENT_SYSTEM, [{"role": "user", "content": text}], max_tokens=80)
    m = re.search(r'\{[^}]+\}', reply)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return {"intent": "unknown", "job_id": None}


def run(
    user_input: str,
    job_id: int = None,
    edit_request: str = None,
    doe_goal: str = "prototype_fast",
    plate_items: list = None,
    printer: dict = None,
    auto_advance: bool = False,
) -> ProjectState:
    """
    Main entry point.

    auto_advance: if True, automatically runs the full pipeline from current state forward.
    Otherwise stops after each agent and returns state for inspection.
    """
    llm = LLM()
    print(f"\nDjinn Manufacturing [{llm.name}]")
    print("─" * 52)

    if printer is None:
        printer = {
            "model": "Ender-3 V3 Plus",
            "has_enclosure": False,
            "hotend_sock": True,
            "bed_insulated": False,
        }

    # Load or create state
    if job_id:
        state = ProjectState.load(job_id)
        intent = _status_to_intent(state.status)
        if edit_request:
            intent = "edit_design"
    else:
        try:
            brief = json.loads(user_input)
        except json.JSONDecodeError:
            brief = {"request": user_input, "piece_name": user_input[:50]}
        state = ProjectState.new(brief)
        state.save()
        print(f"  Job #{state.id} created — {state.note}")
        intent = "new_design"

    print(f"  Status: {state.status} | Intent: {intent}")

    # Route to agent
    if intent == "new_design":
        state = design_gen.run(state, llm)
        state.save()
        _report_concept(state)
        if not auto_advance:
            return state

    if intent in ("edit_design",) or edit_request:
        req = edit_request or user_input
        state = design_edit.run(state, req, llm)
        state.save()
        if not auto_advance:
            return state

    if intent == "optimize" or (auto_advance and state.status == "design_edit"):
        state = proto_opt.run(state, llm)
        state.save()
        _report_variants(state)
        if not auto_advance:
            return state

    if intent == "doe" or (auto_advance and state.status == "doe_opt"):
        state = doe_opt.run(state, doe_goal, printer)
        state.save()
        _report_doe(state)
        if not auto_advance:
            return state

    if intent == "plate" or (auto_advance and state.status == "plate_nest"):
        state = plate_nest.run(state, plate_items)
        state.save()
        if not auto_advance:
            return state

    if intent == "status":
        _show_queue()

    return state


# ── Status helpers ────────────────────────────────────────────────────────────

def _status_to_intent(status: str) -> str:
    return {
        "design_gen":  "new_design",
        "design_edit": "edit_design",
        "proto_opt":   "optimize",
        "doe_opt":     "doe",
        "plate_nest":  "plate",
        "priced":      "price",
    }.get(status, "status")


def _show_queue():
    queue = _load_queue()
    jobs = queue.get("jobs", [])
    if not jobs:
        print("  Queue empty.")
        return
    print(f"\n  {'ID':>3}  {'Status':<16}  Note")
    print("  " + "─" * 55)
    for j in jobs:
        print(f"  {j.get('id', 0):>3}  {j.get('status', '?'):<16}  {str(j.get('note', ''))[:40]}")


def _report_concept(state: ProjectState):
    c = state.concept
    print(f"\n  Concept: {c.get('concept_summary', '—')}")
    for f in c.get("key_features", []):
        print(f"    • {f}")
    print(f"  Orientation: {c.get('print_orientation', '?')} | "
          f"Supports: {c.get('supports_needed', '?')} | "
          f"~{c.get('material_g_estimate', '?')}g / ~{c.get('estimated_print_time_h', '?')}hr")
    print(f"  SCAD → {state.source_scad}")


def _report_variants(state: ProjectState):
    files = state.variants.get("files", {})
    pm = state.variants.get("prototype", {})
    qm = state.variants.get("production", {})
    print(f"\n  Prototype: {pm.get('description', '—')}")
    print(f"    -{pm.get('expected_mass_reduction_pct', '?')}% mass  "
          f"-{pm.get('expected_time_reduction_pct', '?')}% time")
    print(f"    → {files.get('prototype', '—')}")
    print(f"  Production: {qm.get('description', '—')}")
    print(f"    {qm.get('strength_notes', '')}")
    print(f"    → {files.get('production', '—')}")


def _report_doe(state: ProjectState):
    d = state.doe_profile
    p = d.get("recommended_profile", {})
    s = d.get("expected_savings_vs_standard", {})
    print(f"\n  DOE ({d.get('goal')}) — {d.get('candidates_passing')}/{d.get('candidates_total')} candidates")
    print(f"  Best: {p.get('layer_height_mm')}mm | {p.get('print_speed_mms')}mm/s | "
          f"{p.get('infill_type')} {p.get('infill_density_pct')}% | {p.get('wall_count')} walls")
    print(f"  Savings: -{s.get('time_reduction_pct', 0)}% time | "
          f"-{s.get('material_reduction_pct', 0)}% material | "
          f"confidence: {d.get('confidence')}")
    for n in d.get("machine_notes", []):
        print(f"    ⚙ {n}")
    for t in d.get("tradeoffs", []):
        print(f"    ⚠ {t}")
