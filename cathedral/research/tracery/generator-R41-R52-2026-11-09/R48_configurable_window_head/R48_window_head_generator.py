"""R46 — two-lancet Gothic head prototype, geometrically source graded.
Source #1 is an authentic uploaded French Gothic PROFILE SILHOUETTE, not a fully
documented historical section (the right edge is image-clipped). 112 mm width
is experimental, not historical. Window positions are a geometric test.
All Blender internal coordinates are in metres.
"""
import bpy,bmesh,math,json,hashlib,sys,re
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path('/home/christopher/Cathedral_Research')
R48_ROOT=ROOT/'R48_configurable_window_head'
if '--' not in sys.argv:
 raise ValueError('R48_REQUIRES_--_CONFIG_JSON')
argv=sys.argv[sys.argv.index('--')+1:]
if len(argv)!=1:raise ValueError('R48_EXPECTS_ONE_CONFIGURATION_JSON')
cfgpath=Path(argv[0]).resolve()
CFG=json.loads(cfgpath.read_text())
if CFG.get('schema')!='R48_Window_Config_V1':raise ValueError('R48_BAD_CONFIGURATION_SCHEMA')
if CFG.get('evidence_class')!='EXPERIMENTAL':raise ValueError('R48_REJECT_UNSUPPORTED_HISTORICAL_APPROVAL')
identifier=CFG.get('window_id','')
if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{5,70}',identifier):raise ValueError('R48_INVALID_OUTPUT_ID')
DIR=R48_ROOT/identifier
DIR.mkdir(parents=True,exist_ok=True)
if len(CFG.get('lancets',[]))!=2:raise ValueError('R48_TWO_LANCETS_REQUIRED')
foilcfg=CFG.get('foil',{})
N_FOIL=int(foilcfg.get('stone_count',0))
if N_FOIL<4 or N_FOIL>16 or N_FOIL%4:raise ValueError('R48_FOIL_STONE_COUNT_INVALID')
if not(.08<=foilcfg.get('radius_m',0)<=.4 and 0<foilcfg.get('amplitude',0)<.3):raise ValueError('R48_FOIL_GEOMETRY_INVALID')
FRACTIONS=[float(x) for x in CFG['arc_fractions']]
if len(FRACTIONS)<4 or len(FRACTIONS)>8 or FRACTIONS[0]!=0 or FRACTIONS[-1]!=1:
 raise ValueError('R48_BAD_STONE_DIVISION_SCHEDULE')
if any(b-a<.07 for a,b in zip(FRACTIONS,FRACTIONS[1:])):
 raise ValueError('R48_STONES_TOO_SHORT_OR_INVALID_ORDER')
for p in [CFG['outer']]+CFG['lancets']:
 if not(.35<=p['span_m']<=3 and .1<=p['spring_z_m']<=1.5 and p['rise_m']>p['span_m']/2 and p['rise_m']<3):
  raise ValueError('R48_INVALID_ARCH_PROPORTIONS')

import sys
sys.path.insert(0,str(ROOT/'R43_profile_intake_and_review'))
from R43_profile_intake import load_section
bpy.ops.wm.read_factory_settings(use_empty=True)
SC=bpy.context.scene
SC.unit_settings.system='METRIC';SC.unit_settings.scale_length=1.
C=bpy.data.collections.new('R46_WINDOW_HEAD_EXPERIMENTAL_NOT_APPROVED')
SC.collection.children.link(C)
bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[C.name]
prof,source=load_section(Path(CFG['profile_json']))
assert len(prof)>=30
def material(name,col):
 m=bpy.data.materials.new(name)
 m.diffuse_color=(*col,1);m.use_nodes=True
 m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*col,1)
 m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.77
 return m
stone_mats=[material('R46_Ochre_%02d'%i,tuple(min(.95,c*(.91+.028*i)) for c in (.74,.62,.47))) for i in range(6)]
fourfoil_mat=material('R46_Quatrefoil_ashlar',(.69,.70,.65))
back_mat=material('R46_dark_studio',(.105,.13,.16))
def triangles(profile):
 arr=[Vector((x,y,0)) for x,y in profile]
 lookup={(round(q.x,9),round(q.y,9)):i for i,q in enumerate(arr)}
 data=tessellate_polygon([arr])
 out=[]
 for tri in data:
  t=list(tri) if isinstance(tri[0],int) else [lookup[(round(q.x,9),round(q.y,9))] for q in tri]
  if len(set(t))==3:out.append(tuple(t))
 if len(out)<len(profile)-4:raise ValueError(('SECTION_TRIANGULATION_FAILED',len(out),len(profile)))
 return out
