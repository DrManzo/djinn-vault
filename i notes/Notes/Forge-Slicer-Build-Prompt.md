---
subject: djinn/printer/forge-slicer
tags:
  - cs/programming/docker
  - 3d-printing/slicing
  - forge-slicer/critical-details
created: 2026-06-28
source: Perplexity export
---

# Forge-Slicer Build Prompt

## Summary
This note provides the detailed instructions and technical specifications for building `forge-slicer`, a Docker container that wraps Creality Print for headless STL slicing. The goal is to create a reliable slicing pipeline for 3D printing projects.

## Key Points
- **Purpose**: Create a Docker container for headless slicing of STL files using Creality Print.
- **Challenges**: Creality Print's CLI crashes in headless mode, necessitating running it inside Docker with Xvfb and Mesa.
- **Deliverables**:
  - `Dockerfile`
  - `entrypoint.py`
  - `profiles/` directory
  - `slice.sh` shell script

## Details
The task involves setting up a Docker container that can handle the slicing process for various 3D printing projects. The key steps include:

1. **Extracting Creality Print AppImage**: Use the `--appimage-extract` flag to extract the AppImage.
2. **Running Creality Print in Xvfb**: Utilize `xvfb-run` to run Creality Print with a virtual display and Mesa for rendering.
3. **Profile Formats**: Ensure correct JSON formats for process and filament profiles, as specified by Creality Print 7.x.
4. **Output Parsing**: Parse the gcode file to extract printing time and filament usage details.

### Critical Technical Details
- **AppImage Extraction**:
  ```dockerfile
  RUN ./CrealityPrint.AppImage --appimage-extract && \
  mv squashfs-root /opt/creality-print
  ```
- **Xvfb Usage**:
  ```bash
  xvfb-run --server-args="-screen 0 1024x768x24" /opt/creality-print/AppRun \
  --load-settings "<machine>;<process>" \
  --load-filaments "<filament>" \
  --slice 0 \
  --outputdir /output/ \
  /input/model.stl
  ```
- **Profile Format**:
  - Process Profile Example:
    ```json
    {
      "type": "process",
      "from": "User",
      "inherits": "0.25mm Standard @Creality Ender-3 V3 Plus 0.4 nozzle",
      "name": "Calliope-Proto",
      "print_settings_id": "Calliope-Proto",
      "version": "26.1.31.15",
      "compatible_printers": ["Creality Ender-3 V3 Plus 0.4 nozzle"],
      "layer_height": "0.28",
      "wall_loops": "2",
      "sparse_infill_density": "8",
      "sparse_infill_pattern": "gyroid",
      "outer_wall_speed": "60",
      "inner_wall_speed": "80",
      "sparse_infill_speed": "80",
      "bottom_shell_layers": "2",
      "top_shell_layers": "2",
      "brim_type": "no_brim",
      "enable_support": "0"
    }
    ```
  - Filament Profile Example:
    ```json
    {
      "type": "filament",
      "from": "User",
      "inherits": "Hyper PLA @Creality Ender-3 V3 Plus 0.4 nozzle",
      "name": "Calliope-PLA-Blue",
      "filament_settings_id": "Calliope-PLA-Blue",
      "version": "26.1.31.15",
      "nozzle_temperature": "215",
      "nozzle_temperature_initial_layer": "215",
      "cool_plate_temp": "60",
      "cool_plate_temp_initial_layer": "60",
      "pressure_advance": "0.042",
      "fan_min_speed": "100",
      "fan_max_speed": "100"
    }
    ```
- **entrypoint.py JSON Output**:
  ```json
  {
    "success": true,
    "gcode_path": "/output/model_proto.gcode",
    "print_time_raw": "1h 23m",
    "print_time_s": 4980,
    "filament_g": 14.2,
    "filament_mm": 4821,
    "error": null
  }
  ```
- **slice.sh (Host-Side)**:
  ```bash
  #!/bin/bash
  # Usage: slice.sh <abs_stl_path> <profile: proto|production|quality> <material: pla|petg|abs>
  ```

## References
- `~/Obsidian/djinn/printer/forge-slicer/SPEC.md`
- Creality Print 7.x documentation

## Related
- [[forge/forge-slicer/MARCUS-SUPPORT-PROMPT]] — Detailed build instructions
- [[3d-printing/slicing/critical-details]] — Additional slicing best practices