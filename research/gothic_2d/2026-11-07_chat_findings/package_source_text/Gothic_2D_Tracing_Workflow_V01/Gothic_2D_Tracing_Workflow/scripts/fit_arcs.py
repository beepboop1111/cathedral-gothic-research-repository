#!/usr/bin/env python3
"""Fit truly measured circle arcs from manual trace points, no guessed data.

Use template `docs/ARC_POINT_TEMPLATE.json`. An input arc needs >=3 noncollinear
points selected from the original visible arc. Output is an editable SVG with
full dotted circles and a machine-readable report. A fit is NOT historical proof.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
import cairosvg

def fit_circle(points):
    q=np.asarray(points,float)
    if q.ndim!=2 or q.shape[1]!=2 or len(q)<3:raise ValueError('3+ XY points required')
    A=np.column_stack([2*q,np.ones(len(q))]);b=np.sum(q*q,axis=1)
    if np.linalg.matrix_rank(A)<3:raise ValueError('collinear or degenerate points')
    x,y,k=np.linalg.lstsq(A,b,rcond=None)[0]
    r=math.sqrt(max(0,k+x*x+y*y))
    if r<1:raise ValueError('Invalid small circle')
    residuals=np.linalg.norm(q-[x,y],axis=1)-r
    return {'center':[float(x),float(y)],'radius':r,
            'rmse':float(np.sqrt(np.mean(residuals**2))),
            'max_residual':float(np.max(abs(residuals))),'n':len(q)}

def run(config,out):
    d=json.loads(Path(config).read_text())
    W,H=d['canvas_px'];res={};parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
    '<rect width="100%" height="100%" fill="white"/>',
    '<g id="FULL_RECOVERED_CIRCLES" stroke="black" fill="none" stroke-width="1.5" stroke-dasharray="2.4 5">']
    for arc in d['arcs']:
        fit=fit_circle(arc['points'])
        res[arc['id']]=dict(fit,source_points=arc['points'],status='analytical fit to manually selected image pixels')
        cx,cy=fit['center'];r=fit['radius']
        parts.append(f'<circle cx="{cx:.4f}" cy="{cy:.4f}" r="{r:.4f}"/>')
    parts.append('</g><g id="CENTER_MARKERS" fill="#159b2f">')
    for fit in res.values():
        cx,cy=fit['center'];parts.append(f'<circle cx="{cx:.4f}" cy="{cy:.4f}" r="3.5"/>')
    parts.append('</g></svg>')
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    out.with_suffix('.svg').write_text('\n'.join(parts))
    cairosvg.svg2png(bytestring='\n'.join(parts).encode(),write_to=str(out.with_suffix('.png')))
    out.with_suffix('.json').write_text(json.dumps(dict(source_reference=d.get('source_reference'),units='original source pixels',circles=res),indent=2))
    return res
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('points_json');p.add_argument('-o','--out',required=True);a=p.parse_args()
    print(json.dumps(run(a.points_json,a.out),indent=2))
