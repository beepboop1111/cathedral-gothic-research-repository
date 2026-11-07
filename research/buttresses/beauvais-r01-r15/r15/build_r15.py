#!/usr/bin/env python3
"""F5ZP R15: independent Burges (1870) four-span source-guided study.
Experimental image-space geometry. NO source or F5ZP baseline modified.
"""
from pathlib import Path
import numpy as np, csv,json,hashlib,zipfile,math,shutil
from PIL import Image,ImageDraw
from scipy.interpolate import PchipInterpolator
from scipy.optimize import least_squares
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parent
SOURCE=Path('/home/christopher/Desktop/F5ZP_Buttress_R14_INDEPENDENT_EVIDENCE_20261104/originals/Burges_1870_Beauvais_Plate06.jpg')
assert SOURCE.is_file()
work=ROOT/'RESULTS'
for d in ('original','svg','overlay','data','qa','notes'): (work/d).mkdir(parents=True,exist_ok=True)
dst=work/'original'/'Burges_Plate06_1870_UNMODIFIED.jpg'
shutil.copyfile(SOURCE,dst)
im=Image.open(dst).convert('RGB')
a=np.asarray(im.convert('L'),np.uint8)
H,W=a.shape
assert (W,H)==(1793,2560)
# Dark sepia diagnostic ink; raw scan is not perfectly uniform.
# Define a conservative threshold; noncorrespondence means geometry is only hypothetical.
ink=a<170
dist=distance_transform_edt(~ink)
# Visual anchors selected from Burges plate 6, not from VLD61. They follow
# the *soffit* of the four distinct visible flying-arch spans.
# Columns 0-1 are source pixel coordinates, no architectural scale.
ANCHORS={
 'UPPER_INNER':[(482,516),(525,530),(565,550),(606,579),(653,624),(692,674),(736,730),(770,793),(792,854),(811,930)],
 'UPPER_OUTER':[(950,774),(982,790),(1015,816),(1040,840),(1070,873),(1100,915),(1125,956)],
 'LOWER_INNER':[(484,1031),(536,1059),(590,1093),(647,1141),(692,1196),(732,1263),(764,1341),(789,1413),(805,1482)],
 'LOWER_OUTER':[(948,1285),(987,1304),(1022,1330),(1053,1368),(1081,1409),(1110,1452)]
}
# visible core only; no guess crossing pier capital, gargoyle or masonry obscuration
CORE_RANGES={'UPPER_INNER':(536,771),'UPPER_OUTER':(977,1096),
             'LOWER_INNER':(536,781),'LOWER_OUTER':(982,1090)}
# geometric analysis must not assume true circles. Compare against polynomials and raw sampled shape.
def fit_circle(p):
 p=np.asarray(p,float); mean=p.mean(0); q=p-mean
 z=np.linalg.lstsq(np.c_[2*q[:,0],2*q[:,1],np.ones(len(q))],(q*q).sum(1),rcond=None)[0]
 c=mean+z[:2];r=np.sqrt(max(0,z[2]+z[:2]@z[:2]))
 res=least_squares(lambda t:np.linalg.norm(p-t[:2],axis=1)-t[2],[*c,r],loss='soft_l1',f_scale=2,max_nfev=500)
 c=res.x;err=np.linalg.norm(p-c[:2],axis=1)-c[2]
 return {'center_px':c[:2].tolist(),'radius_px':float(c[2]),'rmse_px':float(np.sqrt(np.mean(err**2)))}
def measure(pts):
 ix=np.clip(pts[:,0].round().astype(int),0,W-1);iy=np.clip(pts[:,1].round().astype(int),0,H-1)
 d=dist[iy,ix]
 return {'mean_ink_distance_px':float(d.mean()),'p90_ink_distance_px':float(np.percentile(d,90)),
         'fraction_within_3px':float((d<=3).mean()),'fraction_within_6px':float((d<=6).mean()),
         'fraction_dark_lt170':float((a[iy,ix]<170).mean())}
def poly_rmse(p,deg):
 x=p[:,0];y=p[:,1];co=np.polyfit(x-x.mean(),y,deg)
 return float(np.sqrt(np.mean((np.polyval(co,x-x.mean())-y)**2)))
def pathstr(pts):return ' '.join(('M' if i==0 else 'L')+f'{x:.3f},{y:.3f}' for i,(x,y) in enumerate(pts))
vectors={}
for name,points in ANCHORS.items():
 pts=np.asarray(points,float)
 xs=np.arange(pts[0,0],pts[-1,0]+0.1,1.0)
 ys=PchipInterpolator(pts[:,0],pts[:,1])(xs)
 curve=np.c_[xs,ys]
 lo,hi=CORE_RANGES[name]
 core=curve[(curve[:,0]>=lo)&(curve[:,0]<=hi)]
 # Give independent visual evidence of source correspondence but DO NOT
 # move traces onto whichever adjacent ink line happens to be darkest.
 # A nearest-ink correction could snap to intrados voussoir joints.
 raw_metric=measure(core)
 # JPEG image-space comparisons are NOT masonry thickness/structural loads.
 circle=fit_circle(core)
 results={'anchors_source_xy_px':pts.tolist(),'visible_core_range_x_px':[lo,hi],
         'curve_method':'piecewise monotone cubic through visual anchors, source-guided candidate',
         'core_n':len(core),'core_ink_metrics':raw_metric,
         'fits_px':{'line_rmse':poly_rmse(core,1),'quadratic_rmse':poly_rmse(core,2),'cubic_rmse':poly_rmse(core,3),'circle_candidate':circle},
         'junctions':'uncertain: terminal segments cropped from core (source decoration)',
         'not_a_historical_compass_arc':True}
 vectors[name]={'full':curve,'core':core,'metadata':results}
