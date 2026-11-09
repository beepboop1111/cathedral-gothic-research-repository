"""R48 review-only camera framing. No geometry changes to validated assets."""
import bpy
from pathlib import Path
from mathutils import Vector
R=Path('/home/christopher/Cathedral_Research/R48_configurable_window_head/R48_BASELINE_PROFILE_1')
bpy.ops.wm.open_mainfile(filepath=str(R/'R48_Experimental_Window_Head.blend'))
scene=bpy.context.scene;cam=scene.camera
assert cam is not None
cam.location=(2.15,-5.9,2.52)
target=Vector((0,0,1.4))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=4.20
scene.cycles.samples=40
scene.render.resolution_x=1800;scene.render.resolution_y=1120
scene.render.resolution_percentage=100
scene.render.filepath=str(R/'R48_REVIEW_Camera_Framed.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'R48_Viewer_Only.blend'))
bpy.ops.render.render(write_still=True)
print('R48_VIEWPORT_RENDER_PASS',scene.render.filepath)
