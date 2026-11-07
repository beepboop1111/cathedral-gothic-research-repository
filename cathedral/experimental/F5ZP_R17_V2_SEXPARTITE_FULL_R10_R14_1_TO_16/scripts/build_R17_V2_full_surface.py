#!/usr/bin/env python3
"""R17 V2: R09 triangular skeleton + R10 cubic Hermite + R13 normalised
two-family meridians + R14 sin(pi*t)^2 web-height blending and 1:16 STL.
Only new experimental six-cell sexpartite geometry; R10–R14 untouched.
Original R17 V1 exact arch AND six groin curves retained as immutable input.
"""
import sys,hashlib,json,math
from pathlib import Path
import numpy as np,trimesh
from scipy.interpolate import CubicHermiteSpline
D=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(D/'R16_dependency/src'))
from guarded_vault_adapter import guarded_build,source_lock_snapshot
from strict_crown_guard import CrownBelowArchApex
V1=D.parent/'F5ZP_R17_SEXPARTITE_DOUBLE_BAY_1_TO_16_EXPERIMENTAL'
O=V1/'outputs/R17_EXACT_SIX_ARCH_SIX_GROIN_SKELETON_NATIVE.json'
assert O.is_file()
oldsource=json.loads(O.read_text())
LINEAGE=json.loads((D/'qa/R17_V2_SOURCE_LINEAGE.json').read_text())
for info in LINEAGE.values():
    source=Path(info['original']);archive=Path(info['archived'])
    assert hashlib.sha256(source.read_bytes()).hexdigest()==info['sha256']
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==info['sha256']
N=128; S=257; SPRING=3000.; BOSS=4700.; DENOM=16
PLAN=np.array([[-2200,-1200],[0,-1200],[2200,-1200],
              [2200,1200],[0,1200],[-2200,1200]],float)
RISE=np.array([1200,1200,1320,1200,1200,1320],float)
TYPES=['A','A','B','A','A','B']
PROTECTED=list((D/'R16_dependency/src').glob('*.py'))+list((D/'R16_dependency/reference').glob('*.py'))
PROTECTED+=[O]+[Path(info['original']) for info in LINEAGE.values()]
ARCHIVED_LOCKS={
 'experimental_boundary_plan_native':PLAN.tolist(),'experimental_arch_rises':RISE.tolist(),
 'original_R17_V1_arch_groin_skeleton_SHA256':hashlib.sha256(O.read_bytes()).hexdigest(),
 'F5ZK_C_F5ZN_A_Pass6J':'external locked geometry untouched',
 'R10_R14_sources_sha256':{name:obj['sha256'] for name,obj in LINEAGE.items()},
 'model_scale':'native 1:1 algebra, exact 1/16 delivered mesh'}
def arch(i,t):
    """Exact original two-centred Gothic boundary profile."""
    a=PLAN[i];b=PLAN[(i+1)%6]
    L=float(np.linalg.norm(b-a)); x=L*min(float(t),1-float(t))
    R=L/4.+RISE[i]**2/L
    h=math.sqrt(max(0.,R**2-(x-R)**2))
    return np.array([*((1-t)*a+t*b),SPRING+h],float)
def baseline(i,t,s):
    """Protected original R17 skeleton, used only as R09 basefn."""
    p=arch(i,t)
    return np.array([*((1-s)*p[:2]),BOSS-(1-s)**2*(BOSS-p[2])],float)
def profile(i):
    """Controlled 2-piece C1 cubic-Hermite apex to BOSS (R10/R13/R14).
    Two independent arch types A/B. Derivatives measured dZ/ds.
    Set R10-like endpoint tangents equal to source baseline to avoid
    spurious arch/boss derivative steps. Curvature adjustment interior only.
    """
    z0=SPRING+RISE[i]; dz=BOSS-z0
    bump=45. if TYPES[i]=='A' else 35.
    mid=BOSS-.25*dz+bump
    slopes=[2*dz,.5*dz,0.]
    knots=[z0,mid,BOSS]
    return CubicHermiteSpline([0.,.5,1.],knots,slopes,extrapolate=False)
