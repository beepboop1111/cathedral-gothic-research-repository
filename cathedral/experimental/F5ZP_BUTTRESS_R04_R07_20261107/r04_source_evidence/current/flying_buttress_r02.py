"""R02: optional pierced quatrefoil spandrel and receiving tower.
Standalone demonstration; no cathedral integration or structural approval.
"""
import bpy,math,json,sys,argparse,importlib.util
from pathlib import Path
from collections import Counter
from mathutils import Vector
HERE=Path(globals().get('__file__',str(Path.cwd()/'flying_buttress_r02.py'))).resolve().parent
spec=importlib.util.spec_from_file_location('buttress_base',HERE/'base_r01.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
base.TAG='SIMPLE_FLYING_BUTTRESS_R02'
OPTIONS=dict(tracery=True,tower=True,pinnacle=True,tracery_count=5,spandrel_rise=1450.,panel_width=280.,coping_thickness=140.,tower_stage_height=650.,pinnacle_height=1100.)
DEFAULTS={**base.DEFAULTS,**OPTIONS}
def normals(o):
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
def extrude(col,name,poly,y,width,mat):
 n=len(poly);verts=[(x,y+s*width/2,z) for s in [-1,1] for x,z in poly]
 faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 o=base.mesh(col,name,verts,faces,mat);normals(o);return o
def contains(p,poly):
 x,y=p;v=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:v=not v
 return v
def quatrefoil(x,z,r):
 # Envelope of four equal overlapping circles; four rounded lobes.
 points=[];offset=.9
 for i in range(96):
  t=2*math.pi*i/96;d=Vector((math.cos(t),math.sin(t)))
  rr=max(offset*math.cos(t-a)+math.sqrt(1-offset**2+(offset*math.cos(t-a))**2) for a in [0,math.pi/2,math.pi,3*math.pi/2])
  points.append((x+d.x*r*rr/(1+offset),z+d.y*r*rr/(1+offset)))
 return points
def build(config):
 p=base.DEFAULTS.copy();p.update({k:v for k,v in config.items() if k in p})
 opt={**OPTIONS,**{k:v for k,v in config.items() if k in OPTIONS}}
 for k in ['tracery','tower','pinnacle']:
  if not isinstance(opt[k],bool):raise ValueError(k+' must be true/false')
 for k in set(OPTIONS)-{'tracery','tower','pinnacle'}:
  if not isinstance(opt[k],(int,float)) or isinstance(opt[k],bool) or not math.isfinite(opt[k]) or opt[k]<=0:raise ValueError(k+' must be positive and finite')
 if int(opt['tracery_count'])!=opt['tracery_count'] or not 1<=opt['tracery_count']<=12:raise ValueError('tracery_count must be 1..12')
 base.validate(p);p['segments']=int(p['segments']);p['repeat_count']=int(p['repeat_count'])
 bottom,top,center,R,sweep=base.arc(p)
 if opt['panel_width']>p['flyer_width']:raise ValueError('panel must fit within flyer width')
 rise=opt['spandrel_rise'];slope=(top[-1].y-top[0].y)/(top[-1].x-top[0].x)
 def upper(x):return top[0].y+rise+slope*(x-top[0].x)
 if opt['tracery']:
  if min(upper(v.x)-v.y for v in top)<300:raise ValueError('increase spandrel_rise to leave an openwork panel')
  p['pier_headroom']=max(p['pier_headroom'],upper(0)+opt['coping_thickness']+100-p['outer_landing_z'])
  if upper(p['span'])+opt['coping_thickness']>=p['wall_height']:raise ValueError('wall must rise above coping')
 objects,qa=base.build(p);col=bpy.data.collections[base.TAG];mat=base.material(base.TAG+'_DRESSING',(.8,.74,.61));hole_rows=[]
 poly=[list(v) for v in top]+[(top[-1].x,upper(top[-1].x)),(top[0].x,upper(top[0].x))]
 def lower(x):
  for a,b in zip(top,top[1:]):
   if a.x<=x<=b.x:return a.y+(b.y-a.y)*(x-a.x)/(b.x-a.x)
  raise ValueError('x outside arc')
 for k in range(int(p['repeat_count'])):
  y=k*p['spacing'];name=f'FB_{k+1:02d}'
  if opt['tracery']:
   panel=extrude(col,name+'_PIERCED_TRACERY',poly,y,opt['panel_width'],mat);objects.append(panel)
   xmin=max(p['pier_depth']/2+250,top[0].x+300);xmax=min(p['span']-p['wall_depth']/2-250,top[-1].x-300)
   if xmax<=xmin:raise ValueError('span too short for tracery')
   step=(xmax-xmin)/int(opt['tracery_count'])
   for j in range(int(opt['tracery_count'])):
    x=xmin+(j+.5)*step;z=(lower(x)+upper(x))/2;r=min((upper(x)-lower(x))*.32,step*.35)
    points=quatrefoil(x,z,r)
    for attempt in range(30):
     # Expanded contour reserves an unpierced ligament around each opening.
     if all(contains((x+1.2*(a-x),z+1.2*(b-z)),poly) for a,b in points):break
     r*=.9;points=quatrefoil(x,z,r)
    else:raise ValueError('cannot fit tracery opening')
    cutter=extrude(col,name+'_TEMP_CUTTER',points,y,p['flyer_width']*4,mat)
    bpy.context.view_layer.objects.active=panel
    modifier=panel.modifiers.new('QUATREFOIL','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    data=cutter.data;bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(data)
    hole_rows.append(dict(unit=k+1,index=j+1,center_xz=[x,z],radius=r,contour_xz=points))
   normals(panel)
   copingpoly=[(top[0].x,upper(top[0].x)),(top[-1].x,upper(top[-1].x)),(top[-1].x,upper(top[-1].x)+opt['coping_thickness']),(top[0].x,upper(top[0].x)+opt['coping_thickness'])]
   objects.append(extrude(col,name+'_COPING',copingpoly,y,p['flyer_width']+80,mat))
  if opt['tower']:
   h=p['outer_landing_z']+p['pier_headroom'];stage=opt['tower_stage_height']
   for suffix,z,dx,dy,dz in [('STRINGCOURSE',h,p['pier_depth']+140,p['pier_width']+140,150),('TOWER_STAGE',h+stage/2,p['pier_depth']*.8,p['pier_width']*.8,stage),('TOWER_CAP',h+stage,p['pier_depth']*.94,p['pier_width']*.94,140)]:
    objects.append(base.box(col,name+'_'+suffix,0,y,z,dx,dy,dz,mat))
   if opt['pinnacle']:
    z=h+stage+70;dx=p['pier_depth']*.75;dy=p['pier_width']*.75
    objects.append(base.mesh(col,name+'_PINNACLE',[(-dx/2,y-dy/2,z),(dx/2,y-dy/2,z),(dx/2,y+dy/2,z),(-dx/2,y+dy/2,z),(0,y,z+opt['pinnacle_height'])],[(3,2,1,0),(0,1,4),(1,2,4),(2,3,4),(3,0,4)],mat))
 qa['features']=opt;qa['effective_base_parameters']=p;qa['holes']=hole_rows;qa['mesh_checks']=[]
 for o in objects:
  edges=Counter(tuple(sorted((f.vertices[i],f.vertices[(i+1)%len(f.vertices)]))) for f in o.data.polygons for i in range(len(f.vertices)))
  assert all(v==2 for v in edges.values()),o.name
  assert all(f.area>1e-6 for f in o.data.polygons),o.name
  qa['mesh_checks'].append(dict(object=o.name,vertices=len(o.data.vertices),nonmanifold_edges=0))
 col['R02_options']=json.dumps(opt);return objects,qa
# Modular detail layer. The original builder remains the isolated core producer.
_core_builder=build
from mathutils import Matrix
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
DETAIL_DEFAULTS=dict(scale=1.,projection=0.,orientation_degrees=0.,spacing=240.,count=4)
MOULDING=[(-1.,-.5),(-1.,0),(-.7,.2),(-.6,.65),(0.,1.),(.6,.65),(.7,.2),(1.,0),(1.,-.5)]
COMPONENTS={'tracery','flyer_moulding','coping_moulding','tower_details','anchor_details'}

def _profile_check(profile):
 if len(profile)<3:raise ValueError('Profile needs at least three vertices')
 if any(len(p)!=2 or not all(math.isfinite(v) for v in p) for p in profile):raise ValueError('Invalid profile coordinate')
 area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(profile,profile[1:]+profile[:1]))/2
 if abs(area)<1e-9:raise ValueError('Zero-area profile')
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 for i,(a,b) in enumerate(zip(profile,profile[1:]+profile[:1])):
  if (Vector(a)-Vector(b)).length<1e-9:raise ValueError('Repeated profile vertex')
  for j in range(i+2,len(profile)):
   if i==0 and j==len(profile)-1:continue
   c,d=profile[j],profile[(j+1)%len(profile)]
   if cross(a,b,c)*cross(a,b,d)<=0 and cross(c,d,a)*cross(c,d,b)<=0:
    # Bounding boxes distinguish separated collinear segments.
    if all(max(min(a[k],b[k]),min(c[k],d[k]))<=min(max(a[k],b[k]),max(c[k],d[k])) for k in [0,1]):raise ValueError('Self-intersecting profile')
 return area

def sweep_profile(col,name,path,profile,material,closed=False,scale=1.,projection=0.,orientation_degrees=0.):
 """Sweep any simple closed 2-D polygon; tangent-following transport frames.
 profile U is across the path, V is outward from it. No voxelization.
 """
 _profile_check(profile)
 if scale<=0 or not all(math.isfinite(x) for x in [scale,projection,orientation_degrees]):raise ValueError('Invalid sweep controls')
 pp=[Vector(p) for p in path]
 if closed and (pp[0]-pp[-1]).length<1e-7:pp.pop()
 n=len(pp);m=len(profile)
 if n<(3 if closed else 2):raise ValueError('Path too short')
 if any((pp[(i+1)%n]-pp[i]).length<1e-7 for i in range(n if closed else n-1)):raise ValueError('Duplicate path point')
 tangents=[]
 for i in range(n):
  tangent=pp[(i+1)%n]-pp[(i-1)%n] if closed or 0<i<n-1 else pp[1]-pp[0] if i==0 else pp[-1]-pp[-2]
  if tangent.length<1e-8:raise ValueError('Path reverses at a vertex')
  tangents.append(tangent.normalized())
 side=Vector((0,1,0));side-=tangents[0]*side.dot(tangents[0])
 if side.length<1e-6:side=tangents[0].orthogonal()
 sides=[side.normalized()]
 for a,b in zip(tangents,tangents[1:]):
  side=a.rotation_difference(b)@sides[-1];side-=b*side.dot(b);sides.append(side.normalized())
 if closed:
  returned=tangents[-1].rotation_difference(tangents[0])@sides[-1]
  correction=math.atan2(tangents[0].dot(returned.cross(sides[0])),returned.dot(sides[0]))
 else:correction=0.
 verts=[]
 for i,(p,t,s) in enumerate(zip(pp,tangents,sides)):
  rot=Matrix.Rotation(math.radians(orientation_degrees)+correction*i/n,3,t);s=rot@s;up=t.cross(s).normalized()
  verts.extend(tuple(p+s*(u*scale)+up*(v*scale+projection)) for u,v in profile)
 faces=[]
 for i in range(n if closed else n-1):
  j=(i+1)%n
  for k in range(m):faces.append((i*m+k,i*m+(k+1)%m,j*m+(k+1)%m,j*m+k))
 if not closed:
  poly=[Vector((u,v,0)) for u,v in profile];tris=tessellate_polygon([poly]);ids={tuple(v):i for i,v in enumerate(poly)}
  for tri in tris:
   indices=tuple(v if isinstance(v,int) else ids[tuple(v)] for v in tri);faces.extend([tuple(reversed(indices)),tuple((n-1)*m+k for k in indices)])
 ob=base.mesh(col,name,verts,faces,material);normals(ob);ob['sweep_profile']=json.dumps(profile);return ob

def path_from_spec(spec):
 """Editable circle/arc/polyline primitives in local XYZ coordinates."""
 kind=spec['type']
 if kind=='polyline':return spec['points'],spec.get('closed',False)
 if kind not in ['circle','arc']:raise ValueError('Unknown tracery primitive')
 center=Vector(spec.get('center',(0,0,0)));radius=spec['radius'];n=int(spec.get('segments',64))
 if radius<=0 or n<8:raise ValueError('Invalid arc radius/resolution')
 start=math.radians(spec.get('start_degrees',0));end=math.radians(spec.get('end_degrees',360))
 if not 0<abs(end-start)<=2*math.pi+1e-9:raise ValueError('Arc sweep outside (0,360]')
 closed=kind=='circle' or abs(abs(end-start)-2*math.pi)<1e-9
 path=[tuple(center+Vector((radius*math.cos(start+(end-start)*i/n),0,radius*math.sin(start+(end-start)*i/n)))) for i in range(n if closed else n+1)]
 return path,closed

def anchor(position,x_axis=(1,0,0),z_axis=(0,0,1)):
 x=Vector(x_axis).normalized();z=Vector(z_axis);z=(z-x*z.dot(x)).normalized();y=z.cross(x)
 mat=Matrix((x,y,z)).transposed().to_4x4();mat.translation=Vector(position);return mat

def place_detail(col,name,local_path,profile,mat,anchor_matrix,controls,closed=False):
 """Local template -> named anchor; count/spacing repeat along anchor local Y."""
 count=controls.get('count',1);spacing=controls.get('spacing',0)
 if int(count)!=count or count<1 or spacing<0:raise ValueError('Invalid detail repetition')
 result=[]
 for i in range(int(count)):
  offset=Vector((0,(i-(count-1)/2)*spacing,0));path=[tuple(anchor_matrix@(Vector(p)+offset)) for p in local_path]
  result.append(sweep_profile(col,name+f'_{i+1}',path,profile,mat,closed,controls.get('scale',1),controls.get('projection',0),controls.get('orientation_degrees',0)))
 return result

def bounded_insert(col,name,specs,profile,mat,boundary,y_offset=0.,controls=None):
 """Build real stone bars, rejecting swept vertices outside the opening."""
 result=[];controls=controls or {}
 for i,spec in enumerate(specs):
  path,closed=path_from_spec(spec);path=[(p[0],p[1]+y_offset,p[2]) for p in path]
  ob=sweep_profile(col,name+f'_{i}',path,profile,mat,closed,**{k:v for k,v in controls.items() if k in ['scale','projection','orientation_degrees']})
  if not all(contains((v.co.x,v.co.z),boundary) for v in ob.data.vertices):
   data=ob.data;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(data)
   raise ValueError('Tracery bar crosses its opening boundary')
  result.append(ob)
 return result

def _component(root,name):
 existing=bpy.data.collections.get(base.TAG+'_'+name)
 if existing:
  if existing.get('owner')!=base.TAG:raise ValueError('Unowned component collection')
  for ob in list(existing.objects):
   data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
   if data and data.users==0:bpy.data.meshes.remove(data)
  return existing
 col=bpy.data.collections.new(base.TAG+'_'+name);root.children.link(col);col['owner']=base.TAG;return col

def _geometry_tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(f.vertices) for f in ob.data.polygons])

