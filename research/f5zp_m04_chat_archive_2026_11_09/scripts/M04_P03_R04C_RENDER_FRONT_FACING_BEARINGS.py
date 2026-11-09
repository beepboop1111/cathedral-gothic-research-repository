import bpy,hashlib,json
from pathlib import Path
from mathutils import Vector
from PIL import Image,ImageDraw,ImageFont
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
orig=R/"M04_P03_R04B_CUTAWAY_REAL_FIVE_ARCHES_AND_STONES_EXPERIMENTAL/M04_P03_R04B_CUTAWAY_SOURCE_AND_FIVE_COURSES_EXPERIMENTAL.blend"
O=R/"M04_P03_R04C_FRONT_FACING_BEARING_REVIEW_EXPERIMENTAL"
assert not O.exists()
O.mkdir()
sha=hashlib.sha256(orig.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(orig))
c=bpy.context.scene.camera
target=Vector((31000.,-1320.,2110.))
c.location=target+Vector((720,1450,850))
c.rotation_euler=(target-c.location).to_track_quat("-Z","Y").to_euler()
c.data.type="ORTHO";c.data.ortho_scale=1800;c.data.clip_start=.1;c.data.clip_end=20000
sc=bpy.context.scene
sc.render.filepath=str(O/"FRONT_RAW.png")
sc.render.resolution_x=1700;sc.render.resolution_y=1320
sc.render.image_settings.file_format="PNG"
bpy.ops.wm.save_as_mainfile(filepath=str(O/"M04_P03_R04C_FRONT_FACING_UNAPPROVED_SOURCE_CUTAWAY.blend"))
bpy.ops.render.render(write_still=True)
with Image.open(O/"FRONT_RAW.png") as pic:im=pic.convert("RGB")
canvas=Image.new("RGB",(1700,1515),(246,248,250))
canvas.paste(im,(0,118))
draw=ImageDraw.Draw(canvas)
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
draw.rectangle((0,0,1700,117),fill=(27,48,59))
draw.text((30,15),"M04 P03 R04 | True R03 five-bearing springing • front-facing source cutaway",font=ImageFont.truetype(bold,29),fill=(240,246,249))
draw.text((30,65),"ORIGINAL lower receiving walls + five source arches  /  five corrected experimental courses",font=ImageFont.truetype(regular,19),fill=(180,211,222))
draw.rectangle((0,1438,1700,1515),fill=(247,248,250))
draw.text((28,1453),"LOWER BED: 99.99985% supported by actual R03 pier and receiving masonry",font=ImageFont.truetype(regular,20),fill=(31,86,67))
draw.text((28,1482),"UPPER: 9,064 sq. native units unmatched; masonry replacement NOT APPROVED",font=ImageFont.truetype(regular,20),fill=(143,53,48))
final=O/"F5ZP_M04_P03_R04C_SINGLE_TRUE_GOTHIC_BEARING_REVIEW.png"
canvas.save(final,optimize=True)
assert hashlib.sha256(orig.read_bytes()).hexdigest()==sha
print("FRONT_VIEW_PASS",final,final.stat().st_size)
