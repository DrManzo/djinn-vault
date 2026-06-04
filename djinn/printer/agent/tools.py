"""
Tool implementations for Djinn Print agent.
"""

import os, subprocess, tempfile, json, requests

MOONRAKER   = "http://192.168.1.113:7125"
MODELS_DIR  = os.path.expanduser("~/printer-files/models")


# ── Tool definitions for Ollama ─────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_and_run",
            "description": (
                "Write a Python script to disk and execute it. "
                "Use this to generate STL or gcode files. "
                "The script should write its output file to MODELS_DIR."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Script filename, e.g. gen_widget.py"
                    },
                    "code": {
                        "type": "string",
                        "description": "Complete Python source code"
                    }
                },
                "required": ["filename", "code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "printer_status",
            "description": "Get current printer state, print progress, and temperatures.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upload_and_print",
            "description": "Upload a gcode file to the printer and start printing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Absolute path to the .gcode file"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upload_stl",
            "description": "Upload an STL file to the printer (for manual slicing via OrcaSlicer).",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Absolute path to the .stl file"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List STL and gcode files available in the models directory.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_print",
            "description": "Cancel the current print job.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]


# ── Tool implementations ─────────────────────────────────────────────────────

def write_and_run(filename: str, code: str) -> str:
    os.makedirs(MODELS_DIR, exist_ok=True)
    script_path = os.path.join(MODELS_DIR, filename)
    with open(script_path, "w") as f:
        f.write(code)
    result = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=60
    )
    out = result.stdout.strip()
    err = result.stderr.strip()
    if result.returncode != 0:
        return f"ERROR (exit {result.returncode}):\n{err}\n{out}"
    return f"OK:\n{out}" + (f"\nSTDERR: {err}" if err else "")


def printer_status() -> str:
    try:
        r = requests.get(
            f"{MOONRAKER}/printer/objects/query",
            params={"objects": "print_stats toolhead heater_bed extruder"},
            timeout=5
        )
        d = r.json()["result"]["status"]
        ps  = d.get("print_stats", {})
        hb  = d.get("heater_bed", {})
        ext = d.get("extruder", {})
        lines = [
            f"State:    {ps.get('state', '?')}",
            f"File:     {ps.get('filename', '—')}",
            f"Progress: {ps.get('progress', 0)*100:.1f}%",
            f"Hotend:   {ext.get('temperature', 0):.1f}°C / {ext.get('target', 0):.0f}°C",
            f"Bed:      {hb.get('temperature', 0):.1f}°C / {hb.get('target', 0):.0f}°C",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"Moonraker unreachable: {e}"


def upload_and_print(filepath: str) -> str:
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"
    filename = os.path.basename(filepath)
    try:
        # Upload
        with open(filepath, "rb") as f:
            r = requests.post(
                f"{MOONRAKER}/server/files/upload",
                files={"file": (filename, f, "application/octet-stream")},
                data={"path": "gcodes"},
                timeout=30
            )
        if r.status_code != 201:
            return f"Upload failed ({r.status_code}): {r.text}"
        # Start print
        r2 = requests.post(
            f"{MOONRAKER}/printer/print/start",
            json={"filename": f"gcodes/{filename}"},
            timeout=10
        )
        if r2.status_code != 200:
            return f"Upload OK but start failed ({r2.status_code}): {r2.text}"
        return f"Printing: {filename}"
    except Exception as e:
        return f"Error: {e}"


def upload_stl(filepath: str) -> str:
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"
    filename = os.path.basename(filepath)
    try:
        with open(filepath, "rb") as f:
            r = requests.post(
                f"{MOONRAKER}/server/files/upload",
                files={"file": (filename, f, "application/octet-stream")},
                data={"path": "gcodes"},
                timeout=30
            )
        if r.status_code == 201:
            return f"Uploaded: {filename}"
        return f"Failed ({r.status_code}): {r.text}"
    except Exception as e:
        return f"Error: {e}"


def list_files() -> str:
    if not os.path.exists(MODELS_DIR):
        return "Models directory not found."
    files = sorted(os.listdir(MODELS_DIR))
    stls   = [f for f in files if f.endswith(".stl")]
    gcodes = [f for f in files if f.endswith(".gcode")]
    scripts = [f for f in files if f.endswith(".py")]
    out = []
    if stls:   out.append("STL:\n  " + "\n  ".join(stls))
    if gcodes: out.append("Gcode:\n  " + "\n  ".join(gcodes))
    if scripts: out.append("Scripts:\n  " + "\n  ".join(scripts))
    return "\n".join(out) if out else "No files found."


def cancel_print() -> str:
    try:
        r = requests.post(f"{MOONRAKER}/printer/print/cancel", timeout=5)
        return "Cancelled." if r.status_code == 200 else f"Failed ({r.status_code}): {r.text}"
    except Exception as e:
        return f"Error: {e}"


# ── Dispatch ─────────────────────────────────────────────────────────────────

TOOL_MAP = {
    "write_and_run":   lambda a: write_and_run(**a),
    "printer_status":  lambda a: printer_status(),
    "upload_and_print":lambda a: upload_and_print(**a),
    "upload_stl":      lambda a: upload_stl(**a),
    "list_files":      lambda a: list_files(),
    "cancel_print":    lambda a: cancel_print(),
}


def run_tool(name: str, args: dict) -> str:
    fn = TOOL_MAP.get(name)
    if fn is None:
        return f"Unknown tool: {name}"
    try:
        return fn(args)
    except Exception as e:
        return f"Tool error ({name}): {e}"
