import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
folder=Path('/home/christopher/Desktop/sketch2stl/_EXPERIMENTS/STLEU_FIG80_R03')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(folder/'StLeu_R03_PROFILED_UPRIGHT.stl'))
obj=bpy.context.object
obj.name='ST LEU Fig 80 | R03 profiled window | experimental'
obj.data.name='Source-derived analytic contours, integrated profile'
obj['MODEL_STATUS']='EXPERIMENTAL_NOT_APPROVED'
obj['SOURCE']='St Leu d Esserent Fig. 80 engraving'
obj['SCALE']='image-pixel units only, not calibrated'
obj['RIGHT_SIDE']='mirrored candidate, not independently traced'
obj['MOULDING']='provisional, not historic section'
mat=bpy.data.materials.new('Limestone | provisional display')
mat.diffuse_color=(0.67,0.64,0.56,1.0)
mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF')
if bs:
    bs.inputs['Base Color'].default_value=(0.68,0.65,0.57,1)
    bs.inputs['Roughness'].default_value=0.86
obj.data.materials.clear()
obj.data.materials.append(mat)
# optional plain comparison, hidden by default
bpy.ops.wm.stl_import(filepath=str(folder/'StLeu_R03_PLAIN_UPRIGHT.stl'))
plain=bpy.context.object
plain.name='Comparison | R03 plain (hidden)'
plain.hide_set(True)
plain.hide_render=True
plain['MODEL_STATUS']='EXPERIMENTAL'
# keep profiled selected
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active=obj
bpy.context.view_layer.update()
bounds=[obj.matrix_world@Vector(p) for p in obj.bound_box]
mn=Vector([min(v[i] for v in bounds) for i in range(3)])
mx=Vector([max(v[i] for v in bounds) for i in range(3)])
center=(mn+mx)*.5
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active
            sp.region_3d.view_perspective='ORTHO'
            sp.region_3d.view_rotation=Quaternion((1,0,0),math.pi/2)
            sp.region_3d.view_location=center
            sp.region_3d.view_distance=float(mx.z-mn.z)*1.55
            sp.overlay.show_floor=False
            sp.overlay.show_axis_x=False
            sp.overlay.show_axis_y=False
            sp.shading.type='SOLID'
# camera for simple reference rendering
camera_data=bpy.data.cameras.new('Front orthographic camera')
cam=bpy.data.objects.new('Front orthographic camera',camera_data)
bpy.context.collection.objects.link(cam)
cam.location=(float(center.x),float(mn.y)-1000.,float(center.z))
aim=center-cam.location
cam.rotation_euler=aim.to_track_quat('-Z','Y').to_euler()
camera_data.type='ORTHO'
camera_data.clip_end=5000
camera_data.ortho_scale=float(mx.z-mn.z)*1.17
bpy.context.scene.camera=cam
# simple studio lights
light_data=bpy.data.lights.new('Softbox left','AREA')
light=bpy.data.objects.new('Softbox left',light_data)
bpy.context.collection.objects.link(light)
light.location=(float(center.x)-300,float(mn.y)-500,float(center.z)+150)
light_data.energy=140000
light_data.shape='DISK'
light_data.size=700
light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
world=bpy.context.scene.world
world.color=(0.8,0.8,0.8)
bpy.context.scene.render.engine='BLENDER_EEVEE'
bpy.context.scene.render.resolution_x=780
bpy.context.scene.render.resolution_y=1280
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.render.image_settings.file_format='PNG'
bpy.context.scene.render.filepath=str(folder/'StLeu_R03_blender_front.png')
bpy.context.scene.render.film_transparent=False
bpy.context.scene.unit_settings.system='NONE'
note=bpy.data.texts.new('READ_ME_FIRST__EXPERIMENTAL')
note.write('ST LEU FIG 80 - EXPERIMENTAL R03\nSource coordinates are pixels, not architectural units.\nFoil and arch contours use R01/R02 candidates.\n3D profile not measured from the historical source.\nDo not promote to approved cathedral baseline.\nOriginal reference plates and generators untouched.\n')
dest=folder/'StLeu_Fig80_R03_UPRIGHT_REVIEW.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
print('BLEND_SAVED',str(dest), 'triangles',len(obj.data.polygons),'bounds',tuple(mn),tuple(mx),flush=True)
bpy.ops.render.render(write_still=True)
print('RENDER_SAVED',str(folder/'StLeu_R03_blender_front.png'),flush=True)
