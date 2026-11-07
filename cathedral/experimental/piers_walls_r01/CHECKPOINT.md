# PIERS AND WALLS R01 — EXPERIMENTAL

Native 1:1 coordinate fixture from axial chapel R04 bay 1; not an approved baseline. Existing ribs/webs/shaft geometry preserved. New outward walls and provisional receiving cores only. 320 native units is a trial; SI conversion unresolved. No cathedral/Pass6J/working inner-middle generator changes. F5ZL-C schedule unresolved. No historical or structural assessment.

## Reproduce
Save the Python section as generate.py in a new experimental directory on MR COMPUTER and run `blender -b -t 4 --python /absolute/path/generate.py`. Source .blend and its SHA256 are recorded below. Output .blend/.glb/QA and renders remain on MR COMPUTER at `/home/christopher/Documents/Cathedral/experimental/PIERS_WALLS_R01`. This checkpoint records source and test evidence; it does not embed the source .blend or generated binaries. Receiving contact check is vertex incidence at backing lines, not full bearing-area verification; solids overlap intentionally and are not boolean-unioned. Visual inspection completed for the composite PNG. PNG shows a near-wall cutaway and complete two-wall view.

## Source and measured QA

/home/christopher/Documents/Cathedral/experimental/PIERS_WALLS_R01/CONFIG.json: text/plain (text)
/home/christopher/Documents/Cathedral/experimental/PIERS_WALLS_R01/QA.json: text/plain (text)

--- /home/christopher/Documents/Cathedral/experimental/PIERS_WALLS_R01/CONFIG.json contents: ---
[Reading 40 lines from start (total: 40 lines, 0 remaining)]

{
  "revision": "PIERS_WALLS_R01_EXPERIMENTAL",
  "parameters": {
    "west": 28600.0,
    "east": 31000.0,
    "half": 1250.0,
    "spring": 1800.0,
    "wall": 320.0,
    "core_half_length": 220.0,
    "wall_top": 4100.0
  },
  "source": "/home/christopher/Downloads/F5ZP_Axial_Chapel_R04_EXPERIMENTAL/Axial_Chapel_R04_EXPERIMENTAL.blend",
  "source_sha256": "e87d95019f22fc88083dca564b46c3b0f0e378bc372269c8002dfe5a3eb44906",
  "units": "native project units, numerical 1:1; SI calibration unresolved",
  "reference_objects": [
    "BAY1_BOSS",
    "BAY1_FORMERET_0",
    "BAY1_FORMERET_2",
    "BAY1_RIB_0",
    "BAY1_RIB_0_MATCHING_SHAFT",
    "BAY1_RIB_1",
    "BAY1_RIB_1_MATCHING_SHAFT",
    "BAY1_RIB_2",
    "BAY1_RIB_2_MATCHING_SHAFT",
    "BAY1_RIB_3",
    "BAY1_RIB_3_MATCHING_SHAFT",
    "BAY1_WEB_0",
    "BAY1_WEB_1",
    "BAY1_WEB_2",
    "BAY1_WEB_3",
    "CHAPEL_TRANSVERSE_31000",
    "CHAPEL_TRANSVERSE_31000_SHAFT_0",
    "CHAPEL_TRANSVERSE_31000_SHAFT_1",
    "ENTRANCE_ORDER_4",
    "ENTRANCE_ORDER_4_SHAFT_0",
    "ENTRANCE_ORDER_4_SHAFT_1"
  ],
  "scope": "Axial chapel bay1 R04 experimental fixture; not Pass6J or approved inner/middle vaults",
  "core_status": "provisional receiving envelopes, no detailed profile or capacity approval"
}

--- /home/christopher/Documents/Cathedral/experimental/PIERS_WALLS_R01/QA.json contents: ---
[Reading 65 lines from start (total: 65 lines, 0 remaining)]

