#!/usr/bin/env python3
"""R23: 960 E-W architectural intent vs actual Q1–Q2 interfaces. 2D, sources read-only."""
from pathlib import Path
import json,csv,hashlib,zipfile,shutil,xml.etree.ElementTree as ET
from shapely.geometry import shape,box,Polygon,mapping,LineString
from shapely.ops import unary_union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly,Patch,Rectangle
from matplotlib.lines import Line2D
from PIL import Image
R=Path(__file__).resolve().parent
O=R/"R23_Q1Q2_960_INTERFACE_EXPERIMENTAL";O.mkdir(exist_ok=True)
paths={
 "R11":R/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "R13":R/"R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson",
 "R16":R/"R16_Q1_Q2_BEARING_FACE_CONTACT_EXPERIMENTAL/R16_Q1_Q2_EXACT_FACE_CONTACT_STRIPS.geojson",
 "R17":R/"R17_Q1_Q2_MASONRY_JUNCTION_2D_EXPERIMENTAL/R17_EXISTING_MASONRY_JUNCTION_REFERENCES.geojson",
 "R22":R/"R22_Q1_Q2_EW_DEPTH_COMPARISON_EXPERIMENTAL/R22_NUMERICAL_QA.json",
}
hashes={key:hashlib.sha256(f.read_bytes()).hexdigest() for key,f in paths.items()}
feat={key:json.loads(paths[key].read_text())["features"] for key in ("R11","R13","R16","R17")}
qa22=json.loads(paths["R22"].read_text())
assert qa22["preferred_experimental_depth_X"]==960 and qa22["preferred_envelope_bounds_X"]==[4025,4985]
vault={z["properties"]["id"]:shape(z["geometry"]) for z in feat["R11"] if z["properties"].get("role")=="CLEAR"}
assert len(vault)==218
masonry=[shape(z["geometry"]) for z in feat["R11"] if "MASONRY" in z["properties"].get("id","")]
choir=next(shape(z["geometry"]) for z in feat["R11"] if z["properties"].get("id")=="CHOIR_MASONRY_R10")
voids={z["properties"]["id"]:shape(z["geometry"]) for z in feat["R13"]
 if z["properties"].get("variant")=="B_BALANCED" and z["properties"].get("layer")=="EXPERIMENTAL_PASSAGE_VOID"}
assert len(voids)==7
reference={z["properties"]["opening"]+"_"+z["properties"]["end"]:shape(z["geometry"]) for z in feat["R16"]}
assert len(reference)==14
junction={z["properties"]["name"]:shape(z["geometry"]) for z in feat["R17"]}
assert len(junction)==8
retained=choir.difference(unary_union(list(voids.values())))
protected_clear=unary_union(list(vault.values()))
assert (vault["Q1"].bounds[2],vault["Q2_MAIN"].bounds[0])==(3925,5085)
assert all(voids[k].bounds[2]-voids[k].bounds[0]==470 for k in voids if "MAIN" not in k)
left,right,axis=4025,4985,4505
assert (left+right)/2==axis and right-left==960
assert (3925+5085)/2==axis

