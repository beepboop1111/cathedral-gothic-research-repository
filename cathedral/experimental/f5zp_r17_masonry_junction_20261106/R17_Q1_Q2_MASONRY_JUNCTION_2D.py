#!/usr/bin/env python3
"""F5ZP R17: auditable 2D masonry-junction continuity; all sources read-only.
R16 contact strips are unchanged reference geometry, not approved physical piers.
"""
from pathlib import Path
import csv,json,hashlib,zipfile,shutil,xml.etree.ElementTree as ET
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlPoly,Patch
from matplotlib.lines import Line2D
from shapely.geometry import shape,box,mapping
from shapely.ops import unary_union
from PIL import Image
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"R17_Q1_Q2_MASONRY_JUNCTION_2D_EXPERIMENTAL";OUT.mkdir(exist_ok=True)
PATHS={
 "R12C":ROOT/"R12C_PLAN_NATIVE.geojson",
 "R11":ROOT/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "R13":ROOT/"R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson",
 "R16":ROOT/"R16_Q1_Q2_BEARING_FACE_CONTACT_EXPERIMENTAL/R16_Q1_Q2_EXACT_FACE_CONTACT_STRIPS.geojson",
}
sha={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in PATHS.items()}
f11=json.loads(PATHS["R11"].read_text())["features"]
clear={f["properties"]["id"]:shape(f["geometry"]) for f in f11 if f["properties"].get("role")=="CLEAR"}
cu=unary_union(list(clear.values()))
masonry=next(shape(f["geometry"]) for f in f11 if f["properties"].get("id")=="CHOIR_MASONRY_R10")
f13=json.loads(PATHS["R13"].read_text())["features"]
voids={f["properties"]["id"]:shape(f["geometry"]) for f in f13 if f["properties"].get("variant")=="B_BALANCED" and f["properties"].get("layer")=="EXPERIMENTAL_PASSAGE_VOID"}
assert len(voids)==7
vu=unary_union(list(voids.values()))
ret=masonry.difference(vu)
original={f["properties"]["id"]:shape(f["geometry"]) for f in json.loads(PATHS["R12C"].read_text())["features"]}
f16=json.loads(PATHS["R16"].read_text())["features"]
contacts={f["properties"]["opening"]+"_"+f["properties"]["end"]:shape(f["geometry"]) for f in f16}
assert len(contacts)==14
assert (clear["Q1"].bounds[2]+clear["Q2_MAIN"].bounds[0])/2==4505
# Treat the ORIGINAL R12C major 800x320 bands as original reference only.
# Candidate bridge annotations extract existing unmodified R11 masonry.
# No polygons are subtracted or added to the actual floor-plan model.
data=[];export=[];main_connections=[]
def emit(name,side,role,g,west=None,east=None,parent=None):
    assert g.is_valid and not g.is_empty and g.area>0
    assert g.difference(ret).area<1e-5,(name,"outside",g.difference(ret).area)
    assert g.intersection(cu).area<1e-5,(name,"vault conflict")
    assert g.intersection(vu).area<1e-5,(name,"opening conflict")
    wa=g.boundary.intersection(west.boundary).length if west is not None else 0.
    ea=g.boundary.intersection(east.boundary).length if east is not None else 0.
    row={"name":name,"side":side,"role":role,"xmin":g.bounds[0],"ymin":g.bounds[1],
      "xmax":g.bounds[2],"ymax":g.bounds[3],"area":g.area,
      "length_contact_to_west":wa,"length_contact_to_east":ea,
      "outside_existing_retained_masonry":g.difference(ret).area,
      "overlap_R13_B_openings":g.intersection(vu).area,
      "overlap_protected_vaults":g.intersection(cu).area,
      "status":"EXPERIMENTAL_2D_REGISTRATION_NOT_STRUCTURAL"}
    data.append(row)
    export.append({"type":"Feature","properties":row,"geometry":mapping(g)})
    return wa,ea
