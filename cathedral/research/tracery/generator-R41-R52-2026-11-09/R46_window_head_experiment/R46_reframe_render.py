"""R46 framing-only review — original checkpoint geometry remains untouched."""
import bpy
from pathlib import Path
from mathutils import Vector
DIR=Path('/home/christopher/Cathedral_Research/R46_window_head_experiment')
src=DIR/'R46_Window_Head_Experimental_Study.blend'
assert src.exists()
bpy.ops.wm.open_mainfile(filepath=str(src))
scene=bpy.context.scene
cam=scene.camera
assert cam is not None
cam.location=(2.15,-5.9,2.52)
target=Vector((0,0,1.40))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'
cam.data.ortho_scale=4.20
scene.cycles.samples=40
scene.render.resolution_x=1800
scene.render.resolution_y=1120
scene.render.resolution_percentage=100
scene.render.filepath=str(DIR/'R46_reframed_blender_render.png')
bpy.ops.wm.save_as_mainfile(filepath=str(DIR/'R46_REVIEW_ONLY_Viewer.blend'))
bpy.ops.render.render(write_still=True)
print('R46_REFRAME_DONE',scene.render.filepath)
