#!/usr/bin/env python3
"""M04 P04 R02 comparative Blender scene: A unmodified source shoulder,
B 80-native-unit NON-APPROVED backing wedge.
Original R03 and source-generated five-course R14 are never overwritten.
Output: one final comparison PNG plus isolated experimental GLB and .blend.
"""
from pathlib import Path
import bpy,bmesh,hashlib,json,math
from mathutils import Vector,Matrix
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
SRC=R/"M04_P03_R06_ALL_FIVE_ORIGINAL_ARCHES_SOURCE_MATCHED_EXPERIMENTAL/M04_P03_R06_R03_SOURCE_MATCHED_FIVE_MEMBER_CUTAWAY_EXPERIMENTAL.blend"
KEY=R/"M04_P04_R01_SHOULDER_OR_TAPERED_BACKING_STUDIES_EXPERIMENTAL/M04_P04_R01_EXPERIMENTAL_80_UNIT_TAPERED_BACKING_KEY.glb"
Q=R/"M04_P04_R01_SHOULDER_OR_TAPERED_BACKING_STUDIES_EXPERIMENTAL/M04_P04_R01_BACKING_STUDY_NUMERICAL_QA.json"
protected=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
O=R/"M04_P04_R02B_BLENDER_AXIS_ALIGNED_BACKING_ALTERNATIVES_EXPERIMENTAL"
assert not O.exists(),"Prior revision protected"
O.mkdir()
inputs=[SRC,KEY,Q,protected]
assert all(f.is_file() for f in inputs)
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
q=json.loads(Q.read_text())
bpy.ops.wm.open_mainfile(filepath=str(SRC))
all_before=[o for o in bpy.data.objects if o.type=="MESH"]
assert len(all_before)==14,len(all_before)
cam=bpy.context.scene.camera
assert cam
focus=Vector((31000.,-1200.,2445.))
cam.location=focus+Vector((500,940,445))
cam.rotation_euler=(focus-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.type="ORTHO"
cam.data.ortho_scale=800
cam.data.clip_start=.1
cam.data.clip_end=20000
sc=bpy.context.scene
sc.camera=cam
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.color_type="MATERIAL"
sc.display.shading.light="STUDIO"
sc.display.shading.show_cavity=True
sc.display.shading.show_shadows=True
sc.render.resolution_x=1120
sc.render.resolution_y=960
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.view_settings.view_transform="Standard"
# Scene A: source original five arch meshes plus source-restored five
# experimental courses, WITHOUT speculative backing.
sc.render.filepath=str(O/"A_SOURCE_SHOULDER_RENDER_INTERNAL.png")
bpy.ops.render.render(write_still=True)
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(KEY))
additional=[o for o in bpy.data.objects if o not in before and o.type=="MESH"]
assert len(additional)==1,[(x.name,x.type) for x in additional]
wedge=additional[0]
# Trimesh's native Z-up GLB is converted by Blender's glTF Y-up importer
# to (x,-z,y). Apply the measured inverse axis map (x,z,-y) explicitly.
# World-space x retains 1:1 absolute cathedral coordinates.
wedge.matrix_world=Matrix.Rotation(-math.pi/2,4,"X")@wedge.matrix_world
wedge["geometry_import_correction"]="Measured source Z-up -> Blender Z-up: rotate -90 degrees around global X"
wedge.name="R04B_EXPERIMENTAL_UNCERTAIN_BACKING_CAP_80_NATIVE"
wedge["status"]="EXPERIMENTAL CONSTRUCTION ALTERNATIVE ONLY"
wedge["source_5_bearings_and_3D_ribs_unchanged"]=True
wedge["source_78_R14_QA_unchanged"]=True
wedge["masonry_bond_to_R03_wall_verified"]=False
wedge["structural_capacity_verified"]=False
def bounds(obj):
 pts=[obj.matrix_world@Vector(p) for p in obj.bound_box]
 return [[min(v[k] for v in pts),max(v[k] for v in pts)] for k in range(3)]
