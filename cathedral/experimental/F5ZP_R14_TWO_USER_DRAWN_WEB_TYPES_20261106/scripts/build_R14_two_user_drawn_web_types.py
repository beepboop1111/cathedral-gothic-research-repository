#!/usr/bin/env python3
"""F5ZP R14 two red-line Gothic vault web families (experimental).
Type A sectors 00-04: preserve EXACT user-accepted R13 surface.
Type B sector 05: user-drawn red-stroke piecewise C1 Hermite apex->boss.
Never move arches, radial ogives, floor plan, Z4296 boss or source files.
Open intrados only until Type A haunch conflicts resolved.
"""
from pathlib import Path
import hashlib,json,math
import numpy as np,trimesh
from scipy.interpolate import CubicHermiteSpline
from scipy.spatial import cKDTree
D=Path(__file__).resolve().parents[1]
C=json.loads((D/'configs/R14_TWO_TYPES_REDLINE.json').read_text())
R13=Path(C['source_R13_directory'])
generator=R13/'scripts/build_R13_five_matching_webs.py'
R13C=R13/'configs/R13_TWO_TYPES.json'
R13blend=R13/'F5ZP_R13_FIVE_MATCHING_TYPE_A_WEBS_UNIQUE_TYPE_B_PENDING_LIVE_EXPERIMENTAL.blend'
assert hashlib.sha256(generator.read_bytes()).hexdigest()==C['source_R13_generator_sha256']
assert hashlib.sha256(R13C.read_bytes()).hexdigest()==C['source_R13_config_sha256']
assert hashlib.sha256(R13blend.read_bytes()).hexdigest()==C['source_R13_blend_sha256']

# Recover verified R13 analytical functions ONLY; no export calls executed.
source=generator.read_text()
assert '# Save five normalized mappings' in source
r13={'__file__':str(generator),'__name__':'R13_ANALYTIC_SOURCE_ONLY'}
exec(compile(source.split('# Save five normalized mappings')[0],
             str(generator),'exec'),r13)
old=r13['shape'] # contains accepted 02 curve for sectors 00..04.
slopes=C['sector_05_C1_knots_dZds']
meridian_B=CubicHermiteSpline(C['sector_05_C1_knots_s'],
      C['sector_05_C1_knots_Z'],slopes,extrapolate=False)
assert abs(float(meridian_B(0))-4296)<1e-8
assert abs(float(meridian_B(1))-4296)<1e-8
N=128
def sculpt(k,t,s):
    p=np.asarray(old(k,float(t),float(s)),float).copy()
    if k==5:
        old_mid=old(5,.5,float(s))[2]
        p[2]+=math.sin(math.pi*float(t))**2 * (
                 float(meridian_B(float(s)))-old_mid)
    return p

# Exact registered 1:1 red stroke. Match user-side reference SHA bytewise
# so no calibration drift can enter the Blender shell.
svals=np.linspace(0,1,257)
curve=np.asarray([sculpt(5,.5,s) for s in svals])
meridian_path=D/'outputs/R14_SECTOR05_TYPE_B_USER_RED_MERIDIAN_WORLD_1to1.csv'
assert not meridian_path.exists()
np.savetxt(meridian_path,curve,fmt='%.12f',delimiter=',',
           header='world_X,world_Y,world_Z',comments='')
csv_sha=hashlib.sha256(meridian_path.read_bytes()).hexdigest()
assert csv_sha==C['user_fitted_257point_curve_csv_sha256'],(
    csv_sha,C['user_fitted_257point_curve_csv_sha256'])
assert np.linalg.norm(curve[0]-C['sector_05_arch_apex'])<1e-7
assert np.linalg.norm(curve[-1]-C['sector_05_crown'])<1e-7

# Five accepted reference centerlines are not regenerated or overwritten.
r13QA=json.loads((R13/'qa/R13_FIVE_MATCHING_TYPE_A_VAULT_QA.json').read_text())
type_A_unchanged={}
for k in range(5):
    ref=R13/'outputs'/r13QA['meridian_files'][str(k)]['filename']
    assert hashlib.sha256(ref.read_bytes()).hexdigest()==r13QA['meridian_files'][str(k)]['sha256']
    candidate=np.asarray([sculpt(k,.5,t) for t in svals])
    baseline=np.loadtxt(ref,delimiter=',',skiprows=1)
    delta=float(np.max(np.abs(candidate-baseline)))
    assert delta<1e-8,(k,delta)
    type_A_unchanged[str(k)]={'source_curve':ref.name,'analytic_difference_native':delta}

# Exact triangular sampling of all six sectors. Radial seams share
# identical boundary coordinates; "merge_vertices" welds shared ribs.
verts=[];faces=[]
max_sectorB_height=-1e10
for k in range(6):
    ix={}
    for j in range(N+1):
        ss=j/N
        for i in range(N-j+1):
            tt=i/(N-j) if j<N else .5
            p=sculpt(k,tt,ss)
            if k==5:max_sectorB_height=max(max_sectorB_height,float(p[2]))
            ix[(j,i)]=len(verts)
            verts.append(p)
    for j in range(N):
        for i in range(N-j):
            a=ix[j,i];b=ix[j,i+1];c=ix[j+1,i]
            faces.append((a,c,b))
            if i<N-j-1:
                d=ix[j+1,i+1]
                faces.append((b,c,d))
mesh=trimesh.Trimesh(vertices=np.asarray(verts,float),
                     faces=np.asarray(faces,int),process=False)
mesh.merge_vertices(digits_vertex=5)
mesh.remove_unreferenced_vertices()
assert mesh.is_winding_consistent and not mesh.is_watertight
assert mesh.euler_number==1 and len(mesh.faces)==98304

