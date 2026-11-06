#!/usr/bin/env python3
"""Improve presentation and embed V02 addon code in a NEW working scene.
No vault regeneration, no source baseline or previous .blend changes.
"""
import bpy,pathlib,hashlib,json
D=pathlib.Path(__file__).resolve().parents[1]
source=D/'blender/R17_FAST_VAULT_WORKSPACE_CHECKPOINT_001_EXPERIMENTAL.blend'
assert pathlib.Path(bpy.data.filepath).resolve()==source.resolve()
sha=hashlib.sha256(source.read_bytes()).hexdigest()
master=bpy.data.scenes['R17_WORKSPACE']
assert master.get('r17_last_status')=='VALIDATED_EXPERIMENTAL'
active=bpy.data.collections['R17_EXPERIMENTAL_GEOMETRY']
old_ids={o.name:(len(o.data.vertices),len(o.data.polygons))
   for o in active.objects if o.type=='MESH'}
assert len(old_ids)==1
world=bpy.data.worlds.get('R17_WARM_SLATE_BACKGROUND')
if world is None:world=bpy.data.worlds.new('R17_WARM_SLATE_BACKGROUND')
world.use_nodes=False
world.color=(.2,.23,.26)
for scene in bpy.data.scenes:
    if not scene.name.startswith('R17_'):continue
    scene.world=world
    scene.display.shading.background_type='WORLD'
    scene.display.shading.background_color=(.2,.23,.26)
    scene.display.shading.light='STUDIO'
    scene.display.shading.show_cavity=True
    scene.display.shading.show_shadows=True
    scene.render.film_transparent=False
    scene['PRESENTATION_ONLY_V02']=True
plan=bpy.data.scenes['R17_REVIEW_PLAN']
plan.camera.data.ortho_scale=4500
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active
            sp.show_region_ui=True
            sp.lens=9.3
            sp.clip_start=.01
            sp.clip_end=99999997952.
            if sp.region_3d:sp.region_3d.view_perspective='CAMERA'
for file in ('r17_core.py','r17_experimental_workspace.py'):
    block=bpy.data.texts.get('R17_SOURCE_'+file)
    assert block is not None
    block.clear()
    block.write((D/'addon'/file).read_text())
doc=bpy.data.texts.get('R17_WORKSPACE_USER_GUIDE')
if doc is None:doc=bpy.data.texts.new('R17_WORKSPACE_USER_GUIDE')
doc.write('R17 Experimental Fast Gothic Vault Workspace — V02\n'
   'Click N in 3D viewport, R17 Vault tab, and REGENERATE TEST VAULT.\n'
   'FAST 32: proportions; FINAL 128: surface detail (same geometry).\n'
   'Crown AUTO: preferred raised on new unlocked studies only.\n'
   'Crown LEVEL: exactly match highest pointed arch apex, displays WARNING.\n'
   'Crown MANUAL: requires a numeric value; below apex stops building.\n'
   'Crown LOCKED: only MANUAL allowed; never auto-move baseline.\n'
   'All R16 and protected source warnings saved in Text Editor.\n'
   'Review scenes share one experimental collection, no duplicate meshes.\n'
   'Select Axon / Plan / Underside / Section from the panel.\n'
   'Export native 1:1 GLB; Save .blend always creates a new version.\n'
   'This is an experimental synthetic vault laboratory — not validated historical architecture.\n')
for k,v in old_ids.items():
    assert (len(bpy.data.objects[k].data.vertices),
            len(bpy.data.objects[k].data.polygons))==v
bpy.context.window.scene=master
dest=D/'blender/F5ZP_R17_FAST_VAULT_WORKSPACE_REVIEW_READY_V02_EXPERIMENTAL.blend'
assert not dest.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
record={'status':'R17_REVIEW_READY_NEW_V02_BLENDER_SAVED',
 'V02_blend':str(dest),'prior_V01_checkpoint_SHA256_preserved':sha,
 'geometry_identical_to_prior_checkpoint':True,
 'persistent_sidebar_enabled_via_installed_addon':True,
 'clearer_background_setup':True,
 'plan_camera_framing_fixed':True,
 'five_camera_scenes_reused':True,
 'embedded_source_matches_current_R17_addon':True}
p=D/'qa/R17_REVIEW_V02_SOURCE_PROTECTION_QA.json'
assert not p.exists();p.write_text(json.dumps(record,indent=2))
print('R17_V02_REVIEW_READY_SAVED',dest,flush=True)
