"""Independent GLB roundtrip for two selectable front/rear profile families."""
import bpy,bmesh,json
from pathlib import Path
R=Path('/home/christopher/Cathedral_Research/R43_profile_intake_and_review')
source=json.loads((R/'R43_generated_profile_qa.json').read_text())
expected={item['object']:item for item in source['technical_qa']}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'R43_INPUT_PROFILE_FAMILIES_4_SOLIDS.glb'))
objs=[ob for ob in bpy.context.scene.objects if ob.type=='MESH']
assert len(objs)==4
got=[]
for ob in objs:
 tag=ob.name
 assert tag in expected,('unexpected object',tag)
 bm=bmesh.new();bm.from_mesh(ob.data)
 raw=len(bm.verts)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 bad=sum(not e.is_manifold for e in bm.edges)
 n=len(bm.verts)
 vol=abs(bm.calc_volume(signed=True))*1000
 exp=expected[tag]
 assert n==exp['vertices'],(tag,'vertex mismatch',n,exp['vertices'])
 assert bad==0,(tag,'nonmanifold',bad)
 assert abs(vol-exp['volume_litres'])<.0001,(tag,'volume drift',vol,exp['volume_litres'])
 got.append({'object':tag,'raw_vertices':raw,'welded_vertices':n,
    'volume_litres':vol,'nonmanifold_after_weld':bad,'PASS':True})
 bm.free()
report={'checkpoint':'R43','blender_importer':bpy.app.version_string,
 'meshes':len(got),'roundtrip':'PASS','profiles_distinct':len(set(x['source_sha256'] for x in source['technical_qa']))==2,
 'source_historical_joint_verified':False,'objects':got}
out=R/('R43_roundtrip_'+bpy.app.version_string.split()[0].replace('.','_')+'.json')
out.write_text(json.dumps(report,indent=2))
print('R43_ROUNDTRIP_PASS',json.dumps(report))
