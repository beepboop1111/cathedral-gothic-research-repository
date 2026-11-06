#!/usr/bin/env python3
"""R17 functional Blender integration tests, using real saved V01 .blend.
Test 7 layouts, both quality modes, R16 level/below/locks, export,
scene links, source SHA protection. Save NEW checkpoint, never V01.
"""
import bpy,pathlib,sys,json,hashlib,time,math
D=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(D/'addon'))
import r17_core as core
import r17_experimental_workspace as workspace
from strict_crown_guard import enforce

source=D/'blender/F5ZP_R17_FAST_UNIVERSAL_VAULT_WORKSPACE_V01_EXPERIMENTAL.blend'
assert pathlib.Path(bpy.data.filepath).resolve()==source.resolve()
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert 'r17_experimental_workspace' in bpy.context.preferences.addons
master=bpy.data.scenes['R17_WORKSPACE']
bpy.context.window.scene=master
p=master.r17_props
runs=[]
source_register=workspace.source_snapshot()
reference_names={o.name for o in bpy.data.objects if o.name.startswith('R17_')}
assert len([s for s in bpy.data.scenes if s.name.startswith('R17_')])==5

def operate(family,quality,irregularity=0.,custom=7):
    p.vault_type=family
    p.quality=quality
    p.irregularity=irregularity
    p.custom_sectors=custom
    p.crown_mode='AUTO'
    p.crown_locked=False
    p.cap_enabled=False
    tic=time.perf_counter()
    status=bpy.ops.r17.regenerate()
    delta=time.perf_counter()-tic
    assert status=={'FINISHED'},(family,quality,status)
    assert master.get('r17_last_status')=='VALIDATED_EXPERIMENTAL'
    coll=bpy.data.collections.get('R17_EXPERIMENTAL_GEOMETRY')
    n=core.Settings(vault_type=family,quality=quality,custom_sectors=custom).sector_count
    assert len(coll.objects)==1+2*n
    mesh=next(o for o in coll.objects if o.type=='MESH')
    divisions=32 if quality=='FAST' else 128
    assert len(mesh.data.polygons)==n*divisions*divisions
    assert mesh.get('R17_NATIVE_1TO1')
    assert 'LOCKED_GEOMETRY_WARNING_ALWAYS' in master.get('r17_last_warnings')
    report=json.loads(bpy.data.texts['R17_LATEST_COMPLETE_QA.json'].as_string())
    assert report['R16_prebuild']['crown_relation']=='RAISED'
    assert report['R16_postbuild']['crown_relation']=='RAISED'
    assert report['R16_postbuild']['locked_snapshot_hash_verified']
    assert report['R16_postbuild']['rise_above_apex_native']>0
    assert report['geometry_QA']['Euler']==1
    assert report['geometry_QA']['boundary_edges']==n*divisions
    assert report['R16_prebuild']['arch_count']==n
    assert report['source_SHA_before']==source_register
    assert report['source_SHA_after']==source_register
    for view in ('R17_WORKSPACE','R17_REVIEW_AXON',
                 'R17_REVIEW_PLAN','R17_REVIEW_INTERIOR','R17_REVIEW_SECTION'):
        assert bpy.data.collections['R17_EXPERIMENTAL_GEOMETRY'].name in (
           c.name for c in bpy.data.scenes[view].collection.children)
    runs.append({'family':family,'n':n,'quality':quality,
         'seconds':round(delta,3),'triangles':len(mesh.data.polygons),
         'crown_Z':report['resolved_crown_Z'],
         'highest_apex_Z':report['R16_prebuild']['highest_apex_Z'],
         'web_peak_Z':report['web_peak_Z']})
    print('R17_GENERATE_VALID',family,quality,n,'faces',
          len(mesh.data.polygons),'runtime_s',round(delta,3),flush=True)
    return mesh

for family in ('TRI','QUAD','PENTA','HEXA','OCTA'):
    operate(family,'FAST')
operate('CUSTOM','FAST',irregularity=.18,custom=7)
full=operate('QUAD','FINAL')
full_mesh_vertex_count=len(full.data.vertices)
full_mesh_face_count=len(full.data.polygons)
settings=core.Settings(vault_type='QUAD',quality='FINAL',
    crown_mode='AUTO')
arches=core.measured_boundary_arches(settings)
apex=max(max(v[2] for v in a['points_xyz']) for a in arches)

