#!/usr/bin/env python3
"""P02 final four R17 real Blender results; one review PNG; rigorous
negative gate tests; source checksum; immutable experimental handoff.
Original R11/R17, cathedral source, Pass6J and user ZIP untouched.
"""
from pathlib import Path
import csv,hashlib,json,subprocess,sys,zipfile,shutil
import trimesh
from PIL import Image, ImageDraw, ImageFont, ImageOps
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
P01=R/"M04_P01_R11_SHARED_PROFILE_LIBRARY_EXPERIMENTAL"
O=R/"M04_P02_R17_TRUE_PROFILE_REGENERATION_EXPERIMENTAL"
E=Path("/home/christopher/Documents/Cathedral/experimental")
RUN=R/"M04_P02_BUILD_SELECTED_PROFILE_THROUGH_EXISTING_R17.py"
SOURCE=Path("/home/christopher/Downloads/downlods/3/french gothic profiles with optional soffets.zip")
ENG=E/"SPRINGER_PROFILE_INPUT_R11/profile_input.py"
WK=E/"SPRINGER_WORKFLOW_R14/build_springer.py"
F=E/"SPRINGER_REPRODUCIBLE_R17/fixture/manifest.json"
IQA=E/"UNIFIED_JUNCTION_INTERFACE_R01/INTERFACE_QA.json"
assert all(p.is_file() for p in (RUN,SOURCE,ENG,WK,F,IQA))
cases=[
 ("PROFILE_1_SIMPLE","1__01","A · Simple outline","Profile 1", "R17_workflow"),
 ("PROFILE_31_ORIGINAL_R17_REFERENCE","31__01","B · Original R17 control","Profile 31","R17_workflow"),
 ("PROFILE_36_FINE_DETAIL","36__01","C · Finer moulding","Profile 36","R17_workflow"),
 ("PROFILE_11_RASTER_DERIVATIVE_TEST","11__01","D · Raster microhole derivative","Profile 11","R17_regenerated")]
results=[]
for folder,profile,label,title,subdir in cases:
 p=O/folder
 summary=json.loads((p/subdir/"WORKFLOW_SUMMARY.json").read_text())
 assert summary["status"]=="passed" and summary["passed"]==summary["total"]==76,(folder,summary)
 qa=json.loads((p/subdir/"build/QA.json").read_text())
 assert qa["passed"]==qa["total"]==76,(folder,qa.get("passed"))
 g=p/subdir/"build/springer_variant.glb"
 assert g.is_file() and g.stat().st_size>100000
 mesh=trimesh.load(str(g),force="scene",process=False)
 assert len(mesh.geometry)>=5
 assert (p/subdir/"build/variant_review.png").is_file()
 profile_input=json.loads((p/"profile_input/section.json").read_text())
 assert profile_input["schema"]=="springer_png_section_v1"
 originalsha=json.loads((P01/"R11_section_json"/(profile+".json")).read_text())["source_original_sha256"] if profile!="11__01" else json.loads((O/"PROFILE_11_EXPLICIT_TINY_HOLE_REPAIR_QA.json").read_text())["original_source_png_sha256"]
 # Note for #11, original P01 masked png SHA is not the original upload
 # image SHA; both remain available in original source inventory.
 line={
 "source_profile":profile,"test_label":label,
 "profile_width_native":round(profile_input["width"],6),
 "profile_depth_native":round(profile_input["depth"],6),
 "source_converter_section_vertices":profile_input["vertices"],
 "R17_Blender_checks_passed":summary["passed"],
 "R17_Blender_checks_total":summary["total"],
 "GLB_mesh_assets":len(mesh.geometry),
 "GLB_file_bytes":g.stat().st_size,
 "GLB_sha256":hashlib.sha256(g.read_bytes()).hexdigest(),
 "original_upload_artwork_sha256":originalsha,
 "source_profile_is_approved":False,
 "source_PNG_modified":False,
 "uses_isolated_one_pixel_derivative":profile=="11__01",
 "soffit_geometry_merged":False,
 "workflow_status":"passed",
 "full_cathedral_five_bearing_acceptance":"BLOCKED"}
 results.append(line)
# Source profile 11 original still rejected; derivative is a one-white-pixel
# optional repair, never an overwrite.
hole=json.loads((O/"PROFILE_11_EXPLICIT_TINY_HOLE_REPAIR_QA.json").read_text())
assert hole["actual_raster_pixels_white_to_black"]==1 and hole["new_R11_section_valid"]
assert hole["original_contour_hole_area_pixel_sq"]==2.
# Test the public gate: no negative tests may touch existing source or create output.
base=[sys.executable,str(RUN),"--width","141.2507","--nose","left",
 "--experimental","--fixture",str(F)]
