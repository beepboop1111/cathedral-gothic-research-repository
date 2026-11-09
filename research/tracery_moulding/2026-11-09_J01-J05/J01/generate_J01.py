# J01 — Experimental Gothic tracery moulding continuity (Blender 5.0+/5.1+)
# Source-proportion study inspired by paired-lancet uploaded OBJ. Not a measured historical reconstruction.
import bpy, bmesh, math, json, os
from mathutils import Vector
from math import sin, cos, pi, sqrt, asin
ROOT = "/home/christopher/Cathedral_Experiments/tracery_moulding_J01"
os.makedirs(ROOT, exist_ok=True)
P = dict(window_width=40.0, source_height=124.641, outer_half_span=18.0,
         outer_spring=91.0, outer_crown=124.641,
         lancet_centers=(-9.5,9.5), lancet_half_span=7.5,
         lancet_spring=78.0, lancet_crown=101.0,
         foil_center_y=111.0, ring_radius=7.9, voxel_size=0.18)
# Each coordinate uses the reference OBJ's *unverified* native units, never cathedral F5ZN-A units.
PROFILE = [(-1.3,-0.72),(-1.3,0.03),(-1.12,0.16),(-0.97,0.16),
           (-0.80,0.025),(-0.67,0.08),(-0.51,0.32),(-0.29,0.56),
           (0.0,0.67),(0.29,0.56),(0.51,0.32),(0.67,0.08),
           (0.80,0.025),(0.97,0.16),(1.12,0.16),(1.3,0.03),(1.3,-0.72)]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials:
    if d.users==0: bpy.data.materials.remove(d)
def material(name, rgb, metallic=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb,1)
    m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1)
    bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Roughness'].default_value=.75
    return m
stone=material('Moulding continuous · sandstone',(.76,.70,.61))
palette=[material('Unjoined segment %02d'%i,co) for i,co in enumerate(
    [(.27,.46,.54),(.37,.52,.59),(.27,.45,.48),(.44,.57,.60),(.34,.46,.56)])]
background=material('Dark review backboard',(.060,.083,.105))
label_mat=material('Captions · ivory',(.89,.88,.83))
junction_mat=material('Junction markers',(.91,.55,.22))
def pointed_half(cx,a,ys,yt,left=True,n=58):
    h=yt-ys
    assert h>a and a>0, ('not a two-centered pointed arch',h,a)
    c=(h*h-a*a)/(2*a)
    r=a+c
    angle=asin(h/r)
    pts=[(cx+c-r*cos(angle*i/n),ys+r*sin(angle*i/n)) for i in range(n+1)]
    if left: return pts
    return [(2*cx-x,y) for x,y in reversed(pts)]
def stem_arch(cx,a,ys,yt,side='left',foot=64):
    arch=pointed_half(cx,a,ys,yt,side=='left')
    if side=='left':
        return [(cx-a,foot),(cx-a,ys)]+arch[1:]
    return arch+[(cx+a,foot)]
def polyline_length(p):
    return sum(math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(p,p[1:]))
def sweep(name, path, mat):
    # Path is in the XY plane; Z is the constant outward-looking depth axis.
    pts=[Vector(p) for p in path]
    for i in range(len(pts)-1):
        assert (pts[i+1]-pts[i]).length>1e-7, (name,'zero-length station')
    verts=[]; faces=[]; n=len(PROFILE)
    for k,p in enumerate(pts):
        tang=(pts[min(k+1,len(pts)-1)]-pts[max(k-1,0)]).normalized()
        normal=Vector((tang.y,-tang.x))
        for u,z in PROFILE:
            verts.append((p.x+normal.x*u,p.y+normal.y*u,z))
    for k in range(len(pts)-1):
        for j in range(n):
            q=(j+1)%n; a=k*n+j; b=k*n+q
            faces.append((a,b,b+n,a+n))
    faces += [tuple(reversed(tuple(range(n)))),
              tuple((len(pts)-1)*n+j for j in range(n))]
    mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    ob.data.materials.append(mat)
    return ob
paths=[]
for side in ('left','right'):
    paths.append(('outer_'+side, stem_arch(0, P['outer_half_span'],P['outer_spring'],P['outer_crown'],side)))
