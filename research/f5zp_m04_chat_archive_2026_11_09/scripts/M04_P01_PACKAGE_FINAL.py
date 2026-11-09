#!/usr/bin/env python3
"""M04 P01 final immutable ZIP and independent GLB reimport QA."""
from pathlib import Path
import csv,json,hashlib,zipfile,shutil
import trimesh
from PIL import Image
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
O=R/"M04_P01_R11_SHARED_PROFILE_LIBRARY_EXPERIMENTAL"
src=Path("/home/christopher/Downloads/downlods/3/french gothic profiles with optional soffets.zip")
engine=Path("/home/christopher/Documents/Cathedral/experimental/SPRINGER_PROFILE_INPUT_R11/profile_input.py")
glb=O/"M04_P01_49_R11_VECTOR_CONTOURS_GLTF_TEST.glb"
scene=trimesh.load(str(glb),force="scene",process=False)
assert len(scene.geometry)==len(scene.graph.nodes_geometry)==49
# glTF duplicates vertices at sharp normal seams; weld identical positions to
# verify geometric closure without altering source export.
for source_mesh in scene.geometry.values():
 testmesh=source_mesh.copy()
 testmesh.merge_vertices()
 assert testmesh.is_watertight
q=json.loads((O/"M04_P01_PROFILE_LIBRARY_QA.json").read_text())
assert (q["source_png_count"],q["isolated_source_component_count"],q["R11_schema_validated_count"],q["optional_soffit_components"])==(38,50,49,5)
assert q["R08_3000_and_3259_profile_sensitivity_tests"]==1056
assert len(q["rejections"])==1 and q["rejections"][0]["id"]=="11__01"
with Image.open(O/"M04_P01_ALL_ORIGINAL_SILHOUETTES_REVIEW.png") as im:
 assert im.size[0]==1500
 im.verify()
with Image.open(O/"M04_P01_BLENDER_CONTOUR_IMPORT_QA.png") as im:
 assert im.size==(1800,1120)
 im.verify()
sources={
 "original_png_zip":src,
 "original_R11_engine":engine,
 "library_script":R/"M04_P01_SHARED_R11_PROFILE_LIBRARY.py",
 "R08_comparison_script":R/"M04_P01_R08_PROFILE_BEDDING_COMPARISON.py",
 "Blender_script":R/"M04_P01_BLENDER_R11_CONTOUR_IMPORT.py",
 "R06_reference":R/"M04_R06_V12_PROFILE_RECOVERY_EXPERIMENTAL/M04_R06_EIGHT_ORIGINAL_PROFILES_AND_COMPOUND_PIER_1TO1.geojson",
 "R05_reference":R/"M04_R05_R1_78_EXACT_COMPOUND_PIER_2D_FOOTPRINT_EXPERIMENTAL/M04_R05_EIGHT_CURRENT_PLAN_BEARING_AXES_AND_MEASURED_PIER_FACE_CONTACTS.csv",
 "R08_reference":R/"M04_R08_R02_DENSE_F5ZNA_CARRIER_RECEIVERS_EXPERIMENTAL/M04_R08_PROVISIONAL_RECEIVER_BED_OUTLINES_1TO1.geojson"}
assert all(x.is_file() for x in sources.values())
hashes={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in sources.items()}
report={"milestone":"M04 P01 actual Gothic profile ZIP integration with existing R11",
 "PNG_images":38,"isolated_component_shapes":50,"R11_compatible_sections":49,
 "rejected_with_real_interior_hole":["11__01"],
 "independent_soffit_options":5,
 "R06_sensitivity_tests":1056,"R08_receiver_tests":1056,
 "R08_Y3000_provisional_overhang_trial_count":q["R08_2d_test_rows_with_coverage_below_100_percent"],
 "Blender_version":"5.0.1","GLB_independently_reimported_closed_meshes_after_seam_vertex_weld":49,
 "user_selected_profile_to_arch_family":False,"verified_historic_profile_nose_direction":False,
 "all_source_files_unchanged":True,"original_R11_converter_hash":hashes["original_R11_engine"],
 "original_zip_hash":hashes["original_png_zip"],
 "architectural_structural_validation":"NOT APPROVED",
 "project_locked_Pass6J_F5ZKC_R06_R08_geometry_changed":False}
