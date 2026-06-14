---
subject: 3d-printing/models/puffco-proxy/upgrades
tags:
  - cs/scripting
  - cs/geometry
  - 3d-printing/bore-design
  - 3d-printing/calibration/cube
created: 2026-06-14
source: Perplexity export
---

# Script for Puffco Proxy Core Bore

## Summary
This note outlines the process to create a Python script that will scan an STL file of a Puffco Proxy body, locate its top face, and subtract a cylindrical bore with specified dimensions (38mm diameter × 51mm depth).

## Key Points
- The task involves creating a pure Python pipeline without AI.
- The script needs to handle both binary and ASCII STL formats.
- Determining the "top" of the object is critical; three methods are discussed.

## Details
The goal is to create a bore in a Puffco Proxy body using a Python script. Here’s how we can approach this:

1. **STL Format**: Most slicer-exported STLs are binary, but we need to handle both binary and ASCII formats.
2. **Defining "the Top"**:
   - **Highest Z face centroid**: Simplest method for flat-top objects.
   - **Largest upward-facing flat region**: Better for complex geometry with multiple flat faces.
   - **User-specified Z coordinate**: Most robust for production use.

The script will perform the following steps:
- Read the STL file.
- Identify the top face of the object based on the chosen method.
- Subtract a cylindrical bore (38mm diameter × 51mm depth) from this face.

## References
- [STL Format](https://math.mit.edu/~djk/calculus_beginners/chapter00/section02.html)

## Related
- [[Designing-A-Script-For-Puffco-Proxy-Bore]] — similar geometry operations
- [[3d-printing/filament/tracking]] — filament usage in bore creation
