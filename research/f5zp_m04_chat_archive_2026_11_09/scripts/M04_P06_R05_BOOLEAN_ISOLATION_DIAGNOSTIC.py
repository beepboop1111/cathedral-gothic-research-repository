#!/usr/bin/env python3
"""F5ZP M04 P06 — Blender 5.2.3 exact-boolean masonry coordination.

Goal: preserve actual R03 source arch/world geometry and source-restored
R14 five tas-de-charge courses; exactly truncate the *EXPERIMENTAL COPY*
of upper wall and ribs at the Z2400 interface; quantify prior double
masonry volume and leave upper exposed shoulder unfilled. Source R03 is
never saved and remains unmodified. All coordinates 1:1 native units.
"""
import bpy,bmesh,hashlib,json,math,csv
from pathlib import Path
from mathutils import Vector, Matrix
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
SOURCE=Path("/home/christopher/Documents/Cathedral/experimental/WALL_PIER_JUNCTION_R03/WALL_PIER_JUNCTION_R03.blend")
CAND=R/"M04_P05_BLENDER523_R14_CANONICAL_FIVE_SOURCE_EXPERIMENTAL/build/springer_variant.glb"
PREV=R/"M04_P05_BLENDER523_FULL_COMPATIBILITY_REGRESSION_EXPERIMENTAL/M04_P05_B523_FINAL_COMPARATIVE_REGRESSION.json"
O=R/"M04_P06_R05_BOOLEAN_DIAGNOSTIC_EXPERIMENTAL"
assert bpy.app.version[:2]==(5,2),bpy.app.version_string
assert all(p.is_file() for p in (SOURCE,CAND,PREV))
assert not O.exists(),"Existing approved or experimental P06 output protected"
O.mkdir()
sh={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,CAND,PREV)}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
source_objects=[ob for ob in bpy.data.objects if ob.type=="MESH"]
assert len(source_objects)==247,len(source_objects)
five=("CHAPEL_TRANSVERSE_31000","BAY1_RIB_1","BAY2_RIB_0","BAY1_FORMERET_0","BAY2_FORMERET_0")
lower=("SHARED_PIER_S","RECEIVING_S_LOWER_0","RECEIVING_S_LOWER_1")
upper="RECEIVING_S_UPPER_0"
for n in (*five,*lower,upper):assert n in bpy.data.objects
orig_fingerprint={}
for name in (*five,*lower,upper):
 ob=bpy.data.objects[name]
 orig_fingerprint[name]=(len(ob.data.vertices),len(ob.data.polygons),sum(round(v.co.x,6) for v in ob.data.vertices))
# Keep original mesh data untouched; analyze on copies.
bpy.ops.object.select_all(action="DESELECT")
existing=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(CAND))
imported=[o for o in bpy.data.objects if o not in existing]
members=[o for o in imported if o.type=="MESH"]
assert len(members)==12,(len(members),[m.name for m in members])
origin=Vector((31000.,-1250.,1800.))
for o in imported:
 if o.parent not in imported:o.matrix_world=Matrix.Translation(origin)@o.matrix_world
courses=[next(x for x in members if x.name==f"course_{j:02d}") for j in range(1,6)]
# No normals/materials/matrix changes on source; world-space copies used.
def world_copy(obj,label,weld=False):
 mesh=obj.data.copy()
 mesh.name=label+"_DATA"
 mesh.transform(obj.matrix_world)
 if weld:
  bm=bmesh.new()
  bm.from_mesh(mesh)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.006)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  bm.to_mesh(mesh);bm.free();mesh.update()
 copied=bpy.data.objects.new(label,mesh)
 bpy.context.scene.collection.objects.link(copied)
 copied.matrix_world=Matrix.Identity(4)
 return copied
def mesh_metrics(ob):
 bm=bmesh.new();bm.from_mesh(ob.data)
 n_closed=sum(not e.is_manifold for e in bm.edges)
 vol=abs(bm.calc_volume(signed=True))
 faces=len(bm.faces)
 bm.free()
 return {"tri_or_poly_count":faces,"nonmanifold_edges":n_closed,"abs_volume_native_cubed":round(vol,6)}
