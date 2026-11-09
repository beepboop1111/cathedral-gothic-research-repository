"""R45 executable batch: test source-graded selected PNG and JSON sections,
build/reject/validate configurable branching, export a 6-stone GLB, render one preview.
No approved geometry and no prior checkpoint modified.
"""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path('/home/christopher/Cathedral_Research')
R=ROOT/'R45_native_5_1_compatibility'
sys.path.insert(0,str(R))
sys.path.insert(0,str(ROOT/'R43_profile_intake_and_review'))
from R43_profile_intake import load_section
bpy.ops.wm.read_factory_settings(use_empty=True)
import R45_engine as E
scene=bpy.context.scene
E.create_study_collection()
base={
 'arm_total_length_mm':480,'extension_length_mm':165,
 'base_z_mm':55,'stem_top_mm':460,'branch_z_mm':385,
 'rebate_width_mm':29,'rebate_depth_mm':28,'rebate_offset_mm':43,
 'rebate_face_y_mm':-17,'rebate_overrun_mm':15,
 'rebate_start_before_joint_mm':68,'evidence_class':'EXPERIMENTAL'
}
config_src=[
 ('R45_PNG_A42',42,R/'R45_profile_from_PNG_1.json','PNG_PROFILE'),
 ('R45_JSON_B35',35,ROOT/'R43_profile_intake_and_review/R43_profile_family_2.json','SELECTED_JSON_PROFILE'),
 ('R45_JSON_A50',50,ROOT/'R43_profile_intake_and_review/R43_profile_family_1.json','LEGACY_REGRESSION')]
results=[];mainmodels=[]
for name,angle,path,kind in config_src:
 prof,metadata=load_section(path)
 cfg=dict(base,branch_angle_deg=angle)
 o=E.build_stone_assembly(prof,metadata,cfg,name)
 assert len(o['objects'])==3 and len(o['contacts'])==2
 assert all(x['normal_dot_product']<-0.9999 for x in o['contacts'])
 assert all(x['face_area_error_mm2']<.25 for x in o['contacts'])
 assert o['setout']['joint_distance_mm']==315.
 assert all(x['nonmanifold_edges']==0 and x['connected_components']==1 for x in [o['y_mesh_QA']]+o['extension_mesh_QA'])
 expected=metadata['section_area_mm2']
 assert all(.70*expected<=x['face_area_mm2']<expected for x in o['contacts'])
 q={k:v for k,v in o.items() if k not in ('objects','joint_bearings')}
 q['name']=name;q['source_profile_kind']=kind
 results.append(q)
 if kind=='LEGACY_REGRESSION':
  reference=json.loads((ROOT/'R44_bearing_regression/R44_A50/R44_qa.json').read_text())
  assert abs(o['contacts'][0]['face_area_mm2']-reference['contacts'][0]['cap_area_mm2'])<.3
  for ob in o['objects']:bpy.data.objects.remove(ob,do_unlink=True)
 else:mainmodels.append((name,o))
# Negative input unit tests: reject malicious geometry and unsupported historical labels
prof,_=load_section(R/'R45_profile_from_PNG_1.json')
negative={}
invalid=[
 ('reject_zero_extension',dict(base,branch_angle_deg=42,extension_length_mm=0)),
 ('reject_joint_outside_bearings',dict(base,branch_angle_deg=42,extension_length_mm=240,arm_total_length_mm=380)),
 ('reject_75deg_branches',dict(base,branch_angle_deg=75)),
 ('reject_obscure_rebate',dict(base,branch_angle_deg=42,rebate_width_mm=0)),
 ('reject_stem_support_too_short',dict(base,branch_angle_deg=42,stem_top_mm=399)),
 ('reject_false_historical_approval',dict(base,branch_angle_deg=42,evidence_class='APPROVED')),
 ('reject_rebate_overrun_0',dict(base,branch_angle_deg=42,rebate_overrun_mm=0))]
for label,cfg in invalid:
 try:
  E.validate_setout(cfg,prof)
  negative[label]=False
 except (ValueError,TypeError):negative[label]=True
