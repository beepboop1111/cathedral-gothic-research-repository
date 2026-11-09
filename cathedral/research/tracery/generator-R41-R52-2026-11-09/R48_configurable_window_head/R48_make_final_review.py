#!/usr/bin/env python3
"""One final R48 PNG and historical/geometry QA checkpoint; no geometry edits."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('/home/christopher/Cathedral_Research')
R=ROOT/'R48_configurable_window_head'
A=R/'R48_BASELINE_PROFILE_1'
B=R/'R48_ALTERNATE_PROFILE_8'
dA=json.loads((A/'R48_QA.json').read_text())
dB=json.loads((B/'R48_QA.json').read_text())
neg=json.loads((R/'R48_negative_test_results.json').read_text())
source_A=json.loads((R/'R48_source_1_rebated.json').read_text())
source_B=json.loads((R/'R48_source_8_rebated.json').read_text())
assert neg['all_pass']
checks=[]
for directory in (A,B):
 for v in ('5.0.1','5.1.2','5.2.2'):
  p=directory/('R48_roundtrip_'+v.replace('.','_')+'.json')
  assert p.exists(),('missing GLB regression result',p)
  info=json.loads(p.read_text())
  assert info['imported_meshes']==29 and info['independently_matched_contact_faces']==26
  assert not info['intergroup_collision_pairs'] and info['geometric_contact_pass']
  checks.append(info)
assert len(checks)==6
maxerr=max(j['imported_area_delta_mm2'] for x in checks for j in x['contacts'])
maxcen=max(j['centroid_delta_mm'] for x in checks for j in x['contacts'])
assert maxerr<.005 and maxcen<.001
assert dA['3d_member_count']==dB['3d_member_count']==29
assert dA['matched_independent_stone_joints']==dB['matched_independent_stone_joints']==26
assert (A/'R48_WINDOW_HEAD_1to1_EXPERIMENT.glb').is_file()
assert (B/'R48_WINDOW_HEAD_1to1_EXPERIMENT.glb').is_file()
assert (A/'R48_REVIEW_Camera_Framed.png').is_file()
assert abs(source_A['rebate_area_reduction_mm2']-256)<.0001
assert abs(source_B['rebate_area_reduction_mm2']-256)<.0001
assert json.loads((R/'R48_NATIVE51_PROFILE1/R48_QA.json').read_text())['software']=='5.1.2'
vsource=[source_A,source_B]
W,H=2380,1420
poster=Image.new('RGB',(W,H),'#f5f6f2')
d=ImageDraw.Draw(poster)
fontroot='/usr/share/fonts/truetype/dejavu/DejaVuSans'
F=lambda z,b=False:ImageFont.truetype(fontroot+('-Bold' if b else '')+'.ttf',z)
dark='#20313b';muted='#596770';accent='#326d4e';warn='#ad6144';ink='#26343b'
d.rectangle((0,0,W,142),fill=dark)
d.text((47,25),'R48   CONFIGURABLE GOTHIC WINDOW-HEAD GENERATOR',font=F(37,True),fill='white')
d.text((49,81),'2 French Gothic source profiles  •  1:1 stone geometry  •  compound pointed arches  •  continuous glazing rebates',font=F(21),fill='#d0dedd')
render=Image.open(A/'R48_REVIEW_Camera_Framed.png').convert('RGB')
w=1660
view=render.resize((w,round(render.height*w/render.width)),Image.Resampling.LANCZOS)
poster.paste(view,(20,192))
d=ImageDraw.Draw(poster)
d.rounded_rectangle((38,208,825,265),radius=12,fill='#263741')
d.text((57,224),'PROFILE 1   /   29 STONE WINDOW-HEAD ASSEMBLY',font=F(20,True),fill='white')
d.text((43,1234),'Blender 5.2.2 LTS Cycles render. Pointed arches use exact two-centred arcs; voussoir and glazing dimensions are experimental.',font=F(16),fill=muted)
# Sidebar
sx=1715
d.rounded_rectangle((sx,168,2350,1257),radius=18,fill='white',outline='#d3dcd9',width=2)
d.text((sx+27,196),'R48  |  VALIDATION',font=F(25,True),fill=ink)
meta=[
 ('Profiles accepted','Archive 1 + Archive 8'),
 ('Stone meshes per assembly','29 closed solids'),
 ('Mating joints per assembly','26 matched'),
 ('Cross-component collision checks','315 each / 0 collisions'),
 ('GLB importers','5.0.1, 5.1.2, 5.2.2'),
 ('Native Blender generator','5.1.2 + 5.2.2'),
 ('Input rejection tests','11 / 11 PASS'),
 ('Largest area mismatch',f'{maxerr:.6f} mm²'),
 ('Largest centroid mismatch',f'{maxcen:.6f} mm')
]
y=253
for label,value in meta:
 d.text((sx+27,y),label,font=F(16),fill=muted)
 d.text((sx+27,y+26),value,font=F(19,True),fill=accent if ('PASS' in value or '0 collisions' in value) else ink)
 y+=64
d.line((sx+27,y+6,2322,y+6),fill='#d9e1dc',width=2)
d.text((sx+27,y+27),'SOURCE PROFILES  /  EXPLICIT ASSUMPTIONS',font=F(17,True),fill=ink)
# Two experimental cross-sections, shown side-by-side with their true contours.
def trace(source,x0,y0):
 pp=source['closed_points_mm']
 xx=[float(a) for a,b in pp];yy=[float(b) for a,b in pp]
 minx,maxx=min(xx),max(xx);miny,maxy=min(yy),max(yy)
 size=155
 scale=min(size/(maxx-minx),size/(maxy-miny))
 cx=x0+130;cy=y0+86
 pts=[(round(cx+(float(a)-(maxx+minx)/2)*scale),round(cy-(float(b)-(maxy+miny)/2)*scale)) for a,b in pp]
 d.polygon(pts,fill='#e6ddd1')
 d.line(pts+[pts[0]],fill='#303a40',width=3,joint='curve')
 # rebate recess highlighted as assumed width x cross-sectional depth
 d.text((x0+39,y0+169),source['source_archive_member'],font=F(16,True),fill=ink)
trace(source_A,sx+18,y+64)
trace(source_B,sx+302,y+64)
d.text((sx+27,y+272),'112 mm assumed width; 16 × 16 mm assumed rebate',font=F(15,True),fill=warn)
d.text((sx+27,y+300),'Original silhouette backing edge is clipped.',font=F(15),fill=muted)
d.text((sx+27,y+332),'Neither is an authenticated historical stone scan.',font=F(15),fill=muted)
# Footer
d.rectangle((0,1294,W,H),fill=dark)
d.text((43,1311),'TECHNICAL / GEOMETRIC   PASS',font=F(23,True),fill='#c7e9d5')
d.text((1050,1312),'HISTORICAL / STRUCTURAL   UNVALIDATED',font=F(21,True),fill='#f0c7b9')
d.text((43,1358),'Full original jamb bearings, measured historical window set-out and actual 3D joint contacts remain unresolved.',font=F(17),fill='#d5dfe0')
d.text((43,1386),'F5ZP / F5ZN-A / Pass 6J and R34–R47 protected; source work not overwritten.',font=F(16),fill='#d5dfe0')
target=R/'R48_FINAL_Validated_Window_Generator.png'
poster.save(target,optimize=True)
assert Image.open(target).size==(W,H)
check={
 'checkpoint':'R48',
 'state':'REUSABLE_EXPERIMENTAL_WINDOW_GENERATOR',
 'type':'Blender 5.1+ procedural 1:1 meshes',
 'script':str(R/'R48_window_head_generator.py'),
 'profile_preparation':str(R/'R48_prepare_profile.py'),
 'config_files':[str(R/'R48_baseline_config.json'),str(R/'R48_alternate_config.json')],
 'GLBs':[str(A/'R48_WINDOW_HEAD_1to1_EXPERIMENT.glb'),str(B/'R48_WINDOW_HEAD_1to1_EXPERIMENT.glb')],
 'tested_profile_members':['1.png','8.png'],
 'native_blender_tested':['5.1.2','5.2.2 LTS'],
 'GLB_importer_tested':['5.0.1','5.1.2','5.2.2 LTS'],
 'all_GLb_matrix_entries_passed':len(checks),
 'closed_stone_parts_per_case':29,'matching_contact_surfaces_per_case':26,
 'cross_component_pair_checks_each':315,'collisions_detected':0,
 'max_joint_area_mismatch_mm2':maxerr,'max_joint_centroid_delta_mm':maxcen,
 'rejected_invalid_inputs':11,
 'historical_accuracy':'NOT CERTIFIED',
 'archaeological_profile_source':'User French Gothic archive, page 1 and 8 silhouettes; right backing edge clipped',
 'assumed_width_mm':112,
 'assumed_glazing_rebate_mm':[16,16],
 'geometrical_foil':'parametric fourfold study, not historical compass set-out',
 'masonry_bearings':'NOT INCLUDED',
 'structural_forces':'NOT VALIDATED',
 'approved_cathedral_geometry_untouched':True,
 'review_image':str(target)}
(R/'R48_CHECKPOINT_HANDOFF.json').write_text(json.dumps(check,indent=2))
(R/'R48_RUNBOOK.txt').write_text(
 'R48 WORKFLOW — experimental source-graded stone-window generator\n'
 '1) python3 R48_prepare_profile.py --source <zip-or-png> --member 1.png --profile-id TEST --width-mm 112 --rebate-depth-mm 16 --rebate-height-mm 16 --out custom_profile.json\n'
 '2) Edit R48_baseline_config.json with selected profile_json, head spans/rises, foil and arc fractions. Use a NEW window_id.\n'
 '3) blender --factory-startup -b --python R48_window_head_generator.py -- config.json\n'
 '4) blender --factory-startup -b --python R48_import_validation.py -- <output_directory>\n'
 '5) Review GLB; geometry is experimental until authenticated historical surveys establish the joints and measures.\n'
 )
print('R48_FINAL_IMAGE_VERIFIED',target,'bytes',target.stat().st_size,'QA',len(checks),len(meta),check['rejected_invalid_inputs'])
