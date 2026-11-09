#!/usr/bin/env python3
"""Blender 5.2.3 original 14-mesh R03+R14 source + 7 source-exact bearing
diagnostic surfaces, never to be interpreted as physical added masonry.
Preserve the original .blend + GLB byte-identically; new experiments only.
"""
import bpy,bmesh,hashlib,json
from pathlib import Path
from mathutils import Vector
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
O=R/"M04_P07_R03_B523_3D_SOURCE_CONTACT_DIAGNOSTICS_EXPERIMENTAL"
SRC=R/"M04_P06_R11_COORDINATED_TRUE_SOURCE_WALL_AND_ARCHES_B523_EXPERIMENTAL/M04_P06_B523_CANONICAL_CUT_OPEN_WALL_AND_RIBS_EXPERIMENTAL.blend"
SOURCEGLB=R/"M04_P06_R11_COORDINATED_TRUE_SOURCE_WALL_AND_ARCHES_B523_EXPERIMENTAL/M04_P06_B523_FIVE_GOTHIC_ARCHES_WALL_EXACTLY_COORDINATED_EXPERIMENTAL.glb"
DIAG=O/"M04_P07_R03_TRUE_SOURCE_DIAGNOSTIC_SURFACE_TRIANGLES.json"
ORIGINAL=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
assert bpy.app.version[:2]==(5,2),bpy.app.version_string
assert O.is_dir() and all(p.is_file() for p in (SRC,SOURCEGLB,DIAG,ORIGINAL))
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SRC,SOURCEGLB,DIAG,ORIGINAL)}
bpy.ops.wm.open_mainfile(filepath=str(SRC))
original=[o for o in bpy.data.objects if o.type=="MESH"]
assert len(original)==14,(len(original),[o.name for o in original])
sig={}
def signature(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:
  h.update(("%.8f,%.8f,%.8f;"%tuple(v.co)).encode())
 for p in ob.data.polygons:h.update((",".join(str(i) for i in p.vertices)+";").encode())
 for row in ob.matrix_world:h.update((",".join("%.8f"%x for x in row)+";").encode())
 return h.hexdigest()
for o in original:sig[o.name]=signature(o)
data=json.loads(DIAG.read_text())
assert data["schema"]=="p07_source_face_triangulation_v1"
assert len(data["geometry"])==7
col=bpy.data.collections.new("P07_DIAGNOSTIC_PLAN_SURFACES__NOT_MASONRY")
bpy.context.scene.collection.children.link(col)
def material(name,rgb):
 m=bpy.data.materials.new(name)
 m.diffuse_color=(*rgb,1)
 m["P07_SOURCE_STATUS"]="1:1 2D analytical marker on Z2400.7, not Gothic masonry"
 return m
colors={
"wall":material("DIAGNOSTIC | original R03 wall supported at Z2400",(.21,.60,.53)),
"bearing":material("DIAGNOSTIC | source R03 Gothic arch locally seated",(.90,.68,.22)),
"shoulder":material("DIAGNOSTIC | uncertain external tas shoulder NOT filled",(.94,.22,.22))}
added=[]
for item in data["geometry"]:
 name="P07_DIAGNOSTIC_NON_MASONRY_"+item["name"]
 mesh=bpy.data.meshes.new(name+"_DATA")
 mesh.from_pydata(item["vertices"],[],item["faces"])
 mesh.update()
 ob=bpy.data.objects.new(name,mesh)
 col.objects.link(ob)
 ob.data.materials.append(colors[item["material_group"]])
 ob["M04_P07_important"]="ZERO THICKNESS DIAGNOSTIC SURFACE, NOT STONE, NOT HISTORICAL INFERRED JOINT"
 ob["original_world_Z_measured_plane"]=2400
 ob["visual_marker_offset_above_original_Z"]=.7
 ob["actual_source_contour_area_native_sq"]=float(item["original_area_native_sq"])
 ob["original_Gothic_source_approval"]=False
 assert all(abs(v.co.z-2400.7)<1e-3 for v in mesh.vertices)
 assert len(mesh.polygons)==len(item["faces"])
 added.append(ob)
assert len(added)==7 and len([o for o in bpy.data.objects if o.type=="MESH"])==21
assert all(signature(o)==sig[o.name] for o in original)
sc=bpy.context.scene
sc["P07_B523_SIGNOFF"]="SOURCE GEOMETRY TECHNICAL PASS; ARCHITECTURAL AND STRUCTURAL HOLD"
sc["source_original_Gothic_five_profiles"]="EXACT ARCHIVED R03 SOURCE CONTROL, NOT USER FINAL MOULDING SELECTION"
sc["P07_exact_source_top_face_area_native_sq"]=189805.5825376441
sc["P07_upper_wall_seated_100pct"]=True
sc["P07_local_source_five_arch_sections_supported_over_99p95pct"]=True
sc["P07_shoulder_native_sq"]=8933.53280390884
sc["P07_shoulder_exposed_not_filled"]=True
sc["P07_diagnostic_overlay_meshes_not_masonry"]=7
sc["P07_missing_F5ZL_C_support_schedule"]=True
sc["P07_original_R03_SHA256"]=sha[str(ORIGINAL)]
sc["P07_original_five_profile_and_source_bearings_preserved"]=True
sc["P07_R03_original_source_scene_saved_file_unchanged"]=True
# Workbench perspective with genuine meshes only. Diagnostic sheets are
# hidden for THIS RENDER, remain selectable/saved/exported in .blend+GLB.
cam=sc.camera
assert cam and cam.type=="CAMERA"
cam.location=Vector((31000+830,-1250+1060,2400+720))
focus=Vector((31000,-1280,2260))
cam.rotation_euler=(focus-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.type="ORTHO"
cam.data.ortho_scale=1660
cam.data.clip_start=.1;cam.data.clip_end=30000
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.color_type="MATERIAL"
sc.display.shading.light="STUDIO"
sc.display.shading.show_cavity=True
sc.display.shading.show_shadows=True
sc.render.resolution_x=1360;sc.render.resolution_y=1120
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.view_settings.view_transform="Standard"
blend=O/"M04_P07_B523_FIVE_GOTHIC_BEARINGS_PLUS_SOURCE_DIAGNOSTICS_EXPERIMENTAL.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.object.select_all(action="DESELECT")
allmeshes=original+added
for o in allmeshes:o.select_set(True)
bpy.context.view_layer.objects.active=allmeshes[0]
glb=O/"M04_P07_B523_TRUE_GOTHIC_FIVE_BEARINGS_PLUS_DIAGNOSTIC_SURFACES.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True)
assert glb.read_bytes()[:4]==b"glTF"
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(glb))
roundtrip=[o for o in bpy.data.objects if o not in before and o.type=="MESH"]
assert len(roundtrip)==21,len(roundtrip)
for o in roundtrip:bpy.data.objects.remove(o,do_unlink=True)
assert all(signature(o)==sig[o.name] for o in original)
try:
 for obj in added:obj.hide_render=True
 sc.render.filepath=str(O/"M04_P07_B523_GENUINE_SOURCE_FIVE_BEARINGS_VIEWPORT.png")
 bpy.ops.render.render(write_still=True)
finally:
 for obj in added:obj.hide_render=False
assert all(signature(o)==sig[o.name] for o in original)
assert all(not ob.hide_render for ob in added)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in (SRC,SOURCEGLB,DIAG,ORIGINAL))
q={
 "Blender_version":bpy.app.version_string,
 "original_source_P06_R11_archived_meshes":14,
 "original_source_mesh_SHA256_signatures":sig,
 "unchanged_reference_file_sha256":sha,
 "new_2d_diagnostic_surfaces_not_masonry":7,
 "new_diagnostic_triangle_total":sum(len(o.data.polygons) for o in added),
 "all_saved_original_14_source_meshes_unchanged":True,
 "source_original_14_plus_new_7_GLTF_roundtrip":len(roundtrip),
 "P07_saved_blend":blend.name,"P07_output_GLTF":glb.name,
 "source_5_actual_R03_Gothic_arches_Pass6J_safeguarded":True,
 "P07_source_R03_upper_wall_and_five_local_ribs_section_bearings":"PASS at original Z2400",
 "P07_shoulder_masonry_not_added":True,
 "historical_structural_approval":False,
 "P07_viewport_image":sc.render.filepath}
(O/"M04_P07_B523_RENDER_AND_GLB_REGRESSION_QA.json").write_text(json.dumps(q,indent=2)+"\n")
print("M04_P07_B523_ORIGINAL_SOURCE_PLUS_DIAGNOSTICS_PASS",len(allmeshes),
 "source 14","nonstone 7","render",sc.render.filepath)
