#!/usr/bin/env python3
"""Create NEW R18 live Blender file from frozen R17 V02, without saving to R17."""
import bpy,sys,pathlib,hashlib,shutil,json
HERE=pathlib.Path(__file__).resolve().parents[1]
R17=pathlib.Path("/home/christopher/Downloads/F5ZP_UNIVERSAL_GOTHIC_VAULT_GENERATOR_R01_EXPERIMENTAL/experiments/F5ZP_R17_FAST_UNIVERSAL_VAULT_WORKSPACE_EXPERIMENTAL")
source=R17/"blender/F5ZP_R17_FAST_VAULT_WORKSPACE_REVIEW_READY_V02_EXPERIMENTAL.blend"
dest=HERE/"blender/F5ZP_R18_SKELETON_FIRST_LIVE_V01_EXPERIMENTAL.blend"
if dest.exists():raise FileExistsError("R18 V01 already exists: "+str(dest))
checks=[source,R17/"addon/r17_core.py",R17/"addon/r17_experimental_workspace.py",
        R17/"addon/r17_vendor/strict_crown_guard.py",
        R17/"addon/r17_vendor/guarded_vault_adapter.py"]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p) for p in checks}
# Install only the separately named R18 addon; no R17 or unrelated addon changed.
addons=pathlib.Path(bpy.utils.user_resource("SCRIPTS",path="addons",create=True))
src=HERE/"addon/r18_live.py";target=addons/"r18_live.py"
if target.exists() and sha(target)!=sha(src):raise FileExistsError("Different installed R18 addon; no overwrite")
if not target.exists():shutil.copy2(src,target)
if str(addons) not in sys.path:sys.path.insert(0,str(addons))
sys.path.insert(0,str(HERE))
bpy.ops.preferences.addon_enable(module="r17_experimental_workspace")
bpy.ops.preferences.addon_enable(module="r18_live")
assert "r18_live" in bpy.context.preferences.addons
bpy.ops.wm.save_userpref()
import r18_live as r18
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
r18.register()
master=bpy.data.scenes["R17_WORKSPACE"]
old=bpy.data.collections.get("R17_EXPERIMENTAL_GEOMETRY")
assert old is not None
# Hide earlier R17 presentation in only this NEW copied workspace.
old.hide_render=True
old.hide_viewport=True
p=master.r17_props
p.vault_type="QUAD";p.quality="FINAL";p.crown_mode="AUTO"
p.crown_locked=False;p.irregularity=0.;p.radius=1200.
p.spring_z=3000.;p.arch_rise_ratio=.72
p.meridian_exponent=1.75;p.dome_lift=.3
p.cap_enabled=False
bpy.context.window.scene=master
result=bpy.ops.r18.regenerate()
assert result=={"FINISHED"},result
assert master["r18_status"]=="VALIDATED_SYNTHETIC"
active=bpy.data.collections["R18_ACTIVE_GEOMETRY"]
assert len([o for o in active.objects if o.type=="MESH"])==1
assert len(active.objects)==1+2*4
export=bpy.ops.r18.export_glb()
assert export=={"FINISHED"},export
# Store editable new R18 source in Text Editor for transparent reproduction.
for name in ("r18_core.py","addon/r18_live.py","scripts/run_R18_validation.py"):
    txt=bpy.data.texts.load(str(HERE/name),internal=True)
    txt.name="R18_EXPERIMENTAL_"+pathlib.Path(name).name
notes=bpy.data.texts.new("R18_READ_ME_FIRST")
notes.write("R18 SKELETON FIRST / EXPERIMENTAL ONLY\n"
 "R16 strict crown & original hashes checked before/after each build.\n"
 "Press N in 3D viewport, use R18 Vault sidebar to regenerate.\n"
 "R18 ribs are mathematically independent circular groins.\n"
 "Thin colored lines are GUIDES, not finished Gothic rib sections.\n"
 "R17 V02 remains preserved in separate file; hidden in this copied scene.\n"
 "GLB exports only the validated open web. No physical masonry certification.\n"
 "F5ZN-A, V13, Pass 6J, F5ZK-C unchanged. F5ZL-C unresolved.\n")
master["r18_baseline"]="F5ZP R17 V02 reference; physical architecture not imported"
master["r18_status"]="VALIDATED_SYNTHETIC"
master["r18_experiment_root"]=str(HERE)
# Review cameras are inherited; all four share ONE active collection.
review=[]
for scene_name,label in [("R17_REVIEW_AXON","axon"),
                          ("R17_REVIEW_PLAN","plan"),
                          ("R17_REVIEW_INTERIOR","underside"),
                          ("R17_REVIEW_SECTION","section")]:
    sc=bpy.data.scenes[scene_name]
    sc.render.engine="BLENDER_WORKBENCH"
    sc.render.resolution_x=1280;sc.render.resolution_y=840
    sc.render.resolution_percentage=100
    sc.render.image_settings.file_format="PNG"
    sc.render.filepath=str(HERE/"review"/("R18_"+label+".png"))
    bpy.context.window.scene=sc
    bpy.ops.render.render(write_still=True)
    output=pathlib.Path(sc.render.filepath)
    if output.stat().st_size<5000:raise RuntimeError("RENDER_TOO_SMALL "+label)
    review.append({"scene":scene_name,"path":str(output),"bytes":output.stat().st_size})
bpy.context.window.scene=master
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
assert dest.stat().st_size>30000
after={str(p):sha(p) for p in checks}
assert before==after,"R17 frozen sources changed!"
record={"status":"R18_LIVE_BLENDER_V01_VALIDATED_EXPERIMENTAL",
 "source_R17_V02_hash_preserved":before==after,
 "source_R17_and_R16_SHA256":before,
 "new_R18_blend":str(dest),"new_R18_blend_SHA256":sha(dest),
 "addon_installed":str(target),"addon_enabled":True,
 "glb_exported":str(HERE/"outputs"/f"R18_BUILD_{master['r18_build_count']:03d}_WEB_ONLY_1TO1.glb"),
 "review_cameras":review,"generator_r18_distinct_from_approved":True,
 "architectural_validation":False,"historical_validation":False,"structural_validation":False}
out=HERE/"qa/R18_LIVE_BLENDER_BOOTSTRAP_QA.json"
with out.open("x") as f:json.dump(record,f,indent=2)
print("R18_LIVE_V01_SAVED",dest,"RENDERS",len(review),"R17_BASELINE_HASHES_UNCHANGED",flush=True)