CURVES=[profile(i) for i in range(6)]
def sculpt(i,t,s):
    """R10 adapted() cross-web weighting exactly as R14 sculpt().
    No xy change, no arch/groin change; only interior height correction.
    """
    t=float(t);s=float(s)
    p=baseline(i,t,s)
    old_mid=baseline(i,.5,s)[2]
    wanted=float(CURVES[i](s))
    p[2]+=math.sin(math.pi*t)**2*(wanted-old_mid)
    return p
def arch_profiles():
    return [{'id':f'REAL_R17_SEXPARTITE_ARCH_{i:02d}',
      'points_xyz':[arch(i,j/(S-1)).tolist() for j in range(S)]}
      for i in range(6)]
ARCHES=arch_profiles()
def evaluate():
    # Original R17 V1 boundary & radial rib reference, independently checked.
    gap=0.
    for k in range(6):
        for j in range(129):
            u=j/128
            p=np.array(oldsource['arches'][k][j],float)
            gap=max(gap,float(np.linalg.norm(arch(k,u)-p)))
        for j in range(97):
            s=j/96
            expected=np.asarray(oldsource['groins'][k][j])
            got=baseline(k,0,s)
            gap=max(gap,float(np.linalg.norm(got-expected)))
    assert gap<1e-7,('Original source skeleton drift',gap)
    bone_error=0.;mono_viol=0.;arch_error=0.;controls=[]
    for k in range(6):
        for s in np.linspace(0,1,41):
            for t in (0.,1.):
                bone_error=max(bone_error,float(np.linalg.norm(sculpt(k,t,s)-baseline(k,t,s))))
        for t in np.linspace(0,1,33):
            arch_error=max(arch_error,float(np.linalg.norm(sculpt(k,t,0)-baseline(k,t,0))))
            heights=np.array([sculpt(k,t,s)[2] for s in np.linspace(0,1,501)])
            mono_viol=max(mono_viol,float(max(0.,np.max(-np.diff(heights)))))
            assert max(heights)<=BOSS+1e-7,('Web rises over central boss',k,t,max(heights))
        vals=np.array([float(CURVES[k](s)) for s in np.linspace(0,1,2001)])
        assert vals.min()>=SPRING+RISE[k]-1e-7 and vals.max()<=BOSS+1e-7
        assert np.max(-np.diff(vals))<1e-10
        controls.append({'sector':k,'type':TYPES[k],
          'apex_Z':float(SPRING+RISE[k]),'boss_Z':BOSS,
          'meridian_mid_Z':float(CURVES[k](.5)),
          'meridian_dZds_at_apex':float(CURVES[k](0.,1)),
          'meridian_dZds_at_mid':float(CURVES[k](.5,1)),
          'meridian_dZds_at_boss':float(CURVES[k](1.,1))})
    assert arch_error<1e-7 and bone_error<1e-7 and mono_viol<1e-7
    return {'original_R17_V1_skeleton_max_error_native':gap,
      'boundary_arch_error_native':arch_error,'groin_error_native':bone_error,
      'maximum_downhill_meridian_delta_native':mono_viol,'sector_controls':controls}
def build_mesh():
    verts=[];faces=[]
    for k in range(6):
        index={}
        for j in range(N+1):
            s=j/N
            for i in range(N-j+1):
                t=i/(N-j) if j<N else .5
                index[(j,i)]=len(verts)
                verts.append(sculpt(k,t,s))
        for j in range(N):
            for i in range(N-j):
                a=index[(j,i)];b=index[(j,i+1)];c=index[(j+1,i)]
                faces.append((a,c,b))
                if i<N-j-1:
                    d=index[(j+1,i+1)]
                    faces.append((b,c,d))
    m=trimesh.Trimesh(vertices=np.asarray(verts,float),
      faces=np.asarray(faces,int),process=False)
    m.merge_vertices(digits_vertex=5);m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m)
    assert len(m.faces)==6*N*N and m.euler_number==1
    assert m.is_winding_consistent and not m.is_watertight
    return {'mesh':m,'crown_Z':BOSS,'web_peak_Z':float(m.vertices[:,2].max()),
      'boundary_arches':ARCHES,'locks':ARCHIVED_LOCKS}
