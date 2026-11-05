import bpy,json,pathlib,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Axial_Chapel_R03_EXPERIMENTAL.blend'))
segments={}
for group in ['WEBS','ARCHES','RIBS','ROOF','FLOORS']:
 lines=[]
 for ob in bpy.data.collections[group].objects:
  if ob.type!='MESH':continue
  me=ob.data;me.calc_loop_triangles()
  for tri in me.loop_triangles:
   vv=[ob.matrix_world@me.vertices[k].co for k in tri.vertices];hits=[]
   if all(abs(v.y)<1e-6 for v in vv):continue
   for a,b in zip(vv,vv[1:]+vv[:1]):
    if abs(a.y)<1e-6:hits.append(a)
    elif a.y*b.y<0:hits.append(a+(b-a)*(-a.y/(b.y-a.y)))
   unique=[]
   for p in hits:
    if all((p-q).length>1e-5 for q in unique):unique.append(p)
   if len(unique)==2 and (unique[0]-unique[1]).length>1e-5:lines.append([[float(p.x),float(p.z)] for p in unique])
 segments[group]=lines
(R/'LONGITUDINAL_MESH_SECTION.json').write_text(json.dumps(segments))
# Verify roof-off file really excludes roof objects by reading it as an independent export.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/'Axial_Chapel_R03_ROOF_OFF.glb'))
q=json.loads((R/'QA.json').read_text());q['checks']['roof_off_export_has_no_roof_objects']=not any(o.name.startswith('ROOF_') for o in bpy.context.scene.objects)
q['measured']['roof_off_mesh_count']=sum(o.type=='MESH' for o in bpy.context.scene.objects)
(R/'QA.json').write_text(json.dumps(q,indent=2))
print('Section segments',sum(map(len,segments.values())))
