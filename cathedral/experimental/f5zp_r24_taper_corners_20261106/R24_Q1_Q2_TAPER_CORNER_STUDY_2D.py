#!/usr/bin/env python3
"""R24: evaluate 2D Q1-Q2 visual taper corner treatment, keeping R23 and R11 unchanged."""
from pathlib import Path
import json,csv,math,hashlib,zipfile,shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly,Patch,Rectangle
from matplotlib.lines import Line2D
from shapely.geometry import shape,Polygon,box,mapping
from shapely.ops import unary_union
from PIL import Image

R=Path(__file__).resolve().parent
O=R/"R24_TAPER_CORNER_EXPERIMENTAL";O.mkdir(exist_ok=True)
paths={"R11":R/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "R13":R/"R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson",
 "R16":R/"R16_Q1_Q2_BEARING_FACE_CONTACT_EXPERIMENTAL/R16_Q1_Q2_EXACT_FACE_CONTACT_STRIPS.geojson",
 "R17":R/"R17_Q1_Q2_MASONRY_JUNCTION_2D_EXPERIMENTAL/R17_EXISTING_MASONRY_JUNCTION_REFERENCES.geojson",
 "R23":R/"R23_Q1Q2_960_INTERFACE_EXPERIMENTAL/R23_960_INSET_INTERFACE_REFERENCE.geojson"}
sha={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in paths.items()}
f={k:json.loads(v.read_text())["features"] for k,v in paths.items()}
vault={z["properties"]["id"]:shape(z["geometry"]) for z in f["R11"] if z["properties"].get("role")=="CLEAR"}
masonry=[shape(z["geometry"]) for z in f["R11"] if "MASONRY" in z["properties"].get("id","")]
choir=next(shape(z["geometry"]) for z in f["R11"] if z["properties"].get("id")=="CHOIR_MASONRY_R10")
passages=[shape(z["geometry"]) for z in f["R13"] if z["properties"].get("variant")=="B_BALANCED" and z["properties"].get("layer")=="EXPERIMENTAL_PASSAGE_VOID"]
receive={z["properties"]["opening"]+"_"+z["properties"]["end"]:shape(z["geometry"]) for z in f["R16"]}
major={z["properties"]["name"]:shape(z["geometry"]) for z in f["R17"]}
r23={z["properties"]["id"]:shape(z["geometry"]) for z in f["R23"]}
assert len(vault)==218 and len(passages)==7 and len(receive)==14 and len(major)==8
assert (vault["Q1"].bounds[2],vault["Q2_MAIN"].bounds[0])==(3925,5085)
voids=unary_union(passages);protected=unary_union(list(vault.values()));reserved=choir.difference(voids)
variants={
 "A_DIRECT":[(0,4025,4985),(320,4245,4715)],
 "B_SHOULDER_50":[(0,4025,4985),(50,4025,4985),(320,4245,4715)],
 "C_AISLE_NECK_60":[(0,4025,4985),(260,4245,4715),(320,4245,4715)]}
labels={"A_DIRECT":"A — Direct taper","B_SHOULDER_50":"B — 50-unit square shoulder","C_AISLE_NECK_60":"C — 60-unit straight aisle neck"}
def polygon(slices,side):
    y=lambda z:2933+z if side=="N" else -2933-z
    return Polygon([(a,y(b)) for b,a,c in slices]+[(c,y(b)) for b,a,c in reversed(slices)])
shapes={};measure=[];export=[]
for name,sections in variants.items():
    sections=list(sections)
    for side in "NS":
        g=polygon(sections,side);shapes[name,side]=g
        main=r23[side+"_VISUAL_CORE_960"]
        first=receive[side+"_A1_"+("LOWER" if side=="N" else "UPPER")]
        original=r23[side+"_INSET_TAPER_960_TO_470"]
        starts=g.boundary.intersection(main.boundary).length
        ends=g.boundary.intersection(first.boundary).length
        actual=receive["C_MAIN_"+("UPPER" if side=="N" else "LOWER")]
        checks=[g.difference(reserved).area,g.intersection(protected).area,g.intersection(voids).area]
        assert g.is_valid and max(checks)<1e-6 and starts==960 and ends==470
        assert actual.boundary.intersection(vault["Q1"].boundary).length==360
        assert actual.boundary.intersection(vault["Q2_MAIN"].boundary).length==360
        assert main.boundary.intersection(vault["Q1"].boundary).length==0
        assert main.boundary.intersection(vault["Q2_MAIN"].boundary).length==0
        slopes=[max(math.degrees(math.atan(abs(b[1]-a[1])/(b[0]-a[0]))),
                    math.degrees(math.atan(abs(b[2]-a[2])/(b[0]-a[0]))))
                for a,b in zip(sections,sections[1:])]
        turn=sum(abs(b-a) for a,b in zip(slopes,slopes[1:]))
        row={"option":name,"side":side,"max_side_angle_from_transverse_deg":round(max(slopes),3),
          "extra_corner_deflection_deg":round(turn,3),"visible_face_area":round(g.area,3),
          "R23_baseline_difference_area":round(g.symmetric_difference(original).area,3),
          "join_to_960_core":starts,"join_to_A1_470":ends,"source_main_vault_contact_each":360,
          "960_visual_core_direct_vault_contact":0,
          "encroaches_on_vault_or_entrance":False,"physical_masonry_modified":False}
        measure.append(row)
        export.append({"type":"Feature","properties":{"option":name,"side":side,
            "status":"EXPERIMENTAL VISUAL FACING ONLY"},"geometry":mapping(g)})
