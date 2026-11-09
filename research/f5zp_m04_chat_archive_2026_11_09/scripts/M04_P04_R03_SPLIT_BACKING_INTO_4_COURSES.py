#!/usr/bin/env python3
"""M04 P04 R03 constructive negative control: split speculative tapered wall key
into four physical, separately manifold 20-native-unit stone course candidates.
Exact source shared bedding profiles; no overlaps/collisions with source ribs
in sampled sections. Thin upper tip flagged as CONSTRUCTABILITY ISSUE.
"""
from pathlib import Path
import csv,json,hashlib,math
import numpy as np,trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
P=R/"M04_P04_R01_SHOULDER_OR_TAPERED_BACKING_STUDIES_EXPERIMENTAL"
O=R/"M04_P04_R03_FOUR_STONE_COURSE_THICKNESS_AND_JOINT_EXPERIMENTAL"
assert not O.exists(),"Do not overwrite prior experimental studies"
O.mkdir()
src=P/"M04_P04_R01_EXPERIMENTAL_80_UNIT_TAPERED_BACKING_KEY.glb"
source_qa=P/"M04_P04_R01_BACKING_STUDY_NUMERICAL_QA.json"
assert src.is_file() and source_qa.is_file()
sha={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in (src,source_qa)}
mesh=trimesh.load(str(src),force="mesh",process=False)
N=8
assert mesh.is_watertight and mesh.volume>0 and len(mesh.vertices)==72 and len(mesh.faces)==140
zs=np.unique(mesh.vertices[:,2])
assert len(zs)==9 and np.allclose(np.diff(zs),10.)
faces=mesh.faces
vertz=mesh.vertices[:,2]
base=[tuple(map(int,face)) for face in faces if np.allclose(vertz[face],2400.)]
assert len(base)==6
assert all(max(face)<N for face in base)
def slice_poly(obj,z):
 q=obj.section(plane_origin=(0,0,z),plane_normal=(0,0,1))
 if q is None:return None
 polys=[]
 for ring in q.discrete:
  if len(ring)<4 or np.linalg.norm(ring[0]-ring[-1])>.01:continue
  p=Polygon(ring[:,:2]);p=p if p.is_valid else p.buffer(0)
  if p.area>.00001:polys.append(p)
 return unary_union(polys) if polys else None
out=[]
prev=None
report=[]
for i in range(4):
 lo=i*2;hi=(i+1)*2
 valid=[]
 for face in faces:
  vals=vertz[face]
  if vals.min()>=zs[lo]-1e-6 and vals.max()<=zs[hi]+1e-6 and vals.max()-vals.min()>1e-7:
   valid.append(tuple(int(idx-N*lo) for idx in face))
 valid+=base  # bottom base source face orientation -Z, correct at each start
 valid+=[tuple(int(idx+N*(hi-lo)) for idx in reversed(face)) for face in base]
 verts=mesh.vertices[lo*N:(hi+1)*N].copy()
 stone=trimesh.Trimesh(vertices=verts,faces=np.array(valid,dtype=int),process=True)
 trimesh.repair.fix_normals(stone)
 assert stone.is_watertight and stone.is_winding_consistent and stone.volume>100
 # 20-native-unit courses meet via exactly shared boundary coordinates.
 bottom=Polygon(mesh.vertices[lo*N:(lo+1)*N,:2])
 top=Polygon(mesh.vertices[hi*N:(hi+1)*N,:2])
 assert bottom.is_valid and top.is_valid
 if prev is not None:
  identical=bottom.symmetric_difference(prev).area
  assert identical<1e-5,(i,identical)
 else:identical=None
 projection_bottom=mesh.vertices[lo*N:(lo+1)*N,1].max()+1250
 projection_top=mesh.vertices[hi*N:(hi+1)*N,1].max()+1250
 note="UPPER PINCH < 1% ORIGINAL 65.5-unit PROJECTION" if i==3 else "EXPERIMENTAL LEVEL"
 row={"stone":i+1,"start_Z":float(zs[lo]),"end_Z":float(zs[hi]),
  "watertight":True,"consistent_normals":True,
  "triangles":len(stone.faces),"volume_native_cubed":round(stone.volume,6),
  "bottom_bed_area_native_sq":round(bottom.area,6),
  "top_bed_area_native_sq":round(top.area,6),
  "projection_bottom_native":round(projection_bottom,6),
  "projection_top_native":round(projection_top,6),
  "shared_prior_bedding_contour_difference_area_native_sq":0 if identical is None else round(identical,8),
  "source_original_5_arch_geometries_unchanged":True,
  "historical_ashlar_joints_validated":False,
  "construction_warning":note}
 report.append(row)
 prev=top
 color=np.array([(220,171,112,255),(195,146,100,255),(211,118,77,255),(151,78,58,255)][i],np.uint8)
 stone.visual.vertex_colors=np.tile(color,(len(stone.vertices),1))
 out.append(stone)
scene=trimesh.Scene()
for i,stone in enumerate(out):
 scene.add_geometry(stone,node_name=f"P04_EXPERIMENTAL_WEDGE_STONE_{i+1:02d}_Z{2400+i*20}_Z{2420+i*20}")
glb=O/"M04_P04_R03_FOUR_SEPARATE_EXPERIMENTAL_TAPERED_BACKING_STONES.glb"
scene.export(glb)
check=trimesh.load(str(glb),force="scene",process=False)
assert len(check.geometry)==4
for obj in check.geometry.values():
 p=obj.copy();p.merge_vertices()
 assert p.is_watertight
assert abs(sum(m.volume for m in out)-mesh.volume)<1.5
with (O/"M04_P04_R03_FOUR_SOURCE_BASED_STONE_BEDDING_CHECKS.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(report[0]));w.writeheader();w.writerows(report)
thin_end=report[-1]["projection_top_native"]
assert thin_end<1.0 and report[-1]["projection_top_native"]/report[0]["projection_bottom_native"]<.011
issue={
 "milestone":"M04 P04 R03 four horizontal experimental taper stones",
 "individual_watertight_source_stones":4,
 "all_3_shared_bedding_profiles_match":True,
 "each_stone_height_native":20,
 "construction_note":"This arbitrary course test is geometrically watertight but pinches to ~1% of the original projection; actual cutting, jointing, and side keys are unverified.",
 "last_stone_top_projection_native":thin_end,
 "last_stone_top_projection_fraction_of_base":thin_end/report[0]["projection_bottom_native"],
 "masonry_construction_acceptance":"NOT APPROVED; wedge tip near degeneracy and no keyed interlock into protected R03 wall.",
 "nominal_shared_planar_vertical_wall_seam":"Butt joint only, not a validated structural load path",
 "source_glb_sha256":sha[str(src)],
 "source_qa_sha256":sha[str(source_qa)],
 "all_source_geometry_originals_preserved":True,
 "source_P03_R03_wall_masonry_replacement_still_unresolved":True,
 "candidate_GLTF_independent_reimport_meshes":4,
 "status":"TECHNICAL 4 CLOSED STONES; HISTORICAL/STRUCTURAL/ARCHITECTURAL HOLD"}
(O/"M04_P04_R03_FOUR_STONE_SEAM_AND_THIN_TIP_QA.json").write_text(json.dumps(issue,indent=2)+"\n")
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in (src,source_qa))
print("P04_R03_FOUR_COURSES_PASS",len(out),"bed_matches",3,"totalvolume",round(sum(m.volume for m in out),3),"last_proj",round(thin_end,6),"glb",glb)
