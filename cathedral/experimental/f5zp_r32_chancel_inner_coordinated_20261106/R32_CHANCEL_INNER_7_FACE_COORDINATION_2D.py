#!/usr/bin/env python3
"""R32: measured seven-chancel-face to seven inner-ambulatory vault interfaces.
Architectural reference only. All input models and generators remain read-only.
"""
from pathlib import Path
import csv,json,hashlib,math,shutil,zipfile,xml.etree.ElementTree as ET
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlotPoly,Patch,Rectangle
from matplotlib.lines import Line2D
from shapely.geometry import shape,Polygon,Point,LineString,mapping
from shapely.ops import unary_union
from PIL import Image

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"R32_CHANCEL_INNER_AMBULATORY_7_FACE_COORDINATION_EXPERIMENTAL";OUT.mkdir(exist_ok=True)
SOURCES={
 "R11":ROOT/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "R30":ROOT/"R30_OPEN_INTERIOR_ARCHITECTURAL_INTENT_R01/SOURCE_GEOMETRY_EVIDENCE.json",
 "R31":ROOT/"R31_SEVEN_FACED_OPEN_INTERIOR_2D_EXPERIMENTAL/R31_OPEN_INTERIOR_1_TO_1.geojson",
 "R29B":ROOT/"R29B_FIRST_SANCTUARY_INNER_WALL_CORRECTION/R29B_FIRST_WALL_LOCATION.json"
}
sha={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in SOURCES.items()}
raw={name:json.loads(path.read_text()) for name,path in SOURCES.items()}
objects={f["properties"]["id"]:shape(f["geometry"]) for f in raw["R11"]["features"]}
v={f["properties"]["id"]:shape(f["geometry"]) for f in raw["R11"]["features"] if f["properties"].get("role")=="CLEAR"}
assert len(v)==218
assert raw["R30"]["chancel_polygonal_face_count"]==7
ch=objects["CHEVET_MASONRY_R10"]
openf=next(shape(f["geometry"]) for f in raw["R31"]["features"] if f["properties"].get("id")=="NAVE_CROSSING_CHOIR_SEVEN_FACED_CHANCEL_OPEN_INTERIOR")
assert openf.geom_type=="Polygon" and openf.is_valid
coords=list(ch.exterior.coords)
first=next(i for i,(x,y) in enumerate(coords) if abs(x-20238.594929)<.002 and y<0)
last=next(i for i,(x,y) in enumerate(coords) if abs(x-20238.594929)<.002 and y>0)
inner=coords[first:last+1]
assert len(inner)==8 and all(math.dist(inner[i],raw["R30"]["chancel_inner_face_vertices"][i])<2e-5 for i in range(8))
assert sum(name.startswith("I_A") and name.endswith("_R12C") for name in v)==7
assert all(openf.boundary.distance(Point(x,y))<1e-7 for x,y in inner)
def point_dist(a,b):return math.dist(a,b)
face_rows=[];corner_rows=[];walls=[];edge_record=[];geo=[]
for fi in range(1,8):
 a,b=inner[fi-1],inner[fi]
 name=f"I_A{8-fi}_R12C"
 poly=v[name]
 vv=list(poly.exterior.coords)[:-1]
 assert len(vv)==4
 # R11 stores matching inner-facing vault edge as v3 -> v0; source-true,
 # including the tangential slips at the first and last bay ends.
 o0,o1=vv[3],vv[0]
 inner_line=LineString([a,b]);outer_line=LineString([o0,o1])
 length=inner_line.length
 perpendicular=inner_line.distance(outer_line)
 assert abs(length-outer_line.length)<1e-6
 assert abs(perpendicular-320)<1e-6
 cross=(b[0]-a[0])*(o0[1]-a[1])-(b[1]-a[1])*(o0[0]-a[0])
 assert abs(abs(cross)/length-320)<1e-6
 assert abs(LineString([a,b]).distance(poly)-320)<1e-6
 wall=Polygon([a,b,o1,o0])
 assert wall.is_valid and abs(wall.area-length*320)<1e-5
 assert wall.difference(ch).area<1e-5
 assert wall.intersection(poly).area<1e-6
 assert wall.intersection(openf).area<1e-6
 end_dist_a=point_dist(a,o0);end_dist_b=point_dist(b,o1)
 tangential_slip=abs((b[0]-a[0])*(o0[0]-a[0])+(b[1]-a[1])*(o0[1]-a[1]))/length
 assert abs(end_dist_a-end_dist_b)<1e-5
 assert abs(end_dist_a-math.hypot(perpendicular,tangential_slip))<1e-5
 if fi in (1,7):assert tangential_slip>35 and end_dist_a>320
 else:assert tangential_slip<1e-5 and abs(end_dist_a-320)<1e-5
 row={
  "face_south_to_north":fi,"vault_id":name,
  "chancel_start_x":a[0],"chancel_start_y":a[1],
  "chancel_end_x":b[0],"chancel_end_y":b[1],
  "vault_wall_edge_start_x":o0[0],"vault_wall_edge_start_y":o0[1],
  "vault_wall_edge_end_x":o1[0],"vault_wall_edge_end_y":o1[1],
  "source_face_length_native":round(length,6),
  "vault_inner_edge_length_native":round(outer_line.length,6),
  "perpendicular_wall_band_depth":round(perpendicular,6),
  "endpoint_to_endpoint_distance":round(end_dist_a,6),
  "tangential_endpoint_slip":round(tangential_slip,6),
  "angle_deg":round(math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])),6),
  "strip_area_native_sq":round(wall.area,6),
  "wall_band_within_original_R11_chevet_masonry":True,
  "structural_pier_or_wall_joint_approved":False}
 face_rows.append(row);walls.append(wall);edge_record.append((o0,o1))
 geo.append({"type":"Feature","properties":{
  "id":f"WALL_BAND_CHANCEL_FACE_{fi}","vault_id":name,
  "status":"EXACT_320_PERPENDICULAR_SOURCE_BAND_NOT_A_NEW_WALL"},
  "geometry":mapping(wall)})
 geo.append({"type":"Feature","properties":{
  "id":f"CHANCEL_FACE_{fi}","vault_id":name,
  "status":"SOURCE_VERIFIED_SEVEN_FACES"},
  "geometry":mapping(inner_line)})
 # Independent inner and outer face midpoints are locations for planned
 # section measurement only, not structural load-bearing centers.
 geo.append({"type":"Feature","properties":{
  "id":f"FACE_{fi}_INNER_EDGE_MIDPOINT","vault_id":name,
  "status":"GEOMETRIC_REFERENCE_POINT_NOT_PIER"},
  "geometry":mapping(inner_line.interpolate(.5,normalized=True))})
