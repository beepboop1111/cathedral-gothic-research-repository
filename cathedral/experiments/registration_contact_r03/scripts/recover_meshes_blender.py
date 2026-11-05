import bpy,json,hashlib,gzip,base64
from pathlib import Path
from mathutils import Vector
O=Path('/tmp/F5ZP_R03_RECOVERY');r={}
p=Path('/home/christopher/Desktop/Cathedral_F5ZP_G40_Working.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
r['source_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();r['objects']=[]
names=['G40F__G40_CONTEXT_MINUS_G24_ORIGINAL','G40F__OPTION_C_G24_G25_REPLACEMENTS','G40_BOTH_TRANSEPTS_EXACT_G24_G39_CANDIDATE_STAIR_AND_GALLERY_1to16','G40M2_DERIVED_FULL_CHOIR_FIRST_FLOOR_X2360_TO_X10709_JOIN']
for name in names:
 ob=bpy.data.objects.get(name)
 if not ob:continue
 me=ob.data;me.calc_loop_triangles()
 r['objects'].append({'name':name,'vertices':[list(ob.matrix_world@v.co) for v in me.vertices],'faces':[list(t.vertices) for t in me.loop_triangles],'matrix':[list(v) for v in ob.matrix_world],'hide_viewport':ob.hide_viewport,'hide_render':ob.hide_render,'hidden':ob.hide_get(),'props':{k:str(v) for k,v in ob.items()}})
p=Path('/home/christopher/Desktop/newgen_F5ZN_A_CHEVET_STUDY_1to1.blend');bpy.ops.wm.open_mainfile(filepath=str(p))
r['chevet_source_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();r['guides']=[]
sc=bpy.data.scenes['CATHEDRAL_F5ZN_A_FULL_SCALE']
for ob in sc.objects:
 if ob.type=='EMPTY':r['guides'].append({'name':ob.name,'type':'EMPTY','point':list(ob.matrix_world.translation)})
 elif ob.type=='CURVE':r['guides'].append({'name':ob.name,'type':'CURVE','splines':[[list(ob.matrix_world@Vector(pt.co[:3])) for pt in s.points] for s in ob.data.splines]})
raw=json.dumps(r,separators=(',',':')).encode();enc=base64.b64encode(gzip.compress(raw,mtime=0)).decode()
(O/'meshes.json.gz.b64').write_text(enc)
print('MESH_DATA_READY',len(raw),len(enc),[x['name'] for x in r['objects']],flush=True)
