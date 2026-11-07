# Compound pier generator R01 — EXPERIMENTAL

## Baseline and bounded delta
Parent is saved MASONRY_STONES_R01.blend on MR COMPUTER, exact SHA256 in QA below. This is the experimental axial chapel bay1 fixture, not an approved cathedral baseline and not Pass6J R1/78. GitHub Master Reference recovered at task start, governance-r01 blob 1d7e358ff7562fcc64088854baa2abd3d31a729e. Scale: native numerical 1:1, X east/Y north/Z up; physical SI conversion unresolved.

Replace eight existing isolated arch/rib shaft meshes with four unified compound pier meshes. Each corner receives three actual spring sections: transverse, diagonal rib, formeret. Four missing formeret responds are included. Sections come from the saved arch/rib meshes at Z1800, 69 source vertices each; no new circle/profile approximation. The twelve actual bearings are extracted, not regularized. Core is derived after overlay from the section backing points and two outward anchors, then clipped to the prior 320-depth wall reservation. Its shape is a trial, not an authenticated or capacity-designed core. Straight extrusion runs Z0 to Z1800. No new tas-de-charge above spring, base/plinth redesign or individual pier stone cutting is attempted.

All 252 retained mesh objects have unchanged vertex arrays and polygon connectivity, including ribs, webs, existing masonry stones/mortar, backing blocks and floor. Original source files remain unchanged. Existing backing masonry remains in place; the new isolated pier contains a core that geometrically overlaps this backing intentionally. Assembly is not a boolean-unioned load model. No approved inner/middle generator, F5ZK-C/F5ZN-A geometry, original historical source or Pass6J record changed or regenerated. No promotion.

## Results and limitations
39/39 listed technical/geometric checks pass. Four connected source-derived sections, outward-only trial cores, disjoint pier footprints, closure, consistent winding, positive volume and straight vertical continuation tested. Twelve original spring section boundaries checked at 301 samples each against actual Blender float32 pier cap triangle unions, tolerance 0.005 native units; maximum sampled containment gap 0.0006580695. This is containment/contact evidence, not full load-bearing area or capacity validation. Small float32 sliver areas are explicitly reported below.

Conservative clear rectangle between pier bounding boxes: 2201.5546875 longitudinal by 2200 transverse native units. It concerns this bay and these piers only, not a full circulation compliance assessment. Parent bay set-out remains 2400 by 2500. Actual GLB reimport retains all names/counts, world bounds (zero error) and oriented world-triangle signatures at 0.001 quantization. Three-pane composite reviewed: whole assembly, isolated pier, measured spring-section overlay. Black source contours confirm recovered mesh geometry only; dashed red core is experimental; dashed gray axes are construction.

Architectural: local three-bearing chapel pier requires review; no general cathedral pier approval. Historical: not assessed, source profiles are experimental designs. Structural: not assessed; F5ZL-C support schedule remains unresolved. Exact exterior core anchor choice, current backing overlap, plinth transition, common springing mass, masonry bonding and capacities remain later work.

## Reproduction
Save the four scripts below together in a new experimental directory. Requires MR COMPUTER Blender 5.0.1 and system Python with Shapely 2.1.2, plus the exact source .blend recorded below. Execute in order:

1. `blender -b -t 4 --python extract_sections.py`
2. `python3 prepare_piers.py`
3. `blender -b -t 4 --python build_and_verify.py`
4. `python3 compose_preview.py` (Pillow, matplotlib)

The contact verifier runs automatically from build_and_verify.py. Source selectors/node IDs are specific to this first chapel-bay fixture; the per-node union, core derivation, extrusion and QA functions are procedural and shared. Outputs saved on MR COMPUTER at `/home/christopher/Documents/Cathedral/experimental/COMPOUND_PIERS_R01`: editable .blend, GLB, measurable PIER_0_SECTION_NATIVE.svg, extracted source sections, per-node mesh data, section/contact/overall QA and PNGs. User-facing upload: PNG only. Script bundle versioned here; binary models retained on MR COMPUTER, not embedded in this file.

