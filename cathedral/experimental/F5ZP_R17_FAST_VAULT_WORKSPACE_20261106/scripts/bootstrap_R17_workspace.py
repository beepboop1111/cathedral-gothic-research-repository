#!/usr/bin/env python3
"""Create a fresh, reusable R17 Blender testing workspace.
The only geometry generated is a new synthetic test vault. No source
cathedral .blend is opened/edited. Run with Blender --factory-startup.
"""
import bpy,sys,pathlib,json,hashlib,math
from mathutils import Vector

D=pathlib.Path(__file__).resolve().parents[1]
ADDON=D/'addon'
sys.path.insert(0,str(ADDON))
import r17_experimental_workspace as r17
r17.register()

def look(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def camera(scene,label,eye,target,scale):
    data=bpy.data.cameras.new(label+'_DATA')
    obj=bpy.data.objects.new(label,data)
    scene.collection.objects.link(obj)
    obj.location=Vector(eye)
    look(obj,target)
    data.type='ORTHO'
    data.ortho_scale=scale
    data.clip_start=1.
    data.clip_end=150000.
    scene.camera=obj
    return obj

# New empty scene built from factory state; do not import approved cathedral.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.scene.name='R17_WORKSPACE'
master=bpy.context.scene
assert master.r17_props is not None
active=bpy.data.collections.new(r17.GEO_COLLECTION)
ref=bpy.data.collections.new(r17.REF_COLLECTION)
for col in (active,ref):master.collection.children.link(col)
ref.color_tag='COLOR_03'
master['r17_guard_baseline']='Frozen R16 SHA-256; parent R16 files protected'
master['r17_warning']='LOCKED GEOMETRY ALWAYS: none imported/modified here'
master['r17_outputs_dir']=str(D/'outputs')
master['r17_checkpoints_dir']=str(D/'blender')
master['r17_authority']='SYNTHETIC EXPERIMENT ONLY; NO APPROVED ARCHITECTURE'
master['r17_build_count']=0
master['r17_checkpoint_count']=0
master['r17_native_scale']='1:1 CAD units; native units not independently converted to physical SI'
master['r17_user_viewport_preset']={'lens_mm':9.3,
 'clip_start_m':.01,'clip_end_m':99999997952.}
V=master.r17_props
V.vault_type='QUAD';V.quality='FAST';V.crown_mode='AUTO'
V.crown_locked=False;V.irregularity=0.
V.radius=1200.;V.spring_z=3000.
V.arch_rise_ratio=.72;V.meridian_exponent=1.75
V.dome_lift=.3;V.cap_enabled=False

# One shared experimental geometry collection across 5 scene views.
scenes=[master]
for name in ('R17_REVIEW_AXON','R17_REVIEW_PLAN',
             'R17_REVIEW_INTERIOR','R17_REVIEW_SECTION'):
    sc=bpy.data.scenes.new(name)
    sc.collection.children.link(active)
    sc.collection.children.link(ref)
    scenes.append(sc)
for sc in scenes:
    sc.render.engine='BLENDER_WORKBENCH'
    sc.render.resolution_x=1540
    sc.render.resolution_y=1000
    sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG'
    sc.display.shading.light='STUDIO'
    sc.display.shading.color_type='MATERIAL'
    sc.display.shading.show_cavity=True
    sc.display.shading.cavity_type='BOTH'
    sc.display.shading.show_shadows=True
    sc.display.shading.background_type='VIEWPORT'
    sc.display.shading.background_color=(.80,.83,.86)
    sc['R17_SHARED_SCENE']='All review scenes show the SAME experimental objects'
    sc['R17_PROTECTED_ARCHITECTURE']='Nothing imported, original baseline untouched'
R=V.radius
camera(master,'R17_CAM_WORKSPACE',(2.4*R,-2.4*R,6000),
       (0,0,3900),3.25*R)
camera(bpy.data.scenes['R17_REVIEW_AXON'],'R17_CAM_AXON',
       (2.3*R,-2.3*R,5650),(0,0,3910),3.2*R)
camera(bpy.data.scenes['R17_REVIEW_PLAN'],'R17_CAM_PLAN',
       (0,0,7800),(0,0,3650),2.8*R)
camera(bpy.data.scenes['R17_REVIEW_INTERIOR'],'R17_CAM_UNDERSIDE',
       (0,-2.2*R,3230),(0,0,4130),3.5*R)
camera(bpy.data.scenes['R17_REVIEW_SECTION'],'R17_CAM_SECTION',
       (0,-3*R,4300),(0,0,3800),2.95*R)

# User's established 9.3-mm, 0.01 / large far-clip viewport settings
# preserved. Scene camera clipping independent to avoid precision artifacts.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.lens=9.3
            space.clip_start=.01
            space.clip_end=99999997952.
            space.shading.color_type='MATERIAL'
            if space.region_3d:space.region_3d.view_perspective='CAMERA'

notes=bpy.data.texts.new('R17_READ_ME_FIRST')
notes.write(
'F5ZP R17 FAST UNIVERSAL GOTHIC VAULT WORKSPACE\n'
'Experimental only: no original cathedral mesh or generator replaced.\n'
'Open 3D View Sidebar (N) > R17 Vault for one-click regeneration.\n'
'Switch 3,4,5,6,8 or custom 3-12 sectors and FAST (32)/FINAL (128).\n'
'R16 STRICT: never allow a boss BELOW any measured pointed arch apex.\n'
'Level is valid WITH WARNING because dome rise is diminished.\n'
'Prefer higher boss in NEW unlocked samples; NEVER auto-move locked crown.\n'
'Every build warns of protected geometry and unverified historic scope.\n'
'Review scenes (upper right) share the same one experimental geometry.\n'
'R17_LATEST_COMPLETE_QA.json and R17_LATEST_R16_WARNINGS.json\n'
'are saved in Blender Text Editor, plus QA files per build.\n'
'Only after a valid build: Export GLB and Save Versioned .blend.\n'
'Native 1:1 preview; historical structural capacity NOT validated.\n')
for file in ('r17_core.py','r17_experimental_workspace.py'):
    txt=bpy.data.texts.load(str(ADDON/file),internal=True)
    txt.name='R17_SOURCE_'+file
# First generate and assert guard application before saving new file.
bpy.context.window.scene=master
out=bpy.ops.r17.regenerate()
assert out=={'FINISHED'},'R17 bootstrap generator failed'
assert master.get('r17_last_status')=='VALIDATED_EXPERIMENTAL'
assert int(master.get('r17_build_count'))>=1  # versioned QA ledger may preexist
assert bpy.data.collections.get(r17.GEO_COLLECTION)
assert len(active.objects)==1+r17._config(V).sector_count*2

# Workbench outputs plus preinstalled review cameras.
output=D/'blender/F5ZP_R17_FAST_UNIVERSAL_VAULT_WORKSPACE_V01_EXPERIMENTAL.blend'
assert not output.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
assert output.stat().st_size>30000
records={'status':'R17_WORKSPACE_INITIAL_BLEND_SAVED_EXPERIMENTAL',
 'file':str(output),'addon_registered_during_creation':True,
 'all_review_scenes':[x.name for x in scenes],
 'single_shared_geometry_collection':active.name,
 'live_panel_id':r17.R17_PT_main.bl_idname,
 'source_R16_vendor_SHA_verified':r17.source_snapshot(),
 'first_build_r16_guarded':True,'locked_source_geometry_modified':False}
(D/'qa/R17_BLENDER_WORKSPACE_BOOTSTRAP_QA.json').write_text(json.dumps(records,indent=2))
print('R17_BOOTSTRAP_BLEND_SAVED',output,'scenes',len(scenes),
      'owned_objects',len(active.objects),'initial_status',
      master.get('r17_last_status'),flush=True)
