#!/usr/bin/env python3
"""R29: Correct Q5->chevet region from assumed solid walls to an OPEN planning zone.
Sources unchanged. No gates, through-wall openings, structural claims or new vault geometry.
"""
from pathlib import Path
import csv,json,hashlib,zipfile,shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as DrawPoly,Rectangle,Patch
from matplotlib.lines import Line2D
from shapely.geometry import shape,box
from shapely.ops import unary_union
from PIL import Image
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"R29_Q5_CHEVET_OPEN_ZONE_2D_CORRECTION";OUT.mkdir(exist_ok=True)
sources={
 "R11":ROOT/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "R27":ROOT/"R27_Q5_CHEVET_INTERFACE_2D_EXPERIMENTAL/R27_ACTUAL_RESERVED_MASONRY_CONNECTORS.geojson",
 "R28":ROOT/"R28_Q5_CHEVET_ENTRANCES_2D_EXPERIMENTAL/R28_SEVEN_PROPOSED_OPENINGS_VISUAL_GEOJSON.geojson",
 "R28_QA":ROOT/"R28_Q5_CHEVET_ENTRANCES_2D_EXPERIMENTAL/R28_NUMERICAL_QA.json",
 "R24_APPROVAL":ROOT/"R25_Q2_Q5_CHOIR_RHYTHM_2D_EXPERIMENTAL/R24_APPROVAL_SCOPE_CARRIED_FORWARD.json"
}
sha={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in sources.items()}
data={name:json.loads(path.read_text()) for name,path in sources.items()}
F=data["R11"]["features"]
vault={f["properties"]["id"]:shape(f["geometry"]) for f in F if f["properties"].get("role")=="CLEAR"}
assert len(vault)==218
curved={k:geom for k,geom in vault.items() if k.startswith(("I_A","M_A","T_A")) and k.endswith("_R12C")}
assert len(curved)==21
for ring in ("I","M","T"):
 assert sum(k.startswith(ring+"_A") for k in curved)==7
q5={k:geom for k,geom in vault.items() if k.startswith("Q5_")}
assert len(q5)==13
regions={f["properties"]["id"]:shape(f["geometry"]) for f in F if f["properties"].get("id") in
         ("CHOIR_MASONRY_R10","CHEVET_MASONRY_R10")}
assert set(regions)=={"CHOIR_MASONRY_R10","CHEVET_MASONRY_R10"}
r27=[f for f in data["R27"]["features"] if f["properties"].get("rank") in ("A1","A2","A3")]
assert len(r27)==6
r28=data["R28"]["features"]
assert len(r28)==7
# Physical-wall interpretation explicitly superseded by the user's statement.
# The true outlines of vault cells and reservation rectangles remain valid
# coordinates for vault scheduling; no false passage width is promoted.
planning_distances=[]
for f in r27:
 p=f["properties"];rank=p["rank"];side=p["side"]
 planning_distances.append({
   "planning_interface":rank+"_"+side,
   "source_Q5_face":p["Q5_vault"],
   "source_curved_chevet_face":p["chevet_vault"],
   "source_min_face_distance_native_units":p["min_clear_polygon_distance"],
   "architectural_reading":"OPEN SPACE / planning gap — NOT a physical masonry thickness",
   "doorway_required":False})
assert len(planning_distances)==6
with (OUT/"R29_OPEN_VAULT_PLANNING_INTERFACES.csv").open("w",newline="") as file:
 w=csv.DictWriter(file,fieldnames=planning_distances[0].keys());w.writeheader();w.writerows(planning_distances)
correction={
 "checkpoint":"R29 OPEN Q5–CHEVET 2D INTERPRETATION",
 "reason":"Direct user correction: 'this entire area is open the dividers are just planning tools'",
 "architecture_status":"USER-CONFIRMED OPEN SPACE INTENT; no physical masonry or doorway implementation approved",
 "scope":"Q5 to curved chevet transition region, including central axial approach and the six side planning interfaces",
 "protected_sources_unchanged":True,
 "source_sha256":sha,
 "unchanged_cleared_vault_planning_polygons":218,
 "unchanged_7_each_chevet_ring_polygon_ids":{"I":7,"M":7,"T":7},
 "unchanged_Q5_planning_vault_polygon_count":13,
 "R24_Option_A_approved_visual_reference_preserved":True,
 "reclassified_components":{
    "CHOIR_MASONRY_R10_and_CHEVET_MASONRY_R10_in_Q5_chevet_scope":
       "Source layer names retained, but divider shapes are planning reservations, NOT evidence of built wall",
    "Q5_center_320_segment":"Planning separation / reserved span, NOT an existing wall requiring a cut",
    "six_R27_side_connectors":"Open planning intervals between scheduled vault faces, NOT wall-thickness passageways",
    "seven_R28_opening_candidates":"RETIRED / historical experiment, NOT architecture to implement",
    "R28_reported_2200_axial_corridor_masonry_collision":"NOT a physical architectural obstacle under user-confirmed open-space intent",
    "geometric_R11_divider_outlines":"Unmodified as drafting guides only"},
 "validation":{
 "technical":"PASS: source hashes, 2D diagram, JSON/CSV and zip integrity",
 "geometric":"PASS: source vault geometries not altered and all planning identities retained",
 "architectural":"User-confirmed open zone intent; vault adjacency and actual support positions still to be designed",
 "historical":"NOT assessed — sources are plan geometry, not verified Gothic historical placement",
 "structural":"NOT assessed — no piers/load paths assigned; openness alone does not prove structural support"},
 "remaining_work":[
  "Study continuity of open vault geometry and bay transitions at Q5 to I/M/T; schedule bearing points later",
  "Keep 7 chevet bay identities; outer paired 14-vault program remains outside saved 7 T-ring records",
  "Do not add central or side passage cuts, and do not silently infer masonry from old layer names",
  "F5ZL-C support schedule remains unresolved"]}
