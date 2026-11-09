"""R50 launch in Blender 5.2.2 with user's custom /home/christopher/tab.py
keymap explicitly installed & activated (no global preference save).
Open only R50 experimental metric proxy, never a protected cathedral .blend.
"""
from pathlib import Path
import bpy
from mathutils import Vector
R=Path('/home/christopher/Cathedral_Research/R50_source_graded_tracery')
glb=R/'R50_Brandon_R03_Hypothetical_Metric_Proxy.glb'
preset=Path('/home/christopher/tab.py')
assert glb.is_file() and preset.is_file()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(glb))
stones=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(stones)==1
stone=stones[0]
stone['R50_PROVENANCE']='R03 source-pixel traced geometry; display scale invented'
stone['NO_HISTORICAL_CERTIFICATION']=True
stone['RIB_ARCH_PROFILES_USED']=False
stone.select_set(True)
bpy.context.view_layer.objects.active=stone
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1.
# Required launch preset is imported after factory setup / asset import.
result=bpy.ops.preferences.keyconfig_import(filepath=str(preset),keep_original=True)
wm=bpy.context.window_manager
active=wm.keyconfigs.active
assert result=={'FINISHED'} and active and active.name=='tab'
assert len(active.keymaps)>=10 and sum(len(m.keymap_items) for m in active.keymaps)>=500
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type!='VIEW_3D':continue
  sp=area.spaces.active
  sp.shading.type='SOLID'
  sp.shading.color_type='MATERIAL'
  sp.shading.light='STUDIO'
  sp.shading.show_cavity=True
  sp.shading.cavity_type='BOTH'
  sp.overlay.show_floor=False
  sp.overlay.show_axis_x=False
  sp.overlay.show_axis_y=False
  region=sp.region_3d
  region.view_location=Vector((0,0,.96))
  region.view_distance=3.7
  eye=Vector((.6,-2.8,1.25))
  region.view_rotation=(-eye).to_track_quat('-Z','Y')
  region.view_perspective='PERSP'
print('R50_GUI_GLB_OPEN_WITH_TAB_KEYMAP_SUCCESS',glb,
  'Blender',bpy.app.version_string,
  'keyconfig_active',active.name,
  'keymaps',len(active.keymaps),
  'bindings',sum(len(m.keymap_items) for m in active.keymaps),flush=True)
