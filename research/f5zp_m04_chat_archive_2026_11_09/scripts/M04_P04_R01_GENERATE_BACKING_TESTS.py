#!/usr/bin/env python3
"""F5ZP M04 P04 R01 upper springer shoulder vs experimental tapering wall-key.
Recover R03 source as immutable evidence. No automatic infill of 8,881-unit²
shoulder; alternate B is a clearly UNAPPROVED geometry-only hypothesis.

In local native XYZ, global source spring is (31000,-1250,1800).
R14 glTF mesh input converted from glTF Y-up to user Z-up for auditing.
"""
from pathlib import Path
import hashlib,csv,json,math
import numpy as np,trimesh
import shapely
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
O=R/"M04_P04_R01_SHOULDER_OR_TAPERED_BACKING_STUDIES_EXPERIMENTAL"
assert not O.exists(),"No replacing earlier experiments"
O.mkdir()
source_glb=R/"M04_P03_R02B_CANONICAL_SPRINGER_AND_BEARING_MASONRY_EXPERIMENTAL/R03_TEN_PROTECTED_PIER_ARCH_AND_BEARING_MASONRY_REFERENCES.glb"
spring_glb=R/"M04_P03_R05_ORIGINAL_RIB_SOURCE_ARCHITECTURAL_CONTACT_REBUILD_EXPERIMENTAL/build/springer_variant.glb"
source_blend=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
source_qa=R/"M04_P03_R07_FIVE_GENUINE_ARCHES_PROTECTED_SOURCE_REGRESSION_EXPERIMENTAL/M04_P03_R07_FINAL_NUMERICAL_SOURCE_AND_APPROVAL_QA.json"
files=[source_glb,spring_glb,source_blend,source_qa]
assert all(p.is_file() for p in files)
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
def load(path,translation=None):
 sc=trimesh.load(str(path),force="scene",process=False)
 out={}
 for n in sc.graph.nodes_geometry:
  T,k=sc.graph[n]
  mesh=sc.geometry[k].copy()
  mesh.apply_transform(T)
  v=mesh.vertices
  v[:]=np.c_[v[:,0],-v[:,2],v[:,1]]
  if translation is not None:v[:]+=translation
  mesh.vertices=v
  out[n]=mesh
 return out
ref=load(source_glb)
spring=load(spring_glb,[31000,-1250,1800])
names=["CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0","BAY1_FORMERET_0","BAY2_FORMERET_0"]
assert len(ref)==10 and len(spring)==12
def cut(mesh,z):
 sec=mesh.section(plane_origin=(0,0,z),plane_normal=(0,0,1))
 if sec is None:return None
 result=[]
 for points in sec.discrete:
  if len(points)<4 or np.linalg.norm(points[0]-points[-1])>.01:continue
  poly=Polygon(points[:,:2])
  if not poly.is_valid:poly=poly.buffer(0)
  if poly.area>.001:result.append(poly)
 return unary_union(result) if result else None
def members_at(z):
 pieces=[g for key in names if (g:=cut(ref[key],z)) is not None]
 return unary_union(pieces)
wall0=cut(ref["RECEIVING_S_UPPER_0"],2400.1)
upper0=unary_union([wall0,members_at(2400.1)])
course_top=cut(spring["course_05"],2399.9)
unknown=course_top.difference(upper0)
assert unknown.geom_type=="MultiPolygon"
parts=sorted((p for p in unknown.geoms if p.area>.001),key=lambda g:g.area,reverse=True)
main=orient(parts[0],1.0)
wall_face=-1250.
assert abs(main.bounds[1]-wall_face)<1e-5 and len(main.interiors)==0
assert main.area>8800
assert main.boundary.intersection(wall0.boundary).length>210
# Simplify tiny independent numerical corners of this ONE selected region.
# Never fill or change other disconnected source mismatch regions.
shape=orient(main.simplify(.03,preserve_topology=True),1.)
assert shape.is_valid and shape.geom_type=="Polygon" and shape.area>0
assert main.symmetric_difference(shape).area<.001
ring=np.array(shape.exterior.coords[:-1],dtype=float)
N=len(ring)
assert 6<=N<=80,N
# On first bed y=-1250 is the ORIGINAL outer face of R03 upper wall.
# Scaling ONLY the OUTWARD projected distance preserves the wall contact
# along a 211.087 native unit *vertical face*, as a wall-side joint study.
def projected(k):
 return np.c_[ring[:,0],wall_face+k*(ring[:,1]-wall_face)]
def triangle_ids(p):
 geoms=constrained_delaunay_triangles(p).geoms
 coords=np.array(p.exterior.coords[:-1],dtype=float)
 faces=[]
 for triangle in geoms:
  q=np.array(triangle.exterior.coords[:-1],dtype=float)
  ids=[]
  for xy in q:
   ds=np.linalg.norm(coords-xy,axis=1)
   j=int(np.argmin(ds))
   assert ds[j]<1e-5,(ds.min(),xy)
   ids.append(j)
  faces.append(tuple(ids))
 assert len(faces)==len(coords)-2,(len(faces),len(coords))
 assert abs(sum(Polygon(coords[list(t)]).area for t in faces)-p.area)<1e-5
 return faces
