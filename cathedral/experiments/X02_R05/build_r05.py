#!/usr/bin/env python3
"""R05 architectural bearing set-out and roof composition, metres / glTF Y up.
Source R04 is read only. Structural member sizes are design-study assumptions.
"""
from pathlib import Path
import sys,json,hashlib,math,struct,csv,textwrap
from collections import Counter
sys.path.append(str(Path(__file__).resolve().parent.parent/'.x04_deps'))
import numpy as np
from shapely.geometry import shape,mapping,Polygon,Point,LineString,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles,set_precision
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
R=Path(__file__).resolve().parent;O=R/'outputs';V=R/'previews'
base=R/'sources/R04_GEOMETRY.json';H0=hashlib.sha256(base.read_bytes()).hexdigest()
d=json.loads(base.read_text());b={k:shape(v) for k,v in d['active_R04_bodies'].items()}
par=d['stair']['parameters'];roof_thick=.18
checks=[]
def ck(n,v,detail=''):checks.append({'id':n,'result':'PASS' if bool(v) else 'FAIL','detail':detail})
ck('R04_VERIFIED_BYTES',H0=='54e2066ba97b2b787f2976b07c055fa9a4053087a9d3504f88617a06618c52a5')
# Four bearing stations, each with west/east piers. New supports, NOT F5ZL-C.
xs=[-29.70,-27.60];stations=[27.65,32.60,35.40,40.25]
piers=[{'id':f'P{i+1}{side}','x':x,'z':z,'geometry':box(x-.35,z-.35,x+.35,z+.35)} for i,z in enumerate(stations) for side,x in zip(['W','E'],xs)]
beams=[];seats=[]
for si,(za,zb) in enumerate(zip(stations[:-1],stations[1:])):
 for side,x in zip(['W','E'],xs):
  bid=f'G{si+1}{side}';q=box(x-.15,za,x+.15,zb)
  beams.append({'id':bid,'geometry':q,'span_clear_m':zb-za-.7,'length_m':zb-za,'bottom_Y_m':2.97,'top_Y_m':3.42})
  for end,z,sign in [('S',za,1),('N',zb,-1)]:
   seat=box(x-.15,min(z,z+sign*.35),x+.15,max(z,z+sign*.35));p=next(p for p in piers if p['x']==x and abs(p['z']-z)<1e-8)
   seats.append({'id':bid+'_'+end,'pier':p['id'],'geometry':seat,'length_m':.35,'area_m2':seat.area})
   ck('SEAT_CONTAINED_'+bid+end,p['geometry'].buffer(1e-8).covers(seat),'350 mm seat, nominal contact area 0.105 m2; capacity unverified.')
   ck('SEAT_AREA_'+bid+end,abs(seat.area-.105)<1e-8)
vest_path=box(-30.4,33.1,-23.1,34.9)
ck('VESTIBULE_1_8M_ROUTE_NO_PIERS',vest_path.intersection(unary_union([p['geometry'] for p in piers])).area<1e-8)
ck('VESTIBULE_LOCAL_CLEAR_WIDTH',abs((stations[2]-.35)-(stations[1]+.35)-2.10)<1e-9)
ck('WEST_CLEAR_HEIGHT',abs(3.6-.18-.45-2.97)<1e-9,'Floor 3.600, deck 180 mm, girder 450 mm.')
ck('VESTIBULE_CLEAR_HEIGHT_TARGET',2.97>=2.10,'Ground route is flat-headed in the western crossing zone.')
# Roof underside planes. Wall plate heights refer to underside, not slate top.
raw=[];roof_specs=[]
def add_face(name,q,a,c0,c1):
 if q.area>1e-9:raw.append({'id':name,'polygon':q,'plane':[a,c0,c1]})
def gable(name,q,axis,ridge,plate,run,slope=1):
 # run = distance from ridge to external WALL face, before eaves overhang.
 # q is already the roof footprint including any overhang.
 if axis=='Z':
  halves=[(q.intersection(box(-100,-100,ridge,100)),slope,0,plate+slope*run-slope*ridge),
          (q.intersection(box(ridge,-100,100,100)),-slope,0,plate+slope*run+slope*ridge)]
 else:
  halves=[(q.intersection(box(-100,-100,100,ridge)),0,slope,plate+slope*run-slope*ridge),
          (q.intersection(box(-100,ridge,100,100)),0,-slope,plate+slope*run+slope*ridge)]
 for i,(p,a,bb,c) in enumerate(halves):add_face(name+'_'+str(i+1),p,a,bb,c)
 roof_specs.append({'id':name,'form':'gable','ridge_axis':axis,'wall_plate_underside_m':plate,'ridge_underside_m':plate+run*slope,'pitch_deg':math.degrees(math.atan(slope))})
