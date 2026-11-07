#!/usr/bin/env python3
"""R16 Q1-Q2 exact 2D bearing-face continuity test, no source changes.
Bridge strips occupy R13-B retained end masonry and touch the real west/east
vault boundaries over nonzero length. They are conceptual receiving reservations,
NOT proven structural bearers, pier schedule or arch sections.
"""
from pathlib import Path
import json,csv,hashlib,zipfile,shutil,math,xml.etree.ElementTree as ET
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP,Patch
from matplotlib.lines import Line2D
from shapely.geometry import shape,box,mapping,LineString,Point
from shapely.ops import unary_union
from PIL import Image
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"R16_Q1_Q2_BEARING_FACE_CONTACT_EXPERIMENTAL";OUT.mkdir(exist_ok=True)
PATHS={
 "R12C":ROOT/"R12C_PLAN_NATIVE.geojson",
 "R11":ROOT/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "R13":ROOT/"R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson",
 "R15":ROOT/"R15_Q1_Q2_MAIN_AXIS_2D_EXPERIMENTAL/R15_Q1_Q2_MAIN_AXIS_QA.json"}
sha={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in PATHS.items()}
r11=json.loads(PATHS["R11"].read_text())["features"]
d={f["properties"]["id"]:shape(f["geometry"]) for f in r11 if f["properties"].get("role")=="CLEAR"}
masonry=next(shape(f["geometry"]) for f in r11 if f["properties"].get("id")=="CHOIR_MASONRY_R10")
v={f["properties"]["id"]:shape(f["geometry"]) for f in json.loads(PATHS["R13"].read_text())["features"]
 if f["properties"].get("variant")=="B_BALANCED" and f["properties"].get("layer")=="EXPERIMENTAL_PASSAGE_VOID"}
assert len(v)==7
void=unary_union(list(v.values()));cu=unary_union(list(d.values()))
ret=masonry.difference(void)
axis=4505
assert (d["Q1"].bounds[2]+d["Q2_MAIN"].bounds[0])/2==axis
r15=json.loads(PATHS["R15"].read_text());assert r15["source_Q1_Q2_main_axis_x"]==axis
old={f["properties"]["id"]:shape(f["geometry"]) for f in json.loads(PATHS["R12C"].read_text())["features"]}
# Each span is defined by actual vertical boundary faces in R11. Every face
# overlaps a proposed R13 B opening; end margins are construction reservations.
pairs=[("C","MAIN","Q1","Q2_MAIN")]
pairs += [(side,f"A{level}",f"E_{side}_J1 R{level}C3",f"Q2_{side}_A{level}_1")
          for side in ("N","S") for level in (1,2,3)]
def find_opening(side,level):
    name="B_BALANCED_MAIN_PASSAGE" if side=="C" else f"B_BALANCED_{side}_{level}_PASSAGE"
    return v[name]
