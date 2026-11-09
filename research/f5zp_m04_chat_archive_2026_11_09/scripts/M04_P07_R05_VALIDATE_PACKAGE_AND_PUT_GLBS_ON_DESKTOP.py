#!/usr/bin/env python3
"""M04 P07 R05 – verified Desktop GLBs + one PNG, immutable handoff.
No source overwrites, no GitHub, user-profile assignments withheld.
"""
from pathlib import Path
import hashlib,json,shutil,zipfile
import numpy as np,trimesh
from PIL import Image
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
P1=R/"M04_P07_R01_FIVE_REAL_ARCH_INTERFACE_CONTACT_EXPERIMENTAL"
P2=R/"M04_P07_R02_EXACT_TOP_BED_NATIVE_SOURCE_BEARINGS_EXPERIMENTAL"
P3=R/"M04_P07_R03_B523_3D_SOURCE_CONTACT_DIAGNOSTICS_EXPERIMENTAL"
P6=R/"M04_P06_R11_COORDINATED_TRUE_SOURCE_WALL_AND_ARCHES_B523_EXPERIMENTAL"
P6QA=R/"M04_P06_R12_INDEPENDENT_TRUE_SOURCE_GLTF_REGRESSION_B523_EXPERIMENTAL"
ORIGINAL=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
A=P6/"M04_P06_B523_FIVE_GOTHIC_ARCHES_WALL_EXACTLY_COORDINATED_EXPERIMENTAL.glb"
B=P3/"M04_P07_B523_TRUE_GOTHIC_FIVE_BEARINGS_PLUS_DIAGNOSTIC_SURFACES.glb"
IMG=P3/"F5ZP_M04_P07_FINAL_ONE_REAL_GOTHIC_BEARING_REVIEW.png"
assert all(p.is_file() for p in [A,B,IMG,ORIGINAL])
p1=json.loads((P1/"M04_P07_R01_SOURCE_CONTACT_NUMERICAL_QA.json").read_text())
p2=json.loads((P2/"M04_P07_R02_EXACT_NATIVE_SOURCE_BEARING_QA.json").read_text())
p3=json.loads((P3/"M04_P07_B523_RENDER_AND_GLB_REGRESSION_QA.json").read_text())
p6=json.loads((P6QA/"M04_P06_R12_INDEPENDENT_GEOMETRY_AND_FIVE_WAY_SOURCE_QA.json").read_text())
assert p6["true_original_world_space_GLTF_scene_elements"]==14 and p6["sampled_source_arch_walls_lower_and_tas_shape_tests"]==25
assert p1["base_tas_support_coverage_pct"]>99.9998 and p2["five_local_seating_fraction_min"]>.9995
assert p2["upper_wall_outside_tas_top_area"]<.001
assert 8900<p2["upper_exact_top_uncertain_shoulder_native_sq"]<9000
assert p3["source_original_14_plus_new_7_GLTF_roundtrip"]==21
assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()==p2["source_sha256"][str(ORIGINAL)]
with Image.open(IMG) as im:assert im.size==(2630,1590);im.verify()
source=trimesh.load(str(A),force="scene",process=False)
diag=trimesh.load(str(B),force="scene",process=False)
names=set(source.graph.nodes_geometry)
diag_names=set(diag.graph.nodes_geometry)
assert len(names)==14 and len(diag_names)==21 and names<diag_names
max_bbox_error=0.
for n in names:
 ta,ka=source.graph[n];tb,kb=diag.graph[n]
 ma=source.geometry[ka].copy();ma.apply_transform(ta)
 mb=diag.geometry[kb].copy();mb.apply_transform(tb)
 ma.merge_vertices()
 assert ma.is_watertight,n
 max_bbox_error=max(max_bbox_error,float(np.abs(ma.bounds-mb.bounds).max()))
assert max_bbox_error<.0001,max_bbox_error
# Source 14 meshes retain same geometry; 7 diagnostic overlays are open
# zero-thickness surfaces and MUST NOT be counted as new stone.
extra=diag_names-names
assert len(extra)==7 and all(n.startswith("P07_DIAGNOSTIC_NON_MASONRY_") for n in extra)
finalqa={
 "checkpoint":"M04 P07 R05 / Blender 5.2.3",
 "original_R03_source_file_SHA256":hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),
 "original_14_source_GLB_SHA256":hashlib.sha256(A.read_bytes()).hexdigest(),
 "source_plus_7_nonphysical_diagnostic_GLB_SHA256":hashlib.sha256(B.read_bytes()).hexdigest(),
 "first_course_supported_by_original_lower_pier_pct":p1["base_tas_support_coverage_pct"],
 "exact_top_371_triangle_faces":p2["exact_371_source_course05_horizontal_triangle_faces"],
 "last_course_original_upper_wall_footprint_supported_pct":100.,
 "local_five_original_Gothic_arch_seating_fraction_min":p2["five_local_seating_fraction_min"],
 "exact_external_shoulder_plan_area_native_sq":p2["upper_exact_top_uncertain_shoulder_native_sq"],
 "source_14_meshes_closed":True,
 "source_14_meshes_roundtrip_identical_world_bounds_native_max_error":max_bbox_error,
 "source_diagnostic_GLTF_total_meshes":21,
 "additional_zero_thickness_nonmasonry_contact_patches":len(extra),
 "P06_25_source_comparisons_passed":True,
 "P07_geometric_source_bearings_five_passed":True,
 "historical_bonding_verified":False,"structural_load_capacity_verified":False,
 "architectural_approval":False,
 "F5ZL_C_support_schedule":"MISSING",
 "original_eight_bearing_Pass6J_separate_and_untouched":True,
 "source_R03_original_file_unchanged":True,
 "user_final_profile_selection":"NONE"}
