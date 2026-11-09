#!/usr/bin/env python3
"""M04 P07 R02 exact native top-bed source contact and local bearing archive.
Uses original R03 and R14 geometry with exact 371-triangle top cap.
Five independent local Gothic arch-to-course contacts measured at Z2400.
No source modification, no user profile selection, no fictitious masonry.
"""
from pathlib import Path
import json,hashlib,csv
import numpy as np,trimesh
from shapely.geometry import Polygon,mapping
from shapely.ops import unary_union
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
O=R/"M04_P07_R02_EXACT_TOP_BED_NATIVE_SOURCE_BEARINGS_EXPERIMENTAL"
assert not O.exists(),"Protect existing checkpoint"
O.mkdir()
SOURCE=R/"M04_P03_R02B_CANONICAL_SPRINGER_AND_BEARING_MASONRY_EXPERIMENTAL/R03_TEN_PROTECTED_PIER_ARCH_AND_BEARING_MASONRY_REFERENCES.glb"
COURSES=R/"M04_P05_BLENDER523_R14_CANONICAL_FIVE_SOURCE_EXPERIMENTAL/build/springer_variant.glb"
REFERENCE=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
CAN=Path("/home/christopher/Documents/Cathedral/experimental/UNIFIED_JUNCTION_INTERFACE_R01/INTERFACE_QA.json")
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,COURSES,REFERENCE,CAN)}
def load(path,shift=None):
 sc=trimesh.load(str(path),force="scene",process=False)
 result={}
 for n in sc.graph.nodes_geometry:
  T,k=sc.graph[n]
  m=sc.geometry[k].copy();m.apply_transform(T)
  v=m.vertices;v[:]=np.c_[v[:,0],-v[:,2],v[:,1]]
  if shift is not None:v[:]+=shift
  m.vertices=v
  result[n]=m
 return result
source=load(SOURCE)
courses=load(COURSES,[31000,-1250,1800])
assert len(source)==10 and len(courses)==12
m=courses["course_05"]
tri=m.vertices[m.faces]
top_faces=tri[np.all(abs(tri[:,:,2]-2400)<1.e-5,axis=1)]
assert len(top_faces)==371,len(top_faces)
top=unary_union([Polygon(points[:,:2]) for points in top_faces])
assert top.geom_type=="Polygon" and len(top.interiors)==0 and top.is_valid
assert abs(top.area-189805.5825)<.1,top.area
def sample(mesh,z):
 c=mesh.section(plane_origin=(0,0,z),plane_normal=(0,0,1))
 if c is None:return None
 cells=[]
 for points in c.discrete:
  if len(points)<4 or np.linalg.norm(points[0]-points[-1])>.005:continue
  p=Polygon(points[:,:2])
  if not p.is_valid:p=p.buffer(0)
  if p.area>.001:cells.append(p)
 return unary_union(cells) if cells else None
wall=sample(source["RECEIVING_S_UPPER_0"],2400.1)
assert wall is not None and abs(wall.area-144000)<.01
assert wall.difference(top).area<.001
names=("CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0","BAY1_FORMERET_0","BAY2_FORMERET_0")
canonical=json.loads(CAN.read_text())["actual_five_bearings"]
members=[]
local_sections=[]
features=[]
def feature(name,geom,role,color):
 if geom is None or geom.is_empty:return
 features.append({"type":"Feature","geometry":mapping(geom),
   "properties":{"name":name,"z":2400,"role":role,"style":color,
   "source_native_scale_1to1":True,"architecturally_approved":False,
   "area_native_sq":round(geom.area,6)}})
feature("R14_SOURCE_TAS_05_EXACT_TRIANGULATED_TOP",top,"original source-correct top", "dashed-gray")
feature("R03_ORIGINAL_UPPER_WALL_CONTACT",wall,"actual source wall", "solid-black")
for name in names:
 section=sample(source[name],2400.1)
 assert section is not None
 components=[p for p in (section.geoms if hasattr(section,"geoms") else [section])
             if p.area>.1]
 local=unary_union([p for p in components if p.distance(top)<1])
 distant=unary_union([p for p in components if p.distance(top)>=1])
 assert local.area>5000
 ratio=local.intersection(top).area/local.area
 assert ratio>.9995,(name,ratio)
 local_sections.append(local)
 members.append({"name":name,
  "canonical_bearing_deg":canonical[name],
  "local_pier_R03_arch_area":round(local.area,8),
  "local_arch_area_seated_on_exact_tas_top":round(local.intersection(top).area,8),
  "local_arch_seating_fraction":round(ratio,10),
  "local_arch_outside_tas_top_native_sq":round(local.difference(top).area,8),
  "remote_end_count":sum(p.distance(top)>=1 for p in components),
  "remote_arch_end_not_a_support_deficiency":True,
  "source_classification":"REAL ORIGINAL ARCH SECTION AT Z2400.1",
  "full_arch_source_section_area":round(section.area,8)})
 feature("R03_ACTUAL_LOCAL_BEARING_"+name,local,"real local Gothic arch bearing","solid-black")
 feature("R03_LOCAL_BEARING_ON_TAS_"+name,local.intersection(top),"supported local arch contact","solid-black")
