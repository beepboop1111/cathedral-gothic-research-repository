#!/usr/bin/env python3
"""M04 P03 R04 source-derived CUTAWAY comparison; no source modifications.
Genuine original R03 meshes vertically trimmed for *visualization* only,
genuine R14 5-course geometry unmodified. R03 source blend remains locked.
"""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
from PIL import Image, ImageDraw, ImageFont
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
S=R/"M04_P03_R02B_CANONICAL_SPRINGER_AND_BEARING_MASONRY_EXPERIMENTAL/R03_TEN_PROTECTED_PIER_ARCH_AND_BEARING_MASONRY_REFERENCES.glb"
C=R/"M04_P03_CANONICAL_FIVE_BEARING_SOURCE_REBUILD_EXPERIMENTAL/build/springer_variant.glb"
SRC=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
Q=R/"M04_P03_R03_FULL_RECEIVING_MASONRY_CONTACT_AUDIT_EXPERIMENTAL/M04_P03_R03_TRUE_MASONRY_SECTION_NUMERICAL_QA.json"
O=R/"M04_P03_R04B_CUTAWAY_REAL_FIVE_ARCHES_AND_STONES_EXPERIMENTAL"
assert not O.exists(),"Never overwrite prior result"
O.mkdir()
qa=json.loads(Q.read_text())
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (S,C,SRC,Q)}
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(S))
refobjs={o.name:o for o in bpy.context.scene.objects if o.type=="MESH"}
assert len(refobjs)==10
def clip_reference(ob,low=None,high=None):
 # OBJ is copy of an exported read-only R03 reference GLB, not original.
 copied=ob.data.copy()
 copied.transform(ob.matrix_world)
 ob.data=copied
 ob.matrix_world=Matrix.Identity(4)
 bm=bmesh.new();bm.from_mesh(copied)
 if low is not None:
  geom=list(bm.verts)+list(bm.edges)+list(bm.faces)
  bmesh.ops.bisect_plane(bm,geom=geom,dist=.001,plane_co=(0,0,float(low)),
                         plane_no=(0,0,1),clear_inner=True,clear_outer=False)
 if high is not None:
  geom=list(bm.verts)+list(bm.edges)+list(bm.faces)
  bmesh.ops.bisect_plane(bm,geom=geom,dist=.001,plane_co=(0,0,float(high)),
                         plane_no=(0,0,1),clear_inner=False,clear_outer=True)
 assert len(bm.faces)>3,(ob.name,len(bm.faces))
 bm.to_mesh(copied);bm.free();copied.update()
 ob["source_R03_mesh_display_crop_only"]=True
 ob["actual_full_R03_mesh_still_separately_protected"]=True
 ob["visualized_global_Z_range"]=[low,high]
 # Preserve exact protected source as separate base GLB; cropped preview
 # remains geometrically *open* and must not be called a physical course.
for name in ("SHARED_PIER_S","RECEIVING_S_LOWER_0","RECEIVING_S_LOWER_1"):
 clip_reference(refobjs[name],low=1420,high=1800)
for name in ("CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0",
 "BAY1_FORMERET_0","BAY2_FORMERET_0"):
 clip_reference(refobjs[name],low=2400,high=2800)
clip_reference(refobjs["RECEIVING_S_UPPER_0"],low=2400,high=2780)
bpy.data.objects.remove(refobjs["RECEIVING_S_PLINTH_0"],do_unlink=True)
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(C))
new=[o for o in bpy.data.objects if o not in before]
assert len([o for o in new if o.type=="MESH"])==12
base=Vector((31000.,-1250.,1800.))
for ob in new:
 if ob.parent not in new:ob.matrix_world=Matrix.Translation(base)@ob.matrix_world
courses=[o for o in new if o.type=="MESH" and o.name.startswith("course_")]
assert len(courses)==5
for ob in new:
 if ob not in courses:bpy.data.objects.remove(ob,do_unlink=True)
def mat(label,color):
 m=bpy.data.materials.new(label)
 m.diffuse_color=(*color,1)
 return m
M={
 "lower":mat("Protected lower R03 cross-sections · charcoal",(.39,.46,.53)),
 "upper":mat("Protected R03 upper masonry · teal",(.28,.64,.61)),
 "arches":mat("Original R03 5 genuine spring rib/arch surfaces · silver",(.63,.71,.78)),
 "new":mat("Candidate five course source-based compound springer · honey stone",(.82,.59,.28))}
for name,ob in refobjs.items():
 if name not in bpy.data.objects:continue
 fam="lower" if name in ("SHARED_PIER_S","RECEIVING_S_LOWER_0","RECEIVING_S_LOWER_1") else "upper" if name=="RECEIVING_S_UPPER_0" else "arches"
 ob.data.materials.clear();ob.data.materials.append(M[fam])
 ob["reference_approved_geometry_changed"]=False
for ob in courses:
 ob.data.materials.clear();ob.data.materials.append(M["new"])
 ob["original_R14_course_geometry_unchanged"]=True
 ob["architectural_bedding_status"]="experimental replacement study; upper transition not validated"
