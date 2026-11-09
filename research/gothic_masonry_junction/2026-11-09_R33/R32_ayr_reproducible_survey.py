#!/usr/bin/env python3
"""R32 Ayr Figure 8 source-graded 2D masonry-section survey. No 3D claims."""
from pathlib import Path
import json,csv,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import median_filter
from xml.etree import ElementTree as ET
A=Path('/home/christopher/Cathedral_Research/R31')
O=Path('/home/christopher/Cathedral_Research/R32')
O.mkdir(exist_ok=True)
src=A/'ayr_page16.png'
arr=np.asarray(Image.open(src).convert('L'))
assert arr.shape==(1018,1400)
ticks=np.array([333,380,427,475,522,569],float)
positions=np.arange(6)*100.
slope,offset=np.polyfit(positions,ticks,1)
mmpp=1./slope
rms_ticks=float(np.sqrt(np.mean((ticks-(positions*slope+offset))**2)))
assert rms_ticks<0.7
Y=np.arange(767,888)
def trace(threshold):
 l=np.full(len(Y),np.nan);r=l.copy()
 for i,y in enumerate(Y):
  samples=(arr[y-1:y+2,227:299]<threshold).sum(axis=0)
  x=np.where(samples>=2)[0]+227
  if len(x)>=2 and x.max()-x.min()>=5:
   l[i]=x.min();r[i]=x.max()
 good=np.isfinite(l)&np.isfinite(r)
 assert good.sum()>80
 for q in (l,r):
  ok=np.isfinite(q)
  q[~ok]=np.interp(Y[~ok],Y[ok],q[ok])
 l=median_filter(l,size=3);r=median_filter(r,size=3)
 # Suppress isolated threshold jumps from the exterior outline to interior hatching.
 baseline=median_filter(r,size=7)
 outlier=np.abs(r-baseline)>10
 r[outlier]=baseline[outlier]
 assert (r-l).min()>1
 return l,r,int(good.sum())
l,r,n=trace(175)
width=r-l
wmm=float(width.max()*mmpp)
hmm=float((Y[-1]-Y[0])*mmpp)
amm=float(np.trapezoid(width,Y)*mmpp**2)
variants={}
for t in (160,175,190):
 a,b,k=trace(t)
 variants[str(t)]={'valid_rows':k,'max_width_mm':round(float((b-a).max()*mmpp),3),
  'mean_absolute_width_delta_mm':round(float(np.mean(abs((b-a)-width))*mmpp),3)}
pts=np.vstack([np.column_stack([l,Y]),np.column_stack([r[::-1],Y[::-1]])])
mask=np.uint8(arr>=175)
dist=cv2.distanceTransform(mask,cv2.DIST_L2,3)
dd=np.array([dist[int(y),int(round(x))] for x,y in pts])
rms_ink=float(np.sqrt(np.mean(dd**2)));p95_ink=float(np.percentile(dd,95))
print('scale',mmpp,'ticksRMS',rms_ticks,'profile',wmm,hmm,'ink RMS',rms_ink,'p95',p95_ink)
assert rms_ink<3 and p95_ink<6
# Source drawing scale only; SVG never asserts the original stone was dimensionally scanned.
unitpts=[((x-220)*mmpp+10,(y-Y[0])*mmpp+12) for x,y in pts]
poly=' '.join(f'{x:.2f},{y:.2f}' for x,y in unitpts)
svg=['<?xml version="1.0" encoding="UTF-8"?>',
'<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="320mm" viewBox="0 0 180 320">',
'<title>Ayr figure 8, provisional 1:1 paper-scale section</title>',
'<desc>Raster extracted archaeological line drawing. No authenticated bedding or front/rear stone registration.</desc>',
'<rect width="180" height="320" fill="white"/>']
for y in [12,62,112,162,212,262]:
 svg.append(f'<path d="M8 {y}H170" fill="none" stroke="#999" stroke-width=".3" stroke-dasharray="3,2"/>')
