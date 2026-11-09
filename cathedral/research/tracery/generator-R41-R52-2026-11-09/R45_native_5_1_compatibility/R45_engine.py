"""R45 unified procedural Gothic stone generator, Blender 5.1+.
Geometric methods recovered from R44 validated checkpoint; fully isolated.
All profiles are user-selectable and source-graded. No historical certification.
All positions/dimensions in meters internally, user config in millimetres.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
C=None
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
def path_sweep(name,coords,prof,material,coll=None):
 # coords = centerline coordinates in X/Z; sample uniformly along path, profiles
 # are perpendicular to tangent. Y is façade depth. Convex caps are triangulated.
 if coll is None:coll=C
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
def cut_box(name,origin,unit,u_width=.024,depth=.026,length=.14,side=1.,inset=.043,face_y=-.017):
 # Physical rebate: subtract shallow slot on inner arm side, with a nominal
 # rectangular 24x26mm tool cross-section; source lacks measured groove dims.
 tangent=unit.normalized()
 perp=Vector((tangent.z,0,-tangent.x))
 center=origin+perp*(side*inset)+Vector((0,face_y,0))
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


def create_study_collection(label='R45_EXPERIMENTAL'):
 global C
 C=bpy.data.collections.new(label)
 bpy.context.scene.collection.children.link(C)
 bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[C.name]
 bpy.context.scene.unit_settings.system='METRIC'
 bpy.context.scene.unit_settings.scale_length=1.
 return C

def validate_setout(cfg,profile):
 angle=float(cfg['branch_angle_deg'])
 total=float(cfg['arm_total_length_mm'])
 extension=float(cfg['extension_length_mm'])
 source_branch=float(cfg['branch_z_mm'])
 stem=float(cfg['stem_top_mm'])
 base=float(cfg['base_z_mm'])
 width=float(cfg['rebate_width_mm'])
 depth=float(cfg['rebate_depth_mm'])
 offset=float(cfg['rebate_offset_mm'])
 face=float(cfg['rebate_face_y_mm'])
 if not (25<=angle<=60):raise ValueError('BRANCH_ANGLE_UNSUPPORTED')
 if not(380<=total<=700):raise ValueError('ARM_LENGTH_UNSUPPORTED')
 if not(125<=extension<=250):raise ValueError('EXTENSION_LENGTH_UNSUPPORTED')
 joint=total-extension
 if not(220<=joint<=500):raise ValueError('AUTO_JOINT_OUTSIDE_ACCEPTED_BAND')
 if not(40<=base<source_branch<stem<=700):raise ValueError('STEM_BRANCH_BEARING_INVALID')
 if stem-source_branch<45:raise ValueError('STEM_UNION_OVERLAP_TOO_SHORT')
 if not (12<=width<=38 and 10<=depth<=38):raise ValueError('REBATE_SIZE_OUTSIDE_EXPERIMENTAL_ENVELOPE')
 if not(20<=offset<=70 and -40<=face<=0):raise ValueError('REBATE_POSITION_OUTSIDE_EXPERIMENTAL_ENVELOPE')
 if not(5<=cfg.get('rebate_overrun_mm',15)<=30):raise ValueError('REBATE_OVERRUN_UNSUPPORTED')
 if cfg.get('evidence_class','EXPERIMENTAL')!='EXPERIMENTAL':raise ValueError('HISTORICAL_CERTIFICATION_UNSUPPORTED')
 if not 25<=len(profile)<=2048:raise ValueError('PROFILE_VERTEX_COUNT_UNSUPPORTED')
 if abs(signed_area(profile))<.002:raise ValueError('PROFILE_AREA_TOO_SMALL')
 return {'joint_distance_mm':joint,'extension_mm':extension,'arm_total_mm':total,'branch_angle_deg':angle}

def build_stone_assembly(profile,profile_info,cfg,identifier,primary=None,secondary=None):
 """Build one real solid junction with two arm stones, shared recessed glazing slots."""
 if C is None:raise RuntimeError('CALL_create_study_collection_FIRST')
 setout=validate_setout(cfg,profile)
 a=math.radians(setout['branch_angle_deg'])
 branch_root=vec2(0,cfg['branch_z_mm']/1000)
 start=vec2(0,cfg['base_z_mm']/1000)
 stem_end=vec2(0,cfg['stem_top_mm']/1000)
 joint_m=setout['joint_distance_mm']/1000
 total_m=setout['arm_total_mm']/1000
 base_profile_area=abs(signed_area(profile))*1e6
 obj=path_sweep(identifier+'_Y_STONE',segment(start,stem_end),profile,primary or sand)
 branches=[]
 for side in (-1,1):
  direction=Vector((side*math.sin(a),0,math.cos(a)))
  joint=point_line(branch_root,direction,joint_m)
  tip=point_line(branch_root,direction,total_m)
  stub=path_sweep(identifier+'_TEMP_UNION',segment(branch_root,joint),profile,primary or sand)
  boolean(obj,stub,'UNION')
  bpy.data.objects.remove(stub,do_unlink=True)
  branches.append({'side':side,'direction':direction,'joint':joint,'tip':tip})
 # Independent cuts through common Y stone and each extension using SAME cutter.
 extensions=[];contacts=[];vol_removed=[]
 for i,info in enumerate(branches):
  ext=path_sweep(identifier+f'_EXTENSION_{i+1}',segment(info['joint'],info['tip']),profile,secondary or cream)
  stats_before=stats(ext)
  side=1 if info['side']<0 else -1
  cutoff_start=point_line(branch_root,info['direction'],
        joint_m-float(cfg.get('rebate_start_before_joint_mm',68))/1000)
  cutoff_end=point_line(branch_root,info['direction'],
        total_m+float(cfg.get('rebate_overrun_mm',15))/1000)
  cutter=cut_box(identifier+f'_RECESS_CUTTER_{i+1}',(cutoff_start+cutoff_end)*.5,
       info['direction'],u_width=cfg['rebate_width_mm']/1000,
       depth=cfg['rebate_depth_mm']/1000,length=(cutoff_end-cutoff_start).length,
       side=side,inset=cfg['rebate_offset_mm']/1000,face_y=cfg['rebate_face_y_mm']/1000)
  boolean(obj,cutter,'DIFFERENCE')
  boolean(ext,cutter,'DIFFERENCE')
  bpy.data.objects.remove(cutter,do_unlink=True)
  stats_after=stats(ext)
  volume_removed=stats_before['volume_litres']-stats_after['volume_litres']
  if volume_removed<.0001:raise ValueError('REBATE_TOOL_DID_NOT_REMOVE_MATERIAL')
  extensions.append(ext);vol_removed.append(volume_removed)
 # Post-boolean topology and measured mating surfaces.
 ym=stats(obj)
 if ym['connected_components']!=1:raise ValueError('Y_UNION_DISCONNECTED')
 em=[stats(x) for x in extensions]
 for i,info in enumerate(branches):
  capA=cap_test(obj,info['joint'],info['direction'])
  capB=cap_test(extensions[i],info['joint'],info['direction'])
  if min(capA['face_count'],capB['face_count'])<3:raise ValueError('CAP_FACES_MISSING')
  error=abs(capA['area_mm2']-capB['area_mm2'])
  normal=sum(a*b for a,b in zip(capA['normal'],capB['normal']))
  if error>.25 or abs(normal+1)>5e-5:raise ValueError('CONTACT_AREA_NORMAL_FAILURE')
  if capA['area_mm2']>=base_profile_area-40:raise ValueError('CONTACT_REBATE_NOT_VISIBLE')
  contacts.append({'joint_index':i,'face_area_mm2':capA['area_mm2'],
       'face_area_error_mm2':error,'normal_dot_product':normal,
       'rebate_area_difference_mm2':base_profile_area-capA['area_mm2']})
 for ob in [obj]+extensions:
  ob['R45_evidence_class']='EXPERIMENTAL'
  ob['source_profile_id']=profile_info['profile_id']
  ob['source_SHA256']=profile_info['source_sha256']
  ob['joint_historical_certification']=False
  ob['physical_scale']='Blender units are meters; 1:1 scale'
  ob['stone_part_of']=identifier
 return {'objects':[obj]+extensions,'contacts':contacts,'joint_bearings':branches,
    'rebate_removed_volume_litres_per_extension':vol_removed,
    'profile':profile_info,'setout':setout,'y_mesh_QA':ym,'extension_mesh_QA':em,
    'combined_volume_litres':ym['volume_litres']+sum(x['volume_litres'] for x in em)}

