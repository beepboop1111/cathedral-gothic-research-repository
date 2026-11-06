"""Standalone flying-buttress study. Run in Blender Text Editor or background.
Only the tagged SIMPLE_FLYING_BUTTRESS_R01 collection is rebuilt.
Demonstration native units; no cathedral dimensions or structural claim.
"""
import bpy, math, json, sys, argparse
from pathlib import Path
from collections import Counter
from mathutils import Vector

DEFAULTS=dict(span=5000.0,outer_landing_z=3400.0,wall_landing_z=6000.0,
              arc_sagitta=650.0,flyer_thickness=320.0,flyer_width=420.0,
              pier_depth=1000.0,pier_width=1200.0,pier_headroom=700.0,
              wall_depth=1000.0,wall_width=1600.0,wall_height=8000.0,
              base_spread=200.0,base_height=300.0,segments=64,
              repeat_count=1,spacing=3500.0)
TAG='SIMPLE_FLYING_BUTTRESS_R01'
def validate(p):
 for k,v in p.items():
  if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):raise ValueError(k+' must be a finite number')
 for k in p:
  if k not in ('outer_landing_z','wall_landing_z') and p[k]<=0:raise ValueError(k+' must be positive')
 for k in ['segments','repeat_count']:
  if int(p[k])!=p[k]:raise ValueError(k+' must be an integer')
 if not 8<=p['segments']<=512:raise ValueError('segments must be 8..512')
 if not 1<=p['repeat_count']<=20:raise ValueError('repeat_count must be 1..20')
 if min(p['outer_landing_z'],p['wall_landing_z'])<=p['base_height']:raise ValueError('landings must be above the base')
 chord=math.hypot(p['span'],p['wall_landing_z']-p['outer_landing_z'])
 if p['arc_sagitta']>=chord/2:raise ValueError('sagitta must be less than half the chord')
 if p['span']<=(p['pier_depth']+p['wall_depth'])/2:raise ValueError('supports leave no open span')
 if p['repeat_count']>1 and p['spacing']<=max(p['wall_width'],p['pier_width']+2*p['base_spread']):raise ValueError('repeated supports overlap')

