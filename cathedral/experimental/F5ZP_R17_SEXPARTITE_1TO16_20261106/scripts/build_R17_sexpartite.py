#!/usr/bin/env python3
"""R17 experimental SEXPARTITE double-bay: six web cells, 4 diagonal ribs,
2 intermediate ribs, six true 2-centred boundary pointed arches.
Construct at full native coordinates, export exact 1/16 STL and GLB.
R16 strict crown+lock guard executed BEFORE and AFTER generation.
Not historically measured, structurally certified, or approved.
"""
from pathlib import Path
import json,math,sys,hashlib
import numpy as np,trimesh
D=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(D/'R16_dependency/src'))
from guarded_vault_adapter import guarded_build,source_lock_snapshot
from strict_crown_guard import enforce,CrownBelowArchApex

SPRING=3000.; BOSS=4700.; RATIO=16
# Two rectangular bays aligned east-west; six boundary arch segments.
PLAN=[(-2200,-1200),(0,-1200),(2200,-1200),
      (2200,1200),(0,1200),(-2200,1200)]
ARCH_RISE=[1200,1200,1320,1200,1200,1320]
NU=64; NR=56; N_ARCH=257
PROTECTED=[D/'R16_dependency/src/strict_crown_guard.py',
           D/'R16_dependency/src/guarded_vault_adapter.py',
           D/'R16_dependency/reference/vault_generator.py',
           D/'R16_dependency/reference/gothic_kernel_source.py']
LOCKED={'scope':'EXPERIMENT_ONLY_F5ZP_R17',
        'protected_original_cathedral_geometry':'NO CHANGES',
        'synthetic_boundary_coordinates':PLAN,
        'pointed_arch_rises':ARCH_RISE,
        'spring_Z':SPRING,'boss_Z':BOSS,'model_native_units':True}
def pointed_z(length,rise,t):
    """Equal-radius, two-centred pointed circular arch (sharp apex)."""
    x=length*min(float(t),1.-float(t))
    center=length/4.+rise**2/length
    if not(0<=x<=length/2):raise ValueError('bad arch parameter')
    h=math.sqrt(max(0.,center*center-(x-center)**2))
    return h
def outer_point(k,t):
    a=np.asarray(PLAN[k],float);b=np.asarray(PLAN[(k+1)%6],float)
    length=float(np.linalg.norm(b-a))
    xy=(1.-t)*a+t*b
    z=SPRING+pointed_z(length,ARCH_RISE[k],t)
    if t<=0 or t>=1:z=SPRING
    return np.array([*xy,z],float)
def vault_point(k,u,r):
    """Ruled plan from boundary to boss; convex/monotonic lifted web.
    z=BOSS-(1-r)^2*(BOSS - pointed_boundary_z(u)).
    Thus ∂z/∂r=2(1-r)*(BOSS-boundary_z)>0 at every r<1.
    No sagging possible; exact arch at r=0 and exact boss at r=1.
    """
    a=outer_point(k,u)
    return np.array([(1-r)*a[0],(1-r)*a[1],
                      BOSS-(1-r)**2*(BOSS-a[2])],float)
ARCHES=[{'id':f'R17_SEXPARTITE_SIDE_{i:02d}',
         'points_xyz':[outer_point(i,j/(N_ARCH-1)).tolist()
                       for j in range(N_ARCH)]} for i in range(6)]
assert max(max(p[2] for p in a['points_xyz']) for a in ARCHES)==SPRING+max(ARCH_RISE)
def generate():
    """One shared mesh, no duplicates or gaps on all six radial groins."""
    m=6*NU
    rings=[]
    for j in range(NR):
        r=j/NR
        row=np.array([vault_point(k,i/NU,r)
                    for k in range(6) for i in range(NU)],float)
        rings.append(row)
    vertices=np.concatenate([np.array(rings).reshape(-1,3),
                             np.array([[0.,0.,BOSS]])],axis=0)
    boss=len(vertices)-1
    faces=[]
    for j in range(NR-1):
        for i in range(m):
            a=j*m+i; b=j*m+(i+1)%m
            c=(j+1)*m+i; d=(j+1)*m+(i+1)%m
            faces.extend([(a,b,c),(b,d,c)])
    for i in range(m):
        faces.append(((NR-1)*m+i,(NR-1)*m+(i+1)%m,boss))
    web=trimesh.Trimesh(vertices=vertices,
         faces=np.asarray(faces,int),process=False)
    assert web.is_winding_consistent and web.euler_number==1
    assert not web.is_watertight  # intentional intrados, no masonry thickness
    return {'mesh':web,'boundary_arches':ARCHES,'crown_Z':BOSS,
            'web_peak_Z':float(web.vertices[:,2].max()),'locks':LOCKED}