def pyramid(name,q,eave,apex):
 c=q.centroid;vs=list(q.exterior.coords)
 for i,(p1,p2) in enumerate(zip(vs[:-1],vs[1:])):
  poly=Polygon([p1,p2,(c.x,c.y)]);a,bb,cc=np.linalg.solve(np.array([[*p1,1],[*p2,1],[c.x,c.y,1]]),np.array([eave,eave,apex]));add_face(name+'_'+str(i+1),poly,float(a),float(bb),float(cc))
 roof_specs.append({'id':name,'form':'octagonal pavilion','outer_eave_underside_m':eave,'apex_underside_m':apex})
gable('NORTH_MAIN',box(-30.25,44.4,-18.25,55.65),'Z',-24.25,6.35,5.75)
gable('NORTH_NECK',box(-30.25,39.65,-22.75,44.9),'Z',-26.5,6.35,3.5)
gable('UPPER_LINK',box(-30.05,27.20,-27.25,40.75),'Z',-28.65,6.35,1.2,.8)
gable('NIGHT_RANGE',b['night_range'].buffer(.25,join_style=2),'X',25.2,6.35,2.8)
pyramid('STAIR_TURRET',b['stair_turret'].buffer(.20,join_style=2),6.05,9.55)
gable('VESTIBULE_EAST',box(-27.45,32.10,-23.20,35.90),'X',34.0,4.00,1.75)
pyramid('CHAPTER_HOUSE',b['chapter_house'].buffer(.30,join_style=2),5.30,11.60)
# Trim roofs to their visible upper envelope. Positive half-plane clipping.
def positive_half(A,B,C):
 pts=[(-100,-100),(100,-100),(100,100),(-100,100)];res=[]
 for p,q in zip(pts,pts[1:]+pts[:1]):
  u=A*p[0]+B*p[1]+C;v=A*q[0]+B*q[1]+C
  if u>=0:res.append(p)
  if (u>=0)!=(v>=0):
   t=u/(u-v);res.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
 return Polygon(res) if len(res)>=3 else Polygon()
faces=[]
for i,f in enumerate(raw):
 q=f['polygon'];a,bb,c=f['plane']
 for j,g in enumerate(raw):
  if i==j or q.is_empty:continue
  inter=q.intersection(g['polygon'])
  if inter.area<1e-10:continue
  A,B,C=np.array(g['plane'])-np.array(f['plane'])
  if abs(A)+abs(B)<1e-10:above=inter if C>1e-9 or (abs(C)<1e-9 and j<i) else Polygon()
  else:above=inter.intersection(positive_half(A,B,C))
  q=q.difference(above)
 if q.area>1e-8:faces.append({**f,'polygon':q})
raw_union=unary_union([f['polygon'] for f in raw]);vis_union=unary_union([f['polygon'] for f in faces])
ck('ROOF_ENVELOPE_COVERS_RAW',raw_union.symmetric_difference(vis_union).area<1e-7)
for k in ['residential_range','night_range','stair_turret','chapter_house','chapter_vestibule']:
 ck('ROOF_COVERS_'+k,b[k].difference(vis_union).area<1e-7)
ck('ROOF_COVERS_LINK',shape(d['upper_bridge']).difference(vis_union).area<1e-7)
for i,f in enumerate(faces):
 ck('ROOF_FACE_VALID_'+str(i),f['polygon'].is_valid and f['polygon'].area>0)
 for g in faces[i+1:]:ck('ROOF_NO_PLAN_OVERLAP_'+f['id']+'_'+g['id'],f['polygon'].intersection(g['polygon']).area<1e-7)
def roof_min_over(q):
 vals=[]
 for f in faces:
  inter=q.intersection(f['polygon']);a,bb,c=f['plane']
  for p in getattr(inter,'geoms',[inter]):
   if p.geom_type=='Polygon':vals.extend(a*x+bb*z+c for x,z in p.exterior.coords)
 return min(vals)
landing=shape(d['stair']['landing']);flight=unary_union([shape(t['geometry']) for t in d['stair']['treads']])
landing_roof_min=roof_min_over(landing);flight_roof_min=roof_min_over(flight)
ck('STAIR_ROOF_COVERS_LANDING',landing.difference(vis_union).area<1e-8)
ck('STAIR_ROOF_ABOVE_RESERVED_PLANE',min(landing_roof_min,flight_roof_min)>=5.7-1e-8)
ck('LANDING_ACTUAL_ROOF_CLEARANCE',landing_roof_min-3.6>=2.1-1e-8)
clear_treads=[]
for t in d['stair']['treads']:
 v=roof_min_over(shape(t['geometry']))-t['top_y_m'];clear_treads.append(v);ck('ROOF_HEADROOM_TREAD_'+str(t['id']),v>=2.1)
for room in d['rooms']:
 if room['level']=='UPPER':ck('ROOM_ROOF_ABOVE_CEILING_'+room['room'],roof_min_over(shape(room['geometry']))>=6.3)
