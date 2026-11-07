# Individual stone masonry R01 — EXPERIMENTAL

## Scope and preservation
Split the saved PIERS_WALLS_R01 bay masonry mass into individually editable stone and mortar solids. Original R04 ribs, webs, compound shafts and display floor are reused without vertex/face changes. Native numerical 1:1, X east/Y north/Z up. Physical SI calibration remains unresolved. No approved architecture, protected generator or Pass6J record changed. No promotion.

## Trial construction
200-unit courses, nominal 520-unit blocks, 6-unit joints, 120-unit radial arch ring, ten voussoirs per arch half. 192 ashlar/plinth blocks, 40 voussoirs and six mortar solids. Mortar and stones together reconstruct the source envelopes. Overlapping R01 wall/core masses are first unioned; source plinths are owned by their separate 350-depth layer. Alternating joint staggering is a local planar trial; full-depth blocks do not establish a historically authenticated three-dimensional bond. Original compound responds and vault rib profiles remain continuous, not stone-cut. Two sub-500 square-unit slivers are assigned to mortar and require later refinement for a cutting schedule. No fabrication-ready or structural claim.

## Tests and interpretation
22/22 recorded technical/geometric checks passed. Plan union comparisons use area tolerance 0.01 square native units. All generated meshes closed, finite and positive-volume before export. Actual GLB export/reimport checks object names/count, triangle counts and bounds (tolerance 0.01 native units). Source/reference meshes and source file hash unchanged. Caps with holes use constrained triangulation. Numerical plan-envelope difference is zero; GLB bounds difference zero. Visual review completed on the two-panel PNG rendered from the imported GLB.

Architectural: experimental dimensions and local bond, review pending. Historical: not assessed. Structural: not assessed; F5ZL-C support schedule missing; no capacity or mortar property checks. Collision/envelope tests are not structural signoff. No precision/fabrication schedule is certified.

## Reproduce
Keep prepare_stones.py and build_and_verify.py together in a new experimental directory; run `blender -b -t 4 --python /absolute/path/build_and_verify.py`. Requires MR COMPUTER Blender, system Python 3 with Shapely 2.1.2, source .blend recorded below. Inputs are extracted from the saved mesh; no vault rebuild. Outputs: MASONRY_STONES_R01.blend, .glb, SOURCE_SILHOUETTES.json, STONE_MESHES.json, PLAN_QA.json, QA.json and rendered previews. Retained at `/home/christopher/Documents/Cathedral/experimental/MASONRY_STONES_R01`. User-facing upload is PNG only.

## Measured QA
```json
{
  "revision": "MASONRY_STONES_R01_EXPERIMENTAL",
  "source": "/home/christopher/Documents/Cathedral/experimental/PIERS_WALLS_R01/PIERS_WALLS_R01.blend",
  "source_sha256": "71c0e1908f0a2643acb214f9aeb8acdccb5794d68a0de3de2a07cf6a151512a4",
  "checks": {
    "-1_MAIN_no_stone_overlap": true,
    "-1_MAIN_within_source": true,
    "-1_MAIN_envelope_retained": true,
    "-1_PLINTH_no_stone_overlap": true,
    "-1_PLINTH_within_source": true,
    "-1_PLINTH_envelope_retained": true,
    "1_MAIN_no_stone_overlap": true,
    "1_MAIN_within_source": true,
    "1_MAIN_envelope_retained": true,
    "1_PLINTH_no_stone_overlap": true,
    "1_PLINTH_within_source": true,
    "1_PLINTH_envelope_retained": true,
    "all_caps_exactly_triangulated": true,
    "all_prepared_meshes_closed": true,
    "retained_ribs_webs_shafts_floor_unchanged": true,
    "parent_blend_hash_unchanged": true,
    "all_new_meshes_closed": true,
    "all_new_meshes_finite": true,
    "all_new_meshes_positive_volume": true,
    "glb_name_count_roundtrip": true,
    "glb_bounds_roundtrip_within_0_01": true,
    "glb_triangle_counts_roundtrip": true
  },
  "stone_counts": {
    "voussoir": 40,
    "ashlar": 192,
    "mortar": 6
  },
  "glb_roundtrip_max_bounds_error": 0,
  "geometry_metrics": {
    "-1_MAIN": {
      "source_area": 6248084.833984375,
      "stone_area": 5918671.527763923,
      "mortar_area": 329413.3062204518,
      "stone_overlap_area": -9.313225746154785e-10,
      "outside_source_area": 0,
      "envelope_difference_area": 0
    },
    "-1_PLINTH": {
      "source_area": 100000,
      "stone_area": 91744,
      "mortar_area": 8256,
      "stone_overlap_area": 0,
      "outside_source_area": 0,
      "envelope_difference_area": 0
    },
    "1_MAIN": {
      "source_area": 6248084.833984375,
      "stone_area": 5918671.527763923,
      "mortar_area": 329413.3062204518,
      "stone_overlap_area": -9.313225746154785e-10,
      "outside_source_area": 0,
      "envelope_difference_area": 0
    },
    "1_PLINTH": {
      "source_area": 100000,
      "stone_area": 91744,
      "mortar_area": 8256,
      "stone_overlap_area": 0,
      "outside_source_area": 0,
      "envelope_difference_area": 0
    }
  },
  "small_pieces_omitted_to_mortar": 2,
  "validation": {
    "technical": "Python/Blender execution and actual GLB reimport tested",
    "geometric": "source mass envelopes retained, disjoint stones and mortar, original rib/web/shaft arrays unchanged",
    "architectural": "EXPERIMENTAL local bay; course/bond/ring dimensions unapproved; compound profiles remain continuous",
    "historical": "not assessed; no claim of a historical bonding pattern",
    "structural": "not assessed; F5ZL-C support schedule missing; no capacity or mortar-property checks"
  },
  "passed": 22,
  "total": 22
}
```

