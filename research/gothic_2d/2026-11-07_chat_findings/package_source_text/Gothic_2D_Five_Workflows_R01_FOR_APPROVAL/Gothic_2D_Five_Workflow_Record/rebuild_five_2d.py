#!/usr/bin/env python3
"""Experimental *new* analytic 2D drawings, not the original image-generation engine.
Produces five SVG geometry studies; does not overwrite or calibrate historical sources.
Uses only Python standard library. Coordinate convention: SVG pixels, Y down.
"""
import math
from pathlib import Path
import csv

OUT=Path(__file__).parent/'vector_experiments'; OUT.mkdir(exist_ok=True)
PI=math.pi

def xy(cx,cy,r,a):return (cx+r*math.cos(a),cy+r*math.sin(a))
def P(x,y):return f'{x:.4f},{y:.4f}'
def circle(cx,cy,r,kind='construction'):
    return f'<circle class="{kind}" cx="{cx:.4f}" cy="{cy:.4f}" r="{r:.4f}"/>'
def line(a,b,kind):return f'<line class="{kind}" x1="{a[0]:.4f}" y1="{a[1]:.4f}" x2="{b[0]:.4f}" y2="{b[1]:.4f}"/>'
def polypath(pts,cls='outline'):
    return f'<path class="{cls}" d="M '+ ' L '.join(P(*p) for p in pts)+' Z"/>'

def rosette(n,cx,cy,R,ring=False):
    """Lobes are arcs of n equally spaced radius-r circles.
    For adjacent circles choose the radially *outer* intersection as cusp.
    Radius r=1.18 R sin(pi/n) is a DESIGN PARAMETER, not historical evidence.
    """
    r=1.18*R*math.sin(PI/n)
    ctr=[xy(cx,cy,R,-PI/2+i*2*PI/n) for i in range(n)]
    # intersection of adjacent equal-radius circles, outer solution
    cusps=[]
    for i in range(n):
        a,b=ctr[i],ctr[(i+1)%n]; mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
        dx,dy=b[0]-a[0],b[1]-a[1]; d=math.hypot(dx,dy)
        assert d < 2*r
        h=math.sqrt(r*r-(d/2)**2)
        c1=(mx-dy/d*h,my+dx/d*h);c2=(mx+dy/d*h,my-dx/d*h)
        cusps.append(max((c1,c2),key=lambda c:math.hypot(c[0]-cx,c[1]-cy)))
    lines=[]
    for i in range(n):
        a=-PI/2+i*2*PI/n
        lines.append(line((cx,cy),xy(cx,cy,R+r+35,a),'axis'))
        lines.append(circle(*ctr[i],r))
        lines.append(f'<circle class="center" cx="{ctr[i][0]:.4f}" cy="{ctr[i][1]:.4f}" r="2.5"/>')
    # circle through center positions
    lines.append(circle(cx,cy,R))
    pts=[]
    for i in range(n):
        c=ctr[i]; start=cusps[(i-1)%n]; finish=cusps[i]
        a0=math.atan2(start[1]-c[1],start[0]-c[0]); a1=math.atan2(finish[1]-c[1],finish[0]-c[0]); outward=-PI/2+i*2*PI/n
        # choose angular span containing outward vector and less than full circle
        while a0>outward:a0-=2*PI
        while a1<a0:a1+=2*PI
        if not a0<=outward<=a1:
            a0,a1=a1-2*PI,a0
        pts.extend([xy(*c,r,a0+(a1-a0)*j/64) for j in range(65)])
    shapes=[polypath(pts)]
    if ring:
        tip=R+r; inner=tip+10; outer=inner+22
        shapes=[circle(cx,cy,inner,'outline'),circle(cx,cy,outer,'outline')]+shapes
    return lines,shapes,dict(n_lobes=n,center=[cx,cy],pitch_radius=R,lobe_radius=r,outermost_lobe_radius=R+r,ring_inner_radius=(R+r+10 if ring else None),ring_outer_radius=(R+r+32 if ring else None),cusps=cusps)

def arch(cx,base_y,halfspan,offset):
    """Two-centered equilateral pointed arch made from arcs centered at opposite springing points."""
    rise=math.sqrt(3)*halfspan
    def one(h):
        # left half, circle centered at right spring; right half centered left spring
        left=[];right=[]
        # left spring = (cx-h,base_y), apex=(cx,base_y-rise)
        for i in range(101):
            t=PI+(PI/3)*i/100 # left shoulder at pi, apex 4pi/3 -> y down is +? incorrect
        # source coordinate uses y down; left center at right, left spring is angle pi,
        # apex vector (-h,-sqrt(3)h) is 240 degrees = -120 degrees; span 180 -> 240 (positive y). 
        # use negative angles: pi -> 4pi/3 yields positive y, so take pi -> 2pi/3 yields negative y.
        for i in range(101):
            a=PI+(PI/3)*i/100
            left.append(xy(cx+h,base_y,2*h,a))
            a2=-PI/3+(PI/3)*i/100
            right.append(xy(cx-h,base_y,2*h,a2))
        return left+right
    parts=[]
    for h in (halfspan,halfspan+offset,halfspan+2*offset):
        pts=one(h)
        parts.append('<polyline class="outline" points="'+' '.join(P(*p) for p in pts)+'"/>')
        for x in (cx-h,cx+h):parts.append(line((x,base_y),(x,base_y+80),'outline'))
    parts.append(line((cx-halfspan-2*offset,base_y+80),(cx+halfspan+2*offset,base_y+80),'outline'))
    return parts

def render(i,n,ring,pointed):
    cx=500; cy=710 if pointed else 535
    R=140 if n==8 else (150 if n==6 else 160)
    guides,shapes,info=rosette(n,cx,cy,R,ring)
    if pointed:
        # maintain two-center arch geometrically; these are separate new-design units
        shapes += arch(cx,950,365,12)
    title=f'W{i:02d} • {n}-foil' + (' + outer ring' if ring else '') + (' + pointed arch' if pointed else '')
    style='''<style>
.outline{fill:none;stroke:#111;stroke-width:2.3;stroke-linejoin:round;stroke-linecap:round}
.axis{stroke:#aaa;stroke-width:0.8;stroke-dasharray:6 5}
.construction{fill:none;stroke:#111;stroke-width:0.9;stroke-dasharray:1 5;stroke-linecap:round}
.uncertain{fill:none;stroke:#c22;stroke-width:1;stroke-dasharray:7 5}
.center{fill:#111}
</style>'''
    s=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1100" width="1000" height="1100">\n<title>{title}</title>\n<desc>Experimental mathematical construction; not a traced historical artifact. Source pixel units, uncalibrated.</desc>\n{style}\n<rect width="1000" height="1100" fill="white"/>\n'
    s+='\n'.join(guides+shapes)+'\n</svg>\n'
    (OUT/f'W{i:02d}_experimental.svg').write_text(s)
    return info

def main():
    cases=[(1,4,False,False),(2,8,True,False),(3,6,True,False),(4,6,True,True),(5,8,True,True)]
    infos=[]
    for c in cases:infos.append(render(*c))
    with (OUT/'GEOMETRY_PARAMETERS.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['work','lobes','cx_px','cy_px','pitch_radius_px','lobe_radius_px','ring_inner_px','ring_outer_px'])
        for i,x in enumerate(infos,1):w.writerow([i,x['n_lobes'],*x['center'],f'{x["pitch_radius"]:.6f}',f'{x["lobe_radius"]:.6f}',x['ring_inner_radius'],x['ring_outer_radius']])
    print('Generated 5 experimental SVGs (not historic traces)')
if __name__=='__main__':main()
