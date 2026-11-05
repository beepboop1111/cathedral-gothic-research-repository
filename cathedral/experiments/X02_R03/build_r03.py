#!/usr/bin/env python3
"""R03: reopen precinct design assumptions; draw an architectural concept in 2D.
All measurements below are authored design-study values, never historic facts.
"""
from pathlib import Path
import sys,json,math,hashlib,csv
from itertools import combinations
from xml.sax.saxutils import escape
deps=Path(__file__).resolve().parent.parent/'.x02_deps'
if deps.exists():sys.path.append(str(deps))
from shapely.geometry import Polygon,box,Point,LineString,mapping,shape
from shapely.ops import unary_union
from shapely.affinity import rotate,translate
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
R=Path(__file__).resolve().parent;O=R/'outputs';O.mkdir(exist_ok=True)
source=R/'sources/R02_GEOMETRY.json';before=hashlib.sha256(source.read_bytes()).hexdigest()
old=json.loads(source.read_text());g={f['id']:shape(f['geometry']) for f in old['features']}
def octagon(cx,z,across):
 rr=(across/2)/math.cos(math.pi/8)
 return Polygon([(cx+rr*math.cos(math.pi/8+i*math.pi/4),z+rr*math.sin(math.pi/8+i*math.pi/4)) for i in range(8)])
def chamfer(x1,z1,x2,z2,ch):
 return Polygon([(x1+ch,z1),(x2-ch,z1),(x2,z1+ch),(x2,z2-ch),(x2-ch,z2),(x1+ch,z2),(x1,z2-ch),(x1,z1+ch)])
cx=-33.8277
bodies={
 'refectory':Polygon([(-59,46.7),(-56.5,44.9),(-32.5,44.9),(-32.5,53.4),(-56.5,53.4),(-59,51.6)]),
 'kitchen':box(-49,53.4,-39,61.4),
 'west_range':box(-58.5,26,-52,44.9),
 'residential_range':Polygon([(-30,39.9),(-23,39.9),(-23,44.4),(-18.5,44.4),(-18.5,55.4),(-30,55.4)]),
 'chapter_house':octagon(-17.5,34,12),
 'chapter_vestibule':box(-30,32.25,-23.5,35.75),
 'night_range':Polygon([(-30,22.4),(-24.5,22.4),(-23,23.9),(-23,28),(-30,28)]),
 'stair_turret':octagon(-23,25.2,4),
 'gate_hall':chamfer(cx-2,17.3,cx+3.2,21.3,.7),
}
cloister=g['cloister_outer'];garth=g['cloister_garden'];walks=cloister.difference(garth)
entry_garden=Polygon([(-48,15.2),(-46.3,14.25),(-35.9277,14.25),(-35.9277,18.75),(-48,18.75)])
root_features={n:q for n,q in g.items() if n.startswith('ROOT-')};roots=unary_union(list(root_features.values()))
link=g['n4_link']
service_link=box(-32.5,47,-30,49.4)
solid_bodies=unary_union(list(bodies.values())+[service_link])
chapter_court=box(-30,35.75,-20,41.4).difference(solid_bodies)
service_court=box(-38.5,55.4,-24,63.0).difference(solid_bodies)
arrival=Polygon([(-62.5,17),(-53,17),(-52,24),(-58.5,26),(-63,22)])

