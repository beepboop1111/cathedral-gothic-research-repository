#!/usr/bin/env python3
"""R50 source-grade Brandon M04 R03: numerical 2D measurements & evidence-overlay.
Pixel coordinates only. Original R03 files are read-only; no historical scale assumed.
"""
from pathlib import Path
import json,hashlib,math,xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import Polygon, LinearRing
from shapely.affinity import scale as affine_scale
from PIL import Image,ImageDraw,ImageFont
R=Path('/home/christopher/Cathedral_Research/R50_source_graded_tracery');R.mkdir(parents=True,exist_ok=True)
SRC=Path('/home/christopher/Downloads/downlods/3/1/BRANDON_M04_R03_EXPERIMENTAL_LOCAL/BRANDON_M04_R03_CONTOURS.json')
DATA=json.loads(SRC.read_text())
H0=hashlib.sha256(SRC.read_bytes()).hexdigest()
rings=[np.array(a,dtype=np.float64) for a in DATA['rings']]
assert len(rings)==4
POLY=Polygon(rings[0],[x for x in rings[1:]])
assert POLY.is_valid and len(POLY.interiors)==3
assert rings[0][:,1].min()==6 and rings[0][:,1].max()==499
bounds=POLY.bounds
pxwidth=bounds[2]-bounds[0];pxheight=bounds[3]-bounds[1]
assert pxwidth==622 and pxheight==493
def fit_circle(P):
 x=P[:,0];y=P[:,1]
 A=np.c_[2*x,2*y,np.ones(len(x))]
 b=x*x+y*y
 cx,cy,c=np.linalg.lstsq(A,b,rcond=None)[0]
 rad=math.sqrt(c+cx*cx+cy*cy)
 residual=np.hypot(x-cx,y-cy)-rad
 return {'center_px':[float(cx),float(cy)],'radius_px':float(rad),
   'RMS_to_R03_trace_px':float(np.sqrt(np.mean(residual**2))),
   'maximum_residual_px':float(max(abs(residual))),
   'fit_points':len(P)}
tip=int(rings[0][:,1].argmin())
left_edge=int(rings[0][:,0].argmin())
assert 10<tip<24 and 28<left_edge<48
fits={'right_outer':fit_circle(rings[0][:tip+1]),
      'left_outer':fit_circle(rings[0][tip:left_edge+1])}
minimum_gaps=[float(POLY.exterior.distance(LinearRing(r))) for r in rings[1:]]
for i in range(3):
 for j in range(i+1,3):
  assert Polygon(rings[i+1]).distance(Polygon(rings[j+1]))>=0.
sym=affine_scale(POLY,xfact=-1,yfact=1,origin=((bounds[0]+bounds[2])/2,0))
iou=POLY.intersection(sym).area/POLY.union(sym).area
outline_perimeter=POLY.exterior.length
areas=[Polygon(r).area for r in rings]
assert abs(areas[0]-sum(areas[1:])-POLY.area)<1e-6
metrics={'checkpoint':'R50','evidence_class':'TRACED_R03_PIXEL_GEOMETRY_NOT_ORIGINAL_INK',
 'source_file':str(SRC),'source_SHA256':H0,'original_image_SHA256_mentioned_in_R03':DATA['original_reference_sha256'],
 'original_source_scan_verified_or_mounted':False,
 'source_units':DATA['units'],
 'source_old_extrusion_height_units':DATA['height'],
 'outer_bbox_pixels':[float(x) for x in bounds],
 'outline_span_pixels':float(pxwidth),'outline_height_pixels':float(pxheight),
 'outer_ring_vertices':len(rings[0]),'hole_vertices':[len(q) for q in rings[1:]],
 'stone_face_area_in_source_px2':float(POLY.area),
 'outer_2D_polygon_area_px2':areas[0],
 'three_hole_areas_px2':areas[1:],
 'minimum_outer_to_hole_spacing_pixels':minimum_gaps,
 'profile_symmetry_IoU_fraction':float(iou),
 'circle_fit_status':'RED DASHED: uncertain fitted construction, not certified compass setout',
 'outer_arc_fits':fits,
 'scale_bar_verified':False,'physical_stone_thickness_measured':False,
 'historically_authenticated_mullion_joins':False,
 'arch_springing_and_crown_historical_geometry':'R03 extracted contours only; fit candidates require original plate comparison',
 'source_old_mesh_expected_genus':3,
 'baseline_files_modified':False}
# XML-safe source overlay: confirmed R03 shape black, uncertain constructions red,
# guides dashed grey. Black is confirmation of tracing data, NOT original print itself.
def xy_line(P):
 return 'M '+ ' L '.join(f'{p[0]:.5f},{p[1]:.5f}' for p in P)+' Z'