svg += [f'<polygon points="{poly}" fill="#ededed" stroke="black" stroke-width=".7"/>',
'<path d="M100 10V275" stroke="#999" stroke-width=".3" stroke-dasharray="4,3"/>',
'<path d="M12 279h50m-50 -3v6m50 -6v6" stroke="#222" stroke-width=".4" fill="none"/>',
'<text x="12" y="288" font-size="4.5">50 mm graphic length</text>',
'<path d="M12 294H150" stroke="#b44" stroke-width=".3" stroke-dasharray="2,2"/>',
'<text x="12" y="303" font-size="4.5" fill="#b44">Historical joint polygon unmeasured</text>',
'<text x="12" y="311" font-size="4">Original physical dimensions NOT certified</text>','</svg>']
svgtext='\n'.join(svg)
ET.fromstring(svgtext)
(O/'R32_Ayr_Fig8_Section_Provisional_1to1.svg').write_text(svgtext)
with open(O/'R32_section_trace_samples.csv','w',newline='') as f:
 wr=csv.writer(f)
 wr.writerow(['source_y_px','source_left_x_px','source_right_x_px','drawing_local_y_mm','drawing_left_x_mm','drawing_right_x_mm','drawing_apparent_width_mm'])
 for i,y in enumerate(Y):
  wr.writerow([y,round(float(l[i]),2),round(float(r[i]),2),round(float((y-Y[0])*mmpp),2),
    round(float((l[i]-220)*mmpp),2),round(float((r[i]-220)*mmpp),2),round(float(width[i]*mmpp),2)])
