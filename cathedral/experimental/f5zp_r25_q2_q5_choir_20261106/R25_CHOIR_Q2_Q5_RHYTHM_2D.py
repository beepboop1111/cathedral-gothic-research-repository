#!/usr/bin/env python3
"""F5ZP R25 — Q2–Q5 2D choir masonry rhythm.
R24 Option A approved as VISUAL DESIGN ONLY; all source model files read-only.
"""
from pathlib import Path
from shapely.geometry import shape,Polygon,box,LineString,mapping
from shapely.ops import unary_union
import csv,json,hashlib,zipfile,shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as P,Rectangle,Patch
from matplotlib.lines import Line2D
from PIL import Image

R=Path(__file__).resolve().parent
O=R/"R25_Q2_Q5_CHOIR_RHYTHM_2D_EXPERIMENTAL";O.mkdir(exist_ok=True)
sources={
"R11":R/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
"R13":R/"R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson",
"R23":R/"R23_Q1Q2_960_INTERFACE_EXPERIMENTAL/R23_960_INSET_INTERFACE_REFERENCE.geojson",
"R24":R/"R24_TAPER_CORNER_EXPERIMENTAL/R24_QA.json"}
digests={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in sources.items()}
j11=json.loads(sources["R11"].read_text())["features"]
j13=json.loads(sources["R13"].read_text())["features"]
j23=json.loads(sources["R23"].read_text())["features"]
j24=json.loads(sources["R24"].read_text())
r24={r["option"]:r for r in j24["results"] if r["side"]=="N"}
assert r24["A_DIRECT"]["R23_baseline_difference_area"]==0
assert len(j24["results"])==6
vault={f["properties"]["id"]:shape(f["geometry"]) for f in j11 if f["properties"].get("role")=="CLEAR"}
assert len(vault)==218
masonry=[shape(f["geometry"]) for f in j11 if "MASONRY" in f["properties"].get("id","")]
choir=next(shape(f["geometry"]) for f in j11 if f["properties"].get("id")=="CHOIR_MASONRY_R10")
entrances=[shape(f["geometry"]) for f in j13 if f["properties"].get("variant")=="B_BALANCED" and f["properties"].get("layer")=="EXPERIMENTAL_PASSAGE_VOID"]
assert len(entrances)==7
original_void=unary_union(entrances)
available=choir.difference(original_void)
all_clear=unary_union(list(vault.values()))
r23={f["properties"]["id"]:shape(f["geometry"]) for f in j23}
assert r23["N_INSET_TAPER_960_TO_470"].area>0
def face(g,x):
    hit=g.boundary.intersection(LineString([(x,-16000),(x,16000)]))
    assert hit.length>1, ("missing vertical face",x,g.bounds)
    return hit.bounds[1],hit.bounds[3]
