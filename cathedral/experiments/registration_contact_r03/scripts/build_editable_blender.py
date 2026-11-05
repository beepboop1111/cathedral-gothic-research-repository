import bpy,json,zipfile,hashlib,sys
from pathlib import Path
from mathutils import Vector
O=Path('/home/christopher/Desktop/F5ZP_Registration_Contact_R03_EXPERIMENTAL');O.mkdir(exist_ok=True)
tmp=Path('/tmp/F5ZP_R03_RECOVERY')
handoff=Path('/home/christopher/Downloads/F5ZP_Chevet_Registration_Crossing_Junction_WORK_HANDOFF_R02.zip')
z=zipfile.ZipFile(handoff)
name=next(n for n in z.namelist() if n.endswith('SOURCE_Crossing_Full_Cell_R05_Package.zip'))
p=tmp/'SOURCE_R05.zip';p.write_bytes(z.read(name))
inner=zipfile.ZipFile(p);inner.extractall(tmp/'R05')
source=next((tmp/'R05').rglob('Crossing_Full_Cell_R05.blend'))
bpy.ops.wm.open_mainfile(filepath=str(source))
sc=bpy.context.scene
source_count=sum(o.type in {'MESH','CURVE'} and o.get('role')!='GUIDE' for o in sc.objects)
# Separate study only: remove diagram floors and source cameras from the copy.
for ob in list(sc.objects):
 if ob.type not in {'MESH','CURVE'} or ob.get('role')=='GUIDE':bpy.data.objects.remove(ob,do_unlink=True)
r05=bpy.data.collections.new('01_SELECTED_R05_UNCHANGED_GEOMETRY');sc.collection.children.link(r05)
for ob in list(sc.objects):
 for c in list(ob.users_collection):c.objects.unlink(ob)
 r05.objects.link(ob)
def load_objects(path,names,colname):
 co=bpy.data.collections.new(colname);sc.collection.children.link(co)
 with bpy.data.libraries.load(path,link=False) as (a,b):b.objects=[n for n in a.objects if n in names]
 for ob in b.objects:
  if ob:
   co.objects.link(ob);ob.hide_viewport=False;ob.hide_render=False;ob.hide_set(False)
   ob['R03_source_file']=path
 return co
gpath='/home/christopher/Desktop/Cathedral_F5ZP_G40_Working.blend'
gnames=['G40F__G40_CONTEXT_MINUS_G24_ORIGINAL','G40F__OPTION_C_G24_G25_REPLACEMENTS','G40M2_DERIVED_FULL_CHOIR_FIRST_FLOOR_X2360_TO_X10709_JOIN']
load_objects(gpath,gnames,'02_SAVED_G40_FRAGMENTS_NOT_COMPLETE_CATHEDRAL')
data=json.loads(__import__('gzip').decompress(__import__('base64').b64decode((tmp/'meshes.json.gz.b64').read_text())))
load_objects('/home/christopher/Desktop/newgen_F5ZN_A_CHEVET_STUDY_1to1.blend',[g['name'] for g in data['guides']],'03_SAVED_CHEVET_GUIDES_NOT_MASONRY')
sc.name='R03_REGISTRATION_AND_CONTACT_EXPERIMENT'
sc.unit_settings.system='NONE';sc.unit_settings.scale_length=1.
sc['R03_status']='EXPERIMENTAL ONLY, no promotion; R05 source retained'
sc['R03_axes']='X east, Y north, Z height; actual saved G40 principal object world coordinates; stale G40 global axis metadata rejected'
sc['R03_physical_m_per_unit']='UNRESOLVED; do not interpret native coordinate numbers as metres'
sc['R03_missing']='adjoining nave/choir/crossing piers; installed chevet wall/pier solids; F5ZL-C support schedule'
sc['R03_R05_source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
sc['R03_R05_source_objects']=source_count
notes=bpy.data.texts.new('READ_ME_R03')
notes.write('Native 1:1 project units. Physical SI coefficient unresolved. Selected R05 full cells preserved. G40 saved fragments do not include adjoining crossing piers/walls. Black/gray diagrams and QA are separate exports. No source library or generator overwritten.')
def camera(name,pos,target,scale):
 cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=scale;cd.clip_start=1;cd.clip_end=150000;return cam
aerial=camera('R03_CROSSING_AERIAL',(24000,-30000,29500),(0,0,8500),38000)
camera('R03_CROSSING_PLAN',(0,0,60000),(0,0,0),29000)
camera('R03_CHEVET_PLAN',(24500,0,60000),(24500,0,0),17000)
sc.camera=aerial
sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True
sc.world=bpy.data.worlds.new('R03 review world');sc.world.color=(.8,.8,.8)
sc.render.resolution_x=1200;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.clip_end=150000;area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.context.preferences.filepaths.save_version=0
out=O/'F5ZP_Registration_Contact_R03.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sc.render.filepath=str(O/'BLENDER_REVIEW.png');bpy.ops.render.render(write_still=True)
qa={'Blender_version':bpy.app.version_string,'R05_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'R05_source_objects_preserved':source_count,'saved_objects':len(sc.objects),'units_system':sc.unit_settings.system,'scale_length':sc.unit_settings.scale_length,'source_G40_sha256':hashlib.sha256(Path(gpath).read_bytes()).hexdigest(),'result':str(out),'result_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'rendered':True,'Exhibit_available':False}
(O/'BLENDER_QA.json').write_text(json.dumps(qa,indent=2));print('R03_BLEND_READY',json.dumps(qa),flush=True)
