#!/usr/bin/env python3
"""Consolidated source-preserving M02 Phase F local checkpoint.
No approved generators modified; excludes experimental 14 outer subdivisions.
"""
from pathlib import Path
import json,csv,hashlib,shutil,zipfile
from shapely.geometry import shape
from PIL import Image
R=Path(__file__).resolve().parent
OUT=R/"F5ZP_M02_CONSOLIDATED_CHECKPOINT_R01_LOCAL"
STAGE=OUT/"CHECKPOINT"
assert not STAGE.exists(),"Protected existing checkpoint: version before new run"
sources=[
("source/R11_ORIGINAL.geojson","R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson"),
("intent/R30_OPEN_INTERIOR_INTENT.md","R30_OPEN_INTERIOR_ARCHITECTURAL_INTENT_R01/ARCHITECTURAL_OPEN_INTERIOR_INTENT.md"),
("intent/R30_MEASURED_SEVEN_FACES.json","R30_OPEN_INTERIOR_ARCHITECTURAL_INTENT_R01/SOURCE_GEOMETRY_EVIDENCE.json"),
("intent/R31_OPEN_SANCTUARY_1TO1.geojson","R31_SEVEN_FACED_OPEN_INTERIOR_2D_EXPERIMENTAL/R31_OPEN_INTERIOR_1_TO_1.geojson"),
("phase_b/B_R03_24_EXPERIMENTAL_WALL_STUDIES.csv","M02_PHASE_B_COMPLETION_R03_LOCAL_EXPERIMENTAL/M02_B_R03_WALL_CONNECTED_24_VARIANTS.csv"),
("phase_b/B_R03_24_UNAPPROVED_STUDIES.geojson","M02_PHASE_B_COMPLETION_R03_LOCAL_EXPERIMENTAL/M02_B_R03_WALL_CONNECTED_RESERVATIONS_1_TO_1.geojson"),
("phase_b/B_R03_QA.json","M02_PHASE_B_COMPLETION_R03_LOCAL_EXPERIMENTAL/M02_B_R03_FINAL_QA.json"),
("phase_c/C_SOURCE_RHYTHM_QA_NO_TRIAL_CELLS.json","M02_PHASE_C_AMBULATORY_RHYTHM_LOCAL_EXPERIMENTAL/M02_C_NUMERICAL_QA.json"),
("phase_d/D_WORKING_FLOORPLAN_SEVEN_OUTER_ONLY.geojson","M02_PHASE_D_MASONRY_SUPPORT_LOCAL/M02_D_1TO1_SOURCE_FLOORPLAN_NO_FOURTEEN.geojson"),
("phase_d/D_QA.json","M02_PHASE_D_MASONRY_SUPPORT_LOCAL/M02_D_NUMERICAL_QA.json"),
("phase_d/D_SEVEN_320_WALL_FACES.csv","M02_PHASE_D_MASONRY_SUPPORT_LOCAL/M02_D_SEVEN_320_WALL_FACES.csv"),
("phase_d/D_32_INTERFACE_GAPS.csv","M02_PHASE_D_MASONRY_SUPPORT_LOCAL/M02_D_THIRTY_TWO_INTERFACE_GAPS.csv"),
("phase_d/D_8_SUPPORT_REFERENCES.csv","M02_PHASE_D_MASONRY_SUPPORT_LOCAL/M02_D_EIGHT_PROVISIONAL_SUPPORT_REFERENCES.csv"),
("phase_d/D_MASONRY_ROLE_AUDIT.csv","M02_PHASE_D_MASONRY_SUPPORT_LOCAL/M02_D_R11_MASONRY_LAYER_CLASSIFICATION.csv"),
("phase_e/E_FULL_REGRESSION_QA.json","M02_PHASE_E_FULL_CATHEDRAL_2D_REGRESSION_LOCAL/M02_E_NUMERICAL_QA.json"),
("phase_e/E_REVIEW_CHECKLIST.csv","M02_PHASE_E_FULL_CATHEDRAL_2D_REGRESSION_LOCAL/M02_E_FULL_REGRESSION_CHECKLIST.csv"),
("phase_e/E_SEVEN_BAY_RING_QA.csv","M02_PHASE_E_FULL_CATHEDRAL_2D_REGRESSION_LOCAL/M02_E_SEVEN_BAY_RING_AND_CLEARANCE_QA.csv"),
("phase_e/E_18_ADJACENT_VAULT_GAPS.csv","M02_PHASE_E_FULL_CATHEDRAL_2D_REGRESSION_LOCAL/M02_E_EIGHTEEN_SAME_RING_VAULT_GAPS.csv"),
("phase_e/E_EIGHT_SUPPORT_CLEARANCES.csv","M02_PHASE_E_FULL_CATHEDRAL_2D_REGRESSION_LOCAL/M02_E_EIGHT_PROVISIONAL_SUPPORT_CLEARANCES.csv"),
("drawings/MASTER_CATHEDRAL_DARK.png","M02_PHASE_E_FULL_CATHEDRAL_2D_REGRESSION_LOCAL/F5ZP_M02_PHASE_E_FULL_CATHEDRAL_REGRESSION_DARK.png"),
("drawings/MASONRY_PLAN_DARK.png","M02_PHASE_D_MASONRY_SUPPORT_LOCAL/F5ZP_M02_PHASE_D_SOURCE_ONLY_MASONRY_PLAN_DARK.png"),
("scripts/B_R03_WALL_CONNECTED.py","M02_PHASE_B_R03_WALL_CONNECTED_COMPLETION.py"),
("scripts/D_SOURCE_ONLY_MASONRY.py","M02_PHASE_D_MASONRY_RESERVATIONS_NO_OUTER_14.py"),
("scripts/E_FULL_REGRESSION.py","M02_PHASE_E_FULL_CATHEDRAL_REGRESSION_2D.py")
]
assert all((R/src).is_file() for _,src in sources)
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={out:hashfile(R/src) for out,src in sources}
STAGE.mkdir(parents=True)
for out,src in sources:
 dest=STAGE/out
 dest.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(R/src,dest)
 assert hashfile(dest)==checks[out]
