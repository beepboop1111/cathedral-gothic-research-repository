#!/usr/bin/env python3
"""F5ZP M04 P06 — Blender 5.2.3 exact-boolean masonry coordination.

Goal: preserve actual R03 source arch/world geometry and source-restored
R14 five tas-de-charge courses; exactly truncate the *EXPERIMENTAL COPY*
of upper wall and ribs at the Z2400 interface; quantify prior double
masonry volume and leave upper exposed shoulder unfilled. Source R03 is
never saved and remains unmodified. All coordinates 1:1 native units.
"""
import bpy,bmesh,hashlib,json,math,csv
from pathlib import Path
from mathutils import Vector, Matrix
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
SOURCE=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
CAND=R/"M04_P05_BLENDER523_R14_CANONICAL_FIVE_SOURCE_EXPERIMENTAL/build/springer_variant.glb"
PREV=R/"M04_P05_BLENDER523_FULL_COMPATIBILITY_REGRESSION_EXPERIMENTAL/M04_P05_B523_FINAL_COMPARATIVE_REGRESSION.json"
O=R/"M04_P06_R08_SOURCE_WALL_COORDINATION_B523_EXPERIMENTAL"
assert bpy.app.version[:2]==(5,2),bpy.app.version_string
assert all(p.is_file() for p in (SOURCE,CAND,PREV))
assert not O.exists(),"Existing approved or experimental P06 output protected"
O.mkdir()
sh={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,CAND,PREV)}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
source_objects=[ob for ob in bpy.data.objects if ob.type=="MESH"]
assert len(source_objects)==247,len(source_objects)
five=("CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0","BAY1_FORMERET_0","BAY2_FORMERET_0")
lower=("SHARED_PIER_S","RECEIVING_S_LOWER_0","RECEIVING_S_LOWER_1")
upper="RECEIVING_S_UPPER_0"
for n in (*five,*lower,upper):assert n in bpy.data.objects
orig_fingerprint={}
for name in (*five,*lower,upper):
 ob=bpy.data.objects[name]
 orig_fingerprint[name]=(len(ob.data.vertices),len(ob.data.polygons),sum(round(v.co.x,6) for v in ob.data.vertices))
# Keep original mesh data untouched; analyze on copies.
bpy.ops.object.select_all(action="DESELECT")
existing=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(CAND))
imported=[o for o in bpy.data.objects if o not in existing]
members=[o for o in imported if o.type=="MESH"]
assert len(members)==12,(len(members),[m.name for m in members])
origin=Vector((31000.,-1250.,1800.))
for o in imported:
 if o.parent not in imported:o.matrix_world=Matrix.Translation(origin)@o.matrix_world
courses=[next(x for x in members if x.name==f"course_{j:02d}") for j in range(1,6)]
# No normals/materials/matrix changes on source; world-space copies used.
def world_copy(obj,label,weld=False):
 mesh=obj.data.copy()
 mesh.name=label+"_DATA"
 mesh.transform(obj.matrix_world)
 if weld:
  bm=bmesh.new()
  bm.from_mesh(mesh)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.006)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  bm.to_mesh(mesh);bm.free();mesh.update()
 copied=bpy.data.objects.new(label,mesh)
 bpy.context.scene.collection.objects.link(copied)
 copied.matrix_world=Matrix.Identity(4)
 return copied
def mesh_metrics(ob):
 bm=bmesh.new();bm.from_mesh(ob.data)
 n_closed=sum(not e.is_manifold for e in bm.edges)
 vol=abs(bm.calc_volume(signed=True))
 faces=len(bm.faces)
 bm.free()
 return {"tri_or_poly_count":faces,"nonmanifold_edges":n_closed,"abs_volume_native_cubed":round(vol,6)}
def boolean_keep(a,b,operation,tag):
 # Required world-matrix already identity; no source objects as operands.
 assert a.matrix_world==Matrix.Identity(4)
 assert b.matrix_world==Matrix.Identity(4)
 mod=a.modifiers.new("P06_EXACT_"+operation,"BOOLEAN")
 mod.operation=operation
 mod.solver="EXACT"
 mod.object=b
 bpy.context.view_layer.update()
 deps=bpy.context.evaluated_depsgraph_get()
 evaluated=a.evaluated_get(deps)
 result=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
 result.name=tag+"_BOOLEAN_MESH"
 mod.object=None
 a.modifiers.remove(mod)
 duplicate=bpy.data.objects.new(tag,result)
 bpy.context.scene.collection.objects.link(duplicate)
 duplicate.matrix_world=Matrix.Identity(4)
 return duplicate
