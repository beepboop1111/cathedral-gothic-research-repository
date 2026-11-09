"""R50 direct reuse of protected Brandon R03 tracing GLB.
Produces a new explicitly hypothetical metric *proxy* based on source pixel rings,
not an authenticated 1:1 reconstruction. 1 Blender unit = 1 m for study.
Reuses existing watertight M04 mesh; no modelling of new historical joint cuts.
"""
from pathlib import Path
import bpy,bmesh,json,math,hashlib
from mathutils import Vector,Matrix
R=Path('/home/christopher/Cathedral_Research/R50_source_graded_tracery')
source=Path('/home/christopher/Downloads/downlods/BRANDON_M04_R03_EXPERIMENTAL_REMOTE.glb')
evidence=json.loads((R/'R50_source_measurements.json').read_text())
assert source.is_file()
oldhash=hashlib.sha256(source.read_bytes()).hexdigest()
# Every dimension explicit and marked non-historical.
assumed_width_m=2.4
assumed_depth_m=.18
source_width_px=evidence['outline_span_pixels']
source_extruded_depth=31.5
unit_per_pixel=assumed_width_m/source_width_px
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(objects)==1,('R03 expected exactly one traced piece',len(objects))
o=objects[0]
raw_positions=[o.matrix_world @ v.co for v in o.data.vertices]
mins=[min(float(v[i]) for v in raw_positions) for i in range(3)]
maxs=[max(float(v[i]) for v in raw_positions) for i in range(3)]
expected_bbox=[[14,-31.5,6],[636,0,499]]
for i in range(3):
 assert abs(mins[i]-expected_bbox[0][i])<.02 and abs(maxs[i]-expected_bbox[1][i])<.02,('IMPORT_ORIGINAL_BOUNDS_UNEXPECTED',i,mins,maxs)
o.matrix_world.identity()
# Direct scaled coordinate relation; no changes to the pre-existing source.
for v,p in zip(o.data.vertices,raw_positions):
 x=(p.x-325)*unit_per_pixel
 y=(p.y+31.5)*assumed_depth_m/source_extruded_depth - assumed_depth_m/2
 z=(499-p.z)*unit_per_pixel
 v.co=Vector((x,y,z))
o.data.update()
o.name='R50_BRANDON_M04_R03_METRIC_PROXY_NOT_HISTORIC'
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1.0
C=bpy.data.collections.new('R50_RESEARCH_EXPERIMENTAL_NO_CATHEdRAL_APPROVAL')
bpy.context.scene.collection.children.link(C)
for c in list(o.users_collection):c.objects.unlink(o)
C.objects.link(o)
bm=bmesh.new();bm.from_mesh(o.data)
raw=len(bm.verts)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
if bm.calc_volume(signed=True)<0:
 bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
nonman=sum(not e.is_manifold for e in bm.edges)
vol=bm.calc_volume(signed=True)
euler=len(bm.verts)-len(bm.edges)+len(bm.faces)
vnum=len(bm.verts)
face_count=len(bm.faces)
# source has one connected solid, three through openings => genus 3.
assert nonman==0 and vol>0 and euler==-4
# All 3D vertices should still match a source tracing boundary in X/Z.
rings=json.loads(Path(evidence['source_file']).read_text())['rings']
ref={(round(float(x),3),round(float(y),3)) for loop in rings for x,y in loop}
mapped={(round(float(v.co.x/unit_per_pixel+325),3),round(float(499-v.co.z/unit_per_pixel),3)) for v in bm.verts}
maxdelta=max(min(math.hypot(x-a,y-b) for a,b in ref) for x,y in mapped)
assert maxdelta<.015,('TRACING_2D_PROFILE_DRIFT',maxdelta)
assert len(mapped)==len(ref),('TRACING_VERTEX_COUNT_DIFFERENCE',len(mapped),len(ref))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(o.data);bm.free();o.data.update()
phys_expected=evidence['stone_face_area_in_source_px2']*unit_per_pixel**2*assumed_depth_m
assert abs(vol-phys_expected)<5e-7,('MESH_VOLUME_NOT_EXPECTED_AREA_TIMES_DEPTH',vol,phys_expected)
o['evidence_grade']='M04_R03_PIXEL_TRACE_ONLY'
o['historic_original_scan_registered']=False
o['scale_calibrated_from_historic_source']=False
o['assumed_display_width_mm']=2400.
o['assumed_display_depth_mm']=180.
o['historical_stone_joints']='NOT IDENTIFIED'
o['source_extrusion_height_31p5_is_unscaled']='TRUE'
o['user_arch_rib_moulding_profiles_used']=False
o['source_contours_sha256']=evidence['source_SHA256']
def material(name,c,roughness=.82):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=(*c,1)
 bs.inputs['Roughness'].default_value=roughness
 return m
