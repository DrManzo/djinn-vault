================================================================================
                   DJINN WEBCAM MONITOR MANUAL
         Print Failure Detection + Social Reel Pipeline
================================================================================
Version: 1.1 | Last updated: 2026-06-15 | Maintained by: Owner / Marcus

> Continuous monitoring service for the print bed. Detects failures via
> frame diff analysis and captures milestone clips at key progress points.
> On job completion, assembles clips into a social reel automatically.

================================================================================
TABLE OF CONTENTS
================================================================================

  1.  Hardware + Endpoints
  2.  Failure Detection Behavior
  3.  Scheduled Recordings
  4.  Milestone Clip System (new — 2026-06-15)
  5.  Social Reel Assembly
  6.  Notifications
  7.  State File
  8.  Service Management
  9.  Social Workflow (post-completion)

================================================================================
1. HARDWARE + ENDPOINTS
================================================================================

  Camera:     AKASO Brave 4
  Device:     /dev/video2
  Moonraker:  192.168.1.114:7125

If /dev/video2 is not available, the service will log an error and exit.
Confirm the device is present before troubleshooting anything else:
  ls -la /dev/video*

================================================================================
2. FAILURE DETECTION BEHAVIOR
================================================================================

The service monitors the print bed using frame difference analysis.

  - Captures frames at a configured interval from /dev/video2
  - Computes pixel diff between current frame and reference frame
  - If diff exceeds threshold, failure is flagged
  - On confirmed failure:
      1. Parks the printer toolhead at the registered safe position
      2. Posts alert to Telegram and Discord with failure frame
      3. Stops monitoring for the current job

A 0% progress reading does NOT trigger failure. Large files sit at 0%
for an extended time while the first layer builds — this is expected.

================================================================================
3. SCHEDULED RECORDINGS
================================================================================

Every 45 minutes, the service captures a 5-minute clip from /dev/video2.
These are background interval recordings, independent of milestone logic.

  Output dir:  ~/Videos/print-monitor/
  Format:      mp4 via ffmpeg
  Purpose:     General archive / manual review

These clips are not used in the social reel pipeline.

================================================================================
4. MILESTONE CLIP SYSTEM
================================================================================

New behavior added 2026-06-15.

At five progress thresholds (read from Moonraker virtual_sdcard.progress):

  1%    25%    50%    75%    100%

The service captures a short milestone clip. Each clip is saved to:

  ~/Videos/print-monitor/jobs/<timestamp>_<jobname>/milestone_XXXpct.mp4

Example paths:
  ~/Videos/print-monitor/jobs/20260615_083000_calliope-v2/milestone_001pct.mp4
  ~/Videos/print-monitor/jobs/20260615_083000_calliope-v2/milestone_025pct.mp4
  ~/Videos/print-monitor/jobs/20260615_083000_calliope-v2/milestone_050pct.mp4
  ~/Videos/print-monitor/jobs/20260615_083000_calliope-v2/milestone_075pct.mp4
  ~/Videos/print-monitor/jobs/20260615_083000_calliope-v2/milestone_100pct.mp4

Progress is polled from Moonraker. Milestones are one-shot — once a
threshold is crossed, it does not fire again for the same job.

================================================================================
5. SOCIAL REEL ASSEMBLY
================================================================================

On print completion (Moonraker reports job done):

  1. ffmpeg concatenates all milestone clips captured for that job in order.
  2. Output file:
       ~/Videos/print-monitor/jobs/<timestamp>_<jobname>/social_reel.mp4
  3. Metadata file saved alongside the reel:
       ~/Videos/print-monitor/jobs/<timestamp>_<jobname>/job_meta.json

Fields in job_meta.json:
  {
    "filename":       "<original stl/jobname>",
    "start_ts":       "<ISO 8601 timestamp>",
    "milestones_hit": ["001pct", "025pct", "050pct", "075pct", "100pct"],
    "reel_path":      "<abs path to social_reel.mp4>"
  }

  Note: milestones_hit stores strings in XXXpct format, not integers.
  When parsing programmatically, expect string values — not [1, 25, 50 ...].

If fewer than 5 milestones were captured (e.g., job cancelled before
100%), the reel is assembled from whatever clips exist. milestones_hit
reflects only the thresholds that were actually reached.

================================================================================
6. NOTIFICATIONS
================================================================================

On job completion and reel assembly:
  - Telegram message with reel filename
  - Discord message with reel filename
  - Both messages include a prompt to add cleanup shots:
      "Reel ready: social_reel.mp4 — drop cleanup shots/video into
      ~/djinn-media-inbox to build the final post."

On failure detection:
  - Telegram + Discord alert with failure frame
  - Printer parked
  - No reel is assembled for failed jobs

================================================================================
7. STATE FILE
================================================================================

Location:
  ~/.local/share/djinn/webcam-state.json

Tracked fields include:
  - current job name + start timestamp
  - current print progress (float, from Moonraker)
  - milestones_hit (list of strings in XXXpct format, e.g. "001pct")
  - milestone_clip (dict mapping threshold string → clip path)
  - last_frame_diff (for failure detection logic)
  - reel_path (set on completion)

Inspect state:
  cat ~/.local/share/djinn/webcam-state.json | python3 -m json.tool

Reset state (start fresh for a new job if state is stale):
  rm ~/.local/share/djinn/webcam-state.json
  systemctl --user restart djinn-webcam-monitor

================================================================================
8. SERVICE MANAGEMENT
================================================================================

  systemctl --user status djinn-webcam-monitor
  systemctl --user restart djinn-webcam-monitor
  systemctl --user stop djinn-webcam-monitor

View live logs:
  journalctl --user -u djinn-webcam-monitor -f

The service is enabled and set to start at login. It does not need to be
started manually for normal operation.

================================================================================
9. SOCIAL WORKFLOW (POST-COMPLETION)
================================================================================

After the reel notification fires:

  1. Review social_reel.mp4 in the job directory.
  2. Capture any cleanup shots (finished part on bed, detail photos, etc.).
  3. Drop cleanup photos and supplemental video into:
       ~/djinn-media-inbox/
  4. Work the final post with Djinn (caption, hashtags, platform selection).

This workflow is handled by the media pipeline — djinn-webcam-monitor's
responsibility ends at reel assembly and notification.

================================================================================
*— Marcus, 2026-06-15*
================================================================================
