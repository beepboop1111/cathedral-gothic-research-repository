#!/usr/bin/env python3
"""M04 P06 R12 independent 1:1 GLB scene morphology and alignment QA.
No source edits. Distinguishes technical, geometric, architectural,
historical and structural statuses; no phantom signoff.
"""
from pathlib import Path
import json,csv,hashlib
import numpy as np,trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
P=R/"M04_P06_R11_COORDINATED_TRUE_SOURCE_WALL_AND_ARCHES_B523_EXPERIMENTAL"
O=R/"M04_P06_R12_INDEPENDENT_TRUE_SOURCE_GLTF_REGRESSION_B523_EXPERIMENTAL"
assert not O.exists(),"Protect previous study"
O.mkdir()
FINAL=P/"M04_P06_B523_FIVE_GOTHIC_ARCHES_WALL_EXACTLY_COORDINATED_EXPERIMENTAL.glb"
SOURCE=R/"M04_P03_R02B_CANONICAL_SPRINGER_AND_BEARING_MASONRY_EXPERIMENTAL/R03_TEN_PROTECTED_PIER_ARCH_AND_BEARING_MASONRY_REFERENCES.glb"
COURSES=R/"M04_P05_BLENDER523_R14_CANONICAL_FIVE_SOURCE_EXPERIMENTAL/build/springer_variant.glb"
Q=P/"M04_P06_B523_EXACT_WALL_BOOL_AND_GLTF_TECHNICAL_QA.json"
ORIGINAL=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
files=[FINAL,SOURCE,COURSES,Q,ORIGINAL]
assert all(p.is_file() for p in files)
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
def load(path,translation=None):
 sc=trimesh.load(str(path),force="scene",process=False)
 result={}
 for n in sc.graph.nodes_geometry:
  t,k=sc.graph[n]
  mesh=sc.geometry[k].copy()
  mesh.apply_transform(t)
  v=mesh.vertices
  v[:]=np.c_[v[:,0],-v[:,2],v[:,1]]
  if translation is not None:v[:]+=translation
  mesh.vertices=v
  result[n]=mesh
 return result
new=load(FINAL)
old=load(SOURCE)
r14=load(COURSES,[31000,-1250,1800])
assert len(new)==14 and len(old)==10 and len(r14)==12,(len(new),len(old),len(r14))
source_names=["CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0","BAY1_FORMERET_0","BAY2_FORMERET_0"]
lowernames=["SHARED_PIER_S","RECEIVING_S_LOWER_0","RECEIVING_S_LOWER_1"]
by={}
for n in source_names:
 k="P06_COORDINATED_ABOVE_Z2400_"+n
 assert k in new
 by[n]=new[k]
wallname="P06_COORDINATED_ABOVE_Z2400_RECEIVING_S_UPPER_0"
assert wallname in new
lower={}
for n in lowernames:
 k="P06_COORDINATED_SOURCE_LOWER_"+n
 assert k in new
 lower[n]=new[k]
course={}
for i in range(1,6):
 name=f"P06_FIVE_ARCH_SOURCE_RESTORED_COURSE_{i:02d}_Z{1800+(i-1)*120}"
 assert name in new
 course[i]=new[name]
geometry=[]
for n,mesh in new.items():
 test=mesh.copy()
 test.merge_vertices()
 assert test.is_watertight,(n,len(test.faces),len(test.vertices))
 heights=test.bounds[:,2]
 if n.startswith("P06_COORDINATED_ABOVE_Z2400_"):
  assert heights[0]>=2399.95,(n,heights)
 if n.startswith("P06_FIVE_ARCH_SOURCE_RESTORED_"):
  assert heights[0]>=1799.95 and heights[1]<=2400.05,(n,heights)
 if n.startswith("P06_COORDINATED_SOURCE_LOWER_"):
  assert heights[1]<=1800.05,(n,heights)
 geometry.append({"mesh":n,"vertices_after_glTF_weld":len(test.vertices),"faces":len(test.faces),
   "Z_min":round(float(heights[0]),5),"Z_max":round(float(heights[1]),5),
   "source_geometry_is_watertight":test.is_watertight})
def section(obj,z):
 c=obj.section(plane_origin=(0,0,z),plane_normal=(0,0,1))
 if c is None:return None
 shapes=[]
 for line in c.discrete:
  if len(line)<4 or np.linalg.norm(line[0]-line[-1])>.01:continue
  poly=Polygon(line[:,:2])
  if not poly.is_valid:poly=poly.buffer(0)
  if poly.area>.001:shapes.append(poly)
 return unary_union(shapes) if shapes else None