QA=P3/"M04_P07_R05_INDEPENDENT_GLB_SHA256_AND_SOURCE_APPROVAL_QA.json"
QA.write_text(json.dumps(finalqa,indent=2)+"\n")
handoff=P3/"M04_P07_R05_HANDOFF.md"
handoff.write_text("""# F5ZP M04 P07 — Source-correct Gothic 5-way junction

## Preserved baseline
Shared chapel/wall junction **S** at XYZ (31000,-1250,1800), not the separately protected 8-way Pass6J R1/78 ambulatory pier. The source R03 blend, original R14 R15, vaults, all approved F5ZK-C/F5ZN-A geometry, original sections and generators are read-only. Tested Blender 5.2.3 LTS.

## Validations
M04 P06: 14 closed source-aligned solids (3 original lower supports, 5 source-restored coursed springer meshes, 1 original R03 upper wall and 5 genuine original arch/rib meshes), exact experimental copies trimmed at Z2400. Blender 5.2.3 GLB reimport 14/14 and 25 original-mesh sampled source comparisons PASS. Original upper wall no longer occupies same Z range as the new five spring courses in this isolated assembly; no actual approved wall was removed.

M04 P07: source original R14 top of course 05 measured from exactly 371 planar mesh triangles at Z2400. Original wall 144,000 native square units is **100%** on that top bearing. The source FIVE local arch/rib spring seats individually overlap 99.9588–99.9768% of the precise horizontal course. Remote arch ends (at their other piers) are excluded rather than miscounted as unsupported local stone. The first tas course is 99.999817% over the combined THREE lower R03 source support solids in an adjacent-plane section comparison.

The exact top of the course has a 8,933.53 native² outward shoulder not covered by upper wall or sampled original arches. It is an exposed construction discrepancy, NOT proof of a void or an invitation to automatically add stone. Upper rear keying, bedding shear, historic coursing, final profile selection and F5ZL-C schedule remain open. No structural or historical approval granted.

Two final Desktop GLBs: clean 14-mesh source coordination and 21-mesh source+7 **zero thickness NON-MASONRY** XY bearing diagnostic surfaces; both maintain the identical 14 original mesh objects and world-space bounds (max difference 0). Contact surfaces are designed to be toggled by their own Blender collection. No additional construction solids were added.

Final one review PNG uses a genuine Blender 5.2.3 rendered source scene and a measured 1:1 Z2400 plan. SVG layer conventions: confirmed original wall solid black, experimental course outline dashed gray, uncertain external shoulder dashed red.

Reproducible scripts and checks are in this ZIP and the local experimental checkpoint directories. No GitHub operations or approved source writes.
""")
files={
 "GLB/M04_P06_CLEAN_14_SOURCE_COURSES_WALL_ARCHES.glb":A,
 "GLB/M04_P07_REAL_SOURCE_PLUS_7_NONMASONRY_DIAGNOSTICS.glb":B,
 "BLEND/M04_P07_B523_EDITABLE_SOURCE_PLUS_DIAGNOSTICS.blend":P3/"M04_P07_B523_FIVE_GOTHIC_BEARINGS_PLUS_SOURCE_DIAGNOSTICS_EXPERIMENTAL.blend",
 "BLEND/M04_P06_B523_CLEAN_SOURCE.blend":P6/"M04_P06_B523_CANONICAL_CUT_OPEN_WALL_AND_RIBS_EXPERIMENTAL.blend",
 "REVIEW/ONE_FINAL_GOTHIC_ARCHITECTURAL_REVIEW.png":IMG,
 "QA/M04_P07_R05_INDEPENDENT_GLB_SHA256_AND_SOURCE_APPROVAL_QA.json":QA,
 "QA/M04_P07_R01_SOURCE_CONTACT_NUMERICAL_QA.json":P1/"M04_P07_R01_SOURCE_CONTACT_NUMERICAL_QA.json",
 "QA/M04_P07_R02_EXACT_NATIVE_SOURCE_BEARING_QA.json":P2/"M04_P07_R02_EXACT_NATIVE_SOURCE_BEARING_QA.json",
 "QA/M04_P07_R03_BLENDER_523_RENDER_AND_GLB_QA.json":P3/"M04_P07_B523_RENDER_AND_GLB_REGRESSION_QA.json",
 "QA/M04_P06_25_REAL_SOURCE_COMPARE_QA.json":P6QA/"M04_P06_R12_INDEPENDENT_GEOMETRY_AND_FIVE_WAY_SOURCE_QA.json",
 "QA/P07_R01_12_BEARING_TESTS.csv":P1/"M04_P07_R01_ALL_REAL_ARCH_AND_TAS_CONTACTS.csv",
 "QA/P07_R02_FIVE_EXACT_GOTHIC_BEARINGS.csv":P2/"M04_P07_R02_FIVE_ACTUAL_GOTHIC_ARCH_LOCAL_BEARINGS.csv",
 "QA/P07_TRUE_SOURCE_EXACT_Z2400.geojson":P2/"M04_P07_R02_EXACT_TOP_AND_ACTUAL_FIVE_ARCHES.geojson",
 "QA/P07_SOURCE_MASONRY_EXPOSED_SHOULDER_1TO1.svg":P2/"M04_P07_R02_EXACT_1TO1_BEARING_AND_UNCERTAIN_SHOULDER.svg",
 "QA/P07_DIAGNOSTIC_TRIANGLES.json":P3/"M04_P07_R03_TRUE_SOURCE_DIAGNOSTIC_SURFACE_TRIANGLES.json",
 "SCRIPT/M04_P07_R01_LOCAL_FIVE_ARCH_CONTACTS.py":R/"M04_P07_R01_AUDIT_FIVE_REAL_BEARING_CONTACTS.py",
 "SCRIPT/M04_P07_R02_EXACT_SOURCE_TOP.py":R/"M04_P07_R02_EXACT_TOP_AND_FIVE_ARCH_BEARINGS.py",
 "SCRIPT/M04_P07_R03_GENERATE_REAL_SOURCE_OVERLAY_TRIANGLES.py":R/"M04_P07_R03_PREPARE_EXACT_CONTACT_DIAGNOSTIC_MESHES.py",
 "SCRIPT/M04_P07_R03_BLENDER523_RENDER_AND_GLTF.py":R/"M04_P07_R03_B523_RENDER_SOURCE_AND_EXPORT_DIAGNOSTICS.py",
 "SCRIPT/M04_P07_R04_COMPOSITE_ONE_PNG.py":R/"M04_P07_R04_COMPOSE_ONE_SOURCE_ARCH_BEARING_PNG.py",
 "SCRIPT/M04_P07_R05_FINAL_QA_AND_DESKTOP_FILES.py":R/"M04_P07_R05_VALIDATE_PACKAGE_AND_PUT_GLBS_ON_DESKTOP.py",
 "REPORT/M04_P07_R05_HANDOFF.md":handoff}
