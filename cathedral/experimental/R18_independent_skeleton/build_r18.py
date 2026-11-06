#!/usr/bin/env python3
"""R18 independent-skeleton study. Run with Blender --background --python."""
from pathlib import Path
import sys, math, json, hashlib, zipfile
from dataclasses import asdict
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
R17=BASE/'F5ZP_R17_FAST_UNIVERSAL_VAULT_WORKSPACE_EXPERIMENTAL'
sys.path[:0]=[str(R17/'addon'),str(R17/'addon/r17_vendor')]
import r17_core as core
from strict_crown_guard import enforce,preferred_crown
for d in ('qa','outputs','review'): (ROOT/d).mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
protected=[R17/'addon/r17_core.py',R17/'addon/r17_experimental_workspace.py',
 R17/'blender/F5ZP_R17_FAST_VAULT_WORKSPACE_REVIEW_READY_V02_EXPERIMENTAL.blend',
 BASE/'CHAPEL_POLYGONAL_APSE_V4_SKELETON_R07_EXPERIMENTAL/scripts/build_R07_polygonal_skeleton_and_webs.py']
protected+=list((R17/'addon/r17_vendor').glob('*.py'))
before={str(p):sha(p) for p in protected}
original=core.interpolated_web_point
def independent_rib(A,r,spring,crown):
    run=math.hypot(*A); rise=crown-spring
    R=(run*run+rise*rise)/(2*run)
    if rise<run: raise ValueError('Circular branch requires rise >= radial run; no automatic fallback')
    z=spring+math.sqrt(max(0.,R*R-(R-run*r)**2))
    return ((1-r)*A[0],(1-r)*A[1],z)
def skeleton_point(C,corners,k,t,r,crown):
    if r>=1: return (0.,0.,crown)
    A=corners[k]; B=corners[(k+1)%len(corners)]
    ga=independent_rib(A,r,C.spring_Z,crown)[2]
    gb=independent_rib(B,r,C.spring_Z,crown)[2]
    radial=(1-t)*ga+t*gb
    *_,L,rise=core.edge_data(C,A,B)
    edge=core.true_two_centred_pointed_height(t,L,C.spring_Z,rise)
    # R07 bounded blend. Web-only exponent cannot move the independent ribs.
    z=radial+(crown-radial)*(edge-C.spring_Z)/(crown-C.spring_Z)*(1-r)**C.meridian_exponent
    return ((1-r)*((1-t)*A[0]+t*B[0]),(1-r)*((1-t)*A[1]+t*B[1]),z)
def make(C):
    arches=core.measured_boundary_arches(C)
    crown=preferred_crown(boundary_arches=arches,spring_Z=C.spring_Z)
    policy=enforce(vault_id='R18_'+C.vault_type,crown_Z=crown,boundary_arches=arches,spring_Z=C.spring_Z)
    core.interpolated_web_point=skeleton_point
    try: data=core.build_mesh_data(C,crown)
    finally: core.interpolated_web_point=original
    return data,policy
def checks(C,data):
    corners=core.plan_corners(C); crown=data['crown_Z']
    rib_error=arch_error=control_error=0.
    for k,A in enumerate(corners):
        for j in range(257):
            u=j/256
            rib_error=max(rib_error,math.dist(skeleton_point(C,corners,k,0,u,crown),independent_rib(A,u,C.spring_Z,crown)))
            arch_error=max(arch_error,math.dist(skeleton_point(C,corners,k,u,0,crown),data['arches'][k]['points_xyz'][j]))
    V=data['vertices']; F=data['faces']; edges={}; degenerate=0
    for face in F:
        a,b,c=(Vector(V[i]) for i in face)
        if (b-a).cross(c-a).length/2 <1e-10: degenerate+=1
        for a,b in zip(face,face[1:]+face[:1]):
            e=tuple(sorted((a,b))); edges[e]=edges.get(e,0)+1
    boundary=sum(n==1 for n in edges.values())
    q={'rib_fit_max_native':rib_error,'arch_fit_max_native':arch_error,
       'seam_gap_native':data['seam_gap_native'],'degenerate_triangles':degenerate,
       'nonmanifold_edges_gt2':sum(n>2 for n in edges.values()),
       'open_perimeter_edges':boundary,'expected_perimeter_edges':C.sector_count*C.divisions,
       'euler_characteristic':len(V)-len(edges)+len(F),
       'peak_above_crown_native':max(v[2] for v in V)-crown,
       'max_displacement_vs_R17_native':max(abs(skeleton_point(C,corners,k,t,r,crown)[2]-original(C,corners,k,t,r,crown)[2])
          for k in range(C.sector_count) for t in (0,.25,.5,.75,1) for r in (.1,.25,.5,.75,.9))}
    assert rib_error<1e-7 and arch_error<1e-7 and data['seam_gap_native']<1e-7,q
    assert degenerate==0 and q['nonmanifold_edges_gt2']==0 and boundary==C.sector_count*C.divisions,q
    assert q['euler_characteristic']==1 and abs(q['peak_above_crown_native'])<1e-7,q
    return q
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
def mesh(name,data,offset,mat):
    m=bpy.data.meshes.new(name);m.from_pydata(data['vertices'],[],data['faces']);m.update()
    o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o.location.x=offset;o.data.materials.append(mat)
    return o
