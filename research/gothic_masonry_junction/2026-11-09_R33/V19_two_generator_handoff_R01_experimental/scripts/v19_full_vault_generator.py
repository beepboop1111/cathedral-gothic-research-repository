#!/usr/bin/env python3
"""V19 COMPONENT 2/2 — FULL skeleton-first Gothic VAULT WITH USER MERIDIANS.

Self-contained *as a pair* with v19_rib_arch_generator.py (same directory).
No R17/R18 installs, no v18 add-on, no old .blend, no remote repository needed.

Reconstructs V19 by preserving:
  1. R17 true two-centred Gothic boundary arches;
  2. R18 independent R07-style circle groins and original boss;
  3. R18 interior web base; and, CRITICALLY,
  4. the USER-ACCEPTED four-segment R12B Sector 02 Type A C1 HERMITE
     meridian, normalized to each experimental boundary-apex/boss span.
The unique R14 Type B/sector05 curve is NOT used in this unrelated
four-sided synthetic study. Open intrados ONLY. Roof clearance unresolved.

Run:
blender -b --factory-startup --python v19_full_vault_generator.py -- --out ./output_vault
"""
from __future__ import annotations
import sys,math,json,hashlib,argparse
from pathlib import Path
from dataclasses import asdict,replace

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:sys.path.insert(0,str(SCRIPTS))
import v19_rib_arch_generator as arch
VERSION="V19_HANDOFF_R01_FULL_VAULT_USER_HERMITE"
# Exact source configuration:
# F5ZP R12B ... /configs/R12B_USER_RED_HERMITE_REGISTRATION.json
# source SHA-256 a9312346824a17153f7a5eabce488d8f1f0911cac1357d1d4b06d3568eea97b5
# Original signed offsets are relative to Z4296, NOT a universal absolute height.
ACCEPTED_R12B_SOURCE_Z=4296.0
ACCEPTED_R12B_REFERENCE_RUN=738.8206500000015
KNOT_T=(0.0,0.25,0.5,0.75,1.0)
KNOT_WORLD_Z=(4296.0,4356.254741314415,4369.825253124143,
              4347.047844059482,4296.0)
KNOT_DZ_DS=(248.97069966590794,122.45209025304281,
            -27.85941314245789,-142.1618793549983,
            -176.04933307532278)
KNOT_H=tuple(z-ACCEPTED_R12B_SOURCE_Z for z in KNOT_WORLD_Z)
R12B_ACCEPTED_SOURCE_PEAK_Z=4370.341134563053
R12B_SOURCE_FIT_RMS_NATIVE=.7371464676754621

def accepted_hermite_hump(s):
    """EXACT accepted R12B cubic Hermite function, with zero end offsets.
    Derivatives are dZ/ds (normalized full-span parameter), not per-segment.
    """
    s=float(s)
    if not 0<=s<=1:raise ValueError("MERIDIAN_STATION_OUT_OF_RANGE")
    if s in (0.,1.):return 0.
    k=next((i for i in range(4) if s<=KNOT_T[i+1]),3)
    dt=KNOT_T[k+1]-KNOT_T[k]
    u=(s-KNOT_T[k])/dt
    u2=u*u
    u3=u2*u
    return ((2*u3-3*u2+1)*KNOT_H[k]
           +(u3-2*u2+u)*dt*KNOT_DZ_DS[k]
           +(-2*u3+3*u2)*KNOT_H[k+1]
           +(u3-u2)*dt*KNOT_DZ_DS[k+1])

def base_r18_web_point(s,C,k,t,r,crown):
    """Exact V19-applicable R18 independently constrained web before red-line."""
    t=float(t);r=float(r)
    if not 0<=t<=1 or not 0<=r<=1:raise ValueError("WEB_PARAMETER_OUT_OF_RANGE")
    A=C[k];B=C[(k+1)%len(C)]
    x,y,dx,dy,L,rise=arch.edge_data(s,A,B)
    if r==1.:return (0.,0.,float(crown))
    if t==0.:return arch.groin_point(A,s.spring_Z,crown,r)
    if t==1.:return arch.groin_point(B,s.spring_Z,crown,r)
    edge_z=arch.two_centered_height(t,L,s.spring_Z,rise)
    if r==0.:return (x+t*dx,y+t*dy,edge_z)
    lz=arch.groin_point(A,s.spring_Z,crown,r)[2]
    rz=arch.groin_point(B,s.spring_Z,crown,r)[2]
    radial=(1-t)*lz+t*rz
    factor=max(0.,min(1.,(edge_z-s.spring_Z)/(crown-s.spring_Z)))
    z=radial+(crown-radial)*factor*(1-r)**s.meridian_exponent
    z+=s.dome_lift*(crown-z)*math.sin(math.pi*t)**2*math.sin(math.pi*r)**2
    return ((1-r)*(x+t*dx),(1-r)*(y+t*dy),z)

