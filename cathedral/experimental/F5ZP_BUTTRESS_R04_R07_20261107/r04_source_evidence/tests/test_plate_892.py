import bpy,runpy,json,math
from pathlib import Path
from mathutils import Vector
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];m=runpy.run_path(str(P/'current/flying_buttress_r02.py'),run_name='module')
bpy.ops.wm.read_factory_settings(use_empty=True)
objects,qa=m['build_plate_892']()
assert qa['opening_inside'];assert qa['max_residual_px']<15
bad=[v for v in qa['checks'] if v['nonmanifold_edges'] or v['degenerate_polygons']];assert not bad,bad
print('PLATE_892_TEST_PASS',json.dumps({k:qa[k] for k in ['rms_px','max_residual_px','radius_px','circle_center_px','study_span','depth']}))
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_cavity=True;sc.world=bpy.data.worlds.new('Review');sc.world.color=(.82,.84,.86)
bpy.ops.object.camera_add(location=(10500,-21000,12000));cam=bpy.context.object;cam.rotation_euler=(Vector((1700,0,5300))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=14000;cam.data.clip_end=100000;sc.camera=cam
sc.render.resolution_x=1000;sc.render.resolution_y=1250;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';bpy.ops.render.render();bpy.data.images['Render Result'].save_render('/tmp/892_model.png',scene=sc)
source=Image.open(P/'sources/ungewitter_v2_p087.png').convert('RGB');cropbox=(565,465,1515,1650);crop=source.crop(cropbox);draw=ImageDraw.Draw(crop)
# Fit overlay on source: red dashed = uncertain approximation.
cx,cy=qa['circle_center_px'];r=qa['radius_px'];a0=math.atan2(1320-cy,846-cx);a1=math.atan2(770-cy,1388-cx);s=(a1-a0+math.pi)%(2*math.pi)-math.pi
for i in range(100):
 if i%4<2:
  pts=[(cx+r*math.cos(a0+s*t/100)-cropbox[0],cy+r*math.sin(a0+s*t/100)-cropbox[1]) for t in [i,i+1]];draw.line(pts,fill='#b32931',width=3)
for x,y in m['PLATE_892']['soffit_picks']:draw.ellipse((x-cropbox[0]-4,y-cropbox[1]-4,x-cropbox[0]+4,y-cropbox[1]+4),fill='#b32931')
canvas=Image.new('RGB',(2000,1400),'#e6e8eb');canvas.paste(crop.resize((950,1185)),(20,85));canvas.paste(Image.open('/tmp/892_model.png').convert('RGB'),(1000,65));d=ImageDraw.Draw(canvas)
d.text((25,22),'Ungewitter / Plate LXXXIV / fig. 892 / Freiburg',fill='#172638',font_size=29);d.text((1040,22),'Generator study / simplified details',fill='#172638',font_size=29)
d.text((25,1290),f"Coarse arch fit: RMS {qa['rms_px']:.1f} px; max {qa['max_residual_px']:.1f} px | red dashed = uncertain fit",fill='#172638',font_size=25)
d.text((25,1335),'Study span 5000 native units; depth conjectural. Historical scale and structural adequacy unverified.',fill='#172638',font_size=25)
canvas.save(P/'current/output/plate_892_generator_result.png')
