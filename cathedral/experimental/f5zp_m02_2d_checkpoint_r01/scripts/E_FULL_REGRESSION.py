#!/usr/bin/env python3
"""M02 Phase E full-cathedral 2D regression, local only, source read-only.
Separates numerical geometry PASS from architecture/historical/structural review.
"""
from pathlib import Path
import json,csv,hashlib,zipfile,shutil,math
from collections import Counter
from shapely.geometry import shape,LineString,Polygon,Point,mapping
from shapely.ops import unary_union
from shapely.strtree import STRtree
from shapely.affinity import scale
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPLPolygon,Patch
from matplotlib.lines import Line2D
from PIL import Image
R=Path(__file__).resolve().parent
OUT=R/"M02_PHASE_E_FULL_CATHEDRAL_2D_REGRESSION_LOCAL";OUT.mkdir(exist_ok=True)
sources={
"R11":R/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
"R30":R/"R30_OPEN_INTERIOR_ARCHITECTURAL_INTENT_R01/SOURCE_GEOMETRY_EVIDENCE.json",
"R31":R/"R31_SEVEN_FACED_OPEN_INTERIOR_2D_EXPERIMENTAL/R31_OPEN_INTERIOR_1_TO_1.geojson",
"R32":R/"R32_CHANCEL_INNER_AMBULATORY_7_FACE_COORDINATION_EXPERIMENTAL/R32_NUMERICAL_QA.json",
"R33":R/"R33_CHANCEL_JUNCTIONS_LOCAL_EXPERIMENTAL/R33_QA.json",
"B3":R/"M02_PHASE_B_COMPLETION_R03_LOCAL_EXPERIMENTAL/M02_B_R03_FINAL_QA.json",
"C":R/"M02_PHASE_C_AMBULATORY_RHYTHM_LOCAL_EXPERIMENTAL/M02_C_NUMERICAL_QA.json",
"D":R/"M02_PHASE_D_MASONRY_SUPPORT_LOCAL/M02_D_NUMERICAL_QA.json",
"D_PLAN":R/"M02_PHASE_D_MASONRY_SUPPORT_LOCAL/M02_D_1TO1_SOURCE_FLOORPLAN_NO_FOURTEEN.geojson",
"D_STUDY":R/"M02_PHASE_D_MASONRY_SUPPORT_LOCAL/M02_D_EIGHT_PROVISIONAL_SUPPORT_REFERENCES.csv"
}
digests={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in sources.items()}
data={name:json.loads(p.read_text()) for name,p in sources.items() if p.suffix==".json" or p.suffix==".geojson"}
r11=data["R11"]["features"]
named={x["properties"]["id"]:shape(x["geometry"]) for x in r11}
C={x["properties"]["id"]:shape(x["geometry"]) for x in r11 if x["properties"].get("role")=="CLEAR"}
names=list(C);geoms=list(C.values())
assert len(C)==218 and len(named)==len(r11)
assert all(g.is_valid and not g.is_empty and g.geom_type=="Polygon" and g.area>0 for g in geoms)
rolecounts=Counter(x["properties"].get("role") for x in r11)
assert rolecounts["CLEAR"]==218 and rolecounts["RESERVED_MASONRY"]==3
assert data["R30"]["chancel_polygonal_face_count"]==7
assert data["B3"]["phase_B_completion_criteria"]["8_source_junctions_measured"]=="PASS"
assert data["D"]["experimental_outer_14_cells_excluded_from_floor_plan"] is True
assert data["D"]["source_chevet_7_7_7_retained"] is True
openplan=next(shape(x["geometry"]) for x in data["R31"]["features"]
 if x["properties"]["id"]=="NAVE_CROSSING_CHOIR_SEVEN_FACED_CHANCEL_OPEN_INTERIOR")
assert openplan.is_valid and openplan.geom_type=="Polygon" and len(openplan.interiors)==0
# Phase E full 218-cell collision sweep: exact intersections via STRtree, single pass.
tree=STRtree(geoms)
pairs=0;overlaps=[];zeroarea_contacts=0
for i,g in enumerate(geoms):
 for j in tree.query(g):
  j=int(j)
  if j<=i:continue
  pairs+=1
  h=geoms[j];inter=g.intersection(h)
  if inter.area>1e-5:overlaps.append({"vault_a":names[i],"vault_b":names[j],"overlap_native_sq":inter.area})
  elif inter.length>1e-6:zeroarea_contacts+=1