# Graphic-only 960 facing envelope. The 320-high separator at either end of the
# main opening can taper from 960 at the sanctuary to 470 at the first aisle.
# These are INSET architectural annotations, not actual material nor supports.
face_main={}
tapers={}
wings={}
report=[]
for side,sgn in (("N",1),("S",-1)):
    main=reference["C_MAIN_"+("UPPER" if sgn==1 else "LOWER")]
    first=reference[side+"_A1_"+("LOWER" if sgn==1 else "UPPER")]
    old=junction[side+"_MAJOR_ORIGINAL_800"]
    rest=junction[side+"_EAST_360"]
    if sgn==1:
        core=box(left,2573,right,2933)
        taper=Polygon([(left,2933),(right,2933),(4715,3253),(4245,3253)])
        fullband=box(3925,2933,5085,3253)
    else:
        core=box(left,-2933,right,-2573)
        taper=Polygon([(4245,-3253),(4715,-3253),(right,-2933),(left,-2933)])
        fullband=box(3925,-3253,5085,-2933)
    wing=main.difference(core)
    assert wing.area==2*100*360 and abs(taper.area-((960+470)/2*320))<1e-5
    assert taper.is_valid
    assert core.difference(retained).area<1e-6
    assert taper.difference(retained).area<1e-6
    assert wing.difference(retained).area<1e-6
    assert core.intersection(protected_clear).area==taper.intersection(protected_clear).area==0
    assert old.bounds[0]==3925 and old.bounds[2]==4725
    assert rest.bounds[0]==4725 and rest.bounds[2]==5085
    assert fullband.equals(unary_union([old,rest]))
    # The TRUE receiving strip still touches 360 of Q1+Q2 face. An isolated
    # 960-wide visual core has 0 contact to both real vault X faces.
    true_w=main.boundary.intersection(vault["Q1"].boundary).length
    true_e=main.boundary.intersection(vault["Q2_MAIN"].boundary).length
    core_w=core.boundary.intersection(vault["Q1"].boundary).length
    core_e=core.boundary.intersection(vault["Q2_MAIN"].boundary).length
    taper_to_core=taper.boundary.intersection(core.boundary).length
    taper_to_aisle=taper.boundary.intersection(first.boundary).length
    assert (true_w,true_e,core_w,core_e,taper_to_core,taper_to_aisle)==(360,360,0,0,960,470)
    assert fullband.boundary.intersection(main.boundary).length==1160
    assert old.intersection(taper).area>0 and rest.intersection(taper).area>0
    assert min(taper.bounds[0]-3925,5085-taper.bounds[2])==100
    assert 4387.5>left and 4622.5<right
    assert first.bounds[0]==4245 and first.bounds[2]==4715
    face_main[side]=core;tapers[side]=taper;wings[side]=wing
    report.append({
      "side":side,"current_real_vault_face_gap_x":1160,
      "visual_core_x_span":960,"visual_core_x_min":left,"visual_core_x_max":right,
      "west_inset":100,"east_inset":100,
      "main_strip_y_depth":360,"old_real_main_vault_contact_each_face":true_w,
      "visual_core_direct_main_vault_contact":0,
      "transverse_band_y_depth":320,
      "visual_taper_start_width":960,"visual_taper_A1_end_width":470,
      "taper_to_visual_main_strip_contact":taper_to_core,
      "taper_to_R16_A1_strip_contact":taper_to_aisle,
      "taper_start_to_first_aisle_west_shoulder":4245-left,
      "taper_start_to_first_aisle_east_shoulder":right-4715,
      "visual_taper_overlaps_original_major_support_area":taper.intersection(old).area,
      "visual_taper_overlaps_existing_east_reservation_area":taper.intersection(rest).area,
      "no_vault_or_passage_intrusion":True,
      "not_approved_masonry_or_pier":True
    })
# Graphically annotate the remainder of the REAL 1160-wide masonry band
# outside the 960->470 facing taper, never mistake it for newly excavated space.
construction={}
for side,sgn in (("N",1),("S",-1)):
    band=box(3925,2933,5085,3253) if sgn==1 else box(3925,-3253,5085,-2933)
    construction[side]=band.difference(tapers[side])
    assert construction[side].difference(retained).area<1e-6
assert len(report)==2
features=[]
for side in "NS":
 for name,g in (("VISUAL_CORE_960",face_main[side]),("INSET_TAPER_960_TO_470",tapers[side]),
                 ("REAL_MASONRY_OUTSIDE_TAPER",construction[side]),("REAL_MAIN_RECEIVER_WINGS",wings[side])):
    features.append({"type":"Feature","properties":{"id":side+"_"+name,
       "status":"EXPERIMENTAL_VISUAL_REGISTRATION_ONLY","actual_geometry_modified":False},
       "geometry":mapping(g)})