def fit_checks(objects,interfaces=(),neighbors=(),tolerance=.02):
 report={'meshes':[],'interfaces':[],'neighbor_overlaps':[]}
 for ob in objects:
  edges=Counter(tuple(sorted((f.vertices[i],f.vertices[(i+1)%len(f.vertices)]))) for f in ob.data.polygons for i in range(len(f.vertices)))
  bad=sum(v!=2 for v in edges.values());deg=sum(f.area<=1e-7 for f in ob.data.polygons)
  report['meshes'].append({'name':ob.name,'nonmanifold_edges':bad,'degenerate_polygons':deg})
 for label,point,target in interfaces:
  point=Vector(point);tree=_geometry_tree(target);nearest=tree.find_nearest(point)
  # Rectangular core landing support: exact local bounding-box containment.
  p=target.matrix_world.inverted()@point;bb=[Vector(v) for v in target.bound_box]
  embedded=all(min(v[i] for v in bb)-tolerance<=p[i]<=max(v[i] for v in bb)+tolerance for i in range(3))
  report['interfaces'].append({'name':label,'inside_support_envelope':embedded,'surface_distance':nearest[3], 'gap':not embedded and nearest[3]>tolerance})
 for a,b in neighbors:
  hit=len(_geometry_tree(a).overlap(_geometry_tree(b)))
  if hit:report['neighbor_overlaps'].append({'a':a.name,'b':b.name,'surface_triangle_pairs':hit})
 report['limitations']='Mesh surface overlaps do not detect every solid containment; interfaces use rectangular core envelopes. No structural or bonding assessment.'
 return report

