import bpy,sys,json,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import network_workspace as nw
sc=bpy.context.scene
nw.register(sc)
assert len(sc.network_vaults)==15
def hashes():
 return {o.name:nw.digest([tuple(v.co) for v in o.data.vertices]) for o in sc.objects if o.name.startswith('WEB_')}
before=hashes()
z=sc.network_vaults[0].crown
nw.BUSY=True
sc.network_vaults[0].crown=z+35
nw.BUSY=False
valid=nw.build(sc,nw.inputs(sc),sc.network_divisions)
assert valid['generated_webs']==['V01'] and len(valid['reused_webs'])==14,valid['generated_webs']
nw.BUSY=True
sc.network_vaults[0].crown=z
nw.BUSY=False
nw.build(sc,nw.inputs(sc),sc.network_divisions)
assert hashes()==before
sc.network_vaults[0].crown=-1
assert bpy.app.timers.is_registered(nw.timer)
bpy.app.timers.unregister(nw.timer)
nw.timer()
assert 'REJECTED' in sc['network_status'] and hashes()==before
nw.BUSY=True
sc.network_vaults[0].crown=z
nw.BUSY=False
sc['network_status']='WEBS_VALIDATED'
tmp=bpy.data.scenes.new('GLB_READBACK')
bpy.context.window.scene=tmp
bpy.ops.import_scene.gltf(filepath=str(ROOT/'V19_R02_15_VAULTS_1TO1.glb'))
metrics={}
for vid in json.loads(sc['network_config'])['vaults']:
 a=sc.objects['WEB_'+vid]
 b=next(o for o in tmp.objects if o.name.startswith('WEB_'+vid))
 av=[a.matrix_world@v.co for v in a.data.vertices]; bv=[b.matrix_world@v.co for v in b.data.vertices]
 err=max(abs(fn(v[i] for v in av)-fn(v[i] for v in bv)) for i in range(3) for fn in (min,max))
 pts={tuple(round(x,3) for x in v) for v in bv}
 missing=sum(tuple(round(x,3) for x in v) not in pts for v in av)
 assert err<.002 and missing==0 and len(a.data.polygons)==len(b.data.polygons),(vid,err,missing)
 metrics[vid]=dict(bounds_error=err,missing_vertex_positions=missing,triangles=len(b.data.polygons))
bpy.context.window.scene=sc
for ob in list(tmp.objects):
 data=ob.data; bpy.data.objects.remove(ob,do_unlink=True)
 if isinstance(data,bpy.types.Mesh) and data.users==0:bpy.data.meshes.remove(data)
bpy.data.scenes.remove(tmp)
assert hashes()==before and nw.protected()
qa=json.loads((ROOT/'NUMERICAL_QA.json').read_text())
qa['regression']['UI_crown_edit_reused_14_unaffected_webs']=True
bpy.data.texts['network_workspace.py'].clear(); bpy.data.texts['network_workspace.py'].write((ROOT/'network_workspace.py').read_text())
bpy.data.texts['RUN_NETWORK_UI.py'].clear(); bpy.data.texts['RUN_NETWORK_UI.py'].write('import bpy,sys\nsys.path.insert(0,'+repr(str(ROOT))+')\nimport network_workspace as nw\nnw.register(bpy.context.scene)\n')
qa['fresh_session']=dict(loaded_all_15_webs=True,sidebar_registered=True,automatic_update_callback_scheduled=True,automatic_rejection_kept_last_valid_meshes=True,GLB_readback=metrics,saved_geometry_not_regenerated=True,protected_hashes_unchanged=True)
(ROOT/'NUMERICAL_QA.json').write_text(json.dumps(qa,indent=2)); sc['network_QA']=json.dumps(qa)
# Avoid retaining a redundant backup of this unapproved candidate.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'V19_R02_NETWORK_EXPERIMENTAL.blend'),compress=True)
print('FRESH_SESSION_EXPORT_PASS',json.dumps(dict(webs=len(metrics),max_bounds_error=max(v['bounds_error'] for v in metrics.values()),geometry_not_regenerated=True)),flush=True)
