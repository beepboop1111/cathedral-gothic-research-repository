#!/usr/bin/env python3
"""Figure 1236: read-only source-pixel 2D study, not cathedral geometry.
Derived from original crop supplied in Gothic_Tracery_New_Chat_Handoff.
Run: python reconstruct_1236.py --source /path/to/Ungewitter_1236_original_crop.png --out /path/to/folder
Requires PIL, numpy, scipy, cairosvg, V08 gothic_geometry.py and gothic_plate_reader.py.
"""
from __future__ import annotations
import argparse,csv,json,hashlib,math,sys,base64,xml.sax.saxutils as xsu
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

BASE=Path(__file__).resolve().parent
V08=BASE/'V08'
if V08.exists():sys.path.insert(0,str(V08))
from Gothic_V08_Project_Integration.gothic_geometry import circle_fit
from Gothic_V08_Project_Integration.gothic_plate_reader import inspect_plate

def arc_ink_fit(ink,name,seed,lo,hi,avoid_deg,rad_window=3,gray_cutoff=197):
    cx,cy,r=seed
    ts=np.deg2rad(np.arange(lo,hi,1.5))
    ts=ts[np.abs((np.rad2deg(ts)-avoid_deg+180)%360-180)>9]
    radii=np.arange(r-rad_window,r+rad_window+0.001,.25)
    xx=cx+np.cos(ts)[:,None]*radii
    yy=cy+np.sin(ts)[:,None]*radii
    values=map_coordinates(ink,[yy,xx],order=1,mode='constant',cval=255)
    ids=np.argmin(values,axis=1)
    accepted=values[np.arange(len(ts)),ids]<gray_cutoff
    P=np.c_[xx[np.arange(len(ts)),ids],yy[np.arange(len(ts)),ids]][accepted]
    for _ in range(3):
        obj=circle_fit(P)
        res=np.linalg.norm(P-np.array(obj.center),axis=1)-obj.radius
        deviations=np.abs(res-np.median(res))
        mask=deviations < max(1.35,2.2*np.median(deviations))
        if mask.sum()>=8:P=P[mask]
    obj=circle_fit(P)
    return {'name':name,'center':[round(x,5) for x in obj.center],
            'radius':round(obj.radius,5),'rmse_sampled_ink_px':round(obj.rmse,5),
            'n_samples':obj.n_points,'fit_span_deg':[lo,hi],
            'classification':'fitted_to_selected_historical_ink_not_verified_compass_intent'},P

def xings(a,b):
    A=np.array(a['center'],float);B=np.array(b['center'],float)
    r=float(a['radius']);s=float(b['radius']);v=B-A;d=np.linalg.norm(v)
    if d > r+s or d < abs(r-s):return []
    u=v/d;t=(r*r-s*s+d*d)/(2*d);h=max(0.,r*r-t*t)**.5
    mid=A+u*t;off=np.array([-u[1],u[0]])*h
    return [(mid+off).tolist(),(mid-off).tolist()]

def outer_intersection(circle_a,circle_b,approx):
    pts=xings(circle_a,circle_b)
    if not pts:raise ValueError('Missing circle intersection')
    return min(pts,key=lambda p:math.dist(p,approx))

def f(x):return f'{x:.3f}'
def xy(p):return f'{f(p[0])} {f(p[1])}'

def foil_path(circles):
    # circle order T,R,B,L; use intersections near the four historically visible cusps.
    T,R,B,L=circles
    UR=outer_intersection(T,R,[214,101] if T['radius']<45 else [223,92])
    LR=outer_intersection(R,B,[211,180] if R['radius']<45 else [221,191])
    LL=outer_intersection(B,L,[133,179] if B['radius']<45 else [123,190])
    UL=outer_intersection(L,T,[134,101] if L['radius']<45 else [123,91])
    pieces=[('top',T,UL,UR),('right',R,UR,LR),('bottom',B,LR,LL),('left',L,LL,UL)]
    segs=[]
    for name,c,p0,p1 in pieces:
        theta0=math.degrees(math.atan2(p0[1]-c['center'][1],p0[0]-c['center'][0]))
        theta1=math.degrees(math.atan2(p1[1]-c['center'][1],p1[0]-c['center'][0]))
        sweep=(theta1-theta0)%360
        segs.append({'name':name,'radius':c['radius'],'angle_deg':round(sweep,4),'from':[round(v,4) for v in p0],'to':[round(v,4) for v in p1], 'large_arc':int(sweep>180)})
    commands=[f'M {xy(UL)}']
    for seg in segs:
        rad=seg['radius'];p=seg['to'];commands.append(f'A {f(rad)} {f(rad)} 0 {seg["large_arc"]} 1 {xy(p)}')
    commands.append('Z')
    pts={'UL':UL,'UR':UR,'LR':LR,'LL':LL}
    return ' '.join(commands),segs,pts