def build(config,components=None):
 """Full build, or selective rebuild of named detail components.
 Core parameter changes require a full build; untouched component objects persist.
 """
 controls={**DETAIL_DEFAULTS,**config.get('detail_controls',{})};profile=config.get('moulding_profile',MOULDING)
 _profile_check(profile)
 if controls['scale']<=0 or not all(math.isfinite(v) for v in controls.values()):raise ValueError('Invalid detail controls')
 selected=set(COMPONENTS if components is None else components)
 if not selected<=COMPONENTS:raise ValueError('Unknown rebuild component')
 core={**DEFAULTS,**{k:v for k,v in config.items() if k in DEFAULTS}}
 bottom,top,center,R,sweep=base.arc(core)
 slope=(top[-1].y-top[0].y)/(top[-1].x-top[0].x)
 def upper(x):return top[0].y+core['spandrel_rise']+slope*(x-top[0].x)
 def lower(x):
  for a,b in zip(top,top[1:]):
   if a.x<=x<=b.x:return a.y+(b.y-a.y)*(x-a.x)/(b.x-a.x)
  raise ValueError('Outside arch')
 if min(upper(v.x)-v.y for v in top)<300:raise ValueError('Spandrel too shallow')
 effective=core.copy();effective['tracery']=False
 if core['tracery']:effective['pier_headroom']=max(core['pier_headroom'],upper(0)+core['coping_thickness']+100-core['outer_landing_z'])
 if upper(core['span'])+core['coping_thickness']>=core['wall_height']:raise ValueError('Wall below coping')
 root=bpy.data.collections.get(base.TAG)
 if components is None:
  if root:
   for child in list(root.children):
    if child.get('owner')==base.TAG:
     _component(root,child.name.removeprefix(base.TAG+'_'));bpy.data.collections.remove(child)
  coreobjects,qa=_core_builder(effective);root=bpy.data.collections[base.TAG];root['modular_core_config']=json.dumps(core,sort_keys=True)
 else:
  if root is None or root.get('modular_core_config')!=json.dumps(core,sort_keys=True):raise ValueError('Core parameters changed: request a full build')
  coreobjects=list(root.objects)
 stone=base.material(base.TAG+'_DETAIL',(.86,.79,.64));anchors={};neighbors=[];interfaces=[]
 for k in range(int(core['repeat_count'])):
  y=k*core['spacing'];prefix=f'FB_{k+1:02d}';h=core['outer_landing_z']+effective['pier_headroom'];stage=core['tower_stage_height']
  unitanchors={'outer_landing':anchor((0,y,core['outer_landing_z'])),'wall_landing':anchor((core['span'],y,core['wall_landing_z'])), 'coping_start':anchor((top[0].x,y,upper(top[0].x))),'coping_end':anchor((top[-1].x,y,upper(top[-1].x))), 'tower_stage':anchor((0,y,h)), 'pinnacle_base':anchor((0,y,h+stage+70))}
  for i,(xoff,yoff) in enumerate([(-1,-1),(-1,1),(1,-1),(1,1)]):unitanchors['tower_corner_'+str(i)]=anchor((xoff*core['pier_depth']*.4,y+yoff*core['pier_width']*.4,h+80))
  anchors.update({prefix+'/'+n:[list(r) for r in a] for n,a in unitanchors.items()})
  if 'tracery' in selected:
   col=_component(root,'tracery') if k==0 else bpy.data.collections[base.TAG+'_tracery']
   if core['tracery']:
    boundary=[list(p) for p in top]+[(top[-1].x,upper(top[-1].x)),(top[0].x,upper(top[0].x))]
    xmin=core['pier_depth']/2+220;xmax=core['span']-core['wall_depth']/2-220;count=int(core['tracery_count']);step=(xmax-xmin)/count
    if count<1 or step<150:raise ValueError('Tracery spacing too small')
    rings=[]
    for j in range(count):
     x=xmin+(j+.5)*step;z=(upper(x)+lower(x))/2;r=min((upper(x)-lower(x))*.32,step*.36)
     specs=[dict(type='circle',center=(x,0,z),radius=r),dict(type='polyline',points=[(a,0,b) for a,b in quatrefoil(x,z,r*.78)],closed=True)]
     bars=bounded_insert(col,prefix+f'_TRACERY_{j}',specs,[(-60,-24),(60,-24),(60,24),(-60,24)],stone,boundary,y,dict(scale=controls['scale'],projection=controls['projection'],orientation_degrees=controls['orientation_degrees']))
     for a in [0,math.pi/2,math.pi,3*math.pi/2]:
      path=[(x+rr*math.cos(a),y,z+rr*math.sin(a)) for rr in [r*.78,r]]
      sweep_profile(col,prefix+f'_LOBE_JOINT_{j}_{a}',path,[(-55,-22),(55,-22),(55,22),(-55,22)],stone)
     for lo,hi in [(lower(x),z-r),(z+r,upper(x))]:
      sweep_profile(col,prefix+f'_RING_STEM_{j}_{lo}',[(x,y,lo),(x,y,hi)],[(-55,-24),(55,-24),(55,24),(-55,24)],stone)
     rings.append(bars)
    for a,b in zip(rings,rings[1:]):neighbors.extend((x,y) for x in a for y in b)
    coping=[(top[0].x,upper(top[0].x)),(top[-1].x,upper(top[-1].x)),(top[-1].x,upper(top[-1].x)+core['coping_thickness']),(top[0].x,upper(top[0].x)+core['coping_thickness'])]
    extrude(col,prefix+'_MODULAR_COPING',coping,y,core['flyer_width']+80,stone)
    # Thin engaged uprights connect openwork to both bounding members.
    for j in range(count+1):
     x=xmin+j*step;path=[(x,y,lower(x)+1),(x,y,upper(x)-1)]
     sweep_profile(col,prefix+f'_TRACERY_POST_{j}',path,[(-45,-32),(45,-32),(45,32),(-45,32)],stone)
  if 'flyer_moulding' in selected:
   col=_component(root,'flyer_moulding') if k==0 else bpy.data.collections[base.TAG+'_flyer_moulding']
   for side in [-1,1]:sweep_profile(col,prefix+f'_SOFFIT_MOULDING_{side}',[(p.x,y+side*(core['flyer_width']/2+15),p.y) for p in bottom],profile,stone,scale=42*controls['scale'],projection=controls['projection'],orientation_degrees=controls['orientation_degrees'])
  if 'coping_moulding' in selected:
   col=_component(root,'coping_moulding') if k==0 else bpy.data.collections[base.TAG+'_coping_moulding']
   if core['tracery']:
    for side in [-1,1]:sweep_profile(col,prefix+f'_COPING_MOULDING_{side}',[(p.x,y+side*(core['flyer_width']/2+45),upper(p.x)+core['coping_thickness']) for p in [top[0],top[-1]]],profile,stone,scale=48*controls['scale'],projection=controls['projection'],orientation_degrees=controls['orientation_degrees'])
  if 'tower_details' in selected:
   col=_component(root,'tower_details') if k==0 else bpy.data.collections[base.TAG+'_tower_details']
   if core['tower']:
    for label in ['tower_stage','pinnacle_base']:
     path=[(-core['pier_depth']*.48,-core['pier_width']*.48,0),(core['pier_depth']*.48,-core['pier_width']*.48,0),(core['pier_depth']*.48,core['pier_width']*.48,0),(-core['pier_depth']*.48,core['pier_width']*.48,0)]
     place_detail(col,prefix+'_'+label+'_COLLAR',path,profile,stone,unitanchors[label],dict(scale=40*controls['scale'],projection=controls['projection'],orientation_degrees=controls['orientation_degrees']),True)
    for i in range(4):place_detail(col,prefix+f'_CORNER_SHAFT_{i}',[(0,0,0),(0,0,stage-100)],profile,stone,unitanchors['tower_corner_'+str(i)],dict(scale=30*controls['scale']))
  if 'anchor_details' in selected:
   col=_component(root,'anchor_details') if k==0 else bpy.data.collections[base.TAG+'_anchor_details']
   controls2={**controls,'scale':35*controls['scale']}
   # A repeated, user-oriented ribbed frieze under the tower stage.
   if core['tower']:
    c=int(controls['count']);spacing=controls['spacing']
    if (c-1)*spacing+100>core['pier_width']:raise ValueError('Repeated details exceed tower width')
    a=unitanchors['tower_stage']@Matrix.Translation((-core['pier_depth']/2-35,0,-180))
    place_detail(col,prefix+'_ANCHORED_FRIEZE',[(0,0,0),(0,0,150)],profile,stone,a,controls2)
  receiver=next(o for o in coreobjects if o.name==prefix+'_RECEIVER');wall=next(o for o in coreobjects if o.name==prefix+'_WALL')
  interfaces.extend([(prefix+'/outer_landing',(0,y,core['outer_landing_z']),receiver),(prefix+'/wall_landing',(core['span'],y,core['wall_landing_z']),wall)])
 root['named_anchors']=json.dumps(anchors);root['detail_controls']=json.dumps(controls)
 allobjects=list(root.all_objects);checks=fit_checks(allobjects,interfaces,neighbors)
 return allobjects,dict(status='EXPERIMENTAL_MODULAR_GENERATOR',components_rebuilt=sorted(selected),anchors=anchors,fit_checks=checks,detail_controls=controls)