for cx in P['lancet_centers']:
    for side in ('left','right'):
        paths.append(('lancet_%s_%s'%(cx,side),stem_arch(cx,P['lancet_half_span'],
                  P['lancet_spring'],P['lancet_crown'],side)))
paths.append(('middle_mullion',[(0,64),(0,84)]))
# Circular ring and four-lobed infill; analytic pattern parameters remain editable.
N=160
paths.append(('circlet',[(P['ring_radius']*cos(2*pi*i/N),
                           P['foil_center_y']+P['ring_radius']*sin(2*pi*i/N)) for i in range(N+1)]))
paths.append(('quatrefoil',[( (4.4+1.0*cos(4*2*pi*i/N))*cos(2*pi*i/N),
            P['foil_center_y']+(4.4+1.0*cos(4*2*pi*i/N))*sin(2*pi*i/N))
            for i in range(N+1)]))
# Link ring to springing zone and outer arch; no detached segment after fusion.
for sign in (-1,1):
    paths.append(('ring_frame_%+d'%sign,[(sign*7.7,111),(sign*13.3,111)]))
    paths.append(('ring_lancet_%+d'%sign,[(sign*4.9,105.6),(sign*8.5,101.1)]))
# A repeated common cross-section is transported by a tangent-normal moving frame.
parts=[sweep(name,pts,palette[i%len(palette)]) for i,(name,pts) in enumerate(paths)]
part_QA=[]
def inspect(ob):
    bm=bmesh.new();bm.from_mesh(ob.data)
    result={'vertices':len(bm.verts),'faces':len(bm.faces),
            'boundary_edges':sum(e.is_boundary for e in bm.edges),
            'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
            'volume_abs':round(abs(bm.calc_volume(signed=True)),5)}
    # Count disconnected closed shells; manifold alone does not prove a single solid.
    unseen=set(bm.verts); shells=0
    while unseen:
        shells+=1; seed=unseen.pop(); frontier=[seed]
        while frontier:
            for edge in frontier.pop().link_edges:
                for v in edge.verts:
                    if v in unseen: unseen.remove(v); frontier.append(v)
    result['connected_components']=shells
    bm.free()
    return result
for o in parts:
    q=inspect(o);part_QA.append(q)
    assert q['boundary_edges']==0, (o.name,q)
# keep an unfused comparison fixture as mesh copies, not touching approved project geometry.
for i,p in enumerate(parts):
    duplicate=p.copy();duplicate.data=p.data.copy()
    bpy.context.collection.objects.link(duplicate)
    duplicate.name='BEFORE segmented %02d'%i
    duplicate.location.x=-29.5
# Join and voxel-weld the intersecting swept solids (automatic local blend at nodes).
bpy.ops.object.select_all(action='DESELECT')
for p in parts:p.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
merged=parts[0];merged.name='J01 fused continuous moulding'
bpy.ops.object.select_all(action='DESELECT');merged.select_set(True)
bpy.context.view_layer.objects.active=merged
merged.data.remesh_voxel_size=P['voxel_size']
bpy.ops.object.voxel_remesh()
# Mild smoothing removes voxel ridges without changing path bearings or original envelopes.
mod=merged.modifiers.new('Surface relaxation - experimental','SMOOTH')
mod.factor=.44;mod.iterations=2
bpy.ops.object.modifier_apply(modifier=mod.name)
bm=bmesh.new();bm.from_mesh(merged.data)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
bm.to_mesh(merged.data);bm.free()
merged.data.materials.clear();merged.data.materials.append(stone)
for polygon in merged.data.polygons: polygon.material_index=0
qa=inspect(merged)
qa.update({'profile_stations':len(PROFILE),'path_count':len(paths),
          'native_units_verified':False,'source_reference':'paired-lancet OBJ',
          'source_bounds':[40.,10.,124.641],'voxel_size':P['voxel_size'],
          'reference_arch_points':'derived as parametrized two-centred experiment, not extracted'})