## Measured QA
```json
{
  "revision": "COMPOUND_PIERS_R01_EXPERIMENTAL",
  "source": "/home/christopher/Documents/Cathedral/experimental/MASONRY_STONES_R01/MASONRY_STONES_R01.blend",
  "source_sha256": "6977937bdf353aa24adc2450646945bcde64de8a62d3729c4c20cbaff445bbcb",
  "checks": {
    "pier0_three_source_bearings": true,
    "pier0_all_sections_received": true,
    "pier0_core_outside_vault_reservation": true,
    "pier0_connected_section": true,
    "pier1_three_source_bearings": true,
    "pier1_all_sections_received": true,
    "pier1_core_outside_vault_reservation": true,
    "pier1_connected_section": true,
    "pier2_three_source_bearings": true,
    "pier2_all_sections_received": true,
    "pier2_core_outside_vault_reservation": true,
    "pier2_connected_section": true,
    "pier3_three_source_bearings": true,
    "pier3_all_sections_received": true,
    "pier3_core_outside_vault_reservation": true,
    "pier3_connected_section": true,
    "positive_clear_longitudinal_gap": true,
    "positive_clear_transverse_gap": true,
    "pairwise_piers_disjoint": true,
    "retained_vault_and_all_masonry_geometry_unchanged": true,
    "four_new_piers_closed_consistently_wound": true,
    "four_new_piers_positive_volume": true,
    "vertical_extrusion_without_bends": true,
    "source_masonry_file_hash_unchanged": true,
    "pier0_BAY1_RIB_0_cap_gap_within_0_005": true,
    "pier0_BAY1_FORMERET_0_cap_gap_within_0_005": true,
    "pier0_ENTRANCE_ORDER_4_cap_gap_within_0_005": true,
    "pier1_BAY1_RIB_1_cap_gap_within_0_005": true,
    "pier1_BAY1_FORMERET_0_cap_gap_within_0_005": true,
    "pier1_CHAPEL_TRANSVERSE_31000_cap_gap_within_0_005": true,
    "pier2_BAY1_RIB_2_cap_gap_within_0_005": true,
    "pier2_BAY1_FORMERET_2_cap_gap_within_0_005": true,
    "pier2_CHAPEL_TRANSVERSE_31000_cap_gap_within_0_005": true,
    "pier3_BAY1_RIB_3_cap_gap_within_0_005": true,
    "pier3_BAY1_FORMERET_2_cap_gap_within_0_005": true,
    "pier3_ENTRANCE_ORDER_4_cap_gap_within_0_005": true,
    "glb_object_names_and_count": true,
    "glb_world_bounds_within_0_01": true,
    "glb_oriented_triangle_signatures_at_0_001": true
  },
  "passed": 39,
  "total": 39,
  "source_sections": 12,
  "piers": 4,
  "added_formeret_responds": 4,
  "replaced_source_shafts": 8,
  "retained_mesh_objects": 252,
  "clear_rectangle_native": [
    2201.5546875,
    2200
  ],
  "contact_metrics": {
    "0": [
      {
        "source": "BAY1_RIB_0",
        "bearing": 46.169139722084374,
        "max_boundary_gap": 0.0006580694986670695,
        "unreceived_area": 0.001500682106050144
      },
      {
        "source": "BAY1_FORMERET_0",
        "bearing": 0,
        "max_boundary_gap": 0.00017574674653251938,
        "unreceived_area": 0.0003471572383950683
      },
      {
        "source": "ENTRANCE_ORDER_4",
        "bearing": 90,
        "max_boundary_gap": 0.00023475594932835197,
        "unreceived_area": 0.0018163293460247143
      }
    ],
    "1": [
      {
        "source": "BAY1_RIB_1",
        "bearing": 133.83086027791563,
        "max_boundary_gap": 0.0004142488289186621,
        "unreceived_area": 0.001500682106050144
      },
      {
        "source": "BAY1_FORMERET_0",
        "bearing": 180,
        "max_boundary_gap": 0.00017574674653251938,
        "unreceived_area": 0.0003471572383950683
      },
      {
        "source": "CHAPEL_TRANSVERSE_31000",
        "bearing": 90,
        "max_boundary_gap": 0.0002543252432044007,
        "unreceived_area": 0.0018163293460240482
      }
    ],
    "2": [
      {
        "source": "BAY1_RIB_2",
        "bearing": -133.83086027791563,
        "max_boundary_gap": 0.0006580694986670695,
        "unreceived_area": 0.001500682106050144
      },
      {
        "source": "BAY1_FORMERET_2",
        "bearing": 180,
        "max_boundary_gap": 0.00017574674653251938,
        "unreceived_area": 0.0003471572383950683
      },
      {
        "source": "CHAPEL_TRANSVERSE_31000",
        "bearing": -90,
        "max_boundary_gap": 0.00025432524320451833,
        "unreceived_area": 0.0018163293460247143
      }
    ],
    "3": [
      {
        "source": "BAY1_RIB_3",
        "bearing": -46.169139722084374,
        "max_boundary_gap": 0.0004142488289186621,
        "unreceived_area": 0.001500682106050144
      },
      {
        "source": "BAY1_FORMERET_2",
        "bearing": 0,
        "max_boundary_gap": 0.00017574674653251938,
        "unreceived_area": 0.0003471572383950683
      },
      {
        "source": "ENTRANCE_ORDER_4",
        "bearing": -90,
        "max_boundary_gap": 0.00023475594932858727,
        "unreceived_area": 0.0018163293460240482
      }
    ]
  },
  "roundtrip_bounds_max_error": 0,
  "validation": {
    "technical": "scripts, mesh winding/closure/volume, actual GLB reimport and oriented triangle comparison",
    "geometric": "12 actual spring section containment, straight vertical extrusion, protected masonry/vault arrays unchanged, conservative clear rectangle",
    "architectural": "experimental 3-bearing chapel bay piers; outside core derived from source backlines; backing masonry retained; no common tas-de-charge added above spring",
    "historical": "not assessed; source profile designs are experimental, not authenticated historical traces",
    "structural": "not assessed; core sizes/bearing areas and capacities not certified; F5ZL-C schedule unresolved"
  }
}
```


