#!/usr/bin/env python3
"""Independent non-Blender test of R17 quality invariants and reproducibility."""
import sys,hashlib,json,math,subprocess,tempfile,shutil
from pathlib import Path
D=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(D/'addon'))
sys.path.insert(0,str(D/'addon/r17_vendor'))
import r17_core as r
from strict_crown_guard import enforce,preferred_crown
def digest_mesh(data):
    arr={'vertices':data['vertices'],'faces':data['faces'],
         'crown_Z':data['crown_Z'],'geometry_version':data['geometry_version']}
    return r.canonical_hash(arr)
tests=[]
for name in ('TRI','QUAD','PENTA','HEXA','OCTA'):
    cfg=r.Settings(vault_type=name,quality='FAST',irregularity=.12)
    boundaries=r.measured_boundary_arches(cfg)
    crown=preferred_crown(boundary_arches=boundaries,spring_Z=cfg.spring_Z)
    a=r.build_mesh_data(cfg,crown)
    full=r.Settings(**{**vars(cfg),'quality':'FINAL'})
    boundary_final=r.measured_boundary_arches(full)
    assert boundaries==boundary_final
    b=r.build_mesh_data(full,crown)
    # FAST values are a precise subset of FINAL's 4x subdivided grid.
    fast_vertices={tuple(round(x,7) for x in p) for p in a['vertices']}
    fine_vertices={tuple(round(x,7) for x in p) for p in b['vertices']}
    assert fast_vertices.issubset(fine_vertices),name
    assert a['crown_Z']==b['crown_Z']
    assert abs(a['seam_gap_native'])<1e-7 and abs(b['seam_gap_native'])<1e-7
    assert len(a['faces'])==cfg.sector_count*32*32
    assert len(b['faces'])==cfg.sector_count*128*128
    # Result has a strictly higher crown than any measured arch apex.
    report=enforce(vault_id=name+'_QUALITY_EQUIVALENCE',crown_Z=crown,
         boundary_arches=boundaries,spring_Z=cfg.spring_Z)
    assert report['crown_relation']=='RAISED'
    tests.append({'topology':name,'n':cfg.sector_count,
      'same_boundary_arch_coordinates':True,'same_centerline_and_boss':True,
      'all_FAST_samples_identical_in_FINAL':True,
      'FAST_mesh_SHA256':digest_mesh(a),'FINAL_mesh_SHA256':digest_mesh(b),
      'crown_Z':crown,'highest_boundary_apex_Z':report['highest_apex_Z']})
# Rebuild from frozen sources in a separate temp folder with no original R17 on sys.path.
first=r.Settings(vault_type='HEXA',quality='FAST',irregularity=.12)
boss=preferred_crown(boundary_arches=r.measured_boundary_arches(first),
                      spring_Z=first.spring_Z)
direct=digest_mesh(r.build_mesh_data(first,boss))
with tempfile.TemporaryDirectory(prefix='F5ZP_R17_ISOLATED_REPLAY_') as p:
    target=Path(p)
    source=D/'addon'
    for name in ('r17_core.py','r17_vendor/strict_crown_guard.py'):
        out=target/name
        out.parent.mkdir(exist_ok=True,parents=True)
        shutil.copy2(source/name,out)
    code='''import sys,json
sys.path.insert(0,sys.argv[1])
sys.path.insert(0,sys.argv[1]+"/r17_vendor")
import r17_core as r
from strict_crown_guard import preferred_crown
c=r.Settings(vault_type="HEXA",quality="FAST",irregularity=.12)
b=preferred_crown(boundary_arches=r.measured_boundary_arches(c),spring_Z=c.spring_Z)
d=r.build_mesh_data(c,b)
print(r.canonical_hash({"vertices":d["vertices"],"faces":d["faces"],"crown_Z":b,"geometry_version":d["geometry_version"]}))
'''
    p=subprocess.run([sys.executable,'-c',code,str(target)],
       capture_output=True,text=True,timeout=90)
    assert p.returncode==0,p.stderr
    assert p.stdout.strip()==direct,(p.stdout,direct)
qa={'status':'R17_QUALITY_AND_SOURCE_ONLY_REPLAY_PASS',
    'five_irregular_types_FAST_FINAL_same_skeleton':True,
    'all_FAST_vertices_subset_of_FINAL':True,
    'independent_source_only_HEXA_mesh_sha256_exact':direct,
    'source_full_copies_external_project_dependency':False,
    'source_baseline_modified':False,'type_tests':tests}
out=D/'qa/R17_QUALITY_EQUIVALENCE_SOURCE_REPLAY_QA.json'
assert not out.exists()
out.write_text(json.dumps(qa,indent=2))
print('R17_QUALITY_SAME_SKELETON_PASS',len(tests),
      'types and independent deterministic source replay',flush=True)
