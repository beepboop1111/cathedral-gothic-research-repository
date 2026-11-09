"""UNIFIED_JUNCTION_INTERFACE_R01 / experimental, non-authoritative.
Read-only R03 scene plus R15 original-backed five-bearing Springer geometry.
A geometry specimen is rendered even when the placement compatibility gate rejects it.
All new objects and exports are isolated in a NEW output directory.
"""
import bpy, json, math, hashlib, pathlib, sys
from mathutils import Vector, Matrix
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path("/home/christopher/Documents/Cathedral/experimental")
OUT = ROOT / "UNIFIED_JUNCTION_INTERFACE_R01"
R03 = ROOT / "WALL_PIER_JUNCTION_R03"
R02 = ROOT / "SHARED_PIERS_R02"
R15 = ROOT / "SPRINGER_JUNCTION_R15"
R17 = ROOT / "SPRINGER_REPRODUCIBLE_R17"
BLEND = R03 / "WALL_PIER_JUNCTION_R03.blend"
GLB = R15 / "original_backing_test/build/springer_variant.glb"
BASE = Vector((31000.0,-1250.0,1800.0))
qa02=json.loads((R02/"QA.json").read_text())
qa03=json.loads((R03/"QA.json").read_text())
m15=json.loads((R15/"original_backing_manifest.json").read_text())
m17=json.loads((R17/"fixture/manifest.json").read_text())
p15=json.loads((R15/"original_backing_inputs.json").read_text())
assert qa02["passed"]==qa02["total"]==50
assert qa03["passed"]==qa03["total"]==59
assert p15["source"]["source_origin"]==list(BASE)
assert len(qa02["contact_metrics"]["S"])==5
expected = {r["source"]:float(r["bearing"]) for r in qa02["contact_metrics"]["S"]}
def signed_delta(a,b):return (a-b+180)%360-180
def assess(manifest):
    members=manifest["members"]
    sources=[m["source_name"] for m in members]
    missing=sorted(set(expected)-set(sources))
    extra=sorted(set(sources)-set(expected))
    edited={}
    for m in members:
        if "bearing_degrees" in m and m["source_name"] in expected:
            edited[m["source_name"]]=round(signed_delta(float(m["bearing_degrees"]),expected[m["source_name"]]),6)
    return dict(count=len(members),expected_count=5,missing=missing,extra=extra,explicit_bearing_delta_degrees=edited,compatible=(not missing and not extra and all(abs(x)<0.005 for x in edited.values()) and len(members)==5))
g15=assess(m15);g17=assess(m17)
assert not g15["compatible"] and not g17["compatible"]
assert "BAY2_FORMERET_0" in g17["missing"]
assert 11.9 < g15["explicit_bearing_delta_degrees"]["BAY2_RIB_0"] < 12.1
assert -4.1 < g17["explicit_bearing_delta_degrees"]["BAY2_RIB_0"] < -3.9
# Exact-metadata positive control; does NOT certify physical springer geometry.
positive=assess({"members":[{"source_name":n,"bearing_degrees":a} for n,a in expected.items()]})
assert positive["compatible"]
source_hash_before=hashlib.sha256(BLEND.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
protected=[o for o in bpy.data.objects if o.type=="MESH"]
protected_names={o.name for o in protected}
def geo_sig(o):
    # Do not use calculated triangulation; hash untouched stored mesh topology/coordinates.
    h=hashlib.sha256()
    for v in o.data.vertices: h.update(("%0.6f,%0.6f,%0.6f;"%tuple(v.co)).encode())
    for f in o.data.polygons: h.update((",".join(map(str,f.vertices))+";").encode())
    return h.hexdigest()
protected_signatures={o.name:geo_sig(o) for o in protected}
# Show source geometry only in bounded S-arch junction, no changes to meshes.
focus_names={"SHARED_PIER_S","BAY1_RIB_1","BAY2_RIB_0","BAY1_FORMERET_0","BAY2_FORMERET_0","CHAPEL_TRANSVERSE_31000"}
for o in protected:
    o.hide_render = (o.name not in focus_names and not o.name.startswith("RECEIVING_S_")) or o.name.startswith("RECEIVING_S_UPPER_")
    if o.hide_render:continue
    o.color=(0.65,0.69,0.72,1) if o.name in focus_names else (0.49,0.53,0.56,1)
    if o.name=="SHARED_PIER_S":o.color=(0.65,0.61,0.52,1)

before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(GLB))
imported=[o for o in bpy.data.objects if o not in before]
assert imported, "R15 GLB import returned no objects"
for o in imported:
    if o.parent not in imported: o.matrix_world=Matrix.Translation(BASE)@o.matrix_world