negative=[
 ("original_11_hole_no_explicit_optin",["--profile","11__01","--member","member_2"]),
 ("wrong_member_kind_mesh",["--profile","1__01","--member","member_0"]),
 ("profile_id_unrecognized",["--profile","nonexistent__09","--member","member_2"]),
 ("false_soffit_category",["--profile","31__01","--member","member_2","--soffit","1__01"]),
 ("reject_overwrite_existing_path",["--profile","31__01","--member","member_2"])]
neg=[]
for label,flags in negative:
 destination=(O/"PROFILE_1_SIMPLE") if label=="reject_overwrite_existing_path" else (O/("SHOULD_NOT_CREATE_"+label))
 cmd=base+flags+["--out",str(destination),"--prepare-only"]
 result=subprocess.run(cmd,text=True,capture_output=True)
 assert result.returncode!=0,(label,result.stdout,result.stderr)
 assert not destination.exists() if label!="reject_overwrite_existing_path" else destination.is_dir()
 neg.append({"test":label,"returncode":result.returncode,"expected_rejection":True,
  "error":(result.stderr or result.stdout).strip()[-400:]})
# Test positive prepare-only case w/ separate soffit option; no Blender needed
prepared=O/"P02_PREPARE_ONLY_EXAMPLE_SEPARATE_SOFFIT"
assert not prepared.exists()
cmd=base+["--profile","31__01","--depth","145"] if False else [
 sys.executable,str(RUN),"--depth","145","--nose","left","--experimental",
 "--fixture",str(F),"--profile","31__01","--member","member_2",
 "--soffit","soffet_3__01","--out",str(prepared),"--prepare-only"]
