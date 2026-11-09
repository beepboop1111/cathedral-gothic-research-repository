# J05: export immutable J01 sweep fixtures as triangulated numeric meshes.
import bpy,bmesh,numpy as np,os,json
root='/home/christopher/Cathedral_Experiments/tracery_moulding_J05'
s=open('/home/christopher/Cathedral_Experiments/tracery_moulding_J01/generate_J01.py').read()
exec(s[:s.index('paths=[]')],globals())
exec(s[s.index('paths=[]'):s.index('parts=[sweep(')],globals())
for i,(name,curve) in enumerate(paths):
    ob=sweep(name,curve,stone)
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bm.verts.ensure_lookup_table()
    for n,v in enumerate(bm.verts):v.index=n
    verts=np.array([tuple(v.co) for v in bm.verts],dtype=np.float64)
    tris=np.array([[v.index for v in f.verts] for f in bm.faces],dtype=np.uint32)
    bm.free()
    np.savez_compressed(f'{root}/path_{i:02d}.npz',vertices=verts,triangles=tris)
    print('PATH',i,name,len(verts),len(tris),flush=True)
with open(f'{root}/paths.json','w') as f:json.dump([x[0] for x in paths],f)