for side,sgn in [("N",1),("S",-1)]:
    main=contacts["C_MAIN_"+("UPPER" if sgn==1 else "LOWER")]
    aisle=contacts[f"{side}_A1_"+("LOWER" if sgn==1 else "UPPER")]
    old=original[f"Q1_Q2_major_{sgn}"]
    assert old.bounds[0:][0]==3925
    mlen=old.boundary.intersection(main.boundary).length
    alen=old.boundary.intersection(aisle.boundary).length
    assert mlen==800 and alen==470
    assert main.distance(aisle)==320
    assert old.difference(ret).area<1e-5
    # The still-reserved eastern part x4725..5085 in y2933..3253 is NOT
    # "new masonry": it is a nominated remainder of R11 reserved masonry.
    east=box(4725,2933,5085,3253) if sgn==1 else box(4725,-3253,5085,-2933)
    join=old.boundary.intersection(east.boundary).length
    assert join==320
    mw,aw=emit(f"{side}_MAJOR_ORIGINAL_800",side,"RECOVERED_MASONRY_REFERENCE",old,main,aisle)
    ew,ea=emit(f"{side}_EAST_360",side,"EXISTING_R11_MASONRY_EAST_RESERVATION",east,old,main)
    assert mw==800 and aw==470 and ew==320
    # Union of the original rectangle with its east 360 remainder is precisely
    # the 1160x320 transverse masonry band, within existing saved reservation.
    full=unary_union([old,east])
    assert full.geom_type=="Polygon"
    assert abs(full.area-1160*320)<.01
    assert full.boundary.intersection(main.boundary).length==1160
    assert full.boundary.intersection(aisle.boundary).length==470
    main_connections.append({"side":side,"original_major_to_main_face":mlen,
      "original_major_to_A1_face":alen,"major_to_east_extension":join,
      "full_1160_to_main_contact":full.boundary.intersection(main.boundary).length,
      "full_1160_to_A1_contact":full.boundary.intersection(aisle.boundary).length,
      "original_major_x_mid":4325,"full_band_x_mid":4505})
    # A1 -> A2 and A2 -> A3 connecting reservations: original 197 vs 321
    # effective within this Q1/Q2 overlap due to staggered polygon edges.
    for i,expected in [(1,197),(2,321)]:
        low=contacts[f"{side}_A{i}_"+("UPPER" if sgn==1 else "LOWER")]
        high=contacts[f"{side}_A{i+1}_"+("LOWER" if sgn==1 else "UPPER")]
        ymin,ymax=sorted([low.bounds[3 if sgn==1 else 1],high.bounds[1 if sgn==1 else 3]])
        assert ymax-ymin==expected
        g=box(4245,ymin,4715,ymax)
        l1,l2=emit(f"{side}_A{i}_TO_A{i+1}",side,"R11_EXISTING_MASONRY_BRIDGE_REFERENCE",g,low,high)
        assert l1==l2==470
        assert g.difference(ret).area<1e-5
# Only count standalone old step-support footprints by name; do not claim fully
# viable construction for outer portions beyond the R11 masonry boundary.
outer_status={}
for side in ("N","S"):
    q=original["Q1_Q2_step_132" if side=="N" else "Q1_Q2_step_133"]
    a2=contacts[f"{side}_A2_"+("UPPER" if side=="N" else "LOWER")]
    a3=contacts[f"{side}_A3_"+("LOWER" if side=="N" else "UPPER")]
    bridge=next(shape(z["geometry"]) for z in export if z["properties"]["name"]==f"{side}_A2_TO_A3")
    outer_status[side]={"historic_inner_step_area":q.area,
         "historic_step_within_retained_masonry":q.difference(ret).area<1e-5,
         "historic_step_intersects_bridge_area":q.intersection(bridge).area,
         "bridge_effective_width_y":bridge.bounds[3]-bridge.bounds[1],
         "bridge_to_A2_contact":bridge.boundary.intersection(a2.boundary).length,
         "bridge_to_A3_contact":bridge.boundary.intersection(a3.boundary).length}
assert len(data)==8 and len(main_connections)==2
assert all(x["historic_step_intersects_bridge_area"]>0 for x in outer_status.values())
# Generate larger-scale contact drawing for review. Original R16 contacts remain
# untouched; light outline highlights accepted source geometry.
def draw(ax,g,fc,edge="#657987",lw=.4,alpha=1,z=2):
    ps=[g] if g.geom_type=="Polygon" else [p for p in getattr(g,"geoms",[]) if p.geom_type=="Polygon"]
    for p in ps:
        ax.add_patch(PlPoly(list(p.exterior.coords),facecolor=fc,edgecolor=edge,
                            linewidth=lw,alpha=alpha,zorder=z))
        if fc!="none":
            for ring in p.interiors:
                ax.add_patch(PlPoly(list(ring.coords),facecolor="#fffefa",edgecolor="none",zorder=z+.02))