def svg_style():
    return '''<style>
.background{fill:white}
.outline{fill:none;stroke:#0b0b0b;stroke-width:1.00;stroke-linecap:round;stroke-linejoin:round}
.outline-light{fill:none;stroke:#141414;stroke-width:.76;stroke-linecap:round;stroke-linejoin:round}
.major{fill:none;stroke:#090909;stroke-width:1.22;stroke-linejoin:round}
.axis{fill:none;stroke:#adb2b5;stroke-width:.48;stroke-dasharray:3.0 3.4}
.understudy{fill:none;stroke:#c2423a;stroke-width:.76;stroke-dasharray:3 3}
.historical-label{font-family:Georgia,'Times New Roman',serif;font-style:italic;font-size:8px;fill:#545454}
.dotted-circle{stroke:#111;fill:none;stroke-width:.54;stroke-dasharray:.4 3;stroke-linecap:round;opacity:.75}
.center-dot{fill:#444;stroke:none}
</style>'''

def axes():
    return '''<g id="dividing-axes" aria-label="Analytical guides, NOT historical ink">
      <path class="axis" d="M 174.2 0 L 174.2 338 M 20 141 L 337 141"/>
      <path class="axis" d="M 174 88.6 L 225.4 141.9 L 171.9 194.2 L 120.0 140.3 Z"/>
      <path class="axis" d="M 95 192 L 95 338 M 249 192 L 249 338"/>
    </g>'''

