# Shared compound piers R02 — EXPERIMENTAL

## Scope and authority
Two existing adjoining axial chapel bays, native numerical 1:1, Blender X east/Y north/Z up; physical SI conversion unresolved. Start from saved COMPOUND_PIERS_R01.blend and append selected existing bay2 geometry from Axial_Chapel_R04_EXPERIMENTAL.blend. Exact paths and SHA256 below. GitHub Master Reference recovered at task start, governance-r01 blob 1d7e358ff7562fcc64088854baa2abd3d31a729e. Both models are experimental fixtures, not approved cathedral baselines or Pass6J eight-bearing R1/78.

## Delta
Replace the two R01 three-bearing piers at X31000 with one five-bearing compound pier per shared node: south and north Y±1250. Each receives the single shared transverse arch, two diagonals and two formerets. Do not duplicate the shared arch. Add two three-bearing piers at X33400 to receive the source bay2 end geometry, replacing six imported isolated shafts. Retain the two R01 west-end piers unchanged. Result: six piers total, two shared.

All 284 retained mesh objects match their saved source geometry, both before and after building: ribs, webs, walls, glass, source mullions, masonry stones/mortar, backing cores, old west piers and original display floor. Original saved source file hashes unchanged. Bay2 vaults are appended from saved meshes, never regenerated. New separate display-floor tile extends the studio fixture only; it is not a new architectural floor. Existing wall depths are deliberately retained: bay1 320, bay2 source170. Wall-depth transition and source bay2 mullion/glass differences remain architectural review items. No approved geometry, historic original, authoritative generator or Pass6J record changed; no promotion.

Core derivation follows R01: overlay actual spring sections, recover backing points, derive a hull with outward anchors, then clip it to actual recovered masonry footprint reservations and outside the vault plan. Five bearings are actual source directions, not a regularized fan. Profiles are straight vertical extrusions from Z0 to Z1800. Existing backing cores remain and overlap the new cores intentionally; this is not a boolean-unioned structural model. No common tas-de-charge above spring, new base/plinth or stone-bond redesign is included.

## Measured validation
50/50 listed technical/geometric checks passed. Sixteen extracted source spring sections: five at each shared pier, three at each new east pier. Source section boundaries sampled at 301 points against actual Blender float32 top-cap triangle unions; maximum containment gap 0.0013891936 native units (tolerance0.005). This tests fit, not structural bearing capacity. Both web shells have identical sampled shared-edge vertices: maximum mismatch0. Conservative clear rectangles remain 2201.5546875 by2200 in each bay. Shared transverse arch stored once. New piers are connected, disjoint from one another, closed, consistently wound, positive-volume, and vertically straight.

Actual GLB round trip checks every object name/count, world bounds (error0, tolerance0.01) and oriented triangle signatures at0.001 quantization. Rendered composite inspected: complete assembly, isolated shared pier and measurable source-section overlay. Black contours confirm recovered source mesh geometry only; dashed redcore remains experimental, gray dashedaxes construction.

A failed source-preservation check during development identified signatures being captured before imported object transforms were updated. The extractor now updates the view layer before capturing world-coordinate signatures. All source checks passed on rerun; their tolerances were not relaxed.

Architectural: experimental chapel fixture; wall-depth transition, full neighboring clearance, above-spring masonry, backing overlap, bearing areas and profiles need review. Historical: not assessed; source profiles are experimental designs, not authenticated traces. Structural: not assessed; F5ZL-C support schedule unresolved. Collision/fit tests do not establish capacities.

## Reproduction and retained files
Save the five scripts below together in a new experimental directory. Requires Blender5.0.1, system Python3 with Shapely2.1.2, Pillow/matplotlib for preview, and the exact source models in QA. Run:

1. `blender -b -t 4 --python extract_inputs.py`
2. `python3 prepare_piers.py`
3. `blender -b -t 4 --python build_and_verify.py`
4. `python3 compose_preview.py`

build_and_verify.py invokes verify_contacts.py automatically. The extraction scene also saves ASSEMBLED_INPUT.blend. Final outputs: SHARED_PIERS_R02.blend and .glb, INPUTS.json with source signatures, PIER_MESHES.json, SECTION_QA.json, CONTACT_QA.json, QA.json, SHARED_S_SECTION_NATIVE.svg (one SVG user unit per native unit), and rendered PNGs. All retained on MR COMPUTER at `/home/christopher/Documents/Cathedral/experimental/SHARED_PIERS_R02`. Only the final PNG is uploaded for the user. Binary sources/outputs are not embedded in this text checkpoint.