def meridian_target(s,C,k,r,crown):
    """Exact V19 adaptation: straight arch-apex/boss line + scaled red hump."""
    A=C[k];B=C[(k+1)%len(C)]
    x,y,dx,dy,L,rise=arch.edge_data(s,A,B)
    arch_apex=arch.two_centered_height(.5,L,s.spring_Z,rise)
    run=math.hypot(x+.5*dx,y+.5*dy)
    return ((1-r)*arch_apex+r*crown
            +accepted_hermite_hump(r)*run/ACCEPTED_R12B_REFERENCE_RUN)

def full_web_point(s,C,k,t,r,crown):
    """R12B/R14 red-line control with 0 effect on arch, groin, plan, boss.

    Hnew(k,t,r)= Hbase(k,t,r) + sin(pi*t)^2 * (M_target(k,r)-Hbase(k,.5,r))
    At t=0,1 this is EXACTLY the independent groin; at r=0,1 it is
    EXACTLY the R17 arch/boss. Center meridian t=.5 follows user shape.
    """
    p=base_r18_web_point(s,C,k,t,r,crown)
    if r==0 or r==1 or t==0 or t==1:return p
    baseline_mid=base_r18_web_point(s,C,k,.5,r,crown)[2]
    target=meridian_target(s,C,k,r,crown)
    weight=math.sin(math.pi*t)**2
    return (p[0],p[1],p[2]+weight*(target-baseline_mid))

def build_vault(s=None):
    s=(s or arch.VaultSettings()).validate()
    C=arch.plan_corners(s)
    crown=arch.resolve_crown(s,C)
    skeleton_report=arch.skeleton_qa(s,C,crown)
    n=len(C);N=s.divisions
    V=[];F=[];index={}
    def vertex(p):
        key=tuple(round(float(x),8) for x in p)
        if key not in index:
            index[key]=len(V)
            V.append(tuple(map(float,p)))
        return index[key]
    for k in range(n):
        grid={}
        for j in range(N+1):
            r=j/N
            for i in range(N-j+1):
                t=i/(N-j) if j<N else .5
                grid[j,i]=vertex(full_web_point(s,C,k,t,r,crown))
        for j in range(N):
            for i in range(N-j):
                a=grid[j,i];b=grid[j,i+1];c=grid[j+1,i]
                F.append((a,c,b)) # downward-facing intrados surface
                if i<N-j-1:F.append((b,c,grid[j+1,i+1]))
    result={"vertices":V,"faces":F,"corners":C,"crown":crown,
            "web_peak":max(pt[2] for pt in V),"config":skeleton_report}
    return result

