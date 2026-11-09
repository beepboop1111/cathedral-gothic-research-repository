#!/usr/bin/env python3
"""Supplement P01: compare each source-derived R11 section alternative with
the *EXPERIMENTAL* M04 R08 original 3000 receiver trial; never select a
profile or claim upper 3D compatibility."""
from pathlib import Path
import csv,json,math,hashlib
import numpy as np
from shapely.geometry import Polygon,shape
from shapely.ops import unary_union
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
O=R/"M04_P01_R11_SHARED_PROFILE_LIBRARY_EXPERIMENTAL"
R08=R/"M04_R08_R02_DENSE_F5ZNA_CARRIER_RECEIVERS_EXPERIMENTAL/M04_R08_PROVISIONAL_RECEIVER_BED_OUTLINES_1TO1.geojson"
R06=R/"M04_R06_V12_PROFILE_RECOVERY_EXPERIMENTAL/M04_R06_EIGHT_ORIGINAL_PROFILES_AND_COMPOUND_PIER_1TO1.geojson"
R05=R/"M04_R05_R1_78_EXACT_COMPOUND_PIER_2D_FOOTPRINT_EXPERIMENTAL/M04_R05_EIGHT_CURRENT_PLAN_BEARING_AXES_AND_MEASURED_PIER_FACE_CONTACTS.csv"
assert all(x.exists() for x in (R08,R06,R05))
beds={float(f["properties"]["id"].split("_Y")[-1]):shape(f["geometry"]) for f in json.loads(R08.read_text())["features"]}
assert 3000 in beds and 3259 in beds
q=json.loads(R06.read_text())
xy=np.array(q["properties"]["trial_origin_global_XY"])
bearings=list(csv.DictReader(R05.open()))
assert len(bearings)==8
dims={"Doubleau":38.159911,"D ogive":35.99999,"U1 longitudinal":33.517707}
assets=list(csv.DictReader((O/"isolated_components_and_contour_measurements.csv").open()))
source_sections={a["id"]:np.array(json.loads((O/"R11_section_json"/(a["id"]+".json")).read_text())["section"],float)
for a in assets if a["state"]=="PASS" and a["type"]=="numbered_profile"}
comp=[]
for id,points in source_sections.items():
 for factor in (.8,1.,1.2):
  for member in bearings:
   width=dims[member["source_family"]]*factor
   uv=points*width
   depth=float(np.ptp(uv[:,1]))
   theta=math.radians(float(member["F5ZKC_target_plan_heading_from_trial_center_deg"]))
   outward=np.array([math.cos(theta),math.sin(theta)])
   transverse=np.array([-math.sin(theta),math.cos(theta)])
   section=Polygon(xy+np.outer(uv[:,0],transverse)+np.outer(uv[:,1]-depth*.42,outward))
   assert section.is_valid
   line={"id":id,"family_trial":member["source_family"],"member":member["name"],
     "nominal_width_factor":factor,"width":round(width,6),"depth":round(depth,6),
     "provisional_anchor_depth_fraction":.42,
     "historical_orientation_confirmed":False}
   for height in (3000,3259):
    bed=beds[height]
    line[f"R08_{height}_covered_area_sq"]=round(section.intersection(bed).area,5)
    line[f"R08_{height}_uncovered_area_sq"]=round(section.difference(bed).area,5)
    line[f"R08_{height}_covered_fraction"]=round(section.intersection(bed).area/section.area,7)
   comp.append(line)
assert len(comp)==1056
with (O/"M04_P01_R08_RECEIVER_1056_OPTIONAL_PROFILE_COMPARISONS.csv").open("w",newline="") as fp:
 w=csv.DictWriter(fp,fieldnames=comp[0].keys());w.writeheader();w.writerows(comp)
summary=[]
for id in source_sections:
 rows=[x for x in comp if x["id"]==id and x["nominal_width_factor"]==1.0]
 summary.append({"profile_id":id,"reference_scale_eight_roles":8,
  "total_uncovered_R08_Y3000_native_sq":round(sum(x["R08_3000_uncovered_area_sq"] for x in rows),4),
  "max_uncovered_R08_Y3000_member_sq":round(max(x["R08_3000_uncovered_area_sq"] for x in rows),4),
  "total_uncovered_R08_Y3259_native_sq":round(sum(x["R08_3259_uncovered_area_sq"] for x in rows),4),
  "max_uncovered_R08_Y3259_member_sq":round(max(x["R08_3259_uncovered_area_sq"] for x in rows),4),
  "all_roles_source_profile_assigned":False,
  "historical_orientation_verified":False})
with (O/"M04_P01_R08_COMPARE_NOT_RANK_USER_SELECTED.csv").open("w",newline="") as fp:
 w=csv.DictWriter(fp,fieldnames=summary[0].keys());w.writeheader();w.writerows(summary)
qa=json.loads((O/"M04_P01_PROFILE_LIBRARY_QA.json").read_text())
qa["R08_3000_and_3259_profile_sensitivity_tests"]=len(comp)
qa["R08_source_geojson_sha256"]=hashlib.sha256(R08.read_bytes()).hexdigest()
qa["R08_source_model_is_approved"]=False
qa["R08_source_role_formeret_discrepancy"]="True F5ZN-A current carrier set uses formerets, older V13 R05 eight-member axes label U1. Do not conflate."
qa["source_roles_selected_by_user"]=False
qa["R08_actual_3D_moulded_fit_certified"]=False
qa["R08_2d_test_rows_with_coverage_below_100_percent"]=sum(x["R08_3000_uncovered_area_sq"]>.01 for x in comp)
(O/"M04_P01_PROFILE_LIBRARY_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
handoff=O/"HANDOFF.md"
with handoff.open("a") as f:
 f.write("\n## R08 test caveat\nA separate 1,056-row measured source-derived contour comparison against R08 saved receiver polygon levels Y3000 and Y3259 was carried out. These are original 2D profile shapes with provisional up-nose and 42% depth anchoring. The R08 source receiver itself is experimentally incomplete at the first bed and its formerets are NOT V13 U1. The test cannot imply true 3D arch geometry, approve a selected profile or resolve the architectural pier center.\n")
print("R08_COMPARISONS_PASS",len(comp),"rows","uncovered_3000",qa["R08_2d_test_rows_with_coverage_below_100_percent"])
print("EXAMPLE_SUMMARIES",summary[:4])