rows=[];features=[];pass_checks=[]
for side,level,wn,en in pairs:
    west,east=d[wn],d[en];opening=find_opening(side,level)
    wx=west.bounds[2];ex=east.bounds[0];assert ex>wx
    overlap_low=max(west.bounds[1],east.bounds[1])
    overlap_high=min(west.bounds[3],east.bounds[3])
    opmin,opmax=opening.bounds[1],opening.bounds[3]
    assert opmin>overlap_low and opmax<overlap_high
    # MAIN lower/upper +/-360, A1/A2 +/-160, A3 +/-220 from actual
    # both-side overlap, with unequal original A3 y minima.
    ends=[("LOWER",overlap_low,opmin),("UPPER",opmax,overlap_high)]
    expected_jamb=(360 if side=="C" else (220 if level=="A3" else 160))
    widths=[]
    for tag,lo,hi in ends:
        width=hi-lo;assert width>0
        assert abs(width-expected_jamb)<1e-4,(side,level,tag,width,expected_jamb)
        g=box(wx,lo,ex,hi)
        overlap_vault=g.intersection(cu).area
        overlap_void=g.intersection(void).area
        outside=g.difference(ret).area
        assert overlap_vault<1e-5 and overlap_void<1e-5 and outside<1e-5,(side,level,tag,overlap_vault,overlap_void,outside)
        # Face lengths touch the actual 2D vault boundary in vertical line.
        # Do not confuse touching the opening walls with an arch-section
        # bearing calculation; this is planar geometric interface evidence.
        contact_w=g.boundary.intersection(west.boundary).length
        contact_e=g.boundary.intersection(east.boundary).length
        assert abs(contact_w-width)<1e-5,(side,level,tag,contact_w,width)
        assert abs(contact_e-width)<1e-5,(side,level,tag,contact_e,width)
        assert g.is_valid
        ycenter=(lo+hi)/2
        # The chosen main organizing axis X4505 lies through every strip.
        assert wx<axis<ex,(side,level)
        rec={"opening":f"{side}_{level}","end":tag,"west_vault":wn,"east_vault":en,
           "x_west_face":wx,"x_east_face":ex,"main_reference_axis_x":axis,
           "aisle_entrance_axis_x":(wx+ex)/2,
           "y_lower":lo,"y_upper":hi,"planned_end_margin":width,
           "strip_length_x":ex-wx,"west_face_contact_length":contact_w,
           "east_face_contact_length":contact_e,"overlap_protected_vault_area":overlap_vault,
           "overlap_R13_B_opening_area":overlap_void,"outside_R11_retained_masonry_area":outside,
           "physical_support_capacity_verified":False}
        rows.append(rec)
        features.append({"type":"Feature","properties":dict(rec,layer="PROPOSED_2D_FACE_CONTACT_RESERVATION_ONLY"),
                         "geometry":mapping(g)})
        widths.append(width)
    pass_checks.append(dict(opening=side+"_"+level,span_x=ex-wx,opening_width_y=opmax-opmin,
      transverse_masonry_end_margins=widths,
      north_south_face_contacts="GEOMETRIC_2D_ONLY",
      all_four_end_face_contacts_verified=True))
assert len(rows)==14
# Distinguish the 235 facing's original purpose from the measurable strip
# contacts: centerline of visible facing lies at 4505, not a real pier.
for row in rows:
    if row["opening"]!="C_MAIN":
        assert row["aisle_entrance_axis_x"]==4480
    else:assert row["aisle_entrance_axis_x"]==4505
# Each strip reaches both original vault-side x faces and cannot be replaced
# by an isolated 800-wide main bearing, which stops short of Q2 x=5085.
original=old["Q1_Q2_major_1"]
assert original.bounds==(3925,2933,4725,3253)
original_face_w=original.boundary.intersection(d["Q1"].boundary).length
original_face_e=original.boundary.intersection(d["Q2_MAIN"].boundary).length
assert original_face_w==0 and original_face_e==0
# Existing 320 band is distinct from the new 360-high main end margins.
# Check join between the new north main upper strip and old original major
# transverse piece; overlap at shared y2933 boundary x3925..4725.
new_upper=shape(next(f["geometry"] for f in features if f["properties"]["opening"]=="C_MAIN" and f["properties"]["end"]=="UPPER"))
old_join_len=new_upper.boundary.intersection(original.boundary).length
assert old_join_len==800
# Contact strip entire width 1160 is a reservation, not a 1160-square pier.
with (OUT/"R16_BEARING_FACE_CONTACT_MEASUREMENTS.csv").open("w",newline="") as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
(OUT/"R16_Q1_Q2_EXACT_FACE_CONTACT_STRIPS.geojson").write_text(json.dumps({
 "type":"FeatureCollection","properties":{
 "status":"EXPERIMENTAL 2D FACE-TO-FACE INTERFACE TEST",
 "source_sha256":sha,"main_axis":axis,"physical_load_path_not_verified":True},
 "features":features},separators=(",",":"))+"\n")
def draw(ax,g,fc,ec="#476474",alpha=1,lw=.55,z=1):
    polys=[g] if g.geom_type=="Polygon" else [h for h in getattr(g,"geoms",[]) if h.geom_type=="Polygon"]
    for p in polys:
        ax.add_patch(MP(list(p.exterior.coords),facecolor=fc,edgecolor=ec,alpha=alpha,linewidth=lw,zorder=z))
        if fc!="none":
            for ring in p.interiors:
                ax.add_patch(MP(list(ring.coords),facecolor="#fffdfa",edgecolor="none",zorder=z+.05))