r=subprocess.run(cmd,text=True,capture_output=True)
assert r.returncode==0,(r.stdout,r.stderr)
assert (prepared/"profile_input/section.json").exists()
pqa=json.loads((prepared/"CHOICE_PROVENANCE.json").read_text())
assert abs(pqa["actual_depth"]-145)<1e-5
assert pqa["soffit_candidate_not_attached"]=="soffet_3__01"
assert not (prepared/"R17_regenerated").exists()
# Canonical integration guard from project's latest source only; do not
# borrow its old 5-bearings into the four-member R17 test.
interface=json.loads(IQA.read_text())
assert interface["r17_gate"]["count"]==4
assert interface["r17_gate"]["expected_count"]==5
assert interface["r17_gate"]["compatible"] is False
assert "BAY2_FORMERET_0" in interface["r17_gate"]["missing"]
assert len(json.loads(F.read_text())["members"])==4
# A1 real four-panel review PNG, only visible final image.
W,H=2400,1540
im=Image.new("RGB",(W,H),(246,248,251))
draw=ImageDraw.Draw(im)
fontreg="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
fontbold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
titlefont=ImageFont.truetype(fontbold,35)
subfont=ImageFont.truetype(fontreg,18)
headfont=ImageFont.truetype(fontbold,25)
bodyfont=ImageFont.truetype(fontreg,19)
tinyfont=ImageFont.truetype(fontreg,15)
draw.text((40,18),"M04 P02  |  Four genuine R17 Gothic springer regenerations",font=titlefont,fill=(24,42,58))
draw.text((42,65),"Original source profiles • unchanged R11 + R17 generators • four independent Blender GLB round trips",font=subfont,fill=(65,86,100))
colors=[(22,100,143),(42,120,91),(133,83,151),(173,105,55)]
panels=[]
for n,((folder,profile,label,title,subdir),line) in enumerate(zip(cases,results)):
 col=n%2;row=n//2
 x=35+col*1170;y=103+row*666
 draw.rounded_rectangle((x,y,x+1145,y+645),radius=16,fill=(255,255,255),outline=(206,216,225),width=2)
 draw.rounded_rectangle((x+10,y+10,x+1135,y+53),radius=8,fill=colors[n])
 draw.text((x+27,y+15),label,font=headfont,fill=(255,255,255))
 original_img=O/folder/subdir/"build/variant_review.png"
 with Image.open(original_img) as candidate:
  tile=ImageOps.fit(candidate.convert("RGB"),(600,535),method=Image.Resampling.LANCZOS)
 im.paste(tile,(x+18,y+70))
 draw.text((x+635,y+92),"Actual source silhouette",font=subfont,fill=(57,69,75))
 src=P01/"isolated_source_png"/(profile+".png")
 with Image.open(src) as sil:
  crop=ImageOps.contain(sil.convert("RGB"),(455,215),method=Image.Resampling.LANCZOS)
  im.paste(crop,(x+658+(425-crop.width)//2,y+131+(215-crop.height)//2))
 info=[
 f"Width       {line['profile_width_native']:.2f}",
 f"Depth       {line['profile_depth_native']:.2f}",
 f"R11 points  {line['source_converter_section_vertices']}",
 "Blender QA  76 / 76  PASS",
 ]
 for j,textline in enumerate(info):
  draw.text((x+654,y+378+j*34),textline,font=bodyfont,fill=(40,60,72))
 note="1 original white pixel repaired in copy only" if profile=="11__01" else "Original artwork unchanged"
 draw.text((x+654,y+535),note,font=tinyfont,fill=(102,80,64) if profile=="11__01" else (77,91,100))
 draw.text((x+24,y+617),"R17 LOCAL EXPERIMENT ONLY • user selection and cathedral interface approval outstanding",font=tinyfont,fill=(99,68,61))
 panels.append({"profile":profile,"Blender_image":str(original_img),"panel":[x,y,1145,645]})
draw.line((40,1445,2360,1445),fill=(169,178,187),width=2)
draw.text((44,1461),"Architectural gate: R17 has 4 bearing members; canonical cathedral junction requires 5. Do not register to approved F5ZK-C.",font=subfont,fill=(153,59,52))
draw.text((44,1490),"Four experimental validation passes do not establish actual tas-de-charge backing, F5ZL-C support schedule, or structural capacity.",font=tinyfont,fill=(93,106,118))
review=O/"F5ZP_M04_P02_FOUR_R17_TRUE_PROFILE_BLENDER_COMPARISON.png"
im.save(review,optimize=True)
with Image.open(review) as chk:assert chk.size==(W,H);chk.verify()
sha_references={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [SOURCE,ENG,WK,F,IQA]}
q={"milestone":"M04 P02 true R11-to-R17 integration; four independent Blender runs",
 "validation_status":"EXPERIMENTAL TECHNICAL PASS, ARCHITECTURAL INTEGRATION BLOCKED",
 "test_results":results,
 "negative_guard_tests":neg,
 "one_pixel_original11_derivative_geometry_accepted":True,
 "original11_source_rejection_preserved":True,
 "optional_soffit_choices_reference_only_not_physically_merged":True,
 "positive_prepare_only_control":pqa,
 "R17_canonical_5_bearing_interface_gate":interface["r17_gate"],
 "true_profile_blender_regressions_pass":sum(x["workflow_status"]=="passed" for x in results),
 "actual_GLB_independent_reimport_meshes":sum(x["GLB_mesh_assets"] for x in results),
 "not_a_source_historical_arch_provenance_approval":True,
 "current_F5ZKC_8_member_spring_path_registration":"NOT COMPLETED",
 "real_F5ZNA_formeret_replaces_older_V13_U1":"NOT EQUIVALENT",
 "missing_F5ZL_C":True,
 "original_source_SHA256":sha_references,
 "one_review_PNG":review.name,
 "all_originals_untouched":True,
 "Blender_version":"5.0.1"}
(O/"M04_P02_FINAL_NUMERICAL_AND_REGRESSION_QA.json").write_text(json.dumps(q,indent=2)+"\n")
with (O/"M04_P02_FOUR_R17_GLB_RESULTS.csv").open("w",newline="") as fp:
 w=csv.DictWriter(fp,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
(O/"M04_P02_STATUS_AND_HANDOFF.md").write_text("""# M04 P02 — Shared R11 profile library -> existing R17 true Blender/GLB workflow

Tested three original user silhouettes (profile 1, profile 31 — verified original R17 source-image hash, profile 36) and an experimental **one-pixel** internal-hole correction derivative of profile 11 against *exact same R17 source fixture*. Each real existing R14/R17 workflow passed 76/76 checks, with a distinct GLB and Blender review. Original R11 profile importer and R14/R17 generators are UNMODIFIED. Original 11.png and its R11 rejection remain intact; derivative is an explicit opt-in variant and is not marked original historical geometry.

The reusable CLI selector is M04_P02_BUILD_SELECTED_PROFILE_THROUGH_EXISTING_R17.py, with --profile, --width OR --depth (uniform proportional scale only), required --nose direction, --member (sweep only), optional --mirror, and --soffit metadata reference. A soffit is not fused/attached by this workflow. Always supply --experimental and a NEW --out directory; no prior checkpoint overwrites. A prepare-only test, with depth 145 and independent soffet_3, passes. Five negative controls correctly reject unmodified profile 11, a mesh rather than sweep member, unknown profile, invalid soffit category and overwriting a prior output.

CRITICAL: Existing reproducible R17 fixture contains FOUR members whereas latest canonical wall-pier junction has FIVE. The fifth BAY2_FORMERET_0 is missing and BAY2_RIB_0 has an original bearing mismatch. This study is an isolated engine regression, never an approval or new cathedral registered pier. Other Pass6J/V13 8-member arrangement uses U1 longitudinals while later F5ZN-A test carrier set uses formerets. Do not conflate them. Architectural floorplan-pier location and missing F5ZL-C support schedule still unresolved. No structural, historical or architectural approval. Do not assign the four demonstration profile choices to Gothic member roles without user decision.

Source hashes recorded, one final PNG comparison is rendered from four real Blender viewport render outputs. No approved cathedral or other-chat experimental work overwritten; no GitHub.
""")
# Deliver an economical ZIP: 4 final independent source-derived R17 GLBs,
# real render previews, their QA, selectors and source artwork from one ZIP,
# NOT 100MB of duplicated raw internal fixture geometry.
files=[
 ("scripts/M04_P02_RUN_THREE_R17_SPRINGER_PROFILES.py",R/"M04_P02_RUN_THREE_R17_SPRINGER_PROFILES.py"),
 ("scripts/M04_P02_BUILD_SELECTED_PROFILE_THROUGH_EXISTING_R17.py",RUN),
 ("scripts/M04_P02_REPAIR_PROFILE_11_SOURCE_TINY_HOLE.py",R/"M04_P02_REPAIR_PROFILE_11_SOURCE_TINY_HOLE.py"),
 ("scripts/M04_P02_FINALIZE_REGRESSION_AND_PNG.py",Path(__file__)),
 ("source/ORIGINAL_FRENCH_GOTHIC_PROFILES_ZIP_READ_ONLY.zip",SOURCE),
 ("source/EXISTING_R17_MANIFEST.json",F),
 ("source/CANONICAL_FIVE_BEARING_GATE_QA.json",IQA),
 ("source/ORIGINAL_R11_CONVERTER_READ_ONLY.py",ENG),
 ("source/ORIGINAL_R14_SPRINGER_WORKFLOW_READ_ONLY.py",WK),
 ("review/"+review.name,review)]
for folder,profile,label,title,subdir in cases:
 p=O/folder
 for f in ("profile_input/section.json","profile_input/orientation_preview.png",
           subdir+"/WORKFLOW_SUMMARY.json",
           subdir+"/build/QA.json",subdir+"/build/GEOMETRY_QA.json",
           subdir+"/build/springer_variant.glb"):
  files.append((f"case/{profile}/"+Path(f).name,p/f))
files.extend((f"reports/{p.name}",p) for p in O.iterdir() if p.is_file() and p.suffix in (".md",".json",".csv"))
files.extend((f"source_derivative/{p.name}",p) for p in O.iterdir() if p.is_file() and p.name.startswith("PROFILE_11_"))
# Avoid overwriting names and duplicate reports.
names=[name for name,p in files]
assert len(names)==len(set(names)),[n for n in names if names.count(n)>1]
assert all(p.exists() for name,p in files)
manifest=[{"path":name,"size":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for name,p in files]
mp=O/"M04_P02_PACKAGED_FILES_SHA256_MANIFEST.json"
mp.write_text(json.dumps(manifest,indent=2)+"\n")
zipout=Path.home()/"Downloads"/"F5ZP_M04_P02_R17_SHARED_GOTHIC_PROFILE_REGENERATION_EXPERIMENTAL_LOCAL.zip"
assert not zipout.exists(),"Prior handoff file protected"
with zipfile.ZipFile(zipout,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for name,p in files:z.write(p,"M04_P02/"+name)
 z.write(mp,"M04_P02/MANIFEST_SHA256.json")
with zipfile.ZipFile(zipout) as z:assert z.testzip() is None
destination=Path.home()/"Downloads"/review.name
shutil.copy2(review,destination)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha_references[str(p)] for p in [SOURCE,ENG,WK,F,IQA])
print("M04_P02_FINAL_SOURCE_QA_PASS",len(results),"real R17 meshes",len(neg),"negative controls",
 "ZIP",zipout.stat().st_size,"bytes","FILES",len(files)+1)
print("IMAGE",destination)
print("ARCHIVE",zipout)