## extract_sections.py
```python
import bpy,json,pathlib,hashlib,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent
S=pathlib.Path('/home/christopher/Documents/Cathedral/experimental/MASONRY_STONES_R01/MASONRY_STONES_R01.blend')
bpy.ops.wm.open_mainfile(filepath=str(S))
nodes=[(28600.,-1250.),(31000.,-1250.),(31000.,1250.),(28600.,1250.)]
groups={str(i):dict(node=list(p),sections=[]) for i,p in enumerate(nodes)}
names=['BAY1_RIB_'+str(i) for i in range(4)]+['BAY1_FORMERET_0','BAY1_FORMERET_2','ENTRANCE_ORDER_4','CHAPEL_TRANSVERSE_31000']
for name in names:
 o=bpy.data.objects[name];pts=[tuple(o.matrix_world@v.co) for v in o.data.vertices]
 matches={i:[] for i in range(4)}
 for index,p in enumerate(pts):
  if abs(p[2]-1800.)<.002:
   ni=min(range(4),key=lambda i:math.dist(p[:2],nodes[i]))
   if math.dist(p[:2],nodes[ni])<300:matches[ni].append((index,list(p[:2])))
 for ni,arr in matches.items():
  if len(arr)<3:continue
  center=nodes[ni]
  if 'RIB' in name:target=(29800.,0.)
  elif 'FORMERET' in name:target=(31000. if center[0]==28600 else 28600.,center[1])
  else:target=(center[0],-center[1])
  h=Vector((target[0]-center[0],target[1]-center[1]));h.normalize()
  groups[str(ni)]['sections'].append(dict(name=name,polygon=[p for j,p in arr],bearing_degrees=math.degrees(math.atan2(h.y,h.x)),direction=list(h)))
data=dict(source=str(S),source_sha256=hashlib.sha256(S.read_bytes()).hexdigest(),spring=1800.,nodes=groups)
(R/'SPRING_SECTIONS.json').write_text(json.dumps(data,indent=2))
print(json.dumps({k:dict(node=v['node'],profiles=[dict(name=s['name'],vertices=len(s['polygon']),bearing=s['bearing_degrees']) for s in v['sections']]) for k,v in groups.items()}))

```