def compare(a,b,z):
 p=section(a,z)
 q=section(b,z)
 assert p is not None and q is not None,(z,a,b)
 total=p.area+q.area
 err=p.symmetric_difference(q).area
 ratio=1-err/max(total,.001)
 return {"Z":z,"source_area":p.area,"candidate_area":q.area,
         "symmetric_section_difference_area":err,"normalized_similarity":ratio}
shapes=[]
for name in source_names:
 for z in (2440.,2500.,2750.):
  v=compare(old[name],by[name],z)
  v["source_member"]=name
  v["test"]="upper source preserved after z2400 clip"
  assert v["normalized_similarity"]>.99999,v
  shapes.append(v)
for z in (2500.,3100.):
 p=compare(old["RECEIVING_S_UPPER_0"],new[wallname],z)
 p["source_member"]="RECEIVING_S_UPPER_0"
 p["test"]="upper wall trimmed but exact original source above z2400"
 assert p["normalized_similarity"]>.99999,p
 shapes.append(p)
for n in lowernames:
 p=compare(old[n],lower[n],1500.)
 p["source_member"]=n
 p["test"]="lower source support untouched 1:1"
 assert p["normalized_similarity"]>.99999,p
 shapes.append(p)
for i,z in enumerate((1830.,1980.,2100.,2220.,2340.),1):
 p=compare(r14[f"course_{i:02d}"],course[i],z)
 p["source_member"]=f"course_{i:02d}"
 p["test"]="actual five source-restored tas courses unchanged"
 assert p["normalized_similarity"]>.99999,p
 shapes.append(p)
assert len(shapes)==25
with (O/"M04_P06_R12_25_WORLD_SECTION_SOURCE_MATCHES.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(shapes[0]))
 w.writeheader();w.writerows(shapes)
with (O/"M04_P06_R12_ALL_14_MESH_CLOSED_Z_RANGES.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(geometry[0]))
 w.writeheader();w.writerows(geometry)
# Exact solid Z partition between 5 R14 courses and R03 upper region.
tas_max=max(course[i].bounds[1,2] for i in course)
upper_min=min(new[wallname].bounds[0,2],*(m.bounds[0,2] for m in by.values()))
assert tas_max<=2400.05 and upper_min>=2399.95
# Verified morphological contact match persisted: original source top
# shoulder stays exposed and clearly labeled, not filled.
upper_source=unary_union([x for a in [old["RECEIVING_S_UPPER_0"],*([old[k] for k in source_names])] if (x:=section(a,2400.1)) is not None])
new_tas_top=section(course[5],2399.9)
assert upper_source and new_tas_top
gap=new_tas_top.difference(upper_source).area
assert 8800<gap<9100,gap
baseline=json.loads(Q.read_text())
assert baseline["Blender_5_2_3_GLTF_reimport_mesh_elements"]==14
assert baseline["all_source_truncated_6_upper_pieces_watertight"]
assert sha[str(ORIGINAL)]==baseline["original_source_blend_SHA256"]
qa={
 "stage":"M04 P06 R12: 14-piece Gothic source five-bearing wall geometry 5.2.3",
 "Blender_version":baseline["Blender_version"],
 "true_original_world_space_GLTF_scene_elements":14,
 "14_source_aligned_watertight_meshes":True,
 "sampled_source_arch_walls_lower_and_tas_shape_tests":len(shapes),
 "all_25_original_source_geometry_matches_gt_99p999pct":True,
 "minimum_normalized_source_similarity":min(x["normalized_similarity"] for x in shapes),
 "native_replacement_interface_Z":2400.,
 "source_upper_wall_and_all_five_original_arches_start_z_at_2400":True,
 "source_five_restored_tas_courses_end_z_at_2400":True,
 "volume_of_intersection_of_tas_with_upper_wall":"ZERO BY DISJOINT Z INTERIORS",
 "actual_top_shoulder_left_unfilled_native_sq":gap,
 "status_technical":"PASS",
 "status_geometric":"PARTIAL: source shape and nonduplication PASS; rear tas-to-wall bond and architectural contact not established",
 "status_architectural":"UNAPPROVED",
 "status_historical":"NOT VALIDATED",
 "status_structural":"NOT VALIDATED",
 "original_R03_plus_Pass6J_unchanged":True,
 "missing_F5ZL_C":"OPEN",
 "source_SHA256":sha,
 "not_original_eight_ambulatory_Pass6J_pier":True,
 "accepted_profile_choices":"NONE; original ribs used as test control"}
(O/"M04_P06_R12_INDEPENDENT_GEOMETRY_AND_FIVE_WAY_SOURCE_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in files)
print("M04_P06_SOURCE_MATCH_QA_PASS",len(shapes),"sections",len(new),"watertight mesh","max source shape diff",max(x["symmetric_section_difference_area"] for x in shapes),"upper mismatch",gap)