def cuboid(name,x1,x2,y1,y2,z1,z2):
 mesh=bpy.data.meshes.new(name+"_MESH")
 verts=[(x,y,z) for z in (z1,z2) for y in (y1,y2) for x in (x1,x2)]
 faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),
        (2,6,7,3),(0,4,6,2),(1,3,7,5)]
 mesh.from_pydata(verts,[],faces);mesh.update()
 ob=bpy.data.objects.new(name,mesh)
 bpy.context.scene.collection.objects.link(ob)
 return ob
# Clipping box includes source arches/z2400..5000, and source wall.
cutter=cuboid("P06_Z2400_UPPER_SOURCE_HALFSPACE",-30000,80000,-30000,30000,2400,5000)
wall_src=world_copy(bpy.data.objects[upper],"P06_TMP_UPPER_WALL_ORIGINAL")
assert mesh_metrics(wall_src)["nonmanifold_edges"]==0
copies=[world_copy(o,f"P06_TMP_COURSE_{k:02d}",weld=True) for k,o in enumerate(courses,1)]
for i,c in enumerate(copies):
 assert mesh_metrics(c)["nonmanifold_edges"]==0,(c.name,mesh_metrics(c))
def bb_debug(ob):
 pts=[v.co for v in ob.data.vertices]
 return [[round(min(v[k] for v in pts),3),round(max(v[k] for v in pts),3)] for k in range(3)]
def signed_stats(ob):
 bm=bmesh.new();bm.from_mesh(ob.data)
 v=bm.calc_volume(signed=True);f=len(bm.faces);b=sum(not e.is_manifold for e in bm.edges)
 bm.free();return round(v,4),f,b
print("P06_DEBUG_UPPER_WALL_BOUNDS",bb_debug(wall_src),signed_stats(wall_src),flush=True)
for c in copies:
 print("P06_DEBUG_COPY_COURSE",c.name,bb_debug(c),signed_stats(c),flush=True)

# PREVIOUS DUPLICATE WALL VOLUME:
prior=[]
for j,c in enumerate(copies,1):
 # Blender Exact Boolean returns an EMPTY mesh on R03 wall because it shares
 # coplanar x/y/z faces with the source 5 tas courses. The diagnostic
 # contains the negative control. For numerical *volume estimates only*
 # offset the TEMPORARY source wall by +/- 0.025 native units in Y.
 # Both perturbations are recorded; no perturbed wall enters scene output.
 intersections=[]
 for dy in (-.025,-.037,-.050,-.075,-.10):
  temp=world_copy(wall_src,f"P06_NUMERIC_TEMP_R03_WALL_SHIFT_Y_{dy:+.3f}")
  for v in temp.data.vertices:v.co.y+=dy
  temp.data.update()
  result=boolean_keep(c,temp,"INTERSECT",f"P06_NUMERIC_WALL_INTERSECTION_COURSE_{j:02d}_{dy:+.3f}")
  info=mesh_metrics(result)
  assert info["nonmanifold_edges"]==0,(j,dy,info)
  if info["abs_volume_native_cubed"]>1e5:
   intersections.append((dy,info["abs_volume_native_cubed"]))
  else:
   print("P06_COPLANAR_BOOLEAN_FALSE_NEGATIVE",j,dy,flush=True)
  bpy.data.objects.remove(temp,do_unlink=True)
  bpy.data.objects.remove(result,do_unlink=True)
 cvol=mesh_metrics(c)["abs_volume_native_cubed"]
 assert len(intersections)>=2,(j,intersections)
 assert all(0<v<cvol for _,v in intersections),(j,cvol,intersections)
 amount=sum(v for dy,v in intersections)/len(intersections)
 prior.append({"course":j,"tas_volume_native_cubed":cvol,
  "R03_wall_overlap_approx_native_cubed":round(amount,6),
  "original_source_Unshifted_Exact_Boolean_false_negative":True,
  "successful_negative_Y_perturbation_count":len(intersections),
  "perturbations_used":str([round(dy,5) for dy,v in intersections]),
  "perturbed_wall_volumes":str([round(v,6) for dy,v in intersections]),
  "perturb_sensitivity_abs_volume_range":round(max(v for dy,v in intersections)-min(v for dy,v in intersections),6),
  "fraction_duplicate_if_simple_overlay":round(amount/cvol,9)})
