#!/usr/bin/env python3
"""Experimental non-destructive ink-contour vectorization of Ungewitter Plate CXVIII.
These are contours from a historical scan, NOT mathematically reconstructed architecture.
Usage: python trace_plate.py /path/to/plate.png /path/to/output_dir
"""
import sys, pathlib, hashlib, json, shutil
import numpy as np, cv2
from PIL import Image
try: import cairosvg
except ImportError: cairosvg=None

def vectorize(img, minimum_area=4, threshold=190, offset=(0,0)):
    g=np.array(img.convert('L'))
    mask=np.uint8(g<threshold)*255
    # conservative removal of isolated dust only
    num, labels, stats, centroids=cv2.connectedComponentsWithStats(mask,8)
    cleaned=np.zeros_like(mask)
    for i in range(1,num):
        if stats[i,cv2.CC_STAT_AREA]>=minimum_area: cleaned[labels==i]=255
    contours, hierarchy=cv2.findContours(cleaned,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    paths=[]; n=0
    for contour in contours:
        if cv2.arcLength(contour,True)<3: continue
        epsilon=0.37
        approx=cv2.approxPolyDP(contour,epsilon,True).reshape(-1,2)
        if len(approx)<3:continue
        x,y=offset
        paths.append('M'+' L'.join(f'{int(q[0]+x)},{int(q[1]+y)}' for q in approx)+' Z')
        n+=1
    return ' '.join(paths),n,cleaned

def svg_for(original, crop, name, axis=None, circles=None, speculative=None):
    W,H=original.size
    if crop: x0,y0,x1,y1=crop; piece=original.crop(crop)
    else: x0=y0=0;piece=original
    w,h=piece.size
    path,n,mask=vectorize(piece,minimum_area=5 if not crop else 3,offset=(0,0))
    # All paths are filled, not stroked. This preserves the historic scanned ink with holes.
    layers=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
      f'<title>{name} — 2D vectorized historical ink, construction overlays provisional</title>',
      '<desc>Solid black is image-derived ink silhouette, not certified analytic circle geometry. Gray guides are design axes; red guides indicate hypotheses. Dotted black circles are fitted or reference circle candidates.</desc>',
      '<rect width="100%" height="100%" fill="white"/>',
      f'<g id="scan-derived-black-ink" fill="black" fill-rule="evenodd"><path d="{path}"/></g>']
    if axis:
        cx,cy=axis
        layers.append(f'<g id="dividing-axes-lightgray-dashed" fill="none" stroke="#a3a3a3" stroke-width="1" stroke-dasharray="8,6"><path d="M {cx} 0 V {h} M 0 {cy} H {w}"/></g>')
    if circles:
        layers.append('<g id="complete-reference-circles-black-dotted" fill="none" stroke="#111" stroke-width="1.15" stroke-dasharray="1,5" stroke-linecap="round">')
        for cx,cy,r in circles:layers.append(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>')
        layers.append('</g>')
    if speculative:
        layers.append('<g id="unverified-construction-red-dashed" fill="none" stroke="#c62828" stroke-width="1.05" stroke-dasharray="7,5">')
        for x1,y1,x2,y2 in speculative:layers.append(f'<path d="M{x1},{y1} L{x2},{y2}"/>')
        layers.append('</g>')
    layers.append('</svg>')
    dest=out/(name+'.svg');dest.write_text('\n'.join(layers))
    if cairosvg:
        cairosvg.svg2png(bytestring=('\n'.join(layers)).encode(),write_to=str(out/(name+'.png')),output_width=min(1800,w*2),output_height=min(1800,h*2))
    return {'file':name+'.svg','image_box_original_pixels':list(crop) if crop else [0,0,W,H],'contour_count':n,'status':'scan-derived vector silhouettes; not compass-certified'}

src=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);out.mkdir(exist_ok=True,parents=True)
original=Image.open(src).convert('RGB')
shutil.copyfile(src,out/'ORIGINAL_UNMODIFIED.png')
results=[]
results.append(svg_for(original,None,'PLATE_CXVIII_FULL_SCAN_VECTOR'))
# Figure crops anchored directly to scanned image pixels; not measurements of historical architectural scale.
regions={
'FIG_1203':((255,174,585,493),(421,337),None,None),
'FIG_1204':((680,185,980,510),(133,145),[(133,145,132)],[(133,145,35,98),(133,145,234,89)]),
'FIG_1204a':((1051,188,1346,485),(149,152),[(149,152,124)],None),
'FIG_1205':((1340,175,1680,510),(172,166),[(172,166,144)],[(172,166,68,61)]),
'FIG_1206':((160,514,485,845),(161,171),None,None),
'FIG_1207':((467,475,831,857),(177,183),None,None),
'FIG_1207a':((819,475,1172,852),(171,181),None,None),
'FIG_1207b':((1150,483,1513,855),(183,181),None,None),
'FIG_1207c':((1480,488,1870,856),(190,180),None,None),
'FIG_1208':((127,858,510,1265),(196,216),None,None),
'FIG_1210':((537,930,729,1185),(92,119),None,None),
'FIG_1211':((729,913,995,1195),(138,146),None,None),
'FIG_1212':((1010,921,1244,1202),(123,144),None,None),
'FIG_1212a':((1235,914,1466,1214),(117,151),None,None),
'FIG_1209':((1450,850,1900,1270),(221,209),None,None),
}
for name,(crop,axis,circles,spec) in regions.items():
    results.append(svg_for(original,crop,name+'_SCAN_TRACE',axis,circles,spec))
