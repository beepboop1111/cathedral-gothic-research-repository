"""R17 V2 Blender review: complete R10–R14-style Gothic surface.
All Blender geometry is 1:16; no full-scale geometry scene.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.name='R17_V2_FULL_GOTHIC_SEXPARTITE_1_TO_16'
model=D/'outputs/guarded/R17_V2_R10_R14_FULL_SEXPARTITE_1to16.stl'
bpy.ops.wm.stl_import(filepath=str(model))
web=bpy.context.object
web.name='R17_V2_HERMITE_GOTHIC_OPEN_INTRADOS_1to16'
assert web.type=='MESH'
assert web.scale[:]==(1.,1.,1.)
def mat(name,rgba):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgba,1)
    return m
stone=mat('R17_V2_SCULPTED_WEB_UNAPPROVED',(0.73,0.80,0.77))
blue=mat('R17_V2_POINTED_BOUNDARY_ARCHES',(0.22,0.49,0.80))
gold=mat('R17_V2_LOCKED_RIB_CENTERLINES',(0.91,0.65,0.31))
violet=mat('R17_V2_ADJUSTABLE_CUBIC_HERMITE_MERIDIANS',(0.61,0.31,0.69))
web.data.materials.append(stone)
for face in web.data.polygons:face.use_smooth=True
web['SCALE']='TRUE GEOMETRIC 1:16'
web['ARCH_HIGHEST_Z_NATIVE']=4320.
web['CROWN_Z_NATIVE']=4700.
web['ARCH_GROIN_MODIFICATIONS']='NONE; V1 skeleton intact'
web['LOCKED_GEOMETRY_WARNING']='DO NOT MODIFY F5ZK-C F5ZN-A Pass6J or approved generators'
skeleton=json.loads((D/'outputs/R17_V2_MATCHED_SKELETON_NATIVE.json').read_text())
def curve(name,path,radius,color):
    data=bpy.data.curves.new(name,'CURVE')
    data.dimensions='3D'
    data.bevel_depth=radius/16.
    data.bevel_resolution=4
    line=data.splines.new('POLY')
    line.points.add(len(path)-1)
    for p,pt in zip(line.points,path):p.co=(*[float(q)/16 for q in pt],1.)
    ob=bpy.data.objects.new(name,data)
    scene.collection.objects.link(ob)
    data.materials.append(color)
    ob['GEOMETRY_SCALE']='1:16'
    return ob
for k in range(6):
    curve(f'R17_V2_BOUNDARY_ARCH_{k:02d}',skeleton['arches'][k],9.,blue)
    curve(f'R17_V2_GROIN_{k:02d}',skeleton['groins'][k],11.,gold)
    import numpy as np
    coords=np.loadtxt(D/'outputs'/f'R17_V2_MERIDIAN_{k:02d}_NATIVE_REFERENCED.csv',delimiter=',',skiprows=1).tolist()
    c=curve(f'R17_V2_HERMITE_MERIDIAN_{k:02d}',coords,5.5,violet)
    c.hide_render=True
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1440;scene.render.resolution_y=1020
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
camdata=bpy.data.cameras.new('R17_V2_1to16_ISOMETRIC')
cam=bpy.data.objects.new('R17_V2_1to16_ISOMETRIC_CAMERA',camdata)
scene.collection.objects.link(cam)
cam.location=(490,-520,402)
target=Vector((0,0,248))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO';camdata.ortho_scale=380.
camdata.clip_start=.01;camdata.clip_end=100000.
scene.camera=cam
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.lens=9.3
            space.clip_start=.01
            space.clip_end=99999997952.
            space.shading.color_type='MATERIAL'
            space.region_3d.view_perspective='CAMERA'
scene['SCALE']='1:16 source mesh and all rib and meridian curves'
scene['R10_R14_REUSE']='Two-piece cubic Hermite curves, six triangular Gothic web surfaces; R14 raised web interior; two arch families'
scene['CROWN_RULE']='PASS: Boss4700 > highest pointed arch apex4320 (native), +380'
scene['LOCKED_GEOMETRY_WARNING']='EXPERIMENTAL ONLY; F5ZN-A, F5ZK-C, Pass6J, generators unchanged'
scene['MASONRY']='OPEN INTRADOS ONLY; cap and structural validation unresolved'
txt=bpy.data.texts.new('READ_ME_R17_V2_1to16_LOCKS_AND_CONTROLS')
txt.write('R17 V2 SEXPartite six-cell Gothic vault, 1:16 ALL objects.\n'
  'R10-R14 methods adapted to new independent sexpartite scaffold.\n'
  'V1 original pointed perimeter arches and radial groin paths unchanged.\n'
  'Six cubic Hermite apex-to-crown meridians (purple) control web shape.\n'
  'Interior sin(pi*t)^2 blending respects the groin/arch skeleton.\n'
  'WARNING: protected cathedral geometry and authoritative generators untouched.\n'
  'Native arch apex 4320, boss 4700, +380. Not approved masonry.\n')
for fn in ('build_R17_V2_full_surface.py','make_R17_V2_blender.py'):
    bpy.data.texts.load(str(D/'scripts'/fn),internal=True)
dest=D/'F5ZP_R17_V2_FULL_R10_R14_GOTHIC_SEXPARTITE_1to16_LIVE_EXPERIMENTAL.blend'
assert not dest.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
print('R17_V2_BLENDER_1to16_SAVED',str(dest),
      'verts',len(web.data.vertices),'scenes',list(bpy.data.scenes.keys()),
      'mesh_scale',tuple(web.scale))
