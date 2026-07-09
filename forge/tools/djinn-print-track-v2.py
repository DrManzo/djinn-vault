#!/usr/bin/env python3
"""
djinn-print-track v2 — WebSocket-driven print tracker for Typhon's Forge.
Replaces v1 (HTTP polling) with event-driven Moonraker WebSocket subscription.
Single script, zero Docker dependencies.

CLI:
  djinn-print-track                    Run daemon (foreground)
  djinn-print-track status             Current print + spool bar
  djinn-print-track summary            Print history, success rate, filament totals
  djinn-print-track spool ...          Add/swap active spool
  djinn-print-track backfill ...       Backfill a completed print
  djinn-print-track verify             Data integrity check
"""
import os, sys, time, json, datetime, pathlib, signal, shutil, math, re, traceback

# ── Paths ────────────────────────────────────────────────────────────────────
MOONRAKER_HTTP = "http://192.168.1.113:7125"
MOONRAKER_WS   = "ws://192.168.1.113:7125/websocket"
DATA_DIR       = pathlib.Path.home() / ".local/share/djinn/print-track"
DJINN_DIR      = pathlib.Path.home() / ".local/share/djinn"
BIN_DIR        = pathlib.Path.home() / ".local/bin"
RECORDS_DIR    = pathlib.Path.home() / "Obsidian/djinn/printer/prints"

POLL_S         = 15       # HTTP fallback interval
WS_RETRY_S     = 10       # WebSocket reconnect interval
BACKUP_KEEP    = 3        # rotating backup generations

DATA_DIR.mkdir(parents=True, exist_ok=True)
DJINN_DIR.mkdir(parents=True, exist_ok=True)
RECORDS_DIR.mkdir(parents=True, exist_ok=True)

# ── Density lookup ────────────────────────────────────────────────────────────
MATERIAL_DENSITY = {
    "pla":   1.24, "pla+": 1.24, "plax": 1.24,
    "petg":  1.27,
    "abs":   1.04,
    "asa":   1.07,
    "tpu":   1.21, "tpu95": 1.21,
    "nylon": 1.08, "pa": 1.08, "pa12": 1.08,
    "pc":    1.20,
    "pp":    0.90,
}

FILAMENT_DIAMETER_MM = 1.75
FILAMENT_RADIUS_CM   = (FILAMENT_DIAMETER_MM / 2) / 10  # 0.0875 cm

# ── File paths ────────────────────────────────────────────────────────────────
PRINTS_PATH          = DATA_DIR / "prints.json"
QUEUE_PATH           = DATA_DIR / "print-queue.json"
CURRENT_PATH         = DATA_DIR / "current.json"
INVENTORY_PATH       = DJINN_DIR / "filament-inventory.json"

# ── Safe I/O — atomic writes, rotating backups, auto-heal ────────────────────

def _bak_path(path: pathlib.Path, gen: int) -> pathlib.Path:
    return path.with_name(f"{path.name}.bak.{gen}")

def _rotate_backup(path: pathlib.Path, keep: int = BACKUP_KEEP):
    """Rotate backups: .bak.3 → drop, .bak.2 → .bak.3, .bak.1 → .bak.2, live → .bak.1"""
    if not path.exists():
        return
    for g in range(keep, 1, -1):
        src = _bak_path(path, g - 1)
        dst = _bak_path(path, g)
        if src.exists():
            shutil.move(str(src), str(dst))
    shutil.copy2(str(path), str(_bak_path(path, 1)))

def atomic_write(path: pathlib.Path, data) -> None:
    """Write data to path atomically: rotate → .tmp → fsync → os.replace"""
    _rotate_backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    raw = json.dumps(data, indent=2, default=str).encode("utf-8")
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        os.write(fd, raw)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(str(tmp), str(path))