# Actual concept wall poche, not room-colored zoning blocks.
walls={n:q.difference(q.buffer(-(.60 if n=='chapter_house' else .45),join_style=2)) for n,q in bodies.items()}
walls['service_link']=service_link.difference(service_link.buffer(-.35,join_style=2))
walls['cloister']=cloister.difference(cloister.buffer(-.40,join_style=2))
doors=[('refectory',box(-42.8,44,-41.2,45.7)),('refectory',box(-44.7,52.6,-43.3,54.2)),
 ('kitchen',box(-44.7,52.6,-43.3,54.2)),('kitchen',box(-42.8,60.7,-41.2,62)),
 ('west_range',box(-52.8,33.1,-51.2,34.9)),('west_range',box(-59.3,28.2,-57.7,29.8)),
 ('residential_range',box(-30.8,41.3,-29.2,43.1)),
 ('chapter_vestibule',box(-30.8,33.0,-29.2,35.0)),('chapter_vestibule',box(-24.3,33,-22.7,35)),
 ('chapter_house',box(-24.3,33,-22.7,35)),
 ('night_range',box(-30.8,24.5,-29.2,26.3)),('night_range',box(-25.5,21.6,-24.2,23.2)),
 ('night_range',box(-25.8,24.4,-22,26)),('stair_turret',box(-25.8,24.4,-22,26)),
 ('gate_hall',box(cx-1.75,16.5,cx+1.75,18.1)),('gate_hall',box(cx-1.75,20.5,cx+1.75,22.1)),
 ('service_link',box(-33.2,47.5,-31.8,48.9)),('service_link',box(-30.7,47.5,-29.3,48.9)),
 ('refectory',box(-33.2,47.5,-31.8,48.9)),('residential_range',box(-30.7,47.5,-29.3,48.9))]
cloister_cuts=[box(-43,44.1,-41,45.7),box(-53,33,-51,35),box(-31,33,-29,35),
 box(-31,24.5,-29,26.3),box(-31,41.3,-29,43.1),box(cx-1.75,18.1,cx+1.75,19.7)]
for q in cloister_cuts:walls['cloister']=walls['cloister'].difference(q)
for n,q in doors:walls[n]=walls[n].difference(q)

windows=[]
def win(n,x,z,w=1.25,angle=0):
 # Local horizontal window cut, optionally rotated about its center.
 q=rotate(box(-w/2,-.8,w/2,.8),angle,origin=(0,0));q=translate(q,xoff=x,yoff=z)
 walls[n]=walls[n].difference(q);windows.append((x,z,w,angle))
for x in [-53.5,-50,-46.5,-43,-39.5,-36]:win('refectory',x,53.4)
for z in [31.4,36.5,41.6]:win('west_range',-58.5,z,1.1,90)
for x in [-46.5,-42]:win('kitchen',x,61.4)
for z in [46.5,50,53]:win('residential_range',-18.5,z,1.2,90)
for x in [-27.5,-24,-20.5]:win('residential_range',x,55.4,1.15)
for x in [-28,-25.7]:win('night_range',x,22.4,.8)
for angle in [0,45,90,135,225,270,315]:
 a=math.radians(angle);x=-17.5+6*math.cos(a);z=34+6*math.sin(a)
 win('chapter_house',x,z,1.55,angle-90)

buttresses=[]
for x,z in list(bodies['chapter_house'].exterior.coords)[:-1]:
 a=math.degrees(math.atan2(z-34,x+17.5))
 q=rotate(box(-.20,-.30,1.05,.30),a,origin=(0,0));q=translate(q,xoff=x,yoff=z)
 buttresses.append(q)

# Garden arcade rhythm: six bays on short sides, eight on long sides.
columns=[];corner_piers=[]
for x in [-48.5,-33.5]:
 for z in [22.4,41.4]:corner_piers.append(box(x-.30,z-.30,x+.30,z+.30))
for x in [-48.5,-33.5]:
 for i in range(1,8):columns.append(Point(x,22.4+i*19/8).buffer(.19,quad_segs=12))
for z in [22.4,41.4]:
 for i in range(1,6):columns.append(Point(-48.5+i*15/6,z).buffer(.19,quad_segs=12))
plinth=garth.boundary.buffer(.10,cap_style=2,join_style=2).difference(box(-40.5,21.9,-39,22.9))
basin=octagon(-41,31.9,2.2)
garden_paths=unary_union([box(-40.15,22.4,-39.35,41.4),box(-48.5,31.5,-33.5,32.3)]).difference(basin)
chapter_pier=Point(-17.5,34).buffer(.35,quad_segs=16)
all_wall=unary_union(list(walls.values())+buttresses+columns+corner_piers+[plinth,chapter_pier])