m=material('R50_neutral_limestone_not_authenticated',(.58,.57,.53))
o.data.materials.clear();o.data.materials.append(m)
# Export ONLY the tested study proxy before introducing camera/studio.
bpy.ops.object.select_all(action='DESELECT')
o.select_set(True)
bpy.context.view_layer.objects.active=o
glb=R/'R50_Brandon_R03_Hypothetical_Metric_Proxy.glb'
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True)
assert glb.is_file() and glb.stat().st_size>10000
o.select_set(False)
# Render only; no modifications to tracing shape.
scene=bpy.context.scene
floor_mat=material('R50_studio',(.14,.17,.19))
bpy.ops.mesh.primitive_plane_add(size=5,location=(0,0,-.018))
floor=bpy.context.object
floor.name='R50_studio_only_floor'
floor.data.materials.append(floor_mat)
def light(name,pos,energy,size):
 b=bpy.data.lights.new(name,'AREA')
 b.shape='DISK';b.energy=energy;b.size=size
 ob=bpy.data.objects.new(name,b)
 C.objects.link(ob)
 ob.location=pos
 ob.rotation_euler=(Vector((0,0,.92))-ob.location).to_track_quat('-Z','Y').to_euler()
light('R50_key',(-1.6,-1.8,3.9),120,2.2)
light('R50_fill',(2.4,.9,2.3),85,1.8)
world=bpy.data.worlds.new('R50_world')
scene.world=world;world.use_nodes=True
world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.57,.6,.62,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.20
camdata=bpy.data.cameras.new('R50_orthographic')
cam=bpy.data.objects.new('R50_orthographic',camdata)
C.objects.link(cam)
cam.location=(1.95,-4.25,2.24)
aim=Vector((0,0,.98))
cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO';camdata.ortho_scale=3.4
scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=28
scene.cycles.use_denoising=True
scene.render.resolution_x=1520;scene.render.resolution_y=1080
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(R/'R50_Blender_Render.png')
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=-.3
bpy.ops.wm.save_as_mainfile(filepath=str(R/'R50_Research_Only_Study.blend'))
bpy.ops.render.render(write_still=True)
assert Path(scene.render.filepath).is_file()
report={'pass':'R50','classification':'SOURCE-GRADED EXPERIMENTAL R03 TRACED GEOMETRY ONLY',
 'Blender':bpy.app.version_string,
 'physical_units':'metres; width and depth are independent assumptions',
 'source_glb_unmodified_sha256':oldhash,
 'source_R03_json_sha256':evidence['source_SHA256'],
 'user_profile_source_applied':False,
 'mesh_count':1,'vertex_count':vnum,'faces':face_count,
 'nonmanifold_edges':nonman,'Euler_characteristic':euler,'through_holes':3,
 'source_pixel_span_width':source_width_px,
 'source_pixel_span_height':evidence['outline_height_pixels'],
 'max_inverse_projection_to_R03_source_vertex_error_px':maxdelta,
 'provisional_width_mm':2400.,
 'provisional_depth_mm':180.,
 'provisional_height_mm':evidence['outline_height_pixels']*unit_per_pixel*1000,
 'volume_litres':vol*1000,'area_times_depth_volume_litres':phys_expected*1000,
 'historical_springing_and_jamb_bearings':'NOT VERIFIED',
 'historical_masonry_joint_beds':'NONE MEASURED',
 'original_reference_image_verified':False,
 'GLB':str(glb),'render':scene.render.filepath,
 'cathedral_or_R03_baseline_modified':False}
(R/'R50_Blender_geometry_QA.json').write_text(json.dumps(report,indent=2))
print('R50_BLENDER_GEOMETRY_PASS',json.dumps({'Blender':bpy.app.version_string,
 'watertight':True,'through_holes':3,'vertices':vnum,
 'volume_litres':round(vol*1000,5),
 'mesh_projection_error_px':round(maxdelta,7),
 'scale_status':'HYPOTHETICAL WIDTH AND DEPTH'}))
