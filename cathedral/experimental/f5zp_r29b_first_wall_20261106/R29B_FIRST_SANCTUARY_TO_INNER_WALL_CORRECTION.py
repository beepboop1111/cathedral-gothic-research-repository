#!/usr/bin/env python3
"""R29B 2D interpretation correction: true first 320 sanctuary-to-inner wall."""
from pathlib import Path
import json,hashlib,zipfile,shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PatchPolygon,Rectangle,Patch
from shapely.geometry import shape,LineString
from shapely.ops import unary_union
from PIL import Image
R=Path(__file__).resolve().parent
O=R/"R29B_FIRST_SANCTUARY_INNER_WALL_CORRECTION";O.mkdir(exist_ok=True)
original=R/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson"
old=R/"R29_Q5_CHEVET_OPEN_ZONE_2D_CORRECTION/R29_CORRECTED_ARCHITECTURAL_INTERPRETATION.json"
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (original,old)}
f=json.loads(original.read_text())["features"]
g={k["properties"]["id"]:shape(k["geometry"]) for k in f}
v={k["properties"]["id"]:shape(k["geometry"]) for k in f if k["properties"].get("role")=="CLEAR"}
assert len(v)==218
c=g["CHEVET_MASONRY_R10"]
ray=LineString([(22000,0),(25000,0)])
hit=c.intersection(ray)
parts=sorted([x for x in getattr(hit,"geoms",[hit]) if x.length>1],key=lambda x:x.bounds[0])
assert len(parts)>=2
a,b=parts[0].bounds[0],parts[0].bounds[2]
assert abs(a-23081.9069)<.002 and abs(b-23401.9069)<.002
assert abs((b-a)-320)<.002
assert abs(v["I_A4_R12C"].bounds[0]-b)<.002
assert v["Q5_MAIN"].bounds[2]==19893
assert abs(20213-a)>2800
note={
 "version":"R29B — CORRECTED FIRST WALL LOCATION (supersedes overly broad R29 open-area wording)",
 "user_clarification":"not exactly the first wall starts at the first 320 width sanctuary to inner layer",
 "status":"USER-CONFIRMED ARCHITECTURAL INTENT; specific central axial cross-section checked against saved 2D geometry",
 "planning_region":"Q5 and the open sanctuary approach BEFORE the sanctuary-to-inner-layer wall",
 "first_actual_wall":"SANCTUARY_TO_INNER_LAYER_320",
 "on_axis_y":0,
 "first_wall_west_x":round(a,6),
 "first_wall_east_x":round(b,6),
 "first_wall_width_on_axis_x":round(b-a,6),
 "Q5_end_x":19893,
 "prior_X19893_to_20213_320":"planning reservation only, not physical wall, per user correction",
 "source_mapping":"CHEVET_MASONRY_R10 polygon has 320 X intersection at Y0 adjoining I_A4_R12C",
 "other_ring_divider_physical_status":"NOT RESOLVED HERE; do not generalize open-all-the-way-through",
 "R28_doorway_proposals":"superseded, not approved",
 "source_SHA256":hashes,
 "validation":{
  "technical":"PASS source hashes and artifact exports",
  "geometric":"PASS centerline 320 wall cross-section and next inner-vault start",
  "architectural":"User confirms FIRST wall at sanctuary–inner boundary; actual doorway/support design unapproved",
  "historical":"NOT assessed",
  "structural":"NOT assessed"},
 "source_geom_modified":False,
 "unresolved":["Wall full 2D shape outside the confirmed axial section needs architectural detailing","F5ZL-C support schedule missing"]}
(O/"R29B_FIRST_WALL_LOCATION.json").write_text(json.dumps(note,indent=2)+"\n")
plt.rcParams.update({"text.color":"#edf5fa","axes.labelcolor":"#b5ceda",
 "xtick.color":"#a9c6d5","ytick.color":"#a9c6d5","axes.edgecolor":"#839aa9","savefig.facecolor":"#0b1723"})