# No old geometry is displaced. Only k=5 internal web changes.
errs={'perimeter_pointed_arches':0.,'all_six_groins':0.,
      'bosses_Z4296':0.,'all_five_Type_A_webs':0.,
      'Type_B_user_curve_match':0.,'plan_XY':0.}
for k in range(6):
    for t in np.linspace(0,1,65):
        errs['perimeter_pointed_arches']=max(errs['perimeter_pointed_arches'],
            float(np.max(abs(sculpt(k,t,0)-old(k,t,0)))))
    for ss in np.linspace(0,1,65):
        for t in (0.,1.):
            errs['all_six_groins']=max(errs['all_six_groins'],
                float(np.max(abs(sculpt(k,t,ss)-old(k,t,ss)))))
        errs['bosses_Z4296']=max(errs['bosses_Z4296'],
            float(np.max(abs(sculpt(k,.5,1)-old(k,.5,1)))))
        if k==5:
            errs['Type_B_user_curve_match']=max(errs['Type_B_user_curve_match'],
                abs(sculpt(5,.5,ss)[2]-float(meridian_B(ss))))
        for t in np.linspace(0,1,17):
            p=sculpt(k,t,ss);q=old(k,t,ss)
            errs['plan_XY']=max(errs['plan_XY'],float(np.max(abs(p[:2]-q[:2]))))
            if k!=5:
                errs['all_five_Type_A_webs']=max(errs['all_five_Type_A_webs'],
                    float(np.max(abs(p-q))))
assert max(errs.values())<1e-8,errs

cap=float(C['provisional_haunch_cap_Z'])
dense=np.linspace(0,1,4001)
peak=float(meridian_B(dense).max())
assert max_sectorB_height < cap
assert peak < cap
assert 3 < cap-peak < 5
# Type A still exceeds this cap, so do NOT falsely close as a solid.
assert r13QA['cap_conflict_native']>0

stl=D/'outputs/R14_FIVE_TYPE_A_PLUS_USER_RED_TYPE_B_OPEN_INTRADOS_1to16.stl'
assert not stl.exists()
small=mesh.copy();small.apply_scale(1/16);small.export(stl)
loaded=trimesh.load_mesh(stl,process=True)
assert loaded.is_winding_consistent and not loaded.is_watertight
assert loaded.euler_number==1 and len(loaded.faces)==98304
tree=cKDTree(loaded.vertices*16)
mesh_gap=0
for k in range(6):
    tests=np.asarray([sculpt(k,.5,j/N) for j in range(0,N+1,2)])
    mesh_gap=max(mesh_gap,float(tree.query(tests)[0].max()))
assert mesh_gap<.004,mesh_gap
glb=D/'outputs/R14_TWO_USER_DRAWN_APSE_WEB_TYPES_FULL_1to1_EXPERIMENTAL.glb'
assert not glb.exists()
display=mesh.copy()
display.visual.face_colors=[180,199,179,255]
display.export(glb)
assert glb.stat().st_size>500_000

qa={'status':'R14_TWO_USER_DRAWN_APSE_WEB_TYPES_COMPLETE_EXPERIMENTAL',
    'Type_A_user_accepted_sectors':[0,1,2,3,4],
    'Type_A_curve_reference_R12B_sector02_unchanged':True,
    'Type_A_webs_exactly_reused':type_A_unchanged,
    'Type_B_unique_user_redrawn_sector':5,
    'Type_B_stroke_image_sha256':C['source_image_sha256'],
    'Type_B_redline_C1_hermite_fit_RMS_native':C['fit_RMS_native'],
    'Type_B_peak_Z':peak,
    'Type_B_max_evaluated_web_Z':max_sectorB_height,
    'Type_B_cap_clearance_meridian_native':cap-peak,
    'Type_B_cap_clearance_whole_web_native':cap-max_sectorB_height,
    'Type_A_cap_conflict_still_native':r13QA['cap_conflict_native'],
    'boss_height_Z':4296,
    'fixed_skeleton_plan_errors':errs,
    'mesh_winding_consistent':bool(mesh.is_winding_consistent),
    'mesh_watertight':bool(mesh.is_watertight),
    'mesh_Euler_characteristic':int(mesh.euler_number),
    'triangles':len(mesh.faces),
    'max_csv_meridian_to_STL_grid_error_native':mesh_gap,
    'TypeB_meridian_csv':meridian_path.name,
    'TypeB_meridian_csv_sha256':csv_sha,
    'Source_R13_Blender_SHA256_preserved':C['source_R13_blend_sha256'],
    'source_STL_1to16':stl.name,
    'STL_SHA256':hashlib.sha256(stl.read_bytes()).hexdigest(),
    'fullscale_GLTF':glb.name,
    'geometry_scope':'only unique sector05 interior red meridian changed',
    'masonry_or_roof_approval':'NOT APPROVED; whole-vault closed shell impossible under existing Type A cap',
    'structural_validation':'NOT PERFORMED',
    'evidence_source':'the actual marked user 2048x1284 pixel image, see local image-fit registration'
}
(D/'qa/R14_APSE_ALL_SIX_WEB_TYPES_GEOMETRY_QA.json').write_text(json.dumps(qa,indent=2))
print('R14_EXPERIMENTAL_GEOMETRY_PASS',
      'type B meridian peak',round(peak,4),'typeB whole-web max',round(max_sectorB_height,4),
      'cap clearance',round(cap-max_sectorB_height,4),
      'Type A unchanged',5,
      'all 6 skeleton errors',max(errs.values()),
      'STL gap',mesh_gap,'triangles',len(mesh.faces))

[executed on device: MR.COMPUTER (c5066a3f-7c79-446e-8649-efbb75d9e7d4)]