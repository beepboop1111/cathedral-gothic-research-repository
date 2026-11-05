#!/usr/bin/env python3
"""X02 R01: source-preserving 2D precinct coordination, with explicit blockers.

Run with Python 3.12+, numpy, shapely 2+, matplotlib and reportlab.
Reads the geometry-only prefix of the retained X01 study. Never runs its
export commands or a cathedral vault generator. All outputs stay beside this file.
"""
from pathlib import Path
import ast, csv, hashlib, json, math, sys, textwrap
from itertools import combinations
from xml.sax.saxutils import escape

DEPS=Path(__file__).resolve().parent.parent/'.x02_deps'
if DEPS.exists(): sys.path.append(str(DEPS))
from shapely.geometry import box, LineString, mapping, shape
from shapely.ops import unary_union
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'sources/x01'
OUT=ROOT/'outputs'
OUT.mkdir(exist_ok=True)
RED='#a33737'; GRAY='#a3a3a3'; INK='#202529'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(name,d): (OUT/name).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
baseline={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'sources').rglob('*') if p.is_file()}
text=(SRC/'build_gate_study.py').read_text()
prefix=text.split('# Intersections with real source support envelopes')[0]
tree=ast.parse(prefix)
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and
               n.func.attr in ['write_text','write_bytes','savefig','unlink'] for n in ast.walk(tree))
g={'__file__':str(SRC/'build_gate_study.py')}
exec(compile(tree,'retained_X01_geometry_only','exec'),g)
x01=json.loads((SRC/'X01_QA.json').read_text())
evidence=json.loads((ROOT/'sources/MR_SOURCE_EVIDENCE.json').read_text())
cx=g['n4_gate']; nx=g['n6_night']; wf=g['WF']
g['N5_THROAT']=box(g['n5_gate']-.6,wf,g['n5_gate']+.6,14.1625)
roots=[r['geometry'] for r in g['roots']]
root_union=unary_union(roots)
walks=g['cloister_outer'].difference(g['cloister_garden'])

# New X02 hypotheses: routes and a stair reservation only, never built doors.
# Their interiors have no recovered room partitions or stair geometry.
ceremony=LineString([(cx,wf),(cx,20.65),(-31.75,20.65),(-31.75,34),(-15,34)])
night=LineString([(nx,wf),(nx,25.1)])
chapter=LineString([(-31.75,34),(-15,34)])
stair=box(nx-1.2,23.9,nx+1.2,26.3)
corridor=ceremony.buffer(.6,cap_style=2,join_style=2)
night_sweep=night.buffer(.6,cap_style=2,join_style=2)
permitted_domain=unary_union([g['n4_link'],walks,g['east_wing'],g['chapter_hall']])
night_domain=unary_union([g['night_route'],g['east_wing']])
features=[]
def feature(id,geom,status,source,role):
    features.append({'type':'Feature','id':id,'properties':{'status':status,'source':source,'role':role},'geometry':mapping(geom)})
for n in ['wall','cloister_outer','cloister_garden','east_wing','chapter_hall','refectory',
          'new_garden','chapel_reference','n4_link','night_route']:
    feature(n,g[n],'RETAINED_X01_EXPERIMENT','sources/x01/build_gate_study.py',n)
for i,r in enumerate(g['roots']):
    feature(r['source_id'],r['geometry'],'RETAINED_X01_TRANSFORMED_ROOT','sources/x01/build_gate_study.py','screening_root')
for id,geom,role in [('CEREMONY_R1',ceremony,'route_centerline'),('NIGHT_R2',night,'route_centerline'),
                     ('CHAPTER_R3',chapter,'route_centerline'),('CEREMONY_1p2m_SWEEP',corridor,'route_sweep'),
                     ('NIGHT_1p2m_SWEEP',night_sweep,'route_sweep'),('NIGHT_STAIR_RESERVATION',stair,'unbuilt_stair_zone')]:
    feature(id,geom,'X02_HYPOTHESIS','build_x02.py',role)