def safe_read_json(path: pathlib.Path, default=None) -> dict:
    """Read JSON with auto-heal from .bak.N chain. Returns default on total loss."""
    candidates = [path] + [_bak_path(path, i) for i in range(1, BACKUP_KEEP + 1)]
    for i, p in enumerate(candidates):
        if p.exists():
            try:
                data = json.loads(p.read_text())
                if i > 0:
                    log(f"  Auto-heal: restored {path.name} from .bak.{i}")
                    atomic_write(path, data)
                return data
            except (json.JSONDecodeError, OSError) as e:
                log(f"  Corrupt: {p.name} ({e})")
    return default if default is not None else {}

# ── Logging ───────────────────────────────────────────────────────────────────

def log(*a, **kw):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}]", *a, **kw, flush=True)

# ── Filament math ─────────────────────────────────────────────────────────────

def mm_to_grams(mm: float, material: str = "pla") -> float:
    density = MATERIAL_DENSITY.get(material.lower().strip(), 1.24)
    radius_mm = FILAMENT_DIAMETER_MM / 2  # 0.875 mm
    area_mm2 = 3.14159 * (radius_mm ** 2)
    vol_mm3 = area_mm2 * mm
    vol_cm3 = vol_mm3 / 1000
    return round(vol_cm3 * density, 2)

def density_for(material: str) -> float:
    return MATERIAL_DENSITY.get(material.lower().strip(), 1.24)

# ── Filename encoding parser ──────────────────────────────────────────────────
# Format: ORD-0042__Model_Name__Material_color.gcode
# Parts split on __ (double underscore). Material/color split on _.

def parse_filename(fname: str) -> dict:
    stem = pathlib.Path(fname).stem
    parts = stem.split("__")
    meta = {
        "order_id": parts[0] if len(parts) >= 1 else "",
        "model_name": parts[1] if len(parts) >= 2 else stem,
        "material": "",
        "color": "",
    }
    if len(parts) >= 3:
        mat_color = parts[2]
        if "_" in mat_color:
            meta["material"], meta["color"] = mat_color.rsplit("_", 1)
        else:
            meta["material"] = mat_color
    return meta

def material_from_filename(fname: str) -> str:
    return parse_filename(fname).get("material", "pla") or "pla"

# ── Inventory ─────────────────────────────────────────────────────────────────

def load_inventory() -> dict:
    return safe_read_json(INVENTORY_PATH, {"spools": []})

def save_inventory(inv: dict) -> None:
    atomic_write(INVENTORY_PATH, inv)

def get_active_spool(inv: dict) -> dict | None:
    return next((s for s in inv["spools"] if s.get("loaded")), None)

