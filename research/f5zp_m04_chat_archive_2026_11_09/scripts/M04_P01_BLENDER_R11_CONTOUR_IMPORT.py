#!/usr/bin/env python3
"""M04 P01: independent Blender round-trip of R11 library vector geometry.
49 isolated examples in a compact catalog grid, normalized width=1.
This is mesh IO testing only, not physical architectural piercing geometry.
"""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
O=R/"M04_P01_R11_SHARED_PROFILE_LIBRARY_EXPERIMENTAL"
sections=sorted((O/"R11_section_json").glob("*.json"))
assert len(sections)==49
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
sums=[]
for i,p in enumerate(sections):
 q=json.loads(p.read_text())
 assert q["schema"]=="springer_png_section_v1"
 coords=q["section"]
 n=len(coords)
 assert n>=3
 col=i%10;row=i//10
 origin=(col*2.8,row*2.8,0)
 verts=[(origin[0]+x,origin[1]+y,z) for z in (.0,.08) for x,y in coords]
 faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]
 for j in range(n):
  k=(j+1)%n
  faces.append((j,k,k+n,j+n))
 mesh=bpy.data.meshes.new(p.stem+"_MESH")
 mesh.from_pydata(verts,[],faces);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh)
 bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
 bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method="BEAUTY",ngon_method="BEAUTY")
 assert all(e.is_manifold for e in bm.edges),p.stem
 bm.to_mesh(mesh);bm.free();mesh.update()
 ob=bpy.data.objects.new("SOURCE_R11_PROFILE_"+p.stem,mesh)
 bpy.context.scene.collection.objects.link(ob)
 ob["source_section_json_sha256"]=hashlib.sha256(p.read_bytes()).hexdigest()
 ob["source_R11_schema"]="springer_png_section_v1"
 ob["source_profile_width_normalized_native"]=1.0
 ob["profile_nose_orientation_historical_verified"]=False
 ob["is_soffit_optional"]=bool(q["optional_soffit"])
 ob["architecturally_approved_profile"]=False
 sums.append({"asset":p.stem,"vertices":len(mesh.vertices),"triangles":len(mesh.polygons)})
assert len([o for o in bpy.context.scene.objects if o.type=="MESH"])==49
# One workbench review render with consistent axial orientation.
camd=bpy.data.cameras.new("SOURCE_PROFILE_LIBRARY_GRID_CAMERA")
cam=bpy.data.objects.new(camd.name,camd)
bpy.context.scene.collection.objects.link(cam)
cam.location=(13.1,5.6,65)
cam.rotation_euler=(0,0,0)
camd.type="ORTHO";camd.ortho_scale=32
sc=bpy.context.scene;sc.camera=cam
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.light="STUDIO"
sc.display.shading.color_type="SINGLE"
sc.display.shading.single_color=(.28,.40,.54)
sc.render.resolution_x=1800;sc.render.resolution_y=1120
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.view_settings.view_transform="Standard"
sc["P01"]="49 actual source-converted R11 polygons 1:1 normalized width in 3D editability test"
sc["real_cathedral_scale_assigned"]=False
sc["selected_moulding_family"]=False
sc["original_R11_engine_untouched"]=True
b=O/"M04_P01_49_R11_VECTOR_CONTOURS_BLENDER_EDITABLE.blend"
g=O/"M04_P01_49_R11_VECTOR_CONTOURS_GLTF_TEST.glb"
png=O/"M04_P01_BLENDER_CONTOUR_IMPORT_QA.png"
bpy.ops.wm.save_as_mainfile(filepath=str(b))
bpy.ops.export_scene.gltf(filepath=str(g),export_format="GLB",export_apply=False)
sc.render.filepath=str(png)
bpy.ops.render.render(write_still=True)
assert g.read_bytes()[:4]==b"glTF"
(O/"M04_P01_BLENDER_ROUNDTRIP_QA.json").write_text(json.dumps({
 "Blender_version":bpy.app.version_string,"source_png_contour_count":49,
 "mesh_objects":49,"all_prisms_closed_manifold":True,
 "export_format":"GLB","artifacts":{"blend":b.name,"glb":g.name,"PNG":png.name},
 "historical_architectural_approval":False,
 "mesh_summary":sums},indent=2)+"\n")
print("BLENDER_49_R11_CONTOUR_MESH_PASS",len(sums),bpy.app.version_string)
