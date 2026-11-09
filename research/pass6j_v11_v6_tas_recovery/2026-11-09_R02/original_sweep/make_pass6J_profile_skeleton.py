#!/usr/bin/env python3
"""
make_pass6J_profile_skeleton.py

Replace the locked Pass 7 rib cross-section with a user PNG profile while
preserving the ACTUAL Pass 6J / Pass 7 rib paths recovered from the original
84-rib guide STL.

The guide STL is the authority: no new Gothic arc fit is calculated.
Each of its 84 watertight rib solids contains 340 pentagonal section stations.
The script reconstructs the original web-following reference curve from those
stations, then sweeps the chosen PNG silhouette along that curve.

Default profile placement:
  - image horizontal axis -> rib lateral width, centered on the guide path
  - image vertical axis   -> rib height/depth away from the web
  - bottom of profile sits `--embed` blocks below the recovered web path

Outputs individual rib STLs, a manifest CSV, and one merged STL.
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import os
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

try:
    from shapely.geometry import Polygon, MultiPolygon, GeometryCollection
    from shapely.ops import triangulate
except Exception as e:
    raise SystemExit("This script needs shapely. Install with: python3 -m pip install shapely\n" + str(e))


BOUNDARIES = [0.0, 28.0, 54.0, 78.0, 102.0, 126.0, 152.0, 180.0]
RINGS = {"R0": 2933.0, "R1": 4181.0, "R2": 4901.0, "R3": 5957.0}
CENTERS = [14.0, 41.0, 66.0, 90.0, 114.0, 139.0, 166.0]
BOSSES = {
    "inner": [
        (3348.82,4368.00,834.96),(2615.70,4368.00,2273.79),(1415.15,4368.00,3178.47),
        (0.00,4368.00,3479.27),(-1415.15,4368.00,3178.47),(-2615.70,4368.00,2273.79),(-3348.82,4368.00,834.96)],
    "middle": [
        (4275.23,4512.00,1065.94),(3339.30,4512.00,2902.81),(1806.63,4512.00,4057.76),
        (0.00,4512.00,4441.77),(-1806.63,4512.00,4057.76),(-3339.30,4512.00,2902.81),(-4275.23,4512.00,1065.94)],
    "outer": [
        (5181.21,4480.00,1291.82),(4037.55,4480.00,3509.79),(2179.73,4480.00,4895.75),
        (0.00,4480.00,5359.06),(-2179.73,4480.00,4895.75),(-4037.55,4480.00,3509.79),(-5181.21,4480.00,1291.82)],
}
BAND_ORDER = {"inner":0, "middle":1, "outer":2}


def discover_guide(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if not p.is_file():
            raise SystemExit(f"guide STL not found: {p}")
        return p
    names = [
        "pass6J_7bay_ALL21_PASS7_GOTHIC_RIBS_ONLY.stl",
        "pass6J_7bay_ALL21_PASS7_GOTHIC_RIBS_ONLY(1).stl",
    ]
    roots = [Path.cwd(), Path.home()/"Downloads", Path.home()/"Desktop"]
    for root in roots:
        for name in names:
            p = root/name
            if p.is_file(): return p.resolve()
    raise SystemExit("Pass 6J rib guide STL not found. Use --guide /path/to/pass6J_7bay_ALL21_PASS7_GOTHIC_RIBS_ONLY.stl")


def load_mask(path: Path, threshold: float, invert: bool):
    im = Image.open(path).convert("L")
    a = np.asarray(im, dtype=np.uint8)
    solid = a < int(round(255.0*threshold))
    if invert: solid = ~solid
    rows = np.any(solid, axis=1); cols = np.any(solid, axis=0)
    if not rows.any(): raise SystemExit("profile contains no solid pixels after thresholding")
    r=np.where(rows)[0]; c=np.where(cols)[0]
    solid = solid[r[0]:r[-1]+1, c[0]:c[-1]+1]
    return np.ascontiguousarray(solid)


def mask_contours(mask: np.ndarray):
    # Prefer OpenCV; fall back to scikit-image.
    try:
        import cv2
        cs, _ = cv2.findContours((mask.astype(np.uint8)*255), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        out=[]
        for c in cs:
            q=c[:,0,:].astype(float)
            if len(q)>=3: out.append(q)
        return out
    except Exception:
        try:
            from skimage import measure
        except Exception as e:
            raise SystemExit("Need either opencv-python or scikit-image to trace the PNG profile.\n"
                             "Install one with: python3 -m pip install opencv-python\n" + str(e))
        out=[]
        for c in measure.find_contours(mask.astype(float), 0.5):
            q=np.stack([c[:,1], c[:,0]], axis=1)
            if len(q)>=3: out.append(q)
        return out


def profile_geometry(mask: np.ndarray, ppb: float, embed: float, simplify: float):
    h,w = mask.shape
    contours = mask_contours(mask)
    if not contours: raise SystemExit("could not trace profile boundary")
    geom=None
    for q in contours:
        # pixel center -> block coordinates; image top is positive profile height
        xy=np.empty_like(q, dtype=float)
        xy[:,0]=(q[:,0] + 0.5 - w/2.0)/ppb
        xy[:,1]=(h - (q[:,1] + 0.5))/ppb - embed
        p=Polygon(xy)
        if not p.is_valid: p=p.buffer(0)
        if p.is_empty or p.area<=1e-9: continue
        geom = p if geom is None else geom.symmetric_difference(p)
    if geom is None or geom.is_empty: raise SystemExit("profile tracing produced empty geometry")
    if simplify>0:
        geom=geom.simplify(float(simplify), preserve_topology=True)
    if not geom.is_valid: geom=geom.buffer(0)
    polys=[]
    def collect(g):
        if isinstance(g, Polygon):
            if g.area>1e-8: polys.append(g)
        elif isinstance(g, (MultiPolygon, GeometryCollection)):
            for x in g.geoms: collect(x)
    collect(geom)
    if not polys: raise SystemExit("no usable profile polygons after simplification")
    return polys


def recover_reference_path(comp: trimesh.Trimesh) -> np.ndarray:
    """Recover the exact Pass 7 web-following reference path from one rib solid.

    The locked rib has a 5-vertex pointed section at 340 longitudinal stations.
    Four low-valence vertices identify each cap; graph traversal then recovers
    all 340 section rings. The web path is the midpoint of the two section
    shoulder vertices (the old section had 5-block embed and 24-block rise).
    """
    adj=[set() for _ in range(len(comp.vertices))]
    for a,b in comp.edges_unique:
        a=int(a); b=int(b); adj[a].add(b); adj[b].add(a)
    deg=np.array([len(s) for s in adj])
    special=np.where(deg<6)[0]
    if len(special)!=8:
        raise RuntimeError(f"unexpected guide topology: expected 8 cap-special vertices, got {len(special)}")
    spring4=list(special[np.argsort(comp.vertices[special,1])[:4]])
    cnt=collections.Counter()
    for v in spring4:
        for u in adj[int(v)]:
            if u not in spring4: cnt[u]+=1
    fifth=[int(u) for u,n in cnt.items() if n==4]
    if len(fifth)!=1: raise RuntimeError("could not reconstruct first 5-vertex section ring")
    cur=set([int(v) for v in spring4]+fifth)
    prev=set(); rings=[cur]
    while True:
        nxt=set()
        for v in cur:
            nxt.update(u for u in adj[v] if u not in cur and u not in prev)
        if not nxt: break
        if len(nxt)!=5: raise RuntimeError(f"guide section traversal broke: next ring has {len(nxt)} vertices")
        rings.append(nxt); prev,cur=cur,nxt
        if len(rings)>1000: raise RuntimeError("guide traversal loop")
    if len(rings)!=340:
        raise RuntimeError(f"expected 340 Pass 7 section stations, got {len(rings)}")
    path=[]
    for ring in rings:
        q=np.array([comp.vertices[i] for i in ring], dtype=float)
        d=np.linalg.norm(q[:,None,:]-q[None,:,:], axis=-1)
        apex=int(np.argmax(d.sum(axis=1)))
        others=[i for i in range(5) if i!=apex]
        shoulders=sorted(others, key=lambda i:d[apex,i])[:2]
        path.append(q[shoulders].mean(axis=0))
    return np.asarray(path)


def boss_class(path):
    refs=[]
    for band, arr in BOSSES.items():
        for i,p in enumerate(arr,1): refs.append((band,i,np.asarray(p,float)))
    end=path[-1]
    band,bay,boss=min(refs, key=lambda r:np.linalg.norm(end-r[2]))
    return band,bay,float(np.linalg.norm(end-boss))


def spring_class(path):
    p=path[0]
    r=math.hypot(p[0],p[2])
    a=math.degrees(math.atan2(p[2],p[0]))%360.0
    ring=min(RINGS, key=lambda k:abs(RINGS[k]-r))
    ang=min(BOUNDARIES, key=lambda x:abs(x-a))
    return ring,ang,r,a


def path_frames(path: np.ndarray):
    # Tangent along recovered guide. side is constant horizontal normal to the
    # spring->boss vertical plane; depth stays perpendicular to tangent and side.
    t=np.gradient(path, axis=0)
    t/=np.maximum(np.linalg.norm(t,axis=1)[:,None],1e-12)
    h=path[-1]-path[0]; h[1]=0.0
    h/=max(np.linalg.norm(h),1e-12)
    side=np.array([-h[2],0.0,h[0]], dtype=float)
    side/=max(np.linalg.norm(side),1e-12)
    depth=np.cross(np.repeat(side[None,:],len(path),axis=0), t)
    depth/=np.maximum(np.linalg.norm(depth,axis=1)[:,None],1e-12)
    # Make depth point generally upward/outward.
    flip=depth[:,1].mean()<0
    if flip: depth=-depth
    return t,side,depth


def polygon_loops(poly: Polygon):
    loops=[np.asarray(poly.exterior.coords[:-1], dtype=float)]
    loops += [np.asarray(r.coords[:-1], dtype=float) for r in poly.interiors]
    return [q for q in loops if len(q)>=3]


def cap_triangles_2d(poly: Polygon):
    out=[]
    safe=poly.buffer(1e-9)
    for tri in triangulate(poly):
        if safe.covers(tri):
            q=np.asarray(tri.exterior.coords[:3],dtype=float)
            if len(q)==3: out.append(q)
    return out


def sweep_profile(path: np.ndarray, polys, path_step: int):
    if path_step>1:
        idx=list(range(0,len(path)-1,path_step))
        if idx[-1] != len(path)-1: idx.append(len(path)-1)
        path=path[idx]
    _,side,depth=path_frames(path)
    tris=[]
    for poly in polys:
        loops=polygon_loops(poly)
        # side walls
        for loop in loops:
            u=loop[:,0]; v=loop[:,1]
            stations = path[:,None,:] + u[None,:,None]*side[None,None,:] + v[None,:,None]*depth[:,None,:]
            for i in range(len(path)-1):
                a=stations[i]; b=stations[i+1]
                j=np.arange(len(loop)); k=(j+1)%len(loop)
                tris.append(np.stack([a[j], b[j], b[k]],axis=1))
                tris.append(np.stack([a[j], b[k], a[k]],axis=1))
        # caps
        caps=cap_triangles_2d(poly)
        for local in caps:
            for si,rev in ((0,True),(-1,False)):
                u=local[:,0]; v=local[:,1]
                world=path[si][None,:] + u[:,None]*side[None,:] + v[:,None]*depth[si][None,:]
                if rev: world=world[::-1]
                tris.append(world.reshape(1,3,3))
    if not tris: return np.empty((0,3,3),dtype=np.float32)
    return np.concatenate(tris,axis=0).astype(np.float32)


def write_binary_stl(path: Path, tris: np.ndarray, header=b"Pass6J PNG profile rib"):
    path.parent.mkdir(parents=True,exist_ok=True)
    n=len(tris)
    e1=tris[:,1]-tris[:,0]; e2=tris[:,2]-tris[:,0]
    normals=np.cross(e1,e2)
    norms=np.linalg.norm(normals,axis=1)
    good=norms>1e-12
    normals[good]/=norms[good,None]
    normals[~good]=0
    dtype=np.dtype([('normal','<f4',(3,)),('verts','<f4',(3,3)),('attr','<u2')])
    rec=np.zeros(n,dtype=dtype); rec['normal']=normals.astype(np.float32); rec['verts']=tris
    with path.open('wb') as f:
        f.write(header[:80].ljust(80,b'\0')); f.write(struct.pack('<I',n)); f.write(rec.tobytes())
    return n


def merge_binary_stls(paths, out: Path):
    items=[]; total=0
    for p in paths:
        with open(p,'rb') as f: head=f.read(84)
        if len(head)!=84: raise RuntimeError(f"bad STL {p}")
        n=struct.unpack_from('<I',head,80)[0]
        if os.path.getsize(p)!=84+n*50: raise RuntimeError(f"not binary STL {p}")
        items.append((p,n)); total+=n
    if total>0xFFFFFFFF: raise RuntimeError("merged STL exceeds binary STL triangle count limit")
    with open(out,'wb') as dst:
        dst.write(b'Pass6J merged PNG profile skeleton'.ljust(80,b'\0')); dst.write(struct.pack('<I',total))
        for p,_ in items:
            with open(p,'rb') as src:
                src.seek(84)
                while True:
                    b=src.read(16*1024*1024)
                    if not b: break
                    dst.write(b)
    return total


def main():
    ap=argparse.ArgumentParser(description="Sweep a PNG profile along the locked Pass 6J / Pass 7 rib paths.")
    ap.add_argument('profile', nargs='?', default='sections/PROFILE.png')
    ap.add_argument('--guide', default=None, help='locked 84-rib Pass 7 guide STL')
    ap.add_argument('--out', default='out/pass6J_profile_skeleton')
    ap.add_argument('--ppb', type=float, default=14.0, help='profile pixels per block')
    ap.add_argument('--embed', type=float, default=5.0, help='blocks of profile below recovered web path')
    ap.add_argument('--threshold', type=float, default=0.5)
    ap.add_argument('--invert', action='store_true')
    ap.add_argument('--simplify', type=float, default=0.20, help='profile contour simplification in blocks; 0 disables')
    ap.add_argument('--path-step', type=int, default=1, help='use every Nth recovered guide station; 1 = exact 340-station path')
    ap.add_argument('--limit', type=int, default=0, help='test only first N ribs; 0 = all 84')
    ap.add_argument('--no-merge', action='store_true')
    args=ap.parse_args()
    if args.ppb<=0: ap.error('--ppb must be > 0')
    if args.path_step<1: ap.error('--path-step must be >= 1')
    if not (0<args.threshold<1): ap.error('--threshold must be between 0 and 1')

    profile=Path(args.profile).expanduser().resolve()
    if not profile.is_file(): ap.error(f'profile not found: {profile}')
    guide=discover_guide(args.guide)
    out=Path(args.out).expanduser().resolve(); out.mkdir(parents=True,exist_ok=True)
    parts=out/'ribs'; parts.mkdir(exist_ok=True)

    mask=load_mask(profile,args.threshold,args.invert)
    polys=profile_geometry(mask,args.ppb,args.embed,args.simplify)
    print('Pass 6J profile skeleton')
    print(f'  profile : {profile}')
    print(f'  guide   : {guide}')
    print(f'  ppb     : {args.ppb:g}')
    print(f'  embed   : {args.embed:g}')
    print(f'  profile : {mask.shape[1]/args.ppb:.2f} x {mask.shape[0]/args.ppb:.2f} blocks')
    print(f'  method  : recover locked Pass 7 paths -> sweep PNG profile')

    mesh=trimesh.load(guide, force='mesh', process=True)
    comps=list(mesh.split(only_watertight=False))
    if len(comps)!=84:
        raise SystemExit(f'expected 84 Pass 7 rib solids in guide, found {len(comps)}')

    records=[]
    for c in comps:
        path=recover_reference_path(c)
        band,bay,boss_gap=boss_class(path)
        ring,ang,r,a=spring_class(path)
        records.append((BAND_ORDER[band],bay,ring,ang,path,boss_gap,r,a))
    records.sort(key=lambda x:(x[0],x[1],x[2],x[3]))
    if args.limit>0: records=records[:args.limit]

    written=[]; manifest=[]
    for idx,rec in enumerate(records,1):
        _,bay,ring,ang,path,boss_gap,r,a=rec
        band=[k for k,v in BAND_ORDER.items() if v==rec[0]][0]
        name=f'{band}_B{bay}_{ring}_A{ang:g}'
        tris=sweep_profile(path,polys,args.path_step)
        p=parts/(name+'.stl')
        n=write_binary_stl(p,tris)
        written.append(p)
        length=float(np.linalg.norm(np.diff(path,axis=0),axis=1).sum())
        manifest.append({
            'name':name,'band':band,'bay':bay,'spring_ring':ring,'spring_angle_deg':f'{ang:g}',
            'spring_x':f'{path[0,0]:.6f}','spring_y':f'{path[0,1]:.6f}','spring_z':f'{path[0,2]:.6f}',
            'trimmed_end_x':f'{path[-1,0]:.6f}','trimmed_end_y':f'{path[-1,1]:.6f}','trimmed_end_z':f'{path[-1,2]:.6f}',
            'recovered_stations':len(path),'path_length':f'{length:.6f}','boss_gap':f'{boss_gap:.6f}',
            'triangles':n
        })
        print(f'[{idx:02d}/{len(records)}] {name:24s} {n:,} triangles')

    mf=out/'pass6J_profile_skeleton_manifest.csv'
    with mf.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(manifest[0].keys())); w.writeheader(); w.writerows(manifest)
    print(f'manifest : {mf}')
    if written and not args.no_merge:
        merged=out/'pass6J_profile_skeleton_merged.stl'
        total=merge_binary_stls(written,merged)
        print(f'merged   : {merged} ({total:,} triangles)')
    print(f'finished : {len(written)} locked Pass 6J rib paths')
    return 0

if __name__=='__main__':
    raise SystemExit(main())