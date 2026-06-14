---
subject: Creative/Aesthetic
tags:
  - 3d-printing/design/embossing
  - 3d-printing/calibration/cube
  - cs/scripting/blender
created: 2026-06-14
source: Perplexity export
---

# Text Engraving Depth and Cup Surface Alignment

## Summary
The text engraving on a cup is not correctly aligned due to the cup's curved surface. The solution involves adjusting the text depth using Blender scripting.

## Key Points
- The text is flat at Y 50.07, 51.57.
- The cup surface curves from Y≈52 at center to Y≈50 at edges (X=±25).
- Text barely overlaps the cup wall by only 0.07mm at X≈±25.
- Solution: Push text deeper into the cup.

## Details
To ensure that the text is engraved correctly, the script needs to adjust the depth of the text based on the cup's surface curvature. The current text is positioned at Y~50-52, while the cup's outer surface is at Y~54. To achieve a 1.9mm engrave depth, the text must be translated inward by 0.4mm in the -Y direction.

### Steps to Adjust Text Depth
1. **Import Cup Model**: Load the STL file of the cup.
2. **Parse Text Mesh**: Extract the text mesh from the 3MF file.
3. **Apply Transform**: Apply the transformation matrix to position the text correctly.
4. **Project Text onto Surface**: Use Blender's Shrinkwrap modifier to project the text onto the cup surface.
5. **Recess Text for Engrave**: Move the vertices of the text inward by 1.9mm along their normals.

### Example Code
```python
import bpy
import os

# Clean slate
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import cup model
cup_path = os.path.expanduser('/tmp/opencode/cup.stl')
bpy.ops.wm.stl_import(filepath=cup_path)
cup_obj = bpy.context.active_object

# Parse text mesh from 3MF file
ns3mf_path = os.path.expanduser(
    '~/Obsidian/djinn/printer/library/cup/cup_engraved-Terp Tribe HQ.3mf'
)
with zipfile.ZipFile(ns3mf_path) as zf:
    mesh_xml = zf.read('3D/Objects/cup_engraved.stl_1.model').decode('utf-8')
    model_xml = zf.read('3D/3dmodel.model').decode('utf-8')

mesh_root = ET.fromstring(mesh_xml)
model_root = ET.fromstring(model_xml)

def parse_mesh_xml(root):
    meshes = {}
    for obj in root.findall('.//ns:object', NS):
        oid = int(obj.get('id'))
        mesh_elem = obj.find('ns:mesh', NS)
        if mesh_elem is None:
            continue
        verts_elem = mesh_elem.find('ns:vertices', NS)
        tris_elem = mesh_elem.find('ns:triangles', NS)
        verts = []
        for v in verts_elem.findall('ns:vertex', NS):
            verts.append((float(v.get('x')), float(v.get('y')), float(v.get('z'))))
        faces = []
        for t in tris_elem.findall('ns:triangle', NS):
            faces.append((int(t.get('v1')), int(t.get('v2')), int(t.get('v3'))))
        meshes[oid] = (verts, faces)
    return meshes

meshes = parse_mesh_xml(mesh_root)
text_verts, text_faces = meshes[2]

# Get transform
resources = model_root.find('ns:resources', NS)
obj3 = resources.find(".//ns:object[@id='3']", NS)
for comp in obj3.findall('.//ns:component', NS):
    if int(comp.get('objectid')) == 2:
        vals = list(map(float, comp.get('transform').split()))
        break
a, b, c, d, e, f, g, h, i, tx, ty, tz = vals
transform = mathutils.Matrix((
    (a, d, g, tx),
    (b, e, h, ty),
    (c, f, i, tz),
    (0, 0, 0, 1)
))

# Create text mesh in Blender
mesh_data = bpy.data.meshes.new("text_mesh")
mesh_data.from_pydata(text_verts, [], text_faces)
mesh_data.update()
text_obj = bpy.data.objects.new("text", mesh_data)
bpy.context.collection.objects.link(text_obj)
text_obj.matrix_world = transform

# Project text onto cup surface using Shrinkwrap
shrink = text_obj.modifiers.new(name="ProjectToCup", type='SHRINKWRAP')
shrink.target = cup_obj
shrink.offset = 0.0 # snap exactly to cup surface
shrink.wrap_method = 'NEAREST_SURFACEPOINT' # project to nearest surface
shrink.use_keep_above_surface = False

# Apply the shrinkwrap
bpy.context.view_layer.objects.active = text_obj
bpy.ops.object.modifier_apply(modifier=shrink.name)

# Recess text for engrave
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.translate(value=(0, 0, -1.9)) # push to use transform
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.transform.push_pull(value=-1.9) # negative = push inward
bpy.ops.object.mode_set(mode='OBJECT')

# Boolean difference for engraving
bpy.ops.object.select_all(action='DESELECT')
cup_obj.select_set(True)
text_obj.select_set(True)
bpy.context.view_layer.objects.active = cup_obj
mod = cup_obj.modifiers.new(name="Engrave", type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = text_obj
mod.solver = 'EXACT'
bpy.ops.object.modifier_apply(modifier=mod.name)

# Export final model
out_path = os.path.expanduser('~/Downloads/cup_engraved_final.stl')
bpy.ops.wm.stl_export(
    filepath=out_path,
    check_existing=False,
    global_scale=1.0,
    export_selected_objects=False,
    ascii_format=False,
    forward_axis='Y',
    up_axis='Z',
    apply_modifiers=True
)

print(f"Exported: {out_path}")
```

## References
- [Claude Chat](https://claude.ai/chat/f650de23-c25b-4eec-b053-bb97cdfda1d5)
- Blender scripting documentation

## Related
- [[Text-Engraving-Depth-And-Cup-Surface-Alignment]] — similarity 0.93
- [[Script-For-Puffco-Proxy-Core-Bore]] — similarity 0.70
