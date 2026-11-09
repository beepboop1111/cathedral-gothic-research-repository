#!/usr/bin/env python3
"""M04 P04 R02C final non-obscured real Blender cutaway; one final image.
B hides the five original R03 ribs ONLY DURING RENDER to expose speculative
tapered wedge. Saved new scene restores ALL source rib visibility unchanged.
"""
from pathlib import Path
import bpy,json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
P=R/"M04_P04_R02B_BLENDER_AXIS_ALIGNED_BACKING_ALTERNATIVES_EXPERIMENTAL"
SRC=P/"M04_P04_R02_BACKING_ALTERNATIVES_EDITABLE_EXPERIMENTAL.blend"
A=P/"A_SOURCE_SHOULDER_RENDER_INTERNAL.png"
E=R/"M04_P04_R01_SHOULDER_OR_TAPERED_BACKING_STUDIES_EXPERIMENTAL"
Q=E/"M04_P04_R01_BACKING_STUDY_NUMERICAL_QA.json"
O=R/"M04_P04_R02C_FINAL_SOURCE_AND_SEPARATED_WEDGE_VISUAL_EXPERIMENTAL"
assert not O.exists(),"Existing experiment protected"
O.mkdir()
assert all(p.is_file() for p in (SRC,A,Q))
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SRC,A,Q)}
qa=json.loads(Q.read_text())
bpy.ops.wm.open_mainfile(filepath=str(SRC))
names=("CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0","BAY1_FORMERET_0","BAY2_FORMERET_0")
assert all(n in bpy.data.objects for n in names)
wedge=bpy.data.objects["R04B_EXPERIMENTAL_UNCERTAIN_BACKING_CAP_80_NATIVE"]
assert wedge.type=="MESH"
ob=[q for q in bpy.data.objects if q.type=="MESH"]
assert len(ob)==15
# Hide ONLY during this B cutaway (all 5 source ribs/arches preserve topology).
prior={n:bpy.data.objects[n].hide_render for n in names}
try:
 for n in names:bpy.data.objects[n].hide_render=True
 bpy.context.scene.render.resolution_x=1120
 bpy.context.scene.render.resolution_y=960
 bpy.context.scene.render.resolution_percentage=100
 bpy.context.scene.render.filepath=str(O/"B_RIBS_HIDDEN_SOURCE_WEDGE_EXPOSED_INTERNAL.png")
 bpy.ops.render.render(write_still=True)
finally:
 for n in names:bpy.data.objects[n].hide_render=prior[n]
assert all(bpy.data.objects[n].hide_render==prior[n] for n in names)
sc=bpy.context.scene
sc["M04_P04_R02C_B_RENDER_NOTE"]="Original 5 arch meshes TEMPORARILY HIDDEN IN B PNG ONLY for visibility. Restored in saved scene."
sc["M04_P04_R02C_5_arch_source_original_meshes_preserved"]=True
sc["M04_P04_R02C_speculative_wedge_architectural_approval"]=False
sc["M04_P04_R02C_source_upper_wall_masonry_replacement"]="NOT APPROVED"
blend=O/"M04_P04_R02C_ALL_FIVE_ARCHES_RESTORED_SOURCE_AND_EXPERIMENTAL_KEY.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
W,H=2320,1535
out=Image.new("RGB",(W,H),(246,248,251))
draw=ImageDraw.Draw(out)
fonts="/usr/share/fonts/truetype/dejavu"
bold=lambda n:ImageFont.truetype(fonts+"/DejaVuSans-Bold.ttf",n)
regular=lambda n:ImageFont.truetype(fonts+"/DejaVuSans.ttf",n)
draw.rectangle((0,0,W,100),fill=(25,44,56))
draw.text((27,11),"M04 P04 | Real Gothic springer — exposed shoulder vs tapered backing hypothesis",font=bold(29),fill=(244,250,253))
draw.text((29,56),"Original five-bearing R03 arch geometry and R14 restored masonry retained • identical 1:1 camera and coordinates",font=regular(19),fill=(185,214,224))
panels=[
 ("A · SOURCE-RETAINED","All five ORIGINAL arch meshes visible; no new stone",A,(58,94,119)),
 ("B · GEOMETRIC BACKING CANDIDATE","Five R03 arch meshes temporarily hidden in IMAGE ONLY to expose the copper key",O/"B_RIBS_HIDDEN_SOURCE_WEDGE_EXPOSED_INTERNAL.png",(157,79,51))]