metadata={'source_filename':src.name,'original_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'original_dimensions':list(original.size),'method':'threshold 190; connected component dust threshold 3-5 pixels; cv2 findContours RETR_TREE; approxPolyDP 0.37 px; fill-rule evenodd','figures':results,'interpretation_warning':'All black tracings are scan-derived, not validated analytic circular arcs. Dashed red lines mark hypotheses; circles are rough reference candidates pending fitting. Measured units are pixels only. No historical geometry or project baseline modified.'}
(out/'TRACE_MANIFEST.json').write_text(json.dumps(metadata,indent=2))
(out/'README.md').write_text('''# Ungewitter–Mohrmann, Volume II, Plate CXVIII — 2D tracing R01\n\n## Contents\n- `ORIGINAL_UNMODIFIED.png`: exact supplied original (byte-for-byte).\n- `PLATE_CXVIII_FULL_SCAN_VECTOR.svg`: editable entire historical ink image as black filled contours. Includes all engraved marks, including lettering.\n- `FIG_*_SCAN_TRACE.svg`: cropped, individually editable figure traces with light-gray dashed axes.\n- `FIG_1204` and `FIG_1205`: black dotted circle candidates and red dashed provisional compass guides. These are NOT confirmed original compass centers.\n- `TRACE_MANIFEST.json`: hashes, crop coordinates, processing settings and contour counts.\n- `trace_plate.py`: reproducible tracing code.\n\n## Status: experimental — needs geometric validation and user review\nThe black drawing is *image-derived vector ink*, rather than a mathematically recovered compass-and-straightedge reconstruction. This preserves the distinctive published engraving and is a useful first pass before separately replacing individual curves with fitted true circles. Thin ink and crowded labels can be fragmented; the crop boxes should be checked. Recovered circles shown are approximate reference candidates only. There is **no architectural scale calibration**. The source is not silently promoted to cathedral geometry or a working approved generator.\n\n## Next pass\nIndividually identify and fit the circular arcs in figures 1204, 1205 and 1209 from selectively sampled ink points, then test tangencies, intersections and source residuals. Keep solid outlines black; axes light-gray dashed; full recovered circles dotted black; conjectures red dashed.\n\nRun: `python trace_plate.py plate.png output_folder` (requires opencv-python, numpy, Pillow; CairoSVG optional for PNG previews).\n''')
print(json.dumps({'figures':len(results),'total_contours':sum(i['contour_count'] for i in results),'source_sha256':metadata['original_sha256']},indent=2))
