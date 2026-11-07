#!/usr/bin/env python3
"""M02 Phase B final: true LINE-CONTACT preliminary support reservations at
six chancel corners and two choir/chevet ends. R11-R33 source never edited."""
from pathlib import Path
import hashlib,json,csv,math,zipfile,shutil
from shapely.geometry import shape,LineString,Point,Polygon,mapping
from shapely.ops import unary_union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPatch
from PIL import Image
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"M02_PHASE_B_COMPLETION_R03_LOCAL_EXPERIMENTAL";OUT.mkdir(exist_ok=True)
base={
"R11":ROOT/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
"R30":ROOT/"R30_OPEN_INTERIOR_ARCHITECTURAL_INTENT_R01/SOURCE_GEOMETRY_EVIDENCE.json",
"R31":ROOT/"R31_SEVEN_FACED_OPEN_INTERIOR_2D_EXPERIMENTAL/R31_OPEN_INTERIOR_1_TO_1.geojson",
"R32":ROOT/"R32_CHANCEL_INNER_AMBULATORY_7_FACE_COORDINATION_EXPERIMENTAL/R32_NUMERICAL_QA.json",
"R33":ROOT/"R33_CHANCEL_JUNCTIONS_LOCAL_EXPERIMENTAL/R33_QA.json",
"PHASE_B_R01":ROOT/"M02_PHASE_B_EIGHT_JUNCTIONS_R01_LOCAL_EXPERIMENTAL/M02_PHASE_B_NUMERICAL_QA.json",
"PHASE_B_R02":ROOT/"M02_PHASE_B_R02_FOOTPRINT_ALTERNATIVES_LOCAL_EXPERIMENTAL/M02_B_R02_NUMERICAL_QA.json",
}
hashes={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in base.items()}
docs={k:json.loads(v.read_text()) for k,v in base.items()}
F=docs["R11"]["features"]
d={f["properties"]["id"]:shape(f["geometry"]) for f in F}
v={f["properties"]["id"]:shape(f["geometry"]) for f in F if f["properties"].get("role")=="CLEAR"}
assert len(v)==218
clear=unary_union(list(v.values()))
reservation=unary_union([d["CHEVET_MASONRY_R10"],d["CHOIR_MASONRY_R10"]])
op=next(shape(f["geometry"]) for f in docs["R31"]["features"]
 if f["properties"].get("id")=="NAVE_CROSSING_CHOIR_SEVEN_FACED_CHANCEL_OPEN_INTERIOR")
assert op.is_valid and op.geom_type=="Polygon"
assert docs["R30"]["chancel_polygonal_face_count"]==7
assert docs["R32"]["matched_source_inner_ambulatory_vaults"]==7
assert docs["R33"]["two_end_transitions"]==2
ch=d["CHEVET_MASONRY_R10"];coords=list(ch.exterior.coords)
a=next(i for i,(x,y) in enumerate(coords) if 20238<x<20239 and y<0)
b=next(i for i,(x,y) in enumerate(coords) if 20238<x<20239 and y>0)
chain=coords[a:b+1]
assert len(chain)==8
walls=[];face_lines=[]
for j,(start,end) in enumerate(zip(chain,chain[1:]),1):
 I=v[f"I_A{8-j}_R12C"]
 P=list(I.exterior.coords)[:-1]
 wall=Polygon([start,end,P[0],P[3]])
 assert wall.is_valid and abs(LineString([start,end]).distance(LineString([P[3],P[0]]))-320)<1e-6
 assert wall.difference(ch).area<1e-5
 walls.append(wall)
 face_lines.append(LineString([start,end]))
source_ends={}
for side,index,rank in (("S",0,7),("N",7,1)):
 Q=v[f"Q5_{side}_A1_2"];I=v[f"I_A{rank}_R12C"]
 from shapely.ops import nearest_points
 pq,pi=nearest_points(Q,I)
 # Use strict source-derived convex hull from actual shortest segment and chancel vertex
 source_ends[side]=Polygon([chain[index],(pq.x,pq.y),(pi.x,pi.y)])
 assert source_ends[side].is_valid and source_ends[side].difference(reservation).area<1e-5
