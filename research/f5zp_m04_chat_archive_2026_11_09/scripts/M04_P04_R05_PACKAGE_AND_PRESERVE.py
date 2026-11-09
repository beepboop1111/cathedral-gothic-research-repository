#!/usr/bin/env python3
"""M04 P04 final local archive and one final PNG to Downloads, sources protected."""
from pathlib import Path
import json,hashlib,shutil,zipfile
import trimesh
from PIL import Image
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
P=R/"M04_P04_R01_SHOULDER_OR_TAPERED_BACKING_STUDIES_EXPERIMENTAL"
D=R/"M04_P04_R03_FOUR_STONE_COURSE_THICKNESS_AND_JOINT_EXPERIMENTAL"
E=R/"M04_P04_R04_FINAL_FOUR_STONE_CONSTRUCTABILITY_REVIEW_EXPERIMENTAL"
S=R/"M04_P03_R07_FIVE_GENUINE_ARCHES_PROTECTED_SOURCE_REGRESSION_EXPERIMENTAL"
G=R/"M04_P03_R05_ORIGINAL_RIB_SOURCE_ARCHITECTURAL_CONTACT_REBUILD_EXPERIMENTAL"
O=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
qa=json.loads((P/"M04_P04_R01_BACKING_STUDY_NUMERICAL_QA.json").read_text())
stone=json.loads((D/"M04_P04_R03_FOUR_STONE_SEAM_AND_THIN_TIP_QA.json").read_text())
sceneqa=json.loads((E/"M04_P04_R04_BLENDER_ASSEMBLY_AND_DRAWING_QA.json").read_text())
p03=json.loads((S/"M04_P03_R07_FINAL_NUMERICAL_SOURCE_AND_APPROVAL_QA.json").read_text())
assert qa["B_99_total_true_source_arch_clearance_samples"]==99
assert len(qa["experimental_B_variant_metrics"])==3
assert stone["individual_watertight_source_stones"]==4 and stone["all_3_shared_bedding_profiles_match"]
assert stone["last_stone_top_projection_native"]<1
assert sceneqa["saved_scene_total_18_meshes"]==18
assert sceneqa["round_trip_experimental_glb_mesh_count"]==18
assert sceneqa["saved_scene_original_five_arch_meshes_visible"]
assert hashlib.sha256(O.read_bytes()).hexdigest()==p03["sources_SHA256"][str(O)]
for count,p in ((1,P/"M04_P04_R01_EXPERIMENTAL_80_UNIT_TAPERED_BACKING_KEY.glb"),
 (4,D/"M04_P04_R03_FOUR_SEPARATE_EXPERIMENTAL_TAPERED_BACKING_STONES.glb"),
 (18,E/"M04_P04_R04_FIVE_ARCHES_AND_FOUR_SEPARATE_TEST_STONES_EXPERIMENTAL.glb")):
 s=trimesh.load(str(p),force="scene",process=False)
 assert len(s.geometry)==count
 if count in (1,4):
  for obj in s.geometry.values():
   cp=obj.copy()
   cp.merge_vertices()
   assert cp.is_watertight
final=E/"F5ZP_M04_P04_R04_ONE_ASHLAR_FEASIBILITY_REVIEW.png"
with Image.open(final) as png:
 assert png.size==(2320,1500);png.verify()