assert all(p.is_file() for p in files.values())
manifest=[{"archive_entry":name,"file_size_bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for name,p in sorted(files.items())]
manifest_file=P3/"M04_P07_R05_FINAL_FILE_SHA256_MANIFEST.json"
manifest_file.write_text(json.dumps(manifest,indent=2)+"\n")
zipout=Path.home()/"Downloads"/"F5ZP_M04_P07_B523_FIVE_GOTHIC_BEARING_SOURCE_AND_CONTACT_HANDOFF_EXPERIMENTAL.zip"
assert not zipout.exists(),"Preserve previous handoffs"
with zipfile.ZipFile(zipout,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for name,p in sorted(files.items()):z.write(p,"M04_P07/"+name)
 z.write(manifest_file,"M04_P07/SHA256_MANIFEST.json")
with zipfile.ZipFile(zipout) as z:
 assert z.testzip() is None and len(z.namelist())==len(files)+1
# User requested GLBs on Desktop. Only after all technical tests and ZIP
# validation pass are files copied: never overwrite pre-existing work.
desk=Path.home()/"Desktop"
destA=desk/"F5ZP_M04_P06_B523_FIVE_GOTHIC_BEARINGS_CLEAN_SOURCE_14_MESHES.glb"
destB=desk/"F5ZP_M04_P07_B523_GOTHIC_BEARING_CONTACT_DIAGNOSTICS_21_MESHES.glb"
pngout=Path.home()/"Downloads"/"F5ZP_M04_P07_FINAL_ONE_REAL_GOTHIC_BEARING_REVIEW.png"
assert desk.is_dir()
assert all(not p.exists() for p in (destA,destB,pngout)), "Never overwrite Desktop or review checkpoint"
shutil.copy2(A,destA)
shutil.copy2(B,destB)
shutil.copy2(IMG,pngout)
assert hashlib.sha256(destA.read_bytes()).hexdigest()==finalqa["original_14_source_GLB_SHA256"]
assert hashlib.sha256(destB.read_bytes()).hexdigest()==finalqa["source_plus_7_nonphysical_diagnostic_GLB_SHA256"]
assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()==p2["source_sha256"][str(ORIGINAL)]
print("M04_P07_FINAL_DELIVERABLE_QA_PASS",len(files)+1,"archive_files",zipout.stat().st_size,"bytes")
print("DESKTOP_GLB_CLEAN",destA)
print("DESKTOP_GLB_BEARING_DIAGNOSTICS",destB)
print("ONE_REVIEW_PNG",pngout)
print("LOCAL_HANDOFF_ZIP",zipout)
print("ORIGINAL_14_MESHES_SAME_BOUNDS",max_bbox_error)
