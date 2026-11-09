"""Open validated R45 GLB on MR.COMPUTER in Blender 5.2.2.
Read-only inspection. Do not open, save or alter the protected F5ZP scene.
"""
import bpy
from pathlib import Path
from mathutils import Vector
R=Path('/home/christopher/Cathedral_Research/R45_production_candidate')
G=R/'R45_UNIFIED_BRANCHING_STONE_GENERATOR.glb'
assert G.is_file() and G.stat().st_size>20000
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(G))
pieces=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(pieces)==6, ('Expected 6 stones in GLB',len(pieces))
for ob in pieces:
 ob['R45_REVIEW_CLASS']='EXPERIMENTAL; NOT HISTORICALLY CERTIFIED'
 ob.select_set(False)
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type!='VIEW_3D':continue
  space=area.spaces.active
  space.shading.type='SOLID'
  space.shading.color_type='MATERIAL'
  space.shading.light='STUDIO'
  space.shading.show_cavity=True
  space.shading.cavity_type='BOTH'
  space.overlay.show_floor=False
  space.overlay.show_axis_x=False
  space.overlay.show_axis_y=False
  v=space.region_3d
  v.view_location=Vector((0,0,.40))
  v.view_distance=2.50
  eye=Vector((1.0,-1.8,1.10))
  v.view_rotation=(-eye).to_track_quat('-Z','Y')
  v.view_perspective='PERSP'
print('R45_GUI_GLB_OPEN_SUCCESS',G,'independent_stones',len(pieces),
      'Blender',bpy.app.version_string,flush=True)
