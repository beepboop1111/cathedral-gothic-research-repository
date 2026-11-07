#!/usr/bin/env python3
"""R03: reproducible image-space vector tracing, faces, circle candidates and QA.
Usage: python reconstruct_r03.py /path/to/mirrored.png output_dir
Never modifies the source, existing generators or any cathedral dimensions.
"""
import sys, csv, json, hashlib, math, shutil
from pathlib import Path
import numpy as np, cv2
from PIL import Image
from scipy.ndimage import map_coordinates

# measured APPROXIMATE locations selected from the supplied image; validation below
FEATURES=[('U_top_L','sexfoil',632,382,136),('U_top_R','sexfoil',932,382,136),
 ('U_middle_L','sexfoil',485,642,137),('U_middle_C','sexfoil',783,642,137),('U_middle_R','sexfoil',1081,642,137),
 ('U_bottom_L','sexfoil',633,902,137),('U_bottom_R','sexfoil',933,902,137),
 ('lower_L','sexfoil',418,1370,219),('lower_R','sexfoil',1148,1370,219),
 ('side_L','trefoil',218,941,107),('side_R','trefoil',1348,941,107)]


def contour_path(contour, tolerance=0.65):
    p=cv2.approxPolyDP(contour,tolerance,True)[:,0,:]
    if len(p)<3:return ''
    return 'M '+' L '.join(f'{x},{y}' for x,y in p)+' Z'

def circle_candidate(ink, cx,cy,r):
    # Search for a near-circular black circumference. This locates a raster
    # ring, not the historical regulating circle or physical scale.
    h,w=ink.shape
    t=np.linspace(0,2*np.pi,360,endpoint=False)
    ct,st=np.cos(t),np.sin(t)
    best=(-1,None)
    for x in np.arange(cx-7,cx+8,2):
      for y in np.arange(cy-7,cy+8,2):
        for rr in np.arange(r-14,r+15,2):
          xx=np.rint(x+rr*ct).astype(int);yy=np.rint(y+rr*st).astype(int)
          valid=(xx>=0)&(yy>=0)&(xx<w)&(yy<h)
          score=float(np.mean(ink[yy[valid],xx[valid]])) if valid.any() else 0
          if score>best[0]:best=(score,(float(x),float(y),float(rr)))
    score,(x,y,rr)=best
    # nearest detected black pixel along radial line, within 3 px;
    # geometric least squares of these independent measured pixel positions.
    points=[]
    for a,b in zip(ct,st):
       matches=[]
       for off in np.linspace(-3,3,13):
          qx=int(round(x+(rr+off)*a));qy=int(round(y+(rr+off)*b))
          if 0<=qx<w and 0<=qy<h and ink[qy,qx]:matches.append((abs(off),qx,qy))
       if matches:
          _,qx,qy=min(matches)
          points.append([qx,qy])
    if len(points)>=12:
       sys.path.insert(0,str(Path(__file__).resolve().parent))
       try:
          from gothic_geometry import circle_fit
          fit=circle_fit(points)
          x,y=fit.center; rr=fit.radius; rmse=fit.rmse
       except Exception:
          rmse=None
    else:rmse=None
    return dict(center_x_px=round(x,3),center_y_px=round(y,3),radius_px=round(rr,3),
                circumference_ink_coverage=round(score,3),n_measured_points=len(points),
                radial_fit_rmse_px=None if rmse is None else round(rmse,3),
                status='experimental_raster_fitted_ring_not_historical_proof')