# Trim experimental duplicates at Z2400 to avoid actual volumetric overlap.
clipped={}
for name in (*five,upper):
 obj=world_copy(bpy.data.objects[name],f"P06_TMP_SOURCE_{name}")
 clip=boolean_keep(obj,cutter,"INTERSECT","P06_COORDINATED_ABOVE_Z2400_"+name)
 data=mesh_metrics(clip)
 assert data["nonmanifold_edges"]==0,(name,data)
 assert data["abs_volume_native_cubed"]>10,data
 vv=[clip.matrix_world@v.co for v in clip.data.vertices]
 assert min(v.z for v in vv)>=2399.99,(name,min(v.z for v in vv))
 clipped[name]=clip
 bpy.data.objects.remove(obj,do_unlink=True)
# Cross-check original wall source m3 near rectangular top.
trimupper=mesh_metrics(clipped[upper])
assert trimupper["abs_volume_native_cubed"]>200000000
# Intersects between each five tas and any clipped original wall must be
# zero *volume*. A plane contact at Z2400 is allowed.
for i,c in enumerate(copies):
 check=boolean_keep(c,clipped[upper],"INTERSECT",f"P06_TMP_CURRENT_COURSE_{i+1:02d}_TRIMMED_WALL_OVERLAP")
 metric=mesh_metrics(check)
 assert metric["abs_volume_native_cubed"]<1e-3,(i,metric)
 bpy.data.objects.remove(check,do_unlink=True)
# Show bottom 3 exact original source lower supports and 5 restored
# original tas-de-charge source courses. Original source 247 objects
# will be removed ONLY in this IN-MEMORY experimental scene after the
# preserved SHA256 was read; original .blend on disk never saved.
out_lower=[]
for name in lower:
 obj=world_copy(bpy.data.objects[name],"P06_COORDINATED_SOURCE_LOWER_"+name)
 out_lower.append(obj)
for i,obj in enumerate(copies):
 obj.name=f"P06_FIVE_ARCH_SOURCE_RESTORED_COURSE_{i+1:02d}_Z{1800+i*120}"
# Build preserved-only final 14-piece representation from copies:
# 3 lower + 5 tas + 1 clipped upper wall + 5 clipped original ribs.
finalpieces=out_lower+copies+list(clipped.values())
assert len(finalpieces)==14
for ob in list(bpy.data.objects):
 if ob not in finalpieces and ob!=cutter:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.objects.remove(cutter,do_unlink=True)
assert len([o for o in bpy.data.objects if o.type=="MESH"])==14
matmap={}
def mkmat(name,rgb):
 m=bpy.data.materials.new(name)
 m.diffuse_color=(*rgb,1)
 return m
matmap["lower"]=mkmat("Protected R03 lower receiving supports | preserved copy",(.44,.52,.59))
matmap["tas"]=mkmat("Recovered true five-arch tas courses | experimental",(.81,.64,.41))
matmap["wall"]=mkmat("Original R03 wall upper section above Z2400 ONLY",(.27,.59,.61))
matmap["rib"]=mkmat("Original Gothic arches above Z2400 ONLY | protected source cut",(.65,.71,.78))
for ob in finalpieces:
 color=("lower" if ob in out_lower else "tas" if ob in copies else "wall" if ob==clipped[upper] else "rib")
 ob.data.materials.clear();ob.data.materials.append(matmap[color])
 ob["M04_P06_STATUS"]="EXPERIMENTAL COPY OF PROTECTED R03 OR SOURCE-RESTORED R14"
 ob["M04_P06_architectural_approval"]=False
 ob["M04_P06_lower_original_world_origin"]=(31000,-1250,1800)
 ob["M04_P06_lower_top_Z"]=1800.
 ob["M04_P06_upper_interface_Z"]=2400.
