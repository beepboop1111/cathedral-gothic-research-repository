#!/usr/bin/env python3
"""R04 east-range floor plans and measured spiral-stair section.

Authored 1:1 design study, not a regulatory, fire or structural certification.
Requires shapely and reportlab. Only writes within this experiment.
"""
from pathlib import Path
import sys,json,math,hashlib,csv,textwrap
from itertools import combinations
from xml.sax.saxutils import escape
deps=Path(__file__).resolve().parent.parent/'.x04_deps'
if deps.exists():sys.path.append(str(deps))
from shapely.geometry import shape,mapping,Polygon,Point,LineString,box
from shapely.ops import unary_union
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
R=Path(__file__).resolve().parent;O=R/'outputs';O.mkdir(exist_ok=True)
src=R/'sources/R03_GEOMETRY.json';source_hash=hashlib.sha256(src.read_bytes()).hexdigest()
model=json.loads(src.read_text())
# R03 uses repeated names for body and wall roles: resolve both explicitly.
body={f['id']:shape(f['geometry']) for f in model['features'] if f['properties']['role']=='building'}
context_walls={f['id']:shape(f['geometry']) for f in model['features'] if f['properties']['role']=='wall'}
cx,cz=-23.,25.2
def octagon(across):
 rr=across/2/math.cos(math.pi/8)
 return Polygon([(cx+rr*math.cos(math.pi/8+i*math.pi/4),cz+rr*math.sin(math.pi/8+i*math.pi/4)) for i in range(8)])
def sector(rin,rout,a,b,n=96):
 count=max(2,math.ceil((b-a)/360*n))
 aa=[math.radians(a+(b-a)*i/count) for i in range(count+1)]
 return Polygon([(cx+rout*math.cos(t),cz+rout*math.sin(t)) for t in aa]+[(cx+rin*math.cos(t),cz+rin*math.sin(t)) for t in reversed(aa)])

H=3.6;N=20;RISE=H/N;PITCH=12.;A0=246.;ATOP=A0+(N-1)*PITCH
RIN=.62;ROUT=1.67;RWALK=(RIN+ROUT)/2
SLAB=.18;TARGET=2.10
turret=octagon(4.4);turret_inside=turret.buffer(-.45,join_style=2)
newel=Point(cx,cz).buffer(RIN,quad_segs=64)
treads=[{'id':i+1,'angle_start_deg':A0+i*PITCH,'angle_end_deg':A0+(i+1)*PITCH,
 'top_y_m':(i+1)*RISE,'geometry':sector(RIN,ROUT,A0+i*PITCH,A0+(i+1)*PITCH)} for i in range(N-1)]
flight=unary_union([t['geometry'] for t in treads])
aperture=sector(.60,1.70,A0,ATOP)
landing=turret_inside.difference(aperture).difference(newel)
landing_rect=box(-24.74,24.6,-23.69,25.8)
night_inner=body['night_range'].buffer(-.45,join_style=2)
res_inner=body['residential_range'].buffer(-.45,join_style=2)
night_floor=unary_union([night_inner,turret_inside]).difference(newel)
upper_night=night_floor.difference(aperture)
bridge=box(-29.85,27.4,-27.45,40.5)
bridge_clear=box(-29.55,27.4,-27.75,40.8)
bridge_wall=bridge.difference(box(-29.55,27.3,-27.75,40.6))

# Six upper chambers share a straight 1.50 m hall. Ground service access is
# deliberately kept as a cross-passage, not forced through a room.
hall=box(-24.95,41.45,-23.45,54.95)
common=box(-29.55,40.35,-23.45,44.85)
dz=(54.95-44.85-.30)/3
rows=[(44.85+i*(dz+.15),44.85+i*(dz+.15)+dz) for i in range(3)]
rooms_g={
 'G01 Reading parlour':box(-29.55,44.85,-25.10,47.35),
 'G02 Common room':box(-29.55,49.05,-25.10,54.95)}
rooms_u={}
for i,(z1,z2) in enumerate(rows):
 rooms_g[['G03 House office','G04 Linen store','G05 Workroom'][i]]=box(-23.30,z1,-18.95,z2)
 rooms_u[f'U0{i+1} Chamber {i+1}']=box(-29.55,z1,-25.10,z2)
 rooms_u[f'U0{i+4} Chamber {i+4}']=box(-23.30,z1,-18.95,z2)
service=box(-30.3,47.5,-24.95,48.9)
doors_g=[];doors_u=[]
for name,q in rooms_g.items():
 b=q.bounds;z=(b[1]+b[3])/2
 x=-25.025 if b[0]<-25 else -23.375
 doors_g.append((name,x,z,box(x-.25,z-.45,x+.25,z+.45)))
for name,q in rooms_u.items():
 b=q.bounds;z=(b[1]+b[3])/2
 x=-25.025 if b[0]<-25 else -23.375
 doors_u.append((name,x,z,box(x-.25,z-.45,x+.25,z+.45)))