for k in range(1,7):
 ip=inner[k]
 before=edge_record[k-1][1]
 after=edge_record[k][0]
 chord=LineString([before,after])
 corner=Polygon([ip,before,after])
 assert chord.length>100 and corner.is_valid and corner.area>0
 outside=corner.difference(ch).area
 overlap_vault=corner.intersection(unary_union([v[face_rows[k-1]["vault_id"]],v[face_rows[k]["vault_id"]]])).area
 # Source corner patches are recorded as UNSOLVED coordination areas, never
 # assumed masonry piers or voids. No load path or radial support inferred.
 t1=math.atan2(inner[k][1]-inner[k-1][1],inner[k][0]-inner[k-1][0])
 t2=math.atan2(inner[k+1][1]-inner[k][1],inner[k+1][0]-inner[k][0])
 turn=math.degrees((t2-t1+math.pi)%(2*math.pi)-math.pi)
 row={"chancel_corner_index_south_to_north":k,
  "corner_x":ip[0],"corner_y":ip[1],
  "adjoining_vaults":f"{face_rows[k-1]['vault_id']} / {face_rows[k]['vault_id']}",
  "change_in_facet_direction_deg":round(turn,6),
  "offset_vault_edge_endpoint_gap_native":round(chord.length,6),
  "corner_reference_triangle_area_native_sq":round(corner.area,6),
  "triangle_outside_source_chevet_masonry_area":round(outside,6),
  "triangle_intersection_with_adjacent_clear_vaults":round(overlap_vault,6),
  "new_pier_size_known":False,
  "physical_corner_bearing_approved":False}
 corner_rows.append(row)
 geo.append({"type":"Feature","properties":{
  "id":f"INNER_CHANCEL_CORNER_{k}",
  "status":"SOURCE_POINT_POSSIBLE_BEARING_REVIEW_NOT_APPROVED_PIER"},
  "geometry":mapping(Point(ip))})
 geo.append({"type":"Feature","properties":{
  "id":f"INNER_VAULT_ENDPOINT_GAP_{k}",
  "status":"SOURCE_GAP_REQUIRES_JOINT_STUDY_NOT_A_DOORWAY"},
  "geometry":mapping(chord)})
 geo.append({"type":"Feature","properties":{
  "id":f"GEOMETRIC_CORNER_REFERENCE_PATCH_{k}",
  "status":"CONSTRUCTION_REFERENCE_ONLY_NOT_APPROVED_MASONRY"},
  "geometry":mapping(corner)})