# Meshing uses constrained polygon triangles, including floor holes.
meshes=[];colors={'stone':[.70,.65,.54,1],'wall':[.84,.81,.72,1],'timber':[.32,.19,.10,1],'roof':[.20,.29,.34,1],'floor':[.65,.63,.55,1],'glass':[.48,.66,.72,1]}
solids=[]
def prism(name,q,lo,hi,material):
 if q.is_empty:return
 solids.append((name,q,lo,hi,material))
 for ni,p in enumerate(getattr(q,'geoms',[q])):
  if p.geom_type!='Polygon' or p.area<1e-9:continue
  p=set_precision(p,1e-5)
  if p.is_empty:continue
  vertices=[];inds=[];lookup={}
  def vert(x,z,y):
   key=tuple(round(float(v),9) for v in [x,y,z])
   if key not in lookup:lookup[key]=len(vertices);vertices.append(key)
   return lookup[key]
  def val(v,x,z):return v(x,z) if callable(v) else v
  for tri in constrained_delaunay_triangles(p).geoms:
   vs=list(tri.exterior.coords)[:3]
   dx,dz=np.array(vs[1])-vs[0];ex,ez=np.array(vs[2])-vs[0]
   if dx*ez-dz*ex<0:vs.reverse()
   bot=[vert(x,z,val(lo,x,z)) for x,z in vs];top=[vert(x,z,val(hi,x,z)) for x,z in vs]
   inds.extend([bot,[top[0],top[2],top[1]]])
  for ri,ring in enumerate([p.exterior,*p.interiors]):
   vs=list(ring.coords);ar=sum(x*z2-x2*z for (x,z),(x2,z2) in zip(vs[:-1],vs[1:]))
   if (ar>0)!=(ri==0):vs.reverse()
   for (x,z),(xx,zz) in zip(vs[:-1],vs[1:]):
    ba=vert(x,z,val(lo,x,z));ta=vert(x,z,val(hi,x,z));bb=vert(xx,zz,val(lo,xx,zz));tb=vert(xx,zz,val(hi,xx,zz));inds.extend([[ba,ta,tb],[ba,tb,bb]])
  vv=np.array(vertices,dtype=np.float32);ii=np.array(inds,dtype=np.uint32)
  # Tiny overlay remnants may collapse at float32 precision: filter them.
  area=np.linalg.norm(np.cross(vv[ii[:,1]]-vv[ii[:,0]],vv[ii[:,2]]-vv[ii[:,0]]),axis=1)
  ii=ii[area>1e-10]
  meshes.append({'name':name+(f'_{ni}' if ni else ''),'vertices':vv,'indices':ii,'material':material})
newel=Point(-23,25.2).buffer(.62,quad_segs=64)
wg=shape(d['floor_specific_walls']['ground']).difference(newel);wu=shape(d['floor_specific_walls']['upper']).difference(newel)
prism('R04_ground_wall_study',wg,0,3.42,'wall');prism('R04_upper_wall_study',wu,3.6,6.0,'wall')
prism('R04_upper_floor',shape(d['upper_floor']),3.42,3.6,'floor')
prism('Ground_floor',shape(d['ground_floor']),-.15,0,'floor')
prism('Chapter_ground_floor',b['chapter_house'],-.15,0,'floor')
prism('R04_stair_newel',newel,0,5.7,'stone')
for t in d['stair']['treads']:prism('R04_tread_'+str(t['id']),shape(t['geometry']),t['top_y_m']-.12,t['top_y_m'],'stone')
# R04 coordinate footprints, schematic vertical chapter/vestibule context.
for k,ht in [('chapter_house',5.30),('chapter_vestibule',3.85)]:
 q=b[k].difference(b[k].buffer(-.45,join_style=2))
 if k=='chapter_house':q=q.difference(box(-24.2,33.1,-22.8,34.9))
 else:q=q.difference(box(-30.8,33.1,-22.8,34.9))
 if k=='chapter_vestibule':
  prism(k+'_west_below_link',q.intersection(box(-100,-100,-27.45,100)),0,3.42,'wall')
  q=q.intersection(box(-27.45,-100,100,100))
 prism(k+'_wall_study',q,0,ht,'wall')
 for f in faces:
  a,bb,c0=f['plane'];part=q.intersection(f['polygon'])
  prism(k+'_roof_closure_'+f['id'],part,ht,lambda x,z,a=a,bb=bb,c0=c0:a*x+bb*z+c0,'wall')
for p in piers:prism(p['id'],p['geometry'],0,2.97,'stone')
for g in beams:prism(g['id'],g['geometry'],2.97,3.42,'timber')
# Close gables and the upper window heads against the measured roof envelope.
# The body union avoids adding a fictitious internal wall at the night/turret join.
upper_bodies=unary_union([b['night_range'],b['residential_range'],b['stair_turret'],shape(d['upper_bridge'])])
upper_ring=upper_bodies.difference(upper_bodies.buffer(-.30,join_style=2))
for f in faces:
 a,bb,c0=f['plane'];part=upper_ring.intersection(f['polygon'])
 prism('Roof_bearing_wall_'+f['id'],part,6.0,lambda x,z,a=a,bb=bb,c0=c0:a*x+bb*z+c0,'wall')