## QA
```json
{
  "revision": "SHARED_PIERS_R02_EXPERIMENTAL",
  "parent": "/home/christopher/Documents/Cathedral/experimental/COMPOUND_PIERS_R01/COMPOUND_PIERS_R01.blend",
  "parent_sha256": "dd53c31f50338ea12eb055099d89bc22f050b56fd1ca3795c841b663d233ca62",
  "bay2_source": "/home/christopher/Downloads/F5ZP_Axial_Chapel_R04_EXPERIMENTAL/Axial_Chapel_R04_EXPERIMENTAL.blend",
  "bay2_source_sha256": "e87d95019f22fc88083dca564b46c3b0f0e378bc372269c8002dfe5a3eb44906",
  "checks": {
    "all_retained_meshes_match_their_saved_sources": true,
    "two_web_shared_shell_edges_match_within_0_005": true,
    "single_retained_shared_transverse_arch": true,
    "new_piers_closed_consistently_wound": true,
    "new_piers_positive_volume": true,
    "vertical_extrusion_no_bends": true,
    "six_total_piers_two_shared_nodes_once_each": true,
    "retained_geometry_unchanged_after_build": true,
    "parent_and_R04_files_unchanged": true,
    "S_BAY1_RIB_1_contact_gap_within_0_005": true,
    "S_BAY2_RIB_0_contact_gap_within_0_005": true,
    "S_BAY1_FORMERET_0_contact_gap_within_0_005": true,
    "S_BAY2_FORMERET_0_contact_gap_within_0_005": true,
    "S_CHAPEL_TRANSVERSE_31000_contact_gap_within_0_005": true,
    "N_BAY1_RIB_2_contact_gap_within_0_005": true,
    "N_BAY2_RIB_3_contact_gap_within_0_005": true,
    "N_BAY1_FORMERET_2_contact_gap_within_0_005": true,
    "N_BAY2_FORMERET_2_contact_gap_within_0_005": true,
    "N_CHAPEL_TRANSVERSE_31000_contact_gap_within_0_005": true,
    "ES_BAY2_RIB_1_contact_gap_within_0_005": true,
    "ES_BAY2_FORMERET_0_contact_gap_within_0_005": true,
    "ES_CHAPEL_TRANSVERSE_33400_contact_gap_within_0_005": true,
    "EN_BAY2_RIB_2_contact_gap_within_0_005": true,
    "EN_BAY2_FORMERET_2_contact_gap_within_0_005": true,
    "EN_CHAPEL_TRANSVERSE_33400_contact_gap_within_0_005": true,
    "S_expected_bearing_count": true,
    "S_profile_containment": true,
    "S_connected_pier_section": true,
    "S_core_within_recovered_backing_reservation": true,
    "S_core_outside_protected_vault_plan": true,
    "N_expected_bearing_count": true,
    "N_profile_containment": true,
    "N_connected_pier_section": true,
    "N_core_within_recovered_backing_reservation": true,
    "N_core_outside_protected_vault_plan": true,
    "ES_expected_bearing_count": true,
    "ES_profile_containment": true,
    "ES_connected_pier_section": true,
    "ES_core_within_recovered_backing_reservation": true,
    "ES_core_outside_protected_vault_plan": true,
    "EN_expected_bearing_count": true,
    "EN_profile_containment": true,
    "EN_connected_pier_section": true,
    "EN_core_within_recovered_backing_reservation": true,
    "EN_core_outside_protected_vault_plan": true,
    "positive_conservative_clear_rectangles": true,
    "new_piers_pairwise_disjoint": true,
    "GLB_object_names_and_count": true,
    "GLB_bounds_within_0_01": true,
    "GLB_oriented_triangle_signatures_at_0_001": true
  },
  "passed": 50,
  "total": 50,
  "retained_mesh_count": 284,
  "total_piers": 6,
  "shared_piers": 2,
  "bearings_per_shared_pier": 5,
  "source_contact_sections": 16,
  "clear_rectangles": {
    "bay1": [
      2201.5546875,
      2200
    ],
    "bay2": [
      2201.5546875,
      2200
    ]
  },
  "web_shared_edge_error": 0,
  "glb_bounds_error": 0,
  "contact_metrics": {
    "S": [
      {
        "source": "BAY1_RIB_1",
        "bearing": 133.83086027791563,
        "max_boundary_gap": 0.0004142488289186621,
        "unreceived_area": 0.001500682106050144
      },
      {
        "source": "BAY2_RIB_0",
        "bearing": 46.169139722084374,
        "max_boundary_gap": 0.0006580694986670695,
        "unreceived_area": 0.001500682106050144
      },
      {
        "source": "BAY1_FORMERET_0",
        "bearing": 180,
        "max_boundary_gap": 0.00017574674653251938,
        "unreceived_area": 0.0003471572383950683
      },
      {
        "source": "BAY2_FORMERET_0",
        "bearing": 0,
        "max_boundary_gap": 0.00017574674653251938,
        "unreceived_area": 0.0003471572383950683
      },
      {
        "source": "CHAPEL_TRANSVERSE_31000",
        "bearing": 90,
        "max_boundary_gap": 0.0002543252432044007,
        "unreceived_area": 0.0036326586920487625
      }
    ],
    "N": [
      {
        "source": "BAY1_RIB_2",
        "bearing": -133.83086027791563,
        "max_boundary_gap": 0.0006580694986670695,
        "unreceived_area": 0.001500682106050144
      },
      {
        "source": "BAY2_RIB_3",
        "bearing": -46.169139722084374,
        "max_boundary_gap": 0.0004142488289186621,
        "unreceived_area": 0.001500682106050144
      },
      {
        "source": "BAY1_FORMERET_2",
        "bearing": 180,
        "max_boundary_gap": 0.00017574674653251938,
        "unreceived_area": 0.0003471572383950683
      },
      {
        "source": "BAY2_FORMERET_2",
        "bearing": 0,
        "max_boundary_gap": 0.00017574674653251938,
        "unreceived_area": 0.0003471572383950683
      },
      {
        "source": "CHAPEL_TRANSVERSE_31000",
        "bearing": -90,
        "max_boundary_gap": 0.00025432524320451833,
        "unreceived_area": 0.0036326586920487625
      }
    ],
    "ES": [
      {
        "source": "BAY2_RIB_1",
        "bearing": 133.83086027791563,
        "max_boundary_gap": 0.001389193573584077,
        "unreceived_area": 0.0059256927894333344
      },
      {
        "source": "BAY2_FORMERET_0",
        "bearing": 180,
        "max_boundary_gap": 2.6806725799672204e-12,
        "unreceived_area": 0.0007295003911815812
      },
      {
        "source": "CHAPEL_TRANSVERSE_33400",
        "bearing": 90,
        "max_boundary_gap": 0.0011044130465695092,
        "unreceived_area": 0.00803165754175339
      }
    ],
    "EN": [
      {
        "source": "BAY2_RIB_2",
        "bearing": -133.83086027791563,
        "max_boundary_gap": 0.0009799858406409968,
        "unreceived_area": 0.0059256927894333344
      },
      {
        "source": "BAY2_FORMERET_2",
        "bearing": 180,
        "max_boundary_gap": 2.6806725799672204e-12,
        "unreceived_area": 0.0007295003911815812
      },
      {
        "source": "CHAPEL_TRANSVERSE_33400",
        "bearing": -90,
        "max_boundary_gap": 0.001104413046569373,
        "unreceived_area": 0.008031657541754278
      }
    ]
  },
  "validation": {
    "technical": "scripts, mesh topology/volume, actual GLB reimport and oriented triangle signatures",
    "geometric": "actual spring section containment, shared shell-edge fit, straight extrusion, original masonry/vault mesh preservation, conservative clear rectangles",
    "architectural": "experimental two-bay chapel fixture; bay1 wall 320, source bay2 wall170 retained; original backing cores intentionally overlap new core; no transition redesign or tas-de-charge above spring",
    "historical": "not assessed; experimental profiles/bond retained",
    "structural": "not assessed; source support areas/capacity unverified; missing F5ZL-C schedule unresolved"
  }
}
```