# R03 research-oriented assembly API. Native XYZ, Z up; no scale conversion.
# Existing build()/selective rebuild API remains available unchanged.
HISTORICAL_PRESETS={
 'ungewitter_intermediate':dict(source='Ungewitter, Vol II, plates LXXXIV–LXXXVII',status='UNMEASURED_RESEARCH_LEAD',measured_proportions=None,uncertainty=None,choices={'intermediate':True,'receiver_section':'stepped'}),
 'viollet_t_receiver':dict(source='Viollet-le-Duc, buttress figures 60–70',status='UNMEASURED_RESEARCH_LEAD',measured_proportions=None,uncertainty=None,choices={'receiver_section':'T'}),
 'double_flyer_study':dict(source='Comparative Amiens/Reims/Soissons research; exact plate unresolved',status='DESIGN_STUDY',measured_proportions=None,uncertainty=None,choices={'two_tiers':True})}
SYSTEM_DEFAULTS=dict(two_tiers=True,upper_outer_z=5400.,upper_wall_z=7300.,upper_sagitta=400.,intermediate=False,intermediate_fraction=.5,receiver_section='T',receiver_yaw=0.,course_height=280.,joint=6.,voussoirs=22,tracery_rule='quatrefoil',gutter_width=120.,gutter_depth=70.,gutter_fall=.025,gargoyle=True,preset=None)

