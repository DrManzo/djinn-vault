---
subject: djinn/printer/forge-slicer
tags:
  - cs/programming/docker
  - 3d-printing/slicing/critical-details
created: 2026-06-28
source: Perplexity export
---

# forge-slicer Project Overview

## Summary
This project involves building a Docker container for slicing 3D models using Creality Print, addressing issues with the flatpak CLI crashing during initialization. The solution is to run it inside a Docker container with Xvfb and Mesa.

## Key Points
- **Problem:** Creality Print's flatpak CLI crashes on host during engine initialization.
- **Solution:** Run Creality Print in a Docker container using Xvfb and Mesa.
- **Deliverables:**
  - `Dockerfile`
  - `entrypoint.py` script
  - Profile files for different processes and filaments
  - Shell wrapper script `slice.sh`

## Details
The project aims to create a robust slicing pipeline for the Djinn/Forge 3D printing process. The critical technical details include:
- **AppImage extraction:** Prefer using AppImage extraction over FUSE.
- **Xvfb usage:** Use `xvfb-run` with specific server arguments.
- **Profile format:** Ensure correct JSON format, especially setting `compatible_printers`.
- **entrypoint.py output:** Parse gcode comments for print time and filament usage.

## References
- Full spec: `~/Obsidian/djinn/printer/forge-slicer/SPEC.md`
- Dockerfile content:
  ```dockerfile
  RUN ./CrealityPrint.AppImage --appimage-extract && \
  mv squashfs-root /opt/creality-print
  ```
- Xvfb usage example:
  ```bash
  xvfb-run --server-args="-screen 0 1024x768x24" /opt/creality-print/AppRun \
  --load-settings "<machine>;<process>" \
  --load-filaments "<filament>" \
  --slice 0 \
  --outputdir /output/ \
  /input/model.stl
  ```

## Related
- [[forge-slicer-SPEC]] — Full project specification
- [[Djinn-Forge-3D-printing-pipeline]] — Overview of the Djinn Forge pipeline

TAG RULES:
- topic MUST be one of: psychology, law, business, cs, personal, creative
- path: topic/context/relevant/commonality/specific-tag
- 2-4 tags per note, use hyphens not spaces
- You may create new nodes at context level and below
- Existing vault tags for reference: 1800s/literature/style, 3d-printing/automation, 3d-printing/bore-design, 3d-printing/calibration, 3d-printing/design, 3d-printing/design/embossing, 3d-printing/engraving, 3d-printing/filament/compatible, 3d-printing/filament/handling, 3d-printing/filament/preparation, 3d-printing/filament/profiles/ender-3-v3-plus/pla, 3d-printing/filament/profiles/puffco-recycler, 3d-printing/filament/recommendations, 3d-printing/filament/tracking, 3d-printing/filament/types, 3d-printing/fixes, 3d-printing/glassware/attachment, 3d-printing/inventory-management, 3d-printing/models/benchmark, 3d-printing/models/benchmark-3343, 3d-printing/models/ender-3-v3-plus, 3d-printing/models/ender-3v3-plus, 3d-printing/models/kraken-proxy-pipe, 3d-printing/models/modification/freecad, 3d-printing/models/modification/meshmixer, 3d-printing/models/modification/tinkercad, 3d-printing/models/puffco-proxy, 3d-printing/models/smoking-accessories, 3d-printing/printer-maintenance, 3d-printing/printer-models/ender-3-v3-plus, 3d-printing/printer-setup/beginner-guide, 3d-printing/printer-subsystem, 3d-printing/quality-assurance, 3d-printing/quality/test, 3d-printing/research/marcus, 3d-printing/scripting/python, 3d-printing/slicing, 3d-printing/test-suite