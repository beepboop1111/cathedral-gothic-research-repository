#!/usr/bin/env python3
"""
Pass 6J — R1 @ 78° French Gothic compound-pier springing set-out.

LOCKED INPUTS
-------------
* Pass 6J radii: R0=2933, R1=4181, R2=4901, R3=5957
* Springing plane: Y=3000
* Representative pier: R1 @ 78°
* Four diagonal-ogive bearings point to the locked Pass 6J inner/middle bosses.
* Four stronger major-arch bearings come directly from the locked plan network:
  radial to R0/R2 and chordal along R1 to the adjacent 54°/102° boundaries.

HISTORICAL PROFILE FAMILY
-------------------------
S1 = stronger mature-mid-13th-c. doubleau profile family, normalized from the
     Sainte-Chapelle A profile recorded by Viollet-le-Duc (fig. 41).
S2 = lighter matching ogive family, normalized from the Sainte-Chapelle B
     profile in the same figure.

This file intentionally DOES NOT calculate generic bayframe arches and DOES NOT
re-use the old fan-shaped springing experiment.  The height slices below are a
local tas-de-charge / projection set-out only: they show how the eight actual
section bearings overlap and begin to release from a common springing mass.
They are not substitute arch centerlines.  The four ogive centerlines remain
subject to the locked Pass 6J guide when the 3-D sweep is attached.

The source engraving is not dimensioned.  Therefore absolute profile size is a
project scaling decision; SHAPE_SCALE below is explicit and easy to change.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from itertools import combinations
from pathlib import Path

from shapely.affinity import rotate, scale, translate
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

RINGS = {"R0":2933.0, "R1":4181.0, "R2":4901.0, "R3":5957.0}
SPRING_Y = 3000.0
PIER_RING = "R1"
PIER_ANGLE_DEG = 78.0
# A conservative first physical size.  At 0.75:
# S1 ≈ 84 wide x 73.5 deep; S2 ≈ 40.5 wide x 57.75 deep.
SHAPE_SCALE = 0.75

# Locked Pass 6J bosses needed by the R1/78 representative pier.
BOSSES = {
    "inner_B3": (1415.15, 3178.47),
    "inner_B4": (0.00, 3479.27),
    "middle_B3": (1806.63, 4057.76),
    "middle_B4": (0.00, 4441.77),
}

# Diagnostic slice schedule only — not arch curves.
# (height above Y=3000, outward release along each actual bearing)
SLICE_RELEASE = [
    (0.0,   0.0),
    (40.0,  0.0),
    (80.0,  6.0),
    (120.0, 14.0),
    (160.0, 24.0),
    (220.0, 35.0),
    (300.0, 45.0),
    (400.0, 60.0),
]


def ring_point(ring: str, angle_deg: float):
    r=RINGS[ring]
    a=math.radians(angle_deg)
    return (r*math.cos(a), r*math.sin(a))


def bearing_deg(p0, p1):
    return math.degrees(math.atan2(p1[1]-p0[1], p1[0]-p0[0])) % 360.0


def raw_S1_doubleau():
    """Dimensionless multi-order/tori-and-gorges reconstruction of VLD fig.41 A.

    local x = lateral width; local y = direction toward the supported arch.
    """
    parts = [
        box(-52,-18,52,8),
        Point(-40,10).buffer(16,resolution=64),
        Point( 40,10).buffer(16,resolution=64),
        box(-35,4,35,21),
        Point(-25,28).buffer(17,resolution=64),
        Point( 25,28).buffer(17,resolution=64),
        box(-15,18,15,48),
        Point(0,50).buffer(24,resolution=64),
        Polygon([(-6,70),(6,70),(0,80)]),
    ]
    return unary_union(parts).buffer(0)


def raw_S2_ogive():
    """Dimensionless lighter one-course/pear-rib reconstruction of VLD fig.41 B."""
    parts = [
        box(-26,-14,26,9),
        Point(-16,10).buffer(11,resolution=64),
        Point( 16,10).buffer(11,resolution=64),
        box(-13,6,13,35),
        Point(0,34).buffer(21,resolution=64),
        Polygon([(-6,51),(6,51),(0,63)]),
    ]
    return unary_union(parts).buffer(0)


def profiles(shape_scale=SHAPE_SCALE):
    return {
        "S1": scale(raw_S1_doubleau(), xfact=shape_scale, yfact=shape_scale, origin=(0,0)),
        "S2": scale(raw_S2_ogive(), xfact=shape_scale, yfact=shape_scale, origin=(0,0)),
    }


def members():
    c=ring_point("R1",PIER_ANGLE_DEG)
    targets = [
        # Four lighter locked diagonal-ogive responses.
        ("O1_inner_B3", "ogive", "S2", BOSSES["inner_B3"], "locked inner bay 3 boss"),
        ("O2_inner_B4", "ogive", "S2", BOSSES["inner_B4"], "locked inner bay 4 boss"),
        ("O3_middle_B3","ogive", "S2", BOSSES["middle_B3"],"locked middle bay 3 boss"),
        ("O4_middle_B4","ogive", "S2", BOSSES["middle_B4"],"locked middle bay 4 boss"),
        # Four stronger major-arch responses from the locked plan network.
        ("M1_transverse_inner", "major", "S1", ring_point("R0",78.0), "radial R1 -> R0 @ 78°"),
        ("M2_transverse_middle","major", "S1", ring_point("R2",78.0), "radial R1 -> R2 @ 78°"),
        ("M3_longitudinal_prev", "major", "S1", ring_point("R1",54.0), "R1 chord to previous 54° boundary"),
        ("M4_longitudinal_next", "major", "S1", ring_point("R1",102.0),"R1 chord to next 102° boundary"),
    ]
    out=[]
    for name,kind,profile,target,source in targets:
        out.append({
            "name":name,"kind":kind,"profile":profile,
            "bearing_deg":bearing_deg(c,target),
            "target_x":float(target[0]),"target_z":float(target[1]),
            "source":source,
        })
    return c,out


def orient_profile(poly, bearing, release=0.0):
    # Canonical profile +local-y nose points toward its supported arch.
    p=rotate(poly, bearing-90.0, origin=(0,0), use_radians=False)
    a=math.radians(bearing)
    return translate(p, xoff=release*math.cos(a), yoff=release*math.sin(a))


def central_overlap_core(placed):
    """Core derived AFTER profile overlay: region covered by >=2 sections."""
    pairs=[]
    for a,b in combinations(placed,2):
        q=a.intersection(b)
        if not q.is_empty:
            pairs.append(q)
    if not pairs:
        return None
    ov=unary_union(pairs).buffer(0)
    origin=Point(0,0)
    if ov.geom_type == "Polygon":
        return ov
    candidates=[g for g in ov.geoms if g.distance(origin)<1e-7]
    return max(candidates,key=lambda g:g.area) if candidates else max(ov.geoms,key=lambda g:g.area)


def geom_paths(g):
    if g is None or g.is_empty:
        return []
    polys=[g] if g.geom_type=="Polygon" else list(g.geoms)
    out=[]
    for p in polys:
        out.append(list(p.exterior.coords))
        for ring in p.interiors:
            out.append(list(ring.coords))
    return out


def svg_path(coords, scale_px, ox, oy):
    pts=[]
    for x,y in coords:
        X=ox+x*scale_px
        Y=oy-y*scale_px
        pts.append((X,Y))
    if not pts: return ""
    s=f"M {pts[0][0]:.2f},{pts[0][1]:.2f} "
    s += " ".join(f"L {x:.2f},{y:.2f}" for x,y in pts[1:])
    return s+" Z"


def write_profile_svg(path, poly, title):
    minx,miny,maxx,maxy=poly.bounds
    pad=12
    px=5.0
    w=(maxx-minx)*px+2*pad
    h=(maxy-miny)*px+2*pad
    ox=pad-minx*px
    oy=pad+maxy*px
    d=svg_path(list(poly.exterior.coords),px,ox,oy)
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.2f} {h:.2f}">
<title>{title}</title><rect width="100%" height="100%" fill="white"/>
<path d="{d}" fill="black" stroke="black" stroke-width="1"/>
</svg>''')


def write_profile_png(path, poly, ppb=14, rotate_for_sweep=False):
    from PIL import Image, ImageDraw
    p=rotate(poly,-90,origin=(0,0),use_radians=False) if rotate_for_sweep else poly
    minx,miny,maxx,maxy=p.bounds
    margin=2.0
    W=max(16,int(math.ceil((maxx-minx+2*margin)*ppb)))
    H=max(16,int(math.ceil((maxy-miny+2*margin)*ppb)))
    im=Image.new("L",(W,H),255)
    dr=ImageDraw.Draw(im)
    pts=[]
    for x,y in p.exterior.coords:
        X=(x-minx+margin)*ppb
        Y=(maxy-y+margin)*ppb
        pts.append((X,Y))
    dr.polygon(pts,fill=0)
    im.save(path)


def write_slice_svg(path, y_world, release, placed, core, members_data):
    allg=unary_union(placed)
    minx,miny,maxx,maxy=allg.bounds
    pad_blocks=28
    minx-=pad_blocks; miny-=pad_blocks; maxx+=pad_blocks; maxy+=pad_blocks
    px=3.2
    w=(maxx-minx)*px; h=(maxy-miny)*px
    ox=-minx*px; oy=maxy*px
    lines=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.2f} {h:.2f}">',
           f'<title>Pass 6J R1@78 compound pier slice Y={y_world:g}</title>',
           '<rect width="100%" height="100%" fill="white"/>']
    # Derived overlap core first.
    if core is not None:
        for coords in geom_paths(core):
            lines.append(f'<path d="{svg_path(coords,px,ox,oy)}" fill="#dddddd" stroke="none"/>')
    # Profiles: major thicker stroke than ogive; no artificial circles.
    for m,g in zip(members_data,placed):
        sw=2.0 if m['kind']=='major' else 1.25
        dash='' if m['kind']=='major' else ' stroke-dasharray="6,3"'
        for coords in geom_paths(g):
            lines.append(f'<path d="{svg_path(coords,px,ox,oy)}" fill="none" stroke="black" stroke-width="{sw}"{dash}/>' )
    # Pier center and bearing rays.
    cx,cy=ox,oy
    lines.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="3" fill="black"/>')
    ray=20.0
    for m in members_data:
        a=math.radians(m['bearing_deg'])
        x2=cx+ray*px*math.cos(a); y2=cy-ray*px*math.sin(a)
        sw=1.0 if m['kind']=='major' else 0.7
        lines.append(f'<line x1="{cx:.2f}" y1="{cy:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#666" stroke-width="{sw}"/>')
    lines.append(f'<text x="10" y="20" font-family="monospace" font-size="14">Y={y_world:g}  release={release:g}</text>')
    lines.append('</svg>')
    path.write_text('\n'.join(lines))


def svg_to_png(svg_path, png_path):
    # CairoSVG is optional. If absent, use cairosvg if installed; otherwise skip.
    try:
        import cairosvg
        cairosvg.svg2png(url=str(svg_path),write_to=str(png_path),output_width=900)
        return True
    except Exception:
        return False


def write_dxf(outpath, slices, members_data):
    try:
        import ezdxf
    except Exception:
        return False
    doc=ezdxf.new("R2010")
    msp=doc.modelspace()
    for y_world,release,placed,core in slices:
        lname=f"Y{int(round(y_world))}"
        if lname not in doc.layers:
            doc.layers.add(lname)
        for m,g in zip(members_data,placed):
            for coords in geom_paths(g):
                msp.add_lwpolyline([(x,z) for x,z in coords],close=True,dxfattribs={"layer":lname})
        if core is not None:
            cl=lname+"_CORE"
            if cl not in doc.layers: doc.layers.add(cl)
            for coords in geom_paths(core):
                msp.add_lwpolyline([(x,z) for x,z in coords],close=True,dxfattribs={"layer":cl})
    doc.saveas(outpath)
    return True


def make_contact_sheet(pngs, output):
    from PIL import Image, ImageOps, ImageDraw
    ims=[Image.open(p).convert("RGB") for p in pngs if p.exists()]
    if not ims: return False
    thumb=540
    cells=[]
    for im in ims:
        im.thumbnail((thumb,thumb))
        cell=Image.new("RGB",(thumb,thumb),"white")
        cell.paste(im,((thumb-im.width)//2,(thumb-im.height)//2))
        cells.append(cell)
    cols=2; rows=math.ceil(len(cells)/cols)
    sheet=Image.new("RGB",(cols*thumb,rows*thumb),"white")
    for i,im in enumerate(cells):
        sheet.paste(im,((i%cols)*thumb,(i//cols)*thumb))
    sheet.save(output,quality=95)
    return True


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',default='out/pass6J_R1_78_french_pier')
    ap.add_argument('--shape-scale',type=float,default=SHAPE_SCALE)
    ap.add_argument('--ppb',type=float,default=14.0,help='pixels per block for sweep-input PNGs')
    args=ap.parse_args()
    out=Path(args.out).expanduser().resolve(); out.mkdir(parents=True,exist_ok=True)
    prof=profiles(args.shape_scale)
    center,mem=members()

    # Profile assets.
    write_profile_svg(out/'S1_DOUBLEAU_plan.svg',prof['S1'],'S1 mature French Gothic doubleau — normalized VLD fig.41 A')
    write_profile_svg(out/'S2_OGIVE_plan.svg',prof['S2'],'S2 mature French Gothic ogive — normalized VLD fig.41 B')
    write_profile_png(out/'S1_DOUBLEAU_plan.png',prof['S1'],ppb=6)
    write_profile_png(out/'S2_OGIVE_plan.png',prof['S2'],ppb=6)
    # Current Pass6J sweep script rotates +90° by default; these are pre-rotated inputs.
    write_profile_png(out/'S1_DOUBLEAU_sweep_input.png',prof['S1'],ppb=args.ppb,rotate_for_sweep=True)
    write_profile_png(out/'S2_OGIVE_sweep_input.png',prof['S2'],ppb=args.ppb,rotate_for_sweep=True)

    # Bearing table.
    fields=['name','kind','profile','bearing_deg','target_x','target_z','source']
    with (out/'pass6J_R1_78_bearings.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for m in sorted(mem,key=lambda q:q['bearing_deg']):
            row=m.copy(); row['bearing_deg']=f"{row['bearing_deg']:.9f}"; row['target_x']=f"{row['target_x']:.6f}"; row['target_z']=f"{row['target_z']:.6f}"; w.writerow(row)

    # Slices, keeping local plan coordinates relative to actual R1/78 pier center.
    slices=[]; pngs=[]
    slice_dir=out/'slices'; slice_dir.mkdir(exist_ok=True)
    for rise,release in SLICE_RELEASE:
        placed=[orient_profile(prof[m['profile']],m['bearing_deg'],release) for m in mem]
        core=central_overlap_core(placed)
        y_world=SPRING_Y+rise
        slices.append((y_world,release,placed,core))
        svg=slice_dir/f'R1_78_Y{int(y_world)}.svg'
        png=slice_dir/f'R1_78_Y{int(y_world)}.png'
        write_slice_svg(svg,y_world,release,placed,core,mem)
        if svg_to_png(svg,png): pngs.append(png)

    write_dxf(out/'pass6J_R1_78_slices.dxf',slices,mem)
    make_contact_sheet(pngs,out/'pass6J_R1_78_slice_sheet.png')

    # Geometry metadata.
    b1=prof['S1'].bounds; b2=prof['S2'].bounds
    meta={
        'pier_center_global': {'x':center[0],'y':SPRING_Y,'z':center[1]},
        'pier_ring':'R1','pier_angle_deg':PIER_ANGLE_DEG,
        'shape_scale':args.shape_scale,
        'S1_doubleau_dimensions_blocks': {'width':b1[2]-b1[0],'depth':b1[3]-b1[1]},
        'S2_ogive_dimensions_blocks': {'width':b2[2]-b2[0],'depth':b2[3]-b2[1]},
        'slice_release': [{'y':SPRING_Y+r,'rise':r,'release':s} for r,s in SLICE_RELEASE],
        'note':'Slice release is a tas-de-charge set-out diagnostic only; it is not a replacement for locked Pass 6J arch/rib centerlines.'
    }
    (out/'geometry_metadata.json').write_text(json.dumps(meta,indent=2))

    readme=f"""PASS 6J — FIRST FRENCH GOTHIC COMPOUND PIER\n\nRepresentative pier\n  R1 @ 78 degrees\n  global center = X {center[0]:.6f}, Y {SPRING_Y:.3f}, Z {center[1]:.6f}\n\nProfile choice\n  S1 = stronger mature-mid-13th-century doubleau family (Viollet-le-Duc, Sainte-Chapelle fig. 41 A)\n  S2 = lighter matching ogive family (same figure, B)\n  The engraving has no construction scale; these are normalized source-family reconstructions, not claimed archaeological measurements.\n\nCurrent project scale\n  S1 = {b1[2]-b1[0]:.3f} wide x {b1[3]-b1[1]:.3f} deep blocks\n  S2 = {b2[2]-b2[0]:.3f} wide x {b2[3]-b2[1]:.3f} deep blocks\n\nWhat is locked\n  - Pass 6J radii and R1/78 pier center\n  - four diagonal bearings to the actual inner/middle Pass 6J bosses\n  - two radial and two adjacent-ring/chord major-arch bearings\n  - Y=3000 springing datum\n\nWhat is NOT locked yet\n  - absolute S1/S2 profile scale\n  - exact tas-de-charge course heights/release distances\n  - final derived pier shaft/core below Y=3000\n  - base/plinth\n\nImportant\n  This package does NOT use the old fan-shaped springing experiment and does NOT calculate generic bayframe arches.\n  The slices are top-down projection/set-out studies only.  Once approved, attach S2 to the locked Pass 6J diagonal paths and derive the major-arch paths from the locked web/structural boundaries before building the final 3-D springing mass.\n\nFiles\n  S1_DOUBLEAU_plan.svg/png\n  S2_OGIVE_plan.svg/png\n  S1_DOUBLEAU_sweep_input.png\n  S2_OGIVE_sweep_input.png\n  pass6J_R1_78_bearings.csv\n  pass6J_R1_78_slice_sheet.png\n  slices/*.svg + *.png\n  pass6J_R1_78_slices.dxf\n  geometry_metadata.json\n"""
    (out/'README.txt').write_text(readme)
    print(readme)
    print('output:',out)

if __name__=='__main__':
    main()