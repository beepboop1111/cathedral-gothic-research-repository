"""F5ZP R18 skeleton-first universal vault kernel; synthetic experimental geometry.
Imports R17 two-centred boundary arches READ ONLY. Groins precede web fitting.
"""
import math
from dataclasses import asdict
import r17_core as old
VERSION="R18_SKELETON_FIRST_CIRCULAR_GROINS_V01"

def groin_point(corner,spring,crown,r):
    """Monotone single circular arc; R07 exact when rise >= radial run.
    Shallower vaults place the circle center at boss projection to
    eliminate the R07-like unintentional pre-crown overshoot.
    """
    x,y=map(float,corner);run=math.hypot(x,y);rise=crown-spring
    if run<=1e-8 or rise<=0:raise ValueError("INVALID_GROIN_SPAN_OR_RISE")
    r=float(r)
    if not 0<=r<=1:raise ValueError("GROIN_PARAMETER_OUT_OF_RANGE")
    a=max(run,(run*run+rise*rise)/(2*run))
    b=(run*run+rise*rise-2*a*run)/(2*rise)
    R=math.hypot(a,b);pos=run*r
    z=spring+b+math.sqrt(max(0.,R*R-(pos-a)**2))
    if r==0:z=spring
    if r==1:z=crown
    return ((1-r)*x,(1-r)*y,z)

def web_point(s,C,k,t,r,crown):
    """Exact arch, both independent rib lines, boss, and shared C0 seam."""
    n=len(C);A=C[k];B=C[(k+1)%n]
    x,y,dx,dy,L,rise=old.edge_data(s,A,B)
    t=float(t);r=float(r)
    if not 0<=t<=1 or not 0<=r<=1:raise ValueError("PARAMETER_OUT_OF_RANGE")
    if r==1:return (0.,0.,float(crown))
    if t==0:return groin_point(A,s.spring_Z,crown,r)
    if t==1:return groin_point(B,s.spring_Z,crown,r)
    edge_z=old.true_two_centred_pointed_height(t,L,s.spring_Z,rise)
    if r==0:return (x+t*dx,y+t*dy,edge_z)
    l=groin_point(A,s.spring_Z,crown,r)[2]
    q=groin_point(B,s.spring_Z,crown,r)[2]
    radial=(1-t)*l+t*q
    factor=max(0.,min(1.,(edge_z-s.spring_Z)/(crown-s.spring_Z)))
    z=radial+(crown-radial)*factor*(1-r)**s.meridian_exponent
    z+=s.dome_lift*(crown-z)*math.sin(math.pi*t)**2*math.sin(math.pi*r)**2
    return ((1-r)*(x+t*dx),(1-r)*(y+t*dy),z)

def generate(s,crown):
    s.check();C=old.plan_corners(s);N=s.divisions;n=len(C)
    arches=old.measured_boundary_arches(s)
    apex=max(max(p[2] for p in a["points_xyz"]) for a in arches)
    if crown<apex-1e-8:raise ValueError("CROWN_BELOW_HIGHEST_ARCH_APEX")
    verts=[];faces=[];index={}
    def vi(p):
        key=tuple(round(float(v),8) for v in p)
        if key not in index:index[key]=len(verts);verts.append(tuple(map(float,p)))
        return index[key]
    for k in range(n):
        grid={}
        for j in range(N+1):
            r=j/N
            for i in range(N-j+1):
                t=i/(N-j) if j<N else .5
                grid[j,i]=vi(web_point(s,C,k,t,r,crown))
        for j in range(N):
            for i in range(N-j):
                a,b,c=grid[j,i],grid[j,i+1],grid[j+1,i]
                faces.append((a,c,b))
                if i<N-j-1:faces.append((b,c,grid[j+1,i+1]))
    ribs=[{"id":f"R18_INDEPENDENT_GROIN_{k:02d}",
           "points_xyz":[groin_point(A,s.spring_Z,crown,j/256) for j in range(257)]}
          for k,A in enumerate(C)]
    return {"vertices":verts,"faces":faces,"arches":arches,"ribs":ribs,
       "corners":C,"sectors":n,"divisions":N,"crown_Z":float(crown),
       "apex_Z":float(apex),"web_peak_Z":max(v[2] for v in verts),
       "version":VERSION,"settings":asdict(s)}