## prepare_piers.py
```python
import json,pathlib,math,collections
from shapely.geometry import Polygon,MultiPoint,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
from shapely.geometry.polygon import orient
R=pathlib.Path(__file__).resolve().parent
D=json.loads((R/'SPRING_SECTIONS.json').read_text())
out=[];checks={};measurements={};unions={}
for nodeid,node in D['nodes'].items():
 x,y=node['node'];sign=1 if y>0 else -1;polys=[];backs=[]
 for sec in node['sections']:
  p=Polygon(sec['polygon']);assert p.is_valid and p.area>0,sec['name'];polys.append(p)
  h=sec['direction'];depth=[(a-x)*h[0]+(b-y)*h[1] for a,b in sec['polygon']];minimum=min(depth)
  backs.extend([pt for pt,d in zip(sec['polygon'],depth) if d<=minimum+.003])
 xmin,xmax=min(p[0] for p in backs),max(p[0] for p in backs)
 half=max(x-xmin,xmax-x)
 # Core comes after source-section overlay; it stays in the existing outside wall reservation.
 core=MultiPoint(backs+[[x-half*.75,y+sign*320],[x+half*.75,y+sign*320]]).convex_hull
 core=core.intersection(box(x-220,min(y,y+sign*320),x+220,max(y,y+sign*320)))
 profiles=unary_union(polys);whole=unary_union([profiles,core])
 assert whole.geom_type=='Polygon' and whole.is_valid
 checks['pier'+nodeid+'_three_source_bearings']=len(polys)==3
 checks['pier'+nodeid+'_all_sections_received']=all(p.difference(whole).area<.001 for p in polys)
 checks['pier'+nodeid+'_core_outside_vault_reservation']=core.intersection(box(28600,-1250,31000,1250)).area<.001
 checks['pier'+nodeid+'_connected_section']=whole.geom_type=='Polygon'
 p=orient(whole,sign=1);v=[];index={};faces=[]
 def vertex(a,b,level):
  key=(float(a),float(b),0. if level==0 else 1800.)
  if key not in index:index[key]=len(v);v.append(key)
  return index[key]
 tris=list(constrained_delaunay_triangles(p).geoms)
 assert abs(sum(t.area for t in tris)-p.area)<.001
 for t in tris:
  co=list(orient(t,sign=1).exterior.coords)[:-1]
  faces.extend([list(reversed([vertex(a,b,0) for a,b in co])),[vertex(a,b,1) for a,b in co]])
 for loop in [p.exterior,*p.interiors]:
  co=list(loop.coords)
  for a,b in zip(co,co[1:]):faces.append([vertex(*a,0),vertex(*b,0),vertex(*b,1),vertex(*a,1)])
 unions[nodeid]=p
 out.append(dict(name='COMPOUND_PIER_'+nodeid,vertices=v,faces=faces,section=list(p.exterior.coords),core=list(core.exterior.coords),node=[x,y],bearings=[s['bearing_degrees'] for s in node['sections']]))
 measurements[nodeid]=dict(node=[x,y],bearings=[s['bearing_degrees'] for s in node['sections']],source_profile_union_area=profiles.area,core_area=core.area,compound_area=p.area,section_bounds=list(p.bounds),core_rule='convex hull of actual section backing points and two outward anchors; clipped to prior 320-deep reservation')
# Conservative clear rectangle between the four complete section bounding boxes.
clearx=min(unions['1'].bounds[0],unions['2'].bounds[0])-max(unions['0'].bounds[2],unions['3'].bounds[2])
cleary=min(unions['2'].bounds[1],unions['3'].bounds[1])-max(unions['0'].bounds[3],unions['1'].bounds[3])
checks['positive_clear_longitudinal_gap']=clearx>0
checks['positive_clear_transverse_gap']=cleary>0
checks['pairwise_piers_disjoint']=all(unions[str(a)].intersection(unions[str(b)]).area<.001 for a in range(4) for b in range(a+1,4))
report=dict(checks=checks,piers=measurements,conservative_clear_rectangle=[clearx,cleary],units='native project units, numerical 1:1; physical SI unresolved',basis='three actual R04-source profiles per bay corner; NOT Pass6J representative eight-bearing pier')
(R/'PIER_MESHES.json').write_text(json.dumps(out,separators=(',',':')))
(R/'SECTION_QA.json').write_text(json.dumps(report,indent=2))
# Measurable local SVG: black source profiles, dashed gray axes, dashed red experimental core.
p=out[0];x,y=p['node']
def path(poly):return 'M '+' L '.join(str(a-x)+','+str(-(b-y)) for a,b in poly)+' Z'
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-180 -200 400 580" width="600" height="870">']
svg.append('<g fill="none" stroke="#999" stroke-width="0.8" stroke-dasharray="4 4"><path d="M -180 0 L 220 0 M 0 -200 L 0 380"/></g>')
svg.append('<path d="'+path(p['core'])+'" fill="#e6d6bd" fill-opacity=".5" stroke="#b33" stroke-width="1" stroke-dasharray="4 3"/>')
for s in D['nodes']['0']['sections']:svg.append('<path d="'+path(s['polygon'])+'" fill="none" stroke="black" stroke-width="1.2"/>')
svg.append('</svg>');(R/'PIER_0_SECTION_NATIVE.svg').write_text(''.join(svg))
assert all(checks.values()),report
print('SECTIONS_READY',clearx,cleary)

```

