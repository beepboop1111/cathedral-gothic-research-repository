#!/usr/bin/env python3
"""M04 P03 R02 protected R03 source vs canonical 5-bearing rebuilt R14 springer.
Load original blend read-only, export six unchanged source meshes to separate
GLB and overlay new 5-course assembly. No approved source saves.
"""
import bpy,hashlib,json,math,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
R=Path("/home/christopher/Documents/Cathedral/experimental")
BASE=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
OUT=BASE/"M04_P03_R02_CANONICAL_SPRINGER_WALL_CONTACT_EXPERIMENTAL"
assert not OUT.exists(),"Do not overwrite existing checkpoint"
OUT.mkdir()
source=R/"WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend"
candidate=BASE/"M04_P03_CANONICAL_FIVE_BEARING_SOURCE_REBUILD_EXPERIMENTAL/build/springer_variant.glb"
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
candidate_sha=hashlib.sha256(candidate.read_bytes()).hexdigest()
qa_json=R/"UNIFIED_JUNCTION_INTERFACE_R01/INTERFACE_QA.json"
canonical=json.loads(qa_json.read_text())["actual_five_bearings"]
source_pier="SHARED_PIER_S"
names=["CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0",
       "BAY1_FORMERET_0","BAY2_FORMERET_0"]
origin=Vector((31000.,-1250.,1800.))
bpy.ops.wm.open_mainfile(filepath=str(source))
protected=[o for o in bpy.data.objects if o.type=="MESH"]
assert len(protected)==247
assert all(x in bpy.data.objects for x in [source_pier]+names)
sig={}
def meshhash(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(("%0.6f,%0.6f,%0.6f;"%tuple(v.co)).encode())
 for face in ob.data.polygons:h.update((",".join(map(str,face.vertices))+";").encode())
 return h.hexdigest()
for key in [source_pier]+names:sig[key]=meshhash(bpy.data.objects[key])
def world_bounds(ob):
 pts=[ob.matrix_world@Vector(x) for x in ob.bound_box]
 return [[round(min(v[k] for v in pts),5),round(max(v[k] for v in pts),5)] for k in range(3)]
protected_bounds={k:world_bounds(bpy.data.objects[k]) for k in [source_pier]+names}
# Protected surfaces exported as separate read-only reference comparison only.
bpy.ops.object.select_all(action="DESELECT")
for key in [source_pier]+names:bpy.data.objects[key].select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects[names[0]]
srcglb=OUT/"R03_SIX_PROTECTED_SOURCE_MESHES_REFERENCE_ONLY.glb"
bpy.ops.export_scene.gltf(filepath=str(srcglb),export_format="GLB",use_selection=True,
 export_apply=False)
bpy.ops.object.select_all(action="DESELECT")
original_names=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(candidate))
introduced=[o for o in bpy.data.objects if o not in original_names]
newmesh=[o for o in introduced if o.type=="MESH"]
assert len(newmesh)==12,(len(newmesh),[x.name for x in newmesh])
for ob in introduced:
 if ob.parent not in introduced:ob.matrix_world=Matrix.Translation(origin)@ob.matrix_world
pairs=[("CHAPEL_TRANSVERSE_31000","member_0"),
       ("BAY1_RIB_1","member_1"),
       ("BAY2_RIB_0","member_2"),
       ("BAY1_FORMERET_0","member_3"),
       ("BAY2_FORMERET_0","member_4")]
entries=[]
for name,ref in pairs:
 candidate_ob=next((o for o in newmesh if o.name==ref or o.name.startswith(ref+".")),None)
 assert candidate_ob,(name,ref,[o.name for o in newmesh])
 bb=world_bounds(candidate_ob)
 orig=protected_bounds[name]
 err=max(abs(bb[j][k]-orig[j][k]) for j in range(3) for k in range(2))
 entries.append({"source_name":name,"rebuilt_member":ref,
  "canonical_source_bearing_degrees":float(canonical[name]),
  "protected_original_bounds_global":orig,
  "candidate_translated_bounds_global":bb,
  "bounding_box_max_coordinate_error_native":round(err,7),
  "source_original_TRI":len(bpy.data.objects[name].data.polygons),
  "candidate_TRI":len(candidate_ob.data.polygons)})
# Source four unchanged mesh members should register near exact R03 bound.
# Reswept member_2 uses alternate original R15 sample and may differ.
for q in entries:
 if q["rebuilt_member"]!="member_2":
  assert q["bounding_box_max_coordinate_error_native"]<1,(q["source_name"],q["bounding_box_max_coordinate_error_native"])
