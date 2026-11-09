"""R42 modular branching Gothic stone generator — EXPERIMENTAL.
Different anterior/posterior moulding faces, true 3D Y-junction ashlar,
matching independent arm-extension stones, physical Boolean glazing rebates,
curved member control sample, source-graded QA.
Units: meters. No actual architectural fabric changed.
"""
import bpy,bmesh,math,json,csv,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from dataclasses import dataclass
R=Path('/home/christopher/Cathedral_Research/R44_bearing_regression/R44_B35')
R.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.
C=bpy.data.collections.new('R42_EXPERIMENTAL_GEOMETRY_NOT_APPROVED')
scene.collection.children.link(C)
bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[C.name]
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*c,1)
 p.inputs['Roughness'].default_value=.8
 return m
sand=mat('R42_branching_stone',(.53,.42,.31))
cream=mat('R42_individual_arm_stones',(.72,.59,.43))
ground=mat('R42_ground',(.15,.17,.20))
def stable_profile(depth_m=.16, half_m=.05, front_ridge=1.,rear_ridge=.55):
 # Symmetric L/R outline but intentionally DISTINCT front/back moulding rhythms.
 # x = transverse width, y = façade depth; measured historical profiles NOT available.
 if not(.08<=depth_m<=.30 and .025<=half_m<=.10):raise ValueError('BAD_CROSS_SECTION_DIMENSIONS')
 # Fractional façade-depth stations, with source-independent front/rear shape controls.
 stations=[(-.5,.22),(-.455,.36),(-.415,.44),(-.38,.40),(-.34,.57),(-.285,.71),
           (-.225,.63),(-.17,.85),(-.09,.97),(0,.95),(.09,.94),
           (.17,.85),(.225,.80),(.285,.73),(.33,.77),(.39,.56),(.44,.41),(.50,.28)]
 # front and rear topography have different physical lateral width as a function of depth.
 levels=[]
 for f,w in stations:
  modulation=front_ridge if f<0 else rear_ridge
  actual=.73*w+.27*max(.16,w*modulation)
  levels.append((f*depth_m,actual*half_m))
 # Draw one side top-to-bottom and return opposite side to create a simple closed contour.
 p=[(w,y) for y,w in levels]
 p += [(-w,y) for y,w in reversed(levels)]
 assert min(y for x,y in p)<0 and max(y for x,y in p)>0
 return p
def signed_area(poly):
 return .5*sum(x*v-u*y for (x,y),(u,v) in zip(poly,poly[1:]+poly[:1]))
def triangulation(poly):
 vertices=[Vector((u,v,0)) for u,v in poly]
 lookup={(round(v.x,10),round(v.y,10)):i for i,v in enumerate(vertices)}
 tris=tessellate_polygon([vertices])
 out=[]
 for tri in tris:
  idx=list(tri) if isinstance(tri[0],int) else [lookup[round(v.x,10),round(v.y,10)] for v in tri]
  if len(set(idx))==3:out.append(tuple(idx))
 assert len(out)==len(poly)-2, (len(out),len(poly))
 return out
def path_sweep(name,coords,prof,material,coll=C):
 # coords = centerline coordinates in X/Z; sample uniformly along path, profiles
 # are perpendicular to tangent. Y is façade depth. Convex caps are triangulated.
 if len(coords)<2:raise ValueError('NEED_PATH_STATIONS')
 cp=[Vector((x,0,z)) for x,z in coords]
 assert all((b-a).length>.001 for a,b in zip(cp,cp[1:]))
 area=signed_area(prof)
 if area<0:prof=list(reversed(prof))
 n=len(prof);verts=[]
 for i,p in enumerate(cp):
  t=(cp[min(i+1,len(cp)-1)]-cp[max(0,i-1)]).normalized()
  u=Vector((t.z,0,-t.x))
  for w,y in prof:
   q=p+u*w+Vector((0,y,0))
   verts.append(tuple(q))
 faces=[]
 for j in range(len(cp)-1):
  base=j*n; nxt=(j+1)*n
  for i in range(n):
   k=(i+1)%n
   faces.extend(((base+i,base+k,nxt+k),(base+i,nxt+k,nxt+i)))
 tri=triangulation(prof)
 faces.extend(tuple(reversed(t)) for t in tri)
 faces.extend(tuple((len(cp)-1)*n+i for i in t) for t in tri)
 mesh=bpy.data.meshes.new(name+'_mesh')
 mesh.from_pydata(verts,[],faces);mesh.update()
 ob=bpy.data.objects.new(name,mesh);coll.objects.link(ob)
 mesh.materials.append(material)
 cleanup(ob)
 return ob
