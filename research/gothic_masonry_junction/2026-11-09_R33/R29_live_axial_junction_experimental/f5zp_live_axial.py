bl_info = {
    "name": "F5ZP Live Axial Junction (Experimental)",
    "author": "F5ZP procedural study",
    "version": (0, 1, 0),
    "blender": (4, 3, 0),
    "location": "3D View > Sidebar > F5ZP",
    "description": "Guarded, rebuildable axial trial geometry; does not edit R28 references",
    "category": "3D View",
}
import bpy
import hashlib
import json
import math
import re
from pathlib import Path
from mathutils import Vector

OWNER = "F5ZP_R29_AXIAL_EXPERIMENT"
REF_COLL = "00_R28_PROTECTED_REFERENCE_DO_NOT_EDIT"
GEN_COLL = "90_R29_LIVE_GENERATED_EXPERIMENTAL"
MANIFEST_KEY = "R29_REFERENCE_SIGNATURE"
FILE_STEM = "R29_LIVE_AXIAL_JUNCTION_EXPERIMENTAL"
PALETTE = {
    "web": (0.72, 0.39, 0.14, 1),
    "rib": (0.86, 0.70, 0.43, 1),
    "arch": (0.92, 0.18, 0.39, 1),
    "receiver": (0.17, 0.66, 0.53, 1),
    "ridge": (0.98, 0.77, 0.23, 1),
}