## prepare_stones.py
```python
import json,math,pathlib,collections
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
from shapely.geometry.polygon import orient
R=pathlib.Path(__file__).resolve().parent
D=json.loads((R/'SOURCE_SILHOUETTES.json').read_text())
cfg=dict(course=200.,block=520.,joint=6.,arch_ring=120.,voussoirs_per_half=10,units='native project units; numerical 1:1; SI unresolved',status='EXPERIMENTAL')
items=[];metrics={};checks={};tiny=[]
def polygons(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for x in g.geoms for p in polygons(x)]
def add(name,g,ylo,yhi,kind):
 for i,p in enumerate(polygons(g)):
  if p.area>1e-5:items.append(dict(name=name+'_'+str(i),poly=p,ylo=ylo,yhi=yhi,kind=kind))
def courses(mask,label,ylo,yhi,course=200):
 stones=[]
 zmin,zmax=mask.bounds[1],mask.bounds[3];xmin,xmax=mask.bounds[0],mask.bounds[2]
 for row,z0 in enumerate(range(int(zmin//course)*course,int(zmax)+1,course)):
  shift=cfg['block']/2 if row%2 else 0
  for col in range(math.floor((xmin-shift)/cfg['block'])-1,math.ceil((xmax-shift)/cfg['block'])+1):
   x0=shift+col*cfg['block']
   stone=mask.intersection(box(x0,z0,x0+cfg['block'],z0+course)).buffer(-cfg['joint']/2,join_style=2)
   for p in polygons(stone):
    if p.area<500:tiny.append(dict(region=label,area=p.area));continue
    add(label+'_C%02d_B%03d'%(row,col),p,ylo,yhi,'ashlar');stones.append(p)
 return stones
for side,source in D['sides'].items():
 sign=int(side);full=unary_union([Polygon(p) for p in source['main']]);base=unary_union([Polygon(p) for p in source['base']])
 wall=full.difference(base)
 ylo,yhi=sorted([sign*1250,sign*1570]);blo,bhi=sorted([sign*1250,sign*1600])
 left,right,mid,spring=28840.,30760.,29800.,1800.
 h=(right-left)/2;rise=1350.;c=(rise*rise-h*h)/(2*h);radius=h+c;ringparts=[]
 for hand in (-1,1):
  cx=left+radius if hand<0 else right-radius
  apex=math.acos(-c/(radius+cfg['arch_ring']))
  for j in range(cfg['voussoirs_per_half']):
   a0=math.pi-(math.pi-apex)*j/cfg['voussoirs_per_half'];a1=math.pi-(math.pi-apex)*(j+1)/cfg['voussoirs_per_half']
   aa=[a0+(a1-a0)*k/12 for k in range(13)]
   def point(r,a):
    x=cx+r*math.cos(a);return (x if hand<0 else 2*cx-x,spring+r*math.sin(a))
   poly=Polygon([point(radius,a) for a in aa]+[point(radius+cfg['arch_ring'],a) for a in reversed(aa)])
   clip=box(left-200,spring,mid,4100) if hand<0 else box(mid,spring,right+200,4100)
   p=poly.intersection(clip).intersection(wall);ringparts.append(p)
   add('VOUSSOIR_S%s_H%s_%02d'%(side,hand,j),p.buffer(-cfg['joint']/2,join_style=2),ylo,yhi,'voussoir')
 ring=unary_union(ringparts)
 courses(wall.difference(ring),'WALL_S'+side,ylo,yhi)
 courses(base,'PLINTH_S'+side,blo,bhi,100)
 for label,mask,stones,a,b in [('MAIN',wall,[i['poly'] for i in items if i['ylo']==ylo and i['yhi']==yhi],ylo,yhi),('PLINTH',base,[i['poly'] for i in items if i['ylo']==blo and i['yhi']==bhi],blo,bhi)]:
  u=unary_union(stones);mortar=mask.difference(u);add('MORTAR_S'+side+'_'+label,mortar,a,b,'mortar')
  overlap=sum(p.area for p in stones)-u.area;outside=u.difference(mask).area;err=u.union(mortar).symmetric_difference(mask).area
  metrics[side+'_'+label]=dict(source_area=mask.area,stone_area=u.area,mortar_area=mortar.area,stone_overlap_area=overlap,outside_source_area=outside,envelope_difference_area=err)
  checks[side+'_'+label+'_no_stone_overlap']=abs(overlap)<.01
  checks[side+'_'+label+'_within_source']=outside<.01
  checks[side+'_'+label+'_envelope_retained']=err<.01
meshes=[]
for item in items:
 p=orient(item['poly'],sign=1);verts=[];index={}
 def vertex(x,z,layer):
  key=(float(x),item['ylo'] if layer==0 else item['yhi'],float(z))
  if key not in index:index[key]=len(verts);verts.append(key)
  return index[key]
 faces=[];ts=list(constrained_delaunay_triangles(p).geoms)
 assert abs(sum(t.area for t in ts)-p.area)<.01
 for tri in ts:
  co=list(orient(tri,sign=1).exterior.coords)[:-1]
  faces.extend([[vertex(x,z,0) for x,z in co],list(reversed([vertex(x,z,1) for x,z in co]))])
 for loop in [p.exterior,*p.interiors]:
  co=list(loop.coords)
  for a,b in zip(co,co[1:]):
   i,j=vertex(*a,0),vertex(*b,0);k,l=vertex(*a,1),vertex(*b,1);faces.append([j,i,k,l])
 count=collections.Counter()
 for f in faces:
  for a,b in zip(f,f[1:]+f[:1]):count[tuple(sorted((a,b)))]+=1
 assert all(n==2 for n in count.values()),item['name']
 meshes.append(dict(name=item['name'],vertices=verts,faces=faces,kind=item['kind']))
checks['all_caps_exactly_triangulated']=True;checks['all_prepared_meshes_closed']=True
(R/'STONE_MESHES.json').write_text(json.dumps(meshes,separators=(',',':')))
report=dict(config=cfg,checks=checks,metrics=metrics,counts=dict(collections.Counter(i['kind'] for i in items)),omitted_small_pieces_to_mortar=tiny)
(R/'PLAN_QA.json').write_text(json.dumps(report,indent=2))
assert all(checks.values()),report
print('PREPARED',len(meshes),report['counts'])

```