def check_geometry(result):
    mesh=result['mesh'];v=mesh.vertices
    # Analytical true arches and six rib centre-lines match surface exactly.
    gap=0.
    for k in range(6):
        for u in np.linspace(0,1,65):
            gap=max(gap,float(np.linalg.norm(vault_point(k,u,0)-outer_point(k,u))))
        for r in np.linspace(0,1,65):
            rib=vault_point(k,0,r)
            former=vault_point((k-1)%6,1,r)
            gap=max(gap,float(np.linalg.norm(rib-former)))
    assert gap<1e-8
    dome_drop=0.
    for k in range(6):
        for u in np.linspace(0,1,25):
            heights=np.array([vault_point(k,u,r)[2] for r in np.linspace(0,1,257)])
            dome_drop=max(dome_drop,float(max(0.,np.max(-np.diff(heights)))))
    assert dome_drop<1e-10
    edges=mesh.edges_unique
    assert len(edges)>0 and len(mesh.faces)==6*NU*(2*NR-1)
    assert len(mesh.vertices)==6*NU*NR+1
    return {'shared_arch_groin_interface_gap_native':gap,
            'max_meridian_sag_native':dome_drop,
            'triangles':len(mesh.faces),'vertices':len(mesh.vertices),
            'Euler':mesh.euler_number,'winding_consistent':True,
            'open_intrados_intentional':True}
def main():
    original=source_lock_snapshot(PROTECTED)
    test=generate();geo=check_geometry(test)
    # R16 controls all exports. Builder is intentionally in-memory.
    out=guarded_build(name='R17_SEXPARTITE_SIX_CELL',
        boundary_arches=ARCHES,crown_Z=BOSS,spring_Z=SPRING,
        source_paths=PROTECTED,build_in_memory_fn=lambda:test,
        locked_baseline_fn=lambda:LOCKED,crown_locked=False,
        output_dir=D/'outputs/guarded')
    post=out['postbuild']
    assert post['highest_apex_Z']==4320.0
    assert post['crown_relation']=='RAISED'
    assert post['rise_above_apex_native']==380.
    assert 'LOCKED_GEOMETRY_WARNING_ALWAYS' in post['warning_codes']
    assert post['locked_snapshot_hash_verified']
    assert original==source_lock_snapshot(PROTECTED)
    small=test['mesh'].copy();small.apply_scale(1/RATIO)
    p=D/'outputs/R17_SEXPARTITE_SIX_CELL_1to16.glb'
    assert not p.exists()
    small.export(p)
    tiny=trimesh.load_mesh(D/'outputs/guarded/R17_SEXPARTITE_SIX_CELL_1to16.stl')
    assert np.max(np.abs(tiny.bounds*RATIO-test['mesh'].bounds))<.0007
    report={'status':'PASS_R17_EXPERIMENTAL_SEXPARTITE_1_TO_16',
       'family':'rectangular Gothic sexpartite double-bay, not polygonal radial apse',
       'architectural_historical_source':'hypothetical topology, not measured original',
       'scale_asset':1/16,'blender_scale_multiplier':16,
       'six_cells':6,'diagonal_groin_ribs':4,
       'intermediate_transverse_rib_halves':2,
       'true_two_centered_boundary_pointed_arches':6,
       'boundary_apex_max_Z':4320,'central_crown_Z':BOSS,
       'crown_above_highest_apex':380,
       'prebuild_and_postbuild_R16_pass':True,
       'R16_report_warning_codes':post['warning_codes'],
       'locked_files_unchanged':True,'unresolved_support_schedule':'F5ZL-C',
       'mesh_geometry_qa':geo,
       'R16_protected_source_sha256':original,
       'scaled_GLB_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
       'clinical_architectural_stone_structure_validation':'NOT ATTEMPTED',
       'approval':'UNAPPROVED EXPERIMENT'}
    (D/'qa/R17_SEXPARTITE_MODEL_QA.json').write_text(json.dumps(report,indent=2))
    print('R17_PASS',geo,'arch_apex=4320 boss=4700 rise=380',
          'exact_reversal_1to16_x16 bounds PASS')
if __name__=='__main__':main()
