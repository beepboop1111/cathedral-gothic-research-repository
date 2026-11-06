# R14 independent Blender review. Protected R13 is opened READ-ONLY,
# and NEW R14 .blend receives only one experimental open-intrados shell,
# a Type B red line and additional cameras. No approved geometry replaced.
import bpy,math,pathlib,json,hashlib,numpy as np
from mathutils import Vector
D=pathlib.Path(__file__).resolve().parents[1]
C=json.loads((D/'configs/R14_TWO_TYPES_REDLINE.json').read_text())
Q=json.loads((D/'qa/R14_APSE_ALL_SIX_WEB_TYPES_GEOMETRY_QA.json').read_text())
R13=pathlib.Path(C['source_R13_directory'])
source=R13/'F5ZP_R13_FIVE_MATCHING_TYPE_A_WEBS_UNIQUE_TYPE_B_PENDING_LIVE_EXPERIMENTAL.blend'
assert pathlib.Path(bpy.data.filepath).resolve()==source.resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest()==C['source_R13_blend_sha256']
assert Q['fixed_skeleton_plan_errors']['all_six_groins']==0
assert Q['Type_B_cap_clearance_whole_web_native']>0
previous={o.name:(len(o.data.vertices),len(o.data.polygons))
           for o in bpy.data.objects if o.type=='MESH'}
source_scene=bpy.data.scenes.get('Scene')
assert source_scene
oldweb=bpy.data.objects['R13_TYPE_A_00_TO_04_USER_ACCEPTED_WEB_TYPE_B_05_UNMODIFIED']
arch=[bpy.data.objects['R07_APSE_EXTERIOR_POINTED_ARCH_'+str(i)]
       for i in range(5)]
arch.append(bpy.data.objects['V4_SKELETON_BAY2_EAST_POINTED_BOUNDARY'])
groins=[bpy.data.objects['R07_APSE_INDEPENDENT_GROIN_'+str(i)]
       for i in range(6)]
five_A=[bpy.data.objects['R13_MERIDIAN_'+str(i)+'_A_APPROVED_SHAPE']
        for i in range(5)]
B_old=bpy.data.objects['R13_MERIDIAN_5_B_OLD_REFERENCE']
assert len(arch)==6 and len(groins)==6 and len(five_A)==5
newcol=bpy.data.collections.new('R14_TWO_USER_DRAWN_WEB_TYPES__EXPERIMENTAL')
source_scene.collection.children.link(newcol)
newcol.color_tag='COLOR_05'
def make_mat(name,color):
    mat=bpy.data.materials.get(name)
    if not mat:mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1)
    return mat
stone=make_mat('R14_NEW_TYPE_A_AND_TYPE_B_LIMESTONE',(0.66,0.79,0.70))
red=make_mat('R14_TYPE_B_USER_RED_MERIDIAN',(0.91,0.16,0.17))
gray=make_mat('R14_OLD_R13_TYPE_B_COMPARE_GRAY',(0.47,0.48,0.55))
capmat=make_mat('R14_CAP_Z4341_ORANGE_WARNING',(0.91,0.51,0.24))
stl=D/'outputs'/Q['source_STL_1to16']
assert hashlib.sha256(stl.read_bytes()).hexdigest()==Q['STL_SHA256']
bpy.ops.wm.stl_import(filepath=str(stl))
selected=list(bpy.context.selected_objects)
assert len(selected)==1
web=selected[0]
web.name='R14_APSE_FIVE_TYPE_A_ONE_RED_TYPE_B_OPEN_INTRADOS_1to1'
for col in tuple(web.users_collection):col.objects.unlink(web)
newcol.objects.link(web)
web.scale=(16,16,16)
web.data.materials.append(stone)
for face in web.data.polygons:face.use_smooth=True
web['TYPE_A_CURVES']='00..04 accepted user sector02 silhouette, unchanged'
web['TYPE_B_CURVE']='05 independent user redline C1 cubic Hermite'
web['ALL_GROINS_AND_POINTED_ARCHES_FIXED']=True
web['BOSS_Z']=4296
web['HAUNCH_CAP_UNRESOLVED_FOR_TYPE_A']=True
web['TYPE_B_CAP_CLEARANCE_NATIVE']=Q['Type_B_cap_clearance_whole_web_native']
web['OPEN_SURFACE_ONLY']='No roof closure until thickness/cap resolved'
def make_line(name,points,material,radius=5):
    cu=bpy.data.curves.new(name+'_PATH','CURVE')
    cu.dimensions='3D'
    cu.resolution_u=3
    cu.bevel_depth=radius
    cu.bevel_resolution=3
    sp=cu.splines.new('POLY')
    sp.points.add(len(points)-1)
    for q,xyz in zip(sp.points,points):q.co=(*map(float,xyz),1)
    obj=bpy.data.objects.new(name,cu)
    newcol.objects.link(obj)
    cu.materials.append(material)
    return obj
