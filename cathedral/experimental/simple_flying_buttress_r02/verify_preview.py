import bpy,runpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent
m=runpy.run_path(str(P/'flying_buttress_r02.py'),run_name='generator_module')
bpy.ops.wm.read_factory_settings(use_empty=True)
sentinel=bpy.data.objects.new('UNRELATED',None);bpy.context.scene.collection.objects.link(sentinel);sentinel.location=(12,34,56)
plain={**m['DEFAULTS'],'tracery':False,'tower':False}
oo,_=m['build'](plain);assert len(oo)==4
original=[tuple(v.co) for v in next(o for o in oo if o.name.endswith('_FLYER')).data.vertices]
oo,q=m['build'](m['DEFAULTS']);oo,q=m['build'](m['DEFAULTS'])
assert len(oo)==10 and tuple(sentinel.location)==(12,34,56)
assert original==[tuple(v.co) for v in next(o for o in oo if o.name.endswith('_FLYER')).data.vertices]
panel=next(o for o in oo if o.name.endswith('_PIERCED_TRACERY'))
tree=BVHTree.FromPolygons([v.co for v in panel.data.vertices],[list(f.vertices) for f in panel.data.polygons])
for h in q['holes']:
 x,z=h['center_xz'];hit=tree.ray_cast(Vector((x,-1000,z)),Vector((0,1,0)),2000)
 assert hit[0] is None,'uncut hole'
# Two repeated systems must build independently.
two={**m['DEFAULTS'],'repeat_count':2};oo,qq=m['build'](two);assert len(oo)==20 and len(qq['holes'])==10
bpy.ops.wm.open_mainfile(filepath=str(P/'output/flying_buttress_r02.blend'))
def bounds(o):return [[min((o.matrix_world@Vector(v))[i] for v in o.bound_box) for i in range(3)],[max((o.matrix_world@Vector(v))[i] for v in o.bound_box) for i in range(3)]]
expected={o.name:bounds(o) for o in bpy.context.scene.objects if o.type=='MESH'}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(P/'output/flying_buttress_r02.glb'))
actual={o.name:bounds(o) for o in bpy.context.scene.objects if o.type=='MESH'}
assert set(expected)==set(actual)
err=max(abs(a-b) for n in expected for r,s in zip(expected[n],actual[n]) for a,b in zip(r,s));assert err<.01
report=dict(plain_objects=4,ornamented_objects=10,repeated_units_objects=20,holes_ray_test_passed=5,flyer_vertices_unchanged=True,idempotence=True,unrelated_object_preserved=True,glb_max_bound_error=err)
(P/'output/VERIFICATION.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(P/'output/flying_buttress_r02.blend'))
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_cavity=True
sc.world=bpy.data.worlds.new('Review');sc.world.color=(.85,.85,.85)
bpy.ops.object.camera_add(location=(10000,-18000,11000));cam=bpy.context.object;cam.rotation_euler=(Vector((2300,0,4100))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=11500;cam.data.clip_end=100000;sc.camera=cam
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.clip_end=100000;area.spaces.active.region_3d.view_location=(2300,0,4100);area.spaces.active.region_3d.view_distance=11500
sc.render.resolution_x=1200;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.filepath=str(P/'output/preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'output/flying_buttress_r02.blend'));bpy.ops.render.render(write_still=True)
print('R02_VERIFIED',report)