checks=[]
def ck(n,ok,detail):checks.append({'id':n,'pass':bool(ok),'detail':detail})
for n,q in bodies.items():ck('VALID_'+n,q.is_valid and not q.is_empty,'Defined concept footprint.')
for n,q in walls.items():ck('WALL_VALID_'+n,q.is_valid,'Valid concept wall and opening geometry.')
ck('N4_ROOT_SCREEN_UNCHANGED',abs(link.distance(roots)-.1956)<1e-9,'Same candidate throat; no approved door or clearance claim.')
ck('ENTRY_GARDEN_ROOT_SCREEN',entry_garden.intersection(roots).area<1e-8,'Retained 12-root screen only.')
ck('NEW_BODIES_ROOT_SCREEN',solid_bodies.intersection(roots).area<1e-8,'New precinct bodies avoid the screened roots.')
ck('GATE_HALL_GARTH_CLEAR',bodies['gate_hall'].intersection(garth).area<1e-8,'Gate hall stops inside the south covered walk.')
ck('GATE_HALL_ENTRY_GARDEN_CLEAR',bodies['gate_hall'].intersection(entry_garden).area<1e-8,'Arrival garden kept out of the gate hall.')
ck('VESTIBULE_JOINS_CHAPTER',bodies['chapter_vestibule'].distance(bodies['chapter_house'])<1e-9,'Short two-bay link joins octagon west face.')
ck('VESTIBULE_JOINS_WALK',bodies['chapter_vestibule'].distance(walks)<1e-9,'Chapter approach directly from east walk.')
ck('CLOISTER_ARCADE_COUNT',len(columns)==24 and len(corner_piers)==4,'28 conceptual arcade bays: 6+8+6+8, intentionally proposed anew.')
allowed={frozenset(['night_range','stair_turret']),frozenset(['gate_hall','cloister'])}
for a,b in combinations(bodies,2):
 area=bodies[a].intersection(bodies[b]).area
 if frozenset([a,b]) in allowed:continue
 ck('SEPARATE_'+a+'_'+b,area<1e-8,f'Non-overlapping bodies, area overlap {area:.8f} m2.')
ck('SOURCE_R02_UNCHANGED',before==hashlib.sha256(source.read_bytes()).hexdigest(),'R02 retained byte-for-byte.')
qa={'revision':'X02_R03','status':'REOPENED ARCHITECTURAL DESIGN STUDY','checks':checks,'pass_count':sum(t['pass'] for t in checks),'fail_count':sum(not t['pass'] for t in checks),
 'authority':'User authorized reconsidering the layout and earlier locks. This is a new design proposal; adoption not implied.',
 'source_sha256':before,'units':'metres; 1 SVG coordinate unit = 1 m',
 'design_values':{'chapter_across_flats_m':12,'chapter_area_m2':bodies['chapter_house'].area,'chapter_vestibule_m':[6.5,3.5],
  'cloister_outer_m':[22,26],'cloister_garden_m':[15,19],'arcade_bays':28,'wall_thickness_study_m':.45,'chapter_wall_study_m':.60},
 'not_validated':['masonry capacity','finished door/window clearances','actual CH-N5 exterior','new stair rise/height','site boundaries','roof and flying-buttress clearance'],
 'preservation':'No vault generator, cathedral geometry, original research or previous scheme edited.'}
