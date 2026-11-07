#!/usr/bin/env python3
"""R15 experimental Q1-Q2 main-axis coordination study, in 2D only.
Source baselines remain immutable. No pointed-arch/elevation, pier load or moulding design.
"""
from pathlib import Path
import json,csv,hashlib,zipfile,shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as P,Patch
from matplotlib.lines import Line2D
from shapely.geometry import shape,box,mapping
from shapely.ops import unary_union
from PIL import Image
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"R15_Q1_Q2_MAIN_AXIS_2D_EXPERIMENTAL";OUT.mkdir(exist_ok=True)
paths={
 "R12C":ROOT/"R12C_PLAN_NATIVE.geojson",
 "R11":ROOT/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "R13":ROOT/"R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson",
 "R14_S2":ROOT/"R14_Q1_Q2_BEARING_FOOTPRINTS_STEP2_EXPERIMENTAL/R14_Q1_Q2_CANDIDATE_BEARINGS_R02_EXPERIMENTAL.geojson"
}
digest={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in paths.items()}
a=json.loads(paths["R12C"].read_text())["features"]
r11=json.loads(paths["R11"].read_text())["features"]
r13=json.loads(paths["R13"].read_text())["features"]
r14=json.loads(paths["R14_S2"].read_text())["features"]
old={f["properties"]["id"]:shape(f["geometry"]) for f in a}
clear={f["properties"]["id"]:shape(f["geometry"]) for f in r11 if f["properties"].get("role")=="CLEAR"}
masonry=next(shape(f["geometry"]) for f in r11 if f["properties"].get("id")=="CHOIR_MASONRY_R10")
voids={f["properties"]["id"]:shape(f["geometry"]) for f in r13 if f["properties"].get("variant")=="B_BALANCED" and f["properties"].get("layer")=="EXPERIMENTAL_PASSAGE_VOID"}
vu=unary_union(list(voids.values()));cu=unary_union(list(clear.values()));remaining=masonry.difference(vu)
assert len(voids)==7
xmain=(clear["Q1"].bounds[2]+clear["Q2_MAIN"].bounds[0])/2
xaisle=(clear["E_N_J1 R1C3"].bounds[2]+clear["Q2_N_A1_1"].bounds[0])/2
assert (xmain,xaisle)==(4505,4480)
span=(clear["Q1"].bounds[2],clear["Q2_MAIN"].bounds[0])
assert span==(3925,5085)
# Construction zones only. Original 800-wide major support x3925..4725;
# centered 800-wide alternative x4105..4905; full gap x3925..5085.
scenarios={
 "S0_ORIGINAL_OFFSET":{"xmin":3925,"xmax":4725,"status":"RECOVERED_REFERENCE_UNCHANGED"},
 "S1_CENTERED_800":{"xmin":4105,"xmax":4905,"status":"EXPERIMENTAL_CENTERED_800_ONLY"},
 "S2_FULL_WIDTH_1160":{"xmin":3925,"xmax":5085,"status":"EXPERIMENTAL_CONTINUITY_ACROSS_GAP_ONLY"}
}
# Each north/south major wall zone is 320 native units wide in Y.
oldmajor=[old["Q1_Q2_major_1"],old["Q1_Q2_major_-1"]]
assert all(abs(g.area-256000)<.001 for g in oldmajor)
records=[];features=[]
for key,item in scenarios.items():
    axis=(item["xmin"]+item["xmax"])/2
    for side,sgn in [("N",1),("S",-1)]:
        y0,y1=(2933,3253) if sgn==1 else (-3253,-2933)
        g=box(item["xmin"],y0,item["xmax"],y1)
        source=old["Q1_Q2_major_1" if sgn==1 else "Q1_Q2_major_-1"]
        actual_x=source.bounds[0]
        q1=clear["Q1"];q2=clear["Q2_MAIN"]
        # A point/corner meeting is not a robust linear bearing face. Measure
        # actual boundary intersection LENGTH and point-to-polygon distances.
        west_face=g.boundary.intersection(q1.boundary).length
        east_face=g.boundary.intersection(q2.boundary).length
        rec={"scenario":key,"side":side,"x_min":g.bounds[0],"x_max":g.bounds[2],
             "y_min":y0,"y_max":y1,"mid_axis_x":axis,
             "offset_from_main_axis":axis-xmain,"offset_from_aisle_axis":axis-xaisle,
             "width_x":g.bounds[2]-g.bounds[0],
             "area":g.area,
             "area_outside_R11_retained_masonry":g.difference(remaining).area,
             "area_intersect_B_openings":g.intersection(vu).area,
             "area_intersect_R11_clear_vaults":g.intersection(cu).area,
             "overlap_original_major_footprint":g.intersection(source).area,
             "lost_original_major_footprint":source.difference(g).area,
             "additional_reserved_area":g.difference(source).area,
             "Q1_main_clear_boundary_contact_length":west_face,
             "Q2_main_clear_boundary_contact_length":east_face,
             "status":item["status"]}
        assert rec["area_outside_R11_retained_masonry"]<.001
        assert rec["area_intersect_B_openings"]<.001 and rec["area_intersect_R11_clear_vaults"]<.001
        records.append(rec)
        features.append({"type":"Feature","properties":rec,"geometry":mapping(g)})
