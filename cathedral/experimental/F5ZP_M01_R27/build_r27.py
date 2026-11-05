"""R27 isolated receiver proposals. Blender 5.0.1. No generator execution.
Run: blender -b --python build_r27.py
All sizes below are experimental; 1:1 native units, no physical conversion.
"""
import bpy, math, json, hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/home/christopher/Desktop/F5ZP_M01_R21_EXPERIMENTAL_20261105')
OUT=Path('/home/christopher/Desktop/F5ZP_M01_R27_RECEIVERS_EXPERIMENTAL_20261105')
SOURCE=ROOT/'F5ZP_M01_R21_B_PORTABLE_EXPERIMENTAL.blend'
PROTECTED=[SOURCE,Path('/home/christopher/Desktop/newgen_F5ZN_A_CHEVET_STUDY_1to1.blend'),Path('/home/christopher/Desktop/F5ZP_M01_R15_R20_EXPERIMENTAL_20261105/F5ZP_M01_R15_R20_EXPERIMENTAL_V03.blend')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p) for p in PROTECTED}
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False)
sc=bpy.context.scene
def signature(o):
 if o.type=='MESH':d=[[list(v.co) for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons]]
 elif o.type=='CURVE':d=[[[list(p.co) for p in s.points],[list(p.co) for p in s.bezier_points]] for s in o.data.splines]
 else:d=[]
 return hashlib.sha256(json.dumps([d,[list(r) for r in o.matrix_world]],sort_keys=True).encode()).hexdigest()
original={o.name:signature(o) for o in sc.objects}
def coords(o):return [o.matrix_world@v.co for v in o.data.vertices]
def tree(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
 t=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[list(f.vertices) for f in m.polygons]);e.to_mesh_clear();return t
def hull(points):
 pp=sorted(set((round(p[0],5),round(p[1],5)) for p in points))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 ll=[]
 for p in pp:
  while len(ll)>1 and cross(ll[-2],ll[-1],p)<=0:ll.pop()
  ll.append(p)
 uu=[]
 for p in reversed(pp):
  while len(uu)>1 and cross(uu[-2],uu[-1],p)<=0:uu.pop()
  uu.append(p)
 return ll[:-1]+uu[:-1]
def inside(p,poly):
 x,y=p;res=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:res=not res
 return res
def poly_overlap(a,b):
 if any(inside(q,b) for q in a) or any(inside(q,a) for q in b):return True
 def cr(x,y):return x[0]*y[1]-x[1]*y[0]
 for p,q in zip(a,a[1:]+a[:1]):
  for r,t in zip(b,b[1:]+b[:1]):
   d=Vector(q)-Vector(p);e=Vector(t)-Vector(r);den=cr(d,e)
   if abs(den)>1e-9:
    ac=Vector(r)-Vector(p);x=cr(ac,e)/den;y=cr(ac,d)/den
    if 0<=x<=1 and 0<=y<=1:return True
 return False