assert not overlaps,overlaps[:3]
# Large source polygons have EXPERIMENTAL RESERVED_MASONRY roles only;
# never use the giant R11 reserve as a filled physical wall.
reserved=[named[n] for n in ("NAVE_MASONRY_R10","CHOIR_MASONRY_R10","CHEVET_MASONRY_R10")]
reserved_overlap=[round(g.intersection(openplan).area,4) for g in reserved]
# Recovery source purple area must be continuous along centerline from west
# through seven-sided chancel boundary.
ch=named["CHEVET_MASONRY_R10"]
poly=list(ch.exterior.coords)
i=next(k for k,(x,y) in enumerate(poly) if 20238<x<20239 and y<0)
j=next(k for k,(x,y) in enumerate(poly) if 20238<x<20239 and y>0)
facet=poly[i:j+1]
assert len(facet)==8
assert all(math.dist(q,data["R30"]["chancel_inner_face_vertices"][k])<2e-5 for k,q in enumerate(facet))
assert all(openplan.boundary.distance(Point(p))<1e-5 for p in facet)
assert len([key for key in C if key.startswith("I_A") and key.endswith("_R12C")])==7
assert len([key for key in C if key.startswith("M_A") and key.endswith("_R12C")])==7
assert len([key for key in C if key.startswith("T_A") and key.endswith("_R12C")])==7
ringnames={ring:[f"{ring}_A{k}_R12C" for k in range(1,8)] for ring in "IMT"}
# Explicitly enforce no experimental 14-cell outer subdivisions in Phase D source
d_features=data["D_PLAN"]["features"]
dids=[f["properties"]["id"] for f in d_features]
assert len(d_features)==36 and len(set(dids))==36
assert all(not ("TRIAL" in s or "_L1" in s or "_L2" in s) for s in dids)
for ring in "IMT":
 assert all(dids.count(name)==1 for name in ringnames[ring])
 # Source geometry in delivered Phase D is EXACT; no simplifications
 for obj in d_features:
  if obj["properties"]["id"] in ringnames[ring]:
   assert shape(obj["geometry"]).equals_exact(C[obj["properties"]["id"]],1e-9)
d_role=Counter(f["properties"]["role"] for f in d_features)
assert d_role["UNCHANGED_R11_VAULT_PLANNING_POLYGON"]==21
assert d_role["USER_CONFIRMED_FIRST_WALL_MEASURED_BAND"]==7
assert d_role["B3_MODERATE_REFERENCE_ONLY_NOT_A_PIER"]==8
# Physical first wall measured centerline + every inner-face section.
wallbands=[]
for k,(start,end) in enumerate(zip(facet,facet[1:]),1):
 points=list(C[f"I_A{8-k}_R12C"].exterior.coords)[:-1]
 a=LineString([start,end]);b=LineString([points[3],points[0]])
 band=Polygon([start,end,points[0],points[3]])
 assert abs(a.distance(b)-320)<1e-6
 assert abs(a.length-b.length)<1e-6
 assert band.is_valid and band.difference(ch).area<1e-5
 assert band.intersection(openplan).area<1e-5
 wallbands.append(band)
ringrows=[]
for k in range(1,8):
 I,M,T=(C[f"{ring}_A{k}_R12C"] for ring in "IMT")
 dist1=I.distance(M);dist2=M.distance(T)
 assert abs(dist1-197)<1e-6 and abs(dist2-292)<1e-6
 vI,vM,vT=([p for p in x.exterior.coords][:-1] for x in (I,M,T))
 assert abs(LineString([vI[1],vI[2]]).length-LineString([vM[3],vM[0]]).length)<1e-6
 assert abs(LineString([vM[1],vM[2]]).length-LineString([vT[3],vT[0]]).length)<1e-6
 ringrows.append({"bay":k,"inner_to_middle_gap_native":round(dist1,6),
 "middle_to_third_gap_native":round(dist2,6),
 "source_7_7_7_retained":True,"outer_14_subdivisions":False})
