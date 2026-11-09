import bpy,bmesh,json,hashlib,subprocess,os
from pathlib import Path
from mathutils import Vector
R=Path('/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL')
O=R/'M04_P08_B523_REAR_AND_COURSE_EVIDENCE_EXPERIMENTAL'
assert not O.exists(),'Never overwrite'
O.mkdir()
SRC=R/'M04_P07_R03_B523_3D_SOURCE_CONTACT_DIAGNOSTICS_EXPERIMENTAL/M04_P07_B523_FIVE_GOTHIC_BEARINGS_PLUS_SOURCE_DIAGNOSTICS_EXPERIMENTAL.blend'
REF=Path('/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend')
SOURCE=R/'M04_P03_R02B_CANONICAL_SPRINGER_AND_BEARING_MASONRY_EXPERIMENTAL/R03_TEN_PROTECTED_PIER_ARCH_AND_BEARING_MASONRY_REFERENCES.glb'
protected=[SRC,REF,SOURCE]
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
assert bpy.app.version[:3]==(5,2,3),bpy.app.version_string
bpy.ops.wm.open_mainfile(filepath=str(SRC))
physical=[o for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('P07_DIAGNOSTIC')]
assert len(physical)==14
def signature(o):
 return hashlib.sha256(repr(([(tuple(v.co)) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[tuple(r) for r in o.matrix_world])).encode()).hexdigest()
sig={o.name:signature(o) for o in physical}
def bounds(o):
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]
 return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
base={o.name:bounds(o) for o in physical}
payload={}
for o in physical:
 o.data.calc_loop_triangles()
 payload[o.name]={'v':[list(o.matrix_world@v.co) for v in o.data.vertices],'f':[list(t.vertices) for t in o.data.loop_triangles]}
(O/'physical_mesh_evidence.json').write_text(json.dumps(payload))
analysis=r"""
import json,sys
from pathlib import Path
import numpy as np,trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
O=Path(sys.argv[1]);S=Path(sys.argv[2])
data=json.loads((O/'physical_mesh_evidence.json').read_text())
meshes={n:trimesh.Trimesh(vertices=d['v'],faces=d['f'],process=False) for n,d in data.items()}
courses=sorted((n for n in meshes if 'RESTORED_COURSE_' in n))
assert len(courses)==5
def cap(m,z):
 t=m.vertices[m.faces];t=t[np.all(abs(t[:,:,2]-z)<.002,axis=1)]
 return unary_union([Polygon(a[:,:2]) for a in t if Polygon(a[:,:2]).area>1e-8])
beds=[]
for i in range(4):
 z=1920+120*i;a=cap(meshes[courses[i]],z);b=cap(meshes[courses[i+1]],z)
 assert a.area>1 and b.area>1
 beds.append(dict(z=z,lower_top_area=a.area,upper_bottom_area=b.area,contact_area=a.intersection(b).area,upper_bearing_fraction=a.intersection(b).area/b.area,lower_exposed_area=a.difference(b).area,upper_overhang_area=b.difference(a).area,symmetric_difference_area=a.symmetric_difference(b).area))
sc=trimesh.load(str(S),force='scene',process=False)
wall=None
for n in sc.graph.nodes_geometry:
 T,k=sc.graph[n]
 if 'RECEIVING_S_UPPER_0' in n:
  wall=sc.geometry[k].copy();wall.apply_transform(T);v=wall.vertices.copy();wall.vertices=np.c_[v[:,0],-v[:,2],v[:,1]]
assert wall is not None
def section(m,z):
 s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
 if s is None:return Polygon()
 polys=[]
 for p in s.discrete:
  if len(p)>3 and np.linalg.norm(p[0]-p[-1])<.01:
   q=Polygon(p[:,:2]);q=q if q.is_valid else q.buffer(0)
   polys.append(q)
 return unary_union(polys)
rear=[]
for i,n in enumerate(courses):
 for dz in [1,30,60,90,119]:
  z=1800+i*120+dz;a=section(meshes[n],z);w=section(wall,z)
  rear.append(dict(course=i+1,z=z,source_wall_area=w.area,course_wall_overlap_area=a.intersection(w).area,course_outside_source_wall_area=a.difference(w).area))
qa=dict(exact_internal_beds=beds,source_rear_sections=rear,physical_watertight={n:bool(m.is_watertight) for n,m in meshes.items()},interpretation='Original wall overlaps recovered springer envelope below Z2400. Overlap is replacement coordination evidence, not rear keying or bonding. No source-proven separate backing stone recovered.',architectural='HOLD: rear bond and stone subdivision not proven',historical='HOLD: source geometry does not establish historic joint or construction sequence; F5ZL-C schedule absent from handoff',structural='HOLD: contact area alone does not verify thrust, eccentricity, bed shear, mortar or stone strength')
(O/'independent_geometry_qa.json').write_text(json.dumps(qa,indent=2))
print(json.dumps(qa))
"""
result=subprocess.run(['/usr/bin/python3','-c',analysis,str(O),str(SOURCE)],capture_output=True,text=True)
(O/'analysis.log').write_text(result.stdout+result.stderr)
assert result.returncode==0,result.stderr
qa=json.loads((O/'independent_geometry_qa.json').read_text())
assert all(qa['physical_watertight'].values())
# Expose exact existing horizontal beds as separate analytical sheets, never stone.
col=bpy.data.collections.new('P08_INTERNAL_BED_SURFACES_NON_MASONRY')
bpy.context.scene.collection.children.link(col)
added=[]
courses=sorted([o for o in physical if 'RESTORED_COURSE_' in o.name],key=lambda o:o.name)
mat=bpy.data.materials.new('P08 analytical course beds NOT STONE');mat.diffuse_color=(.1,.65,.85,1)
for i,o in enumerate(courses[:-1]):
 z=1920+120*i;verts=[];faces=[]
 for t in o.data.loop_triangles:
  pts=[o.matrix_world@o.data.vertices[j].co for j in t.vertices]
  if all(abs(p.z-z)<.002 for p in pts):
   j=len(verts);verts.extend([list(p) for p in pts]);faces.append((j,j+1,j+2))
 assert faces
 me=bpy.data.meshes.new('P08_BED_DATA');me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new('P08_NON_MASONRY_EXACT_BED_Z'+str(z),me);col.objects.link(ob);me.materials.append(mat)
 ob['status']='Zero thickness exact source top bed; no inferred joint or structural approval';added.append(ob)