(OUT/"R29_CORRECTED_ARCHITECTURAL_INTERPRETATION.json").write_text(json.dumps(correction,indent=2)+"\n")
# One full cathedral and one exact-coordinate open-zone view with dashed
# planning guides. Explicitly no pink "wall cuts" from R28.
plt.rcParams.update({"text.color":"#eaf1f7","axes.labelcolor":"#b7cbd8",
 "xtick.color":"#a7bfcc","ytick.color":"#a7bfcc","axes.edgecolor":"#7b94a1",
 "font.size":10,"savefig.facecolor":"#0b1624"})
def paint(ax,g,fill="none",ec="#728fa0",lw=.4,ls="solid",alpha=1,z=2):
 ps=[g] if g.geom_type=="Polygon" else [p for p in getattr(g,"geoms",[]) if p.geom_type=="Polygon"]
 for poly in ps:
  ax.add_patch(DrawPoly(list(poly.exterior.coords),facecolor=fill,edgecolor=ec,
      linewidth=lw,linestyle=ls,alpha=alpha,zorder=z))
  if fill!="none":
   for hole in poly.interiors:ax.add_patch(DrawPoly(list(hole.coords),facecolor="#152938",edgecolor="none",zorder=z+.02))
def base(ax,detail=False):
 ax.set_facecolor("#142737")
 # All existing clear vaults = planned geometric cells, not masonry walls.
 for g in vault.values():
  paint(ax,g,fill="#173e4e" if not detail else "none",ec="#6d91a5" if not detail else "#9baeb9",
    lw=.35 if not detail else .64,ls=(0,(4,3)) if detail else "-",z=3)
 # Render named R11 masonry layers only as DESCRIPTIVE/PLANNING OUTLINES.
 for g in regions.values():
  paint(ax,g,fill="none",ec="#9ea5b1",lw=.65,ls=(0,(3,5)),alpha=.8,z=5)
 ax.set_aspect("equal","box");ax.grid(alpha=.055)
 ax.set_xlabel("Global X • native project units")
 ax.set_ylabel("Global Y • native project units")
fig=plt.figure(figsize=(18,12),facecolor="#0b1624")
gs=fig.add_gridspec(2,1,height_ratios=[.82,1.28],left=.06,right=.98,top=.875,bottom=.12,hspace=.27)
overview=fig.add_subplot(gs[0]);focus=fig.add_subplot(gs[1])
base(overview);base(focus,True)
extent=unary_union(list(vault.values())).bounds
overview.set_xlim(extent[0]-1800,extent[2]+1700)
overview.set_ylim(extent[1]-1300,extent[3]+1300)
overview.add_patch(Rectangle((18350,-7900),10100,15800,fill=False,edgecolor="#8be7db",lw=2.2,zorder=15))
overview.annotate("Q5–CHEVET: OPEN PLANNING ZONE",xy=(24800,7900),xytext=(14700,11200),
 color="#a5f5e8",fontsize=11,weight="bold",arrowprops={"arrowstyle":"->","color":"#8be7db"},zorder=17)
focus.set_xlim(17400,28400);focus.set_ylim(-8250,8250)
# Distinct color per curved bay ring; all remain only geometric vault scheduling.
for ring,col in (("I","#79d9eb"),("M","#88cda6"),("T","#d2c987")):
 for key,g in curved.items():
  if key.startswith(ring+"_"):
   paint(focus,g,fill="none",ec=col,lw=1.25,ls=(0,(6,3)),z=8)
# Show R27 connective planning widths as sparse dashed construction, never material.
for f in r27:
 g=shape(f["geometry"])
 paint(focus,g,fill="none",ec="#9aa9b8",lw=.85,ls=(0,(2,5)),z=9)