def numerical_qa(s,result):
    """Independent analytic constraints, topology, actual R12B fitted meridian."""
    C=result["corners"];V=result["vertices"];F=result["faces"]
    crown=result["crown"];n=len(C)
    errors={key:0. for key in
       ("plan_displacement","pointed_arch","independent_groin_left",
        "independent_groin_right","shared_groin_seam","boss",
        "type_A_meridian")}
    meridian_peaks=[]
    original_to_new=[]
    for k in range(n):
        samples=[]
        for j in range(257):
            r=j/256
            for t in (0.,.125,.25,.5,.75,.875,1.):
                p=full_web_point(s,C,k,t,r,crown)
                b=base_r18_web_point(s,C,k,t,r,crown)
                errors["plan_displacement"]=max(errors["plan_displacement"],
                    math.dist(p[:2],b[:2]))
                if r==0.:
                    errors["pointed_arch"]=max(errors["pointed_arch"],
                        math.dist(p,arch.boundary_point(s,C,k,t)))
                if t==0.:
                    expected=arch.groin_point(C[k],s.spring_Z,crown,r)
                    errors["independent_groin_left"]=max(
                        errors["independent_groin_left"],math.dist(p,expected))
                if t==1.:
                    expected=arch.groin_point(C[(k+1)%n],s.spring_Z,crown,r)
                    errors["independent_groin_right"]=max(
                        errors["independent_groin_right"],math.dist(p,expected))
                if r==1.:
                    errors["boss"]=max(errors["boss"],math.dist(p,(0.,0.,crown)))
                if t==.5:
                    errors["type_A_meridian"]=max(
                        errors["type_A_meridian"],
                        abs(p[2]-meridian_target(s,C,k,r,crown)))
                    original_to_new.append(abs(p[2]-b[2]))
                    samples.append(p[2])
            seam_L=full_web_point(s,C,k,1.,r,crown)
            seam_R=full_web_point(s,C,(k+1)%n,0.,r,crown)
            errors["shared_groin_seam"]=max(errors["shared_groin_seam"],
                math.dist(seam_L,seam_R))
        meridian_peaks.append(max(samples))
    if max(errors.values())>1e-6:
        raise ValueError("V19_ANALYTIC_SURFACE_QA_FAILURE "+str(errors))
    if len(F)!=n*s.divisions*s.divisions:
        raise ValueError("TRIANGLE_COUNT_ERROR")
    edges={}
    min_area=math.inf
    for a,b,c in F:
        if len({a,b,c})!=3:raise ValueError("COLLAPSED_FACE")
        P=V[a];Q=V[b];R=V[c]
        u=(Q[0]-P[0],Q[1]-P[1],Q[2]-P[2])
        v=(R[0]-P[0],R[1]-P[1],R[2]-P[2])
        cross=(u[1]*v[2]-u[2]*v[1],
               u[2]*v[0]-u[0]*v[2],
               u[0]*v[1]-u[1]*v[0])
        area=.5*math.sqrt(sum(x*x for x in cross))
        min_area=min(min_area,area)
        if area<1e-8:raise ValueError("DEGENERATE_TRIANGLE")
        for x,y in ((a,b),(b,c),(c,a)):
            edge=(min(x,y),max(x,y))
            edges[edge]=edges.get(edge,0)+1
    if max(edges.values())!=2:raise ValueError("NONMANIFOLD_EDGES")
    boundary=sum(1 for v in edges.values() if v==1)
    if boundary!=n*s.divisions:raise ValueError("BOUNDARY_EDGE_COUNT_ERROR")
    Euler=len(V)-len(edges)+len(F)
    if Euler!=1:raise ValueError("OPEN_DISK_EULER_ERROR")
    if not min_area>0:raise ValueError("INVALID_TRIANGLE_AREAS")
    return {
        "status":"V19_TWO_SCRIPT_REPRODUCIBLE_GEOMETRY_PASS",
        "skeleton":result["config"],
        "settings":asdict(s),"version":VERSION,
        "meridian_reference":{
           "source":"R12B_ACCEPTED_SECTOR_02_TYPE_A",
           "source_world_end_Z":ACCEPTED_R12B_SOURCE_Z,
           "original_peak_Z":R12B_ACCEPTED_SOURCE_PEAK_Z,
           "original_fit_RMS_native":R12B_SOURCE_FIT_RMS_NATIVE,
           "reference_plan_run":ACCEPTED_R12B_REFERENCE_RUN,
           "knot_t":list(KNOT_T),
           "knot_world_Z":list(KNOT_WORLD_Z),
           "knot_dZ_ds":list(KNOT_DZ_DS),
           "applicability":"V19 scaled Type A experimental; NOT R14 unique Type B"},
        "max_analytic_residuals_native":errors,
        "meridian_peaks_by_sector_Z":meridian_peaks,
        "max_baseline_to_user_meridian_midpoint_shift_Z":max(original_to_new),
        "highest_boundary_arch_Z":arch.highest_arch_apex(s,C),
        "boss_Z":crown,
        "web_peak_Z":result["web_peak"],
        "web_peak_above_boss_Z":result["web_peak"]-crown,
        "vertices":len(V),"triangles":len(F),"Euler_open_intrados":Euler,
        "open_boundary_edges":boundary,"min_triangle_area_native2":min_area,
        "R16_geometric_guard":"PASS; crown >= highest arch; lock respected; no cap assumed",
        "roof_clearance":"UNRESOLVED",
        "historical_validation":"NOT ESTABLISHED",
        "physical_section":"NOT PROVIDED / no actual rib moulding",
        "structural_validation":"NOT ESTABLISHED",
        "status_approval":"EXPERIMENTAL ONLY",
    }