def qa(s,d):
    """Verify analytic boundary and independent rib constraints, not architecture."""
    C=d["corners"];crown=d["crown_Z"];n=len(C)
    errs={k:0. for k in ("boundary","rib_left","rib_right","shared_groin","boss",
                        "web_overshoot","web_below_radial_baseline")}
    delta=0.
    for k in range(n):
        A=C[k];B=C[(k+1)%n];L=old.edge_data(s,A,B)[4]
        for j in range(129):
            r=j/128
            for t in (0.,.17,.5,.83,1.):
                p=web_point(s,C,k,t,r,crown)
                if r==0:
                    arch=old.true_two_centred_pointed_height(t,L,s.spring_Z,s.arch_rise_ratio*L)
                    errs["boundary"]=max(errs["boundary"],abs(p[2]-arch))
                if t==0:
                    errs["rib_left"]=max(errs["rib_left"],math.dist(p,groin_point(A,s.spring_Z,crown,r)))
                    delta=max(delta,abs(p[2]-old.interpolated_web_point(s,C,k,0.,r,crown)[2]))
                if t==1:
                    errs["rib_right"]=max(errs["rib_right"],math.dist(p,groin_point(B,s.spring_Z,crown,r)))
                errs["shared_groin"]=max(errs["shared_groin"],math.dist(
                    web_point(s,C,k,1.,r,crown),web_point(s,C,(k+1)%n,0.,r,crown)))
                errs["web_overshoot"]=max(errs["web_overshoot"],p[2]-crown)
                l=groin_point(A,s.spring_Z,crown,r)[2]
                q=groin_point(B,s.spring_Z,crown,r)[2]
                errs["web_below_radial_baseline"]=max(errs["web_below_radial_baseline"],(1-t)*l+t*q-p[2])
        errs["boss"]=max(errs["boss"],math.dist(web_point(s,C,k,.5,1,crown),(0,0,crown)))
    if max(errs.values())>1e-6:raise ValueError("SKELETON_WEB_MISMATCH "+str(errs))
    if d["web_peak_Z"]>crown+1e-6:raise ValueError("WEB_PEAK_ABOVE_BOSS")
    if delta<1e-3:raise ValueError("RIB_NOT_INDEPENDENT_OF_OLD_R17_SURFACE")
    edges={}
    for tri in d["faces"]:
        if len(set(tri))!=3:raise ValueError("DEGENERATE_FACE")
        for x,y in ((tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])):
            key=tuple(sorted((x,y)));edges[key]=edges.get(key,0)+1
    if max(edges.values())>2:raise ValueError("NONMANIFOLD_EDGE")
    Euler=len(d["vertices"])-len(edges)+len(d["faces"])
    if Euler!=1:raise ValueError("NOT_A_DISK")
    if len(d["faces"])!=n*s.divisions**2:raise ValueError("FACE_COUNT")
    return {"status":"GEOMETRIC_QA_PASS_SYNTHETIC","residuals_native":errs,
      "R17_to_R18_groin_max_delta_native":delta,
      "mesh_vertices":len(d["vertices"]),"triangles":len(d["faces"]),
      "Euler_open_intrados":Euler,"boundary_edges":sum(v==1 for v in edges.values()),
      "apex_Z":d["apex_Z"],"crown_Z":crown,"web_peak_Z":d["web_peak_Z"],
      "NOT_VALIDATED":["actual cathedral layout","roof cover","historical rib section",
                       "physical springer joins","structural loads"]}
