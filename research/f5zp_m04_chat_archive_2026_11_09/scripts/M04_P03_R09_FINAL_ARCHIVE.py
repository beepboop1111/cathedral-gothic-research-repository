#!/usr/bin/env python3
"""Immutable P03 source-canonical five-bearing handoff. One final PNG."""
from pathlib import Path
import hashlib,json,shutil,zipfile
import trimesh
from PIL import Image
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
C=Path("/home/christopher/Documents/Cathedral/experimental")
Q=R/"M04_P03_R07_FIVE_GENUINE_ARCHES_PROTECTED_SOURCE_REGRESSION_EXPERIMENTAL"
S=R/"M04_P03_R05_ORIGINAL_RIB_SOURCE_ARCHITECTURAL_CONTACT_REBUILD_EXPERIMENTAL"
V=R/"M04_P03_R06_ALL_FIVE_ORIGINAL_ARCHES_SOURCE_MATCHED_EXPERIMENTAL"
REF=R/"M04_P03_R02B_CANONICAL_SPRINGER_AND_BEARING_MASONRY_EXPERIMENTAL"
FIX=R/"M04_P03_R05_ORIGINAL_FIVE_MEMBER_SECTION_FIXTURE_EXPERIMENTAL"
qa=json.loads((Q/"M04_P03_R07_FINAL_NUMERICAL_SOURCE_AND_APPROVAL_QA.json").read_text())
status=json.loads((S/"WORKFLOW_SUMMARY.json").read_text())
assert status["status"]=="passed" and status["passed"]==status["total"]==78
assert qa["R03_genuine_source_5_member_3D_sections_checked"]==35
assert qa["min_real_source_restore_overlap_fraction"]>.99997
assert qa["supported_source_first_bed_pct"]>99.999
assert 8800<qa["top_2d_mismatch_total_area_native_sq"]<9100
review=V/"F5ZP_M04_P03_R06_TRUE_FIVE_BEARING_RECOVERED_SOURCE_REVIEW.png"
with Image.open(review) as pic:
 assert pic.size==(1700,1515);pic.verify()
glbs=[
 (10,REF/"R03_TEN_PROTECTED_PIER_ARCH_AND_BEARING_MASONRY_REFERENCES.glb"),
 (12,S/"build/springer_variant.glb"),
 (14,V/"M04_P03_R06_R03_SOURCE_MATCHED_FIVE_MEMBER_CUTAWAY.glb")]
for count,path in glbs:
 sc=trimesh.load(str(path),force="scene",process=False)
 assert len(sc.geometry)==count,(path,len(sc.geometry))