def panel(ax,zoom=False):
    ax.set_facecolor("#fffdfa")
    draw(ax,ret,"#cfbda5",lw=.3)
    for n,g in d.items():
        if g.bounds[2]<3550 or g.bounds[0]>5550:continue
        draw(ax,g,"#e5f0e9",lw=.55,z=3)
    for g in v.values():draw(ax,g,"#a9d9e9","#367694",.55,z=5)
    for f in features:
        g=shape(f["geometry"])
        draw(ax,g,"#458c78","#245946",.55,.92,7)
    # historic support projection, outline only
    for side in (-1,1):
        oldmajor=old[f"Q1_Q2_major_{side}"]
        draw(ax,oldmajor,"none",ec="#b17444",lw=1.1,z=8)
    ax.axvline(axis,color="#a24349",ls="--",lw=1,zorder=10)
    ax.axvline(4480,color="#567ab1",ls=":",lw=.7,zorder=10)
    if zoom:
        ax.set_xlim(3650,5510);ax.set_ylim(2270,4930)
        for f in features:
            r=f["properties"]
            if r["opening"] not in ("C_MAIN","N_A1"):continue
            b=shape(f["geometry"]).bounds
            x=(b[0]+b[2])/2;y=(b[1]+b[3])/2
            ax.text(x,y,f'{r["opening"]} {r["end"]}: {r["planned_end_margin"]:g}',fontsize=8,ha="center",va="center",color="#fff",weight="bold",zorder=12)
    else:
        ax.set_xlim(3600,5460);ax.set_ylim(-8240,8240)
    ax.grid(alpha=.1)
    ax.set_aspect("equal","box");ax.set_xlabel("X • native units");ax.set_ylabel("Y • native units")
fig,axes=plt.subplots(1,2,figsize=(16.5,11.7),facecolor="white")
panel(axes[0]);panel(axes[1],True)
axes[0].set_title("All seven openings — fourteen original-face contact strips",
 loc="left",pad=13,fontsize=11,weight="bold")
axes[1].set_title("Enlargement: main vault upper jamb + A1 lower/upper jambs",
 loc="left",pad=13,fontsize=11,weight="bold")
fig.suptitle("F5ZP R16 — Q1–Q2 ACTUAL 2D VAULT-FACE CONNECTION TEST\n"
"Existing Option B end margins: 360 main, 160 A1/A2, 220 A3 • centered by reference to X=4505",
x=.05,y=.978,ha="left",fontsize=15.4,color="#263c48",weight="bold")
fig.legend(handles=[
 Patch(facecolor="#458c78",label="Tested face-contact strips (not approved masonry)"),
 Patch(facecolor="#a9d9e9",label="R13-B opening"),
 Patch(facecolor="#e5f0e9",label="Protected clear vault"),
 Line2D([0],[0],color="#b17444",label="Original 800-wide bearing outline"),
 Line2D([0],[0],color="#a24349",ls="--",label="Main reference axis X=4505"),
 Line2D([0],[0],color="#567ab1",ls=":",label="Aisle axis X=4480")],
 loc="lower center",bbox_to_anchor=(.5,.046),ncol=3,fontsize=8.7,frameon=False)
fig.text(.05,.016,"Face-to-face contact in PLAN is verified. Neither arch springing, 3D loading, masonry bonding, nor structural adequacy follows from these tests.",
 fontsize=9.5,color="#8e5040")
