#!/usr/bin/env python3
"""One-command fresh reproduction. Refuses existing output; preserves all inputs."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PACKAGE=Path(__file__).resolve().parents[1]

def command(argv,log,cwd):
    print('RUN', ' '.join(map(str,argv)),flush=True)
    with open(log,'w') as stream:
        p=subprocess.run(list(map(str,argv)),cwd=cwd,stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHON=sys.executable))
    if p.returncode:
        raise RuntimeError(f'Failed ({p.returncode}); see {log}')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True,help='new checkpoint folder, must not exist')
    ap.add_argument('--skip-renders',action='store_true',help='explicit numerical-only rerun; no Blender review claim')
    a=ap.parse_args();out=a.output.resolve()
    if out.exists():raise FileExistsError(out)
    manifest=json.loads((PACKAGE/'BENCHMARK_MANIFEST_R03.json').read_text())
    for row in json.loads((PACKAGE/'qa/originals_frozen_R03.json').read_text()):
        if hashlib.sha256((PACKAGE/row['path']).read_bytes()).hexdigest()!=row['sha256']:
            raise RuntimeError('Protected input changed: '+row['path'])
    out.mkdir(parents=True)
    shutil.copytree(PACKAGE/'originals',out/'originals')
    shutil.copytree(PACKAGE/'scripts',out/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
    (out/'semantic').mkdir()
    for p in (PACKAGE/'semantic').iterdir():
        if p.is_file() and p.suffix in ('.py','.sh','.md'):shutil.copy(p,out/'semantic'/p.name)
    for file in ['BENCHMARK_MANIFEST_R03.json','requirements_R03.txt']:
        shutil.copy(PACKAGE/file,out/file)
    for sub in ['baseline/maps','baseline/models','baseline/logs','experimental/models','experimental/qa','comparisons','qa']:(out/sub).mkdir(parents=True,exist_ok=True)
    shutil.copy(PACKAGE/'qa/originals_frozen_R03.json',out/'qa/originals_frozen_R03.json')
    for case in manifest['benchmarks']:
        name=case['name'];mp=out/'baseline/maps'/f'{name}_map.png';model=out/'baseline/models'/f'{name}_R02_reproduced.stl'
        command([sys.executable,out/'originals/kit/tracery_regions.py',out/case['source'],'-o',mp,*case['region_options']],out/'baseline/logs'/f'{name}_regions.log',out)
        command([sys.executable,out/'originals/kit/tracery_build.py',mp,'-o',model,*case['mesh_options']],out/'baseline/logs'/f'{name}_build.log',out)
        if hashlib.sha256(model.read_bytes()).hexdigest()!=case['original_final_stl_sha256']:
            raise RuntimeError('Original STL byte regression mismatch: '+name)
        command([sys.executable,out/'scripts/tracery_repair_R03.py',model,'-o',out/'experimental/models'/f'{name}_M02_R03.stl','--report',out/'experimental/qa'/f'{name}_mesh_R03.json'],out/'experimental/qa'/f'{name}_repair.log',out)
        command([sys.executable,out/'scripts/compare_geometry_R03.py',name,'--root',out],out/'experimental/qa'/f'{name}_geometry.log',out)
    command([sys.executable,out/'scripts/check_intersections_R03.py','--root',out],out/'qa/self_intersections_R03.log',out)
    command(['bash',out/'semantic/reproduce_semantics_R03.sh'],out/'qa/semantic_reproduction.log',out)
    command([sys.executable,out/'scripts/test_mesh_regression_R03.py'],out/'qa/mesh_regression_tests_R03.log',out)
    if not a.skip_renders:
        command(['blender','-b','-t','4','--python',out/'scripts/render_comparisons_R03.py','--',out],out/'qa/blender_render.log',out)
        audits=json.loads((out/'qa/blender_import_render_R03.json').read_text())
        if len(audits)!=4 or any(r['bounds_max_delta_mm']>1e-4 for r in audits):
            raise RuntimeError('Blender import bounds mismatch')
        command([sys.executable,out/'scripts/compose_review_R03.py'],out/'qa/review_composition.log',out)
    (out/'REPRODUCTION_COMPLETE.json').write_text(json.dumps({'status':'EXPERIMENTAL','numerical_regression':'PASS','renders_requested':not a.skip_renders,'no_promotion':True},indent=2))
    print('COMPLETE',out)

if __name__=='__main__':main()
