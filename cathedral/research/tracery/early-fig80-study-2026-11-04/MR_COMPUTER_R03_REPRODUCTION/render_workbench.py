import bpy
from pathlib import Path
folder=Path('/home/christopher/Desktop/sketch2stl/_EXPERIMENTS/STLEU_FIG80_R03')
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='SINGLE'
scene.display.shading.single_color=(0.78,0.73,0.65)
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.2
scene.display.shading.curvature_valley_factor=1.0
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(folder/'StLeu_R03_blender_front_WORKBENCH.png')
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'StLeu_Fig80_R03_UPRIGHT_REVIEW.blend'),compress=True)
bpy.ops.render.render(write_still=True)
print('RENDER_FINAL',scene.render.filepath)
