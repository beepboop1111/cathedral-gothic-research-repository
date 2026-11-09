"""R43 non-destructive review of validated R42 scene with revised camera framing."""
import bpy,json
from mathutils import Vector
from pathlib import Path
root=Path('/home/christopher/Cathedral_Research')
out=root/'R43_profile_intake_and_review';out.mkdir(exist_ok=True)
src=root/'R42_branching_stone_engine/R42_Experimental_Branching_Stone.blend'
assert src.is_file()
bpy.ops.wm.open_mainfile(filepath=str(src))
scene=bpy.context.scene
cam=scene.camera
assert cam is not None
cam.location=(.85,-1.55,.84)
target=Vector((.0,0,.44))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=2.15
scene.render.filepath=str(out/'R43_framed_R42_render.png')
scene.render.resolution_x=1820
scene.render.resolution_y=1080
scene.cycles.samples=28
bpy.ops.wm.save_as_mainfile(filepath=str(out/'R43_R42_Review_Only.blend'))
bpy.ops.render.render(write_still=True)
print('R43_RENDER_PASS',scene.render.filepath)
