#!/usr/bin/env python3
"""Last attached four-circle construction, exact geometry study.

Reference coordinates are estimated from displayed image ink and labeled
points; revise them after independent source-curve fitting. No medieval
construction attribution and no scale conversion.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import json, math, argparse
import numpy as np
import cairosvg

# Center and midpoint coordinates estimated manually from this 1190x1006 image.
CENTER = np.array([562.5,503.5],float)
C = {
 'K':(407.5,348.5),'I':(717.5,348.5),
 'H':(407.5,658.5),'J':(717.5,658.5),
}
# Horizontal center spacing 310, vertical spacing 310: exact nominal square.
# Nominal radius = half center pitch, NOT blindly asserted measured radius.
R = 155.0
OUTER_R = 375.0

def circle_intersections(c0,r0,c1,r1,tol=1e-8):
    a=np.array(c0,float);b=np.array(c1,float);d=float(np.linalg.norm(b-a))
    if d<tol or d>r0+r1+tol or d<abs(r0-r1)-tol:return []
    x=(r0*r0-r1*r1+d*d)/(2*d)
    h2=max(0.,r0*r0-x*x)
    mid=a+x*(b-a)/d
    q=np.array([-(b-a)[1],(b-a)[0]])/d*math.sqrt(h2)
    if np.linalg.norm(q)<tol:return [mid.tolist()]
    return [(mid+q).tolist(),(mid-q).tolist()]

def polylines_xml():
    # Black source-faithful curves are in the vector trace. For this analytical
    # study, use only major arc SEGMENTS of each of the four circles, staying
    # within the outer construction disk. Shown dark, never as measured ink.
    lines=[]
    # visually external semicircular petal arcs centered K/I/H/J
    for key,(x,y) in C.items():
        if key=='K':start,end=135,450 # except inner directions? shown full arc for analysis
        elif key=='I':start,end=-90,225
        elif key=='H':start,end=45,360
        else:start,end=-180,135
        # Use full circles separately; avoid pretending these arc limits are source fit
    return lines

def build(root):
    out=root/'outputs';out.mkdir(exist_ok=True)
    x0,y0,w,h=90,78,900,856
    stroke='.95'
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x0} {y0} {w} {h}">',
       '<rect x="0" y="0" width="1190" height="1006" fill="white"/>',
       '<title>Four-circle square construction — analytical comparison</title>',
       '<desc>Nominal construction, estimated from uploaded screenshot. Not a fitted historical source.</desc>',
       '<g id="DIVIDING_AXES" fill="none" stroke="#c5c5c5" stroke-width="1" stroke-dasharray="5 5">',
       f'<path d="M {CENTER[0]} 110 V 895 M 175 {CENTER[1]} H 970"/>',
       '</g>',
       '<g id="FULL_DOTTED_CONSTRUCTION_CIRCLES" fill="none" stroke="black" stroke-width="1.4" stroke-dasharray="2.5 5.5">']
    for x,y in C.values():s.append(f'<circle cx="{x}" cy="{y}" r="{R}"/>')
    s.append(f'<circle cx="{CENTER[0]}" cy="{CENTER[1]}" r="{OUTER_R}"/>')
    s+=['</g>','<g id="CENTER_POLYGON" stroke="#aeb1b3" fill="none" stroke-width="1.2" stroke-dasharray="7 5">',
        '<path d="M 407.5 348.5 L 717.5 348.5 L 717.5 658.5 L 407.5 658.5 Z"/>',
        '<path d="M 407.5 348.5 L 717.5 658.5 M 717.5 348.5 L 407.5 658.5"/>','</g>',
        '<g id="CIRCLE_CENTERS" fill="#19a13c" stroke="#096b21" stroke-width="1">']
    for label,(x,y) in C.items():s.append(f'<circle cx="{x}" cy="{y}" r="4"/>')
    s.append(f'<circle cx="{CENTER[0]}" cy="{CENTER[1]}" r="4"/>')
    s+=['</g>','<g id="INTERSECTIONS" fill="#df2626" stroke="#a80000" stroke-width="1">']
    pts=[]
    for left,right in [('K','I'),('I','J'),('J','H'),('H','K')]:
        for point in circle_intersections(C[left],R,C[right],R):
            pts.append({'circles':[left,right],'point':point})
            s.append(f'<circle cx="{point[0]}" cy="{point[1]}" r="4"/>')
    s+=['</g>','<g id="LABELS" font-family="sans-serif" fill="#444" font-size="16">']
    for label,(x,y) in C.items():s.append(f'<text x="{x+8}" y="{y-9}">{escape(label)}</text>')
    s+=['<text x="571" y="492">A</text>','</g>','</svg>']
    svg='\n'.join(s)
    (out/'FOUR_CIRCLE_ANALYTICAL.svg').write_text(svg)
    cairosvg.svg2png(bytestring=svg.encode(),write_to=str(out/'FOUR_CIRCLE_ANALYTICAL.png'),output_width=1200,output_height=1141)
    centers=np.array(list(C.values()),float)
    edges=np.linalg.norm(np.roll(centers,-1,axis=0)-centers,axis=1) # order K I H J is NOT perimeter!
    poly=np.array([C[k] for k in ['K','I','J','H']],float)
    sides=np.linalg.norm(np.roll(poly,-1,axis=0)-poly,axis=1)
    report={'case':'LAST_UPLOADED_FOUR_CIRCLE','priority':'HIGH',
            'geometry_status':'provisional nominal circle construction from displayed screenshot, not independent pixel fit',
            'centers_source_px':C,'main_center_source_px':CENTER.tolist(),
            'nominal_lobe_radius_px':R,'nominal_outer_radius_px':OUTER_R,
            'center_square_side_lengths_px':sides.tolist(),
            'center_square_side_length_max_spread_px':float(np.ptp(sides)),
            'intersections_between_adjacent_lobes':pts,
            'center_to_outer_circle_diagonal_point_distance_px':float(np.linalg.norm(np.array([298,237])-CENTER)),
            'outer_circle_nominal_difference_at_upper_left_diagonal_px':float(np.linalg.norm(np.array([298,237])-CENTER)-OUTER_R),
            'two_circle_tangency_predicted':True,
            'angle_degrees':90,'scale':'source screenshot pixels only',
            'not_verified':'Outermost and four lobe circles need systematic fitting to source pixels before historical claims; analytical construction is a controlled hypothesis.'}
    (out/'FOUR_CIRCLE_GEOMETRY.json').write_text(json.dumps(report,indent=2))
    print('Analytical last-figure geometry generated; square sides',sides)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args();build(a.root)