faces2=triangle_ids(shape)
# Wedge loft is a fully enclosed EXPERIMENTAL stone. Source upper wall and
# protected ribs remain UNCHANGED. No physical bond capacity proven.
def wedge(height):
 levels=np.linspace(2400.,2400.+height,9)
 factors=np.linspace(1.,.01,9)
 verts=np.vstack([np.c_[projected(float(scale)),np.full(N,z)]
                  for z,scale in zip(levels,factors)])
 faces=[]
 for layer in range(len(levels)-1):
  low=N*layer;high=N*(layer+1)
  for j in range(N):
   k=(j+1)%N
   faces.append((low+j,low+k,high+k))
   faces.append((low+j,high+k,high+j))
 faces.extend(tuple(reversed(tri)) for tri in faces2)
 faces.extend(tuple(N*(len(levels)-1)+idx for idx in tri) for tri in faces2)
 mesh=trimesh.Trimesh(vertices=verts,faces=faces,process=True)
 trimesh.repair.fix_normals(mesh)
 assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>1000
 assert mesh.bounds[0,2]==2400. and abs(mesh.bounds[1,2]-(2400+height))<1e-9
 return mesh,levels,factors
def writecsv(file,records):
 with (O/file).open("w",newline="") as out:
  w=csv.DictWriter(out,fieldnames=list(records[0]))
  w.writeheader();w.writerows(records)
# Test 3 alternative tapers without adding any of them to source scene.
alternatives=[]
all_section_rows=[]
for height in (40.,80.,120.):
 mesh,zs,ks=wedge(height)
 sample=[]
 for h in np.linspace(2400.1,2400+height-.1,33):
  p=cut(mesh,float(h))
  assert p is not None and p.is_valid
  source_arch=members_at(float(h))
  original_upper_wall=cut(ref["RECEIVING_S_UPPER_0"],float(h))
  assert source_arch and original_upper_wall
  arch_collision=p.intersection(source_arch).area
  wall_collision=p.intersection(original_upper_wall).area
  assert arch_collision<.05,(height,h,arch_collision)
  assert wall_collision<.05,(height,h,wall_collision)
  # Base cap is NOT a hole: it lies upon the top course.
  sample.append({"trial_height":height,"sample_Z":round(float(h),6),
   "wedge_section_native_sq":round(p.area,6),
   "overlap_5_original_arch_sections_sq":round(arch_collision,8),
   "overlap_R03_upper_wall_interior_sq":round(wall_collision,8),
   "source_arch_min_clearance_in_XY_native":round(p.distance(source_arch),6)})
 all_section_rows.extend(sample)
 bottom=cut(mesh,2400.00001)
 top=cut(mesh,2399.99+height)
 supported=bottom.intersection(course_top).area
 base_overhang=bottom.difference(course_top).area
 base_fraction=supported/bottom.area
 assert base_fraction>.9999
 contact_edge=shape.boundary.intersection(wall0.boundary).length
 # Guaranteed contact with R03 along a common Y=-1250 vertical planar face,
 # not evidence of bonded continuous ashlar or sufficient shear resistance.
 vertical_contact_planar_sq=contact_edge*height
 metric={"trial":"TAPER_TO_WALL_"+str(int(height)),
  "original_restored_5_source_profile_arches_unchanged":True,
  "source_R03_upper_wall_mesh_unchanged":True,
  "trial_course_5_source_mesh_unchanged":True,
  "wedge_z_start":2400.,"wedge_z_top":2400.+height,
  "wedge_section_bottom_area_native_sq":round(bottom.area,6),
  "wedge_section_top_area_native_sq":round(top.area,6),
  "wedge_watertight":mesh.is_watertight,
  "wedge_positive_volume_native_cubed":round(mesh.volume,6),
  "shared_R03_upper_wall_face_length_native":round(contact_edge,6),
  "nominal_vertical_wall_face_contact_area_native_sq":round(vertical_contact_planar_sq,6),
  "source_bottom_course_top_face_geometrically_under_wedge_fraction":round(base_fraction,9),
  "wedge_bottom_outside_source_course_5_sq":round(base_overhang,6),
  "max_arch_section_interpenetration":max(q["overlap_5_original_arch_sections_sq"] for q in sample),
  "max_wall_section_interpenetration":max(q["overlap_R03_upper_wall_interior_sq"] for q in sample),
  "architectural_or_structural_approval":False}
 alternatives.append(metric)
 if height==80:
  best=mesh
  bestlabel=metric
  best.export(str(O/"M04_P04_R01_EXPERIMENTAL_80_UNIT_TAPERED_BACKING_KEY.glb"))
  assert (O/"M04_P04_R01_EXPERIMENTAL_80_UNIT_TAPERED_BACKING_KEY.glb").read_bytes()[:4]==b"glTF"
