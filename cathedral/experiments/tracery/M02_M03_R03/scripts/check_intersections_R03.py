#!/usr/bin/env python3
"""Independent full-mesh triangle intersection predicate, including GLB reload."""
import json
import time
from pathlib import Path
import argparse
import importlib.metadata
import numpy as np
import pymeshlab
import trimesh

def run(root):
    root=Path(root);rows=[]
    for name in ['meaux','haina_1264','haina_1265','chalons']:
        for status,p in [
            ('original',root/'baseline/models'/f'{name}_R02_reproduced.stl'),
            ('candidate_STL',root/'experimental/models'/f'{name}_M02_R03.stl'),
            ('candidate_GLB',root/'experimental/models'/f'{name}_M02_R03.glb')]:
            start=time.monotonic();m=trimesh.load(p,force='mesh',process=True)
            if p.suffix=='.glb':m.apply_scale(1000)
            s=pymeshlab.MeshSet();s.add_mesh(pymeshlab.Mesh(np.asarray(m.vertices),np.asarray(m.faces,dtype=np.int32)))
            s.compute_selection_by_self_intersections_per_face()
            ids=np.flatnonzero(s.current_mesh().face_selection_array())
            row={'name':name,'status':status,'faces':len(m.faces),'intersecting_face_count':len(ids),
                 'selected_face_indices':ids.tolist(),'predicate':'compute_selection_by_self_intersections_per_face',
                 'pymeshlab_version':importlib.metadata.version('pymeshlab'),'coordinates':'model millimeters',
                 'elapsed_seconds':time.monotonic()-start,
                 'limitation':'Full-mesh library triangle predicate, subject to floating point tolerance; not structural or historical validation.'}
            rows.append(row);(root/'qa/self_intersections_R03.json').write_text(json.dumps(rows,indent=2))
            print(json.dumps({k:v for k,v in row.items() if k!='selected_face_indices'}),flush=True)
    return rows

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));a=ap.parse_args();run(a.root)
