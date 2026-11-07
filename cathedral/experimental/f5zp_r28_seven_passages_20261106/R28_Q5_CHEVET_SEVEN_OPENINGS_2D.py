#!/usr/bin/env python3
"""R28: experimental seven passage candidates through existing Q5/chevet masonry.
Read R11 and R27 actual geometry, never mutate architectural originals.
"""
from pathlib import Path
import csv,hashlib,json,zipfile,shutil
from shapely.geometry import shape,box,Polygon,mapping
from shapely.ops import unary_union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Paint,Rectangle,Patch
from matplotlib.lines import Line2D
from PIL import Image

ROOT=Path(__file__).resolve().parent
O=ROOT/"R28_Q5_CHEVET_ENTRANCES_2D_EXPERIMENTAL";O.mkdir(exist_ok=True)
src={
 "R11":ROOT/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "R13":ROOT/"R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson",
 "R27":ROOT/"R27_Q5_CHEVET_INTERFACE_2D_EXPERIMENTAL/R27_ACTUAL_RESERVED_MASONRY_CONNECTORS.geojson",
 "R27_QA":ROOT/"R27_Q5_CHEVET_INTERFACE_2D_EXPERIMENTAL/R27_NUMERICAL_QA.json",
}
hashes={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in src.items()}
j={n:json.loads(p.read_text()) for n,p in src.items()}
objects={f["properties"]["id"]:shape(f["geometry"]) for f in j["R11"]["features"]}
v={f["properties"]["id"]:shape(f["geometry"]) for f in j["R11"]["features"] if f["properties"].get("role")=="CLEAR"}
assert len(v)==218
C,H=objects["CHOIR_MASONRY_R10"],objects["CHEVET_MASONRY_R10"]
solid=unary_union([C,H]);protected=unary_union(list(v.values()))
assert solid.geom_type=="Polygon"
assert C.boundary.intersection(H.boundary).length>9600
existing={
 f["properties"]["id"]:shape(f["geometry"]) for f in j["R13"]["features"]
 if f["properties"].get("variant")=="B_BALANCED" and f["properties"].get("layer")=="EXPERIMENTAL_PASSAGE_VOID"}
assert len(existing)==7
existing_v=unary_union(list(existing.values()))
ref={
 (f["properties"].get("rank"),f["properties"].get("side")):shape(f["geometry"])
 for f in j["R27"]["features"] if f["properties"].get("rank") in ("A1","A2","A3")}
assert len(ref)==6
assert j["R27_QA"]["no_axial_opening_defined"]
# Q5->curved-chevet central threshold: plain through-wall aperture. This is
# 2200 along Y through actual 320-thick X terminal band; not a 2200 X cut.
AXIAL_WIDTH=2200
ax=box(19893,-AXIAL_WIDTH/2,20213,AXIAL_WIDTH/2)
assert ax.difference(C).area<1e-6
assert ax.intersection(protected).area==0
assert ax.intersection(existing_v).area==0
assert ax.boundary.intersection(v["Q5_MAIN"].boundary).length==AXIAL_WIDTH
assert (2933-AXIAL_WIDTH/2)==1833
# The approach from X20213 toward chevet radial inner front is a void at y=0,
# but an UNBROKEN straight 2200-wide corridor conflicts with curved masonry.
approach=box(20213,-1100,23081.91,1100)
approach_collision=approach.intersection(H)
assert approach_collision.area>0
assert approach.intersection(protected).area==0
# Side passage openings follow the exact slightly sloping chevet edge.
# Each R27 connector uses four vertices in order: Q5-low, Q5-high,
# chevet-high, chevet-low. Trim each of the two opposite faces by the same
# fractions, retaining shoulders, without modifying R27 original.
def mix(p,q,t):return (p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t)
TRIM=0.15
cutouts={("CENTRAL","AXIAL"):ax}
records=[];features=[]
features.append({"type":"Feature","properties":{
 "id":"R28_TRIAL_AXIAL_2200","rank":"CENTRAL","side":"AXIAL",
 "role":"PROPOSED_MASONRY_CUT_NOT_APPROVED","clear_y":AXIAL_WIDTH,
 "wall_depth_x":320},"geometry":mapping(ax)})
