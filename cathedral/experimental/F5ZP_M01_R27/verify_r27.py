import bpy,json,hashlib,base64,zlib
from pathlib import Path
from mathutils import Vector
from collections import Counter
P=Path('/home/christopher/Desktop/F5ZP_M01_R27_RECEIVERS_EXPERIMENTAL_20261105')
bpy.ops.wm.open_mainfile(filepath=str(P/'F5ZP_M01_R27_B_RECEIVERS_EXPERIMENTAL.blend'),load_ui=False)
q=json.loads((P/'R27_MEASUREMENTS.json').read_text());results={}
for c in bpy.data.collections:
 if c.name.startswith('R27_'):c.hide_viewport=False
for kind in ['ENGAGED','T_PLAN','DETACHED']:
 bpy.ops.object.select_all(action='DESELECT')
 sel=[o for o in bpy.context.scene.objects if o.type=='MESH' and (o.name.startswith('R27_'+kind+'_') or (o.name.startswith('R18_') and ('WALL' in o.name or 'CHEEK' in o.name)) or o.name.startswith('TRIAL_PAD_O_'))]
 expected={}
 for o in sel:
  o.hide_set(False);o.select_set(True)
  expected[o.name]=[[min((o.matrix_world@Vector(p))[i] for p in o.bound_box) for i in range(3)],[max((o.matrix_world@Vector(p))[i] for p in o.bound_box) for i in range(3)]]
 f=P/f'R27_{kind}_LOCAL_CONTEXT.glb'
 bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',use_selection=True,export_extras=True)
 results[kind]={'object_count':len(sel),'expected_bounds':expected,'file_sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
 # Independent empty-scene GLB reopen.
 bpy.ops.object.select_all(action='SELECT')
 # Use a temporary scene, preserving loaded source by reopening before next iteration.
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(f))
 errs=[]
 for o in bpy.context.scene.objects:
  if o.name in expected:
   actual=[[min((o.matrix_world@Vector(p))[i] for p in o.bound_box) for i in range(3)],[max((o.matrix_world@Vector(p))[i] for p in o.bound_box) for i in range(3)]]
   errs.extend(abs(a-b) for row,exp in zip(actual,expected[o.name]) for a,b in zip(row,exp))
 results[kind]['reimport_mesh_count']=sum(o.type=='MESH' for o in bpy.context.scene.objects)
 results[kind]['max_bound_error']=max(errs,default=None)
 assert results[kind]['max_bound_error']<.02
 bpy.ops.wm.open_mainfile(filepath=str(P/'F5ZP_M01_R27_B_RECEIVERS_EXPERIMENTAL.blend'),load_ui=False)
 for c in bpy.data.collections:
  if c.name.startswith('R27_'):c.hide_viewport=False
results['native_reopen_receiver_count']=sum(o.name.startswith('R27_') and o.type=='MESH' for o in bpy.context.scene.objects)
assert results['native_reopen_receiver_count']==18
(P/'R27_INDEPENDENT_QA.json').write_text(json.dumps(results,indent=2))
print('R27_VALIDATION',json.dumps({k:{n:v for n,v in r.items() if n!='expected_bounds'} if isinstance(r,dict) else r for k,r in results.items()}))
