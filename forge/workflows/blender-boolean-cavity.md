---
title: Blender — Boolean Cavity / Hollow
tags: [blender, workflow, modeling, boolean]
created: 2026-07-12
---

# Blender — Cut a Cavity into an STL

Use when you want to hollow out part of a model (pocket, recess, blind hole) without rebuilding it from scratch.

## Steps

1. **Import the STL**
   File → Import → STL

2. **Add a cutter shape**
   `Shift+A` → Mesh → Cube (flat pocket) or Cylinder (round pocket)

3. **Position and size the cutter**
   - `S` to scale, `S Z` for height only
   - `G Z` to move up/down
   - The overlap between cutter and model is what gets removed
   - Let the cutter stick out above the model surface — it needs to fully penetrate

4. **Apply scale on both objects first**
   Select each object → `Ctrl+A` → Apply → Scale
   (Skip this and booleans will behave badly)

5. **Add the Boolean modifier to the main model**
   Select the main model → Properties panel (wrench icon) → Add Modifier → Boolean
   - Operation: **Difference**
   - Object: select your cutter
   - Click **Apply**

6. **Delete the cutter**
   Select it → `X`

7. **Check geometry**
   `Tab` into Edit Mode, look for flipped normals or holes on the inside of the cut

8. **Export**
   File → Export → STL

## Notes

- Cube cutter → flat-bottomed rectangular pocket
- Cylinder cutter → round or dome-shaped recess
- For a tapered pocket, use a cone or a scaled cylinder
- If the result looks wrong, Undo and check that scale was applied on both objects before running the boolean
- Blender's boolean can leave internal geometry — run Mesh → Clean Up → Merge by Distance after applying if exporting to print

## Used on

- Camood top hollow — 2026-07-12
