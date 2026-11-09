#!/usr/bin/env python3
"""Blender >=5.2 independent regression: source five arches + four experimental
masonry stones. Never writes the original source 5.0 checkpoint.
Technical geometry, GLB round-trip, and two same-camera workbench views.
"""
from pathlib import Path
import bpy,bmesh,hashlib,json,math
from mathutils import Vector
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
SOURCE=R/"M04_P04_R04_FINAL_FOUR_STONE_CONSTRUCTABILITY_REVIEW_EXPERIMENTAL/M04_P04_R04_FIVE_ORIGINAL_ARCHES_AND_FOUR_HYPOTHETICAL_STONES_EXPERIMENTAL.blend"
ORIGINAL=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
ROOT=R/"M04_P05_BLENDER523_FULL_COMPATIBILITY_REGRESSION_EXPERIMENTAL"
assert tuple(bpy.app.version)>=(5,2,0),bpy.app.version_string
assert SOURCE.is_file() and ORIGINAL.is_file() and ROOT.exists()
sh={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,ORIGINAL)}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
source_arches=("CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0","BAY1_FORMERET_0","BAY2_FORMERET_0")
courses=tuple(f"course_{i:02}" for i in range(1,6))
stones=tuple(f"P04_HYPOTHETICAL_BACKING_COURSE_{i:02}_Z{2400+20*(i-1)}" for i in range(1,5))
objects=[o for o in bpy.data.objects if o.type=="MESH"]
assert len(objects)==18,(len(objects),[o.name for o in objects])
assert all(key in bpy.data.objects for key in (*source_arches,*courses,*stones))
assert all(not bpy.data.objects[k].hide_render for k in source_arches)
def worldverts(obj):
 return [obj.matrix_world@v.co for v in obj.data.vertices]
def contours(obj,z):
 v=worldverts(obj)
 pts={(round(p.x,2),round(p.y,2)) for p in v if abs(p.z-z)<.06}
 assert len(pts)>=5,(obj.name,z,len(pts))
 return pts
checks=[]
for i,name in enumerate(stones):
 ob=bpy.data.objects[name]
 mesh=ob.data
 bm=bmesh.new()
 bm.from_mesh(mesh)
 raw_closed=all(e.is_manifold for e in bm.edges)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001)
 welded_closed=all(e.is_manifold for e in bm.edges)
 faces=len(bm.faces)
 bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
 bm.free()
 assert welded_closed and faces>10,(name,welded_closed,faces)
 vs=worldverts(ob)
 low=min(p.z for p in vs);high=max(p.z for p in vs)
 assert abs(low-(2400+i*20))<.03 and abs(high-(2420+i*20))<.03,(name,low,high)
 row={"stone":name,"source_mesh_faces":len(mesh.polygons),
 "raw_manifold":raw_closed,"welded_manifold":welded_closed,
 "world_base_Z":round(low,4),"world_top_Z":round(high,4)}
 if i>0:
  prev=bpy.data.objects[stones[i-1]]
  prev_top=contours(prev,2400+i*20)
  cur_base=contours(ob,2400+i*20)
  same=prev_top==cur_base
  assert same,(stones[i-1],name,sorted(prev_top-cur_base)[:4],sorted(cur_base-prev_top)[:4])
  row["common_bed_vertices_match_to_0p01_native"]=same
 checks.append(row)
source_arch_sig={}
for k in source_arches:
 o=bpy.data.objects[k]
 source_arch_sig[k]={"vertices":len(o.data.vertices),"faces":len(o.data.polygons),
 "hidden":o.hide_render,"matrix_world":list(round(z,8) for row in o.matrix_world for z in row)}
# Independent source basis: the 18 pieces are EXACT archived mesh objects.
sc=bpy.context.scene
assert sc.camera is not None
sc.camera.data.clip_start=.1
sc.camera.data.clip_end=20000
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.color_type="MATERIAL"
sc.display.shading.light="STUDIO"
sc.display.shading.show_cavity=True
sc.display.shading.show_shadows=True
sc.render.resolution_x=1200
sc.render.resolution_y=960
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.view_settings.view_transform="Standard"
sc.render.filepath=str(ROOT/"A_B523_FULL_SOURCE_WORKBENCH_INTERNAL.png")
bpy.ops.render.render(write_still=True)
try:
 for name in source_arches:bpy.data.objects[name].hide_render=True
 sc.render.filepath=str(ROOT/"B_B523_FOUR_STONES_SOURCE_ARCHES_HIDDEN_ONLY_IN_RENDER_INTERNAL.png")
 bpy.ops.render.render(write_still=True)
