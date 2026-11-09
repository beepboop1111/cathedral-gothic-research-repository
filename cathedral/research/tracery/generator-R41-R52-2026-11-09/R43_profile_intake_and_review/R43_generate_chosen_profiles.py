"""R43 chosen-profile sections -> actual closed Blender member meshes and GLB."""
import sys,math,json,hashlib
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path('/home/christopher/Cathedral_Research/R43_profile_intake_and_review')
sys.path.insert(0,str(R))
from R43_profile_intake import load_section,area
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.
C=bpy.data.collections.new('R43_CHOOSEN_PROFILES_EXPERIMENTAL')
scene.collection.children.link(C)
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1)
 m.use_nodes=True
 m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1)
 return m
mats=[mat('R43_Profile_A',(.68,.49,.30)),mat('R43_Profile_B',(.56,.65,.71))]
def sweep(name,section,xy_points,mat):
 n=len(section)
 outline=[Vector((u,v,0)) for u,v in section]
 index={(round(p.x,10),round(p.y,10)):i for i,p in enumerate(outline)}
 cap=[]
 for tri in tessellate_polygon([outline]):
  ids=list(tri) if isinstance(tri[0],int) else [index[round(p.x,10),round(p.y,10)] for p in tri]
  if len(set(ids))==3:cap.append(ids)
 assert len(cap)==n-2
 points=[Vector((x,0,z)) for x,z in xy_points]
 rings=[]
 for j,P in enumerate(points):
  t=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized()
  width_axis=Vector((t.z,0,-t.x))
  for u,v in section:
   rings.append(tuple(P+width_axis*u+Vector((0,v,0))))
 faces=[]
 for j in range(len(points)-1):
  off=j*n;nxt=(j+1)*n
  for i in range(n):
   k=(i+1)%n
   faces.extend(((off+i,off+k,nxt+k),(off+i,nxt+k,nxt+i)))
 faces.extend(tuple(reversed(tri)) for tri in cap)
 faces.extend(tuple((len(points)-1)*n+i for i in tri) for tri in cap)
 mesh=bpy.data.meshes.new(name+'_mesh');mesh.from_pydata(rings,[],faces);mesh.update()
 ob=bpy.data.objects.new(name,mesh);C.objects.link(ob)
 mesh.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(mesh)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 vol=bm.calc_volume(signed=True)
 nm=sum(not edge.is_manifold for edge in bm.edges)
 vs=len(bm.verts);nf=len(bm.faces)
 bm.to_mesh(mesh);bm.free();mesh.update()
 assert vol>0 and nm==0
 ob['evidence_class']='SYNTHETIC'
 ob['original_front_rear_scan_available']=False
 return ob,{'object':name,'volume_litres':vol*1000,'vertices':vs,
            'faces':nf,'nonmanifold':nm,'ring_count':len(points)}
allobjects=[];results=[]
for family in (1,2):
 path=R/f'R43_profile_family_{family}.json'
 profile,info=load_section(path)
 for shape in ('straight','curved'):
  line=[]
  for j in range(21 if shape=='curved' else 2):
   t=j/(20 if shape=='curved' else 1)
   line.append(((family-1)*.25+(.032*math.sin(math.pi*t) if shape=='curved' else 0.),.10+.43*t))
  name=f'R43_family_{family}_{shape}'
  ob,qa=sweep(name,profile,line,mats[family-1])
  assert ob['evidence_class']=='SYNTHETIC'
  qa.update(info)
  allobjects.append(ob);results.append(qa)
# All 4 meshes exported; no scene props or representative cathedral geometry.
bpy.ops.object.select_all(action='DESELECT')
for ob in allobjects:ob.select_set(True)
bpy.context.view_layer.objects.active=allobjects[0]
file=R/'R43_INPUT_PROFILE_FAMILIES_4_SOLIDS.glb'
bpy.ops.export_scene.gltf(filepath=str(file),export_format='GLB',
  use_selection=True,export_yup=True,export_apply=True,export_extras=True)
assert file.stat().st_size>20000
report={'checkpoint':'R43','blender':bpy.app.version_string,
 'profiles_loaded':2,'members_generated':len(results),
 'technical_qa':results,
 'profile_evidence':'SYNTHETIC explicit mm sections, two different front/rear profiles',
 'historical_masonry_joint_accepted':False,
 'source_cross_specimen_dimensions_transferred':False,
 'GLB':str(file),'approved_cathedral_geometry_modified':False}
(R/'R43_generated_profile_qa.json').write_text(json.dumps(report,indent=2))
print('R43_3D_PROFILE_PASS',json.dumps(report))
