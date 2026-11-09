#!/usr/bin/env python3
"""M04 P02 — R17 interoperability regression on genuine user profiles.
Uses unchanged R11 converter and R14 build_springer workflow.
No selection of approved architectural mouldings or alteration of source.
All generated meshes remain in one new experimental directory.
"""
from pathlib import Path
import hashlib,json,importlib.util,sys,subprocess,time
ROOT=Path("/home/christopher/Documents/Cathedral/experimental")
P01=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL/M04_P01_R11_SHARED_PROFILE_LIBRARY_EXPERIMENTAL")
BASE=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
O=BASE/"M04_P02_R17_TRUE_PROFILE_REGENERATION_EXPERIMENTAL"
assert not O.exists(),"Protect prior experimental checkpoints"
O.mkdir()
ENGINE=ROOT/"SPRINGER_PROFILE_INPUT_R11/profile_input.py"
WORKFLOW=ROOT/"SPRINGER_WORKFLOW_R14/build_springer.py"
FIXTURE=ROOT/"SPRINGER_REPRODUCIBLE_R17/fixture/manifest.json"
assert all(p.exists() for p in (ENGINE,WORKFLOW,FIXTURE))
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ENGINE,WORKFLOW,FIXTURE)}
spec=importlib.util.spec_from_file_location("unchanged_springer_r11_profile_importer",str(ENGINE))
converter=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=converter
spec.loader.exec_module(converter)
# These are experimental regression examples, NOT selected target Gothic profiles.
cases=[("PROFILE_1_SIMPLE","1__01",141.2507,"left"),
       ("PROFILE_31_ORIGINAL_R17_REFERENCE","31__01",141.2507,"left"),
       ("PROFILE_36_FINE_DETAIL","36__01",141.2507,"left")]
results=[]
for label,pid,width,nose in cases:
 path=P01/"isolated_source_png"/(pid+".png")
 assert path.exists()
 folder=O/label
 folder.mkdir()
 original_sha=json.loads((P01/"R11_section_json"/(pid+".json")).read_text())["source_original_sha256"]
 c=converter.convert(path,width=width,depth=None,nose=nose,mirror=False,threshold=128,simplify=.55)
 assert c["schema"]=="springer_png_section_v1"
 c.update({"is_automatic_cathedral_choice":False,
 "source_original_upload_sha256":original_sha,
 "user_selected_final_moulding":False,
 "profile_orientation_provisionally_left":True})
 sourcefolder=folder/"profile_input"
 sourcefolder.mkdir()
 section=sourcefolder/"section.json"
 section.write_text(json.dumps(c,indent=2)+"\n")
 converter.preview(c,path,sourcefolder/"orientation_preview.png")
 dest=folder/"R17_workflow"
 cmd=[sys.executable,str(WORKFLOW),"--fixture",str(FIXTURE),"--section",str(section),
      "--member","member_2","--out",str(dest),"--blender","/usr/bin/blender","--threads","4"]
 start=time.monotonic()
 with (folder/"workflow.log").open("w") as output:
  r=subprocess.run(cmd,stdout=output,stderr=subprocess.STDOUT,timeout=360)
 seconds=round(time.monotonic()-start,3)
 if not (dest/"WORKFLOW_SUMMARY.json").exists():
  summary={"status":"missing_summary","returncode":r.returncode}
 else:summary=json.loads((dest/"WORKFLOW_SUMMARY.json").read_text())
 test={"label":label,"source_profile_id":pid,"source_original_sha256":original_sha,
       "profile_proportions_width_native":round(c["width"],8),
       "profile_proportions_depth_native":round(c["depth"],8),
       "profile_section_vertices":c["vertices"],"test_nose_direction":nose,
       "workflow_returncode":r.returncode,"seconds":seconds,
       "status":summary.get("status"),"diagnostic_status":summary.get("diagnostic_status"),
       "validation_total":summary.get("total"),"validation_passed":summary.get("passed"),
       "declared_spring_origin_from_R17_fixture":"local Z=0; not F5ZK-C global spring Y3000",
       "approved_cathedral_profile":False}
 results.append(test)
 print("CASE_RESULT",json.dumps(test),flush=True)
# Negative profile 11 explicitly retains internal hole, do not erase it.
png=P01/"isolated_source_png/11__01.png"
try:
 converter.convert(png,width=141.2507,depth=None,nose="left",mirror=False,threshold=128,simplify=.55)
 raise AssertionError("Invalid source hole unexpectedly passed R11")
except ValueError as e:
 assert "interior holes" in str(e),str(e)
 bad={"asset":"11__01","expected":"REJECT","got":"REJECT",
      "reason":str(e),"hole_preserved":True}
results.append(bad)
# R17 canonical five-bearing guard: R17 has four only — never pass this off
# as an integrated cathedral springer test.
fixture=json.loads(FIXTURE.read_text())
assert len(fixture["members"])==4
assert len([m for m in fixture["members"] if m["kind"]=="sweep"])==1
qa={"experiment":"M04 P02 genuine three separate original user profile inputs into existing R17 springer",
"cases":results,"source_sha256_before":hashes,
"source_sha256_after":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ENGINE,WORKFLOW,FIXTURE)},
"all_source_files_byte_unchanged":all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p)] for p in (ENGINE,WORKFLOW,FIXTURE)),
"roles_in_original_R17_fixture":len(fixture["members"]),
"canonical_junction_requires_five":True,
"existing_R17_four_member_cannot_be_architecturally_integrated":True,
"current_R17_other_3_members_remain_real_source_fixture_references":True,
"historical_source_member_role_and_section_orientation_validated":False,
"F5ZL_C_support_schedule_missing":True,
"architectural_and_structural_approval":False}
(O/"M04_P02_THREE_PROFILE_REGENERATION_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
assert qa["all_source_files_byte_unchanged"]
print("R17_EXPERIMENTAL_PROFILE_VARIANT_COMPLETE",json.dumps([q.get("status",q.get("got")) for q in results]))
