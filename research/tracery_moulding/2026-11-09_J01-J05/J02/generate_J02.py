# J02 — localized exact junction union, reference-only and non-destructive.
import bpy,bmesh,math,os,json
from mathutils import Vector,kdtree
ROOT='/home/christopher/Cathedral_Experiments/tracery_moulding_J02'
os.makedirs(ROOT,exist_ok=True)
prev='/home/christopher/Cathedral_Experiments/tracery_moulding_J01/generate_J01.py'
source=open(prev).read()
# Recover J01's true profile, sweep, analytic set-out and inspection unchanged.
exec(source[:source.index('paths=[]')],globals())
exec(source[source.index('def inspect(ob):'):source.index('for o in parts:')],globals())
ROOT='/home/christopher/Cathedral_Experiments/tracery_moulding_J02'
# J02 uses three independently parameterized paths, meeting at an architectural Y junction.
def build_test(prefix):
    specs=[
      ('main',[(0,0),(0,7),(0,12),(0,16),(0,20),(0,24),(0,28),(0,34),(0,40),(0,48)]),
      ('branch_left',[(-16,39),(-11,34),(-7,30),(-4,27),(-1.3,24.3),(.4,22.6)]),
      ('branch_right',[(16,39),(11,34),(7,30),(4,27),(1.3,24.3),(-.4,22.6)])
    ]
    return [sweep(prefix+' '+name,pts,palette[i]) for i,(name,pts) in enumerate(specs)]
def smooth_render_mat(ob,mat):
    ob.data.materials.clear();ob.data.materials.append(mat)
    for f in ob.data.polygons:f.material_index=0
def exact_union(parts):
    base=parts[0]
    for other in parts[1:]:
        bpy.context.view_layer.objects.active=base
        mod=base.modifiers.new('EXACT '+other.name,'BOOLEAN')
        mod.operation='UNION'; mod.solver='EXACT';mod.object=other
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(other,do_unlink=True)
    # Weld only near-coincident vertices. No global voxel remesh or smoothing.
    bm=bmesh.new();bm.from_mesh(base.data)
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.00001)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(base.data);bm.free()
    return base
def displaced(ob,x):
    ob.location.x=x
    return ob
# Copy input exact coordinates (outside junction) for numeric preservation tests.
parts=build_test('EXACT')
source_verts=[tuple(v.co) for v in parts[0].data.vertices if v.co.y < 14 or v.co.y > 42]
exact=exact_union(parts)
q_exact=inspect(exact)
coords=[v.co.copy() for v in exact.data.vertices]
tree=kdtree.KDTree(len(coords))
for i,p in enumerate(coords):tree.insert(p,i)
tree.balance()
deviations=[tree.find(Vector(p))[2] for p in source_verts]
q_exact['control_vertices']=len(source_verts)
q_exact['max_control_vertex_drift']=max(deviations)
q_exact['preservation_tolerance']=1e-5
assert q_exact['connected_components']==1 and q_exact['boundary_edges']==0 and q_exact['nonmanifold_edges']==0, q_exact
assert max(deviations)<1e-5,('Non-junction profile drift',max(deviations))
# Round trip the exact profile union, then verify glTF seam splits are weldable.
bpy.ops.object.select_all(action='DESELECT')
exact.select_set(True);bpy.context.view_layer.objects.active=exact
glb=os.path.join(ROOT,'J02_exact_local_junction.glb')
bpy.ops.export_scene.gltf(filepath=glb,export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.import_scene.gltf(filepath=glb)
imported=[o for o in bpy.context.selected_objects if o.type=='MESH']
assert imported
for o in imported:
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.00001)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(o.data);bm.free()
q_glb=[inspect(o) for o in imported]
assert all(z['connected_components']==1 and z['boundary_edges']==0 and z['nonmanifold_edges']==0 for z in q_glb),q_glb
for o in imported:bpy.data.objects.remove(o,do_unlink=True)
# Competing J01 voxel approach, same three source sweeps, to isolate only the fusion algorithm.
voxel_parts=build_test('VOXEL')
bpy.ops.object.select_all(action='DESELECT')
for o in voxel_parts:o.select_set(True)
bpy.context.view_layer.objects.active=voxel_parts[0]
bpy.ops.object.join()
voxel=voxel_parts[0]
voxel.data.remesh_voxel_size=.18
bpy.ops.object.select_all(action='DESELECT')
voxel.select_set(True);bpy.context.view_layer.objects.active=voxel
bpy.ops.object.voxel_remesh()
q_voxel=inspect(voxel)
assert q_voxel['boundary_edges']==0 and q_voxel['nonmanifold_edges']==0
voxel_coords=[v.co.copy() for v in voxel.data.vertices]
vt=kdtree.KDTree(len(voxel_coords))
for i,p in enumerate(voxel_coords):vt.insert(p,i)
vt.balance()
q_voxel['max_control_vertex_drift']=max(vt.find(Vector(p))[2] for p in source_verts)
# Composition: 2 exactly equivalent local Y junctions positioned side by side.
displaced(voxel,-25.0);displaced(exact,25.0)
smooth_render_mat(voxel,palette[0])
smooth_render_mat(exact,stone)
def label(text,x,y,size=1.6):
    curve=bpy.data.curves.new('review text','FONT');curve.body=text
    curve.size=size;curve.align_x='CENTER'
    obj=bpy.data.objects.new('label: '+text,curve)
    bpy.context.collection.objects.link(obj);obj.location=(x,y,1.0)
    curve.materials.append(label_mat)
