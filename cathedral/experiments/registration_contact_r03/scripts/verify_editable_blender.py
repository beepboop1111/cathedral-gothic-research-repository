import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
O=Path('/home/christopher/Desktop/F5ZP_Registration_Contact_R03_EXPERIMENTAL')
source=next(Path('/tmp/F5ZP_R03_RECOVERY/R05').rglob('Crossing_Full_Cell_R05.blend'))
def signature(ob):
 if ob.type=='MESH':data={'v':[list(ob.matrix_world@v.co) for v in ob.data.vertices],'f':[list(p.vertices) for p in ob.data.polygons]}
 else:data={'splines':[[list(ob.matrix_world@Vector(v.co[:3])) for v in s.points] for s in ob.data.splines]}
 return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
base={o.name:signature(o) for o in bpy.context.scene.objects if o.type in {'MESH','CURVE'} and o.get('role')!='GUIDE'}
bpy.ops.wm.open_mainfile(filepath=str(O/'F5ZP_Registration_Contact_R03.blend'))
checks=[{'name':n,'identical_world_geometry':signature(bpy.data.objects[n])==h} for n,h in base.items()]
qa={'reopened':True,'source_R05_mesh_curve_objects':len(base),'matching':sum(c['identical_world_geometry'] for c in checks),'checks':checks,'source_files_modified':False}
(O/'BLENDER_REGRESSION_QA.json').write_text(json.dumps(qa,indent=2))
assert all(c['identical_world_geometry'] for c in checks)
print('BLENDER_REGRESSION_PASS',len(checks))
