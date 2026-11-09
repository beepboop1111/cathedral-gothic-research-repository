#!/usr/bin/env python3
"""R52 isolated, reproducible 2D Gothic tracery baseline verifier.
U01 historical source bytes are recovered unchanged from the archived U01–U05
package. This runner ONLY invokes Model(...) and never calls build()/solids(),
writes GLBs, guesses 3D profiles or touches F5ZP.
System dependencies: shapely, scipy, numpy, trimesh; triangle is required only
by the U01 3D cap mesher and is never used by this 2D harness.
"""
from __future__ import annotations
import json,sys,hashlib,copy,math,types,importlib.machinery
from pathlib import Path
from typing import Any
import numpy as np
from shapely.geometry import Polygon
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'baseline'
OUT=ROOT/'outputs'
OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(BASE))
# U01 has a module-level triangle import for 3D cap meshes. Strictly bypass
# that optional dependency for this 2D-only run; NEVER use this stub for solids.
try:
    import triangle  # noqa
    TRIANGLE_MODE='installed (not called)'
except ImportError:
    stub=types.ModuleType('triangle')
    stub.__spec__=importlib.machinery.ModuleSpec('triangle',loader=None)
    sys.modules['triangle']=stub
    TRIANGLE_MODE='2D-only unused 3D dependency stub'
import tracery_universal_U01 as U

def stable(v:Any):
    return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)

def recursive_reordered(x):
    if isinstance(x,dict):
        return {k:recursive_reordered(v) for k,v in reversed(list(x.items()))}
    if isinstance(x,list):
        return [recursive_reordered(v) for v in x]
    return x

def good(x,tol=1e-8):
    if not math.isfinite(float(x)):return False
    return abs(float(x))<=tol

def bounds_equal(a,b,tol):
    return max(abs(x-y) for x,y in zip(a,b))<=tol

def polygon_svg_path(p):
    def ring(r):
        t=list(r.coords)
        return 'M '+' L '.join(f'{x:.6f},{-y:.6f}' for x,y in t)+' Z'
    return ring(p.exterior)+' '+ ' '.join(ring(r) for r in p.interiors)

def draw_2d_svg(m,case):
    """Black = generator-confirmed region edges; gray = mathematical construction.
       Red dashed = unconfirmed historical attribution/ideal-source hypothesis."""
    box=m.outline.bounds
    width=max(box[2]-box[0],box[3]-box[1])
    pad=.12*width
    x0=box[0]-pad
    y0=-box[3]-pad
    w=box[2]-box[0]+2*pad
    h=box[3]-box[1]+2*pad
    lines=[
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="960" viewBox="{x0:.8f} {y0:.8f} {w:.8f} {h:.8f}">',
        f'<title>{case}: experimental Gothic 2D construction fixture</title>',
        '<desc>Black solid: 2D model contours verified against archived U01. Dashed gray: construction geometry. Dashed red: unresolved historical interpretation where relevant. No user vault/rib profiles or 3D claims.</desc>',
        '<g id="construction" fill="none" stroke="#929799" stroke-width="0.12%" stroke-dasharray="10 8">',
    ]
    # Mathematical centres (full construction circles have no historic authority).
    for name,a in m.con.get('arches',{}).items():
        for nm in ('CL','CR'):
            rec=a.get(nm)
            if isinstance(rec,list) and len(rec)==3 and rec[2]>0:
                x,z,r=rec
                lines.append(f'<circle cx="{x}" cy="{-z}" r="{r}" />')
        apex=a.get('apex')
        if apex is not None:
            lines.append(f'<circle cx="{apex[0]}" cy="{-apex[1]}" r="{w*.005:.6f}"/>')
    lines += ['</g>','<g id="tracery-stone-region" stroke="#151c20" stroke-width="0.18%" fill="#bec6c3" fill-rule="evenodd">']
    lines.append(f'<path d="{polygon_svg_path(m.stone)}" />')
    lines.append('</g>')
    lines.append('<g id="opening-numbers" font-family="DejaVu Sans,sans-serif" text-anchor="middle" fill="#293c44" font-size="1.1%">')
    for op in m.voids:
        x,y=op['poly'].representative_point().coords[0]
        lines.append(f'<text x="{x:.6f}" y="{-y:.6f}">{op["id"]}</text>')
    lines.append('</g>')
    if case.startswith('stleu_'):
        lines += ['<g id="uncertain-historic-interpretation" fill="none" stroke="#b34e4b" stroke-width="0.12%" stroke-dasharray="12 9">',
                  # Existing metric source scan is NOT currently registered; just signal
                  # the epistemic boundary; no additional red pseudo-tracings.
                  '</g>']
    lines.append('</svg>')
    dest=OUT/f'{case}_2D_construction.svg'
    dest.write_text('\n'.join(lines))
    return dest