def guide(name,pts,offset,mat):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=.8;c.bevel_resolution=1
    s=c.splines.new('POLY');s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts):p.co=(*v,1)
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.location.x=offset;c.materials.append(mat)
    o['representation']='THIN_SKELETON_GUIDE_ONLY_NOT_PHYSICAL_MOULDING'
    return o
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
webmat=material('Experimental web',(0.68,.75,.82)); oldmat=material('R17 reference',(.5,.55,.6))
ribmat=material('Independent ribs',(.8,.13,.035)); archmat=material('Preserved boundary arches',(.02,.18,.6))
reports=[]; studies=[]
# Preserve R17 six-sector crown: R07 vertical-spring circle is inadmissible here.
hexC=core.Settings(vault_type='HEXA',quality='FINAL',arch_rise_ratio=.7200000286102295)
try: make(hexC)
except ValueError as e:
    assert 'Circular branch requires' in str(e)
    hex_rejection={'family':'HEXA','status':'REJECTED_WITH_CROWN_PRESERVED','reason':str(e)}
else: raise AssertionError('Expected explicit six-sector circular incompatibility')
for family in ('QUAD',):
    C=core.Settings(vault_type=family,quality='FINAL',radius=1200,spring_Z=3000,
       arch_rise_ratio=.7200000286102295,meridian_exponent=1.75,dome_lift=.30000001192092896)
    data,policy=make(C); q=checks(C,data)
    old=core.build_mesh_data(C,data['crown_Z'])
    assert data['arches']==old['arches']
    report={'family':family,'settings':asdict(C),'crown_Z':data['crown_Z'],'highest_apex_Z':policy['highest_apex_Z'],
       'geometry_tests':q,'triangles':len(data['faces']),'boundary_arches_unchanged':True,'crown_unchanged':True}
    reports.append(report);studies.append((C,data,old))
    # Paired same-scale studies, no edits to the archived R17 scene.
    row=0 if family=='QUAD' else 6400
    for label,shape,off,mat in [('R17_REFERENCE',old,-1800,oldmat),('R18_INDEPENDENT',data,1800,webmat)]:
        o=mesh(family+'_'+label,shape,off,mat);o.location.y=row
        for kind,paths,ma in [('ARCH',shape['arches'],archmat),('GROIN',shape['ribs'],ribmat)]:
            for path in paths:
                g=guide(family+'_'+label+'_'+path['id'],path['points_xyz'],off,ma);g.location.y=row
    # Export new web plus its thin guides only in native 1:1.
    bpy.ops.object.select_all(action='DESELECT')
    chosen=[o for o in bpy.context.scene.objects if o.name.startswith(family+'_R18_')]
    for o in chosen: o.select_set(True);o.location.x-=1800;o.location.y-=row
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'outputs'/('R18_'+family+'_1TO1.glb')),use_selection=True,export_format='GLB',export_yup=True)
    for o in chosen:o.location.x+=1800;o.location.y+=row
# Broader geometry regression: FAST/FINAL, irregularity and 3..8 sectors.
regress=[]
for n in range(3,9):
    for irregular in (0.,.15):
        C=core.Settings(vault_type='CUSTOM',custom_sectors=n,quality='FAST',irregularity=irregular)
        try:
            d,p=make(C);q=checks(C,d)
            regress.append({'n':n,'irregularity':irregular,'result':'PASS','tests':q})
        except ValueError as e:
            # Explicit unsupported circular branch, never silently alter skeleton.
            assert 'Circular branch requires' in str(e)
            regress.append({'n':n,'irregularity':irregular,'result':'REJECT_UNSUPPORTED_CIRCULAR_BRANCH','reason':str(e)})
# Guards reject below-apex and automatic locked crown.
guard_tests={}
C=core.Settings(); arcs=core.measured_boundary_arches(C); apex=max(p[2] for a in arcs for p in a['points_xyz'])
try: enforce(vault_id='R18_NEGATIVE_TEST',crown_Z=apex-1,boundary_arches=arcs,spring_Z=C.spring_Z)
except Exception as e:guard_tests['below_apex_rejected']=str(e)
assert guard_tests
try: core.Settings(crown_locked=True,crown_mode='AUTO').check()
except ValueError as e:guard_tests['locked_auto_rejected']=str(e)
assert len(guard_tests)==2
# Deterministic numerical readback of Blender-stored float32 mesh, before GLB.
for family in ('QUAD',):
    o=bpy.data.objects[family+'_R18_INDEPENDENT']
    assert abs(max(v.co.z for v in o.data.vertices)-reports[0 if family=='QUAD' else 1]['crown_Z'])<.001