def partition_walls(upper):
 w=[box(-25.10,44.7,-24.95,55.1),box(-23.45,44.7,-23.30,55.1)]
 for i in range(2):
  z=rows[i][1]
  w.append(box(-23.45,z,-18.9,z+.15))
  if upper:w.append(box(-29.6,z,-24.95,z+.15))
 if not upper:
  w.extend([box(-29.6,47.35,-24.95,47.5),box(-29.6,48.9,-24.95,49.05)])
 q=unary_union(w)
 if not upper:q=q.difference(service)
 for _,_,_,d in doors_u if upper else doors_g:q=q.difference(d)
 return q
parts_g=partition_walls(False);parts_u=partition_walls(True)
def shell(q,t=.45):return q.difference(q.buffer(-t,join_style=2))
def cut(q,holes):return q.difference(unary_union(holes))
# Story-specific openings. R03 bodies stay fixed; openings are now coordinated
# with the rooms and the proposed upper connecting passage.
res_base=shell(body['residential_range'])
window_specs=[]
for z1,z2 in rows:
 z=(z1+z2)/2
 window_specs.extend([(-18.5,z,'E'),(-30,z,'W')])
res_window_holes=[box(x-.7,z-.55,x+.7,z+.55) for x,z,_ in window_specs]
ground_res=cut(res_base,res_window_holes+[box(-30.7,41.3,-29.1,43.1),service])
upper_res=cut(res_base,res_window_holes+[box(-29.4,39.4,-27.9,40.9)])
night_base=shell(body['night_range'])
night_common_holes=[box(-30.7,24.5,-29.1,26.3),box(-26.0,24.6,-22.0,25.8)]
ground_night=cut(night_base,night_common_holes+[box(-25.5,21.8,-24.1,23.1)])
upper_night_wall=cut(night_base,night_common_holes+[box(-29.4,27.3,-27.9,28.8)])
turret_wall=cut(shell(turret),[box(-26,24.6,-23.8,25.8)])
floor_g=unary_union([night_floor,res_inner,body['chapter_vestibule'].buffer(-.45,join_style=2)])
floor_u=unary_union([upper_night,res_inner,bridge])
path_u=LineString([(-24.3,25.2),(-28.65,25.2),(-28.65,42.2),(-24.2,42.2),(-24.2,53.4)])
clear_u=unary_union([upper_night,bridge_clear,common,hall]+list(rooms_u.values())+[d for _,_,_,d in doors_u])
service_path=LineString([(-30.1,48.2),(-24.2,48.2)])
clear_g=unary_union([common,hall,service]+list(rooms_g.values())+[d for _,_,_,d in doors_g])
walls_u=unary_union([upper_res,upper_night_wall,turret_wall,bridge_wall,parts_u,newel])
walls_g=unary_union([ground_res,ground_night,turret_wall,parts_g,newel])

tests=[]
def ck(id,ok,detail):tests.append({'id':id,'result':'PASS' if bool(ok) else 'FAIL','detail':detail})
for n in ['night_range','residential_range','chapter_vestibule','chapter_house']:
 ck('SOURCE_BODY_'+n,body[n].is_valid,'R03 footprint read, not modified.')
for level,rooms in [('G',rooms_g),('U',rooms_u)]:
 for n,q in rooms.items():
  ck('ROOM_VALID_'+n,q.is_valid,'Valid room footprint.')
  ck('ROOM_WITHIN_RANGE_'+n,res_inner.buffer(1e-8).covers(q),'Within unchanged R03 residential-range interior.')
 for (a,q),(b,p) in combinations(rooms.items(),2):ck(level+'_ROOMS_SEPARATE_'+a+'_'+b,q.intersection(p).area<1e-8,'No room overlap.')
for i,t in enumerate(treads):
 ck('TREAD_CONTAINED_'+str(i+1),turret_inside.covers(t['geometry']),'Tread band inside enlarged turret interior.')
 ck('APERTURE_CLEARS_TREAD_'+str(i+1),t['geometry'].difference(aperture).area<1e-8,'Upper-floor aperture clears the entire tread footprint.')
ck('LEVEL_RISE',abs(N*RISE-H)<1e-12,'20 equal rises sum to exactly 3.600 m.')
ck('TREAD_COUNT',len(treads)==19,'19 goings between 20 risers; landing is not counted as another tread.')
ck('LANDING_RECTANGLE',landing.buffer(1e-8).covers(landing_rect),'1.05 x 1.20 m landing footprint contained in western landing zone.')
ck('LANDING_NOT_OVER_FLIGHT',landing.intersection(flight).area<1e-8,'Landing and flight are disjoint in plan.')
ck('UPPER_ROUTE_CLEAR',path_u.buffer(.60,join_style=2,cap_style=2).difference(clear_u).area<1e-8,'1.20 m route band connects landing, bridge, common hall and upper hall.')
ck('UPPER_ROUTE_NO_ACTUAL_WALL_COLLISION',path_u.buffer(.60,join_style=2,cap_style=2).intersection(walls_u).area<1e-8,'Route band tested against the exported floor-specific walls and newel.')
ck('UPPER_ROUTE_ON_FLOOR',path_u.buffer(.60,join_style=2,cap_style=2).difference(floor_u).area<1e-8,'Entire upper route band lies on the proposed upper floor.')
ck('GROUND_SERVICE_ROUTE_CLEAR',service_path.buffer(.60,cap_style=2).difference(clear_g).area<1e-8,'1.20 m route band through the preserved ground service entrance.')
ck('GROUND_SERVICE_NO_ACTUAL_WALL_COLLISION',service_path.buffer(.60,cap_style=2).intersection(walls_g).area<1e-8,'Service route tested against actual ground-floor proposal walls.')
for level,rooms,doors,domain in [('G',rooms_g,doors_g,clear_g),('U',rooms_u,doors_u,clear_u)]:
 for name,x,z,d in doors:
  q=rooms[name];mid=q.centroid
  route=LineString([(-24.2,z),(mid.x,z)])
  ck('DOOR_ACCESS_'+name,route.buffer(.40,cap_style=2).difference(domain).area<1e-8,'0.80 m route band through proposed 0.90 m room opening.')
  ck('DOOR_NO_ACTUAL_WALL_COLLISION_'+name,route.buffer(.40,cap_style=2).intersection(walls_g if level=='G' else walls_u).area<1e-8,'Room access band tested against floor-specific proposal walls.')