assert len(vectors)==4
# Scene topology has four separate spans, no dimensional connection asserted.
comparison={}
for n,r in vectors.items():
 for other in vectors:
  if other==n:continue
  # Do not infer real-world dimension by source matching.
  pass
 comparison[n]=r['metadata']
(work/'data'/'R15_BURGES06_FOUR_SPAN_METRICS.json').write_text(json.dumps(comparison,indent=2))
with open(work/'data'/'R15_BURGES06_FOUR_SPAN_POINTS.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['source','feature','x_px','y_px','evidence'])
 for name,v in vectors.items():
  low,high=CORE_RANGES[name]
  for x,y in v['full']:
   w.writerow(['Burges 1870 Plate 06',name,round(x,3),round(y,3),'core_supported_candidate' if low<=x<=high else 'inferred_terminal_red'])
# color overlay on Burges image to make visual check straightforward.
overlay=im.copy();draw=ImageDraw.Draw(overlay)
colors={'UPPER_INNER':'#046aa6','UPPER_OUTER':'#248441','LOWER_INNER':'#7b2cbf','LOWER_OUTER':'#b36a10'}
for name,v in vectors.items():
 core=v['core'];allp=v['full'];lo,hi=CORE_RANGES[name]
 draw.line([tuple(map(int,x)) for x in core],fill=colors[name],width=4)
 uncertain=allp[(allp[:,0]<lo)|(allp[:,0]>hi)]
 for x,y in uncertain[::3]: draw.ellipse((x-1,y-1,x+1,y+1),fill='#c32d3b')
 m=core[len(core)//2];draw.text((int(m[0])+8,int(m[1])-25),name,fill=colors[name])
overlay.save(work/'overlay'/'R15_BURGES06_FOUR_SPANS_SOURCE_OVERLAY.png')
# source-independent vector geometry SVG, black core + red dashed uncertain terminals
S=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
 '<rect width="100%" height="100%" fill="white"/>',
 '<g font-family="Arial" font-size="28" fill="#171717"><text x="100" y="100">R15 BURGES 1870 PLATE 06 — INDEPENDENT FOUR-SPAN STUDY</text>',
 '<text x="100" y="139" font-size="20">Black: observable curve candidates | Gray: reference axes | Red dashed: unverified junctions</text>',
 '<text x="100" y="169" font-size="20">Source image coordinates only — NOT calibrated architectural dimensions</text></g>',
 '<g stroke="#b3b3b3" fill="none" stroke-dasharray="9 9" stroke-width="2"><path d="M420 250 V1750 M900 250 V1750 M1160 250 V1750"/></g>']
for name,v in vectors.items():
 core=v['core'];allp=v['full'];lo,hi=CORE_RANGES[name]
 S.append(f'<g id="{name}" fill="none"><path d="{pathstr(core)}" stroke="#111" stroke-width="4"/>')
 for q in [allp[allp[:,0]<=lo],allp[allp[:,0]>=hi]]:
  if len(q)>1:S.append(f'<path d="{pathstr(q)}" stroke="#c32d3b" stroke-dasharray="12 10" stroke-width="3"/>')
 S.append('</g>')
S.append('</svg>')
(work/'svg'/'R15_BURGES06_VECTOR_ONLY.svg').write_text('\n'.join(S))
# QA no one model joined at a masonry interface automatically.
for n,v in vectors.items():
 p=v['full'];assert np.all(np.diff(p[:,0])>0)
 assert np.isfinite(p).all()
 assert np.all((p[:,0]>=0)&(p[:,0]<W)&(p[:,1]>0)&(p[:,1]<H))
 assert CORE_RANGES[n][1]-CORE_RANGES[n][0]>100
# explicit provenance and license situation
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
provenance={'source_title':'William Burges, Architectural Drawing (1870), Beauvais Cathedral, Plate 6',
'source_link':'https://drawingmatter.org/excerpts-from-architectural-drawing-1870/',
'source_image_link':'https://drawingmatter.org/wp-content/uploads/2022/02/burgess_3423.06_cs_19-01-22-scaled.jpg',
'source_sha256':sha(dst),'source_pixel_dimensions':[W,H],
'historical_scale_calibrated':False,'source_comparison_r14':'Burges and VLD in different orientations; DO NOT register/merge by pixels',
'photo_color_source_preserved':True,'historical_building_geometry_unchanged':True,
'significance':'Four independent visible arch spans; author says only few measurements of flying buttresses possible'}
(work/'data'/'R15_PROVENANCE.json').write_text(json.dumps(provenance,indent=2))
readme='''# F5ZP R15 — four-span Burges tracing; construction-phase screening
Source: William Burges, Architectural Drawing (1870) Plate 6. Its modern reproduction is courtesy of Drawing Matter.
Original JPG preserved bit-for-bit. R14 original never edited.
A source-guided image-space trace of the upper and lower inner/outer spans is in separate SVG and CSV data.
The original drawing is a valuable cross-reference, NOT an exact surveyed as-built flying-buttress dataset:
Burges explicitly says only a few measurements were available on the flying buttresses.
Smooth source-guided paths are hypotheses; visible core is black; inferred terminal lengths are red dashed.
Each curve is fitted independently. Circle residuals do not demonstrate circles used historically.
Avoid mixing R11 (Viollet-le-Duc) and R15 (Burges) coordinates: different projections, orientations and scans.
Modern UPJV Phileas 2021 survey sections are identified in SURVEY_AND_PHASE_EVIDENCE.csv but are not extracted,
re-licensed, transformed or copied into this package because originals are listed as CC BY-NC-ND.
Some 1284 rebuilding changed straight choir bays but do not assign those phases to any chevet element without bay evidence.
No F5ZP floor plan, locked sizes, approved geometries or generators were changed.
This package is an experimental review, not an approved cathedral model.
'''
(work/'notes'/'README_R15.md').write_text(readme)
# source evidence classification
sources=[
 ('Burges06','burges visual original','1870','two-level four-span architectural drawing','source image, visually interpreted','image coordinates only','DIRECT VISUAL + EXPERIMENTAL TRACE','not a calibrated survey of the flying arches'),
 ('Burges06','Burges explanatory text','1870','flying buttresses only partially measurable','historical author statement','none','DIRECT AUTHOR LIMITATION','no exact radius/springing approval'),
 ('VLD61','Viollet-le-Duc Dictionnaire, I, fig 61','1850s','two-level multi-pier buttress support','historical interpretation','legacy 630px source','SECONDARY HISTORICAL DRAWING','not physically registered to Burges'),
 ('UPJV_Profils','https://www.u-picardie.fr/phileas/item/profils-dune-cathedrale/','2021 survey, 2026 catalogue','modern digitized cathedral 2D/3D sections','MIS laboratory metadata','no point-cloud coordinates received','SURVEY SOURCE LOCATED, NO MEASURABLE FILE','CC BY-NC-ND; do not alter/reproduce'),
 ('UPJV_Choeur','https://www.u-picardie.fr/phileas/item/la-cathedrale-a-choeur-ouvert/','2021 survey, 2026 catalogue','choir open digital visualization including tie rods','MIS laboratory metadata','no detailed geometry received','SURVEY SOURCE LOCATED','cannot establish historical phase solely from current state'),
 ('UPJV_Plan','https://www.u-picardie.fr/phileas/item/la-cathedrale-de-beauvais-suivez-le-plan/','2021 survey, 2026 catalogue','choir ambulatory radial chapels, later intermediate piers','MIS laboratory metadata','plan not available as coordinates','CONTEMPORARY COMMENTARY','avoid confusing straight bays with hemicycle'),
 ('Murray','https://projects.mcah.columbia.edu/medieval-architecture/htm/ms/ma_ms_bc_discuss_collapse.htm','modern historical interpretation','bay differences 1284/14thC rebuilding and intermediary upright overhang','historical analysis','none','HISTORICAL PHASE EVIDENCE','bay-by-bay mapping required'),
 ('2026Materials','https://www.mdpi.com/1996-1944/19/21/4659','2026','section VLD is interpretive, not measured; 46.50 vs 46.75m','recent research publication','none','INDEPENDENT QUALIFICATION','modern article source, not historical plate'),
 ('Ungewitter912','Ungewitter-Mohrmann II LXXXVII fig 912','1892','general double buttress system diagram','independent construction treatise','not registered','COMPARATIVE ARCHITECTURAL LOGIC','not the same building as Beauvais')
]
with open(work/'data'/'SURVEY_AND_PHASE_EVIDENCE.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['ID','source','date','content','provenance','measurement_status','evidence_class','constraint']);w.writerows(sources)
manifest={}
for f in work.rglob('*'):
 if f.is_file():manifest[str(f.relative_to(work))]=sha(f)
(work/'data'/'R15_SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
# zip and source-integrity check
out=ROOT/'F5ZP_Buttress_R15_Burges_Survey_Phase_FOR_REVIEW.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in [ROOT/'build_r15.py']+list(work.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(ROOT))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('R15 CREATED',out,'MB',round(out.stat().st_size/1e6,2))
for n,v in vectors.items():
 m=v['metadata']['core_ink_metrics'];c=v['metadata']['fits_px']
 print(n,'points',v['metadata']['core_n'],'ink3',round(m['fraction_within_3px'],3),'ink6',round(m['fraction_within_6px'],3),
       'circle-rmse',round(c['circle_candidate']['rmse_px'],2))
