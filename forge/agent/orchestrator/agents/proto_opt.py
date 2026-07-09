"""
ProtoOptAgent — generates prototype-light and production-ready variants from one design.
Outputs two SCAD files and renders both to STL.
"""
import json, pathlib, re, subprocess
from ..llm import LLM
from ..project_state import ProjectState
from . import support_analysis

MODELS_DIR = pathlib.Path.home() / "printer-files/models"

SYSTEM = """You are ProtoOptAgent. You generate two geometry variants from one OpenSCAD design.

## Prototype-light rules
- Reduce wall thickness to max(1.6, original * 0.55)
- Cut internal solid mass — add hollowing or rib structure where appearance allows
- Remove decorative/structural bulk from non-load-bearing regions
- PRESERVE exactly: mating faces, hole locations, outer silhouette, $fn

## Production-ready rules
- Keep or increase critical wall thickness
- Add fillets at stress concentrations (r=2–3mm)
- Keep all functional interfaces
- Only apply topology improvements, not simplifications

## Output — reply with EXACTLY this structure:

```json
{
  "prototype": {
    "description": "what changed for prototype",
    "parameter_overrides": {"WALL_T": 1.6},
    "expected_mass_reduction_pct": 35,
    "expected_time_reduction_pct": 30
  },
  "production": {
    "description": "what changed for production",
    "parameter_overrides": {"WALL_T": 3.2, "FILLET_R": 2.0},
    "strength_notes": "stronger because ..."
  }
}
```

```openscad_prototype
// Complete prototype variant — full file with prototype parameters applied
```

```openscad_production
// Complete production variant — full file with production parameters applied
```
"""


def _render_stl(scad_path: pathlib.Path, stl_path: pathlib.Path) -> tuple[bool, str]:
    """Return (success, stderr_tail)."""
    result = subprocess.run(
        ["openscad", "--render", "--export-format", "stl", "-o", str(stl_path), str(scad_path)],
        capture_output=True, text=True, timeout=180,
    )
    stderr = (result.stderr or "").strip()
    ok = result.returncode == 0 and stl_path.exists() and stl_path.stat().st_size > 0
    return ok, stderr


def run(state: ProjectState, llm: LLM) -> ProjectState:
    scad_path = pathlib.Path(state.source_scad)
    if not scad_path.exists():
        raise FileNotFoundError(f"Source SCAD not found: {scad_path}")

    current_code = scad_path.read_text()

    user_msg = f"""Design context:
{json.dumps(state.concept, indent=2)}

Source OpenSCAD file ({scad_path.name}):
```openscad
{current_code}
```

Generate prototype-light and production-ready variants."""

    print(f"  [ProtoOptAgent] via {llm.name} ...")
    reply = llm.chat(SYSTEM, [{"role": "user", "content": user_msg}], max_tokens=8000)

    json_match  = re.search(r'```json\s*(.*?)\s*```', reply, re.DOTALL)
    proto_match = re.search(r'```openscad_prototype\s*(.*?)\s*```', reply, re.DOTALL)
    prod_match  = re.search(r'```openscad_production\s*(.*?)\s*```', reply, re.DOTALL)

    variant_meta = {}
    if json_match:
        try:
            variant_meta = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    base = scad_path.stem
    files = {}

    material = state.brief.get("material", "pla")
    production_analysis = None
    render_errors = []

    for tag, match, profile_name in [
        ("prototype",  proto_match, "proto"),
        ("production", prod_match,  "production"),
    ]:
        code = match.group(1) if match else current_code
        scad_out = MODELS_DIR / f"{base}_{tag}.scad"
        scad_out.write_text(code)

        stl_out = MODELS_DIR / f"{base}_{tag}.stl"
        ok, stderr = _render_stl(scad_out, stl_out)
        if ok:
            size_kb = stl_out.stat().st_size // 1024
            print(f"    → {tag} STL: {stl_out.name} ({size_kb}KB)")
            files[tag] = str(stl_out)

            # ── Support analysis ───────────────────────────────────────
            try:
                sa = support_analysis.analyze(
                    stl_out,
                    material=material,
                    profile=profile_name,
                )
                files[tag + "_support"] = sa
                mode  = sa["support_mode"]
                score = sa["risk_score"]
                codes = ", ".join(sa["reason_codes"]) or "clean"
                print(f"    → {tag} support: {mode} (risk {score}) — {codes}")
                if tag == "production":
                    production_analysis = sa
            except Exception as exc:
                print(f"    ⚠ support_analysis failed for {tag}: {exc}")
        else:
            tail = stderr[-400:] if len(stderr) > 400 else stderr
            print(f"    → {tag} render failed — SCAD: {scad_out.name}")
            print(f"       OpenSCAD error: {tail}")
            render_errors.append(f"{tag}: {tail}")

    if render_errors:
        raise RuntimeError(
            f"OpenSCAD render failed for {len(render_errors)} variant(s):\n" +
            "\n".join(render_errors) +
            "\n\nFix the source SCAD and retry. Check: all called modules are defined in the file; "
            "no undefined helpers like fillet_all(); top-level call only uses defined modules."
        )

    # Use production analysis to set state-level support fields
    if production_analysis is not None:
        state.supports_needed = production_analysis["supports_recommended"]
        state.support_mode    = production_analysis["support_mode"]

    state.variants = {**variant_meta, "files": files}
    state.status = "doe_opt"

    return state
