"""F5ZP R17 pure procedural Gothic test vault kernel.
Constrained reusable testing geometry, NOT historical cathedral reconstruction.
Uses two-centred pointed boundary arcs, independent boss, radial groins,
smooth interpolated web; no approved geometry is edited or imported.
"""
from __future__ import annotations
import math,hashlib,json
from dataclasses import dataclass,asdict

FAMILIES={"TRI":3,"QUAD":4,"PENTA":5,"HEXA":6,"OCTA":8}
QUALITY_DIVISIONS={"FAST":32,"FINAL":128}
ALGORITHM_VERSION="R17_FAN_POINTED_ARCH_INDEPENDENT_BOSS_01"

@dataclass
class Settings:
    vault_type:str="QUAD"
    custom_sectors:int=7
    quality:str="FAST"
    radius:float=1200.
    spring_Z:float=3000.
    arch_rise_ratio:float=0.72
    crown_mode:str="AUTO"
    crown_Z:float=4400.
    crown_locked:bool=False
    irregularity:float=0.
    rotation_degrees:float=0.
    meridian_exponent:float=1.75
    dome_lift:float=0.3
    cap_enabled:bool=False
    cap_Z:float=4700.
    def check(self):
        n=self.sector_count
        if not (3<=n<=12):raise ValueError("sector count 3..12")
        if self.quality not in QUALITY_DIVISIONS:raise ValueError("unknown quality")
        if self.crown_mode not in ("AUTO","MANUAL","LEVEL"):
            raise ValueError("unknown crown mode")
        if self.crown_locked and self.crown_mode!="MANUAL":
            raise ValueError("LOCKED_CROWN_MUST_BE_MANUALLY_SPECIFIED; do not autoselect")
        if not (self.radius>10 and math.isfinite(self.radius)):
            raise ValueError("radius invalid")
        if not (self.arch_rise_ratio>.5 and self.arch_rise_ratio<=1.25):
            raise ValueError("two-centred Gothic arch rise/chord must exceed 1/2")
        if not (0<=self.irregularity<=.25 and 1.1<=self.meridian_exponent<=4.):
            raise ValueError("irregularity or meridian exponent out of bounds")
        if not (0<=self.dome_lift<=.85):raise ValueError("dome lift out of bounds")
        if not all(math.isfinite(x) for x in (self.spring_Z,self.crown_Z,
            self.rotation_degrees,self.cap_Z)):raise ValueError("nonfinite value")
        return self
    @property
    def sector_count(self):
        return FAMILIES.get(self.vault_type,self.custom_sectors)
    @property
    def divisions(self):
        return QUALITY_DIVISIONS[self.quality]

def canonical_hash(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,
            separators=(",",":"),allow_nan=False).encode()).hexdigest()

def plan_corners(settings):
    settings.check();n=settings.sector_count
    corners=[]
    for k in range(n):
        # Fixed analytic perturbations avoid irregular hardcoded vertex arrays.
        angle=(2*math.pi*k/n+math.radians(settings.rotation_degrees)
               +settings.irregularity*.18*math.sin(2*math.pi*k/n+0.3))
        r=settings.radius*(1+settings.irregularity*math.cos(
            2*math.pi*k/n+0.51))
        corners.append((r*math.cos(angle),r*math.sin(angle)))
    return corners

def true_two_centred_pointed_height(u,chord_length,spring,rise):
    """Two circular arc segments meeting with a central pointed cusp."""
    x=min(max(0.,float(u)),1.)
    h=float(rise)
    L=float(chord_length)
    if h<=L/2:raise ValueError("pointed arch must rise > half span")
    c=L/4+h*h/L
    # Center lies at horizontal springing elevation on each side.
    d=L*min(x,1-x)
    z2=c*c-(d-c)**2
    if z2 < -1e-7:raise ValueError("invalid Gothic circle set-out")
    return spring+math.sqrt(max(z2,0.))

def edge_data(settings,corner_A,corner_B):
    x0,y0=corner_A;x1,y1=corner_B
    dx=x1-x0;dy=y1-y0
    L=math.hypot(dx,dy);rise=settings.arch_rise_ratio*L
    if rise<=L/2:raise ValueError("not pointed arch")
    return (x0,y0,dx,dy,L,rise)