for rank in ("A1","A2","A3"):
 for side in "NS":
  full=ref[rank,side]
  points=list(full.exterior.coords)[:-1]
  assert len(points)==4 and points[0][0]==points[1][0]==20053
  qlo,qhi,chi,clo=points
  low1=mix(qlo,qhi,TRIM);high1=mix(qlo,qhi,1-TRIM)
  low2=mix(clo,chi,TRIM);high2=mix(clo,chi,1-TRIM)
  opening=Polygon([low1,high1,high2,low2])
  assert opening.is_valid and opening.difference(full).area<1e-5
  qface=v[f"Q5_{side}_{rank}_2"]
  cvname={"A1":"I","A2":"M","A3":"T"}[rank]+"_A"+("1" if side=="N" else "7")+"_R12C"
  chevet=v[cvname]
  qtouch=opening.boundary.intersection(qface.boundary).length
  # Interpolated points lie on the actual sloped edge geometrically, but
  # GEOS exact line intersection loses coincident fragments through float
  # rounding. Use tolerance for membership; report analytic sub-edge length.
  ctouch=opening.boundary.intersection(chevet.boundary.buffer(0.0001)).length-0.0002
  qfull=full.boundary.intersection(qface.boundary).length
  cfull=full.boundary.intersection(chevet.boundary).length
  assert abs(qtouch-qfull*.7)<1e-5 and abs(ctouch-cfull*.7)<2e-4
  assert opening.difference(solid).area<1e-5
  assert opening.intersection(protected).area<1e-5
  assert opening.intersection(existing_v).area<1e-5
  assert opening.intersection(ax).area==0
  # 15% bearing margin reserved at each end of real Q5+chevet faces.
  remainder=full.difference(opening)
  assert remainder.area>0
  leftover_min_Q5=qfull*TRIM
  assert leftover_min_Q5>=170
  row={"opening_id":f"{rank}_{side}","Q5_vault":f"Q5_{side}_{rank}_2",
   "chevet_vault":cvname,
   "full_original_Q5_face":round(qfull,6),
   "proposed_clear_Q5_face":round(qtouch,6),
   "full_chevet_sloping_face":round(cfull,6),
   "proposed_clear_chevet_face":round(ctouch,6),
   "fraction_open":0.7,"retained_end_margin_fraction_each":0.15,
   "Q5_retained_face_margin_each":round(leftover_min_Q5,6),
   "original_corridor_min_x_depth":round(min(points[3][0],points[2][0])-20053,6),
   "opening_area":round(opening.area,6),
   "passage_reaches_both_original_vault_faces":True,
   "original_masonry_cleared_in_saved_model":False,
   "status":"EXPERIMENTAL_NO_ARCHITECTURAL_APPROVAL"}
  records.append(row)
  cutouts[rank,side]=opening
  features.append({"type":"Feature","properties":{
    "id":f"R28_TRIAL_{rank}_{side}","role":"PROPOSED_MASONRY_CUT_NOT_APPROVED",
    "opening_id":row["opening_id"],"fraction_open":0.7,
    "q5_clear_contact":qtouch,"chevet_clear_contact":ctouch},
    "geometry":mapping(opening)})
assert len(records)==6 and len(features)==7
# Validate seven new cuts don't overlap each other; remaining old masonry still
# stays connected. This is GEOMETRIC continuity, not load-bearing adequacy.
proposals=list(cutouts.values());cut_union=unary_union(proposals)
assert abs(cut_union.area-sum(a.area for a in proposals))<1e-5
assert cut_union.difference(solid).area<1e-5
assert cut_union.intersection(protected).area<1e-5
assert cut_union.intersection(existing_v).area<1e-5
remainder=solid.difference(cut_union)
assert remainder.is_valid and remainder.area>0
# R11 main walls may stay as a MultiPolygon due to cutouts, but the
# uncut east-west masonry joint must retain some positive length.
orig_seam=C.boundary.intersection(H.boundary)
seam_left=orig_seam.difference(cut_union)
assert seam_left.length>0
# North/south symmetry and widths, preserve R11 original 7 chevet bay identities.
for rank in ("A1","A2","A3"):
 north=next(x for x in records if x["opening_id"]==rank+"_N")
 south=next(x for x in records if x["opening_id"]==rank+"_S")
 assert north["proposed_clear_Q5_face"]==south["proposed_clear_Q5_face"]
 assert north["proposed_clear_chevet_face"]==south["proposed_clear_chevet_face"]
