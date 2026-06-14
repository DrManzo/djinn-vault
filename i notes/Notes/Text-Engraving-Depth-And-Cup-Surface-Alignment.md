---
subject: 3d-printing/models/cup-engraving
tags:
  - design/3d-printing/engraving
  - design/3d-printing/cup
  - design/3d-printing/text
created: 2026-06-14
source: Perplexity export
---

# Text Engraving Depth and Cup Surface Alignment

## Summary
The text engraving on a cup is not deep enough, causing the text to barely overlap the cup wall. The solution involves pushing the text deeper into the cup.

## Key Points
- The text is flat at Y 50.07, 51.57.
- The cup surface curves from Y≈52 at center to Y≈50 at edges (X=±25).
- The "T" and last "e" are at X≈±25 — the text barely overlaps the cup wall there (only 0.07mm).
- Solution: Push the text deeper into the cup by translating it inward slightly for a 1.9mm engrave.

## Details
To ensure that the text is engraved deeply enough, follow these steps:
1. **Identify the Current Position**: The text is positioned at Y~50-52, while the cup outer surface is at Y~54.
2. **Translate Inward for Engrave Depth**: For a 1.9mm engrave, extend the text inward by 0.4mm in the -Y direction.
   ```python
   bpy.ops.transform.translate(value=(0, -0.4, 0))
   bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
   ```

3. **Project Text Onto Cup Surface**: Use Blender's Shrinkwrap modifier to project the text onto the cup surface.
4. **Recess for Engrave Depth**: After projecting, move the vertices inward by 1.9mm along their normals.
   ```python
   bpy.ops.object.mode_set(mode='EDIT')
   bpy.ops.mesh.select_all(action='SELECT')
   bpy.ops.transform.translate(value=(0, 0, -1.9))
   ```

5. **Boolean Difference**: Perform a Boolean difference operation to carve the text into the cup.

## References
- [Blender Script for Text Engraving](https://claude.ai/chat/f650de23-c25b-4eec-b053-bb97cdfda1d5)

## Related
- [[Report-On-Legibility-Issues-With-Embossed-Text]] — similarity, [[Designing-A-Script-For-Puffco-Proxy-Bore]] — engraving technique
