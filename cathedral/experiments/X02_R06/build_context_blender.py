"""Blender: assemble a review copy from current saved R05; add flat plan guides only."""
import bpy,json,hashlib,struct,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parent;O=R/'outputs';V=R/'previews'
source=R.parent/'F5ZP_X02_R05_BEARINGS_AND_ROOFS/outputs/F5ZP_X02_R05_EDITABLE.blend'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
original=[o for o in bpy.context.scene.objects if o.type=='MESH']
def signature(o):
 data=b''.join(struct.pack('<3f',*(o.matrix_world@v.co)) for v in o.data.vertices)
 data+=b''.join(struct.pack('<I',i) for p in o.data.polygons for i in p.vertices)
 return hashlib.sha256(data).hexdigest()
before={o.name:signature(o) for o in original};assert len(before)==151
for o in original:o.hide_set(False);o.hide_render=False
col=bpy.data.collections.new('R06_DISPLAY_ONLY_PLAN_GUIDES_NO_BUILDING_HEIGHTS');bpy.context.scene.collection.children.link(col)
colors={'court':(.42,.57,.28,1),'unmodeled_wing_footprint':(.48,.43,.35,1),'plan_outline':(.12,.16,.17,1),'route_reservation':(.18,.42,.66,1),'cathedral_reference_fragment':(.40,.30,.27,1),'unresolved':(.72,.07,.04,1)}
levels={'court':-.035,'unmodeled_wing_footprint':.005,'plan_outline':.025,'route_reservation':.045,'cathedral_reference_fragment':.065,'unresolved':.085}
mats={}
for k,color in colors.items():
 m=bpy.data.materials.new('R06_DIAGRAM_'+k);m.diffuse_color=color;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color;mats[k]=m

def rings(geom):
 if geom['type']=='Polygon':return [geom['coordinates']]
 if geom['type']=='MultiPolygon':return geom['coordinates']
 return []
def outline(name,coords,kind):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=.035;curve.bevel_resolution=1
 for ring in coords:
  sp=curve.splines.new('POLY');sp.points.add(len(ring)-1)
  for pt,(x,z) in zip(sp.points,ring):pt.co=(x,-z,levels[kind]+.015,1)
 obj=bpy.data.objects.new('DIAGRAM_'+name,curve);col.objects.link(obj);curve.materials.append(mats[kind]);obj['display_only']='Plan outline; no height or roof authority';return obj

def flat(name,ring,kind):
 vs=[Vector((x,-z,levels[kind])) for x,z in ring[:-1]]
 tris=tessellate_polygon([vs]);verts=[];faces=[]
 for tri in tris:
  a=[vs[v] if isinstance(v,int) else v for v in tri]
  if (a[1]-a[0]).cross(a[2]-a[0]).z<0:a.reverse()
  start=len(verts);verts.extend(tuple(v) for v in a);faces.append((start,start+1,start+2))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new('DIAGRAM_'+name,mesh);col.objects.link(obj);mesh.materials.append(mats[kind]);obj['display_only']='Flat source footprint; building height is UNMODELED'

diagram=json.loads((O/'CONTEXT_DIAGRAM_INPUT.json').read_text())
for f in diagram['features']:
 for i,coords in enumerate(rings(f['geometry'])):
  name=f['id']+'_'+str(i);kind=f['kind'];outline(name,coords,kind)
  if kind!='plan_outline':flat(name,coords[0],kind)
# Convert only added curves for portable GLB export; originals stay unchanged.
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:
 if o.type=='CURVE':o.select_set(True);bpy.context.view_layer.objects.active=o
if any(o.select_get() for o in col.objects):bpy.ops.object.convert(target='MESH')
after={o.name:signature(o) for o in original};assert before==after
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['R06_STATUS']='CONTEXT REVIEW; flat plan guides are not architectural height proposals'
scene['R05_SOURCE_SHA256']=source_hash
for o in scene.objects:
 if o.type=='LIGHT':o.hide_render=True
world=scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.88,.88,.85,1);world.node_tree.nodes['Background'].inputs[1].default_value=.8
bpy.ops.object.light_add(type='SUN',location=(0,0,50));sun=bpy.context.object;sun.rotation_euler=(.3,-.4,-.5);sun.data.energy=2.0;sun.data.angle=.15
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12
scene.render.resolution_x=1500;scene.render.resolution_y=1050;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=88
cameras=[]
for name,loc,target,scale in [('R06_CONTEXT_OBLIQUE',(-89,1,49),(-36,-37,2),78),('R06_EAST_RANGE_VIEW',(-62,-42,15),(-23,-38,5),39)]:
 bpy.ops.object.camera_add(location=loc);camera=bpy.context.object;camera.name=name;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=scale;cameras.append(camera)
scene.camera=cameras[0]
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active;space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.clip_end=1000;space.region_3d.view_location=Vector((-36,-37,2));space.region_3d.view_rotation=cameras[0].rotation_euler.to_quaternion();space.region_3d.view_distance=80;space.region_3d.view_perspective='ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'F5ZP_X02_R06_CONTEXT_REVIEW.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in original+list(col.objects):
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'F5ZP_X02_R06_CONTEXT_DIAGRAM.glb'),export_format='GLB',use_selection=True,export_extras=True)
assert before=={o.name:signature(o) for o in original}
qa={'source_saved_R05_blend_SHA256':source_hash,'original_meshes':len(original),'original_meshes_unchanged':before==after,'diagram_objects':len(col.objects),'source_file_bytes_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==source_hash,'Blender_version':bpy.app.version_string,'units':'metres in inherited precinct frame','limits':'Flat context guides have no architectural height authority; no full-cathedral 3D comparison.'}
(O/'R06_BLENDER_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
for camera in cameras:
 scene.camera=camera;scene.render.filepath=str(V/(camera.name+'.jpg'));bpy.ops.render.render(write_still=True)
print('R06_CONTEXT_COMPLETE '+json.dumps(qa),flush=True)