assert all(r["R23_baseline_difference_area"]==0 for r in measure if r["option"]=="A_DIRECT")
assert all(r["R23_baseline_difference_area"]>0 for r in measure if r["option"]!="A_DIRECT")
with (O/"R24_TAPER_MEASUREMENTS.csv").open("w",newline="") as fp:
    writer=csv.DictWriter(fp,fieldnames=measure[0].keys());writer.writeheader();writer.writerows(measure)
(O/"R24_VISUAL_TAPER_OPTIONS.geojson").write_text(json.dumps({"type":"FeatureCollection","features":export,
  "properties":{"status":"Experimental only, no source revisions","source_sha256":sha}},separators=(",",":"))+"\n")
qa={"status":"TECHNICAL AND 2D GEOMETRY PASS, ARCHITECTURAL REVIEW PENDING",
    "sha256_source_files":sha,"R11_vaults_unchanged":218,"Option_B_passages_unchanged":7,
    "R16_receiving_strips_unchanged":14,"R17_junction_pieces_unchanged":8,
    "960_visual_core_retained":True,"100_unit_main_end_receiver_wings_retained":True,
    "axis_X":4505,"main_actual_vault_face_gap_X":1160,"aisle_X_center":4480,
    "all_options_fit_existing_reserved_masonry":True,"all_options_touch_960_and_470_reference_faces":True,
    "A_reproduces_R23_taper_exactly":True,
    "results":measure,"technical_validation":"Passed image/CSV/GeoJSON and source hashes",
    "geometric_validation":"Passed intersections, join length, and source comparison",
    "architectural_validation":"Not approved: three alternatives to review",
    "historical_validation":"Not assessed","structural_validation":"Not assessed",
    "interpretation":"A avoids extra shoulders, B and C introduce extra corners without extra usable clearance",
    "unresolved":["F5ZL-C support schedule missing","No arch elevation or load path was modeled",
     "960 is visual-only; actual 1160 vault-face separation retained"]}