## build_and_verify.py
```python
import bpy,pathlib,json,hashlib,subprocess,math,collections
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent
SRC=pathlib.Path('/home/christopher/Documents/Cathedral/experimental/PIERS_WALLS_R01/PIERS_WALLS_R01.blend')
parent_hash=hashlib.sha256(SRC.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SRC))
def coords(o):return [tuple(o.matrix_world@v.co) for v in o.data.vertices]
def signature(o):return hashlib.sha256(repr((coords(o),[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
source=[];sides={}
for sign in (-1,1):
 data={'main':[],'base':[]}
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or not o.name.startswith(('WALL_','CORE_','BASE_')):continue
  v=coords(o)
  if (sum(p[1] for p in v)/len(v)>0)!=(sign>0):continue
  ymin=min(p[1] for p in v)
  for f in o.data.polygons:
   pts=[v[i] for i in f.vertices]
   if all(abs(p[1]-ymin)<.001 for p in pts):data['base' if o.name.startswith('BASE_') else 'main'].append([[p[0],p[2]] for p in pts])
  if o not in source:source.append(o)
 sides[str(sign)]=data
retained=[o for o in bpy.context.scene.objects if o.type=='MESH' and o not in source]
before={o.name:signature(o) for o in retained}
(R/'SOURCE_SILHOUETTES.json').write_text(json.dumps(dict(source=str(SRC),sha256=parent_hash,sides=sides)))
subprocess.run(['/usr/bin/python3',str(R/'prepare_stones.py')],check=True)
for o in source:bpy.data.objects.remove(o,do_unlink=True)
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.82;return m
stone=[mat('ASHLAR_TONE_%d'%i,(.45+i*.022,.36+i*.019,.24+i*.016)) for i in range(5)]
mortar=mat('MORTAR',(.16,.14,.11));new=[]
for i,d in enumerate(json.loads((R/'STONE_MESHES.json').read_text())):
 me=bpy.data.meshes.new(d['name']);me.from_pydata(d['vertices'],[],d['faces']);me.update()
 o=bpy.data.objects.new(d['name'],me);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mortar if d['kind']=='mortar' else stone[i%5]);o['construction_role']=d['kind'];new.append(o)
checks={}
checks['retained_ribs_webs_shafts_floor_unchanged']=all(signature(o)==before[o.name] for o in retained)
checks['parent_blend_hash_unchanged']=hashlib.sha256(SRC.read_bytes()).hexdigest()==parent_hash
def closed(o):
 c=collections.Counter()
 for p in o.data.polygons:
  f=list(p.vertices)
  for a,b in zip(f,f[1:]+f[:1]):c[tuple(sorted((a,b)))]+=1
 return all(n==2 for n in c.values())
def volume(o):
 o.data.calc_loop_triangles();v=[Vector(x) for x in coords(o)];origin=v[0]
 return sum((v[t.vertices[0]]-origin).dot((v[t.vertices[1]]-origin).cross(v[t.vertices[2]]-origin))/6 for t in o.data.loop_triangles)
checks['all_new_meshes_closed']=all(closed(o) for o in new)
checks['all_new_meshes_finite']=all(math.isfinite(x) for o in new for v in coords(o) for x in v)
checks['all_new_meshes_positive_volume']=all(volume(o)>0 for o in new)
assert all(checks.values()),checks
bpy.ops.wm.save_as_mainfile(filepath=str(R/'MASONRY_STONES_R01.blend'))
def snapshot(obs):
 return {o.name:dict(bounds=[[min(v[k] for v in coords(o)) for k in range(3)],[max(v[k] for v in coords(o)) for k in range(3)]],triangles=sum(len(p.vertices)-2 for p in o.data.polygons)) for o in obs}
snap=snapshot(retained+new)
bpy.ops.export_scene.gltf(filepath=str(R/'MASONRY_STONES_R01.glb'),export_format='GLB',export_cameras=False,export_lights=False)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(R/'MASONRY_STONES_R01.glb'))
now=snapshot([o for o in bpy.context.scene.objects if o.type=='MESH'])
checks['glb_name_count_roundtrip']=set(snap)==set(now)
err=max(abs(snap[n]['bounds'][j][k]-now[n]['bounds'][j][k]) for n in snap for j in range(2) for k in range(3))
checks['glb_bounds_roundtrip_within_0_01']=err<.01
checks['glb_triangle_counts_roundtrip']=all(snap[n]['triangles']==now[n]['triangles'] for n in snap)
plan=json.loads((R/'PLAN_QA.json').read_text())
qa=dict(revision='MASONRY_STONES_R01_EXPERIMENTAL',source=str(SRC),source_sha256=parent_hash,checks={**plan['checks'],**checks},stone_counts=plan['counts'],glb_roundtrip_max_bounds_error=err,geometry_metrics=plan['metrics'],small_pieces_omitted_to_mortar=len(plan['omitted_small_pieces_to_mortar']),validation=dict(technical='Python/Blender execution and actual GLB reimport tested',geometric='source mass envelopes retained, disjoint stones and mortar, original rib/web/shaft arrays unchanged',architectural='EXPERIMENTAL local bay; course/bond/ring dimensions unapproved; compound profiles remain continuous',historical='not assessed; no claim of a historical bonding pattern',structural='not assessed; F5ZL-C support schedule missing; no capacity or mortar-property checks'))
qa['passed']=sum(qa['checks'].values());qa['total']=len(qa['checks'])
(R/'QA.json').write_text(json.dumps(qa,indent=2))
assert all(qa['checks'].values()),qa
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1100;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
scene.world.color=(.65,.65,.65);scene.view_settings.view_transform='AgX'
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(25200,-6500,4900));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=6100;cam.data.clip_end=100000;scene.camera=cam;aim(cam,(29800,0,2050))
for loc,power,size in [((28000,-4000,8500),1800000000,5000),((33000,3500,6500),1300000000,4000)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(29800,0,1800))
scene.render.filepath=str(R/'ASSEMBLY.png');bpy.ops.render.render(write_still=True)
cam.location=(29800,-8000,3400);cam.data.ortho_scale=3650;aim(cam,(29800,-1400,2350))
scene.render.filepath=str(R/'STONE_DETAIL.png');bpy.ops.render.render(write_still=True)
print('RESULT',json.dumps(qa))

```