def prism(name,poly,z,col,mat):
 n=len(poly);verts=[(x,y,h) for h in [0,z] for x,y in poly]
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat);ob['STATUS']='EXPERIMENTAL_UNAPPROVED';return ob
walls=[o for o in sc.objects if o.type=='MESH' and o.name.startswith('R18_') and ('WALL' in o.name or 'CHEEK' in o.name)]
roofs=[o for o in sc.objects if o.type=='MESH' and o.name.startswith('R18_') and 'ROOF' in o.name]
cheeks=[o for o in walls if 'CHEEK' in o.name]
walltrees={o.name:tree(o) for o in walls}
roof_trees={o.name:tree(o) for o in roofs}
pads={i:sc.objects[f'TRIAL_PAD_O_{i}'] for i in [40,60,80,100,120,140]}
centers={i:sum(coords(o),Vector())/len(o.data.vertices) for i,o in pads.items()}
footprints={o.name:hull(coords(o)) for o in walls+list(pads.values())}
cols={};rows=[];objects={};meshes={}
for kind,color in [('ENGAGED',(0.12,.52,.8,1)),('T_PLAN',(.8,.32,.12,1)),('DETACHED',(.55,.25,.7,1))]:
 col=bpy.data.collections.new('R27_'+kind+'_EXPERIMENTAL');sc.collection.children.link(col);cols[kind]=col
 mat=bpy.data.materials.new('R27_'+kind);mat.diffuse_color=color
 objects[kind]=[]
 for station,pad in pads.items():
  p=centers[station].copy();p.z=2300
  wall=min(cheeks,key=lambda o:walltrees[o.name].find_nearest(p)[3])
  vs=coords(wall);xy=[v.to_2d() for v in vs];c=sum(xy,Vector((0,0)))/len(xy)
  xx=sum((q.x-c.x)**2 for q in xy);yy=sum((q.y-c.y)**2 for q in xy);xyc=sum((q.x-c.x)*(q.y-c.y) for q in xy)
  angle=.5*math.atan2(2*xyc,xx-yy);u=Vector((math.cos(angle),math.sin(angle)))
  radial=Vector((p.x-20213,p.y)).normalized()
  if u.dot(radial)<0:u=-u
  v=Vector((-u.y,u.x))
  width=max(v.dot(q.to_2d()-p.to_2d()) for q in coords(pad))-min(v.dot(q.to_2d()-p.to_2d()) for q in coords(pad))
  w=width*.75;L=width*2;back=width*.35;head=width*1.5
  if kind=='ENGAGED':local=[(-back,-w/2),(L,-w/2),(L,w/2),(-back,w/2)]
  elif kind=='T_PLAN':local=[(-back,-w/2),(L-w,-w/2),(L-w,-head/2),(L,-head/2),(L,head/2),(L-w,head/2),(L-w,w/2),(-back,w/2)]
  else:local=[(L+.5*width,-width/2),(L+1.5*width,-width/2),(L+1.5*width,width/2),(L+.5*width,width/2)]
  chapel_center=50 if station in [40,60] else 90 if station in [80,100] else 130
  mid=(centers[chapel_center-10].to_2d()+centers[chapel_center+10].to_2d())/2
  toward=1 if v.dot(mid-p.to_2d())>0 else -1
  wall_v=[v.dot(q.to_2d()-p.to_2d()) for q in vs]
  limit=max(wall_v) if toward>0 else min(wall_v)
  if kind in ['ENGAGED','T_PLAN']:
   adjusted=[]
   for x,y in local:
    span=head if kind=='T_PLAN' and x>=L-w-1e-5 and abs(y)>w/2+1e-5 else w
    # T flange extends solely to the recess side, retaining a flush inner face.
    yy=limit-toward*(span/2)+y
    adjusted.append((x,yy))
   # Explicit T outline avoids reversing the interior edge at the flange.
   if kind=='T_PLAN':
    inner=limit;outer=limit-toward*w;flange=limit-toward*head
    adjusted=[(-back,outer),(L-w,outer),(L-w,flange),(L,flange),(L,inner),(-back,inner)]
    if toward<0:adjusted=list(reversed(adjusted))
   local=adjusted
   poly=[list(p.to_2d()+u*x+v*y) for x,y in local]
  else:
   for step in range(1,21):
    poly=[list(p.to_2d()+u*x+v*(y-toward*width*.5*step)) for x,y in local]
    if not any(poly_overlap(poly,q) for q in footprints.values()):break
  name=f'R27_{kind}_{station}';o=prism(name,poly,3900,col,mat);objects[kind].append(o);t=tree(o)
  contacts=[{'wall':wob.name,'triangle_pairs':len(t.overlap(walltrees[wob.name]))} for wob in walls if t.overlap(walltrees[wob.name])]
  roofhits=[{'roof':n,'triangle_pairs':len(t.overlap(rt))} for n,rt in roof_trees.items() if t.overlap(rt)]
  roofgaps=[]
  for q in poly+[list(sum((Vector(q) for q in poly),Vector((0,0)))/len(poly))]:
   for rt in roof_trees.values():
    hit=rt.ray_cast(Vector((q[0],q[1],3900)),Vector((0,0,1)),10000)
    if hit[0] is not None:roofgaps.append(hit[3])
  edgecount=Counter(tuple(sorted((f.vertices[j],f.vertices[(j+1)%len(f.vertices)]))) for f in o.data.polygons for j in range(len(f.vertices)))
  row={'kind':kind,'station':station,'name':name,'wall_axis_source':wall.name,'landing':[p.x,p.y,p.z],'axis_xy':list(u),'footprint':poly,'top_z':3900,'trial_pad_width':width,'stem_width':w,'stem_length':L,'pad_landing_inside_receiver':inside(p.to_2d(),poly),'nearest_cheek_distance_at_landing':walltrees[wall.name].find_nearest(p)[3],'wall_surface_intersections':contacts,'roof_surface_intersections':roofhits,'sampled_vertical_roof_gap_min':min(roofgaps) if roofgaps else None,'roof_sample_hit_count':len(roofgaps),'nonmanifold_edges':sum(n!=2 for n in edgecount.values()),'approved_bearing':False}
  rows.append(row)
  o['SET_OUT_SOURCE']=wall.name;o['DIMENSIONS_STATUS']='trial proportions from saved pad width; top Z3900 trial';o['LANDING_STATION']=station
