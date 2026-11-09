import bpy
from mathutils import Vector
from pathlib import Path
path=Path('/home/christopher/Cathedral_Research/R44_bearing_regression/R44_A50/R42_BRANCHING_JOINT_AND_REBATES.glb')
assert path.is_file() and path.stat().st_size>10000
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(path))
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(objs)==3, f'Expected three blocks, got {len(objs)}'
for ob in objs:
 ob.select_set(True)
 bpy.context.view_layer.objects.active=ob
 ob['source_status']='R44 EXPERIMENTAL, NOT HISTORICALLY AUTHENTICATED'
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1.0
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active
   sp.shading.type='SOLID'
   sp.shading.color_type='MATERIAL'
   sp.shading.light='STUDIO'
   sp.shading.show_cavity=True
   sp.shading.cavity_type='BOTH'
   sp.overlay.show_floor=False
   sp.overlay.show_axis_x=False
   sp.overlay.show_axis_y=False
   sp.region_3d.view_location=Vector((0,0,.42))
   sp.region_3d.view_distance=1.48
   sp.region_3d.view_rotation=Vector((.9,-1.25,.85)).to_track_quat('-Z','Y')
print('R44_GUI_OPEN_SUCCESS',path,'meshes',len(objs),flush=True)
