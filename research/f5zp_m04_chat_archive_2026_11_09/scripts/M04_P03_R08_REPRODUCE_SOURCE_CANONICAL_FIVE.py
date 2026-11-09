#!/usr/bin/env python3
"""Safely rebuild the restored original SOURCE five-bearing springer baseline.
Uses the original existing R15 input library and original R14 generator.
Never edits any source manifest or approved cathedral blend.
"""
import argparse,hashlib,json,math,subprocess,sys
from pathlib import Path
ROOT=Path("/home/christopher/Documents/Cathedral/experimental")
SRC=ROOT/"SPRINGER_JUNCTION_R15/original_backing_manifest.json"
WORKFLOW=ROOT/"SPRINGER_WORKFLOW_R14/build_springer.py"
QA=ROOT/"UNIFIED_JUNCTION_INTERFACE_R01/INTERFACE_QA.json"
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",required=True,type=Path,help="NEW output root; must not exist")
 p.add_argument("--prepare-only",action="store_true")
 p.add_argument("--blender",default="/usr/bin/blender")
 a=p.parse_args()
 dest=a.out.resolve()
 if dest.exists():p.error("Output directory already exists—approved/experimental checkpoint protected")
 assert all(x.exists() for x in (SRC,WORKFLOW,QA))
 originals={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in (SRC,WORKFLOW,QA)}
 original=json.loads(SRC.read_text())
 can=json.loads(QA.read_text())["actual_five_bearings"]
 assert len(original["members"])==5
 assert {x["source_name"] for x in original["members"]}==set(can)
 assert len([m for m in original["members"] if m["kind"]=="sweep"])==1
 target=next(m for m in original["members"] if m["source_name"]=="BAY2_RIB_0")
 assert target["section_ref"]=="user_profile_18"
 target["section_ref"]="original"
 target["bearing_degrees"]=float(can["BAY2_RIB_0"])
 original["M04_recovered_source_experiment"]={
  "source_R15_manifest_sha256":originals[str(SRC)],
  "intent":"Original archived profile only, NOT user final profile selection",
  "full_R03_arch_metadata":can,
  "F5ZL_C_schedule_missing":True,
  "architectural_and_structural_approval":False}
 dest.mkdir(parents=True)
 manifest=dest/"M04_P03_R05_RESTORED_CANONICAL_FIVE_SOURCE_MANIFEST.json"
 manifest.write_text(json.dumps(original,indent=2)+"\n")
 if a.prepare_only:
  print("SOURCE_PREPARED",manifest);return
 cmd=[sys.executable,str(WORKFLOW),"--fixture",str(manifest),"--out",str(dest/"R14_regenerated"),
      "--blender",a.blender,"--threads","4"]
 with (dest/"R14_workflow.log").open("w") as fp:
  proc=subprocess.run(cmd,stdout=fp,stderr=subprocess.STDOUT)
 results=dest/"R14_regenerated/WORKFLOW_SUMMARY.json"
 report=json.loads(results.read_text()) if results.exists() else {}
 assert proc.returncode==0 and report.get("status")=="passed" and report.get("passed")==78 and report.get("total")==78,report
 for f,originalsha in originals.items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==originalsha
 print("CANONICAL_FIVE_SOURCE_78_OF_78_PASS",dest)
if __name__=="__main__":
 try:main()
 except (AssertionError,ValueError,KeyError,FileNotFoundError) as e:
  print("BLOCKED_OR_FAILED",e,file=sys.stderr);sys.exit(2)
