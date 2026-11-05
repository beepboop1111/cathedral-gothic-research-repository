"""Run with blender -b --factory-startup --python open_in_blender.py.
Imports the experimental GLB at metre scale, validates import and saves a new blend.
"""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
r=Path(__file__).resolve().parent;o=r/'outputs'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(o/'F5ZP_X02_R05_ROOF_AND_BEARING_STUDY.glb'))
objects=[x for x in bpy.context.scene.objects if x.type=='MESH']
qa=json.loads((o/'R05_QA.json').read_text());assert len(objects)==qa['metrics']['mesh_objects']
changes=[]
for obj in objects:
 if obj.data.validate(verbose=False):changes.append(obj.name)
 obj['status']='EXPERIMENTAL R05; structural sizing unverified'
assert not changes,changes
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bounds=[obj.matrix_world@Vector(corner) for obj in objects for corner in obj.bound_box]
lo=[min(v[i] for v in bounds) for i in range(3)];hi=[max(v[i] for v in bounds) for i in range(3)]
# Blender maps glTF X,Y,Z to X,-Z,Y: validate physical height and north/south extent.
assert 11<hi[2]<13 and lo[2]<0 and hi[0]-lo[0]>18 and hi[1]-lo[1]>30
scene['source_R04_SHA256']=qa['parent_R04_SHA256'];scene['architectural_status']='EXPERIMENTAL; not promoted'
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12
scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.world.color=(.65,.65,.65)
world=scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.85,.84,.80,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
bpy.ops.object.light_add(type='AREA',location=(-5,-18,35));light=bpy.context.object;light.data.energy=3500;light.data.shape='DISK';light.data.size=18
bpy.ops.object.light_add(type='SUN',location=(0,0,30));sun=bpy.context.object;sun.rotation_euler=(math.radians(25),math.radians(-25),math.radians(-20));sun.data.energy=2;sun.data.angle=.15
bpy.ops.object.camera_add(location=(10,3,31));cam=bpy.context.object;target=Vector((-22,-38,4));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=44;scene.camera=cam
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(o/'R05_BLENDER_PREVIEW.png')
bpy.ops.wm.save_as_mainfile(filepath=str(o/'F5ZP_X02_R05_EDITABLE.blend'),compress=True)
result={'Blender_version':bpy.app.version_string,'mesh_objects':len(objects),'mesh_validation_changes':changes,'bounds_native_Z_up_m':{'min':lo,'max':hi},'units':'metres','saved_blend':str(o/'F5ZP_X02_R05_EDITABLE.blend')}
(o/'BLENDER_IMPORT_QA.json').write_text(json.dumps(result,indent=2)+'\n')
print('R05_IMPORT_QA '+json.dumps(result),flush=True)
bpy.ops.render.render(write_still=True)
print('R05_RENDER_SAVED',flush=True)