# Experimental 5-course specimen, overlaid for inspection but deliberately NOT integrated.
for o in imported:
    o.hide_render=not (o.name.startswith("course_") or o.name=="member_2")
    o.color=(0.93,0.67,0.30,1) if o.name.startswith("course_") else (0.85,0.26,0.23,1)
    o["status"]="REJECTED_FOR_CATHEDRAL_INTEGRATION"
    o["source"]="R15 five-bearing; one bearing intentionally edited 12 degrees"
col=bpy.data.collections.new("EXPERIMENTAL_INTERFACE_GUIDES_R01")
bpy.context.scene.collection.children.link(col)
def rod(name,start,end,r,color):
    d=end-start;mid=(start+end)/2
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=mid)
    ob=bpy.context.object;ob.name=name;ob.rotation_euler=d.to_track_quat("Z","Y").to_euler()
    for c in list(ob.users_collection):c.objects.unlink(ob)
    col.objects.link(ob);ob.color=(*color,1.0);return ob
def pointer(name,angle,radius,rgb,z=2180):
    p=BASE+Vector((0,0,z-BASE.z))
    v=Vector((math.cos(math.radians(angle)),math.sin(math.radians(angle)),0))
    rod(name+"_SHAFT",p,p+v*radius,6,rgb)
    bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=17,radius2=0,depth=45,location=p+v*(radius+17))
    ob=bpy.context.object;ob.name=name+"_TIP";ob.rotation_euler=v.to_track_quat("Z","Y").to_euler()
    for c in list(ob.users_collection):c.objects.unlink(ob)
    col.objects.link(ob);ob.color=(*rgb,1.0)
for name,az in expected.items():
    if name=="BAY2_RIB_0": continue
    pointer("SOURCE_"+name,az,225,(0.32,0.74,0.82),z=2080)