sc=bpy.context.scene
sc['P08_REAR_CONNECTION']='UNRESOLVED: no source proven separate backing, no speculative masonry'
sc['P08_APPROVAL']='TECHNICAL CHECKS ONLY; architectural historical structural HOLD'
allmesh=[o for o in bpy.data.objects if o.type=='MESH']
assert len(allmesh)==25
blend=O/'F5ZP_M04_P08_B523_REAR_COURSE_EVIDENCE_EXPERIMENTAL.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
roundtrips={}
desktop=Path('/home/christopher/Desktop')
outputs=[]
for label,objects in [('CLEAN_SOURCE_14_MESHES',physical),('DIAGNOSTIC_25_MESHES_NON_MASONRY_OVERLAYS',allmesh)]:
 path=desktop/('F5ZP_M04_P08_B523_'+label+'_EXPERIMENTAL.glb')
 assert not path.exists(),str(path)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True)
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path))
 imported=[ob for ob in bpy.data.objects if ob not in before and ob.type=='MESH']
 assert len(imported)==len(objects)
 # Name-independent global bounds comparison for each exported object.
 errors=[]
 for original in objects:
  target=min(imported,key=lambda ob:sum(abs(bounds(ob)[k][j]-bounds(original)[k][j]) for k in range(2) for j in range(3)))
  errors.append(max(abs(bounds(target)[k][j]-bounds(original)[k][j]) for k in range(2) for j in range(3)))
 assert max(errors)<.02,errors
 roundtrips[label]={'mesh_count':len(imported),'max_native_bounds_error':max(errors)}
 for ob in imported:bpy.data.objects.remove(ob,do_unlink=True)
 outputs.append(str(path))
assert all(signature(o)==sig[o.name] for o in physical)
# Exactly one new PNG; original physical source geometry, analytical overlays hidden.
for ob in allmesh:
 if ob not in physical:ob.hide_render=True
cam=sc.camera;cam.location=Vector((31830,-190,3120))
cam.rotation_euler=(Vector((31000,-1280,2220))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=1660;cam.data.clip_end=30000
sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.color_type='MATERIAL'
sc.display.shading.show_cavity=True;sc.display.shading.show_shadows=True
sc.render.resolution_x=1360;sc.render.resolution_y=1120;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.filepath=str(O/'F5ZP_M04_P08_ONE_REVIEW.png')
bpy.ops.render.render(write_still=True)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in protected)
report={'Blender':bpy.app.version_string,'technical':'PASS','physical_meshes_preserved':14,'new_stone_solids':0,'new_diagnostic_bed_surfaces':4,'existing_P07_diagnostic_surfaces':7,'GLB_roundtrips':roundtrips,'protected_file_sha256_unchanged':sha,'source_mesh_signatures':sig,'independent_geometry':qa,'Desktop_GLBs':outputs,'review_PNG':sc.render.filepath}
(O/'P08_FINAL_REPORT.json').write_text(json.dumps(report,indent=2))
(O/'P08_HANDOFF.md').write_text('# M04 P08 experimental course and rear audit\n\n14 physical meshes preserved. Four exact internal bed diagnostic surfaces added to seven P07 overlays; all 11 are NON-MASONRY. No backing invented.\n\nOriginal source wall overlap below Z2400 identifies envelope coordination, not a construction bond. Rear keying and bed shear remain unresolved; historic course subdivision and F5ZL-C schedule need evidence. No architectural, historical or structural approval.\n\nSee P08_FINAL_REPORT.json for independent bed contact areas, 25 rear sections, watertight checks, GLB roundtrips and preserved hashes.\n')
print('P08_COMPLETE',json.dumps({'outputs':outputs,'beds':qa['exact_internal_beds'],'roundtrip':roundtrips}),flush=True)