ck('NEWEL_CLEARANCE',newel.intersection(landing_rect).area<1e-8,'Landing footprint avoids the 1.24 m-diameter newel.')
ck('SOURCE_BYTES_UNCHANGED',source_hash==hashlib.sha256(src.read_bytes()).hexdigest(),'Original R03 model checksum unchanged.')
ck('RECOVERED_R03_HASH',source_hash=='f45d36620a57bc671e3d76e3c78ed50c36ee1dca1b76987b5663ae1fa1ca473c','Matches the recovered and verified R03 package input.')
going_inner=2*RIN*math.sin(math.radians(PITCH/2))
going_walk=2*RWALK*math.sin(math.radians(PITCH/2))
going_outer=2*ROUT*math.sin(math.radians(PITCH/2))
metrics={'ground_FFL_m':0,'upper_FFL_m':H,'slab_study_thickness_m':SLAB,'upper_floor_soffit_m':H-SLAB,
 'risers':N,'rise_m':RISE,'goings':N-1,'angle_per_going_deg':PITCH,'total_flight_rotation_deg':(N-1)*PITCH,
 'inner_radius_m':RIN,'outer_radius_m':ROUT,'tread_band_width_before_rails_m':ROUT-RIN,
 'walking_line_radius_m':RWALK,'going_inner_chord_m':going_inner,'going_walk_chord_m':going_walk,
 'going_outer_chord_m':going_outer,'going_walk_arc_m':RWALK*math.radians(PITCH),
 'pitch_at_walking_line_deg':math.degrees(math.atan(RISE/going_walk)),
 'two_rises_plus_walking_going_m':2*RISE+going_walk,
 'turret_across_flats_R03_m':4.0,'turret_across_flats_R04_m':4.4,
 'upper_headroom_control_plane_m':H+TARGET,'headroom_target_m':TARGET,
 'minimum_flight_clearance_to_control_plane_m':H+TARGET-treads[-1]['top_y_m'],
 'floor_aperture_overlap_with_flight_m2':flight.intersection(aperture).area,
 'stair_door_study_width_m':1.2,'upper_hall_width_m':1.5,'bridge_clear_width_m':1.8,
 'bridge_floor_area_m2':bridge.area,'bridge_open_gap_spans_m':[4.25,4.15],
 'ground_assigned_rooms':len(rooms_g),'upper_chambers':len(rooms_u),
 'upper_chambers_net_area_m2':sum(q.area for q in rooms_u.values())}
qa={'id':'F5ZP_X02_R04','status':'EXPERIMENTAL FLOOR-PLAN AND STAIR GEOMETRY STUDY',
 'source_R03_sha256':source_hash,'metrics':metrics,'checks':tests,
 'pass_count':sum(t['result']=='PASS' for t in tests),'fail_count':sum(t['result']=='FAIL' for t in tests),
 'validation_limits':['Roof is not modeled: +5.70 m is a required clear control plane, not a verified roof soffit.',
 'Tread band precedes handrail/guard detailing; no finished clear stair-width claim.',
 'Upper-link soffit is provisionally +3.420 m: chapter vestibule entry/vault height is not yet coordinated.',
 'Bridge spans, stair support, floor construction, fire/egress and occupancy classification require separate review.',
 'No actual cathedral masonry opening, vault generator or original model changed.'],
 'changes_from_R03':['Turret enlarged by 0.40 m across flats, same center.',
 'Upper passage added over west edge of the two gaps and chapter vestibule to connect night stair to dormitory.',
 'Floor-specific room partitions, openings and private stair geometry defined.']}