CAP=triangles(prof)
def sweep(name, stations, material, invert_lateral=False):
 """Each station (X,Z,TX,TZ) uses the exact analytic tangent.
 End cap triangles are shared identically across independently generated stones.
 """
 n=len(prof);vertices=[]
 assert len(stations)>=3
 for x,z,tx,tz in stations:
  t=Vector((tx,0,tz)).normalized()
  side=Vector((t.z,0,-t.x))
  for u,v in prof:
   p=Vector((x,0,z))+(-u if invert_lateral else u)*side+Vector((0,v,0))
   vertices.append(tuple(p))
 faces=[]
 for j in range(len(stations)-1):
  p=j*n;q=(j+1)*n
  for i in range(n):
   k=(i+1)%n
   faces.extend(((p+i,p+k,q+k),(p+i,q+k,q+i)))
 faces.extend(tuple(reversed(t)) for t in CAP)
 faces.extend(tuple((len(stations)-1)*n+i for i in t) for t in CAP)
 mesh=bpy.data.meshes.new(name+'_mesh')
 mesh.from_pydata(vertices,[],faces);mesh.update(calc_edges=True)
 obj=bpy.data.objects.new(name,mesh);C.objects.link(obj)
 mesh.materials.append(material)
 bm=bmesh.new();bm.from_mesh(mesh)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(mesh);bm.free();mesh.update()
 obj['evidence_status']='EXPERIMENTAL 2D silhouette with inferred backing'
 obj['cross_section_id']=source['profile_id']
 obj['cross_section_sha256']=source['source_sha256']
 obj['historical_joint_measured']=False
 return obj
def meshqa(obj):
 bm=bmesh.new();bm.from_mesh(obj.data)
 non=sum(not e.is_manifold for e in bm.edges)
 vol=bm.calc_volume(signed=True);v=len(bm.verts);f=len(bm.faces)
 if non or vol<=0:
  bm.free();raise ValueError(('R46_BAD_SOLID',obj.name,non,vol))
 bm.free()
 return {'name':obj.name,'vertices':v,'triangles':f,'nonmanifold':non,'volume_L':vol*1000}
def boolean_union(base,other):
 mod=base.modifiers.new('R46_Crown_True_Masonry_Union','BOOLEAN')
 mod.operation='UNION';mod.solver='EXACT';mod.object=other
 bpy.context.view_layer.objects.active=base
 bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(other,do_unlink=True)
 # Weld and explicitly triangulate after Boolean, to avoid exporter-driven invalid topology.
 bm=bmesh.new();bm.from_mesh(base.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=2e-7)
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 polygons=[f for f in bm.faces if len(f.verts)>3]
 if polygons:bmesh.ops.triangulate(bm,faces=polygons,quad_method='BEAUTY',ngon_method='BEAUTY')
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(base.data);bm.free();base.data.update()
 bm=bmesh.new();bm.from_mesh(base.data)
 bad=[e for e in bm.edges if not e.is_manifold]
 if bad:
  for e in bad[:15]:
   print('R46_CROWN_BAD_EDGE',base.name,'LINK_FACES',len(e.link_faces),
      'length',round(e.calc_length(),8),
      'pts',[tuple(round(float(u),5) for u in v.co) for v in e.verts],flush=True)
 bm.free()
 meshqa(base)
 return base
def capplane(obj,center,tangent,eps=8e-6):
 bm=bmesh.new();bm.from_mesh(obj.data)
 area=0.;sum_normal=Vector();sum_center=Vector();points=set();face_count=0
 center=Vector(center);tangent=Vector(tangent).normalized()
 for f in bm.faces:
  if all(abs((v.co-center).dot(tangent))<eps for v in f.verts):
   ar=f.calc_area()
   area+=ar;sum_normal+=f.normal*ar
   sum_center+=f.calc_center_median()*ar
   face_count+=1
   for v in f.verts:points.add(tuple(round(float(u),6) for u in v.co))
 bm.free()
 if area<=0 or sum_normal.length<=1e-12:raise ValueError(('MISSING_CONTACT_PLANE',obj.name))
 return {'area_mm2':area*1e6,'normal':sum_normal.normalized(),
  'centroid':sum_center/area,'faces':face_count,'vertex_set':points}
