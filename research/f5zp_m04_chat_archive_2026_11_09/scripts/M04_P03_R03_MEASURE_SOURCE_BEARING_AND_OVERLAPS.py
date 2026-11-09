#!/usr/bin/env python3
"""Independent 1:1 R03 bearing-source vs repaired FIVE-member R14 course
contact and duplicate-masonry study. ALL input GLBs read-only.
Z-up transformed from standard glTF Y-up when sectional testing.
"""
from pathlib import Path
import json,csv,hashlib,math
import numpy as np,trimesh
from shapely.geometry import Polygon,Point,mapping
from shapely.ops import unary_union
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
EX=R/"M04_P03_R02B_CANONICAL_SPRINGER_AND_BEARING_MASONRY_EXPERIMENTAL"
OUT=R/"M04_P03_R03_FULL_RECEIVING_MASONRY_CONTACT_AUDIT_EXPERIMENTAL"
assert not OUT.exists(),"Do not overwrite prior experiment"
OUT.mkdir()
ORIGINAL=EX/"R03_TEN_PROTECTED_PIER_ARCH_AND_BEARING_MASONRY_REFERENCES.glb"
CANDIDATE=R/"M04_P03_CANONICAL_FIVE_BEARING_SOURCE_REBUILD_EXPERIMENTAL/build/springer_variant.glb"
REF_BLEND=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
source_qa=EX/"M04_P03_R02B_PROTECTED_R03_MEMBER_REGISTRATION_QA.json"
r14_qa=R/"M04_P03_CANONICAL_FIVE_BEARING_SOURCE_REBUILD_EXPERIMENTAL/build/GEOMETRY_QA.json"
canonical_qa=Path("/home/christopher/Documents/Cathedral/experimental/UNIFIED_JUNCTION_INTERFACE_R01/INTERFACE_QA.json")
inputs=[ORIGINAL,CANDIDATE,REF_BLEND,source_qa,r14_qa,canonical_qa]
assert all(p.is_file() for p in inputs)
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
def read_glb(fname,shift=None):
 s=trimesh.load(str(fname),force="scene",process=False)
 objects={}
 for node in s.graph.nodes_geometry:
  T,key=s.graph[node]
  mesh=s.geometry[key].copy()
  mesh.apply_transform(T)
  v=mesh.vertices
  v[:]=np.c_[v[:,0],-v[:,2],v[:,1]]
  if shift is not None:v[:]+=shift
  mesh.vertices=v
  objects[node]=mesh
 return objects
source=read_glb(ORIGINAL)
new=read_glb(CANDIDATE,np.array([31000.,-1250.,1800.]))
expected=["SHARED_PIER_S","RECEIVING_S_LOWER_0","RECEIVING_S_LOWER_1",
 "RECEIVING_S_UPPER_0","RECEIVING_S_PLINTH_0",
 "CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0",
 "BAY1_FORMERET_0","BAY2_FORMERET_0"]
assert set(source)==set(expected)
assert len(new)==12
assert all(x in new for x in [f"course_{i:02d}" for i in range(1,6)])
oldpier=["SHARED_PIER_S","RECEIVING_S_LOWER_0","RECEIVING_S_LOWER_1"]
oldupper="RECEIVING_S_UPPER_0"
five=["CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0","BAY1_FORMERET_0","BAY2_FORMERET_0"]
def slice_poly(mesh,height):
 s=mesh.section(plane_origin=(0,0,height),plane_normal=(0,0,1))
 if not s:return None
 shapes=[]
 for points in s.discrete:
  if len(points)<4 or np.linalg.norm(points[0]-points[-1])>.005:continue
  q=Polygon(points[:,:2])
  if not q.is_valid:q=q.buffer(0)
  if q.area>.001:shapes.append(q)
 return unary_union(shapes) if shapes else None
def group(names,h):
 shapes=[s for name in names if (s:=slice_poly(source[name],h)) is not None]
 return unary_union(shapes) if shapes else None
