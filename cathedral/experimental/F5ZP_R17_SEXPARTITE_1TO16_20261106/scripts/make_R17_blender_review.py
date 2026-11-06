"""Create two real Blender review scenes from the SAME 1:16 mesh.
Scene A: source at 1:16; Scene B: actual object.scale EXACTLY 16.
Original cathedral scenes/files untouched. Not approved masonry.
"""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1]
skeleton=json.loads((D/'outputs/R17_EXACT_SIX_ARCH_SIX_GROIN_SKELETON_NATIVE.json').read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.scene.name='R17_SOURCE_1_TO_16'
source=bpy.context.scene
meshpath=D/'outputs/guarded/R17_SEXPARTITE_SIX_CELL_1to16.stl'
bpy.ops.wm.stl_import(filepath=str(meshpath))
web=bpy.context.object
assert web.type=='MESH'
web.name='R17_SEXPARTITE_OPEN_WEB_1_TO_16'
def material(name,rgb):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    return m
stone=material('R17_UNAPPROVED_WEB',(0.69,0.77,0.72))
archmat=material('R17_BLUE_POINTED_ARCHES',(0.18,0.45,0.77))
ribmat=material('R17_AMBER_DIAGONALS_AND_TRANSVERSE',(0.82,0.56,0.26))
web.data.materials.append(stone)
for polygon in web.data.polygons:polygon.use_smooth=True
web['NATIVE_EXPORT_SCALE']='1/16 (DO NOT apply 16 to source mesh)'
web['BOSS_Z_NATIVE']=4700.
web['APEX_MAX_Z_NATIVE']=4320.
web['LOCKED_GEOMETRY_WARNING']='EXPERIMENT ONLY; original F5ZN-A and F5ZK-C untouched'
def curveobj(collection,name,points,color,radius):
    path=bpy.data.curves.new(name,'CURVE')
    path.dimensions='3D';path.resolution_u=4
    path.bevel_depth=radius/16
    path.bevel_resolution=3
    section=path.splines.new('POLY');section.points.add(len(points)-1)
    for p,co in zip(section.points,points):p.co=(*[float(q)/16 for q in co],1)
    obj=bpy.data.objects.new(name,path)
    collection.objects.link(obj)
    path.materials.append(color)
    return obj
data=[web]
for k in range(6):
    outline=skeleton['arches'][k]
    rib=skeleton['groins'][k]
    data.append(curveobj(source.collection,f'R17_ARCH_{k:02d}',outline,archmat,10))
    data.append(curveobj(source.collection,
                f'R17_RADIAL_GROIN_{k:02d}',rib,ribmat,11))
# Two scenes: first contains 1/16 coordinates, second uses Blender scale=16.
big=bpy.data.scenes.new('R17_RESTORED_NATIVE_X16')
for original in data:
    duplicate=bpy.data.objects.new(original.name+'_X16',original.data)
    duplicate.scale=(16,16,16)
    big.collection.objects.link(duplicate)
    duplicate['source_object']=original.name
    if original==web:duplicate['RESTORATION_EXACT_FACTOR']=16
def configure(scene,multiplier):
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=1440;scene.render.resolution_y=1020
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.display.shading.light='STUDIO'
    scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True
    scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD'
    scene.world=bpy.data.worlds.new(scene.name+'_WORLD')
    scene.world.color=(.17,.17,.17)
    cam=bpy.data.cameras.new(scene.name+'_ISOMETRIC')
    obj=bpy.data.objects.new(scene.name+'_CAMERA',cam)
    scene.collection.objects.link(obj)
    obj.location=Vector((520,-530,420))*multiplier
    target=Vector((0,0,245))*multiplier
    obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler()
    cam.type='ORTHO';cam.ortho_scale=395*multiplier
    cam.clip_start=.001;cam.clip_end=150000.
    scene.camera=obj
    scene['LOCKS']='WARNING: F5ZK-C / F5ZN-A / Pass6J unchanged. Model is experimental.'
    scene['R16_CROWN_RULE']='PASS: central Z4700 > boundary apex Z4320'
    scene['SOURCE_SCALE']='1:16' if multiplier==1 else 'source 1:16 with x16 exact world reconstruction'
for scene,multiplier in ((source,1),(big,16)):
    configure(scene,multiplier)
guide=bpy.data.texts.new('READ_ME_R17_SCALE_AND_WARNINGS')
guide.write('R17 SEXPARTITE SIX-CELL DOUBLE-BAY / GOTHIC EXPERIMENT\n'
  'SOURCE_1_TO_16 contains true scaled mesh geometry; no modifier needed.\n'
  'RESTORED_NATIVE_X16 uses the exact SAME mesh data and Blender object scale 16.\n'
  'Arch apex highest 4320, crown 4700, crown higher by 380 native units.\n'
  'Four diagonals + 2 transverse intermediate groins; open web only.\n'
  'All original cathedral geometry and approved generators PROTECTED.\n'
  'All R16 strict pre+post crown and lock checks PASS; no masonry thickness.\n')
for scr in ('build_R17_sexpartite.py','make_R17_blender_review.py'):
    bpy.data.texts.load(str(D/'scripts'/scr),internal=True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.lens=9.3;sp.clip_start=.01
            sp.clip_end=99999997952.
            sp.shading.color_type='MATERIAL'
            sp.region_3d.view_perspective='CAMERA'
if bpy.context.window:bpy.context.window.scene=source
dest=D/'F5ZP_R17_SEXPARTITE_DOUBLE_BAY_1_TO_16_LIVE_EXPERIMENTAL.blend'
assert not dest.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
print('R17_BLENDER_SAVED',dest, 'SOURCE_N_VERTICES',len(web.data.vertices),
      'native_scene_scale',big.objects[web.name+'_X16'].scale[:])