# LEVEL is ALLOWED and explicitly warns about diminished dome effect.
p.crown_mode='LEVEL'  # exact apex avoids Blender FloatProperty rounding
status=bpy.ops.r17.regenerate()
assert status=={'FINISHED'}
level=json.loads(bpy.data.texts['R17_LATEST_COMPLETE_QA.json'].as_string())
assert level['R16_postbuild']['crown_relation']=='LEVEL_WARNING'
assert 'LEVEL_CROWN_REDUCES_DOME_EFFECT' in master.get('r17_last_warnings')
assert level['R16_postbuild']['crown_Z']==level['R16_postbuild']['highest_apex_Z']  # exact same measured source, independent of Blender UI float32 rounding
runs.append({'family':'QUAD','quality':'LEVEL_VALID_WARNING',
    'highest_apex_Z':apex})

# Restore a higher crown at FINAL quality for saved workspace.
p.crown_mode='AUTO'
status=bpy.ops.r17.regenerate()
assert status=={'FINISHED'}
prior=next(x for x in bpy.data.collections['R17_EXPERIMENTAL_GEOMETRY'].objects
           if x.type=='MESH')
prior_n=len(prior.data.vertices)
prior_f=len(prior.data.polygons)
prior_id=prior.as_pointer()
count=int(master['r17_build_count'])

# STRICT failure: below highest arch apex -> NO replacement of existing mesh.
p.crown_mode='MANUAL'
p.crown_z=apex-10
try:failed=bpy.ops.r17.regenerate()
except RuntimeError:failed={'CANCELLED'}
assert failed=={'CANCELLED'}
active=next(x for x in bpy.data.collections['R17_EXPERIMENTAL_GEOMETRY'].objects
           if x.type=='MESH')
assert active.as_pointer()==prior_id
assert len(active.data.vertices)==prior_n and len(active.data.polygons)==prior_f
assert int(master['r17_build_count'])==count
assert master['r17_last_status']=='HARD_STOP'
assert 'LOCKED_GEOMETRY_WARNING_ALWAYS' in master.get('r17_last_warnings')

# STRICT failure: locked elevation cannot be silently raised.
p.crown_locked=True;p.crown_mode='AUTO'
try:failed=bpy.ops.r17.regenerate()
except RuntimeError:failed={'CANCELLED'}
assert failed=={'CANCELLED'}
assert active.as_pointer()==prior_id
assert int(master['r17_build_count'])==count
p.crown_locked=False;p.crown_mode='AUTO'
assert bpy.ops.r17.regenerate()=={'FINISHED'}

# Export only the current web: 1:1 GLB (not entire cathedral/workspace).
try:exp=bpy.ops.r17.export_glb()
except RuntimeError as exc:raise AssertionError('R17 GLB export failed') from exc
assert exp=={'FINISHED'}
index=int(master['r17_build_count'])
glb=D/'outputs'/f'R17_BUILD_{index:03d}_OPEN_INTRADOS_1TO1.glb'
assert glb.exists() and glb.stat().st_size>6000

# Save a new numbered .blend checkpoint, preserve V01 byte-for-byte.
assert bpy.ops.r17.save_checkpoint()=={'FINISHED'}
checkpoint=D/'blender/R17_FAST_VAULT_WORKSPACE_CHECKPOINT_001_EXPERIMENTAL.blend'
assert checkpoint.exists() and checkpoint.stat().st_size>50000
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
assert source_register==workspace.source_snapshot()
QA={'status':'R17_FULL_BLENDER_UI_INTEGRATION_PASS',
 'source_R16_unchanged_SHA256':source_register,
 'source_V01_blend_unchanged_SHA256':source_sha,
 'persistent_addon_enabled':True,
 'five_reusable_shared_geometry_scenes':True,
 'vault_test_families':runs,
 'quality_FAST_divisions':32,'quality_FINAL_divisions':128,
 'FINAL_quad_triangles':full_mesh_face_count,
 'level_crown_warns':True,
 'below_arch_apex_rejected_without_mesh_change':True,
 'locked_crown_AUTO_rejected_without_mesh_change':True,
 'live_1to1_GLB_export_verified':str(glb),
 'versioned_checkpoint_saved':str(checkpoint),
 'approved_architecture_modified':False,
 'technical_validation_passed':True,
 'geometric_validation_passed':True,
 'structural_or_historical_approval':False}
out=D/'qa/R17_FULL_BLENDER_OPERATOR_REGRESSION_QA.json'
assert not out.exists()
out.write_text(json.dumps(QA,indent=2))
print('R17_BLENDER_OPERATOR_SUITE_PASS',
       'families',len(runs),'final GLB',glb.stat().st_size,
       'V01 original hash unchanged',flush=True)