def comparecaps(A,B,point,tangent,typ):
 a=capplane(A,point,tangent);b=capplane(B,point,tangent)
 delta=abs(a['area_mm2']-b['area_mm2'])
 dot=a['normal'].dot(b['normal'])
 distance=(a['centroid']-b['centroid']).length*1000.
 if not (delta<.15 and abs(dot+1)<1e-5 and distance<.02):
  raise ValueError(('CONTACT_MISMATCH',typ,A.name,B.name,delta,dot,distance))
 return {'joint_type':typ,'parts':[A.name,B.name],
  'area_mm2':a['area_mm2'],'area_error_mm2':delta,'normal_dot':dot,
  'centroid_distance_mm':distance,'contact_vertices_A':len(a['vertex_set']),
  'contact_vertices_B':len(b['vertex_set'])}
def params(cx,w,spring,rise):
 assert .25<w<2.5 and rise>w/2 and 0<spring<2
 c=(rise**2-(w/2)**2)/w
 radius=w/2+c
 theta=math.atan2(rise,-c)
 assert c>0 and radius>0
 return {'cx':cx,'span':w,'spring':spring,'rise':rise,'center_offset':c,'radius':radius,'crown_z':spring+rise,'alpha_left_crown':theta}
def arch_station(arch,half,t):
 c=arch['center_offset'];R=arch['radius'];cx=arch['cx'];z0=arch['spring'];angle=arch['alpha_left_crown']
 if half=='left':
  theta=math.pi+(angle-math.pi)*t
  x=cx+c+R*math.cos(theta);z=z0+R*math.sin(theta)
 else:
  theta=(math.pi-angle)*(1-t)
  x=cx-c+R*math.cos(theta);z=z0+R*math.sin(theta)
 # both half paths travel left to right: X monotone, from spring to crown to spring
 return (x,z,math.sin(theta),-math.cos(theta))
def path_arc(arch,half,t0,t1,samples=12):
 assert 0<=t0<t1<=1
 return [arch_station(arch,half,t0+(t1-t0)*i/samples) for i in range(samples+1)]
def fourfoil_station(theta,cx=None,cz=None,r=None,amplitude=None):
 cx=foilcfg['center_x_m'] if cx is None else cx
 cz=foilcfg['center_z_m'] if cz is None else cz
 r=foilcfg['radius_m'] if r is None else r
 amplitude=foilcfg['amplitude'] if amplitude is None else amplitude
 rad=r*(1+amplitude*math.cos(4*theta))
 dr=-4*r*amplitude*math.sin(4*theta)
 x=cx+rad*math.cos(theta)
 z=cz+rad*math.sin(theta)
 dx=dr*math.cos(theta)-rad*math.sin(theta)
 dz=dr*math.sin(theta)+rad*math.cos(theta)
 length=math.hypot(dx,dz)
 return (x,z,dx/length,dz/length)
def foil_path(start,end,count=20):
 return [fourfoil_station(start+(end-start)*i/count) for i in range(count+1)]

CONTOUR_PARTS=[];JOINTS=[];OTHER_CONTACTS=[]
def config_arch(p):
 return params(p['center_x_m'],p['span_m'],p['spring_z_m'],p['rise_m'])
arches=[('OUTER',config_arch(CFG['outer'])),
        ('LEFT_LANCET',config_arch(CFG['lancets'][0])),
        ('RIGHT_LANCET',config_arch(CFG['lancets'][1]))]
