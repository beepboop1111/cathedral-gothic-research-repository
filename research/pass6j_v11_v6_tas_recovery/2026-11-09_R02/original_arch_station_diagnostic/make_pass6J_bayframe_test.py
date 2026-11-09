#!/usr/bin/env python3
"""
make_pass6J_bayframe_test.py

Diagnostic Pass 6J structural skeleton pass.

Keeps the locked 84 Pass 6J diagonal half-rib paths, but fixes the springing
behavior and adds the missing bay-boundary arch network used to size the
compound piers.

This script imports make_pass6J_profile_skeleton_face_locked.py from the same
directory. Keep both scripts together.

New geometry in this diagnostic:
  - diagonal ribs: lower end becomes a short straight shaft, then blends gently
    back into the locked guide path
  - 24 radial/transverse arches:
      8 Pass 6J boundary angles x 3 ambulatory spans
  - 28 longitudinal/perimeter arches:
      7 bays x 4 ring lines
  - all boundary arches use pointed two-center geometry with vertical tangents
    at springing
  - every incident member gets its own shaft landing around a common pier core

The boundary-arch crown heights are DIAGNOSTIC, chosen from the locked Pass 6J
boss elevations so we can solve pier spacing before final arch-profile fitting.
"""

from __future__ import annotations
import argparse, math, csv, collections, importlib.util, sys
from pathlib import Path
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
BASE_CANDIDATES = [
    HERE / "make_pass6J_profile_skeleton_face_locked.py",
    HERE / "make_pass6J_profile_skeleton.py",
]
BASE = next((p for p in BASE_CANDIDATES if p.is_file()), None)
if BASE is None:
    raise SystemExit(
        "Put make_pass6J_profile_skeleton_face_locked.py in the same folder "
        "as this script."
    )
spec = importlib.util.spec_from_file_location("pass6j_base", BASE)
B = importlib.util.module_from_spec(spec)
sys.modules["pass6j_base"] = B
spec.loader.exec_module(B)

BOUNDARIES = B.BOUNDARIES
RINGS = B.RINGS
BOSSES = B.BOSSES
BAND_ORDER = B.BAND_ORDER
SPRING_Y = 3000.0

# Diagnostic crown elevations. These preserve the established vertical order
# while we solve plan/springing geometry.
BAND_CROWN_Y = {
    "inner": 4368.0,
    "middle": 4512.0,
    "outer": 4480.0,
}
RING_CROWN_Y = {
    "R0": 4368.0,                 # choir/inner arcade
    "R1": (4368.0 + 4512.0)/2.0, # shared inner/middle edge
    "R2": (4512.0 + 4480.0)/2.0, # shared middle/outer edge
    "R3": 4480.0,                 # outer wall edge
}

def unit_xz(v):
    q=np.array([float(v[0]),0.0,float(v[2])],dtype=float)
    n=float(np.linalg.norm(q))
    if n < 1e-9:
        raise RuntimeError("zero XZ direction")
    return q/n

def pier_point(ring: str, angle_deg: float):
    r=float(RINGS[ring])
    a=math.radians(float(angle_deg))
    return np.array([r*math.cos(a), SPRING_Y, r*math.sin(a)], dtype=float)

def shaft_landing(core, target, radius):
    d=unit_xz(np.asarray(target)-np.asarray(core))
    q=np.asarray(core,dtype=float).copy()
    q += d*float(radius)
    q[1]=core[1]
    return q

def verticalize_start(path, core, target, radius=110.0,
                      straight_height=140.0, blend_height=300.0):
    """Turn the bottom of a rib into a true straight attached shaft.

    From spring_y through straight_height, X/Z are constant at the shaft
    landing. Over the next blend_height, the centerline eases back into the
    untouched locked path. Above that, the Pass 6J guide is exact.
    """
    path=np.asarray(path,dtype=float)
    core=np.asarray(core,dtype=float)
    landing=shaft_landing(core,target,radius)
    out=path.copy()
    rise=np.maximum(out[:,1]-core[1], 0.0)
    h0=max(float(straight_height),0.0)
    h1=h0+max(float(blend_height),1e-6)

    # weight 0 = shaft landing, 1 = original locked path
    w=np.zeros(len(out),dtype=float)
    hi=rise>=h1
    mid=(rise>h0)&(rise<h1)
    w[hi]=1.0
    u=(rise[mid]-h0)/(h1-h0)
    w[mid]=u*u*(3.0-2.0*u)

    out[:,0]=landing[0]*(1.0-w)+path[:,0]*w
    out[:,2]=landing[2]*(1.0-w)+path[:,2]*w

    return out, landing

