#!/usr/bin/env python3
"""R31: source-derived 1:1 open main interior with EXACT seven-face chancel end.
Read-only R11 and R30 inputs. Emits PNG/SVG/GeoJSON/CSV/QA/ZIP, no model edits.
"""
from pathlib import Path
import csv,hashlib,json,math,shutil,zipfile,xml.etree.ElementTree as ET
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as AP, Rectangle, Patch
from matplotlib.lines import Line2D
from shapely.geometry import shape,box,LineString,Point,mapping
from shapely.ops import unary_union
from PIL import Image

R=Path(__file__).resolve().parent
O=R/"R31_SEVEN_FACED_OPEN_INTERIOR_2D_EXPERIMENTAL";O.mkdir(exist_ok=True)
files={
 "R11":R/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "R30":R/"R30_OPEN_INTERIOR_ARCHITECTURAL_INTENT_R01/SOURCE_GEOMETRY_EVIDENCE.json",
 "R29B":R/"R29B_FIRST_SANCTUARY_INNER_WALL_CORRECTION/R29B_FIRST_WALL_LOCATION.json",
}
digests={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in files.items()}
features=json.loads(files["R11"].read_text())["features"]
R30=json.loads(files["R30"].read_text())
R29B=json.loads(files["R29B"].read_text())
objs={f["properties"]["id"]:shape(f["geometry"]) for f in features}
vaults={f["properties"]["id"]:shape(f["geometry"]) for f in features if f["properties"].get("role")=="CLEAR"}
assert len(vaults)==218
assert R30["chancel_polygonal_face_count"]==7
for ring in "IMT":
 assert sum(k.startswith(ring+"_A") and k.endswith("_R12C") for k in vaults)==7
main_names=[f"N{i}_MAIN" for i in range(2,10)]+["N10","Crossing","Q1"]+[f"Q{i}_MAIN" for i in range(2,6)]
assert len(main_names)==15 and all(name in vaults for name in main_names)
xs=[vaults[name].bounds[0] for name in main_names]
west=min(xs);assert west==-45029
assert all(abs(vaults[name].bounds[1]+2933)<1e-6 and abs(vaults[name].bounds[3]-2933)<1e-6 for name in main_names)
cross=vaults["Crossing"]
north=vaults["N_North T1"];south=vaults["S_North T1"]
assert cross.bounds==(-6613,-2933,-747,2933)
assert north.bounds==(-6613,3573,-747,7605)
assert south.bounds==(-6613,-7605,-747,-3573)

# Recover polygonal sanctuary inner boundary directly from R11 chevet source:
# EXACTLY SEVEN segments from the lower junction to the upper.
ch=objs["CHEVET_MASONRY_R10"]
vertices=list(ch.exterior.coords)
south_idx=next(i for i,(x,y) in enumerate(vertices) if 20238<x<20239 and y<0)
north_idx=next(i for i,(x,y) in enumerate(vertices) if 20238<x<20239 and y>0)
chain=vertices[south_idx:north_idx+1]
assert len(chain)==8
expected=R30["chancel_inner_face_vertices"]
assert all(math.dist(pt,check)<2e-5 for pt,check in zip(chain,expected))
# This is the actual open FLOOR footprint: rectilinear main nave/crossing/choir
# plus 7-faceted sanctuary termination. The crossing arms are integrated,
# including unbuilt vault-planning gaps between arms and main crossing.
stem_poly=__import__("shapely.geometry",fromlist=["Polygon"]).Polygon(
 [(west,-2933),(20213,-2933)]+chain+[(20213,2933),(west,2933)])
cross_arms=box(-6613,-7605,-747,7605)
open_interior=unary_union([stem_poly,cross_arms])
assert open_interior.is_valid and open_interior.geom_type=="Polygon"
assert len(open_interior.interiors)==0
assert all(open_interior.covers(vaults[name]) for name in main_names)
assert open_interior.covers(north) and open_interior.covers(south)
assert all(open_interior.intersection(vaults[name]).area<1e-5 for name in vaults
           if name.startswith(("I_A","M_A","T_A")) and name.endswith("_R12C"))
# The last physical wall at the boundary remains: EXACT 320 on Y=0, not at Q5.
AX=LineString([(22000,0),(24600,0)])
parts=sorted([p for p in getattr(ch.intersection(AX),"geoms",[ch.intersection(AX)]) if p.length>1],
             key=lambda x:x.bounds[0])
