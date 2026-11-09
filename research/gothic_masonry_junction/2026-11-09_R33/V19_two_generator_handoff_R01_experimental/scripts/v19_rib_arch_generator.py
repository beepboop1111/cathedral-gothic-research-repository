#!/usr/bin/env python3
"""V19 COMPONENT 1/2 — reproducible Gothic pointed arches and independent groins.

Direct lineage: F5ZP R17 two-centred pointed arches, R18 independent circular
groins and R16 *crown/apex rules*. The real R16 guard has more features;
this portable script implements its mandatory geometric subset, NOT its
governance checksum certification. No imported cathedral geometry is changed.

1:1 project-NATIVE coordinates (not asserted millimetres/metres).
X/Y = plan, Z = elevation. Guides are NOT approved cut-stone rib profiles.

Requires Blender 5.0+ for actual curve objects. Pure geometry works in Python 3.
Run independently:
blender -b --factory-startup --python v19_rib_arch_generator.py -- --out ./output_skeleton
"""
from __future__ import annotations
import math
import json
import hashlib
import argparse
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

VERSION = "V19_HANDOFF_R01_RIB_ARCH_R17_R18"
EPS = 1e-8

@dataclass(frozen=True)
class VaultSettings:
    sectors: int = 4
    radius: float = 620.0
    irregularity: float = 0.12
    rotation_degrees: float = 13.0
    spring_Z: float = 0.0
    arch_rise_ratio: float = 0.92
    crown_mode: str = "AUTO"  # AUTO / LEVEL / MANUAL
    crown_Z: Optional[float] = None
    crown_locked: bool = False
    divisions: int = 128
    meridian_exponent: float = 1.75
    dome_lift: float = 0.12

    def validate(self):
        if not 3 <= int(self.sectors) <= 12 or self.sectors != int(self.sectors):
            raise ValueError("Sector count must be an integer between 3 and 12")
        if self.divisions not in (16, 32, 64, 128):
            raise ValueError("Divisions must be 16/32/64/128 (V19 FINAL=128)")
        if self.crown_mode not in ("AUTO","LEVEL","MANUAL"):
            raise ValueError("Invalid crown mode")
        if self.crown_locked and self.crown_mode != "MANUAL":
            raise ValueError("LOCKED_CROWN_MUST_BE_MANUALLY_SPECIFIED")
        if self.crown_mode == "MANUAL" and self.crown_Z is None:
            raise ValueError("MANUAL_CROWN_REQUIRES_COORDINATE")
        floats = [self.radius,self.irregularity,self.rotation_degrees,
                  self.spring_Z,self.arch_rise_ratio,self.meridian_exponent,
                  self.dome_lift]
        if self.crown_Z is not None: floats.append(self.crown_Z)
        if not all(math.isfinite(float(v)) for v in floats):
            raise ValueError("Nonfinite geometry parameter")
        if self.radius <= 10.0:
            raise ValueError("Invalid plan radius")
        if not 0 <= self.irregularity <= 0.25:
            raise ValueError("Plan irregularity outside validated range")
        if not 0.5 < self.arch_rise_ratio <= 1.25:
            raise ValueError("Pointed-arch rise/span must be greater than 0.5")
        if not 1.1 <= self.meridian_exponent <= 4:
            raise ValueError("Web exponent outside validated range")
        if not 0 <= self.dome_lift <= 0.85:
            raise ValueError("Base web convexity outside validated range")
        return self

def plan_corners(settings: VaultSettings):
    """Exact deterministic R17 irregular polygonal set-out."""
    settings.validate()
    C = []
    for k in range(settings.sectors):
        phi = 2 * math.pi * k / settings.sectors
        theta = (phi + math.radians(settings.rotation_degrees)
                 + settings.irregularity * .18 * math.sin(phi + .3))
        rad = settings.radius * (
            1 + settings.irregularity * math.cos(phi + .51))
        C.append((rad * math.cos(theta), rad * math.sin(theta)))
    return C

def edge_data(settings, a, b):
    x,y = a
    dx,dy = b[0]-x,b[1]-y
    L = math.hypot(dx,dy)
    if L <= EPS: raise ValueError("Degenerate edge")
    rise = settings.arch_rise_ratio * L
    return x,y,dx,dy,L,rise

def two_centered_height(t, span, spring, rise):
    """R17 actual two-circle pointed arch, with apex at t=.5."""
    t = max(0.0,min(1.0,float(t)))
    L = float(span)
    if L <= 0 or rise <= L/2: raise ValueError("Not a two-centred Gothic arch")
    c = L/4 + rise*rise/L
    d = L * min(t,1-t)
    return float(spring) + math.sqrt(max(0.,c*c-(d-c)**2))

def boundary_point(settings, corners, edge, t):
    A = corners[edge]
    B = corners[(edge+1)%len(corners)]
    x,y,dx,dy,L,rise=edge_data(settings,A,B)
    return (x+t*dx, y+t*dy,
            two_centered_height(t,L,settings.spring_Z,rise))

