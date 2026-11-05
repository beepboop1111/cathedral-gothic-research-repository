# M01 rib connections R02 — EXPERIMENTAL

Source: MR COMPUTER Desktop/F5ZP_M01_RIB_RECOVERY_R01_EXPERIMENTAL/F5ZP_RIB_ONLY_R21_WITH_MIDDLE_REFERENCE_R01_EXPERIMENTAL.blend
Source SHA256: 0176b6fc8e43fd1e352da0776ab3baab9ed084cce9e16c7dbedce9c346a7355e

Output directory: /home/christopher/Desktop/F5ZP_M01_RIB_CONNECTIONS_R02_EXPERIMENTAL (adjacent ZIP contains full native package).

35 experimental curves corrected at 42 spring ends using local cubic transitions. All endpoint displacements zero. 64 unaffected object geometry signatures matched during build. Native METRIC scale_length=1 retained. Independent Blender 5.0.1 reopen: maximum vertical tangent and transition join angle errors 0 degrees at stored precision; transition derivatives nonzero and vertical motion monotonic at 101 samples per transition. GLB reimport: 92 named meshes, finite vertices. Source file hash unchanged.

Not visually reviewed. No historical circular-arc, web fit, masonry bearing or structural validation claimed. F5ZL-C missing support schedule unresolved. M01 OPEN. No approved architecture or generator replaced.

## Build script
```python
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
src=Path('/home/christopher/Desktop/F5ZP_M01_RIB_RECOVERY_R01_EXPERIMENTAL/F5ZP_RIB_ONLY_R21_WITH_MIDDLE_REFERENCE_R01_EXPERIMENTAL.blend')
out=Path('/home/christopher/Desktop/F5ZP_M01_RIB_CONNECTIONS_R02_EXPERIMENTAL')
out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(src))
def signature(o):
 d={'matrix':[list(r) for r in o.matrix_world],'type':o.type}
 if o.type=='CURVE':
  d['bevel']=[o.data.bevel_depth,o.data.bevel_resolution]
  d['splines']=[[[*p.co] for p in s.points] for s in o.data.splines]
 elif o.type=='MESH': d['verts']=[list(v.co) for v in o.data.vertices];d['faces']=[list(p.vertices) for p in o.data.polygons]
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
before={o.name:signature(o) for o in bpy.data.objects}
rows=[]
targets=[o for o in bpy.data.objects if o.name.startswith(('R21_OGIVE_','R21_INWARD_ARCH_'))]
for o in targets:
 s=o.data.splines[0]
 pts=[p.co.xyz.copy() for p in s.points]
 # Replace only first/last eight original segments with cubic transitions.
 k=8; both=o.name.startswith('R21_INWARD_ARCH_')
 ids=[0]+list(range(k,len(pts)-k if both else len(pts)))+([len(pts)-1] if both else [])
 q=[pts[i] for i in ids]
 old=o.data
 data=old.copy();data.splines.clear()
 ns=data.splines.new('BEZIER');ns.bezier_points.add(len(q)-1)
 for i,p in enumerate(ns.bezier_points):
  p.co=q[i];p.handle_left_type='FREE';p.handle_right_type='FREE'
  p.handle_left=q[i]-(q[i]-q[max(0,i-1)])/3
  p.handle_right=q[i]+(q[min(len(q)-1,i+1)]-q[i])/3
 zlocal=o.matrix_world.to_3x3().inverted() @ Vector((0,0,1))
 zlocal.normalize()
 a,b=ns.bezier_points[:2]; length=(q[1]-q[0]).length
 a.handle_right=a.co+zlocal*length/3
 b.handle_left=b.co-(pts[k+1]-pts[k]).normalized()*length/3
 if both:
  a,b=ns.bezier_points[-2:];length=(q[-1]-q[-2]).length
  a.handle_right=a.co+(pts[-k-1]-pts[-k-2]).normalized()*length/3
  b.handle_left=b.co+zlocal*length/3
 data.resolution_u=12;data.use_fill_caps=True;o.data=data
 angle=math.degrees((o.matrix_world.to_3x3()@(pts[1]-pts[0])).angle(Vector((0,0,1))))
 assert (ns.bezier_points[0].co-pts[0]).length==0 and (ns.bezier_points[-1].co-pts[-1]).length==0
 rows.append({'name':o.name,'spring_angle_before_deg':angle,'spring_angle_after_deg':0,'endpoints_displacement':0,'unchanged_original_samples':len(ids)-2,'local_transition_original_segments':k})
protected={n:h for n,h in before.items() if n not in {o.name for o in targets}}
assert all(signature(bpy.data.objects[n])==h for n,h in protected.items())
qa={'status':'EXPERIMENTAL_GEOMETRIC_SPRING_TANGENT_CORRECTION','source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'changed_curves':len(rows),'corrected_spring_ends':42,'unchanged_objects':len(protected),'source_scale_length':bpy.context.scene.unit_settings.scale_length,'rows':rows,'limitations':['Local cubic transitions are experimental, not historical circular-arc reconstruction.','Existing crown and boss paths preserved.','Web interfaces not repaired by this rib-only change.','F5ZL-C receiving faces missing; masonry and structural validation unresolved.']}
(out/'QA.json').write_text(json.dumps(qa,indent=2))
(out/'protected_signatures.json').write_text(json.dumps(protected))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'F5ZP_RIB_CONNECTIONS_R02_EXPERIMENTAL.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in {'CURVE','MESH'}:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'F5ZP_RIB_CONNECTIONS_R02_EXPERIMENTAL.glb'),export_format='GLB',use_selection=True)
print('REPAIR_RESULT',json.dumps({k:v for k,v in qa.items() if k!='rows'}))

```