def boolean_join(objects,name,boundary=None):
 """Exact solid unions remove intersecting bar end caps; optional frame clipping."""
 if not objects:return None
 target=objects[0];target.name=name
 for ob in objects[1:]:
  bpy.context.view_layer.objects.active=target
  mod=target.modifiers.new('MOULDING_JUNCTION','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=ob
  bpy.ops.object.modifier_apply(modifier=mod.name)
  data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
  if data.users==0:bpy.data.meshes.remove(data)
 if boundary:
  bpy.context.view_layer.objects.active=target
  mod=target.modifiers.new('FRAME_TRIM','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=boundary
  bpy.ops.object.modifier_apply(modifier=mod.name)
 import bmesh
 bm=bmesh.new();bm.from_mesh(target.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.002)
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.002)
 bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(target.data);bm.free()
 target.data.update();return target

def rule_paths(kind,x,z,r):
 """Compass-defined centerline graph, with exact circle centers retained."""
 if kind=='pointed':
  # Equilateral two-centred arch: radius 2r, centers at opposite springings.
  return [dict(type='arc',center=(x-r,0,z-r),radius=2*r,start_degrees=0,end_degrees=60),dict(type='arc',center=(x+r,0,z-r),radius=2*r,start_degrees=120,end_degrees=180)]
 n={'trefoil':3,'quatrefoil':4}.get(kind)
 if n is None:raise ValueError('Unknown tracery construction')
 # Equal circular lobes meet at explicit circle intersections.
 return [dict(type='circle',center=(x+r*.45*math.cos(2*math.pi*i/n),0,z+r*.45*math.sin(2*math.pi*i/n)),radius=r*.62) for i in range(n)]

def receiver_plan(kind,dx,dy):
 if kind=='rectangular':return [(-dx/2,-dy/2),(dx/2,-dy/2),(dx/2,dy/2),(-dx/2,dy/2)]
 if kind=='T':return [(-dx/2,-dy/2),(dx/2,-dy/2),(dx/2,-dy*.15),(dx*.18,-dy*.15),(dx*.18,dy/2),(-dx*.18,dy/2),(-dx*.18,-dy*.15),(-dx/2,-dy*.15)]
 if kind=='stepped':return [(-dx/2,-dy/2),(dx/2,-dy/2),(dx/2,0),(dx*.32,0),(dx*.32,dy/2),(-dx*.32,dy/2),(-dx*.32,0),(-dx/2,0)]
 raise ValueError('Unknown receiver section')

def course_receiver(col,name,x,y,height,dx,dy,opts,mat):
 poly=receiver_plan(opts['receiver_section'],dx,dy);angle=math.radians(opts['receiver_yaw']);out=[]
 count=math.ceil(height/opts['course_height'])
 for i in range(count):
  lo=i*height/count;hi=(i+1)*height/count;gap=opts['joint']/2
  ob=extrude(col,name+f'_COURSE_{i:03}',poly,0,hi-lo-gap*2,mat)
  # extrusion local XZ -> horizontal XY, extrusion Y -> vertical Z
  for v in ob.data.vertices:
   a,b,c=v.co;v.co=(x+a*math.cos(angle)-c*math.sin(angle),y+a*math.sin(angle)+c*math.cos(angle),(lo+hi)/2+b)
  ob.data.update();normals(ob);out.append(ob)
 return out

def course_arch(col,name,p,opts,mat,offset=0.,y=0.):
 p={**p,'segments':int(opts['voussoirs'])};bottom,top,c,r,s=base.arc(p);out=[]
 for i in range(len(bottom)-1):
  # Constant angular joints; joints deliberately remain separate stones.
  a,b=bottom[i],bottom[i+1];u,v=top[i],top[i+1];t=opts['joint']/max((b-a).length,1)/2
  if t>=.25:raise ValueError('Joint too large for voussoir')
  points=[a.lerp(b,t),a.lerp(b,1-t),u.lerp(v,1-t),u.lerp(v,t)]
  out.append(extrude(col,name+f'_VOUSSOIR_{i:03}',[(q.x+offset,q.y) for q in points],y,p['flyer_width'],mat))
 return out

def drainage(col,name,span,y,z,opts,mat):
 fall=opts['gutter_fall'];w=opts['gutter_width'];d=opts['gutter_depth']
 if fall<=0 or w<=20 or d<=10:raise ValueError('Drain requires positive fall and open channel')
 # x=span is inlet, x=-700 outlet; all segments fall toward receiver.
 path=[(-700,y,z-700*fall),(0,y,z),(span,y,z+span*fall)]
 profile=[(-w/2-20,0),(-w/2-20,d),(-w/2,d),(-w/2,20),(w/2,20),(w/2,d),(w/2+20,d),(w/2+20,0)]
 ob=sweep_profile(col,name+'_OPEN_GUTTER',path,profile,mat)
 if opts['gargoyle']:
  base.box(col,name+'_OUTLET_NOSE',-550,y,z-550*fall-70,400,w+100,100,mat)
 slopes=[(b[2]-a[2])/(b[0]-a[0]) for a,b in zip(path,path[1:])]
 assert min(slopes)>0
 return dict(inlet=path[-1],outlet=path[0],slopes=slopes,minimum_fall=min(slopes),status='GEOMETRIC_FALL_ONLY')

def build_system(config,options=None):
 """Full assembly of the standalone experiment; build() handles R02 selective edits.
 Historical presets carry evidence, never silently import measured dimensions.
 """
 opts={**SYSTEM_DEFAULTS,**(options or {})}
 if set(opts)-set(SYSTEM_DEFAULTS):raise ValueError('Unknown system option')
 preset=HISTORICAL_PRESETS.get(opts['preset']) if opts['preset'] else None
 if opts['preset'] and preset is None:raise ValueError('Unknown historical preset')
 # Explicit options take precedence over preset design choices.
 if preset:opts={**SYSTEM_DEFAULTS,**preset['choices'],**(options or {})}
 p={**DEFAULTS,**config};base.validate({k:p[k] for k in base.DEFAULTS})
 if not 0<opts['intermediate_fraction']<1:raise ValueError('Intermediate fraction must be inside span')
 if opts['course_height']<=0 or not 0<=opts['joint']<opts['course_height']/3 or int(opts['voussoirs'])!=opts['voussoirs'] or opts['voussoirs']<8:raise ValueError('Invalid coursing')
 receiver_plan(opts['receiver_section'],p['pier_depth'],p['pier_width'])
 rule_paths(opts['tracery_rule'],0,0,100)
 # Build original lower assembly and keep profile details and anchors intact.
 objects,qa=build(p);root=bpy.data.collections[base.TAG];col=_component(root,'research_system')
 stone=base.material(base.TAG+'_COURSED',(.71,.65,.53));detail=base.material(base.TAG+'_TRACERY_STONE',(.9,.8,.60))
 tiers=[dict(outer=p['outer_landing_z'],wall=p['wall_landing_z'],sag=p['arc_sagitta'])]
 if opts['two_tiers']:tiers.append(dict(outer=opts['upper_outer_z'],wall=opts['upper_wall_z'],sag=opts['upper_sagitta']))
 if any(t['outer']>=p['wall_height'] or t['wall']+p['flyer_thickness']>=p['wall_height'] for t in tiers):raise ValueError('Tier exceeds wall height')
 for ob in list(root.objects):
  if ob.name.endswith(('_FLYER','_RECEIVER')):
   data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
   if data.users==0:bpy.data.meshes.remove(data)
 drains=[];rules=[];endpoints=[]
 for unit in range(int(p['repeat_count'])):
  y=unit*p['spacing'];prefix=f'SYSTEM_{unit}'
  height=max(t['outer'] for t in tiers)+p['flyer_thickness']+250
  course_receiver(col,prefix+'_RECEIVER',0,y,height,p['pier_depth'],p['pier_width'],opts,stone)
  stations=[0.,p['span']*opts['intermediate_fraction'],p['span']] if opts['intermediate'] else [0.,p['span']]
  if opts['intermediate']:
   x=stations[1];h=max(t['outer']+(t['wall']-t['outer'])*x/p['span'] for t in tiers)+p['flyer_thickness']+200
   course_receiver(col,prefix+'_INTERMEDIATE',x,y,h,p['pier_depth']*.7,p['pier_width']*.8,opts,stone)
  for level,t in enumerate(tiers):
   for bay,(a,b) in enumerate(zip(stations,stations[1:])):
    q={**p,'span':b-a,'outer_landing_z':t['outer']+(t['wall']-t['outer'])*a/p['span'],'wall_landing_z':t['outer']+(t['wall']-t['outer'])*b/p['span'],'arc_sagitta':t['sag']*(b-a)/p['span']}
    pieces=course_arch(col,prefix+f'_TIER{level}_BAY{bay}',q,opts,stone,a,y)
    bottom,top,c,r,s=base.arc(q);endpoints.append(dict(tier=level,bay=bay,start=[a,q['outer_landing_z']],end=[b,q['wall_landing_z']],center=[c.x+a,c.y],radius=r))
    if level:
     # Coping + compass-defined inserts on upper tier. Radius constrained by bay.
     rise=1050.;z0=top[0].y+rise;z1=top[-1].y+rise
     extrude(col,prefix+f'_UPPER_COPING{bay}',[(a,z0),(b,z1),(b,z1+100),(a,z0+100)],y,p['flyer_width']+60,detail)
     boundary=[(v.x+a,v.y) for v in top]+[(b,z1),(a,z0)]
     for j in range(3):
      x=a+(j+.5)*(b-a)/3;f=(x-a)/(b-a);z=(z0+(z1-z0)*f)+(-rise*.48);rad=min(215.,(b-a)/12)
      idx=int(f*(len(top)-1));z=(top[idx].y+z0+(z1-z0)*f)/2
      for attempt in range(35):
       specs=rule_paths(opts['tracery_rule'],x,z,rad)
       paths=[path_from_spec(spec)[0] for spec in specs]
       if all(contains((v[0]+dx,v[2]+dz),boundary) for path in paths for v in path for dx,dz in [(-42,-42),(-42,42),(42,-42),(42,42)]):break
       rad*=.9
      else:raise ValueError('No clearance for upper tracery')
      rules.extend(specs)
      bars=[]
      for si,spec in enumerate(specs):
       width=38+si*.4
       bars.extend(bounded_insert(col,prefix+f'_RULE{bay}_{j}_{si}',[spec],[(-width,-24),(width,-24),(width,24),(-width,24)],detail,boundary,y))
      boolean_join(bars,prefix+f'_JOINED_RULE{bay}_{j}')
      # Posts connect the enclosure to the arch; separate from moulded inserts.
      idx=int(f*(len(top)-1));sweep_profile(col,prefix+f'_UPRIGHT{bay}_{j}',[(x,y,top[idx].y),(x,y,z0+(z1-z0)*f)], [(-40,-32),(40,-32),(40,32),(-40,32)],detail)
  drains.append(drainage(col,prefix,p['span'],y-p['flyer_width']/2-120,height+160,opts,detail))
 root['research_options']=json.dumps(opts);root['historical_evidence']=json.dumps(preset)
 allobjects=list(root.all_objects);checks=fit_checks(allobjects)
 return allobjects,dict(status='EXPERIMENTAL_R03',options=opts,source=preset,construction_arcs=rules,flyer_sections=endpoints,drainage=drains,mesh_checks=checks['meshes'],limitations=['Unmeasured historical presets','No structural capacity or hydraulic capacity validation','Coursing is geometric; bonding and load transfer unresolved','R03 full assembly rebuild; R02 selective detail API retained'])

def proportion_studies(config,variants):
 """Named independent studies, identical coordinate scale; no file exports."""
 original=base.TAG;result=[]
 try:
  for index,(name,options) in enumerate(variants.items()):
   base.TAG=original+'_STUDY_'+name
   objects,qa=build_system(config,options)
   for ob in objects:
    ob.location.y+=index*4500;ob.name=name+'__'+ob.name
   result.append((name,objects,qa))
 finally:base.TAG=original
 return result

# Plate-specific study: measured raster proportions, not cathedral dimensions.
PLATE_892=dict(source='Ungewitter Vol II, Plate LXXXIV, figure 892, Freiburg',image='ungewitter_v2_p087.png',raster_size=[1934,2800],outer_pixel=[846,1320],wall_pixel=[1388,770],span_study_units=5000.,outer_z_study=3000.,pick_uncertainty_px=5.,soffit_picks=[[846,1320],[870,1190],[930,1060],[1010,960],[1100,890],[1200,830],[1300,790],[1388,770]],coping_pixels=[[846,1008],[1390,540]],opening_pixel=[1318,698],opening_radius_px=35.,depth_status='CONJECTURAL',physical_scale=None)

def build_plate_892(study_span=5000.,depth=420.):
 """Least-squares circle from coarse manual raster picks; source bytes untouched.
 The 5000-unit span is an explicit study scale, not an engraved measurement.
 """
 import numpy as np
 if study_span<=0 or depth<=0:raise ValueError('Positive study span and depth required')
 source=PLATE_892;pts=np.array(source['soffit_picks'],dtype=float)
 A=np.column_stack((2*pts[:,0],2*pts[:,1],np.ones(len(pts))))
 cx,cy,c0=np.linalg.lstsq(A,np.sum(pts*pts,axis=1),rcond=None)[0];radius=math.sqrt(c0+cx*cx+cy*cy)
 residual=np.linalg.norm(pts-[cx,cy],axis=1)-radius
 scale=study_span/(source['wall_pixel'][0]-source['outer_pixel'][0])
 def world(p):return ((p[0]-846)*scale,3000+(1320-p[1])*scale)
 center=Vector(world((cx,cy)));R=radius*scale
 a0=math.atan2(1320-cy,846-cx);a1=math.atan2(770-cy,1388-cx)
 sweep=(a1-a0+math.pi)%(2*math.pi)-math.pi
 def point(t,offset=0.):
  angle=a0+sweep*t;return Vector(world((cx+(radius+offset)*math.cos(angle),cy+(radius+offset)*math.sin(angle))))
 soffit=[point(i/96) for i in range(97)];top=[point(i/96,25.) for i in range(97)]
 tag=base.TAG+'_PLATE_892';root=bpy.data.collections.get(tag)
 if root:
  if root.get('owner')!=tag:raise ValueError('Unowned plate collection')
  for ob in list(root.objects):
   data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
   if data.users==0:bpy.data.meshes.remove(data)
 else:root=bpy.data.collections.new(tag);bpy.context.scene.collection.children.link(root)
 root['owner']=tag;root['source']=json.dumps(source);root['scale_status']='ILLUSTRATIVE; NOT PHYSICAL CALIBRATION'
 stone=base.material(tag+'_STONE',(.72,.66,.54));dress=base.material(tag+'_DRESS',(.86,.8,.67))
 # Curved voussoirs follow the fitted radius rather than a stock arch.
 for i in range(28):
  ts=[i/28+.0005,(i+1)/28-.0005]
  path=[point(ts[0]),point(ts[1]),point(ts[1],25),point(ts[0],25)]
  extrude(root,f'892_VOUSSOIR_{i:02}',[tuple(v) for v in path],0,depth,stone)
 coping=[world(p) for p in source['coping_pixels']];boundary=[tuple(p) for p in top]+[coping[1],coping[0]]
 panel=extrude(root,'892_SOLID_SPANDREL',boundary,0,depth*.66,stone)
 ox,oz=world(source['opening_pixel']);rad=source['opening_radius_px']*scale
 contour=quatrefoil(ox,oz,rad)
 cutter=extrude(root,'892_OPENING_CUTTER',contour,0,depth*4,stone)
 bpy.context.view_layer.objects.active=panel;mod=panel.modifiers.new('PIERCED_QUATREFOIL','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name)
 data=cutter.data;bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(data);normals(panel)
 # Annular moulding follows the plate's enclosing circle.
 circle,_=path_from_spec(dict(type='circle',center=(ox,-depth*.36,oz),radius=rad*1.16,segments=96))
 sweep_profile(root,'892_OCULUS_FRAME',circle,[(-35,-25),(35,-25),(35,25),(-35,25)],dress,True)
 for side in [-1,1]:
  sweep_profile(root,'892_SOFFIT_MOULDING'+str(side),[(v.x,side*(depth/2+8),v.y) for v in soffit],MOULDING,dress,scale=32)
  sweep_profile(root,'892_COPING_EDGE'+str(side),[(x,side*(depth/2+22),z) for x,z in coping],MOULDING,dress,scale=44)
 extrude(root,'892_COPING',coping+[(coping[1][0],coping[1][1]+85),(coping[0][0],coping[0][1]+85)],0,depth+80,dress)
 # Receiver dimensions from the visible silhouette; unseen depth is a study choice.
 left,right=world((650,1080))[0],world((846,1080))[0];h=world((650,1080))[1];dx=right-left;x=(left+right)/2
 opts={**SYSTEM_DEFAULTS,'receiver_section':'rectangular','course_height':250.,'joint':4.}
 course_receiver(root,'892_RECEIVER',x,0,h,dx,depth*2.5,opts,stone)
 for z in [h,h+100]:base.box(root,'892_RECEIVER_CAP',x,0,z,dx+160,depth*2.5+160,100,dress)
 # Pinnacle shaft and taper use raster heights; ornaments are simplified.
 shaftbase=h+150;shafttop=world((780,790))[1];tip=world((780,550))[1]
 base.box(root,'892_PINNACLE_SHAFT',world((780,0))[0],0,(shaftbase+shafttop)/2,dx*.46,depth*1.3,shafttop-shaftbase,dress)
 px=world((780,0))[0];w=dx*.3
 base.mesh(root,'892_PINNACLE_SPIRE',[(px+a*w,b*w,shafttop) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]+[(px,0,tip)],[(0,3,2,1),(0,1,4),(1,2,4),(2,3,4),(3,0,4)],dress)
 for sign in [-1,1]:
  path=[(px+sign*w*.8,-depth*.7,shaftbase),(px+sign*w*.8,-depth*.7,shafttop)]
  sweep_profile(root,'892_ENGAGED_SHAFT'+str(sign),path,[(-40,-30),(40,-30),(40,30),(-40,30)],dress)
 # High wall attachment is cropped context, not a reconstruction of the nave.
 wallheight=world((1390,490))[1]
 base.box(root,'892_WALL_CONTEXT',study_span+220,0,wallheight/2,440,depth*3,wallheight,stone)
 drain=drainage(root,'892',study_span,0,h+130,{**SYSTEM_DEFAULTS,'gutter_fall':(coping[1][1]-coping[0][1])/study_span},dress)
 objects=list(root.objects);qa=dict(source=source,circle_center_px=[cx,cy],radius_px=radius,rms_px=float(np.sqrt(np.mean(residual**2))),max_residual_px=float(max(abs(residual))),scale_study_units_per_pixel=scale,study_span=study_span,depth=depth,opening_inside=all(contains(p,boundary) for p in contour),drain=drain,checks=fit_checks(objects)['meshes'],limitations=['Coarse manually selected raster points, not dense tracing','Depth, hidden geometry and ornaments conjectural','No physical calibration or structural validation'])
 root['fit_qa']=json.dumps(qa);return objects,qa

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--config');ap.add_argument('--out')
 opt=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
 p=DEFAULTS.copy()
 if opt.config:
  data=json.loads(Path(opt.config).read_text())
  if set(data)-set(p):raise ValueError('Unknown parameter')
  p.update(data)
 objects,qa=build(p);out=Path(opt.out) if opt.out else HERE/'output';out.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(out/'flying_buttress_r02.glb'),export_format='GLB',use_selection=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(out/'flying_buttress_r02.blend'))
 (out/'parameters.json').write_text(json.dumps(p,indent=2));(out/'QA.json').write_text(json.dumps(qa,indent=2))
if __name__=='__main__':main()
