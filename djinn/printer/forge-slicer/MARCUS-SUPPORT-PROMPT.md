# Marcus Build Prompt — Support Decision Module

## What This Is

Add mesh-based support analysis to the Djinn design pipeline.
Right now the pipeline asks an LLM to guess `supports_needed: true/false` — that's unreliable.
Replace it with real geometry analysis using trimesh (already in the project).

This is a Python-only task. No Docker, no new services.

---

## Research Context

Full research doc at: `~/Downloads/support-decision-workflow-research.md`

Key decisions already made:
- Supports off by default — they're a cost center
- Three modes: none / local / full (not binary)
- Decision variables: overhang angle, bridge length, material, profile intent
- Material thresholds: PLA most permissive, ABS strictest

---

## Starting Point

A draft module already exists at:
`~/Obsidian/djinn/printer/agent/orchestrator/agents/support_analysis.py`

Read it. It contains the geometry math, threshold tables, scoring logic, and `analyze()` function.
Your job is to wire it into the existing pipeline and fix anything that doesn't work.

---

## Files To Modify

### 1. `agents/proto_opt.py`

After each STL renders successfully (inside the `for tag, match in [...]` loop where `ok` is True),
call `support_analysis.analyze()` on the STL.

Use:
- `material = state.brief.get("material", "pla")`  
- `profile = "proto"` for the prototype variant, `"production"` for the production variant

Store the result in `files[tag + "_support"] = analysis_result`.

After the loop, use the **production** variant's analysis to set:
```python
state.supports_needed = analysis_result["supports_recommended"]
state.support_mode    = analysis_result["support_mode"]
```

Print a one-liner per variant:
```
    → prototype support: none (risk 12)
    → production support: local (risk 34) — steep_overhang
```

### 2. `project_state.py`

Add one field to the `ProjectState` dataclass:
```python
support_mode: str = "none"
```
Place it next to `supports_needed` (line ~63).

### 3. `agents/doe_opt.py`

In `run()`, at the end where `profile = { ... }` is built (around line 211),
add this key so `djinn-model-slice` can read it:
```python
"supports_needed": supports,
"support_mode":    "local" if supports else "none",
```

The `support_mode` here is a fallback — `proto_opt` will have already set the real value on `state`.

### 4. `orchestrator.py` — `_report_variants()` function

Add support recommendation output after the existing variant lines:
```python
for tag in ("prototype", "production"):
    sa = state.variants.get("files", {}).get(f"{tag}_support", {})
    if sa:
        mode  = sa.get("support_mode", "?")
        score = sa.get("risk_score", "?")
        codes = ", ".join(sa.get("reason_codes", [])) or "clean"
        print(f"  Support ({tag}): {mode} (risk {score}) — {codes}")
        print(f"    {sa.get('user_message', '')}")
```

---

## Validation

```bash
cd ~/Obsidian/djinn/printer/agent
python3 -c "
from orchestrator.agents import support_analysis
result = support_analysis.analyze(
    '$HOME/printer-files/queue/plate_job3.stl',
    material='pla',
    profile='production'
)
import json; print(json.dumps(result, indent=2))
"
```

Expected: JSON with `support_mode`, `risk_score`, `reason_codes`, `stats.total_faces` > 0.

Then run a full pipeline job and confirm the variant report shows the support lines.

---

## What To Report Back

1. Does `support_analysis.analyze()` run without error on a real STL?
2. What support mode + risk score did it give on `plate_job3.stl` with PLA/production?
3. Any threshold adjustments needed (if scores seem too high/low for obvious geometry)?
4. Are there any import errors or trimesh version issues?

Do NOT modify `djinn-model-slice` — Claude will wire support_mode → Creality Print flags after forge-slicer is done.

---

*Spec by Claude — 2026-06-14*