for i,(name,subtitle,photo,color) in enumerate(panels):
 x=23+i*1152
 draw.rounded_rectangle((x,110,x+1131,1129),radius=10,fill=(255,255,255),outline=(183,199,207),width=2)
 draw.rectangle((x+3,112,x+1128,164),fill=color)
 draw.text((x+17,122),name,font=bold(25),fill=(255,255,255))
 draw.text((x+16,171),subtitle,font=regular(16),fill=(65,77,87))
 with Image.open(photo) as im:
  assert im.size==(1120,960)
  pic=ImageOps.fit(im.convert("RGB"),(1113,905),method=Image.Resampling.LANCZOS)
  out.paste(pic,(x+9,209))
# Lower architectural plan plot from exact source perimeter in the study QA.
draw.rectangle((22,1147,2299,1524),fill=(255,255,255),outline=(181,193,200),width=2)
draw.text((39,1162),"Z2400 PLAN CONTACT (exact source XY, no arbitrary silhouette fill)",font=bold(22),fill=(38,59,72))
poly=qa["main_source_original_largest_boundary_xy"]
bounds=(30735.,31265.,-1595.,-1080.)
plot=(42,1210,830,1497)
def xypt(x,y):
 a,b,c,d=bounds
 xpix=plot[0]+(x-a)/(b-a)*(plot[2]-plot[0])
 ypix=plot[3]-(y-c)/(d-c)*(plot[3]-plot[1])
 return (int(round(xpix)),int(round(ypix)))
wall=[xypt(x,y) for x,y in ((30760,-1570),(31240,-1570),(31240,-1250),(30760,-1250))]
draw.polygon(wall,fill=(218,224,226))
draw.line(wall+[wall[0]],fill=(10,18,22),width=4)
shape=[xypt(x,y) for x,y in poly]
overlay=Image.new("RGBA",out.size,(0,0,0,0))
od=ImageDraw.Draw(overlay)
od.polygon(shape,fill=(207,51,55,115),outline=(179,32,35,255),width=4)
out=Image.alpha_composite(out.convert("RGBA"),overlay).convert("RGB")
draw=ImageDraw.Draw(out)
draw.text((885,1210),"BLACK = recorded R03 upper wall face",font=regular(21),fill=(33,45,51))
draw.text((885,1247),"RED = largest exposed shoulder; uncertain whether infill is needed",font=regular(21),fill=(171,56,48))
draw.text((885,1298),f"Measured shoulder: {qa['source_main_exposed_shoulder_area_native_sq']:,.2f} native²   |   Projection: {qa['max_shoulder_outward_offset_native']:.2f} native",font=regular(20),fill=(34,61,73))
draw.text((885,1331),f"Shared wall-face line: {qa['main_shoulder_shared_wall_edge_length_native']:.2f} native units",font=regular(20),fill=(34,61,73))
draw.text((885,1364),"B: 80-unit taper, watertight; 33 sampled levels with no original rib/wall intrusion",font=regular(19),fill=(36,79,68))
draw.text((885,1403),"A and B remain experimental: no verified ashlar keying or load path.",font=bold(20),fill=(145,54,47))
draw.text((885,1442),"No protected geometry modified. F5ZL-C schedule still missing.",font=regular(19),fill=(105,105,111))
png=O/"F5ZP_M04_P04_R02C_ONE_TRUE_BACKING_COMPARISON.png"
out.save(png,optimize=True)
with Image.open(png) as check:
 assert check.size==(W,H)
 check.verify()
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in (SRC,A,Q))
record={
 "R02C_B_source_five_arches_hidden_for_render_only":True,
 "R02C_new_save_all_original_arches_visible":all(not bpy.data.objects[n].hide_render for n in names),
 "R02C_source_arch_meshes_not_deleted_or_edited":True,
 "R02C_world_scale_1to1":True,
 "R02C_source_blend_sha256":sha[str(SRC)],
 "Blender_version":bpy.app.version_string,
 "source_study_QA_sha256":sha[str(Q)],
 "review":png.name,
 "editable_experimental_scene":blend.name,
 "approval":"EXPERIMENTAL, HISTORICAL/STRUCTURAL NOT VALIDATED"}
(O/"M04_P04_R02C_VISIBILITY_AND_SOURCE_QA.json").write_text(json.dumps(record,indent=2)+"\n")
print("M04_P04_R02C_CLARIFIED_REVIEW_PASS",png,png.stat().st_size)
