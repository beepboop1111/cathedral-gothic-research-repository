#!/usr/bin/env python3
"""R22 — native-unit 2D visualization ONLY: Q1/Q2 separator 1160,1080,960.
Original saved R11, R13-B and R19 remain byte-for-byte untouched.
"""
from pathlib import Path
import json,csv,hashlib,zipfile,shutil,xml.etree.ElementTree as ET
from shapely.geometry import shape,box,mapping
from shapely.ops import unary_union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Poly,Rectangle,Patch
from matplotlib.lines import Line2D
from PIL import Image

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"R22_Q1_Q2_EW_DEPTH_COMPARISON_EXPERIMENTAL";OUT.mkdir(exist_ok=True)
SOURCES={
 "R11":ROOT/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "R13":ROOT/"R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson",
 "R19":ROOT/"R19_MASONRY_PROPORTIONS_EXPERIMENTAL/R19_NUMERICAL_QA.json",
}
digest={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in SOURCES.items()}
r11=json.loads(SOURCES["R11"].read_text())["features"]
r13=json.loads(SOURCES["R13"].read_text())["features"]
q19=json.loads(SOURCES["R19"].read_text())
clear={f["properties"]["id"]:shape(f["geometry"]) for f in r11 if f["properties"].get("role")=="CLEAR"}
assert len(clear)==218
masonry=[shape(f["geometry"]) for f in r11 if "MASONRY" in f["properties"].get("id","")]
voids={f["properties"]["id"]:shape(f["geometry"]) for f in r13
 if f["properties"].get("variant")=="B_BALANCED"
 and f["properties"].get("layer")=="EXPERIMENTAL_PASSAGE_VOID"}
assert len(voids)==7 and q19["main_axis_x"]==4505
main=voids["B_BALANCED_MAIN_PASSAGE"]
assert main.bounds==(3925, -2573, 5085, 2573)
x0,x1=clear["Q1"].bounds[2],clear["Q2_MAIN"].bounds[0]
axis=(x0+x1)/2
assert (x0,x1,axis)==(3925,5085,4505)
assert all(g.bounds[2]-g.bounds[0]==470 for k,g in voids.items() if k!="B_BALANCED_MAIN_PASSAGE")
assert q19["visual_width_x"]==235
trials=[("R19 EXISTING",1160),("PREVIOUS TRIAL",1080),("CURRENT TRIAL",960)]
measurements=[];features=[]
for label,span in trials:
    xx0=axis-span/2;xx1=axis+span/2;inset=(1160-span)/2
    assert 3925<=xx0<xx1<=5085
    geom=box(xx0,-2573,xx1,2573)  # dimensional envelope, NOT an edited void polygon
    assert main.covers(geom)
    measurements.append({"label":label,"proposed_EW_separator_depth":span,
      "reference_main_axis_X":axis,"trial_west_X":xx0,"trial_east_X":xx1,
      "inset_from_existing_west_face":inset,"inset_from_existing_east_face":inset,
      "six_aisle_X_depths_unchanged":470,
      "vault_positions_unchanged":True,"status":"VISUAL ENVELOPE ONLY"})
    features.append({"type":"Feature","properties":{"label":label,"status":"NOT A BUILDABLE REVISION",
        "trial_EW_span":span,"source_plan_unchanged":True},
        "geometry":mapping(geom)})
assert [m["inset_from_existing_west_face"] for m in measurements]==[0,40,100]
(OUT/"R22_EW_TRIAL_OUTLINES_ONLY.geojson").write_text(json.dumps({
 "type":"FeatureCollection","properties":{"status":"VISUAL_ONLY_NOT_PHYSICAL_RELOCATION",
 "source_sha256":digest,"note":"To physically reduce vault-face separation, protected footprints or adjacent spatial allocation would need further design/approval."},
 "features":features},separators=(",",":"))+"\n")
with (OUT/"R22_DIMENSION_COMPARISON.csv").open("w",newline="") as f:
 writer=csv.DictWriter(f,fieldnames=list(measurements[0]))
 writer.writeheader();writer.writerows(measurements)