## verify_contacts.py
```python
import json,pathlib
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
R=pathlib.Path(__file__).resolve().parent
D=json.loads((R/'SPRING_SECTIONS.json').read_text());tops=json.loads((R/'BLENDER_TOP_CAPS.json').read_text());checks={};metrics={}
for i,node in D['nodes'].items():
 cap=unary_union([Polygon(t) for t in tops['COMPOUND_PIER_'+i]]);errors=[]
 for s in node['sections']:
  p=Polygon(s['polygon'])
  # Vertex + independently sampled boundary containment against exported-to-Blender top triangles.
  pts=[p.exterior.interpolate(p.exterior.length*j/300) for j in range(301)]
  maxgap=max(cap.distance(q) for q in pts)
  errors.append(dict(source=s['name'],bearing=s['bearing_degrees'],max_boundary_gap=maxgap,unreceived_area=p.difference(cap).area))
  checks['pier'+i+'_'+s['name']+'_cap_gap_within_0_005']=maxgap<=.005
 metrics[i]=errors
(R/'CONTACT_QA.json').write_text(json.dumps(dict(checks=checks,metrics=metrics),indent=2))
assert all(checks.values()),metrics

```

## build_and_verify.py
```python
import bpy,json,pathlib,hashlib,math,collections,subprocess
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent
D=json.loads((R/'SPRING_SECTIONS.json').read_text());SRC=pathlib.Path(D['source'])
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==D['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(SRC))
def coords(o):return [tuple(o.matrix_world@v.co) for v in o.data.vertices]
def sig(o):return hashlib.sha256(repr((coords(o),[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
removed=[o for o in bpy.context.scene.objects if o.type=='MESH' and 'SHAFT' in o.name]
assert len(removed)==8
retained=[o for o in bpy.context.scene.objects if o.type=='MESH' and o not in removed]
before={o.name:sig(o) for o in retained}
for o in removed:bpy.data.objects.remove(o,do_unlink=True)
material=bpy.data.materials.new('NEW_COMPOUND_PIERS');material.diffuse_color=(.70,.60,.43,1);material.use_nodes=True
material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.70,.60,.43,1)
material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
piers=[]
for d in json.loads((R/'PIER_MESHES.json').read_text()):
 me=bpy.data.meshes.new(d['name']);me.from_pydata(d['vertices'],[],d['faces']);me.update()
 o=bpy.data.objects.new(d['name'],me);bpy.context.scene.collection.objects.link(o);o.data.materials.append(material);o['source_bearings_degrees']=d['bearings'];piers.append(o)
def topology(o):
 edges=collections.Counter();directions=collections.defaultdict(list)
 for p in o.data.polygons:
  v=list(p.vertices)
  for a,b in zip(v,v[1:]+v[:1]):
   key=tuple(sorted((a,b)));edges[key]+=1;directions[key].append(a<b)
 return all(n==2 for n in edges.values()) and all(x[0]!=x[1] for x in directions.values())
def volume(o):
 o.data.calc_loop_triangles();v=[Vector(p) for p in coords(o)];center=v[0]
 return sum((v[t.vertices[0]]-center).dot((v[t.vertices[1]]-center).cross(v[t.vertices[2]]-center))/6 for t in o.data.loop_triangles)
section=json.loads((R/'SECTION_QA.json').read_text());checks=section['checks']
checks['retained_vault_and_all_masonry_geometry_unchanged']=all(sig(o)==before[o.name] for o in retained)
checks['four_new_piers_closed_consistently_wound']=all(topology(o) for o in piers)
checks['four_new_piers_positive_volume']=all(volume(o)>0 for o in piers)
checks['vertical_extrusion_without_bends']=all(all(any(abs(a[0]-b[0])<1e-8 and abs(a[1]-b[1])<1e-8 and abs(a[2]-b[2])>1799 for b in coords(o)) for a in coords(o)) for o in piers)
checks['source_masonry_file_hash_unchanged']=hashlib.sha256(SRC.read_bytes()).hexdigest()==D['source_sha256']
# Re-evaluate containment against the actual Blender float32 top cap, not just the host polygons.
tops={}
for o in piers:
 o.data.calc_loop_triangles();v=coords(o)
 tops[o.name]=[[v[i][:2] for i in t.vertices] for t in o.data.loop_triangles if all(abs(v[i][2]-1800)<.001 for i in t.vertices)]
(R/'BLENDER_TOP_CAPS.json').write_text(json.dumps(tops))
subprocess.run(['/usr/bin/python3',str(R/'verify_contacts.py')],check=True)
contact=json.loads((R/'CONTACT_QA.json').read_text());checks.update(contact['checks'])
assert all(checks.values()),checks
bpy.ops.wm.save_as_mainfile(filepath=str(R/'COMPOUND_PIERS_R01.blend'))
def snapshot(obs):
 result={}
 for o in obs:
  v=coords(o);o.data.calc_loop_triangles();tris=[]
  for t in o.data.loop_triangles:
   pts=[tuple(round(v[i][k],3) for k in range(3)) for i in t.vertices]
   tris.append(min(tuple(pts[j:]+pts[:j]) for j in range(3)))
  result[o.name]=dict(bounds=[[min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]],triangles=sorted(tris))
 return result
snap=snapshot(retained+piers)
bpy.ops.export_scene.gltf(filepath=str(R/'COMPOUND_PIERS_R01.glb'),export_format='GLB',export_cameras=False,export_lights=False)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(R/'COMPOUND_PIERS_R01.glb'))
now=snapshot([o for o in bpy.context.scene.objects if o.type=='MESH'])
checks['glb_object_names_and_count']=set(snap)==set(now)
error=max(abs(snap[n]['bounds'][j][k]-now[n]['bounds'][j][k]) for n in snap for j in range(2) for k in range(3))
checks['glb_world_bounds_within_0_01']=error<.01
checks['glb_oriented_triangle_signatures_at_0_001']=all(snap[n]['triangles']==now[n]['triangles'] for n in snap)
qa=dict(revision='COMPOUND_PIERS_R01_EXPERIMENTAL',source=str(SRC),source_sha256=D['source_sha256'],checks=checks,passed=sum(checks.values()),total=len(checks),source_sections=12,piers=4,added_formeret_responds=4,replaced_source_shafts=8,retained_mesh_objects=len(retained),clear_rectangle_native=section['conservative_clear_rectangle'],contact_metrics=contact['metrics'],roundtrip_bounds_max_error=error,validation=dict(technical='scripts, mesh winding/closure/volume, actual GLB reimport and oriented triangle comparison',geometric='12 actual spring section containment, straight vertical extrusion, protected masonry/vault arrays unchanged, conservative clear rectangle',architectural='experimental 3-bearing chapel bay piers; outside core derived from source backlines; backing masonry retained; no common tas-de-charge added above spring',historical='not assessed; source profile designs are experimental, not authenticated historical traces',structural='not assessed; core sizes/bearing areas and capacities not certified; F5ZL-C schedule unresolved'))
(R/'QA.json').write_text(json.dumps(qa,indent=2));assert all(checks.values()),qa
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.world.color=(.65,.65,.65);scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(25200,-6500,4900));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=6100;cam.data.clip_end=100000;scene.camera=cam;aim(cam,(29800,0,2050))
for loc,power,size in [((28000,-4000,8500),1800000000,5000),((33000,3500,6500),1300000000,4000)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(29800,0,1800))
scene.render.filepath=str(R/'ASSEMBLY.png');bpy.ops.render.render(write_still=True)
for o in scene.objects:
 if o.type=='MESH':o.hide_render=o.name!='COMPOUND_PIER_0'
cam.location=(29300,50,2900);cam.data.ortho_scale=2300;aim(cam,(28600,-1250,900))
scene.render.filepath=str(R/'PIER_DETAIL.png');bpy.ops.render.render(write_still=True)
print('RESULT',json.dumps(qa))

```

