bl_info={"name":"F5ZP R18 Skeleton First Vault (Experimental)",
         "author":"F5ZP research","version":(0,18,0),"blender":(5,0,0),
         "location":"View3D > N > R18 Vault",
         "description":"Independent circular groin skeleton and constrained Gothic webs",
         "category":"3D View"}
import bpy,pathlib,sys,json,hashlib,traceback
from bpy.props import EnumProperty
HERE=pathlib.Path("/home/christopher/Downloads/F5ZP_R18_INDEPENDENT_GROIN_WEB_TEST_EXPERIMENTAL")
R17=pathlib.Path("/home/christopher/Downloads/F5ZP_UNIVERSAL_GOTHIC_VAULT_GENERATOR_R01_EXPERIMENTAL/experiments/F5ZP_R17_FAST_UNIVERSAL_VAULT_WORKSPACE_EXPERIMENTAL")
sys.path[:0]=[str(HERE),str(R17/"addon"),str(R17/"addon/r17_vendor")]
import r17_experimental_workspace as r17
import r17_core as old
import r18_core as core
from strict_crown_guard import enforce,preferred_crown
NAME="R18_ACTIVE_GEOMETRY"
GUIDE="R18_VISUAL_GUIDE_NOT_MASONRY"
MATERIALS={"WEB":(.79,.77,.66,1),"ARCH":(.2,.5,.72,1),
           "GROIN":(.92,.44,.19,1)}

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def source_snapshot():
    ledger=r17.source_snapshot()
    ledger["r18_core.py"]=sha(HERE/"r18_core.py")
    ledger["R17_V02_blend"]=sha(R17/"blender/F5ZP_R17_FAST_VAULT_WORKSPACE_REVIEW_READY_V02_EXPERIMENTAL.blend")
    return ledger

def master_scene():
    sc=bpy.data.scenes.get("R17_WORKSPACE")
    if sc is None:raise RuntimeError("R18 requires recovered R17_WORKSPACE")
    return sc

def material(label,rgba):
    name="R18_"+label
    m=bpy.data.materials.get(name)
    if not m:m=bpy.data.materials.new(name)
    m.diffuse_color=rgba
    return m

def ensure_collection():
    col=bpy.data.collections.get(NAME)
    if col is None:col=bpy.data.collections.new(NAME)
    for sc in bpy.data.scenes:
        if sc.name.startswith("R17_"):
            if col.name not in [c.name for c in sc.collection.children]:
                sc.collection.children.link(col)
    return col

def guide_curve(name,xyz,coll,mat):
    curve=bpy.data.curves.new(name,"CURVE")
    curve.dimensions="3D";curve.resolution_u=1
    curve.bevel_depth=0.75
    curve.bevel_resolution=1
    spline=curve.splines.new("POLY")
    spline.points.add(len(xyz)-1)
    for point,v in zip(spline.points,xyz):point.co=(*map(float,v),1)
    obj=bpy.data.objects.new(name,curve);coll.objects.link(obj)
    curve.materials.append(mat)
    obj["GUIDE_ONLY"]=True
    obj["PHYSICAL_MOULDING"]=False

def textblock(name,obj):
    txt=bpy.data.texts.get(name) or bpy.data.texts.new(name)
    txt.clear();txt.write(json.dumps(obj,indent=2))
    return txt