assert sum(1 for name in v if name.startswith("I_A") and name.endswith("_R12C"))==7
assert sum(1 for name in v if name.startswith("M_A") and name.endswith("_R12C"))==7
assert sum(1 for name in v if name.startswith("T_A") and name.endswith("_R12C"))==7
with (O/"R28_SIX_SIDE_OPENINGS_MEASUREMENTS.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
(O/"R28_SEVEN_PROPOSED_OPENINGS_VISUAL_GEOJSON.geojson").write_text(json.dumps({
 "type":"FeatureCollection","properties":{
  "status":"EXPERIMENTAL PLAN CUTS; SAVED MASONRY NOT MODIFIED",
  "central_trial_width_y":2200,"trial_side_open_fraction":.7,
  "source_sha256":hashes},"features":features},
  separators=(",",":"))+"\n")
qa={"milestone":"R28 — Q5 axial + six curved chevet side openings, 2D experimental",
 "status":"TECHNICAL AND 2D GEOMETRIC PASS; ARCHITECTURAL APPROVAL PENDING",
 "source_sha256":hashes,"source_geometry_unchanged":True,
 "source_R11_vaults_unchanged":218,"source_seven_bay_I_M_T_ring_identities_unchanged":True,
 "original_R13_Q1_Q2_passages_unchanged":7,
 "trial_openings_count":7,"trial_central_clear_width_Y":AXIAL_WIDTH,
 "central_320_X_wall_depth_original_and_unchanged":320,
 "axial_terminal_masonry_remaining_Y_per_end":1833,
 "six_side_trim_fraction_each":TRIM,
 "six_side_open_fraction":1-2*TRIM,
 "passage_candidates_nonoverlapping":True,
 "all_candidate_cuts_inside_original_masonry":True,
 "all_candidate_cuts_avoid_protected_vault_spaces":True,
 "each_side_candidate_touches_two_actual_vault_clear_boundaries":True,
 "all_6_Q5_face_retained_end_margins_at_least_170":True,
 "choir_chevet_source_seam_total_length":orig_seam.length,
 "choir_chevet_seam_remaining_after_trial_cuts":round(seam_left.length,6),
 "hypothetical_remainder_valid_geometry":remainder.is_valid,
 "axial_approach_width_2200_chevet_masonry_conflict_area":round(approach_collision.area,6),
 "axial_corridor_continuity_validated":False,
 "axial_opening_would_breach_the_solid_Q5_terminal_wall":True,
 "technical_validation":"PASS: output file QA and preserved input hashes",
 "geometric_validation":"PASS: trial cuts fit original R11 wall reservation, do not enter vault clear spaces, have measured Q5/chevet face contact",
 "architectural_validation":"PROVISIONAL: actual 2D openings not yet approved; central approach still conflicts with inner chevet ring wall",
 "historical_validation":"NOT VERIFIED: no plate-derived jamb profiles, proportion claims or tracery",
 "structural_validation":"NOT VERIFIED: load paths, pier stability and lintel/arch capacity unavailable",
 "outstanding":["Opening clearance through terminal Q5 band is only the first axial threshold; the route farther east needs curved chevet masonry/doorway coordination.",
 "No source masonry permanently cut: proposals are separate experimental overlay polygons.",
 "Side-wall margins 15% at each end are proportional studies, not minimum structural supports.",
 "Existing R11 T-ring has 7 polygons, not proof of independent outer 14-vault paired design.",
 "F5ZL-C support schedule missing."]}
(O/"R28_NUMERICAL_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
# One sheet, dark mode: location, entire junction, focal axial + side interfaces.
plt.rcParams.update({"text.color":"#eaf3f8","axes.labelcolor":"#bad0df",
 "xtick.color":"#acc5d6","ytick.color":"#acc5d6",
 "axes.edgecolor":"#7895a6","font.size":10,"savefig.facecolor":"#0c1623"})
def paint(ax,g,color,edge="#6b93a7",lw=.32,z=1,alpha=1):
 ps=[g] if g.geom_type=="Polygon" else [p for p in getattr(g,"geoms",[]) if p.geom_type=="Polygon"]
 for p in ps:
  ax.add_patch(Paint(list(p.exterior.coords),facecolor=color,edgecolor=edge,
    linewidth=lw,zorder=z,alpha=alpha))
  if color!="none":
   for hole in p.interiors:ax.add_patch(Paint(list(hole.coords),facecolor="#142635",edgecolor="none",zorder=z+.02))
def base(ax):
 ax.set_facecolor("#142635")
 for g in (C,H):paint(ax,g,"#4a5d6e",lw=.18,z=1)
 for g in v.values():paint(ax,g,"#193a49",edge="#709aaf",lw=.32,z=2)
 for g in existing.values():paint(ax,g,"#267d9c",edge="#8bd9f3",lw=.65,z=3)
 for (rank,side),g in ref.items():paint(ax,g,"none",edge="#c6ad7a",lw=.95,z=7)
 for (rank,side),g in cutouts.items():
  color="#ed92c8" if rank=="CENTRAL" else "#4bd3b3"
  paint(ax,g,color,edge="#ffe3ff" if rank=="CENTRAL" else "#c7fff1",lw=.75,z=9,alpha=.97)
 ax.set_aspect("equal","box");ax.grid(alpha=.075)
 ax.set_xlabel("Global X • native units");ax.set_ylabel("Global Y • native units")
fig=plt.figure(figsize=(19,12.5),facecolor="#0c1623")
gs=fig.add_gridspec(2,2,height_ratios=[.86,1.25],width_ratios=[1.2,1],
 left=.055,right=.985,top=.87,bottom=.13,hspace=.25,wspace=.16)
full=fig.add_subplot(gs[0,:]);junction=fig.add_subplot(gs[1,0]);focus=fig.add_subplot(gs[1,1])
for aa in (full,junction,focus):base(aa)
bounds=unary_union(list(v.values())).bounds
full.set_xlim(bounds[0]-1900,bounds[2]+1900)
full.set_ylim(bounds[1]-1500,bounds[3]+1500)
full.add_patch(Rectangle((18500,-7800),5700,15600,fill=False,edgecolor="#ff94d6",linewidth=2.3,zorder=20))
full.annotate("Q5 → chevet: seven trial openings",xy=(23900,8000),xytext=(14000,10600),
 color="#ffb6e0",fontsize=11,weight="bold",arrowprops={"arrowstyle":"->","color":"#ffb6e0"})
junction.set_xlim(18200,23900);junction.set_ylim(-8100,8100)
focus.set_xlim(19350,23600);focus.set_ylim(-3250,3250)
# Conflicting ring masonry if someone assumes a straight 2200-wide axial corridor:
paint(focus,approach_collision,"none",edge="#fd9a64",lw=1.75,z=11)
focus.annotate("Farther axial route encounters\\nexisting curved masonry",xy=(22800,1040),xytext=(20800,2460),
 fontsize=9,color="#ffbc91",ha="left",arrowprops={"arrowstyle":"->","color":"#ffbc91"},zorder=15)
focus.text(20053,0,"2200\\nCLEAR",color="#1e1b23",ha="center",va="center",fontsize=10,weight="bold",rotation=90,zorder=15)
junction.axvline(20213,color="#f6e2a1",ls=":",lw=1,zorder=12)
full.set_title("1 · Complete cathedral, Q5–chevet marked",loc="left",pad=11,fontsize=12,weight="bold")
junction.set_title("2 · All seven trial cuts, with original masonry underneath",loc="left",pad=11,fontsize=11.2,weight="bold")
focus.set_title("3 · 2200 central opening, further east approach unresolved",loc="left",pad=11,fontsize=10.9,weight="bold")
fig.suptitle("F5ZP R28 | SEVEN Q5–CHEVET PASSAGES — 2D ARCHITECTURAL TRIAL\n"
 "Central 2200 through 320 wall · six sloping-face aisle cuts · no original masonry changed",
 x=.055,y=.979,ha="left",fontsize=15.6,weight="bold")
fig.legend(handles=[
 Patch(facecolor="#193a49",edgecolor="#709aaf",label="Protected vault"),
 Patch(facecolor="#4a5d6e",label="Original solid masonry"),
 Patch(facecolor="#ed92c8",label="Experimental axial opening"),
 Patch(facecolor="#4bd3b3",label="Six experimental side openings"),
 Line2D([0],[0],color="#fd9a64",lw=2,label="Unresolved axial route into curved masonry")],
 loc="lower center",ncol=3,frameon=False,bbox_to_anchor=(.5,.052),labelcolor="#eaf3f8",fontsize=9.3)
fig.text(.055,.013,"Technical and geometric clearance pass only. Proposed openings are independent 2D overlays, not pier/structural approval.",
 color="#b7cad7",fontsize=9.5)
png=O/"F5ZP_R28_FULL_FLOOR_PLAN_SEVEN_TRIAL_PASSAGES_DARK.png"
fig.savefig(png,dpi=170,bbox_inches="tight");plt.close(fig)
with Image.open(png) as img:img.verify();print("R28 PNG verified",img.size)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[k] for k,p in src.items())
(O/"README_HANDOFF.md").write_text("""# R28 — Q5 central axial threshold and six chevet side passages (experimental 2D)

**Source authority:** original R11 polygons and R27 original face-to-face masonry connector reference. All sources verified byte-identical after R28. R24 Q1–Q2 approved visual treatment unaffected. Seven I + seven M + seven T ring polygon IDs retained unchanged; this is not verification of paired outer 14-vault rhythm.

**Axial trial:** Cut through the already-existing Q5 terminal 320-X masonry band X19893..20213, Y-1100..+1100, a centered clear width 2200 (Y). Reserve 1833 native units of original wall at each end (north and south). This is a trial, not an approved arch or bearing design. A straight 2200-wide corridor from X20213 to the inner chevet masonry at X23081.91 has a measurable **existing chevet masonry collision**. Do not claim continuous access to the axial chapel or a finished axial route.

**Side passages:** At Q5 A1→I_A1/A7, A2→M_A1/A7, A3→T_A1/A7, use each exact R27 skew quadrilateral as a reference. A candidate cut connects 70% of each Q5/chevet vault face, preserving 15% of each original face at both ends. This creates six proportioned non-overlapping trial cuts, all fully inside existing masonry and meeting actual original clear-vault boundary edges. On the left faces, 806.4/840/960.4 native units of clear length; on right chevet faces slightly longer due to sloping edges. These dimensions are experimental, not guaranteed safe support margins.

**Checks:** Seven candidate cuts do not overlap one another, original protected vaults, or existing R13 Q1-Q2 passages. Cut union is inside original masonry. Choir–chevet original shared masonry seam retains positive line contact. Hypothetical post-cut masonry remains a valid geometry; no structural capacity proven. See R28_NUMERICAL_QA.json.

**Unresolved:** More eastern axial passage, physical pier/masonry support scheme, F5ZL-C, paired 14-outer-vault schedule. No saved R11 or generator changed. Historic and structural verification not performed.

Reproduce: python3 R28_Q5_CHEVET_SEVEN_OPENINGS_2D.py
""")
shutil.copy2(png,Path.home()/"Downloads"/png.name)
zipout=Path.home()/"Downloads"/"F5ZP_R28_Q5_CHEVET_SEVEN_PASSAGES_2D_EXPERIMENTAL.zip"
with zipfile.ZipFile(zipout,"w",compression=zipfile.ZIP_DEFLATED) as z:
 z.write(Path(__file__),arcname=Path(__file__).name)
 for path in sorted(O.iterdir()):z.write(path,arcname=path.name)
with zipfile.ZipFile(zipout) as z:assert z.testzip() is None
print("R28 QA_PASS 7 openings, six side contacts. Axial farther-east collision area:",round(approach_collision.area,2),"zip",zipout)