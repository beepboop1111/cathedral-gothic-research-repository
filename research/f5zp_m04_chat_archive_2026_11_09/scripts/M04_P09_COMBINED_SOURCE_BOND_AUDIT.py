import bpy,json,hashlib,os,re
from pathlib import Path
from mathutils import Vector
R=Path('/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL')
E=Path('/home/christopher/Documents/Cathedral/experimental')
O=R/'M04_P09_B523_SOURCE_BOND_PROVENANCE_EXPERIMENTAL'
assert not O.exists()
O.mkdir()
roots=[Path('/home/christopher/Documents/Cathedral'),Path('/home/christopher/Downloads'),Path('/home/christopher/Cathedral_Research')]
hits=[];named=[];errors=[];count=0
for root in roots:
 for d,ds,fs in os.walk(root,onerror=lambda e:errors.append(str(e))):
  ds[:]=[s for s in ds if s not in ['.git','node_modules','runtime','venv','.venv','__pycache__'] and Path(d)/s!=O]
  for n in fs:
   f=Path(d)/n
   if 'F5ZL' in n.upper():named.append(str(f))
   if f.suffix.lower() not in ['.md','.txt','.json','.csv','.py','.yaml','.yml']:continue
   try:
    if f.stat().st_size>3000000:continue
    count+=1
    for line_no,line in enumerate(f.read_text(errors='replace').splitlines(),1):
     if re.search(r'F5ZL[-_ ]?C',line,re.I):
      hits.append({'file':str(f),'line':line_no,'excerpt':line[:700]})
   except OSError as e:errors.append(str(e))
search={'roots':list(map(str,roots)),'text_files_scanned':count,'filename_hits':named,'F5ZL_C_text_references':hits,'errors':errors,'limits':'Excluded runtime, caches and text files over 3 MB; archives, PDFs and images not content-searched. References are not an authenticated schedule.'}
(O/'P09_SCHEDULE_SEARCH.json').write_text(json.dumps(search,indent=2))
source_files=[E/'WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend',E/'WALL_PIER_JUNCTION_R03/prepare_junction.py',E/'WALL_PIER_JUNCTION_R03/PLAN.json',E/'SPRINGER_WORKFLOW_R14/CHECKPOINT.md',E/'SPRINGER_JUNCTION_R15/CHECKPOINT.md',R/'M04_P08_B523_REAR_AND_COURSE_EVIDENCE_EXPERIMENTAL/F5ZP_M04_P08_B523_REAR_COURSE_EVIDENCE_EXPERIMENTAL.blend']
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
plan=json.loads(source_files[2].read_text())
code=source_files[1].read_text()
assert "('UPPER',target,1800,4100)" in code
bpy.ops.wm.open_mainfile(filepath=str(source_files[0]))
inventory=[]
for ob in bpy.data.objects:
 if ob.type!='MESH' or not ob.name.startswith('RECEIVING_S_'):continue
 pts=[ob.matrix_world@v.co for v in ob.data.vertices]
 zs=sorted(set(round(v.z,4) for v in pts))
 inventory.append({'name':ob.name,'vertices':len(pts),'faces':len(ob.data.polygons),'unique_vertex_Z':zs,'custom_properties':{k:str(ob[k]) for k in ob.keys()}})
upper=[a for a in inventory if a['name']=='RECEIVING_S_UPPER_0']
assert len(upper)==1 and upper[0]['unique_vertex_Z']==[1800.0,4100.0],upper
(O/'P09_ORIGINAL_RECEIVING_OBJECT_INVENTORY.json').write_text(json.dumps(inventory,indent=2))
# Carry forward the validated assembly unchanged. No speculative reconstruction.
bpy.ops.wm.open_mainfile(filepath=str(source_files[-1]))
meshes=[ob for ob in bpy.data.objects if ob.type=='MESH']
physical=[ob for ob in meshes if ob.name.startswith('P06_')]
assert len(physical)==14 and len(meshes)==25
def sig(ob):
 return hashlib.sha256(repr(([tuple(v.co) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],[tuple(r) for r in ob.matrix_world])).encode()).hexdigest()
signatures={o.name:sig(o) for o in physical}
def bounds(o):
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]
 return [min(p[k] for p in pts) for k in range(3)]+[max(p[k] for p in pts) for k in range(3)]