fig.subplots_adjust(left=.05,right=.98,top=.89,bottom=.14,wspace=.22)
png=OUT/"F5ZP_R16_Q1_Q2_2D_BEARING_FACE_OVERLAY.png"
svg=OUT/"F5ZP_R16_Q1_Q2_2D_BEARING_FACE_OVERLAY.svg"
fig.savefig(png,dpi=170,bbox_inches="tight");fig.savefig(svg,bbox_inches="tight");plt.close(fig)
qa={
 "status":"R16 EXPERIMENTAL 2D VAULT-FACE CONTACT VALIDATED; NO STRUCTURAL VALIDATION",
 "source_SHA256":sha,"source_files_unchanged":True,
 "main_axis_x":axis,"aisle_axis_x":4480,"aisle_offset_from_main_axis":-25,
 "original_major_support_contact_Q1_length":original_face_w,
 "original_major_support_contact_Q2_length":original_face_e,
 "new_end_strips_count":14,"seven_openings_with_both_end_strips":True,
 "all_west_and_east_vault_faces_contact_with_positive_lengths":True,
 "main_upper_test_strip_to_original_800_support_contact_length":old_join_len,
 "main_opening_strips_face_contacts_native":360,
 "A1_A2_aisle_opening_strips_face_contacts_native":160,
 "A3_outer_aisle_opening_strips_face_contacts_native":220,
 "all_strips_inside_existing_R11_retained_masonry":True,
 "all_strips_avoid_original_vault_clear_spaces":True,
 "all_strips_avoid_optionB_entrance_openings":True,
 "contact_geometry_pass":True,
 "architectural_validation":False,"structural_capacity_validated":False,
 "unresolved":[
 "2D face contact alone is not a tested continuous 3D load path or a completed structural pier.",
 "The original major support stripe and new contact region connect at an 800-long plan edge; physical masonry bonding and capacity are not established.",
 "Aisle openings center at X4480 (25 west of the main separator axis X4505).",
 "Outer historical supports remain displaced in current R11 coordinate frame.",
 "F5ZL-C support schedule is unavailable; no arch curvature or moulding geometry approved.",
 "Q1-Q2 geometry remains an experimental floor-plan study."]
}
(OUT/"R16_Q1_Q2_FACE_CONTACT_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
(OUT/"README_HANDOFF.md").write_text("""# F5ZP R16 — True vault-face contact in 2D (experimental)

## Finding
The old R15 transverse bands at y2933–3253 stop at corners of Q1 and Q2 vaults.
Actual R13 Option B leaves 360-unit high north/south jamb regions inside the main
Q1/Q2 bay clear faces; it leaves 160 at each A1/A2 aisle end and 220 at each A3
outer-aisle end on BOTH north and south sides.

The 14 experimental 2D contact strips extend through the pre-existing masonry
reservation from each west clear-vault X face to its corresponding east clear-vault
X face. Each strip has a **measured nonzero line-contact length** with each real
vault boundary (360/160/220 as listed). Fourteen strip shapes, seven openings,
28 measurable west+east face contacts.

Q1/Q2 main contacts are at X3925 and X5085. Six aisle contacts use X4245/4715,
while their physical opening centerline X4480 remains 25 west of organizational
main-axis X4505. No coordinates silently moved.

The main upper jamb contact strip joins the recovered original 800-wide transverse
support strip along a shared 800-unit plan edge. This is 2D polygonal continuity
and not evidence of sound masonry bonding, a valid rib bearing, or load capacity.

## Constraints
Original R11 218 clear-space polygons unmodified; seven R13 Option B entrance
voids unmodified. All candidate strips are entirely inside retained R11 masonry.
No profiles/mouldings/elevation, real arch springing heights, 3D supports,
or physically approved masonry change. No structural proof; F5ZL-C missing.

## Reproduction
python3 R16_Q1_Q2_BEARING_FACE_CONTACT_2D.py
""")
ET.parse(svg)
with Image.open(png) as im:print("R16 PNG VERIFIED",im.size);im.verify()
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[k] for k,p in PATHS.items())
archive=Path.home()/"Downloads"/"F5ZP_R16_Q1_Q2_BEARING_FACE_CONTACT_2D_EXPERIMENTAL.zip"
with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as z:
    z.write(Path(__file__),arcname=Path(__file__).name)
    for f in sorted(OUT.iterdir()):z.write(f,arcname=f.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
dest=Path.home()/"Downloads"/"F5ZP_R16_Q1_Q2_2D_BEARING_FACE_OVERLAY.png"
shutil.copy2(png,dest)
print("R16 PASS:",len(rows),"strips; 28 face contacts; ZIP",archive)