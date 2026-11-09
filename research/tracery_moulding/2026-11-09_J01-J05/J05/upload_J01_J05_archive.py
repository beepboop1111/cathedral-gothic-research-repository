#!/usr/bin/env python3
from pathlib import Path
import os,subprocess,hashlib,json,tempfile
home=Path.home()
repo=home/"Cathedral_Research_Staging/repo"
src=home/"Cathedral_Experiments"
ref="research/tracery-moulding-j01-j05-2026-11-09"
base_ref="research/tracery-generator-r41-r52-2026-11-09"
root="research/tracery_moulding/2026-11-09_J01-J05"
def git(*args,env=None):
    p=subprocess.run(["git","-C",str(repo),*map(str,args)],env=env,text=True,capture_output=True)
    if p.returncode:raise RuntimeError("git command failed: "+p.stderr[-1500:])
    return p.stdout.strip()
git("fetch","--no-tags","origin",base_ref)
base=git("rev-parse","FETCH_HEAD")
remote=git("ls-remote","--heads","origin",ref).split()
if not remote or remote[0]!=base:raise RuntimeError("remote branch head mismatch")
files={}
for i in range(1,6):
    j="J%02d"%i;d=src/("tracery_moulding_"+j)
    if not d.is_dir():raise RuntimeError("missing "+str(d))
    for p in d.iterdir():
        if not p.is_file() or p.name=="J04_FULL_PASS.glb":continue
        name=p.name
        keep=(name.endswith(".py") or name.endswith("_QA.json") or name.endswith(".blend")
              or name.endswith(".glb") or (name.endswith(".png") and "FINAL" in name)
              or (j=="J05" and (name.endswith(".npz") or name=="paths.json")))
        if keep:files[root+"/"+j+"/"+name]=p
assert len(files)>25,("missing data",len(files))
readme="""# Gothic tracery moulding generator J01–J05 (research archive)

**Archive date:** 2026-11-09. Separate from R33 masonry research. Never overwrite approved cathedral geometry.

## Pass dispositions

| Pass | Outcome | Status |
|---|---|---|
| J01 | 13 procedural swept members, voxel union and GLB round-trip passed | geometric baseline |
| J02 | Isolated Y junction exact Boolean, 68 exterior controls with zero tested drift | isolated test validated |
| J03 | Full exact-Boolean fusion: 35 boundary edges and 1571 nonmanifold edges | FAIL |
| J04 | Manifold Boolean silently dropped most inputs, despite watertight output | FAIL_INPUT_LOSS |
| J05 | manifold3d union of 13 members; one connected solid, 0 open/nonmanifold edges, GLB roundtrip passed | GEOMETRIC EXPERIMENT PASS |

**No architectural, historical, or structural approval.** Source units are unverified and source-derived plate geometry was not reconstructed.
J05 does not preserve every vertex at intersections; require explicit construction trimming and moulding-flow improvements before approval.
The discarded J04_FULL_PASS.glb is intentionally excluded because it was a FALSE POSITIVE.

## Reproduction

Run individual J01–J04 generator Python scripts in Blender with matching fixture assumptions.
J05: run export_paths.py inside Blender, robust_union.py in local Python (numpy, trimesh, manifold3d==3.5.4), then render_validate.py in Blender.
The installed manifold3d wheel itself is intentionally excluded.
**Executed tests used Blender 5.0.1. Blender 5.1+/5.2+ not tested.**
All saves are experimental; no cathedral baselines were modified.
Next step J06: explicit curve intersections, trimmed junction topology, profile continuity and regression.

## Files
"""
manifest=[]
for dest,p in sorted(files.items()):
    manifest.append(dict(path=dest,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
readme+="".join("- "+v["path"].split(root+"/")[1]+" ("+str(v["bytes"])+" bytes)\n" for v in manifest)
tmp=Path(tempfile.mkdtemp(prefix="tracery_J01_J05_"))
(tmp/"README.md").write_text(readme)
(tmp/"MANIFEST.json").write_text(json.dumps(dict(date="2026-11-09",base_branch=base_ref,base_sha=base,files=manifest),indent=2))
files[root+"/README.md"]=tmp/"README.md"
files[root+"/MANIFEST.json"]=tmp/"MANIFEST.json"
env=dict(os.environ,GIT_INDEX_FILE=str(tmp/"index"))
git("read-tree",base,env=env)
for n,(path,p) in enumerate(sorted(files.items()),1):
    sha=git("hash-object","-w","--",str(p))
    git("update-index","--add","--cacheinfo","100644,"+sha+","+path,env=env)
    if n%10==0:print("STAGED",n,"/",len(files),flush=True)
tree=git("write-tree",env=env)
commit=git("-c","user.name=Cathedral Research Archive","-c","user.email=archive@users.noreply.github.com",
           "commit-tree",tree,"-p",base,"-m","Archive tracery moulding J01-J05 research and QA")
git("push","origin",commit+":refs/heads/"+ref)
check=git("ls-remote","--heads","origin",ref).split()
assert check and check[0]==commit
print(json.dumps(dict(status="UPLOADED",branch=ref,commit=commit,files=len(files),
 total_bytes=sum(p.stat().st_size for p in files.values()),
 url="https://github.com/beepboop1111/cathedral-gothic-research-repository/tree/"+ref+"/"+root),indent=2))