def create_full_blender_scene(s,result,qa,render_path=None):
    """New separate Blender scene, never deletes existing user data."""
    import bpy
    from mathutils import Vector
    scene=bpy.data.scenes.new("V19_HANDOFF_FULL_EXPERIMENTAL")
    if bpy.context.window:bpy.context.window.scene=scene
    collection=bpy.data.collections.new("V19_OPEN_INTRADOS_EXPERIMENTAL")
    scene.collection.children.link(collection)
    mesh=bpy.data.meshes.new("V19_USER_HERMITE_OPEN_INTRADOS")
    mesh.from_pydata(result["vertices"],[],result["faces"])
    mesh.update(calc_edges=True)
    if len(mesh.polygons)!=qa["triangles"]:
        raise RuntimeError("BLENDER_MESH_IMPORT_NOT_EQUAL")
    obj=bpy.data.objects.new("V19_WEB_R12B_TYPE_A",mesh)
    collection.objects.link(obj)
    mat=bpy.data.materials.new("V19_OPEN_LIMESTONE_PREVIEW")
    mat.diffuse_color=(.78,.77,.70,1)
    mesh.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=True
    obj["STATUS"]="SYNTHETIC_EXPERIMENTAL_OPEN_INTRADOS"
    obj["MERIDIAN"]="R12B_TYPE_A_NORMALIZED_CUBIC_HERMITE"
    obj["SKELETON"]="R17_POINTED_ARCHES_R18_INDEPENDENT_GROINS"
    obj["CAP_CLEARANCE"]="UNRESOLVED"
    obj["NO_MASONRY_THICKNESS"]=True
    # Both kinds of lines are clearly guides. Initially hide the skeleton
    # to match the clean V19 review; users can enable to inspect bearings.
    guides=arch.create_guide_collections(s,result["corners"],result["crown"],scene)
    guides.hide_render=True
    guides.hide_viewport=True
    redcol=bpy.data.collections.new("V19_TYPE_A_HERMITE_MERIDIAN_GUIDES")
    scene.collection.children.link(redcol)
    red=bpy.data.materials.new("V19_RED_MERIDIAN_GUIDE")
    red.diffuse_color=(.85,.08,.04,1.)
    for k in range(s.sectors):
        crv=bpy.data.curves.new(f"MERIDIAN_0{k:02d}","CURVE")
        crv.dimensions="3D"
        crv.bevel_depth=1.7
        crv.bevel_resolution=1
        line=crv.splines.new("POLY")
        line.points.add(256)
        for j,pt in enumerate(line.points):
            pt.co=(*full_web_point(s,result["corners"],k,.5,j/256,result["crown"]),1.)
        crv.materials.append(red)
        marker=bpy.data.objects.new(f"V19_RED_TYPE_A_MERIDIAN_{k:02d}",crv)
        redcol.objects.link(marker)
        marker["DISPLAY_ONLY_NOT_MASONRY"]=True
    camera_data=bpy.data.cameras.new("V19_REVIEW_CAMERA")
    camera=bpy.data.objects.new("V19_REVIEW_CAMERA",camera_data)
    scene.collection.objects.link(camera)
    scene.camera=camera
    mid=Vector((0.,0., result["crown"]*.52))
    eye=Vector((s.radius*2.71,-s.radius*2.56,result["crown"]*1.61))
    camera.location=eye
    camera.rotation_euler=(mid-eye).to_track_quat("-Z","Y").to_euler()
    camera_data.type="ORTHO"
    camera_data.ortho_scale=s.radius*3.19
    camera_data.clip_start=1
    camera_data.clip_end=30000
    scene.render.engine="BLENDER_WORKBENCH"
    scene.render.resolution_x=1280
    scene.render.resolution_y=900
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.display.shading.color_type="MATERIAL"
    scene["V19_STATUS"]="REGENERATED_VERIFIED_EXPERIMENTAL"
    scene["V19_APEX_Z"]=qa["highest_boundary_arch_Z"]
    scene["V19_BOSS_Z"]=qa["boss_Z"]
    scene["V19_WEB_PEAK_Z"]=qa["web_peak_Z"]
    scene["V19_ROOF_CLEARANCE"]="UNRESOLVED"
    scene["V19_GENERATOR_VERSIONS"]=arch.VERSION+" / "+VERSION
    scene["V19_LOADED_SETTINGS_SHA256"]=hashlib.sha256(
        json.dumps(asdict(s),sort_keys=True).encode()).hexdigest()
    if render_path is not None:
        scene.render.filepath=str(render_path)
        bpy.ops.render.render(write_still=True,scene=scene.name)
    return scene,obj