def cleanup(ob):
 bm=bmesh.new();bm.from_mesh(ob.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=2e-7)
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 # Non-planar / n-gon Boolean output must be triangulated *before* GLB export.
 polys=[f for f in bm.faces if len(f.verts)>3]
 if polys:bmesh.ops.triangulate(bm,faces=polys,quad_method='BEAUTY',ngon_method='BEAUTY')
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(ob.data);bm.free();ob.data.update()
def stats(ob,require_manifold=True):
 bm=bmesh.new();bm.from_mesh(ob.data)
 bad=sum(not e.is_manifold for e in bm.edges)
 vol=bm.calc_volume(signed=True)
 faces=len(bm.faces);vertices=len(bm.verts)
 # Count connected mesh components by BFS edge traversal.
 visited=set(); parts=0
 for v in bm.verts:
  if v.index in visited:continue
  parts+=1
  group=[v]
  while group:
   k=group.pop()
   if k.index in visited:continue
   visited.add(k.index)
   group.extend(ed.other_vert(k) for ed in k.link_edges if ed.other_vert(k).index not in visited)
 bm.free()
 if require_manifold:assert bad==0 and vol>0,(ob.name,bad,vol,parts)
 return {'vertices':vertices,'faces':faces,'volume_litres':vol*1000.,
         'nonmanifold_edges':bad,'connected_components':parts}
def boolean(base,tool,operation):
 m=base.modifiers.new('R42_'+operation,'BOOLEAN')
 m.operation=operation;m.solver='EXACT';m.object=tool
 bpy.context.view_layer.objects.active=base
 bpy.ops.object.modifier_apply(modifier=m.name)
 cleanup(base)
 return base
def vec2(x,z):return Vector((x,0,z))
def point_line(origin,unit,dist):return origin+unit*dist
def segment(p,q):
 return [(p.x,p.z),(q.x,q.z)]
def cut_box(name,origin,unit,u_width=.024,depth=.026,length=.14,side=1.):
 # Physical rebate: subtract shallow slot on inner arm side, with a nominal
 # rectangular 24x26mm tool cross-section; source lacks measured groove dims.
 tangent=unit.normalized()
 perp=Vector((tangent.z,0,-tangent.x))
 center=origin+perp*(side*.043)+Vector((0,-.017,0))
 bpy.ops.mesh.primitive_cube_add(size=1,location=center)
 ob=bpy.context.object;ob.name=name
 if ob.users_collection and C not in ob.users_collection:
  for c in list(ob.users_collection):c.objects.unlink(ob)
  C.objects.link(ob)
 # Local x along cross-member perpendicular, local z along tangent, local y façade depth.
 basis=__import__('mathutils').Matrix(((perp.x,0,tangent.x),(0,1,0),(perp.z,0,tangent.z)))
 ob.rotation_euler=basis.to_euler()
 ob.dimensions=(u_width,depth,length)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return ob
def cap_test(ob,cap_center,axis,eps=2e-6):
 # Find interface face triangles in the plane through cap_center.
 # The union may triangulate in a new way: use area & normals, not equality of vertices.
 bm=bmesh.new();bm.from_mesh(ob.data)
 plane=(cap_center,axis.normalized())
 ar=0;normal=Vector();num=0
 for f in bm.faces:
  if all(abs((v.co-plane[0]).dot(plane[1]))<eps for v in f.verts):
   fa=f.calc_area();ar+=fa;normal+=f.normal*fa;num+=1
 out={'area_mm2':ar*1e6,'face_count':num,
      'normal':tuple(normal.normalized()) if normal.length else None}
 bm.free()
 return out

# Modelling inputs and machine guardrails.
import sys
sys.path.insert(0,'/home/christopher/Cathedral_Research/R43_profile_intake_and_review')
from R43_profile_intake import load_section
profile,PROVENANCE=load_section(Path('/home/christopher/Cathedral_Research/R43_profile_intake_and_review/R43_profile_family_2.json'))
profile_area_mm2=abs(signed_area(profile))*1e6
assert profile_area_mm2>4000
assert len(profile)>=24
main_origin=vec2(0,.055)
stem_end=vec2(0,.46)
branch_origin=vec2(0,.385)
branch_angle=math.radians(35)
ANG=[]
branches=[]
for side in (-1,1):
 direction=Vector((side*math.sin(branch_angle),0,math.cos(branch_angle)))
 joint=point_line(branch_origin,direction,.315)
 tip=point_line(branch_origin,direction,.48)
 branches.append({'side':side,'direction':direction,'joint':joint,'tip':tip})
# Main trunk and two intersecting daughter sweeps are ONE masonry block by exact solid union.
Y=path_sweep('R42_Y_junction_ashlar',segment(main_origin,stem_end),profile,sand)
prior=stats(Y)
assert prior['connected_components']==1
for i,info in enumerate(branches):
 stub=path_sweep(f'R42_union_branch_{i}',segment(branch_origin,info['joint']),profile,sand)
 boolean(Y,stub,'UNION')
 bpy.data.objects.remove(stub,do_unlink=True)