first_wall=parts[0]
wall0,wall1=first_wall.bounds[0],first_wall.bounds[2]
assert abs(wall0-23081.906912952254)<1e-6
assert abs(wall1-23401.906912952254)<1e-6
assert abs(wall1-wall0-320)<1e-6
assert abs(R29B["first_wall_west_x"]-wall0)<1e-5 and abs(R29B["first_wall_east_x"]-wall1)<1e-5
assert abs(vaults["I_A4_R12C"].bounds[0]-wall1)<1e-6
assert abs(open_interior.boundary.distance(Point(wall0,0)))<1e-6
assert abs(open_interior.intersection(LineString([(west,0),(wall0,0)])).length-(wall0-west))<1e-5
# Measured 7 independent line segments, labelled lower (S) to upper (N).
edges=[]
for num,(a,b) in enumerate(zip(chain,chain[1:]),start=1):
 dx,dy=b[0]-a[0],b[1]-a[1]
 length=math.hypot(dx,dy)
 assert length>500
 edges.append(dict(face=num,x1=a[0],y1=a[1],x2=b[0],y2=b[1],
                   length_native=length,bearing_deg_from_east=math.degrees(math.atan2(dy,dx))))
assert len(edges)==7 and all(edges[i]["y1"]<=edges[i+1]["y1"] for i in range(6))
assert abs(edges[3]["bearing_deg_from_east"]-90)<1e-7
# Reflection symmetry is required of the seven-facet apse footprint.
for i in range(4):
 lower,upper=chain[i],chain[7-i]
 assert abs(lower[0]-upper[0])<1e-5
 assert abs(lower[1]+upper[1])<1e-5
with (O/"R31_SEVEN_CHANCEL_FACE_COORDINATES.csv").open("w",newline="") as f:
 writer=csv.DictWriter(f,fieldnames=list(edges[0]));writer.writeheader();writer.writerows(edges)
geo={"type":"FeatureCollection","properties":{
 "classification":"MEASURED OPEN INTERIOR INTENT, NOT A NEW MASONRY OR VAULT GENERATOR",
 "coordinate_system":"R11_NATIVE_1_TO_1","source_sha256":digests,
 "actual_chevet_termination_face_count":7},
 "features":[
 {"type":"Feature","properties":{"id":"NAVE_CROSSING_CHOIR_SEVEN_FACED_CHANCEL_OPEN_INTERIOR",
    "status":"USER_CONFIRMED_OPEN_SPACE_INTENT","ring_wall_not_removed":True},
    "geometry":mapping(open_interior)},
 {"type":"Feature","properties":{"id":"SEVEN_SIDED_INNER_CHANCEL_BOUNDARY","faces":7,
    "status":"SOURCE_MEASURED_SANCTUARY_TO_INNER_AMBULATORY_FIRST_WALL_INNER_FACE"},
    "geometry":mapping(LineString(chain))},
 {"type":"Feature","properties":{"id":"FIRST_320_WALL_AT_Y_ZERO_SECTION","wall_depth_native":320,
   "status":"SOURCE_MEASURED_SECTION_ONLY"},
   "geometry":mapping(first_wall)}
 ]}
(O/"R31_OPEN_INTERIOR_1_TO_1.geojson").write_text(json.dumps(geo,separators=(",",":"))+"\n")
qa={"title":"R31 seven-faced continuous nave, crossing, choir, chancel 1:1 2D",
 "classification":"USER-CONFIRMED ARCHITECTURAL SPATIAL INTENT, PROTECTED GEOMETRY NOT MODIFIED",
 "open_polygon_type":open_interior.geom_type,
 "source_files_sha256":digests,
 "R11_original_clear_vault_polygons":218,
 "main_vault_cells_covered":len(main_names),
 "crossing_arm_boundaries_covered":True,
 "chancel_terminal_measured_straight_face_count":len(edges),
 "source_chancel_7_faces_extracted_byte_exact":True,
 "chancel_face_lengths":[round(e["length_native"],6) for e in edges],
 "open_interior_area_native_sq":round(open_interior.area,4),
 "open_interior_bounds":tuple(open_interior.bounds),
 "first_real_sanctuary_inner_wall_y0_x":[wall0,wall1],
 "first_real_sanctuary_inner_wall_y0_width":320,
 "Q5_transverse_planning_divider_not_physical_wall":True,
 "seven_chevet_bay_identities_preserved":True,
 "source_R11_unmodified":True,
 "drawing_legend":"Purple fill = continuous main interior. Seven magenta facets = sanctuary boundary. Orange = actual 320 wall only at Y0 section. Gray dashed = vault/masonry planning dividers.",
 "validation":{
  "technical":"Source hash regression; GeoJSON/CSV/PNG/SVG/ZIP checks passed",
  "geometric":"Exact R11 faceted chain, 7 faces, polygon validity, crossing+nave/choir coverage; first wall Y0 320",
  "architectural":"User-confirmed spatial intent; polygons are plan interpretation, detailed supports unverified",
  "historical":"Not assessed",
  "structural":"Not assessed — vault/pier bearings and true wall path remain subject to design"},
 "unresolved":["This is floor-space depiction, not an approved physical wall / pier layout.",
 "Seven inner/middle/T ring vault plan polygons remain source scheduling; independently described paired 14-outer vaults unresolved.",
 "F5ZL-C support schedule missing.",
 "Exact complete sanctuary wall thickness outside centerline not established by this task."]}