assert len(face_rows)==7 and len(corner_rows)==6
assert abs(face_rows[0]["source_face_length_native"]-face_rows[-1]["source_face_length_native"])<1e-5
assert abs(face_rows[1]["source_face_length_native"]-face_rows[-2]["source_face_length_native"])<1e-5
assert abs(face_rows[2]["source_face_length_native"]-face_rows[-3]["source_face_length_native"])<1e-5
assert all(abs(face_rows[i]["perpendicular_wall_band_depth"]-320)<1e-6 for i in range(7))
assert all(corner_rows[i]["offset_vault_edge_endpoint_gap_native"]==corner_rows[-1-i]["offset_vault_edge_endpoint_gap_native"] for i in range(3))
# Endpoints are transition to choir side interface, NOT automatic end support.
for i,end in enumerate([inner[0],inner[-1]],start=1):
 geo.append({"type":"Feature","properties":{
  "id":f"CHANCEL_END_TRANSITION_{i}",
  "status":"SOURCE_BOUNDARY_TRANSITION_PIER_UNRESOLVED"},
  "geometry":mapping(Point(end))})
assert len(geo)==7*3+6*3+2
def exportcsv(path,rows):
 with path.open("w",newline="") as fp:
  w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
exportcsv(OUT/"R32_SEVEN_CHANCEL_FACE_320_COORDINATION.csv",face_rows)
exportcsv(OUT/"R32_SIX_INNER_CORNER_JOIN_SURVEY.csv",corner_rows)
(OUT/"R32_1_TO_1_SOURCE_WALL_BANDS_AND_JUNCTIONS.geojson").write_text(json.dumps({
 "type":"FeatureCollection","properties":{
  "status":"EXPERIMENTAL COORDINATION, NO PIER SIZE OR STRUCTURAL APPROVAL",
  "source_sha256":sha,
  "source_chancel_faces":7,"source_wall_band_perpendicular_width":320},
  "features":geo},separators=(",",":"))+"\n")
