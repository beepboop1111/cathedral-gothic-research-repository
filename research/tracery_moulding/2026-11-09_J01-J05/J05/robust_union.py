# J05: Manifold3D alternate robust CSG, no source mesh changes.
import sys,os,json,time
import numpy as np
sys.path.insert(0,'/home/christopher/Cathedral_Experiments/tracery_moulding_J05/vendor')
import manifold3d as m
import trimesh
root='/home/christopher/Cathedral_Experiments/tracery_moulding_J05'
names=json.load(open(root+'/paths.json'))
meshes=[]
allqa=[]
for i,name in enumerate(names):
    a=np.load(root+f'/path_{i:02d}.npz')
    verts=a['vertices'].astype(np.float32);tri=a['triangles'].astype(np.uint32)
    ma=m.Manifold(m.Mesh(verts,tri))
    status=str(ma.status())
    tm=trimesh.Trimesh(vertices=verts,faces=tri,process=False)
    allqa.append(dict(name=name,mesh_status=status,volume=float(tm.volume),watertight=bool(tm.is_watertight),verts=len(verts),triangles=len(tri)))
    print('INPUT',i,name,status,'water',tm.is_watertight,'volume',tm.volume,flush=True)
    meshes.append(ma)
results=[]
for count in (3,13):
    t=time.time()
    try:
        acc=meshes[0]
        for idx in range(1,count):
            acc=acc+meshes[idx]
            print('MERGE',idx,names[idx],str(acc.status()),round(acc.volume(),3),acc.num_tri(),flush=True)
        mesh=acc.to_mesh()
        v=np.asarray(mesh.vert_properties)[:,:3]
        f=np.asarray(mesh.tri_verts)
        tm=trimesh.Trimesh(vertices=v,faces=f,process=False)
        out=dict(n=count,status=str(acc.status()),volume=float(acc.volume()),
                 num_tri=len(f),num_vertices=len(v),water=bool(tm.is_watertight),
                 winding=bool(tm.is_winding_consistent),components=len(tm.split(only_watertight=False)),seconds=round(time.time()-t,2))
        np.savez_compressed(root+f'/union_{count:02d}.npz',vertices=v,triangles=f)
        results.append(out)
        print('RESULT',out,flush=True)
    except Exception as exc:
        out={'n':count,'error':repr(exc)}
        print('ERROR',out,flush=True);results.append(out)
with open(root+'/J05_kernel_QA.json','w') as f:
    json.dump(dict(inputs=allqa,results=results),f,indent=2)