model={'type':'FeatureCollection','id':'F5ZP-X02-R01','units':'metres','axes':'X east; Z north (GeoJSON y = project Z)',
       'authority':'EXPERIMENTAL, PARTIAL COORDINATION; no source promotion',
       'scope':'north nave / experimental E5-R3 monastery only; not a recovered whole-cathedral plan',
       'transform':{'source_native_mm_to_X01_X':'1.3*x/1000',
                    'source_native_mm_to_X01_north_Z':'1.3*z/1000 + 2.7584',
                    'limitation':'retained X01 nave-root study transform only; never apply globally to F5ZK-C/F5ZN-A'},
       'unplaced_protected_south':{'house_m':[30,34],'cloister_m':[20.2,22.4],'garden_m':[13.2,15.4],
           'walk_depth_m':3.5,'reported_Z_m':[-69,-35],
           'site_X':None,'exact_lock_file_recovered':False,'no_site_polygon_synthesized':True},
       'features':features}
write_json('X02_GEOMETRY.json',model)

checks=[]
def check(id,ok,scope,detail): checks.append({'id':id,'result':'PASS' if bool(ok) else 'FAIL','scope':scope,'detail':detail})
def close(a,b,tol=5.1e-5): return abs(a-b)<=tol
check('INPUT_PREFIX_READONLY',True,'technical','AST checked for file writing / deletion / export calls before evaluating retained X01 parameter geometry.')
for f in features:
    q=shape(f['geometry'])
    check('VALID_'+f['id'],q.is_valid and not q.is_empty,'geometry','Valid nonempty geometry; no repair applied.')
metrics={'N4_portal_X_m':cx,'N6_reservation_X_m':nx,'N4_wall_face_Z_m':wf,
         'N4_root_gap_m':g['n4_throat'].distance(root_union),'garden_area_m2':g['new_garden'].area,
         'garden_root_gap_m':g['new_garden'].distance(root_union),
         'N5_conditional_chapel_overlap_m2':g['N5_THROAT'].intersection(g['chapel_reference']).area,
         'ceremony_sweep_root_overlap_m2':corridor.intersection(root_union).area,
         'ceremony_sweep_garden_overlap_m2':corridor.intersection(g['cloister_garden']).area,
         'ceremony_outside_known_route_domain_m2':corridor.difference(permitted_domain).area,
         'night_outside_known_route_domain_m2':night_sweep.difference(night_domain).area,
         'night_sweep_root_overlap_m2':night_sweep.intersection(root_union).area,
         'ceremony_night_sweep_overlap_m2':corridor.intersection(night_sweep).area,
         'stair_reservation_outside_east_wing_m2':stair.difference(g['east_wing']).area,
         'ceremony_centerline_length_m':ceremony.length,'night_centerline_length_m':night.length}
for id,new,old in [('N4_CENTER',cx,x01['candidate_comparison']['N4_east']['x_m']),
                   ('N6_CENTER',nx,x01['candidate_comparison']['N6_east_night_reservation']['x_m']),
                   ('N4_ROOT_GAP',metrics['N4_root_gap_m'],x01['planning_widths']['N4_root_gap_to_throat_m']),
                   ('GARDEN_AREA',metrics['garden_area_m2'],x01['checks']['N4_relocated_entrance_garden']['footprint_area_sqm']),
                   ('N5_CHAPEL_TEST',metrics['N5_conditional_chapel_overlap_m2'],x01['checks']['N5_original_candidate_throat']['overlaps_chapel_test_sqm'])]:
    check('REGRESSION_'+id,close(new,old),'X01 regression',f'{new:.8f} vs recorded {old:.8f}; tolerance 0.000051 in stated units.')
for key in ['ceremony_sweep_root_overlap_m2','ceremony_sweep_garden_overlap_m2',
            'ceremony_outside_known_route_domain_m2','night_outside_known_route_domain_m2',
            'night_sweep_root_overlap_m2','ceremony_night_sweep_overlap_m2','stair_reservation_outside_east_wing_m2']:
    check(key,metrics[key]<1e-8,'2D reservation screening',f'{metrics[key]:.10f} m2; interior partitions, door cuts and 3D clearance unverified.')
retained=['cloister_outer','east_wing','chapter_hall','refectory']
for a,b in combinations(retained,2):
    check('MASSING_'+a+'__'+b,g[a].intersection(g[b]).area<1e-8,'retained X01 massing','Pairwise footprint area overlap; garden is deliberately excluded from this test.')
for f in features:
    geom=shape(f['geometry']); check('ROUNDTRIP_'+f['id'],geom.equals_exact(shape(json.loads(json.dumps(mapping(geom)))),1e-10),'serialization','GeoJSON round-trip tolerance 1e-10 m.')

def max_throat_width():
    lo,hi=1.2,2.5
    for _ in range(60):
        w=(lo+hi)/2
        if box(cx-w/2,wf,cx+w/2,14.1625).intersection(root_union).area>1e-10:hi=w
        else:lo=w
    return lo