points=np.loadtxt(D/'outputs'/Q['TypeB_meridian_csv'],delimiter=',',skiprows=1)
assert points.shape==(257,3)
B_red=make_line('R14_NEW_TYPE_B_SECTOR05_USER_RED_DRAWN_HERMITE',points,red,7)
B_red['MERIDIAN_PEAK_Z']=Q['Type_B_peak_Z']
B_red['IMAGE_FIT_RMS_NATIVE']=C['fit_RMS_native']
B_red['EXACT_FIXED_ENDPOINTS_Z']=4296
cap=make_line('R14_REFERENCE_PROVISIONAL_Z4341_CAP_SECTION',
              [(33400,0,4341),(33850,0,4341)],capmat,3)
for name,counts in previous.items():
    assert counts==(len(bpy.data.objects[name].data.vertices),
                    len(bpy.data.objects[name].data.polygons)),name

# Identical review cameras for before/after, and a dedicated transverse
# 2D elevation showing drawn red peak vs provisional cap.
scenes={
 'R14_ALL_SIX_WEBS_TWO_TYPES':('whole',web,True,True),
 'R14_ALL_SIX_WEBS_CLEAN_INTRADOS':('whole',web,False,False),
 'R14_TYPE_B_BEFORE_R13_REFERENCE':('entrance',oldweb,False,False),
 'R14_TYPE_B_AFTER_USER_RED':('entrance',web,True,False),
 'R14_TYPE_B_SKELETON_ONLY':('entrance',None,True,False),
 'R14_TYPE_B_SECTION_RED_VS_CAP':('section',None,True,True),
 'R14_TYPE_A_ACCEPTED_AXIAL_VIEW':('axial',web,True,False),
 'R14_INSIDE_APSE_UNDERSIDE':('inside',web,True,False),
}
poses={
 'whole':((39300,-7400,3450),(33850,0,3890),8000),
 'entrance':((30400,-4400,3340),(33700,0,4030),6300),
 'axial':((38900,-3900,3750),(34200,0,4180),5000),
 'inside':((33700,-1600,3100),(33900,0,4200),3300),
 'section':((33625,-2700,4380),(33625,0,4380),880),
}
for label,(camera,subject,showB,showCap) in scenes.items():
    scene=bpy.data.scenes.new(label)
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=1580
    scene.render.resolution_y=1060
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.display.shading.light='STUDIO'
    scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_cavity=True
    scene.display.shading.cavity_type='BOTH'
    scene.display.shading.show_shadows=True
    scene.display.shading.background_type='VIEWPORT'
    scene.display.shading.background_color=(.77,.79,.8)
    coll=bpy.data.collections.new('R14_SCENE_ONLY_'+label)
    scene.collection.children.link(coll)
    if camera=='section':
        objs=[B_old,B_red,cap]
    else:
        objs=[*arch,*groins,*five_A]
        if subject:objs.append(subject)
        if showB:objs.append(B_red if subject!=oldweb else B_old)
        if showCap:objs.append(cap)
    for o in objs:coll.objects.link(o)
    camdat=bpy.data.cameras.new(label+'_ORTHOGRAPHIC')
    cam=bpy.data.objects.new(label+'_CAMERA',camdat)
    coll.objects.link(cam)
    eye,target,scale=poses[camera]
    cam.location=Vector(eye)
    if camera=='section':
        cam.rotation_euler=(math.pi/2,0,0) # world X across; Z up
    else:
        cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    camdat.type='ORTHO'
    camdat.ortho_scale=scale
    camdat.clip_start=1
    camdat.clip_end=120000
    scene.camera=cam
    scene['ARCHITECTURAL_STATUS']='R14 experimental 2 type web profiles; roof and structural approval pending'
    scene['SECTOR05_PEAK_Z']=Q['Type_B_peak_Z']
    scene['ALL_BOSSES_Z']=4296
    scene['NEW_TYPE_B_CAP_CLEARANCE_NATIVE']=Q['Type_B_cap_clearance_whole_web_native']
    scene['TYPE_A_CAP_CONFLICT_NATIVE']=Q['Type_A_cap_conflict_still_native']
    scene['ALL_ORIGINAL_ARCH_GROIN_PLAN_BEARINGS_UNCHANGED']=True