label('J02     /     PROFILE-PRESERVING Y JUNCTION',0,56,2.25)
label('A     VOXEL FUSION',-25,51,1.95)
label('B     EXACT LOCAL UNION',25,51,1.95)
label('Global remesh, profile approximated',-25,-6,1.2)
label('No voxel remesh, original control points retained',25,-6,1.2)
label('UNVERIFIED SOURCE SCALE     /     EXPERIMENTAL ONLY',0,-12,1.1)
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,21,-2.5))
floor=bpy.context.object;floor.name='review backing'
floor.scale=(53,42,1);floor.data.materials.append(background)
world=bpy.context.scene.world or bpy.data.worlds.new('World')
bpy.context.scene.world=world;world.color=(.17,.19,.25)
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.23,.25,.28,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
for name,loc,power,size in [
    ('soft box',(-30,35,52),1200,45),('edge light',(35,30,40),1000,40)]:
    ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size
    ob=bpy.data.objects.new(name,ld);bpy.context.collection.objects.link(ob)
    ob.location=loc;ob.rotation_euler=(Vector((0,21,0))-ob.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('Front review')
cam=bpy.data.objects.new('Front review',camdata);bpy.context.collection.objects.link(cam)
cam.location=(0,23,140);cam.rotation_euler=(0,0,0)
camdata.type='ORTHO';camdata.ortho_scale=114
sc=bpy.context.scene;sc.camera=cam
sc.render.engine='CYCLES';sc.cycles.samples=25
sc.render.resolution_x=1480;sc.render.resolution_y=980
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.render.filepath=os.path.join(ROOT,'J02_FINAL_profile_preservation.png')
sc.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'J02_EXPERIMENTAL.blend'))
result={'status':'experimental','blender':bpy.app.version_string,
        'method':'exact mesh boolean union, local node isolated; no voxel remesh',
        'exact':q_exact,'voxel_reference':q_voxel,'glb_roundtrip':q_glb,
        'profile':PROFILE,'control_region':'main stem y <14 or y >42',
        'source_geometry':'J01 synthetic Y-junction using same 17-point experimental profile',
        'historical_validation':False,'architectural_validation':False,
        'structural_validation':False,'native_units_verified':False}
with open(os.path.join(ROOT,'J02_QA.json'),'w') as f:json.dump(result,f,indent=2)
bpy.ops.render.render(write_still=True)
print('J02_PASS',json.dumps(result))