pointer("SOURCE_RIB2_NATIVE_46",expected["BAY2_RIB_0"],430,(0.14,0.8,0.65),z=2250)
pointer("R15_EDITED_RIB2_58",float(next(m for m in m15["members"] if m["source_name"]=="BAY2_RIB_0")["bearing_degrees"]),430,(0.96,0.16,0.14),z=2250)
# Geometry preservation in-memory and source-file preservation on disk.
assert len(protected_signatures)==len(protected)==247
assert all(geo_sig(o)==protected_signatures[o.name] for o in protected)
assert hashlib.sha256(BLEND.read_bytes()).hexdigest()==source_hash_before
# Export only the isolated NEW specimen, not cathedral reference meshes.
new_meshes=[o for o in imported if o.type=="MESH" and o.name.startswith("course_")]
assert len(new_meshes)==5
bpy.ops.object.select_all(action="DESELECT")
for o in new_meshes:o.select_set(True)
bpy.context.view_layer.objects.active=new_meshes[0]
exp=OUT/"INTERFACE_SPECIMEN_R01.glb"
bpy.ops.export_scene.gltf(filepath=str(exp),export_format="GLB",use_selection=True)
initial_bounds={o.name:(tuple(round(c,3) for c in o.matrix_world.translation),tuple(round(x,3) for x in o.dimensions)) for o in new_meshes}
bpy.ops.import_scene.gltf(filepath=str(exp))
roundtrip=[o for o in bpy.data.objects if o.name.endswith(".001") and o.name.split(".001")[0] in initial_bounds]
# Additional imported objects must be hidden from review, and round-trip existence recorded.
for o in roundtrip:o.hide_render=True
roundtrip_count=len(roundtrip)
assert roundtrip_count==len(new_meshes),(roundtrip_count,len(new_meshes))
print("ROUNDTRIP_TRANSFORMS",[(o.name,tuple(round(v,3) for v in o.matrix_world.translation),tuple(round(v,3) for v in new_meshes[[x.name for x in new_meshes].index(o.name.removesuffix(".001"))].matrix_world.translation)) for o in roundtrip])
assert all((o.matrix_world.translation-new_meshes[[x.name for x in new_meshes].index(o.name.removesuffix(".001"))].matrix_world.translation).length < .02 for o in roundtrip)
# Rendering setup. Source scene saved separately and never overwritten.
sc=bpy.context.scene
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.light="STUDIO";sc.display.shading.color_type="OBJECT"
sc.display.shading.show_cavity=True;sc.display.shading.cavity_type="BOTH"
sc.world.color=(0.84,0.86,0.87)
bpy.ops.object.camera_add(location=(32750,-4300,3900))
cam=bpy.context.object
cam.rotation_euler=(Vector((31000,-1250,2350))-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.type="ORTHO";cam.data.ortho_scale=3000;cam.data.clip_end=1000000
sc.camera=cam
sc.render.resolution_x=1500;sc.render.resolution_y=1080;sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
raw=OUT/"JUNCTION_R01_RENDER_RAW.png";sc.render.filepath=str(raw)
bpy.ops.render.render(write_still=True)
# Save a new experiment only. Never modify R03's working BLEND.
saved=OUT/"UNIFIED_JUNCTION_INTERFACE_R01_EXPERIMENTAL.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(saved))
img=Image.open(raw).convert("RGB")
draw=ImageDraw.Draw(img,"RGBA")
font_title=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",23)
font_body=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",17)
draw.rounded_rectangle((25,20,1475,133),radius=15,fill=(26,38,51,234))
draw.text((45,37),"UNIFIED GOTHIC JUNCTION  |  R01 EXPERIMENTAL",fill=(255,255,255),font=font_title)
draw.text((45,80),"R03 SOUTH PIER + R15 SPRINGER / 1:1 NATIVE UNITS",fill=(220,232,238),font=font_body)
draw.rounded_rectangle((24,890,1475,1060),radius=16,fill=(27,40,52,234))
draw.text((45,910),"GREEN  Native rib bearing 46.169°      RED  R15 profile bearing 58.169°",fill=(246,246,246),font=font_body)
draw.text((45,947),"R15 REJECTED: +12.000°       R17 REJECTED: missing fifth bearing, -4.000°",fill=(255,176,160),font=font_body)
draw.text((45,984),"Gold: R15 experimental courses. Upper wall hidden for visibility; no integration approval.",fill=(235,235,235),font=font_body)
draw.text((45,1021),"247 R03 meshes preserved  |  GLB round-trip passed  |  F5ZL-C / capacity unresolved",fill=(210,221,229),font=font_body)
out_image=OUT/"UNIFIED_JUNCTION_R01_FINAL.png"
img.save(out_image,optimize=True)
report=dict(revision="UNIFIED_JUNCTION_INTERFACE_R01_EXPERIMENTAL",runtime=bpy.app.version_string,base_scene=str(BLEND),base_sha256_before_after=source_hash_before,protected_meshes_unchanged=len(protected),source_spring_xyz=list(BASE),actual_five_bearings=expected,positive_control=positive,r15_gate=g15,r17_gate=g17,r15_glb_courses=len(new_meshes),glb_export_reimport_count=roundtrip_count,glb_status="ROUNDTRIP_TESTED_EXPERIMENTAL_ONLY",r03_recorded_checks=qa03["passed"],r02_recorded_checks=qa02["passed"],cathedral_integration="BLOCKED_MISMATCH",architectural_approval=False,historical_approval=False,structural_capacity_approval=False,physical_scale="1:1 numerical native units; SI unresolved",profile_policy="user-selected; no substitution or automatic bearing repair",limits=["R15 source bearing edited +12 degrees","R17 missing one of five receiving members","No current five-bearing generator output with five exact canonical bearings","Existing wall/springer full 3D contact not signed off","F5ZL-C support schedule missing","Not tested Blender 5.1+"],png=str(out_image),blend=str(saved),glb=str(exp))
(OUT/"INTERFACE_QA.json").write_text(json.dumps(report,indent=2))
print("UNIFIED_R01_COMPLETE",json.dumps({k:report[k] for k in ["protected_meshes_unchanged","r15_gate","r17_gate","glb_export_reimport_count","cathedral_integration","png"]}))