def manual_lines():
    # These are careful source-pixel *interpreted* outlines, not independent proven circles.
    # Limit to visible y=0..338; no completion outside the source crop.
    # For pointed arch, circle-like cubic profiles are manually anchored from the crop.
    parts=[
      ('pointed-enclosing-arch','major',[
       'M 10.0 338 L 10.0 249',
       'C 9.6 170, 47.8 77.6, 174.5 9.6',
       'C 296.1 77.4, 334.1 169.9, 333.6 249 L 333.6 338']),
      ('arch-inner-rail','outline',[
       'M 24.0 338 L 24.0 253 C 23.0 181, 63.0 94, 111.9 57.9',
       'M 331 338 L 331 253 C 330 182, 292 94, 237.2 58.1']),
      ('arch-shortest-rail','outline-light',[
       'M 37.0 338 L 37.0 260 C 37 213 46 179 61 141',
       'M 319 338 L 319 261 C 319 210 309 177 288 140']),
      # Small upper triangular spandrel frames visible between outer arch and fourfoil.
      ('top-left-spandrel','outline-light',['M 106.9 82.6 L 115.8 70.5 Q 114.4 82.7 125.2 91.0',
                                          'M 106.9 82.6 Q 115.0 78.8 115.8 70.5']),
      ('top-right-spandrel','outline-light',['M 239.5 82.2 L 232.9 69.2 Q 235.3 82.6 222.4 92.6',
                                           'M 239.5 82.2 Q 229.0 79.0 232.9 69.2']),
      ('lower-left-foil-strand','outline-light',[
          'M 123.0 189.7 L 112.1 198.2 L 122.4 193.8',
          'M 133.1 179.4 L 112.1 198.2',
          'M 122.4 193.8 L 147.0 207.2',
          'M 120.8 194.4 L 102.7 194.5']),
      ('lower-right-foil-strand','outline-light',[
          'M 221.4 191.1 L 231.7 199.1 L 222.4 193.1',
          'M 211.2 180.7 L 231.7 199.1',
          'M 221.4 193.5 L 202.7 209.5',
          'M 232.3 198.5 L 242.0 197.6']),
      ('left-buttress-band','outline-light',[
          'M 33.0 144 L 49.0 151 L 66.6 160',
          'M 41.5 149 L 49.0 151',
          'M 63.0 159 L 71.5 156']),
      ('right-buttress-band','outline-light',[
          'M 311.0 143 L 294.8 153 L 278 159',
          'M 302.0 148 L 294.8 153',
          'M 283 155 L 273 160']),
      # Two lower trefoils: ONLY portions actually inside the crop. Tips 3 rails each.
      ('lower-left-inner','outline',[
          'M 95.3 210.3 C 72.5 223.2 61.6 254.1 62.3 277.5',
          'M 95.3 210.3 C 116.1 221.1 125.7 252.3 124.7 278.6',
          'M 62.3 277.5 C 35.5 288.0 19.1 311 13.8 338',
          'M 124.7 278.6 C 149.8 290.8 161.9 314.0 165.6 338']),
      ('lower-left-middle','outline',[
          'M 95.3 201.7 C 68.2 215.6 51.8 250.2 52.7 275.4',
          'M 95.3 201.7 C 119.6 214.1 134.8 248.9 135.1 276.1',
          'M 52.7 275.4 C 27.1 288.5 12.8 314.6 9.9 338',
          'M 135.1 276.1 C 157.6 290 170.1 315 173.5 338']),
      ('lower-left-outer','outline-light',[
          'M 95.3 192.7 C 59.1 210.5 39.3 248.3 40.1 275.0',
          'M 95.3 192.7 C 128.7 210.5 146.2 246.8 147.2 275.0',
          'M 40.1 275 C 18.7 286.2 9.5 316.1 9.3 338',
          'M 147.2 275 C 170 285 180.7 308 184.3 338']),
      ('lower-right-inner','outline',[
          'M 248.4 210.0 C 228.1 221.7 219.9 252.3 219.0 278.4',
          'M 248.4 210.0 C 270.7 221.9 281.4 254.2 281.6 278.7',
          'M 219 278.4 C 194.6 291.0 182.0 314.8 177.1 338',
          'M 281.6 278.7 C 308 292 325.7 316 331.9 338']),
      ('lower-right-middle','outline',[
          'M 248.4 201.8 C 219.9 215.1 208.1 248.4 208.4 276.0',
          'M 248.4 201.8 C 275.5 214.0 291.2 249.4 290.8 277.8',
          'M 208.4 276 C 184.0 291.9 174.2 316.2 173.3 338',
          'M 290.8 277.8 C 316.7 292.5 330.8 315 332.8 338']),
      ('lower-right-outer','outline-light',[
          'M 248.4 193.6 C 212.1 211.6 195.6 247.8 195.2 276.6',
          'M 248.4 193.6 C 282.7 212.4 309.0 244.8 309.5 274.0',
          'M 195.2 276.6 C 180.6 284.4 174.0 294.7 174.0 305.0',
          'M 309.5 274.0 C 324 287.9 330.3 306.5 332.6 338']),
      # Central interstice, stops at printed crop boundary; dense curves kept local.
      ('central-spandrel','outline',[
          'M 151 252 C 157 256 168 256 175 256 C 184 256 190 256 194 252',
          'M 151 252 L 151 268 Q 163 277 174 291 Q 185 277 194 268 L 194 252',
          'M 146 265 Q 162 281 174 304 Q 188 282 200 266',
          'M 142 273 Q 163 288 174 315 Q 185 290 206 274']),
      ('junction-lines','outline-light',[
          'M 135 275 L 148 269 L 151 268',
          'M 194 268 L 208 276 L 219 278',
          'M 52.7 275.4 L 41 275',
          'M 290.8 277.8 L 309.5 274']),
    ]
    arr=[]
    for gid,cls,paths in parts:
        joined=' '.join(paths)
        arr.append(f'<g id="{gid}" class="{cls}"><path d="{xsu.escape(joined)}"/></g>')
    return '\n'.join(arr)