# Joists across the link, below the deck, independent of the two girders.
for z in np.arange(28.2,39.9,.60):prism('Link_joist_'+f'{z:.2f}',box(-29.7,z-.045,-27.6,z+.045),3.24,3.42,'timber')
for f in faces:
 a,bb,c=f['plane'];prism('Roof_'+f['id'],f['polygon'],lambda x,z,a=a,bb=bb,c=c:a*x+bb*z+c,lambda x,z,a=a,bb=bb,c=c:a*x+bb*z+c+roof_thick,'roof')
# Vertical gable upstands close discontinuous roof steps at volume junctions.
for i,f in enumerate(faces):
 for g in faces[i+1:]:
  shared=f['polygon'].boundary.intersection(g['polygon'].boundary)
  for line in getattr(shared,'geoms',[shared]):
   if line.geom_type!='LineString' or line.length<1e-5:continue
   mid=line.interpolate(.5,normalized=True);p=np.array([mid.x,mid.y,1]);delta=np.dot(np.array(f['plane'])-g['plane'],p)
   if abs(delta)<=roof_thick+1e-5:continue
   high,low=(f,g) if delta>0 else (g,f)
   A,B,C=np.array(high['plane'])-low['plane']
   q=line.buffer(.12,cap_style=2).intersection(high['polygon']).intersection(positive_half(A,B,C-roof_thick-1e-5))
   a,bb,cc=low['plane'];aa,bbb,ccc=high['plane']
   prism('Roof_step_'+high['id']+'_'+low['id'],q,lambda x,z,a=a,bb=bb,cc=cc:a*x+bb*z+cc+roof_thick,lambda x,z,aa=aa,bbb=bbb,ccc=ccc:aa*x+bbb*z+ccc,'wall')
# Test the actual 3D extrusions, including vestibule wall heights.
upper_route=LineString([(-24.3,25.2),(-28.65,25.2),(-28.65,42.2),(-24.2,42.2),(-24.2,53.4)]).buffer(.6,join_style=2,cap_style=2)
for label,route,y0,y1 in [('GROUND_VESTIBULE',vest_path,0,2.97),('UPPER_PASSAGE',upper_route,3.6,5.7)]:
 conflicts=[]
 for name,q,lo,hi,mat in solids:
  it=q.intersection(route)
  if it.area<1e-8:continue
  pts=[pt for poly in getattr(it,'geoms',[it]) if poly.geom_type=='Polygon' for pt in poly.exterior.coords]
  if not pts:continue
  low=min(lo(x,z) if callable(lo) else lo for x,z in pts);high=max(hi(x,z) if callable(hi) else hi for x,z in pts)
  if low<y1-1e-7 and high>y0+1e-7:conflicts.append(name)
 ck(label+'_ACTUAL_3D_VOLUME_CLEAR',not conflicts,str(conflicts))
# Roof penetrations and bearing connections are a geometric set-out only.
for m in meshes:
 ck('MESH_FINITE_'+m['name'],np.isfinite(m['vertices']).all())
 ck('MESH_NONDEGENERATE_'+m['name'],len(m['indices'])>0 and min(np.linalg.norm(np.cross(m['vertices'][m['indices'][:,1]]-m['vertices'][m['indices'][:,0]],m['vertices'][m['indices'][:,2]]-m['vertices'][m['indices'][:,0]]),axis=1))>1e-10)
 edges=Counter(tuple(sorted((int(tr[k]),int(tr[(k+1)%3])))) for tr in m['indices'] for k in range(3))
 ck('MESH_CLOSED_'+m['name'],all(v==2 for v in edges.values()),'Each object is a closed shell; separate objects may intentionally contact.')
# Minimal GLB 2.0 writer with separate objects; normals are per-vertex.
buf=bytearray();views=[];accessors=[]
def accessor(arr,kind,component):
 while len(buf)%4:buf.append(0)
 off=len(buf);data=arr.tobytes();buf.extend(data);vi=len(views);views.append({'buffer':0,'byteOffset':off,'byteLength':len(data)})
 ac={'bufferView':vi,'componentType':component,'count':len(arr),'type':kind}
 if kind=='VEC3':ac.update(min=arr.min(axis=0).astype(float).tolist(),max=arr.max(axis=0).astype(float).tolist())
 accessors.append(ac);return len(accessors)-1
materials=[{'name':k,'pbrMetallicRoughness':{'baseColorFactor':v,'metallicFactor':0,'roughnessFactor':.85},'doubleSided':True} for k,v in colors.items()]
gm=[];nodes=[]
for m in meshes:
 vv=m['vertices'];ii=m['indices'];norm=np.zeros_like(vv)
 face=np.cross(vv[ii[:,1]]-vv[ii[:,0]],vv[ii[:,2]]-vv[ii[:,0]])
 for j in range(3):np.add.at(norm,ii[:,j],face)
 ln=np.linalg.norm(norm,axis=1);norm/=np.where(ln>0,ln,1)[:,None]
 pa=accessor(vv,'VEC3',5126);na=accessor(norm.astype(np.float32),'VEC3',5126);ia=accessor(ii.flatten(),'SCALAR',5125)
 gm.append({'name':m['name'],'primitives':[{'attributes':{'POSITION':pa,'NORMAL':na},'indices':ia,'material':list(colors).index(m['material'])}]});nodes.append({'name':m['name'],'mesh':len(gm)-1})