def rebuild():
    sc=master_scene();s=r17._config(sc.r17_props)
    before=source_snapshot()
    arches=old.measured_boundary_arches(s,257)
    apex=max(max(p[2] for p in a["points_xyz"]) for a in arches)
    crown=(preferred_crown(boundary_arches=arches,spring_Z=s.spring_Z)
           if s.crown_mode=="AUTO" else apex
           if s.crown_mode=="LEVEL" else s.crown_Z)
    kwargs=dict(vault_id="R18_"+s.vault_type,crown_Z=crown,
       boundary_arches=arches,spring_Z=s.spring_Z,
       cap_Z=s.cap_Z if s.cap_enabled else None,
       crown_locked=s.crown_locked,intended_export="open_intrados")
    pre=enforce(**kwargs,locks_before=before,locks_after=before,phase="PREBUILD")
    shape=core.generate(s,crown)
    if shape["arches"]!=arches:raise RuntimeError("ORIGINAL_ARCH_RECONSTRUCTION_CHANGED")
    metric=core.qa(s,shape)
    after=source_snapshot()
    post=enforce(**kwargs,web_peak_Z=shape["web_peak_Z"],
       locks_before=before,locks_after=after,phase="POSTBUILD")
    if before!=after:raise RuntimeError("SOURCE_OR_V02_BASELINE_MUTATION")
    out={"status":"R18_SYNTHETIC_GEOMETRY_VALIDATED","quality":s.quality,
       "sector_count":s.sector_count,"geometry":metric,
       "R16_PRE":pre,"R16_POST":post,
       "original_source_hashes_before":before,"original_source_hashes_after":after,
       "locked_geometry_warning":"LOCKED_GEOMETRY_WARNING_ALWAYS",
       "stone_sections":"NOT MODELED; GUIDES ARE NOT PHYSICAL RIBS",
       "roof_clearance":"UNRESOLVED","historical_validation":False,
       "structural_validation":False,"approved_cathedral_generator_replaced":False}
    active=ensure_collection()
    pending=bpy.data.collections.new("R18_PENDING_VALIDATED_ONLY")
    sc.collection.children.link(pending)
    try:
        mesh=bpy.data.meshes.new("R18_OPEN_INTRADOS_"+s.vault_type)
        mesh.from_pydata(shape["vertices"],[],shape["faces"])
        mesh.update(calc_edges=True)
        obj=bpy.data.objects.new("R18_WEB_OPEN_INTRADOS_EXPERIMENTAL",mesh)
        pending.objects.link(obj)
        mesh.materials.append(material("LIMESTONE_WEB",MATERIALS["WEB"]))
        for face in mesh.polygons:face.use_smooth=True
        obj["R18_NATIVE_SCALE"]="1:1 native units"
        obj["R18_CROWN_Z"]=crown
        obj["R18_SOURCE_HASH"]=after["r18_core.py"]
        obj["R18_CONFIG_SHA256"]=old.canonical_hash(shape["settings"])
        obj["R18_STATUS"]="SYNTHETIC_APPROVAL_PENDING"
        A=material("POINTED_ARCH_GUIDES",MATERIALS["ARCH"])
        B=material("INDEPENDENT_GROIN_GUIDES",MATERIALS["GROIN"])
        for a in shape["arches"]:guide_curve(a["id"],a["points_xyz"],pending,A)
        for r in shape["ribs"]:guide_curve(r["id"],r["points_xyz"],pending,B)
        previous=list(active.objects)
        for thing in list(pending.objects):
            pending.objects.unlink(thing);active.objects.link(thing)
        for thing in previous:bpy.data.objects.remove(thing,do_unlink=True)
    except Exception:
        for thing in list(pending.objects):
            bpy.data.objects.remove(thing,do_unlink=True)
        raise
    finally:bpy.data.collections.remove(pending)
    sc["r18_status"]="VALIDATED_SYNTHETIC"
    sc["r18_crown_z"]=crown
    sc["r18_apex_z"]=apex
    sc["r18_last_QA"]=json.dumps(metric)
    sc["r18_guard_warnings"]=" | ".join(post["warning_codes"])
    folder=HERE/"outputs";folder.mkdir(parents=True,exist_ok=True)
    k=1
    while (folder/f"R18_BUILD_{k:03d}_QA.json").exists():k+=1
    sc["r18_build_count"]=k
    path=folder/f"R18_BUILD_{k:03d}_QA.json"
    with path.open("x") as f:json.dump(out,f,indent=2)
    textblock("R18_LAST_VALIDATED_QA.json",out)
    return out

class R18_OT_regenerate(bpy.types.Operator):
    bl_idname="r18.regenerate"
    bl_label="Rebuild R18 Skeleton-First Vault"
    bl_options={"REGISTER","UNDO"}
    def execute(self,context):
        try:
            report=rebuild()
            self.report({"INFO"},"R18 verified "+str(report["sector_count"])+
                        " sectors; original R17 preserved.")
            return {"FINISHED"}
        except Exception as exc:
            master_scene()["r18_status"]="HARD_STOP_KEEP_LAST_VALID"
            textblock("R18_LAST_REJECTION.json",{"status":"HARD_STOP_NO_COMMIT",
                "error":str(exc),"warnings":["LOCKED_GEOMETRY_WARNING_ALWAYS"]})
            self.report({"ERROR"},"R18 HARD STOP: "+str(exc)[:180])
            return {"CANCELLED"}

class R18_OT_guides(bpy.types.Operator):
    bl_idname="r18.guides"
    bl_label="Toggle Thin Guide Curves"
    def execute(self,context):
        col=bpy.data.collections.get(NAME)
        if col is None:return {"CANCELLED"}
        visible=any(o.type=="CURVE" and not o.hide_render for o in col.objects)
        for ob in col.objects:
            if ob.type=="CURVE":
                ob.hide_render=visible
                ob.hide_set(visible)
        return {"FINISHED"}