assert all(negative.values()),negative
assert len(mainmodels)==2
# Translate separate 1:1 geometric experimental models after construction/QA.
# Parent transform remains part of exported GLB; contact fits are tested in world coordinates.
positions={'R45_PNG_A42':-.48,'R45_JSON_B35':.48}
for name,o in mainmodels:
 for ob in o['objects']:
  ob.location.x=positions[name]
  ob['source_type']='R45 user-selectable synthetically generated input'
  ob['R45_stone_geometry']='EXPERIMENTAL'
# Export exactly six separate stones: assembled A42 and B35.
bpy.ops.object.select_all(action='DESELECT')
selected=[ob for name,o in mainmodels for ob in o['objects']]
for ob in selected:ob.select_set(True)
bpy.context.view_layer.objects.active=selected[0]
GLB=R/'R45_UNIFIED_BRANCHING_STONE_GENERATOR.glb'
bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',
 use_selection=True,export_apply=True,export_yup=True,export_extras=True)
assert GLB.stat().st_size>20000
# Save studio-only scene after stable GLB. No extra duplicate geometry in exported model.
bpy.ops.mesh.primitive_plane_add(size=3.5,location=(0,0,-.015))
floor=bpy.context.object
floor.name='R45_STUDIO_ONLY_FLOOR'
floor.data.materials.append(E.ground)
def light(name,xyz,energy,size):
 lamp=bpy.data.lights.new(name,'AREA');lamp.shape='DISK';lamp.energy=energy;lamp.size=size
 ob=bpy.data.objects.new(name,lamp);E.C.objects.link(ob)
 ob.location=xyz;ob.rotation_euler=(Vector((0,0,.42))-ob.location).to_track_quat('-Z','Y').to_euler()
light('R45_main_key',(-.7,-.9,1.32),54,.95)
light('R45_main_fill',(.6,.25,1.00),28,.75)
world=bpy.data.worlds.new('R45 neutral studio')
scene.world=world;world.use_nodes=True
world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.5,.53,.57,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.15
cam=bpy.data.cameras.new('R45_review_camera')
camera=bpy.data.objects.new('R45_review_camera',cam)
E.C.objects.link(camera)
camera.location=(1.05,-1.7,1.05)
aim=Vector((0,0,.42))
camera.rotation_euler=(aim-camera.location).to_track_quat('-Z','Y').to_euler()
cam.type='ORTHO';cam.ortho_scale=2.30
scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=True
scene.render.resolution_x=1800;scene.render.resolution_y=1080
scene.render.resolution_percentage=50
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(R/'R45_blender_review_render.png')
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=-.55
BLEND=R/'R45_UNIFIED_Experimental_Study.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.render.render(write_still=True)
assert (R/'R45_blender_review_render.png').stat().st_size>15000
data={'checkpoint':'R45',
 'status':'UNIFIED_EXPERIMENTAL_GENERATOR_VALIDATION',
 'blender':bpy.app.version_string,
 'generator':'R45_engine.py','selected_profile_input':'R45_png_profile_converter.py',
 'source_profile_cases':results,
 'built_model_count':3,'exported_model_count':2,'GLB_solid_count':6,
 'negative_tests':negative,
 'GLB_export':str(GLB),'BLEND_scene':str(BLEND),
 'historical_3D_joints_certified':False,
 'source_type':'SYNTHETIC user-selectable PNG and JSON; not medieval measured stone geometry',
 'profile_dimensions_explicitly_metric':True,
 'joint_algorithm':'joint_distance = arm_total_length - extension_length, limits enforced; no load-bearing design',
 'f5zp_and_pass6j_unmodified':True}
(R/'R45_native_build_QA.json').write_text(json.dumps(data,indent=2))
print('R45_BUILD_PASS',json.dumps({'models':[(d['name'],d['contacts']) for d in results],
    'GLB_solid_count':6,'negatives':negative,'version':bpy.app.version_string}))