metrics['conditional_N4_root_screen_width_ceiling_m']=max_throat_width()
metrics['retained_X01_root_count']=len(roots)
metrics['south_cloister_area_m2']=20.2*22.4
metrics['north_cloister_area_m2']=22*26
metrics['cloister_area_increase_percent']=(22*26/(20.2*22.4)-1)*100
metrics['south_garden_area_m2']=13.2*15.4
metrics['north_garden_area_m2']=15*19
metrics['north_known_massing_union_m2']=unary_union([g[n] for n in retained]).area
sensitivity=[]
for west_growth in [0,.5,1,1.454,1.5,2]:
    b=g['chapel_reference'].bounds
    p=box(b[0]-west_growth,b[1],b[2],b[3])
    sensitivity.append({'west_growth_m':west_growth,'N4_throat_overlap_m2':g['n4_throat'].intersection(p).area,
                        'status':'CONDITIONAL RECTANGLE TEST ONLY - NOT CHAPEL RECOVERY'})
write_json('X02_SENSITIVITY.json',{'N4_root_width_ceiling_is_not_design_approval':True,'metrics':metrics,'CH_N5_tests':sensitivity})

conflicts=[
 ('A01','BLOCKED','CH-N5 exterior','Vault preset 2304 x 1728 mm verified; exterior walls, position, projection and roof not recovered.','Recover actual chapel plan/masonry before clearing N4 or N5 as an opening.'),
 ('A02','UNVERIFIED','N4 portal and windows','N4 1.2 m throat is a reservation; original wall remains uncut. N4-west window retained as a planning reservation.','Verify actual jamb, respond, window and capital envelopes.'),
 ('B01','COORDINATED_IN_2D','Ceremonial/gallery/chapter route','1.2 m swept reservation fits retained walk/link/wing/hall union; no garden/root overlap in the 12-root screen.','Resolve actual partitions and controlled thresholds before architectural acceptance.'),
 ('B02','UNVERIFIED','Private night route','N6 route and 2.4 x 2.4 m stair zone are hypotheses; no stair or door is recovered.','Recover east-wing stair and actual N6 wall/opening.'),
 ('B03','BLOCKED','Public transept and Great Library','Exact entrance/stairs, library footprint and scholarly-cloister coordinates not recovered.','Keep routes separate in functional schedule; do not fabricate site geometry.'),
 ('C01','COORDINATED_IN_2D','Entrance garden','Retained 47.5753 m2 X01 garden has no overlap with the transformed 12-root screen.','Site boundaries, access landscaping and complete-root check remain open.'),
 ('C02','UNVERIFIED','Roof connections','X01 roof levels are hypothetical; actual masonry/eaves/cloister roofs and site elevations unavailable.','No roof adoption or vertical clearance claim.'),
 ('D01','BLOCKED','Protected southern plan placement','Reported dimensions recovered; original E5-C3-L1 lock file and exact site X placement missing.','Use unplaced dimensional template only. Do not transplant E5-R1 south comparison coordinates.'),
 ('D02','PARTIAL_DELIVERED','Overall precinct/master plan','Northern-sector drawing, detail, circulation and dimensional comparison delivered. Complete cathedral/site source not recovered.','Whole-precinct integration remains blocked; this sector is not a replacement master plan.'),
 ('G01','UNRESOLVED','F5ZL-C supports','248-support CSV missing. Twelve X01 screening roots are not the 88-root schedule or the 248 supports.','Preserve missing schedule status.'),
 ('G02','UNRESOLVED','Other cathedral authorities','Bay angles, gallery 4521/4950, Q1/J1 5400/5429 and generator identity remain separate open records.','No selection or global transform in this experiment.'),
]
with (OUT/'X02_CONFLICT_REGISTER.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['id','status','scope','finding','next_action']);w.writerows(conflicts)
with (OUT/'X02_MEASUREMENTS.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['measurement','value','units_from_key','scope']);
    for k,v in metrics.items():w.writerow([k,v,'see measurement suffix','experimental 2D screening only'])

# Shared drawing model. All site geometry shown is experimental: dashed red.
def svg_paths(geom):
    paths=[]
    if geom.geom_type=='Polygon':
        for r in [geom.exterior,*geom.interiors]:
            pts=list(r.coords);paths.append('M '+' L '.join(f'{x:.8f},{-z:.8f}' for x,z in pts)+' Z')
    elif geom.geom_type=='LineString':paths.append('M '+' L '.join(f'{x:.8f},{-z:.8f}' for x,z in geom.coords))
    else:
        for q in geom.geoms: paths.extend(svg_paths(q))
    return paths
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="57000mm" height="60000mm" viewBox="-56 -60 57 60">',
     '<title>X02 R01 north-sector experimental plan - 1 SVG unit = 1 metre; physical SVG 1:1</title>',
     '<desc>Dashed red = uncertain / experimental. Dashed gray = axes. No approved source geometry changed. Whole precinct and chapel exterior not recovered.</desc>']
for z in range(0,61,5):svg.append(f'<path d="M -56,{-z} H 1" fill="none" stroke="{GRAY}" stroke-width="0.014" stroke-dasharray=".12 .12"/>')
for x in range(-55,1,5):svg.append(f'<path d="M {x},0 V -60" fill="none" stroke="{GRAY}" stroke-width="0.014" stroke-dasharray=".12 .12"/>')
for f in features:
    role=f['properties']['role']
    if role=='route_sweep':continue
    fill='#fff4f3' if shape(f['geometry']).geom_type=='Polygon' else 'none'
    if f['id']=='cloister_garden':fill='#f6f6f6'
    svg.append(f'<g id="{escape(f["id"])}" data-authority="{f["properties"]["status"]}">')
    for p in svg_paths(shape(f['geometry'])):
        svg.append(f'<path d="{p}" fill="{fill}" fill-rule="evenodd" stroke="{RED}" stroke-width="{.055 if role=="route_centerline" else .028}" stroke-dasharray=".18 .10"/>')
    svg.append('</g>')
labels=[(-41,32,'E5-R3 NORTH CLOISTER / EXPERIMENT'),(-26,43,'EAST WING'),(-15,34,'CHAPTER HALL'),
        (-42,50,'REFECTORY'),(-41,16.5,'GARDEN 47.58 m2'),(-31,13.3,'CH-N5 TEST ONLY'),
        (-43,5,'PARTIAL E5-S2 NAVE CONTEXT'),(-53,58,'X02 R01 - SECTOR ONLY; NO BASELINE PROMOTION')]
for x,z,t in labels:svg.append(f'<text x="{x}" y="{-z}" font-family="sans-serif" font-size=".45" fill="{INK}">{escape(t)}</text>')
svg.append('</svg>');(OUT/'X02_NORTH_SECTOR_1to1.svg').write_text('\n'.join(svg))

PDF=OUT/'F5ZP_X02_R01_FLOOR_PLAN_REVIEW.pdf'
c=Canvas(str(PDF),pagesize=(420*mm,297*mm))
c.setTitle('Cathedral F5ZP X02 R01 - Experimental floor-plan coordination')
c.setAuthor('Cathedral Project')
def header(title,sub,page):
    c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',17);c.drawString(15*mm,282*mm,title)
    c.setFont('Helvetica',8.5);c.drawString(15*mm,275*mm,sub)
    c.setStrokeColor(HexColor(GRAY));c.line(15*mm,270*mm,405*mm,270*mm)
    c.setFont('Helvetica',7);c.drawString(15*mm,10*mm,'F5ZP / X02 R01 / EXPERIMENTAL - NO APPROVAL PROMOTION / 05 NOV 2026')
    c.drawRightString(405*mm,10*mm,str(page))
def notes(x,y,title,body,width=140):
    c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',10);c.drawString(x*mm,y*mm,title)
    y-=6;c.setFont('Helvetica',9)
    for para in body.split('\n'):
        for l in textwrap.wrap(para,width=int(width/1.68)) or ['']:
            c.drawString(x*mm,y*mm,l);y-=4.5
        y-=2
    return y-4
def panel(bounds,left,bottom,scale):
    xmin,zmin,xmax,zmax=bounds
    s=1000/scale*mm
    def pt(x,z):return left*mm+(x-xmin)*s,bottom*mm+(z-zmin)*s
    def drawgeom(q,fill=False,lw=.45,color=RED,dash=True):
        c.setStrokeColor(HexColor(color));c.setLineWidth(lw);c.setDash([2,1.7] if dash else [])
        if fill:c.setFillColor(HexColor('#fff6f5'))
        for d in getattr(q,'geoms',[q]):
            rings=[d.exterior,*d.interiors] if d.geom_type=='Polygon' else [d]
            p=c.beginPath()
            for ring in rings:
                coords=list(ring.coords);p.moveTo(*pt(*coords[0]))
                for a in coords[1:]:p.lineTo(*pt(*a))
                if d.geom_type=='Polygon':p.close()
            c.drawPath(p,stroke=1,fill=int(fill))
        c.setDash([])
    def label(x,z,t,size=7,bold=False,color=INK,align='center'):
        c.setFillColor(HexColor(color));c.setFont('Helvetica-Bold' if bold else 'Helvetica',size)
        getattr(c,{'center':'drawCentredString','left':'drawString','right':'drawRightString'}[align])(*pt(x,z),t)
    def dimh(x1,x2,z,t):
        c.setStrokeColor(black);c.setLineWidth(.45);c.setDash([])
        c.line(*pt(x1,z),*pt(x2,z))
        for x in [x1,x2]:c.line(*pt(x-.1,z-.13),*pt(x+.1,z+.13))
        label((x1+x2)/2,z+.25,t,7)
    c.setStrokeColor(HexColor(GRAY));c.setLineWidth(.2);c.setDash([1.5,2])
    for x in range(math.ceil(xmin/5)*5,math.floor(xmax/5)*5+1,5):
        c.line(*pt(x,zmin),*pt(x,zmax));label(x,zmin-.75,str(x),6)
    for z in range(math.ceil(zmin/5)*5,math.floor(zmax/5)*5+1,5):
        c.line(*pt(xmin,z),*pt(xmax,z));label(xmin-.4,z,str(z),6,align='right')
    c.setDash([])
    return pt,drawgeom,label,dimh
def render_site(drawgeom):
    for n in ['wall','cloister_outer','cloister_garden','east_wing','chapter_hall','refectory','new_garden','chapel_reference']:
        drawgeom(g[n],True)
    for r in roots:drawgeom(r,True)
    drawgeom(g['n4_link'],False,.9);drawgeom(g['night_route'],False,.65)
    drawgeom(ceremony,False,1.25);drawgeom(night,False,1.0);drawgeom(stair,False,.65)

header('X02 | NORTHERN SECTOR AND CIRCULATION','1:250 at A3 / metres / X east, Z north / retained X01 geometry + new route reservations',1)
pt,d,l,dh=panel((-56,0,1,60),15,25,250);render_site(d)
for x,z,t in labels[:-1]:l(x,z,t,6.7,True)
l(cx,18.4,'R1',8,True);l(-31.75,29,'R1',8,True);l(nx,19,'R2',8,True)
l(-41,30.7,'GARDEN / 15 x 19 m',7)
l(-22.4,35,'R3',8,True);l(nx,25,'STAIR?',6)
dh(-54,-44,2,'10 m');l(-54,59,'NORTH ^',7,True,align='left')
y=259
for title,body in [
 ('What this sheet establishes','A dimensioned northern-sector coordination study. The north cloister, east wing, chapter hall, refectory and garden retain their X01 footprints. No cathedral wall is cut.'),
 ('R1 / ceremonial and chapter route','N4 candidate -> 1.20 m throat -> 2.70 m gallery -> existing south/east walks -> proposed chapter-house corridor. The 1.20 m swept reservation avoids the garden and retained screening roots.'),
 ('R2 / private night reservation','Separate N6 threshold and 1.20 m route to an unbuilt 2.40 x 2.40 m stair reservation inside the east wing. Actual stair, door and partitions remain unknown.'),
 ('Public / library / service access','Remain separate functional requirements. Exact transept doorway, Great Library footprint and service access are missing; no invented site routes are plotted.'),
 ('Drawing authority','Dashed red: uncertain / experimental geometry. Dashed gray: axes. R1-R3 are reservations, not built or approved passages. This is not a recovered whole-cathedral or whole-precinct plan.'),
 ('Screening limit','Only 12 transformed X01 nave roots are present. This does not validate all 88 roots or the missing F5ZL-C 248-support schedule.')]:
    y=notes(259,y,title,body)
c.showPage()

header('X02-A/B | N4 THRESHOLD, CHAPEL AND NIGHT ROUTE','1:100 at A3 / continuous wall retained / all candidate openings and routes remain hypothetical',2)
c.saveState();c.rect(20*mm,35*mm,200*mm,220*mm,stroke=0,fill=0)
clip=c.beginPath();clip.rect(20*mm,35*mm,200*mm,220*mm);c.clipPath(clip,stroke=0,fill=0)
pt,d,l,dh=panel((-39,8,-19,30),20,35,100);render_site(d)
for bay,name in [(g['N4'],'N4'),(g['N5'],'N5'),(g['N6'],'N6')]:
    l(sum(bay)/2,9,name,10,True)
    for x in bay:d(LineString([(x,8),(x,30)]),False,.25,GRAY)
l(cx-.4,15.6,'N4 EAST',7,True,align='right');l(g['N5_mid'],13.4,'CH-N5 TEST',7,True)
l(nx,21,'N6 / R2',7,True);l(-32,23.3,'CLOISTER WALK',7)
l(nx,25.1,'STAIR?',7,True)
dh(cx-.6,cx+.6,13.4,'1.20 m');dh(cx-1.35,cx+1.35,17.4,'2.70 m')
west_window=(-37.4049-35.5641)/2
d(LineString([(west_window-.6,wf),(west_window+.6,wf)]),False,1.6)
l(west_window,10.8,'N4-W WINDOW RESERVE',6)
c.restoreState()
y=258
for title,body in [
 ('Verified chapel evidence','The saved UG script names CH-N5 and a 2304 x 1728 mm single vault. Its exterior walls, total projection, exact position and roof have not been recovered.'),
 ('Conditional chapel test','The red rectangle retains the X01 assumption: 2.9952 x 2.2464 m at 130%, centered on N5 and projected north. These assumptions cannot clear a real doorway.'),
 ('Measured screening results',f'N4 root gap: {metrics["N4_root_gap_m"]:.4f} m. N5 throat overlaps the conditional chapel rectangle by {metrics["N5_conditional_chapel_overlap_m2"]:.4f} m2. These reproduce X01.'),
 ('Sensitivity, not a new design',f'At the fixed N4 center the modeled root-only width ceiling is about {metrics["conditional_N4_root_screen_width_ceiling_m"]:.4f} m. Jambs/capitals/pier profiles are absent. A 1.454 m westward growth of the assumed chapel reaches the 1.20 m N4 throat.'),
 ('Threshold and window gate','Keep the source wall continuous. N4-east portal, N4-west retained window and N6 night doorway are planning reservations. Actual masonry openings and room partitions require source evidence.')]:
    y=notes(237,y,title,body,168)
c.showPage()

header('X02-D | SAME-SCALE CLOISTER DIMENSIONS','1:150 at A3 / independent local origins / southern site placement deliberately not inferred',3)
for left,w,h,gw,gh,title in [(22,20.2,22.4,13.2,15.4,'SOUTH / PROTECTED E5-C3-L1'),(222,22,26,15,19,'NORTH / EXPERIMENTAL E5-R3')]:
    pt,d,l,dh=panel((-1,-1,w+1,h+1),left,55,150)
    d(box(0,0,w,h),False,.9,INK,False)
    # This is a local dimension template, not a recovered site polygon.
    d(box(3.5,3.5,3.5+gw,3.5+gh),False,.65,INK,False)
    l(w/2,h+2.4,title,9,True)
    l(w/2,h/2,f'{gw:.1f} x {gh:.1f} m GARDEN',8)
    dh(0,w,-1.3,f'{w:.1f} m');l(w/2,h+.5,f'DEPTH {h:.1f} m / WALKS 3.50 m',8)
    l(w/2,1.5,'LOCAL DIMENSION TEMPLATE',7)
c.setFillColor(HexColor(INK));c.setFont('Helvetica',9)
c.drawString(22*mm,38*mm,'South: house 30 x 34 m; cloister 452.48 m2; garden 203.28 m2.')
c.drawString(222*mm,38*mm,'North: cloister 572.00 m2; garden 285.00 m2.')
c.drawString(22*mm,31*mm,'Original lock file and exact site X placement not recovered. No site relocation drawn.')
c.drawString(222*mm,31*mm,f'Cloister area difference: +{metrics["cloister_area_increase_percent"]:.2f}%. No scheme selected.')
c.drawString(22*mm,23*mm,'Black outlines confirm the reported component dimensions only. They do not certify installed geometry or southern site placement.')
c.showPage()

header('X02 | EVIDENCE, VALIDATION AND OPEN GATES','Technical and 2D geometric checks only / architectural adoption and structural validation remain open',4)
y=259
for title,body in [
 ('Completed independent work','Recovered X01 source package and geometry; verified CH-N5 vault preset against saved UG source; coordinated ceremonial/chapter and separate night reservations; tested swept route widths; retained garden; produced same-scale component comparison and machine-readable geometry.'),
 ('X02-A / source gate','PARTIAL: chapel vault dimensions verified, exterior footprint missing. Actual portal, window, respond and threshold envelopes remain unverified.'),
 ('X02-B / route coordination','PARTIAL: northern route reservations screened inside retained geometry. Actual stairs, room partitions and built doors missing. Public transept, library and service geometry not recovered.'),
 ('X02-C / precinct coordination','PARTIAL: retained northern garden and known massing screened. Roof levels remain X01 hypotheses; library, wider site and southern placement are missing.'),
 ('X02-D / review delivery','Sector plan, N4 detail, dimension comparison, route measures, conflict register, sources and scripts delivered. An overall approved master plan cannot be established from the available inputs.')]:
    y=notes(18,y,title,body,180)
notes(222,259,'Preserved authorities','F5ZK-C and F5ZN-A untouched. Existing working inner/middle vault generator not rebuilt. Pass 6J retained; no historical fixes restarted. No Blender or 3D changes. No promotion of Study D, E5-S2 or any precinct alternative.',180)
notes(222,208,'Unresolved cathedral records','Bay-angle conflict; gallery Y4521 / Y4950; Q1/J1 radius 5400 / 5429; original Pass 6J bearing authority; exact working 14-vault generator identity; missing F5ZL-C 248-support schedule. No values selected in X02.',180)
notes(222,148,'Source limits','X01 script and QA retained byte-for-byte. Original F5ZM-C root JSON, E5-R3 notes and E5-C3-L1 lock file were not recovered at their recorded paths. X01 embeds source checksums, but those missing originals cannot be independently hash-verified.',180)
notes(222,91,'Next bounded action','Recover the CH-N5 exterior plan and original southern E5-C3-L1 lock/input pair. Then replace only the marked conditional placeholders and complete site-level comparison. Final precinct selection requires user approval.',180)
c.showPage();c.save()

after={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'sources').rglob('*') if p.is_file()}
check('ALL_RETAINED_SOURCE_BYTES_UNCHANGED',baseline==after,'preservation',f'{len(baseline)} source files SHA-256 compared before/after.')
check('SVG_PHYSICAL_1_TO_1','width="57000mm" height="60000mm" viewBox="-56 -60 57 60"' in (OUT/'X02_NORTH_SECTOR_1to1.svg').read_text(),'scale','57 x 60 metre coordinate viewBox has 57000 x 60000 mm physical SVG size.')
qa={'id':'F5ZP-X02-R01','status':'VALIDATED_PARTIAL_EXPERIMENTAL_REVIEW',
    'validation_levels':{'technical':'checks below','geometric':'2D retained footprint and reservation screening only',
                         'architectural':'UNRESOLVED','historical':'not claimed','structural':'NOT ASSESSED'},
    'checks':checks,'pass_count':sum(x['result']=='PASS' for x in checks),
    'fail_count':sum(x['result']=='FAIL' for x in checks),'metrics':metrics,
    'scope_limits':['CH-N5 exterior unavailable','protected south site geometry unavailable','12 transformed roots only',
                    'no actual portal cut','whole precinct and library source unavailable','no structural approval'],
    'source_SHA256_before':baseline,'source_SHA256_after':after}
