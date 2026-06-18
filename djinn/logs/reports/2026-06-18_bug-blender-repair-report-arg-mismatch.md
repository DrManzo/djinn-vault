---
title: Bug Report — repair.py --report arg mismatch (required path vs bool flag)
system: djinn-blender-repair / typhons-forge
severity: high
status: fixed
date: 2026-06-18
---

# Bug — repair.py --report arg: required path vs bool flag

**System:** `~/typhons-forge/blender/scripts/repair.py`, `~/.local/bin/djinn-blender-repair`
**Severity:** high (tool completely non-functional on first run)
**Status:** fixed

## Root Cause

Marcus's `repair.py` defines `--report` as a required positional-style path argument:
```python
p.add_argument('--report', required=True)  # expects a file path
```

The wrapper `djinn-blender-repair` was written (by Claude) treating `--report` as a boolean store_true flag and never passing it to Blender. Blender's argparse then exited with:
```
usage: blender [-h] --input INPUT --out OUT --report REPORT
blender: error: the following arguments are required: --report
```

## Symptom

First run of `djinn-blender-repair` immediately exits non-zero. Misleading error: wrapper prints "non-manifold edges remain" but the real cause is a missing CLI arg.

## Fix

Wrapper now derives `report_path` from `out_path` and always passes it:
```python
report_path = out_path.replace(".stl", "_report.json").replace(".STL", "_report.json")
cmd = [..., "--report", report_path]
```

## Rule Learned

When writing a wrapper for a script you didn't write, read the actual argparse definitions before coding the call — don't assume flag semantics from the flag name. `--report` is ambiguous (path vs bool).

*— Claude, 2026-06-18*