(O/'R03_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
if qa['fail_count']:raise ValueError([t for t in checks if not t['pass']])
features=[]
for typ,items in [('building',bodies),('wall',walls),('court',{'chapter_court':chapter_court,'service_court':service_court,'arrival':arrival,'garth':garth,'entry_garden':entry_garden}),
                  ('link',{'n4_link':link,'service_link':service_link})]:
 for n,q in items.items():features.append({'type':'Feature','id':n,'properties':{'role':typ,'status':'DEFINED R03 CONCEPT - UNAPPROVED'},'geometry':mapping(q)})
for typ,items in [('buttress',buttresses),('column',columns),('corner_pier',corner_piers)]:
 for i,q in enumerate(items):features.append({'type':'Feature','id':typ+str(i),'properties':{'role':typ,'status':'CONCEPT ONLY'},'geometry':mapping(q)})
model={'type':'FeatureCollection','id':'X02_R03','units':'metres','authority':qa['authority'],'features':features}
(O/'R03_GEOMETRY.json').write_text(json.dumps(model,separators=(',',':'))+'\n')

INK='#242629';GRAY='#a8adb1';RED='#b23c3c';GREEN='#e4e8dc';STONE='#d7d6cf';PAPER='#fcfbf7'
pdf=O/'F5ZP_X02_R03_ARCHITECTURAL_REDESIGN.pdf';c=Canvas(str(pdf),pagesize=(420*mm,297*mm))
c.setTitle('F5ZP X02 R03 - Architectural precinct redesign')
def header(t,sub,page):
 c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',17);c.drawString(14*mm,282*mm,t)
 c.setFont('Helvetica',8);c.drawString(14*mm,275*mm,sub);c.setStrokeColor(HexColor(GRAY));c.line(14*mm,270*mm,406*mm,270*mm)
 c.setFont('Helvetica',7);c.drawString(14*mm,10*mm,'X02 R03 | NEW ARCHITECTURAL PROPOSAL | EARLIER LAYOUT ASSUMPTIONS REOPENED | 05 NOV 2026');c.drawRightString(406*mm,10*mm,str(page))
def panel(bounds,left,bottom,scale):
 x1,z1,x2,z2=bounds;s=1000/scale*mm
 def pt(x,z):return left*mm+(x-x1)*s,bottom*mm+(z-z1)*s
 def draw(q,fill=None,line=INK,lw=.45,dash=False):
  c.setLineWidth(lw);c.setStrokeColor(HexColor(line));c.setFillColor(HexColor(fill or PAPER));c.setDash([2,1.7] if dash else [])
  for a in getattr(q,'geoms',[q]):
   if a.is_empty:continue
   p=c.beginPath()
   rings=[a.exterior,*a.interiors] if a.geom_type=='Polygon' else [a]
   for ring in rings:
    vs=list(ring.coords);p.moveTo(*pt(*vs[0]))
    for v in vs[1:]:p.lineTo(*pt(*v))
    if a.geom_type=='Polygon':p.close()
   c.drawPath(p,stroke=1,fill=int(fill is not None),fillMode=0)
  c.setDash([])
 def text(x,z,t,size=7,bold=False):
  c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);c.setFillColor(HexColor(INK));c.drawCentredString(*pt(x,z),t)
 return pt,draw,text
def note(x,y,t,lines):
 c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',10);c.drawString(x*mm,y*mm,t);y-=6;c.setFont('Helvetica',9)
 import textwrap
 for p in lines.split('\n'):
  for line in textwrap.wrap(p,82):c.drawString(x*mm,y*mm,line);y-=4.5
  y-=2
 return y-4
header('X02 R03 | A CLOISTER PRECINCT WITH ARCHITECTURAL CHARACTER','1:250 at A3 | authored design geometry in black; unresolved cathedral interfaces in red | metres',1)
pt,d,t=panel((-66,8,-6,65),14,27,250)
d(arrival,fill='#f0eee6',line='#babbb5',lw=.25)
d(service_court,fill='#f0eee6',line='#babbb5',lw=.25)
d(chapter_court,fill='#edf0e6',line='#babbb5',lw=.25)
d(garth,fill=GREEN,line='#b0b8a4',lw=.4)
d(entry_garden,fill=GREEN,line='#b0b8a4',lw=.4)
d(garden_paths,fill='#f4f1e8',line='#cdc9bf',lw=.2)
for q in bodies.values():d(q,fill=PAPER,line='#c0bdb3',lw=.25)
d(walks,fill=PAPER,line='#c0bdb3',lw=.25)
d(link,fill=PAPER,line='#c0bdb3',lw=.3)
d(service_link,fill=PAPER,line='#c0bdb3',lw=.25)
d(all_wall,fill=INK,line=INK,lw=.2)
for x,z,w,a in windows:
 q=translate(rotate(LineString([(-w/2,0),(w/2,0)]),a,origin=(0,0)),xoff=x,yoff=z)
 d(q,line='#727a7e',lw=.35)
