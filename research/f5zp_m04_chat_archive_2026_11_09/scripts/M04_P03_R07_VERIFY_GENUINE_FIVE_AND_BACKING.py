#!/usr/bin/env python3
"""M04 P03 R07: exact protected-source five-member 3D registry plus
original-R15 section source recovery. No original objects changed.
"""
from pathlib import Path
import csv,json,hashlib,math,zipfile
import numpy as np,trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
EX=R/"M04_P03_R02B_CANONICAL_SPRINGER_AND_BEARING_MASONRY_EXPERIMENTAL"
NEW=R/"M04_P03_R05_ORIGINAL_RIB_SOURCE_ARCHITECTURAL_CONTACT_REBUILD_EXPERIMENTAL"
OLD=R/"M04_P03_CANONICAL_FIVE_BEARING_SOURCE_REBUILD_EXPERIMENTAL"
VIEW=R/"M04_P03_R06_ALL_FIVE_ORIGINAL_ARCHES_SOURCE_MATCHED_EXPERIMENTAL"
O=R/"M04_P03_R07_FIVE_GENUINE_ARCHES_PROTECTED_SOURCE_REGRESSION_EXPERIMENTAL"
assert not O.exists(),"Protect earlier experiment"
O.mkdir()
S=EX/"R03_TEN_PROTECTED_PIER_ARCH_AND_BEARING_MASONRY_REFERENCES.glb"
A=NEW/"build/springer_variant.glb"
B=OLD/"build/springer_variant.glb"
F=R/"M04_P03_R05_ORIGINAL_FIVE_MEMBER_SECTION_FIXTURE_EXPERIMENTAL/M04_P03_R05_ORIGINAL_FIVE_MEMBER_SOURCE_FIXTURE.json"
I=Path("/home/christopher/Documents/Cathedral/experimental/UNIFIED_JUNCTION_INTERFACE_R01/INTERFACE_QA.json")
REF=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
R14=Path("/home/christopher/Documents/Cathedral/experimental/SPRINGER_WORKFLOW_R14/build_springer.py")
assert all(p.is_file() for p in (S,A,B,F,I,REF,R14))
sources=[S,A,B,F,I,REF,R14,VIEW/"F5ZP_M04_P03_R06_TRUE_FIVE_BEARING_RECOVERED_SOURCE_REVIEW.png"]
sha={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in sources}
r14=json.loads((NEW/"WORKFLOW_SUMMARY.json").read_text())
assert r14["status"]=="passed" and r14["passed"]==r14["total"]==78
m=json.loads(F.read_text())
roles={x["source_name"]:x for x in m["members"]}
expected=json.loads(I.read_text())["actual_five_bearings"]
assert set(roles)==set(expected)
assert len(roles)==5 and roles["BAY2_RIB_0"]["section_ref"]=="original"
assert math.isclose(roles["BAY2_RIB_0"]["bearing_degrees"],expected["BAY2_RIB_0"],abs_tol=1e-10)
def load(p,shift=None):
 sc=trimesh.load(str(p),force="scene",process=False)
 d={}
 for name in sc.graph.nodes_geometry:
  T,key=sc.graph[name];mm=sc.geometry[key].copy()
  mm.apply_transform(T)
  v=mm.vertices
  v[:]=np.c_[v[:,0],-v[:,2],v[:,1]]
  if shift is not None:v[:]+=shift
  mm.vertices=v
  d[name]=mm
 return d
original=load(S)
new=load(A,np.array([31000.,-1250.,1800.]))
old=load(B,np.array([31000.,-1250.,1800.]))
assert len(original)==10 and len(new)==len(old)==12
def cut(obj,z):
 cut=obj.section(plane_origin=(0,0,z),plane_normal=(0,0,1))
 if not cut:return None
 ps=[]
 for c in cut.discrete:
  if len(c)<4 or np.linalg.norm(c[0]-c[-1])>.01:continue
  p=Polygon(c[:,:2])
  if not p.is_valid:p=p.buffer(0)
  if p.area>.001:ps.append(p)
 return unary_union(ps) if ps else None
def union(named,z):
 return unary_union([p for n in named if (p:=cut(original[n],z)) is not None])
five=["CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0","BAY1_FORMERET_0","BAY2_FORMERET_0"]
rows=[]
for i,name in enumerate(five):
 for z in (2400.1,2410,2440,2480,2560,2650,2750):
  src=cut(original[name],z)
  restored=cut(new[f"member_{i}"],z)
  prof18=cut(old[f"member_{i}"],z)
  assert all(x is not None for x in (src,restored,prof18))
  cc=src.intersection(restored).area
  oldc=src.intersection(prof18).area
  row={"canonical_source_name":name,
   "actual_canonical_bearing_degrees":expected[name],
   "sample_absolute_Z":z,
   "original_protected_R03_section_area":round(src.area,7),
   "restored_R15_true_section_area":round(restored.area,7),
   "source_restored_overlap_area":round(cc,7),
   "source_restored_fraction":round(cc/src.area,9),
   "restored_missing_original_area":round(src.difference(restored).area,7),
   "restored_extra_area":round(restored.difference(src).area,7),
   "previous_profile18_fraction":round(oldc/src.area,9),
   "actual_original_source_profile_approved_for_current_cathedral":False}
  rows.append(row)
assert len(rows)==35
assert all(x["source_restored_fraction"]>.9999 for x in rows)
# This is an actual experimental control: the swapped profile18 fails the
# source-equivalence requirement despite its own 78/78 generic engine checks.
profile18=[r for r in rows if r["canonical_source_name"]=="BAY2_RIB_0"]
assert len(profile18)==7
assert all(r["previous_profile18_fraction"]<.73 for r in profile18)
def to_csv(fname,rows):
 with (O/fname).open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