(O/'R04_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
if qa['fail_count']:raise ValueError([t for t in tests if t['result']=='FAIL'])
rooms_rows=[]
for lev,rooms in [('GROUND',rooms_g),('UPPER',rooms_u)]:
 for n,q in rooms.items():rooms_rows.append({'level':lev,'room':n,'net_area_m2':q.area,'geometry':mapping(q)})
with (O/'ROOM_SCHEDULE.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['level','room','net_area_m2']);w.writerows((r['level'],r['room'],f'{r["net_area_m2"]:.4f}') for r in rooms_rows)
with (O/'STAIR_SCHEDULE.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['riser','riser_angle_deg','bottom_Y_m','top_Y_m','following_surface'])
 for i in range(N):w.writerow([i+1,A0+i*PITCH,i*RISE,(i+1)*RISE,'landing' if i==N-1 else 'tread'])
geom={'id':'X02_R04','units':'metres','axes':'X east, Z north, Y vertical','source_R03_sha256':source_hash,
 'baseline_R03_bodies':{k:mapping(q) for k,q in body.items()},
 'active_R04_bodies':{k:mapping(turret if k=='stair_turret' else q) for k,q in body.items()},
 'turret_R04':mapping(turret),'upper_bridge':mapping(bridge),
 'rooms':rooms_rows,'ground_floor':mapping(floor_g),'upper_floor':mapping(floor_u),
 'floor_specific_walls':{'ground':mapping(walls_g),'upper':mapping(walls_u)},
 'stair':{'parameters':metrics,'aperture':mapping(aperture),
 'landing':mapping(landing),'treads':[{**{k:v for k,v in t.items() if k!='geometry'},'geometry':mapping(t['geometry'])} for t in treads]}}
(O/'R04_GEOMETRY.json').write_text(json.dumps(geom,separators=(',',':'))+'\n')

INK='#242a2e';GRAY='#a4aaad';RED='#a83e3e';PAPER='#fcfbf7';GREEN='#e6eadf';BLUE='#dfe9ef'
pdf=O/'F5ZP_X02_R04_GROUND_UPPER_AND_STAIR.pdf'
c=Canvas(str(pdf),pagesize=(297*mm,420*mm))
c.setTitle('F5ZP X02 R04 - East range ground floor, upper floor and stair section')
def head(title,sub,page,landscape=False):
 w,h=(420,297) if landscape else (297,420)
 c.setPageSize((w*mm,h*mm));c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',15)
 c.drawString(14*mm,(h-16)*mm,title);c.setFont('Helvetica',8);c.drawString(14*mm,(h-23)*mm,sub)
 c.setStrokeColor(HexColor(GRAY));c.setLineWidth(.4);c.line(14*mm,(h-28)*mm,(w-14)*mm,(h-28)*mm)
 c.setFont('Helvetica',7);c.drawString(14*mm,10*mm,'F5ZP X02 R04 | PREFERRED R03 COMPOSITION DEVELOPED | EXPERIMENTAL | 05 NOV 2026');c.drawRightString((w-14)*mm,10*mm,str(page))
def note(x,y,t,body,width=95):
 c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',9);c.drawString(x*mm,y*mm,t);y-=5.5;c.setFont('Helvetica',8)
 for para in body.split('\n'):
  for line in textwrap.wrap(para,width=int(width/1.5)) or ['']:c.drawString(x*mm,y*mm,line);y-=4
  y-=2
 return y-4
def panel(bounds,left,bottom,scale):
 xmin,zmin,xmax,zmax=bounds;s=1000/scale*mm
 def pt(x,z):return left*mm+(x-xmin)*s,bottom*mm+(z-zmin)*s
 def draw(q,fill=None,line=INK,lw=.4,dashed=False):
  c.setFillColor(HexColor(fill or PAPER));c.setStrokeColor(HexColor(line));c.setLineWidth(lw);c.setDash([2,1.5] if dashed else [])
  for a in getattr(q,'geoms',[q]):
   if a.is_empty:continue
   p=c.beginPath()
   for ring in [a.exterior,*a.interiors] if a.geom_type=='Polygon' else [a]:
    vs=list(ring.coords);p.moveTo(*pt(*vs[0]))
    for v in vs[1:]:p.lineTo(*pt(*v))
    if a.geom_type=='Polygon':p.close()
   c.drawPath(p,stroke=1,fill=int(fill is not None),fillMode=0)
  c.setDash([])
 def lab(x,z,t,size=6.5,bold=False):
  c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);c.drawCentredString(*pt(x,z),t)
 def dimh(x1,x2,z,t):
  c.setStrokeColor(HexColor(INK));c.setLineWidth(.35);c.setDash([]);c.line(*pt(x1,z),*pt(x2,z))
  for x in [x1,x2]:c.line(*pt(x-.06,z-.08),*pt(x+.06,z+.08))
  lab((x1+x2)/2,z+.15,t,6.5)
 return pt,draw,lab,dimh

def dim_vertical(pt,x,z1,z2,label):
 c.setStrokeColor(HexColor(INK));c.setLineWidth(.35);c.setDash([])
 c.line(*pt(x,z1),*pt(x,z2))
 for z in [z1,z2]:c.line(*pt(x-.08,z-.06),*pt(x+.08,z+.06))
 px,py=pt(x-.18,(z1+z2)/2)
 c.saveState();c.translate(px,py);c.rotate(90);c.setFillColor(HexColor(INK));c.setFont('Helvetica',6.5)
 c.drawCentredString(0,0,label);c.restoreState()

def floor_page(upper):
 page=2 if upper else 1
 head('R04 | UPPER FLOOR +3.600' if upper else 'R04 | GROUND FLOOR +0.000','1:100 at A3 portrait | east range, night stair and chapter connection | metres',page)
 bounds=(-33,21,-17.5,56.5);pt,d,t,dim=panel(bounds,18,28,100)
 c.saveState();clip=c.beginPath();clip.rect(18*mm,28*mm,155*mm,355*mm);c.clipPath(clip,stroke=0,fill=0)
 # Light context is the same in both plans; only this east-range study is cut in black.
 for n in ['chapter_house','chapter_vestibule']:
  d(body[n],fill='#f1f0e9',line='#b7bab7',lw=.25)
 for n in ['cloister','chapter_house','chapter_vestibule']:
  d(context_walls[n],fill='#c1c3bf',line='#c1c3bf',lw=.2)
 t(-20.2,34,'CHAPTER HOUSE',7);t(-26.8,34,'VESTIBULE',6)
 if upper:
  d(bridge,fill=BLUE,line='#7e919c',lw=.35)
  d(upper_night,fill=PAPER,line='#ccc9c0',lw=.2)
  d(res_inner,fill=PAPER,line='#ccc9c0',lw=.2)
  d(bridge_wall,fill=INK,line=INK,lw=.2)
  d(upper_res,fill=INK,line=INK,lw=.2);d(upper_night_wall,fill=INK,line=INK,lw=.2)
 else:
  d(bridge,line=GRAY,lw=.5,dashed=True)
  d(ground_res,fill=INK,line=INK,lw=.2);d(ground_night,fill=INK,line=INK,lw=.2)
 d(turret_wall,fill=INK,line=INK,lw=.2)
 d(parts_u if upper else parts_g,fill=INK,line=INK,lw=.15)
 rooms=rooms_u if upper else rooms_g
 for name,q in rooms.items():
  b=q.bounds;mx=(b[0]+b[2])/2;mz=(b[1]+b[3])/2
  words=name.split(' ',1);t(mx,mz+.22,words[1],6.5,True);t(mx,mz-.23,f'{q.area:.1f} m2',6)
  if upper:
   bed=box(b[0]+.3,b[1]+.25,b[0]+1.2,b[1]+2.25) if b[0]<-25 else box(b[2]-1.2,b[1]+.25,b[2]-.3,b[1]+2.25)
   d(bed,fill='#eef0e9',line='#777f82',lw=.3)
   d(LineString([(bed.bounds[0],bed.bounds[3]-.4),(bed.bounds[2],bed.bounds[3]-.4)]),line='#777f82',lw=.25)
   d(box(b[0]+.3,b[3]-.7,b[0]+1.6,b[3]-.15),fill='#eeede7',line='#888888',lw=.25)
 for name,x,z,q in doors_u if upper else doors_g:
  direction=-1 if x<-24 else 1
  d(LineString([(x,z-.45),(x+direction*.8,z-.45)]),line='#737b80',lw=.3)
 # Floor-level door leaves are diagrammatic and do not claim fire-door certification.
 for td in treads:
  q=td['geometry']
  d(q,fill=None,line='#9ea4a8' if upper or td['top_y_m']>1.2 else INK,lw=.3,dashed=upper or td['top_y_m']>1.2)
 d(newel,fill=INK,line=INK,lw=.15)
 d(landing_rect,line='#728a98',lw=.4,dashed=True)
 if upper:d(aperture,line=RED,lw=.5,dashed=True)
 t(-27.3,23.7,'STAIR LANDING' if upper else 'NIGHT LOBBY',6.5,True)
 t(-27.4,26.0,'+3.600' if upper else 'SACRISTY / STORE',6)
 t(-28.4,42.1,'COMMON LANDING' if upper else 'COMMON HALL',6,True)
 t(-24.2,44.1,'1.50 m',6);t(-24.2,43.7,'HALL',6)
 if not upper:t(-27.5,48.1,'SERVICE PASSAGE',5.6)
 t(-28.65,30.5,'UPPER LINK' if upper else 'BRIDGE OVERHEAD',5.8)
 # Section location and actual direction of travel along the curved flight.
 d(LineString([(-31.3,25.2),(-20.2,25.2)]),line='#788185',lw=.35,dashed=True)
 for x in [-31.3,-20.2]:
  d(LineString([(x,25.2),(x,24.93),(x-.08,25.05),(x,24.93),(x+.08,25.05)]),line=INK,lw=.5)
  t(x,24.65,'A',6.5,True)
 aa=[math.radians(A0+8+(ATOP-A0-16)*i/80) for i in range(81)]
 arrow=[(cx+RWALK*math.cos(a),cz+RWALK*math.sin(a)) for a in aa]
 if upper:arrow.reverse()
 d(LineString(arrow),line=INK,lw=.6)
 tip=arrow[-1];prev=arrow[-2];vx,vz=tip[0]-prev[0],tip[1]-prev[1];L=math.hypot(vx,vz);vx/=L;vz/=L
 d(LineString([(tip[0]-.16*vx+.07*vz,tip[1]-.16*vz-.07*vx),tip,(tip[0]-.16*vx-.07*vz,tip[1]-.16*vz+.07*vx)]),line=INK,lw=.6)
 t(-19.1,23.6,'DOWN' if upper else 'UP 20',6,True)
 dim(-30,-18.5,55.9,'11.50 m northern range')
 dim_vertical(pt,-31.25,39.9,55.4,'15.50 m northern range')
 if upper:dim(-29.85,-27.45,29.5,'2.40 m gross')
 dim(-25.2,-20.8,22.2,'4.40 m turret')
 # North arrow and scale bar.
 d(LineString([(-32.6,53),(-32.6,54.8)]),line=INK,lw=.5);t(-32.6,55.2,'N',7,True)
 dim(-32.4,-30.4,21.6,'2 m')
 c.restoreState()
 y=380
 if upper:
  notes=[('Upper floor proposal','FFL +3.600 m. Six chambers share a 1.50 m central hall; a common landing connects to the night stair through the new upper passage.'),
   ('Six chambers',f'Net room areas: 14.5 m2 on the west, 14.2 m2 on the east (rounded). Total chamber area {sum(q.area for q in rooms_u.values()):.2f} m2. Beds and cupboards show basic use, not occupancy certification.'),
   ('The necessary connection','The 2.40 m gross upper passage has a 1.80 m clear study band. It crosses two R03 gaps and the western part of the chapter vestibule, linking the previously separate ranges.'),
   ('Spans and vestibule clearance','The open spans are 4.25 m and 4.15 m. Bearings and roof remain to develop. The provisional soffit is +3.420 m over the west vestibule; its entry/vault height must be coordinated.'),
   ('Stair opening','The red dashed aperture clears the full 228-degree flight. The western landing remains outside the opening. A 1.05 x 1.20 m landing footprint is checked.'),
   ('R03 composition','Night room, northern range, chapter hall and vestibule footprints are retained. Turret enlargement and upper connection are explicit R04 changes.')]
 else:
  notes=[('Ground-floor arrangement','The night lobby/sacristy, chapter vestibule and northern common hall retain their R03 relationships. The northern block now has five assigned rooms plus its circulation.'),
   ('Service entry resolved','The existing western service connection becomes a 1.40 m cross-passage into the central hall. It does not pass through the reading parlour or common room.'),
   ('Ground rooms','Reading parlour; common room; house office; linen store; workroom. These are proposed program assignments, open to refinement.'),
   ('Night stair','The octagonal turret grows from 4.00 to 4.40 m across flats, keeping the same center. Twenty equal rises reach the proposed upper floor.'),
   ('Overhead connection','Gray dashes show the upper passage. It covers only a strip at the western edge of the gaps/court rather than filling the entire space.'),
   ('Geometry status','Defined proposal walls are black. Gray is context/projection. Red marks unresolved interfaces or the upper stair aperture. No original cathedral wall opening or vault geometry has changed.')]
 for a,b in notes:y=note(185,y,a,b,96)
 c.showPage()

floor_page(False);floor_page(True)

head('R04 | NIGHT STAIR - SECTION A-A','1:50 at A3 landscape | true center section above; developed walking-line section below | proposed levels',3,True)
# True vertical cut at Z=25.2, along the X diameter.
pt,d,t,dim=panel((-31,-.4,-20,6.2),20,140,50)
section_masonry=[box(-30,2.1,-29.55,H-SLAB),box(-25.2,2.1,-24.75,H-SLAB),box(-21.25,0,-20.8,5.7)]
for wall in section_masonry:
 # Spandrels above the 2.10 m ground doors are retained. The upper door
 # reaches the 5.70 m roof-control plane; the roof remains undesigned.
 d(wall,fill='#dadbd7',line=INK,lw=.45)
d(box(cx-RIN,0,cx+RIN,5.7),fill='#d2d4d1',line=INK,lw=.45)
d(box(-31,-.18,-20,0),fill='#d6d7d3',line=INK,lw=.45)
d(box(-30,H-SLAB,cx-.60,H),fill='#d6d7d3',line=INK,lw=.45)
d(box(cx+1.70,H-SLAB,-20.8,H),fill='#d6d7d3',line=INK,lw=.45)
# At the eastern diameter the stair intersects tread 10 at +1.800 m.
east_theta=360.;east_tread=next(ti for ti in treads if ti['angle_start_deg']<=east_theta<ti['angle_end_deg'])
d(box(cx+RIN,east_tread['top_y_m']-.12,cx+ROUT,east_tread['top_y_m']),fill='#d5d7d2',line=INK,lw=.45)
d(LineString([(-31,H+TARGET),(-20,H+TARGET)]),line=RED,lw=.6,dashed=True)
t(-26,5.92,'REQUIRED CLEAR CONTROL PLANE +5.700',7,True)
t(-27.9,3.84,'UPPER FFL +3.600',7,True);t(-27.9,.18,'GROUND +0.000',7,True)
t(-21.95,2.02,'TREAD 10',6.5)
t(-25.8,1.1,'WEST LANDINGS / DOOR',6)
t(-28,4.6,'NIGHT ROOM / UPPER LANDING',7)
dim_vertical(pt,-30.6,0,H,'3.600 m floor to floor')
c.setFillColor(HexColor(INK));c.setFont('Helvetica',8);c.drawString(20*mm,132*mm,'A-A is a true X/Y section at Z=25.200. Only intersected stair material is shown; the full flight is developed below.')

# Developed walking-line section: 19 goings and 20 risers, no false full-turn count.
gw=RWALK*math.radians(PITCH);run=(N-1)*gw
pt,d,t,dim=panel((-1.3,-.3,run+1.5,6.0),20,20,50)
stairs=[(-1.2,0),(0,0)]
for i in range(N):
 x=i*gw if i<N-1 else run
 stairs.append((x,(i+1)*RISE))
 if i<N-1:stairs.append(((i+1)*gw,(i+1)*RISE))
stairs.extend([(run+1.2,H)])
d(LineString(stairs),line=INK,lw=1)
t(run/2,4.55,'DEVELOPED ALONG MEAN WALKING LINE',7,True)
t(run/2,4.18,'Flight unrolled for measurement; roof headroom control is shown in A-A above.',6.5)
dim(0,run,-.12,f'19 goings / developed run {run:.3f} m')
t(-.6,.35,'GROUND',6.5);t(run+.6,H+.25,'UPPER',6.5)
for i in [0,4,9,14,19]:
 x=min(i*gw,run);t(x-.1,(i+1)*RISE+.17,str(i+1),5.8)
y=258
for title,bodytext in [
 ('Measured stair',f'20 risers x {RISE*1000:.0f} mm = {H:.3f} m. 19 goings at 12 degrees = 228 degrees of rotation. The upper landing is not counted as another tread.'),
 ('Treads and shell',f'Inner radius {RIN:.2f} m; outer {ROUT:.2f} m; tread band {ROUT-RIN:.2f} m before rail detailing. Turret 4.40 m across flats, wall study 0.45 m.'),
 ('Walking line',f'Mean radius {RWALK:.3f} m. Chord going {going_walk*1000:.1f} mm, arc going {gw*1000:.1f} mm. Local pitch {metrics["pitch_at_walking_line_deg"]:.1f} degrees. Inner/outer chords {going_inner*1000:.1f}/{going_outer*1000:.1f} mm.'),
 ('Headroom result',f'The aperture removes upper-floor obstruction over every tread. Required control plane +5.700 gives {metrics["minimum_flight_clearance_to_control_plane_m"]:.2f} m over the highest tread and 2.10 m over the landing. Roof geometry must preserve this envelope.'),
 ('Limits to the check','Geometry and access are checked for this proposal. Handrails, guarding, structural support, occupancy/escape strategy and the applicable stair standard remain separate design checks. This is not a claim of regulatory compliance.')]:y=note(270,y,title,bodytext,135)
c.showPage();c.save()

def paths(q):
 if q.is_empty:return []
 if q.geom_type=='Polygon':return ['M '+' L '.join(f'{x:.8f},{-z:.8f}' for x,z in rr.coords)+' Z' for rr in [q.exterior,*q.interiors]]
 if q.geom_type=='LineString':return ['M '+' L '.join(f'{x:.8f},{-z:.8f}' for x,z in q.coords)]
 return [p for a in q.geoms for p in paths(a)]
for lev in ['GROUND','UPPER']:
 upper=lev=='UPPER'
 layers=[('outer_range',upper_res if upper else ground_res,INK),('night',upper_night_wall if upper else ground_night,INK),
  ('turret',turret_wall,INK),('partitions',parts_u if upper else parts_g,INK),('newel',newel,INK)]
 if upper:
  layers.insert(0,('upper_passage',bridge,BLUE));layers.append(('upper_passage_walls',bridge_wall,INK))
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="15500mm" height="35500mm" viewBox="-33 -56.5 15.5 35.5">',f'<title>R04 {lev} floor; metre coordinates; physical 1:1; proposal</title>']
 for n,q,fill in layers:svg.append(f'<g id="{n}"><path d="'+ ' '.join(paths(q))+f'" fill="{fill}" fill-rule="evenodd" stroke="{INK}" stroke-width=".015"/></g>')
 for td in treads:svg.append('<path d="'+' '.join(paths(td['geometry']))+'" fill="none" stroke="#747b80" stroke-width=".014"/>')
 if upper:svg.append('<g id="proposed_upper_aperture"><path d="'+' '.join(paths(aperture))+f'" fill="none" stroke="{RED}" stroke-width=".02" stroke-dasharray=".10 .08"/></g>')
 for name,q in (rooms_u if upper else rooms_g).items():
  p=q.centroid;svg.append(f'<text x="{p.x}" y="{-p.y}" text-anchor="middle" font-family="sans-serif" font-size=".30">{escape(name)}</text>')
 svg.append('</svg>');(O/f'R04_{lev}_PLAN_1to1.svg').write_text('\n'.join(svg))

# Source-scale editable section: the second view is a developed measurement
# diagram translated 7 m below the true cut, not a second building section.
section_svg=['<svg xmlns="http://www.w3.org/2000/svg" width="12000mm" height="14000mm" viewBox="-31.5 -6.5 12 14">',
 '<title>R04 stair A-A: true section at Z=25.200; metre coordinates; physical 1:1</title>']
section_parts=section_masonry+[box(cx-RIN,0,cx+RIN,5.7),box(-31,-.18,-20,0),box(-30,H-SLAB,cx-.60,H),box(cx+1.70,H-SLAB,-20.8,H),box(cx+RIN,east_tread['top_y_m']-.12,cx+ROUT,east_tread['top_y_m'])]
for q in section_parts:section_svg.append('<path d="'+' '.join(paths(q))+f'" fill="#d6d7d3" stroke="{INK}" stroke-width=".012"/>')
section_svg.append('<path d="M -31,-5.7 L -20,-5.7" fill="none" stroke="'+RED+'" stroke-width=".015" stroke-dasharray=".10 .08"/>')
for x,y,txt in [(-27.8,6.0,'A-A | REQUIRED ROOF CLEARANCE CONTROL +5.700'),(-27.8,3.8,'UPPER +3.600'),(-27.8,.2,'GROUND +0.000'),(-27.8,-2.3,'DEVELOPED MEAN WALKING LINE - NOT A BUILDING CUT')]:
 section_svg.append(f'<text x="{x}" y="{-y}" font-family="sans-serif" font-size=".15" text-anchor="middle">{escape(txt)}</text>')
dev=LineString([(x-29.5,y-7) for x,y in stairs])
section_svg.append('<path d="'+' '.join(paths(dev))+f'" fill="none" stroke="{INK}" stroke-width=".018"/>')
section_svg.append('</svg>');(O/'R04_STAIR_SECTION_1to1.svg').write_text('\n'.join(section_svg))
references=[{'source':'Approved Document K (2013 edition), spiral and helical stairs, paragraph 1.28','url':'https://assets.publishing.service.gov.uk/media/60d5bdcde90e07716f516cfd/Approved_Document_K.pdf','use':'Points spiral/helical stair design to BS 5395-2; not a blanket compliance test for this project.'},
 {'source':'Government-commissioned evidence on domestic stairs, prepared 2023, published 2025','url':'https://assets.publishing.service.gov.uk/media/6900a48684b816d72cb9aa56/Evidence_to_support_potential_changes_to_Approved_Document_K_guidance_on_domestic_stairs.pdf','use':'Technical background only; report states its conclusions are not necessarily government policy. No project classification or statutory approval inferred.'}]
(O/'REFERENCE_AND_LIMITS.json').write_text(json.dumps(references,indent=2)+'\n')
(R/'README.md').write_text(f'''# F5ZP X02 R04 - East range floors and stair

EXPERIMENTAL ARCHITECTURAL DEVELOPMENT FROM THE PREFERRED R03 COMPOSITION.

Delivered: ground floor, upper floor and stair section A-A; developed walking-line section is shown below the true diameter cut. Plans are 1:100 at A3 portrait. Section is 1:50 at A3 landscape. Editable SVG plans use physical 1:1 dimensions and metre coordinates.

## Proposed arrangement
Ground: night lobby/sacristy and storage; existing chapter vestibule; northern common hall; five rooms (reading parlour, common room, office, linen store, workroom). The western service entrance has its own 1.40 m cross-passage into the 1.50 m central hall.

Upper: six chambers, total net {sum(q.area for q in rooms_u.values()):.3f} m2, around the 1.50 m hall. A new 2.40 m gross / 1.80 m clear study passage links night stair to northern range, above the western portion of the R03 gaps and chapter vestibule. Required open spans are 4.25 m and 4.15 m; their support is unverified. The provisional +3.420 m link soffit requires coordination with the chapter vestibule entry and any vault. This is the dependent change needed to make the preferred separated ranges function upstairs.

## Stair and vertical proposal
Ground FFL 0.000; upper FFL +3.600; slab study .180; soffit +3.420. Turret enlarges from 4.0 to 4.4 m across flats, same center (-23,25.2). Other principal R03 body footprints are unchanged.

20 risers at .180 m; 19 goings at 12 degrees; total rotation 228 degrees. Tread inner/outer radii .620/1.670 m, band 1.050 m before handrail detailing. Mean walking radius {RWALK:.3f}; chord going {going_walk:.6f}; developed arc going {gw:.6f}. No extra top tread is invented: riser 20 meets the upper landing.

The upper aperture covers all flight treads. A 1.05 x 1.20 m western landing footprint fits outside the flight and newel. The +5.700 control plane gives 2.10 m over upper landing and 2.28 m over highest tread. It is a required unobstructed envelope for future roofs, not verified roof headroom. No existing roof has been silently raised.

## Validation and source limits
{qa['pass_count']} source-preservation, room fit/access, stair containment, landing/aperture and route-band checks pass; {qa['fail_count']} fail. This is technical/geometric checking, not structural, fire/escape or regulatory approval. The chosen tread band is not a finished width after rails. Consult applicable spiral-stair design guidance and usage classification before any physical construction decision. External references are identified in outputs/REFERENCE_AND_LIMITS.json; no compliance conclusion is drawn from a straight-stair table.

Original R03 input hash: {source_hash}. It stays unchanged. All changes are confined to this R04 proposal. No cathedral geometry, vault generator or Pass 6J is rebuilt. F5ZL-C missing schedule remains unresolved. The candidate cathedral entrance and actual CH-N5 interface are outside this east-range task.

## Reproduction
python3 build_r04.py with shapely and reportlab. It reads the role-qualified R03 body/wall model, never executes a source generator, and writes outputs within this experiment. Full source copy and numerical schedules are included. PDF visual QA is performed after rendering.

## Next design stage
Develop bridge bearing and roof volumes around the reserved stair headroom and bedroom floor levels. Confirm the proposed room program and turret enlargement through architectural review. No baseline promotion is implied by the preferred design direction.
''')
print(json.dumps({'pass':qa['pass_count'],'fail':qa['fail_count'],'metrics':metrics},indent=2))