y_geom=stats(Y)
if y_geom['connected_components']!=1:raise AssertionError(('Y_BODY_MULTIPART',y_geom))
# Two standalone stones follow the branch ends, with precisely matching cap frames.
extensions=[]
for i,info in enumerate(branches):
 ex=path_sweep(f'R42_extension_stone_{i+1}',segment(info['joint'],info['tip']),profile,cream)
 extensions.append(ex)
# Glazing rebate: cut through Y branch end and matching extension from the SAME tool;
# leave a 22mm buffer towards internal Y topology but groove crosses actual joint plane.
for i,info in enumerate(branches):
 side=1. if info['side']==-1 else -1.
 section_start=point_line(branch_origin,info['direction'],.247)
 # Tool intentionally overshoots the outer cap by 15mm to prevent coplanar Boolean artifacts.
 section_end=point_line(branch_origin,info['direction'],.495)
 mid=(section_start+section_end)*.5
 cutter=cut_box(f'R42_REBATE_boolean_tool_{i+1}',mid,info['direction'],
                u_width=.029,depth=.028,length=(section_end-section_start).length,side=side)
 boolean(Y,cutter,'DIFFERENCE')
 boolean(extensions[i],cutter,'DIFFERENCE')
 bpy.data.objects.remove(cutter,do_unlink=True)
# Validate post-rebate individual stone geometry and seams.
sy=stats(Y)
extstats=[stats(ob) for ob in extensions]
assert sy['connected_components']==1
assert all(q['connected_components']==1 for q in extstats)
assert all(q['nonmanifold_edges']==0 for q in [sy]+extstats)
contacts=[]
for i,info in enumerate(branches):
 cap_y=cap_test(Y,info['joint'],info['direction'])
 cap_e=cap_test(extensions[i],info['joint'],info['direction'])
 assert cap_y['face_count']>2 and cap_e['face_count']>2,('Missing cap face',i,cap_y,cap_e)
 assert abs(cap_y['area_mm2']-cap_e['area_mm2'])<.25,('Mismatched machined joint area',i,cap_y,cap_e)
 dot=sum(a*b for a,b in zip(cap_y['normal'],cap_e['normal']))
 assert abs(dot+1)<5e-5,('normals not opposite',i,dot)
 contacts.append({'branch':i+1,'cap_area_mm2':cap_y['area_mm2'],'mating_area_mm2':cap_e['area_mm2'],
                  'area_error_mm2':abs(cap_y['area_mm2']-cap_e['area_mm2']),
                  'contact_normal_dot':dot,'face_count_Y':cap_y['face_count'],'face_count_extension':cap_e['face_count']})
# Separate curved sweep smoke control. A Bezier centerline is a distinct engineering
# capability, not evidence of a specific medieval curve.
curve=[]
for i in range(21):
 t=i/20
 x=.15+(.27-.15)*t+.037*math.sin(math.pi*t)
 z=.10+.38*t
 curve.append((x,z))
curved=path_sweep('R42_CURVED_MEMBER_TEST_ONLY',curve,profile,sand)
sc=stats(curved)
assert sc['connected_components']==1
# Include synthetic evidence plus source separation; do not claim Ayr dimensions for R42.
for ob in [Y]+extensions+[curved]:
 ob['historical_accuracy']='NOT_ASSESSED'
 ob['profile_provenance']='R42 SYNTHETIC: front/rear profile values NOT archaeological'
 ob['source_note']='Ayr drawing used as qualitative comparison ONLY, no physical fitting faces'
 ob['project_baseline']='R41 locked / F5ZP protected'
# export only the Y+2 arm stones to GLB; curve control remains separate render-only.
bpy.ops.object.select_all(action='DESELECT')
for ob in [Y]+extensions:ob.select_set(True)
bpy.context.view_layer.objects.active=Y
outglb=R/'R42_BRANCHING_JOINT_AND_REBATES.glb'
bpy.ops.export_scene.gltf(filepath=str(outglb),export_format='GLB',
  use_selection=True,export_apply=True,export_yup=True,export_extras=True)
assert outglb.stat().st_size>15000

qa={'fixture':'R44_B35','branch_angle_deg':35,'source_profile_family':PROVENANCE['profile_id'],
    'profile_sha256':PROVENANCE['source_sha256'],'number_of_stones':3,
    'branching_body':sy,'extensions':extstats,'contacts':contacts,
    'all_contacts_pass':all(c['area_error_mm2']<.25 and abs(c['contact_normal_dot']+1)<5e-5 for c in contacts),
    'source_class':'SYNTHETIC','historical_joint_authenticated':False,
    'GLB':str(outglb),'protected_baselines_modified':False}
assert qa['all_contacts_pass']
(R/'R44_qa.json').write_text(json.dumps(qa,indent=2))
print('R44_VARIANT_PASS',json.dumps(qa))