def render_review(models):
    W,H=2300,1520
    board=Image.new('RGB',(W,H),'#f4f5f2')
    d=ImageDraw.Draw(board)
    root='/usr/share/fonts/truetype/dejavu/DejaVuSans'
    font=lambda sz,b=False:ImageFont.truetype(root+('-Bold' if b else '')+'.ttf',sz)
    dark='#20323b';grey='#637179';red='#ac5a4e'
    d.rectangle((0,0,W,139),fill=dark)
    d.text((45,19),'R52  /  UNIVERSAL 2D TRACERY ENGINE HANDOFF',font=font(39,True),fill='white')
    d.text((47,80),'Recovered U01 analytical geometry  •  5 verified fixtures  •  no 3D profiles / masonry assumptions',font=font(21),fill='#d1dcda')
    order=['stleu_fig80_rebuild','bar_2light_sexfoil','intersecting_3light','bar_4light_recursive']
    rects=[(25,167,1110,751),(1178,167,2276,751),(25,775,1110,1371),(1178,775,2276,1371)]
    for name,rect in zip(order,rects):
        m=models[name]
        x0,y0,x1,y1=rect
        d.rounded_rectangle(rect,radius=18,fill='#ffffff',outline='#d4dcd7',width=2)
        title={'stleu_fig80_rebuild':'St-Leu 80  /  plate-trace source pixels',
               'bar_2light_sexfoil':'2 lights  /  sixfold oculus',
               'intersecting_3light':'3 lights  /  intersecting tracery',
               'bar_4light_recursive':'4 lights  /  recursive tracery'}[name]
        d.text((x0+23,y0+20),title,font=font(22,True),fill=dark)
        d.text((x0+24,y0+56),f'{len(m.voids)} stable openings   ·   {len(m.members)} named members   ·   0 failed checks',font=font(16),fill=grey)
        p=m.stone
        a,b,c,e=m.outline.bounds
        width,depth=x1-x0-70,y1-y0-135
        scale=min(width/(c-a),depth/(e-b))
        midx=(a+c)/2;midy=(b+e)/2
        def P(coords):
            return [(round((x0+x1)/2+(x-midx)*scale),round((y0+y1)/2+26-(y-midy)*scale)) for x,y in coords]
        # Faceted preview of the constructed vector, not a source plate.
        d.polygon(P(p.exterior.coords),fill='#c9d0cc')
        for ring in p.interiors:
            d.polygon(P(ring.coords),fill='#ffffff')
        d.line(P(p.exterior.coords),fill='#28383d',width=3,joint='curve')
        for ring in p.interiors:
            d.line(P(ring.coords),fill='#28383d',width=2,joint='curve')
        if len(m.voids)<=10:
            for op in m.voids:
                pt=op['poly'].representative_point()
                X,Y=P([(pt.x,pt.y)])[0]
                text=op['id']
                bbs=d.textbbox((0,0),text,font=font(16,True))
                d.text((X-(bbs[2]-bbs[0])/2,Y-(bbs[3]-bbs[1])/2),text,font=font(16,True),fill='#4a676a')
    d.rectangle((0,1400,W,H),fill=dark)
    d.text((45,1419),'TECHNICAL / GEOMETRIC: VERIFIED U01 2D REPRODUCTION',font=font(22,True),fill='#c9e9d6')
    d.text((1195,1419),'HISTORICAL / STRUCTURAL: NOT CERTIFIED',font=font(21,True),fill='#f0c8b9')
    d.text((46,1462),'Source provenance kept separate: St-Leu pixels uncalibrated; all other layouts are synthetic parameters. Existing R49/R50 and F5ZP locks unchanged.',font=font(16),fill='#d1dfdb')
    path=ROOT/'R52_FINAL_2D_Construction_Engine_Handoff.png'
    board.save(path,optimize=True)
    return path

