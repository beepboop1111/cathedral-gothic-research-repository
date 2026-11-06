from pathlib import Path
import bpy,json,math,hashlib,zipfile
D=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(D/'outputs/R18_QUAD_1TO1.glb'))
web=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.name=='QUAD_R18_INDEPENDENT')
v=[web.matrix_world@p.co for p in web.data.vertices]
bounds=[[min(p[i] for p in v),max(p[i] for p in v)] for i in range(3)]
assert abs(bounds[0][0]+1200)<.001 and abs(bounds[0][1]-1200)<.001,bounds
assert abs(bounds[1][0]+1200)<.001 and abs(bounds[1][1]-1200)<.001,bounds
assert abs(bounds[2][0]-3000)<.001 and abs(bounds[2][1]-4319.631011759006)<.001,bounds
assert len(web.data.polygons)==65536
report={'status':'PASS','GLB_imported_in_Blender':bpy.app.version_string,'bounds_native_1to1':bounds,'web_triangles':len(web.data.polygons),
'max_allowed_roundtrip_tolerance_native':.001,'physical_rib_solids':False,'analytic_spring_tangents':'boundary arches and independent groins vertical at spring; does not prove physical joint'}
(D/'qa/R18_GLB_READBACK_QA.json').write_text(json.dumps(report,indent=2))
manifest={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in D.rglob('*') if p.is_file() and p.name not in ('SHA256.json','run.log','verify.log')}
(D/'SHA256.json').write_text(json.dumps(manifest,indent=2))
archive=D.parent/'F5ZP_R18_INDEPENDENT_SKELETON_MATCHED_WEBS_EXPERIMENTAL.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in D.rglob('*'):
  if p.is_file() and p.name not in ('run.log','verify.log'):z.write(p,str(Path(D.name)/p.relative_to(D)))
print(json.dumps(report))
print('ARCHIVE_BYTES',archive.stat().st_size)
