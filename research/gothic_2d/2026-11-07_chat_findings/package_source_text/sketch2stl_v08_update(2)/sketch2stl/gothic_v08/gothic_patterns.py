"""Parametric Gothic construction modules and rigid propagation.

A SOURCE-derived representative unit stays unchanged; generated instances are
transforms, with ornament/animal-head slots kept independent of symmetry.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np


def transform_points(points, matrix):
    pts=np.asarray(points,float)
    if pts.ndim!=2 or pts.shape[1]!=2:raise ValueError('Expected Nx2 points')
    h=np.column_stack((pts,np.ones(len(pts))))
    m=np.asarray(matrix,float)
    if m.shape!=(3,3):raise ValueError('Expected 3x3 affine matrix')
    return (h@m.T)[:,:2]


def rotate_about(origin,angle_degrees):
    x,y=origin;a=math.radians(angle_degrees);c=math.cos(a);s=math.sin(a)
    return np.array([[c,-s,x-c*x+s*y],[s,c,y-s*x-c*y],[0,0,1.]],float)


def translate(dx,dy):
    return np.array([[1.,0.,dx],[0.,1.,dy],[0.,0.,1.]])


def mirror_about_x(x=0.):
    return np.array([[-1.,0.,2*x],[0.,1.,0.],[0.,0.,1.]])


def radial_instances(origin,count=8,master_index=0,selected=None):
    """Image-Y-down positive angle convention; count modules at 360/count."""
    if not 2<=count<=256 or not 0<=master_index<count:raise ValueError('Bad radial setup')
    picks=list(range(count)) if selected is None else sorted(set(selected))
    if not picks or any(i<0 or i>=count for i in picks):raise ValueError('Bad selected sectors')
    return [dict(index=i,rotation_degrees=(i-master_index)*360./count,
                 transform=rotate_about(origin,(i-master_index)*360./count).tolist(),
                 source_master_index=master_index) for i in picks]


def linear_instances(dx,dy,count):
    if not 1<=count<=10000:raise ValueError('Bad count')
    return [dict(index=i,transform=translate(dx*i,dy*i).tolist()) for i in range(count)]


def instantiate_points(master_points,instances):
    return [dict(index=inst['index'],points=transform_points(master_points,inst['transform']).tolist())
            for inst in instances]


def preserve_unique_decorations(positions):
    """Keep distinct decoration slots as identities, never clone head sculpture."""
    return [dict(id=i,position=list(map(float,p)),geometry=None,
                 status='unmodeled_individual_decoration') for i,p in enumerate(positions)]