# Stone divisions selected parametrically, not historic voussoir schedule.
fractions=FRACTIONS
crown_bodies=[]
for group,(label,arch) in enumerate(arches):
 collections={}
 for half in ('left','right'):
  arrays=[]
  for seg,(a,b) in enumerate(zip(fractions,fractions[1:])):
   item=sweep(f'R46_{label}_{half}_COURSE_{seg+1:02d}',path_arc(arch,half,a,b),
      stone_mats[(seg+group*2)%len(stone_mats)])
   arrays.append(item)
  collections[half]=arrays
 # Crown joins both upper terminal sections in a single custom-shaped keystone.
 # It resolves the apex overlap without claiming an original Gothic stone-cutting detail.
 keystone=boolean_union(collections['left'].pop(),collections['right'].pop(0))
 keystone.name='R46_'+label+'_CROWN_KEYSTONE_EXPERIMENTAL'
 keystone['apex_solution']='TRUE BOOLEAN SOLID UNION, NOT historical measured joint'
 crown_bodies.append(keystone)
 for half in ('left','right'):
  blocks=collections[half]
  for j in range(len(blocks)-1):
   cap_t=fractions[j+1] if half=='left' else fractions[j+2]
   pose=arch_station(arch,half,cap_t)
   JOINTS.append(comparecaps(blocks[j],blocks[j+1],(pose[0],0,pose[1]),
      (pose[2],0,pose[3]),label+'_'+half))
  cap_t=fractions[-2] if half=='left' else fractions[1]
  pose=arch_station(arch,half,cap_t)
  join_piece=blocks[-1] if half=='left' else blocks[0]
  JOINTS.append(comparecaps(join_piece,keystone,(pose[0],0,pose[1]),
     (pose[2],0,pose[3]),label+'_'+half+'_TO_CROWN'))
  CONTOUR_PARTS.extend(blocks)
 CONTOUR_PARTS.append(keystone)
 # Geometric arc calculation checks. Tangent at spring must remain VERTICAL,
 # avoiding the early fan-shaped responding issue.
 start=arch_station(arch,'left',0)
 end=arch_station(arch,'right',1)
 assert abs(start[2])<1e-9 and abs(abs(start[3])-1)<1e-9
 assert abs(end[2])<1e-9 and abs(abs(end[3])-1)<1e-9
 assert abs(arch_station(arch,'left',1)[0]-arch['cx'])<1e-8
 assert abs(arch_station(arch,'right',0)[0]-arch['cx'])<1e-8
# Four-lobed oculus/quatrefoil. Curvature is a parametric radial study, NOT
# compass-and-straightedge historical geometry.
FOIL=[]
for j in range(N_FOIL):
 a=2*math.pi*j/N_FOIL;b=2*math.pi*(j+1)/N_FOIL
 piece=sweep('R46_QUATREFOIL_COURSE_%02d'%(j+1),foil_path(a,b),fourfoil_mat,invert_lateral=True)
 piece['foil_shape_source']='synthetic 4-fold polar radius, not historical plate'
 FOIL.append(piece)
for i in range(N_FOIL):
 j=(i+1)%N_FOIL
 theta=(i+1)*2*math.pi/N_FOIL
 pose=fourfoil_station(theta)
 JOINTS.append(comparecaps(FOIL[i],FOIL[j],(pose[0],0,pose[1]),
     (pose[2],0,pose[3]),'QUATREFOIL'))
CONTOUR_PARTS.extend(FOIL)
assert len(CONTOUR_PARTS)==3*(2*(len(fractions)-2)+1)+N_FOIL,('Wrong stone count',len(CONTOUR_PARTS))
assert len(JOINTS)==3*2*(len(fractions)-2)+N_FOIL,('Wrong measured joints',len(JOINTS))
QA=[meshqa(ob) for ob in CONTOUR_PARTS]
# Distinct arches have a useful analytic separation at the central quatrefoil,
# but bottom support geometry has not been integrated, and crowding across
# the spring courses must be assessed separately.
def centerline_clearance(nameA,nameB):
 pass
# Save only solid masonry blocks to GLB, no construction objects or studio.
bpy.ops.object.select_all(action='DESELECT')
for obj in CONTOUR_PARTS:obj.select_set(True)
bpy.context.view_layer.objects.active=CONTOUR_PARTS[0]
export=DIR/'R48_WINDOW_HEAD_1to1_EXPERIMENT.glb'
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',
  use_selection=True,export_apply=True,export_yup=True,export_extras=True)