## extract_inputs.py
```python
import bpy,pathlib,json,hashlib,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent
P=pathlib.Path('/home/christopher/Documents/Cathedral/experimental/COMPOUND_PIERS_R01/COMPOUND_PIERS_R01.blend')
S=pathlib.Path('/home/christopher/Downloads/F5ZP_Axial_Chapel_R04_EXPERIMENTAL/Axial_Chapel_R04_EXPERIMENTAL.blend')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def coords(o):return [tuple(o.matrix_world@v.co) for v in o.data.vertices]
def sig(o):return hashlib.sha256(repr((coords(o),[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));parent={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
with bpy.data.libraries.load(str(S),link=False) as (src,dst):
 names=[n for n in src.objects if n.startswith(('BAY2_','CHAPEL_TRANSVERSE_33400','SIDE_-1_BAY2','SIDE_1_BAY2')) or n.startswith('CHAPEL_CORE_') and '33400' in n]
 dst.objects=names
for o in dst.objects:
 if o:bpy.context.scene.collection.objects.link(o)
bpy.context.view_layer.update()
imported={o.name:sig(o) for o in dst.objects if o}
# Walls/core backing remain source geometry; linked profiles are independently sectioned.
nodes={'S':(31000.,-1250.),'N':(31000.,1250.),'ES':(33400.,-1250.),'EN':(33400.,1250.)}
sections={k:dict(node=list(v),sections=[]) for k,v in nodes.items()}
names=['BAY1_RIB_1','BAY1_RIB_2']+['BAY2_RIB_'+str(i) for i in range(4)]+['BAY1_FORMERET_0','BAY1_FORMERET_2','BAY2_FORMERET_0','BAY2_FORMERET_2','CHAPEL_TRANSVERSE_31000','CHAPEL_TRANSVERSE_33400']
for name in names:
 o=bpy.data.objects[name];vs=coords(o);near={k:[] for k in nodes}
 for index,p in enumerate(vs):
  if abs(p[2]-1800)<.002:
   k=min(nodes,key=lambda k:math.dist(p[:2],nodes[k]))
   if math.dist(p[:2],nodes[k])<300:near[k].append(list(p[:2]))
 for k,arr in near.items():
  if len(arr)<3:continue
  x,y=nodes[k]
  if 'RIB' in name:target=(29800. if 'BAY1' in name else 32200.,0.)
  elif 'FORMERET' in name:target=(28600. if 'BAY1' in name else (33400. if x==31000 else 31000.),y)
  else:target=(x,-y)
  h=Vector((target[0]-x,target[1]-y));h.normalize()
  sections[k]['sections'].append(dict(name=name,polygon=arr,direction=list(h),bearing_degrees=math.degrees(math.atan2(h.y,h.x))))
# Derive floor-plan backing reservations from actual source masonry projections.
reservations=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name not in ['COMPOUND_PIER_0','COMPOUND_PIER_1','COMPOUND_PIER_2','COMPOUND_PIER_3'] and o.name.startswith(('WALL_','PLINTH_','MORTAR_','SIDE_','CHAPEL_CORE_')):
  reservations.append([list(v[:2]) for v in coords(o)])
data=dict(parent=str(P),parent_sha256=digest(P),bay2_source=str(S),bay2_source_sha256=digest(S),parent_mesh_signatures=parent,imported_mesh_signatures=imported,nodes=sections,reservation_pointclouds=reservations)
(R/'INPUTS.json').write_text(json.dumps(data))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ASSEMBLED_INPUT.blend'))
print(json.dumps(dict(imported=list(imported),sections={k:[dict(name=s['name'],bearing=s['bearing_degrees'],count=len(s['polygon'])) for s in v['sections']] for k,v in sections.items()})))

```

