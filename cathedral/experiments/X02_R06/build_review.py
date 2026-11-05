#!/usr/bin/env python3
"""R06 context review. Read-only source geometry; no architectural redesign."""
from pathlib import Path
import sys,json,hashlib,math,csv,textwrap
sys.path.append(str(Path(__file__).resolve().parent.parent/'.x04_deps'))
from shapely.geometry import shape,mapping,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;S=R/'sources';O=R/'outputs';V=R/'previews'
d3=json.loads((S/'R03_GEOMETRY.json').read_text());d2=json.loads((S/'R02_CONTEXT.json').read_text());d4=json.loads((S/'R04_GEOMETRY.json').read_text());d5=json.loads((S/'R05_GEOMETRY.json').read_text())
features=d3['features'];context={f['id']:shape(f['geometry']) for f in d2['features']};bodies={k:shape(q) for k,q in d4['active_R04_bodies'].items()};courts={f['id']:shape(f['geometry']) for f in features if f['properties']['role']=='court'}
roof=unary_union([shape(f['polygon']) for f in d5['roofs']]);roots=unary_union([q for n,q in context.items() if n.startswith('ROOT')]);n4=next(shape(f['geometry']) for f in features if f['id']=='n4_link' and f['properties']['role']=='link');tests=[]
def ck(name,value,detail=''):tests.append({'id':name,'result':'PASS' if bool(value) else 'FAIL','detail':detail})
source_hashes=json.loads((S/'SOURCE_HASHES.json').read_text())
for n,h in source_hashes.items():ck('SOURCE_HASH_'+n,hashlib.sha256((S/n).read_bytes()).hexdigest()==h)
for name,q in courts.items():ck('COURT_VALID_'+name,q.is_valid)
ck('N4_NO_2D_ROOT_OVERLAP',n4.intersection(roots).area<1e-9,'Only the 12 inherited root polygons; no 3D portal/flyer validation.')
ck('N4_NO_REFERENCE_CHAPEL_OVERLAP',n4.intersection(context['chapel_reference']).area<1e-9,'Reference chapel footprint remains unverified.')
ck('R05_DOES_NOT_OVERHANG_GARTH',roof.intersection(courts['garth']).area<1e-9)
heights=[]
for s in d5['roof_schedule']:
 v=s.get('ridge_underside_m',s.get('apex_underside_m'));heights.append({'roof':s['id'],'underside_peak_m':v,'outer_peak_m':v+.18})