for name,ref in pairs:
 assert meshhash(bpy.data.objects[name])==sig[name]
assert meshhash(bpy.data.objects[source_pier])==sig[source_pier]
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
assert hashlib.sha256(candidate.read_bytes()).hexdigest()==candidate_sha
# Separate source from experimental objects, preserving source meshes.
for ob in protected:
 ob.hide_render=(ob.name not in set(names+[source_pier]))
 if not ob.hide_render:
  ob.color=(.52,.62,.68,1) if ob.name in names else (.54,.56,.58,1)
def material(name,color):
 m=bpy.data.materials.new(name)
 m.diffuse_color=(*color,1.)
 return m
material_course=material("P03 corrected 5-bearing springer courses • experimental",(.76,.49,.20))
material_old=material("Original R03 cathedral reference • untouched",(.44,.57,.67))
coursed=[o for o in newmesh if o.name.startswith("course_")]
assert len(coursed)==5
for ob in newmesh:
 # hide double displays of historical member meshes so course/opening
 # relationship is unambiguous in this one review image
 ob.hide_render=not ob.name.startswith("course_")
 if ob in coursed:
  ob.data.materials.clear();ob.data.materials.append(material_course)
  ob["status"]="CANONICAL_FIVE_SOURCE_BEARINGS, UNAPPROVED MASONRY CONTACT"
  ob["source_blend_SHA256"]=source_sha
source_selection=[bpy.data.objects[x] for x in [source_pier]+names]
for ob in source_selection:
 # Scene copy changes visual color only, not source object topology or saved blend.
 ob.data.materials.clear()
 # WARNING: changes current in-memory reference datablock's material slots; the
 # original file on disk remains byte-unchanged and export was before this step.
 ob.data.materials.append(material_old)
# Camera: focus on spring around original R03 global station
camera_data=bpy.data.cameras.new("P03_TRUE_GOTHIC_FIVE_BEARING_CONNECTION_ISOMETRIC")
camera=bpy.data.objects.new(camera_data.name,camera_data)
bpy.context.scene.collection.objects.link(camera)
focus=origin+Vector((0,0,190))
camera.location=focus+Vector((700,-930,770))
camera.rotation_euler=(focus-camera.location).to_track_quat("-Z","Y").to_euler()
camera_data.type="ORTHO";camera_data.ortho_scale=1600
sc=bpy.context.scene
sc.camera=camera
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.color_type="OBJECT"
sc.display.shading.light="STUDIO"
sc.display.shading.show_cavity=True
sc.display.shading.show_shadows=True
sc.render.resolution_x=1800;sc.render.resolution_y=1300
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.view_settings.view_transform="Standard"
sc["source_protected_blend"]=str(source)
sc["R03_247_protected_objects_unchanged_on_disk"]=True
sc["source_pier_global_spring"]=list(origin)
sc["five_canonical_member_names"]=names
sc["five_canonical_member_bearings"]=canonical
sc["five_bearing_P03_member_2_profile"]="original R15 experimental user profile 18, not user-approved final choice"
sc["R15_change_member_2_bearing_to_canonical_46p169139722"]=True
sc["cathedral_approval"]="NOT YET — contact area requires genuine 3D cross-section comparison"
sc["source_project_geometry_scale"]="1:1 native units; SI conversion unresolved"
blend=OUT/"M04_P03_R02_FIVE_GOTHIC_MEMBERS_AND_WALL_PROTECTED_OVERLAY_EXPERIMENTAL.blend"
png=OUT/"M04_P03_R02_5_BEARING_COURSES_VS_WALL_PIER_BLENDER_REVIEW.png"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
sc.render.filepath=str(png)
bpy.ops.render.render(write_still=True)
assert source_sha==hashlib.sha256(source.read_bytes()).hexdigest()
(OUT/"M04_P03_R02_PROTECTED_R03_MEMBER_REGISTRATION_QA.json").write_text(json.dumps({
 "R03_source_sha256":source_sha,
 "candidate_P03_r14_sha256":candidate_sha,
 "original_247_meshes_seen":len(protected),
 "unmodified_R03_six_selected_geometry_signatures":sig,
 "unchanged_selected_mesh_source_reference":True,
 "member_names":names,
 "members":entries,
 "experimental_courses":len(coursed),
 "source_spring_global_Z_up":list(origin),
 "source_source_R03_BLEND_unchanged":True,
 "Blender_version":bpy.app.version_string,
 "render_PNG":png.name,
 "architectural_approval":False},indent=2)+"\n")
print("M04_P03_R02_SOURCE_MEMBER_OVERLAY_PASS",len(entries),"measured members; source remains protected; review",png)