{
  "checks": {
    "reference_world_vertices_and_faces_unchanged": true,
    "new_solids_closed": true,
    "finite_coordinates": true,
    "new_masonry_outside_reserved_plan": true,
    "all_retained_shafts_received": true,
    "source_file_hash_unchanged": true,
    "glb_object_names_and_count": true,
    "glb_bounds_within_0_01": true,
    "glb_triangle_counts": true
  },
  "passed": 9,
  "total": 9,
  "glb_bounds_max_error": 0.0,
  "shaft_receiving_contacts": [
    {
      "shaft": "BAY1_RIB_0_MATCHING_SHAFT",
      "top_vertices": 69,
      "vertices_received": 10
    },
    {
      "shaft": "BAY1_RIB_1_MATCHING_SHAFT",
      "top_vertices": 69,
      "vertices_received": 10
    },
    {
      "shaft": "BAY1_RIB_2_MATCHING_SHAFT",
      "top_vertices": 69,
      "vertices_received": 10
    },
    {
      "shaft": "BAY1_RIB_3_MATCHING_SHAFT",
      "top_vertices": 69,
      "vertices_received": 10
    },
    {
      "shaft": "CHAPEL_TRANSVERSE_31000_SHAFT_0",
      "top_vertices": 69,
      "vertices_received": 2
    },
    {
      "shaft": "CHAPEL_TRANSVERSE_31000_SHAFT_1",
      "top_vertices": 69,
      "vertices_received": 2
    },
    {
      "shaft": "ENTRANCE_ORDER_4_SHAFT_0",
      "top_vertices": 69,
      "vertices_received": 2
    },
    {
      "shaft": "ENTRANCE_ORDER_4_SHAFT_1",
      "top_vertices": 69,
      "vertices_received": 2
    }
  ],
  "validation": {
    "technical": "script executed; GLB export/import; meshes and bounds tested",
    "geometric": "listed checks only; core contact is sampled backing-line incidence, not area/capacity proof",
    "architectural": "EXPERIMENTAL, R04 fixture and 320 wall trial; not approved cathedral architecture",
    "historical": "not assessed; no historical profile claim",
    "structural": "not assessed; F5ZL-C support schedule unresolved"
  }
}

[executed on device: MR.COMPUTER (c5066a3f-7c79-446e-8649-efbb75d9e7d4)]

## Executed generator

