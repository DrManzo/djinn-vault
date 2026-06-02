"""
ProjectState — shared state object for the manufacturing pipeline.
Extends the existing print-queue.json schema with design, optimization,
plate phases, and native engraving support.
"""
import json, pathlib, datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

QUEUE_PATH = pathlib.Path.home() / ".local/share/djinn/print-queue.json"


@dataclass
class ProjectState:
    # Identity
    id: int = 0
    status: str = "design_gen"
    # design_gen | design_edit | proto_opt | doe_opt | plate_nest | priced
    # | engrave_pending_approval | engrave_approved | engrave_error
    # | pending | printing
    added: str = ""
    note: str = ""

    # Design phase
    brief: dict = field(default_factory=dict)
    concept: dict = field(default_factory=dict)
    source_scad: str = ""
    source_stl: str = ""

    # Edit phase
    edit_history: list = field(default_factory=list)

    # Optimization phase
    variants: dict = field(default_factory=dict)  # {"prototype": meta, "production": meta, "files": {...}}

    # DOE phase
    doe_profile: dict = field(default_factory=dict)

    # Plate phase
    plate_stl: str = ""

    # Pricing phase
    quote: dict = field(default_factory=dict)

    # ── Engraving phase ──────────────────────────────────────────────────────
    # engraving_request   : human natural-language string (e.g. "add Typhon's Forge near the base")
    # engraving_proposals : full JSON blob from EngravingAgent (3 proposals + geometry notes)
    # engraving_approved  : 1, 2, or 3 — which proposal Javier selected
    # engraving_spec      : the approved proposal dict (subset of engraving_proposals)
    # mesh                : geometry summary computed by EngravingAgent for downstream use
    engraving_request: str = ""
    engraving_proposals: dict = field(default_factory=dict)
    engraving_approved: int = 0
    engraving_spec: dict = field(default_factory=dict)

    # Compatibility with existing queue fields
    url: str = ""
    model_path: str = ""
    gcode_path: str = ""
    infill: int = 20
    brim: bool = False
    supports_needed: bool = False
    mesh: dict = field(default_factory=dict)
    stats: dict = field(default_factory=dict)

    def save(self):
        queue = _load_queue()
        d = asdict(self)
        if not d["added"]:
            d["added"] = datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"

        jobs = queue.get("jobs", [])
        for i, job in enumerate(jobs):
            if job.get("id") == self.id:
                merged = {**job, **d}
                jobs[i] = merged
                queue["jobs"] = jobs
                _save_queue(queue)
                return

        # New job
        self.id = queue.get("next_id", 1)
        d["id"] = self.id
        d["added"] = datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"
        queue["next_id"] = self.id + 1
        queue.setdefault("jobs", []).append(d)
        _save_queue(queue)

    @classmethod
    def load(cls, job_id: int) -> "ProjectState":
        queue = _load_queue()
        for job in queue.get("jobs", []):
            if job.get("id") == job_id:
                valid = {k: v for k, v in job.items() if k in cls.__dataclass_fields__}
                return cls(**valid)
        raise ValueError(f"Job {job_id} not found in queue")

    @classmethod
    def new(cls, brief: dict, note: str = "") -> "ProjectState":
        piece = brief.get("piece_name", brief.get("request", ""))[:60]
        return cls(brief=brief, note=note or piece, status="design_gen")


def _load_queue() -> dict:
    if QUEUE_PATH.exists():
        return json.loads(QUEUE_PATH.read_text())
    return {"next_id": 1, "jobs": []}


def _save_queue(queue: dict):
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_PATH.write_text(json.dumps(queue, indent=2))