assert all(rec["Q1_main_clear_boundary_contact_length"]==0 and rec["Q2_main_clear_boundary_contact_length"]==0 for rec in records)
assert scenarios["S1_CENTERED_800"]["xmin"]+800==4905
assert all(rec["offset_from_main_axis"]==0 for rec in records if rec["scenario"]!="S0_ORIGINAL_OFFSET")
assert all(rec["offset_from_main_axis"]==-180 for rec in records if rec["scenario"]=="S0_ORIGINAL_OFFSET")
# Keep the 235-unit emphasis independent of actual support width, as agreed.
core_strip=box(4505-117.5,-8094,4505+117.5,8094)
core_ref=[f for f in r14 if f["properties"].get("variant")=="P_PRESERVE"
          and f["properties"].get("kind")=="235_VISUAL_RESPOND_FACING"]
assert len(core_ref)==6
assert all(shape(f["geometry"]).difference(core_strip).area<.0001 for f in core_ref)
with (OUT/"R15_Q1_Q2_MAIN_AXIS_MEASUREMENTS.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
(OUT/"R15_Q1_Q2_AXIS_ALTERNATIVES.geojson").write_text(json.dumps({
 "type":"FeatureCollection","properties":{
 "status":"EXPERIMENTAL_PLAN_RESERVATIONS_NO_APPROVED_PIER_GEOMETRY",
 "main_axis_x":xmain,"aisle_axis_x":xaisle,"source_sha256":digest},
 "features":features},separators=(",",":"))+"\n")
def draw(ax,g,fc,ec="#57616b",alpha=1,lw=.5,z=1):
    polys=[g] if g.geom_type=="Polygon" else [t for t in getattr(g,"geoms",[]) if t.geom_type=="Polygon"]
    for p in polys:
        ax.add_patch(P(list(p.exterior.coords),facecolor=fc,edgecolor=ec,alpha=alpha,linewidth=lw,zorder=z))
        if fc!="none":
            for hole in p.interiors:
                ax.add_patch(P(list(hole.coords),facecolor="#fffdfa",edgecolor="none",zorder=z+.01))
def panel(ax,key):
    draw(ax,remaining,"#cebaa0",lw=.3)
    for n,g in clear.items():
        if g.bounds[2]<3500 or g.bounds[0]>5600:continue
        draw(ax,g,"#e4eee9",ec="#547382",lw=.5,z=3)
    for g in voids.values():draw(ax,g,"#a7d8ea",ec="#427e9b",lw=.6,z=4)
    for g in oldmajor:draw(ax,g,"none",ec="#906b52",lw=1.2,z=6)
    for f in features:
        if f["properties"]["scenario"]==key:
            draw(ax,shape(f["geometry"]),"#b26d49",ec="#7f4c39",alpha=.82,lw=.6,z=7)
    for f in core_ref:
        draw(ax,shape(f["geometry"]),"#9272b1",ec="none",alpha=.76,lw=0,z=8)
    ax.axvline(xmain,color="#a53e4a",ls="--",lw=1,zorder=10)
    ax.axvline(xaisle,color="#557cb0",ls=":",lw=.9,zorder=10)
    ax.set_xlim(3550,5520);ax.set_ylim(-8130,8130)
    ax.set_aspect("equal","box");ax.grid(alpha=.11)
    ax.set_xlabel("Global X • native units");ax.set_ylabel("Global Y • native units")
fig,axes=plt.subplots(1,3,figsize=(19,12.5),facecolor="white")
for ax,key,title in zip(axes,scenarios,["S0 | Existing 800 strip, 180 west",
                                        "S1 | 800 strip centered at X=4505",
                                        "S2 | Full 1160 gap, centered on X=4505"]):
    panel(ax,key);ax.set_title(title,loc="left",pad=12,fontsize=10.7,weight="bold")
fig.suptitle("F5ZP R15 — Q1–Q2 MAIN SEPARATOR AXIS: 2D BEARING-RESERVATION STUDY\n"
"Agreed organizing axis X=4505 • R11 vaults and R13 Option B passages unchanged",
x=.048,y=.977,ha="left",fontsize=16,weight="bold",color="#273b43")
fig.legend(handles=[Patch(facecolor="#b26d49",label="Alternative major bearing reservation"),
   Line2D([0],[0],color="#906b52",label="Recovered original 800 strip outline"),
   Patch(facecolor="#9272b1",label="235 visual emphasis, not a structural pier"),
   Patch(facecolor="#a7d8ea",label="Option B passages"),
   Line2D([0],[0],color="#a53e4a",ls="--",label="Main axis 4505"),
   Line2D([0],[0],color="#557cb0",ls=":",label="Aisle opening axis 4480")],
  loc="lower center",bbox_to_anchor=(.5,.043),ncol=3,frameon=False,fontsize=9.5)
fig.text(.048,.014,"Geometric reservations only. All variants meet the sanctuary vaults at corners, not proven bearing faces; the 25-unit aisle-axis offset and F5ZL-C remain unresolved.",fontsize=9,color="#8e5147")
fig.subplots_adjust(top=.88,bottom=.13,left=.035,right=.99,wspace=.19)
png=OUT/"F5ZP_R15_Q1_Q2_MAIN_AXIS_STUDY.png";svg=OUT/"F5ZP_R15_Q1_Q2_MAIN_AXIS_STUDY.svg"
fig.savefig(png,dpi=170,bbox_inches="tight");fig.savefig(svg,bbox_inches="tight");plt.close(fig)
qa={"status":"R15 EXPERIMENTAL 2D AXIS COORDINATION, NOT APPROVED SUPPORT GEOMETRY",
 "source_sha256":digest,"source_files_unchanged":True,"source_Q1_Q2_main_axis_x":xmain,
 "source_aisle_axis_x":xaisle,"aisle_axis_offset":xaisle-xmain,
 "original_major_center_x":4325,"original_major_offset_from_main_axis":-180,
 "source_original_major_width":800,"centered_study_width":800,"full_gap_study_width":1160,
 "all_scenarios_inside_R11_retained_masonry":True,
 "all_scenarios_avoid_seven_R13_B_passages":True,
 "all_scenarios_avoid_R11_clear_vaults":True,
 "all_scenarios_have_zero_line_contact_with_main_Q1_Q2_vault_boundaries":True,
 "architectural_interpretation":"Main separator axis adopted for reservation composition; not a completed pier bearing.",
 "unresolved":["Need explicit vault-corner/respond geometry to establish real bearing faces.",
 "S1 centered 800 strip ceases to preserve original 800 footprint and would require geometric approval to implement.",
 "S2 full-width masonry reservation is not proof of a load-bearing 1160-wide pier.",
 "R13 B aisle openings remain centered at 4480 (25 west of the 4505 main separator).",
 "235 visual facing remains experimental and not a structural width.",
 "F5ZL-C support schedule missing; no structural loading or real arch profile developed."]}
(OUT/"R15_Q1_Q2_MAIN_AXIS_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
(OUT/"README_HANDOFF.md").write_text("""# R15 — Adopt main separator axis as organizing reference, 2D only

Design intent: use the established Q1–Q2 **main-bay separator axis X=4505** for all new studies. The Q1–Q2 aisle opening axis is X=4480; its 25-unit west offset is not silently corrected. R11, R13, R14, historical source footprints and all vault clear spaces remain unchanged.

## Three measured plan reservations
- S0: original R12C major bearing x3925..4725 (800 wide), center x4325, -180 from axis.
- S1: experimental x4105..4905 (800 wide), center x4505; loses original west portion, gains east reservation.
- S2: experimental x3925..5085 (1160 wide), center x4505; retains original footprint and extends to main bay divider endpoints. This is NOT an endorsement of a 1160-wide pier or load path.

Each scenario is projected onto the two existing 320-wide north/south transverse masonry bands: y2933..3253 and y-3253..-2933. All clear spaces and Option B passage footprints remain untouched. A 235-wide purple facing remains a wholly separate visual study.

## Critical limitation
None of the three study bands has a measurable LENGTH of common boundary with the Q1 or Q2 main vault polygon; at most there are corner contacts. This demonstrates why a centered strip alone cannot establish true supports: need to test the actual vault corner, respond, and wall-interface geometry before deciding bearing.

## Validation
All six experimental footprints fit entirely inside current R11 retained choir masonry, do not overlap R11 clear vaults or seven R13-B passages. Geometric validation only; no historical/structural adequacy. F5ZL-C remains missing.

## Reproduction
python3 R15_Q1_Q2_MAIN_AXIS_RESERVATION_2D.py
""")
with Image.open(png) as im:print("IMAGE",im.size);im.verify()
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digest[k] for k,p in paths.items())
archive=Path.home()/"Downloads"/"F5ZP_R15_Q1_Q2_MAIN_AXIS_2D_EXPERIMENTAL.zip"
with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as z:
    z.write(Path(__file__),arcname=Path(__file__).name)
    for f in OUT.iterdir():z.write(f,arcname=f.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
shutil.copy2(png,Path.home()/"Downloads"/"F5ZP_R15_Q1_Q2_MAIN_AXIS_STUDY.png")
print("R15",len(records),"measurements",len(features),"footprints, QA PASS; zip",archive)