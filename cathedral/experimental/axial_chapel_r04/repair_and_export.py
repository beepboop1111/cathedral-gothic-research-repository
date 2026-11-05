"""Create R04 from the saved R03 mesh, without rebuilding the architecture.
Run: blender -b -t 4 --python repair_and_export.py -- /path/to/R03.blend
"""
import bpy,bmesh,numpy as np,collections,json,pathlib,hashlib,math,sys,ast
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if not args:raise SystemExit('Pass the preserved R03 .blend after --')
source=pathlib.Path(args[0]).resolve();source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
def cyclic(face):
 f=tuple(face);return min(f[i:]+f[:i] for i in range(len(f)))
def unoriented(face):return min(cyclic(face),cyclic(tuple(reversed(face))))
def digest(data):return hashlib.sha256(data).hexdigest()
def snapshot(o):
 me=o.data;vs=np.array([v.co[:] for v in me.vertices],dtype=np.float32)
 faces=[unoriented(p.vertices) for p in me.polygons]
 return {'vertices_sha256':digest(vs.tobytes()),'faces_unoriented_sha256':digest(json.dumps(faces).encode()),'vertices':len(vs),'faces':len(faces),'matrix_world':[list(row) for row in o.matrix_world],'materials':[m.name if m else None for m in me.materials],'smooth_flags_sha256':digest(bytes(p.use_smooth for p in me.polygons)),'collections':sorted(c.name for c in o.users_collection),'bounds':[vs.min(0).tolist(),vs.max(0).tolist()]}
def topology(o):
 bm=bmesh.new();bm.from_mesh(o.data)
 result={'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_nonboundary_edges':sum(not e.is_manifold and not e.is_boundary for e in bm.edges),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True)}
 bm.free();return result
objects={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
before={name:snapshot(o) for name,o in objects.items()}
targets=sorted(set(o.name for g in ['WEBS','ROOF'] for o in bpy.data.collections[g].objects if o.type=='MESH'))
assert len(targets)==33 and len(objects)==253
# Evaluate the corrected procedural shell function in isolation on every saved shell.
module=ast.parse((R/'build_chapel_r04.py').read_text());fn=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='shell')
def capture(name,vertices,faces,*_):return np.array(vertices),faces
ns={'np':np,'collections':collections,'Z':np.array([0.,0.,1.]),'thickness':45.,'mesh':capture}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'build_chapel_r04.py:shell','exec'),ns)
repairs=[]
for name in targets:
 o=objects[name];me=o.data;nv=len(me.vertices)//2
 verts=np.array([v.co[:] for v in me.vertices],dtype=float)
 tris=[tuple(reversed(p.vertices[:])) for p in me.polygons if all(i<nv for i in p.vertices)]
 expected_verts,expected_faces=ns['shell'](name,verts[:nv],tris)
 fixture_rounding=float(np.max(np.abs(expected_verts-verts)))
 assert fixture_rounding<0.001,('saved float32 sheet offset recovery exceeds tolerance',name,fixture_rounding)
 expected={unoriented(f):cyclic(f) for f in expected_faces}
 assert len(expected)==len(me.polygons)
 pre=topology(o);flipped=0
 for p in me.polygons:
  desired=expected[unoriented(p.vertices)]
  if cyclic(p.vertices)!=desired:
   assert cyclic(tuple(reversed(p.vertices)))==desired
   p.flip();flipped+=1
 me.update();post=topology(o)
 assert post['inconsistent_winding_edges']==0 and post['boundary_edges']==0 and post['nonmanifold_nonboundary_edges']==0 and post['signed_volume']>0,(name,post)
 assert snapshot(o)==before[name],('saved geometry/property changed',name)
 assert all(cyclic(p.vertices)==expected[unoriented(p.vertices)] for p in me.polygons)
 repairs.append({'name':name,'flipped_faces':flipped,'before':pre,'after':post,'corrected_generator_matches_saved_shell':True,'recovered_sheet_offset_rounding_max_native':fixture_rounding})