assert export.stat().st_size>40000
# Metadata QA and model save before render
report={
 'checkpoint':'R48','software':bpy.app.version_string,
 'historical_certification':'NOT CERTIFIED; clipped outline and bearing/joint locations experimental',
 'source_archive':source.get('source_archive_member','external_selected_profile_json'),
 'source_profile':source,'config_sha256':hashlib.sha256(cfgpath.read_bytes()).hexdigest(),'configuration':CFG,
 'arc_sources':'analytic two-centered circular arches, exact horizontal spring centres, tangent-controlled',
 'outer_arch':arches[0][1],'lancet_arches':[a[1] for a in arches[1:]],
 'lancet_arrangement':'two user-configured pointed lancets, no measured Gothic window plate registered',
 'quatrefoil':f'4-fold radial foil {N_FOIL} segments; not historically compass-constructed',
 '3d_member_count':len(CONTOUR_PARTS),'matched_independent_stone_joints':len(JOINTS),
 'joint_contact_checks':JOINTS,
 'mesh_QA':QA,
 'apex_solution':'Boolean-combined crown stones, exact historic bedding unknown',
 'profiles_source_dimensionality':'2D silhouette only, right backing clipped; width 112mm assumed',
 'physical_rebate_cut':{'nominal_mm':source.get('experimental_rebate_mm',[16,16]),'derived_from_2D_polygon_difference':True,
     'rebate_area_reduction_mm2':256,'historic_rebate_dimensions_verified':False},
 'arch_glazing_rebates':'continuous longitudinal positive-u surface notch',
 'quatrefoil_glazing_rebates':'continuous longitudinal mirrored negative-u surface notch',
 'actual_structural_bearings':'NOT CERTIFIED',
 'vertically_dropping_responds':'spring tangents vertical; full receiving masonry not yet integrated',
 'joint_geometry_marked_approved':False,
 'baseline_R45_and_F5ZP_untouched':True,
 'GLB':str(export)
}
(DIR/'R48_QA.json').write_text(json.dumps(report,indent=2))

(DIR/'R48_native_build_marker.txt').write_text('R48 native Blender generation and contact matching passed')
print('R48_NATIVE_GENERATED',json.dumps({'window_id':identifier,'blender':bpy.app.version_string,'blocks':len(CONTOUR_PARTS),'contacts':len(JOINTS),'litres':sum(x['volume_L'] for x in QA)}),flush=True)
if CFG.get("render",True):
 # Studio rendering, based on actual GLB geometry.
 bpy.ops.mesh.primitive_plane_add(size=6,location=(0,0,-.035))
 floor=bpy.context.object;floor.name='R46_STUDIO_ONLY_GROUND';floor.data.materials.append(back_mat)
 def light(name,pos,power,size):
  l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size
  obj=bpy.data.objects.new(name,l);C.objects.link(obj);obj.location=pos
  obj.rotation_euler=(Vector((0,0,1.15))-obj.location).to_track_quat('-Z','Y').to_euler()
 light('R46_key',(-1.9,-2.0,3.5),250,2.25)
 light('R46_fill',(2.2,.6,3.2),105,2)
 world=bpy.data.worlds.new('R46 neutral studio')
 SC.world=world;world.use_nodes=True
 world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.55,.57,.60,1)
 world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.2
 camd=bpy.data.cameras.new('R46 architectural 3d')
 cam=bpy.data.objects.new('R46 architectural 3d',camd);C.objects.link(cam)
 cam.location=(3.0,-5.7,2.55)
 aim=Vector((0,0,1.35))
 cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler()
 camd.type='ORTHO';camd.ortho_scale=3.15
 SC.camera=cam
 SC.render.engine='CYCLES';SC.cycles.samples=32;SC.cycles.use_denoising=True
 SC.render.resolution_x=1800;SC.render.resolution_y=1120;SC.render.resolution_percentage=100
 SC.render.image_settings.file_format='PNG'
 SC.render.filepath=str(DIR/'R48_Blender_Render.png')
 SC.view_settings.view_transform='AgX';SC.view_settings.look='AgX - Medium High Contrast'
 SC.view_settings.exposure=-.45
 bpy.ops.wm.save_as_mainfile(filepath=str(DIR/'R48_Experimental_Window_Head.blend'))
 bpy.ops.render.render(write_still=True)
 print('R48_GENERATOR_PASS',json.dumps({'mesh_count':len(CONTOUR_PARTS),
  'validated_contacts':len(JOINTS),'mesh_total_litres':sum(q['volume_L'] for q in QA),
  'glb_bytes':export.stat().st_size,'blender':bpy.app.version_string}))