## prepare_piers.py
```python
import json,pathlib,collections
from shapely.geometry import Polygon,MultiPoint,box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
R=pathlib.Path(__file__).resolve().parent;D=json.loads((R/'INPUTS.json').read_text())
reserve=unary_union([MultiPoint(p).convex_hull for p in D['reservation_pointclouds']])
out=[];checks={};metrics={};sections={}
for key,node in D['nodes'].items():
 x,y=node['node'];sign=1 if y>0 else -1;polys=[];back=[]
 for s in node['sections']:
  p=Polygon(s['polygon']);assert p.is_valid;polys.append(p);h=s['direction'];depth=[(a-x)*h[0]+(b-y)*h[1] for a,b in s['polygon']]
  back += [p for p,d in zip(s['polygon'],depth) if d<=min(depth)+.003]
 half=max(abs(a-x) for a,b in back)
 core=MultiPoint(back+[[x-half*.75,y+sign*320],[x+half*.75,y+sign*320]]).convex_hull
 core=core.intersection(reserve).intersection(box(x-220,min(y,y+sign*320),x+220,max(y,y+sign*320)))
 full=unary_union([*polys,core]);assert full.geom_type=='Polygon' and full.is_valid
 sections[key]=full
 checks[key+'_expected_bearing_count']=len(polys)==(5 if key in ('S','N') else 3)
 checks[key+'_profile_containment']=all(p.difference(full).area<.001 for p in polys)
 checks[key+'_connected_pier_section']=full.geom_type=='Polygon'
 checks[key+'_core_within_recovered_backing_reservation']=core.difference(reserve).area<.001
 checks[key+'_core_outside_protected_vault_plan']=core.intersection(box(28600,-1250,33400,1250)).area<.001
 p=orient(full,sign=1);verts=[];indices={};faces=[]
 def vertex(a,b,k):
  t=(float(a),float(b),1800. if k else 0.)
  if t not in indices:indices[t]=len(verts);verts.append(t)
  return indices[t]
 triangles=list(constrained_delaunay_triangles(p).geoms)
 assert abs(sum(t.area for t in triangles)-p.area)<.001
 for t in triangles:
  c=list(orient(t,sign=1).exterior.coords)[:-1];faces.extend([list(reversed([vertex(a,b,0) for a,b in c])),[vertex(a,b,1) for a,b in c]])
 for loop in [p.exterior,*p.interiors]:
  c=list(loop.coords)
  for a,b in zip(c,c[1:]):faces.append([vertex(*a,0),vertex(*b,0),vertex(*b,1),vertex(*a,1)])
 name=('SHARED_PIER_' if key in ('S','N') else 'END_PIER_')+key
 out.append(dict(name=name,key=key,node=[x,y],vertices=verts,faces=faces,section=list(p.exterior.coords),core=list(core.exterior.coords),bearings=[s['bearing_degrees'] for s in node['sections']]))
 metrics[key]=dict(section_area=p.area,core_area=core.area,bounds=list(p.bounds),bearings=[s['bearing_degrees'] for s in node['sections']])
old=json.loads(pathlib.Path('/home/christopher/Documents/Cathedral/experimental/COMPOUND_PIERS_R01/PIER_MESHES.json').read_text())
westS=Polygon(old[0]['section']);westN=Polygon(old[3]['section'])
def clear(a,b,c,d):
 return [min(b.bounds[0],c.bounds[0])-max(a.bounds[2],d.bounds[2]),min(c.bounds[1],d.bounds[1])-max(a.bounds[3],b.bounds[3])]
gaps=dict(bay1=clear(westS,sections['S'],sections['N'],westN),bay2=clear(sections['S'],sections['ES'],sections['EN'],sections['N']))
checks['positive_conservative_clear_rectangles']=all(v>0 for a in gaps.values() for v in a)
checks['new_piers_pairwise_disjoint']=all(sections[a].intersection(sections[b]).area<.001 for i,a in enumerate(sections) for b in list(sections)[i+1:])
(R/'PIER_MESHES.json').write_text(json.dumps(out))
(R/'SECTION_QA.json').write_text(json.dumps(dict(checks=checks,metrics=metrics,clear_rectangles=gaps),indent=2))
assert all(checks.values())
print('SECTIONS',gaps)

```