bb=bounds(wedge)
expected=[[30890.887,31101.974],[-1250.,-1184.483],[2400.,2480.]]
assert all(abs(bb[k][j]-expected[k][j])<.1 for k in range(3) for j in range(2)),bb
mat=bpy.data.materials.new("Experimental CAP B • copper / provisional")
mat.diffuse_color=(.96,.35,.11,1)
wedge.data.materials.clear()
wedge.data.materials.append(mat)
# Scene B same camera and source; only wedge visible.
sc.render.filepath=str(O/"B_UNAPPROVED_BACKING_RENDER_INTERNAL.png")
bpy.ops.render.render(write_still=True)
# Save output after render; the reference original file stays byte-identical.
sc["M04_P04_approval"]="EXPERIMENTAL ONLY"
sc["M04_P04_Source_SHOULDER_1TO1_geometry"]="PROTECTED 5 source arch meshes"
sc["M04_P04_class_A"]="Retain source exposed shoulder without filling it"
sc["M04_P04_class_B"]="Add separate 80-unit taper with no original mesh edits"
sc["M04_P04_backing_bond_to_original_wall"]="UNVERIFIED"
sc["M04_P04_source_99_planar_contact_checks"]="PASS against original 5 arch and wall source"
sc["M04_P04_wedge_3D_watertight"]="PASS"
sc["M04_P04_F5ZL_C_schedule"]="UNRESOLVED"
scene_path=O/"M04_P04_R02_BACKING_ALTERNATIVES_EDITABLE_EXPERIMENTAL.blend"
glb_path=O/"M04_P04_R02_EXPERIMENTAL_FIVE_ARCHES_WITH_UNAPPROVED_WEDGE.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(scene_path))
bpy.ops.object.select_all(action="DESELECT")
objects=[o for o in bpy.data.objects if o.type=="MESH"]
assert len(objects)==15,len(objects)
for obj in objects:obj.select_set(True)
bpy.context.view_layer.objects.active=wedge
bpy.ops.export_scene.gltf(filepath=str(glb_path),export_format="GLB",use_selection=True)
assert glb_path.read_bytes()[:4]==b"glTF"
# Difference illustration: same original scene and camera, without any
# extra rotations/scaling or substituted Gothic profile.
W,H=2320,1248
out=Image.new("RGB",(W,H),(245,247,250))
draw=ImageDraw.Draw(out)
fonts="/usr/share/fonts/truetype/dejavu"
title=ImageFont.truetype(fonts+"/DejaVuSans-Bold.ttf",29)
heading=ImageFont.truetype(fonts+"/DejaVuSans-Bold.ttf",24)
body=ImageFont.truetype(fonts+"/DejaVuSans.ttf",19)
small=ImageFont.truetype(fonts+"/DejaVuSans.ttf",17)
draw.rectangle((0,0,W,94),fill=(26,45,57))
draw.text((26,13),"M04 P04 | Gothic five-bearing upper backing: measured alternatives",font=title,fill=(241,249,252))
draw.text((28,58),"Both show real R03 arch surfaces and source-restored R14 courses | 1:1 geometry, fixed matching view",font=small,fill=(184,216,226))
for idx,(label,desc,imgfile) in enumerate((
 ("A  /  SOURCE SHOULDER RETAINED",
  "No additional masonry; shoulder remains exposed",
  O/"A_SOURCE_SHOULDER_RENDER_INTERNAL.png"),
 ("B  /  EXPERIMENTAL TAPERED CAP",
  "80-unit backing hypothesis; no original source altered",
  O/"B_UNAPPROVED_BACKING_RENDER_INTERNAL.png"))):
 x=25+idx*1150
 draw.rectangle((x,105,x+1120,1136),fill=(255,255,255),outline=(184,196,205),width=2)
 draw.rectangle((x+4,110,x+1116,158),fill=(58,90,112) if idx==0 else (151,73,44))
 draw.text((x+22,119),label,font=heading,fill=(255,255,255))
 draw.text((x+24,164),desc,font=small,fill=(70,80,88))
 with Image.open(imgfile) as i:
  assert i.size==(1120,960)
  picture=ImageOps.fit(i.convert("RGB"),(1100,914))
  out.paste(picture,(x+10,205))
draw.text((30,1151),f"Exposed source shoulder: {q['source_main_exposed_shoulder_area_native_sq']:,.1f} native²     |     Projection: {q['max_shoulder_outward_offset_native']:.2f} native",font=body,fill=(33,61,79))
draw.text((30,1182),"B: 99/99 sampled geometry contact/clearance checks, but ashlar bonding & structural capacity UNVERIFIED.",font=body,fill=(128,49,47))
draw.text((30,1211),"Approval: EXPERIMENTAL ONLY — upper R03 wall coordination below Z2400 and missing F5ZL-C schedule remain unresolved.",font=small,fill=(91,99,111))
png=O/"F5ZP_M04_P04_R02_ONE_BACKING_ALTERNATIVE_REVIEW.png"
out.save(png,optimize=True)
with Image.open(png) as img:assert img.size==(W,H);img.verify()
# Independent GLB reimport: reference cutaway pieces are intentionally
# open as sections; new wedge alone was checked watertight independently.
before_reimport=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(glb_path))
check=[o for o in bpy.data.objects if o not in before_reimport and o.type=="MESH"]
assert len(check)==15,len(check)
assert any("R04B_EXPERIMENTAL_UNCERTAIN" in o.name for o in check)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in inputs)
qa={
 "Blender_version":bpy.app.version_string,
 "source_14_reference_meshes_unchanged_in_original_blend":True,
 "reimported_complete_review_GLTF_geometry_count":len(check),
 "experimental_tapered_new_mesh_count":1,
 "source_protected_arch_meshes_count":5,
 "B_backing_fits_absolute_native_bounds":bb,
 "B_wedge_GLTF_geometry_watertight_previously_verified":True,
 "source_Original_files_SHA256":sha,
 "one_review_PNG":png.name,
 "source_shoulder_fill_required":"NOT ESTABLISHED",
 "B_unapproved_architectural_and_structural":True,
 "final_experimental_blend":scene_path.name,
 "final_experimental_glb":glb_path.name}
(O/"M04_P04_R02_BLENDER_VIEW_AND_GLTF_REIMPORT_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
print("M04_P04_R02_SOURCE_AND_3D_PREVIEW_PASS",len(check),"meshes","FINAL",png)
