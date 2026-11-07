#!/usr/bin/env python3
"""Experimental, non-destructive Gothic raster-to-SVG face register.

Usage: python build_gothic_svg_test.py SOURCE.png OUTPUT_DIRECTORY
Does not claim raster contours are exact historical circle construction.
"""
import sys, json, hashlib, csv
from pathlib import Path
import numpy as np, cv2
from PIL import Image

def to_path(contours, offset=0.65):
    commands=[]
    for c in contours:
        if len(c)<3: continue
        a=cv2.approxPolyDP(c,offset,True)[:,0,:]
        if len(a)<3: continue
        commands.append('M '+' L '.join(f'{x},{y}' for x,y in a)+' Z')
    return ' '.join(commands)

def main(source,out):
    source=Path(source);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    img=np.array(Image.open(source).convert('RGB'))
    h,w=img.shape[:2]
    gray=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    ink=(gray<135).astype('uint8')
    count,lab,stats,cent=cv2.connectedComponentsWithStats(1-ink,8)
    facepaths=[]; records=[]
    for i in range(1,count):
        x,y,ww,hh,area=[int(z) for z in stats[i]]
        if area<120:continue
        mask=(lab[y:y+hh,x:x+ww]==i).astype('uint8')
        c,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        if not c:continue
        contour=max(c,key=cv2.contourArea)
        contour[:,0,0]+=x;contour[:,0,1]+=y
        path=to_path([contour],.55)
        if not path:continue
        touches=x==0 or y==0 or x+ww>=w or y+hh>=h
        facepaths.append((i,path,touches))
        records.append(dict(face_id=f'face_{i:03}',area_px=area,bbox_px=[x,y,ww,hh],centroid_px=[round(float(v),2) for v in cent[i]],touches_crop_boundary=touches,classification='unclassified',physical_depth='unknown'))
    # Black source ink faithfully vectorized as filled shapes: NOT circular-arc fit.
    contours,hier=cv2.findContours(ink,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    parts=[]
    for c in contours:
        if cv2.arcLength(c,True)<7:continue
        p=to_path([c],.6)
        if p:parts.append(p)
    paths=' '.join(parts)
    start=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
    def faces():
        return '\n'.join(f'<path id="face_{i:03}" class="{("partial-face" if t else "enclosed-face")}" d="{p}" fill="white" stroke="none" data-status="unclassified"/>' for i,p,t in facepaths)
    end=f'\n<path id="ink_vector" d="{paths}" fill="black" fill-rule="evenodd" stroke="none"/>\n</svg>\n'
    (out/'BLACK_TRACE_WITH_SELECTABLE_FACES.svg').write_text(start+'<rect width="100%" height="100%" fill="white"/>\n<g id="independent_faces">\n'+faces()+'\n</g>'+end,encoding='utf-8')
    # QC preview only: enclosed regions violet tint; cropped regions pale blue; no architectural classification assumed.
    qc=img.copy()
    for i,p,t in facepaths:
        region=lab==i
        color=np.array([205,225,247] if t else [224,241,216])
        qc[region]=(0.65*qc[region]+0.35*color).astype('uint8')
    qc[ink.astype(bool)]=[0,0,0]
    Image.fromarray(qc).save(out/'FACE_DETECTION_QA.png')
    (out/'FACE_REGISTER.json').write_text(json.dumps({'source':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'image_size_px':[w,h],'faces':records,'note':'Pixel-derived faces; no mathematical circular-arc proof, historical scale, or depth inferred.'},indent=2))
    with (out/'FACE_REGISTER.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=['face_id','area_px','bbox_px','centroid_px','touches_crop_boundary','classification','physical_depth']);wr.writeheader();wr.writerows(records)
    (out/'README.md').write_text('''# Gothic 2D face-and-trace test — experimental

This is a reproducible **raster-derived** SVG, **not yet** a genuinely measured circular-arc reconstruction. Each detected background region is an independent `<path>` with `id="face_NNN"`, accessible in SVG editors. The black linework is vectorized from the source ink; the original source is not changed.

Files:
- `BLACK_TRACE_WITH_SELECTABLE_FACES.svg`: selectable face objects plus separate black-ink layer.
- `FACE_DETECTION_QA.png`: diagnostic color only (green-tinted fully enclosed image regions; blue-tinted regions touching the crop border). These colors do **not** imply physical open/closed classification.
- `FACE_REGISTER.csv`/`.json`: pixel areas, positions, crop-boundary status, unclassified semantics.
- `build_gothic_svg_test.py`: repeatable script.

Next validation stage: identify each foil and moulding boundary, manually assign semantic opening/closed/stone states, locate and fit arc centers with source pixels, evaluate residuals and junction tangencies, and replace the traced stroke with analytic SVG A/arcs or parametric curves. Retain all failed hypotheses in a QA log. Depth is not determinable from this elevation.

No prior scripts, approved generators or cathedral geometry were touched.
''')
    print('faces',len(records),'partial',sum(x['touches_crop_boundary'] for x in records),'ink-contours',len(parts))

if __name__=='__main__':main(sys.argv[1],sys.argv[2])
