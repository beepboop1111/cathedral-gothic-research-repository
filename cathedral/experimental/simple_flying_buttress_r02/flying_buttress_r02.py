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