## Independent validation
```python
import bpy,json,math,hashlib,shutil,zipfile
from pathlib import Path
from mathutils import Vector
root=Path('/home/christopher/Desktop/F5ZP_M01_RIB_CONNECTIONS_R02_EXPERIMENTAL')
qa=json.loads((root/'QA.json').read_text())
bpy.ops.wm.open_mainfile(filepath=qa['source'])
def coords(o):
 return [o.matrix_world@p.co.xyz for p in o.data.splines[0].points]
original={o.name:coords(o) for o in bpy.data.objects if o.type=='CURVE'}
bpy.ops.wm.open_mainfile(filepath=str(root/'F5ZP_RIB_CONNECTIONS_R02_EXPERIMENTAL.blend'))
errors=[]; angles=[]; joins=[]; deviations=[]
for r in qa['rows']:
 o=bpy.data.objects[r['name']];p=o.data.splines[0].bezier_points;old=original[o.name]
 errors.extend([(o.matrix_world@p[0].co-old[0]).length,(o.matrix_world@p[-1].co-old[-1]).length])
 ends=[(p[0].handle_right-p[0].co,Vector((0,0,1)))]
 segs=[(p[0],p[1])]
 joins.append((p[1].co-p[1].handle_left).angle(p[1].handle_right-p[1].co))
 if 'INWARD_ARCH' in o.name:
  ends.append((p[-1].co-p[-1].handle_left,Vector((0,0,-1))))
  segs.append((p[-2],p[-1]))
  joins.append((p[-2].co-p[-2].handle_left).angle(p[-2].handle_right-p[-2].co))
 for d,z in ends:angles.append(math.degrees((o.matrix_world.to_3x3()@d).angle(z)))
 for a,b in segs:
  for j in range(101):
   t=j/100
   der=3*(1-t)**2*(a.handle_right-a.co)+6*(1-t)*t*(b.handle_left-a.handle_right)+3*t*t*(b.co-b.handle_left)
   assert der.length>0
   assert der.z*(b.co.z-a.co.z)>0
assert max(errors)<0.001 and max(angles)<0.01 and max(joins)<0.005
expected={o.name for o in bpy.context.scene.objects if o.type in {'CURVE','MESH'}}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(root/'F5ZP_RIB_CONNECTIONS_R02_EXPERIMENTAL.glb'))
actual={o.name for o in bpy.context.scene.objects if o.type=='MESH'}
assert actual==expected,(len(actual),len(expected))
assert all(math.isfinite(c) for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices for c in v.co)
result={'reopened_blend':True,'spring_tangents_checked':len(angles),'max_vertical_tangent_error_deg':max(angles),'max_endpoint_displacement':max(errors),'max_transition_join_angle_deg':math.degrees(max(joins)),'transition_samples_monotonic':True,'glb_reimport_meshes':len(actual),'finite_export_coordinates':True,'visual_inspection':'not performed','source_hash_unchanged':hashlib.sha256(Path(qa['source']).read_bytes()).hexdigest()==qa['source_sha256']}
(root/'INDEPENDENT_QA.json').write_text(json.dumps(result,indent=2))
shutil.copy2('/home/christopher/Desktop/f5zp_fix_rib_connections_r02.py',root/'build.py')
shutil.copy2(__file__,root/'validate.py')
(root/'README.md').write_text('# Rib connections R02 — EXPERIMENTAL\n\n35 experimental curves receive 42 vertical springing tangents with local cubic transitions. All endpoints retained; 64 other objects unchanged during build. F5ZN-A reference unchanged. Native scale 1.0 retained. Crown junctions preserved.\n\nRun Blender background with build.py, then validate.py. See QA.json and INDEPENDENT_QA.json. This repairs rib spring tangents only; webs, masonry bearings, historical profiles and structural adequacy remain unresolved. No visual review yet. M01 OPEN.\n')
with zipfile.ZipFile(root.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for f in root.iterdir():
  if f.is_file():z.write(f,f.name)
print('INDEPENDENT_QA',json.dumps(result))

```