gltf={'asset':{'version':'2.0','generator':'Cathedral R05 measured design study'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':gm,'materials':materials,'buffers':[{'byteLength':len(buf)}],'bufferViews':views,'accessors':accessors,'extras':{'units':'metres','axes':'X east, Y up, Z north','status':'EXPERIMENTAL, no structural certification'}}
jb=json.dumps(gltf,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);buf+=b'\x00'*((-len(buf))%4)
glb=struct.pack('<4sII',b'glTF',2,12+8+len(jb)+8+len(buf))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(buf),b'BIN\x00')+buf
(O/'F5ZP_X02_R05_ROOF_AND_BEARING_STUDY.glb').write_bytes(glb)
ck('GLB_LENGTH',struct.unpack_from('<I',glb,8)[0]==len(glb));ck('SOURCE_UNCHANGED',hashlib.sha256(base.read_bytes()).hexdigest()==H0)
metrics={'bearing_stations_Z_m':stations,'girder_centers_X_m':xs,'piers':8,'pier_size_m':[.7,.7,2.97],'girders':6,'girder_section_m':[.30,.45],'bearing_length_m':.35,'nominal_seat_area_m2':.105,'clear_spans_m':[4.25,2.1,4.15],'west_vestibule_clear_width_m':2.10,'west_vestibule_clear_height_m':2.97,'reserved_stair_plane_m':5.7,'roof_min_over_upper_landing_m':landing_roof_min,'upper_landing_min_roof_headroom_m':landing_roof_min-3.6,'min_tread_roof_headroom_m':min(clear_treads),'upper_flat_ceiling_m':6.3,'upper_room_clear_height_m':2.7,'roof_skin_vertical_thickness_m':roof_thick,'mesh_objects':len(meshes),'GLB_bytes':len(glb)}
qa={'id':'F5ZP_X02_R05','status':'EXPERIMENTAL ARCHITECTURAL SET-OUT AND ROOF COMPOSITION','parent_R04_SHA256':H0,'metrics':metrics,'checks':checks,'pass_count':sum(x['result']=='PASS' for x in checks),'fail_count':sum(x['result']=='FAIL' for x in checks),'limits':['Pier, girder, joist and bearing dimensions are unverified structural sizing assumptions; loads, deflection, connections, foundations and capacity not certified.','Western vestibule uses flat timber ceiling under link; no low pointed masonry arch imposed. Eastern vestibule remains taller.','Roof clearance checked against this generated roof skin only; future rafters, ties, linings and services must retain the reserved envelope.','Roof flashings, gutters, valleys, drainage and weatherproof junction details remain design work.','3D walls are schematic extrusions of R04 plan cuts; full window/door heads, room ceilings and historic details are not modeled.','No approved cathedral geometry or working vault generator changed. F5ZL-C missing support schedule remains unresolved.']}
(O/'R05_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
if qa['fail_count']:raise ValueError([q for q in checks if q['result']=='FAIL'])
geo={'id':'X02_R05','units':'metres','axes':'X east, Z north, Y vertical','parent_R04_SHA256':H0,'piers':[{**{k:v for k,v in p.items() if k!='geometry'},'geometry':mapping(p['geometry'])} for p in piers],'girders':[{**{k:v for k,v in g.items() if k!='geometry'},'geometry':mapping(g['geometry'])} for g in beams],'seats':[{**{k:v for k,v in s.items() if k!='geometry'},'geometry':mapping(s['geometry'])} for s in seats],'roofs':[{'id':f['id'],'polygon':mapping(f['polygon']),'underside_plane_Y_equals_aX_bZ_c':f['plane']} for f in faces],'roof_schedule':roof_specs,'metrics':metrics}
(O/'R05_GEOMETRY.json').write_text(json.dumps(geo,separators=(',',':'))+'\n')
with (O/'R05_BEARING_SCHEDULE.csv').open('w',newline='') as ff:
 w=csv.writer(ff,lineterminator='\n');w.writerow(['seat','pier','length_m','nominal_area_m2','status']);w.writerows([s['id'],s['pier'],'.350','.105','EXPERIMENTAL sizing; capacity unresolved'] for s in seats)
with (O/'R05_ROOF_SCHEDULE.csv').open('w',newline='') as ff:
 w=csv.writer(ff,lineterminator='\n');w.writerow(['roof','form','plate_or_eave_underside_m','ridge_or_apex_underside_m','pitch_deg']);w.writerows([s['id'],s['form'],s.get('wall_plate_underside_m',s.get('outer_eave_underside_m')),s.get('ridge_underside_m',s.get('apex_underside_m')),s.get('pitch_deg','facet planes in JSON')] for s in roof_specs)
# Technical axonometric preview of the exported mesh, matching X/Y/Z data.
fig=plt.figure(figsize=(13,11));ax=fig.add_subplot(111,projection='3d');polys=[];cc=[]
for m in meshes:
 vv=m['vertices'];ii=m['indices']
 for tri in ii:
  a=vv[tri];polys.append(np.column_stack([a[:,0],a[:,2],a[:,1]]));cc.append(colors[m['material']])
coll=Poly3DCollection(polys,facecolors=cc,edgecolors=(.1,.1,.1,.06),linewidths=.1,shade=True,lightsource=matplotlib.colors.LightSource(azdeg=310,altdeg=45));ax.add_collection3d(coll)
ax.set(xlim=(-32,-10),ylim=(21,57),zlim=(0,13));ax.set_box_aspect([22,36,13]);ax.view_init(elev=28,azim=-40);ax.set_axis_off();fig.tight_layout(pad=0);fig.savefig(V/'R05_AXON.png',dpi=140,facecolor='#f8f6f0');plt.close(fig)
# PDF drawings.
INK='#242b30';GRAY='#a6adaf';BLUE='#557587';RED='#a53d3d'
c=Canvas(str(O/'F5ZP_X02_R05_BEARINGS_CLEARANCE_AND_ROOFS.pdf'),pagesize=(297*mm,420*mm),invariant=1)
def head(title,sub,num,land=False):
 W,H=(420,297) if land else (297,420);c.setPageSize((W*mm,H*mm));c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',15);c.drawString(14*mm,(H-16)*mm,title);c.setFont('Helvetica',8);c.drawString(14*mm,(H-23)*mm,sub);c.setStrokeColor(HexColor(GRAY));c.line(14*mm,(H-28)*mm,(W-14)*mm,(H-28)*mm);c.setFont('Helvetica',7);c.drawString(14*mm,10*mm,'F5ZP X02 R05 | EXPERIMENTAL ARCHITECTURAL DEVELOPMENT | 05 NOV 2026');c.drawRightString((W-14)*mm,10*mm,str(num))
def note(x,y,title,body,width=95):
 c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',9);c.drawString(x*mm,y*mm,title);c.setFont('Helvetica',8);y-=5
 for line in textwrap.wrap(body,int(width/1.45)):c.drawString(x*mm,y*mm,line);y-=4
 return y-8
def panel(bounds,x0,y0,scale):
 xmin,zmin,xmax,zmax=bounds;s=1000/scale*mm
 def pt(x,z):return (x0*mm+(x-xmin)*s,y0*mm+(z-zmin)*s)
 def draw(q,fill=None,line=INK,dash=False,lw=.4):
  c.setStrokeColor(HexColor(line));c.setFillColor(HexColor(fill or '#ffffff'));c.setLineWidth(lw);c.setDash([2,1.5] if dash else [])
  for poly in getattr(q,'geoms',[q]):
   if poly.is_empty:continue
   p=c.beginPath()
   rings=[poly.exterior,*poly.interiors] if poly.geom_type=='Polygon' else [poly]
   for ring in rings:
    vv=list(ring.coords);p.moveTo(*pt(*vv[0]));[p.lineTo(*pt(*v)) for v in vv[1:]]
    if poly.geom_type=='Polygon':p.close()
   c.drawPath(p,fill=fill is not None,stroke=True,fillMode=0)
  c.setDash([])
 def lab(x,z,text,size=6.5):c.setFillColor(HexColor(INK));c.setFont('Helvetica',size);c.drawCentredString(*pt(x,z),text)
 return pt,draw,lab
head('R05 | PASSAGE BEARING PLAN','1:100 at A3 | new support set-out below retained R04 upper passage | metres',1)
pt,dr,lab=panel((-32,21,-16,56.5),18,28,100)
c.saveState();clip=c.beginPath();clip.rect(18*mm,28*mm,160*mm,355*mm);c.clipPath(clip,stroke=0,fill=0)
for k in ['night_range','residential_range','chapter_house','chapter_vestibule']:dr(b[k],line=GRAY,lw=.35)
dr(shape(d['upper_bridge']),fill='#e4edf1',line=BLUE)
dr(vest_path.intersection(b['chapter_vestibule']),fill='#f0ead8',line='#a39364',dash=True)
for g in beams:dr(g['geometry'],fill='#b89b7b',line='#786149')
for p in piers:
 dr(p['geometry'],fill=INK);lab(p['x']+(-.95 if p['x']<-29 else .95),p['z'],p['id'],6)
for z in stations:lab(-25.5,z,f'Z {z:.2f}',6)
lab(-28.65,30.1,'4.25 m',7);lab(-28.65,37.9,'4.15 m',7);lab(-26.2,34,'2.10 m clear',6.5)
lab(-25,54,'R04 NORTH RANGE',7);lab(-26.6,24,'R04 NIGHT ROOM',6.5)
dr(LineString([(-27.6,22),(-27.6,55)]),line=GRAY,dash=True);lab(-27.6,55.8,'B-B',7)
dr(LineString([(-31,34),(-24,34)]),line=GRAY,dash=True);lab(-31,34.5,'C-C',7)
c.restoreState()
y=380
for title,txt in [('Architectural load path','Light timber-framed link walls and the retained floor sit on two longitudinal girder lines. Six girder pieces seat on eight masonry piers at four stations.'),('Bearing set-out','Girder centerlines X -29.700 and -27.600. Piers 0.70 x 0.70 m. Each end has a 0.35 m seat and nominal 0.105 m2 contact area.'),('Members for this study','Girder section 0.30 x 0.45 m; top +3.420, underside +2.970. Short joists span between the girder lines. Sizes are assumptions for structural review.'),('Vestibule resolved in section','The piers leave a 2.10 m local width. The checked 1.80 m route band avoids every pier. Flat timber ceiling in the west keeps 2.97 m height; the eastern approach has a taller roof.'),('Protected source','R04 floor levels, rooms, stair and principal footprints are retained. New supports are R05 items, not recovered F5ZL-C supports.'),('Still unresolved','Loads, timber deflection, joints, masonry stress and foundations. Architectural contact and clearance do not establish structural adequacy.')]:y=note(185,y,title,txt)
c.showPage()
# Section helper: actual roof-envelope intersection with a vertical cut.
def roof_section(axis,fixed):
 out=[];line=LineString([(fixed,-100),(fixed,100)]) if axis=='Z' else LineString([(-100,fixed),(100,fixed)])
 for f in faces:
  it=f['polygon'].intersection(line);a,bb,cc=f['plane']
  for ls in getattr(it,'geoms',[it]):
   if ls.geom_type=='LineString' and ls.length>1e-8:
    pts=list(ls.coords);out.append(LineString([(z if axis=='Z' else x,a*x+bb*z+cc) for x,z in pts]))
 return out
def draw_section(axis,fixed,bounds):
 line=LineString([(fixed,-100),(fixed,100)]) if axis=='Z' else LineString([(-100,fixed),(100,fixed)])
 for name,q,lo,hi,mat in solids:
  it=q.intersection(line)
  for ls in getattr(it,'geoms',[it]):
   if ls.geom_type!='LineString' or ls.length<1e-7:continue
   vs=list(ls.coords);bot=[(z if axis=='Z' else x,lo(x,z) if callable(lo) else lo) for x,z in vs];top=[(z if axis=='Z' else x,hi(x,z) if callable(hi) else hi) for x,z in reversed(vs)]
   p=Polygon(bot+top).intersection(box(*bounds))
   if p.area>1e-8:dr(p,fill={'wall':'#e3dfd2','stone':'#c9c1af','timber':'#a78968','floor':'#ccc8ba','roof':'#b0c4ce'}[mat],line=INK,lw=.25)
head('R05 | COORDINATED SECTIONS','B-B 1:125 | C-C 1:100 | D-D stair 1:100 | true cuts and proposed elevations',2,True)
pt,dr,lab=panel((21,-.5,57,13),20,151,125)
draw_section('Z',-27.6,(21,-.5,57,13))
dr(LineString([(22,3.6),(56,3.6)]),line=GRAY,dash=True);lab(52,3.9,'FFL +3.600',7)
lab(30.1,1.3,'4.25 m gap',7);lab(37.8,1.3,'4.15 m gap',7);lab(25,10.8,'B-B | X=-27.600',8)
lab(45,10.8,'RANGE ROOF UNDERSIDE',7)
# C-C includes whole chapter approach, not an invented developed projection.
pt,dr,lab=panel((-31,-.5,-10,13),20,18,100)
draw_section('X',34,(-31,-.5,-10,13))
lab(-28.65,2.5,'2.97 m',7);lab(-17.5,1,'CHAPTER HOUSE',7);lab(-25.8,3.1,'TALLER EAST',6.5)
lab(-24.5,12.4,'C-C | Z=34.000',8)
# True east-west cut through the saved stair, showing only intersected tread.
pt,dr,lab=panel((-25.8,-.4,-20.2,10.1),255,18,100)
draw_section('X',25.2,(-25.8,-.4,-20.2,10.1))
dr(LineString([(-25.5,5.7),(-20.5,5.7)]),line=RED,dash=True)
lab(-23,6.0,'RESERVED +5.700',6.5);lab(-23,9.9,'D-D | STAIR Z=25.200',8);lab(-24.3,3.9,'+3.600',6.5)
note(365,215,'Measured roof clearance',f'Landing: {landing_roof_min-3.6:.3f} m minimum to generated roof underside. Minimum over all saved treads: {min(clear_treads):.3f} m.',40)
note(365,158,'Ceiling control','Upper rooms: +6.300 flat ceiling, 2.700 m clear. Roof planes clear it. Rafters and ties must respect these controls.',40)
note(365,90,'Section limits','Roof skin is modeled. Rafters, foundations and historic vaults are not certified or inferred.',40)
c.showPage()
head('R05 | EAST-RANGE ROOF COMPOSITION','1:150 at A3 | visible roof envelope with intersections trimmed | underside levels in schedule',3)
pt,dr,lab=panel((-32,20,-10,57),18,75,150)
for k in ['night_range','residential_range','chapter_house','chapter_vestibule']:dr(b[k],line=GRAY,dash=True)
for i,f in enumerate(faces):dr(f['polygon'],fill=['#d3dfe4','#e1e8e9'][i%2],line=BLUE,lw=.45)
for x,z,txt in [(-24.25,50,'NORTH MAIN'),(-26.5,42,'LOWER NECK'),(-28.65,30.2,'UPPER LINK'),(-26.8,25.2,'NIGHT RANGE'),(-23,25.2,'TURRET'),(-25.2,34,'VESTIBULE'),(-17.5,34,'CHAPTER')]:lab(x,z,txt,5.8)
y=380
for title,txt in [('Roof hierarchy','A tall gabled residential block steps down through the narrower neck. A lower link connects to the night range; an octagonal turret roof marks the stair. The chapter-house pavilion remains a separate major volume.'),('Range roof','Main underside ridge +12.100, wall plate +6.350, 45 degrees. Neck ridge +9.850 at the same plate level. Proposed upper room ceiling +6.300.'),('Link and night roofs','Link underside ridge +7.310, slope 0.8 (38.7 degrees). Night ridge +9.150, 45 degrees. Low link keeps the larger roof forms distinct.'),('Octagonal roofs','Turret outer eave underside +6.050, apex +9.550. Chapter outer eave underside +5.300, apex +11.600. These are new R05 design choices.'),('Vestibule transition','Eastern vestibule ridge +5.750, 45 degrees. It meets the higher link wall at the west and the chapter roof at the east. West ceiling stays below the upper passage.'),('Junctions to detail','Plane intersections are trimmed to a single upper envelope. Flashings, valleys, gutters and drainage outlets remain to develop; no weatherproofing approval is claimed.')]:y=note(180,y,title,txt,100)
c.showPage()
head('R05 | ROOF AND BEARING STUDY','Measured 1:1 geometry | axonometric technical preview | separate experimental model',4,True)
c.drawImage(str(O/'R05_BLENDER_PREVIEW.jpg') if (O/'R05_BLENDER_PREVIEW.jpg').exists() else str(V/'R05_AXON.png'),15*mm,22*mm,width=292*mm,height=247*mm,preserveAspectRatio=True,mask='auto')
y=252
for title,txt in [('Delivered geometry','Editable GLB with individual roof, pier, girder, floor and source-wall objects. Original coordinates and metre scale are retained.'),('Validation',f"{qa['pass_count']} technical/geometric checks pass; {qa['fail_count']} fail. Roof coverage, plane overlaps, bearing seats, route clearance and saved-stair roof clearances checked."),('Architectural result','Passage bearing locations and vestibule ceiling are now explicit. Roof volumes respond to actual upper-floor and stair controls.'),('Review boundary','This remains experimental. Structural member sizes and foundations need assessment. Full window heads, roof carpentry and drainage details remain undeveloped.'),('Preserved work','F5ZK-C, F5ZN-A, the working inner/middle vault generator and Pass 6J remain untouched. Missing F5ZL-C support schedule stays unresolved.')]:y=note(315,y,title,txt,90)
c.showPage();c.save()
def svgpath(q):
 if q.is_empty:return ''
 if q.geom_type=='Polygon':return ' '.join('M '+' L '.join(f'{x:.8f},{-z:.8f}' for x,z in ring.coords)+' Z' for ring in [q.exterior,*q.interiors])
 return ' '.join(svgpath(p) for p in q.geoms if p.geom_type=='Polygon')
for which in ['ROOF','BEARING']:
 sv=['<svg xmlns="http://www.w3.org/2000/svg" width="22000mm" height="37000mm" viewBox="-32 -57 22 37">',f'<title>R05 {which} set-out; experimental; metres; physical 1:1; X east, negative SVG y is north</title>']
 for k in ['night_range','residential_range','stair_turret','chapter_house','chapter_vestibule']:
  sv.append(f'<path d="{svgpath(b[k])}" fill="none" stroke="#a6adaf" stroke-width=".025" stroke-dasharray=".12 .10"/>')
 items=[(f['id'],f['polygon'],'#dbe5e9') for f in faces] if which=='ROOF' else [(p['id'],p['geometry'],'#242b30') for p in piers]+[(g['id'],g['geometry'],'#b89b7b') for g in beams]
 for name,q,color in items:sv.append(f'<g id="{name}"><path d="{svgpath(q)}" fill="{color}" stroke="#242b30" stroke-width=".018" fill-rule="evenodd"/></g>')
 sv.append('</svg>');(O/f'R05_{which}_PLAN_1to1.svg').write_text('\n'.join(sv))
print(json.dumps({'pass':qa['pass_count'],'fail':qa['fail_count'],'metrics':metrics},indent=2))