qa={"preferred_experimental_depth_X":960,"preferred_envelope_bounds_X":[4025,4985],"reduction_from_current":200,"inset_each_side":100,"status":"R22 GRAPHICAL 2D COMPARISON: PASS; ACTUAL GEOMETRY NOT MODIFIED",
 "source_sha256":digest,"original_main_clear_vault_west_X":3925,
 "original_main_clear_vault_east_X":5085,"original_gap_X":1160,
 "design_organizing_axis_X":4505,"trial_spans":measurements,
 "R11_clear_vault_polygon_count":218,"R13_B_entrance_void_count":7,
 "all_six_aisle_openings_unchanged":True,"proposed_physical_wall_change":False,
 "conceptual_fit_only":True,"source_files_unchanged":True,
 "technical_validation":True,"geometric_overlay_validation":True,
 "architectural_approval":False,"historical_validation":False,
 "structural_validation":False,
 "known_limitation":"Both protected main vault faces remain at X3925/5085. The 1080/960 envelopes are inset from them by 20/40 on each side. They are NOT smaller existing gaps and would require a separate architectural change to make real.",
 "unresolved":["F5ZL-C schedule remains missing.",
 "No load-bearing pier or pointed-arch elevation changed.",
 "Decision needed whether small revision is an apparent masonry profile versus repositioned bay boundaries."]}
(OUT/"R22_NUMERICAL_QA.json").write_text(json.dumps(qa,indent=2)+"\n")

plt.rcParams.update({"text.color":"#e9f1f7","axes.labelcolor":"#a7c3d2",
 "xtick.color":"#aec8d5","ytick.color":"#aec8d5","axes.edgecolor":"#7793a3",
 "font.size":10,"savefig.facecolor":"#0b1420"})
def draw(ax,g,fc,ec="#7e9aac",alpha=1,lw=.35,z=1):
    polys=[g] if g.geom_type=="Polygon" else [t for t in getattr(g,"geoms",[]) if t.geom_type=="Polygon"]
    for p in polys:
        ax.add_patch(Poly(list(p.exterior.coords),facecolor=fc,edgecolor=ec,
                          alpha=alpha,linewidth=lw,zorder=z))
        if fc!="none":
            for ring in p.interiors:
                ax.add_patch(Poly(list(ring.coords),facecolor="#12212d",edgecolor="none",zorder=z+.05))
fig=plt.figure(figsize=(19.5,11.7),facecolor="#0b1420")
gs=fig.add_gridspec(2,3,height_ratios=[0.95,1.16],
 left=.055,right=.985,top=.87,bottom=.11,hspace=.31,wspace=.12)
full=fig.add_subplot(gs[0,:])
full.set_facecolor("#142331")
for g in masonry:draw(full,g,"#526272","#536575",lw=.2)
for g in clear.values():draw(full,g,"#193747","#7798a9",lw=.33,z=2)
for k,g in voids.items():draw(full,g,"#2c87aa","#85dcf4",lw=.66,z=3)
# Demonstrate WHERE the comparisons belong without drawing false changes at full scale.
full.add_patch(Rectangle((3525,-3070),1940,6140,fill=False,linewidth=2.6,
 edgecolor="#fa77c3",zorder=8))
full.annotate("Q1–Q2 | compare below",xy=(5500,3000),xytext=(11300,9800),
 color="#ff9bd5",fontsize=12,weight="bold",
 arrowprops={"arrowstyle":"->","color":"#ff9bd5","lw":1.4})
b=unary_union(list(clear.values())).bounds
full.set_xlim(b[0]-1750,b[2]+1750);full.set_ylim(b[1]-1450,b[3]+1450)
full.set_aspect("equal","box");full.grid(alpha=.06)
full.set_title("Full cathedral • actual R11 plan unchanged • choir threshold outlined",fontsize=13,pad=10,loc="left",weight="bold")
colors=["#7db2c8","#96d5be","#ffbf71"]
for idx,((label,span),color) in enumerate(zip(trials,colors)):
    ax=fig.add_subplot(gs[1,idx]);ax.set_facecolor("#142331")
    for key in ("Q1","Q2_MAIN"):
        draw(ax,clear[key],"#1d3c4d","#89b8c6",lw=1.1,z=1)
    # A small plan slice through Y=0 illustrates X distance, not elevation.
    draw(ax,box(3925,-750,5085,750),"#285d79","#6cd3f0",alpha=.45,lw=.8,z=2)
    # Actual R11 faces are fixed; fade/dash original 1160 extent for comparison.
    for xx in (3925,5085):
        ax.axvline(xx,color="#c1d4df",ls=(0,(4,3)),lw=1.5,zorder=10)
    inset=(1160-span)/2
    # Colored inset slivers are *not* freed rooms. They expose what would need architectural reallocation.
    if inset:
        for xa in (3925,5085-inset):
            draw(ax,box(xa,-750,xa+inset,750),"#c36383","#f1a9bd",alpha=.9,lw=.45,z=6)
    trial_left=axis-span/2;trial_right=axis+span/2
    ax.plot([trial_left,trial_left],[-750,750],color=color,lw=2.4,zorder=11)
    ax.plot([trial_right,trial_right],[-750,750],color=color,lw=2.4,zorder=11)
    ax.annotate("",xy=(trial_right,75),xytext=(trial_left,75),
        arrowprops={"arrowstyle":"<->","lw":2.2,"color":color},zorder=13)
    ax.text(4505,170,f"{span} native units",ha="center",va="bottom",color="#f0f4f8",
        weight="bold",fontsize=15,zorder=14)
    ax.text(4505,-340,("Actual gap" if inset==0 else f"{inset:g} inset each end"),
      ha="center",va="center",color="#f9b7cc" if inset else "#cce3e9",
      fontsize=11,weight="bold",zorder=14)
    ax.axvline(axis,color="#ffde83",ls=":",lw=1.0,zorder=12)
    ax.set_xlim(3590,5420);ax.set_ylim(-1100,1100)
    ax.set_aspect("equal","box");ax.grid(alpha=.09)
    ax.set_title(f"{idx+1}. {label}",fontsize=12,loc="left",pad=9,color=color,weight="bold")
    ax.set_xlabel("Global X • native units")
    if idx==0:ax.set_ylabel("Global Y • native units")