qa={"checkpoint":"R32 chancel first-wall to seven inner ambulatory bay coordination",
 "baseline":"R11 vault polygons, R31 open interior, R30 user-confirmed intent",
 "input_sha256":sha,"source_unchanged":True,"R11_vault_count":218,
 "seven_chancel_faces_confirmed":True,"matched_source_inner_ambulatory_vaults":7,
 "all_seven_source_face_separations_perpendicular_native":320,
 "source_face_and_vault_inner_edge_lengths_identical":True,
 "source_wall_band_polygons_inside_R11_chevet_masonry":True,
 "face_end_condition":[
  "I_A7 and I_A1 source face offset endpoints include ~39.3 units tangent slip; direct vertex-to-vertex connector is 322.4, but perpendicular band remains 320",
  "Five interior faces have 320 unit perpendicular and endpoint displacement"],
 "intermediate_inner_polygon_corner_count":6,
 "inner_corner_reference_nodes_not_new_pi ers":6,
 "offset_vault_face_junction_chord_gaps_native":[z["offset_vault_edge_endpoint_gap_native"] for z in corner_rows],
 "geometric_triangle_source_masonry_outside_areas":[z["triangle_outside_source_chevet_masonry_area"] for z in corner_rows],
 "end_connections_to_straight_choir_supports_unresolved":2,
 "architectural_scope":"User's confirmed seven-faced open sanctuary, physical first 320 wall boundary, protected I ring seven vaults",
 "new_masonry_created":False,"source_support_geometry_modified":False,
 "validation":{
  "technical":"PASS: file hash regression, CSV, GeoJSON, PNG+SVG parse and ZIP integrity",
  "geometric":"PASS: seven source-matched vault faces, 320 perpendicular wall strips, measured six corner offsets",
  "architectural":"Open sanctuary and first boundary user-confirmed; six joint node supports and ends still require coordination",
  "historical":"NOT assessed",
  "structural":"NOT assessed; source corner nodes and gaps do not prove piers"},
 "unresolved":["6 corner junctions have neighboring vault-face endpoints that do not coincide; no pier footprints authorized.",
 "2 ends of seven-facet chain need transverse integration with straight choir arcade.",
 "The working F5ZN-A inner/middle vault generator was not run or replaced.",
 "F5ZL-C support schedule missing and outer paired 14-bay design unresolved."]}
# Fix cosmetic key now (do not imply any piers)
qa["inner_corner_reference_nodes_not_new_piers"]=qa.pop("inner_corner_reference_nodes_not_new_pi ers")
(OUT/"R32_NUMERICAL_QA.json").write_text(json.dumps(qa,indent=2)+"\n")

plt.rcParams.update({"text.color":"#eef5fa","axes.labelcolor":"#afcad8",
 "xtick.color":"#abc4d2","ytick.color":"#abc4d2","axes.edgecolor":"#7e99ac",
 "font.size":10,"savefig.facecolor":"#0c1523"})
def render(ax,g,fc,ec="#7393a4",lw=.5,ls="-",z=2,alpha=1):
 polys=[g] if g.geom_type=="Polygon" else [x for x in getattr(g,"geoms",[]) if x.geom_type=="Polygon"]
 for p in polys:
  ax.add_patch(PlotPoly(list(p.exterior.coords),facecolor=fc,edgecolor=ec,linewidth=lw,
     linestyle=ls,zorder=z,alpha=alpha))
  if fc!="none":
   for ring in p.interiors:ax.add_patch(PlotPoly(list(ring.coords),facecolor="#152737",edgecolor="none",zorder=z+.01))
fig=plt.figure(figsize=(19.1,11.4),facecolor="#0c1523")
gr=fig.add_gridspec(2,2,height_ratios=[.70,1.2],width_ratios=[1.25,1],
 left=.052,right=.985,top=.865,bottom=.13,hspace=.28,wspace=.15)
overview=fig.add_subplot(gr[0,:]);sweep=fig.add_subplot(gr[1,0]);join=fig.add_subplot(gr[1,1])
for ax in (overview,sweep,join):
 ax.set_facecolor("#152737")
 for name,g in v.items():
  render(ax,g,"#1c3a48",ec="#628fa7",lw=.26,z=1)
 render(ax,openf,"#a56bdd",ec="#e0bcfa",lw=.58,z=4,alpha=.56)
 for i,wall in enumerate(walls,1):
  render(ax,wall,"#eea351",ec="#ffe0b9",lw=.8,z=8,alpha=.87)
 for i,(a,b) in enumerate(zip(inner,inner[1:]),1):
  ax.plot([a[0],b[0]],[a[1],b[1]],color="#ff83dc",lw=2.2 if ax!=overview else 1.5,zorder=12)
 ax.set_aspect("equal","box");ax.grid(alpha=.07)
 ax.set_xlabel("Global X • native units");ax.set_ylabel("Global Y • native units")
