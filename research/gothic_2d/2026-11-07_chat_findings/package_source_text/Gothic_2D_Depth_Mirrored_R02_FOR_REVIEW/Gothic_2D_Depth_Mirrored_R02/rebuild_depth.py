#!/usr/bin/env python3
"""Experimental editable 2D depth/face illustration from the mirrored Gothic PNG.
Uses connected face regions, hand-identified landmark locations and contextual
color rules. No measured physical depth and no inferred original masonry section.
Source PNG is never changed. Requirements: numpy, opencv-python, Pillow.
"""
from pathlib import Path
import argparse, json, csv, hashlib, math
import numpy as np, cv2
from PIL import Image

COLORS={'open':'#FFA13B','closed':'#70D936','outer':'#873CE3','indigo':'#4939CF','frame':'#2155D5','middle':'#248DEA','inner':'#65C8F5','ring':'#FDE240','deep':'#F47738','unclassified':'#FFFFFF'}
# Measured only as approximate pixel centers/radii of roundels, not historical dimensions.
ROUNDELS=[(405,245,91,'sixfoil'),(607,245,91,'sixfoil'),(307,412,89,'sixfoil'),(501,412,89,'sixfoil'),(694,412,89,'sixfoil'),(405,577,91,'sixfoil'),(608,577,91,'sixfoil'),(143,598,68,'trefoil'),(858,598,68,'trefoil'),(268,883,159,'sixfoil'),(733,883,159,'sixfoil'),(500,779,31,'circle')]
# Only these seeds are treated as explicit probable openings.
OPEN_SEEDS=[(405,239),(608,238),(306,407),(500,411),(696,406),(404,567),(604,566),(148,606),(860,603),(260,896),(735,896),(499,780)]

def svgpath(cnt):
    v=cv2.approxPolyDP(cnt,.6,True).reshape(-1,2)
    if len(v)<3:return None
    return 'M'+' L'.join(f'{int(x)},{int(y)}' for x,y in v)+' Z'