def verticalize_end(path, core, target, radius=110.0,
                    straight_height=140.0, blend_height=300.0):
    rev=path[::-1].copy()
    out,landing=verticalize_start(
        rev, core, target, radius, straight_height, blend_height
    )
    return out[::-1],landing

def pointed_arch_path(p0, p1, crown_y, n_half=170):
    """Symmetric two-center pointed arch in the vertical plane of p0--p1.

    The circle centers lie on the spring line, so both spring tangents are
    vertical. This is a diagnostic structural arch, not yet a final moulding fit.
    """
    p0=np.asarray(p0,dtype=float)
    p1=np.asarray(p1,dtype=float)
    v=p1-p0
    v[1]=0.0
    L=float(np.linalg.norm(v))
    if L < 1e-9:
        raise RuntimeError("zero arch span")
    d=v/L
    mid=(p0+p1)/2.0
    mid[1]=SPRING_Y
    a=L/2.0
    h=float(crown_y-SPRING_Y)
    if h <= 0:
        raise RuntimeError("crown must be above spring")

    # Circle for left half: center x=c on spring line.
    c=(h*h-a*a)/(2.0*a)
    R=(h*h+a*a)/(2.0*a)
    theta_apex=math.atan2(h,-c)
    # Left spring theta=pi -> apex theta_apex.
    th=np.linspace(math.pi,theta_apex,int(n_half)+1)
    x_left=c+R*np.cos(th)
    y_left=R*np.sin(th)

    left=np.empty((len(th),3),dtype=float)
    left[:]=mid
    left += x_left[:,None]*d[None,:]
    left[:,1]=SPRING_Y+y_left

    # Mirror left half about midpoint to make apex->right spring.
    right=left[-2::-1].copy()
    right[:,0]=2.0*mid[0]-right[:,0]
    right[:,2]=2.0*mid[2]-right[:,2]

    path=np.vstack([left,right])
    path[0]=p0
    path[-1]=p1
    apex_i=len(left)-1
    path[apex_i]=np.array([mid[0],crown_y,mid[2]],dtype=float)
    return path, path[apex_i].copy()

def build_profile(profile, ppb, embed, threshold, invert, simplify, rotate):
    mask=B.load_mask(profile,threshold,invert)
    mask=B.rotate_mask_quarter_turns(mask,rotate)
    return B.profile_geometry(mask,ppb,embed,simplify)

def merge(paths, out):
    return B.merge_binary_stls(paths,out)

def member_bearing(core, landing):
    d=landing-core
    return math.degrees(math.atan2(d[2],d[0]))%360.0