d(basin,fill='#d9e4e6',line=INK,lw=.5)
for n,q in root_features.items():d(q,fill=STONE,line='#747570',lw=.35)
d(g['wall'],fill=STONE,line='#747570',lw=.35)
d(g['chapel_reference'],line=RED,lw=.8,dash=True)
d(g['NIGHT_R2'],line=RED,lw=.7,dash=True)
for z in [22.4+i*19/8 for i in range(9)]:
 for x in [-50.25,-31.75]:
  d(LineString([(x-.9,z),(x+.9,z)]),line=GRAY,lw=.25,dash=True)
for x in [-48.5+i*2.5 for i in range(7)]:
 for z in [20.65,43.15]:d(LineString([(x,z-.9),(x,z+.9)]),line=GRAY,lw=.25,dash=True)
for x,z in list(bodies['chapter_house'].exterior.coords)[:-1]:d(LineString([(-17.5,34),(x,z)]),line=GRAY,lw=.35,dash=True)
d(LineString([(-26.75,32.25),(-26.75,35.75)]),line=GRAY,lw=.4,dash=True)
# Stair symbol is a diagram only; it deliberately carries no riser count.
spiral=[]
for i in range(81):
 a=math.radians(30+i*3.5);rr=.25+1.2*i/80;spiral.append((-23+rr*math.cos(a),25.2+rr*math.sin(a)))
d(LineString(spiral),line='#6e7174',lw=.5)
for x,z,label,size in [(-42.5,49.0,'REFECTORY',7.5),(-44,57.3,'KITCHEN',7),(-55.2,36,'GUEST RANGE',6),
 (-24,50,'RESIDENTIAL RANGE',7),(-41,35.6,'CLOISTER GARTH',8.5),(-41,27.5,'GARDEN',7),
 (-17.5,32.0,'CHAPTER HOUSE',7),(-26.8,34,'VESTIBULE',5.8),(-27.1,25.2,'NIGHT LOBBY',5.5),
 (-41,16.8,'HERB GARDEN',6),(-25.2,38.5,'CHAPTER COURT',5.5),(-29.7,59.3,'SERVICE COURT',6),
 (-58.0,21.5,'ARRIVAL COURT',6),(-31,13.4,'CH-N5 / UNRESOLVED',5.5)]:t(x,z,label,size,True)
t(-62,63,'NORTH ^',7,True)
d(LineString([(-62,11),(-52,11)]),line=INK,lw=.65);t(-57,11.8,'10 m',6.5)
y=259
for title,body in [
 ('01 / An arrival sequence','A small chamfered gate hall introduces the covered walk. The herb garden and arrival court frame the approach instead of a loose collection of room blocks.'),
 ('02 / A legible cloister','Real wall poche, arcade piers, openings and indicative bay rhythm make the court read as an architectural enclosure. The garden is a place within the building.'),
 ('03 / A distinctive chapter house','An octagonal hall becomes the focal building, approached through a short two-bay vestibule. Corner buttresses and a central pier are concept geometry only.'),
 ('04 / Articulated ranges','A stepped residential range, a separate night-stair turret, canted refectory end and kitchen range create varied courts and roof volumes for later development.'),
 ('05 / Earlier assumptions reopened','The prior rectangular chapter hall, continuous east wing, porch and arcade arrangement are open to redesign. This is a new precinct proposal; previous schemes remain recoverable.'),
 ('Drawing status','Black shows defined geometry within this proposal, not approved construction. Gray dashes are indicative set-out. Red marks the unverified cathedral/chapel interface. No stair height, structural capacity or roof solution is claimed.')]:y=note(265,y,title,body)
c.showPage()