after={str(p):sha(p) for p in protected};assert before==after
report={'status':'EXPERIMENTAL_SKELETON_FIRST_GEOMETRIC_STUDY','scale':'native 1:1; X/Y plan, Z elevation',
 'studies':reports,'six_sector_admissibility':hex_rejection,'regression':regress,'guard_tests':guard_tests,'protected_SHA256_before':before,
 'protected_SHA256_after':after,'protected_sources_unchanged':True,
 'warnings':['LOCKED_GEOMETRY_WARNING_ALWAYS: no protected geometry edited',
 'R18 groins intentionally differ from R17; no approval promotion',
 'Thin guides are not physical rib solids; web is open intrados, not masonry shell',
 'No profile sweep, springer trim, bearing or structural acceptance',
 'Circular method rejects rise < radial run instead of inventing a fallback'],
 'next_task':'Review independent rib set-out; then verified profile orientation, soffit contact and separate springer-junction experiment'}
(ROOT/'qa/R18_QA.json').write_text(json.dumps(report,indent=2))
# Measurable SVG section: exact source samples, not AI imagery.
C,d,old=studies[0]; H=d['crown_Z']-C.spring_Z
parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 1600 1700">']
parts.append('<rect x="-100" y="-100" width="1600" height="1700" fill="white"/>')
for pts,color in [(old['ribs'][0]['points_xyz'],'#777'),(d['ribs'][0]['points_xyz'],'black')]:
    points=' '.join(f'{1200-math.hypot(p[0],p[1]):.8f},{H-(p[2]-C.spring_Z):.8f}' for p in pts)
    parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
parts.append('<text x="0" y="1500" font-size="28">Black: R18 independent circle; gray: R17 web-derived rib. Native 1:1 units.</text></svg>')
(ROOT/'review/R18_QUAD_RADIAL_SECTION.svg').write_text('\n'.join(parts))
# Save review scene and render paired reference/new webs with identical scales.
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.world.color=(.8,.8,.8);scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
camera=bpy.data.cameras.new('R18 matched comparison');cam=bpy.data.objects.new('R18 matched comparison',camera)
scene.collection.objects.link(cam);scene.camera=cam;camera.type='ORTHO';camera.ortho_scale=8400;camera.clip_end=100000
cam.location=(4500,-7000,-2000);target=Vector((0,0,3650));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.lens=9.3;area.spaces.active.clip_start=.01;area.spaces.active.clip_end=99999997952
blend=ROOT/'R18_INDEPENDENT_SKELETON_MATCHED_WEBS_EXPERIMENTAL.blend'
assert not blend.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
scene.render.filepath=str(ROOT/'review/R18_PAIRED_UNDERSIDE.png');bpy.ops.render.render(write_still=True)
readme="""# R18 independent skeleton / matched webs — EXPERIMENTAL
Recovered from R17 V02 and its read-only junction audit. R17, R16 and R07 sources are unchanged.
Native architectural 1:1; X/Y plan, Z up. QUAD preserves each R17 boundary arch and crown. HEXA is explicitly rejected: the R07 vertical-spring circle cannot reach its lower preserved crown monotonically.
R07 circular groins are constructed independently; bounded R07-style web blending fits them exactly.
Web exponent shapes interiors without moving groins. This experiment does not reproduce R09/R10 Hermite controls.
Gray left models are regenerated R17 method comparisons; blue right models are new R18 studies.
Review SVG and QA for quantitative differences. Colored curves are thin guides, NOT rib solids.
Open intrados intentionally has only perimeter boundary edges. Do not interpret it as a watertight shell.
No historical, architectural or structural acceptance is claimed. F5ZN-A, Pass 6J and all approved architecture untouched.
F5ZL-C support schedule unresolved. No promotion into the cathedral.
Reproduce using Blender --background --factory-startup --python build_r18.py with original R17 sibling paths.
The script refuses to overwrite its saved Blender study. Use a fresh study directory to reproduce.
Next: review rib set-out, then recover verified profiles and test swept ribs/soffits and a separate springer joint.
"""
(ROOT/'README.md').write_text(readme)
manifest={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256.json'}
(ROOT/'SHA256.json').write_text(json.dumps(manifest,indent=2))
archive=ROOT.parent/'F5ZP_R18_INDEPENDENT_SKELETON_MATCHED_WEBS_EXPERIMENTAL.zip'
assert not archive.exists()
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in ROOT.rglob('*'):
  if p.is_file():z.write(p,str(Path(ROOT.name)/p.relative_to(ROOT)))
print('R18_COMPLETE '+json.dumps({'archive':str(archive),'studies':reports,'regression_cases':len(regress)}))
