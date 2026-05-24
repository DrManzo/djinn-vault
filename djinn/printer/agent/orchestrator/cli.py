#!/usr/bin/env python3
"""
djinn-design — Djinn Manufacturing Orchestrator CLI

Usage:
  djinn-design "make a snap-fit enclosure for a sensor board, PETG, 80x60x30mm"
  djinn-design --job 3 --edit "move mounting holes 5mm inward"
  djinn-design --job 3 --optimize
  djinn-design --job 3 --doe prototype_fast
  djinn-design --job 3 --doe prototype_cheap
  djinn-design --job 3 --doe balanced
  djinn-design --job 3 --plate
  djinn-design --job 3 --plate --items '[{"stl":"/path/a.stl","qty":2}]'
  djinn-design --status
  djinn-design --job 3 --full        # run full pipeline from current status
"""
import sys, os, argparse, json

# Inject venv site-packages
_VENV_SITE = os.path.expanduser("~/.venvs/djinn-orchestrator/lib/python3.11/site-packages")
if _VENV_SITE not in sys.path:
    sys.path.insert(0, _VENV_SITE)

# Inject agent package root
_AGENT_ROOT = os.path.expanduser("~/Obsidian/djinn/printer")
if _AGENT_ROOT not in sys.path:
    sys.path.insert(0, _AGENT_ROOT)

from agent.orchestrator import orchestrator
from agent.orchestrator.project_state import ProjectState
from agent.orchestrator.llm import LLM
from agent.orchestrator.agents import proto_opt, doe_opt, plate_nest


def main():
    ap = argparse.ArgumentParser(
        prog="djinn-design",
        description="Djinn Manufacturing Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("brief", nargs="?", help="Design brief — text or JSON")
    ap.add_argument("--job",      type=int,         help="Existing job ID")
    ap.add_argument("--edit",     metavar="REQUEST", help="Edit request for existing design")
    ap.add_argument("--optimize", action="store_true", help="Generate prototype/production variants")
    ap.add_argument("--doe",      metavar="GOAL",
                    choices=["prototype_fast", "prototype_cheap", "balanced"],
                    help="DOE slicer optimization")
    ap.add_argument("--plate",    action="store_true", help="Arrange print plate")
    ap.add_argument("--items",    help='JSON list: [{"stl":"path","qty":1}]')
    ap.add_argument("--full",     action="store_true", help="Auto-advance full pipeline")
    ap.add_argument("--status",   action="store_true", help="Show job queue")
    ap.add_argument("--enclosure",action="store_true", help="Printer has enclosure")
    ap.add_argument("--no-sock",  action="store_true", help="No hot-end sock installed")

    args = ap.parse_args()

    printer = {
        "model":         "Ender-3 V3 Plus",
        "has_enclosure": args.enclosure,
        "hotend_sock":   not getattr(args, "no_sock", False),
        "bed_insulated": False,
    }

    plate_items = json.loads(args.items) if args.items else None

    if args.status:
        orchestrator.run("status", printer=printer)
        return

    if args.optimize and args.job:
        state = ProjectState.load(args.job)
        llm = LLM()
        state = proto_opt.run(state, llm)
        state.save()
        orchestrator._report_variants(state)
        _done(state)
        return

    if args.doe and args.job:
        state = ProjectState.load(args.job)
        state = doe_opt.run(state, args.doe, printer)
        state.save()
        orchestrator._report_doe(state)
        _done(state)
        return

    if args.plate and args.job:
        state = ProjectState.load(args.job)
        state = plate_nest.run(state, plate_items)
        state.save()
        print(f"  Plate: {state.plate_stl}")
        _done(state)
        return

    if args.edit and args.job:
        state = orchestrator.run(
            args.edit, job_id=args.job, edit_request=args.edit,
            printer=printer, auto_advance=args.full,
        )
        _done(state)
        return

    if args.brief:
        state = orchestrator.run(
            args.brief, job_id=args.job,
            doe_goal=args.doe or "prototype_fast",
            plate_items=plate_items,
            printer=printer,
            auto_advance=args.full,
        )
        _done(state)
        return

    if args.job and args.full:
        state = ProjectState.load(args.job)
        state = orchestrator.run(
            state.note or "continue", job_id=args.job,
            printer=printer, auto_advance=True,
        )
        _done(state)
        return

    ap.print_help()


def _done(state: ProjectState):
    print(f"\n  Job #{state.id} | {state.status}")


if __name__ == "__main__":
    main()
