#!/usr/bin/env python3
"""Profile picker -> ORIGINAL R11 converter -> ORIGINAL R14/R17 workflow.
Does not change source engine, bearings, geometry, backing, or approved assets.
R17 is 4-bearing EXPERIMENTAL fixture, not 5-bearing cathedral pier.
"""
import argparse,hashlib,importlib.util,json,math,pathlib,subprocess,sys
P=pathlib.Path
ROOT=P("/home/christopher/Documents/Cathedral/experimental")
LIB=P("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL/M04_P01_R11_SHARED_PROFILE_LIBRARY_EXPERIMENTAL")
ENGINE=ROOT/"SPRINGER_PROFILE_INPUT_R11/profile_input.py"
WORKFLOW=ROOT/"SPRINGER_WORKFLOW_R14/build_springer.py"
R17=ROOT/"SPRINGER_REPRODUCIBLE_R17/fixture/manifest.json"
RASTER_REPAIR=P("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL/M04_P02_R17_TRUE_PROFILE_REGENERATION_EXPERIMENTAL/PROFILE_11_TINY_HOLE_RASTER_REPAIR_CANDIDATE.png")
def main():
 parser=argparse.ArgumentParser(description="Use the existing R11 and R17 engines with an explicit user-selected original Gothic profile.")
 parser.add_argument("--profile",required=True,help="e.g. 31__01 or 11__01 (requires --use-11-repair)")
 size=parser.add_mutually_exclusive_group(required=True)
 size.add_argument("--width",type=float,help="Native numerical width (preserves silhouette proportions)")
 size.add_argument("--depth",type=float,help="Native numerical depth (preserves silhouette proportions)")
 parser.add_argument("--nose",choices=["left","right","up","down"],required=True,help="Explicit inspected image nose direction")
 parser.add_argument("--mirror",action="store_true",help="Explicit intentional transverse reflection, never default")
 parser.add_argument("--member",required=True,help="Existing SWEEP member ID; never replace a mesh member")
 parser.add_argument("--soffit",help="Optional separate soffit ID for future review; NOT attached automatically")
 parser.add_argument("--fixture",type=P,default=R17)
 parser.add_argument("--out",type=P,required=True)
 parser.add_argument("--prepare-only",action="store_true",help="Write profile/preview without building mesh")
 parser.add_argument("--use-11-repair",action="store_true",help="Opt into an isolated 2-pixel raster-hole repair ONLY for #11")
 parser.add_argument("--experimental",action="store_true",required=True,help="Required: never approve as cathedral geometry")
 a=parser.parse_args()
 if not math.isfinite(a.width if a.width is not None else a.depth) or (a.width if a.width is not None else a.depth)<=0:parser.error("size must be positive and finite")
 src=LIB/"isolated_source_png"/(a.profile+".png")
 if a.profile=="11__01":
  if not a.use_11_repair:parser.error("Profile 11 has a 2-pixel raster hole: use --use-11-repair after inspecting it")
  src=RASTER_REPAIR
 elif a.use_11_repair:parser.error("--use-11-repair applies only to profile 11__01")
 if not src.is_file():parser.error("Unknown or missing original source profile "+a.profile)
 soff=None
 if a.soffit:
  soff=LIB/"R11_section_json"/(a.soffit+".json")
  if not soff.is_file():parser.error("Unknown optional soffit "+a.soffit)
  if not json.loads(soff.read_text()).get("optional_soffit"):parser.error("Soffit asset must be from optional soffit group")
 fixture=a.fixture.resolve()
 f=json.loads(fixture.read_text())
 candidates=[m for m in f["members"] if m["id"]==a.member]
 if len(candidates)!=1 or candidates[0]["kind"]!="sweep":parser.error("Existing sweep member ID required")
 # Important: R17 is known missing one canonical shared-pier receiving member.
 # The passed build is never the architectural cathedral junction.
 if fixture==R17 and len(f["members"])!=4:parser.error("R17 source fixture unexpectedly changed")
 out=a.out.resolve()
 if out.exists():parser.error("Output path already exists; revisions must be in a new folder")
 spec=importlib.util.spec_from_file_location("R11_existing_importer",str(ENGINE))
 module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
 data=module.convert(src,width=a.width,depth=a.depth,nose=a.nose,mirror=a.mirror,threshold=128,simplify=.55)
 assert data["schema"]=="springer_png_section_v1"
 out.mkdir(parents=True)
 inp=out/"profile_input";inp.mkdir()
 data.update({"source_user_profile_id":a.profile,
 "source_raster_SHA256":hashlib.sha256(src.read_bytes()).hexdigest(),
 "soffit_choice_for_future_review_only":a.soffit,
 "soffit_is_attached_to_real_3D_section":False,
 "source_11_raster_microhole_repair":a.use_11_repair,
 "run_requires_approval_beyond_technical_QA":True})
 section=inp/"section.json"
 section.write_text(json.dumps(data,indent=2)+"\n")
 module.preview(data,src,inp/"orientation_preview.png")
 provenance={"selected_user_profile_id":a.profile,"requested_size_kind":"width" if a.width is not None else "depth",
 "requested_size":a.width if a.width is not None else a.depth,
 "actual_width":data["width"],"actual_depth":data["depth"],
 "source_original_profile_sha256":data["source_raster_SHA256"],"requested_nose":a.nose,
 "mirrored":a.mirror,"soffit_candidate_not_attached":a.soffit,
 "fixture":str(fixture),"member":a.member,
 "fixture_member_count":len(f["members"]),
 "source_fixture_SHA256":hashlib.sha256(fixture.read_bytes()).hexdigest(),
 "original_R11_SHA256":hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
 "original_R14_SHA256":hashlib.sha256(WORKFLOW.read_bytes()).hexdigest(),
 "provisional_geom_only":True,
 "full_cathedral_architectural_validation":False}
 (out/"CHOICE_PROVENANCE.json").write_text(json.dumps(provenance,indent=2)+"\n")
 if a.prepare_only:
  print("PROFILE_PREPARED_ONLY",out);return
 cmd=[sys.executable,str(WORKFLOW),"--fixture",str(fixture),"--section",str(section),
  "--member",a.member,"--out",str(out/"R17_regenerated"),"--blender","/usr/bin/blender","--threads","4"]
 with (out/"workflow.log").open("w") as log:
  result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 summary=out/"R17_regenerated/WORKFLOW_SUMMARY.json"
 if summary.exists():
  report=json.loads(summary.read_text())
  provenance.update({"R17_workflow_validation":report})
  (out/"CHOICE_PROVENANCE.json").write_text(json.dumps(provenance,indent=2)+"\n")
 if result.returncode:raise SystemExit(f"EXPERIMENTAL_BUILD_FAILED rc={result.returncode}; read workflow.log")
 print("R17_SELECTION_BUILD_PASSED_TECHNICALLY",out)
if __name__=="__main__":
 try:main()
 except (ValueError,OSError,KeyError,AssertionError) as e:
  print("SOURCE_PROFILE_SELECTION_BLOCKED:",e,file=sys.stderr);sys.exit(2)