# Exact line/polygon crossings in plan at Z1500; report central clear interval only.
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
def width_at(c,t,polys):
 if any(inside(c,p) for p in polys):return 0.
 left,right=-2000.,2000.
 for poly in polys:
  for a,b in zip(poly,poly[1:]+poly[:1]):
   d=Vector(b)-Vector(a);den=cross2(t,d)
   if abs(den)<1e-8:continue
   ac=Vector(a)-c;s=cross2(ac,d)/den;v=cross2(ac,t)/den
   if 0<=v<=1:
    if s<=0:left=max(left,s)
    else:right=min(right,s)
 return right-left
sections=[]
basepolys=list(footprints.values())
for chapel,station in [('NORTH',50),('AXIAL',90),('SOUTH',130)]:
 a=centers[station-10].to_2d();b=centers[station+10].to_2d();mid=(a+b)/2;t=(b-a).normalized();u=Vector((mid.x-20213,mid.y)).normalized()
 for depth in [0,500,1000]:
  c=mid+u*depth
  for kind in ['BASELINE']+list(cols):
   polys=basepolys+[r['footprint'] for r in rows if r['kind']==kind]
   sections.append({'chapel':chapel,'depth':depth,'variant':kind,'center':list(c),'direction':list(t),'z':1500,'central_clear_width':width_at(c,t,polys),'search_limit_each_side':2000})
assert all(signature(sc.objects[n])==h for n,h in original.items())
assert all(sha(Path(p))==h for p,h in before.items())
sc['M01_STATUS']='OPEN; R27 RECEIVER MORPHOLOGY STUDY ONLY'
sc['R27_BASELINE']='R21 B preserved; R22 comparator diagnostics retained separately, not used for setout'
sc['R27_HEIGHT']='Z3900 trial; no validated high-vault thrust landing'
# Only engaged proposal is shown by default; others stay selectable in collections.
for k,c in cols.items():c.hide_viewport=k!='ENGAGED';c.hide_render=k!='ENGAGED'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'F5ZP_M01_R27_B_RECEIVERS_EXPERIMENTAL.blend'),check_existing=False)
for kind,col in cols.items():
 for k,c in cols.items():c.hide_viewport=False
 bpy.ops.object.select_all(action='DESELECT')
 selected=[]
 for o in sc.objects:
  if o.type not in ('MESH','CURVE'):continue
  if o.name.startswith('R27_') and o not in objects[kind]:continue
  if any(c.name.startswith(('90_V03','R21_LINKED_R03')) for c in o.users_collection):continue
  o.hide_set(False);o.select_set(True);selected.append(o)
 bpy.ops.export_scene.gltf(filepath=str(OUT/f'R27_B_{kind}_EXPERIMENTAL.glb'),export_format='GLB',use_selection=True,export_extras=True)
report={'status':'EXPERIMENTAL_M01_OPEN','source':str(SOURCE),'source_hashes_before':before,'source_hashes_after':{p:sha(Path(p)) for p in before},'all_original_object_signatures_unchanged':True,'units':'1:1 project native; metres per unit unresolved','coordinate_system':'X east Y north Z up; center (20213,0); azimuth clockwise from +Y','receivers':rows,'passage_sections':sections,'baseline_plan_polygons':footprints,'unresolved':['No approved receiving-face authority/F5ZL-C schedule','Z3900 receiver height and widths are trial assumptions','No high-vault thrust endpoints or flyer profiles recovered: no flyers fabricated','No structural capacity or foundation assessment','No whole cathedral clearance proof','700-unit spring difference preserved, unresolved','Sampled roof gaps do not prove full envelope clearance','BVH surface intersections do not prove bonded masonry or detect all containment','B remains unapproved; protected generator identity still unresolved','R22 corrected comparator diagnosis retained separately; no V13 fit asserted']}
(OUT/'R27_MEASUREMENTS.json').write_text(json.dumps(report,indent=2))
print('R27_RESULT',json.dumps({'receivers':len(rows),'original_objects':len(original),'source_hashes_equal':before==report['source_hashes_after'],'nonmanifold_edges':sum(r['nonmanifold_edges'] for r in rows),'landings_inside':{k:sum(r['pad_landing_inside_receiver'] for r in rows if r['kind']==k) for k in cols}}),flush=True)
