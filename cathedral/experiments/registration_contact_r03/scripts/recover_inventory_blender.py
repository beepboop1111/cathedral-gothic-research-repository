import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
O=Path('/tmp/F5ZP_R03_RECOVERY');O.mkdir(exist_ok=True)
files=['/home/christopher/Desktop/newgen_F5ZN_A_CHEVET_STUDY_1to1.blend','/home/christopher/Desktop/Cathedral_F5ZP_G40_Working.blend','/home/christopher/Cathedral_STLs/Cathedral_Parts_Library.blend','/home/christopher/Downloads/NE_J11_J12_R04_EDITABLE.blend']
report=[]
def props(x):return {k:str(v) for k,v in x.items()}
for f in files:
 p=Path(f)
 if not p.exists():continue
 bpy.ops.wm.open_mainfile(filepath=f)
 rec={'path':f,'size':p.stat().st_size,'mtime':p.stat().st_mtime,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scenes':[],'texts':[{'name':t.name,'length':len(t.as_string()),'head':t.as_string()[:500]} for t in bpy.data.texts]}
 for sc in bpy.data.scenes:
  s={'name':sc.name,'props':props(sc),'units':{'system':sc.unit_settings.system,'scale_length':sc.unit_settings.scale_length,'length_unit':sc.unit_settings.length_unit},'objects':[]}
  for ob in sc.objects:
   d={'name':ob.name,'type':ob.type,'props':props(ob),'matrix':[list(v) for v in ob.matrix_world],'collections':[c.name for c in ob.users_collection]}
   if ob.type in {'MESH','CURVE'}:
    pp=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    d['bounds']=[[min(v[i] for v in pp) for i in range(3)],[max(v[i] for v in pp) for i in range(3)]]
    d['vertices']=len(ob.data.vertices) if ob.type=='MESH' else sum(len(s.points)+len(s.bezier_points) for s in ob.data.splines)
   s['objects'].append(d)
  rec['scenes'].append(s)
 report.append(rec)
 (O/'inventory.json').write_text(json.dumps(report,separators=(',',':')))
 print('PROBED',f,[(s['name'],len(s['objects'])) for s in rec['scenes']],flush=True)
print('INVENTORY_READY',flush=True)