(O/"M04_P01_FINAL_VALIDATION_STATUS.json").write_text(json.dumps(report,indent=2)+"\n")
(O/"FINAL_HANDOFF.md").write_text("""# M04 P01 shared Gothic profile library

Real 38-image upload ZIP produced 50 separately identifiable connected dark silhouettes. 49 were vectorized directly by the existing SPRINGER_PROFILE_INPUT_R11 Python converter into its exact springer_png_section_v1 JSON schema, with separate editable SVG. Profile 11 contains an actual internal opening, which R11 rejects: preserve the image and flag for further user review instead of silently filling it.

All five soffits remain separate and optional. Scale is freely adjustable with a single uniform multiplier per section; geometry preserves the raster proportions. Local face/nose direction (R11 provisional up) is not historically verified, so this cannot select a profile automatically.

The original R05 bearing identities, R06 source pier outline and R08 experimental receiver were read only. Against R06 218 protected clear-vault cells and seven confirmed first walls, 1,056 provisional width variations did not intrude. At Y3000/Y3259, 1,056 further tests measure coverage against the incomplete R08 trial receiver. All results use provisional 42%-depth anchoring: do not call them actual Gothic springing fits. The F5ZN-A carrier formerets differ from the older V13 U1 members.

Blender 5.0.1 created a mesh-catalog view of the 49 actual compatible 2D contours; independently reimported GLB confirms 49 geometrically closed solids after welding duplicate glTF normal-seam vertices. This is interoperability QA only, not building the arches. No approved source files or GitHub were modified.

Reproduce: python3 M04_P01_SHARED_R11_PROFILE_LIBRARY.py; python3 M04_P01_R08_PROFILE_BEDDING_COMPARISON.py; blender -b --factory-startup --python M04_P01_BLENDER_R11_CONTOUR_IMPORT.py; python3 M04_P01_PACKAGE_FINAL.py.
""")
zipout=Path.home()/"Downloads"/"F5ZP_M04_P01_R11_SHARED_GOTHIC_PROFILE_LIBRARY_EXPERIMENTAL_LOCAL.zip"
assert not zipout.exists(),"Never replace validated prior handoff"
items=[("results/"+p.relative_to(O).as_posix(),p) for p in O.rglob("*") if p.is_file()]
items += [("sources/"+p.name,p) for p in sources.values()]
items += [("scripts/"+Path(__file__).name,Path(__file__))]
assert len({name for name,p in items})==len(items)
manifest=[{"path":name,"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for name,p in items]
manifest_path=O/"M04_P01_SHA256_MANIFEST.json"
manifest_path.write_text(json.dumps(manifest,indent=2)+"\n")
with zipfile.ZipFile(zipout,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for name,p in items:z.write(p,"M04_P01/"+name)
 z.write(manifest_path,"M04_P01/MANIFEST_SHA256.json")
with zipfile.ZipFile(zipout) as z:assert z.testzip() is None
review=Path.home()/"Downloads"/"F5ZP_M04_P01_49_REAL_GOTHIC_PROFILES_REVIEW.png"
shutil.copy2(O/"M04_P01_ALL_ORIGINAL_SILHOUETTES_REVIEW.png",review)
assert hashlib.sha256(src.read_bytes()).hexdigest()==hashes["original_png_zip"]
assert hashlib.sha256(engine.read_bytes()).hexdigest()==hashes["original_R11_engine"]
print("M04_P01_DELIVERED",len(items)+1,"files",zipout.stat().st_size,"bytes")
print("REVIEW_PNG",review)
print("ZIP",zipout)
