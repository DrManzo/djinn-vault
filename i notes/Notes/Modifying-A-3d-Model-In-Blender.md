---
subject: 3d-printing/models/modify-models
tags:
  - 3d-printing/models/modification/blender
  - 3d-printing/tips-and-tricks
created: 2026-06-28
source: Perplexity export

# Modifying a 3D Model in Blender

## Summary
This note provides detailed steps on how to modify a 3D model in Blender, specifically focusing on cutting a part of the model, pushing it back for clearance, and smoothing out the body.

## Key Points
- Use Boolean Difference modifier to cut a section.
- Push the section back using `P → Selection` or `G + [axis]`.
- Smooth the seam with Recalculate Normals, Mark Sharp Edges, Smooth by Angle Modifier, Bevel, and Subdivision Surface modifier if needed.
- Clean up mesh before exporting.

## Details
To modify a 3D model in Blender for 3D printing, follow these steps:

1. **Cut the Part with Boolean:**
   - Add a cutter object (e.g., a cube or custom mesh) that covers exactly the region you want to push back.
   - Position it over that area in Object Mode.
   - Select your main model → go to **Properties > Modifier Properties > Add Modifier > Boolean**.
   - Set it to **Difference**, pick your cutter object as the target, and apply the modifier.

2. **Push the Section Back:**
   - For a separate part: Use `P → Selection` in Edit Mode to separate it, then move it back along its normal axis.
   - For an inset/recessed area: Select the face(s) of the recessed region and use `G + [axis]` to push it inward.

3. **Smooth the Seam:**
   - Recalculate Normals: In Edit Mode, select all → `Shift+N`.
   - Mark Sharp Edges: Select the cut edges (`Ctrl+Alt+Shift+M`) then `Mesh > Edges > Mark Sharp`.
   - Add Smooth by Angle Modifier: In the modifier stack, after your boolean, add a **Smooth by Angle** modifier and enable **Ignore Sharpness**.
   - Bevel the transition edge: In Edit Mode, select the hard cut edge and press `Ctrl+B`, add 2 segments with a profile of 1.0 to create a soft chamfer.
   - Optional Subdivision Surface Modifier: Add a **Subdivision Surface** modifier after the bevel for a smooth organic shape.

4. **Before Exporting to STL:**
   - Run **Mesh > Clean Up > Merge by Distance** to weld any duplicate verts from the boolean.
   - Check for non-manifold geometry with `Ctrl+Alt+Shift+M` and apply all modifiers before exporting.

## References
- Boolean Modifier and Bool Tool Tutorial for Blender 3D: [blender](https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/booleans.html)
- 3D Scan Boolean: Precisely Subtract Parts in Blender: [youtube](https://www.youtube.com/watch?v=GHersJCQUVc)
- How to Use the Boolean Modifier in Blender (Tutorial): [youtube](https://www.youtube.com/watch?v=CHqH5oz0DvQ)

## Related
- [[3d-printing/tips-and-tricks]] — General tips for 3D printing.
- [[3d-printing/models/ender-3-v3-plus]] — Specifics on the Ender 3 V3+ printer model.