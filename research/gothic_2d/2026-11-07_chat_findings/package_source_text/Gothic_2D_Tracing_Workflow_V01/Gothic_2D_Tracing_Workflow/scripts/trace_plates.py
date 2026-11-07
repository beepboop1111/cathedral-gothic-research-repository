#!/usr/bin/env python3
"""Reproducible, READ-ONLY-on-input Gothic plate 2D trace batch.

Color conventions: black confirmed image strokes, light gray dashed axes,
red dashed uncertain alternatives. Recovered full circles can be toggled
on as black dotted geometry. No architectural scale is inferred.

This tool performs color-selective *raster vectorization*: contours are editable
SVG polylines, NOT authenticated radius/circle fits. Separate measured geometry
is made by four_circle_analysis.py.
"""
import argparse, json, hashlib
from pathlib import Path
from xml.sax.saxutils import escape
import cv2
import numpy as np

CASES = [
 ('1193','plate_1193_1198.png',(30,62,505,400),'priority_1'),
 ('1194','plate_1193_1198.png',(545,45,1000,400),'priority_1'),
 ('1195','plate_1193_1198.png',(1030,30,1510,405),'priority_1'),
 ('1196','plate_1193_1198.png',(50,455,490,915),'secondary'),
 ('1197','plate_1193_1198.png',(550,460,985,915),'secondary'),
 ('1198','plate_1193_1198.png',(1020,450,1510,923),'secondary'),
 ('TREFOIL','trefoil_quatrefoil.png',(35,102,865,795),'secondary'),
 ('QUATREFOIL','trefoil_quatrefoil.png',(882,102,1750,795),'secondary'),
 ('1236','figure_1236_study.png',(22,24,1100,1323),'secondary_visual_only'),
 ('FOUR_CIRCLE','four_circle_construction.png',(90,78,990,934),'priority_1'),
]

def extract_masks(img):
    a=img.astype(np.int16)
    b,g,r=a[:,:,0],a[:,:,1],a[:,:,2]
    mx=np.maximum.reduce([r,g,b]);mn=np.minimum.reduce([r,g,b])
    dark=(mx<115)&((mx-mn)<45)
    gray=(mx>=115)&(mx<234)&((mx-mn)<15)
    # Black labels, if present, may remain. This is a faithful raster-derived
    # candidate rather than claim of clean historical line discrimination.
    red=(r>105)&(r-g>48)&(r-b>48)
    green=(g>60)&(g-r>40)&(g-b>22)
    return {'outlines':dark.astype('uint8'), 'axes':gray.astype('uint8'),
            'uncertain':red.astype('uint8'), 'source_green_marks':green.astype('uint8')}

def paths(mask,min_area=5,min_perimeter=11,epsilon=.45):
    # OpenCV contour border of each color-classified stroke is retained as an
    # editable closed polyline. The paired edge contours represent ink width.
    cs,_=cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
    result=[]
    for c in cs:
        if cv2.arcLength(c,True)<min_perimeter and cv2.contourArea(c)<min_area:continue
        if len(c)<3:continue
        c=cv2.approxPolyDP(c,epsilon,True).reshape(-1,2)
        if len(c)<3:continue
        result.append(c)
    return result

def path_xml(contours):
    out=[]
    for poly in contours:
        d='M '+' L '.join(f'{x:.2f},{y:.2f}' for x,y in poly)+' Z'
        out.append(f'<path d="{d}"/>')
    return '\n'.join(out)

def svg_case(img,crop,case,source,priority,overlay=False):
    x0,y0,x1,y1=crop; cut=img[y0:y1,x0:x1]; h,w=cut.shape[:2]
    masks=extract_masks(cut)
    groups={}
    for layer,mask in masks.items():
        groups[layer]=paths(mask,epsilon=.65 if layer=='outlines' else .9)
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
       f'<title>{escape(case)} — image-derived editable vector trace</title>',
       f'<desc>Source {escape(source)}. Uncalibrated source pixels, crop {crop}; generated interpretation is not historically verified.</desc>',
       '<rect width="100%" height="100%" fill="white"/>',
       '<g id="dividing_axes" fill="none" stroke="#c4c4c4" stroke-width=".75" stroke-dasharray="4 5" opacity=".72">',
       path_xml(groups['axes']),'</g>',
       '<g id="source_black_outlines" fill="none" stroke="black" stroke-width=".9">',path_xml(groups['outlines']),'</g>',
       '<g id="uncertain_alternative_red" fill="none" stroke="#d32222" stroke-width="1" stroke-dasharray="7 5">',path_xml(groups['uncertain']),'</g>',
       '</svg>']
    return '\n'.join(s), {k:len(v) for k,v in groups.items()},cut

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    a=p.parse_args();out=a.root/'outputs'; inp=a.root/'inputs';out.mkdir(exist_ok=True)
    qa=[]
    for case,filename,crop,priority in CASES:
        path=inp/filename
        image=cv2.imread(str(path),cv2.IMREAD_COLOR)
        if image is None:raise FileNotFoundError(path)
        H,W=image.shape[:2];x0,y0,x1,y1=crop
        if not(0<=x0<x1<=W and 0<=y0<y1<=H):raise ValueError((case,crop,image.shape))
        svg,counts,cut=svg_case(image,crop,case,filename,priority)
        name=f'{case}_VECTOR_TRACE';s=out/(name+'.svg');s.write_text(svg,encoding='utf-8')
        cv2.imwrite(str(out/(case+'_REFERENCE_CROP.png')),cut)
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode('utf-8'),write_to=str(out/(name+'.png')),output_width=(x1-x0)*2,output_height=(y1-y0)*2)
        qa.append(dict(case=case,priority=priority,source=filename,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                       crop_source_px=crop,svg=str(s.relative_to(a.root)),segments=counts,
                       status='image-derived segmented linework, NOT independently curve fitted',
                       caveat='Text, labels, overlapping strokes may be included; gray axes and red alternatives are visual segmentation only.'))
    (out/'TRACE_QA.json').write_text(json.dumps(qa,indent=2))
    print('Produced',len(qa),'editable SVG plate traces')
if __name__=='__main__':main()