sourceblend=C/"WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend"
assert hashlib.sha256(sourceblend.read_bytes()).hexdigest()==qa["sources_SHA256"][str(sourceblend)]
local=Path.home()/"Downloads"/review.name
assert not local.exists(),"User-visible previous review protected"
shutil.copy2(review,local)
paths={
 "sources/R03_PROTECTED_SOURCE.blend":sourceblend,
 "sources/R03_10_SOURCE_PIER_AND_GOTHIC_MEMBERS.glb":glbs[0][1],
 "sources/R03_QA.json":C/"WALL_PIER_JUNCTION_R03/QA.json",
 "sources/R02_CANONICAL_BEARING_QA.json":C/"SHARED_PIERS_R02/QA.json",
 "sources/R15_UNTOUCHED_ORIGINAL_MANIFEST.json":C/"SPRINGER_JUNCTION_R15/original_backing_manifest.json",
 "sources/R15_ORIGINAL_ARCH_SECTIONS_AND_CARRIERS.json":C/"SPRINGER_JUNCTION_R15/original_backing_inputs.json",
 "sources/CANONICAL_FIVE_BEARING_REFERENCE_QA.json":C/"UNIFIED_JUNCTION_INTERFACE_R01/INTERFACE_QA.json",
 "source_control/FIVE_ORIGINAL_SECTION_CANONICAL_FIXTURE.json":FIX/"M04_P03_R05_ORIGINAL_FIVE_MEMBER_SOURCE_FIXTURE.json",
 "source_control/FIVE_SOURCE_RESTORED_MEMBERS_AND_COURSES.glb":glbs[1][1],
 "source_control/R14_REBUILT_BLENDER_QA.json":S/"build/QA.json",
 "source_control/R14_REBUILT_GEOMETRY_QA.json":S/"build/GEOMETRY_QA.json",
 "source_control/R14_WORKFLOW_SUMMARY.json":S/"WORKFLOW_SUMMARY.json",
 "review/ONE_FINAL_GOTHIC_SOURCE_CUTAWAY.png":review,
 "review/R03_SOURCE_FIVE_BEARING_EDITABLE_CUTAWAY.blend":V/"M04_P03_R06_R03_SOURCE_MATCHED_FIVE_MEMBER_CUTAWAY_EXPERIMENTAL.blend",
 "review/R03_SOURCE_FIVE_BEARING_CUTAWAY_GLTF.glb":glbs[2][1],
 "review/CUTAWAY_TECHNICAL_QA.json":V/"M04_P03_R06_RENDER_QA.json",
 "measurements/REAL_R03_MEMBER_REGISTRATION_QA.json":REF/"M04_P03_R02B_PROTECTED_R03_MEMBER_REGISTRATION_QA.json",
 "measurements/35_3D_TRUE_ARCH_SECTION_REGRESSIONS.csv":Q/"M04_P03_R07_35_REAL_R03_SOURCE_ARCH_3D_REGRESSION.csv",
 "measurements/UPPER_JUNCTION_MEASURED_UNCERTAIN_REGIONS.csv":Q/"M04_P03_R07_TOP_BACKING_UNMATCHED_2D_REGIONS.csv",
 "measurements/UPPER_JUNCTION_SOURCE_1TO1.svg":Q/"M04_P03_R07_TRUE_UPPER_BACKING_SOURCE_MISMATCH_1TO1.svg",
 "measurements/NUMERICAL_APPROVAL_GATES.json":Q/"M04_P03_R07_FINAL_NUMERICAL_SOURCE_AND_APPROVAL_QA.json",
 "generator/REPRODUCE_SAFE_CANONICAL_ORIGINAL_SOURCE.py":R/"M04_P03_R08_REPRODUCE_SOURCE_CANONICAL_FIVE.py",
 "generator/COMPARE_35_ORIGINAL_R03_ARCH_SECTIONS.py":R/"M04_P03_R07_VERIFY_GENUINE_FIVE_AND_BACKING.py",
 "generator/CUTAWAY_BLENDER_SCRIPT.py":R/"M04_P03_R06_RENDER_ALL_FIVE_ORIGINAL_SOURCE_CUTAWAY.py",
 "generator/MASONRY_CONTACT_AUDIT.py":R/"M04_P03_R03_MEASURE_SOURCE_BEARING_AND_OVERLAPS.py",
 "engine_reference/R14_UNCHANGED_SPRINGER_WORKFLOW.py":C/"SPRINGER_WORKFLOW_R14/build_springer.py",
 "engine_reference/R12_UNCHANGED_CONTROLS.py":C/"SPRINGER_CONTROLS_R12/controls.py",
 "engine_reference/R11_UNCHANGED_ATTACH_SECTION.py":C/"SPRINGER_PROFILE_INPUT_R11/attach_section.py",
 "engine_reference/R06_UNCHANGED_SPRINGER_CORE.py":C/"SPRINGER_ENGINE_R06/springer_core.py",
 "engine_reference/R06_UNCHANGED_CASE_TOOLS.py":C/"SPRINGER_ENGINE_R06/case_tools.py",
 "engine_reference/R06_UNCHANGED_BLENDER_RUNNER.py":C/"SPRINGER_ENGINE_R06/blender_runner.py",
 "engine_reference/R07_UNCHANGED_RUNNER.py":C/"SPRINGER_ENGINE_R07_THREE_BEARING/run_checked.py",
 "engine_reference/R13_UNCHANGED_DIAGNOSTICS.py":C/"SPRINGER_DIAGNOSTICS_R13/diagnose.py",
 "profile_library/P02_USER_PROFILE_SELECTION_SCRIPT.py":R/"M04_P02_BUILD_SELECTED_PROFILE_THROUGH_EXISTING_R17.py"}