feature("R03_ORIGINAL_FIVE_LOCAL_BEARINGS_UNION",unary_union(local_sections),"five real local source arch ends","solid-black")
union=unary_union([wall]+local_sections)
source_all=unary_union([wall]+[sample(source[n],2400.1) for n in names])
shoulder=top.difference(source_all)
source_local_union=union
assert 8900<shoulder.area<9000
shoulder_local=top.difference(source_local_union)
assert abs(shoulder.area-shoulder_local.area)<.001
ext=list(shoulder.geoms if hasattr(shoulder,"geoms") else [shoulder])
ext=sorted(ext,key=lambda g:g.area,reverse=True)
assert ext[0].area>8800
feature("P07_SOURCE_SPRINGER_SHOULDER_UNCERTAIN_DO_NOT_FILL",shoulder,"uncertain whether exposed shoulder is intended","dashed-red")
feature("P07_TOP_BED_SUPPORTED_BY_R03_WALL_AND_LOCAL_ARCHES",top.intersection(source_local_union),"confirmed source XY bearing","solid-black")
# Exact top level source wall and ribs altogether must not be interpreted as
# original complete 3D contact; vertical +/-0.1 gap at section measurement.
qa={
 "milestone":"M04 P07 R02 exact top-face bearing evidence at shared wall S",
 "source_global_xyz":[31000,-1250,1800],
 "source_R03_actual_five_member_bearings":canonical,
 "Blender_engine_R14_source_profile_version":"Blender 5.2.3 source-restored",
 "exact_R14_source_course_05_top_Z":2400.,
 "exact_371_source_course05_horizontal_triangle_faces":len(top_faces),
 "exact_top_native_area":top.area,
 "original_upper_wall_source_area":wall.area,
 "upper_wall_exact_supported_native_area":wall.intersection(top).area,
 "upper_wall_outside_tas_top_area":wall.difference(top).area,
 "five_source_local_arches_near_pier":members,
 "five_local_seating_fraction_min":min(a["local_arch_seating_fraction"] for a in members),
 "all_five_local_arch_seats_over_99p95pct":True,
 "upper_exact_top_uncertain_shoulder_native_sq":shoulder.area,
 "uncertain_main_region_native_sq":ext[0].area,
 "number_of_separate_small_shoulder_regions":len(ext)-1,
 "original_remote_arch_ends_correctly_excluded":True,
 "source_original_profile_selection_unchanged":True,
 "actual_3D_bonded_arch_rear_section_verified":False,
 "architectural_historical_structural_validation":"UNRESOLVED",
 "F5ZL_C_schedule":"MISSING",
 "source_sha256":sha}
(O/"M04_P07_R02_EXACT_NATIVE_SOURCE_BEARING_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
with (O/"M04_P07_R02_FIVE_ACTUAL_GOTHIC_ARCH_LOCAL_BEARINGS.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(members[0]))
 w.writeheader();w.writerows(members)
(O/"M04_P07_R02_EXACT_TOP_AND_ACTUAL_FIVE_ARCHES.geojson").write_text(json.dumps({"type":"FeatureCollection","features":features})+"\n")
def path(poly):
 polys=[poly] if poly.geom_type=="Polygon" else list(poly.geoms)
 out=[]
 for q in polys:
  if q.geom_type!="Polygon":continue
  for ring in (q.exterior,*q.interiors):
   out.append("M "+" L ".join(f"{x:.6f},{-y:.6f}" for x,y in ring.coords)+" Z")
 return " ".join(out)
svg=f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="30700 980 600 660">
<path d="{path(wall)}" fill="none" stroke="#111" stroke-width="2.4"/>
<path d="{path(top)}" fill="none" stroke="#888" stroke-width="2.2" stroke-dasharray="8 5"/>
<path d="{path(shoulder)}" fill="none" stroke="#d42222" stroke-width="3" stroke-dasharray="6 4"/>
</svg>"""
(O/"M04_P07_R02_EXACT_1TO1_BEARING_AND_UNCERTAIN_SHOULDER.svg").write_text(svg+"\n")
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in (SOURCE,COURSES,REFERENCE,CAN))
print("P07_R02_EXACT_TOP_BEARING_QA_PASS","wall 100%","5 local > 99.95%", "uncertain_shoulder",round(shoulder.area,4),
      "source archetype count",len(members))