header('X02 R03 | FROM PROGRAM BLOCKS TO AN ARCHITECTURAL PLAN','Same 1:350 physical scale in both views | design-study comparison; no scheme adoption implied',2)
for left,concept in [(20,False),(212,True)]:
 pt,d,t=panel((-66,8,-6,65),left,72,350)
 if concept:
  d(garth,fill=GREEN,line='#b0b8a4',lw=.25);d(entry_garden,fill=GREEN,line='#b0b8a4',lw=.25)
  d(walks,fill=PAPER,line='#bbb8b0',lw=.2)
  for q in bodies.values():d(q,fill=PAPER,line='#bbb8b0',lw=.2)
  d(link,fill=PAPER,line='#bbb8b0',lw=.2);d(all_wall,fill=INK,line=INK,lw=.15)
  d(basin,fill='#d9e4e6',line=INK,lw=.35)
 else:
  for n in ['cloister_outer','cloister_garden','east_wing','chapter_hall','refectory','new_garden','n4_link']:
   d(g[n],fill='#f3eeee',line='#a33737',lw=.5,dash=True)
 for q in root_features.values():d(q,fill=STONE,line='#747570',lw=.2)
 d(g['wall'],fill=STONE,line='#747570',lw=.3)
 t(-36,63,'R03 / ARCHITECTURAL REDESIGN' if concept else 'R02 / PLANNING ENVELOPES',10,True)
y=57
note(20,y,'Design values reopened','Chapter house: octagonal, 12 m across flats. Vestibule: 6.5 x 3.5 m. Cloister: 22 x 26 m retained, now drawn with 28 conceptual arcade bays. Wall studies: 0.45 m ranges, 0.60 m chapter. These values are new design proposals.')
note(212,y,'What is still a separate design task','The N4 cathedral opening and CH-N5 remain unresolved. The red N6 route is a reservation. Roofs, stair rise, physical masonry and the final relationship to the southern scheme need further architectural development.')
c.showPage();c.save()

# Editable physical 1:1 SVG uses the same wall and footprint geometry.
def paths(q):
 if q.is_empty:return []
 if q.geom_type=='Polygon':return ['M '+' L '.join(f'{x:.7f},{-z:.7f}' for x,z in ring.coords)+' Z' for ring in [q.exterior,*q.interiors]]
 if q.geom_type=='LineString':return ['M '+' L '.join(f'{x:.7f},{-z:.7f}' for x,z in q.coords)]
 return [p for a in q.geoms for p in paths(a)]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="60000mm" height="57000mm" viewBox="-66 -65 60 57">',
 '<title>X02 R03 authored precinct concept; physical 1:1; no authority promotion</title>']
layers=[('arrival',arrival,'#f0eee6','#babbb5'),('service_court',service_court,'#f0eee6','#babbb5'),
 ('chapter_court',chapter_court,'#edf0e6','#babbb5'),('garth',garth,GREEN,'#b0b8a4'),('entry_garden',entry_garden,GREEN,'#b0b8a4'),
 ('garden_paths',garden_paths,'#f4f1e8','#cdc9bf')]
layers += [(n,q,PAPER,'#c0bdb3') for n,q in bodies.items()]
layers += [('walks',walks,PAPER,'#c0bdb3'),('gallery',link,PAPER,'#c0bdb3'),('service_link',service_link,PAPER,'#c0bdb3'),
 ('walls',all_wall,INK,INK),('basin',basin,'#d9e4e6',INK),('reference_wall',g['wall'],STONE,'#747570')]
for n,q,fill,line in layers:
 svg.append(f'<g id="{n}"><path d="'+ ' '.join(paths(q))+f'" fill="{fill}" fill-rule="evenodd" stroke="{line}" stroke-width=".025"/></g>')
for n,q in root_features.items():svg.append('<path d="'+' '.join(paths(q))+f'" fill="{STONE}" stroke="#747570" stroke-width=".025"/>')
for x,z,w,a in windows:
 q=translate(rotate(LineString([(-w/2,0),(w/2,0)]),a,origin=(0,0)),xoff=x,yoff=z)
 svg.append('<path d="'+' '.join(paths(q))+'" fill="none" stroke="#727a7e" stroke-width=".025"/>')