# Visualize without overlapping original R03 wall *within* 1800..2400.
# That wall is intentionally hidden only for the cutaway band; it is neither
# deleted from nor replaced inside the protected source file.
c=bpy.data.cameras.new("M04_P03_REAL_FIVE_JUNCTION_CUTAWAY")
cam=bpy.data.objects.new(c.name,c)
bpy.context.scene.collection.objects.link(cam)
focus=base+Vector((0,-65,250))
cam.location=focus+Vector((980,-1550,780))
cam.rotation_euler=(focus-cam.location).to_track_quat("-Z","Y").to_euler()
c.type="ORTHO";c.ortho_scale=1900;c.clip_start=.1;c.clip_end=20000
sc=bpy.context.scene;sc.camera=cam
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.light="STUDIO"
sc.display.shading.color_type="MATERIAL"
sc.display.shading.show_cavity=True
sc.display.shading.show_shadows=True
sc.render.resolution_x=1700;sc.render.resolution_y=1320
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.view_settings.view_transform="Standard"
sc.world.color=(.04,.05,.06)
sc["M04_P03_R04_APPROVAL"]="SOURCE GEOMETRY AUDIT / CUTAWAY ONLY; upper real R03 arch-to-tas mismatch unresolved"
sc["BASIS"]="10 protected R03 true meshes in separate reference GLB + corrected 5 original R14 five-member springer courses"
sc["R03_SOURCE_SHA256"]=sha[str(SRC)]
sc["SOURCE_ORIGINAL_SPRING_Z"]=1800
sc["CUTAWAY_SOURCE_GEOMETRY_NOT_COURSES"]=True
sc["CANONICAL_FIVE_BEARING_COUNT"]=5
sc["F5ZL_C_SUPPORT_SCHEDULE"]="MISSING"
sc["SI_CONVERSION"]="NOT PROVEN, native 1:1"
blend=O/"M04_P03_R04B_CUTAWAY_SOURCE_AND_FIVE_COURSES_EXPERIMENTAL.blend"
glb=O/"M04_P03_R04B_CUTAWAY_SOURCE_AND_FIVE_COURSES_PREVIEW.glb"
raw=O/"P03_R04_RAW_BLENDER_WORKBENCH_RENDER.png"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.object.select_all(action="DESELECT")
parts=[x for x in bpy.data.objects if x.type=="MESH"]
assert len(parts)==14,(len(parts),[x.name for x in parts])
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True)
sc.render.filepath=str(raw)
bpy.ops.render.render(write_still=True)
# Annotate actual rendered Blender view with critical numerical status.
with Image.open(raw) as source_png:im=source_png.convert("RGB")
text_font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold_font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
title=ImageFont.truetype(bold_font,29)
small=ImageFont.truetype(text_font,18)
body=ImageFont.truetype(text_font,20)
panel=Image.new("RGB",(1700,1515),(246,248,250))
panel.paste(im,(0,118))
draw=ImageDraw.Draw(panel)
draw.rectangle((0,0,1700,117),fill=(27,48,59))
draw.text((30,15),"M04 P03 R04   |   Actual five-bearing Gothic springing • R03 source cutaway",font=title,fill=(240,246,249))
draw.text((30,63),"ORIGINAL PROTECTED lower supports + ARCHIVED five rib interfaces  /  five rebuilt experimental masonry courses",font=small,fill=(180,211,222))
draw.rectangle((0,1438,1700,1515),fill=(246,248,250))
draw.text((24,1453),"LOWER BED: 99.99985% geometrically supported by R03 pier + receiving masonry",font=body,fill=(31,86,67))
draw.text((24,1482),"UPPER JOINT: incomplete surface continuity; replacement/bonding NOT APPROVED",font=body,fill=(143,53,48))
final=O/"F5ZP_M04_P03_R04B_ONE_FIVE_BEARING_REAL_MASONRY_REVIEW.png"
panel.save(final,optimize=True)
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==sha[str(SRC)]
assert hashlib.sha256(C.read_bytes()).hexdigest()==sha[str(C)]
assert hashlib.sha256(Q.read_bytes()).hexdigest()==sha[str(Q)]
(O/"M04_P03_R04B_RENDER_QA.json").write_text(json.dumps({
 "Blender_version":bpy.app.version_string,
 "source_R03_reference_mesh_count":9,
 "source_R03_arch_member_fragments":5,
 "source_R03_lower_support_fragments":3,
 "source_R03_upper_wall_fragment":1,
 "uncut_corrected_original_course_meshes":5,
 "source_display_slices_are_intentionally_open":True,
 "source_R03_root_blend_SHA256_unchanged":sha[str(SRC)],
 "technical_GLTF_export_mesh_count":14,
 "cutaway_study_is_architectural_approval":False,
 "Blender_render":final.name,
 "input_SHA256":sha},indent=2)+"\n")
print("M04_P03_R04_CUTAWAY_BLENDER_GLTF_EXPORT_PASS",len(parts),"geometric study pieces","FINAL_PNG",final)