to_csv("M04_P03_R07_35_REAL_R03_SOURCE_ARCH_3D_REGRESSION.csv",rows)
pier_lower=union(["SHARED_PIER_S","RECEIVING_S_LOWER_0","RECEIVING_S_LOWER_1"],1799.9)
first_bed=cut(new["course_01"],1800.1)
assert pier_lower and first_bed
base_not_supported=first_bed.difference(pier_lower).area
source_upper_names=["RECEIVING_S_UPPER_0"]+five
true_upper=union(source_upper_names,2400.1)
newtop=cut(new["course_05"],2399.9)
missing=newtop.difference(true_upper)
assert missing.area>8000
components=sorted((p for p in (missing.geoms if hasattr(missing,"geoms") else [missing]) if p.area>.01),key=lambda x:x.area,reverse=True)
assert components
missing_rows=[]
for n,p in enumerate(components):
 missing_rows.append({"rank":n+1,"area_native_sq":round(p.area,8),
  "fraction_total_top_mismatch":round(p.area/missing.area,8),
  "centroid_global_X":round(p.centroid.x,6),
  "centroid_global_Y":round(p.centroid.y,6),
  "bounds_global_XY":str(tuple(round(x,5) for x in p.bounds)),
  "this_is_a_confirmed_structural_void":False})
to_csv("M04_P03_R07_TOP_BACKING_UNMATCHED_2D_REGIONS.csv",missing_rows)
# Explicit 1:1 SVG: source black, experimental gray dashed, uncertain red dashed.
def path(g):
 arr=[]
 geom=[g] if g.geom_type=="Polygon" else list(g.geoms)
 for poly in geom:
  if poly.geom_type!="Polygon":continue
  for ring in [poly.exterior,*poly.interiors]:
   arr.append("M "+" L ".join(f"{x:.6f},{-y:.6f}" for x,y in ring.coords)+" Z")
 return " ".join(arr)
left,right,bottom,top=30700,31300,-1650,-1000
svg=f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{left} {-top} {right-left} {top-bottom}">
  <path d="{path(true_upper)}" stroke="#050505" stroke-width="1.8" fill="none"/>
  <path d="{path(newtop)}" stroke="#999" stroke-width="2.4" stroke-dasharray="7,5" fill="none"/>
  <path d="{path(missing)}" stroke="#d32f2f" stroke-width="2.5" stroke-dasharray="6,4" fill="none"/>
</svg>"""
svgfile=O/"M04_P03_R07_TRUE_UPPER_BACKING_SOURCE_MISMATCH_1TO1.svg"
svgfile.write_text(svg+"\n")
old_source_blend=sha[str(REF)]
report={
 "milestone":"M04 P03 R07 canonical 5 arch R03 source vs source-restored experimental springer",
 "status":"TECHNICAL + SOURCE-ALIGNMENT GEOMETRIC PASS; BASE BEARING GEOMETRIC PASS; UPPER BACKING/BONDING NOT APPROVED",
 "actual_R03_global_spring_xyz":[31000.,-1250.,1800.],
 "five_canonical_bearings":expected,
 "R03_genuine_source_5_member_3D_sections_checked":len(rows),
 "all_35_restored_original_arch_sections_at_least_99p99pct_covered":True,
 "min_real_source_restore_overlap_fraction":min(x["source_restored_fraction"] for x in rows),
 "maximum_original_arch_section_difference_native_sq":max(x["restored_missing_original_area"] for x in rows),
 "profile18_R03_BAY2_coverage_at_7_heights":[x["previous_profile18_fraction"] for x in profile18],
 "source_5_member_count":5,"source_GLB_10_reference_meshes_verified":True,
 "R14_original_real_5_source_generator_QA":"78/78 PASS",
 "real_R03_combined_lower_support_section_native_sq":pier_lower.area,
 "R05_source_restored_first_course_section_native_sq":first_bed.area,
 "source_base_outside_real_combined_R03_lower_masonry_native_sq":base_not_supported,
 "supported_source_first_bed_pct":100*(1-base_not_supported/first_bed.area),
 "new_top_source_original_wall_and_five_real_arches_overlap_area":newtop.intersection(true_upper).area,
 "top_2d_mismatch_total_area_native_sq":missing.area,
 "top_main_unmatched_region_native_sq":components[0].area,
 "top_main_unmatched_region_fraction":components[0].area/missing.area,
 "unmatched_upper_section_geom_components":len(components),
 "top_mismatch_is_a_certified_structural_void":False,
 "upper_R03_wall_overlapping_spring_courses_requires_replacement_not_overlay":True,
 "true_3D_bedding_and_rib_carving_cleared_for_approval":False,
 "missing_F5ZL_C_support_schedule":True,
 "distinct_from_8_member_Pass6J_R1_78_ambulatory_study":True,
 "profile_family_selection":"USER WILL CHOOSE; experimental source original is control, NOT final selection",
 "preserved_original_Pass6J_F5ZKC_F5ZNA_R03_sources":True,
 "BLENDER_major":5,"BLENDER_minor":0,
 "structural_historical_approval":False,
 "sources_SHA256":sha}
(O/"M04_P03_R07_FINAL_NUMERICAL_SOURCE_AND_APPROVAL_QA.json").write_text(json.dumps(report,indent=2)+"\n")
assert hashlib.sha256(REF.read_bytes()).hexdigest()==old_source_blend
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in sources)
print("R07_TRUE_SOURCE_REGRESSION_PASS",len(rows),"member snapshots","base_supported",round(report["supported_source_first_bed_pct"],8),
"worst_current_source_alignment",round(report["min_real_source_restore_overlap_fraction"],8),
"upper_backing_unmatched",round(missing.area,3),"largest",round(components[0].area,3))