def draw_base(ax):
    draw(ax,ret,"#d4c2a9",edge="#9b8471",lw=.22,z=1)
    for n,g in clear.items():
        if g.bounds[0]>5550 or g.bounds[2]<3520:continue
        draw(ax,g,"#e9f2e9",lw=.5,z=3)
    for g in voids.values():draw(ax,g,"#a7d7e7",edge="#42809c",lw=.6,z=4)
    for g in contacts.values():draw(ax,g,"#6ba69a",edge="#2f6b60",lw=.65,z=6)
    for z in export:
        p=z["properties"];g=shape(z["geometry"])
        fc=("#bb8450" if p["role"]=="RECOVERED_MASONRY_REFERENCE" else
            "#ad6688" if p["role"]=="EXISTING_R11_MASONRY_EAST_RESERVATION" else "#6d83af")
        draw(ax,g,fc,edge="#674b46",lw=.5,alpha=.83,z=7)
    ax.axvline(4505,color="#a34c42",lw=.9,ls="--",zorder=10)
    ax.axvline(4480,color="#587aa7",lw=.8,ls=":",zorder=10)
    ax.set_aspect("equal","box");ax.grid(alpha=.1)
    ax.set_xlabel("X (native units)");ax.set_ylabel("Y (native units)")
fig,axes=plt.subplots(1,2,figsize=(17,12),facecolor="white")
for ax in axes:draw_base(ax)
axes[0].set_xlim(3650,5490);axes[0].set_ylim(-7960,7960)
axes[1].set_xlim(3730,5320);axes[1].set_ylim(2250,4870)
axes[0].set_title("Seven original passages and recovered transverse junctions",
 loc="left",fontsize=11.2,weight="bold",pad=12)
axes[1].set_title("Main vault → 320 transverse band → first aisle",
 loc="left",fontsize=11.2,weight="bold",pad=12)
fig.suptitle("F5ZP R17 — 2D RECEIVING-MASONRY JUNCTIONS\n"
"R16 contact strips retained • Q1–Q2 main axis X4505 • no new openings or piers",
x=.045,y=.973,ha="left",fontsize=16.5,weight="bold",color="#273d45")
fig.legend(handles=[Patch(facecolor="#bb8450",label="Recovered 800x320 support"),
 Patch(facecolor="#ad6688",label="Existing east 360x320 masonry remainder"),
 Patch(facecolor="#6d83af",label="Existing 197/321 transverse bridge"),
 Patch(facecolor="#6ba69a",label="Unchanged R16 2D contact strips"),
 Patch(facecolor="#a7d7e7",label="Option B proposed openings"),
 Line2D([0],[0],color="#a34c42",ls="--",label="Main axis 4505")],
 loc="lower center",bbox_to_anchor=(.5,.048),ncol=3,frameon=False,fontsize=9)
fig.text(.045,.015,"All highlighted regions are read-only extractions of R11 masonry. 2D polygon joins do not certify load capacity, bonding, pier sizes, or arch springing.",fontsize=9.3,color="#875143")
fig.subplots_adjust(left=.045,right=.985,top=.89,bottom=.13,wspace=.23)
png=OUT/"F5ZP_R17_Q1_Q2_MASONRY_JUNCTION_CONTINUITY.png"
svg=OUT/"F5ZP_R17_Q1_Q2_MASONRY_JUNCTION_CONTINUITY.svg"
fig.savefig(png,dpi=170,bbox_inches="tight");fig.savefig(svg,bbox_inches="tight");plt.close(fig)
with (OUT/"R17_JUNCTION_CONTACT_MEASUREMENTS.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(OUT/"R17_EXISTING_MASONRY_JUNCTION_REFERENCES.geojson").write_text(json.dumps({
    "type":"FeatureCollection","properties":{"status":"R17_EXPERIMENTAL_JUNCTION_EXTRACTIONS_FROM_EXISTING_R11_MASONRY",
    "no_approved_pier_design":True,"source_sha256":sha},"features":export},separators=(",",":"))+"\n")