def labels():
    labels=[('c',173,7),('g',27,145),('f',316,144),('d',178,141),('p',216,182),('q',176,233),('s',51,163),('s',174,24),('t',229,220),('o',248,195),('r',248,220),('a',333,282),('b',26,280),('m',294,283),('u',61,105)]
    return '<g id="historical-mark-labels" aria-label="Provisional lettering locations, redrawn rather than original ink">'+''.join(f'<text class="historical-label" x="{x}" y="{y}">{ch}</text>' for ch,x,y in labels)+'</g>'

def circles_dotted(fits):
    parts=[]
    for c in fits:
        parts.append(f'<circle class="dotted-circle" cx="{f(c["center"][0])}" cy="{f(c["center"][1])}" r="{f(c["radius"])}"/>')
        parts.append(f'<circle class="center-dot" cx="{f(c["center"][0])}" cy="{f(c["center"][1])}" r=".95"/>')
    return '<g id="recovered-complete-circles" aria-label="Analytical compass-circle extensions: not original ink">'+''.join(parts)+'</g>'

def build_svg(fits,view='clean',source_png=None):
    inn=fits[:4];out=fits[4:]
    inner_path,inner_segs,inner_cusps=foil_path(inn)
    outer_path,outer_segs,outer_cusps=foil_path(out)
    hdr=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" viewBox="0 0 355 338" width="1065" height="1014" role="img" aria-label="Two-dimensional reconstruction of Ungewitter figure 1236, clipped to supplied source extent">