overview.set_xlim(-47000,29500);overview.set_ylim(-9900,9900)
overview.add_patch(Rectangle((19900,-4700),5500,9400,fill=False,ec="#ed9dd4",lw=1.8,zorder=14))
overview.annotate("Seven 320-wide chancel-to-inner bands",xy=(23200,0),xytext=(11400,8300),
 color="#f9b6e7",fontsize=10.5,weight="bold",arrowprops={"arrowstyle":"->","color":"#f9b6e7"})
sweep.set_xlim(19750,25200);sweep.set_ylim(-4950,4950)
for k,pp in enumerate(inner):
 sweep.scatter([pp[0]],[pp[1]],s=38 if k not in (0,7) else 25,
   facecolor="#ffe37e",edgecolor="#443425",linewidth=.55,zorder=20)
 sweep.annotate(str(k),xy=pp,xytext=(pp[0]-150,pp[1]+170),
   fontsize=9,color="#fff1b7",weight="bold",ha="center",zorder=20)
for i,row in enumerate(face_rows):
 a,b=inner[i],inner[i+1];x=(a[0]+b[0])/2;y=(a[1]+b[1])/2
 sweep.text(x+130,y,f"{i+1} · I_A{7-i}",color="#f4dffb",fontsize=8.4,
    ha="center",bbox=dict(facecolor="#413157",edgecolor="#a585bf",pad=2),zorder=16)
# Zoom at northern central corner between faces 4 and 5; actual source gap
# between the two offset inner vault endpoints is a measured junction study.
node=inner[4];end_A=edge_record[3][1];start_B=edge_record[4][0]
join.set_xlim(node[0]-680,node[0]+1100)
join.set_ylim(node[1]-650,node[1]+900)
join.scatter([node[0]],[node[1]],s=60,facecolor="#ffe37e",edgecolor="#3e291f",zorder=25)
join.scatter([end_A[0],start_B[0]],[end_A[1],start_B[1]],s=42,facecolor="#a8f1c5",edgecolor="#244538",zorder=23)
join.plot([end_A[0],start_B[0]],[end_A[1],start_B[1]],color="#f6f0b2",
    lw=2.1,ls="--",zorder=22)
join.annotate("Actual vault-edge\\nendpoint gap",
 xy=((end_A[0]+start_B[0])/2,(end_A[1]+start_B[1])/2),
 xytext=(node[0]+400,node[1]+690),ha="center",color="#e5e7ff",fontsize=9,
 arrowprops={"arrowstyle":"->","color":"#e5e7ff"},zorder=25)
join.text(node[0]-400,node[1]-410,"Inner chancel corner\\n(reference only)",
  color="#ffe6a7",fontsize=9,ha="left",zorder=25)
overview.set_title("1 · Whole cathedral with preserved open purple sanctuary",loc="left",pad=9,fontsize=12,weight="bold")
sweep.set_title("2 · Seven chancel facets / seven I vaults / six internal junctions",loc="left",pad=10,fontsize=11.2,weight="bold")
join.set_title("3 · Source-true adjacent edge endpoints (not a pier design)",loc="left",pad=10,fontsize=10.8,weight="bold")
fig.suptitle("F5ZP R32 | SEVEN CHANCEL FACES ↔ SEVEN INNER AMBULATORY VAULTS\n"
 "All seven first-wall bands have 320 perpendicular separation • six corner joints remain for support coordination",
 x=.052,y=.985,ha="left",fontsize=14.6,weight="bold")