fig=plt.figure(figsize=(16,9.3),facecolor="#0b1723")
gs=fig.add_gridspec(1,2,width_ratios=[1.25,1],left=.057,right=.98,top=.82,bottom=.17,wspace=.13)
whole=fig.add_subplot(gs[0]);detail=fig.add_subplot(gs[1])
def paint(ax,p,fc,ec,lw=0.7,ls="-"):
 objs=[p] if p.geom_type=="Polygon" else [x for x in getattr(p,"geoms",[]) if x.geom_type=="Polygon"]
 for obj in objs:
  ax.add_patch(PatchPolygon(list(obj.exterior.coords),facecolor=fc,edgecolor=ec,linewidth=lw,linestyle=ls,zorder=3))
for ax in [whole,detail]:
 ax.set_facecolor("#152737")
 for key,poly in v.items():
  if key.startswith("Q5") or key.endswith("_R12C"):
   paint(ax,poly,"#143c4c","#76acbe",.65)
 # Physical-wall source is treated as confirmed only at central cross-section;
 # outline other chevet reserve edges as planning geometry.
 paint(ax,c,"none","#919eac",.9,(0,(3,6)))
 ax.plot([a,b],[0,0],color="#ffad70",lw=8,solid_capstyle="butt",zorder=20)
 ax.axhline(0,color="#f5da88",ls=(0,(6,4)),lw=1.05,zorder=10)
 ax.set_aspect("equal","box");ax.grid(alpha=.08)
 ax.set_xlabel("Global X • native units");ax.set_ylabel("Global Y • native units")
whole.set_xlim(16900,28000);whole.set_ylim(-8200,8200)
detail.set_xlim(21600,24500);detail.set_ylim(-1800,1800)
detail.axvline(a,color="#ffbd8a",lw=1,ls=":",zorder=13)
detail.axvline(b,color="#ffbd8a",lw=1,ls=":",zorder=13)
detail.annotate("",xy=(b,0),xytext=(a,0),arrowprops={"arrowstyle":"<->","color":"#ffdda9","lw":2.5},zorder=25)
detail.text((a+b)/2,470,"FIRST WALL • 320",ha="center",fontsize=11,weight="bold",color="#ffdda9",zorder=20)
detail.text(22450,-950,"OPEN SANCTUARY",color="#a9e6e2",ha="center",fontsize=10,weight="bold",zorder=20)
detail.text(23850,-950,"INNER LAYER",color="#a9e6e2",ha="center",fontsize=10,weight="bold",zorder=20)
whole.set_title("Q5 → chevet: first physical wall at sanctuary-to-inner interface",loc="left",pad=13,fontsize=11.2,weight="bold")
detail.set_title("Centerline Y=0: X23081.9–23401.9",loc="left",pad=13,fontsize=11.2,weight="bold")
fig.suptitle("F5ZP R29B | FIRST WALL IS AT THE SANCTUARY → INNER LAYER\n"
 "Earlier Q5 transition bands are planning guides; original vault geometry is unchanged",
 x=.057,y=.97,ha="left",fontsize=15.2,weight="bold")
fig.text(.057,.06,"Confirmed orange segment = measured 320-unit sanctuary/inner wall at Y=0. Gray dashed outlines = source reservations, not independently verified physical walls.",color="#b5cbd7",fontsize=9.4)
png=O/"F5ZP_R29B_FIRST_320_WALL_SANCTUARY_INNER_DARK.png"
fig.savefig(png,dpi=170,bbox_inches="tight");plt.close(fig)
with Image.open(png) as pic:pic.verify()
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[p.name] for p in (original,old))
(O/"README.md").write_text("R29B corrects R29: open Q5 transition only until the first actual 320 native-unit sanctuary-to-inner layer wall; centerline saved R11 polygon shows X23081.9069..23401.9069. Source geom unchanged. Other wall placements unverified. Technical and centerline geometric checks pass, full architectural/structural/historical detail not validated.\n")
shutil.copy2(png,Path.home()/"Downloads"/png.name)
z=Path.home()/"Downloads"/"F5ZP_R29B_FIRST_320_SANCTUARY_WALL_CORRECTION.zip"
with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as archive:
 archive.write(Path(__file__),arcname=Path(__file__).name)
 for p in sorted(O.iterdir()):archive.write(p,arcname=p.name)
with zipfile.ZipFile(z) as archive:assert archive.testzip() is None
print("R29B PASS first wall",a,b,"width",b-a,"output",z)