guide=bpy.data.texts.new('R14_READ_ME_TWO_USER_REDLINE_WEB_TYPES')
guide.write('F5ZP R14 — ALL SIX APSE WEBS USE ONE OF TWO RED DRAWINGS.\n'
    'Type A sectors 00,01,02,03,04: unchanged accepted R12B sector02 curve.\n'
    'Type B sector05: NEW USER RED LINE, fit RMS 0.590 native units.\n'
    'Type B peaks at Z4337.135 and its whole web is below Z4341 cap by 3.865.\n'
    'Type A remains higher than old Z4341 cap by 29.34 native units.\n'
    'GLOBAL SIX-SECTOR UNDERFACE IS OPEN, NOT STRUCTURALLY CLOSED MASONRY.\n'
    'Original arches, diagonal groins, floor plan and all Z4296 bosses are FIXED.\n'
    'Use R14_TYPE_B_BEFORE_R13_REFERENCE and R14_TYPE_B_AFTER_USER_RED\n'
    'for an identical-camera before/after of unique entrance connection.\n'
    'Use R14_TYPE_B_SECTION_RED_VS_CAP for the registered 2D guide profile.\n'
    'R14_ALL_SIX_WEBS_CLEAN_INTRADOS hides control guides.\n')
for script in ['build_R14_two_user_drawn_web_types.py',
               'build_R14_blender_live_comparison.py']:
    block=bpy.data.texts.load(str(D/'scripts'/script),internal=True)
    block.name='R14_SCRIPT_'+script
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.lens=9.3
            space.clip_start=.01
            space.clip_end=99999997952.
            space.shading.color_type='MATERIAL'
            space.region_3d.view_perspective='CAMERA'
bpy.context.window.scene=bpy.data.scenes['R14_ALL_SIX_WEBS_TWO_TYPES']
save=D/'F5ZP_R14_ALL_SIX_APSE_WEBS_TWO_USER_DRAWN_TYPES_LIVE_EXPERIMENTAL.blend'
assert not save.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(save),compress=True)
(D/'qa/R14_BLENDER_SOURCE_PROTECTION_AND_SCENES_QA.json').write_text(
    json.dumps({'status':'R14_SAVED_INDEPENDENT_BLENDER_COMPARISON',
        'blender_file':str(save),'scenes':list(scenes),
        'previous_R13_SHA256_preserved':C['source_R13_blend_sha256'],
        'original_mesh_vertex_and_faces_unchanged':True,
        'new_meridian_count':1,'new_open_intrados_count':1,
        'Type_A_old_meridians_reused':5,'Type_B_accepted_user_stroke_fitted':True,
        'Z4296_all_bosses_fixed':True,'persistent_9.3mm_0.01m_to_99999997952m_view':True,
        'source_blend_ever_overwritten':False},indent=2))
print('R14_NEW_LIVE_BLEND_SAVED',save,'scene_count',len(scenes))

[executed on device: MR.COMPUTER (c5066a3f-7c79-446e-8649-efbb75d9e7d4)]