def all_boundary_arches(settings,corners=None,stations=257):
    corners = corners if corners is not None else plan_corners(settings)
    assert stations>=129
    return [{
        "id":f"V19_TWO_CENTERED_POINTED_ARCH_{k:02d}",
        "points_xyz":[boundary_point(settings,corners,k,j/(stations-1))
                      for j in range(stations)]
    } for k in range(len(corners))]

def highest_arch_apex(settings,corners=None):
    corners = corners if corners is not None else plan_corners(settings)
    return settings.spring_Z + max(
        edge_data(settings,corners[k],corners[(k+1)%len(corners)])[5]
        for k in range(len(corners)))

def resolve_crown(settings,corners=None):
    """R16 geometric hard-stop subset. Never silently move a locked crown."""
    settings.validate()
    corners = corners if corners is not None else plan_corners(settings)
    apex=highest_arch_apex(settings,corners)
    if settings.crown_mode=="AUTO":
        crown=apex+max(25.,.08*max(0.,apex-settings.spring_Z))
    elif settings.crown_mode=="LEVEL":crown=apex
    else:crown=float(settings.crown_Z)
    if crown < apex - EPS:
        raise ValueError(f"CROWN_BELOW_ARCH_APEX_HARD_STOP ({crown} < {apex})")
    if crown<=settings.spring_Z:
        raise ValueError("NO_POSITIVE_GROIN_RISE")
    return crown

def groin_point(corner,spring,crown,r,strict_vertical_spring=True):
    """Exact R18 circular groin. V19 forbids the alternate shallow fallback.

    Plan radial run L = hypot(corner XY), vertical rise h = crown-spring.
    R18 circle center a=max(L,(L²+h²)/2L), b=(L²+h²-2aL)/2h;
    V19 satisfies h>=L; b is ~0, spring tangent vertical, and crown
    is the maximum. When h<L, reject rather than silently adjust bearings.
    """
    x,y = map(float,corner)
    run = math.hypot(x,y)
    rise = crown-spring
    r = float(r)
    if not 0<=r<=1:
        raise ValueError("GROIN_STATION_OUT_OF_RANGE")
    if run<=EPS or rise<=EPS:raise ValueError("INVALID_GROIN_SPAN_RISE")
    if strict_vertical_spring and rise < run - EPS:
        raise ValueError("UNSUPPORTED_SHALLOW_GROIN: no silent geometric fallback")
    a=max(run,(run*run+rise*rise)/(2*run))
    b=(run*run+rise*rise-2*a*run)/(2*rise)
    rad=math.hypot(a,b)
    z=spring+b+math.sqrt(max(0.,rad*rad-(run*r-a)**2))
    if r==0:z=spring
    if r==1:z=crown
    return ((1-r)*x,(1-r)*y,z)

def independent_groins(settings,corners=None,crown=None,stations=257):
    corners = corners if corners is not None else plan_corners(settings)
    crown = resolve_crown(settings,corners) if crown is None else crown
    return [{
        "id":f"V19_INDEPENDENT_GROIN_{k:02d}",
        "points_xyz":[groin_point(corner,settings.spring_Z,crown,j/(stations-1))
                      for j in range(stations)]
    } for k,corner in enumerate(corners)]

def skeleton_qa(settings,corners=None,crown=None):
    corners = corners if corners is not None else plan_corners(settings)
    crown = resolve_crown(settings,corners) if crown is None else crown
    apex=highest_arch_apex(settings,corners)
    if crown<apex-EPS:raise ValueError("CROWN_BELOW_ARCH_APEX_HARD_STOP")
    edge_lengths=[edge_data(settings,corners[i],corners[(i+1)%len(corners)])[4]
                  for i in range(len(corners))]
    radial_runs=[math.hypot(*v) for v in corners]
    if crown-settings.spring_Z < max(radial_runs)-EPS:
        raise ValueError("STRICT_VERTICAL_SPRING_REQUIRED")
    errors={"arch_spring":0.,"arch_apex":0.,"groin_spring":0.,
            "groin_boss":0.,"groin_monotonic":0.}
    for k,A in enumerate(corners):
        B=corners[(k+1)%len(corners)]
        expected_apex=settings.spring_Z+settings.arch_rise_ratio*edge_lengths[k]
        ar0=boundary_point(settings,corners,k,0.)
        ar1=boundary_point(settings,corners,k,1.)
        arm=boundary_point(settings,corners,k,.5)
        errors["arch_spring"]=max(errors["arch_spring"],
            math.dist(ar0,(A[0],A[1],settings.spring_Z)),
            math.dist(ar1,(B[0],B[1],settings.spring_Z)))
        errors["arch_apex"]=max(errors["arch_apex"],abs(arm[2]-expected_apex))
        first=groin_point(A,settings.spring_Z,crown,0.)
        last=groin_point(A,settings.spring_Z,crown,1.)
        errors["groin_spring"]=max(errors["groin_spring"],
            math.dist(first,(*A,settings.spring_Z)))
        errors["groin_boss"]=max(errors["groin_boss"],
            math.dist(last,(0.,0.,crown)))
        prev=first[2]
        for j in range(1,257):
            z=groin_point(A,settings.spring_Z,crown,j/256)[2]
            errors["groin_monotonic"]=max(errors["groin_monotonic"],prev-z)
            prev=z
    if max(errors.values())>1e-6:raise ValueError("SKELETON_QA_FAILED "+str(errors))
    return {
        "status":"V19_POINTED_ARCH_INDEPENDENT_GROIN_GEOMETRIC_QA_PASS",
        "family":"irregular polygon, 4 sectors at V19 baseline",
        "scale":"1:1 native, SI conversion unknown",
        "settings":asdict(settings),
        "plan_corners":corners,"arch_chord_lengths":edge_lengths,
        "radial_groin_runs":radial_runs,
        "highest_arch_apex_Z":apex,
        "crown_Z":crown,
        "spring_Z":settings.spring_Z,
        "strict_vertical_springing":True,
        "residuals_native":errors,
        "status_limitations":"Guides only; no historical physical rib profile/section validated",
    }

