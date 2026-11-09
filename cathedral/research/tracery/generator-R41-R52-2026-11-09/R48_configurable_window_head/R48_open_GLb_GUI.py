"""Open R48 validated experimental 29-stone GLB in Blender GUI on MR.COMPUTER.
Read-only source asset inspection; does not open/alter F5ZP or R41–R47.
"""
import bpy
from pathlib import Path
from mathutils import Vector
R=Path('/home/christopher/Cathedral_Research/R48_configurable_window_head/R48_BASELINE_PROFILE_1')
GLB=R/'R48_WINDOW_HEAD_1to1_EXPERIMENT.glb'
assert GLB.is_file() and GLB.stat().st_size>100000
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(GLB))
stones=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(stones)==29,('Expected 29 physically separate stone meshes',len(stones))
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1.
for ob in stones:
 ob.select_set(False)
 ob['R48_status']='GEOMETRICALLY VALIDATED, HISTORICAL AND STRUCTURAL NOT CERTIFIED'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type!='VIEW_3D':continue
  sp=area.spaces.active
  sp.shading.type='SOLID';sp.shading.color_type='MATERIAL'
  sp.shading.light='STUDIO';sp.shading.show_cavity=True
  sp.shading.cavity_type='BOTH'
  sp.overlay.show_floor=False
  sp.overlay.show_axis_x=False;sp.overlay.show_axis_y=False
  v=sp.region_3d
  v.view_location=Vector((0,0,1.39))
  v.view_distance=4.45
  v.view_rotation=Vector((-2.2,5.0,-1.6)).to_track_quat('-Z','Y')
  v.view_perspective='PERSP'
print('R48_GUI_GLB_OPEN_SUCCESS',GLB,'mesh_stones',len(stones),
      'Blender_version',bpy.app.version_string,flush=True)