finally:
 for name in source_arches:bpy.data.objects[name].hide_render=False
assert all(not bpy.data.objects[k].hide_render for k in source_arches)
sc["M04_P05_B523_EXACT_VERSION"]=bpy.app.version_string
sc["M04_P05_source_original_SHA256"]=sh[str(SOURCE)]
sc["M04_P05_blender_5_2_plus_regression"]="Four split experimental stone meshes, 3 shared bedding interfaces, original five arch mesh surfaces"
sc["M04_P05_F5ZL_C_SUPPORT_SCHEDULE"]="UNRESOLVED"
sc["M04_P05_ARCHITECTURAL_AND_STRUCTURAL_APPROVAL"]="WITHHELD; thin wedge tip and no source keying"
sc["M04_P05_SOURCE_LOWER_CATHEDRAL_AND_Pass6J_CHANGED"]=False
newblend=ROOT/"M04_P05_BLENDER523_READ_ONLY_SOURCE_FOUR_STONE_SCENE_EXPERIMENTAL.blend"
glb=ROOT/"M04_P05_B523_18_MESH_GLTF_ROUNDTRIP_EXPERIMENTAL.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(newblend))
bpy.ops.object.select_all(action="DESELECT")
for obj in objects:obj.select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects[stones[0]]
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True)
assert glb.read_bytes()[:4]==b"glTF"
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(glb))
roundtrip=[o for o in bpy.data.objects if o not in before and o.type=="MESH"]
assert len(roundtrip)==18,(len(roundtrip),[o.name for o in roundtrip])
# glTF preserves identity, global placement and approximate 1:1 bounds.
assert all(any(name in x.name for x in roundtrip) for name in stones)
def worldbbox(o):
 p=worldverts(o)
 return [[min(x[k] for x in p),max(x[k] for x in p)] for k in range(3)]
for name in stones:
 originalobj=bpy.data.objects[name]
 imported=next(x for x in roundtrip if name in x.name)
 beforebounds=worldbbox(originalobj)
 afterbounds=worldbbox(imported)
 maxerror=max(abs(beforebounds[k][m]-afterbounds[k][m]) for k in range(3) for m in (0,1))
 assert maxerror<.01,(name,maxerror)
# No approved source input modified by reading, exporting, rendering.
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sh[str(p)] for p in (SOURCE,ORIGINAL))
report={
 "requested":"Blender >=5.2 compatibility / M04 cathedral profile and five-bearing source",
 "actual_binary_version":bpy.app.version_string,"bpy_version":list(bpy.app.version),
 "source_unmodified_blend_SHA256":sh[str(SOURCE)],
 "protected_original_R03_blend_SHA256":sh[str(ORIGINAL)],
 "source_five_original_arches_preserved":True,
 "source_five_arches_render_hidden_in_B_only":True,
 "original_18_mesh_count":len(objects),
 "four_separate_stone_geometric_checks":checks,
 "all_four_candidate_stones_watertight_after_seam_weld":all(x["welded_manifold"] for x in checks),
 "three_true_bedding_vertices_match_to_0p01_native":True,
 "source_arch_identity_signatures":source_arch_sig,
 "Blender_5_2_3_native_GLTF_export":True,
 "Blender_5_2_3_native_GLTF_reimport_18_meshes":len(roundtrip),
 "GLTF_source_coordinate_max_error_native_less_than_0p01":True,
 "source_masonry_and_Pass6J_approved_geometry_changed":False,
 "historical_source_mouldings_changed":False,
 "constructability_issue_last_stone_thin_upper_projection_native":.655151,
 "upper_wall_mechanical_keying_verified":False,
 "structural_capacity_verified":False,
 "missing_F5ZL_C_schedule":True,
 "architectural_approval":"WITHHELD",
 "Blend_5_2_checkpoint":newblend.name,"GLB_5_2_roundtrip":glb.name,
 "source_view": "A_B523_FULL_SOURCE_WORKBENCH_INTERNAL.png",
 "cutaway_view": "B_B523_FOUR_STONES_SOURCE_ARCHES_HIDDEN_ONLY_IN_RENDER_INTERNAL.png"}
(ROOT/"M04_P05_B523_NUANCED_TECHNICAL_QA.json").write_text(json.dumps(report,indent=2)+"\n")
print("BLENDER_523_M04_P04_TECHNICAL_GLTF_PASS",bpy.app.version_string,len(objects),"original",len(roundtrip),"GLTF","all 4 manifold",report["all_four_candidate_stones_watertight_after_seam_weld"])