assert len(walls)==7
# R03 alternates based on R32 actual wall strip and R33 joint bridge,
# clipped only within the unmodified reserved/clear source geometry.
# Smaller/mid/larger trial radii all less than wall 320 inradius.
options={"A_NARROW":110,"B_MODERATE":180,"C_BROAD":250}
rows=[];features=[];models={}
sources=range(8)
for k in sources:
 name="END_S" if k==0 else ("END_N" if k==7 else f"C{k}")
 anchor=Point(chain[k])
 strips=[walls[0]] if k==0 else ([walls[-1]] if k==7 else [walls[k-1],walls[k]])
 if k in (0,7):
  strips+=[source_ends["S" if k==0 else "N"]]
 else:
  below=list(v[f"I_A{8-k}_R12C"].exterior.coords)[:-1][0]
  above=list(v[f"I_A{7-k}_R12C"].exterior.coords)[:-1][3]
  bridge=Polygon([chain[k],below,above])
  assert bridge.is_valid and bridge.difference(reservation).area<1e-5
  assert bridge.intersection(clear).area<1e-5
  strips.append(bridge)
 local=unary_union(strips)
 # Intersect with a circle at source vertex: nonpolygon artifacts forbidden.
 assert local.is_valid and local.geom_type in ("Polygon","MultiPolygon")
 assert local.intersection(op).area<1e-5
 assert local.difference(reservation).area<1e-5
 wall_edges=[face_lines[0]] if k==0 else ([face_lines[-1]] if k==7 else [face_lines[k-1],face_lines[k]])
 for opt,radius in options.items():
  raw=local.intersection(anchor.buffer(radius,resolution=48))
  assert raw.is_valid and raw.geom_type in ("Polygon","MultiPolygon")
  assert raw.area>1000
  assert raw.difference(reservation).area<1e-5
  protected_overlap=raw.intersection(clear).area
  open_overlap=raw.intersection(op).area
  assert protected_overlap<1e-5 and open_overlap<1e-5
  # A finite continuous source wall-edge contact, not a single-point touch.
  # Buffer tolerance handles GEOS near-collinearity in R11 source.
  contacts=[ln.intersection(raw.buffer(.0002)).length for ln in wall_edges]
  assert len(contacts)>0 and all(c>radius*.75 for c in contacts)
  # Check actual polygon may be multipart at corner; touching components
  # point-only is no good for structural connectivity, flag unresolved.
  pieces=[raw] if raw.geom_type=="Polygon" else list(raw.geoms)
  piece_count=len(pieces)
  # Geometric continuity criterion: connected, positive-area footprint
  # (not a structural certification).
  continuous=piece_count==1
  if not continuous:
   # Multipart is NOT silently joined; present as geometric failure.
   print("MULTIPART_REQUIRES_REVIEW",name,opt,piece_count)
  clearance=raw.distance(clear)
  assert clearance>1e-5
  rows.append({
   "junction":name,"option":opt,"radius_native":radius,
   "footprint_area_native_sq":round(raw.area,5),
   "wall_face_contact_1_native":round(contacts[0],5),
   "wall_face_contact_2_native":round(contacts[1],5) if len(contacts)>1 else "",
   "positive_line_contact_both_neighbor_faces":all(c>radius*.75 for c in contacts),
   "footprint_connected":continuous,
   "clearance_to_nearest_protected_vault_native":round(clearance,5),
   "protected_vault_collision_area":round(protected_overlap,8),
   "purple_open_interior_collision_area":round(open_overlap,8),
   "outside_reserved_masonry_area":round(raw.difference(reservation).area,8),
   "basis":"R11 320 wall strip + measured R33 end bridge",
   "approval":"EXPERIMENTAL GEOMETRIC RESERVATION; NOT AN APPROVED PIER",
   "structural_validation":"NOT ASSESSED"
  })
  models[(name,opt)]=raw
  features.append({"type":"Feature","properties":{"id":name+"_"+opt,
   "type":"WALL_CONNECTED_CONSTRUCTION_ENVELOPE","not_pier":True,
   "radius_native":radius},"geometry":mapping(raw)})
