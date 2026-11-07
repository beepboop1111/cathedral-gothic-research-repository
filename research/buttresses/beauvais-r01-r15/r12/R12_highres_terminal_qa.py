#!/usr/bin/env python3
"""R12 terminal holdout tests on the matching 630px original.
No source or cathedral files modified.
"""
from pathlib import Path
import json, csv, hashlib, math, zipfile, shutil
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parent
R11=Path('/home/christopher/Desktop/F5ZP_Buttress_R11_EXPERIMENTAL_20261104')
SRC=R11/'Beauvais_fig61_Wikimedia_630x1021.png'
assert SRC.exists()
ORIG=ROOT/'originals';ORIG.mkdir(exist_ok=True)
dst=ORIG/'Beauvais_Fig61_630x1021_unchanged.png'
shutil.copyfile(SRC,dst)
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==hashlib.sha256(dst.read_bytes()).hexdigest()
a=np.array(Image.open(SRC).convert('L'))
ink=a<145
dt=distance_transform_edt(~ink)
data=json.loads((R11/'results/data/R11_CURVE_METRICS.json').read_text())
SZ=[a.shape[1],a.shape[0]]
zones={
 'upper_at_A':[251,188,281,277],
 'upper_at_choir':[329,137,370,195],
 'lower_at_A':[251,321,286,399],
 'lower_at_choir':[330,257,371,312]}
# Two circles were fit in R11 on in-span points only. Holdouts below are
# EXCLUDED terminal regions, to avoid circular visual 'validation'.
output={'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
 'size_px':SZ,'source_ink_threshold':145,'geometry_proven':False,
 'not_a_historical_compass_construction':True,'holdouts':{},
 'competing_interpretations':['Circular candidate','Original masonry joints','Decorative/contact obscuration']}
im=Image.open(SRC).convert('RGB');d=ImageDraw.Draw(im,'RGB')
def circle_fit(core):
 p=np.array(core,float)
 mu=p.mean(0);v=p-mu
 z=np.linalg.lstsq(np.column_stack((2*v[:,0],2*v[:,1],np.ones(len(v)))),(v*v).sum(1),rcond=None)[0]
 ctr=mu+z[:2]; r=math.sqrt(max(0,z[2]+z[:2]@z[:2]))
 from scipy.optimize import least_squares
 fit=least_squares(lambda q:np.linalg.norm(p-q[:2],axis=1)-q[2],[*ctr,r],loss='huber',f_scale=1.5).x
 return fit
def circle_y(c,x):
 cx,cy,r=c
 if x<cx-r or x>cx+r: return float('nan')
 return cy-math.sqrt(max(0.,r*r-(x-cx)**2))
def dark_distance(pts):
 xy=np.asarray(pts,float);xx=np.clip(np.rint(xy[:,0]).astype(int),0,SZ[0]-1);yy=np.clip(np.rint(xy[:,1]).astype(int),0,SZ[1]-1)
 vals=dt[yy,xx]
 return dict(n=len(vals),within_1_5px=float((vals<=1.5).mean()),within_3px=float((vals<=3).mean()),mean_dark_distance_px=float(vals.mean()),p90_dark_distance_px=float(np.percentile(vals,90)))
def dash(pts,color=(225,25,35), width=2):
 v=np.asarray(pts,float)
 for i in range(0,len(v)-1,2):
  d.line([tuple(v[i]),tuple(v[i+1])],fill=color,width=width)