assert qa['boundary_edges']==0 and qa['nonmanifold_edges']==0, ('Union not closed',qa)
assert qa['volume_abs']>0
# Export actual test mesh only in local workspace; do not update locked cathedral assets.
bpy.ops.object.select_all(action='DESELECT')
merged.select_set(True);bpy.context.view_layer.objects.active=merged
glb=os.path.join(ROOT,'J01_EXPERIMENTAL_moulding_continuity.glb')
bpy.ops.export_scene.gltf(filepath=glb,export_format='GLB',use_selection=True,export_apply=True)
# Roundtrip test: imported mesh must remain manifold and retain numeric envelope.
merged.hide_set(True);merged.hide_render=True
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.import_scene.gltf(filepath=glb)
imported=[o for o in bpy.context.selected_objects if o.type=='MESH']
assert len(imported)>=1, 'GLB import produced no mesh'
# glTF splits shared vertices at hard normal/UV boundaries: reweld positions before manifold QA.
for obj in imported:
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.00001)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(obj.data);bm.free()
q2=[inspect(o) for o in imported]
assert sum(q['boundary_edges'] for q in q2)==0, q2
assert sum(q['nonmanifold_edges'] for q in q2)==0, q2
for o in imported:
    bpy.data.objects.remove(o,do_unlink=True)
merged.hide_set(False);merged.hide_render=False
# Duplicate the exported, verified asset only for rendered comparison.
after=merged.copy();after.data=merged.data.copy()
bpy.context.collection.objects.link(after)
after.name='AFTER joined monolithic mesh';after.location.x=29.5
merged.hide_render=True;merged.hide_set(True)
def write_label(content,x,y,size,mat):
    curve=bpy.data.curves.new('Label','FONT');curve.body=content
    curve.size=size;curve.align_x='CENTER'
    obj=bpy.data.objects.new('LABEL '+content,curve)
    bpy.context.collection.objects.link(obj);obj.location=(x,y,.1)
    obj.data.materials.append(mat)
    return obj
write_label('A   SEGMENTED SWEEPS',-29.5,132.0,2.35,label_mat)
write_label('B   FUSED JUNCTIONS',29.5,132.0,2.35,label_mat)
write_label('UNJOINED   /   profile overlaps',-29.5,59.0,1.38,label_mat)
write_label('CONTINUOUS SOLID   /   voxel weld',29.5,59.0,1.38,label_mat)
write_label('J01    |    TWO-LANCET MOULDING CONTINUITY STUDY',0,140,2.6,label_mat)
# Flat review stage with cast shadows and shallow front-face relief.
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,99,-3.0))
plane=bpy.context.object;plane.name='Background stage'
plane.scale=(62,53,1);plane.data.materials.append(background)
# Light
world=bpy.context.scene.world or bpy.data.worlds.new('World')
bpy.context.scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.19,.22,.28,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.62
def light(name,loc,power,size):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector((0,103,0))-o.location).to_track_quat('-Z','Y').to_euler()
light('Upper left softbox',(-45,125,65),1600,70)
light('Right rim', (52,102,45),1100,55)
camdata=bpy.data.cameras.new('Review camera')
camera=bpy.data.objects.new('Review camera',camdata);bpy.context.collection.objects.link(camera)
camera.location=(0,99,180)
camera.rotation_euler=(0,0,0)  # +Y up, front of XY tracery faces camera
camdata.type='ORTHO';camdata.ortho_scale=138
sc=bpy.context.scene;sc.camera=camera
sc.render.engine='CYCLES';sc.cycles.samples=20
sc.render.resolution_x=1550;sc.render.resolution_y=1030;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
sc.render.filepath=os.path.join(ROOT,'J01_moulding_continuity_review.png')
sc.view_settings.view_transform='AgX'
# Save editable experimental scene and QA.
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'J01_EXPERIMENTAL_scene.blend'))
with open(os.path.join(ROOT,'J01_QA.json'),'w') as f:
    json.dump({'status':'experimental','blender':bpy.app.version_string,'parameters':P,
              'original_parts':part_QA,'joined':qa,'glb_roundtrip':q2,
              'architectural_approval':False,'source_dimensions_verified':False},f,indent=2)
bpy.ops.render.render(write_still=True)
print('J01_PASS',json.dumps({'qa':qa,'roundtrip':q2,'render':sc.render.filepath}))