final_png=Path.home()/"Downloads"/"F5ZP_M04_P04_FINAL_UPPER_BACKING_ASHLAR_REVIEW.png"
assert not final_png.exists(),"Do not overwrite final review image"
shutil.copy2(final,final_png)
handoff=P/"M04_P04_R05_FINAL_HANDOFF.md"
handoff.write_text("""# F5ZP M04 P04 -- Upper Gothic springer/backing junction

Study is on the experimental FIVE-bearing shared chapel and wall pier S, at world (31000,-1250,1800), not the separate protected eight-member Pass6J R1/78 ambulatory pier.

Original five R03 Gothic source rib sections and R14 source-restored five tas courses are preserved. Previous P03 source registration: 78 of 78 generic tests, 35 genuine original rib section checks at five member identities, and greater than 99.9998% lower R03 pier and wall source bearing coverage.

The upper section discrepancy is NOT a certified hole. Its main source-exposed shoulder is 8881.425 native square units, extends 65.517 native outward from wall face Y=-1250, and shares 211.087 native units of boundary with the original wall.

A: original source shoulder retained without added stone; historical desirability and force path not proven.

B: speculative 40/80/120 unit tapering keys based on that exposed original polygon. All 3 are watertight and 99 sampled 2D checks find no intersection with protected five source rib silhouettes or the upper R03 wall interior. The 80-high example has a nominal vertical wall-face contact but no verified mechanical bond. Only source-derived plan geometry is demonstrated, not an historically measured ashlar.

C: experimental 80-high option split into four independently watertight 20-high candidate courses; all three common horizontal bedding outlines are identical. However the last 20-high stone tapers to only 0.655 native projection (approximately 1 percent of its starting projection) and the wall interface is an unkeyed vertical butt joint. Architectural acceptance WITHHELD for that constructability concern. This is a technical regression, not approval.

The existing R03 upper-wall receiver geometrically duplicates a portion of the lower R14 tas course; no source wall was removed or remodeled. The other small source-mismatch regions were not filled. Full 3D boolean collision testing, stone rear geometry, force path, historical coursing, shear/bearing capacity and F5ZL-C support schedule remain unresolved.

Validation: technical PASS for 1 wedge and 4 closed course solids, three shared beds, and Blender/GLB reimport of 18 source plus candidate objects. Geometric PARTIAL: 99 distinct sampled 2D source-plane clearances, not continuous 3D contact proof. Architectural NOT APPROVED. Historical and structural NOT VALIDATED. Tested in Blender 5.0.1, not 5.1+. Protected R03, Pass6J, R11/R14/R17 generators untouched; no GitHub operations.

B comparison image temporarily hides original five source arches ONLY during the B view to expose the hypothetical backing geometry. In final Blender and GLB all those original arches remain visible and mesh data preserved. Source hashes and scripts included in package, with an independent single final PNG in Downloads.
""")
paths={
"original/R03_PROTECTED_SOURCE.blend":O,
"original/P03_FIVE_ORIGINAL_ARCHES_AND_COURSES.glb":G/"build/springer_variant.glb",
"original/P03_TRUE_SOURCE_JUNCTION_QA.json":S/"M04_P03_R07_FINAL_NUMERICAL_SOURCE_AND_APPROVAL_QA.json",
"original/P03_TRUE_SOURCE_35_ARCH_MEASUREMENTS.csv":S/"M04_P03_R07_35_REAL_R03_SOURCE_ARCH_3D_REGRESSION.csv",
"original/R03_10_PROTECTED_REFERENCE_MESHES.glb":R/"M04_P03_R02B_CANONICAL_SPRINGER_AND_BEARING_MASONRY_EXPERIMENTAL/R03_TEN_PROTECTED_PIER_ARCH_AND_BEARING_MASONRY_REFERENCES.glb",
"scripts/M04_P04_R01_GENERATE_BACKING_TESTS.py":R/"M04_P04_R01_GENERATE_BACKING_TESTS.py",
"scripts/M04_P04_R02_RENDER_BACKING_COMPARISON.py":R/"M04_P04_R02_RENDER_BACKING_COMPARISON.py",
"scripts/M04_P04_R02C_RENDER_SOURCE_EXPOSED_WEDGE.py":R/"M04_P04_R02C_RENDER_SOURCE_EXPOSED_WEDGE.py",
"scripts/M04_P04_R03_SPLIT_BACKING_INTO_4_COURSES.py":R/"M04_P04_R03_SPLIT_BACKING_INTO_4_COURSES.py",
"scripts/M04_P04_R04_RENDER_FOUR_STONE_FEASIBILITY.py":R/"M04_P04_R04_RENDER_FOUR_STONE_FEASIBILITY.py",
"scripts/M04_P04_R05_PACKAGE_AND_PRESERVE.py":R/"M04_P04_R05_PACKAGE_AND_PRESERVE.py",
"QA/3_TAPER_HEIGHT_TESTS.csv":P/"M04_P04_THREE_SOURCE_BACKING_TAPER_VARIANTS.csv",
"QA/99_SOURCE_SECTION_CLEARANCES.csv":P/"M04_P04_99_EXACT_2D_BACKING_CLEARANCE_SECTIONS.csv",
"QA/EXPOSED_SHOULDER_AND_CANDIDATE_1TO1.svg":P/"M04_P04_R01_EXPOSED_SHOULDER_SOURCE_AND_EXPERIMENT_1TO1.svg",
"QA/SOURCE_SHOULDER_TEST.json":P/"M04_P04_R01_BACKING_STUDY_NUMERICAL_QA.json",
"QA/FOUR_STONE_BEDDING.csv":D/"M04_P04_R03_FOUR_SOURCE_BASED_STONE_BEDDING_CHECKS.csv",
"QA/FOUR_STONE_CONSTRUCTABILITY.json":D/"M04_P04_R03_FOUR_STONE_SEAM_AND_THIN_TIP_QA.json",
"QA/BLENDER_GLTF_ROUNDTRIP.json":E/"M04_P04_R04_BLENDER_ASSEMBLY_AND_DRAWING_QA.json",
"asset/ONE_EXPERIMENTAL_TAPERED_KEY.glb":P/"M04_P04_R01_EXPERIMENTAL_80_UNIT_TAPERED_BACKING_KEY.glb",
"asset/FOUR_EXPERIMENTAL_SEPARATE_STONES.glb":D/"M04_P04_R03_FOUR_SEPARATE_EXPERIMENTAL_TAPERED_BACKING_STONES.glb",
"asset/FOUR_STONES_FIVE_TRUE_ARCHES_AND_COURSES.glb":E/"M04_P04_R04_FIVE_ARCHES_AND_FOUR_SEPARATE_TEST_STONES_EXPERIMENTAL.glb",
"asset/EDITABLE_SOURCE_ARCHES_AND_STONES.blend":E/"M04_P04_R04_FIVE_ORIGINAL_ARCHES_AND_FOUR_HYPOTHETICAL_STONES_EXPERIMENTAL.blend",
"review/ONE_FINAL_M04_P04_PNG.png":final,
"report/STATUS_AND_UNRESOLVED_APPROVALS.md":handoff}
assert all(f.exists() for f in paths.values())
manifest=[{"path":k,"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()} for k,f in sorted(paths.items())]
mp=P/"M04_P04_R05_FINAL_SHA256_MANIFEST.json"
mp.write_text(json.dumps(manifest,indent=2)+"\n")
zipout=Path.home()/"Downloads"/"F5ZP_M04_P04_UPPER_BACKING_STONE_FEASIBILITY_EXPERIMENTAL_LOCAL.zip"
assert not zipout.exists(),"Prior handoff archive protected"
with zipfile.ZipFile(zipout,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for k,f in sorted(paths.items()):z.write(f,"M04_P04/"+k)
 z.write(mp,"M04_P04/MANIFEST_SHA256.json")
with zipfile.ZipFile(zipout) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(paths)+1
assert hashlib.sha256(O.read_bytes()).hexdigest()==p03["sources_SHA256"][str(O)]
print("M04_P04_FINAL_ARCHIVE_PASS",len(paths)+1,"FILE_ENTRIES",zipout.stat().st_size,"BYTES")
print("ONE_FINAL_REVIEW_IMAGE",final_png)
print("LOCAL_EXPERIMENTAL_HANDOFF",zipout)
print("SUMMARY",json.dumps({"shoulder_area":qa["source_main_exposed_shoulder_area_native_sq"],
 "contact_samples":qa["B_99_total_true_source_arch_clearance_samples"],
 "four_closed_ashlars":stone["individual_watertight_source_stones"],
 "bed_interfaces":3,"upper_projection":stone["last_stone_top_projection_native"],
 "source_unchanged":True,"architectural_approval":False}))
