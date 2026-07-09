#!/usr/bin/env python3
"""
forge-slicer entrypoint
Runs Creality Print CLI via xvfb-run and returns a JSON result.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="forge-slicer: headless STL → gcode")
    p.add_argument("--stl", required=True, help="Absolute path to input STL inside container")
    p.add_argument("--machine", required=True, help="Path to machine profile JSON")
    p.add_argument("--process", required=True, help="Path to process profile JSON")
    p.add_argument("--filament", required=True, help="Path to filament profile JSON")
    p.add_argument("--output", required=True, help="Output directory for gcode")
    p.add_argument("--supports", default="no", choices=["yes", "no"], help="Enable supports")
    p.add_argument("--support-type", default="normal", choices=["normal", "tree"], help="Support structure type")
    return p.parse_args()


def fail(msg: str):
    print(json.dumps({
        "success": False,
        "gcode_path": None,
        "print_time_raw": None,
        "print_time_s": None,
        "filament_g": None,
        "filament_mm": None,
        "error": msg,
    }))
    sys.exit(1)


def find_gcode(output_dir: str, stl_path: str) -> str | None:
    """
    Creality Print names the output after the input file.
    Try to find any .gcode file newer than we started.
    """
    stl_stem = Path(stl_path).stem
    output = Path(output_dir)
    candidates = sorted(output.glob("*.gcode"), key=lambda f: f.stat().st_mtime, reverse=True)
    # Prefer files whose name contains the STL stem
    for c in candidates:
        if stl_stem.lower() in c.name.lower():
            return str(c)
    # Fall back to most-recently-modified gcode
    if candidates:
        return str(candidates[0])
    return None


def parse_gcode(gcode_path: str) -> dict:
    result = {
        "print_time_raw": None,
        "print_time_s": None,
        "filament_g": None,
        "filament_mm": None,
    }
    try:
        with open(gcode_path, "r", errors="replace") as f:
            for line in f:
                # ── Print time ──────────────────────────────────────────────
                # ; estimated printing time (normal mode) = 1h 23m 4s
                m = re.search(
                    r";\s*estimated printing time.*?=\s*(.+)",
                    line, re.IGNORECASE
                )
                if m and result["print_time_raw"] is None:
                    raw = m.group(1).strip()
                    result["print_time_raw"] = raw
                    result["print_time_s"] = _parse_time_to_seconds(raw)

                # ── Filament grams ───────────────────────────────────────────
                # ; total filament used [g] = 14.23
                m = re.search(
                    r";\s*total filament used \[g\]\s*=\s*([\d.]+)",
                    line, re.IGNORECASE
                )
                if m and result["filament_g"] is None:
                    result["filament_g"] = float(m.group(1))

                # ── Filament mm ──────────────────────────────────────────────
                # ; total filament used [mm] = 4821
                m = re.search(
                    r";\s*total filament used \[mm\]\s*=\s*([\d.]+)",
                    line, re.IGNORECASE
                )
                if m and result["filament_mm"] is None:
                    result["filament_mm"] = float(m.group(1))

                # Stop early once we have everything
                if all(v is not None for v in result.values()):
                    break
    except OSError as e:
        pass  # Return whatever was parsed
    return result


def _parse_time_to_seconds(raw: str) -> int:
    """
    Convert strings like '1h 23m 4s', '45m 10s', '2h 5s' to seconds.
    """
    total = 0
    for match in re.finditer(r"(\d+)\s*([hms])", raw):
        val = int(match.group(1))
        unit = match.group(2)
        if unit == "h":
            total += val * 3600
        elif unit == "m":
            total += val * 60
        elif unit == "s":
            total += val
    return total


def main():
    args = parse_args()

    # Validate inputs
    if not os.path.isfile(args.stl):
        fail(f"STL not found: {args.stl}")
    if not os.path.isfile(args.machine):
        fail(f"Machine profile not found: {args.machine}")
    if not os.path.isfile(args.process):
        fail(f"Process profile not found: {args.process}")
    if not os.path.isfile(args.filament):
        fail(f"Filament profile not found: {args.filament}")

    os.makedirs(args.output, exist_ok=True)
    os.makedirs("/log", exist_ok=True)

    # Build CLI command — use AppRun wrapper (its bundled LD_LIBRARY_PATH is needed)
    creality_bin = "/opt/creality-print/AppRun"
    settings_arg = f"{args.machine};{args.process}"
    filament_arg = args.filament

    cmd = [
        "xvfb-run",
        "--server-args=-screen 0 1024x768x24",
        "--auto-servernum",
        creality_bin,
        "--load-settings", settings_arg,
        "--load-filaments", filament_arg,
        "--slice", "0",
        "--outputdir", args.output,
        args.stl,
    ]

    if args.supports == "yes":
        cmd += ["--enable-support", "1", "--support-type", args.support_type]

    env = os.environ.copy()
    env["TMPDIR"] = "/log"

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10-minute hard timeout
            env=env,
        )
    except subprocess.TimeoutExpired:
        fail("CrealityPrint timed out after 600 seconds")
    except FileNotFoundError as e:
        fail(f"Binary not found: {e}")

    if proc.returncode != 0:
        stderr_snippet = (proc.stderr or "").strip()[-1000:]  # last 1000 chars
        fail(f"CrealityPrint exited with code {proc.returncode}: {stderr_snippet}")

    # Locate gcode output
    gcode_path = find_gcode(args.output, args.stl)
    if not gcode_path:
        fail(f"Slicing appeared to succeed (exit 0) but no .gcode found in {args.output}")

    # Parse metadata from gcode
    stats = parse_gcode(gcode_path)

    print(json.dumps({
        "success": True,
        "gcode_path": gcode_path,
        "print_time_raw": stats["print_time_raw"],
        "print_time_s": stats["print_time_s"],
        "filament_g": stats["filament_g"],
        "filament_mm": stats["filament_mm"],
        "error": None,
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