source=json.loads((STAGE/"source/R11_ORIGINAL.geojson").read_text())
work=json.loads((STAGE/"phase_d/D_WORKING_FLOORPLAN_SEVEN_OUTER_ONLY.geojson").read_text())
e=json.loads((STAGE/"phase_e/E_FULL_REGRESSION_QA.json").read_text())
b=json.loads((STAGE/"phase_b/B_R03_QA.json").read_text())
d=json.loads((STAGE/"phase_d/D_QA.json").read_text())
c=json.loads((STAGE/"phase_c/C_SOURCE_RHYTHM_QA_NO_TRIAL_CELLS.json").read_text())
intent=json.loads((STAGE/"intent/R30_MEASURED_SEVEN_FACES.json").read_text())
vault={f["properties"]["id"]:shape(f["geometry"]) for f in source["features"] if f["properties"].get("role")=="CLEAR"}
assert len(vault)==218 and len(source["features"])==289
assert all(p.is_valid and p.area>0 for p in vault.values())
assert source["properties"]["status"].startswith("R11 experimental")
assert e["positive_area_vault_overlaps"]==0 and e["seven_sanctuary_inner_wall_faces"]==7
assert e["wall_normal_separation"]==320 and e["main_vaults_inside_continuous_open_interior"]==15
assert intent["chancel_polygonal_face_count"]==7
assert b["variants_with_continuous_polygon_finite_wall_face_contact_and_no_protected_collision"]==24
assert d["experimental_outer_14_cells_excluded_from_floor_plan"] is True
assert c["original_R11_CLEAR_polygon_count"]==218
F=work["features"]
ids=[f["properties"]["id"] for f in F]
assert len(ids)==36 and len(set(ids))==36
assert sum(f["properties"]["role"]=="UNCHANGED_R11_VAULT_PLANNING_POLYGON" for f in F)==21
assert sum(f["properties"]["role"]=="USER_CONFIRMED_FIRST_WALL_MEASURED_BAND" for f in F)==7
assert sum(f["properties"]["role"]=="B3_MODERATE_REFERENCE_ONLY_NOT_A_PIER" for f in F)==8
assert {s for s in ids if s.startswith("T_A")}=={f"T_A{i}_R12C" for i in range(1,8)}
assert not any("TRIAL" in n or "_L1" in n or "_L2" in n for n in ids)
for f in F:
 if f["properties"]["id"] in vault:
  assert shape(f["geometry"]).equals_exact(vault[f["properties"]["id"]],1e-9)
