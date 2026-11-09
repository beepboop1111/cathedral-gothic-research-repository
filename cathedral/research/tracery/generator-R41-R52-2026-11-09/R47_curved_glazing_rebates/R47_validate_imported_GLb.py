"""R46 independent GLB import and physical joint-contact verification.
New clean Blender scene; test imported geometry, not original in-memory meshes.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/home/christopher/Cathedral_Research/R47_curved_glazing_rebates')
source=json.loads((R/'R47_QA.json').read_text())
expected={x['name']:x for x in source['mesh_QA']}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'R47_WINDOW_HEAD_WITH_REBATES.glb'))
objects=[ob for ob in bpy.context.scene.objects if ob.type=='MESH']
assert len(objects)==29,('INCORRECT_IMPORT_BLOCK_COUNT',len(objects))
D={ob.name:ob for ob in objects}
assert set(D)==set(expected),('OBJ_NAMES_DIFFER',set(D).symmetric_difference(expected))
stored_bmeshes={};vertsmap={};meshes=[]
def rounded(p):
 return (round(float(p.x),5),round(float(p.y),5),round(float(p.z),5))
for obj in objects:
 bm=bmesh.new();bm.from_mesh(obj.data)
 raw=len(bm.verts);raw_non=sum(not e.is_manifold for e in bm.edges)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 bad=sum(not e.is_manifold for e in bm.edges)
 volume=abs(bm.calc_volume(signed=True))*1000
 if bad or abs(volume-expected[obj.name]['volume_L'])>.001:
  raise ValueError(('IMPORTED_MESH_INVALID',obj.name,bad,volume,expected[obj.name]['volume_L']))
 vertsmap[obj.name]={rounded(v.co) for v in bm.verts}
 stored_bmeshes[obj.name]=bm
 meshes.append({'object':obj.name,'raw_split_vertices':raw,'welded_vertices':len(bm.verts),
    'import_nonmanifold_before_weld':raw_non,'nonmanifold_after_weld':bad,
    'volume_litres':volume})
contact=[]
for rec in source['joint_contact_checks']:
 a,b=rec['parts'];bm1=stored_bmeshes[a];bm2=stored_bmeshes[b]
 common=vertsmap[a].intersection(vertsmap[b])
 if len(common)<50:
  raise ValueError(('SEAM_VERTEX_SET_TOO_SMALL',rec['joint_type'],len(common)))
 def cap_faces(bm):
  fs=[]
  for f in bm.faces:
   if all(rounded(v.co) in common for v in f.verts):
    fs.append(f)
  return fs
 f1=cap_faces(bm1);f2=cap_faces(bm2)
 if len(f1)<10 or len(f2)<10:
  raise ValueError(('SEAM_FACES_MISSING',rec['joint_type'],len(f1),len(f2),len(common)))
 def summary(fs):
  ar=sum(f.calc_area() for f in fs)
  n=sum((f.normal*f.calc_area() for f in fs),Vector())
  ctr=sum((f.calc_center_median()*f.calc_area() for f in fs),Vector())
  return ar,n.normalized(),ctr/ar
 ar1,n1,c1=summary(f1);ar2,n2,c2=summary(f2)
 err=abs(ar1-ar2)*1e6
 dot=n1.dot(n2);cen=(c1-c2).length*1000
 assert err<.25 and abs(dot+1)<1e-4 and cen<.03,(
  'BAD_REIMPORTED_CONTACT',rec['joint_type'],err,dot,cen)
 assert abs(ar1*1e6-rec['area_mm2'])<.25
 contact.append({'name':rec['joint_type'],'area_mm2':ar1*1e6,
   'imported_area_delta_mm2':err,'imported_normal_dot':dot,
   'centroid_delta_mm':cen,'matched_vertices':len(common)})
assert len(contact)==26
# Pairwise inter-arch clearance: do not allow glass openings to be occupied
# by a different unconnected frame. Contact-sharing within SAME arch is intentional.
def category(name):
 if 'OUTER' in name:return 'outer'
 if 'LEFT_LANCET' in name:return 'left_lancet'
 if 'RIGHT_LANCET' in name:return 'right_lancet'
 if 'QUATREFOIL' in name:return 'foil'
 return 'other'
BVH={}
for ob in objects:BVH[ob.name]=BVHTree.FromBMesh(stored_bmeshes[ob.name],epsilon=1e-6)
pairs=0;collisions=[]
for i,a in enumerate(objects):
 for b in objects[i+1:]:
  if category(a.name)==category(b.name):continue
  pairs+=1
  hits=BVH[a.name].overlap(BVH[b.name])
  if hits:collisions.append({'a':a.name,'b':b.name,'triangle_intersections':len(hits)})
# Release bmesh memory before logging
for bm in stored_bmeshes.values():bm.free()
# Geometric output is not considered fully clearance-certified if unrelated groups intersect.
result={'test':'R47 physical rebated 29-stone GLB imported validation','blender':bpy.app.version_string,
 'imported_meshes':len(meshes),'imported_manifold_pass':True,
 'independently_matched_contact_faces':len(contact),
 'intergroup_pair_checks':pairs,
 'intergroup_collision_pairs':collisions,
 'contacts':contact,
 'meshes':meshes,
 'historical_certification':False,
 'geometric_contact_pass':len(collisions)==0,
 'approval_scope':'EXPERIMENTAL; not fully dimensioned historic 2D/3D reference'}
target=R/('R47_roundtrip_'+bpy.app.version_string.split()[0].replace('.','_')+'.json')
target.write_text(json.dumps(result,indent=2))
print('R47_INDEPENDENT_IMPORT',json.dumps({'version':bpy.app.version_string,'meshes':len(meshes),
 'joints':len(contact),'intergroup_checks':pairs,'colliding_pairs':len(collisions),
 'max_area_error_mm2':max(z['imported_area_delta_mm2'] for z in contact),
 'max_centroid_error_mm':max(z['centroid_delta_mm'] for z in contact)}))
if collisions:
 print('R47_INTERGROUP_COLLISIONS',json.dumps(collisions[:10]))
