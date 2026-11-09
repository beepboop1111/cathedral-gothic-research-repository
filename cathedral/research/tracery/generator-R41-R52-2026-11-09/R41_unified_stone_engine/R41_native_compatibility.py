"""R41 smoke: execute the actual modular generator natively in Blender 5.1.2 and 5.2.2."""
import sys,json,math,bpy
from pathlib import Path
R=Path('/home/christopher/Cathedral_Research/R41_unified_stone_engine')
sys.path.insert(0,str(R))
from R41_engine import StoneSpec,read_ayr_r32_profile,build_pair
P=R.parent
profile,prov=read_ayr_r32_profile(P/'R32/R32_section_trace_samples.csv',P/'R32/R32_measurements_and_evidence.json')
bpy.ops.wm.read_factory_settings(use_empty=True)
c=bpy.data.collections.new('R41_native_smoke_EXPERIMENT_ONLY');bpy.context.scene.collection.children.link(c)
qa=[]
for i,spec in enumerate((StoneSpec('BASE',joint_deg=22.5),StoneSpec('CURVED',joint_deg=22.5,curvature_mm=26,taper_pct=7))):
 pair,report=build_pair(profile,prov,spec,c)
 assert report['contact_seam_linear_gap_m']==0
 assert all(o['nonmanifold']==0 for o in report['objects'])
 qa.append(report)
 for ob in pair:bpy.data.objects.remove(ob,do_unlink=True)
assert abs(qa[0]['contact_area_mm2']-22631.85246)<.05
expected=json.loads((R/'R41_generator_qa.json').read_text())
match=next(q for q in expected['cases'] if q['spec']['joint_deg']==22.5 and q['spec']['curvature_mm']==26 and q['spec']['taper_pct']==7)
assert abs(match['combined_volume_m3']-qa[1]['combined_volume_m3'])<1e-8
out={'version':bpy.app.version_string,'engine_source':'R41_engine.py','base_regression':'PASS',
     'curved_and_tapered_regression':'PASS','volume_match_R41_baseline_m3':abs(match['combined_volume_m3']-qa[1]['combined_volume_m3']),
     'contact_area_mm2':qa[1]['contact_area_mm2'],'mesh_manifold':True,
     'source_class':'EXPERIMENTAL_2D_SURVEY','source_3d_authenticated':False}
target=R/('R41_native_generator_'+bpy.app.version_string.split()[0].replace('.','_')+'.json')
target.write_text(json.dumps(out,indent=2))
print('R41_NATIVE_GENERATOR_PASS',json.dumps(out))
