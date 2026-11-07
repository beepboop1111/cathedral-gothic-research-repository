#!/usr/bin/env python3
"""R07: experimental 1:1 paired-flyer test, read-only source R21 B.
F5ZP is Y-up; actual trial piers/pads and 90-degree vaults are unmodified.
Figure 892 source-fit normalized elevation is MORPHED to trial bearing heights;
not calibrated historical radius, section, support or structural validation.
"""
from pathlib import Path
import hashlib,json,math
import numpy as np
import trimesh
from shapely.geometry import MultiPoint
SRC=Path('/home/christopher/Desktop/F5ZP_M01_R21_EXPERIMENTAL_20261105/F5ZP_M01_R21_B_EXPERIMENTAL.glb')
OUT=Path('/home/christopher/Desktop/F5ZP_BUTTRESS_R07_TESTBAY_EXPERIMENTAL/F5ZP_R07_CHEVET_90_PAIRED_FLYERS_1TO1_EXPERIMENTAL.glb')
OUT.parent.mkdir(parents=True,exist_ok=True)
# Values represent measured normalized profile from R05 source-guided Ungewitter fig 892.
ZFORM=np.array([0,.05375,.10934,.16390,.21605,.26730,.31730,.36643,.41467,.46140,.50698,.55166,.59438,.63626,.67628,.71297,.73628,.76334,.79666,.82674,.85521,.88158,.90654,.92943,.95009,.968,.9842,.99698,1.0],float)
src=trimesh.load(SRC,force='scene')
out=trimesh.Scene(base_frame='world')
source_names=['R21_WEB_90_A','R21_WEB_90_B','R21_INWARD_ARCH_90','R21_CROWN_RIDGE_90','R21_BOSS_90_A','R21_BOSS_90_B','R17_POINTED_O_90','AMB_MIDDLE_A4_1to1_SPRING_POLYGON_SNAPSHOT']
for side in ('A','B'):
    source_names+=['R21_OGIVE_90_'+side+'_0','R21_OGIVE_90_'+side+'_1']
source_names+=['PIER_CORE_R5285_A78p0_SNAPSHOT','PIER_CORE_R5285_A102p0_SNAPSHOT','TRIAL_PAD_O_80','TRIAL_PAD_O_100']
def getnode(name):
    matrix,g=src.graph[name];mesh=src.geometry[g].copy()
    mesh.apply_transform(matrix)
    return mesh
def add(mesh,name,rgb):
    mesh.visual.face_colors=np.array([*rgb,255],dtype=np.uint8)
    out.add_geometry(mesh,geom_name=name,node_name=name)
for name in source_names:
    mesh=getnode(name)
    color=(174,174,176) if ('WEB' in name or 'ARCH' in name or 'OGIVE' in name or 'BOSS' in name) else (197,183,158)
    if 'TRIAL_' in name or 'PIER_' in name:color=(156,172,178)
    add(mesh,'R21_SOURCE_'+name,color)