```python
import bpy, json, math, hashlib, pathlib, collections
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent
SRC=pathlib.Path('/home/christopher/Downloads/F5ZP_Axial_Chapel_R04_EXPERIMENTAL/Axial_Chapel_R04_EXPERIMENTAL.blend')
P=dict(west=28600.,east=31000.,half=1250.,spring=1800.,wall=320.,core_half_length=220.,wall_top=4100.)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source_hash=digest(SRC)
bpy.ops.wm.open_mainfile(filepath=str(SRC))
def coords(o):return [tuple(o.matrix_world@v.co) for v in o.data.vertices]
def sig(o):return hashlib.sha256(repr((coords(o),[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
keep=[]
for o in list(bpy.data.objects):
 if o.type=='MESH' and (o.name.startswith('BAY1_') or o.name.startswith('CHAPEL_TRANSVERSE_31000') or o.name.startswith('ENTRANCE_ORDER_4')):
  keep.append(o)
 else:bpy.data.objects.remove(o,do_unlink=True)
reference={o.name:sig(o) for o in keep}
# Retained objects are experimental R04 evidence, never an approved cathedral replacement.
def material(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;return m
stone=material('NEW_OUTWARD_MASONRY',(.48,.38,.25))
ribmat=material('REUSED_R04_MOULDINGS',(.72,.60,.40))
webmat=material('REUSED_R04_WEBS',(.80,.77,.69))
for o in keep:
 o.data.materials.clear();o.data.materials.append(webmat if 'WEB' in o.name else ribmat)
new=[]
def mesh(name,v,f,mat=stone):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
 o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);o.data.materials.append(mat);new.append(o);return o
def prism(name,poly,z0,z1):
 n=len(poly);v=[(x,y,z) for z in (z0,z1) for x,y in poly]
 return mesh(name,v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
def block(name,x0,x1,y0,y1,z0,z1):return prism(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1)
# Cores stay entirely outside |Y|=1250. Footprints are provisional, not capacities.
for x in (P['west'],P['east']):
 for sign in (-1,1):
  y0,y1=sorted([sign*1250,sign*(1250+P['wall'])])
  block('CORE_%d_%d'%(x,sign),x-220,x+220,y0,y1,0,1800)
  block('BASE_%d_%d'%(x,sign),x-250,x+250,*sorted([sign*1250,sign*1600]),0,100)
# Actual pointed lancet apertures: same R04 sill, margin, spring and head; outward depth is the only wall change.
margin=240.;span=1920.;h=span/2;rise=1350.;c=(rise*rise-h*h)/(2*h);r=h+c
curve=[]
for i in range(97):
 u=span*i/96
 curve.append((28600+margin+u,1800+math.sqrt(max(0,r*r-(abs(u-h)+c)**2))))
for sign in (-1,1):
 y0,y1=sorted([sign*1250,sign*1570])
 block('WALL_SILL_'+str(sign),28600,31000,y0,y1,0,550)
 for x0,x1 in ((28600,28840),(30760,31000)):block('WALL_JAMB_'+str(sign)+'_'+str(x0),x0,x1,y0,y1,550,4100)
 poly=curve+[(30760,4100),(28840,4100)]
 n=len(poly);v=[(x,y,z) for y in (y0,y1) for x,z in poly]
 # Recalculate winding below, including the XZ extrusion.
 mesh('WALL_SPANDREL_'+str(sign),v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
floor=block('DISPLAY_FLOOR',28200,31400,-1800,1800,-80,-30)
# Normalize new closed-mesh normals without modifying reference geometry.
for o in new:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
def edge_check(o):
 edges=collections.Counter()
 for p in o.data.polygons:
  vs=list(p.vertices)
  for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))]+=1
 return all(n==2 for n in edges.values())
checks={}
checks['reference_world_vertices_and_faces_unchanged']=all(sig(o)==reference[o.name] for o in keep)
checks['new_solids_closed']=all(edge_check(o) for o in new)
checks['finite_coordinates']=all(math.isfinite(q) for o in keep+new for v in coords(o) for q in v)
checks['new_masonry_outside_reserved_plan']=all(all(abs(v[1])>=1249.999 for v in coords(o)) for o in new if o!=floor)
# Exact shaft-top rows provide attachment tests; core bounds receive their backing line.
shafts=[o for o in keep if 'SHAFT' in o.name]
contacts=[]
for o in shafts:
 top=[Vector(v) for v in coords(o) if abs(v[2]-1800)<.001]
 hits=[]
 for core in [a for a in new if a.name.startswith('CORE_')]:
  vs=coords(core);lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)]
  hits += [v for v in top if all(lo[k]-.01<=v[k]<=hi[k]+.01 for k in range(3))]
 contacts.append(dict(shaft=o.name,top_vertices=len(top),vertices_received=len(hits)))
checks['all_retained_shafts_received']=all(x['vertices_received']>0 for x in contacts)
checks['source_file_hash_unchanged']=digest(SRC)==source_hash
config=dict(revision='PIERS_WALLS_R01_EXPERIMENTAL',parameters=P,source=str(SRC),source_sha256=source_hash,units='native project units, numerical 1:1; SI calibration unresolved',reference_objects=list(reference),scope='Axial chapel bay1 R04 experimental fixture; not Pass6J or approved inner/middle vaults',core_status='provisional receiving envelopes, no detailed profile or capacity approval')
(R/'CONFIG.json').write_text(json.dumps(config,indent=2))
# Save, export, then clear and reimport the actual GLB for round-trip tests and rendering.
bpy.ops.wm.save_as_mainfile(filepath=str(R/'PIERS_WALLS_R01.blend'))
def snapshot(obs):
 return {o.name:dict(bounds=[[min(v[k] for v in coords(o)) for k in range(3)],[max(v[k] for v in coords(o)) for k in range(3)]],triangles=sum(len(p.vertices)-2 for p in o.data.polygons)) for o in obs}
before=snapshot(keep+new)
bpy.ops.export_scene.gltf(filepath=str(R/'PIERS_WALLS_R01.glb'),export_format='GLB',export_cameras=False,export_lights=False)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(R/'PIERS_WALLS_R01.glb'))
after=snapshot([o for o in bpy.context.scene.objects if o.type=='MESH'])
checks['glb_object_names_and_count']=set(before)==set(after)
error=max(abs(before[n]['bounds'][j][k]-after[n]['bounds'][j][k]) for n in before for j in range(2) for k in range(3))
checks['glb_bounds_within_0_01']=error<.01
checks['glb_triangle_counts']=all(before[n]['triangles']==after[n]['triangles'] for n in before)
qa=dict(checks=checks,passed=sum(checks.values()),total=len(checks),glb_bounds_max_error=error,shaft_receiving_contacts=contacts,validation=dict(technical='script executed; GLB export/import; meshes and bounds tested',geometric='listed checks only; core contact is sampled backing-line incidence, not area/capacity proof',architectural='EXPERIMENTAL, R04 fixture and 320 wall trial; not approved cathedral architecture',historical='not assessed; no historical profile claim',structural='not assessed; F5ZL-C support schedule unresolved'))
(R/'QA.json').write_text(json.dumps(qa,indent=2))
assert all(checks.values()),qa
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=1100;scene.render.resolution_y=950;scene.render.resolution_percentage=100
scene.world.color=(.65,.65,.65)
scene.view_settings.view_transform='AgX'
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(25200,-6500,4900));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=6500;cam.data.clip_end=100000;scene.camera=cam;aim(cam,(29800,0,2100))
for loc,power,size in [((28000,-4000,8500),1800000000,5000),((33000,3500,6500),1300000000,4000)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(29800,0,1800))
# Front wall removed only from cutaway rendering; full GLB retains both walls.
for o in scene.objects:
 if o.name.startswith('WALL_') and any(v[1]<-1249 for v in coords(o) if o.type=='MESH'):o.hide_render=True
scene.render.filepath=str(R/'CUTAWAY.png');bpy.ops.render.render(write_still=True)
for o in scene.objects:
 if o.type=='MESH':o.hide_render=False
cam.location=(26500,-5800,3800);aim(cam,(29800,0,1900))
scene.render.filepath=str(R/'EXTERIOR.png');bpy.ops.render.render(write_still=True)
print('RESULT',json.dumps(qa))

```
