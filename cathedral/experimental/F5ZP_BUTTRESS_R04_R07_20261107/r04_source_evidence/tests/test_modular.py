"""One combined modular-generator test. Writes only the requested preview PNG."""
import bpy,runpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]/'current'
m=runpy.run_path(str(P/'flying_buttress_r02.py'),run_name='generator_module')
bpy.ops.wm.read_factory_settings(use_empty=True)
sentinel=bpy.data.objects.new('UNRELATED_REFERENCE',None);bpy.context.scene.collection.objects.link(sentinel);sentinel.location=(12,34,56)
config=m['DEFAULTS'].copy()
objects,qa=m['build'](config)
assert tuple(sentinel.location)==(12,34,56)
assert all(r['nonmanifold_edges']==0 and r['degenerate_polygons']==0 for r in qa['fit_checks']['meshes'])
assert not qa['fit_checks']['neighbor_overlaps']
assert not any(r['gap'] for r in qa['fit_checks']['interfaces'])
def sig(o):return hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons],tuple(map(tuple,o.matrix_world)))).encode()).hexdigest()
root=bpy.data.collections[m['base'].TAG]
protected={o.name:(o.as_pointer(),sig(o)) for o in root.all_objects if o.type=='MESH' and not any(c.name.endswith('_tower_details') for c in o.users_collection)}
changed={**config,'detail_controls':{'scale':1.1,'projection':5.,'orientation_degrees':10.,'count':4,'spacing':240.}}
objects,partial=m['build'](changed,components=['tower_details'])
assert all(o.name in protected and (o.as_pointer(),sig(o))==protected[o.name] for o in root.all_objects if o.name in protected)
assert partial['components_rebuilt']==['tower_details']
assert all(r['nonmanifold_edges']==0 and r['degenerate_polygons']==0 for r in partial['fit_checks']['meshes'])
# The primitive API accepts edited circular arcs and arbitrary moulding sections.
path,closed=m['path_from_spec'](dict(type='arc',center=(0,0,0),radius=100,start_degrees=15,end_degrees=160,segments=24))
assert len(path)==25 and not closed
arc_col=bpy.data.collections.new('TEST_ONLY');bpy.context.scene.collection.children.link(arc_col)
mat=m['base'].material('TEST_MATERIAL',(.6,.6,.6))
probe=m['sweep_profile'](arc_col,'SUPPLIED_PROFILE_TEST',path,[(-5,-4),(5,-4),(7,0),(0,7),(-7,0)],mat,scale=1.3,projection=2,orientation_degrees=23)
assert not any(r['nonmanifold_edges'] for r in m['fit_checks']([probe])['meshes'])
try:
 m['bounded_insert'](arc_col,'OUTSIDE_TEST',[dict(type='circle',center=(100,0,100),radius=20)],[(-2,-2),(2,-2),(2,2),(-2,2)],mat,[(-1,-1),(1,-1),(1,1),(-1,1)])
 raise AssertionError('Boundary failure not rejected')
except ValueError:pass
try:
 m['_profile_check']([(0,0),(10,10),(0,10),(10,0)])
 raise AssertionError('Crossing section not rejected')
except ValueError:pass
# Deliberately duplicated bars must register overlap, and a remote anchor a gap.
a=m['base'].box(arc_col,'OVERLAP_A',0,0,0,20,20,20,mat);b=m['base'].box(arc_col,'OVERLAP_B',5,5,5,20,20,20,mat)
diag=m['fit_checks']([a,b],[('EXPECTED_GAP',(100,100,100),a)],[(a,b)])
assert diag['neighbor_overlaps'] and diag['interfaces'][0]['gap']
for ob in list(arc_col.objects):
 data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
 if data and data.users==0:bpy.data.meshes.remove(data)
bpy.data.collections.remove(arc_col)
assert tuple(sentinel.location)==(12,34,56)
print('COMBINED_TEST_PASS',json.dumps(dict(meshes=len(objects),anchors=len(qa['anchors']),selective_rebuild=True,custom_profile=True,editable_arc=True,boundary_rejection=True,overlap_detection=True,gap_detection=True,unrelated_object_preserved=True)))
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_cavity=True
sc.world=bpy.data.worlds.new('Review');sc.world.color=(.86,.86,.86)
bpy.ops.object.camera_add(location=(9000,-19000,10000));cam=bpy.context.object;cam.rotation_euler=(Vector((2300,0,4150))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=11200;cam.data.clip_end=100000;sc.camera=cam
sc.render.resolution_x=1400;sc.render.resolution_y=1300;sc.render.resolution_percentage=100;sc.render.filepath=str(P/'output/modular_generator_result.png')
bpy.ops.render.render(write_still=True)
