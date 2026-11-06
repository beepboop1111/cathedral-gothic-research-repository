import bpy,runpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
m=runpy.run_path(str(P/'flying_buttress.py'),run_name='generator_module')
bpy.ops.wm.read_factory_settings(use_empty=True)
sentinel=bpy.data.objects.new('UNRELATED_REFERENCE',None);bpy.context.scene.collection.objects.link(sentinel);sentinel.location=(123,456,789)
objects,qa=m['build'](m['DEFAULTS'].copy());objects,qa=m['build'](m['DEFAULTS'].copy())
assert tuple(sentinel.location)==(123,456,789) and len(objects)==4
bad=m['DEFAULTS'].copy();bad['span']=-1
try:m['build'](bad);raise AssertionError('invalid setting accepted')
except ValueError:pass
two=m['DEFAULTS'].copy();two['repeat_count']=2
oo,_=m['build'](two);assert len(oo)==8
bpy.ops.wm.open_mainfile(filepath=str(P/'output/flying_buttress.blend'))
def bounds(o):return [[min((o.matrix_world@Vector(v))[i] for v in o.bound_box) for i in range(3)],[max((o.matrix_world@Vector(v))[i] for v in o.bound_box) for i in range(3)]]
expected={o.name:bounds(o) for o in bpy.context.scene.objects if o.type=='MESH'}
assert len(expected)==4
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(P/'output/flying_buttress.glb'))
actual={o.name:bounds(o) for o in bpy.context.scene.objects if o.type=='MESH'}
assert set(expected)==set(actual)
err=max(abs(a-b) for n in expected for r,s in zip(expected[n],actual[n]) for a,b in zip(r,s));assert err<.01
(P/'output/VERIFICATION.json').write_text(json.dumps(dict(idempotence=True,unrelated_object_preserved=True,invalid_config_rejected=True,two_unit_repeat=True,glb_mesh_count=4,max_bound_error=err),indent=2))
bpy.ops.wm.open_mainfile(filepath=str(P/'output/flying_buttress.blend'))
assert bpy.data.collections[m['TAG']].get('generator')==m['TAG']
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True
scene.world=bpy.data.worlds.new('Demo_world');scene.world.color=(.85,.85,.85)
bpy.ops.object.camera_add(location=(11000,-16000,11000));cam=bpy.context.object
cam.rotation_euler=(Vector((2500,0,4000))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=11500;cam.data.clip_end=100000;scene.camera=cam
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.clip_end=100000;area.spaces.active.region_3d.view_location=(2500,0,4000);area.spaces.active.region_3d.view_distance=11500
scene.render.resolution_x=1100;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.filepath=str(P/'output/preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'output/flying_buttress.blend'))
bpy.ops.render.render(write_still=True)
print('VERIFIED',err)
