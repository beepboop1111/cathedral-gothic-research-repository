#!/usr/bin/env python3
"""M04 P06 R09: INDEPENDENT Shapely source-section integrated R03 wall
vs source-correct tas course overlap. Avoid Blender Exact Boolean zero/
nonmanifold false negatives on coplanar original faces.
Geometric numerical sensitivity, not structural volume certification.
"""
from pathlib import Path
import numpy as np,trimesh,csv,json,hashlib
from scipy.integrate import simpson
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
O=R/"M04_P06_R09_TRUE_SOURCE_WALL_COURSE_SECTION_INTEGRATION_B523_EXPERIMENTAL"
assert not O.exists(),"Prior P06 diagnostic experiments protected"
O.mkdir()
SOURCE=R/"M04_P03_R02B_CANONICAL_SPRINGER_AND_BEARING_MASONRY_EXPERIMENTAL/R03_TEN_PROTECTED_PIER_ARCH_AND_BEARING_MASONRY_REFERENCES.glb"
CAND=R/"M04_P05_BLENDER523_R14_CANONICAL_FIVE_SOURCE_EXPERIMENTAL/build/springer_variant.glb"
ORIG=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
inputs=[SOURCE,CAND,ORIG]
assert all(p.exists() for p in inputs)
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
def glb_objects(path,shift=None):
 sc=trimesh.load(str(path),force="scene",process=False)
 output={}
 for name in sc.graph.nodes_geometry:
  T,key=sc.graph[name]
  mesh=sc.geometry[key].copy()
  mesh.apply_transform(T)
  v=mesh.vertices
  v[:]=np.c_[v[:,0],-v[:,2],v[:,1]]
  if shift is not None:v[:]+=shift
  mesh.vertices=v
  output[name]=mesh
 return output
ref=glb_objects(SOURCE)
task=glb_objects(CAND,np.array([31000.,-1250.,1800.]))
assert len(ref)==10 and len(task)==12
wall=ref["RECEIVING_S_UPPER_0"]
def section(m,z):
 c=m.section(plane_origin=(0,0,z),plane_normal=(0,0,1))
 if not c:raise ValueError(f"Absent section at {z}")
 polys=[]
 for line in c.discrete:
  if len(line)<4 or np.linalg.norm(line[0]-line[-1])>.01:continue
  poly=Polygon(line[:,:2])
  if not poly.is_valid:poly=poly.buffer(0)
  if poly.area>.001:polys.append(poly)
 x=unary_union(polys)
 assert x.is_valid and x.area>0,z
 return x
wall_areas=[section(wall,z).area for z in (1801.,2200.,2399.)]
assert max(wall_areas)-min(wall_areas)<1e-3,wall_areas
print("P06_WALL_EXTRUSION_TRACED",wall_areas)
wallshape=section(wall,2200.)
# Use fixed exact native wall polygon; five source course meshes remain unchanged.
# Equal steps by course; 0.02 from each end suppresses coplanar endpoint
# ambiguity. Uniform integration interpolates those narrow end intervals.
def integrate(course,z0,z1,n):
 zs=np.linspace(z0+.02,z1-.02,n)
 area_inter=[]
 area_course=[]
 for z in zs:
  profile=section(course,float(z))
  area_inter.append(profile.intersection(wallshape).area)
  area_course.append(profile.area)
 overlap=float(simpson(area_inter,x=zs))
 coursevol=float(simpson(area_course,x=zs))
 # Our bounding integration excludes 0.02*2 of the 120-unit extent,
 # and therefore is deliberately an INNER-INTERVAL estimate, not a strict
 # integral over the entire course. Relative error <=~0.04/120 when
 # profiles bounded/slow near course ends; report correctly as sampled
 # interior approximation, not certified 3D exact Boolean.
 return overlap,coursevol,min(area_inter),max(area_inter)