def deduct_spool(grams_used: float, material: str = "pla") -> dict | None:
    inv = load_inventory()
    spool = get_active_spool(inv)
    if not spool:
        log("  No active spool — skipping filament deduction")
        return None
    spool["remaining_g"] = round(spool["remaining_g"] - grams_used, 2)
    spool["last_used"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_inventory(inv)
    if spool["remaining_g"] < spool.get("low_threshold_g", 100):
        log(f"  ⚠ LOW FILAMENT: {spool['color']} {spool['material']} — {spool['remaining_g']}g remaining")
    return spool

def init_inventory_if_missing():
    if not INVENTORY_PATH.exists():
        inv = {"spools": []}
        save_inventory(inv)
        log(f"  Created: {INVENTORY_PATH}")
    else:
        load_inventory()

# ── Queue ─────────────────────────────────────────────────────────────────────

def load_queue() -> dict:
    return safe_read_json(QUEUE_PATH, {"next_id": 1, "jobs": []})

def save_queue(queue: dict) -> None:
    atomic_write(QUEUE_PATH, queue)

def queue_add_entry(fname: str, start_ts: str) -> int:
    queue = load_queue()
    jid = queue["next_id"]
    queue["next_id"] = jid + 1
    meta = parse_filename(fname)
    entry = {
        "id": jid,
        "filename": fname,
        "model_name": meta["model_name"] or fname,
        "material": meta["material"] or "PLA",
        "color": meta["color"] or "",
        "order_id": meta["order_id"] or "",
        "status": "printing",
        "started_at": start_ts,
        "completed_at": None,
        "duration_s": None,
        "filament_mm": None,
        "filament_g": None,
        "outcome": None,
    }
    queue["jobs"].append(entry)
    save_queue(queue)
    return jid

def queue_finalize(fname: str, end_ts: str, duration_s: float, filament_mm: float, outcome: str):
    queue = load_queue()
    for job in queue["jobs"]:
        if job["filename"] == fname and job["status"] == "printing":
            job["status"] = outcome
            job["completed_at"] = end_ts
            job["duration_s"] = round(duration_s, 1)
            job["filament_mm"] = round(filament_mm, 1)
            job["filament_g"] = round(mm_to_grams(filament_mm, job.get("material", "pla")), 2)
            job["outcome"] = outcome
            save_queue(queue)
            return job
    return None

# ── Prints log ────────────────────────────────────────────────────────────────

def load_prints() -> dict:
    return safe_read_json(PRINTS_PATH, {"prints": []})

def save_prints(pl: dict) -> None:
    atomic_write(PRINTS_PATH, pl)

def prints_append(entry: dict) -> None:
    pl = load_prints()
    pl["prints"].append(entry)
    save_prints(pl)

# ── Current state ─────────────────────────────────────────────────────────────

def write_current(state: dict) -> None:
    atomic_write(CURRENT_PATH, state)

def clear_current() -> None:
    if CURRENT_PATH.exists():
        CURRENT_PATH.unlink()

def read_current() -> dict:
    return safe_read_json(CURRENT_PATH, {})

# ── Structured print records ──────────────────────────────────────────────────

def generate_print_dir(job: dict, point: dict) -> pathlib.Path | None:
    fname = job.get("filename", "unknown.gcode")
    meta = parse_filename(fname)
    model_slug = meta["model_name"] or pathlib.Path(fname).stem
    completed_at = job.get("completed_at") or point.get("ts", "")
    date_str = completed_at[:10] if completed_at else datetime.date.today().isoformat()
    dir_path = RECORDS_DIR / f"{date_str}_{model_slug}"
    dir_path.mkdir(parents=True, exist_ok=True)

    outcome = job.get("outcome", "unknown")
    dur_s = job.get("duration_s", 0) or 0
    fil_g = job.get("filament_g", 0) or 0

    plan = f"""# Print Plan
- **Model:** {meta['model_name'] or 'Unknown'}
- **Order ID:** {meta['order_id'] or 'N/A'}
- **Material:** {meta['material'] or 'PLA'}
- **Color:** {meta['color'] or 'N/A'}
- **Started:** {job.get('started_at', '')}
- **Completed:** {job.get('completed_at', '')}
"""

    analysis = {
        "filename": fname,
        "model_name": meta["model_name"],
        "order_id": meta["order_id"],
        "material": meta["material"],
        "color": meta["color"],
        "started_at": job.get("started_at"),
        "completed_at": job.get("completed_at"),
        "duration_s": dur_s,
        "duration_min": round(dur_s / 60, 1),
        "filament_mm": job.get("filament_mm"),
        "filament_grams": fil_g,
        "outcome": outcome,
        "max_progress_pct": point.get("progress", job.get("max_progress_pct")),
        "max_z_mm": point.get("z_mm", job.get("max_z_mm")),
    }

    postmortem = f"""# Postmortem — {meta['model_name'] or 'Unknown'}
**Outcome:** {outcome}
**Duration:** {round(dur_s / 60, 1)} min
**Filament Used:** {fil_g}g

## Issues
- [ ] None

## Notes
"""

    (dir_path / "plan.md").write_text(plan)
    atomic_write(dir_path / "model_analysis.json", analysis)
    (dir_path / "postmortem.md").write_text(postmortem)
    log(f"  Generated: {dir_path}/")
    return dir_path

# ── Moonraker HTTP helpers ────────────────────────────────────────────────────

def http_fetch(endpoint: str, timeout: int = 5) -> dict:
    import urllib.request, urllib.error
    try:
        with urllib.request.urlopen(f"{MOONRAKER_HTTP}/{endpoint}", timeout=timeout) as r:
            return json.loads(r.read().decode()).get("result", {})
    except Exception as e:
        return {"_error": str(e)}

def http_poll() -> dict:
    objs = "print_stats&display_status&tool0&heater_bed&gcode_move&virtual_sdcard"
    data = http_fetch(f"printer/objects/query?{objs}")
    if "_error" in data:
        return data
    s = data.get("status", {})
    ps = s.get("print_stats", {})
    ds = s.get("display_status", {})
    t0 = s.get("tool0", {})
    hb = s.get("heater_bed", {})
    gm = s.get("gcode_move", {})
    vs = s.get("virtual_sdcard", {})
    gpos = gm.get("gcode_position", [None, None, 0])
    z_pos = gpos[2] if len(gpos) > 2 else gm.get("position", [0, 0, 0])[2]
    return {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "state": ps.get("state", "?"),
        "file": ps.get("filename", "") or "",
        "progress": round(ds.get("progress", 0.0) * 100, 1),
        "duration_s": round(ps.get("print_duration", 0.0), 1),
        "z_mm": round(float(z_pos), 2) if z_pos else 0.0,
        "t_nozzle": t0.get("temperature"),
        "t_bed": hb.get("temperature"),
        "t_bed_target": hb.get("target"),
        "filament_mm": round(ps.get("filament_used", 0.0), 1),
        "message": ps.get("message", ""),
        "vs_is_active": vs.get("is_active", False),
        "vs_file_path": vs.get("file_path", ""),
    }

# ── Daemon — WebSocket loop ───────────────────────────────────────────────────

def daemon_loop():
    log(f"djinn-print-track v2 starting")
    log(f"  Data:     {DATA_DIR}")
    log(f"  Records:  {RECORDS_DIR}")
    log(f"  Moonraker:{MOONRAKER_HTTP}")

    init_inventory_if_missing()

    # Recover state from current.json (survive daemon restart mid-print)
    active = None
    recovered = read_current()
    if recovered and recovered.get("state") in ("printing",):
        active = {
            "file": recovered.get("file", ""),
            "start_ts": recovered.get("ts", ""),
            "started": False,
        }
        log(f"  Recovered active print: {active['file']}")

    prev = None
    use_ws = True

    while True:
        if use_ws:
            try:
                _ws_loop(active, prev)
            except Exception as e:
                log(f"WebSocket error: {e}")
                log("  Falling back to HTTP polling")
                use_ws = False
        else:
            _http_loop()

def _ws_loop(active, prev):
    import asyncio
    # websockets 16.x uses asyncio.run with connect()
    import websockets

    async def run():
        nonlocal active, prev
        log("Connecting to Moonraker WebSocket...")
        async for ws in websockets.connect(MOONRAKER_WS, max_size=None, close_timeout=5):
            try:
                # Subscribe to print_stats, virtual_sdcard, heater_bed
                sub = {
                    "jsonrpc": "2.0",
                    "method": "printer.objects.subscribe",
                    "params": {
                        "objects": {
                            "print_stats": None,
                            "virtual_sdcard": None,
                            "heater_bed": None,
                        }
                    },
                    "id": 1,
                }
                await ws.send(json.dumps(sub))
                log("WebSocket connected.")
                log("Subscribed to: print_stats, virtual_sdcard, heater_bed")

                # Catch up: query current state in case we missed events during reconnect
                catchup = http_fetch("printer/objects/query?print_stats&virtual_sdcard")
                if "_error" not in catchup:
                    status = catchup.get("status", {})
                    ps = status.get("print_stats", {})
                    if ps.get("state") == "printing":
                        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
                        active = _handle_start(ps, now_ts, active)

                async for raw in ws:
                    msg = json.loads(raw)
                    _handle_ws_message(msg, active, prev)

            except websockets.ConnectionClosed:
                log("WebSocket disconnected — reconnecting in 10s")
                await asyncio.sleep(WS_RETRY_S)
            except Exception as e:
                log(f"WebSocket error: {e}")
                traceback.print_exc()
                await asyncio.sleep(WS_RETRY_S)

    asyncio.run(run())

_ws_state = {}  # Persistent merged state across delta updates

def _handle_ws_message(msg: dict, active, prev):
    global _ws_state
    raw_params = msg.get("params", {})
    # Moonraker delivers params as [status_dict, eventtime] for notify_status_update
    status = raw_params[0] if isinstance(raw_params, list) and len(raw_params) > 0 else (
        raw_params.get("status", {}) if isinstance(raw_params, dict) else {})

    # Process subscription response (result.status) and status updates
    # A notify_status_update status might be {"print_stats": {"state": "printing"}} (delta)
    # A subscription result status is {"print_stats": {...}} (full)
    if "result" in msg and isinstance(msg["result"], dict):
        status = msg["result"].get("status", {})

    # Merge deltas into persistent state
    if not isinstance(status, dict):
        return
    for key, fields in status.items():
        if isinstance(fields, dict):
            if key not in _ws_state:
                _ws_state[key] = {}
            _ws_state[key].update(fields)

    ps = _ws_state.get("print_stats", {})
    vs = _ws_state.get("virtual_sdcard", {})
    hb = _ws_state.get("heater_bed", {})

    now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    state = ps.get("state", "")
    fname = ps.get("filename", "")
    vs_active = vs.get("is_active", False)
    fil_mm = ps.get("filament_used", 0.0) or 0.0
    dur_s = ps.get("print_duration", 0.0) or 0.0
    progress = ps.get("progress", 0.0) or 0.0

    point = {
        "ts": now_ts,
        "state": state,
        "file": fname,
        "progress": round(progress * 100, 1),
        "duration_s": round(dur_s, 1),
        "z_mm": 0.0,
        "t_nozzle": None,
        "t_bed": hb.get("temperature"),
        "t_bed_target": hb.get("target"),
        "filament_mm": round(fil_mm, 1),
        "message": ps.get("message", ""),
        "vs_is_active": vs_active,
    }

    write_current(point)

    # Detect print start
    if state == "printing" and fname:
        active = _handle_start(ps, now_ts, active)

    # Detect print end
    if state in ("complete", "error", "cancelled") and active and active["file"] == fname:
        _handle_end(active, point, ps)
        active = None
        _ws_state = {}
        clear_current()

def _handle_start(ps, now_ts, active):
    fname = ps.get("filename", "")
    if active and active.get("file") == fname and active.get("started"):
        return active

    fil_mm = ps.get("filament_used", 0.0) or 0.0
    dur_s = ps.get("print_duration", 0.0) or 0.0

    active = {
        "file": fname,
        "start_ts": now_ts,
        "started": True,
    }

    jid = queue_add_entry(fname, now_ts)
    log(f"\n{'='*50}")
    log(f"PRINT STARTED: {fname}  (queue job {jid})")
    log(f"{'='*50}")

    meta = parse_filename(fname)
    log(f"  Order:   {meta['order_id'] or 'N/A'}")
    log(f"  Model:   {meta['model_name'] or 'N/A'}")
    log(f"  Material:{meta['material'] or 'PLA'}")
    log(f"  Color:   {meta['color'] or 'N/A'}")

    return active

def _handle_end(active, point, ps):
    fname = active["file"]
    fil_mm = round(ps.get("filament_used", 0.0) or 0.0, 1)
    dur_s = ps.get("print_duration", 0.0) or 0.0
    duration_s = round(dur_s, 1)
    state = point["state"]
    message = ps.get("message", "")

    outcome_map = {
        "complete": "complete",
        "error": "error",
        "cancelled": "cancelled",
        "standby": "complete",
    }
    outcome = outcome_map.get(state, state)

    log(f"\n{'='*50}")
    log(f"PRINT ENDED: {outcome}")
    log(f"  File:      {fname}")
    log(f"  Duration:  {duration_s/60:.1f} min")
    log(f"  Filament:  {fil_mm:.0f} mm")

    # Finalize queue entry
    end_ts = point["ts"]
    material = material_from_filename(fname)
    queue_finalize(fname, end_ts, duration_s, fil_mm, outcome)

    # Deduct filament
    grams = mm_to_grams(fil_mm, material)
    log(f"  Filament:  {grams:.0f}g ({material})")
    spool = deduct_spool(grams, material)
    if spool:
        log(f"  Spool:     {spool['remaining_g']}g remaining")

    # Build print record
    meta = parse_filename(fname)
    entry = {
        "file": fname,
        "order_id": meta["order_id"] or "",
        "model_name": meta["model_name"] or fname,
        "material": meta["material"] or "PLA",
        "color": meta["color"] or "",
        "start": active["start_ts"],
        "end": end_ts,
        "outcome": outcome,
        "duration_min": round(duration_s / 60, 1),
        "duration_s": duration_s,
        "filament_mm": fil_mm,
        "filament_g": grams,
        "max_progress_pct": point.get("progress", 0),
        "max_z_mm": point.get("z_mm", 0),
        "message": message,
        "detection": "websocket",
    }
    prints_append(entry)

    # Generate structured print directory
    job = {
        "filename": fname,
        "started_at": active["start_ts"],
        "completed_at": end_ts,
        "duration_s": duration_s,
        "filament_mm": fil_mm,
        "filament_g": grams,
        "outcome": outcome,
    }
    generate_print_dir(job, point)

    log(f"{'='*50}\n")
    if message:
        log(f"  Message:   {message}")

def _http_loop():
    log("HTTP polling fallback active (interval: 15s)")
    active = None
    prev = None

    while True:
        point = http_poll()
        if "_error" in point:
            log(f"HTTP error: {point['_error']} — retry in {POLL_S * 2}s")
            time.sleep(POLL_S * 2)
            continue

        state = point["state"]
        fname = point["file"]
        write_current(point)

        if state == "printing" and fname:
            if active is None:
                now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
                jid = queue_add_entry(fname, now_ts)
                log(f"PRINT STARTED (HTTP fallback): {fname}  (queue job {jid})")
                active = {"file": fname, "start_ts": now_ts}

        if state in ("complete", "error", "cancelled") and active is not None:
            outcome = "complete" if state in ("complete", "standby") else state
            dur_s = point["duration_s"]
            fil_mm = point["filament_mm"]
            end_ts = point["ts"]
            material = material_from_filename(fname or active["file"])
            queue_finalize(fname or active["file"], end_ts, dur_s, fil_mm, outcome)
            grams = mm_to_grams(fil_mm, material)
            deduct_spool(grams, material)
            meta = parse_filename(fname or active["file"])
            entry = {
                "file": fname or active["file"],
                "start": active["start_ts"],
                "end": end_ts,
                "outcome": outcome,
                "duration_min": round(dur_s / 60, 1),
                "duration_s": dur_s,
                "filament_mm": fil_mm,
                "filament_g": grams,
                "detection": "http_fallback",
            }
            prints_append(entry)
            job = {
                "filename": fname or active["file"],
                "started_at": active["start_ts"],
                "completed_at": end_ts,
                "duration_s": dur_s,
                "filament_mm": fil_mm,
                "filament_g": grams,
                "outcome": outcome,
            }
            generate_print_dir(job, point)
            log(f"PRINT ENDED (HTTP fallback): {outcome} — {fname or active['file']}")
            active = None

        prev = point
        time.sleep(POLL_S)

# ── CLI Commands ──────────────────────────────────────────────────────────────

def cmd_status():
    cur = read_current()
    inv = load_inventory()
    spool = get_active_spool(inv)

    # Current print state
    if cur:
        log(f"State: {cur.get('state', '?')}")
        if cur.get("file"):
            log(f"  File:     {cur['file']}")
            log(f"  Progress: {cur.get('progress', 0)}%")
            log(f"  Z:        {cur.get('z_mm', 0)}mm")
            log(f"  Duration: {cur.get('duration_s', 0)/60:.1f} min")
            log(f"  Filament: {cur.get('filament_mm', 0):.0f} mm")
    else:
        log("State: unknown (no current data)")

    # Spool bar
    if spool:
        pct = max(0, min(100, (spool["remaining_g"] / spool.get("initial_weight_g", 1000)) * 100))
        bar_len = 20
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        log(f"\nSpool: {spool['material']} {spool['color']}")
        log(f"  [{bar}] {spool['remaining_g']}g / {spool.get('initial_weight_g', 0)}g ({pct:.0f}%)")
        if spool["remaining_g"] < spool.get("low_threshold_g", 100):
            log(f"  ⚠ LOW FILAMENT")
    else:
        log("\nSpool: none loaded")

def cmd_summary():
    pl = load_prints()
    prints = pl.get("prints", [])
    if not prints:
        log("No prints tracked yet.")
        return

    total = len(prints)
    success = sum(1 for p in prints if p.get("outcome") == "complete")
    failed = sum(1 for p in prints if p.get("outcome") == "error")
    cancelled = sum(1 for p in prints if p.get("outcome") == "cancelled")
    rate = (success / total * 100) if total else 0
    total_filament = sum(p.get("filament_g", 0) or 0 for p in prints)
    total_dur = sum(p.get("duration_min", 0) or 0 for p in prints)

    log(f"Prints: {total} total  |  {success} success  |  {failed} failed  |  {cancelled} cancelled")
    log(f"Success rate: {rate:.0f}%")
    log(f"Total filament: {total_filament:.0f}g")
    log(f"Total print time: {total_dur:.0f} min ({total_dur/60:.1f}h)")

    log(f"\n{'START':<20} {'OUTCOME':<12} {'DUR':>6} {'FIL':>5}  FILE")
    log("-" * 80)
    for p in prints[-10:]:
        start = p.get("start", "?")[:19]
        out = p.get("outcome", "?")
        dur = f"{p.get('duration_min', 0):.0f}m"
        fil = f"{p.get('filament_g', 0):.0f}g"
        fn = p.get("file", "?")[:48]
        log(f"{start:<20} {out:<12} {dur:>6} {fil:>5}  {fn}")

def cmd_spool(material: str, color: str, weight: int):
    inv = load_inventory()
    # Unload existing active spools
    for s in inv["spools"]:
        s["loaded"] = False
    spool = {
        "spool_id": f"SPOOL-{len(inv['spools']) + 1:03d}",
        "material": material,
        "color": color,
        "brand": "",
        "initial_weight_g": weight,
        "remaining_g": weight,
        "loaded": True,
        "low_threshold_g": 100,
        "added_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "last_used": None,
    }
    inv["spools"].append(spool)
    save_inventory(inv)
    log(f"Loaded: {material} {color} ({weight}g) — spool {spool['spool_id']}")

def cmd_backfill(filename: str, grams: float, duration: float, filament_mm: float, model: str, order: str):
    now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    start_ts = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=duration)).isoformat()

    # Queue entry
    jid = queue_add_entry(filename, start_ts)
    queue_finalize(filename, now_ts, duration, filament_mm, "complete")
    log(f"Queue: job {jid} — {filename} (completed)")

    # Deduct filament
    material = material_from_filename(filename)
    grams_actual = mm_to_grams(filament_mm, material) if not grams else grams
    spool = deduct_spool(grams_actual, material)
    if spool:
        log(f"Filament: deducted {grams_actual}g from {spool['material']} {spool['color']}")

    # Print record
    meta = parse_filename(filename)
    entry = {
        "file": filename,
        "order_id": meta["order_id"] or order or "",
        "model_name": meta["model_name"] or model or filename,
        "material": meta["material"] or material,
        "color": meta["color"] or "",
        "start": start_ts,
        "end": now_ts,
        "outcome": "complete",
        "duration_min": round(duration / 60, 1),
        "duration_s": round(duration, 1),
        "filament_mm": round(filament_mm, 1),
        "filament_g": round(grams_actual, 2),
        "detection": "backfill",
    }
    prints_append(entry)

    # Print directory
    job = {
        "filename": filename,
        "started_at": start_ts,
        "completed_at": now_ts,
        "duration_s": duration,
        "filament_mm": filament_mm,
        "filament_g": grams_actual,
        "outcome": "complete",
    }
    point = {"ts": now_ts, "progress": 100, "z_mm": 0}
    generate_print_dir(job | {"max_progress_pct": 100, "max_z_mm": 0}, point)
    log("Backfill complete")