(O/"R23_960_INSET_INTERFACE_REFERENCE.geojson").write_text(json.dumps({
 "type":"FeatureCollection","properties":{"reference_axis_x":4505,
 "status":"EXPERIMENTAL 2D VISUAL ENVELOPE, NOT REAL STRUCTURAL REPLACEMENT",
 "source_sha256":hashes},"features":features},separators=(",",":"))+"\n")
with (O/"R23_INTERFACE_MEASUREMENTS.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(report[0]));w.writeheader();w.writerows(report)
qa={
 "status":"R23 2D GEOMETRIC COORDINATION PASS; NOT AN APPROVED ARCHITECTURAL OR STRUCTURAL DESIGN",
 "source_sha256":hashes,"source_inputs_unmodified":True,
 "Q1_west_vault_face_x":3925,"Q2_east_vault_face_x":5085,
 "true_vault_face_to_face_gap":1160,"adopted_experimental_visual_target_x":960,
 "main_reference_axis_x":4505,"visual_inset_each_end":100,
 "all_218_vault_polygons_unchanged":True,"R13_B_seven_passage_polygons_unchanged":True,
 "all_14_R16_receiving_strips_unchanged":True,"all_8_R17_junction_references_unchanged":True,
 "main_north_south_openings_unchanged":True,"six_aisle_openings_unchanged":True,
 "actual_R16_main_face_contact_length_each_side":360,
 "960_only_has_direct_vault_face_contact":False,
 "taper_has_960_line_contact_to_visual_main_core":True,
 "taper_has_470_line_contact_to_existing_A1_strip":True,
 "recovered_800_by_320_major_bearing_kept_unmodified":True,
 "existing_east_360_by_320_masonry_kept_unmodified":True,
 "all_visual_studies_within_retained_R11_masonry":True,
 "technical_validation":"Reproducible valid source geometry, CSV/GeoJSON/SVG outputs",
 "geometric_validation":"Passed for 2D plan overlays and contacts only",
 "architectural_validation":"Unresolved: no physically buildable 960 support selected",
 "historical_validation":"Not assessed","structural_validation":"Not assessed",
 "issues":[
   "Actual protected Q1/Q2 vault faces remain at X3925 and X5085: the geometric gap remains 1160.",
   "Only the facing/core could APPEAR 960, by 100-unit recesses at each side; a true 960 vault-face gap requires new approval and coordinated vault relocation.",
   "A purely 960-wide core does NOT reach Q1 or Q2 vault faces; the original 1160 receiver is retained beneath the graphical study.",
   "A 960→470 tapered face across the existing 320 transverse band is a possible visual transition, not historical or structural validation.",
   "Unchanged R12C original 800-unit support may not itself be centered on X4505.",
   "F5ZL-C support schedule is still missing; no actual pier/arch design is approved."
 ],"per_side":report}
(O/"R23_NUMERICAL_QA.json").write_text(json.dumps(qa,indent=2)+"\n")

plt.rcParams.update({"text.color":"#e8f2f9","axes.labelcolor":"#a9c6d5",
 "xtick.color":"#a9bdcc","ytick.color":"#a9bdcc","axes.edgecolor":"#657f92",
 "savefig.facecolor":"#0b1420","font.size":10})
def draw(ax,g,face,edge="#6c8c9f",lw=.35,z=1,alpha=1):
    polys=[g] if g.geom_type=="Polygon" else [p for p in getattr(g,"geoms",[]) if p.geom_type=="Polygon"]
    for p in polys:
        ax.add_patch(MPoly(list(p.exterior.coords),facecolor=face,edgecolor=edge,
            linewidth=lw,zorder=z,alpha=alpha))
        if face!="none":
            for ring in p.interiors:ax.add_patch(MPoly(list(ring.coords),facecolor="#14222f",edgecolor="none",zorder=z+.02))
def background(ax):
    ax.set_facecolor("#14222f")
    for g in masonry:draw(ax,g,"#4b5b6d",edge="#607488",lw=.18)
    for g in vault.values():draw(ax,g,"#193b4a",edge="#759caa",lw=.33,z=2)
    for g in voids.values():draw(ax,g,"#2f82a3",edge="#82d8f3",lw=.6,z=3)
    ax.grid(alpha=.08);ax.set_aspect("equal","box")
    ax.set_xlabel("Global X • native units");ax.set_ylabel("Global Y • native units")
fig=plt.figure(figsize=(19,12),facecolor="#0b1420")
gr=fig.add_gridspec(2,2,height_ratios=[.85,1.45],left=.05,right=.98,
 top=.88,bottom=.13,hspace=.28,wspace=.19)
full=fig.add_subplot(gr[0,:]);region=fig.add_subplot(gr[1,0]);detail=fig.add_subplot(gr[1,1])
for ax in (full,region,detail):background(ax)
for ax in (region,detail):
    for side in "NS":
        draw(ax,reference["C_MAIN_"+("UPPER" if side=="N" else "LOWER")],
            "none",edge="#60d0bb",lw=2,z=6)
        draw(ax,junction[side+"_MAJOR_ORIGINAL_800"],"none",edge="#e9b468",lw=2,z=8)
        draw(ax,wings[side],"#f77fa7",edge="#ffb6d1",lw=.9,alpha=.85,z=7)
        draw(ax,face_main[side],"#bd68e0",edge="#f2ceff",lw=.8,alpha=.9,z=9)
        draw(ax,tapers[side],"#bd68e0",edge="#f2ceff",lw=.8,alpha=.9,z=9)
    ax.axvline(axis,color="#ffe28c",ls=":",lw=1,zorder=11)
b=unary_union(list(vault.values())).bounds
full.set_xlim(b[0]-1700,b[2]+1700);full.set_ylim(b[1]-1300,b[3]+1300)
full.add_patch(Rectangle((3500,-3550),2050,7100,fill=False,edgecolor="#fd87d3",linewidth=2.3,zorder=15))
full.annotate("Q1–Q2  |  DETAIL BELOW",xy=(5550,3400),xytext=(11000,10600),
 color="#fa99d6",fontsize=11.5,weight="bold",arrowprops={"arrowstyle":"->","color":"#fa99d6","lw":1.4})
region.set_xlim(3250,5800);region.set_ylim(-5200,5200)
detail.set_xlim(3670,5420);detail.set_ylim(2320,3740)
detail.annotate("",xy=(4985,2690),xytext=(4025,2690),arrowprops={"arrowstyle":"<->","color":"#f1d5ff","lw":2.2},zorder=20)
detail.text(4505,2810,"960 VISUAL CORE",ha="center",va="bottom",color="#f1d5ff",
 fontsize=11,weight="bold",zorder=20)
detail.annotate("100",xy=(3975,2810),xytext=(3750,2740),color="#ffb5ce",
 arrowprops={"arrowstyle":"->","color":"#ffb5ce"},fontsize=9)
detail.annotate("100",xy=(5035,2810),xytext=(5190,2740),color="#ffb5ce",
 arrowprops={"arrowstyle":"->","color":"#ffb5ce"},fontsize=9)
detail.text(4505,3320,"FIRST AISLE 470",ha="center",color="#8de8f9",
 fontsize=10,weight="bold",zorder=20)
detail.text(4890,3520,"320-unit\ntransverse band",color="#f8c781",fontsize=9,ha="left",zorder=20)
full.set_title("Complete cathedral | unchanged R11 vaults",loc="left",pad=10,fontsize=12.5,weight="bold")
region.set_title("Q1–Q2 | original geometry + inset visual study",loc="left",pad=10,fontsize=11,weight="bold")
detail.set_title("North junction | 960 → 470 across 320",loc="left",pad=10,fontsize=11,weight="bold")
fig.suptitle("F5ZP R23 | 960 EAST–WEST PREFERENCE — REAL 2D INTERFACE CHECK\n"
 "Actual Q1/Q2 clear-vault separation still 1160 • 960 is an inset visual envelope",
 x=.05,y=.984,ha="left",fontsize=15.8,weight="bold")
fig.legend(handles=[
 Patch(facecolor="#193b4a",edgecolor="#759caa",label="Protected vault"),
 Patch(facecolor="#2f82a3",label="Original Option B passage"),
 Patch(facecolor="#bd68e0",label="960 graphic core and taper"),
 Patch(facecolor="#f77fa7",label="100-unit retained end contact"),
 Line2D([0],[0],color="#e9b468",lw=2,label="Recovered 800-unit major bearing outline")],
 loc="lower center",ncol=3,frameon=False,labelcolor="#edf4fa",bbox_to_anchor=(.5,.05),fontsize=9.2)
fig.text(.05,.013,"Visual study only. Original 1160 receivers and their vault-face contacts remain necessary; no pier, vault, masonry or opening changed.",color="#b7c8d4",fontsize=9.5)
png=O/"F5ZP_R23_960_INTERFACE_FULL_PLAN_DARK.png"
svg=O/"F5ZP_R23_960_INTERFACE_FULL_PLAN_DARK.svg"
fig.savefig(png,dpi=160,bbox_inches="tight");fig.savefig(svg,bbox_inches="tight");plt.close(fig)
ET.parse(svg)
with Image.open(png) as im:im.verify();print("R23 IMAGE VALIDATED",im.size)
(O/"README_HANDOFF.md").write_text("""# R23 — Q1–Q2 960 preference vs. real vault faces (2D only)

**Design status:** Experimental architectural study, not approved masonry, vault or pier geometry. Preserves R19 coordinated floor-plan reference and R22 selected 960 target. R20's Y-shortening remains discarded.

**Essential geometric finding:** Q1 vault reaches X3925; Q2 main vault begins X5085. They remain 1160 apart. A visual 960-wide core centered on organizing axis X4505 runs X4025–4985, with 100 native units of original receiver on each end. Removing those original receiver wings would eliminate the R16 360-unit line contacts to real main-vault faces; the 960 core alone has ZERO such contact. The actual 1160 structural/masonry reservation is unchanged.

**Within the same existing 320-wide transverse bands**, a conceptual tapered visual facing can transition 960-wide from the sanctuary to 470-wide at the first aisle. At Y=2933 (north), it is X4025..4985; by Y=3253 it is X4245..4715, touching the actual A1 470-wide contact strip. On the south, coordinates mirror across Y=0. Both examples lie wholly within R11 reserved masonry and avoid all R11 clear vaults and original R13-B passage voids. The taper is visual set-out, not an architecturally approved or structurally verified pier.

**Decision implied:** Maintain 1160 as the *actual clear-vault face separation*, while carrying 960 as an *apparent/facing depth* and the full masonry as a retained bearing envelope. A true reduction of the actual gap cannot be implemented without relocating protected vault interfaces, which needs separate architectural approval.

**Verification:** 218 clear vault polygons, seven R13-B passages, fourteen R16 receiving strips, eight R17 junction references unchanged; numeric QA and source SHA-256 hashes; one dark full-floor-plan drawing with two detail views. Physical dimensions conversion, F5ZL-C supports, historic and structural validations remain unresolved.

Reproduction: python3 R23_960_Q1Q2_INTERFACE_2D.py
""")
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[k] for k,p in paths.items())
dst=Path.home()/"Downloads"/png.name;shutil.copy2(png,dst)
zippath=Path.home()/"Downloads"/"F5ZP_R23_960_Q1Q2_INTERFACE_2D_EXPERIMENTAL.zip"
with zipfile.ZipFile(zippath,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    z.write(Path(__file__),arcname=Path(__file__).name)
    for p in sorted(O.iterdir()):z.write(p,arcname=p.name)
with zipfile.ZipFile(zippath) as z:assert z.testzip() is None
print("R23 QA PASS /",len(features),"experimental reference polygons /",zippath)