writecsv("M04_P04_99_EXACT_2D_BACKING_CLEARANCE_SECTIONS.csv",all_section_rows)
writecsv("M04_P04_THREE_SOURCE_BACKING_TAPER_VARIANTS.csv",alternatives)
# A second response explicitly REJECTS mandatory infill. One diagnostic
# method keeps original shoulder exposed and does not create extra geometry.
source_source_q=json.loads(source_qa.read_text())
report={
 "milestone":"M04 P04 R01 source upper masonry exposed shoulder and 3D backing hypotheses",
 "true_original_5_member_registration_reused":True,
 "source_bearings_changed":False,
 "source_38_profile_library_automatic_assignment":False,
 "source_blend_and_arches_unchanged":True,
 "class_A":"Exposed masonry shoulder as an unmodified construction option (no additional stone)",
 "class_B":"Experimental source-outside tapered backing key as a hypothetical derivative",
 "source_main_exposed_shoulder_area_native_sq":main.area,
 "original_upper_projection_bounding_Y":wall_face,
 "max_shoulder_outward_offset_native":main.bounds[3]-wall_face,
 "main_shoulder_shared_wall_edge_length_native":main.boundary.intersection(wall0.boundary).length,
 "main_area_fraction_of_old_8937_mismatch":main.area/unknown.area,
 "other_13_small_unknown_components_area_native_sq":unknown.area-main.area,
 "main_source_original_largest_boundary_xy":list(map(list,main.exterior.coords)),
 "main_simplification_total_area_change_native_sq":main.symmetric_difference(shape).area,
 "experimental_B_variant_metrics":alternatives,
 "B_33_section_checks_per_variant":True,
 "B_99_total_true_source_arch_clearance_samples":len(all_section_rows),
 "B_80_upper_section_residual_exposed_area_native_sq":alternatives[1]["wedge_section_top_area_native_sq"],
 "B_80_full_wedge_mesh_watertight":True,
 "B_no_planar_overlap_5_original_R03_arches_in_99_samples":True,
 "B_no_planar_overlap_original_R03_upper_wall_interior_in_99_samples":True,
 "B_has_nominal_vertical_wall_face_but_masonry_bonding_is_not_validated":True,
 "B_mechanical_anchorage_to_source_wall":"NOT ESTABLISHED",
 "original_course_R03_upper_wall_duplicate_masonry_below_Z2400":"UNRESOLVED REPLACEMENT ZONE",
 "full_3D_SAT_boolean_collision":"NOT PERFORMED; 99 planar samples only",
 "historical_and_structural_validity":"NOT ESTABLISHED; speculative trial only",
 "source_F5ZL_C_support_schedule":"MISSING",
 "Blender_5_1_plus_test":"NOT PERFORMED",
 "candidate_80_glb":"M04_P04_R01_EXPERIMENTAL_80_UNIT_TAPERED_BACKING_KEY.glb",
 "source_file_SHA256":sha,
 "from_P03_true_recovered_source_alignment_min_fraction":source_source_q["min_real_source_restore_overlap_fraction"],
 "approval_status":"EXPERIMENTAL ONLY"}
(O/"M04_P04_R01_BACKING_STUDY_NUMERICAL_QA.json").write_text(json.dumps(report,indent=2)+"\n")
# Exact 1:1 plan drawing. Black confirmed source wall+rib envelope; dashed
# gray construction original springer; dashed red uncertain proposed cap.
def path(geom):
 pieces=[geom] if geom.geom_type=="Polygon" else list(geom.geoms)
 parts=[]
 for p in pieces:
  if p.geom_type!="Polygon":continue
  for ring in [p.exterior,*p.interiors]:
   parts.append("M "+" L ".join(f"{x:.6f},{-y:.6f}" for x,y in ring.coords)+" Z")
 return " ".join(parts)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="30700 1000 600 650">
<path d="{path(upper0)}" fill="none" stroke="#000" stroke-width="2"/>
<path d="{path(course_top)}" fill="none" stroke="#888" stroke-width="2.5" stroke-dasharray="9 6"/>
<path d="{path(main)}" fill="none" stroke="#b00" stroke-width="3" stroke-dasharray="8 6"/>
</svg>'''
(O/"M04_P04_R01_EXPOSED_SHOULDER_SOURCE_AND_EXPERIMENT_1TO1.svg").write_text(svg+"\n")
assert all(hashlib.sha256(x.read_bytes()).hexdigest()==sha[str(x)] for x in files)
print("M04_P04_SOURCE_COLLISION_STUDY_PASS",
 "source shoulder",round(main.area,4),
 "main boundary shared",round(report["main_shoulder_shared_wall_edge_length_native"],3),
 "wedge options",len(alternatives),
 "arch/wall samples",len(all_section_rows),
 "80_unit_glb",O/"M04_P04_R01_EXPERIMENTAL_80_UNIT_TAPERED_BACKING_KEY.glb")
print("EXPERIMENTAL_80UNIT_OPTION",bestlabel)