def boolean_keep(a,b,operation,tag):
 # Required world-matrix already identity; no source objects as operands.
 assert a.matrix_world==Matrix.Identity(4)
 assert b.matrix_world==Matrix.Identity(4)
 mod=a.modifiers.new("P06_EXACT_"+operation,"BOOLEAN")
 mod.operation=operation
 mod.solver="EXACT"
 mod.object=b
 bpy.context.view_layer.update()
 deps=bpy.context.evaluated_depsgraph_get()
 evaluated=a.evaluated_get(deps)
 result=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
 result.name=tag+"_BOOLEAN_MESH"
 mod.object=None
 a.modifiers.remove(mod)
 duplicate=bpy.data.objects.new(tag,result)
 bpy.context.scene.collection.objects.link(duplicate)
 duplicate.matrix_world=Matrix.Identity(4)
 return duplicate
def cuboid(name,x1,x2,y1,y2,z1,z2):
 mesh=bpy.data.meshes.new(name+"_MESH")
 verts=[(x,y,z) for z in (z1,z2) for y in (y1,y2) for x in (x1,x2)]
 faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),
        (2,6,7,3),(0,4,6,2),(1,3,7,5)]
 mesh.from_pydata(verts,[],faces);mesh.update()
 ob=bpy.data.objects.new(name,mesh)
 bpy.context.scene.collection.objects.link(ob)
 return ob
# Clipping box includes source arches/z2400..5000, and source wall.
cutter=cuboid("P06_Z2400_UPPER_SOURCE_HALFSPACE",-30000,80000,-30000,30000,2400,5000)
wall_src=world_copy(bpy.data.objects[upper],"P06_TMP_UPPER_WALL_ORIGINAL")
assert mesh_metrics(wall_src)["nonmanifold_edges"]==0
copies=[world_copy(o,f"P06_TMP_COURSE_{k:02d}",weld=True) for k,o in enumerate(courses,1)]
for i,c in enumerate(copies):
 assert mesh_metrics(c)["nonmanifold_edges"]==0,(c.name,mesh_metrics(c))
def bb_debug(ob):
 pts=[v.co for v in ob.data.vertices]
 return [[round(min(v[k] for v in pts),3),round(max(v[k] for v in pts),3)] for k in range(3)]
def signed_stats(ob):
 bm=bmesh.new();bm.from_mesh(ob.data)
 v=bm.calc_volume(signed=True);f=len(bm.faces);b=sum(not e.is_manifold for e in bm.edges)
 bm.free();return round(v,4),f,b
print("P06_DEBUG_UPPER_WALL_BOUNDS",bb_debug(wall_src),signed_stats(wall_src),flush=True)
for c in copies:
 print("P06_DEBUG_COPY_COURSE",c.name,bb_debug(c),signed_stats(c),flush=True)

# PREVIOUS DUPLICATE WALL VOLUME:
prior=[]

print("P06_R05_WALL_VIS",wall_src.visible_get(),wall_src.hide_get(),wall_src.hide_viewport,wall_src.mode,flush=True)
c=copies[0]
print("P06_R05_COURSE_VIS",c.visible_get(),c.hide_get(),c.hide_viewport,c.mode,flush=True)
for desc,x,y in [("ACTUAL_COURSE_WALL",c,wall_src),
                  ("SIMPLE_TWO_BOXES",cuboid("box1",30790,31120,-1510,-1150,1810,1890),cuboid("box2",30760,31240,-1570,-1250,1800,4100)),
                  ("COURSE_BOX",c,cuboid("box3",30760,31240,-1570,-1250,1800,4100)),
                  ("BOX_WALL",cuboid("box4",30790,31120,-1510,-1150,1810,1890),wall_src)]:
 test=boolean_keep(x,y,"INTERSECT","P06_R05_TEST_"+desc)
 print("P06_DEBUG_BOOLEAN",desc,mesh_metrics(test),flush=True)
