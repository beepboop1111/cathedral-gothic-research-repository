#!/usr/bin/env python3
"""M04 P07 source-exact support-interface contact audit.
Read 1:1 native source GLBs; sample +/-0.1 original internal spring/
wall planes, preserve all original meshes and no speculative infill.
"""
from pathlib import Path
import json,csv,hashlib,math
import numpy as np,trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
O=R/"M04_P07_R01_FIVE_REAL_ARCH_INTERFACE_CONTACT_EXPERIMENTAL"
assert not O.exists(),"never overwrite earlier experiment"
O.mkdir()
S=R/"M04_P06_R11_COORDINATED_TRUE_SOURCE_WALL_AND_ARCHES_B523_EXPERIMENTAL/M04_P06_B523_FIVE_GOTHIC_ARCHES_WALL_EXACTLY_COORDINATED_EXPERIMENTAL.glb"
SRC=R/"M04_P03_R02B_CANONICAL_SPRINGER_AND_BEARING_MASONRY_EXPERIMENTAL/R03_TEN_PROTECTED_PIER_ARCH_AND_BEARING_MASONRY_REFERENCES.glb"
C=R/"M04_P05_BLENDER523_R14_CANONICAL_FIVE_SOURCE_EXPERIMENTAL/build/springer_variant.glb"
orig=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
files=[S,SRC,C,orig]
assert all(p.is_file() for p in files)
sha={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
def objects(path,translate=None):
 s=trimesh.load(str(path),force="scene",process=False)
 out={}
 for n in s.graph.nodes_geometry:
  t,k=s.graph[n]
  m=s.geometry[k].copy()
  m.apply_transform(t)
  # GLB's conventional Y-up -> source Z-up
  v=m.vertices
  v[:]=np.c_[v[:,0],-v[:,2],v[:,1]]
  if translate is not None:v[:]+=translate
  m.vertices=v
  out[n]=m
 return out
old=objects(SRC)
cur=objects(S)
r14=objects(C,[31000.,-1250.,1800.])
assert len(old)==10 and len(cur)==14 and len(r14)==12
arches=("CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0","BAY1_FORMERET_0","BAY2_FORMERET_0")
lower=("SHARED_PIER_S","RECEIVING_S_LOWER_0","RECEIVING_S_LOWER_1")
def poly(mesh,z):
 sec=mesh.section(plane_origin=(0,0,z),plane_normal=(0,0,1))
 if sec is None:return None
 polys=[]
 for contour in sec.discrete:
  if len(contour)<4 or np.linalg.norm(contour[0]-contour[-1])>0.005:continue
  q=Polygon(contour[:,:2])
  if not q.is_valid:q=q.buffer(0)
  if q.area>.001:polys.append(q)
 return unary_union(polys) if polys else None
def union_at(ob,names,z):
 shapes=[p for key in names if (p:=poly(ob[key],z)) is not None]
 return unary_union(shapes) if shapes else None
base=poly(r14["course_01"],1800.1)
low=union_at(old,lower,1799.9)
course_top=poly(r14["course_05"],2399.9)
upperwall=poly(old["RECEIVING_S_UPPER_0"],2400.1)
upperarches=union_at(old,arches,2400.1)
upperunion=upperwall.union(upperarches)
assert all(x is not None and x.area>0 for x in (base,low,course_top,upperwall,upperarches,upperunion))
table=[]
def row(name,support,above):
 covered=support.intersection(above)
 excess=above.difference(support)
 remaining=support.difference(above)
 item={"role":name,
       "lower_or_bearing_section_native_sq":round(support.area,6),
       "upper_or_supported_section_native_sq":round(above.area,6),
       "intersection_native_sq":round(covered.area,6),
       "upper_area_outside_support_native_sq":round(excess.area,6),
       "bearing_area_not_in_upper_native_sq":round(remaining.area,6),
       "upper_supported_fraction":round(covered.area/above.area,9),
       "XY_separation_native":round(support.distance(above),6),
       "direct_3D_continuous_bonding_verified":False}
 table.append(item)
 return item
row("Z1800 COMBINED THREE ORIGINAL LOWER SUPPORTS -> TAS 01",low,base)
row("Z2400 COURSE05 -> ORIGINAL UPPER WALL",course_top,upperwall)
for n in arches:
 member=poly(old[n],2400.1)
 assert member and member.area>0
 row("Z2400 COURSE05 -> "+n,course_top,member)
row("Z2400 COURSE05 -> UPPER WALL + FIVE RIBS UNION",course_top,upperunion)
# Internal five horizontal ashlar bedding interfaces.
beds=[]
for i in range(1,5):
 z=1800+i*120
 lower_course=poly(r14[f"course_{i:02d}"],z-.1)
 upper_course=poly(r14[f"course_{i+1:02d}"],z+.1)
 assert lower_course and upper_course
 beds.append(row(f"Z{z} ORIGINAL TAS COURSE{i:02d} -> COURSE{i+1:02d}",lower_course,upper_course))
# Quantify upper shoulder only, not void. Build source-exact cut line.
external=course_top.difference(upperunion)
assert 8800<external.area<9100
components=sorted([p for p in (external.geoms if hasattr(external,'geoms') else [external]) if p.area>.001],key=lambda p:p.area,reverse=True)
assert 1<len(components)<20
# Separate classification: original upper source union area outside bottom course
# is NOT negative structural conclusion: arch plan may support on vertical
# walls and the sampled section is not itself a full load-path analysis.
not_seated=upperunion.difference(course_top)
if not_seated.is_empty:classification="empty"
else:classification=not_seated.geom_type
result={
 "study":"M04 P07 1:1 five original Gothic section bearing contacts and P06 14 mesh source",
 "coordinate_transform":"glTF Y-up -> original Blender Z-up: (x, -z, y)",
 "world_center_xyz":[31000.,-1250.,1800.],
 "comparison_planes_z":{"lower_1799.9_to_first_1800.1":[1799.9,1800.1],
                         "last_2399.9_to_upper_2400.1":[2399.9,2400.1]},
 "sampled_bearing_roles":table,
 "sampled_total_bearing_contact_tests":len(table),
 "arch_five_source_count":len(arches),
 "lower_combined_actual_support_area_native_sq":low.area,
 "base_tas_support_coverage_pct":100*(1-base.difference(low).area/base.area),
 "upper_source_course_05_top_area_native_sq":course_top.area,
 "upper_wall_base_area_native_sq":upperwall.area,
 "upper_ribs_union_area_native_sq":upperarches.area,
 "upper_wall_plus_ribs_union_area_native_sq":upperunion.area,
 "course_05_top_outside_upper_wall_plus_source_ribs_native_sq":external.area,
 "upper_wall_plus_arches_outside_course_05_native_sq":not_seated.area,
 "upper_wall_plus_arches_outside_course_05_type":classification,
 "dominant_upper_shouldered_region_native_sq":components[0].area,
 "dominant_upper_shouldered_region_global_xy_bounds":list(components[0].bounds),
 "all_five_original_rib_sections_against_course05_measured":True,
 "source_all_14_original_glb_pieces_watertight_after_weld":all((lambda g:(g.merge_vertices() or g).is_watertight)(m.copy()) for m in cur.values()),
 "status_technical":"PASS",
 "status_geometric":"SOURCE-FIXED SAMPLE PLANES; CONTINUOUS REAR FACE CONTACT UNPROVEN",
 "status_architectural":"NOT APPROVED",
 "status_historical":"SOURCE ACTUAL MASONRY BONDING UNPROVEN",
 "status_structural":"NO FORCE/CAPACITY CALCULATION",
 "source_original_files_preserved":True,
 "missing_F5ZL_C_support_schedule":True,
 "source_SHA256":sha}
with (O/"M04_P07_R01_ALL_REAL_ARCH_AND_TAS_CONTACTS.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
(O/"M04_P07_R01_SOURCE_CONTACT_NUMERICAL_QA.json").write_text(json.dumps(result,indent=2)+"\n")
# GeoJSON for source-exact Blender diagnostic (only server-local).
from shapely.geometry import mapping
sources={
 "R03_original_upper_wall":upperwall,
 "R03_original_five_arches_union":upperarches,
 "R14_original_tas_course05_top":course_top,
 "R03_original_wall_plus_arches_union":upperunion,
 "P07_springer_exposed_shoulder_not_proven_missing_stone":external,
 "P07_original_upper_source_extent_not_on_tas_top":not_seated,
 "P07_protected_wall_cap_over_tas_course05":upperwall.intersection(course_top),
}
geo={"type":"FeatureCollection","features":[
 {"type":"Feature","geometry":mapping(g),"properties":{"name":key,"native_1to1_plane_Z":2400,"source_material_type":"DIAGNOSTIC_PLAN_ONLY_NOT_MASONRY","area_native_sq":g.area}}
 for key,g in sources.items() if not g.is_empty]}
(O/"M04_P07_R01_TRUE_SOURCE_INTERFACE_Z2400.geojson").write_text(json.dumps(geo)+"\n")
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in files)
print("P07_TRUE_ARCH_CONTACTS_PASS",len(table),"controls,base_supported",round(result["base_tas_support_coverage_pct"],8),
      "top_wall_fraction",next(x["upper_supported_fraction"] for x in table if x["role"]=="Z2400 COURSE05 -> ORIGINAL UPPER WALL"),
      "unmatched_shoulder",round(external.area,3),
      "upper_outside_course_top",round(not_seated.area,3))
print("MEMBERS",[(x["role"].split(" -> ")[-1],x["upper_supported_fraction"]) for x in table[:8]])