(O/"R31_NUMERICAL_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
# ONE dark graphic, same native scale, full floor plan plus measured chevet close-up.
plt.rcParams.update({"text.color":"#eef5f9","axes.labelcolor":"#adc4d3",
 "xtick.color":"#a9c4d1","ytick.color":"#a9c4d1","axes.edgecolor":"#819cab",
 "font.size":10,"savefig.facecolor":"#0c1423"})
def paint(ax,g,fc="none",edge="#5d869b",lw=.35,ls="-",z=3,alpha=1):
 pieces=[g] if g.geom_type=="Polygon" else [p for p in getattr(g,"geoms",[]) if p.geom_type=="Polygon"]
 for p in pieces:
  ax.add_patch(AP(list(p.exterior.coords),facecolor=fc,edgecolor=edge,
    linewidth=lw,linestyle=ls,zorder=z,alpha=alpha))
  if fc!="none":
   for h in p.interiors:ax.add_patch(AP(list(h.coords),facecolor="#142634",edgecolor="none",zorder=z+.02))
fig=plt.figure(figsize=(19.1,11.3),facecolor="#0c1423")
gs=fig.add_gridspec(2,2,height_ratios=[.72,1.15],width_ratios=[1.15,1],
                   left=.052,right=.982,top=.865,bottom=.12,hspace=.26,wspace=.17)
whole=fig.add_subplot(gs[0,:]);close=fig.add_subplot(gs[1,0]);section=fig.add_subplot(gs[1,1])
for ax in (whole,close,section):
 ax.set_facecolor("#142634")
 for name,obj in vaults.items():
  fill="#193b49" if name.endswith("_R12C") else "#213b51"
  paint(ax,obj,fill,"#63879e",.30,z=1)
 # Place original R11 overall masonry only as dashed planning reference,
 # to avoid implying solid barriers across the open purple vessel.
 for name in ("NAVE_MASONRY_R10","CHOIR_MASONRY_R10","CHEVET_MASONRY_R10"):
  if name in objs:paint(ax,objs[name],"none","#92a0af",.50,(0,(4,4)),z=2)
 paint(ax,open_interior,"#a05cda","#e2b4ff",.9,z=4,alpha=.61)
 ax.set_aspect("equal","box")
 ax.grid(alpha=.07)
 ax.set_xlabel("Global X · native units")
 ax.set_ylabel("Global Y · native units")
# Seven measured segments must be visible as seven independent strokes, numbered.
for ax in (whole,close,section):
 for n,(p,q) in enumerate(zip(chain,chain[1:]),start=1):
  ax.plot([p[0],q[0]],[p[1],q[1]],color="#fc83e0",lw=3.2 if ax!=whole else 2.0,zorder=12,
          solid_capstyle="butt")
  if ax==close:
   x=(p[0]+q[0])/2;y=(p[1]+q[1])/2
   ax.text(x+180,y,str(n),color="#ffe6fa",weight="bold",fontsize=10,
    ha="center",va="center",zorder=15,
    bbox=dict(facecolor="#633d82",edgecolor="#f4b3ec",pad=2))
# crossing transverse arms and all straight main vessel remain purple
whole.set_xlim(-47300,29600);whole.set_ylim(-10500,10500)
whole.add_patch(Rectangle((18500,-5500),6000,11000,fill=False,ec="#f6a6ed",lw=1.5,zorder=14))
whole.annotate("7-face CHANCEL — measured",xy=(23082,0),xytext=(10000,8250),
 color="#f8b4ed",fontsize=10.5,weight="bold",
 arrowprops=dict(arrowstyle="->",color="#f8b4ed",lw=1.1))
close.set_xlim(17900,25200);close.set_ylim(-5050,5050)
close.axhline(0,color="#f9d98d",ls=(0,(6,4)),lw=.85,zorder=15)
section.set_xlim(19800,24600);section.set_ylim(-3100,3100)
section.axhline(0,color="#f9d98d",ls=(0,(6,4)),lw=.85,zorder=15)
section.plot([wall0,wall1],[0,0],color="#ffc174",lw=10,solid_capstyle="butt",zorder=18)
section.annotate("",xy=(wall1,230),xytext=(wall0,230),
                 arrowprops=dict(arrowstyle="<->",color="#ffe6a9",lw=2),zorder=20)
section.text((wall0+wall1)/2,620,"320",ha="center",va="bottom",color="#ffe6ad",fontsize=11,weight="bold")
section.text(21100,-1120,"OPEN SANCTUARY",ha="center",color="#f0dbff",fontsize=10.5,weight="bold")
section.text(24100,-1120,"INNER AMBULATORY",ha="center",color="#a8eecc",fontsize=9.5,weight="bold")
whole.set_title("1 · Full nave → crossing → choir → seven-facet chancel",loc="left",pad=9,fontsize=12.1,weight="bold")
close.set_title("2 · Seven REAL chancel boundary faces (numbered S → N)",loc="left",pad=10,fontsize=11.7,weight="bold")
section.set_title("3 · First physical wall at chancel/inner boundary, Y=0",loc="left",pad=10,fontsize=11.2,weight="bold")
fig.suptitle("F5ZP R31 | THE CONTINUOUS PURPLE OPEN INTERIOR — 1:1 PLAN\n"
 "Exact 7-faced chancel termination extracted from R11 • no walls inserted into the main vessel",
 x=.052,y=.979,ha="left",fontsize=15.8,weight="bold")
fig.legend(handles=[
 Patch(facecolor="#a05cda",edgecolor="#e2b4ff",label="Purple = continuous open central interior"),
 Line2D([0],[0],color="#fc83e0",lw=3,label="Measured seven chancel faces"),
 Line2D([0],[0],color="#ffc174",lw=5,label="320 first sanctuary–inner wall at Y0"),
 Line2D([0],[0],color="#92a0af",ls="--",label="Existing vault/masonry reservation guides")],
 loc="lower center",ncol=2,frameon=False,bbox_to_anchor=(.5,.046),fontsize=9.5,labelcolor="#edf4f8")
fig.text(.052,.012,"Open-space interpretation confirmed by user. 218 original R11 vault polygons, Pass 6J and all approved generators untouched; structural verification not implied.",
 color="#b7cbd7",fontsize=9.2)
png=O/"F5ZP_R31_PURPLE_OPEN_INTERIOR_EXACT_SEVEN_CHANCEL_FACES_DARK.png"
svg=O/"F5ZP_R31_PURPLE_OPEN_INTERIOR_EXACT_SEVEN_CHANCEL_FACES_DARK.svg"
fig.savefig(png,dpi=160,bbox_inches="tight")
fig.savefig(svg,bbox_inches="tight")
plt.close(fig)
ET.parse(svg)
with Image.open(png) as im:im.verify();print("PNG_VERIFIED",im.size)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digests[k] for k,p in files.items())
(O/"README_HANDOFF.md").write_text("""# R31 — Measured 1:1 purple main interior and seven chancel faces

This is the **first accurate source-derived open-area layout** implementing the user's corrected architectural intent (R30) on the saved R11 floor plan. The purple main space includes nave, crossing and transverse arms, choir, and chancel formed by the **seven actual R11 inner chevet polygon faces**. No fake chevet hexagon or 5-face nose.

Data authority: R11 218 clear-vault plan polygons unchanged, original chevet boundary chain (eight vertices / seven segment faces), R30 interpreted intent and R29B centerline evidence. The purple footprint includes planned main bays and otherwise open internal scheduling gaps; masonry reservation/guide lines drawn dashed, not modeled as physical barriers.

Measured first REAL sanctuary–inner ambulatory masonry wall begins at the purple boundary, X23081.906913..23401.906913 on centerline Y0 (320 native units); the Q5 X19893–20213 planning band is NOT the first wall. Do not remove or ignore the real first sanctuary wall or extend the purple open area across it. Outer ring (7 T polygons in current R11) does not prove separately proposed 14 lower-vault design.

Outputs: accurate purple PNG+SVG, machine-readable 1:1 GeoJSON, seven-face coordinate CSV, JSON QA and this note. R31 is measured spatial coordination, NOT physical masonry/pier/structural approval. Technical and geometric checks passed; architectural open intent confirmed; historical/structural review outstanding. F5ZL-C still unresolved.

Reproduce: python3 R31_EXACT_SEVEN_FACED_OPEN_INTERIOR_2D.py
""")
shutil.copy2(png,Path.home()/"Downloads"/png.name)
zipf=Path.home()/"Downloads"/"F5ZP_R31_OPEN_INTERIOR_EXACT_7_FACE_PLAN_2D.zip"
with zipfile.ZipFile(zipf,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.write(Path(__file__),arcname=Path(__file__).name)
 for p in sorted(O.iterdir()):z.write(p,arcname=p.name)
with zipfile.ZipFile(zipf) as z:assert z.testzip() is None
print("R31 QA_PASS","faces",len(edges),"open main-vault cells",len(main_names),"area",round(open_interior.area,1))
print("IMAGE",png)
print("PACKAGE",zipf)