assert len(rows)==24
# Count measured wall contacts and full geometric pass after verification
passrows=[r for r in rows if r["positive_line_contact_both_neighbor_faces"] and r["footprint_connected"]
 and r["protected_vault_collision_area"]==0 and r["purple_open_interior_collision_area"]==0
 and r["outside_reserved_masonry_area"]==0]
for j in range(1,4):
 for opt in options:
  assert abs(models[(f"C{j}",opt)].area-models[(f"C{7-j}",opt)].area)<.02
for opt in options:
 assert abs(models[("END_S",opt)].area-models[("END_N",opt)].area)<.02
assert len(passrows)==24,(len(passrows),[(r["junction"],r["option"]) for r in rows if r not in passrows])
for name in ["C1","C2","C3","C4","C5","C6","END_S","END_N"]:
 assert models[(name,"A_NARROW")].difference(models[(name,"B_MODERATE")]).area<1e-5
 assert models[(name,"B_MODERATE")].difference(models[(name,"C_BROAD")]).area<1e-5
with (OUT/"M02_B_R03_WALL_CONNECTED_24_VARIANTS.csv").open("w",newline="") as fp:
 writer=csv.DictWriter(fp,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
(OUT/"M02_B_R03_WALL_CONNECTED_RESERVATIONS_1_TO_1.geojson").write_text(
 json.dumps({"type":"FeatureCollection","properties":{"status":"experimental first-wall bonded interface study; no approved supports",
 "source_sha256":hashes},"features":features},separators=(",",":"))+"\n")
qa={"milestone":"F5ZP M02 Phase B coordination completion R03",
 "status":"GEOMETRIC_COORDINATION_COMPLETE; ARCHITECTURAL SUPPORT DESIGN PROVISIONAL; STRUCTURAL UNRESOLVED",
 "protected_sources_unchanged":True,
 "source_sha256":hashes,
 "verified_original_vaults":218,"source_chancel_faces":7,
 "first_wall_perpendicular_native":320,
 "six_polygon_corner_junctions":6,"two_Q5_end_transitions":2,
 "variants_tested":len(rows),
 "variants_with_continuous_polygon_finite_wall_face_contact_and_no_protected_collision":len(passrows),
 "wall_contact_per_candidate":"Positive length on every adjacent source sanctuary wall face, not vertex-only.",
 "min_protected_vault_clearance_by_option":{
  opt:round(min(r["clearance_to_nearest_protected_vault_native"] for r in rows if r["option"]==opt),5)
  for opt in options},
 "max_footprint_area_by_option":{
  opt:round(max(r["footprint_area_native_sq"] for r in rows if r["option"]==opt),5)
  for opt in options},
 "phase_B_completion_criteria":{
  "8_source_junctions_measured":"PASS",
  "finite_wall_face_contact_at_8_junctions":"PASS",
  "retains_all_218_original_vaults":"PASS",
  "no_open_sanctuary_intrusion":"PASS",
  "no_unverified_pier_approval":"PASS",
  "select_approved_pier_footprints":"NOT ATTEMPTED; separate architectural approval required"},
 "technical":"PASS regenerated and exported from authoritative source; regression & ZIP",
 "geometric":"PASS all 24 options fully within existing masonry and non-colliding",
 "architectural":"PRELIMINARY: open sanctuary arrangement verified; physical pier sizing/masonry bond and arch/rib bearings unresolved",
 "historical":"NOT ASSESSED",
 "structural":"NOT ASSESSED; 2D line contact is not capacity or actual masonry bonding",
 "locked_objects_changed":[],
 "next_dependency":"M02 Phase C ambulatory rhythm; reserve detailed 3D/respond and structural pier design for later approvals",
 "unresolved":["F5ZL-C support schedule missing",
  "Full structural design / load bearings / pier profiles unresolved",
  "Outer paired 14-vault rhythm needs reconciliation beyond seven source T polygons"]}
(OUT/"M02_B_R03_FINAL_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
# One dark review image only: source main area and three types of wall-connected footprints.
plt.rcParams.update({"text.color":"#eaf3f7","axes.labelcolor":"#b6ced8",
 "xtick.color":"#a8c3ce","ytick.color":"#a8c3ce","axes.edgecolor":"#819ca7",
 "savefig.facecolor":"#0e1824"})
fig=plt.figure(figsize=(19,11.8),facecolor="#0e1824")
gs=fig.add_gridspec(2,2,height_ratios=[.7,1.25],width_ratios=[1.2,1],
 left=.052,right=.98,top=.865,bottom=.115,hspace=.27,wspace=.16)
whole=fig.add_subplot(gs[0,:]);detail=fig.add_subplot(gs[1,0]);end=fig.add_subplot(gs[1,1])
cols={"A_NARROW":"#b9da75","B_MODERATE":"#edbd5d","C_BROAD":"#ec806e"}
def paint(ax,g,fc,ec,lw=.5,alpha=1,z=3):
 for p in ([g] if g.geom_type=="Polygon" else [x for x in g.geoms if x.geom_type=="Polygon"]):
  ax.add_patch(MPatch(list(p.exterior.coords),fc=fc,ec=ec,lw=lw,alpha=alpha,zorder=z))
for ax in [whole,detail,end]:
 ax.set_facecolor("#192d3a")
 for poly in v.values():paint(ax,poly,"#1d3a48","#6b8fa1",.24,z=1)
 paint(ax,op,"#a15bdc","#d4aafa",.65,.6,3)
 for name in ("END_S","C1","C2","C3","C4","C5","C6","END_N"):
  for opt in ("C_BROAD","B_MODERATE","A_NARROW"):
   paint(ax,models[(name,opt)],cols[opt],cols[opt],.7,.9,
    {"C_BROAD":5,"B_MODERATE":7,"A_NARROW":9}[opt])
 for ln in face_lines:ax.plot(*ln.xy,color="#ff83dc",lw=1.6,zorder=13)
 ax.set_aspect("equal","box");ax.grid(alpha=.06)
 ax.set_xlabel("Global X • native units");ax.set_ylabel("Global Y • native units")
whole.set_xlim(-46700,29100);whole.set_ylim(-10200,10200)
detail.set_xlim(19750,24750);detail.set_ylim(-4600,4600)
end.set_xlim(19600,22200);end.set_ylim(-4650,4650)
for j,pt in enumerate(chain):
 if j in (0,7):label="END_S" if j==0 else "END_N"
 else:label=f"C{j}"
 detail.text(pt[0]+85,pt[1]+140,label,color="#ffedc8",fontsize=9.3,weight="bold",zorder=20)
for name in ("END_S","END_N"):
 pt=models[(name,"B_MODERATE")].centroid
 end.text(pt.x+120,pt.y+120,name,color="#fff0b9",fontsize=11,weight="bold",zorder=20)
whole.set_title("1 · Full baseline — open sanctuary purple, first wall unaltered",loc="left",pad=10,fontsize=11.5,weight="bold")
detail.set_title("2 · Wall-contact studies at all eight polygon joints",loc="left",pad=10,fontsize=11.3,weight="bold")
end.set_title("3 · Two Q5 entrance-side junctions",loc="left",pad=10,fontsize=11.3,weight="bold")
fig.suptitle("CATHEDRAL F5ZP | M02 PHASE B — COORDINATION COMPLETE (EXPERIMENTAL)\n"
 "24 nested wall-connected 2D reservations • six corners and two end transitions • no piers approved",
 x=.052,y=.982,ha="left",fontsize=14.7,weight="bold")
fig.text(.052,.031,"Green A (110-unit radius)  •  Gold B (180)  •  Coral C (250)   "
 "All 24 pass geometric fit and finite wall-face contact; historical and structural checks remain open.",
 fontsize=9.6,color="#c8d7df")
png=OUT/"F5ZP_M02_PHASE_B_COMPLETION_EIGHT_JUNCTIONS_WALL_CONNECTED_DARK.png"
fig.savefig(png,dpi=162,bbox_inches="tight");plt.close(fig)
with Image.open(png) as im:im.verify();print("IMAGE_VERIFIED",im.size)
assert all(hashlib.sha256(v.read_bytes()).hexdigest()==hashes[n] for n,v in base.items())
(OUT/"M02_PHASE_B_COMPLETION_HANDOFF.md").write_text("""# F5ZP M02 / Phase B — Completed 2D interface coordination (R03)

**Architectural protection:** The continuous purple nave/crossing/choir/7-sided chancel remains fully open. Its first 320 native-unit wall is at the sanctuary-to-inner ambulatory interface only. R11's 218 original vault clear polygons, R30/31 open interior, R32 seven parallel first-wall faces, R33 six corner joints and two Q5 junctions, F5ZK-C, F5ZN-A, Pass 6J and working inner/middle vault generator are never altered. Original source SHA256 recorded in JSON QA.

**Recovery:** R01 established 8 construction hulls and measured the gaps; R02 tested 3 vertex-touching triangle sizes with 2D clearance but no bonded-wall connection. R03 resolves R02's *point-contact limitation geometrically*, by creating actual positive-length boundary contact along the existing wall using the source-matched face strips and measured end transition wedges. At each of 8 measured points, 3 nested shapes (110, 180, 250 native radius) are studied. **All 24 are continuous and fully inside original reserved masonry**, with no protected vault or open central sanctuary overlap. No source geometry moved.

**Critical validation boundary:** A 2D envelope touching a wall along a line is only a *provisional support reservation*. It does NOT prove true masonry bonding, actual pier morphology, architectural approval, vault/rib thrust support, construction feasibility, historic appropriateness or structural capacity. Do not call them final piers or load-bearing validated. Their areas and clearances are given for later decisions, with no winning profile or dimensions selected.

**Completion:** M02 Phase B *2D geometric coordination and measured experimental alternatives* complete. Architectural support design/approval explicitly remains unresolved, outside Phase B's verified deliverable. Phase C can proceed with current vault rhythm and interfaces; full 3D Gothic responds and structural design must use the actual bearing data when recovered.

**Validation:** technical PASS; geometric PASS; architectural open-space intent preserved, support sections provisional; historical NOT CHECKED; structural NOT CHECKED. F5ZL-C support schedule absent.

**Outputs:** one dark review image, numerical QA, 24-row comparison CSV, 1:1 GeoJSON, generator and local ZIP. GitHub intentionally skipped on user request.

Reproduce: python3 M02_PHASE_B_R03_WALL_CONNECTED_COMPLETION.py
""")
shutil.copy2(png,Path.home()/"Downloads"/png.name)
zipf=Path.home()/"Downloads"/"F5ZP_M02_PHASE_B_COMPLETE_8_JUNCTIONS_LOCAL_EXPERIMENTAL.zip"
with zipfile.ZipFile(zipf,"w",zipfile.ZIP_DEFLATED) as z:
 z.write(Path(__file__),arcname=Path(__file__).name)
 for path in sorted(OUT.iterdir()):z.write(path,arcname=path.name)
with zipfile.ZipFile(zipf) as z:assert z.testzip() is None
print("M02_PHASE_B_GEOMETRIC_COORDINATION_COMPLETE",len(passrows),"/24",zipf)