write_json('X02_QA.json',qa)
if qa['fail_count']:raise RuntimeError([x for x in checks if x['result']=='FAIL'])

report=f'''# Cathedral F5ZP X02 R01 - Experimental Floor-Plan Review

Status: VALIDATED PARTIAL EXPERIMENT; NO AUTHORITY PROMOTION.

## Outcome
The independent northern-sector work is delivered. Complete master-precinct integration remains blocked by actual CH-N5 exterior geometry, the original protected southern E5-C3-L1 site file, actual doors/stairs/partitions and Great Library/site inputs. No substitute footprints are presented as recovered architecture.

## Baseline and change
Baseline: completed X01 package `F5ZP_E5_S2_N4_NORTH_GATE_X01_REVIEW.zip`, retained under sources/x01. Governance: cathedral/governance-r01 master reference, blob 1d7e358ff7562fcc64088854baa2abd3d31a729e. Existing X01 coordinates remain unchanged. X02 adds explicit 1.2 m circulation reservations, a hypothetical 2.4 x 2.4 m night-stair zone, route screening, a dimension-only southern comparison, and an evidence/conflict register. These are experimental, unbuilt and unapproved.

Coordinates are metres, X east / Z north; source native architectural units are millimetres. E5-S2 uses X01's 130% design experiment and its additional northern transverse shift. This is not a transform of approved F5ZK-C/F5ZN-A. The SVG is physically 1:1; PDF pages have explicitly labeled presentation scales. Do not import the PDF at 1:1 without its scale conversion.

## Measured results
- Retained N4 portal center: X {cx:.4f} m, north wall Z {wf:.4f} m.
- Retained N4 screening root gap: {metrics['N4_root_gap_m']:.4f} m.
- Garden area: {metrics['garden_area_m2']:.4f} m2; retained root gap {metrics['garden_root_gap_m']:.4f} m.
- N5 throat / conditional chapel overlap: {metrics['N5_conditional_chapel_overlap_m2']:.4f} m2.
- New ceremonial reservation length: {ceremony.length:.4f} m; private night reservation length: {night.length:.4f} m.
- 1.2 m route sweeps: no modeled root/garden overlap or departure from the defined reference domains. No actual door/partition/stair clearance is established.
- South cloister: 20.2 x 22.4 m = 452.48 m2. North: 22 x 26 m = 572 m2, +{metrics['cloister_area_increase_percent']:.2f}%. Reported dimensions are comparable; site impacts cannot yet be compared.

## Source evidence and remaining uncertainty
The saved UG variant eb68a0c16ca5... names CH-N5 as a 2304 x 1728 mm vault at lines 701-703. It does not define exterior walls, projection, complete footprint or position. Its F5ZE/V13 identity is separate from the protected unidentified working F5ZN-A 14-vault generator; it was read as evidence and not executed.

The source paths for the E5-C3-L1 lock and original F5ZM-C root JSON are absent on MR COMPUTER. The X01 embedded E5-R3-notes and E5-C3-handoff hashes could not be checked against those missing originals. A recovered E5-R1 handoff records southern morphology, not its exact site placement. Older E5-R1 experimental south coordinates must not be substituted for the protected lock.

Only 12 reconstructed/transformed X01 roots are screened, not the full 88-root source and not the missing 248-support F5ZL-C schedule. Continuous source walls remain continuous. The conditional chapel rectangle is retained in dashed red. N4-west window, N4-east opening, N6 door, chapter corridor, controlled cloister entry and stair zone are planning reservations.

## Preserved work
F5ZK-C, F5ZN-A, all approved architecture, working inner/middle vault generator and Pass 6J are unchanged. No Blender operation, vault regeneration, source replacement or approval promotion occurred. Bay angles, gallery datums and Q1/J1 radii remain unresolved and unselected. Study D/MP-01G were neither regenerated nor installed here.

## Validation
{qa['pass_count']} technical/2D checks pass; {qa['fail_count']} fail. This does not constitute architectural, historical, structural, accessibility or site approval. Checks cover input preservation, X01 metric regressions, polygon validity, JSON round-trip, 1.2 m swept reservations, pairwise known massing overlap and SVG physical scale. PDF visual QA is recorded separately after rendering.

## Deliverables and reproduction
- outputs/F5ZP_X02_R01_FLOOR_PLAN_REVIEW.pdf: four A3 vector pages.
- outputs/X02_NORTH_SECTOR_1to1.svg: metre coordinates; physical 1:1 SVG.
- outputs/X02_GEOMETRY.json: geometry, authority labels and explicit absent placements.
- outputs/X02_QA.json, X02_MEASUREMENTS.csv, X02_SENSITIVITY.json and X02_CONFLICT_REGISTER.csv.
- sources/: retained source package, GitHub reference and MR COMPUTER read-only evidence.

Run `python3 build_x02.py` with Python 3.12+, numpy, shapely, matplotlib and reportlab. No source generator is rebuilt. The script evaluates only X01's checked geometry prefix; original export commands are never run. Outputs are confined to outputs/.

## Next action
Recover actual CH-N5 exterior plan and the original southern E5-C3-L1 lock file/input pair; verify the opening and stair envelopes. Complete the missing site geometry and then review the northern-versus-southern alternative before any precinct-baseline selection.
'''
(ROOT/'README.md').write_text(report)
(ROOT/'requirements.txt').write_text('numpy>=1.26\nshapely>=2.0\nmatplotlib>=3.8\nreportlab>=4\n')
print(json.dumps({'status':qa['status'],'checks_pass':qa['pass_count'],'checks_fail':qa['fail_count'],'outputs':str(OUT),'metrics':metrics},indent=2))