def svgpaths_from_mask(mask,epsilon=.65):
    cc,_=cv2.findContours(mask.astype('uint8'),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    return [svgpath(cv2.approxPolyDP(c,epsilon,True)) for c in cc if cv2.contourArea(c)>=1.5 and svgpath(c)]

def make_open_arcade_mask(h,w):
    mask=np.zeros((h,w),np.uint8)
    # Four architectural openings are clipped by bottom edge; explicit provisional
    # segment boundaries follow the displayed arch outline, never overwrite ink.
    for left,right,cx,peak in [(57,258,155,1035),(284,477,378,1035),(524,720,622,1035),(747,945,844,1035)]:
        pts=[]
        for x in np.linspace(left,right,100):
            t=abs((x-cx)/max(cx-left,right-cx))
            y=peak+110*(t**1.6)
            pts.append([int(x),int(y)])
        pts += [[right,h-1],[left,h-1]]
        cv2.fillPoly(mask,[np.array(pts,np.int32)],1)
    return mask

def region_color(x,y,w,h,area,idx,labels):
    # Conservatively infer display layer, not actual stone depth.
    near=min((math.hypot(x-cx,y-cy)-r,cx,cy,r) for cx,cy,r,_ in ROUNDELS)
    ringdist=abs(near[0]);
    if ringdist<22: return 'ring'
    if ringdist<36: return 'deep' if ringdist<13 else 'ring'
    # Approximate distance from broad arch perimeter; used for color grouping.
    xc=abs(x-500)/500
    if xc>.82 and y<1070:return 'outer'
    if xc>.72 and y<1080:return 'indigo'
    if xc>.61 and y<1080:return 'frame'
    if xc>.52 and y<1080:return 'middle'
    if xc>.42 and y<1070:return 'inner'
    # distinguish slim curved ring bands from larger green infill, using region area
    if area<105:return 'inner'
    if area<500:return 'middle'
    if area<1500 and y<750:return 'inner'
    return 'closed'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('--out-dir',default='.')
    args=ap.parse_args();out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
    src=Path(args.source);rgb=np.array(Image.open(src).convert('RGB'));h,w=rgb.shape[:2]
    lum=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);ink=(lum<150).astype('uint8')
    barrier=cv2.dilate(ink,np.ones((3,3),np.uint8),iterations=1)
    n,labels,stats,cent=cv2.connectedComponentsWithStats((1-barrier).astype('uint8'),4)
    open_ids={int(labels[y,x]) for x,y in OPEN_SEEDS if 0<=x<w and 0<=y<h and labels[y,x]>0}
    assign={}; rows=[]; closed=0
    for i in range(1,n):
        x,y,ww,hh,area=map(int,stats[i]);cx,cy=cent[i]
        if area<16:continue
        touches=(x<=0 or y<=0 or x+ww>=w or y+hh>=h)
        if i in open_ids:cls='open'
        elif i == 5:cls='outer'  # dominant outer arch-moulding face
        elif i in (918,919,940,958):cls='ring'  # large sixfoil surround candidates
        elif touches or area>h*w*.18:cls='unclassified'
        else:cls=region_color(cx,cy,ww,hh,area,i,labels)
        assign[i]=cls
        rows.append(dict(face_id=i,class_name=cls,area_px=area,center_x=round(cx,2),center_y=round(cy,2),touches_crop_edge=touches,classification='seeded opening' if i in open_ids else 'heuristic candidate'))
    # Draw raster preview in color with every original black pixel held untouched.
    result=np.full((h,w,3),255,np.uint8)
    for i,cls in assign.items():
        if cls=='unclassified':continue
        color=tuple(bytes.fromhex(COLORS[cls][1:]));result[labels==i]=color
    arcade=make_open_arcade_mask(h,w)
    # only recolor pixels NOT in the original ink, preserving every source stroke
    result[(arcade>0)&(ink==0)]=tuple(bytes.fromhex(COLORS['open'][1:]))
    result[ink>0]=(0,0,0)
    Image.fromarray(result).save(out/'MIRRORED_DEPTH_COLOR.png')
    Image.fromarray(rgb).save(out/'SOURCE_MIRRORED_UNMODIFIED.png')
    # Vectorize EACH face as a separately selectable region. Draw paths for black
    # ink contours on top (instead of embedding a PNG), retaining line work.
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
           '<title>Gothic mirrored window — reversible 2D face and layer study</title>',
           '<desc>Experimental colored faces, black original scan-derived contour paths. Display depth only, NOT measured physical depth.</desc>',
           '<rect width="100%" height="100%" fill="white"/>','<g id="face-regions">']
    for i,cls in assign.items():
        if cls=='unclassified':continue
        sub=(labels==i).astype('uint8')
        contours,hierarchy=cv2.findContours(sub,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is None:continue
        d=' '.join(p for c in contours if (p:=svgpath(c)))
        if d:parts.append(f'<path id="face_{i}" data-class="{cls}" data-confidence="experimental" d="{d}" fill="{COLORS[cls]}" fill-rule="evenodd"/>')
    parts.append('</g><g id="lower-arcade-opening-candidates" fill="'+COLORS['open']+'">')
    for j,(left,right,cx,peak) in enumerate([(57,258,155,1035),(284,477,378,1035),(524,720,622,1035),(747,945,844,1035)]):
        points=[]
        for x in np.linspace(left,right,100):
            t=abs((x-cx)/max(cx-left,right-cx));y=peak+110*(t**1.6);points.append((x,y))
        points += [(right,h),(left,h)]
        d='M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in points)+' Z'
        parts.append(f'<path id="lower_opening_{j+1}" data-confidence="provisional" d="{d}"/>')
    parts.append('</g><g id="black-source-ink" fill="black" fill-rule="evenodd">')
    cc, hierarchy=cv2.findContours(ink,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is not None:
        # Use composited compound path with holes represented through evenodd.
        d=' '.join(p for c in cc if (p:=svgpath(c)))
        parts.append(f'<path d="{d}"/>')
    parts.append('</g></svg>')
    (out/'MIRRORED_DEPTH_COLOR_EDITABLE.svg').write_text('\n'.join(parts))
    with (out/'FACE_REGISTER.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['face_id','class_name','area_px','center_x','center_y','touches_crop_edge','classification']);writer.writeheader();writer.writerows(rows)
    report={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_size':[w,h],'connected_regions':n-1,'classified_faces':sum(v!='unclassified' for v in assign.values()),'explicit_opening_seeds':len(OPEN_SEEDS),'resolved_opening_region_ids':sorted(open_ids),'class_counts':{c:list(assign.values()).count(c) for c in COLORS},'lower_arcade_openings':'four provisional crop-clipped masks','known_limitations':['Colors indicate display-layer hierarchy, not physical depth','Some thin/misaligned raster boundaries cause merged or fragmented regions','Lower openings are drawn as provisional shapes and must be validated against scan','Only seeded foil apertures have explicit semantic identification','This output is not a compass-arc reconstruction'],'source_unchanged':True}
    (out/'QA.json').write_text(json.dumps(report,indent=2))
    with (out/'README.md').open('w') as f:
        f.write('# Gothic 2D mirrored color/depth workflow R02 — for review\n\n')
        f.write('Reruns the experimental R01 depth-classification idea on the complete mirrored black-line PNG. All sources unchanged. **Not approved**.\n\n')
        f.write('The files `MIRRORED_DEPTH_COLOR.png` and `MIRRORED_DEPTH_COLOR_EDITABLE.svg` implement colored faces and preserved black linework. `FACE_REGISTER.csv` records every selected face and its candidate class.\n\n')
        f.write('## Conventions\n- Orange: identified or provisional opening\n- Green: provisional closed/spandrel face\n- Purple / indigo / blue / cyan: proposed outer-to-inner visual layer order\n- Yellow / orange-red: foil rings and inner moulding faces\n- Black: source-derived linework\n- White: unclassified/background\n\n')
        f.write('## Reproduction\n`python rebuild_depth.py "SOURCE_MIRRORED_UNMODIFIED.png" --out-dir .`\n\n')
        f.write('## QA and limitations\nThis is **face coloring**, not exact compass construction. Some color-layer assignments are geometric heuristics, not independently verified masonry classifications. Lower cropped openings use provisional masks. Compare each region with the historical source before approval. No cathedral generator or locked dimensions modified.\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
