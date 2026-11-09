import bpy,bmesh
from pathlib import Path
for name in ('R44_B35','R44_A50'):
 p=Path('/home/christopher/Cathedral_Research/R44_bearing_regression')/name/'R42_BRANCHING_JOINT_AND_REBATES.glb'
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=str(p))
 ob=next(o for o in bpy.context.scene.objects if 'extension_stone_1' in o.name)
 for tol in (1e-7,2e-7,5e-7,1e-6,2e-6,1e-5):
  bm=bmesh.new();bm.from_mesh(ob.data)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=tol)
  bad=sum(not e.is_manifold for e in bm.edges)
  tiny=sum(f.calc_area()<1e-12 for f in bm.faces)
  print('R44_WELD_DIAG',name,tol,len(bm.verts),bad,tiny,bm.calc_volume(signed=True),flush=True)
  if tol==1e-7:
   for e in bm.edges:
    if not e.is_manifold:
     print('BOUNDARY_EDGE',name,'faces',len(e.link_faces),[tuple(round(float(v.co[i]),6) for i in range(3)) for v in e.verts],flush=True)
  bm.free()
