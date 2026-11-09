"""R45 independent GLB regression in clean Blender process.
Six independent 1:1 solids; match physical rebated contact polygons by area,
centroid, opposed normals; weld GLTF normal-split vertices for manifold checks.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('/home/christopher/Cathedral_Research')
R=ROOT/'R45_production_candidate'
reference=json.loads((R/'R45_native_build_QA.json').read_text())
expected={x['name']:x for x in reference['source_profile_cases']}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'R45_UNIFIED_BRANCHING_STONE_GENERATOR.glb'))
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(objs)==6,(len(objs),'incorrect GLB object count')
groups={
 'R45_PNG_A42':{'angle_deg':42,'offset':-.48},
 'R45_JSON_B35':{'angle_deg':35,'offset':.48}
}
def topology(obj):
 bm=bmesh.new();bm.from_mesh(obj.data)
 raw_verts=len(bm.verts); raw_bad=sum(not e.is_manifold for e in bm.edges)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 bad=sum(not e.is_manifold for e in bm.edges)
 volume=abs(bm.calc_volume(signed=True))
 welded=len(bm.verts)
 # separate connected parts are not acceptable even for technically closed meshes
 seen=set();components=0
 for v in bm.verts:
  if v in seen:continue
  components+=1;pending=[v]
  while pending:
   x=pending.pop()
   if x in seen:continue
   seen.add(x)
   pending.extend(edge.other_vert(x) for edge in x.link_edges if edge.other_vert(x) not in seen)
 bm.free()
 assert bad==0 and volume>1e-4 and components==1,(obj.name,bad,volume,components)
 return {'name':obj.name,'volume_litres':volume*1000,
  'raw_vertices':raw_verts,'welded_vertices':welded,
  'raw_split_edges':raw_bad,'nonmanifold_welded':bad,'connected_components':components}
def get_cap(obj,origin,tangent,epsilon=7e-6):
 bm=bmesh.new();bm.from_mesh(obj.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 faces=0;area=0.;n=Vector();cent=Vector()
 vertex_set=set()
 for f in bm.faces:
  p=[obj.matrix_world@v.co for v in f.verts]
  if all(abs((q-origin).dot(tangent))<epsilon for q in p):
   ar=f.calc_area()
   area+=ar
   n+=f.normal*ar
   cent+=sum(p,Vector())/len(p)*ar
   vertex_set.update((round(q.x,6),round(q.y,6),round(q.z,6)) for q in p)
   faces+=1
 bm.free()
 assert area>1e-3 and faces>4,(obj.name,'missing contact cap',faces,area)
 return {'area_mm2':area*1e6,'centroid':cent/area,'normal':n.normalized(),
   'faces':faces,'points':vertex_set}
full=[];contacts=[]
for group,cfg in groups.items():
 selected=sorted([x for x in objs if x.name.startswith(group)],key=lambda ob:ob.name)
 assert len(selected)==3,(group,'wrong object count',len(selected))
 body=next(x for x in selected if 'Y_STONE' in x.name)
 ends=[next(x for x in selected if f'EXTENSION_{i}' in x.name) for i in (1,2)]
 sizes=[topology(x) for x in [body]+ends]
 full+=sizes
 ref=expected[group]
 assert abs(sum(t['volume_litres'] for t in sizes)-ref['combined_volume_litres'])<.001
 angle=math.radians(cfg['angle_deg'])
 joint_m=ref['setout']['joint_distance_mm']/1000
 branch_z=.385
 for i,side in enumerate((-1,1)):
  tangent=Vector((side*math.sin(angle),0,math.cos(angle)))
  origin=Vector((cfg['offset'],0,branch_z))+tangent*joint_m
  a=get_cap(body,origin,tangent)
  b=get_cap(ends[i],origin,tangent)
  area_error=abs(a['area_mm2']-b['area_mm2'])
  dot=a['normal'].dot(b['normal'])
  mm_centroid=(a['centroid']-b['centroid']).length*1000
  assert area_error<.3 and abs(dot+1)<1e-4 and mm_centroid<.04,(
     group,area_error,dot,mm_centroid)
  exp=ref['contacts'][i]
  assert abs(a['area_mm2']-exp['face_area_mm2'])<.35
  contacts.append({'group':group,'stone_to_arm':i+1,
      'contact_area_mm2':a['area_mm2'],'area_mismatch_mm2':area_error,
      'centroid_mismatch_mm':mm_centroid,'opposed_normals_dot':dot,
      'cap_face_count':[a['faces'],b['faces']],
      'rebate_was_actual_geometry':True,'PASS':True})
assert len(contacts)==4 and all(q['PASS'] for q in contacts)
assert len(full)==6 and all(m['nonmanifold_welded']==0 for m in full)
report={'checkpoint':'R45','Blender_importer':bpy.app.version_string,
 'GLB_scene_objects':len(objs),'technical_pass':True,
 'profile_sources':'Synthetic grayscale PNG and explicit front/rear JSON sections',
 'source_historical_3d_certified':False,'BLENDER_1_TO_1_SCALE':'meters',
 'mechanical_structural_analysis':'NOT PERFORMED',
 'stone_objects':full,'contact_qa':contacts,
 'F5ZP_approved_geometry_modified':False}
target=R/('R45_import_QA_'+bpy.app.version_string.split()[0].replace('.','_')+'.json')
target.write_text(json.dumps(report,indent=2))
print('R45_GLb_ROUNDTRIP_PASS',json.dumps({'version':bpy.app.version_string,
 'meshes':len(full),'joints':len(contacts),'maximum_mating_area_error_mm2':max(x['area_mismatch_mm2'] for x in contacts),
 'max_centroid_error_mm':max(x['centroid_mismatch_mm'] for x in contacts)}))
