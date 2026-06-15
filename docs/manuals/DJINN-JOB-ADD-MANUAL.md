================================================================================
                      DJINN JOB-ADD MANUAL
              Print Job Queue Entry + Auto-Slice
================================================================================
Version: 1.0 | Last updated: 2026-06-15 | Maintained by: Owner / Marcus

> Queues a print job and immediately triggers slicing. The old behavior
> (queue only, manual slice) is still available via --no-slice.

================================================================================
TABLE OF CONTENTS
================================================================================

  1.  Usage
  2.  Flags
  3.  Positional Key=Value Style
  4.  Default Values
  5.  Auto-Slice Behavior
  6.  --no-slice Flag
  7.  Queue File
  8.  Full Pipeline

================================================================================
1. USAGE
================================================================================

Standard form:
  djinn-job-add <model.stl> [flags]

Examples:
  djinn-job-add bracket.stl
  djinn-job-add bracket.stl --profile production --material petg
  djinn-job-add bracket.stl --profile proto --supports tree --qty 2
  djinn-job-add bracket.stl --notes "customer wants 0.2mm tolerance on top face"
  djinn-job-add bracket.stl --no-slice

================================================================================
2. FLAGS
================================================================================

  Flag              Values                   Description
  ───────────────────────────────────────────────────────────────────────────
  --profile         proto | production        Slicer process profile
                    | quality                 Default: production

  --material        pla | petg | abs          Filament material
                                             Default: pla

  --supports        none | auto | tree        Support type
                                             Default: none (if flag omitted)

  --qty             N (integer)               Number of copies
                                             Default: 1

  --notes           "<string>"                Free-text notes attached to job

  --no-slice        (flag, no value)          Queue only — skip auto-slice

  --cono            (flag, no value)          Mark job as cono (internal tag)

================================================================================
3. POSITIONAL KEY=VALUE STYLE
================================================================================

Key=value pairs are accepted after the STL path as an alternative to flags.
Both styles are equivalent:

  djinn-job-add bracket.stl --profile production --material pla
  djinn-job-add bracket.stl profile=production material=pla

Mixing styles in the same call is supported:
  djinn-job-add bracket.stl profile=production --qty 2

================================================================================
4. DEFAULT VALUES
================================================================================

  profile:    production
  material:   pla
  supports:   none
  qty:        1

================================================================================
5. AUTO-SLICE BEHAVIOR
================================================================================

Default behavior (--no-slice not set):

  After the job is written to print-queue.json with status: confirmed,
  djinn-job-add immediately calls:

    djinn-model-slice <job_id> profile=<X> material=<Y> supports=<Z>

  Slice output is inline — you see the slicer progress in the terminal.
  On success, gcode is written to:
    ~/.local/share/forge/gcode/

  The job entry in print-queue.json is updated with the gcode path.
  The job is then ready to be started with djinn-confirm-print.

  If slicing fails, the job remains in the queue with status: slice_failed.
  The gcode path field will be null. You can re-slice by calling:
    djinn-model-slice <job_id>

================================================================================
6. --NO-SLICE FLAG
================================================================================

Use when:
  - You want to inspect or modify queue settings before committing to a slice
  - You are batch-queuing multiple jobs and will slice in a separate pass
  - Slicing is being handled by another process

With --no-slice:
  - Job is written to print-queue.json with status: confirmed
  - djinn-model-slice is NOT called
  - Terminal prints: "Job <ID> queued. Slice manually with:
    djinn-model-slice <job_id>"

================================================================================
7. QUEUE FILE
================================================================================

Location:
  ~/.local/share/djinn/print-queue.json

Each job entry includes:
  - job_id (auto-generated)
  - stl_path
  - profile
  - material
  - supports
  - qty
  - notes
  - status (confirmed | slice_failed | sliced | printing | done)
  - gcode_path (null until sliced)
  - created_at

Inspect the queue:
  cat ~/.local/share/djinn/print-queue.json | python3 -m json.tool

================================================================================
8. FULL PIPELINE
================================================================================

With auto-slice (default):

  djinn-job-add model.stl
    → job written to print-queue.json (status: confirmed)
    → djinn-model-slice called inline
    → gcode written to ~/.local/share/forge/gcode/
    → job updated (status: sliced, gcode_path set)
    → ready for djinn-confirm-print

With --no-slice:

  djinn-job-add model.stl --no-slice
    → job written to print-queue.json (status: confirmed)
    → (manual) djinn-model-slice <job_id>
    → gcode written to ~/.local/share/forge/gcode/
    → job updated (status: sliced, gcode_path set)
    → ready for djinn-confirm-print

================================================================================
*— Marcus, 2026-06-15*
================================================================================