def run_cli(argv=None):
    import bpy
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default=str(SCRIPTS.parent/"full_vault_output"))
    parser.add_argument("--radius",type=float,default=620.)
    parser.add_argument("--irregularity",type=float,default=.12)
    parser.add_argument("--rotation",type=float,default=13.)
    parser.add_argument("--arch-ratio",type=float,default=.92)
    parser.add_argument("--spring",type=float,default=0.)
    parser.add_argument("--sectors",type=int,default=4)
    parser.add_argument("--quality",choices=("FAST","FINAL"),default="FINAL")
    parser.add_argument("--crown",type=float,default=None)
    parser.add_argument("--locked",action="store_true")
    parser.add_argument("--no-render",action="store_true")
    args=parser.parse_args(argv)
    s=arch.VaultSettings(
       sectors=args.sectors,radius=args.radius,irregularity=args.irregularity,
       rotation_degrees=args.rotation,spring_Z=args.spring,
       arch_rise_ratio=args.arch_ratio,
       crown_mode="MANUAL" if args.crown is not None else "AUTO",
       crown_Z=args.crown,crown_locked=args.locked,
       divisions=128 if args.quality=="FINAL" else 32)
    data=build_vault(s)
    qa=numerical_qa(s,data)
    folder=Path(args.out).resolve()
    folder.mkdir(parents=True,exist_ok=True)
    suffixes=["V19_FULL_VAULT_EXPERIMENTAL.blend",
              "V19_OPEN_INTRADOS_BLENDER.glb","V19_FULL_VAULT_QA.json"]
    if not args.no_render:suffixes.append("V19_SINGLE_PREVIEW.png")
    for name in suffixes:
        if (folder/name).exists():
            raise FileExistsError("Refusing to overwrite existing "+str(folder/name))
    png=None if args.no_render else folder/"V19_SINGLE_PREVIEW.png"
    scene,obj=create_full_blender_scene(s,data,qa,png)
    # Export ONLY the web via a temporary single-object scene. Using the
    # Blender exporter selection filter alone in --factory-startup can also
    # include the default Cube: isolate the object explicitly.
    export_scene=bpy.data.scenes.new("V19_TEMP_EXPORT_ONLY_DO_NOT_SAVE")
    export_scene.collection.objects.link(obj)
    last_scene=bpy.context.window.scene if bpy.context.window else None
    try:
        if bpy.context.window:bpy.context.window.scene=export_scene
        bpy.ops.export_scene.gltf(
            filepath=str(folder/"V19_OPEN_INTRADOS_BLENDER.glb"),
            export_format="GLB",export_yup=True,
            use_active_scene=True,use_selection=False)
    finally:
        if bpy.context.window:bpy.context.window.scene=scene
        bpy.data.scenes.remove(export_scene)
    # Check the isolated source collection; extra Blender default objects
    # must not be imported into the V19 GLB.
    bpy.ops.wm.save_as_mainfile(
        filepath=str(folder/"V19_FULL_VAULT_EXPERIMENTAL.blend"),compress=True)
    arch.exclusive_json(folder/"V19_FULL_VAULT_QA.json",qa)
    print("V19_FULL_VAULT_2_SCRIPT_PASS",qa["triangles"],"FACES",
          "BOSS",round(qa["boss_Z"],4),
          "WEB_PEAK",round(qa["web_peak_Z"],4),
          "ALL_BOUNDS_SKELETON_MERIDIANS_MATCHED")

if __name__=="__main__":
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    run_cli(argv)