## compose_preview.py
```python
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
p=Path('/home/christopher/Documents/Cathedral/experimental/COMPOUND_PIERS_R01')
q=json.loads((p/'QA.json').read_text());D=json.loads((p/'SPRING_SECTIONS.json').read_text());m=json.loads((p/'PIER_MESHES.json').read_text())[0];x,y=m['node']
fig,ax=plt.subplots(figsize=(6.4,3.2),dpi=150)
fig.patch.set_facecolor('#eeeae2');ax.set_facecolor('#eeeae2')
for sec in D['nodes']['0']['sections']:
 a,b=zip(*(sec['polygon']+[sec['polygon'][0]]));ax.plot([v-x for v in a],[v-y for v in b],color='black',linewidth=1.0)
a,b=zip(*m['core']);ax.fill([v-x for v in a],[v-y for v in b],color='#d8c7ac',alpha=.45)
ax.plot([v-x for v in a],[v-y for v in b],color='#b33',linewidth=1,linestyle='--',label='Experimental core')
ax.axhline(0,color='#999',linewidth=.6,linestyle='--');ax.axvline(0,color='#999',linewidth=.6,linestyle='--')
ax.set_aspect('equal');ax.set_xlim(-160,225);ax.set_ylim(-350,175);ax.tick_params(labelsize=7)
ax.set_xlabel('Local X / native units',fontsize=8);ax.set_ylabel('Local Y',fontsize=8)
ax.set_title('SPRING SECTION / black: source profiles; red: trial core',fontsize=9)
fig.tight_layout();fig.savefig(p/'SECTION.png',facecolor=fig.get_facecolor());plt.close(fig)
im=Image.new('RGB',(1600,1100),'#eeeae2');d=ImageDraw.Draw(im);f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';font=ImageFont.truetype(f,25);small=ImageFont.truetype(f,17)
d.text((26,16),'COMPOUND PIER GENERATOR / R01 EXPERIMENTAL',fill='#28251f',font=font)
d.text((26,53),'4 piers | 3 actual bearings per corner | ribs, webs and masonry retained | native scale 1:1',fill='#49443b',font=small)
a=Image.open(p/'ASSEMBLY.png').convert('RGB');a.thumbnail((930,930));im.paste(a,(10,95))
a=Image.open(p/'PIER_DETAIL.png').convert('RGB');a.thumbnail((630,600));im.paste(a,(975,85))
a=Image.open(p/'SECTION.png').convert('RGB');a.thumbnail((640,320));im.paste(a,(950,725))
d.text((26,1040),'COMPLETE BAY - existing masonry backing remains unchanged',fill='#28251f',font=small)
d.text((968,698),'ISOLATED PIER - unified core and three responds',fill='#28251f',font=small)
d.text((26,1070),str(q['passed'])+'/'+str(q['total'])+' technical/geometric checks | architectural review pending | historical and structural validation not performed',fill='#49443b',font=small)
im.save(p/'COMPOUND_PIERS_R01_RESULT.png')
print(json.dumps(dict(passed=q['passed'],total=q['total'],retained=q['retained_mesh_objects'],clear_rectangle=q['clear_rectangle_native'],max_cap_gap=max(z['max_boundary_gap'] for v in q['contact_metrics'].values() for z in v))))

```