adjacent=[]
for ring in "IMT":
 for k in range(1,7):
  a,b=(C[f"{ring}_A{x}_R12C"] for x in (k,k+1))
  g=a.distance(b)
  assert g>0
  adjacent.append({"ring":ring,"bay_left":k,"bay_right":k+1,
  "min_vault_to_vault_gap_native":round(g,6),
  "structural_arch_bearing_verified":False})
 assert all(abs(adjacent[-6+n]["min_vault_to_vault_gap_native"]-
                adjacent[-1-n]["min_vault_to_vault_gap_native"])<1e-4 for n in range(3))
# Exact north/south reflection of 21 chevet cells (except same-center bay A4).
for ring in "IMT":
 for k in range(1,4):
  reflected=scale(C[f"{ring}_A{k}_R12C"],xfact=1,yfact=-1,origin=(0,0))
  assert reflected.symmetric_difference(C[f"{ring}_A{8-k}_R12C"]).area<1e-4
 assert scale(C[f"{ring}_A4_R12C"],xfact=1,yfact=-1,origin=(0,0)).symmetric_difference(C[f"{ring}_A4_R12C"]).area<1e-4
# Full cathedral centerline: all saved main bays inside the open polygon,
# regardless of nonphysical planning separators in between.
main_names=[f"N{k}_MAIN" for k in range(2,10)]+["N10","Crossing","Q1"]+[f"Q{k}_MAIN" for k in range(2,6)]
assert len(main_names)==15
assert all(openplan.covers(C[name]) for name in main_names)
assert openplan.covers(C["N_North T1"]) and openplan.covers(C["S_North T1"])
west=min(C[n].bounds[0] for n in main_names)
sanctuary_wall_x=next(t for t in wallbands if t.intersects(LineString([(22000,0),(24500,0)]))).intersection(LineString([(22000,0),(24500,0)]))
assert abs(sanctuary_wall_x.length-320)<1e-6
assert abs(openplan.intersection(LineString([(west,0),(23081.90691295,0)])).length-(23081.90691295-west))<1e-4
# Eight moderate Phase B envelopes are only reference sites, not validated piers.
supports=[f for f in d_features if f["properties"]["role"]=="B3_MODERATE_REFERENCE_ONLY_NOT_A_PIER"]
assert len(supports)==8
study=[shape(f["geometry"]) for f in supports]
s_union=unary_union(study);clear_union=unary_union(geoms)
assert all(p.is_valid and p.area>1000 and p.distance(clear_union)>0.01 for p in study)
assert s_union.intersection(clear_union).area<1e-6
assert s_union.intersection(openplan).area<1e-6
assert s_union.difference(unary_union(reserved)).area<1e-6
# Finite direct wall LINE contact on all participating facets,
# not merely point touch at an inner wall junction.
supportrows=[]
for f,p in zip(supports,study):
 name=f["properties"]["id"].removeprefix("PROVISIONAL_BEARING_")
 index=int(name[1:]) if name.startswith("C") else (0 if name=="END_S" else 7)
 applicable=([LineString(facet[0:2])] if index==0 else
            ([LineString(facet[-2:])] if index==7 else
             [LineString(facet[index-1:index+1]),LineString(facet[index:index+2])]))
 lengths=[q.intersection(p.buffer(2e-4)).length for q in applicable]
 assert all(length>100 for length in lengths)
 supportrows.append({"junction":name,"source":"Phase B R03 moderate visual only",
 "protected_clearance_native":round(p.distance(clear_union),5),
 "finite_chancel_wall_contact_native":[round(x,5) for x in lengths],
 "physically_approved_pier":False})
# Protect against hidden source rewrites; all original files unchanged.
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digests[k] for k,p in sources.items())
def writecsv(name,rows):
 with (OUT/name).open("w",newline="") as out:
  w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