after={name:snapshot(o) for name,o in objects.items()}
assert before==after
parent_qa=json.loads((R/'inputs/R03/QA.json').read_text())
qa={'status':'EXPERIMENTAL_R04_NOT_APPROVED','scope':'Only shell polygon orientation changed in saved R03; missing exports restored.','blender_version':bpy.app.version_string,'source_blend_sha256':source_hash,'governance_blob':'1d7e358ff7562fcc64088854baa2abd3d31a729e','source_mesh_count':len(objects),'shell_repairs':repairs,'preservation':{'every_object_vertex_array_identical':all(before[n]['vertices_sha256']==after[n]['vertices_sha256'] for n in before),'every_face_membership_identical':all(before[n]['faces_unoriented_sha256']==after[n]['faces_unoriented_sha256'] for n in before),'all_object_snapshots_identical_except_face_orientation':before==after,'source_plan_sha256':digest((R/'inputs/BASELINE.json').read_bytes()),'profile_sha256':digest((R/'PROFILES.json').read_bytes()),'dimension_csv_sha256':digest((R/'DIMENSIONS.csv').read_bytes())},'retained_R03_parameters':parent_qa['parameters'],'prior_R03_checks_not_rerun':parent_qa['checks'],'checks':{},'exports':{},'limitations':parent_qa['limitations']}
qa['checks'].update({'all_33_shells_closed_consistently_wound_outward':all(x['after']['inconsistent_winding_edges']==0 and x['after']['signed_volume']>0 for x in repairs),'corrected_shell_function_matches_all_33_saved_shells':True,'all_253_object_geometry_property_snapshots_retained':before==after,'all_coordinates_finite':all(math.isfinite(c) for o in objects.values() for v in o.data.vertices for c in v.co),'no_degenerate_polygon_faces':all(topology(o)['degenerate_faces']==0 for o in objects.values())})
# Re-measure retained entrance on actual corrected saved geometry.
o=objects['ENTRANCE_ORDER_1'];n=len(o.data.vertices)//97;rows=np.array([list(o.matrix_world@v.co) for v in o.data.vertices]).reshape((97,n,3))
qa['entrance_measured']={'clear_width':float(rows[-1,:,1].min()-rows[0,:,1].max()),'spring_z':float(rows[0,:,2].min()),'soffit_crown_z':float(rows[48,:,2].min()),'back_crown_z':float(rows[48,:,2].max())}
qa['checks']['retained_entrance_dimensions']=qa['entrance_measured']['clear_width']==2200 and qa['entrance_measured']['spring_z']==1800 and qa['entrance_measured']['soffit_crown_z']==3750
scene=bpy.context.scene;scene['status']=qa['status'];scene['R04_parent_blend_sha256']=source_hash;scene['R04_scope']='shell winding repair only; no architectural change'
# Matched previews use the original R03 camera definitions and studio settings.
cam=scene.camera;original_camera=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.type,cam.data.ortho_scale)
shading=(scene.display.shading.show_shadows,scene.display.shading.show_cavity)
def render(name,pos,target,scale=None,cut=False):
 scene.display.shading.show_shadows=name!='INTERIOR';scene.display.shading.show_cavity=name!='INTERIOR'
 for o in objects.values():o.hide_render=False
 if cut:
  for o in bpy.data.collections['ROOF'].objects:o.hide_render=True
  for o in bpy.data.collections['WALLS'].objects:
   if o.name.startswith(('SIDE_-1','THRESHOLD_RETURN_-1')):o.hide_render=True
  for o in bpy.data.collections['WEBS'].objects:
   if o.name.endswith('_WEB_0') or o.name in ['AMB_WEB_0','AMB_WEB_FRONT_S','BAY1_WEB_1','BAY2_WEB_1','APSE_WEB_0','APSE_WEB_1','APSE_WEB_2']:o.hide_render=True
 cam.data.type='ORTHO' if scale else 'PERSP'
 if scale:cam.data.ortho_scale=scale
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
render('CUTAWAY',(37700,-10700,7900),(30100,0,1900),14000,True)
render('INTERIOR',(26000,0,1550),(34000,0,2600))
render('EXTERIOR',(39700,-11700,10500),(30500,0,2000),15000)
for o in objects.values():o.hide_render=False
cam.location,cam.rotation_euler,cam.data.type,cam.data.ortho_scale=original_camera
scene.display.shading.show_shadows,scene.display.shading.show_cavity=shading
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Axial_Chapel_R04_EXPERIMENTAL.blend'))
# Oriented world-space triangle fingerprints verify more than mesh counts/bounds.
def triangle_signature(o):
 me=o.data;me.calc_loop_triangles();verts=np.array([o.matrix_world@v.co for v in me.vertices],dtype=float)
 ids=np.array([t.vertices[:] for t in me.loop_triangles],dtype=int);tris=np.rint(verts[ids]*1000).astype(np.int64)
 # Rotate each oriented triangle so its lexicographically smallest vertex is first.
 out=[]
 for t in tris:
  k=min(range(3),key=lambda j:tuple(t[j]));out.append(np.roll(t,-k,axis=0).reshape(9))
 arr=np.array(out,dtype=np.int64);order=np.lexsort(tuple(arr[:,i] for i in range(8,-1,-1)))
 return {'triangle_count':len(arr),'oriented_triangle_geometry_sha256_quantized_0_001':digest(arr[order].tobytes()),'bounds':[verts.min(0).tolist(),verts.max(0).tolist()]}