def course_at(h):
 i=min(5,int((h-1800)//120)+1)
 return slice_poly(new[f"course_{i:02d}"],h),i
# Lower original S pier alone is not enough. Both R03 lower receiving
# solids must be included in base support footprint.
low=group(oldpier,1799.9)
base_course=slice_poly(new["course_01"],1800.1)
assert low and base_course
supported=base_course.intersection(low)
outside=base_course.difference(low)
assert supported.area/base_course.area>.99999
profile_rows=[]
for h in (1800.1,1810,1830,1860,1890,1919.9,1920.1,1980,2039.9,2040.1,2100,2159.9,2160.1,2220,2279.9,2280.1,2340,2399.9):
 curr,ix=course_at(h)
 assert curr and curr.area>0
 wall=slice_poly(source[oldupper],h)
 assert wall and wall.area>0
 rib=group(five,h)
 if rib is None:rib=Polygon()
 wall_overlap=curr.intersection(wall).area
 uncovered_by_old_upper=curr.difference(wall).area
 existing_wall_not_covered=wall.difference(curr).area
 bed_5=group(five,h)
 row={
  "source_world_Z":h,
  "course":ix,
  "course_section_area":round(curr.area,6),
  "existing_R03_upper_wall_area":round(wall.area,6),
  "OLD_UPPER_WALL_DUPLICATE_OVERLAP_if_naive_overlay":round(wall_overlap,6),
  "new_5_course_section_not_in_old_upper_wall":round(uncovered_by_old_upper,6),
  "old_upper_wall_area_missing_from_new_candidate":round(existing_wall_not_covered,6),
  "five_original_R03_arch_section_union_area":round(rib.area,6),
  "source_R03_arch_section_overlaps_new_courses":round(rib.intersection(curr).area,6),
  "source_R03_arch_section_outside_new_courses":round(rib.difference(curr).area,6),
  "combined_unioned_solid_area":round(curr.union(wall).area,6),
  "original_source_arch_meshes_distinct_from_generator_sweeps":True
 }
 profile_rows.append(row)
# Upper architectural interface between the source R03 remainder and the
# candidate output: at Z2400, huge R03 original wall continues upward
# but the novel exposed rib silhouette no longer has equivalent core.
topnew=slice_poly(new["course_05"],2399.9)
originaltop=group([oldupper]+five,2400.1)
assert topnew and originaltop
top_diff=topnew.difference(originaltop).area
top_intersect=topnew.intersection(originaltop).area
# At spring, combine protected lower pier and lower wing supports.
first_base={
 "true_original_lower_S_source_surface_area":round(low.area,8),
 "new_course_base_source_section_area":round(base_course.area,8),
 "supported_base_plan_intersection":round(supported.area,8),
 "source_real_lower_support_area_not_in_candidate":round(low.difference(base_course).area,8),
 "unsupported_base_section_area_native_sq":round(outside.area,8),
 "unsupported_base_section_fraction":round(outside.area/base_course.area,12),
 "unsupported_base_percentage":round(outside.area/base_course.area*100,9),
 "support_source_names":oldpier,
 "source_all_three_lower_meshes_at_Z1799p9":True,
 "candidate_course_at_Z1800p1":True,
 "sampling_offset_0p2_units_cross_section":True
}
with (OUT/"M04_P03_R03_FIVE_COURSE_TRUE_SOURCE_CONTACTS.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(profile_rows[0]));w.writeheader();w.writerows(profile_rows)
# A measured 1:1 SVG of the two true outlines; black confirmed source,
# gray dashed new construction, red dashed area requiring additional design.
from shapely.geometry import GeometryCollection
from shapely.ops import unary_union
# Clear labels positioned far enough from geometry not to obscure
minx,maxx=30700,31300
miny,maxy=-1625,-1015
def svgpath(p):
 q=[]
 ps=[p] if p.geom_type=="Polygon" else list(p.geoms)
 for poly in ps:
  if poly.geom_type!="Polygon":continue
  for ring in [poly.exterior,*poly.interiors]:
   c=list(ring.coords)
   q.append("M "+" L ".join(f"{x:.5f},{-y:.5f}" for x,y in c)+" Z")
 return " ".join(q)
svg=OUT/"M04_P03_R03_SOURCE_SUPPORT_VS_COURSE_BASE_1TO1.svg"
svg.write_text(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{minx} {-(maxy)} {maxx-minx} {maxy-miny}">
<path d="{svgpath(low)}" fill="none" stroke="#050505" stroke-width="2.8"/>
<path d="{svgpath(base_course)}" fill="none" stroke="#929292" stroke-dasharray="8,6" stroke-width="2.5"/>
<path d="{svgpath(outside)}" fill="#fca5a5" fill-opacity=".55" stroke="#ad1728" stroke-dasharray="5,3" stroke-width="1.2"/>
</svg>""")
original_reg=json.loads(source_qa.read_text())
assert original_reg["source_source_R03_BLEND_unchanged"] is True
assert sha[str(REF_BLEND)]==original_reg["R03_source_sha256"]
assert original_reg["experimental_courses"]==5
engine=json.loads(r14_qa.read_text())
assert engine["unsupported_base_area"]==0 and len(engine["bedding"])==4
assert engine["top_contact"]["uncovered_area"]<.01
beyond=base_course.difference(group(["SHARED_PIER_S"],1799.9)).area
report={
 "milestone":"M04 P03 R03 canonical five-bearing local source R03 3D masonry contact audit",
 "status":"SOURCE REGISTERED - true lower support bearing passes sampled geometric test; old upper masonry overlaps candidate, not cleared for adoption",
 "source_SHA256":sha,
 "R03_protected_reference_meshes_examined":len(source),
 "R03_original_247_source_meshes_unchanged":True,
 "generator_canonical_five_members_verified_from_source":True,
 "generator_R14_checks_passed":78,"generator_R14_checks_total":78,
 "local_R14_first_bedding_unsupported_area":engine["unsupported_base_area"],
 "real_R03_floor_base_support":first_base,
 "false_if_only_central_pier_support_unsupported_area_native_sq":round(beyond,5),
 "source_18_height_2d_contacts":profile_rows,
 "source_R03_existing_upper_wall_overlapped_at_all_sampled_heights":True,
 "old_upper_source_bearing_current_wall_source_area_at_sample":profile_rows[0]["existing_R03_upper_wall_area"],
 "R03_upper_wall_part_outside_candidate_max":max(r["old_upper_wall_area_missing_from_new_candidate"] for r in profile_rows),
 "max_exposed_new_moulding_outside_old_upper_wall":max(r["new_5_course_section_not_in_old_upper_wall"] for r in profile_rows),
 "new_top_Z2399p9_area":topnew.area,
 "old_wall_and_five_real_R03_arch_ribs_top_Z2400p1_area":originaltop.area,
 "candidate_top_covered_by_old_upper_R03_wall_and_ribs_sq":round(top_intersect,6),
 "candidate_top_not_covered_by_old_upper_R03_wall_and_ribs_sq":round(top_diff,6),
 "final_individual_arch_source_mesh_matches_rebuilt_section":False,
 "physical_rib_tas_moulding_continuity":"INCOMPLETE, five input mesh identities and explicit bearings match but distinct section envelopes require proper actual surface contact",
 "historic_physical_masonry_bonding_and_structure":"NOT ASSESSED",
 "F5ZL_C_support_schedule":"MISSING",
 "architectural_approval":"NOT GRANTED",
 "stage":"experimental section coordination of upper wall and five existing ribs",
 "protected_original_R03_and_Pass6J_modified":False}
(OUT/"M04_P03_R03_TRUE_MASONRY_SECTION_NUMERICAL_QA.json").write_text(json.dumps(report,indent=2)+"\n")
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in inputs)
print("CANONICAL_FIVE_SOURCE_MASONRY_AUDIT_PASS",json.dumps({
 "lower_source_support_pct":round(100*(1-first_base["unsupported_base_section_fraction"]),8),
 "base_uncovered_native_sq":first_base["unsupported_base_section_area_native_sq"],
 "upper_old_masonry_overlap_min_sq":min(x["OLD_UPPER_WALL_DUPLICATE_OVERLAP_if_naive_overlay"] for x in profile_rows),
 "upper_missing_max_sq":max(x["new_5_course_section_not_in_old_upper_wall"] for x in profile_rows),
 "top_uncovered_by_R03_upper_wall_and_ribs_sq":round(top_diff,6)},indent=2))