def material(name,color):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
def mesh(col,name,verts,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(mat);o['status']='EXPERIMENTAL_DEMONSTRATION';return o
def box(col,name,x,y,z,dx,dy,dz,mat):
 verts=[(x+sx*dx/2,y+sy*dy/2,z+sz*dz/2) for sz in [-1,1] for sy in [-1,1] for sx in [-1,1]]
 return mesh(col,name,verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat)
def arc(p):
 a=Vector((0.,p['outer_landing_z']));b=Vector((p['span'],p['wall_landing_z']));d=b-a;L=d.length
 n=Vector((-d.y,d.x))/L;s=p['arc_sagitta'];R=L*L/(8*s)+s/2
 center=(a+b)/2+n*(s-R)
 a0=math.atan2(a.y-center.y,a.x-center.x);a1=math.atan2(b.y-center.y,b.x-center.x)
 sweep=(a1-a0+math.pi)%(2*math.pi)-math.pi
 pp=[center+Vector((math.cos(a0+sweep*i/p['segments']),math.sin(a0+sweep*i/p['segments'])))*R for i in range(p['segments']+1)]
 qq=[center+(v-center)*(1+p['flyer_thickness']/R) for v in pp]
 if any(pp[i+1].x<=pp[i].x for i in range(len(pp)-1)):raise ValueError('arc overhangs: reduce sagitta or landing difference')
 return pp,qq,center,R,sweep
def build(p):
 validate(p);p=p.copy();p['segments']=int(p['segments']);p['repeat_count']=int(p['repeat_count'])
 bottom,top,center,R,sweep=arc(p)
 for pts,x,depth,height in [(bottom[:1]+top[:1],0,p['pier_depth'],p['outer_landing_z']+p['pier_headroom']),
                            (bottom[-1:]+top[-1:],p['span'],p['wall_depth'],p['wall_height'])]:
  if any(abs(v.x-x)>=depth/2 or v.y>=height for v in pts):raise ValueError('support does not contain complete flyer end section')
 if p['flyer_width']>min(p['pier_width'],p['wall_width']):raise ValueError('flyer wider than supports')
 old=bpy.data.collections.get(TAG)
 if old:
  if old.get('generator')!=TAG:raise ValueError('Collection name is already in use by unrelated work')
  for o in list(old.objects):
   data=o.data;bpy.data.objects.remove(o,do_unlink=True)
   if data and data.users==0 and isinstance(data,bpy.types.Mesh):bpy.data.meshes.remove(data)
  bpy.data.collections.remove(old)
 col=bpy.data.collections.new(TAG);bpy.context.scene.collection.children.link(col);col['generator']=TAG
 col['parameters_json']=json.dumps(p,sort_keys=True);col['units']='Demonstration native units; physical conversion unspecified'
 stone=material(TAG+'_STONE',(.64,.59,.49));flyer=material(TAG+'_FLYER',(.77,.64,.42))
 created=[];N=len(bottom)
 for k in range(p['repeat_count']):
  y=k*p['spacing'];name=f'FB_{k+1:02d}'
  verts=[(q.x,y+side*p['flyer_width']/2,q.y) for side in [-1,1] for line in [bottom,top] for q in line]
  faces=[]
  for i in range(N-1):
   j=i+1;faces.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
  faces.extend([(0,N,3*N,2*N),(N-1,3*N-1,4*N-1,2*N-1)])
  o=mesh(col,name+'_FLYER',verts,faces,flyer)
  # Consistent outward normals for the closed extruded band.
  import bmesh
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  created.append(o)
  height=p['outer_landing_z']+p['pier_headroom']
  created.append(box(col,name+'_RECEIVER',0,y,height/2,p['pier_depth'],p['pier_width'],height,stone))
  created.append(box(col,name+'_BASE',0,y,p['base_height']/2,p['pier_depth']+2*p['base_spread'],p['pier_width']+2*p['base_spread'],p['base_height'],stone))
  created.append(box(col,name+'_WALL',p['span'],y,p['wall_height']/2,p['wall_depth'],p['wall_width'],p['wall_height'],stone))
 qa=[]
 for o in created:
  edges=Counter(tuple(sorted((f.vertices[i],f.vertices[(i+1)%len(f.vertices)]))) for f in o.data.polygons for i in range(len(f.vertices)))
  assert all(v==2 for v in edges.values()),o.name
  qa.append(dict(object=o.name,vertices=len(o.data.vertices),nonmanifold_edges=0))
 return created,dict(status='EXPERIMENTAL_GEOMETRIC_DEMO',parameters=p,arc_center_xz=list(center),soffit_radius=R,sweep_radians=sweep,
                     endpoint_residual=max((bottom[0]-Vector((0,p['outer_landing_z']))).length,(bottom[-1]-Vector((p['span'],p['wall_landing_z']))).length),mesh_checks=qa,
                     unresolved=['No cathedral setout or historical calibration','No thrust, capacity, masonry bonding, drainage or foundations assessed'])
def main():
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 ap=argparse.ArgumentParser();ap.add_argument('--config');ap.add_argument('--out');opt=ap.parse_args(args)
 p=DEFAULTS.copy()
 if opt.config:
  values=json.loads(Path(opt.config).read_text());unknown=set(values)-set(p)
  if unknown:raise ValueError('Unknown settings: '+str(unknown))
  p.update(values)
 objects,qa=build(p)
 out=Path(opt.out) if opt.out else Path(globals().get('__file__',str(Path.cwd()/'flying_buttress.py'))).resolve().parent/'output'
 out.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.gltf(filepath=str(out/'flying_buttress.glb'),export_format='GLB',use_selection=True,export_extras=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(out/'flying_buttress.blend'))
 (out/'QA.json').write_text(json.dumps(qa,indent=2))
 (out/'parameters.json').write_text(json.dumps(p,indent=2))
 print('FLYING_BUTTRESS_SAVED',out)
if __name__=='__main__':main()