fig.suptitle("F5ZP | Q1–Q2 EAST–WEST SEPARATOR DEPTH — THREE 2D TRIALS\n"
 "Actual geometry unchanged • center X=4,505 • six aisle entrances remain 470",
 x=.055,y=.982,ha="left",fontsize=16.5,weight="bold")
fig.legend(handles=[Patch(facecolor="#193747",edgecolor="#89b8c6",label="Protected vault"),
 Patch(facecolor="#2c87aa",label="Existing entrance"),
 Patch(facecolor="#c36383",label="Inset required for hypothetical reduction"),
 Line2D([0],[0],ls=":",color="#ffde83",label="X=4505 organizing axis")],
 loc="lower center",ncol=4,bbox_to_anchor=(.5,.045),frameon=False,labelcolor="#eaf2f7",fontsize=10)
fig.text(.055,.012,"Bottom panels are local Y=0 PLAN close-ups, not arch elevations. 1080/960 are visual targets only; the true 1160 gap cannot shrink with both vault faces locked.",fontsize=9.8,color="#b2c9d6")
png=OUT/"F5ZP_R22_FULL_PLAN_EW_DEPTH_1160_1080_960_DARK.png"
svg=OUT/"F5ZP_R22_FULL_PLAN_EW_DEPTH_1160_1080_960_DARK.svg"
fig.savefig(png,dpi=160,bbox_inches="tight")
fig.savefig(svg,bbox_inches="tight");plt.close(fig)
ET.parse(svg)
with Image.open(png) as im:im.verify();print("IMAGE VERIFIED",im.size)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digest[k] for k,p in SOURCES.items())
shutil.copy2(png,Path.home()/"Downloads"/png.name)
(OUT/"README_HANDOFF.md").write_text("""# R22 — Three widths, same floor plan

R19 is baseline; R20's north–south edit is NOT incorporated.

The actual fixed Q1/Q2 main bay clear-vault boundaries are X3925 and X5085, separation 1160 centered on reference X4505. All 218 clear-vault polygons and seven R13-B passages remain byte-for-byte unchanged. Six aisle passage in-plan X depths remain 470.

R22 overlays proposed **east–west separator target depths**: 1160 (existing), 1080 (40-unit conceptual inset from each original face), and 960 (100-unit inset from each original face). These insets are not newly available space; this overlay does NOT physically shrink the gap or move vaults. Any physical reduction of the vault-face separation would require a separately approved coordinated plan change, or a visual articulation that leaves the real 1160 gap unchanged.

Review image includes full cathedral at the top, true-scale Y=0 plan slices below, dark-mode high contrast. Preferred CURRENT TRIAL 960 units; this is not an approved physical plan change. No physical support, vaulted bay, passage, arch height, masonry bonding or F5ZL-C schedule altered.

Reproduce: python3 R22_Q1_Q2_EW_DEPTH_COMPARISON_2D.py
""")
zipout=Path.home()/"Downloads"/"F5ZP_R22_EW_DEPTH_1160_1080_960_EXPERIMENTAL.zip"
with zipfile.ZipFile(zipout,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    z.write(Path(__file__),arcname=Path(__file__).name)
    for p in sorted(OUT.iterdir()):z.write(p,arcname=p.name)
with zipfile.ZipFile(zipout) as z:assert z.testzip() is None
print("R22 QA PASS; files:",png,zipout)