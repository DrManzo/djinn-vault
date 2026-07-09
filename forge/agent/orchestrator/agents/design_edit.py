"""
DesignEditAgent — modifies an existing OpenSCAD design without rebuilding from scratch.
Handles: parameter changes, feature additions, printability fixes, variant generation.
"""
import pathlib, re
from ..llm import LLM
from ..project_state import ProjectState

SYSTEM = """You are DesignEditAgent. You modify existing OpenSCAD designs.

## Rules
- Prefer changing PARAMETER VALUES at the top over restructuring geometry
- If geometry must change, preserve all unrelated modules and geometry exactly
- Keep every edit parametric — no magic numbers without a named variable
- Maintain $fn, fillets, and wall thickness from the original
- If source is a mesh-only STL (no SCAD), propose a reconstruction plan first

## Output — reply with EXACTLY this structure:

```changes
Changed: [what you changed]
Preserved: [what you left alone]
Tradeoffs: [strength/printability effects, if any]
```

```openscad
// [full modified file — include everything, not just changed lines]
```
"""


def run(state: ProjectState, edit_request: str, llm: LLM) -> ProjectState:
    scad_path = pathlib.Path(state.source_scad)
    if not scad_path.exists():
        raise FileNotFoundError(f"Source SCAD not found: {scad_path}")

    current_code = scad_path.read_text()

    user_msg = f"""Current design ({scad_path.name}):

```openscad
{current_code}
```

Edit request: {edit_request}

Apply the edit and return the complete modified file."""

    print(f"  [DesignEditAgent] via {llm.name} ...")
    reply = llm.chat(SYSTEM, [{"role": "user", "content": user_msg}], max_tokens=6000)

    changes_match = re.search(r'```changes\s*(.*?)\s*```', reply, re.DOTALL)
    scad_match    = re.search(r'```openscad\s*(.*?)\s*```', reply, re.DOTALL)

    changes_text = changes_match.group(1).strip() if changes_match else "changes applied"
    new_code     = scad_match.group(1)            if scad_match    else reply

    scad_path.write_text(new_code)

    state.edit_history.append({
        "request": edit_request,
        "changes": changes_text,
    })

    print(f"    → edit #{len(state.edit_history)} applied")
    for line in changes_text.splitlines():
        print(f"      {line}")

    return state