def cmd_verify():
    log("🔍  Data integrity check")
    for label, path in [
        ("prints.json", PRINTS_PATH),
        ("print-queue.json", QUEUE_PATH),
        ("current.json", CURRENT_PATH),
    ]:
        if path.exists():
            try:
                data = json.loads(path.read_text())
                sz = path.stat().st_size
                log(f"  ✅  {label:<28} {sz:>6} B  ({_count_records(data)} records)")
            except (json.JSONDecodeError, OSError) as e:
                log(f"  ❌  {label:<28} CORRUPT — {e}")
                # Check backups
                for i in range(1, BACKUP_KEEP + 1):
                    bp = _bak_path(path, i)
                    if bp.exists():
                        try:
                            json.loads(bp.read_text())
                            log(f"      .bak.{i} — OK ({bp.stat().st_size} B)")
                        except Exception:
                            log(f"      .bak.{i} — CORRUPT")
        else:
            log(f"  —   {label:<28} not found (OK — no prints yet)")

    # Inventory
    if INVENTORY_PATH.exists():
        try:
            inv = json.loads(INVENTORY_PATH.read_text())
            sz = INVENTORY_PATH.stat().st_size
            spools = len(inv.get("spools", []))
            log(f"  ✅  filament-inventory.json{'':>11} {sz:>6} B  ({spools} spools)")
        except Exception as e:
            log(f"  ❌  filament-inventory.json{'':>11} CORRUPT — {e}")
    else:
        log(f"  —   filament-inventory.json{'':>11} not found (OK)")

    # Backup integrity
    for path in [PRINTS_PATH, QUEUE_PATH, CURRENT_PATH]:
        if not path.exists():
            continue
        for i in range(1, BACKUP_KEEP + 1):
            bp = _bak_path(path, i)
            if bp.exists():
                try:
                    json.loads(bp.read_text())
                except Exception:
                    log(f"  ⚠  {path.name}.bak.{i} — corrupt (will be rotated out)")

    log("\n  All files intact.")