records=[]
for i in range(1,6):
 m=task[f"course_{i:02d}"]
 z0=1800.+(i-1)*120
 z1=z0+120
 trials=[]
 for n in (17,33,65):
  overlap,volume,mini,maxi=integrate(m,z0,z1,n)
  trials.append({"sampling_n":n,"overlap_cubed":overlap,"course_volume_cubed":volume,"min_contact_area":mini,"max_contact_area":maxi})
 assert all(a["overlap_cubed"]>0 for a in trials)
 convergence=abs(trials[2]["overlap_cubed"]-trials[1]["overlap_cubed"])
 source_meshvol=abs(m.volume)
 frac=trials[-1]["overlap_cubed"]/trials[-1]["course_volume_cubed"]
 assert 0<frac<1,(i,frac)
 records.append({"course_id":i,
  "world_start_Z":z0,"world_end_Z":z1,
  "wall_original_section_native_sq":wallshape.area,
  "source_R14_closed_course_mesh_volume_native_cubed":source_meshvol,
  "17_section_estimated_wall_overlap_cubed":trials[0]["overlap_cubed"],
  "33_section_estimated_wall_overlap_cubed":trials[1]["overlap_cubed"],
  "65_section_estimated_wall_overlap_cubed":trials[2]["overlap_cubed"],
  "65_section_interior_sampled_course_volume_cubed":trials[2]["course_volume_cubed"],
  "fraction_course_duplicate_in_original_wall_65_samples":frac,
  "33_to_65_grid_convergence_abs_native_cubed":convergence,
  "relative_grid_sensitivity":convergence/trials[-1]["overlap_cubed"],
  "diagnostic":"Approximate section integral; original Blender Boolean fails due exact coplanarity"})
 print("SOURCE_WALL_COURSE",i,"overlap_native3",round(records[-1]["65_section_estimated_wall_overlap_cubed"],3),
  "course",round(source_meshvol,3),"frac",round(frac,6),"gridrelative",round(records[-1]["relative_grid_sensitivity"],8),flush=True)
with (O/"M04_P06_SOURCE_R03_WALL_VS_FIVE_REAL_COURSES_3_RESOLUTION_INTEGRALS.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
total=sum(q["65_section_estimated_wall_overlap_cubed"] for q in records)
summed=sum(q["source_R14_closed_course_mesh_volume_native_cubed"] for q in records)
report={
 "Blender_5_2_3_Exact_Boolean_original_source_wall_behavior":"coplanar false-negative/unstable; DO NOT USE",
 "source_original_R03_wall_traced_sections_3_heights":[round(v,6) for v in wall_areas],
 "source_R03_wall_native_cross_section_area":wallshape.area,
 "five_course_17_33_65_sampling_sensitivity":records,
 "5_course_65_point_total_interior_wall_overlap_estimated_native_cubed":total,
 "5_course_total_exact_input_mesh_volume_native_cubed":summed,
 "5_course_wall_overlap_fraction_estimate":total/summed,
 "integral_type":"Shapely true original source XY section polygon intersection integrated with SciPy Simpson at 17/33/65 interior heights per course",
 "sample_boundary_strip_total_per_course_native_Z":.04,
 "full_exact_volumetric_boolean_proven":False,
 "geometric_overlap_is_substantial":total>sum(q["source_R14_closed_course_mesh_volume_native_cubed"] for q in records)*.5,
 "source_arch_five_original_profile_sections_unchanged":True,
 "source_R03_wall_unmodified":True,
 "approved_architectural_masonry_split":False,
 "historical_and_structural_approval":False,
 "source_SHA256":sha}
(O/"M04_P06_SOURCE_TRUE_WALL_SECTION_VOLUME_INTEGRATION_QA.json").write_text(json.dumps(report,indent=2)+"\n")
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in inputs)
print("P06_SOURCE_WALL_SECTION_INTEGRATION_FINISHED",round(total,3),"total native cubic approx",round(total/summed*100,4),"pct total course",flush=True)
