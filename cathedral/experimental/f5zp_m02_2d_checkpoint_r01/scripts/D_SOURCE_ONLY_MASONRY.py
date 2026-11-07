#!/usr/bin/env python3
"""M02-D source-true masonry and support plan. 14 outer trials excluded."""
import json,csv,hashlib,zipfile,shutil
from pathlib import Path
from shapely.geometry import shape,Polygon,LineString,mapping
from shapely.ops import unary_union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
from matplotlib.lines import Line2D
from PIL import Image
R=Path(__file__).resolve().parent
O=R/"M02_PHASE_D_MASONRY_SUPPORT_LOCAL";O.mkdir(exist_ok=True)
sources={
"R11":R/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
"R30":R/"R30_OPEN_INTERIOR_ARCHITECTURAL_INTENT_R01/SOURCE_GEOMETRY_EVIDENCE.json",
"R31":R/"R31_SEVEN_FACED_OPEN_INTERIOR_2D_EXPERIMENTAL/R31_OPEN_INTERIOR_1_TO_1.geojson",
"B3":R/"M02_PHASE_B_COMPLETION_R03_LOCAL_EXPERIMENTAL/M02_B_R03_WALL_CONNECTED_RESERVATIONS_1_TO_1.geojson",
"B3QA":R/"M02_PHASE_B_COMPLETION_R03_LOCAL_EXPERIMENTAL/M02_B_R03_FINAL_QA.json",
"CQA":R/"M02_PHASE_C_AMBULATORY_RHYTHM_LOCAL_EXPERIMENTAL/M02_C_NUMERICAL_QA.json"}
sha={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in sources.items()}
docs={k:json.loads(p.read_text()) for k,p in sources.items()}
F=docs["R11"]["features"]
D={f["properties"]["id"]:shape(f["geometry"]) for f in F}
V={f["properties"]["id"]:shape(f["geometry"]) for f in F if f["properties"].get("role")=="CLEAR"}
assert len(V)==218 and docs["R30"]["chancel_polygonal_face_count"]==7
assert docs["B3QA"]["variants_with_continuous_polygon_finite_wall_face_contact_and_no_protected_collision"]==24
open_area=next(shape(f["geometry"]) for f in docs["R31"]["features"] if f["properties"]["id"]=="NAVE_CROSSING_CHOIR_SEVEN_FACED_CHANCEL_OPEN_INTERIOR")
reserved={name:D[name] for name in ("NAVE_MASONRY_R10","CHOIR_MASONRY_R10","CHEVET_MASONRY_R10")}
reserved_union=unary_union(list(reserved.values()))
vault_union=unary_union(list(V.values()))
C=reserved["CHEVET_MASONRY_R10"]
vtx=list(C.exterior.coords)
lo=next(i for i,(x,y) in enumerate(vtx) if 20238<x<20239 and y<0)
hi=next(i for i,(x,y) in enumerate(vtx) if 20238<x<20239 and y>0)
nodes=vtx[lo:hi+1];assert len(nodes)==8
features=[];wallbands=[];wallrows=[];interface=[]
for j,(a,b) in enumerate(zip(nodes,nodes[1:]),1):
 vp=list(V[f"I_A{8-j}_R12C"].exterior.coords)[:-1]
 l1=LineString([a,b]);l2=LineString([vp[3],vp[0]])
 band=Polygon([a,b,vp[0],vp[3]])
 assert band.is_valid and abs(l1.distance(l2)-320)<1e-6
 assert abs(l1.length-l2.length)<1e-6
 assert band.difference(C).area<1e-5 and band.intersection(open_area).area<1e-5
 assert band.intersection(vault_union).area<1e-5
 wallbands.append(band)
 wallrows.append({"face":j,"vault":f"I_A{8-j}_R12C","face_length":round(l1.length,6),
 "perpendicular_width":320,"source_verified":True,"masonry_bond_approved":False})
 features.append({"type":"Feature","properties":{"id":f"CHANCEL_FIRST_WALL_FACE_{j}",
 "role":"USER_CONFIRMED_FIRST_WALL_MEASURED_BAND","width":320},
 "geometry":mapping(band)})