def measured_boundary_arches(settings,points_per_arch=257):
    corners=plan_corners(settings)
    result=[];s=settings.spring_Z
    for k,A in enumerate(corners):
        B=corners[(k+1)%len(corners)]
        x,y,dx,dy,L,rise=edge_data(settings,A,B)
        samples=[]
        for m in range(points_per_arch):
            t=m/(points_per_arch-1)
            samples.append([x+t*dx,y+t*dy,
                 true_two_centred_pointed_height(t,L,s,rise)])
        result.append({"id":f"R17_EDGE_{k:02d}","points_xyz":samples})
    return result

def interpolated_web_point(settings,corners,k,t,r,crown):
    """Parametric triangular web; t=0/1 are exact ribs, r=0 arch, r=1 boss.
    Radial convex mixing between original boundary and independent boss;
    dome_lift is bounded so no sag below original arch at matching t.
    """
    n=len(corners);A=corners[k];B=corners[(k+1)%n]
    x0,y0,dx,dy,L,rise=edge_data(settings,A,B)
    t=float(t);r=float(r)
    ex=x0+t*dx;ey=y0+t*dy
    x=(1-r)*ex;y=(1-r)*ey
    z_edge=true_two_centred_pointed_height(t,L,settings.spring_Z,rise)
    w=(1-r)**settings.meridian_exponent
    base=w*z_edge+(1-w)*crown
    lift=settings.dome_lift*(crown-base)*(math.sin(math.pi*t)**2)*(
         math.sin(math.pi*r)**2)
    return (x,y,base+lift)

def build_mesh_data(settings,crown):
    """Generate a single welded open-intrados mesh, plus skeleton paths.
    All mesh coordinates are full native 1:1 units; no scaling corrections.
    """
    settings.check();corners=plan_corners(settings)
    n=len(corners);N=settings.divisions
    vertices=[];faces=[];index={}
    def vi(p):
        key=tuple(round(float(v),7) for v in p)
        if key not in index:
            index[key]=len(vertices)
            vertices.append(tuple(float(x) for x in p))
        return index[key]
    for k in range(n):
        grid={}
        for j in range(N+1):
            r=j/N
            for i in range(N-j+1):
                t=i/(N-j) if j<N else .5
                grid[j,i]=vi(interpolated_web_point(settings,corners,k,t,r,crown))
        for j in range(N):
            for i in range(N-j):
                a=grid[j,i];b=grid[j,i+1];c=grid[j+1,i]
                faces.append((a,c,b))
                if i<N-j-1:
                    d=grid[j+1,i+1]
                    faces.append((b,c,d))
    arches=measured_boundary_arches(settings)
    ribs=[]
    for k,A in enumerate(corners):
        ribs.append({"id":f"R17_RADIAL_GROIN_{k:02d}",
            "points_xyz":[list(interpolated_web_point(
                settings,corners,k,0.,j/128,crown)) for j in range(129)]})
    # Every shared edge must be sampled exactly from both neighboring sectors.
    max_gap=0.
    for k in range(n):
        for j in range(129):
            r=j/128
            a=interpolated_web_point(settings,corners,k,1.,r,crown)
            b=interpolated_web_point(settings,corners,(k+1)%n,0.,r,crown)
            max_gap=max(max_gap,math.dist(a,b))
    if max_gap>1e-7:raise ValueError("R17_GROIN_SEAM_MISMATCH "+str(max_gap))
    # Front-facing intrados normals are downward by construction.
    if any(not math.isfinite(x) for p in vertices for x in p):
        raise ValueError("nonfinite vertices")
    webpeak=max(p[2] for p in vertices)
    return {"vertices":vertices,"faces":faces,"arches":arches,"ribs":ribs,
            "crown_Z":float(crown),"web_peak_Z":webpeak,
            "plan_corners":corners,"sector_count":n,
            "divisions":N,"seam_gap_native":max_gap,
            "config_SHA256":canonical_hash(asdict(settings)),
            "geometry_version":ALGORITHM_VERSION}

