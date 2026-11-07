"""Vector 2-rail section sweeps and clean 3D rigid instances.

A useful reusable core distilled from V06, not the monument-specific exporter.
Bar paths are independent; preserve both rails, never voxelize. Depth is
provisional unless explicitly calibrated. STL alone does not retain instancing.
"""
from __future__ import annotations
import math
import numpy as np
import trimesh


def polygon_area(points):
    p=np.asarray(points,float)
    return 0.5*float(np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1)))


def normalize_section(profile_xy):
    """Normalize an ordered CCW solid cross-section to [0,1] x [0,1]."""
    p=np.asarray(profile_xy,float)
    if len(p)<3 or p.ndim!=2 or p.shape[1]!=2:raise ValueError('Need ordered polygon points')
    if np.linalg.norm(p[0]-p[-1])<1e-9:p=p[:-1]
    if abs(polygon_area(p))<1e-12:raise ValueError('Degenerate profile')
    if polygon_area(p)<0:p=p[::-1].copy()
    span=np.ptp(p,axis=0)
    if np.any(span<=0):raise ValueError('Zero span')
    return (p-p.min(axis=0))/span


def _ear_clip(p):
    """Triangulate simple ordered CCW polygon with no extra mesh dependencies."""
    p=np.asarray(p,float);n=len(p);idx=list(range(n));tris=[]
    if polygon_area(p)<0:raise ValueError('Polygon must be CCW')
    def cross(a,b,c):
        x=b-a;y=c-b
        return float(x[0]*y[1]-x[1]*y[0])
    def inside(q,a,b,c):
        def cross2(x,y):return x[0]*y[1]-x[1]*y[0]
        u=cross2(b-a,q-a);v=cross2(c-b,q-b);w=cross2(a-c,q-c)
        return min(u,v,w)>=-1e-10
    budget=n*n
    while len(idx)>3 and budget>0:
        budget-=1
        for k in range(len(idx)):
            i,j,h=idx[k-1],idx[k],idx[(k+1)%len(idx)]
            if cross(p[i],p[j],p[h])<=1e-10:continue
            if any(inside(p[t],p[i],p[j],p[h]) for t in idx if t not in (i,j,h)):
                continue
            tris.append((i,j,h));idx.pop(k);break
        else:raise ValueError('Self-intersecting or invalid profile; triangulation failed')
    if budget<=0:raise ValueError('Exceeded triangulation budget')
    tris.append(tuple(idx))
    return np.asarray(tris,int)


def sweep_between_rails(outer_xy,inner_xy,profile_xy,relief_height,
                        axis='xy',cap=True):
    """Build a manifold stone bar between corresponding Nx2 analytical rails.

    Normalized section-u=0 follows outer exactly, u=1 follows inner exactly.
    Both arrays must be ordered in the SAME travel direction and have matching
    station count. Returns (trimesh, QA).  No physical-unit interpretation.
    """
    a=np.asarray(outer_xy,float);b=np.asarray(inner_xy,float)
    if a.shape!=b.shape or a.ndim!=2 or a.shape[1]!=2 or len(a)<3:
        raise ValueError('Rails must have matching Nx2 samples, at least 3')
    if relief_height<=0:raise ValueError('Positive relief required')
    u=normalize_section(profile_xy)
    widths=np.linalg.norm(b-a,axis=1)
    if np.min(widths)<1e-5:raise ValueError('Crossing or coincident rails')
    cross_xy=a[:,None,:]*(1-u[None,:,0,None])+b[:,None,:]*u[None,:,0,None]
    z=np.broadcast_to(u[None,:,1]*relief_height,(len(a),len(u)))
    xyz=np.dstack((cross_xy,z));n=len(u)
    faces=[]
    for k in range(len(a)-1):
        for i in range(n):
            j=(i+1)%n;p=k*n;q=(k+1)*n
            faces.extend([(p+i,q+i,p+j),(p+j,q+i,q+j)])
    if cap:
        tris=_ear_clip(u)
        faces.extend(tuple(int(x) for x in tri) for tri in tris)
        offset=(len(a)-1)*n
        faces.extend(tuple(offset+int(x) for x in tri[::-1]) for tri in tris)
    mesh=trimesh.Trimesh(vertices=xyz.reshape(-1,3),faces=np.asarray(faces,int),process=False)
    trimesh.repair.fix_normals(mesh)
    if cap and (not mesh.is_watertight or not mesh.is_winding_consistent):
        raise ValueError('Stonework is not a closed consistently wound manifold')
    outer_errors=np.max(np.linalg.norm(xyz[:,np.isclose(u[:,0],0),:2]-a[:,None,:],axis=2))
    inner_errors=np.max(np.linalg.norm(xyz[:,np.isclose(u[:,0],1),:2]-b[:,None,:],axis=2))
    qa=dict(stations=len(a),section_vertices=len(u),triangles=len(mesh.faces),
            min_rail_separation=float(min(widths)),max_rail_separation=float(max(widths)),
            outer_rail_max_residual=float(outer_errors),inner_rail_max_residual=float(inner_errors),
            watertight=bool(mesh.is_watertight),winding_consistent=bool(mesh.is_winding_consistent),
            note='Image/drawing units; stone relief hypothetical until dimensionally calibrated.')
    return mesh,qa


def repeat_mesh_radially(master,count,master_index=0):
    """Return a scene with one reusable geometry and N rigid scene nodes."""
    if not 1<=count<=256:raise ValueError('Bad count')
    scene=trimesh.Scene(base_frame='world')
    geom=master.copy()
    scene.add_geometry(geom,geom_name='SHARED_MASTER',node_name='SECTOR_0',
                       transform=trimesh.transformations.rotation_matrix(
                           math.radians(-(0-master_index)*360/count),[0,0,1]))
    for k in range(1,count):
        scene.graph.update(frame_to=f'SECTOR_{k}',frame_from='world',geometry='SHARED_MASTER',
                           matrix=trimesh.transformations.rotation_matrix(
                              math.radians(-(k-master_index)*360/count),[0,0,1]))
    return scene
