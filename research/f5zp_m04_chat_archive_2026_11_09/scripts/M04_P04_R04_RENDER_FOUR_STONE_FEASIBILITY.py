#!/usr/bin/env python3
"""F5ZP M04 P04 R04 — one final PNG comparing unmodified exposed source
shoulder with four experimental, CONSTRUCTION-REJECTED tapered ashlar courses.
Only the image hides the 5 protected R03 arches during B render. GLB and
saved .blend preserve all arches and all 5 source-based original tas courses.
"""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
X=R/"M04_P04_R02C_FINAL_SOURCE_AND_SEPARATED_WEDGE_VISUAL_EXPERIMENTAL"
C=R/"M04_P04_R03_FOUR_STONE_COURSE_THICKNESS_AND_JOINT_EXPERIMENTAL"
G=C/"M04_P04_R03_FOUR_SEPARATE_EXPERIMENTAL_TAPERED_BACKING_STONES.glb"
R02=X/"M04_P04_R02C_ALL_FIVE_ARCHES_RESTORED_SOURCE_AND_EXPERIMENTAL_KEY.blend"
QA=C/"M04_P04_R03_FOUR_STONE_SEAM_AND_THIN_TIP_QA.json"
S=R/"M04_P04_R01_SHOULDER_OR_TAPERED_BACKING_STUDIES_EXPERIMENTAL/M04_P04_R01_BACKING_STUDY_NUMERICAL_QA.json"
A=R/"M04_P04_R02B_BLENDER_AXIS_ALIGNED_BACKING_ALTERNATIVES_EXPERIMENTAL/A_SOURCE_SHOULDER_RENDER_INTERNAL.png"
O=R/"M04_P04_R04_FINAL_FOUR_STONE_CONSTRUCTABILITY_REVIEW_EXPERIMENTAL"
assert not O.exists(),"Existing report protected"
O.mkdir()
inputs=[G,R02,QA,S,A]
assert all(p.exists() for p in inputs)
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
q=json.loads(QA.read_text())
p=json.loads(S.read_text())
assert q["individual_watertight_source_stones"]==4 and q["all_3_shared_bedding_profiles_match"]
bpy.ops.wm.open_mainfile(filepath=str(R02))
orig=[o for o in bpy.data.objects if o.type=="MESH"]
assert len(orig)==15
wedge=bpy.data.objects["R04B_EXPERIMENTAL_UNCERTAIN_BACKING_CAP_80_NATIVE"]
bpy.data.objects.remove(wedge,do_unlink=True)
baseline=[o for o in bpy.data.objects if o.type=="MESH"]
assert len(baseline)==14
prior=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(G))
added=[o for o in bpy.data.objects if o not in prior and o.type=="MESH"]
assert len(added)==4,[(o.name,o.type) for o in added]
# Correct measured Blender glTF rotation from native Z-up Trimesh GLB.
colors=[(.76,.55,.37),(.83,.47,.29),(.72,.37,.27),(.51,.27,.22)]
def bbox(ob):
 pts=[ob.matrix_world@Vector(x) for x in ob.bound_box]
 return [[round(min(v[k] for v in pts),6),round(max(v[k] for v in pts),6)] for k in range(3)]
for i,ob in enumerate(sorted(added,key=lambda o:o.name)):
 ob.matrix_world=Matrix.Rotation(-math.pi/2,4,"X")@ob.matrix_world
 ob.name=f"P04_HYPOTHETICAL_BACKING_COURSE_{i+1:02d}_Z{2400+i*20}"
 bb=bbox(ob)
 assert abs(bb[2][0]-(2400+i*20))<.05
 assert abs(bb[2][1]-(2420+i*20))<.05
 mat=bpy.data.materials.new(f"P04 four-course feasibility test {i+1}")
 mat.diffuse_color=(*colors[i],1)
 ob.data.materials.clear();ob.data.materials.append(mat)
 ob["source_architectural_approval"]="WITHHELD; simulated tapered cap only"
 ob["original_R03_bonding_verified"]=False
 ob["thin_upper_tip_will_be_rejected"]=i==3
names=("CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0","BAY1_FORMERET_0","BAY2_FORMERET_0")
assert all(n in bpy.data.objects for n in names)
# B image hides all five true source ribs to reveal construction course seams;
# saved scene returns to fully visible protected 5 original rib/arch pieces.
priorhide={n:bpy.data.objects[n].hide_render for n in names}
try:
 for n in names:bpy.data.objects[n].hide_render=True
 bpy.context.scene.render.filepath=str(O/"B_FOUR_COURSES_WITH_SOURCE_RIBS_TEMP_HIDDEN.png")
 bpy.context.scene.render.resolution_x=1120
 bpy.context.scene.render.resolution_y=960
 bpy.context.scene.render.resolution_percentage=100
 bpy.ops.render.render(write_still=True)
finally:
 for n in names:bpy.data.objects[n].hide_render=priorhide[n]