svg.append('<path d="'+' '.join(paths(g['chapel_reference']))+f'" fill="none" stroke="{RED}" stroke-width=".04" stroke-dasharray=".18 .10"/>')
for x,z,label in [(-42.5,49,'REFECTORY'),(-44,57.3,'KITCHEN'),(-55.2,36,'GUEST RANGE'),(-24,50,'RESIDENTIAL RANGE'),
 (-41,35.6,'CLOISTER GARTH'),(-17.5,32,'CHAPTER HOUSE'),(-26.8,34,'VESTIBULE'),(-27.1,25.2,'NIGHT LOBBY')]:
 svg.append(f'<text x="{x}" y="{-z}" text-anchor="middle" font-family="sans-serif" font-size=".48" fill="{INK}">{escape(label)}</text>')
svg.append('</svg>');(O/'R03_ARCHITECTURAL_PLAN_1to1.svg').write_text('\n'.join(svg))
(R/'README.md').write_text(f'''# X02 R03 - Architectural precinct redesign

Status: NEW DESIGN STUDY; former precinct layout assumptions reopened by user instruction. This records the requested redesign, not automatic adoption into the cathedral baseline.

The previous plans were functional envelopes. R03 develops a connected architectural composition: arcaded cloister, chamfered entrance hall, octagonal chapter house with buttresses and a short two-bay vestibule, stepped residential range, night stair turret, canted refectory, kitchen range, herb garden and distinct arrival/chapter/service courts. Concept walls have doors and windows cut into them. These are authored proposals, not recovered historical or existing geometry.

User direction: "Locked architecture can be unlocked ... not a huge fan of how the layout looks ... a bunch of squares and rectangles." Scope applied: reconsider the precinct masses, hall form, range arrangement, gateway, courts and arcade rhythm. Source R02 is preserved byte-for-byte. The cathedral vault generators and geometry are not involved in this 2D design change.

## New design values
Octagonal chapter house: 12 m across flats, {bodies['chapter_house'].area:.3f} m2 footprint before buttresses. Vestibule 6.5 x 3.5 m in two 3.25 m concept bays, replacing the R02 9 m vestibule. The 22 x 26 m cloister and 15 x 19 m garden remain as useful proportions; arcade rhythm is proposed as 28 bays (6+8+6+8), not inherited as a lock. Wall thicknesses .45 m and chapter .60 m are graphic design-study values with no structural acceptance. The turret stair symbol carries no rise or tread count.

## Drawing convention
Black solid/poche = defined geometry within this authored concept, not source verification or construction approval. Gray dashed = indicative set-out. Red dashed = unresolved cathedral interface / chapel test. All new architecture remains a proposal. Prior schemes and the southern baseline are retained as historical references, rather than used as a prohibition on this design study.

## Validation
{qa['pass_count']} geometry/preservation checks pass, {qa['fail_count']} fail. New bodies, wall cuts and garden are valid; unintended body overlaps screened; chapter vestibule meets hall/walk; root screen unchanged; source hash unchanged. The night room/turret union and gate hall/cloister overlap are deliberate architectural joins. Only 12 transformed X01 roots are available. Stair height, actual chapel footprint, finished openings, roof/flyer interfaces, site boundaries, structural capacity and missing F5ZL-C schedule are not resolved by this concept.

## Reproduction
python3 build_r03.py with shapely and reportlab. Reads sources/R02_GEOMETRY.json only and writes within this experiment. Native coordinates are metres; source reference uses the inherited experimental E5-S2 context. SVG is physical 1:1; PDF scales are 1:250 and 1:350 at A3. PNG is a preview.

## Review
Assess the architectural composition and circulation character before detailed profiles, roofs or additional modeling. The red N4/CH-N5 and N6 interfaces remain named design holds; no cathedral wall opening has been created.
''')
print(json.dumps({'pass':qa['pass_count'],'fail':qa['fail_count'],'chapter_area_m2':bodies['chapter_house'].area,'building_count':len(bodies),'wall_opening_count':len(doors)+len(windows),'arcade_bays':28},indent=2))
