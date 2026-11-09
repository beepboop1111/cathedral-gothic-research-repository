import bpy
import json
import hashlib
import sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,"/home/christopher/Desktop/F5ZP_M01_R29_LIVE_AXIAL_EXPERIMENTAL_20261105")
import f5zp_live_axial as live

BASE=Path("/home/christopher/Desktop/F5ZP_M01_R29_LIVE_AXIAL_EXPERIMENTAL_20261105")
R28=Path("/home/christopher/Desktop/F5ZP_M01_R28_AXIAL_JUNCTION_EXPERIMENTAL_20261105/R28_AXIAL_JUNCTION_EXPERIMENTAL.blend")
OUT=BASE/"R29_LIVE_AXIAL_JUNCTION_EXPERIMENTAL_V01.blend"
addon=BASE/"f5zp_live_axial.py"
scene=bpy.context.scene
bpy.ops.preferences.addon_enable(module='f5zp_live_axial')
bpy.ops.wm.save_userpref()

print("R29_BOOTSTRAP_INITIAL_OBJECTS",len(scene.objects),flush=True)
assert len(scene.objects)==60,"Expected source R28 59 geometry + camera"
old_names=set(scene.objects.keys())

# Do not delete or alter the saved R28 study: only change this independent copy.
ref=live.collection(scene,live.REF_COLL)
view=live.collection(scene,"95_R29_WORKING_VIEW")
for coll in list(scene.collection.children):
    if coll.name not in (live.REF_COLL,live.GEN_COLL,view.name):
        scene.collection.children.unlink(coll)
        ref.children.link(coll)
for obj in list(scene.collection.objects):
    scene.collection.objects.unlink(obj)
    ref.objects.link(obj)
ref.hide_select=True

assert set(o.name for o in live.reference_objects(scene))==old_names
scene[live.MANIFEST_KEY]=live.reference_signature(scene)
scene["R29_SOURCE_R28_SHA256"]=hashlib.sha256(R28.read_bytes()).hexdigest()
scene["R29_SOURCE_PATH"]=str(R28)
scene["R29_NOTE"]="R28 geometry is copied only; no automatic promotion; F5ZL-C remains unresolved."
scene["R29_ARCHITECTURAL_STATUS"]="EXPERIMENTAL_OPEN"
scene["R29_STRUCTURAL_STATUS"]="NOT_VALIDATED"
scene["R29_PHYSICAL_CONVERSION"]="UNRESOLVED; native units 1:1"
scene["R29_REFERENCE_COUNT"]=len(old_names)

# New view camera is independent of protected R28 camera and meshes.
camera_data=bpy.data.cameras.new("R29_AXIAL_VIEW_CAMERA")
cam=bpy.data.objects.new("R29_AXIAL_VIEW_CAMERA",camera_data)
view.objects.link(cam)
cam.location=(29500,-6750,7000)
target=Vector((26700,0,3000))
cam.rotation_euler=(target-Vector(cam.location)).to_track_quat("-Z","Y").to_euler()
camera_data.type="ORTHO"
camera_data.ortho_scale=7600
scene.camera=cam
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=="VIEW_3D":
            space=area.spaces.active
            space.shading.type="SOLID"
            space.shading.color_type="MATERIAL"
            space.shading.light="STUDIO"
            space.shading.show_cavity=True
            space.clip_end=1000000
            space.region_3d.view_location=target
            space.region_3d.view_distance=6300
            space.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
            space.region_3d.view_perspective="PERSP"

# Retain the full source of the active add-on inside the blend for recovery.
text=bpy.data.texts.get("R29_LIVE_AXIAL_ADDON_SOURCE.py") or bpy.data.texts.new("R29_LIVE_AXIAL_ADDON_SOURCE.py")
text.clear()
text.write(addon.read_text())
text.use_module=False

before=live.reference_signature(scene)
first=live.do_rebuild(scene)
generated=bpy.data.collections.get(live.GEN_COLL)
first_names=sorted(o.name for o in generated.objects)
assert first==17 and all(not name.endswith(".001") for name in first_names)
second=live.do_rebuild(scene)
second_names=sorted(o.name for o in generated.objects)
assert first_names==second_names and second==17
assert before==live.reference_signature(scene)
original_p=scene.f5zp_axial.longitudinal_lift
scene.f5zp_axial.longitudinal_lift=original_p+90
live.do_rebuild(scene)
height_changed=scene["R29_CROWN_ESTIMATE"]
scene.f5zp_axial.longitudinal_lift=original_p
live.do_rebuild(scene)
height_restored=scene["R29_CROWN_ESTIMATE"]
assert abs(height_changed-height_restored-90)<0.001
assert before==live.reference_signature(scene)
assert len(live.reference_objects(scene))==len(old_names)
assert all(o.get("F5ZP_OWNER")==live.OWNER for o in generated.objects)

scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.color_type="MATERIAL"
scene.render.resolution_x=1260
scene.render.resolution_y=940
scene.render.resolution_percentage=100
scene.render.filepath=str(BASE/"R29_LIVE_AXIAL_PREVIEW.png")
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
print("R29_SAVED",OUT,flush=True)

checks={
 "status":"EXPERIMENTAL_ONLY_NOT_APPROVED",
 "reference_object_count":len(old_names),
 "generated_object_count":len(generated.objects),
 "baseline_sha256":before,
 "baseline_is_unchanged":before==live.reference_signature(scene),
 "r28_input_sha256":scene["R29_SOURCE_R28_SHA256"],
 "r28_original_still_matches":hashlib.sha256(R28.read_bytes()).hexdigest()==scene["R29_SOURCE_R28_SHA256"],
 "two_rebuilds_keep_exact_object_names":first_names==second_names,
 "parameter_change_updates_crown":height_changed-height_restored==90.0,
 "generated_object_names":second_names,
 "parameters":{k:getattr(scene.f5zp_axial,k) for k in ("inner_x","center_y","radial_span","half_width","inner_spring","outer_spring","transverse_rise","longitudinal_lift","web_thickness","rib_radius","receiver_depth","receiver_width","samples")},
 "source_units":"native 1:1; physical conversion unresolved",
 "unresolved":["F5ZL-C receiving masonry / bearing schedule","No structural or architectural approval","Provisional V13 web interface","B chapel configuration remains experimental"]
}
(BASE/"R29_LIVE_QA.json").write_text(json.dumps(checks,indent=2))
print("R29_QA",json.dumps({k:checks[k] for k in ("reference_object_count","generated_object_count","baseline_is_unchanged","two_rebuilds_keep_exact_object_names","parameter_change_updates_crown")}),flush=True)
bpy.ops.render.render(write_still=True)
print("R29_PREVIEW_DONE",flush=True)
