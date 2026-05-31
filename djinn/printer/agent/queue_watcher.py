#!/usr/bin/env python3
"""
queue_watcher.py — Djinn print queue watcher.
Scans queue/ for new gcode files, extracts metadata from filenames and gcode
headers, routes through brief -> price -> report, and outputs the quote.

Usage:
  python3 queue_watcher.py              # scan all files in queue/
  python3 queue_watcher.py --name model  # scan files matching name
  python3 queue_watcher.py --all         # re-scan even previously processed files

— Marcus
"""
import json, os, re, sys, argparse
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
AGENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = AGENT_DIR.parent
COMMS_DIR = PROJECT_DIR / "commissions"
QUEUE_DIR = PROJECT_DIR / "queue"

# ── Processed file tracker ──────────────────────────────────────────────────
PROCESSED_LOG = AGENT_DIR / ".queue_processed.json"


def _load_processed() -> set:
    if PROCESSED_LOG.exists():
        return set(json.loads(PROCESSED_LOG.read_text()))
    return set()


def _save_processed(files: set):
    PROCESSED_LOG.write_text(json.dumps(sorted(files), indent=2))


# ── Gcode metadata parser ────────────────────────────────────────────────────

GCODE_FILAMENT_RE = re.compile(r'; filament used \[g\]\s*=\s*([\d.]+)')
GCODE_TOTAL_FILAMENT_RE = re.compile(r'; total filament used \[g\]\s*=\s*([\d.]+)')
GCODE_TIME_FULL_RE = re.compile(r'; estimated printing time \(normal mode\)\s*=\s*(?:(\d+)h\s*)?(\d+)m\s*(\d+)s')
GCODE_TIME_MIN_RE = re.compile(r'; estimated printing time \(normal mode\)\s*=\s*(\d+)m\s*(\d+)s')
GCODE_TIME_SEC_RE = re.compile(r'; estimated printing time \(normal mode\)\s*=\s*(\d+)s')


def parse_gcode_metadata(path: Path) -> dict:
    """Extract filament weight (g) and print time (h) from a gcode file header."""
    meta = {"grams": None, "hours": None}
    try:
        text = path.read_text(errors="replace")
    except Exception:
        return meta

    m = GCODE_TOTAL_FILAMENT_RE.search(text)
    if not m:
        m = GCODE_FILAMENT_RE.search(text)
    if m:
        meta["grams"] = float(m.group(1))

    m = GCODE_TIME_FULL_RE.search(text)
    if m:
        h = int(m.group(1)) if m.group(1) else 0
        mn, s = int(m.group(2)), int(m.group(3))
        meta["hours"] = round(h + mn / 60 + s / 3600, 4)
    else:
        m = GCODE_TIME_MIN_RE.search(text)
        if m:
            mn, s = int(m.group(1)), int(m.group(2))
            meta["hours"] = round(mn / 60 + s / 3600, 4)
        else:
            m = GCODE_TIME_SEC_RE.search(text)
            if m:
                meta["hours"] = round(int(m.group(1)) / 3600, 4)

    return meta


# ── Filename parser ──────────────────────────────────────────────────────────

JOB_ID_RE = re.compile(r'_job(\d+)')


def parse_filename(name: str) -> dict:
    """Extract piece name and job id from a queue filename."""
    stem = Path(name).stem
    m = JOB_ID_RE.search(stem)
    job_id = int(m.group(1)) if m else None
    piece_name = JOB_ID_RE.sub("", stem).replace("_", " ").strip().title()
    if not piece_name:
        piece_name = stem
    return {"piece_name": piece_name, "job_id": job_id}


# ── Queue scanner ────────────────────────────────────────────────────────────

def scan_queue(name_filter: str = None, force: bool = False) -> list[dict]:
    """Scan queue/, extract metadata, build briefs. Returns list of brief dicts."""
    processed = set() if force else _load_processed()
    results = []

    if not QUEUE_DIR.exists():
        print(f"  Queue dir not found: {QUEUE_DIR}")
        return results

    files = sorted(QUEUE_DIR.iterdir(), key=lambda p: p.stat().st_mtime)

    for f in files:
        if not f.is_file():
            continue
        if f.name in processed:
            continue

        ext = f.suffix.lower()
        if ext not in (".gcode", ".stl", ".3mf"):
            continue

        info = parse_filename(f.name)
        if name_filter and name_filter.lower() not in info["piece_name"].lower():
            continue

        grams = None
        hours = None

        if ext == ".gcode":
            meta = parse_gcode_metadata(f)
            grams = meta["grams"]
            hours = meta["hours"]
        elif ext == ".stl":
            grams = None
            hours = None

        brief = {
            "job_type": "functional_custom_part",
            "piece_name": info["piece_name"],
            "quantity": 1,
            "material": {
                "type": "PLA",
                "part_weight_g": grams or 50,
                "support_weight_g": 0,
                "waste_buffer_pct": 10,
            },
            "print": {
                "print_time_hours": hours or 2.0,
            },
            "labor": {
                "prep_minutes": 10,
                "postprocess_minutes": 10,
                "design_minutes": 0,
            },
            "extras": {
                "packaging_cost_usd": 0.50,
            },
            "market": {
                "comparables": [],
            },
        }

        results.append({
            "filename": f.name,
            "gcode_grams": grams,
            "gcode_hours": hours,
            "brief": brief,
        })

        if not force:
            processed.add(f.name)

    _save_processed(processed)

    return results


# ── Pipeline runner ──────────────────────────────────────────────────────────

def run_pipeline(results: list[dict], output: str = "terminal"):
    """Run brief -> price -> report for each result."""
    sys.path.insert(0, str(COMMS_DIR.parent))
    from commissions import brief as brf
    from commissions import price as prc
    from commissions import report as rpt

    scan_msg = f"  Queue scan: {len(results)} new file(s)"
    if results:
        scan_msg += " — " + ", ".join(r["filename"] for r in results)
    print(scan_msg)

    for r in results:
        print(f"\n{'=' * 52}")
        print(f"  File: {r['filename']}")
        if r["gcode_grams"]:
            print(f"  From gcode: {r['gcode_grams']}g @ {r['gcode_hours']}h")
        print(f"  {'─' * 48}")

        bf = r["brief"]
        validated = brf.validate_brief(bf)
        if not validated.valid:
            for e in validated.errors:
                print(f"  Validation error: {e}")
            continue

        quote = prc.quote_from_dict(validated.brief)
        quoted = rpt.render(quote, bf, output=output, save=True)
        print(quoted)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Djinn print queue watcher — scan queue/ and run brief → price → report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--name", help="Filter by piece name (case-insensitive substring)")
    ap.add_argument("--all", action="store_true", help="Re-scan all files, including processed")
    ap.add_argument("--output", choices=["terminal", "telegram", "markdown", "json"],
                    default="terminal", help="Output format (default: terminal)")
    ap.add_argument("--watch", action="store_true", help="Continuous watch mode (poll every 30s)")
    args = ap.parse_args()

    results = scan_queue(name_filter=args.name, force=args.all)

    if args.watch:
        import time
        print(f"  Watching {QUEUE_DIR} every 30s...")
        processed = set(f.name for f in QUEUE_DIR.iterdir() if f.is_file()) if not args.all else set()
        while True:
            time.sleep(30)
            new_results = scan_queue(name_filter=args.name, force=False)
            if new_results:
                run_pipeline(new_results, output=args.output)
    else:
        run_pipeline(results, output=args.output)

    if not results:
        print("  No new files to process.")


if __name__ == "__main__":
    main()