writecsv("M02_E_SEVEN_BAY_RING_AND_CLEARANCE_QA.csv",ringrows)
writecsv("M02_E_EIGHTEEN_SAME_RING_VAULT_GAPS.csv",adjacent)
writecsv("M02_E_EIGHT_PROVISIONAL_SUPPORT_CLEARANCES.csv",supportrows)
rows=[
 {"check":"218 source valid vault cells","result":"PASS","detail":"No empty/invalid/zero area polygons"},
 {"check":"R11 unique vault-overlap scan","result":"PASS","detail":f"{pairs} adjacent bounding box pairs checked; {len(overlaps)} positive-area overlaps, {zeroarea_contacts} line contacts"},
 {"check":"Continuous open nave/crossing/choir/chancel","result":"PASS","detail":"15 main vault clear cells plus crossing north/south arms covered by single continuous purple area"},
 {"check":"Exactly seven chancel inner facets","result":"PASS","detail":"8 source vertices, 7 true straight facets"},
 {"check":"320 first chancel-to-inner wall","result":"PASS","detail":"Seven source parallel strips, on-axis width 320"},
 {"check":"Original ambulatory rhythm","result":"PASS","detail":"7 I, 7 M, 7 T source polygons, 197 and 292 normal gaps"},
 {"check":"Explicit removal of 14 outer trial cells","result":"PASS","detail":"No trial outer cells or divider lines in Phase D source"},
 {"check":"Chevet mirrored footprint geometry","result":"PASS","detail":"7 source ring cells in all 3 rings reflect across central axis"},
 {"check":"Six+two candidate supports do not intrude","result":"PASS","detail":"8 provisional moderate construction envelope sites clear protected vaults and open interior"},
 {"check":"Large saved masonry reservations represent built walls","result":"NOT VALIDATED","detail":"R11 layers status EXPERIMENTAL; must not conflate with physical masonry"},
 {"check":"Architectural pier/arch bearing placement","result":"UNRESOLVED","detail":"Reference 8 sites not approved structural piers"},
 {"check":"Lower fourteen-vault architectural program","result":"EXCLUDED","detail":"Phase C trial remains separate; not part of floor plan"},
 {"check":"F5ZL-C support schedule","result":"MISSING","detail":"Not invented"},
 {"check":"Physical units conversion","result":"UNRESOLVED","detail":"native 1:1 coordinates; physical conversion not verified"},
 {"check":"Historical validation","result":"NOT ASSESSED","detail":"No plate-based approval from geometry alone"},
 {"check":"Structural validation","result":"NOT ASSESSED","detail":"No capacity, construction sequencing or masonry-bond assessment"}]
writecsv("M02_E_FULL_REGRESSION_CHECKLIST.csv",rows)
qa={
 "milestone":"F5ZP M02 Phase E full-cathedral 2D regression and architectural review",
 "status":"TECHNICAL + 2D GEOMETRIC REGRESSION PASS; ARCHITECTURAL PHYSICAL SUPPORT APPROVAL OPEN",
 "source_sha256":digests,"source_metadata":data["R11"].get("properties",{}),
 "protected_vault_polygons":218,"source_geometry_invalid":0,
 "candidate_bounding_box_pairs_tested":pairs,
 "positive_area_vault_overlaps":len(overlaps),
 "saved_vault_line_contacts":zeroarea_contacts,
 "main_vaults_inside_continuous_open_interior":len(main_names),
 "crossing_arms_inside_open_interior":True,
 "seven_sanctuary_inner_wall_faces":7,"wall_normal_separation":320,
 "ring_counts_source":{"I":7,"M":7,"T":7},
 "ring_gap_I_to_M":197,"ring_gap_M_to_T":292,
 "mirror_symmetry_all_source_chevet_cells":True,
 "Phase_D_delivered_source_features":len(d_features),
 "fourteen_experimental_outer_cells_in_delivery":0,
 "support_envelopes_reference_only":8,"approved_physical_piers":0,
 "support_overlap_original_clear":s_union.intersection(clear_union).area,
 "support_overlap_purple_open":s_union.intersection(openplan).area,
 "source_reserved_masonry_layer_overlap_purple":reserved_overlap,
 "interpretation":"Source R11 experimental masonry reservations overlap open intent and are NOT all physical walls.",
 "validation":{
  "technical":"PASS — source hashes, all exports and package integrity",
  "geometric":"PASS — 218-cell validity/nonoverlap, 7 chevet facets/320 first wall, 7+7+7 ring 197/292, 8 support-envelope no-collision",
  "architectural":"PARTIAL — confirmed open interior and first chancel wall, but physical pier/arch bearings not approved",
  "historical":"NOT ASSESSED",
  "structural":"NOT ASSESSED"},
 "regression_items":rows,
 "unresolved":[
  "M02 Phase F packaging and architectural approval required before promoting any new design",
  "Actual masonry bond and arch/rib bearing sections at 8 sites not validated",
  "Outer 14-vault paired subdivision excluded pending explicit later decision",
  "F5ZL-C support schedule missing",
  "Physical unit conversion unresolved",
  "Chevet window and low outer vault elevations not verified",
  "R11 overall status is experimental; tests do not promote it to approved authority"
 ]}