## verify_contacts.py
```python
import pathlib,json
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=pathlib.Path(__file__).resolve().parent;D=json.loads((R/'INPUTS.json').read_text());tops=json.loads((R/'BLENDER_TOP_CAPS.json').read_text())
checks={};metrics={}
for key,node in D['nodes'].items():
 cap=unary_union([Polygon(t) for t in tops[key]]);metrics[key]=[]
 for s in node['sections']:
  p=Polygon(s['polygon']);gap=max(cap.distance(p.exterior.interpolate(p.exterior.length*j/300)) for j in range(301))
  checks[key+'_'+s['name']+'_contact_gap_within_0_005']=gap<=.005
  metrics[key].append(dict(source=s['name'],bearing=s['bearing_degrees'],max_boundary_gap=gap,unreceived_area=p.difference(cap).area))
(R/'CONTACT_QA.json').write_text(json.dumps(dict(checks=checks,metrics=metrics),indent=2))
assert all(checks.values()),metrics

```

## build_and_verify.py
```python
import bpy,json,pathlib,hashlib,math,collections,subprocess
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;D=json.loads((R/'INPUTS.json').read_text())
def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
assert digest(D['parent'])==D['parent_sha256'] and digest(D['bay2_source'])==D['bay2_source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(R/'ASSEMBLED_INPUT.blend'))
def coords(o):return [tuple(o.matrix_world@v.co) for v in o.data.vertices]
def signature(o):return hashlib.sha256(repr((coords(o),[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
remove=[o for o in bpy.context.scene.objects if o.type=='MESH' and (o.name in ['COMPOUND_PIER_1','COMPOUND_PIER_2'] or 'SHAFT' in o.name)]
assert len(remove)==8
retained=[o for o in bpy.context.scene.objects if o.type=='MESH' and o not in remove]
before={o.name:signature(o) for o in retained};checks={}
expect={**D['parent_mesh_signatures'],**D['imported_mesh_signatures']}
checks['all_retained_meshes_match_their_saved_sources']=all(before[n]==expect[n] for n in before)
# Independent matched web-shell edge comparison across X31000.
edge=[]
for name in ['BAY1_WEB_1','BAY2_WEB_3']:
 edge.append([Vector(p) for p in coords(bpy.data.objects[name]) if abs(p[0]-31000)<.001])
edge_error=max(max(min((p-q).length for q in edge[1]) for p in edge[0]),max(min((p-q).length for q in edge[0]) for p in edge[1]))
checks['two_web_shared_shell_edges_match_within_0_005']=edge_error<.005
checks['single_retained_shared_transverse_arch']=sum(o.name=='CHAPEL_TRANSVERSE_31000' for o in retained)==1
for o in remove:bpy.data.objects.remove(o,do_unlink=True)
m=bpy.data.materials.new('R02_COMPOUND_PIERS');m.diffuse_color=(.66,.51,.32,1);m.use_nodes=True
m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.66,.51,.32,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
piers=[]
for p in json.loads((R/'PIER_MESHES.json').read_text()):
 me=bpy.data.meshes.new(p['name']);me.from_pydata(p['vertices'],[],p['faces']);me.update()
 o=bpy.data.objects.new(p['name'],me);bpy.context.scene.collection.objects.link(o);o.data.materials.append(m);o['node_id']=p['key'];piers.append(o)
# A separate display floor extension is not architectural floor geometry.
v=[(x,y,z) for z in (-80,-30) for x,y in [(31400,-1800),(33800,-1800),(33800,1800),(31400,1800)]]
me=bpy.data.meshes.new('DISPLAY_FLOOR_EXTENSION');me.from_pydata(v,[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update()
floor=bpy.data.objects.new('DISPLAY_FLOOR_EXTENSION',me);bpy.context.scene.collection.objects.link(floor);floor.data.materials.append(bpy.data.objects['DISPLAY_FLOOR'].data.materials[0])
def topology(o):
 edges=collections.defaultdict(list)
 for p in o.data.polygons:
  v=list(p.vertices)
  for a,b in zip(v,v[1:]+v[:1]):edges[tuple(sorted((a,b)))].append(a<b)
 return all(len(v)==2 and v[0]!=v[1] for v in edges.values())
def volume(o):
 o.data.calc_loop_triangles();v=[Vector(p) for p in coords(o)];c=v[0]
 return sum((v[t.vertices[0]]-c).dot((v[t.vertices[1]]-c).cross(v[t.vertices[2]]-c))/6 for t in o.data.loop_triangles)
checks['new_piers_closed_consistently_wound']=all(topology(o) for o in piers)
checks['new_piers_positive_volume']=all(volume(o)>0 for o in piers)
checks['vertical_extrusion_no_bends']=all(all(any(abs(a[0]-b[0])<1e-8 and abs(a[1]-b[1])<1e-8 and abs(a[2]-b[2])>1799 for b in coords(o)) for a in coords(o)) for o in piers)
checks['six_total_piers_two_shared_nodes_once_each']=len([o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('COMPOUND_PIER_','SHARED_PIER_','END_PIER_'))])==6
checks['retained_geometry_unchanged_after_build']=all(signature(o)==before[o.name] for o in retained)
checks['parent_and_R04_files_unchanged']=digest(D['parent'])==D['parent_sha256'] and digest(D['bay2_source'])==D['bay2_source_sha256']
tops={}
for o in piers:
 o.data.calc_loop_triangles();v=coords(o);tops[o['node_id']]=[[v[i][:2] for i in t.vertices] for t in o.data.loop_triangles if all(abs(v[i][2]-1800)<.001 for i in t.vertices)]
(R/'BLENDER_TOP_CAPS.json').write_text(json.dumps(tops));subprocess.run(['/usr/bin/python3',str(R/'verify_contacts.py')],check=True)
contacts=json.loads((R/'CONTACT_QA.json').read_text());section=json.loads((R/'SECTION_QA.json').read_text())
checks.update(contacts['checks']);checks.update(section['checks']);assert all(checks.values()),checks
bpy.ops.wm.save_as_mainfile(filepath=str(R/'SHARED_PIERS_R02.blend'))
def snapshot(obs):
 out={}
 for o in obs:
  v=coords(o);o.data.calc_loop_triangles();tri=[]
  for t in o.data.loop_triangles:
   pts=[tuple(round(v[i][k],3) for k in range(3)) for i in t.vertices]
   tri.append(min(tuple(pts[j:]+pts[:j]) for j in range(3)))
  out[o.name]=dict(bounds=[[min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]],triangles=sorted(tri))
 return out
snap=snapshot(retained+piers+[floor])
bpy.ops.export_scene.gltf(filepath=str(R/'SHARED_PIERS_R02.glb'),export_format='GLB',export_cameras=False,export_lights=False)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/'SHARED_PIERS_R02.glb'))
now=snapshot([o for o in bpy.context.scene.objects if o.type=='MESH'])
checks['GLB_object_names_and_count']=set(snap)==set(now)
err=max(abs(snap[n]['bounds'][j][k]-now[n]['bounds'][j][k]) for n in snap for j in range(2) for k in range(3))
checks['GLB_bounds_within_0_01']=err<.01
checks['GLB_oriented_triangle_signatures_at_0_001']=all(snap[n]['triangles']==now[n]['triangles'] for n in snap)
qa=dict(revision='SHARED_PIERS_R02_EXPERIMENTAL',parent=D['parent'],parent_sha256=D['parent_sha256'],bay2_source=D['bay2_source'],bay2_source_sha256=D['bay2_source_sha256'],checks=checks,passed=sum(checks.values()),total=len(checks),retained_mesh_count=len(retained),total_piers=6,shared_piers=2,bearings_per_shared_pier=5,source_contact_sections=16,clear_rectangles=section['clear_rectangles'],web_shared_edge_error=edge_error,glb_bounds_error=err,contact_metrics=contacts['metrics'],validation=dict(technical='scripts, mesh topology/volume, actual GLB reimport and oriented triangle signatures',geometric='actual spring section containment, shared shell-edge fit, straight extrusion, original masonry/vault mesh preservation, conservative clear rectangles',architectural='experimental two-bay chapel fixture; bay1 wall 320, source bay2 wall170 retained; original backing cores intentionally overlap new core; no transition redesign or tas-de-charge above spring',historical='not assessed; experimental profiles/bond retained',structural='not assessed; source support areas/capacity unverified; missing F5ZL-C schedule unresolved'))
(R/'QA.json').write_text(json.dumps(qa,indent=2));assert all(checks.values()),qa
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.world.color=(.65,.65,.65);scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(26200,-8200,5800));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=8200;cam.data.clip_end=100000;scene.camera=cam;aim(cam,(31000,0,2200))
for loc,power,size in [((28000,-4000,8500),2200000000,5000),((34000,3500,6500),1700000000,4000)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(31000,0,1800))
scene.render.filepath=str(R/'ASSEMBLY.png');bpy.ops.render.render(write_still=True)
for o in scene.objects:
 if o.type=='MESH':o.hide_render=o.name!='SHARED_PIER_S'
cam.location=(31800,250,2900);cam.data.ortho_scale=2300;aim(cam,(31000,-1250,900));scene.render.resolution_x=1000;scene.render.resolution_y=1000
scene.render.filepath=str(R/'SHARED_PIER_DETAIL.png');bpy.ops.render.render(write_still=True)
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
p=Path('/home/christopher/Documents/Cathedral/experimental/SHARED_PIERS_R02');q=json.loads((p/'QA.json').read_text());D=json.loads((p/'INPUTS.json').read_text());m=json.loads((p/'PIER_MESHES.json').read_text())[0];x,y=m['node']
fig,ax=plt.subplots(figsize=(6.2,3.1),dpi=150);fig.patch.set_facecolor('#eeeae2');ax.set_facecolor('#eeeae2')
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-180 -190 360 550">','<g fill="none" stroke="#999" stroke-width="0.8" stroke-dasharray="4 4"><path d="M -180 0 L 180 0 M 0 -190 L 0 360"/></g>']
def path(poly):return 'M '+' L '.join(str(a-x)+','+str(-(b-y)) for a,b in poly)+' Z'
a,b=zip(*m['core']);ax.fill([v-x for v in a],[v-y for v in b],color='#d8c7ac',alpha=.5);ax.plot([v-x for v in a],[v-y for v in b],color='#b33',linewidth=1,linestyle='--')
svg.append('<path d="'+path(m['core'])+'" fill="#d8c7ac" fill-opacity=".5" stroke="#b33" stroke-width="1" stroke-dasharray="4 3"/>')
for s in D['nodes']['S']['sections']:
 a,b=zip(*(s['polygon']+[s['polygon'][0]]));ax.plot([v-x for v in a],[v-y for v in b],color='black',linewidth=1)
 svg.append('<path d="'+path(s['polygon'])+'" fill="none" stroke="black" stroke-width="1"/>')
svg.append('</svg>');(p/'SHARED_S_SECTION_NATIVE.svg').write_text(''.join(svg))
ax.axhline(0,color='#999',linewidth=.6,linestyle='--');ax.axvline(0,color='#999',linewidth=.6,linestyle='--');ax.set_aspect('equal');ax.set_xlim(-180,180);ax.set_ylim(-350,175);ax.tick_params(labelsize=7)
ax.set_xlabel('Local X / native units',fontsize=8);ax.set_ylabel('Local Y',fontsize=8);ax.set_title('SHARED SECTION / 5 source profiles; dashed red: trial core',fontsize=9)
fig.tight_layout();fig.savefig(p/'SECTION.png',facecolor=fig.get_facecolor());plt.close(fig)
im=Image.new('RGB',(1800,1100),'#eeeae2');d=ImageDraw.Draw(im);f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';font=ImageFont.truetype(f,25);small=ImageFont.truetype(f,17)
d.text((26,16),'TWO CONNECTED BAYS / SHARED COMPOUND PIERS R02 EXPERIMENTAL',fill='#28251f',font=font)
d.text((26,53),'2 shared piers | 5 actual bearings each | one shared arch | original vaults and masonry retained',fill='#49443b',font=small)
a=Image.open(p/'ASSEMBLY.png').convert('RGB');a.thumbnail((1150,930));im.paste(a,(10,100))
a=Image.open(p/'SHARED_PIER_DETAIL.png').convert('RGB');a.thumbnail((600,600));im.paste(a,(1185,85))
a=Image.open(p/'SECTION.png').convert('RGB');a.thumbnail((620,310));im.paste(a,(1170,725))
d.text((26,1040),'EXISTING WALLS RETAINED - bay 1: 320 units / bay 2: 170 units; architectural transition unresolved',fill='#28251f',font=small)
d.text((1180,698),'ISOLATED SHARED PIER - five engaged responds',fill='#28251f',font=small)
d.text((26,1070),str(q['passed'])+'/'+str(q['total'])+' technical/geometric checks | architectural review pending | historical and structural validation not performed',fill='#49443b',font=small)
im.save(p/'SHARED_PIERS_R02_RESULT.png')
print(json.dumps(dict(passed=q['passed'],total=q['total'],edge_error=q['web_shared_edge_error'],retained=q['retained_mesh_count'],max_cap_gap=max(z['max_boundary_gap'] for v in q['contact_metrics'].values() for z in v))))

```