def _count_records(data) -> int:
    if isinstance(data, dict):
        for key in ("prints", "jobs", "spools"):
            if key in data and isinstance(data[key], list):
                return len(data[key])
    return 0

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            cmd_status()
            return
        elif cmd == "summary":
            cmd_summary()
            return
        elif cmd == "spool":
            import argparse
            p = argparse.ArgumentParser(exit_on_error=False)
            p.add_argument("--material", required=True)
            p.add_argument("--color", required=True)
            p.add_argument("--weight", type=int, required=True)
            args = p.parse_args(sys.argv[2:])
            cmd_spool(args.material, args.color, args.weight)
            return
        elif cmd == "backfill":
            import argparse
            p = argparse.ArgumentParser(exit_on_error=False)
            p.add_argument("--filename", required=True)
            p.add_argument("--grams", type=float, default=0)
            p.add_argument("--duration", type=float, required=True)
            p.add_argument("--filament-mm", type=float, required=True)
            p.add_argument("--model", default="")
            p.add_argument("--order", default="")
            args = p.parse_args(sys.argv[2:])
            cmd_backfill(args.filename, args.grams, args.duration, args.filament_mm, args.model, args.order)
            return
        elif cmd == "verify":
            cmd_verify()
            return
        elif cmd == "start":
            daemon_loop()
            return
        elif cmd in ("stop", "foreground", "daemonize"):
            log(f"Command '{cmd}' no longer supported. Run 'djinn-print-track start' for foreground.")
            return
        else:
            log(f"Usage: {sys.argv[0]} [status|summary|spool|backfill|verify|start]")
            sys.exit(1)

    # Default: run daemon in foreground
    daemon_loop()

if __name__ == "__main__":
    main()