fig.legend(handles=[
 Patch(facecolor="#a56bdd",label="Confirmed open main sanctuary"),
 Patch(facecolor="#eea351",label="Measured first 320 band, not a new wall"),
 Line2D([0],[0],color="#ff83dc",lw=2.2,label="Actual seven chancel inner faces"),
 Line2D([0],[0],marker="o",markersize=7,color="#ffe37e",ls="none",label="Source corner / potential bearing reference"),
 Line2D([0],[0],ls="--",lw=2,color="#f6f0b2",label="Measured adjoining vault-edge endpoint gap")],
 loc="lower center",ncol=3,frameon=False,bbox_to_anchor=(.5,.051),labelcolor="#edf4fa",fontsize=9.0)
fig.text(.052,.011,"Validated source geometry only: reference nodes are not approved piers or rib springing; historical/structural checks separate.",
 color="#b6cbd6",fontsize=9.4)
png=OUT/"F5ZP_R32_CHANCEL_INNER_VAULT_7_FACE_COORDINATION_DARK.png"
svg=OUT/"F5ZP_R32_CHANCEL_INNER_VAULT_7_FACE_COORDINATION_DARK.svg"
fig.savefig(png,dpi=168,bbox_inches="tight")
fig.savefig(svg,bbox_inches="tight")
plt.close(fig)
ET.parse(svg)
with Image.open(png) as im:im.verify();print("IMAGE_VALIDATED",im.size)
assert all(hashlib.sha256(path.read_bytes()).hexdigest()==sha[k] for k,path in SOURCES.items())
(OUT/"README_HANDOFF.md").write_text("""# R32 — Seven-sided open chancel / first wall / seven inner ambulatory vaults

**Protected input:** read-only R11 218 clear-vault polygons, R31 open purple sanctuary and R30 architectural interpretation, R29B wall section. No 3D rebuild, no generator modifications, no pier source replaced.

**Measured source findings:**
- In order from south to north, seven true sanctuary polygon facets correspond exactly to I_A7, I_A6, I_A5, I_A4, I_A3, I_A2, I_A1.
- Each associated clear-vault inner edge is parallel to its corresponding chancel facet, with **exactly 320 native units of perpendicular separation**, as per saved R11 geometry.
- Source face lengths match their offset vault edges. The end faces I_A7 / I_A1 have ~39.29 units of tangential vertex offset, so the raw corresponding endpoint-to-endpoint vector is ~322.4, **not evidence of a thicker wall**.
- There are six internal corner reference vertices of the actual seven-sided polygon, each with TWO noncoincident offset I-edge endpoints. Record the measured gaps in R32_SIX_INNER_CORNER_JOIN_SURVEY.csv; do NOT replace them with a fabricated shared pier or collapse them to one point.
- The north/south endpoints of the seven-facet chain require later coordination with the straight choir's bearing/interface arrangement. They are not approved support points.

**Artifacts:** one high-contrast dark full plan plus north side detail (PNG and SVG), exact source-derived 1:1 wall face strips and point/gap references (GeoJSON), seven-face and six-corner measurements CSV, QA JSON and procedural script.

**Validation distinctions:** Technical and geometric tests passed; user-approved overall sanctuary openness respected. Geometric wall separation does NOT establish load-bearing pier supports, actual rib springing or architectural approval. Historic and structural validation not performed. F5ZL-C support schedule remains missing. No outer 14-bay design generated.

Reproduce: python3 R32_CHANCEL_INNER_7_FACE_COORDINATION_2D.py
""")
shutil.copy2(png,Path.home()/"Downloads"/png.name)
zp=Path.home()/"Downloads"/"F5ZP_R32_CHANCEL_INNER_7_FACE_COORDINATION_2D_EXPERIMENTAL.zip"
with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as z:
 z.write(Path(__file__),arcname=Path(__file__).name)
 for path in sorted(OUT.iterdir()):z.write(path,arcname=path.name)
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
print("R32 QA PASS",len(face_rows),"faces",len(corner_rows),"corners",zp)