def box(x0,x1,y0,y1,z0,z1):
    mesh=trimesh.creation.box(extents=(x1-x0,y1-y0,z1-z0))
    mesh.apply_translation(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
    return mesh
def mesh_strip(a,b):
    # Four corners at each station, rectangle in (Y,Z), connected as solid.
    def section(p):
        x,y,z,t,w=p
        return np.array([[x,y-t/2,z-w/2],[x,y-t/2,z+w/2],
                         [x,y+t/2,z+w/2],[x,y+t/2,z-w/2]],float)
    v=np.vstack((section(a),section(b)))
    f=np.array([(0,2,1),(0,3,2),(4,5,6),(4,6,7),
                (0,1,5),(0,5,4),(1,2,6),(1,6,5),
                (2,3,7),(2,7,6),(3,0,4),(3,4,7)],dtype=int)
    mesh=trimesh.Trimesh(vertices=v,faces=f,process=True)
    mesh.fix_normals()
    if not mesh.is_watertight or not mesh.is_volume:raise ValueError('Invalid arch strip')
    return mesh
def support_overlap(a,b):
    # Both real trial supports are vertical extrusions of planar convex sections.
    # For these sections, convex XZ footprints times overlap in height gives
    # study-only contact. The full cathedral meshes are NOT all manifold.
    ah=MultiPoint(a.vertices[:,[0,2]]).convex_hull
    bh=MultiPoint(b.vertices[:,[0,2]]).convex_hull
    ym=max(0.,min(a.bounds[1,1],b.bounds[1,1])-max(a.bounds[0,1],b.bounds[0,1]))
    return float(ah.intersection(bh).area*ym)
metrics={}
new=[]
for sign,label,core,pad in [(-1,'90_A','PIER_CORE_R5285_A78p0_SNAPSHOT','TRIAL_PAD_O_80'),
                            (1,'90_B','PIER_CORE_R5285_A102p0_SNAPSHOT','TRIAL_PAD_O_100')]:
    coremesh=getnode(core);padmesh=getnode(pad)
    core_c=coremesh.bounds.mean(axis=0)[2]
    pad_c=padmesh.bounds.mean(axis=0)[2]
    # Adjust to observed saved support footprints; do not assign approval.
    # The boundary-flyer stays tangentially beyond the saved bay web edge.
    in_z=core_c+sign*83.0
    out_z=pad_c+sign*75.0
    inner_seat=box(25390,25465,2815,3000,in_z-31,in_z+31)
    outer_seat=box(26620,26730,2420,2620,out_z-60,out_z+60)
    adds=[(inner_seat,'EXP_INNER_RECEIVING_SEAT',(221,170,94)),
          (outer_seat,'EXP_OUTER_RECEIVING_SEAT',(221,170,94))]
    # Insert 28 separately identifiable voussoirs with fine open joints.
    def station(t):
        k=float(np.interp(t,np.linspace(0,1,len(ZFORM)),ZFORM))
        x=26685+(25430-26685)*t
        y=2530+(2910-2530)*k
        z=out_z+(in_z-out_z)*t+sign*28*math.sin(math.pi*t)
        return [x,y,z,110-32*t,80-30*t]
    voussoirs=[]
    for i in range(28):
        p=station((i+0.004)/28);q=station((i+0.996)/28)
        v=mesh_strip(p,q)
        adds.append((v,f'EXP_VOUSSOIR_{i:02d}',(171,127,90)))
        voussoirs.append(v)
    # Remove masonry bodies from core of the reserved vault; only seats proposed.
    for mesh,key,color in adds:
        name=f'R07_{label}_{key}'
        add(mesh,name,color)
        new.append(name)
    metrics[label]={
       'real_reference_core':core,'real_reference_pad':pad,
       'core_center_native':np.round(coremesh.bounds.mean(axis=0),3).tolist(),
       'pad_center_native':np.round(padmesh.bounds.mean(axis=0),3).tolist(),
       'seat_to_trial_core_overlap_u3':support_overlap(inner_seat,coremesh),
       'seat_to_trial_pad_overlap_u3':support_overlap(outer_seat,padmesh),
       'first_voussoir_to_outer_seat_overlap_u3':support_overlap(voussoirs[0],outer_seat),
       'last_voussoir_to_inner_seat_overlap_u3':support_overlap(voussoirs[-1],inner_seat),
       'new_component_watertight':all(m.is_watertight and m.is_volume for m,_,_ in adds),
       'new_min_tangential_coordinate':float(min(v.bounds[0,2] for v in voussoirs)),
       'new_max_tangential_coordinate':float(max(v.bounds[1,2] for v in voussoirs)),
    }
critical=[k for p in metrics.values() for k in ['seat_to_trial_core_overlap_u3','seat_to_trial_pad_overlap_u3','first_voussoir_to_outer_seat_overlap_u3','last_voussoir_to_inner_seat_overlap_u3'] if p[k]<=0]
if critical:raise RuntimeError('Nonpositive contact: '+str(critical))
out.export(OUT)
chk=trimesh.load(OUT,force='scene')
assert len(chk.graph.nodes_geometry)==len(source_names)+len(new)
assert all(np.isfinite(mesh.vertices).all() for mesh in chk.geometry.values())
# All recovered protected-reference meshes are transformed but geometrically identical:
for key in source_names:
    m=getnode(key);n=chk.geometry[chk.graph['R21_SOURCE_'+key][1]]
    assert np.allclose(m.bounds,n.bounds,atol=.02)
print(json.dumps({'output':str(OUT),'bytes':OUT.stat().st_size,
 'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
 'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
 'native_coordinate_system':'1:1 native F5ZP, Y is elevation',
 'source_reference_components':len(source_names),'new_experimental_components':len(new),
 'roundtrip_components':len(chk.graph.nodes_geometry),'bearing_metrics':metrics,
 'geometry_status':'EXPERIMENTAL; F5ZL-C unsupported; collision and structural capacity not certified',
 'historical_status':'figure892 normalized curvature MORPHED to test height, NOT calibrated plate reproduction'},indent=2))
