================================================================================
                      FORGE SLICER MANUAL
           OrcaSlicer CLI Interface — slice.sh + djinn-model-slice
================================================================================
Version: 1.0 | Last updated: 2026-06-15 | Maintained by: Owner / Marcus

> OrcaSlicer v2.3.2 replaced CrealityPrint on 2026-06-14 after a confirmed
> null-pointer segfault in PartPlate::set_shape affected all v6+ Linux
> builds. slice.sh is the new CLI slicing interface. djinn-model-slice
> remains the high-level caller — it reads job settings from the queue and
> invokes slice.sh.

================================================================================
TABLE OF CONTENTS
================================================================================

  1.  Installation Paths
  2.  slice.sh — Usage
  3.  slice.sh — Return Format
  4.  Process Profiles
  5.  Output File Behavior
  6.  Known Limitations
  7.  djinn-model-slice (High-Level Caller)
  8.  Deprecated Infrastructure

================================================================================
1. INSTALLATION PATHS
================================================================================

  Orca binary:     /opt/orca-slicer/AppRun
                   (AppImage extracted to /opt/orca-slicer/)

  Symlink:         /usr/local/bin/orca-slicer

  slice.sh:        ~/Obsidian/djinn/printer/forge-slicer/slice.sh

  Process profiles dir:
    ~/Obsidian/djinn/printer/forge-slicer/profiles/process/
      Calliope-Proto.json
      Calliope-Production.json
      Calliope-Quality.json

  Machine profile: Built-in Orca "Creality Ender-3 V3 Plus 0.4 nozzle"
                   (not a custom file — uses Orca's bundled profile)

  Gcode output dir:
    ~/Videos/print-monitor/
    (Orca writes plate_1.gcode here — see Section 5 for rename behavior)

================================================================================
2. SLICE.SH — USAGE
================================================================================

Location:
  ~/Obsidian/djinn/printer/forge-slicer/slice.sh

Signature:
  slice.sh <abs_stl_path> <profile> <material> [supports]

Arguments:
  abs_stl_path    Absolute path to the STL file. Relative paths are not
                  accepted — callers must resolve before passing.

  profile         proto | production | quality
                  Maps to the corresponding Calliope-*.json process profile.

  material        pla | petg | abs
                  Passed to Orca's filament selection logic.

  supports        (optional) auto | tree
                  If omitted, no supports are generated.

Examples:
  slice.sh /home/javier/models/bracket.stl production pla
  slice.sh /home/javier/models/bracket.stl proto petg tree
  slice.sh /home/javier/models/enclosure.stl quality abs auto

================================================================================
3. SLICE.SH — RETURN FORMAT
================================================================================

slice.sh prints a single JSON object to stdout on exit:

Success:
  {"success": true, "gcode_path": "/abs/path/to/bracket.gcode", "error": null}

Failure:
  {"success": false, "gcode_path": null, "error": "<error message>"}

Callers must parse this JSON. djinn-model-slice handles this automatically.
If calling slice.sh directly, capture stdout and parse before proceeding.

stderr is reserved for Orca's own log output — do not parse it.

================================================================================
4. PROCESS PROFILES
================================================================================

  Profile name   File                        Intended use
  ──────────────────────────────────────────────────────────────────────────
  proto          Calliope-Proto.json         Fast draft — coarse settings,
                                             minimum wall count. Not for
                                             customer-facing parts.

  production     Calliope-Production.json    Standard production settings.
                                             Default for all shop jobs.

  quality        Calliope-Quality.json       Fine detail — slow, higher
                                             infill, more perimeters.
                                             Use for display pieces or
                                             tight-tolerance parts.

All three profiles target the Creality Ender-3 V3 Plus with a 0.4mm nozzle.
Do not pass these profiles to a different machine configuration.

================================================================================
5. OUTPUT FILE BEHAVIOR
================================================================================

Orca always writes its output as:
  ~/Videos/print-monitor/plate_1.gcode

This is a fixed Orca behavior — the filename does not reflect the input STL.

slice.sh renames the output after slicing to include the STL stem:
  ~/Videos/print-monitor/<stl_stem>.gcode

Example:
  Input:   /home/javier/models/bracket.stl
  Orca:    ~/Videos/print-monitor/plate_1.gcode
  After:   ~/Videos/print-monitor/bracket.gcode

The renamed path is what slice.sh returns in gcode_path.

If a file named <stl_stem>.gcode already exists, slice.sh overwrites it.
No versioning is done at this layer — job-level versioning is handled by
djinn-model-slice and the print queue.

================================================================================
6. KNOWN LIMITATIONS
================================================================================

Orca result.json — partial data:
  Orca writes a result.json alongside the gcode containing metadata about
  the slice. The triangle_count field is populated. print_time_s and
  filament_g are null in the current Orca v2.3.2 build.

  Time and filament estimates must be parsed from Orca's log comments in
  the gcode file itself (look for ; estimated printing time and
  ; filament used lines in the gcode header).

  slice.sh does not currently parse these values. If you need them
  programmatically, grep the gcode output directly.

Supports:
  "auto" and "tree" are the only accepted support values. Any other string
  will be ignored and no supports will be generated (same as omitting the
  argument). This is not validated — slice.sh will silently proceed without
  supports if an unrecognized value is passed.

================================================================================
7. DJINN-MODEL-SLICE (HIGH-LEVEL CALLER)
================================================================================

djinn-model-slice is the operator-facing command. It reads job settings
from the print queue and calls slice.sh with the resolved arguments.

Usage (called by djinn-job-add or manually):
  djinn-model-slice <job_id>
  djinn-model-slice <job_id> profile=proto material=petg supports=tree

When called with explicit arguments, those values override whatever is
stored in the queue for that job.

On success:
  - gcode path is written back to the queue entry
  - job status advances to: sliced

On failure (slice.sh returns success: false):
  - error is logged
  - job status set to: slice_failed
  - gcode_path remains null

Retry a failed slice:
  djinn-model-slice <job_id>

================================================================================
8. DEPRECATED INFRASTRUCTURE
================================================================================

The following files are still present in the forge-slicer directory but
are no longer current. Do not use them:

  Dockerfile          — Docker-based CrealityPrint slicing pipeline
  entrypoint.py       — Container entrypoint for above

CrealityPrint was deprecated after a confirmed null-pointer segfault in
PartPlate::set_shape present in all v6+ Linux builds. There is no plan
to return to it. These files are retained for reference only.

================================================================================
*— Marcus, 2026-06-15*
================================================================================