def collection(scene, name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    if c.name not in scene.collection.children:
        if not any(c == ch for ch in scene.collection.children):
            scene.collection.children.link(c)
    return c

def reference_objects(scene):
    ref = bpy.data.collections.get(REF_COLL)
    if ref is None:
        raise RuntimeError("Missing reference collection; refusing to rebuild.")
    return sorted([o for o in ref.all_objects if o.get("F5ZP_OWNER") != OWNER], key=lambda o: o.name)

def reference_signature(scene):
    h = hashlib.sha256()
    objs = reference_objects(scene)
    if not objs:
        raise RuntimeError("Reference collection is empty.")
    for obj in objs:
        h.update((obj.name + "|" + obj.type + "\n").encode())
        h.update((" ".join("%.9f" % v for row in obj.matrix_world for v in row) + "\n").encode())
        if obj.type == "MESH":
            for v in obj.data.vertices:
                h.update(("%.9f,%.9f,%.9f;" % tuple(v.co)).encode())
            for p in obj.data.polygons:
                h.update((",".join(map(str, p.vertices)) + ";").encode())
        elif obj.type == "CURVE":
            for spline in obj.data.splines:
                for p in spline.points:
                    h.update((",".join("%.9f" % v for v in p.co) + ";").encode())
                for p in spline.bezier_points:
                    h.update((",".join("%.9f" % v for v in p.co) + ";").encode())
    return h.hexdigest()

def assert_reference_untouched(scene):
    prior = scene.get(MANIFEST_KEY)
    if not prior:
        raise RuntimeError("Missing R29 baseline hash. Run setup, do not auto-rebaseline.")
    actual = reference_signature(scene)
    if actual != prior:
        raise RuntimeError("R28 reference geometry/coordinates changed. Rebuild blocked.")

def material_for(name):
    mat_name = "R29_MAT_" + name.upper()
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(mat_name)
        mat.diffuse_color = PALETTE[name]
    return mat

def mark_and_link(obj, coll, role):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    obj["F5ZP_OWNER"] = OWNER
    obj["F5ZP_ROLE"] = role
    obj["F5ZP_APPROVAL"] = "EXPERIMENTAL_ONLY_NOT_APPROVED"
    obj.color = PALETTE[role]
    if obj.data and hasattr(obj.data, "materials"):
        obj.data.materials.clear()
        obj.data.materials.append(material_for(role))
    return obj

def create_mesh(coll, name, verts, faces, role):
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    obj["F5ZP_OWNER"] = OWNER
    obj["F5ZP_ROLE"] = role
    obj["F5ZP_APPROVAL"] = "EXPERIMENTAL_ONLY_NOT_APPROVED"
    obj.color = PALETTE[role]
    mesh.materials.append(material_for(role))
    return obj

def create_curve(coll, name, points, radius, role):
    curve = bpy.data.curves.new(name + "_CURVE", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 12
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for p, v in zip(spline.points, points):
        p.co = (*v, 1.0)
    obj = bpy.data.objects.new(name, curve)
    coll.objects.link(obj)
    obj["F5ZP_OWNER"] = OWNER
    obj["F5ZP_ROLE"] = role
    obj["F5ZP_APPROVAL"] = "EXPERIMENTAL_ONLY_NOT_APPROVED"
    obj.color = PALETTE[role]
    curve.materials.append(material_for(role))
    return obj

def arch_rise(y, half_width, height):
    # True two-centered circular Gothic arch in a vertical transverse plane.
    # Circle centers are at +/- c on the springing line.
    a = half_width
    c = (height * height - a * a) / (2.0 * a)
    r = a + c
    center = c if y <= 0 else -c
    return math.sqrt(max(0.0, r * r - (y - center) ** 2))

def upper_surface(u, y, p):
    baseline = p.inner_spring * (1.0 - u) + p.outer_spring * u
    transverse = arch_rise(y, p.half_width, p.transverse_rise)
    long_lift = p.longitudinal_lift * math.sin(math.pi * u)
    long_lift *= (0.35 + 0.65 * transverse / p.transverse_rise)
    return baseline + transverse + long_lift

def point(u, y, p):
    return (p.inner_x + p.radial_span * u, y + p.center_y, upper_surface(u, y, p))

def shell_panel(coll, name, p, y0, y1):
    nu, nv = p.samples, max(8, p.samples // 2)
    verts = []
    for offset in (0.0, -p.web_thickness):
        for i in range(nu + 1):
            u = i / nu
            for j in range(nv + 1):
                y = y0 + (y1-y0) * j/nv
                x, yy, z = point(u, y, p)
                verts.append((x, yy, z + offset))
    stride = nv+1
    layer = (nu+1)*stride
    faces = []
    def idx(i,j,k=0): return k*layer + i*stride+j
    for i in range(nu):
        for j in range(nv):
            a,b,c,d = idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1)
            faces.append((a,b,c,d))
            faces.append((idx(i,j,1),idx(i,j+1,1),idx(i+1,j+1,1),idx(i+1,j,1)))
    for i in range(nu):
        faces.append((idx(i,0),idx(i,0,1),idx(i+1,0,1),idx(i+1,0)))
        faces.append((idx(i,nv),idx(i+1,nv),idx(i+1,nv,1),idx(i,nv,1)))
    for j in range(nv):
        faces.append((idx(0,j),idx(0,j+1),idx(0,j+1,1),idx(0,j,1)))
        faces.append((idx(nu,j),idx(nu,j,1),idx(nu,j+1,1),idx(nu,j+1)))
    return create_mesh(coll, name, verts, faces, "web")

def receiver(coll, name, x, y, h, p):
    # Simple trial bearing blocks; NOT a validated structural design.
    dx, dy = p.receiver_depth, p.receiver_width
    x0,x1=x-dx/2,x+dx/2
    y0,y1=y-dy/2,y+dy/2
    z0,z1=0,max(100.0,h)
    verts=[(a,b,c) for c in (z0,z1) for b in (y0,y1) for a in (x0,x1)]
    faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    return create_mesh(coll,name,verts,faces,"receiver")

def build_geometry(scene, target, p):
    # Assemble the panels from one shared surface: ribs and webs cannot drift apart.
    for sign, label in [(-1,"SOUTH"),(1,"NORTH")]:
        lo,hi = (-p.half_width,0) if sign<0 else (0,p.half_width)
        shell_panel(target,"R29_WEB_"+label,p,lo,hi)
        mid = (lo+hi)/2
        boss_u = 0.5
        boss = point(boss_u, mid, p)
        for n,(u0,y0) in enumerate(((0,lo),(0,hi),(1,lo),(1,hi)),start=1):
            samples=[]
            for k in range(p.samples+1):
                f=k/p.samples
                u=u0+(boss_u-u0)*f
                y=y0+(mid-y0)*f
                x,yy,z=point(u,y,p)
                samples.append((x,yy,z+p.rib_radius*0.38))
            create_curve(target,f"R29_RIB_{label}_{n:02d}",samples,p.rib_radius,"rib")
        create_curve(target,"R29_BOSS_RING_"+label,
                     [(boss[0]+p.rib_radius*1.3*math.cos(2*math.pi*k/32),
                       boss[1]+p.rib_radius*1.3*math.sin(2*math.pi*k/32),
                       boss[2]+p.rib_radius*0.65) for k in range(33)],
                     p.rib_radius*0.5,"rib")
    create_curve(target,"R29_TRANSVERSE_INNER_POINTED_ARCH",
                 [point(0,-p.half_width+2*p.half_width*k/(p.samples*3),p)
                  for k in range(p.samples*3+1)],p.rib_radius*1.1,"arch")
    create_curve(target,"R29_TRANSVERSE_OUTER_POINTED_ARCH",
                 [point(1,-p.half_width+2*p.half_width*k/(p.samples*3),p)
                  for k in range(p.samples*3+1)],p.rib_radius*1.1,"arch")
    create_curve(target,"R29_CROWN_RIDGE",
                 [point(k/p.samples,0,p) for k in range(p.samples+1)],
                 p.rib_radius*0.75,"ridge")
    for side, y in [("SOUTH",-p.half_width),("NORTH",p.half_width)]:
        receiver(target,"R29_OUTER_BEARING_"+side,
                 p.inner_x+p.radial_span,y+p.center_y,p.outer_spring,p)
    return len(target.objects)

def validate_parameters(p):
    if p.radial_span < 100 or p.half_width < 200:
        raise ValueError("Spans too small for this native-scale study.")
    if p.transverse_rise <= p.half_width:
        raise ValueError("Pointed-arch rise must exceed half-width.")
    if p.web_thickness >= p.transverse_rise or p.receiver_depth >= p.radial_span:
        raise ValueError("Thickness or receiving block is too large.")
    if p.inner_spring <= 0 or p.outer_spring <= 0:
        raise ValueError("Springing must be above floor.")

def remove_owned_object(obj):
    data = obj.data
    kind = obj.type
    bpy.data.objects.remove(obj, do_unlink=True)
    if data and data.users == 0:
        if kind == 'MESH':
            bpy.data.meshes.remove(data)
        elif kind == 'CURVE':
            bpy.data.curves.remove(data)

def do_rebuild(scene):
    assert_reference_untouched(scene)
    p=scene.f5zp_axial
    validate_parameters(p)
    existing=bpy.data.collections.get(GEN_COLL)
    if existing:
        unexpected=[o.name for o in existing.objects if o.get("F5ZP_OWNER")!=OWNER]
        if unexpected:
            raise RuntimeError("Generated collection contains unowned objects: "+str(unexpected))
    trial=bpy.data.collections.new("__R29_BUILD_TRANSACTION")
    scene.collection.children.link(trial)
    try:
        count=build_geometry(scene,trial,p)
        if count!=17:
            raise RuntimeError(f"Unexpected object count {count}; prior version retained.")
        for o in trial.objects:
            if o.get("F5ZP_OWNER")!=OWNER:
                raise RuntimeError("Unowned generated object")
        assert_reference_untouched(scene)
        if existing:
            for o in list(existing.objects):
                remove_owned_object(o)
        else:
            existing=collection(scene,GEN_COLL)
        for o in list(trial.objects):
            canonical=re.sub(r'\.\d{3}$','',o.name)
            o.name=canonical
            trial.objects.unlink(o)
            existing.objects.link(o)
        scene["R29_LAST_BUILD_COUNT"]=count
        scene["R29_GENERATED_STATUS"]="EXPERIMENTAL_NOT_APPROVED"
        scene["R29_CROWN_ESTIMATE"]=round((p.inner_spring+p.outer_spring)/2 + p.transverse_rise + p.longitudinal_lift,3)
        return count
    finally:
        for o in list(trial.objects):
            remove_owned_object(o)
        bpy.data.collections.remove(trial)

class F5ZP_AxialParameters(bpy.types.PropertyGroup):
    inner_x: bpy.props.FloatProperty(name="Junction X",default=25382.51,precision=2)
    center_y: bpy.props.FloatProperty(name="Center Y",default=0.0,precision=2)
    radial_span: bpy.props.FloatProperty(name="Axial depth",default=1515.49,min=100,max=6000,precision=2)
    half_width: bpy.props.FloatProperty(name="Half width",default=1160.0,min=200,max=4000,precision=2)
    inner_spring: bpy.props.FloatProperty(name="Inner spring Z",default=3000.0,min=100,max=10000)
    outer_spring: bpy.props.FloatProperty(name="Outer spring Z",default=2300.0,min=100,max=10000)
    transverse_rise: bpy.props.FloatProperty(name="Pointed rise",default=1180.0,min=100,max=6000)
    longitudinal_lift: bpy.props.FloatProperty(name="Crown adjustment",default=220.0,min=-1500,max=4000)
    web_thickness: bpy.props.FloatProperty(name="Web thickness",default=56.0,min=5,max=300)
    rib_radius: bpy.props.FloatProperty(name="Rib radius (trial)",default=30.0,min=2,max=200)
    receiver_depth: bpy.props.FloatProperty(name="Receiver depth",default=210.0,min=20,max=800)
    receiver_width: bpy.props.FloatProperty(name="Receiver width",default=180.0,min=20,max=800)
    samples: bpy.props.IntProperty(name="Surface samples",default=24,min=12,max=96)

class F5ZP_OT_Rebuild(bpy.types.Operator):
    bl_idname="f5zp.rebuild_axial_junction"
    bl_label="Rebuild Axial Junction"
    bl_description="Regenerate only owned R29 meshes and ribs after verifying R28 source hash"
    bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        try:
            count=do_rebuild(context.scene)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, f"Rebuilt {count} experimental objects; references verified")
        return {'FINISHED'}

class F5ZP_OT_Checkpoint(bpy.types.Operator):
    bl_idname="f5zp.save_axial_checkpoint"
    bl_label="Save New Checkpoint"
    bl_description="Save a new versioned Blender file without overwriting this checkpoint"
    def execute(self,context):
        scene=context.scene
        try:
            assert_reference_untouched(scene)
            if not bpy.data.filepath:
                raise RuntimeError("Save the initial R29 blend first")
            current=Path(bpy.data.filepath)
            if FILE_STEM not in current.name:
                raise RuntimeError("Not in the R29 live study")
            versions=[int(m.group(1)) for f in current.parent.glob(FILE_STEM+"_V*.blend")
                     if (m:=re.search(r"_V(\d+)\.blend$",f.name))]
            nxt=max(versions+[0])+1
            destination=current.parent/(FILE_STEM+f"_V{nxt:02d}.blend")
            if destination.exists():
                raise RuntimeError("Checkpoint already exists")
            bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
            self.report({'INFO'},"Saved "+destination.name)
            return {'FINISHED'}
        except Exception as exc:
            self.report({'ERROR'},str(exc))
            return {'CANCELLED'}

class F5ZP_PT_AxialPanel(bpy.types.Panel):
    bl_label="Axial Junction R29 | Experimental"
    bl_idname="F5ZP_PT_live_axial"
    bl_space_type="VIEW_3D"
    bl_region_type="UI"
    bl_category="F5ZP"
    def draw(self,context):
        layout=self.layout
        scene=context.scene
        p=getattr(scene,"f5zp_axial",None)
        if p is None:
            layout.label(text="Enable the F5ZP add-on")
            return
        layout.label(text="R28 protected: "+("YES" if scene.get(MANIFEST_KEY) else "NO"),icon="LOCKED")
        layout.label(text="Status: experimental only",icon="INFO")
        layout.label(text="Source units: native 1:1")
        col=layout.column(align=True)
        for field in ("inner_x","center_y","radial_span","half_width",
                      "inner_spring","outer_spring","transverse_rise","longitudinal_lift",
                      "web_thickness","rib_radius","receiver_depth","receiver_width","samples"):
            col.prop(p,field)
        layout.separator()
        layout.operator("f5zp.rebuild_axial_junction",icon="FILE_REFRESH")
        layout.operator("f5zp.save_axial_checkpoint",icon="FILE_TICK")
        layout.label(text="F5ZL-C bearing approval unresolved")
        layout.label(text="Physical unit conversion unresolved")

classes=(F5ZP_AxialParameters,F5ZP_OT_Rebuild,F5ZP_OT_Checkpoint,F5ZP_PT_AxialPanel)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.f5zp_axial=bpy.props.PointerProperty(type=F5ZP_AxialParameters)
def unregister():
    del bpy.types.Scene.f5zp_axial
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
if __name__=="__main__":
    register()