def main():
    ap=argparse.ArgumentParser(
        description="Pass 6J diagnostic with true shaft transitions + bay boundary arches."
    )
    ap.add_argument("profile", nargs="?", default="sections/PROFILE.png")
    ap.add_argument("--guide", default=None)
    ap.add_argument("--out", default="out/pass6J_bayframe_test")
    ap.add_argument("--ppb", type=float, default=14.0)
    ap.add_argument("--embed", type=float, default=5.0)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--invert", action="store_true")
    ap.add_argument("--simplify", type=float, default=0.20)
    ap.add_argument("--path-step", type=int, default=2)
    ap.add_argument("--profile-rotate", type=int, choices=(0,90,180,270), default=90)
    ap.add_argument("--shaft-radius", type=float, default=110.0,
                    help="center-to-center radius of attached shaft cluster around each pier core")
    ap.add_argument("--shaft-straight-height", type=float, default=140.0,
                    help="height above springing kept perfectly straight/vertical")
    ap.add_argument("--shaft-blend-height", type=float, default=300.0,
                    help="height used to blend from straight shaft back to locked rib path")
    ap.add_argument("--arch-half-stations", type=int, default=170)
    ap.add_argument("--no-longitudinal", action="store_true")
    ap.add_argument("--no-transverse", action="store_true")
    args=ap.parse_args()

    if args.ppb<=0 or args.path_step<1 or args.shaft_radius<0:
        ap.error("invalid numeric option")
    if args.shaft_straight_height<0 or args.shaft_blend_height<=0:
        ap.error("invalid shaft heights")

    profile=Path(args.profile).expanduser().resolve()
    guide=B.discover_guide(args.guide)
    out=Path(args.out).expanduser().resolve()
    diag_dir=out/"diagonal_ribs"
    trans_dir=out/"transverse_arches"
    long_dir=out/"longitudinal_arches"
    for d in (out,diag_dir,trans_dir,long_dir):
        d.mkdir(parents=True,exist_ok=True)

    polys=build_profile(
        profile,args.ppb,args.embed,args.threshold,args.invert,
        args.simplify,args.profile_rotate
    )

    mesh=trimesh.load(guide,force="mesh",process=True)
    comps=list(mesh.split(only_watertight=False))
    if len(comps)!=84:
        raise SystemExit(f"expected 84 locked guide ribs; found {len(comps)}")

    diagonal_records=[]
    for c in comps:
        path=B.recover_reference_path(c)
        band,bay,boss,boss_gap=B.boss_class(path)
        ring,ang,_,_=B.spring_class(path)
        diagonal_records.append(
            (BAND_ORDER[band],bay,ring,float(ang),path,boss,boss_gap)
        )
    diagonal_records.sort(key=lambda x:(x[0],x[1],x[2],x[3]))

    all_stls=[]
    diag_stls=[]
    trans_stls=[]
    long_stls=[]
    landings=[]

    # 84 locked diagonal half-ribs.
    for idx,rec in enumerate(diagonal_records,1):
        order,bay,ring,ang,path,boss,boss_gap=rec
        band=[k for k,v in BAND_ORDER.items() if v==order][0]
        core=path[0].copy()
        shafted,landing=verticalize_start(
            path,core,boss,args.shaft_radius,
            args.shaft_straight_height,args.shaft_blend_height
        )
        joined,_=B.extend_path_to_boss(shafted,boss,0.0,8)
        tris=B.sweep_profile(joined,polys,args.path_step,boss,"crown-down")
        name=f"diag_{band}_B{bay}_{ring}_A{ang:g}"
        p=diag_dir/(name+".stl")
        B.write_binary_stl(p,tris)
        diag_stls.append(p); all_stls.append(p)
        landings.append({
            "pier_ring":ring,"pier_angle_deg":ang,"member_type":"diagonal",
            "member_name":name,"shaft_x":landing[0],"shaft_y":landing[1],"shaft_z":landing[2],
            "bearing_deg":member_bearing(core,landing)
        })

    # 24 radial / transverse arches: one at every boundary, across each band.
    if not args.no_transverse:
        spans=[
            ("inner","R0","R1"),
            ("middle","R1","R2"),
            ("outer","R2","R3"),
        ]
        for ang in BOUNDARIES:
            for band,r0,r1 in spans:
                p0=pier_point(r0,ang); p1=pier_point(r1,ang)
                raw,apex=pointed_arch_path(
                    p0,p1,BAND_CROWN_Y[band],args.arch_half_stations
                )
                a0,l0=verticalize_start(
                    raw,p0,p1,args.shaft_radius,
                    args.shaft_straight_height,args.shaft_blend_height
                )
                a1,l1=verticalize_end(
                    a0,p1,p0,args.shaft_radius,
                    args.shaft_straight_height,args.shaft_blend_height
                )
                tris=B.sweep_profile(a1,polys,args.path_step,apex,"crown-down")
                name=f"trans_{band}_A{ang:g}_{r0}_{r1}"
                p=trans_dir/(name+".stl")
                B.write_binary_stl(p,tris)
                trans_stls.append(p); all_stls.append(p)
                landings.extend([
                    {"pier_ring":r0,"pier_angle_deg":float(ang),"member_type":"transverse",
                     "member_name":name+":start","shaft_x":l0[0],"shaft_y":l0[1],"shaft_z":l0[2],
                     "bearing_deg":member_bearing(p0,l0)},
                    {"pier_ring":r1,"pier_angle_deg":float(ang),"member_type":"transverse",
                     "member_name":name+":end","shaft_x":l1[0],"shaft_y":l1[1],"shaft_z":l1[2],
                     "bearing_deg":member_bearing(p1,l1)},
                ])

    # 28 longitudinal / perimeter arches: seven bay intervals along four ring lines.
    if not args.no_longitudinal:
        for bi in range(7):
            a0=float(BOUNDARIES[bi]); a1=float(BOUNDARIES[bi+1])
            for ring in ("R0","R1","R2","R3"):
                p0=pier_point(ring,a0); p1=pier_point(ring,a1)
                raw,apex=pointed_arch_path(
                    p0,p1,RING_CROWN_Y[ring],args.arch_half_stations
                )
                q0,l0=verticalize_start(
                    raw,p0,p1,args.shaft_radius,
                    args.shaft_straight_height,args.shaft_blend_height
                )
                q1,l1=verticalize_end(
                    q0,p1,p0,args.shaft_radius,
                    args.shaft_straight_height,args.shaft_blend_height
                )
                tris=B.sweep_profile(q1,polys,args.path_step,apex,"crown-down")
                name=f"long_{ring}_B{bi+1}_A{a0:g}_{a1:g}"
                p=long_dir/(name+".stl")
                B.write_binary_stl(p,tris)
                long_stls.append(p); all_stls.append(p)
                landings.extend([
                    {"pier_ring":ring,"pier_angle_deg":a0,"member_type":"longitudinal",
                     "member_name":name+":start","shaft_x":l0[0],"shaft_y":l0[1],"shaft_z":l0[2],
                     "bearing_deg":member_bearing(p0,l0)},
                    {"pier_ring":ring,"pier_angle_deg":a1,"member_type":"longitudinal",
                     "member_name":name+":end","shaft_x":l1[0],"shaft_y":l1[1],"shaft_z":l1[2],
                     "bearing_deg":member_bearing(p1,l1)},
                ])

    # Merged togglable sets.
    if diag_stls:
        merge(diag_stls,out/"pass6J_DIAGONALS_SHAFTED.stl")
    if trans_stls:
        merge(trans_stls,out/"pass6J_TRANSVERSE_ARCHES_ONLY.stl")
    if long_stls:
        merge(long_stls,out/"pass6J_LONGITUDINAL_ARCHES_ONLY.stl")
    frame_stls=trans_stls+long_stls
    if frame_stls:
        merge(frame_stls,out/"pass6J_BAY_BOUNDARY_ARCHES_ONLY.stl")
    merge(all_stls,out/"pass6J_COMPLETE_RIB_ARCH_SKELETON.stl")

    # Landing map and pier summary: this is what we will use to size the piers.
    lf=out/"pass6J_pier_shaft_landings.csv"
    with lf.open("w",newline="") as f:
        fields=["pier_ring","pier_angle_deg","member_type","member_name",
                "shaft_x","shaft_y","shaft_z","bearing_deg"]
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for row in landings:
            w.writerow(row)

    grouped=collections.defaultdict(list)
    for row in landings:
        grouped[(row["pier_ring"],float(row["pier_angle_deg"]))].append(row)

    sf=out/"pass6J_pier_summary.csv"
    summary=[]
    for (ring,ang),rows in sorted(grouped.items(),key=lambda kv:(kv[0][0],kv[0][1])):
        pts=np.array([[r["shaft_x"],r["shaft_z"]] for r in rows],dtype=float)
        max_pair=0.0
        for i in range(len(pts)):
            if i+1<len(pts):
                max_pair=max(max_pair,float(np.max(np.linalg.norm(pts[i+1:]-pts[i],axis=1))))
        kinds=collections.Counter(r["member_type"] for r in rows)
        summary.append({
            "pier_ring":ring,"pier_angle_deg":ang,"member_count":len(rows),
            "diagonal_count":kinds.get("diagonal",0),
            "transverse_count":kinds.get("transverse",0),
            "longitudinal_count":kinds.get("longitudinal",0),
            "max_shaft_center_span":max_pair,
            "suggested_min_envelope_with_52block_profile":max_pair+52.0,
        })
    with sf.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0].keys())); w.writeheader(); w.writerows(summary)

    print("Pass 6J bay-frame diagnostic complete")
    print(f"  diagonals          : {len(diag_stls)}")
    print(f"  transverse arches : {len(trans_stls)}")
    print(f"  longitudinal      : {len(long_stls)}")
    print(f"  total solids       : {len(all_stls)}")
    print(f"  landing map        : {lf}")
    print(f"  pier summary       : {sf}")
    print(f"  combined           : {out/'pass6J_COMPLETE_RIB_ARCH_SKELETON.stl'}")

if __name__=="__main__":
    raise SystemExit(main())