class R18_OT_export(bpy.types.Operator):
    bl_idname="r18.export_glb"
    bl_label="Export R18 Web GLB (1:1)"
    def execute(self,context):
        try:
            sc=master_scene()
            if sc.get("r18_status")!="VALIDATED_SYNTHETIC":
                raise RuntimeError("R18 last build not valid")
            active=bpy.data.collections.get(NAME)
            meshes=[o for o in active.objects if o.type=="MESH"]
            if len(meshes)!=1:raise RuntimeError("R18 expected one web mesh")
            if meshes[0].get("R18_SOURCE_HASH")!=source_snapshot()["r18_core.py"]:
                raise RuntimeError("SOURCE_CHANGED_SINCE_BUILD")
            out=HERE/"outputs"/f"R18_BUILD_{sc['r18_build_count']:03d}_WEB_ONLY_1TO1.glb"
            if out.exists():raise FileExistsError(str(out))
            view=bpy.context.view_layer
            prior={o.name:o.select_get() for o in view.objects}
            old_active=view.objects.active
            for ob in view.objects:ob.select_set(False)
            target=meshes[0]
            target.select_set(True);view.objects.active=target
            try:bpy.ops.export_scene.gltf(filepath=str(out),export_format="GLB",
                                          use_selection=True,export_apply=True)
            finally:
                view.objects.active=old_active
                for ob in view.objects:ob.select_set(prior.get(ob.name,False))
            if out.stat().st_size<4096:raise ValueError("EXPORT_TOO_SMALL")
            self.report({"INFO"},"R18 web-only 1:1 GLB saved")
            return {"FINISHED"}
        except Exception as exc:
            self.report({"ERROR"},"R18 GLB blocked: "+str(exc)[:180])
            return {"CANCELLED"}

class R18_OT_checkpoint(bpy.types.Operator):
    bl_idname="r18.checkpoint"
    bl_label="Save New R18 .blend"
    def execute(self,context):
        sc=master_scene()
        if sc.get("r18_status")!="VALIDATED_SYNTHETIC":
            return {"CANCELLED"}
        folder=HERE/"blender";folder.mkdir(exist_ok=True)
        index=1
        while (folder/f"R18_SKELETON_FIRST_CHECKPOINT_{index:03d}_EXPERIMENTAL.blend").exists():index+=1
        out=folder/f"R18_SKELETON_FIRST_CHECKPOINT_{index:03d}_EXPERIMENTAL.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
        self.report({"INFO"},"Saved "+out.name)
        return {"FINISHED"}

class R18_PT_main(bpy.types.Panel):
    bl_label="R18 Independent Groins"
    bl_idname="R18_PT_main"
    bl_space_type="VIEW_3D"
    bl_region_type="UI"
    bl_category="R18 Vault"
    def draw(self,context):
        ui=self.layout
        try:sc=master_scene()
        except RuntimeError:
            ui.label(text="Open R18 workspace file first",icon="ERROR")
            return
        p=sc.r17_props
        ui.label(text="EXPERIMENTAL — protected R16 guard",icon="LOCKED")
        ui.label(text="Groins first; fitted webs second")
        for prop in ("vault_type","custom_sectors","quality","radius","irregularity",
           "arch_rise_ratio","spring_z","crown_mode"):
            if prop=="custom_sectors" and p.vault_type!="CUSTOM":continue
            ui.prop(p,prop)
        if p.crown_mode=="MANUAL":ui.prop(p,"crown_z")
        ui.prop(p,"crown_locked")
        for prop in ("meridian_exponent","dome_lift"):ui.prop(p,prop)
        ui.operator("r18.regenerate",text="REGENERATE R18",icon="FILE_REFRESH")
        ui.operator("r18.guides",text="Toggle thin construction guides")
        ui.label(text="Guides ARE NOT physical mouldings")
        row=ui.row(align=True)
        row.operator("r18.export_glb",text="GLB 1:1",icon="EXPORT")
        row.operator("r18.checkpoint",text="Save .blend",icon="FILE_TICK")
        ui.label(text=str(sc.get("r18_status","NOT GENERATED")))
        if "r18_apex_z" in sc:
            ui.label(text="Highest arch apex: %.2f"%sc["r18_apex_z"])
            ui.label(text="Crown: %.2f"%sc["r18_crown_z"])
        ui.label(text="R17 & approved F5ZN-A unchanged.",icon="LOCKED")

CLASSES=(R18_OT_regenerate,R18_OT_guides,R18_OT_export,R18_OT_checkpoint,R18_PT_main)
def register():
    for cls in CLASSES:
        try:bpy.utils.register_class(cls)
        except ValueError:pass
def unregister():
    for cls in reversed(CLASSES):
        try:bpy.utils.unregister_class(cls)
        except RuntimeError:pass
if __name__=="__main__":register()