def fitted_polyline(points,f):
 ctr=np.array(f['center_px']);r=f['radius_px']
 ang=np.unwrap(np.arctan2(points[:,1]-ctr[1],points[:,0]-ctr[0]))
 ts=np.linspace(ang[0],ang[-1],200)
 return 'M '+' L '.join(f'{ctr[0]+r*np.cos(t):.4f},{ctr[1]+r*np.sin(t):.4f}' for t in ts)
root=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','viewBox':'0 0 660 542',
 'width':'1320','height':'1084'})
ET.SubElement(root,'title').text='Brandon M04 — R50 source-graded ring contours in R03 pixels'
ET.SubElement(root,'desc').text='Black is the previously traced R03 contour, not authenticated historical ink. Grey construction axes; dashed red circles are uncertain fits. Original metric scale unresolved.'
ET.SubElement(root,'path',{'d':'M 325,0 V 520 M 0,499 H 660','stroke':'#999','stroke-width':'.75',
 'stroke-dasharray':'5 4','fill':'none'})
ET.SubElement(root,'path',{'d':xy_line(rings[0]),'fill':'#deded9','stroke':'#151515','stroke-width':'1.4'})
for r in rings[1:]:
 ET.SubElement(root,'path',{'d':xy_line(r),'fill':'#fff','stroke':'#151515','stroke-width':'1.2'})
for name,p in [('right_outer',rings[0][:tip+1]),('left_outer',rings[0][tip:left_edge+1])]:
 ET.SubElement(root,'path',{'d':fitted_polyline(p,fits[name]),'fill':'none',
     'stroke':'#ba4242','stroke-width':'1.8','stroke-dasharray':'4 4'})
ET.ElementTree(root).write(R/'R50_Brandon_R03_measured_source_overlay.svg',encoding='utf-8',xml_declaration=True)
ET.parse(R/'R50_Brandon_R03_measured_source_overlay.svg')
# Render corresponding 2D QA panel with only PIL, no need for any guess at 3D source.
W,H=1250,1110
img=Image.new('RGB',(W,H),'#f1f2ee')
d=ImageDraw.Draw(img)
froot='/usr/share/fonts/truetype/dejavu/DejaVuSans'
ft=lambda n,b=False:ImageFont.truetype(froot+('-Bold' if b else '')+'.ttf',n)
d.text((36,25),'R50  /  BRANDON M04 R03 TRACED WINDOW HEAD',font=ft(29,True),fill='#25353e')
d.text((38,70),'Source-coordinate measurement; not physically calibrated',font=ft(18),fill='#716b69')
factor=1.61; ox=85;oy=120
def cv(q):return [(int(round(ox+p[0]*factor)),int(round(oy+p[1]*factor))) for p in q]
d.line([(ox+int(325*factor),oy),(ox+int(325*factor),oy+int(515*factor))],fill='#acada8',width=1)
d.line([(ox,oy+int(499*factor)),(ox+int(645*factor),oy+int(499*factor))],fill='#acada8',width=1)
d.polygon(cv(rings[0]),fill='#c6c9c6',outline='#20292c',width=3)
for r in rings[1:]:
 d.polygon(cv(r),fill='#f1f2ee')
 d.line(cv(r)+cv(r)[:1],fill='#20292c',width=3,joint='curve')
for key,part in [('right_outer',rings[0][:tip+1]),('left_outer',rings[0][tip:left_edge+1])]:
 f=fits[key];ctr=np.array(f['center_px']);a=np.unwrap(np.arctan2(part[:,1]-ctr[1],part[:,0]-ctr[0]))
 ts=np.linspace(a[0],a[-1],180)
 pts=cv([(ctr[0]+f['radius_px']*np.cos(t),ctr[1]+f['radius_px']*np.sin(t)) for t in ts])
 for i in range(0,len(pts)-2,8):
  d.line(pts[i:i+4],fill='#be4141',width=4)
d.text((35,1010),f'R03 traced outline: {pxwidth:.0f} × {pxheight:.0f} pixels   |   Openings: 3',font=ft(18,True),fill='#263239')
d.text((35,1041),'Black: R03 source trace   /   Grey: construction   /   Red dashed: uncertain fitted arcs',font=ft(15),fill='#6a6d6f')
d.text((35,1070),'M04 unfinished; original print and independent scale-bar registration still required.',font=ft(15),fill='#a24b43')
img.save(R/'R50_source_overlay_2D.png',optimize=True)
(R/'R50_source_measurements.json').write_text(json.dumps(metrics,indent=2))
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==H0
print('R50_SOURCE_QA_PASS',json.dumps({'rings':len(rings),'opening_count':3,'bbox_px':[pxwidth,pxheight],
 'area_px2':round(POLY.area,3),'max_RMS_circle_px':round(max(z['RMS_to_R03_trace_px'] for z in fits.values()),4),
 'source_image_validated':False,'svg_XML_PASS':True}))