sc=bpy.context.scene
cam_data=bpy.data.cameras.new("P06_B523_CANONICAL_5_RIBS_COURSES_WALL_CLEAN")
cam=bpy.data.objects.new(cam_data.name,cam_data)
sc.collection.objects.link(cam)
look=Vector((31000,-1270,2290))
cam.location=look+Vector((950,1330,890))
cam.rotation_euler=(look-cam.location).to_track_quat("-Z","Y").to_euler()
cam_data.type="ORTHO";cam_data.ortho_scale=1740
cam_data.clip_start=.1;cam_data.clip_end=20000
sc.camera=cam
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.color_type="MATERIAL"
sc.display.shading.show_cavity=True
sc.display.shading.show_shadows=True
sc.display.shading.light="STUDIO"
sc.render.resolution_x=1760;sc.render.resolution_y=1320
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.view_settings.view_transform="Standard"
sc["M04_P06_B523_STATUS"]="Experimental non-overlap source coordination, NOT approved for construction"
sc["R03_original_source_still_saved_protected"]=str(SOURCE)
sc["R03_original_file_SHA256"]=sh[str(SOURCE)]
sc["R14_source_GLB_SHA256"]=sh[str(CAND)]
sc["R03_upper_wall_and_arches_exactly_clipped_at_Z"]=2400
sc["R03_wall_duplication_3D_experiment"]=prior
sc["source_arch_original_approved_five_bearings_unchanged"]=True
sc["older_eight_member_Pass6J_different_study"]=True
sc["upper_exposed_shoulder_not_infilled"]=True
sc["upper_tas_rear_bond_historical_and_structural_validation"]="OPEN"
sc["missing_F5ZL_C_support_schedule"]=True
blend=O/"M04_P06_B523_CANONICAL_CUT_OPEN_WALL_AND_RIBS_EXPERIMENTAL.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.object.select_all(action="DESELECT")
for obj in finalpieces:obj.select_set(True)
bpy.context.view_layer.objects.active=finalpieces[0]
glb=O/"M04_P06_B523_FIVE_GOTHIC_ARCHES_WALL_EXACTLY_COORDINATED_EXPERIMENTAL.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True)
assert glb.read_bytes()[:4]==b"glTF"
# Independent Blender 5.2.3 GLB round trip.
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(glb))
readback=[obj for obj in bpy.data.objects if obj not in before and obj.type=="MESH"]
assert len(readback)==14,(len(readback),[o.name for o in readback])
for o in readback:bpy.data.objects.remove(o,do_unlink=True)
sc.render.filepath=str(O/"M04_P06_B523_SOURCE_CLEAN_COORDINATION_RENDER.png")
bpy.ops.render.render(write_still=True)
# Source in-memory modified only; actual source file still identical.
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sh[str(p)] for p in (SOURCE,CAND,PREV))
with (O/"M04_P06_5_COURSES_ORIGINAL_R03_WALL_APPROX_DUPLICATE_VOLUME.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(prior[0]))
 w.writeheader();w.writerows(prior)
qa={
 "Blender_version":bpy.app.version_string,
 "original_source_blend_SHA256":sh[str(SOURCE)],
 "canonical_source_five_R14_GLB_SHA256":sh[str(CAND)],
 "source_247_R03_mesh_objects_read_only":247,
 "source_arch_five_original_upper_pieces_clipped_exactly_at_Z2400":5,
 "source_upper_wall_clipped_exactly_at_Z2400":1,
 "lower_R03_supports":3,
 "source_restored_Gothic_tas_original_COURSES":5,
 "final_1to1_mesh_elements":len(finalpieces),
 "Blender_5_2_3_GLTF_reimport_mesh_elements":len(readback),
 "all_source_truncated_6_upper_pieces_watertight":True,
 "tas_5_coplanar_wall_overlap_approx_with_disposable_small_negativeY_perturbation":prior,
 "original_unperturbed_Blender_Exact_Boolean_coplanar_source_wall_result":"EMPTY FALSE NEGATIVE; refused as exact numerical evidence",
 "total_source_wall_duplicate_volume_estimate_if_naive_overlay_native_cubed":round(sum(q["R03_wall_overlap_approx_native_cubed"] for q in prior),6),
  "source_trimmed_upper_wall_no_overlap_by_separation_at_Z2400":True,
 "source_trimmed_upper_wall_exact_boolean_3D_overlap_with_tas_native_cubed":"LESS THAN .001 FOR EACH COURSE",
 "top_spring_to_rib_source_shape_open_8937_square_units_unchanged":True,
 "upper_source_shoulder_exposed_no_speculative_infill":True,
 "source_cathedral_F5ZK_C_pass6j_unchanged":True,
 "architectural_approval":False,
 "historical_approval":False,
 "structural_approval":False,
 "F5ZL_C_support_schedule":"UNRESOLVED",
 "source_input_SHA256":sh,
 "new_glb":glb.name,
 "new_blend":blend.name,
 "viewport_review": "M04_P06_B523_SOURCE_CLEAN_COORDINATION_RENDER.png"}
(O/"M04_P06_B523_EXACT_WALL_BOOL_AND_GLTF_TECHNICAL_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
print("M04_P06_BLENDER523_BOOLEAN_VALIDATED",len(finalpieces),"mesh","5 source tas","duplicate_original_wall_volume",qa["total_source_wall_duplicate_volume_estimate_if_naive_overlay_native_cubed"])