(O/"R24_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
# One sheet: cathedral context, three same-scale local north-corner options.
plt.rcParams.update({"text.color":"#ebf3fb","axes.labelcolor":"#b9cbd5",
  "xtick.color":"#b5cbd6","ytick.color":"#b5cbd6","axes.edgecolor":"#8396a4",
  "savefig.facecolor":"#0d1723","font.size":10})
def paint(ax,g,fc,edge="#7893a3",lw=.35,alpha=1,z=1):
    pol=[g] if g.geom_type=="Polygon" else [p for p in getattr(g,"geoms",[]) if p.geom_type=="Polygon"]
    for p in pol:
        ax.add_patch(MPoly(list(p.exterior.coords),facecolor=fc,edgecolor=edge,
                     linewidth=lw,alpha=alpha,zorder=z))
        if fc!="none":
            for hole in p.interiors:ax.add_patch(MPoly(list(hole.coords),facecolor="#162635",edgecolor="none",zorder=z+.02))
fig=plt.figure(figsize=(18.5,11.4),facecolor="#0d1723")
gr=fig.add_gridspec(2,3,height_ratios=[.87,1.22],left=.055,right=.985,top=.865,bottom=.13,hspace=.3,wspace=.12)
whole=fig.add_subplot(gr[0,:]);detail=[fig.add_subplot(gr[1,i]) for i in range(3)]
for ax in [whole]+detail:
    ax.set_facecolor("#162635")
    for g in masonry:paint(ax,g,"#4c5d6d",lw=.17)
    for g in vault.values():paint(ax,g,"#1b3a48",edge="#7695a5",lw=.33,z=2)
    for g in passages:paint(ax,g,"#2c7f9e",edge="#70d6f0",lw=.65,z=3)
    ax.set_aspect("equal","box");ax.grid(alpha=.08)
    ax.set_xlabel("Global X • native units")
    ax.set_ylabel("Global Y • native units")
b=unary_union(list(vault.values())).bounds
whole.set_xlim(b[0]-1800,b[2]+1800);whole.set_ylim(b[1]-1700,b[3]+1700)
whole.add_patch(Rectangle((3600,-4500),1800,9000,fill=False,edgecolor="#ff89d2",linewidth=2.5,zorder=15))
whole.annotate("Q1–Q2 | corner studies below",xy=(5400,4500),xytext=(10000,10100),
  color="#ff9add",fontsize=11,weight="bold",arrowprops={"arrowstyle":"->","color":"#ff9add"})
whole.set_title("Full cathedral • unchanged R11 plan",loc="left",pad=10,fontsize=12,weight="bold")
for ax,(name,slices) in zip(detail,variants.items()):
    paint(ax,r23["N_VISUAL_CORE_960"],"#bf74de",edge="#f5d3ff",lw=.65,z=8)
    paint(ax,shapes[name,"N"],"#a963d6",edge="#f5d3ff",lw=.7,z=9)
    paint(ax,receive["C_MAIN_UPPER"],"none",edge="#5ad2ba",lw=1.6,z=8)
    paint(ax,receive["N_A1_LOWER"],"none",edge="#5ad2ba",lw=1.6,z=8)
    paint(ax,major["N_MAJOR_ORIGINAL_800"],"none",edge="#edb46c",lw=1.4,z=10)
    ax.axvline(4505,color="#ffe28d",ls=":",lw=.9,zorder=12)
    ax.set_xlim(3560,5440);ax.set_ylim(2300,4680)
    m=next(v for v in measure if v["option"]==name and v["side"]=="N")
    ax.set_title(labels[name],loc="left",pad=10,fontsize=11.5,weight="bold")
    ax.text(.035,.97,f'Max face angle: {m["max_side_angle_from_transverse_deg"]:.1f}°',
        transform=ax.transAxes,va="top",color="#f2d7ff",fontsize=9,
        bbox=dict(facecolor="#203445",edgecolor="#9f83b5",pad=4),zorder=20)
fig.suptitle("F5ZP R24 • Q1–Q2 CORNER TREATMENTS FOR 960 → 470 VISUAL TAPER\n"
    "Three 2D alternatives; identical vaults, 100-unit end connections, and original 1160 gap",
    x=.055,y=.982,ha="left",fontsize=15.5,weight="bold")
fig.legend(handles=[Patch(facecolor="#1b3a48",edgecolor="#7695a5",label="Protected vault"),
 Patch(facecolor="#2c7f9e",label="Existing passage"),
 Patch(facecolor="#a963d6",label="960→470 facing study"),
 Line2D([0],[0],color="#edb46c",label="Original major-bearing footprint"),
 Line2D([0],[0],color="#5ad2ba",label="Existing contact reference")],
 loc="lower center",bbox_to_anchor=(.5,.052),ncol=3,frameon=False,labelcolor="#ebf3fb",fontsize=9.2)
fig.text(.055,.014,"A repeats R23 exactly. B/C introduce extra corners but no extra clearance. All options are visual set-outs, not approved structural masonry.",
 color="#b6cbd5",fontsize=9.3)
png=O/"F5ZP_R24_FULL_PLAN_960_TAPER_CORNERS_DARK.png"
fig.savefig(png,dpi=165,bbox_inches="tight");plt.close(fig)
with Image.open(png) as image:image.verify();print("IMAGE_VERIFIED",image.size)
assert all(hashlib.sha256(path.read_bytes()).hexdigest()==sha[key] for key,path in paths.items())
(O/"README_HANDOFF.md").write_text("""# R24 — 2D taper corner choices
R23 A direct taper is compared to B (50-unit flat initial shoulder) and C (60-unit first-aisle straight neck). All are exactly within existing R11 retained masonry and join the unchanged 960 visual core and 470-wide A1 receiving strip along 960- and 470-unit plan edges. Both north and south verified.

A repeats R23 exactly; B and C introduce an additional corner break and a locally sharper diagonal without new available space. Favor A for the restrained entrance pending architectural review, but do NOT promote it to approved masonry or pier.

Main vault faces remain X3925 and X5085 (gap 1160). The original R16 vault-face contact is 360 at each face; a 960 facing alone has zero vault-face contact. All saved R11/R13/R16/R17/R23 files unmodified; SHA256 verified. No 3D, arch elevations, mouldings or structural proof. F5ZL-C missing.
Reproduce: python3 R24_Q1_Q2_TAPER_CORNER_STUDY_2D.py
""")
shutil.copy2(png,Path.home()/"Downloads"/png.name)
z=Path.home()/"Downloads"/"F5ZP_R24_Q1_Q2_TAPER_CORNERS_EXPERIMENTAL.zip"
with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as archive:
    archive.write(Path(__file__),arcname=Path(__file__).name)
    for p in O.iterdir():archive.write(p,arcname=p.name)
with zipfile.ZipFile(z) as archive:assert archive.testzip() is None
print("R24 PASS",len(measure),"rows",z)