# Front engraving is connected ink, NOT a clean closed stone-body contour.
image_region=arr[520:742,130:398]
ink=cv2.morphologyEx(cv2.threshold(image_region,160,255,cv2.THRESH_BINARY_INV)[1],cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
cc=max(cv2.findContours(ink,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0],key=cv2.contourArea)
fx,fy,fw,fh=map(int,cv2.boundingRect(cc));fx+=130;fy+=520
d={'study':'R32','status':'RESEARCH_PROVISIONAL','source':'G. Stell in W.J. Lindsay, Digging Up Auld Ayr (1985), fig. 8 pp.220-222',
   'source_url':'https://aanhs.org/wp-content/uploads/2018/05/digging-up-auld-ayr.pdf',
   'source_pdf_page':16,'sha256_preview':hashlib.sha256(src.read_bytes()).hexdigest(),
   'sha256_native_jpeg':hashlib.sha256((A/'primary_page_16-000.jpg').read_bytes()).hexdigest(),
   'calibration':{'scale_tick_mm':positions.tolist(),'scale_tick_x_px':ticks.tolist(),'mm_per_rendered_pixel':mmpp,
                  'graphic_tick_rms_px':rms_ticks,'independent_vertical_metric_control':False},
   'section':{'y_source_px_range':[int(Y[0]),int(Y[-1])],
              'raster_accepted_rows':n,'apparent_width_mm':wmm,'apparent_height_mm':hmm,
              'apparent_area_mm2':amm,'source_ink_rms_px':rms_ink,'source_ink_p95_px':p95_ink,
              'threshold_sensitivity':variants,
              'qualification':'Drawing metric estimate, not authenticated physical block measurement; unverified section pose, original survey and orthogonality.'},
   'face_component':{'source_px_bbox':[fx,fy,fw,fh],
    'warning':'Connected line-art envelope mixes actual edges, decorative relief, breakage and reconstruction. NOT a physical stone silhouette.'},
   'confirmed_text_evidence':['front ogee and fillet','smaller rear filleted roll','two incised marks on upper joint beds','square section glazing grooves'],
   'missing':['true contact-bed polygons','3D stone scan','registered front vs back','mating-block ID','independent stone scale'],
   'validation':{'graphic_scale':'PASS','2d_source_ink_trace':'PASS','historical_contact_geometry':'UNRESOLVED',
     '3d_structure':'NOT GENERATED','cathedral_geometry_changed':False}}
(O/'R32_measurements_and_evidence.json').write_text(json.dumps(d,indent=2))
# One final review image only
out=Image.new('RGB',(1900,1100),'#fafafa');dr=ImageDraw.Draw(out)
fb='/usr/share/fonts/truetype/dejavu/DejaVuSans'
F=lambda z,b=False: ImageFont.truetype(fb+('-Bold' if b else '')+'.ttf',z)
dr.text((45,27),'R32  |  AYR FRAGMENT 8 — SOURCE-MEASURED SECTION STUDY',font=F(30,True),fill='#171717')
dr.text((45,72),'G. Stell, in Lindsay (1985), fig. 8, p.220 | Extracted section only | Experimental / research',font=F(17),fill='#666666')
dr.line((44,113,1855,113),fill='#bbbbbb',width=2)
dr.text((50,135),'A  ORIGINAL PLATE • SCALE CONTROL',font=F(21,True),fill='#202020')
dr.text((50,169),'Dashed reconstruction in the print is not an original stone edge.',font=F(15),fill='#555555')
# Main figure source crop
bounds=(116,432,705,914)
part=Image.open(src).convert('RGB').crop(bounds)
fac=1.29
z=part.resize((round(part.width*fac),round(part.height*fac)),Image.Resampling.LANCZOS)
ox,oy=40,221
out.paste(z,(ox,oy));dr=ImageDraw.Draw(out)
scoords=[(round(ox+(x-bounds[0])*fac),round(oy+(y-bounds[1])*fac)) for x,y in pts]
dr.line(scoords+[scoords[0]],fill='#0a0a0a',width=3,joint='curve')
dr.text((50,865),'Black overlay = one recovered drawn section outline.',font=F(16,True),fill='#222222')
dr.text((50,894),'Upper joint beds are reported in text, but full planes not depicted.',font=F(15),fill='#555555')
# Intermediate enlarged cross-section panel
dr.text((845,135),'B  PROFILE IN PAPER-SCALE UNITS',font=F(20,True),fill='#222222')
dr.text((845,169),'Estimated graphic dimensions; NOT a physical 3D survey.',font=F(15),fill='#555555')
xbase,ybase,fac2=845,220,2.42
for v in range(0,6):
 y=int(ybase+v*50*fac2)
 dr.line((845,y,1295,y),fill='#d3d3d3',width=1)
 dr.text((820,y-8),str(v*50),font=F(13),fill='#888888')
p=[(round(xbase+(x-220)*mmpp*fac2),round(ybase+(y-Y[0])*mmpp*fac2)) for x,y in pts]
dr.polygon(p,fill='#e3e3e3')
dr.line(p+[p[0]],fill='#202020',width=4,joint='curve')
center=xbase+(float(np.median((l+r)*.5))-220)*mmpp*fac2
for y in range(ybase,ybase+round(hmm*fac2),17):
 dr.line((center,y,center,y+8),fill='#999999',width=2)
dr.text((865,875),'Black = source-derived profile trace',font=F(15,True),fill='#2b2b2b')
dr.text((865,907),'Gray dashed = construction datum',font=F(15),fill='#5b5b5b')
for x in range(866,1030,17):dr.line((x,946,x+9,946),fill='#b44',width=2)
dr.text((1044,932),'Red = unresolved surfaces',font=F(15),fill='#9b4545')
# Measurement column
dr.line((1326,135,1326,1032),fill='#c9c9c9',width=2)
dr.text((1360,135),'C  VALIDATION & UNCERTAINTY',font=F(20,True),fill='#222222')
rows=[
 ('Graphic scale / rendered pixel',f'{mmpp:.4f} mm / px'),
 ('Six tick fit',f'{rms_ticks:.2f} px RMS'),
 ('Profile apparent width',f'{wmm:.1f} mm'),
 ('Profile apparent height',f'{hmm:.1f} mm'),
 ('Trace-to-ink RMS',f'{rms_ink:.2f} px'),
 ('Source rows accepted',f'{n} of {len(Y)}'),
 ('Threshold variation (mean)',f'{max(variants["160"]["mean_absolute_width_delta_mm"],variants["190"]["mean_absolute_width_delta_mm"]):.1f} mm'),
 ('Historical joint polygons','0 geometrically measured'),
 ('Original rear-surface registration','Not available'),
 ('Mating stone / contact tests','Not available'),
 ('Generated Blender/GLB mesh','None')]
y=194
for title,val in rows:
 dr.text((1360,y),title,font=F(15,True),fill='#444444')
 dr.text((1360,y+26),val,font=F(17),fill='#181818')
 y+=72
dr.text((1360,996),'UNVALIDATED AS HISTORIC MASONRY',font=F(16,True),fill='#a33939')
dr.line((43,1040,1856,1040),fill='#cccccc',width=2)
dr.text((48,1058),'No reconstructed joint, no approved geometry change, and no GLB: this is a reproducible source-to-section digitization only.',font=F(16),fill='#555555')
out.save(O/'R32_Ayr_Fig8_Survey_Review.png',optimize=True)
print(json.dumps({'png':str(O/'R32_Ayr_Fig8_Survey_Review.png'),'svg':str(O/'R32_Ayr_Fig8_Section_Provisional_1to1.svg'),
 'mm_per_px':mmpp,'section_apparent_mm':[wmm,hmm],'trace_ink_RMS_px':rms_ink,'pdf_source_control':True}))
