"""Reusable analytic lines, circular arcs, and conservative contour joins.

V08 core extracts functions suitable for plate and architectural drawings.
These are mathematical candidates, not certified medieval constructions.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from math import atan2, degrees, acos, pi
import numpy as np
from scipy.spatial import cKDTree

@dataclass(frozen=True)
class CircleFit:
    center: tuple[float,float]
    radius: float
    rmse: float
    n_points: int
    interpretation: str = 'analytical_candidate_not_historical_proof'


def circle_fit(points):
    p=np.asarray(points,dtype=float)
    if p.ndim!=2 or p.shape[1]!=2 or len(p)<3:raise ValueError('Need >=3 XY points')
    a=np.column_stack((2*p[:,0],2*p[:,1],np.ones(len(p))))
    if np.linalg.matrix_rank(a)<3:raise ValueError('Collinear data cannot determine circle')
    solution=np.linalg.lstsq(a,np.sum(p*p,axis=1),rcond=None)[0]
    center=solution[:2]
    radius=float(np.sqrt(max(0.,solution[2]+np.dot(center,center))))
    distances=np.linalg.norm(p-center,axis=1)
    rmse=float(np.sqrt(np.mean((distances-radius)**2)))
    return CircleFit(tuple(map(float,center)),radius,rmse,len(p))


def sample_arc(center,radius,start_deg,end_deg,n=128):
    if radius<=0 or n<2 or not 0<abs(end_deg-start_deg)<360:
        raise ValueError('Bad circle arc')
    theta=np.deg2rad(np.linspace(start_deg,end_deg,n))
    return np.asarray(center)+radius*np.column_stack((np.cos(theta),np.sin(theta)))


def _unit(v):
    n=float(np.linalg.norm(v))
    if n<1e-9:raise ValueError('Zero-length tangent')
    return v/n


def joining_candidates(paths,max_gap=5.0,max_turn_degrees=20.0,ambiguity_margin=0.20):
    """Conservative end-to-end links with tangent and competing-match rejection.

    Returns LINKS only; does not assert closed patterns or erase branching evidence.
    Paths are ordered sequences of points with at least two distinct samples.
    """
    if max_gap<=0 or not 0<max_turn_degrees<=180:raise ValueError('Bad limits')
    endpoints=[]
    for index,path in enumerate(paths):
        p=np.asarray(path,float)
        if len(p)<2:continue
        for side in (0,1):
            pos=p[0] if side==0 else p[-1]
            away=p[1]-p[0] if side==0 else p[-2]-p[-1]
            if np.linalg.norm(away)>1e-9:
                endpoints.append((index,side,pos,_unit(away)))
    if len(endpoints)<2:return []
    pairs=cKDTree(np.stack([e[2] for e in endpoints])).query_pairs(max_gap)
    proposals={}
    for a,b in pairs:
        ea,eb=endpoints[a],endpoints[b]
        if ea[0]==eb[0]:continue
        turn=degrees(acos(float(np.clip(np.dot(ea[3],-eb[3]),-1,1))))
        if turn>max_turn_degrees:continue
        gap=float(np.linalg.norm(ea[2]-eb[2]))
        # Disallow parallel side-by-side strokes: the gap direction must
        # roughly follow both endpoint tangents, except at near-zero gaps.
        if gap>1.0:
            v=(eb[2]-ea[2])/gap
            if np.dot(-ea[3],v)<0.45 or np.dot(eb[3],v)<0.45:continue
        score=gap/max_gap+turn/max_turn_degrees
        proposals.setdefault(a,[]).append((score,b,gap,turn))
        proposals.setdefault(b,[]).append((score,a,gap,turn))
    unique={}
    for i,items in proposals.items():
        items.sort()
        if len(items)>1 and items[1][0]-items[0][0]<ambiguity_margin:continue
        unique[i]=items[0]
    out=[]
    for i,(score,j,gap,turn) in unique.items():
        if i<j and j in unique and unique[j][1]==i:
            out.append(dict(a=list(endpoints[i][:2]),b=list(endpoints[j][:2]),
                            gap=gap,tangent_mismatch_degrees=turn,
                            status='unapproved_candidate'))
    return sorted(out,key=lambda x:(x['a'],x['b']))


def repeated_radius_groups(fits,relative_tolerance=0.075,min_count=2):
    """Find approximate repeated-radii groups; not historical design attribution."""
    records=sorted(enumerate(fits),key=lambda x:x[1].radius)
    groups=[];used=set()
    for i,(idx,fit) in enumerate(records):
        if idx in used:continue
        group=[idx]
        for j,(other_idx,other) in enumerate(records[i+1:],i+1):
            if other_idx not in used and abs(other.radius-fit.radius)<=relative_tolerance*fit.radius:
                group.append(other_idx)
        if len(group)>=min_count:
            groups.append(dict(members=group,mean_radius=float(np.mean([fits[k].radius for k in group])),
                               status='candidate'))
            used.update(group)
    return groups