metrics=[];features=[];sections={};transitions={}
for i in (2,3,4):
    left=vault[f"Q{i}_MAIN"];right=vault[f"Q{i+1}_MAIN"]
    lx=left.bounds[2];rx=right.bounds[0];cx=(lx+rx)/2
    assert rx-lx==520 and (cx in (9089,13065,16753))
    bounds=[left.bounds[1],right.bounds[1],left.bounds[3],right.bounds[3]]
    main=box(lx,max(left.bounds[1],right.bounds[1]),rx,min(left.bounds[3],right.bounds[3]))
    assert main.bounds[1:4:2]==(-2933,2933)
    sections[(i,"MAIN")]=main
    for aisle in ("MAIN",)+tuple(f"{side}_A{j}" for side in "NS" for j in (1,2,3)):
        if aisle=="MAIN":
            a,b=left,right;g=main;nominal=520
        else:
            side,rank=aisle.split("_")
            a=vault[f"Q{i}_{side}_{rank}_2"];b=vault[f"Q{i+1}_{side}_{rank}_1"]
            lx2=a.bounds[2];rx2=b.bounds[0]
            lowA,highA=face(a,lx2);lowB,highB=face(b,rx2)
            ylo,yhi=max(lowA,lowB),min(highA,highB)
            assert yhi>ylo
            g=box(lx2,ylo,rx2,yhi);nominal=270
            assert rx2-lx2==nominal
        assert g.is_valid and g.area>0
        assert g.difference(available).area<1e-5,(i,aisle,"outside")
        assert g.intersection(all_clear).area<1e-5,(i,aisle,"vault")
        assert g.intersection(original_void).area<1e-5,(i,aisle,"R13")
        westcontact=g.boundary.intersection(a.boundary).length
        eastcontact=g.boundary.intersection(b.boundary).length
        assert westcontact>0 and eastcontact>0
        row={"junction":f"Q{i}–Q{i+1}","aisle":aisle,"x_west":g.bounds[0],
          "x_east":g.bounds[2],"center_x":(g.bounds[0]+g.bounds[2])/2,
          "gap_in_plan_X":g.bounds[2]-g.bounds[0],
          "face_overlap_y":g.bounds[3]-g.bounds[1],
          "west_vault_face_contact":westcontact,"east_vault_face_contact":eastcontact,
          "geometric_contact_pass":True,
          "status":"R11_READONLY_RESERVED_MASONRY"}
        metrics.append(row)
        sections[(i,aisle)]=g
        features.append({"type":"Feature","properties":row,"geometry":mapping(g)})
    for side in "NS":
        ag=sections[(i,side+"_A1")]
        alo,ahi=ag.bounds[0],ag.bounds[2]
        my=2933 if side=="N" else -2933
        ay=3253 if side=="N" else -3253
        p=Polygon([(main.bounds[0],my),(main.bounds[2],my),
                   (ahi,ay),(alo,ay)])
        # Each side faces main bay gap (520) and first aisle gap (270).
        assert p.is_valid and p.area==(520+270)*320/2
        assert p.difference(available).area<1e-5
        assert p.intersection(all_clear).area<1e-5
        assert p.intersection(original_void).area<1e-5
        contactMain=p.boundary.intersection(main.boundary).length
        contactA1=p.boundary.intersection(ag.boundary).length
        assert (contactMain,contactA1)==(520,270)
        transitions[(i,side)]=p
        features.append({"type":"Feature","properties":{
          "junction":f"Q{i}–Q{i+1}","side":side,
          "study":"520_TO_270_STRAIGHT_2D_VISUAL_TAPER",
          "status":"EXPERIMENTAL_NOT_APPROVED",
          "contact_main_X":contactMain,"contact_A1_X":contactA1
        },"geometry":mapping(p)})
assert len(metrics)==21 and len(transitions)==6
assert all(m["geometric_contact_pass"] for m in metrics)
assert [sections[(i,"MAIN")].bounds[2]-sections[(i,"MAIN")].bounds[0] for i in (2,3,4)]==[520]*3
assert all(sections[(i,f"{s}_A{rank}")].bounds[2]-sections[(i,f"{s}_A{rank}")].bounds[0]==270
 for i in (2,3,4) for s in "NS" for rank in (1,2,3))