roundtrips={}
for label,obs in [('CLEAN_SOURCE_14_MESHES',physical),('DIAGNOSTIC_25_MESHES_NON_MASONRY',meshes)]:
 path=Path('/home/christopher/Desktop')/('F5ZP_M04_P09_B523_'+label+'_EXPERIMENTAL.glb')
 assert not path.exists()
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True)
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path))
 new=[ob for ob in bpy.data.objects if ob not in before and ob.type=='MESH']
 assert len(new)==len(obs)
 remaining=list(new);errs=[]
 for ob in obs:
  target=min(remaining,key=lambda q:max(abs(a-b) for a,b in zip(bounds(ob),bounds(q))))
  errs.append(max(abs(a-b) for a,b in zip(bounds(ob),bounds(target))));remaining.remove(target)
 assert max(errs)<.02
 roundtrips[str(path)]={'objects':len(new),'max_bounds_error':max(errs)}
 for ob in new:bpy.data.objects.remove(ob,do_unlink=True)
assert all(sig(ob)==signatures[ob.name] for ob in physical)
sc=bpy.context.scene
sc['P09_FINDING']='R03 upper wall is continuous extrusion Z1800-4100, not a stone bonding schedule. No source-proven rear key recovered.'
sc['P09_STATUS']='TECHNICAL PASS / ARCHITECTURAL HISTORICAL STRUCTURAL UNRESOLVED'
for ob in meshes:ob.hide_render=ob not in physical
cam=sc.camera;cam.location=Vector((31850,-2450,2850))
cam.rotation_euler=(Vector((31000,-1370,2220))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=1600
sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1360;sc.render.resolution_y=1120
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
sc.render.filepath=str(O/'F5ZP_M04_P09_ONE_REAR_REVIEW.png')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'F5ZP_M04_P09_SOURCE_BOND_AUDIT_EXPERIMENTAL.blend'))
bpy.ops.render.render(write_still=True)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in source_files)
report={'technical':{'Blender':bpy.app.version_string,'source_files_unchanged':sha,'physical_meshes_unchanged':14,'new_masonry':0,'GLB_roundtrips':roundtrips,'new_PNG_count':len(list(O.glob('*.png')))},'geometric':{'original_R03_receiving_upper':upper[0],'R03_generator_layers':plan['config']['layers'],'P08_internal_beds':'Preserved; previously measured >=99.9999968% bearing. Not repeated as a new result.'},'architectural':{'status':'UNRESOLVED','finding':'No original stone-level rear key, header or staggered joint established by continuous receiving extrusion. No backing solid justified.'},'historical':{'status':'UNRESOLVED','finding':'Procedural experimental geometry is not historical construction evidence. No authenticated F5ZL-C schedule recovered in bounded search; see search inventory.'},'structural':{'status':'UNRESOLVED','missing_inputs':['SI scale','stone and mortar properties','arch thrust and load cases','resultant eccentricities','rear bond geometry','bed shear resistance'],'capacity_calculated':False},'search_summary':{'text_files':count,'filename_hits':len(named),'text_references':len(hits),'errors':errors}}
assert report['technical']['new_PNG_count']==1
(O/'P09_FINAL_REPORT.json').write_text(json.dumps(report,indent=2))
(O/'P09_HANDOFF.md').write_text('# M04 P09 source bond provenance\n\nThe original R03 RECEIVING_S_UPPER_0 has vertex elevations only 1800 and 4100. prepare_junction.py explicitly extrudes the upper target over that interval. This is envelope geometry, not an individual-stone bond record. R14/R15 checkpoint text explicitly leaves F5ZL-C and historical/structural validation unresolved.\n\nNo source-proven rear key or authentic support schedule recovered in the bounded filename/text search. Search coverage and all references are in P09_SCHEDULE_SEARCH.json; archives and image/PDF contents remain outside this search.\n\nNo new masonry. P08 assembly carried forward unchanged, two newly named Desktop GLBs reimported, one rear review PNG rendered. Architectural/historical/structural status remains unresolved. Next required evidence: dimensioned construction section and stone schedule, physical unit scale, load/material data.\n')
print('P09_COMPLETE',json.dumps(report),flush=True)