def main():
    proof=evaluate()
    src_hash=source_lock_snapshot(PROTECTED)
    produced=build_mesh()
    m=produced['mesh']
    report=guarded_build(name='R17_V2_R10_R14_FULL_SEXPARTITE',
       boundary_arches=ARCHES,crown_Z=BOSS,spring_Z=SPRING,
       source_paths=PROTECTED,build_in_memory_fn=lambda:produced,
       locked_baseline_fn=lambda:ARCHIVED_LOCKS,crown_locked=False,
       output_dir=D/'outputs/guarded',intended_export='open_intrados')
    assert report['postbuild']['highest_apex_Z']==4320.0
    assert report['postbuild']['crown_relation']=='RAISED'
    assert 'LOCKED_GEOMETRY_WARNING_ALWAYS' in report['postbuild']['warning_codes']
    assert src_hash==source_lock_snapshot(PROTECTED)
    # All deliveries 1:16, NOT a native 1:1 review GLB.
    small=m.copy();small.apply_scale(1/DENOM)
    f=D/'outputs/R17_V2_R10_R14_1to16_OPEN_WEB.glb'
    assert not f.exists()
    small.visual.face_colors=[189,206,199,255]
    small.export(f)
    sections=[]
    for k in range(6):
        p=D/'outputs'/f'R17_V2_MERIDIAN_{k:02d}_NATIVE_REFERENCED.csv'
        assert not p.exists()
        np.savetxt(p,np.array([sculpt(k,.5,s) for s in np.linspace(0,1,257)]),
           fmt='%.12f',delimiter=',',header='world_X,world_Y,world_Z',comments='')
        sections.append({'sector':k,'type':TYPES[k],
            'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    skeleton=D/'outputs/R17_V2_MATCHED_SKELETON_NATIVE.json'
    assert not skeleton.exists()
    skeleton.write_text(json.dumps({'reference':str(O),
       'arches':[[arch(k,j/128).tolist() for j in range(129)] for k in range(6)],
       'groins':[[baseline(k,0,j/96).tolist() for j in range(97)] for k in range(6)],
       'apex_Z_max':4320.,'boss_Z':BOSS},separators=(',',':')))
    stl=trimesh.load_mesh(D/'outputs/guarded/R17_V2_R10_R14_FULL_SEXPARTITE_1to16.stl')
    assert np.max(abs(stl.bounds*16-m.bounds))<.0008
    qa={'status':'R17_V2_FULL_R10_R14_METHOD_TESTED_1_TO_16_EXPERIMENTAL',
     'replaced_simplified_R17_surface':True,'V1_original_arches_unchanged':True,
     'V1_original_groins_unchanged':True,'user_architectural_approvals_modified':False,
     'exact_scale':'1:16 geometry for STL GLB Blender',
     'formula':'R09 6 triangular patches; R10 C1 two-piece Hermite; R13 normalised two families; R14 sin(pi*t)^2 interior control',
     'six_sexpartite_cells':True,'control_curves':sections,
     'geometric_proof':proof,'faces':int(len(m.faces)),'vertices':int(len(m.vertices)),
     'highest_boundary_apex_Z':4320.,'central_boss_Z':BOSS,
     'native_crown_above_arch':BOSS-4320.,
     'R16_prebuild_and_postbuild_verified':True,
     'R16_warnings':report['postbuild']['warning_codes'],
     'open_intrados_only':True,'cap_masonry_validation':'NOT VERIFIED',
     'structural_validation':'NOT PERFORMED',
     'R16_source_sha256_preserved':src_hash,'scaled_glb_sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
    (D/'qa/R17_V2_FULL_SURFACE_VALIDATION.json').write_text(json.dumps(qa,indent=2))
    print('R17_V2_FULL_R10_R14_PASS','triangles',len(m.faces),
       'boundary_errors',proof['boundary_arch_error_native'],
       'groin_errors',proof['groin_error_native'],
       'monotonic_sag',proof['maximum_downhill_meridian_delta_native'],
       'native_crown_rise',380,'scale',1/16)
if __name__=='__main__':main()