for p in (STAGE/"drawings").iterdir():
 with Image.open(p) as im:im.verify()
register={
"checkpoint":"F5ZP_M02_2D_ARCHITECTURAL_CHECKPOINT_R01_LOCAL",
"classification":"Validated 2D technical and geometric work; NOT approved architectural supports",
"source_original_status":"R11 EXPERIMENTAL, verified source but not blanket promotion",
"source_vaults":218,"positive_area_source_overlaps":0,
"working_chevet_ring_counts":{"I":7,"M":7,"T":7},
"14_outer_subdivisions_in_working_floorplan":False,
"7_sided_open_chancel":"USER CONFIRMED; 7 source faces",
"first_physical_wall":"7 sanctuary-to-inner faces / perpendicular 320 native units",
"source_ring_gaps":{"I_M":197,"M_T":292},
"phase_B_eight_sites":"Measured; 24 experimental options, no selected physical pier",
"phase_C_paired_lower_outer":"Research only, excluded from working floorplan",
"phase_D":"2D plan spatial classifications verified; wall joins/pier bearings unapproved",
"phase_E":"218 vault polygon regression PASS",
"approval_protection":["F5ZK-C unchanged","F5ZN-A unchanged","Working inner/middle generator untouched","Pass 6J records untouched","Outer paired cells not promoted"],
"technical_validation":"PASS","geometric_validation":"PASS",
"architectural_validation":"Confirmed open central sanctuary and first wall; other details provisional",
"historical_validation":"NOT ASSESSED","structural_validation":"NOT ASSESSED",
"missing_support_schedule":"F5ZL-C unresolved",
"native_to_physical_unit_conversion":"UNRESOLVED",
"github":"NOT USED"}
(STAGE/"M02_ARCHITECTURAL_CHECKPOINT_REGISTER.json").write_text(json.dumps(register,indent=2)+"\n")
open_issues=[
("F5ZL-C missing support schedule","Cannot certify support layout or structural load paths"),
("Eight chancel pier and rib-bearing sections","Only construction reservations, not approved piers"),
("Seven chancel wall joins and choir end interfaces","2D line contact measured, real bonding not validated"),
("Paired fourteen lower outer vaults","Explicitly EXCLUDED from working floor plan; future architectural approval needed"),
("Lower outer crown/springing heights and windows","Not established by this 2D plan"),
("Native physical units","1:1 project coordinates used; SI conversion unresolved"),
("Historical Gothic geometric verification","Not performed by Phase B–E regression"),
("Structural loads and masonry feasibility","Not assessed"),
("Large R11 reserved-masonry areas","Experimental planning boundaries may overlap confirmed open interior"),
("R11 whole-model approval","Source remains experimental; no blanket approval claimed")]
with (STAGE/"M02_UNRESOLVED_ISSUES.csv").open("w",newline="") as f:
 w=csv.writer(f);w.writerow(["issue","open_consequence"]);w.writerows(open_issues)
