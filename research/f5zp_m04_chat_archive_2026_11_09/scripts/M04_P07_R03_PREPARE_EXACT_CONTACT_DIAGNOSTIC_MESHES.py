#!/usr/bin/env python3
"""Build exact 2D source-contact polygons as FLAT diagnostics ONLY.
Never creates stone; every triangle must match original Shapely area.
Generated JSON read by Blender 5.2.3 (no Shapely dependency in Blender).
"""
from pathlib import Path
import json,hashlib
from shapely.geometry import shape
from shapely import constrained_delaunay_triangles
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
P=R/"M04_P07_R02_EXACT_TOP_BED_NATIVE_SOURCE_BEARINGS_EXPERIMENTAL"
O=R/"M04_P07_R03_B523_3D_SOURCE_CONTACT_DIAGNOSTICS_EXPERIMENTAL"
assert not O.exists(),"Preserve previous diagnostic"
O.mkdir()
src=P/"M04_P07_R02_EXACT_TOP_AND_ACTUAL_FIVE_ARCHES.geojson"
q=P/"M04_P07_R02_EXACT_NATIVE_SOURCE_BEARING_QA.json"
assert src.is_file() and q.is_file()
data=json.loads(src.read_text())["features"]
select=lambda n:n=="R03_ORIGINAL_UPPER_WALL_CONTACT" or n.startswith("R03_LOCAL_BEARING_ON_TAS_") or n=="P07_SOURCE_SPRINGER_SHOULDER_UNCERTAIN_DO_NOT_FILL"
out=[]
for f in data:
 n=f["properties"]["name"]
 if not select(n):continue
 geom=shape(f["geometry"])
 polys=[geom] if geom.geom_type=="Polygon" else list(geom.geoms)
 vertices=[];faces=[]
 for poly in polys:
  ts=constrained_delaunay_triangles(poly).geoms
  for tri in ts:
   coords=list(tri.exterior.coords)[:3]
   indices=[]
   for x,y in coords:
    indices.append(len(vertices))
    vertices.append([round(float(x),8),round(float(y),8),2400.7])
   faces.append(indices)
 assert len(faces)>=2
 shoelace=sum(abs((vertices[a][0]*(vertices[b][1]-vertices[c][1])+
                  vertices[b][0]*(vertices[c][1]-vertices[a][1])+
                  vertices[c][0]*(vertices[a][1]-vertices[b][1]))*.5) for a,b,c in faces)
 assert abs(shoelace-geom.area)<.001,(n,shoelace,geom.area)
 out.append({"name":n,"vertices":vertices,"faces":faces,
  "original_area_native_sq":geom.area,"zero_thickness_diagnostic_surface":True,
  "not_masonry":True,"material_group":"wall" if n.startswith("R03_ORIGINAL_UPPER_WALL") else "shoulder" if n.startswith("P07_") else "bearing"})
assert len(out)==7,len(out)
(O/"M04_P07_R03_TRUE_SOURCE_DIAGNOSTIC_SURFACE_TRIANGLES.json").write_text(json.dumps({
 "schema":"p07_source_face_triangulation_v1",
 "coordinate_frame":"source original 1:1 Blender native Z-up, XY true, markers displaced only +0.7 native in height",
 "source_geojson_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),
 "geometry":out},separators=(",",":"))+"\n")
print("P07_3D_DIAGNOSTIC_MESHES_PREPARED",len(out),"surface triangles",sum(len(q["faces"]) for q in out),
      "TRUE_SOURCE_SHA",hashlib.sha256(src.read_bytes()).hexdigest()[:15])