def main(source,out):
    source=Path(source);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,out/'SOURCE_MIRRORED_UNMODIFIED.png')
    im=np.asarray(Image.open(source).convert('RGB'));h,w=im.shape[:2]
    g=cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)
    ink=(g<142).astype('uint8')
    count,labels,stats,cent=cv2.connectedComponentsWithStats(1-ink,8)
    records=[];facepaths=[]
    for i in range(1,count):
        x,y,ww,hh,area=map(int,stats[i])
        if area<60:continue
        region=(labels[y:y+hh,x:x+ww]==i).astype('uint8')
        cc,_=cv2.findContours(region,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        if not cc:continue
        c=max(cc,key=cv2.contourArea); c[:,0,0]+=x;c[:,0,1]+=y
        p=contour_path(c,.65)
        if not p:continue
        touch=x==0 or y==0 or x+ww>=w or y+hh>=h
        record=dict(face_id=f'face_{i:04d}',label_index=i,area_px=area,
                    centroid_x_px=round(float(cent[i][0]),2),centroid_y_px=round(float(cent[i][1]),2),
                    x=x,y=y,width=ww,height=hh,crop_edge=touch,classification='unclassified',
                    evidence='raster segmentation',depth='unknown')
        records.append(record);facepaths.append((i,p,record))

    # Explicit candidate seed positions, never automatically assign every region.
    seeds={}
    for name,kind,cx,cy,r in FEATURES:
        for pos,label in [((cx,cy),'opening_candidate')]:
            xx,yy=map(int,pos)
            if 0<=xx<w and 0<=yy<h:
                idx=int(labels[yy,xx]);seeds.setdefault(idx,[]).append((name,label))
    for k,(x,y) in enumerate([(145,1820),(600,1830),(970,1830),(1410,1820)]):
        if 0<=x<w and 0<=y<h:seeds.setdefault(int(labels[y,x]),[]).append((f'arcade_{k+1}','opening_candidate'))
    # Four selected spandrel spots, still hypotheses, not confirmed masonry.
    for k,(x,y) in enumerate([(784,1115),(784,1170),(95,1180),(1470,1180)]):
        if 0<=x<w and 0<=y<h:seeds.setdefault(int(labels[y,x]),[]).append((f'spandrel_{k+1}','closed_candidate'))
    for rec in records:
        choices=seeds.get(rec['label_index'],[])
        if choices and not rec['crop_edge']:
            kinds={z[1] for z in choices}
            if len(kinds)==1:
                rec['classification']=choices[0][1]
                rec['evidence']='manual seed; provisional; check boundary leakage'
        rec['seed_names']=';'.join(z[0] for z in choices)

    cc,hier=cv2.findContours(ink,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    blackpaths=[contour_path(c,.55) for c in cc if cv2.arcLength(c,True)>=7]
    blackpath=' '.join(p for p in blackpaths if p)
    fits=[]
    for name,kind,cx,cy,r in FEATURES:
       fit=circle_candidate(ink,cx,cy,r)
       fits.append(dict(name=name,motif=kind,**fit))
    # numerical comparison of image and horizontally reflected image (diagnostic only)
    region=ink[160:1940,85:w-85]
    reflection_mismatch=float(np.mean(region!=region[:,::-1]))
    svg_head=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n<title>Gothic R03 mirrored tracery - experimental raster-derived reconstruction</title>\n'
    black=f'<path id="raster_ink_vector" fill="black" fill-rule="evenodd" stroke="none" d="{blackpath}"/>\n'
    faces='\n'.join(f'<path id="{r["face_id"]}" d="{p}" fill="{("#ffb45e" if r["classification"]=="opening_candidate" else "#bceab0" if r["classification"]=="closed_candidate" else "white")}" stroke="none" data-state="{r["classification"]}"/>' for _,p,r in facepaths)
    base=f'<rect width="{w}" height="{h}" fill="white"/>\n<g id="selectable_faces">{faces}</g>\n<g id="raster_black_linework">{black}</g>'
    (out/'01_BLACK_ONLY.svg').write_text(svg_head+f'<rect width="{w}" height="{h}" fill="white"/><g id="ink">{black}</g></svg>')
    (out/'02_SELECTABLE_FACES.svg').write_text(svg_head+base+'</svg>')
    circles='\n'.join(f'<circle id="fit_{f["name"]}" cx="{f["center_x_px"]}" cy="{f["center_y_px"]}" r="{f["radius_px"]}" fill="none" stroke="black" stroke-width="1.5" stroke-dasharray="2 6" opacity=".8"/>' for f in fits)
    pts='\n'.join(f'<circle cx="{f["center_x_px"]}" cy="{f["center_y_px"]}" r="3" fill="black"/>' for f in fits)
    axes=f'<g id="axes" stroke="#a7a7a7" stroke-width="1.5" stroke-dasharray="9 8"><path d="M {w/2:.1f} 0 V {h}"/><path d="M0 640 H{w}"/><path d="M0 1360 H{w}"/></g>'
    # Explicitly uncertain construction hypotheses in red.
    uncertain='<g id="unverified_center_connections" stroke="#c43b36" stroke-width="1.3" stroke-dasharray="9 7" fill="none" opacity=".85"><path d="M 633 382 L 933 382 M 485 642 L 783 642 L 1081 642 M 633 902 L 933 902"/></g>'
    (out/'03_CONSTRUCTION_ANALYSIS.svg').write_text(svg_head+f'<rect width="{w}" height="{h}" fill="white"/>'+axes+black+'<g id="fitted_candidate_circles">'+circles+pts+'</g>'+uncertain+'</svg>')
    (out/'04_CLASSIFIED_CANDIDATE_FACES.svg').write_text(svg_head+base+'</svg>')
    with (out/'FACE_REGISTER.csv').open('w',newline='') as fh:
        writer=csv.DictWriter(fh,fieldnames=[k for k in records[0] if k!='label_index']);writer.writeheader()
        for r in records:writer.writerow({k:v for k,v in r.items() if k!='label_index'})
    with (out/'CIRCLE_FIT_REGISTER.csv').open('w',newline='') as fh:
        writer=csv.DictWriter(fh,fieldnames=fits[0].keys());writer.writeheader();writer.writerows(fits)
    qa={'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'image_size_px':[w,h],
        'faces_over_60_px':len(records),'fully_enclosed_faces':sum(not r['crop_edge'] for r in records),
        'crop_edge_faces':sum(r['crop_edge'] for r in records),'opening_candidate_faces':sum(r['classification']=='opening_candidate' for r in records),
        'closed_candidate_faces':sum(r['classification']=='closed_candidate' for r in records),
        'circle_candidates':len(fits),'mirrored_pixel_mismatch_fraction_interior':round(reflection_mismatch,4),
        'note':'All units in image pixels. Circle fits use measured raster contours; no certified historical compass construction, masonry scale or depth.'}
    (out/'QA_REPORT.json').write_text(json.dumps(qa,indent=2)+'\n')
    (out/'README.md').write_text('''# Gothic 2D Reconstruction R03 — experimental / for review

**Source authority:** `SOURCE_MIRRORED_UNMODIFIED.png` (unchanged copy; checksum in QA_REPORT.json). The supplied symmetrical composition is a modern mirrored image, not evidence that the historical original included its reflected half.

## Outputs
- `01_BLACK_ONLY.svg`: whole sheet, image-derived vector paths, no axes or colors.
- `02_SELECTABLE_FACES.svg`: independent background-region SVG paths and black ink overlay, faces are white (unclassified in appearance).
- `03_CONSTRUCTION_ANALYSIS.svg`: whole-sheet black trace, thin dashed light gray axes, dotted black fitted circle candidates, dashed red hypothetical regulating connections.
- `04_CLASSIFIED_CANDIDATE_FACES.svg`: *provisional* orange opening-seed faces and green closed-seed faces. White means unclassified. Never take this as verified open-vs-stone classification.
- `CIRCLE_FIT_REGISTER.csv`: repeat-foil frame candidates, center, radius, pixel-fit RMSE and fraction of circular samples hitting ink.
- `FACE_REGISTER.csv`: face positions and tentative semantics.
- `QA_REPORT.json`: quantitative checks, provenance and limits.
- `reconstruct_r03.py`: repeatable source-to-output workflow.

## Evidence levels
1. **Source ink:** traced black pixel boundaries (vectorized); some line thickness artefacts remain.
2. **Measured analytical candidates:** circles matched to the ink of roundel frames, 11 rings total. Their centers/radii are measurable in source pixels, NOT historical CAD-grade construction circles.
3. **Experimental hypotheses:** red links, classifications, relationship to symmetry; must be checked manually.

The central sixfoil is not yet proven to use identical six circular arcs; no precise cusp/tangency construction has been certified. For future fitting select contour points belonging to each separate arc and check residuals against independent scan pixels. The R03 result is a diagnostic baseline, not approved generator code.

No modifications to V08, cathedral geometry, locked dimensions or existing generators.
''')
    # quick previews from SVG
    import cairosvg
    for fname in ['01_BLACK_ONLY','03_CONSTRUCTION_ANALYSIS','04_CLASSIFIED_CANDIDATE_FACES']:
        cairosvg.svg2png(url=str(out/(fname+'.svg')),write_to=str(out/(fname+'.png')),output_width=1000)
    print(json.dumps(qa,indent=2))

if __name__=='__main__':
    main(sys.argv[1],sys.argv[2])