chapter=courts['chapter_court'];ccover=chapter.intersection(roof).area;remaining=chapter.difference(roof)
metrics={'garth_dimensions_m':[15,19],'garth_area_m2':courts['garth'].area,'R05_roof_projection_on_garth_m2':roof.intersection(courts['garth']).area,'chapter_court_R03_area_m2':chapter.area,'chapter_court_projected_R05_roof_cover_m2':ccover,'chapter_court_remaining_uncovered_by_R05_m2':remaining.area,'chapter_court_R05_cover_percent':100*ccover/chapter.area,'N4_route_min_2D_root_margin_m':n4.distance(roots),'R05_roof_min_2D_root_distance_m':roof.distance(roots),'main_vs_chapter_outer_peak_difference_m':12.28-11.78,'heights':heights}
qa={'id':'X02_R06_CONTEXT_REVIEW','status':'READ-ONLY ARCHITECTURAL REVIEW; NO GEOMETRY PROMOTION','checks':tests,'pass_count':sum(x['result']=='PASS' for x in tests),'fail_count':sum(x['result']=='FAIL' for x in tests),'metrics':metrics,'limits':['Cathedral reference is the retained experimental X01 north-wall/root fragment, not a verified whole-cathedral model.','The inherited 1.3/1000 + Z offset transform is used only as existing R02 context; never applied to approved cathedral geometry.','Other R03 wings and cloister are flat footprint guides, not new height or roof designs.','Court uncovered area is plan projection against R05 roofs only, not a daylight, rain or full-precinct roof assessment.','R05 remains experimental; structural capacities and F5ZL-C support schedule remain unresolved.']}
assert not qa['fail_count'];(O/'R06_REVIEW_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
with (O/'R06_MEASUREMENTS.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['measurement','value','units']);
 for k,v in metrics.items():
  if isinstance(v,(float,int)):w.writerow([k,f'{v:.9f}','see suffix'])
 for h in heights:w.writerow([h['roof']+'_outer_peak',h['outer_peak_m'],'m'])
# Diagram inputs: footprints sit at drawing elevation only; no invented building heights.
diagram=[]
for f in features:
 role=f['properties']['role'];name=f['id']
 if role=='building' and name not in ['residential_range','night_range','stair_turret','chapter_house','chapter_vestibule']:diagram.append({'id':name,'kind':'unmodeled_wing_footprint','geometry':f['geometry']})
 elif role=='court':diagram.append({'id':name,'kind':'court','geometry':f['geometry']})
 elif role=='wall' and name in ['cloister','service_link']:diagram.append({'id':name,'kind':'plan_outline','geometry':f['geometry']})
 elif role=='link':diagram.append({'id':name,'kind':'route_reservation','geometry':f['geometry']})
for name,q in context.items():
 if name=='wall' or name.startswith('ROOT'):diagram.append({'id':name,'kind':'cathedral_reference_fragment','geometry':mapping(q)})
diagram.append({'id':'CH_N5_UNVERIFIED','kind':'unresolved','geometry':mapping(context['chapel_reference'])})
(O/'CONTEXT_DIAGRAM_INPUT.json').write_text(json.dumps({'units':'metres in inherited precinct frame','status':'DISPLAY-ONLY PLAN GUIDES; architecture heights unknown except R05','features':diagram,'metrics':metrics},separators=(',',':'))+'\n')
# Physical 1:1 SVG retains plan geometry, not arbitrary display scaling.
def path(q):
 if q.is_empty:return ''
 if q.geom_type=='Polygon':return ' '.join('M '+' L '.join(f'{x:.8f},{-z:.8f}' for x,z in ring.coords)+' Z' for ring in [q.exterior,*q.interiors])
 return ' '.join(path(p) for p in q.geoms)
sv=['<svg xmlns="http://www.w3.org/2000/svg" width="58000mm" height="58000mm" viewBox="-65 -66 58 58"><title>R06 experimental precinct context; metres; physical 1:1; cathedral fragment only</title>']
for f in diagram:
 color='#b36b60' if f['kind'] in ['unresolved','cathedral_reference_fragment'] else '#9aa6a7';sv.append(f'<g id="{f["id"]}"><path d="{path(shape(f["geometry"]))}" fill="none" stroke="{color}" stroke-width=".05" stroke-dasharray=".18 .12"/></g>')
for f in d5['roofs']:sv.append(f'<path d="{path(shape(f["polygon"]))}" fill="#cbdbe4" fill-rule="evenodd" stroke="#242b30" stroke-width=".04"/>')
sv.append('</svg>');(O/'R06_CONTEXT_PLAN_1to1.svg').write_text('\n'.join(sv))
# Build review PDF after the two native render JPGs are available.
if not (V/'R06_CONTEXT_OBLIQUE.jpg').exists():
 print(json.dumps({'stage':'measurements and diagram ready','QA':qa['pass_count'],'metrics':metrics},indent=2));sys.exit(0)
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
INK='#26333b';GRAY='#9ba5a9';BLUE='#547b90';RED='#a7473c'
c=Canvas(str(O/'F5ZP_X02_R06_OVERALL_CONTEXT_REVIEW.pdf'),pagesize=(420*mm,297*mm),invariant=1)
def header(t,sub,n):
 c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',16);c.drawString(14*mm,281*mm,t);c.setFont('Helvetica',8);c.drawString(14*mm,274*mm,sub);c.setStrokeColor(HexColor(GRAY));c.line(14*mm,269*mm,406*mm,269*mm);c.setFont('Helvetica',7);c.drawString(14*mm,10*mm,'CATHEDRAL F5ZP | R06 CONTEXT REVIEW | NO ARCHITECTURAL CHANGES | EXPERIMENTAL');c.drawRightString(406*mm,10*mm,str(n))
def note(x,y,t,body,width):
 c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',10);c.drawString(x*mm,y*mm,t);c.setFont('Helvetica',8);y-=6
 for l in textwrap.wrap(body,int(width/1.45)):c.drawString(x*mm,y*mm,l);y-=4
 return y-8
def panel(bounds,x0,y0,scale):
 x1,z1,x2,z2=bounds;s=1000/scale*mm
 def pt(x,z):return x0*mm+(x-x1)*s,y0*mm+(z-z1)*s
 def draw(q,fill=None,color=INK,dash=False):
  c.setStrokeColor(HexColor(color));c.setFillColor(HexColor(fill or '#ffffff'));c.setLineWidth(.45);c.setDash([2,1.5] if dash else [])
  for p in getattr(q,'geoms',[q]):
   if p.is_empty:continue
   pp=c.beginPath()
   for ring in [p.exterior,*p.interiors]:
    vv=list(ring.coords);pp.moveTo(*pt(*vv[0]));[pp.lineTo(*pt(*v)) for v in vv[1:]];pp.close()
   c.drawPath(pp,stroke=True,fill=fill is not None,fillMode=0)
  c.setDash([])
 def label(x,z,t,size=6.5):c.setFillColor(HexColor(INK));c.setFont('Helvetica',size);c.drawCentredString(*pt(x,z),t)
 return draw,label
header('R06 | OVERALL PRECINCT CONTEXT','1:250 at A3 | R05 roofs over retained R03 plan | cathedral north-edge fragment only',1)
dr,lab=panel((-65,8,-7,66),14,24,250)
for f in diagram:
 q=shape(f['geometry']);k=f['kind'];fill={'court':'#eff0e6','unmodeled_wing_footprint':'#e6e4df','route_reservation':'#e5eaf0','cathedral_reference_fragment':'#ddd7d2'}.get(k)
 dr(q,fill,color=RED if k=='unresolved' else GRAY,dash=k in ['unresolved','route_reservation'])
for f in d5['roofs']:dr(shape(f['polygon']),'#d3e1e7',BLUE)
dr(remaining,'#d6e5c7','#6c8658');dr(chapter.intersection(roof),None,RED,True)
for x,z,t in [(-41,31.9,'GARTH 15 x 19 m'),(-55.2,35,'WEST RANGE'),(-45,49.3,'REFECTORY'),(-44,57.5,'KITCHEN'),(-25.8,49,'RESIDENTIAL'),(-17.5,34,'CHAPTER'),(-34,16.8,'N4 ROUTE'),(-35,10.2,'CATHEDRAL NORTH EDGE: FRAGMENT ONLY')]:lab(x,z,t,6.5)
c.setStrokeColor(HexColor(INK));c.setFillColor(HexColor(INK));c.setLineWidth(.6);c.line(22*mm,238*mm,22*mm,250*mm);c.line(22*mm,250*mm,21*mm,247*mm);c.line(22*mm,250*mm,23*mm,247*mm);c.setFont('Helvetica',7);c.drawCentredString(22*mm,253*mm,'N')
c.line(22*mm,26*mm,42*mm,26*mm)
for x in [22,42]:c.line(x*mm,25*mm,x*mm,27*mm)
c.drawCentredString(32*mm,29*mm,'5 m')
y=255
for t,body in [('Review finding 1 - composition','Retain the present east-range composition for now. The octagonal chapter house remains distinct in form. The residential ridge is 0.50 m higher; hierarchy comes from form and position, not a taller chapter apex.'),('Review finding 2 - court enclosure',f'The 285 m2 garth receives no R05 roof projection. In the named R03 chapter court, {ccover:.2f} of {chapter.area:.2f} m2 is beneath R05 roof projection; {remaining.area:.2f} m2 remains uncovered by R05. This is not a daylight simulation.'),('Review finding 3 - cathedral connection',f'The inherited N4 route avoids the 12 root polygons, with a minimum 2D margin of {n4.distance(roots)*1000:.1f} mm. The actual portal, CH-N5 exterior and flying supports remain unverified.'),('Source distinction','Blue = developed R05 roofs. Gray = retained plan guides with unmodeled heights. Green = chapter-court footprint not covered by R05 roofs. Red dashes = unresolved interface/cover boundary.'),('Review limit','This is a precinct review in the inherited X01 experimental frame. The cathedral is not a complete verified 3D mass here. No conclusion about its overall height dominance is made.')]:y=note(258,y,t,body,145)
c.showPage()
header('R06 | MODEL IN PLAN CONTEXT','R05 architecture retained | remaining wings and cloister shown as flat plan guides, not height proposals',2)
c.drawImage(str(V/'R06_CONTEXT_OBLIQUE.jpg'),14*mm,76*mm,width=255*mm,height=185*mm,preserveAspectRatio=True,mask='auto')
c.drawImage(str(V/'R06_EAST_RANGE_VIEW.jpg'),274*mm,112*mm,width=132*mm,height=149*mm,preserveAspectRatio=True,mask='auto')
note(16,66,'How to read these views','The only developed building volume is R05. Flat courts, wing footprints and the north cathedral edge show placement. Do not read the thin diagram slabs as low buildings, or infer unknown roof heights from them.',240)
note(274,102,'Architectural judgement','The stepped ridge sequence reads coherently. Keep it while the cathedral portal and chapter-court enclosure are reviewed. Lowering a roof is not justified by this incomplete height context alone.',130)
c.showPage()
header('R06 | HEIGHT HIERARCHY AND NEXT DECISION','Measured R05 outer roof tops | no cathedral or other-wing heights inferred',3)
rows=sorted(heights,key=lambda h:-h['outer_peak_m']);x0=20;y0=238
for i,h in enumerate(rows):
 y=y0-i*20;c.setFillColor(HexColor(BLUE if h['roof']!='CHAPTER_HOUSE' else '#6f895d'));c.rect(72*mm,y*mm,h['outer_peak_m']*9*mm,8*mm,fill=1,stroke=0);c.setFillColor(HexColor(INK));c.setFont('Helvetica',9);c.drawString(x0*mm,(y+2)*mm,h['roof'].replace('_',' '));c.drawString((75+h['outer_peak_m']*9)*mm,(y+2)*mm,f"+{h['outer_peak_m']:.3f} m")
note(20,85,'Vertical controls retained','Upper floor +3.600 m; upper-room ceiling control +6.300 m; reserved stair plane +5.700 m. The current roofs clear these controls. This review changes none of them.',200)
y=250
for t,body in [('Immediate next architectural task','Recover and coordinate the actual N4/CH-N5 cathedral connection in this working plan. Confirm the desired open character of the chapter court, whose upper link now creates a covered edge.'),('Roof decision after coordination','If the residential block dominates in a verified full precinct model, compare one lower-ridge option against R05 using matched views. Do not change it solely because its peak is 0.50 m higher than the chapter roof.'),('Then develop the junctions','Proceed to major entrances and roof connections once the context decision is stable. Decorative mouldings and detailed drainage hardware can wait.'),('Unresolved controls','Whole-cathedral scale/frame and height context; other-wing/cloister roof heights; actual CH-N5 and portal; flying supports; support capacities; site boundary. F5ZL-C 248-support schedule remains unresolved.'),('Preserved work','F5ZK-C, F5ZN-A, the working inner/middle ambulatory generator, Pass 6J and all source models remain untouched. This review is not architectural approval.')]:y=note(258,y,t,body,145)
c.showPage();c.save();print(json.dumps({'QA_pass':qa['pass_count'],'PDF':'F5ZP_X02_R06_OVERALL_CONTEXT_REVIEW.pdf','metrics':metrics},indent=2))