handoff=Q/"M04_P03_R07_FINAL_ARCHITECTURAL_HANDOFF.md"
handoff.write_text("""# M04 P03 R07 -- five true Gothic source members, source-aligned tas-de-charge

Technical/geometric **PASS** on recovered source-shaped 3D five-member fixture; architectural, historical and structural approval not granted.

This is the **S five-bearing shared chapel/wall pier** at global XYZ (31000,-1250,1800), and NOT the eight-bearing Pass6J R1/78 ambulatory pier.

Source five bearings: BAY1_RIB_1 133.8308602779 degrees, BAY2_RIB_0 46.1691397221 degrees, BAY1_FORMERET_0 180 degrees, BAY2_FORMERET_0 0 degrees, CHAPEL_TRANSVERSE_31000 90 degrees.

The initial R15 user-profile-18 substitution matched only ~71.9% of the real R03 BAY2_RIB_0 at upper sampled planes, despite engine QA. Restoring the archived original R15 source section in a COPIED manifest while preserving the canonical original rib azimuth passes all 78 R14 checks. Independent original R03 world-space sections verify 35/35 source member shapes with at least 99.99735% overlap.

A crucial support result: evaluate actual existing R03 central pier AND both lower receiving wall meshes, not just the core. More than 99.99981% of the five-source restored course's bottom section is supported at the sampled springing interface. This is planar geometric contact, not capacity.

The rebuilt five tas-de-charge courses geometrically duplicate existing R03 upper-wall masonry if placed by naive overlay. A source-based cutaway omits the old upper-wall segment at Z1800-2400 in the *experimental* view only, showing a possible replacement coordination. It does NOT alter any protected source.

Remaining above Z2400: 8937.45 square native units of top course are unmatched with the existing original R03 upper-wall plus all five R03 rib/arch sections. 8881.43 units lie in one irregular region behind the springing. This discrepancy is not a confirmed void or evidence to infill automatically; the correct backing junction, stone-bed interfaces and potential exposed ledges need construction evidence. See red-dashed SVG and numerical reports.

The source models were read-only; R03 original file SHA256 was checked. Source original Pass6J eight-member geometry is still separate and untouched. Original user profiles are not assigned: the user will choose mouldings and soffits, with profile P02 still available. F5ZL-C support schedule remains MISSING. Historical and structural validation NOT ASSESSED. Blender verified version 5.0.1; Blender 5.1+ was NOT tested. No GitHub work.

## Reproduce
Run generator/REPRODUCE_SAFE_CANONICAL_ORIGINAL_SOURCE.py --out NEW_DIRECTORY on MR COMPUTER (original project available), then source 35-section verifier and cutaway script. The reproducer rejects existing directories and does not overwrite protected files.
""")
paths["reports/HANDOFF_AND_APPROVAL_STATUS.md"]=handoff
script=R/"M04_P03_R09_FINAL_ARCHIVE.py"
paths["generator/PACKAGER.py"]=script
assert script.is_file() and all(p.exists() for p in paths.values())
manifest=[{"entry":name,"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for name,p in paths.items()]
mp=Q/"M04_P03_R09_FULL_ARCHIVE_SHA256_MANIFEST.json"
mp.write_text(json.dumps(manifest,indent=2)+"\n")
zipout=Path.home()/"Downloads"/"F5ZP_M04_P03_FIVE_CANONICAL_GOTHIC_SOURCE_ALIGNED_R07_EXPERIMENTAL_LOCAL.zip"
assert not zipout.exists(),"Prior handoff protected"
with zipfile.ZipFile(zipout,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for name,p in sorted(paths.items()):z.write(p,"M04_P03_R07/"+name)
 z.write(mp,"M04_P03_R07/MANIFEST_SHA256.json")
with zipfile.ZipFile(zipout) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(paths)+1
assert hashlib.sha256(sourceblend.read_bytes()).hexdigest()==qa["sources_SHA256"][str(sourceblend)]
print("M04_P03_FULL_PACKAGE_PASS","files",len(paths)+1,"size",zipout.stat().st_size,"zip",zipout)
print("FINAL_REVIEW_PNG",local)
print("FIVE_MEMBER_R14",status["passed"],status["total"],"true_Source_35_minfraction",qa["min_real_source_restore_overlap_fraction"],
      "base_support_percent",qa["supported_source_first_bed_pct"],"unresolved_upper",qa["top_2d_mismatch_total_area_native_sq"])
