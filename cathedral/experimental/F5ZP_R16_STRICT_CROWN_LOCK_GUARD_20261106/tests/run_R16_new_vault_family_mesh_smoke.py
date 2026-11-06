#!/usr/bin/env python3
"""Build isolated analytical SAMPLE meshes for new 3-, 5-, 8-sector types.

Not cathedral proposals! Verify actual R16 guarded pre/post generation,
file exports, lock hashes and crown rise on distinct future topologies.
"""
from pathlib import Path
import hashlib,json,math,sys,numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from guarded_vault_adapter import guarded_build,source_lock_snapshot
from strict_crown_guard import CrownBelowArchApex,save_report

SAMPLES=257
SPRING=3000.
APEX_Z=4250.
BOSS=4400.
CAP=4700.
ORIGIN=(0.,0.)
def make_arches(n):
    """Gothic test petals: boundary arch apices 4250, boss 4400."""
    R=620.
    results=[]
    for k in range(n):
        a=2*math.pi*k/n;b=2*math.pi*(k+1)/n
        corner0=np.array([R*math.cos(a),R*math.sin(a)])
        corner1=np.array([R*math.cos(b),R*math.sin(b)])
        arr=[]
        for u in np.linspace(0,1,SAMPLES):
            xy=(1-u)*corner0+u*corner1
            height=SPRING+(APEX_Z-SPRING)*math.sin(math.pi*u)
            arr.append([float(xy[0]),float(xy[1]),float(height)])
        results.append({'id':f'synthetic_{n}_arch_{k:02d}',
                        'points_xyz':arr})
    return results

def build_mesh(arches):
    """Continuous conical test surface from exact pointed arches to boss.
    This is an integration smoke test, NOT a reconstructed Gothic vault."""
    verts=[[0.,0.,BOSS]]
    tris=[]
    for k,arch in enumerate(arches):
        idx=[]
        for p in arch['points_xyz']:
            idx.append(len(verts));verts.append(p)
        for j in range(len(idx)-1):
            tris.append([0,idx[j],idx[j+1]])
    mesh=trimesh.Trimesh(vertices=np.asarray(verts),
                       faces=np.asarray(tris),process=True)
    if not mesh.is_winding_consistent:
        trimesh.repair.fix_normals(mesh)
    assert mesh.is_winding_consistent and not mesh.is_watertight
    assert mesh.euler_number==1
    return mesh

def main():
    sources=[ROOT/'reference/vault_generator.py',
             ROOT/'reference/gothic_kernel_source.py']
    basehash=source_lock_snapshot(sources)
    summary=[]
    for n in (3,5,8):
        arches=make_arches(n)
        lock={'arch_curves_SHA256':hashlib.sha256(
                 json.dumps(arches,sort_keys=True).encode()).hexdigest(),
              'model_units':'native 1:1',
              'protect':'all submitted boundary arches and locations'}
        destination=ROOT/'outputs'/f'SYNTHETIC_{n}_SECTOR_GUARD_TEST'
        def builder(arch=arches,locked=lock):
            mesh=build_mesh(arch)
            return {'mesh':mesh,'crown_Z':BOSS,
                  'boundary_arches':arch,'web_peak_Z':float(mesh.bounds[1,2]),
                  'locks':locked}
        out=guarded_build(name=f'R16_TEST_{n}_SECTOR',
             boundary_arches=arches,crown_Z=BOSS,
             spring_Z=SPRING,cap_Z=CAP,crown_locked=False,
             source_paths=sources,build_in_memory_fn=builder,
             locked_baseline_fn=lambda x=lock:x,
             output_dir=destination)
        post=out['postbuild']
        assert post['crown_relation']=='RAISED'
        assert post['arch_count']==n
        assert post['crown_above_apex_native'] if 'crown_above_apex_native' in post else post['rise_above_apex_native']==150
        assert post['locked_snapshot_hash_verified']
        assert post['cap_clearance_native']==300.
        assert 'LOCKED_GEOMETRY_WARNING_ALWAYS' in post['warning_codes']
        assert len(list(destination.glob('*.stl')))==1
        assert len(list(destination.glob('*.glb')))==1
        summary.append({'topology':'SYNTHETIC_ONLY','sectors':n,
           'crown_Z':post['crown_Z'],'highest_apex_Z':post['highest_apex_Z'],
           'rise_above_apex':post['rise_above_apex_native'],
           'export_folder':str(destination),
           'prebuild_passed':True,'postbuild_passed':True,
           'lock_report_included':True})
    # Prove bad geometry does not even enter the builder callback.
    called=[]
    def forbidden():
        called.append('DID_BUILD');raise AssertionError('MUST_NOT_BUILD')
    try:
        guarded_build(name='R16_TEST_BELOW_APEX_DO_NOT_BUILD',
          boundary_arches=make_arches(5),crown_Z=4249.0,
          spring_Z=SPRING,cap_Z=CAP,crown_locked=True,
          source_paths=sources,build_in_memory_fn=forbidden,
          output_dir=ROOT/'outputs/SYNTHETIC_REJECTED_NEVER_WRITTEN')
    except CrownBelowArchApex:
        assert not called
    else:raise AssertionError('Did not stop below-apex build')
    assert not (ROOT/'outputs/SYNTHETIC_REJECTED_NEVER_WRITTEN').exists()
    assert basehash==source_lock_snapshot(sources)
    report={'status':'PASS_R16_STRICT_CROWN_GUARDED_REAL_EXPORT_3_5_8_SECTOR_FAMILIES',
       'synthetic_vault_types_only':True,'all_existing_cathedral_sources_unchanged':True,
       'proposals_are_not_architectural_designs':True,
       'source_sha256_originals':basehash,
       'below_apex_candidate_rejected_before_build':True,
       'new_family_tests':summary}
    save_report(ROOT/'qa/R16_GUARDED_NEW_FAMILY_MESH_TEST_QA.json',report)
    print('R16_FULL_PRE_AND_POST_GUARD_GENERATION_PASS',
          len(summary),'distinct new topologies; rejected low crown prior build')
if __name__=='__main__':main()
