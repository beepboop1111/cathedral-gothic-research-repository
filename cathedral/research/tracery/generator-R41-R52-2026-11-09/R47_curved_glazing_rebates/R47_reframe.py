"""R47 camera-only high-quality review; protected mesh baseline unchanged."""
import bpy
from pathlib import Path
from mathutils import Vector
DIR=Path('/home/christopher/Cathedral_Research/R47_curved_glazing_rebates')
bpy.ops.wm.open_mainfile(filepath=str(DIR/'R47_Window_Head_Rebated_Experimental.blend'))
sc=bpy.context.scene
cam=sc.camera
cam.location=(2.15,-5.9,2.52)
target=Vector((0,0,1.40))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'
cam.data.ortho_scale=4.20
sc.cycles.samples=40
sc.render.resolution_x=1800
sc.render.resolution_y=1120
sc.render.resolution_percentage=100
sc.render.filepath=str(DIR/'R47_reframed_3d_blender.png')
bpy.ops.wm.save_as_mainfile(filepath=str(DIR/'R47_Viewer_Review_Only.blend'))
bpy.ops.render.render(write_still=True)
print('R47_CAMERA_RENDER_PASS',sc.render.filepath)