# Centreline line is measured planning axis only, with no doorway.
focus.axhline(0,color="#f6d68c",lw=1.25,ls=(0,(7,4)),zorder=10)
focus.text(20100,400,"OPEN AXIAL CONTINUITY",fontsize=12,weight="bold",color="#e9f8ff",zorder=15)
focus.text(21000,-1200,"No physical divider / no doorway cut",fontsize=10,color="#a8dce9",zorder=15)
focus.annotate("",xy=(24250,0),xytext=(19500,0),
  arrowprops={"arrowstyle":"<->","color":"#7ce4dc","lw":1.6},zorder=15)
focus.text(22500,7800,"7 I + 7 M + 7 T bay guides retained",fontsize=10.5,color="#bcece4",
 ha="center",bbox={"facecolor":"#162f3e","edgecolor":"#6cafa5","pad":4},zorder=20)
overview.set_title("Full cathedral | existing R11 geometric plan preserved",loc="left",pad=10,fontsize=12.4,weight="bold")
focus.set_title("Q5 to chevet | OPEN spatial intent; dashed lines are planning guides, not walls",
 loc="left",pad=10,fontsize=12.1,weight="bold")
fig.suptitle("F5ZP R29 | OPEN Q5–CHEVET — CORRECTED 2D ARCHITECTURAL READING\n"
 "Supersedes R27–R28 doorway interpretation • no vault or generator geometry modified",
 x=.06,y=.982,ha="left",fontsize=15.9,weight="bold")
fig.legend(handles=[
 Line2D([0],[0],color="#9ea5b1",ls="--",lw=1,label="Old reservation outline: guide only"),
 Line2D([0],[0],color="#79d9eb",ls="--",lw=1.4,label="Inner I bays"),
 Line2D([0],[0],color="#88cda6",ls="--",lw=1.4,label="Middle M bays"),
 Line2D([0],[0],color="#d2c987",ls="--",lw=1.4,label="Outer T bays"),
 Line2D([0],[0],color="#f6d68c",ls="--",lw=1.5,label="Axial organizing line, open")],
 loc="lower center",ncol=3,frameon=False,bbox_to_anchor=(.5,.046),
 labelcolor="#eaf1f7",fontsize=9.3)
fig.text(.06,.013,"Open intent confirmed by user. Support geometry, actual vault connections and outer paired bay program remain separate unresolved work.",color="#b2cbd9",fontsize=9.4)
png=OUT/"F5ZP_R29_OPEN_Q5_CHEVET_FULL_PLAN_DARK.png"
fig.savefig(png,dpi=170,bbox_inches="tight");plt.close(fig)
with Image.open(png) as im:im.verify();print("IMAGE_VERIFIED",im.size)
assert all(hashlib.sha256(path.read_bytes()).hexdigest()==sha[k] for k,path in sources.items())
(OUT/"README_HANDOFF.md").write_text("""# R29 Q5-to-chevet OPEN zone correction (2D)

**User-authoritative interpretation:** 'this entire area is open the dividers are just planning tools'. This supersedes the physical-wall premise of R27/R28 **within the Q5-to-chevet region**. Do not propose seven piercings/doorways through R11 reservation lines. R27's 320 central 'wall' and the R28 2200 trial doorway are not actual design requirements. The previously reported masonry collision does not represent a physical obstruction.

**Preserve the geometry:** R11's 218 clear-vault planning polygons, Q5 labels and seven inner + seven middle + seven T outer chevet bay records remain byte-identical. Those coordinates still assist spacing and bay interfaces; the R11 role/name 'masonry' is not evidence of a constructed divider here. Keep R24 Option A's user approval within its original Q1–Q2 2D visual scope only. Preserve R27/R28 experiment packages as historical, superseded architectural interpretations.

**Deliverables:** Corrected dark-mode full-floor-plan and detailed open Q5/chevet view; explicit interpretation status JSON; six R27 planning-gap measurements reclassified in CSV; reproducible 2D script and tested ZIP.

**Next work:** Validate the open-zone vault adjacency/connectivity and reconcile Q5 → 7+7 curved rings; only afterward plan real pier/bearing positions, requiring separate architectural decisions. Missing outer paired fourteen-vault rhythm and missing F5ZL-C support schedule remain unresolved.

**Validation:** Technical source hashes & packaging PASS, geometric source continuity retained PASS; architectural OPEN INTENT confirmed by user, while exact vault web/arches and real bearings NOT validated. Historical and structural NOT assessed.

Reproduce: python3 R29_OPEN_Q5_CHEVET_PLAN_CORRECTION_2D.py
""")
shutil.copy2(png,Path.home()/"Downloads"/png.name)
zipPath=Path.home()/"Downloads"/"F5ZP_R29_Q5_CHEVET_OPEN_ZONE_CORRECTED_2D.zip"
with zipfile.ZipFile(zipPath,"w",zipfile.ZIP_DEFLATED) as z:
 z.write(Path(__file__),arcname=Path(__file__).name)
 for p in sorted(OUT.iterdir()):z.write(p,arcname=p.name)
with zipfile.ZipFile(zipPath) as z:assert z.testzip() is None
print("R29_QA_PASS",zipPath)