sigs={name:triangle_signature(o) for name,o in objects.items()}
exports=[('FULL',set(objects)),('ROOF_OFF',set(objects)-set(o.name for o in bpy.data.collections['ROOF'].objects))]
for label,names in exports:
 bpy.ops.object.select_all(action='DESELECT')
 for name in names:objects[name].select_set(True)
 bpy.context.view_layer.objects.active=objects[next(iter(sorted(names)))]
 path=R/('Axial_Chapel_R04_'+label+'.glb')
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True)
 qa['exports'][label]={'file':path.name,'mesh_count':len(names),'source_names':sorted(names),'sha256':digest(path.read_bytes())}
# Verify saved .blend itself reopens with the same geometry and repaired orientations.
bpy.ops.wm.open_mainfile(filepath=str(R/'Axial_Chapel_R04_EXPERIMENTAL.blend'))
reopened={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
assert {n:snapshot(o) for n,o in reopened.items()}==before
qa['checks']['R04_blend_reopened_geometry_retained']=True
qa['checks']['R04_blend_reopened_shell_orientation_retained']=all(topology(reopened[n])['inconsistent_winding_edges']==0 and topology(reopened[n])['signed_volume']>0 for n in targets)
for label,names in exports:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=str(R/qa['exports'][label]['file']))
 imported={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
 assert set(imported)==names,(label,'name mismatch',set(imported)^names)
 mismatch=[];max_error=0.
 for name,o in imported.items():
  sig=triangle_signature(o);ref=sigs[name]
  max_error=max(max_error,float(np.max(np.abs(np.array(sig['bounds'])-np.array(ref['bounds'])))))
  if sig['triangle_count']!=ref['triangle_count'] or sig['oriented_triangle_geometry_sha256_quantized_0_001']!=ref['oriented_triangle_geometry_sha256_quantized_0_001']:mismatch.append(name)
 assert not mismatch,(label,'triangle mismatch',mismatch)
 assert max_error<0.001,(label,'bounds',max_error)
 relevant=set(targets)&names
 top={n:topology(imported[n]) for n in relevant}
 assert all(t['inconsistent_winding_edges']==0 and t['boundary_edges']==0 and t['nonmanifold_nonboundary_edges']==0 and t['signed_volume']>0 for t in top.values()),(label,'shell export topology',top)
 qa['exports'][label].update({'reimport_mesh_count':len(imported),'world_bounds_error_max':max_error,'oriented_triangle_signatures_match_all_meshes':not mismatch,'shell_topology_after_reimport':top})
 qa['checks'][label+'_reimport_counts_names_oriented_geometry_match']=True
 qa['checks'][label+'_shells_closed_consistently_wound_outward']=True
 qa['checks'][label+'_bounds_within_0_001_native']=max_error<0.001
 if label=='ROOF_OFF':qa['checks']['roof_off_contains_no_roof_objects']=not any(n.startswith('ROOF_') for n in imported)
qa['checks']['source_R03_blend_unchanged']=digest(source.read_bytes())==source_hash
assert all(qa['checks'].values()),qa['checks']
(R/'QA_R04.json').write_text(json.dumps(qa,indent=2))
(R/'GEOMETRY_REGRESSION.json').write_text(json.dumps({'comparison':'R03 versus R04; hashes exclude winding only','before':before,'after':after},indent=2))
print('R04 COMPLETE:',sum(qa['checks'].values()),'/',len(qa['checks']),'checks passed; winding edges',sum(x['before']['inconsistent_winding_edges'] for x in repairs),'->',sum(x['after']['inconsistent_winding_edges'] for x in repairs))