for i in range(1,8):
 for ring in "IMT":
  key=f"{ring}_A{i}_R12C"
  assert key in V
  features.append({"type":"Feature","properties":{"id":key,"role":"UNCHANGED_R11_VAULT_PLANNING_POLYGON"},
  "geometry":mapping(V[key])})
 for x,y,dist in (("I","M",197),("M","T",292)):
  p,q=V[f"{x}_A{i}_R12C"],V[f"{y}_A{i}_R12C"]
  assert abs(p.distance(q)-dist)<1e-6
  interface.append({"bay":i,"relationship":x+"-"+y,"gap_native":dist,"type":"RESERVED_INTERFACE_NOT_A_PROVEN_WALL"})
for ring in "IMT":
 for i in range(1,7):
  p,q=V[f"{ring}_A{i}_R12C"],V[f"{ring}_A{i+1}_R12C"]
  interface.append({"bay":i,"relationship":ring+str(i)+"-"+ring+str(i+1),
  "gap_native":round(p.distance(q),6),"type":"VAULT_ADJACENCY_NOT_AN_APPROVED_SHARED_ARCH"})
assert len(interface)==32
studies={}
for f in docs["B3"]["features"]:
 key=f["properties"]["id"]
 if not key.endswith("_B_MODERATE"):continue
 name=key.removesuffix("_B_MODERATE")
 studies[name]=shape(f["geometry"])
 features.append({"type":"Feature","properties":{"id":"PROVISIONAL_BEARING_"+name,
 "role":"B3_MODERATE_REFERENCE_ONLY_NOT_A_PIER","approved":False},
 "geometry":f["geometry"]})
assert set(studies)=={"END_S","END_N"}|{f"C{i}" for i in range(1,7)}
combined=unary_union(list(studies.values()))
assert combined.intersection(open_area).area<1e-5
assert combined.intersection(vault_union).area<1e-5
assert combined.difference(reserved_union).area<1e-5
assert len(features)==36
assert not any("_TRIAL" in f["properties"]["id"] or "_L1_" in f["properties"]["id"] or "_L2_" in f["properties"]["id"] for f in features)
def csvout(n,rows):
 with (O/n).open("w",newline="") as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
