# J05 Blender GLB roundtrip, quantified source-vertex retention, and single review image
import bpy,bmesh,os,json,numpy as np
from mathutils import Vector,kdtree
ROOT='/home/christopher/Cathedral_Experiments/tracery_moulding_J05'
source=open('/home/christopher/Cathedral_Experiments/tracery_moulding_J01/generate_J01.py').read()
exec(source[:source.index('paths=[]')],globals())
exec(source[source.index('def inspect(ob):'):source.index('for o in parts:')],globals())
ROOT='/home/christopher/Cathedral_Experiments/tracery_moulding_J05'
raw=np.load(ROOT+'/union_13.npz')
verts=np.asarray(raw['vertices'],dtype=float)
triangles=np.asarray(raw['triangles'],dtype=int)
mesh=bpy.data.meshes.new('J05 robust full tracery geometry')
mesh.from_pydata(verts.tolist(),[],triangles.tolist());mesh.update()
obj=bpy.data.objects.new('J05 manifold3d full-window union',mesh)
bpy.context.collection.objects.link(obj)
qa=inspect(obj)
assert qa['connected_components']==1 and qa['nonmanifold_edges']==0 and qa['boundary_edges']==0,qa
# Calculate source member survival: exact vertex retention outside clipped intersections.
tree=kdtree.KDTree(len(verts))
for i,v in enumerate(verts):tree.insert(Vector(v),i)
tree.balance()
names=json.load(open(ROOT+'/paths.json'))
member_retention=[]
for i,name in enumerate(names):
    inp=np.load(ROOT+f'/path_{i:02d}.npz')
    d=[tree.find(Vector(p))[2] for p in inp['vertices']]
    n1=sum(x<=1e-4 for x in d);n2=sum(x<=0.002 for x in d)
    member_retention.append({'name':name,'input_vertices':len(d),
         'exact_source_vertices_retained':n1,'within_0_002':n2,
         'max_removed_or_trimmed_distance':round(max(d),4)})
# Check reference distant stems where no merges occur.
distant={}
for i in [0,1,2,3,4,5]:
    arr=np.load(ROOT+f'/path_{i:02d}.npz')['vertices']
    test=arr[arr[:,1]<70]
    if len(test):
        ds=[tree.find(Vector(p))[2] for p in test]
        distant[names[i]]={'sample_count':len(ds),'max_vertex_drift':max(ds)}
# Export the experimental solid, then round-trip and weld glTF's duplicated seam vertices.
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True);bpy.context.view_layer.objects.active=obj
glb=ROOT+'/J05_EXPERIMENTAL_full_tracery.glb'
bpy.ops.export_scene.gltf(filepath=glb,export_format='GLB',
                          use_selection=True,export_apply=True)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.import_scene.gltf(filepath=glb)
reimports=[o for o in bpy.context.selected_objects if o.type=='MESH']
roundtrip=[]
for o in reimports:
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(o.data);bm.free()
    roundtrip.append(inspect(o))
    bpy.data.objects.remove(o,do_unlink=True)
assert len(roundtrip)==1 and roundtrip[0]['boundary_edges']==0
assert roundtrip[0]['nonmanifold_edges']==0 and roundtrip[0]['connected_components']==1
# J01 reference for visual comparison; leave file untouched.
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.import_scene.gltf(filepath='/home/christopher/Cathedral_Experiments/tracery_moulding_J01/J01_EXPERIMENTAL_moulding_continuity.glb')
reference=[o for o in bpy.context.selected_objects if o.type=='MESH']
assert reference
for o in reference:
    o.location.x=-29.5
    o.data.materials.clear();o.data.materials.append(palette[0])
    for face in o.data.polygons:face.material_index=0
obj.location.x=29.5
obj.data.materials.clear();obj.data.materials.append(stone)
for f in obj.data.polygons:f.material_index=0
def caption(string,x,y,size):
    cr=bpy.data.curves.new('caption','FONT');cr.body=string
    cr.size=size;cr.align_x='CENTER'
    ob=bpy.data.objects.new('caption '+string,cr)
    bpy.context.collection.objects.link(ob);ob.location=(x,y,1.5)
    ob.data.materials.append(label_mat)
caption('J05  |  FULL TWO-LANCET TRACERY   /   ROBUST GEOMETRIC UNION',0,140,2.2)
caption('J01  /  GLOBAL VOXEL REMESH',-29.5,133,1.8)
caption('J05  /  PROFILE-PRESERVING BOOLEAN',29.5,133,1.8)
caption('CONNECTED: 1     |     OPEN EDGES: 0     |     NONMANIFOLD: 0',0,55,1.45)
caption('EXPERIMENTAL ARCHITECTURE   /   ORIGINAL WINDOW GEOMETRY UNCHANGED',0,51,1.15)
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,99,-3.5))
back=bpy.context.object;back.scale=(65,58,1);back.data.materials.append(background)
world=bpy.context.scene.world or bpy.data.worlds.new('World');bpy.context.scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.20,.23,.27,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
for name,location,energy,width in [('softbox',(-45,127,60),1800,70),('fill',(45,100,60),1250,60)]:
    light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.shape='DISK';light.size=width
    l=bpy.data.objects.new(name,light);bpy.context.collection.objects.link(l)
    l.location=location;l.rotation_euler=(Vector((0,99,0))-l.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('orthographic');cam=bpy.data.objects.new('orthographic',cd)
bpy.context.collection.objects.link(cam);cam.location=(0,98,180);cam.rotation_euler=(0,0,0)
cd.type='ORTHO';cd.ortho_scale=144
sc=bpy.context.scene;sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=20
sc.render.resolution_x=1536;sc.render.resolution_y=1060
sc.render.image_settings.file_format='PNG'
sc.render.filepath=ROOT+'/J05_FINAL_profile_union_comparison.png'
sc.view_settings.view_transform='AgX'
report={'status':'PASS_GEOMETRIC','blender':bpy.app.version_string,
  'reference':'J01 synthetic unverified-scale window head',
  'approved_geometry_modified':False,'kernel':'manifold3d 3.5.4',
  'input_count':len(names),'mesh':qa,'glb_roundtrip':roundtrip,
  'per_member_retention':member_retention,'unmodified_stem_samples':distant,
  'voxel_remeshing_used':False,'historical_validation':False,
  'architectural_validation':False,'structural_validation':False}
with open(ROOT+'/J05_QA.json','w') as f:json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/J05_EXPERIMENTAL.blend')
bpy.ops.render.render(write_still=True)
print('J05_PASS',json.dumps({'mesh':qa,'roundtrip':roundtrip,'distant':distant}),flush=True)