for name in ['upper_intrados','lower_intrados']:
 core=np.array(data[name]['core_points_px'],float)
 c=circle_fit(core); cx,cy,r=c; xl=cx-r
 left_end=core[0,0];right_start=core[-1,0]
 # Circle param near vertical tangent, not y(x) linear approximation
 xx=np.arange(math.ceil(xl),left_end,.5)
 left=np.array([(x,circle_y(c,x)) for x in xx])
 xx=np.arange(right_start+0.5,348.5,.5)
 right=np.array([(x,circle_y(c,x)) for x in xx])
 assert np.all(np.isfinite(left)) and np.all(np.isfinite(right))
 b={'circle_center_px':[float(cx),float(cy)],'circle_radius_px':float(r),
   'leftmost_tangent_candidate_px':[float(xl),float(cy)],
   'right_candidate_at_x348_px':[348,float(circle_y(c,348))],
   'left_holdout':dark_distance(left),'right_holdout':dark_distance(right),
   'negative_control_left_10px_below':dark_distance(left+np.array([0,10])),
   'negative_control_right_10px_below':dark_distance(right+np.array([0,10])),
   'warning':'Black pixels may be unrelated masonry edges; proximity does not certify the springing contact'}
 output['holdouts'][name]=b
 for pts in (left,right): dash(pts)
 # black line on source is hard to read; thin white halo under black traced core
 for i in range(len(core)-1):
  p=tuple(core[i]); q=tuple(core[i+1]); d.line([p,q],fill='white',width=3); d.line([p,q],fill='black',width=1)
 d.ellipse((xl-3,cy-3,xl+3,cy+3),outline=(215,0,0),width=2)
 d.text((int(xl)-26,int(cy)+8),name.replace('_intrados',''),fill=(215,0,0))
for name,(x0,y0,x1,y1) in zones.items():
 for i in range(x0,x1,6):
  d.line((i,y0,min(i+3,x1),y0),fill=(180,10,20),width=1)
  d.line((i,y1,min(i+3,x1),y1),fill=(180,10,20),width=1)
 for j in range(y0,y1,6):
  d.line((x0,j,x0,min(j+3,y1)),fill=(180,10,20),width=1)
  d.line((x1,j,x1,min(j+3,y1)),fill=(180,10,20),width=1)
im.save(ROOT/'R12_FIG61_630px_SOURCE_JUNCTION_OVERLAY.png')
# localized visual details from actual source (not registration against lower-res reference)
for label,bb in [('upper_pier',(225,145,306,295)),('lower_pier',(225,293,306,423)),('upper_choir',(312,128,381,213)),('lower_choir',(312,255,381,323))]:
 dst=im.crop(bb).resize(((bb[2]-bb[0])*4,(bb[3]-bb[1])*4),Image.Resampling.NEAREST)
 dst.save(ROOT/(label+'_CLOSEUP_4x.png'))
(ROOT/'R12_TERMINAL_INK_QA.json').write_text(json.dumps(output,indent=2))
readme='''# R12 Full-resolution source / junction QA
Independent experimental directory: historical original retained byte-for-byte.
The 630x1021 source was used for all contact tests. R11 full source archives
and approved F5ZP geometry remain untouched.

Source: Viollet-le-Duc, Dictionnaire raisonne, volume I, figure 61.
CIRCLE CANDIDATES derive from R11 in-span selected source points.
Red dashed terminal extensions are hypotheses; NO red path becomes verified
because ink is nearby. Masonry joints, ornaments and unrelated ink are competing
explanations. Original architectural unit scale and springing positions remain
unverified. Numeric holdout checks use dark pixel threshold 145, distances in px.
The 'negative controls' offset fitted paths by +10 px for context, not a formal
statistical significance test. Both support faces and decorated choir wall remain
geometrically underdetermined.

The full R12 image/QA package is for review, NOT an approved cathedral component.
'''
(ROOT/'README.md').write_text(readme)
# archive all QA and source, not the older R11 package
out=ROOT/'F5ZP_Buttress_R12_HIRES_Junctions_FOR_REVIEW.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for f in ROOT.rglob('*'):
  if f.is_file() and f!=out and f.name!='R12_magnify_rois.py':
   z.write(f,f.relative_to(ROOT))
with zipfile.ZipFile(out) as z: assert z.testzip() is None
print('DONE',out,len(out.read_bytes()))
for k,v in output['holdouts'].items():
 print(k,'tangent',v['leftmost_tangent_candidate_px'],'holdout left ink',v['left_holdout'],'right',v['right_holdout'])
