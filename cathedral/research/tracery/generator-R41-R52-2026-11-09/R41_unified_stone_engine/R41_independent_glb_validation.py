"""R41 independent GLB import/mesh seam/volume verification, Blender 5.0.1--5.2.2."""
from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
ROOT=Path('/home/christopher/Cathedral_Research/R41_unified_stone_engine')
qa=json.loads((ROOT/'R41_generator_qa.json').read_text())
expected=next(q for q in qa['cases'] if q['spec']['curvature_mm']==26. and q['spec']['taper_pct']==7. and q['spec']['joint_deg']==22.5)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'R41_Curved_Tapered_Two_Stone_Experiment.glb'))
obj=sorted([ob for ob in bpy.context.scene.objects if ob.type=='MESH'],key=lambda x:x.name)
assert len(obj)==2,('wrong imported object count',len(obj))
shared=[]
volumes=[]
info=[]
for ob in obj:
 bm=bmesh.new();bm.from_mesh(ob.data)
 raw=len(bm.verts)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 nonman=sum(not e.is_manifold for e in bm.edges)
 vol=bm.calc_volume(signed=True)
 verts={(round((ob.matrix_world@v.co).x,7),round((ob.matrix_world@v.co).y,7),round((ob.matrix_world@v.co).z,7)) for v in bm.verts}
 assert nonman==0 and abs(vol)>0 and len(bm.verts)==484
 shared.append(verts)
 volumes.append(abs(vol))
 info.append({'name':ob.name,'raw_vertices':raw,'welded_vertices':len(bm.verts),'nonmanifold':nonman,'volume_litres':abs(vol)*1000})
 bm.free()
intersection=shared[0].intersection(shared[1])
assert len(intersection)==242,('shared seam vertices fail',len(intersection))
# Check seam face triangles share exactly the same surface despite GLTF vertex splits.
contactareas=[]
normals=[]
for ob in obj:
 bm=bmesh.new();bm.from_mesh(ob.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 area=0.;n=Vector();nf=0
 for f in bm.faces:
  keys={(round((ob.matrix_world@v.co).x,7),round((ob.matrix_world@v.co).y,7),round((ob.matrix_world@v.co).z,7)) for v in f.verts}
  if keys.issubset(intersection):
   area+=f.calc_area();n+=f.normal*f.calc_area();nf+=1
 assert nf>=200,('too few seam facets',ob.name,nf)
 contactareas.append(area);normals.append(n.normalized())
 bm.free()
assert abs(contactareas[0]-contactareas[1])<1e-9
normal_dot=normals[0].dot(normals[1])
assert abs(normal_dot+1)<1e-5,('contact face normal mismatch',normal_dot)
assert abs(contactareas[0]*1e6-expected['contact_area_mm2'])<.05
combined=sum(volumes)
print('R41_VOLUME_DIAG',combined,expected['combined_volume_m3'],[float(v) for v in volumes],expected['objects'],flush=True)
assert abs(combined-expected['combined_volume_m3'])<1e-8
assert all(abs(volumes[i]-expected['objects'][i]['volume_m3'])<1e-8 for i in range(2))
report={'importer':bpy.app.version_string,'test':'independent GLB roundtrip of curved/tapered 2-block experiment',
    'technical_pass':True,'GLB_mesh_objects':len(obj),
    'original_vertices_shared':len(intersection),
    'contact_area_mm2':contactareas[0]*1e6,
    'contact_normals_dot':normal_dot,
    'volume_sum_litres':combined*1000,
    'reference_volume_litres':expected['combined_volume_m3']*1000,
    'objects':info,
    'source_historical_authentication':False}
target=ROOT/('R41_GLb_roundtrip_'+bpy.app.version_string.split()[0].replace('.','_')+'.json')
target.write_text(json.dumps(report,indent=2))
print('R41_IMPORT_PASS',json.dumps(report))