assert len(features)==27
with (O/"R25_CHOIR_GAPS_CONTACTS.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)
(O/"R25_Q2_Q5_GAPS_AND_TAPER_VISUALS.geojson").write_text(json.dumps({
 "type":"FeatureCollection","properties":{"status":"EXPERIMENTAL_2D_READONLY_LAYOUT",
 "source_sha256":digests},"features":features},separators=(",",":"))+"\n")
approval={"reference":"R24 Option A direct taper","user_approval":"Approved to move on",
 "scope":"Approved as 2D VISUAL PROPORTIONS / corner treatment at Q1–Q2 only",
 "approved_visual":"R23 original straight 960→470 taper within existing masonry, with 100-unit end receiving wings",
 "not_approved":"Physical masonry, relocated 1160 face gap, pier bearings, arch geometry, elevation, structural design",
 "source_geometry_preserved":True,
 "note":"R25 520→270 Q2–Q5 shapes are new experiments, NOT included in R24 approval."}
(O/"R24_APPROVAL_SCOPE_CARRIED_FORWARD.json").write_text(json.dumps(approval,indent=2)+"\n")
qa={"status":"R25 2D TECHNICAL AND GEOMETRIC CHECKS PASS; NEW CHOIR TAPER STUDY NOT APPROVED",
 "input_sha256":digests,"protected_vaults_unchanged":218,"R13_B_passages_unchanged":7,
 "R24_Option_A_approval_scope":"2D visual proportions only, Q1–Q2",
 "Q1_Q2_approved_visual_axis_X":4505,
 "Q1_Q2_visual_depth_X":960,"actual_face_gap_X":1160,
 "Q2_Q5_separator_centers_X":[9089,13065,16753],
 "Q2_Q5_original_main_masonry_depth_X":520,
 "Q2_Q5_original_aisle_masonry_depth_X":270,
 "measured_in_plan_gaps":21,"experimental_transition_faces":6,
 "all_regions_within_existing_masonry":True,"no_protected_vault_clashes":True,
 "no_R13_entrance_intrusions":True,"all_27_features_geometrically_valid":True,
 "no_source_model_modified":True,"new_choir_visual_transitions_approved":False,
 "technical_validation":"Pass: programmatic source, export and regression checks",
 "geometric_validation":"Pass: vertical face intervals, nonzero edge contact, available masonry",
 "architectural_validation":"R24 visual arrangement user approved; Q2–Q5 new tapers pending review",
 "historical_validation":"No historical construction verified",
 "structural_validation":"No pier capacity or load path verified",
 "unresolved":["F5ZL-C support schedule missing",
 "R24 visual-facing approval is not approval of a physical 960-wide pier",
 "Q2–Q5 tapers are review annotations and do not replace actual wall masonry",
 "Q5 to curved chevet interface not assessed in R25"]}
(O/"R25_NUMERICAL_QA.json").write_text(json.dumps(qa,indent=2)+"\n")

plt.rcParams.update({"text.color":"#eaf1f6","axes.labelcolor":"#b7ceda",
 "xtick.color":"#b7ceda","ytick.color":"#b7ceda","axes.edgecolor":"#718ca0",
 "font.size":10,"savefig.facecolor":"#0c1522"})
def draw(ax,g,color,edge="#7898ab",lw=.3,alpha=1,z=2):
 ps=[g] if g.geom_type=="Polygon" else [p for p in getattr(g,"geoms",[]) if p.geom_type=="Polygon"]
 for p in ps:
  ax.add_patch(P(list(p.exterior.coords),facecolor=color,edgecolor=edge,
     linewidth=lw,alpha=alpha,zorder=z))
  if color!="none":
   for hole in p.interiors:
    ax.add_patch(P(list(hole.coords),facecolor="#162735",edgecolor="none",zorder=z+.05))
fig=plt.figure(figsize=(19,11.4),facecolor="#0c1522")
gs=fig.add_gridspec(2,2,height_ratios=[.8,1.15],width_ratios=[1.47,1],
 left=.05,right=.982,top=.87,bottom=.125,hspace=.24,wspace=.17)
whole=fig.add_subplot(gs[0,:])
choirax=fig.add_subplot(gs[1,0]);detail=fig.add_subplot(gs[1,1])
for ax in (whole,choirax,detail):
 ax.set_facecolor("#162735")
 for g in masonry:draw(ax,g,"#495b6c",edge="#536777",lw=.17,z=1)
 for g in vault.values():draw(ax,g,"#203b4a",edge="#6995a7",lw=.3,z=2)
 for g in entrances:draw(ax,g,"#2a809f",edge="#75d8f1",lw=.65,z=3)
 for key in ("N_VISUAL_CORE_960","S_VISUAL_CORE_960",
             "N_INSET_TAPER_960_TO_470","S_INSET_TAPER_960_TO_470"):
  draw(ax,r23[key],"#ba79d2",edge="#eecaff",lw=.5,alpha=.89,z=8)
 for i in (2,3,4):
  for side in "NS":draw(ax,transitions[i,side],"#d7a352",edge="#ffe3a4",lw=.5,z=6)
  draw(ax,sections[i,"MAIN"],"#498e7d",edge="#6be1ba",lw=.35,z=4)
  for side in "NS":
   for a in (1,2,3):draw(ax,sections[i,f"{side}_A{a}"],"#498e7d",edge="#6be1ba",lw=.35,z=4)
 ax.set_aspect("equal","box");ax.grid(alpha=.075)
 ax.set_xlabel("X • native units");ax.set_ylabel("Y • native units")
b=unary_union(list(vault.values())).bounds
whole.set_xlim(b[0]-1800,b[2]+1800);whole.set_ylim(b[1]-1500,b[3]+1500)
whole.add_patch(Rectangle((7500,-7900),12200,15800,fill=False,edgecolor="#ff9bd9",lw=2.3,zorder=14))
whole.annotate("Q2–Q5 choir • studies below",xy=(19500,7900),xytext=(12500,11200),
 color="#ff9bd9",fontsize=11,weight="bold",arrowprops={"arrowstyle":"->","color":"#ff9bd9"})
choirax.set_xlim(3500,20700);choirax.set_ylim(-8100,8100)
detail.set_xlim(7750,10450);detail.set_ylim(2210,4820)
detail.axvline(9089,color="#fff0a3",ls=":",lw=1.1,zorder=10)
detail.text(9089,2940,"520",ha="center",va="bottom",color="#9dedcd",weight="bold",fontsize=11,zorder=15)
detail.text(9089,3620,"270",ha="center",va="bottom",color="#c3f3ff",weight="bold",fontsize=11,zorder=15)
whole.set_title("1  |  Full R11 cathedral: Q2–Q5 highlighted",loc="left",pad=10,fontsize=12,weight="bold")
choirax.set_title("2  |  Q1–Q2 approved purple + Q2–Q5 measured green/gold",loc="left",pad=10,fontsize=11.3,weight="bold")
detail.set_title("3  |  Q2–Q3 masonry transition, north detail",loc="left",pad=10,fontsize=11.3,weight="bold")
fig.suptitle("F5ZP R25 | CONTINUE THE CHOIR MASONRY RHYTHM IN 2D\n"
"R24 Option A approved visually at entrance • Q2–Q5: 520 main / 270 aisles",
 x=.05,y=.977,ha="left",fontsize=16,weight="bold")
fig.legend(handles=[
 Patch(facecolor="#203b4a",edgecolor="#6995a7",label="Protected clear vault"),
 Patch(facecolor="#2a809f",label="Existing Q1–Q2 passage"),
 Patch(facecolor="#ba79d2",label="Approved Q1–Q2 visual Option A"),
 Patch(facecolor="#498e7d",label="Measured 520/270 masonry gaps"),
 Patch(facecolor="#d7a352",label="New Q2–Q5 taper study (not approved)")],
 loc="lower center",ncol=3,frameon=False,bbox_to_anchor=(.5,.048),
 labelcolor="#eaf1f6",fontsize=9.5)
fig.text(.05,.013,"No vault, passage, pier, wall or generator changed. Geometric clearance verified; structural/historical approval not implied.",fontsize=9.4,color="#b4c5d0")
png=O/"F5ZP_R25_FULL_PLAN_CHOIR_Q2_Q5_DARK.png"
fig.savefig(png,dpi=165,bbox_inches="tight");plt.close(fig)
with Image.open(png) as image:image.verify();print("IMAGE",image.size)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digests[k] for k,p in sources.items())
(O/"README_HANDOFF.md").write_text("""# R25 — Q2–Q5 2D choir rhythm

**Approval carried forward from user:** R24 **Option A direct 960→470 taper** approved for Q1–Q2 visual treatment, not physical/structural masonry, pier or locked vault relocation. Record in R24_APPROVAL_SCOPE_CARRIED_FORWARD.json.

**New investigation:** Exact R11 main bay separators Q2–Q3, Q3–Q4, Q4–Q5 are each **520 native units X** (axes X9089, 13065, 16753). All paired aisle separators A1/A2/A3 north and south at these interfaces are **270 X**. Existing Q1–Q2 entrance's 1160 actual gap and 960 visual-facing width remain distinct.

**Proposed ONLY as visual trials:** Six straight 520→270 transitions across the already-reserved 320-Y transverse bands (three junctions × north/south). Exact end contacts 520 and 270. No new masonry footprint and no reduction of R11 clear vaults. 21 measured gaps, 6 new taper candidates, 27 total GeoJSON polygons. Note that aisle-row Y lengths may vary with R11 staggered quadrilateral geometry and are measured per face, not guessed from bounds.

**Next design question:** Should Q2–Q5 keep these restrained direct tapers or remain orthogonal rectangular masonry? Neither is approved yet. Q5 connection to curved chevet remains for a later 2D study.

**Validation:** Technical/source reproducibility and geometric contacts pass. Architectural proposal awaits review. Historic logic and structural capacity unverified; F5ZL-C missing. Reproduce from unchanged originals with:
python3 R25_CHOIR_Q2_Q5_RHYTHM_2D.py
""")
shutil.copy2(png,Path.home()/"Downloads"/png.name)
z=Path.home()/"Downloads"/"F5ZP_R25_Q2_Q5_CHOIR_RHYTHM_2D_EXPERIMENTAL.zip"
with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as ar:
 ar.write(Path(__file__),arcname=Path(__file__).name)
 for p in sorted(O.iterdir()):ar.write(p,arcname=p.name)
with zipfile.ZipFile(z) as ar:assert ar.testzip() is None
print("R25 PASS",len(metrics),"gaps",len(transitions),"tap ers; package",z)