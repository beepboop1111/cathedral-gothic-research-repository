import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
root=Path('/home/christopher/Downloads/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL')
source=root/'F5ZP_R12C_FULL_PLAN_EXPERIMENTAL.blend'
out=root/'R14_Q1_Q2_SUPPORT_RECOVERY_EXPERIMENTAL/R12C_SAVED_BLEND_Q1_Q2_OBJECTS.json'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
data=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 coords=[o.matrix_world@v.co for v in o.data.vertices]
 if not coords:continue
 x0=min(v.x for v in coords);x1=max(v.x for v in coords);y0=min(v.y for v in coords);y1=max(v.y for v in coords)
 if x1<3650 or x0>6500 or y1<-8700 or y0>8700:continue
 if not any(s in o.name for s in ('Q1_Q2','Lower_node_3-3','Lower node 3-3','lane_')):
  continue
 data.append({'name':o.name,'collection_names':[c.name for c in o.users_collection],
              'bounds_native':[x0,y0,x1,y1],'vertex_count':len(coords),
              'status':o.get('F5ZP_STATUS','UNSPECIFIED')})
data.sort(key=lambda d:d['name'])
out.write_text(json.dumps({'blend_path':str(source),
 'blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'object_count':len(data),'objects':data},indent=2)+'\n')
print('R14 BLENDER SOURCE',len(data),'matching objects, saved',out)
for d in data:print(d['name'],d['bounds_native'],d['status'])