<title>Ungewitter figure 1236: measured central quatrefoil and source-limited window tracery</title>
<desc>Black curves include 8 V08 ink-fitted quatrefoil arcs and provisional manually interpreted lower and frame curves. Pale gray dashed guides are analytical axes. Provisional contours are not validated geometric constructions. Source pixel coordinates, not architectural dimensions.</desc>
{svg_style()}
<defs><clipPath id="crop"><rect x="0" y="0" width="355" height="338"/></clipPath></defs>'''
    if view=='comparison':
        png_data=base64.b64encode(Path(source_png).read_bytes()).decode('ascii')
        bg=f'<image x="0" y="0" width="355" height="338" xlink:href="data:image/png;base64,{png_data}" opacity=".70"/>'
    else:bg='<rect class="background" width="355" height="338"/>'
    all_=[]
    all_.append(hdr);all_.append(bg);all_.append('<g clip-path="url(#crop)">')
    if view=='analytic':all_.append(circles_dotted(fits))
    all_.append(axes())
    all_.append('<g id="provisional-manual-contours" aria-label="Manually placed source-looking contours not geometrically validated">'+manual_lines()+'</g>')
    all_.append('<g id="v08-fitted-quatrefoil-outer" class="outline"><path d="'+outer_path+'"/></g>')
    all_.append('<g id="v08-fitted-quatrefoil-inner" class="major"><path d="'+inner_path+'"/></g>')
    if view=='analytic':
        # Red dashed segments of *uncertain* contact continuations between foil and lower trefoil;
        # not a claim that the following diagonals appear in the historical print.
        all_.append('<g id="unverified-candidate-tangent-connectors" class="understudy"><path d="M 122.6 189.8 L 95.3 192.7 M 221.4 191.1 L 248.4 193.6"/></g>')
    all_.append(labels())
    all_.append('</g></svg>')
    return '\n'.join(all_),{'inner':{'cusps':inner_cusps,'arcs':inner_segs},'outer':{'cusps':outer_cusps,'arcs':outer_segs}}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',required=True)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    source=Path(args.source);out=Path(args.out);out.mkdir(exist_ok=True,parents=True)
    rgb=Image.open(source); ink=np.asarray(rgb.convert('L'),dtype=float)
    assert rgb.size==(355,338),'New crop must be re-registered and remeasured'
    meta=inspect_plate(source)
    definitions=[
      ('inner_top',(174,90,43),194,346,270),
      ('inner_right',(227,139,40),-69,69,0),
      ('inner_bottom',(172,195,41),18,162,90),
      ('inner_left',(119,139,40.5),111,249,180),
      ('outer_top',(174,90,51),197,343,270),
      ('outer_right',(227,139,48),-69,69,0),
      ('outer_bottom',(172,195,49),20,160,90),
      ('outer_left',(119,139,48.5),111,249,180),
    ]
    fits=[];samples=[]
    for name,seed,lo,hi,avoid in definitions:
        obj,P=arc_ink_fit(ink,name,seed,lo,hi,avoid)
        fits.append(obj)
        for x,y in P:samples.append({'contour':name,'sample_x_px':round(float(x),4),'sample_y_px':round(float(y),4)})
    for v in ('clean','comparison','analytic'):
        body,shapes=build_svg(fits,view=v,source_png=source)
        (out/f'FIG1236_{v.upper()}.svg').write_text(body,encoding='utf8')
    try:
        import cairosvg
        for name in ('CLEAN','COMPARISON','ANALYTIC'):
            cairosvg.svg2png(url=str(out/f'FIG1236_{name}.svg'),write_to=str(out/f'FIG1236_{name}.png'),output_width=1420,output_height=1352)
    except Exception as e: print('SVG files created; raster rendering failed:',repr(e))
    with (out/'FIG1236_CIRCULAR_FITS.csv').open('w',newline='',encoding='utf8') as fcsv:
        writer=csv.DictWriter(fcsv,fieldnames=['contour','center_x_px','center_y_px','radius_px','sample_rmse_px','n_samples','interpretation']);writer.writeheader()
        for z in fits: writer.writerow({'contour':z['name'],'center_x_px':z['center'][0],'center_y_px':z['center'][1],
            'radius_px':z['radius'],'sample_rmse_px':z['rmse_sampled_ink_px'],
            'n_samples':z['n_samples'],'interpretation':z['classification']})
    with (out/'FIG1236_SELECTED_INK_POINTS.csv').open('w',newline='',encoding='utf8') as fcsv:
        writer=csv.DictWriter(fcsv,fieldnames=['contour','sample_x_px','sample_y_px']);writer.writeheader();writer.writerows(samples)
    def near(pt,ref):return round(math.dist(pt,ref),3)
    refs={'inner':{'UL':[134,101],'UR':[214,102],'LR':[211,180],'LL':[133,179]},
          'outer':{'UL':[123,91],'UR':[223,92],'LR':[221,191],'LL':[123,190]}}
    errors={k:{name:near(pts,refs[k][name]) for name,pts in shapes[k]['cusps'].items()} for k in refs}
    qa={'case':'Ungewitter Vol II (1892) Plate CXX figure 1236',
        'source':meta,'source_file_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'crop_extent':'355×338 pixels, bottom openings cut off by the supplied crop',
        'source_verified_as':'user-supplied image, original scan not modified',
        'source_units':'pixels, X right, Y down; no physical scale or F5ZP architectural units',
        'fit_algorithm':'V08 gothic_geometry.circle_fit, selected radial-local darkest scanline samples, robust median residual rejection, angular sector masks',
        'ink_fit_error_note':'RMS of selected source pixels to fitted circle; sampling was constrained near a candidate. This is not independent full-contour image error and not proof of exact historical compass geometry.',
        'circle_fits':fits,'recovered_foils':shapes,
        'human_read_cusp_references':refs,'crossing_to_manual_reference_distances_px':errors,
        'points_n':len(samples),
        'uncertain_contours':'pointed enclosing arch, lower trefoil fragments, decorative spandrels and labels were manually reconstructed from the 355x338 crop; they were NOT verified with independent circle fits.',
        'axes_status':'gray analytical guides, not certified historical marks',
        'recovered_full_circles_status':'drawn as optional black dotted analytical extensions; not present in full as source ink',
        'legacy_generator_changes':False,'cathedral_geometry_changes':False,'dimension_locks_changed':False,
        '3d_work':False,
        'historical_text_provenance':'Ungewitter–Mohrmann, 1892, Vol. II, printed p. 517, figure 1236, Plate CXX. Book method described in RESEARCH_NOTES.md.'}
    (out/'FIG1236_QA.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print('Reconstructed 2D geometry',len(fits),'arcs;',len(samples),'ink samples;')
    print('Crop',rgb.size,'sha256',qa['source_file_sha256'])
    for z in fits:print(z['name'],tuple(z['center']),z['radius'],z['rmse_sampled_ink_px'])
    print('Manual-reference cusp distances:',errors)

if __name__=='__main__':main()
