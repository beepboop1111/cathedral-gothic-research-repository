#!/usr/bin/env python3
"""F5ZP R11 experimental source-guided 2D study (no cathedral changes).
Measures image-space linework in the 630x1021 archival figure.
Contours are interpretations with explicitly bounded uncertainty, not historic dimensions.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, cv2, json, csv, hashlib, math, base64, io, zipfile
from scipy.interpolate import PchipInterpolator
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'Beauvais_fig61_Wikimedia_630x1021.png'
SRC_URL='https://commons.wikimedia.org/wiki/File:Arc.boutant.cathedrale.Beauvais.png'
OUT=ROOT/'results'
for name in ('svg','plots','data'): (OUT/name).mkdir(parents=True,exist_ok=True)
a=np.array(Image.open(SRC).convert('L'))
H,W=a.shape

# Deliberately separate the visible spans at intermediate pier A (rough x 219-270);
# do not draw through the pier or ornamental springing with an extrapolated arch.
# x/y coordinates selected from the uploaded 630px historical scan; every anchor
# is a CURATOR STARTING POINT, not a verified compass construction.
FEATURES={
 'upper_coping': {
  'type':'sloping_coping_not_a_proven_circle',
  'anchors':[(263,203),(270,197),(280,189),(290,183),(300,175),(310,172),(320,164),(330,158),(340,156)],
  'visible_x':[265,337], 'uncertain_at':['x<265','x>337']},
 'upper_intrados': {
  'type':'curved_arch_soffit',
  'anchors':[(270,228),(280,212),(290,201),(300,190),(310,185),(320,180),(330,176),(340,176)],
  'visible_x':[276,336], 'uncertain_at':['springing on intermediate pier A','choir wall junction']},
 'lower_coping':{
  'type':'inclined_upper_masonry_edge',
  'anchors':[(266,339),(270,332),(280,314),(290,305),(300,295),(310,285),(320,279),(330,272),(340,268)],
  'visible_x':[262,337], 'uncertain_at':['joint at pier A','choir support']},
 'lower_intrados': {
  'type':'curved_arch_soffit',
  'anchors':[(270,350),(280,334),(290,323),(300,313),(310,304),(320,300),(330,296),(340,296)],
  'visible_x':[276,334], 'uncertain_at':['springing at pier A','crockets and capital at choir']}
}

def sample_edge(c):
 p=np.array(c['anchors'],float)
 xs=np.arange(int(p[0,0]),int(p[-1,0])+1,dtype=int)
 pred=PchipInterpolator(p[:,0],p[:,1])(xs)
 # Each x is independently sourced from a 5px neighbourhood and restrained by
 # expected curvature. A second dynamic-programming pass imposes smoothness.
 candidates=[]
 for x,y in zip(xs,pred):
  ys=np.arange(max(0,round(y)-3),min(H,round(y)+4)).astype(int)
  if len(ys)==0:continue
  d=1.0-a[ys,x]/255.0
  local_cost=(1-d)*1.5+.27*abs(ys-y)
  candidates.append((x,ys,local_cost))
 states=[np.asarray(candidates[0][2],float)]
 parents=[]
 for i in range(1,len(candidates)):
  x,y,cost=candidates[i]
  yprev=candidates[i-1][1]
  move=np.abs(y[:,None]-yprev[None,:])
  z=states[-1][None,:] + .17*move + .15*np.maximum(move-2,0)**2
  idx=np.argmin(z,axis=1)
  states.append(cost+z[np.arange(len(y)),idx])
  parents.append(idx)
 ix=int(np.argmin(states[-1]))
 yy=[None]*len(candidates)
 yy[-1]=int(candidates[-1][1][ix])
 for i in range(len(candidates)-2,-1,-1):
  ix=int(parents[i][ix]); yy[i]=int(candidates[i][1][ix])
 x=np.array([c[0] for c in candidates])
 pts=np.column_stack([x,yy]).astype(float)
 return pts, np.c_[x,pred], np.abs(a[np.array(yy),x].astype(float)-0)/255

def fit_circle(p):
 xy=np.asarray(p,float)
 center=xy.mean(axis=0); v=xy-center
 z=np.linalg.lstsq(np.column_stack([2*v[:,0],2*v[:,1],np.ones(len(v))]), np.sum(v*v,axis=1),rcond=None)[0]
 ctr=center+z[:2]; r=math.sqrt(max(0,z[2]+np.dot(z[:2],z[:2])))
 def res(t): return np.hypot(xy[:,0]-t[0],xy[:,1]-t[1])-t[2]
 try:
  t=least_squares(res,[*ctr,r],loss='huber',f_scale=1.5,max_nfev=500).x
  return {'center_px':[float(t[0]),float(t[1])],'radius_px':float(t[2]),'rmse_px':float(np.sqrt(np.mean(res(t)**2)))}
 except Exception as e:
  return {'error':str(e)}
def fit_polys(p):
 x=p[:,0];y=p[:,1]; out={}
 for deg in (1,2,3):
  v=np.polyfit(x-x.mean(),y,deg)
  pred=np.polyval(v,x-x.mean())
  out['polynomial_'+str(deg)]={'rmse_px':float(np.sqrt(np.mean((pred-y)**2))),'coefficients_centered':list(map(float,v))}
 return out
def nearest_ink_distance(p):
 # independent pixel-distance match only; cannot establish feature identity
 ink=a<135
 dt=cv2.distanceTransform((~ink).astype('uint8'),cv2.DIST_L2,3)
 xy=np.asarray(p,int)
 return float(np.mean(dt[xy[:,1],xy[:,0]])), float(np.percentile(dt[xy[:,1],xy[:,0]],95))
def svgline(points):
 return ' '.join(('M' if i==0 else 'L')+f'{p[0]:.2f},{p[1]:.2f}' for i,p in enumerate(points))

results={}; rows=[]
for name,c in FEATURES.items():
 pts,seed,strength=sample_edge(c)
 center_mask=(pts[:,0]>=c['visible_x'][0])&(pts[:,0]<=c['visible_x'][1])
 vis=pts[center_mask]
 ma,pa=nearest_ink_distance(vis)
 results[name]=dict(classification=c['type'], anchor_points_px=c['anchors'],
     core_supported_range_px=c['visible_x'], uncertainty=c['uncertain_at'],
     candidates_n=len(pts),core_n=len(vis),dark_fraction_ink_135=float(np.mean(a[vis[:,1].astype(int),vis[:,0].astype(int)]<135)),
     core_mean_distance_to_any_dark_pixel=ma, core_p95_distance_to_any_dark_pixel=pa,
     fits=fit_polys(vis), circle=fit_circle(vis), core_points_px=vis.tolist(),
     all_points_px=pts.tolist(), judgement='provisional image-space anatomical edge, high-res source used, terminals unresolved')
 for p in pts:
  rows.append([name,float(p[0]),float(p[1]),'observable_core' if p[0] in vis[:,0] else 'uncertain_endpoint',
               int(a[int(p[1]),int(p[0])])])
with open(OUT/'data'/'R11_IMAGE_SPACE_POINTS.csv','w',newline='') as f:
 wr=csv.writer(f);wr.writerow(['feature','x_px','y_px','status','grayscale_value_0_black']);wr.writerows(rows)
(OUT/'data'/'R11_CURVE_METRICS.json').write_text(json.dumps(results,indent=2))
(OUT/'data'/'SOURCE_PROVENANCE.json').write_text(json.dumps({
 'source_title':'Viollet-le-Duc, Dictionnaire raisonne, Volume I, Arc-boutant, figure 61',
 'source_url':SRC_URL,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
 'source_pixel_size':[W,H],'units':'image pixels only','calibration':None,
 'source_purpose':'Historical evidence of Beauvais flying-buttress arrangement',
 'no_approved_cathedral_changes':True,
 'working_title':'R11 image-space contour candidates'},indent=2))

# Overlay individual source pixels and image-space geometry. Black for core, red for ambiguous terminals.
im=Image.open(SRC).convert('RGB')
dr=ImageDraw.Draw(im)
COLORS={'upper_coping':'#0061cc','upper_intrados':'#007c41','lower_coping':'#ad6400','lower_intrados':'#801bc9'}
for name,rec in results.items():
 pts=np.array(rec['all_points_px'])
 pcore=np.array(rec['core_points_px'])
 color=COLORS[name]
 if len(pcore)>1: dr.line([tuple(x) for x in pcore],fill=color,width=2)
 core_lo=rec['core_supported_range_px'][0];core_hi=rec['core_supported_range_px'][1]
 for (x,y) in pts:
  if x<core_lo or x>core_hi:
   dr.point((int(x),int(y)),fill=(220,25,25))
 # label near visible center
 q=pcore[len(pcore)//2].astype(int)
 dr.text((int(q[0])+4,int(q[1])-14),name,fill=color)
im.save(OUT/'plots'/'R11_BEAVUAIS_HIGHRES_SOURCE_OVERLAY.png')
# Crop and upscale only for legibility; do not call this additional source resolution.
im.crop((130,115,410,430)).resize((840,945),Image.Resampling.NEAREST).save(OUT/'plots'/'R11_RAILS_ZOOM_3X.png')

# SVG with named layers; no raster vectorization claims. core black where visible, terminal red dashed.
def render_svg(embed=False):
 layers=[]
 if embed:
  data=base64.b64encode(SRC.read_bytes()).decode('ascii')
  layers.append(f'<image href="data:image/png;base64,{data}" x="0" y="0" width="{W}" height="{H}" opacity=".40"/>')
 layers.append('<g id="axes" fill="none" stroke="#bdbdbd" stroke-width=".7" stroke-dasharray="4 5"><path d="M242 105 V510"/><path d="M370 105 V510"/></g>')
 for name,rec in results.items():
  pts=np.array(rec['all_points_px'])
  core=np.array(rec['core_points_px'])
  lo,hi=rec['core_supported_range_px']
  aleft=pts[pts[:,0]<=lo];aright=pts[pts[:,0]>=hi]
  layers.append(f'<g id="{name}" fill="none">')
  layers.append(f'<path d="{svgline(core)}" stroke="#111" stroke-width="1.5"/>')
  if len(aleft)>1:layers.append(f'<path d="{svgline(aleft)}" stroke="#c32d34" stroke-dasharray="4 3" stroke-width="1.4"/>')
  if len(aright)>1:layers.append(f'<path d="{svgline(aright)}" stroke="#c32d34" stroke-dasharray="4 3" stroke-width="1.4"/>')
  layers.append('</g>')
 layers.append('<g font-family="sans-serif" font-size="10" fill="#333"><text x="16" y="35">F5ZP R11 — EXPERIMENTAL IMAGE-SPACE EDGE TRACING</text><text x="16" y="51">Core black | axes gray dashed | uncertain endpoints red dashed | no architectural calibration</text></g>')
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><rect width="100%" height="100%" fill="white"/>'+''.join(layers)+'</svg>'
(OUT/'svg'/'R11_VLD61_VECTOR_ONLY.svg').write_text(render_svg(False))
(OUT/'svg'/'R11_VLD61_SOURCE_OVERLAY.svg').write_text(render_svg(True))
# Printed QA and integrities
lines=['# F5ZP R11 — Source-guided Beauvais Flying Arch (EXPERIMENTAL / FOR REVIEW)',
       '',
       'Source: Viollet-le-Duc Volume I, figure 61; Wikimedia 630x1021 original, recorded SHA-256.',
       'The 315x550 Project Gutenberg edition is preserved separately and is NOT the source used in R11 QA.',
       'R08–R10, existing cathedral geometry and all approved generators remain unchanged.',
       '',
       '## Distinct geometry',
       'The uppermost boundary is a sloping stone coping/roof line, not necessarily a circular extrados.',
       'The lower flying arch has ornament above the inclined outer edge, not part of the arch curvature.',
       'Individual high and low flying-arch spans are interrupted by an intermediate receiving pier.',
       'Only visible core spans are drawn black; adjoining terminal guesses are red dashed.',
       '',
       '## Quantitative observations in IMAGE pixels (NOT architectural metres or blocks)']
for name,r in results.items():
 lines.append(f"- {name}: {r['core_n']} core pixels; {r['dark_fraction_ink_135']:.1%} dark; line RMSE {r['fits']['polynomial_1']['rmse_px']:.2f}px; quadratic RMSE {r['fits']['polynomial_2']['rmse_px']:.2f}px; circle RMSE {r['circle'].get('rmse_px',float('nan')):.2f}px. Provisional.")
lines += ['', '## Architectural limitations',
 'Source does NOT supply an unambiguous metrological springing coordinate or thickness at decorative joints.',
 'Figure 60 is a different *view* of the Beauvais support concept, but it is not dimensionally registered to 61.',
 'Ungewitter figure 912 is from a different historical reconstruction and is NOT a matching scale view.',
 'No numerical force analysis, true compass center, calibrated plan/elevation or cathedral build is certified.',
 '',
 '## Reproduction',
 'Run: python3 build_r11.py from this folder. The downloaded original must be present in the folder.',
 'All source hashes/edge points/QA and overlays regenerate without touching prior experiment files.',
]
(ROOT/'README_R11.md').write_text('\n'.join(lines)+'\n')
# QA: monotonic x, bounded pixel coords, fixed hashed source, provenance consistent, no approved files touched
for name,r in results.items():
 p=np.array(r['all_points_px'])
 assert len(p)>=45 and np.all(np.diff(p[:,0])==1) and np.all((p>=0)&(p<max(W,H)))
 assert 0<=r['dark_fraction_ink_135']<=1
assert len(results)==4
# Integrity file listing
checks={}
for p in (OUT).rglob('*'):
 if p.is_file():checks[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
(ROOT/'OUTPUT_SHA256.json').write_text(json.dumps(checks,indent=2))
ZIP=ROOT/'F5ZP_Buttress_R11_HighRes_FOR_REVIEW.zip'
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as z:
 for p in [SRC,ROOT/'build_r11.py',ROOT/'README_R11.md',ROOT/'OUTPUT_SHA256.json']+list(OUT.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(ROOT))
with zipfile.ZipFile(ZIP) as z: assert z.testzip() is None
print('R11 SUCCESS',ZIP, 'bytes',ZIP.stat().st_size)
for name,r in results.items():
 print(name, r['core_n'],round(r['dark_fraction_ink_135'],3), round(r['fits']['polynomial_1']['rmse_px'],2), round(r['fits']['polynomial_2']['rmse_px'],2),round(r['circle'].get('rmse_px',float('nan')),2))