(STAGE/"README_START_HERE.md").write_text("""# Cathedral F5ZP M02 — Coordinated 2D Architectural Checkpoint R01

**Status:** Phase B, C, D, E completed for the specific 2D geometric tasks reported. Technical/geometric regression PASS. This does NOT approve physical pier sections, Gothic arches, structural adequacy, historical details or the experimental R11 whole-model baseline.

## Authoritative user-confirmed spatial intent
The main nave, crossing and arms, choir and polygonal **seven-faced chancel are one continuous OPEN interior**. Internal Q5 divisions are planning references, not walls or seven doorways. First actual wall is the **320-native-unit seven-faced boundary from chancel to inner ambulatory**.

## Working floor plan — critical exclusion
Read **phase_d/D_WORKING_FLOORPLAN_SEVEN_OUTER_ONLY.geojson**. It includes the original **7 I, 7 M and 7 T source chevet bays**. It does **NOT** include the experimental paired **14 lower outer vault** subdivisions. Those prior Phase C trials are referenced only by an isolated QA summary; their geometries and scripts are intentionally omitted. Do not revive them without architectural approval.

## Proven measured geometry
The full saved experimental R11 has **218 nonoverlapping valid CLEAR vault polygons**, retained read-only. At each curved sector, I-to-M gap **197** and M-to-T gap **292** native units. The chancel first wall comprises seven **320 perpendicular-unit** strips. The eight experimental Phase B support footprint studies (6 corners + 2 end transitions) are NOT approved physical piers. The working plan only displays moderate provisional envelopes for reference.

## How to review
- drawings/MASTER_CATHEDRAL_DARK.png — Phase E full plan, one primary review image
- drawings/MASONRY_PLAN_DARK.png — Phase D source-only masonry reserve distinctions
- M02_ARCHITECTURAL_CHECKPOINT_REGISTER.json — authoritative status mapping within this local study
- M02_UNRESOLVED_ISSUES.csv — explicit blockers/approval boundaries
- source/R11_ORIGINAL.geojson — read-only saved experiment, source of coordinates
- phase_d/D_WORKING_FLOORPLAN_SEVEN_OUTER_ONLY.geojson — working 2D coordinated plan
- phase_b, phase_c, phase_d, phase_e — numerical evidence and clearly marked experiments

## Reproduce
From the ORIGINAL project workspace directory with shapely, matplotlib and Pillow available:
python3 M02_PHASE_B_R03_WALL_CONNECTED_COMPLETION.py
python3 M02_PHASE_D_MASONRY_RESERVATIONS_NO_OUTER_14.py
python3 M02_PHASE_E_FULL_CATHEDRAL_REGRESSION_2D.py
python3 M02_PHASE_F_CONSOLIDATE_HANDOFF.py

Included scripts retain original workspace-relative input paths. The checkpoint zip is self-contained for inspecting results; re-generating the scripts requires the original workspace layout.

## Separate validations
Technical PASS. Geometric 2D PASS for reported invariants. Architectural: central open area and first wall user-confirmed; piers/masonry joints unapproved. Historical NOT assessed. Structural NOT assessed. Physical unit conversion unresolved; F5ZL-C missing. Approved F5ZK-C and F5ZN-A, the working inner/middle vault generator and Pass 6J preserved.

GitHub intentionally not used.
""")
manifest=[]
for p in sorted(STAGE.rglob("*")):
 if p.is_file():
  manifest.append({"path":p.relative_to(STAGE).as_posix(),"bytes":p.stat().st_size,"sha256":hashfile(p)})
(STAGE/"M02_CONTENT_MANIFEST_SHA256.json").write_text(json.dumps(manifest,indent=2)+"\n")
zipout=Path.home()/"Downloads"/"F5ZP_M02_COMPLETE_ARCHITECTURAL_2D_HANDOFF_R01_LOCAL.zip"
assert not zipout.exists(),"Existing ZIP protected; choose a new version"
with zipfile.ZipFile(zipout,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(STAGE.rglob("*")):
  if p.is_file():z.write(p,arcname="F5ZP_M02_CHECKPOINT_R01/"+p.relative_to(STAGE).as_posix())
with zipfile.ZipFile(zipout) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(manifest)+1
assert all(hashfile(R/src)==checks[out] for out,src in sources)
assert len(list(STAGE.rglob("*.geojson")))==4
assert all("TRIAL" not in p.name for p in STAGE.rglob("*.geojson"))
print("M02_PHASE_F_VALIDATED_LOCAL_CHECKPOINT")
print("MANIFEST_FILES",len(manifest)+1,"ZIP_BYTES",zipout.stat().st_size)
print("WORKING_PLAN",STAGE/"phase_d/D_WORKING_FLOORPLAN_SEVEN_OUTER_ONLY.geojson")
print("REVIEW",STAGE/"drawings/MASTER_CATHEDRAL_DARK.png")
print("ZIP",zipout)