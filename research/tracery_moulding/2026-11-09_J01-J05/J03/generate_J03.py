# J03: Apply J02 exact Boolean to entire J01 window with QA
import bpy,bmesh,math,os,json,time
from mathutils import Vector,kdtree
ROOT='/home/christopher/Cathedral_Experiments/tracery_moulding_J03'
os.makedirs(ROOT,exist_ok=True)
reference='/home/christopher/Cathedral_Experiments/tracery_moulding_J01/generate_J01.py'
s=open(reference).read()
# Lift tested procedural construction, materials, path generator, and QA helpers only.
exec(s[:s.index('paths=[]')],globals())
exec(s[s.index('paths=[]'):s.index('parts=[sweep(')],globals())
exec(s[s.index('def inspect(ob):'):s.index('for o in parts:')],globals())
ROOT='/home/christopher/Cathedral_Experiments/tracery_moulding_J03'
print('J03 input path count',len(paths),flush=True)
# Mesh components retained to compare original station positions, outside union.
pieces=[sweep(name,pts,palette[i%len(palette)]) for i,(name,pts) in enumerate(paths)]
source_xyz={o.name:[tuple(v.co) for v in o.data.vertices] for o in pieces}
source_q=[inspect(o) for o in pieces]
assert all(q['boundary_edges']==0 for q in source_q)
# Track each Boolean to isolate any unsupported intersection and prevent false positives.
parent=pieces[0]
ops=[]
for other in pieces[1:]:
    bpy.ops.object.select_all(action='DESELECT')
    parent.select_set(True);bpy.context.view_layer.objects.active=parent
    mod=parent.modifiers.new('exact_'+other.name,'BOOLEAN')
    mod.operation='UNION';mod.solver='EXACT';mod.object=other
    t=time.time()
    bpy.ops.object.modifier_apply(modifier=mod.name)
    q=inspect(parent)
    ops.append({'merged':other.name,'seconds':round(time.time()-t,3),
                'connected_components':q['connected_components'],
                'boundary_edges':q['boundary_edges'],'nonmanifold_edges':q['nonmanifold_edges']})
    bpy.data.objects.remove(other,do_unlink=True)
    print('J03 union',ops[-1],flush=True)
# Fusion may produce multiple islands if original J01's bridges miss the other swept paths.
bm=bmesh.new();bm.from_mesh(parent.data)
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1.e-5)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
bm.to_mesh(parent.data);bm.free()
qa=inspect(parent)
print('J03 fused QA',qa,flush=True)
# A local quantitative preservation check on distant arch/mullion stations:
tree=kdtree.KDTree(len(parent.data.vertices))
for i,v in enumerate(parent.data.vertices):tree.insert(v.co,i)
tree.balance()
per_path={}
for name,vertices in source_xyz.items():
    # 0 drift on surviving source stations expected for exact boolean; intersections can trim vertices.
    residuals=[tree.find(Vector(v))[2] for v in vertices]
    per_path[name]={'max_dist_to_surviving_vertex':round(max(residuals),6),
                    'median_dist_to_surviving_vertex':round(sorted(residuals)[len(residuals)//2],6),
                    'station_vertex_count':len(residuals)}
# Moulding profile corner retention is not the same thing as historical fidelity.
if qa['boundary_edges']==0 and qa['nonmanifold_edges']==0 and qa['connected_components']==1:
    status='PASS_GEOMETRIC'
else:
    status='FAIL_TOPOLOGY'
# Export full model whether pass/fail for diagnostic inspection; label status in QA.
bpy.ops.object.select_all(action='DESELECT')
parent.select_set(True);bpy.context.view_layer.objects.active=parent
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'J03_EXPERIMENTAL_full_exact.glb'),
                          export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,'J03_EXPERIMENTAL_full_exact.glb'))
imported=[o for o in bpy.context.selected_objects if o.type=='MESH']
roundtrip=[]
for ob in imported:
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(ob.data);bm.free()
    roundtrip.append(inspect(ob))
    bpy.data.objects.remove(ob,do_unlink=True)
# Compare against J01 fused fixture (protected, read-only).
j01_glb='/home/christopher/Cathedral_Experiments/tracery_moulding_J01/J01_EXPERIMENTAL_moulding_continuity.glb'
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.import_scene.gltf(filepath=j01_glb)
old=[ob for ob in bpy.context.selected_objects if ob.type=='MESH']
assert len(old)>=1
for o in old:
    o.name='J01 reference voxel';o.location.x=-29.5
# J03 shown side by side against baseline.
parent.name='J03 exact full tracery';parent.location.x=29.5
parent.data.materials.clear();parent.data.materials.append(stone)
for face in parent.data.polygons:face.material_index=0
for o in old:
    o.data.materials.clear();o.data.materials.append(palette[0])
    for f in o.data.polygons:f.material_index=0
def caption(content,x,y,size=2):
    cv=bpy.data.curves.new('caption','FONT');cv.body=content;cv.size=size;cv.align_x='CENTER'
    ob=bpy.data.objects.new('CAPTION '+content,cv);bpy.context.collection.objects.link(ob)
    ob.location=(x,y,1.7);cv.materials.append(label_mat)
caption('J03   /   FULL TRACERY JUNCTION TEST',0,141,2.4)
caption('J01    VOXEL BASELINE',-29.5,133,1.9)
caption('J03    EXACT BOOLEAN',29.5,133,1.9)
caption('13 SWEEP PATHS    |    '+status,0,54,1.6)
# Backdrop and orthographic camera.
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,97,-3))
back=bpy.context.object;back.name='backboard'
back.scale=(64,55,1);back.data.materials.append(background)
world=bpy.context.scene.world or bpy.data.worlds.new('World')
bpy.context.scene.world=world;world.color=(.2,.21,.25)
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.24,.27,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
for name,loc,power,width in [
    ('large softbox',(-43,125,55),1650,70),
    ('fill',(47,101,50),1200,60)]:
    ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=width
    obj=bpy.data.objects.new(name,ld);bpy.context.collection.objects.link(obj)
    obj.location=loc
    obj.rotation_euler=(Vector((0,100,0))-obj.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('ortho review');cam=bpy.data.objects.new('ortho review',cd)
bpy.context.collection.objects.link(cam)
cam.location=(0,100,180);cam.rotation_euler=(0,0,0);cd.type='ORTHO';cd.ortho_scale=142
scene=bpy.context.scene;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=22
scene.render.resolution_x=1500;scene.render.resolution_y=1030;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=os.path.join(ROOT,'J03_FINAL_full_tracery_comparison.png')
scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'J03_EXPERIMENTAL.blend'))
report={'version':'J03','status':status,'blender':bpy.app.version_string,
        'approved_baseline_unchanged':True,'source_dimensions_verified':False,
        'source_provenance':'J01 synthetic 13-path reconstruction; not extracted historical plate arcs',
        'exact_union':qa,'union_steps':ops,'glb_roundtrip':roundtrip,
        'per_path_retention':per_path,
        'architectural_validation':False,'historical_validation':False,
        'structural_validation':False}
with open(os.path.join(ROOT,'J03_QA.json'),'w') as f:json.dump(report,f,indent=2)
bpy.ops.render.render(write_still=True)
print('J03_COMPLETED',json.dumps({'status':status,'exact_union':qa,'glb_roundtrip':roundtrip}),flush=True)