(OUT/"M02_E_NUMERICAL_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
# One review graphic with source-true full plan, east rings and border legend.
plt.rcParams.update({"text.color":"#edf4f8","axes.labelcolor":"#b9ced8",
 "xtick.color":"#adc6d3","ytick.color":"#adc6d3","axes.edgecolor":"#8099a7",
 "savefig.facecolor":"#0e1726","font.size":10})
fig=plt.figure(figsize=(19,11.6),facecolor="#0e1726")
gs=fig.add_gridspec(2,2,height_ratios=[.7,1.25],width_ratios=[1.15,1],left=.052,
 right=.98,top=.86,bottom=.13,wspace=.16,hspace=.29)
full=fig.add_subplot(gs[0,:]);east=fig.add_subplot(gs[1,0]);section=fig.add_subplot(gs[1,1])
def draw(ax,g,fc="none",ec="#688ca0",lw=.45,alpha=1,ls="-",z=2):
 ps=[g] if g.geom_type=="Polygon" else [q for q in g.geoms if q.geom_type=="Polygon"]
 for p in ps:ax.add_patch(MPLPolygon(list(p.exterior.coords),fc=fc,ec=ec,
  lw=lw,alpha=alpha,ls=ls,zorder=z))
for ax in (full,east,section):
 ax.set_facecolor("#192c3b")
 for p in geoms:draw(ax,p,"#193b4c","#658ba0",.27,z=1)
 draw(ax,openplan,"#9c63dc","#d2aaff",.75,.65,z=4)
 for p in reserved:draw(ax,p,"none","#959da5",.55,.74,(0,(4,5)),z=2)
 for band in wallbands:draw(ax,band,"#dd9c4e","#ffdfb0",.52,.89,z=7)
 for ring,col in (("I","#78b4cd"),("M","#7ecdb6"),("T","#dbca80")):
  for key in ringnames[ring]:draw(ax,C[key],"none",col,.95,z=10)
 for p in study:draw(ax,p,"none","#f3e177",1.4,1,(0,(6,4)),z=11)
 ax.set_aspect("equal","box");ax.grid(alpha=.065)
 ax.set_xlabel("X · native project units");ax.set_ylabel("Y · native project units")
full.set_xlim(-46700,29100);full.set_ylim(-10200,10200)
east.set_xlim(19100,28200);east.set_ylim(-8000,8000)
section.set_xlim(21300,24800);section.set_ylim(-3450,3450)
full.set_title("1 | Full 218-vault baseline: 2D collision regression PASS",loc="left",pad=11,fontsize=12,weight="bold")
east.set_title("2 | Exact 7+7+7 chevet, no 14-cell trial",loc="left",pad=11,fontsize=11.4,weight="bold")
section.set_title("3 | Seven chancel faces and 8 provisional supports",loc="left",pad=11,fontsize=11.1,weight="bold")
fig.suptitle("CATHEDRAL F5ZP | M02 PHASE E — FULL 2D REGRESSION & ARCHITECTURAL REVIEW\n"
 "218 vaults: no positive overlaps  ·  7-sided open chancel  ·  first 320 wall  ·  outer 14 experiments EXCLUDED",
 x=.052,y=.984,ha="left",fontsize=14.2,weight="bold")
fig.legend(handles=[
 Patch(fc="#9c63dc",label="Confirmed open nave → seven-sided chancel"),
 Patch(fc="#dd9c4e",label="First real 320 sanctuary wall"),
 Line2D([0],[0],color="#f3e177",lw=2,ls="--",label="Provisional eight-site support studies"),
 Line2D([0],[0],color="#959da5",lw=1,ls="--",label="Planning reservations, not necessarily walls"),
 Line2D([0],[0],color="#dbca80",lw=2,label="Original seven outer-ring bay footprints")],
 loc="lower center",ncol=3,frameon=False,bbox_to_anchor=(.5,.054),labelcolor="#e9f2f6",fontsize=9)
fig.text(.052,.011,
 "Technical + geometric validation PASS. Architectural support approval open. Historical + structural NOT ASSESSED. Source model remains EXPERIMENTAL.",
 color="#c3d5de",fontsize=9.25)
png=OUT/"F5ZP_M02_PHASE_E_FULL_CATHEDRAL_REGRESSION_DARK.png"
fig.savefig(png,dpi=165,bbox_inches="tight");plt.close(fig)
with Image.open(png) as im:im.verify();print("PNG_QA_VERIFIED",im.size)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digests[k] for k,p in sources.items())
(OUT/"M02_E_REVIEW_HANDOFF.md").write_text("""# M02 Phase E — Full cathedral 2D regression and architectural review

**Read-only baseline:** The locally stored R11 experimental plan has **218** original clear-vault polygons. They are valid, nonempty, and have **zero positive-area overlaps** in the full spatial-index pair audit. Distinguish source file technical baseline from approved architectural locks: R11 is marked EXPERIMENTAL and none of these tests promote it.

**User-established architectural intent:** One continuous open main nave, crossing with arms, choir and **seven-facet polygonal chancel**. There is no physical Q5 divider and no seven Q5 doorway cuts. The first physical wall is the 320-native-unit perpendicular chancel-to-inner ambulatory band; seven original faces checked. Large R11 named masonry layers are experimental reserved areas, not automatically physical structures.

**Chevet:** **7 original inner, 7 middle, 7 third-ring source vault polygons**, all retained. Normal source ring gaps are 197 and 292 native units throughout. Original neighboring vault spacings and north/south symmetry measured and checked. **No fourteen outer subdivision polygons or guides** are included in the Phase D plan or Phase E review, as expressly requested. The 14-cell Phase C trial remains separate and unapproved.

**Eight support sites:** Reference M02 Phase B R03 moderate wall-connected envelope at six corners and two end transitions ONLY as dashed unapproved construction studies. Source-protected vaults and continuous open interior untouched. Positive line contact to first wall geometrically checked. This does not prove structural masonry bonding, vaulted thrust, French Gothic historic pier sections or actual arch/rib bearings.

**Validation boundary:** Technical PASS, 2D geometry PASS. Architectural open-space/wall intent user-confirmed but actual bearings and pier design unapproved. Historical and structural NOT assessed. Missing F5ZL-C support schedule, actual physical units, outer vault elevations, windows and arches unresolved.

**Outputs:** One source-true dark PNG, complete 218-cell nonoverlap status summary, seven ring-gap CSV, 18 same-ring bay-gap CSV, eight provisional support clearance CSV, review checklist CSV, numerical QA and fully reproducible read-only script. No GitHub operations.

**Next:** M02 Phase F consolidated handoff, not automatic architectural approval.

Reproduce: python3 M02_PHASE_E_FULL_CATHEDRAL_REGRESSION_2D.py
""")
shutil.copy2(png,Path.home()/"Downloads"/png.name)
archive=Path.home()/"Downloads"/"F5ZP_M02_PHASE_E_FULL_CATHEDRAL_2D_REGRESSION_LOCAL.zip"
with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
 z.write(Path(__file__),arcname=Path(__file__).name)
 for file in sorted(OUT.iterdir()):z.write(file,arcname=file.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print("M02_PHASE_E_LOCAL_QA_PASS",len(C),"vault polygons",pairs,"candidate overlaps tested; positive overlaps",len(overlaps),"ZIP",archive)