def main():
    specpath=BASE/'specs_U01.json'
    sourcehash=hashlib.sha256((BASE/'tracery_universal_U01.py').read_bytes()).hexdigest()
    specs=json.loads(specpath.read_text())
    previous=json.loads((BASE/'QA_U01_original_report.json').read_text())['models']
    assert len(specs)==5 and len(previous)==5
    outcomes=[]
    models={}
    for spec in specs:
        label=spec['id']
        m=U.Model(spec)
        models[label]=m
        old=previous[label]
        # Not just U01 self-checks: independent archived-record comparison.
        mids=[x['id'] for x in m.voids]
        expectids=[x['id'] for x in old['openings']]
        assert mids==expectids,(label,'OPENING_ID_DRIFT',mids,expectids)
        assert len(m.voids)==len(m.stone.interiors),(label,'STONE_HOLE_TOPOLOGY')
        assert m.stone.is_valid and m.stone.area>0 and m.stone.geom_type=='Polygon'
        assert abs(m.stone.area-old['stone_face_area'])<.000005,(label,'FACE_AREA_DRIFT')
        assert m.con==old['construction'],(label,'CIRCLE_CONSTRUCTION_CHANGED')
        assert all(q['ok'] for q in m.checks),(label,'U01_2D_CHECK_FAILURE')
        assert len(m.members)==len(old['members']),(label,'MEMBER_GRAPH_DRIFT')
        assert len(m.junctions)==len(old['junctions']),(label,'JUNCTION_GRAPH_DRIFT')
        for op,prior in zip(m.voids,old['openings']):
            assert abs(op['poly'].area-prior['area'])<.000005,(label,'OPENING_AREA_DRIFT',op['id'])
        m2=U.Model(copy.deepcopy(spec))
        mr=U.Model(recursive_reordered(spec))
        assert m2.stone.wkb_hex==m.stone.wkb_hex,(label,'REPEATABILITY')
        assert [v['id'] for v in mr.voids]==mids and abs(mr.stone.area-m.stone.area)<1e-8,(label,'ORDER_INDEPENDENCE')
        mscaled=U.Model(copy.deepcopy(spec),2.)
        assert [o['id'] for o in mscaled.voids]==mids and abs(mscaled.stone.area/(m.stone.area*4)-1)<1e-8,(label,'SCALE_BY_2')
        bb=m.outline.bounds;Bs=mscaled.outline.bounds
        assert max(abs(y-2*x) for x,y in zip(bb,Bs))<1e-5,(label,'2X_BOUNDS_NOT_LINEAR')
        # Direct analytic arc-circle residual checks on all recovered arcs.
        max_apex=0.
        for a in m.con.get('arches',{}).values():
            apex=a.get('apex')
            if not apex:continue
            for k in ('CL','CR'):
                r=a.get(k)
                if r and len(r)==3:
                    resid=abs(math.hypot(apex[0]-r[0],apex[1]-r[1])-r[2])
                    max_apex=max(max_apex,resid)
                    assert resid<2e-5,(label,'CROWN_OFF_ARC',k,resid)
        svg=draw_2d_svg(m,label)
        outcomes.append(dict(id=label,kind=spec['mode'],units=spec.get('units'),
          evidence='MEASURED_UNCALIBRATED_ENGRAVING' if label.startswith('stleu_') and label.endswith('rebuild') else 'SYNTHETIC_OR_IDEALIZED',
          opening_count=len(m.voids),openings=mids,member_count=len(m.members),
          junction_count=len(m.junctions),
          stone_face_area_source_units_sq=m.stone.area,
          source_regression_face_area_abs_error=abs(m.stone.area-old['stone_face_area']),
          apex_circle_residual_max_source_units=max_apex,
          U01_checks_2D=len(m.checks),failed_checks=0,
          stable_against_original=True,stable_on_repeat=True,
          stable_under_reordered_JSON=True,scale_2x_area_4x_pass=True,
          svg=str(svg.relative_to(ROOT))))
    tests={'invalid_mode_rejected':False,
       'invalid_unreachable_measured_arch_rejected':False,
       'invalid_missing_outline_rejected':False}
    malformed=copy.deepcopy(specs[2])
    malformed['mode']='invented'
    try:U.Model(malformed)
    except (ValueError,KeyError,AssertionError):tests['invalid_mode_rejected']=True
    malformed=copy.deepcopy(specs[0])
    malformed['outline']['arch']['CL']=[0,0,.00001]
    try:U.Model(malformed)
    except (ValueError,KeyError,AssertionError):tests['invalid_unreachable_measured_arch_rejected']=True
    malformed=copy.deepcopy(specs[2])
    del malformed['outline']
    try:U.Model(malformed)
    except (ValueError,KeyError,AssertionError):tests['invalid_missing_outline_rejected']=True
    assert all(tests.values()),tests
    png=render_review(models)
    payload={
        'checkpoint':'R52','stage':'2D_SOURCE_ONLY',
        'upstream':'Original unmodified U01 from archived U01–U05 experimental generator',
        'U01_source_sha256':sourcehash,
        'U01_2d_code_run':'T.Model(spec), no 3D solids/export calls',
        'optional_3D_triangle_import_mode':TRIANGLE_MODE,
        'source_spec_count':len(specs),'passing_spec_count':len(outcomes),
        'analytical_numeric_geometric_QA':outcomes,
        'rejected_malformed_input_cases':tests,
        'historical_scale_certification':False,
        'historical_window_layout_certification':False,
        '3D_GLb_render_reexecuted':False,
        'new_2D_runtime_does_not_use_any_user_rib_profile':True,
        'F5ZP_and_R34_to_R51_not_modified':True,
        'review_image':str(png)}
    (OUT/'R52_2D_REGRESSION_QA.json').write_text(json.dumps(payload,indent=2))
    print('R52_2D_REGRESSION_PASS',json.dumps({'fixtures':len(outcomes),
       'checks':sum(x['U01_checks_2D'] for x in outcomes),
       'historical_source_px_scale_validated':False,
       'negative_cases':len(tests),
       'source_hash':sourcehash,
       'review_png':str(png)}))

if __name__=='__main__':
    main()
