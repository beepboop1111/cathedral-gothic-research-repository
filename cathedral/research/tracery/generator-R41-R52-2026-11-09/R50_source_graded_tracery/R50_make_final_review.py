from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path('/home/christopher/Cathedral_Research/R50_source_graded_tracery')
d=json.loads((R/'R50_source_measurements.json').read_text())
q=json.loads((R/'R50_Blender_geometry_QA.json').read_text())
checks=[json.loads(p.read_text()) for p in sorted(R.glob('R50_GLb_roundtrip_*.json'))]
assert len(checks)==2 and all(x['pass'] and x['Euler_characteristic']==-4 and x['source_vertex_exact_after_inverse_mapping'] for x in checks)
assert not q['user_profile_source_applied'] and not d['scale_bar_verified']
assert hashlib.sha256(Path(d['source_file']).read_bytes()).hexdigest()==d['source_SHA256']
P=Image.new('RGB',(2360,1320),'#f6f7f4')
draw=ImageDraw.Draw(P)
froot='/usr/share/fonts/truetype/dejavu/DejaVuSans'
F=lambda n,b=False:ImageFont.truetype(froot+('-Bold' if b else '')+'.ttf',n)
dark='#203039';ink='#24333b';muted='#5d6c70'
draw.rectangle((0,0,2360,140),fill=dark)
draw.text((43,25),'R50   /   SOURCE-GRADED GOTHIC TRACERY STUDY',font=F(37,True),fill='white')
draw.text((45,79),'Brandon M04 R03 traced window head  ·  no user moulding profiles  ·  original physical scale unverified',font=F(21),fill='#cddbd9')
draw.rounded_rectangle((25,159,1120,1002),radius=14,fill='white',outline='#d0d9d7',width=2)
draw.rounded_rectangle((1141,159,2333,1002),radius=14,fill='white',outline='#d0d9d7',width=2)
draw.text((48,181),'01  /  RECOVERED PIXEL-SPACE OUTLINES',font=F(23,True),fill=ink)
draw.text((1163,181),'02  /  BLENDER 5.2.2 EXPERIMENTAL PROXY',font=F(23,True),fill=ink)
source=Image.open(R/'R50_source_overlay_2D.png').convert('RGB').crop((0,105,1250,1005))
source=ImageOps.contain(source,(1060,744),Image.Resampling.LANCZOS)
render=ImageOps.contain(Image.open(R/'R50_Blender_Render.png').convert('RGB'),(1160,744),Image.Resampling.LANCZOS)
P.paste(source,(43+(1060-source.width)//2,239+(744-source.height)//2))
P.paste(render,(1156+(1160-render.width)//2,239+(744-render.height)//2))
draw=ImageDraw.Draw(P)
draw.text((45,972),'Black: R03 traced geometry  ·  Gray: construction  ·  Red dashed: uncertain circle fits',font=F(15),fill=muted)
draw.text((1163,972),'Stone outline only  ·  historical sections and bedding surfaces remain unknown',font=F(15),fill=muted)
for x0,x1 in ((25,1120),(1141,2333)):
 draw.rounded_rectangle((x0,1016,x1,1213),radius=14,fill='white',outline='#d0d9d7',width=2)
draw.text((46,1036),'SOURCE COORDINATES',font=F(20,True),fill=ink)
draw.text((1164,1036),'3D PROXY QA',font=F(20,True),fill=ink)
fit=d['outer_arc_fits']
left=[
 f'4 outline rings  /  3 voids  /  {d["outline_span_pixels"]:.0f} × {d["outline_height_pixels"]:.0f} image pixels',
 f'Preserved stone-face area: {d["stone_face_area_in_source_px2"]:,.1f} pixel²',
 f'Outer arch fit residuals: {fit["right_outer"]["RMS_to_R03_trace_px"]:.3f} / {fit["left_outer"]["RMS_to_R03_trace_px"]:.3f} pixels RMS']
right=[
 'Mesh watertight  /  560 welded vertices  /  topology genus 3',
 '2,400 mm display width and 180 mm depth are hypothetical',
 'GLB reimport: Blender 5.1.2 and 5.2.2 PASS  /  source outline exact']
for i,t in enumerate(left):draw.text((46,1082+i*36),t,font=F(17),fill=muted)
for i,t in enumerate(right):draw.text((1164,1082+i*36),t,font=F(17),fill=muted)
draw.rectangle((0,1232,2360,1320),fill=dark)
draw.text((45,1245),'TECHNICAL GEOMETRY: PASS',font=F(21,True),fill='#c6e6d0')
draw.text((745,1245),'HISTORICAL SCALE / MASONRY / LOAD PATH: UNVERIFIED',font=F(19,True),fill='#f1c6b9')
draw.text((45,1282),'Original Brandon R03 and cathedral checkpoints remain unchanged. Blender opened with tab.py keymap.',font=F(16),fill='#d3dddd')
out=R/'R50_FINAL_Brandon_Source_vs_Blender.png'
P.save(out,optimize=True)
report={'checkpoint':'R50','state':'SOURCE_GRADED_EXPERIMENTAL',
 'original_source':d['source_file'],'source_sha256':d['source_SHA256'],
 'source_pixel_geometry_verified':True,'original_source_image_registered':False,
 'source_scale_bar_verified':False,
 'surfaces_contours':4,'openings':3,
 'GLB':q['GLB'],'GLB_compatibility':[v['Blender'] for v in checks],
 'assumed_width_mm':2400,'assumed_depth_mm':180,
 'no_user_moulding_profiles_used':True,
 'keymap_file':'/home/christopher/tab.py','tab_keymap_active_5_2_2_tested':True,
 'keymap_warning':'Missing User Interface keymap during versioning; completeness not guaranteed',
 'historical_and_structural_validation':'NOT CERTIFIED',
 'protected_R03_and_F5ZP_untouched':True,'review_png':str(out)}
(R/'R50_CHECKPOINT.json').write_text(json.dumps(report,indent=2))
print('R50_FINAL_REVIEW_CREATED',out,'bytes',out.stat().st_size)
