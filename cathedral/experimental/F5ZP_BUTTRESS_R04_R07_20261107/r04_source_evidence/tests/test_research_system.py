import bpy,runpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]/'current'
m=runpy.run_path(str(P/'flying_buttress_r02.py'),run_name='module')
bpy.ops.wm.read_factory_settings(use_empty=True)
sentinel=bpy.data.objects.new('PROTECTED',None);bpy.context.scene.collection.objects.link(sentinel)
variants={'T_Quatrefoil':{'receiver_section':'T','tracery_rule':'quatrefoil'},'Stepped_Intermediate':{'receiver_section':'stepped','intermediate':True,'tracery_rule':'trefoil'},'Rectangle_Pointed':{'receiver_section':'rectangular','tracery_rule':'pointed','preset':'double_flyer_study'}}
results=m['proportion_studies']({},variants)
for name,objects,qa in results:
 bad=[r for r in qa['mesh_checks'] if r['nonmanifold_edges'] or r['degenerate_polygons']]
 assert not bad,(name,bad)
 assert all(d['minimum_fall']>0 for d in qa['drainage'])
 assert len(qa['flyer_sections'])==(4 if qa['options']['intermediate'] else 2)
 assert qa['construction_arcs']
 assert all(math.isfinite(v) for o in objects for p in o.data.vertices for v in p.co)
 print('VARIANT_PASS',name,len(objects),len(qa['construction_arcs']))
assert bpy.data.objects.get('PROTECTED') is sentinel
# Verify intersection equations and source status without historical claims.
for kind in ['trefoil','quatrefoil','pointed']:
 specs=m['rule_paths'](kind,0,0,100)
 for s in specs:
  path,closed=m['path_from_spec'](s);c=Vector(s['center'])
  assert max(abs((Vector(p)-c).length-s['radius']) for p in path)<1e-3
assert all(p['measured_proportions'] is None for p in m['HISTORICAL_PRESETS'].values())
print('COMBINED_R03_TEST_PASS')
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_cavity=True
sc.world=bpy.data.worlds.new('Review');sc.world.color=(.82,.84,.87)
# Matched orthographic front panels: one camera per study, render and tile in memory.
from PIL import Image,ImageDraw
panels=[]
for i,(name,objects,qa) in enumerate(results):
 for j,(_,obs,_) in enumerate(results):
  for ob in obs:ob.hide_render=j!=i
 bpy.ops.object.camera_add(location=(9000,i*4500-19000,10500));cam=bpy.context.object;cam.rotation_euler=(Vector((2400,i*4500,4300))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=11000;cam.data.clip_end=100000;sc.camera=cam
 sc.render.resolution_x=850;sc.render.resolution_y=1050;sc.render.resolution_percentage=100
 bpy.ops.render.render()
 sc.render.image_settings.file_format='PNG'
 bpy.data.images['Render Result'].save_render('/tmp/buttress_panel_'+str(i)+'.png',scene=sc)
 panels.append(Image.open('/tmp/buttress_panel_'+str(i)+'.png').convert('RGB'))
canvas=Image.new('RGB',(2550,1170),'#e5e8eb');d=ImageDraw.Draw(canvas)
for i,((name,_,qa),im) in enumerate(zip(results,panels)):
 canvas.paste(im,(850*i,65));d.text((850*i+25,22),name.replace('_',' / '),fill='#172638',font_size=26)
d.text((30,1090),'Span 5000 | lower landings 3400 / 6000 | upper landings 5400 / 7300 | native demonstration units',fill='#172638',font_size=23)
d.text((30,1120),'R03 EXPERIMENTAL | matched scale | two tiers, compass tracery, stone courses, drainage | historical proportions unmeasured',fill='#172638',font_size=23)
canvas.save(P/'output/research_generator_result.png')
