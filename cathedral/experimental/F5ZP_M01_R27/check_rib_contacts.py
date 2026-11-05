import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('/home/christopher/Desktop/F5ZP_M01_R27_RECEIVERS_EXPERIMENTAL_20261105')
bpy.ops.wm.open_mainfile(filepath=str(P/'F5ZP_M01_R27_B_RECEIVERS_EXPERIMENTAL.blend'),load_ui=False)
q=json.loads((P/'R27_MEASUREMENTS.json').read_text())
def tree(o):
 eo=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eo.to_mesh()
 t=BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);eo.to_mesh_clear();return t
def inside(p,poly):
 x,y=p;res=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:res=not res
 return res
out=[]
for kind in ['ENGAGED','T_PLAN','DETACHED']:
 for c in bpy.data.collections:
  if c.name.startswith('R27_'):c.hide_viewport=False
 for ob in bpy.context.scene.objects:
  if not ob.name.startswith('R21_OGIVE_') or not ob.name.endswith('_0'):continue
  p=ob.matrix_world@ob.data.splines[0].points[0].co.to_3d()
  station=round(math.degrees(math.atan2(p.x-20213,p.y)))
  rr=next((r for r in q['receivers'] if r['station']==station and r['kind']==kind),None)
  if not rr:continue
  target=bpy.context.scene.objects[rr['name']]
  out.append({'kind':kind,'rib':ob.name,'station':station,'spring':list(p),'inside_receiver_volume':inside(p.to_2d(),rr['footprint']) and 0<=p.z<=rr['top_z'],'point_to_receiver_surface':tree(target).find_nearest(p)[3],'surface_triangle_pairs':len(tree(ob).overlap(tree(target)))})
(P/'R27_ACTUAL_RIB_CONTACTS.json').write_text(json.dumps(out,indent=2))
print('CONTACT_BEGIN'+json.dumps(out)+'CONTACT_END')