csvout("M02_D_SEVEN_320_WALL_FACES.csv",wallrows)
csvout("M02_D_THIRTY_TWO_INTERFACE_GAPS.csv",interface)
ms=[{"source_layer":name,"status":"EXPERIMENTAL RESERVATION; NOT ENTIRE PHYSICAL WALL",
"area_native_sq":round(g.area,4),
"area_overlapping_open_plan":round(g.intersection(open_area).area,4)} for name,g in reserved.items()]
csvout("M02_D_R11_MASONRY_LAYER_CLASSIFICATION.csv",ms)
ss=[{"site":name,"candidate":"B3 moderate (180 radius); VISUAL REFERENCE ONLY",
"area_native_sq":round(g.area,5),"vault_clearance_native":round(g.distance(vault_union),5),
"open_plan_intersection_area":round(g.intersection(open_area).area,8),
"approved_real_pier":False} for name,g in sorted(studies.items())]
csvout("M02_D_EIGHT_PROVISIONAL_SUPPORT_REFERENCES.csv",ss)
geo={"type":"FeatureCollection","properties":{
"status":"NO 14 OUTER TRIAL CELLS; original 7 T polygons retained",
"physical_wall_classification":"Seven user-confirmed sanctuary-to-inner bands only",
"source_sha256":sha},"features":features}
(O/"M02_D_1TO1_SOURCE_FLOORPLAN_NO_FOURTEEN.geojson").write_text(json.dumps(geo,separators=(",",":"))+"\n")
qa={"milestone":"M02 Phase D","status":"2D masonry and reservation coordination complete; proposed supports unapproved",
"source_sha256":sha,"original_R11_clear_vaults":218,"source_chevet_7_7_7_retained":True,
"experimental_outer_14_cells_excluded_from_floor_plan":True,
"first_sanctuary_to_inner_wall_faces":7,"first_wall_perpendicular_width":320,
"source_masonry_overlaps_open_zone":[x["area_overlapping_open_plan"] for x in ms],
"provisional_support_sites":8,"provisional_supports_selected_for_architecture":0,
"provisional_support_vault_overlap_area":combined.intersection(vault_union).area,
"provisional_support_open_overlap_area":combined.intersection(open_area).area,
"source_I_M_separator_7_bays_native":197,"source_M_T_separator_7_bays_native":292,
"validation":{"technical":"PASS hash/integrity/export","geometric":"PASS chancel wall strips, source rings, reservations",
"architectural":"OPEN sanctuary and first 320 wall user-confirmed; support profiles provisional",
"historical":"NOT assessed","structural":"NOT assessed"},
"unresolved":["8 real pier/bearing designs and masonry joins",
"Source R11 masonry-reservation layers not all physical walls",
"F5ZL-C missing support schedule","Physical unit conversion unverified",
"14 outer subdivisions explicitly excluded pending approval"]}
(O/"M02_D_NUMERICAL_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
plt.rcParams.update({"text.color":"#eff2f7","axes.labelcolor":"#adbfcb",
"xtick.color":"#abbdc8","ytick.color":"#abbdc8","axes.edgecolor":"#849aa9",
"savefig.facecolor":"#0e1927"})
fig=plt.figure(figsize=(18.6,11.7),facecolor="#0e1927")
gr=fig.add_gridspec(2,2,height_ratios=[.75,1.25],width_ratios=[1.1,1],
 left=.055,right=.98,top=.865,bottom=.12,wspace=.17,hspace=.26)
whole=fig.add_subplot(gr[0,:]);mid=fig.add_subplot(gr[1,0]);detail=fig.add_subplot(gr[1,1])
def paint(ax,g,fill,edge,lw=.5,alpha=1,style="-",z=2):
 for p in [g] if g.geom_type=="Polygon" else [x for x in g.geoms if x.geom_type=="Polygon"]:
  ax.add_patch(Patch(list(p.exterior.coords),fc=fill,ec=edge,lw=lw,alpha=alpha,ls=style,zorder=z))
for ax in (whole,mid,detail):
 ax.set_facecolor("#172d3d")
 for p in V.values():paint(ax,p,"#1e3b4e","#668f9b",.24,z=1)
 paint(ax,open_area,"#9d5fd7","#ddb0f4",.75,.67,z=4)
 for p in reserved.values():paint(ax,p,"none","#9aa2aa",.6,.7,(0,(3,5)),z=3)
 for band in wallbands:paint(ax,band,"#e9a455","#ffe0ae",.6,.93,z=8)
 for ring,c in (("I","#78b4c8"),("M","#75c4a6"),("T","#cfbb76")):
  for i in range(1,8):paint(ax,V[f"{ring}_A{i}_R12C"],"none",c,.9,z=10)
 for p in studies.values():paint(ax,p,"none","#ffe584",1.65,1,(0,(6,3)),z=12)
 ax.set_aspect("equal","box");ax.grid(alpha=.065)
 ax.set_xlabel("Global X, native units");ax.set_ylabel("Global Y, native units")
whole.set_xlim(-46600,28900);whole.set_ylim(-10400,10400)
mid.set_xlim(19300,28600);mid.set_ylim(-8200,8200)
detail.set_xlim(21300,24400);detail.set_ylim(-3000,3000)
whole.set_title("1. Protected cathedral floor plan — 7 original T bays only",loc="left",pad=10,fontsize=11.6,weight="bold")
mid.set_title("2. Seven real first-wall faces; ring reservations / planning outlines",loc="left",pad=10,fontsize=11,weight="bold")
detail.set_title("3. Provisional eight-site reference — not approved piers",loc="left",pad=10,fontsize=11,weight="bold")
fig.suptitle("F5ZP M02 PHASE D | MASONRY & SUPPORT RESERVATION PLAN\n"
"Continuous open sanctuary • first 320 wall • 7 + 7 + 7 original chevet bays • NO 14 trial subdivisions",
x=.055,y=.982,ha="left",fontsize=14.5,weight="bold")
fig.legend(handles=[
 Line2D([0],[0],color="#9d5fd7",lw=6,label="Protected continuous open cathedral"),
 Line2D([0],[0],color="#e9a455",lw=6,label="First 320 sanctuary wall bands"),
 Line2D([0],[0],color="#ffe584",lw=2,ls="--",label="8 unapproved support reservations"),
 Line2D([0],[0],color="#9aa2aa",lw=1,ls="--",label="R11 planning masonry boundaries")],
 loc="lower center",ncol=2,frameon=False,labelcolor="#e7eff4",bbox_to_anchor=(.5,.047),fontsize=9.7)
fig.text(.055,.012,"14 experimental outer lower vaults excluded entirely. Original 218 clear vaults and generators unchanged. No structural approval implied.",
color="#c0d1dc",fontsize=9.3)
png=O/"F5ZP_M02_PHASE_D_SOURCE_ONLY_MASONRY_PLAN_DARK.png"
fig.savefig(png,dpi=160,bbox_inches="tight");plt.close(fig)
with Image.open(png) as im:im.verify();print("IMAGE_VALIDATED",im.size)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[k] for k,p in sources.items())
(O/"M02_D_HANDOFF.md").write_text("""# F5ZP M02 Phase D — local 2D masonry / support reservation coordination
**User instruction:** Exclude all fourteen experimental outer subdivisions from floor plan. This package depicts exactly 7 R11 inner, 7 middle and **7 original third-ring** polygonal vaults. No source T polygon is subdivided or modified.

**Confirmed physical first wall:** Seven 320 native-unit perpendicular chancel-to-inner ring strips measured against R11. Main nave/crossing/choir/seven-facet chancel remains continuous open purple space. Q5 planning divider is not a physical wall.

**Source layers:** NAVE_MASONRY_R10, CHOIR_MASONRY_R10 and CHEVET_MASONRY_R10 have experimental reserved-masonry roles and may overlap this confirmed open interior. Therefore show as dashed planning outlines, NOT fully filled physical walls. Previously approved masonry outside this local interpretation is not revoked.

**Eight experimental support-site references:** Phase B R03's moderate option only, shown dashed for coordination, NOT promoted as physical piers. They clear the protected 218 vaults and open sanctuary and lie in original reserved areas. Actual wall bonding, responds, bearings and pier footprints remain unresolved.

**Verified:** technical reproducibility / hash regression, source chevet 7+7+7 identities, seven 320 wall strips, 197 inner-middle / 292 middle-third separators, no protected collision of eight trial references. Historical and structural validation not performed. Physical native-to-real-world conversion unresolved; F5ZL-C support schedule still missing. Working F5ZN-A inner/middle vault generator, F5ZK-C plan and Pass 6J not modified.

**Next:** Phase E 2D regression of full cathedral and clearly classified architectural interfaces, then review. No GitHub operations per user preference.

Reproduction: python3 M02_PHASE_D_MASONRY_RESERVATIONS_NO_OUTER_14.py
""")
shutil.copy2(png,Path.home()/"Downloads"/png.name)
archive=Path.home()/"Downloads"/"F5ZP_M02_PHASE_D_MASONRY_PLAN_NO_OUTER_14_LOCAL.zip"
with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
 z.write(Path(__file__),arcname=Path(__file__).name)
 for p in sorted(O.iterdir()):z.write(p,arcname=p.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print("PHASE_D_QA_PASS 7 wall faces 8 provisional support refs 14 trial outer EXCLUDED",archive)