assert all(not bpy.data.objects[n].hide_render for n in names)
scene=bpy.context.scene
scene["M04_P04_R04"]="Four 20-unit stone course thought experiment; rejected for architectural constructability"
scene["original_5_R03_arches"]='PROTECTED SOURCE; only hidden for B image'
scene["original_5_R14_tas_courses"]='PROTECTED SOURCE-RESTORED; preserved'
scene["R04_B_stone_bedding_test"]="4/4 watertight, 3/3 common horizontal profiles match; poor top wedge slenderness"
scene["last_taper_course_projection_native"]=q["last_stone_top_projection_native"]
scene["masonry_bonded_into_R03_wall"]=False
scene["architectural_approval"]=False
scene["historical_approval"]=False
scene["structural_approval"]=False
scene["F5ZL_C_support_schedule"]="MISSING"
blend=O/"M04_P04_R04_FIVE_ORIGINAL_ARCHES_AND_FOUR_HYPOTHETICAL_STONES_EXPERIMENTAL.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
objects=[o for o in bpy.data.objects if o.type=="MESH"]
assert len(objects)==18
for ob in bpy.data.objects:ob.select_set(False)
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=added[0]
glb=O/"M04_P04_R04_FIVE_ARCHES_AND_FOUR_SEPARATE_TEST_STONES_EXPERIMENTAL.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True)
assert glb.read_bytes()[:4]==b"glTF"
pre=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(glb))
readback=[o for o in bpy.data.objects if o not in pre and o.type=="MESH"]
assert len(readback)==18,(len(readback),[x.name for x in readback])
# Comparison image: A full source and B temporarily hiding only source ribs.
out=Image.new("RGB",(2320,1500),(247,248,250))
draw=ImageDraw.Draw(out)
font="/usr/share/fonts/truetype/dejavu/"
bold=lambda pt:ImageFont.truetype(font+"DejaVuSans-Bold.ttf",pt)
regular=lambda pt:ImageFont.truetype(font+"DejaVuSans.ttf",pt)
draw.rectangle((0,0,2320,95),fill=(24,43,56))
draw.text((27,10),"M04 P04 | Four-course Gothic backing study — construction feasibility",font=bold(30),fill=(245,250,252))
draw.text((27,57),"All five original arch sections and five lower tas courses retained in saved Blender/GLB. No protected source modifications.",font=regular(18),fill=(192,220,225))
for i,(title,subtitle,photo,color) in enumerate((
 ("A · SOURCE SHOULDER RETAINED","Full original R03 five arch silhouettes, no added masonry",A,(52,89,113)),
 ("B · FOUR PROVISIONAL ASHLAR COURSES","Five Gothic arch references hidden in image to expose candidate bedding",O/"B_FOUR_COURSES_WITH_SOURCE_RIBS_TEMP_HIDDEN.png",(139,74,54)))):
 x=23+1150*i
 draw.rounded_rectangle((x,105,x+1128,1118),radius=10,fill=(255,255,255),outline=(188,200,210),width=2)
 draw.rectangle((x+4,108,x+1124,158),fill=color)
 draw.text((x+20,118),title,font=bold(23),fill=(255,255,255))
 draw.text((x+20,166),subtitle,font=regular(17),fill=(63,77,88))
 with Image.open(photo) as im:
  assert im.size==(1120,960)
  photores=ImageOps.fit(im.convert("RGB"),(1104,916),method=Image.Resampling.LANCZOS)
  out.paste(photores,(x+12,198))
draw=ImageDraw.Draw(out)
draw.rectangle((21,1136,2299,1486),fill=(255,255,255),outline=(190,201,209),width=2)
draw.text((44,1152),"Numerical contact & constructability assessment",font=bold(25),fill=(25,48,66))
draw.text((44,1199),f"Protected upper shoulder = {p['source_main_exposed_shoulder_area_native_sq']:,.2f} native²;  cap base matches that original geometric silhouette.",font=regular(21),fill=(53,81,92))
draw.text((44,1240),"Four candidate stone blocks: 4/4 watertight • 3/3 bed contacts identical • original five ribs still preserved.",font=regular(21),fill=(39,89,73))
draw.text((44,1282),f"Highest stone projection narrows from {p['max_shoulder_outward_offset_native']:.2f} to {q['last_stone_top_projection_native']:.3f} native units.",font=regular(21),fill=(125,70,40))
draw.text((44,1324),"REJECT FOR APPROVAL: thin upper tip, plain vertical wall butt-joint, no demonstrated masonry keying or thrust capacity.",font=bold(20),fill=(160,54,51))
draw.text((44,1371),"Interpretation: an exposed source shoulder remains plausible; adding this taper is an unverified experimental alternative.",font=regular(20),fill=(69,83,91))
draw.text((44,1415),"Source status: R03, R14 and Pass 6J protected. F5ZL-C support schedule unresolved. Blender 5.0.1 tested.",font=regular(19),fill=(92,101,109))
final=O/"F5ZP_M04_P04_R04_ONE_ASHLAR_FEASIBILITY_REVIEW.png"
out.save(final,optimize=True)
with Image.open(final) as chk:assert chk.size==(2320,1500);chk.verify()
assert all(hashlib.sha256(inp.read_bytes()).hexdigest()==sha[str(inp)] for inp in inputs)
(O/"M04_P04_R04_BLENDER_ASSEMBLY_AND_DRAWING_QA.json").write_text(json.dumps({
 "input_sha256":sha,"Blender_version":bpy.app.version_string,
 "source_original_five_arch_meshes_hidden_only_during_B_image":True,
 "saved_scene_original_five_arch_meshes_visible":all(not bpy.data.objects[n].hide_render for n in names),
 "saved_scene_total_18_meshes":len(objects),
 "new_provisional_masonry_courses":len(added),
 "source_original_five_lower_springer_courses":5,
 "round_trip_experimental_glb_mesh_count":len(readback),
 "architectural_or_structural_approval":False,
 "source_GLB_source_z_up_axis_rotation_fixed":True,
 "final_one_PNG":final.name},indent=2)+"\n")
print("M04_P04_R04_REVIEW_FINAL_TECHNICAL_PASS",final,final.stat().st_size,"bytes",len(objects),"source+new meshes")