def create_guide_collections(settings,corners,crown,scene=None,prefix="V19_"):
    """Blender-only 3D CURVE guide objects; NOT physical Gothic masonry."""
    import bpy
    scene=scene or bpy.context.scene
    arches=all_boundary_arches(settings,corners)
    groins=independent_groins(settings,corners,crown)
    coll=bpy.data.collections.new(prefix+"SKELETON_GUIDES_NOT_MASONRY")
    scene.collection.children.link(coll)
    def make_mat(name,color):
        m=bpy.data.materials.new(prefix+name)
        m.diffuse_color=(*color,1.)
        return m
    blue=make_mat("ARCH_BLUE",(.12,.45,.82))
    copper=make_mat("GROIN_COPPER",(.9,.29,.11))
    def make_curve(item,material,bevel=1.25):
        name=item["id"]
        crv=bpy.data.curves.new(name,"CURVE")
        crv.dimensions="3D"
        crv.resolution_u=1
        crv.bevel_depth=bevel # visibly distinguish, NO masonry-diameter claim
        crv.bevel_resolution=2
        sp=crv.splines.new("POLY")
        points=item["points_xyz"]
        sp.points.add(len(points)-1)
        for pt,xyz in zip(sp.points,points):pt.co=(*xyz,1.)
        crv.materials.append(material)
        obj=bpy.data.objects.new(name,crv);coll.objects.link(obj)
        obj["ROLE"]="CONSTRUCTION_PATH_NOT_PHYSICAL_RIB"
        obj["SOURCE"]="R17_TWO_CENTERED_ARCH_OR_R18_INDEPENDENT_GROIN"
        return obj
    for obj in arches:make_curve(obj,blue)
    for obj in groins:make_curve(obj,copper)
    return coll

def generate_skeleton_scene(settings=None):
    """Create a new scene; do not delete user scenes, collections or meshes."""
    import bpy
    settings=(settings or VaultSettings()).validate()
    corners=plan_corners(settings)
    crown=resolve_crown(settings,corners)
    qa=skeleton_qa(settings,corners,crown)
    sc=bpy.data.scenes.new("V19_SKELETON_EXPERIMENTAL")
    if bpy.context.window:bpy.context.window.scene=sc
    create_guide_collections(settings,corners,crown,sc)
    sc["STATUS"]="EXPERIMENTAL_SKELETON_ONLY"
    sc["CROWN_Z"]=crown
    sc["SOURCE_VERSION"]=VERSION
    return sc,qa

def exclusive_json(path,record):
    with Path(path).open("x",encoding="utf-8") as f:
        json.dump(record,f,indent=2)
        f.write("\n")

def run_cli(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default=str(Path(__file__).resolve().parent.parent/"skeleton_output"))
    parser.add_argument("--sectors",type=int,default=4)
    parser.add_argument("--radius",type=float,default=620.)
    parser.add_argument("--irregularity",type=float,default=.12)
    parser.add_argument("--rotation",type=float,default=13.)
    parser.add_argument("--arch-ratio",type=float,default=.92)
    parser.add_argument("--spring",type=float,default=0.)
    args=parser.parse_args(argv)
    s=VaultSettings(sectors=args.sectors,radius=args.radius,
        irregularity=args.irregularity,rotation_degrees=args.rotation,
        arch_rise_ratio=args.arch_ratio,spring_Z=args.spring)
    out=Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    for name in ("V19_SKELETON_EXPERIMENTAL.blend","V19_SKELETON_QA.json"):
        if (out/name).exists():raise FileExistsError("Never overwrite "+str(out/name))
    sc,report=generate_skeleton_scene(s)
    import bpy
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"V19_SKELETON_EXPERIMENTAL.blend"),
                               compress=True)
    exclusive_json(out/"V19_SKELETON_QA.json",report)
    print("V19_SKELETON_PASS",report["crown_Z"],
          "POINTED_ARCHES",s.sectors,"INDEPENDENT_GROINS",s.sectors)

if __name__=="__main__":
    args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    run_cli(args)