qa={"status":"R17 2D PLAN JUNCTION CONTINUITY CHECKS PASSED; architectural / structural validation unresolved",
    "source_sha256":sha,"source_files_unchanged":True,"main_axis_x":4505,"aisle_axis_x":4480,
    "r16_reference_contact_strips_unchanged":14,
    "junction_regions_extracted_from_existing_R11_retained_masonry":8,
    "main_vault_to_first_aisle_bridged_by_original_major_800x320":True,
    "main_major_edges":main_connections,
    "original_major_support_to_R11_east_360_remainder_contact":320,
    "across_full_Q1_Q2_main_transverse_band_width_x":1160,
    "A1_to_A2_effective_bridge_height":197,
    "A2_to_A3_effective_bridge_height":321,
    "A2_to_A3_nominal_separation_note":"Staggered Q1/Q2 vault row edges yield an effective contact-strip separation of 321, not 292; 292 is the general transverse schedule elsewhere.",
    "A1_to_A2_bridge_vault_face_connection_lengths":[470,470],
    "A2_to_A3_bridge_vault_face_connection_lengths":[470,470],
    "historical_step_overlap":outer_status,
    "all_regions_within_R11_retained_masonry":True,
    "all_regions_avoid_R13_B_seven_passages":True,
    "all_regions_avoid_protected_vaults":True,
    "full_2D_wall_union_not_claimed_as_independent_support":True,
    "recovered_old_outermost_supports_still_unresolved":True,
    "structural_capacity_verified":False,
    "architectural_configuration_approved":False,
    "next_review":"Review effective transverse bridge widths and old 800-footprint asymmetry; actual piercing masonry, arch details and 3D springing deferred.",
    "missing_schedule":"F5ZL-C"}
(OUT/"R17_Q1_Q2_JUNCTION_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
(OUT/"README_HANDOFF.md").write_text("""# F5ZP R17 — 2D Q1–Q2 masonry-junction investigation

## Accepted direction, not geometry approval
The R16 fourteen contact strips remain the working 2D reference; no approval as physical piers. The main separator reference is X4505. The recognizable but restrained choir entrance and protected seven-bay chevet remain unchanged.

## Findings
- North and south main-to-A1: R16 main strip and A1 strip are physically 320 native units apart in plan, but the *original* R12C 800×320 major-bearing footprint between them has 800 native units of shared boundary with the main strip and 470 with the A1 strip. This is exact 2D polygonal connection without moving historical geometry.
- The existing *R11 reserved masonry remainder* immediately east of that original bearing is x4725..5085, length 360 and height 320. It contacts the original support on a 320-long vertical edge and, together, spans the complete 1160 wide main separator on the 4505 axis. This is not a newly approved wider structural pier.
- First to second aisle: R11 offers 470-wide × 197-high fully reserved masonry bridges north and south. Each bridge shares 470 units of plan edge with both R16 neighboring strips.
- Second to third aisle: the actual source vault-row alignments yield 470 × 321 bridges north and south, not 292. The discrepancy comes from staggered Q1/Q2 A2/A3 rows and is an architectural coordination issue, not a reason to move vaults.
- Recovered inner step supports overlap the A2–A3 bridge, but their source labels do not make them approved structure. The six other displaced original supports are not silently restored.

## Boundaries
All extracted junctions fit the unmodified R11 masonry after subtracting R13-B proposed passage voids; no incursion into original vault clearances. R16 strips, R13-B passages, major support original source and chevet are unchanged. No section, elevation, 3D arch, masonry bonding or structural load validation.
The missing F5ZL-C schedule stays unresolved.

## Reproduce
python3 R17_Q1_Q2_MASONRY_JUNCTION_2D.py
""")
ET.parse(svg)
with Image.open(png) as im:print("PNG",im.size);im.verify()
assert all(hashlib.sha256(path.read_bytes()).hexdigest()==sha[name] for name,path in PATHS.items())
dest=Path.home()/"Downloads"/"F5ZP_R17_Q1_Q2_MASONRY_JUNCTION_CONTINUITY.png";shutil.copy2(png,dest)
archive=Path.home()/"Downloads"/"F5ZP_R17_Q1_Q2_MASONRY_JUNCTION_2D_EXPERIMENTAL.zip"
with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as z:
    z.write(Path(__file__),arcname=Path(__file__).name)
    for f in sorted(OUT.iterdir()):z.write(f,arcname=f.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print("R17 VERIFIED",len(data),"junction regions; archive",archive)