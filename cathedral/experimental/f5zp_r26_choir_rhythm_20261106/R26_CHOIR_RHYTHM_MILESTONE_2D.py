#!/usr/bin/env python3
"""R26 milestone: 2D rectangular-vs-direct-taper choir rhythm, using existing R25 as truth.
No vaults, supports, approved visual baseline, or R25 sources are altered.
"""
from pathlib import Path
import json,csv,hashlib,math,zipfile,shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as ArtistPolygon,Rectangle,Patch
from matplotlib.lines import Line2D
from shapely.geometry import shape,box,mapping
from shapely.ops import unary_union
from PIL import Image
R=Path(__file__).resolve().parent
O=R/"R26_CHOIR_RHYTHM_MILESTONE_EXPERIMENTAL";O.mkdir(exist_ok=True)
P={
 "R11":R/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "R13":R/"R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson",
 "R23":R/"R23_Q1Q2_960_INTERFACE_EXPERIMENTAL/R23_960_INSET_INTERFACE_REFERENCE.geojson",
 "R25":R/"R25_Q2_Q5_CHOIR_RHYTHM_2D_EXPERIMENTAL/R25_Q2_Q5_GAPS_AND_TAPER_VISUALS.geojson",
 "R24_APPROVAL":R/"R25_Q2_Q5_CHOIR_RHYTHM_2D_EXPERIMENTAL/R24_APPROVAL_SCOPE_CARRIED_FORWARD.json",
}
SHA={key:hashlib.sha256(path.read_bytes()).hexdigest() for key,path in P.items()}
j={key:json.loads(path.read_text()) for key,path in P.items()}
approved=j["R24_APPROVAL"]
assert "Option A" in approved["reference"] and "VISUAL" in approved["scope"]
vault={f["properties"]["id"]:shape(f["geometry"]) for f in j["R11"]["features"] if f["properties"].get("role")=="CLEAR"}
mainmasonry=next(shape(f["geometry"]) for f in j["R11"]["features"] if f["properties"].get("id")=="CHOIR_MASONRY_R10")
masonry=[shape(f["geometry"]) for f in j["R11"]["features"] if "MASONRY" in f["properties"].get("id","")]
passages=[shape(f["geometry"]) for f in j["R13"]["features"]
 if f["properties"].get("variant")=="B_BALANCED" and f["properties"].get("layer")=="EXPERIMENTAL_PASSAGE_VOID"]
refs={f["properties"]["id"]:shape(f["geometry"]) for f in j["R23"]["features"]}
features=j["R25"]["features"]
assert len(vault)==218 and len(passages)==7 and len(features)==27
assert (vault["Q1"].bounds[2],vault["Q2_MAIN"].bounds[0])==(3925,5085)
assert all(refs[s+"_INSET_TAPER_960_TO_470"].is_valid for s in "NS")
clear=unary_union(list(vault.values()));retained=mainmasonry.difference(unary_union(passages))
gaps={(f["properties"]["junction"],f["properties"]["aisle"]):shape(f["geometry"])
   for f in features if "aisle" in f["properties"]}
direct={(f["properties"]["junction"],f["properties"]["side"]):shape(f["geometry"])
   for f in features if f["properties"].get("study")=="520_TO_270_STRAIGHT_2D_VISUAL_TAPER"}
assert len(gaps)==21 and len(direct)==6
records=[];candidates=[];rectangles={};cornerpieces={}
for n in (2,3,4):
 label=f"Q{n}–Q{n+1}"
 main=gaps[label,"MAIN"]
 assert main.bounds[2]-main.bounds[0]==520
 for side,sgn in (("N",1),("S",-1)):
  aisle=gaps[label,side+"_A1"]
  assert aisle.bounds[2]-aisle.bounds[0]==270
  assert (main.bounds[0]+main.bounds[2])/2==(aisle.bounds[0]+aisle.bounds[2])/2
  # full rectangular transverse reserve: same 520 width as main, 320 Y thick.
  if sgn==1:rectangle=box(main.bounds[0],2933,main.bounds[2],3253)
  else:rectangle=box(main.bounds[0],-3253,main.bounds[2],-2933)
  taper=direct[label,side]
  assert rectangle.is_valid and rectangle.covers(taper)
  assert abs(rectangle.area-520*320)<.0001
  assert abs(taper.area-((520+270)/2)*320)<.0001
  assert rectangle.difference(retained).area<.0001
  assert rectangle.intersection(clear).area<.0001
  assert taper.difference(retained).area<.0001
  assert taper.intersection(clear).area<.0001
  # No inlet void overlaps; entrance remains distinctly wider than these.
  assert rectangle.intersection(unary_union(passages)).area<.0001
  assert taper.boundary.intersection(main.boundary).length==520
  assert taper.boundary.intersection(aisle.boundary).length==270
  assert rectangle.boundary.intersection(main.boundary).length==520
  assert rectangle.boundary.intersection(aisle.boundary).length==270
  excess=rectangle.difference(taper)
  assert len(excess.geoms)==2 and abs(excess.area-40000)<.00001
  rectangles[label,side]=rectangle;cornerpieces[label,side]=excess
  angle=math.degrees(math.atan2((520-270)/2,320))
  entrance_angle=math.degrees(math.atan2((960-470)/2,320))
  row={"junction":label,"side":side,
    "main_x_start":main.bounds[0],"main_x_end":main.bounds[2],
    "aisle_x_start":aisle.bounds[0],"aisle_x_end":aisle.bounds[2],
    "reference_axis_x":(main.bounds[0]+main.bounds[2])/2,
    "main_depth_x":520,"aisle_depth_x":270,"transverse_band_y":320,
    "rectangular_facing_area":rectangle.area,"taper_facing_area":taper.area,
    "rectangular_extra_shoulder_area":excess.area,
    "rectangular_shoulders_each_x":125,
    "direct_taper_side_slope_angle_deg":round(angle,4),
    "entrance_R24_reference_side_slope_angle_deg":round(entrance_angle,4),
    "main_endpoint_contact_both_options":520,"aisle_endpoint_contact_both_options":270,
    "intrudes_vault_clear":False,"intrudes_entrance_void":False,
    "rectangle_has_sharp_90_degree_width_step":True,"direct_taper_has_single_oblique_face":True,
    "physical_geometry_changed":False}
  records.append(row)
  for variant,g in (("RECTANGULAR",rectangle),("DIRECT_TAPER",taper)):
   candidates.append({"type":"Feature","properties":{
      "junction":label,"side":side,"variant":variant,
      "approval_status":"EXPERIMENTAL VISUAL OPTION", "no_physical_masonry_change":True},
      "geometry":mapping(g)})
assert len(candidates)==12 and len(records)==6
assert sum(r["rectangular_extra_shoulder_area"] for r in records)==240000
# Consistent rhythm across three junctions, unchanged approved Q1–Q2 hierarchy.
assert len({r["direct_taper_side_slope_angle_deg"] for r in records})==1
assert all(r["entrance_R24_reference_side_slope_angle_deg"]>r["direct_taper_side_slope_angle_deg"] for r in records)
assert 960>520 and 470>270
with (O/"R26_JUNCTION_PROPORTION_MEASUREMENTS.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
(O/"R26_COMPARISON_FACING_GEOMETRY.geojson").write_text(json.dumps({
 "type":"FeatureCollection","properties":{"status":"TWO VISUAL OPTIONS — NO PHYSICAL MASONRY CHANGE",
 "source_sha256":SHA},"features":candidates},separators=(",",":"))+"\n")
qa={"milestone":"R26 — Q2–Q5 2D Choir Masonry Rhythm Comparison",
 "status":"TECHNICAL + GEOMETRIC CHECKS PASSED; R26 NEW FACING NOT YET APPROVED",
 "baseline":"R11, R13 Option B, R23 and R25 saved references",
 "R24_approved_scope":"Q1–Q2 Option A visual proportions and corner treatment ONLY",
 "protected_vault_polygon_count":218,"entrance_passages_unchanged":7,
 "original_R11_R13_R23_R25_files_unchanged":True,
 "Q1_Q2_actual_face_gap":1160,"Q1_Q2_approved_visual_depth":960,
 "Q1_Q2_reference_axis_X":4505,"six_aisle_entrances_depth_X":470,
 "straight_choir_junction_count":3,"studied_walls_north_and_south":6,
 "choir_main_depth":520,"choir_aisle_depth":270,"transverse_band_y":320,
 "rectangular_extra_shoulder_area_each_north_south":40000,
 "total_area_differentiating_the_visual_overlays":240000,
 "Q1_Q2_taper_angle_deg":round(math.degrees(math.atan2(245,320)),4),
 "internal_choir_taper_angle_deg":round(math.degrees(math.atan2(125,320)),4),
 "all_rectangular_and_tapered_faces_fit_reserved_masonry":True,
 "all_candidate_end_interfaces_continuous":True,
 "source_sha256":SHA,"measurement_rows":records,
 "validation":{
 "technical":"PASS: file hashes, generated GeoJSON/CSV/image, packaged checkpoint",
 "geometric":"PASS: overlays contained in retained masonry, zero vault/entrance overlaps, original 520/270 contacts maintained",
 "architectural":"Q1–Q2 R24 visual only approved; Q2–Q5 direct taper is RECOMMENDED, NOT APPROVED",
 "historical":"UNVERIFIED: no plate/profile evidence evaluated",
 "structural":"UNVERIFIED: neither visual profile is a physical pier/load path"},
 "design_interpretation":"Direct tapers preserve 520–270 rhythm with 21.34-degree side slopes versus 37.44-degree approved entrance taper; corners remain simpler than rectangular stepped shoulders.",
 "unresolved":["Q2–Q5 direct tapers require separate architectural approval",
 "No physical masonry removed by any proposed visual face",
 "Q5 chevet junction remains unstudied",
 "F5ZL-C support schedule missing."]}
(O/"R26_MILESTONE_NUMERICAL_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
# One integrated dark-mode review sheet, whole cathedral then TWO side-by-side
# alternative plans. Small inset at Q2/Q3 north provides legible actual corner
# shape differences while maintaining a full multi-junction overview.
plt.rcParams.update({"text.color":"#f0f3f8","axes.labelcolor":"#b3cedd",
 "xtick.color":"#a8c4d1","ytick.color":"#a8c4d1",
 "axes.edgecolor":"#819baa","savefig.facecolor":"#0a1420","font.size":10})
def render(ax,g,fc,ec="#6e8fa0",lw=.35,alpha=1,z=1):
 pieces=[g] if g.geom_type=="Polygon" else [q for q in getattr(g,"geoms",[]) if q.geom_type=="Polygon"]
 for p in pieces:
  ax.add_patch(ArtistPolygon(list(p.exterior.coords),facecolor=fc,edgecolor=ec,
   linewidth=lw,alpha=alpha,zorder=z))
  if fc!="none":
   for ring in p.interiors:
    ax.add_patch(ArtistPolygon(list(ring.coords),facecolor="#142535",edgecolor="none",zorder=z+.02))
def plot_base(ax,alt=None):
 ax.set_facecolor("#142535")
 for g in masonry:render(ax,g,"#4c5c6d",ec="#536777",lw=.18)
 for g in vault.values():render(ax,g,"#1c394a",ec="#7397a8",lw=.33,z=2)
 for g in passages:render(ax,g,"#217e9d",ec="#80d8ed",lw=.7,z=3)
 for side in "NS":
  for role in ("VISUAL_CORE_960","INSET_TAPER_960_TO_470"):
   render(ax,refs[side+"_"+role],"#b46fcd",ec="#f0ccff",lw=.5,z=6)
 if alt:
  for n in (2,3,4):
   label=f"Q{n}–Q{n+1}"
   for side in "NS":
    candidate=rectangles[label,side] if alt=="RECTANGULAR" else direct[label,side]
    render(ax,candidate,"#d4a454" if alt=="RECTANGULAR" else "#5fbc9e",
           ec="#ffe0ab" if alt=="RECTANGULAR" else "#bafee6",lw=.65,z=7)
 ax.set_aspect("equal","box")
 ax.grid(alpha=.07)
 ax.set_xlabel("Global X · native plan units");ax.set_ylabel("Global Y · native plan units")
fig=plt.figure(figsize=(20,12.3),facecolor="#0a1420")
gs=fig.add_gridspec(2,2,height_ratios=[.82,1.2],left=.048,right=.985,
 top=.875,bottom=.115,hspace=.26,wspace=.15)
whole=fig.add_subplot(gs[0,:]);rect=fig.add_subplot(gs[1,0]);taper=fig.add_subplot(gs[1,1])
plot_base(whole)
plot_base(rect,"RECTANGULAR")
plot_base(taper,"DIRECT_TAPER")
bx=unary_union(list(vault.values())).bounds
whole.set_xlim(bx[0]-1800,bx[2]+1800);whole.set_ylim(bx[1]-1650,bx[3]+1650)
whole.add_patch(Rectangle((8250,-7750),9800,15500,fill=False,ec="#fba4dc",lw=2.1,zorder=15))
whole.annotate("Q2–Q5 • same vaults, two visual approaches",xy=(18050,7900),
 xytext=(12500,10500),color="#fface0",fontsize=11,weight="bold",
 arrowprops=dict(arrowstyle="->",color="#fface0"))
for ax in (rect,taper):
 ax.set_xlim(3800,20250);ax.set_ylim(-8050,8050)
 ax.axhline(2933,color="#ffd996",ls=":",lw=.55,alpha=.4,zorder=12)
for i,x in zip((2,3,4),(9089,13065,16753)):
 for ax in (rect,taper):
  ax.text(x,7950,f"Q{i}–Q{i+1}",ha="center",va="top",color="#eff7fc",
          fontsize=10.5,weight="bold",zorder=20)
# Add source-coordinate corner zoom directly inside each comparative panel.
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
for ax,style in ((rect,"RECTANGULAR"),(taper,"DIRECT_TAPER")):
 inset=inset_axes(ax,width="40%",height="42%",loc="upper left",
   bbox_to_anchor=(0.03,.03,.95,.94),bbox_transform=ax.transAxes,borderpad=0)
 inset.set_facecolor("#112636")
 for g in (vault["Q2_MAIN"],vault["Q3_MAIN"],vault["Q2_N_A1_2"],vault["Q3_N_A1_1"]):
  render(inset,g,"#1b3949",ec="#779eaf",lw=1,z=2)
 p=rectangles["Q2–Q3","N"] if style=="RECTANGULAR" else direct["Q2–Q3","N"]
 render(inset,p,"#d4a454" if style=="RECTANGULAR" else "#5fbc9e",
   ec="#ffe0ab" if style=="RECTANGULAR" else "#bafee6",lw=1.4,z=8)
 inset.set_xlim(8550,9600);inset.set_ylim(2480,3600)
 inset.set_xticks([]);inset.set_yticks([])
 inset.text(9060,3375,"520 → 270",ha="center",color="#ffffff",
    fontsize=8.2,weight="bold",
    bbox={"facecolor":"#1a2e3e","edgecolor":"#8aa6b9","pad":2})
whole.set_title("1  |  Full R11 cathedral • Q2–Q5 highlighted",loc="left",pad=8,fontsize=12,weight="bold")
rect.set_title("2  |  Rectangular masonry faces: 125-unit shoulders",loc="left",pad=9,fontsize=11.6,weight="bold")
taper.set_title("3  |  Direct tapers: one clean diagonal per side",loc="left",pad=9,fontsize=11.6,weight="bold")
fig.suptitle("F5ZP R26 | CHOIR MASONRY RHYTHM — 2D MILESTONE\n"
 "R24 entrance visually approved  •  Q2–Q5 new faces compared  •  underlying geometry untouched",
 x=.048,y=.981,ha="left",fontsize=16.5,weight="bold")
fig.legend(handles=[Patch(facecolor="#1c394a",ec="#7397a8",label="Protected vault"),
 Patch(facecolor="#217e9d",label="Original entrance openings"),
 Patch(facecolor="#b46fcd",label="R24 approved entrance taper"),
 Patch(facecolor="#d4a454",label="Rectangular Q2–Q5 alternative"),
 Patch(facecolor="#5fbc9e",label="Direct Q2–Q5 taper trial")],
 loc="lower center",ncol=3,frameon=False,bbox_to_anchor=(.5,.05),
 labelcolor="#edf3f8",fontsize=9.4)
fig.text(.048,.014,"Measured in native project units, not meters. Visual treatments only; no masonry capacity, arch height, or historical verification implied.",
 fontsize=9.4,color="#b8cbd5")
png=O/"F5ZP_R26_CHOIR_MILESTONE_FULL_PLAN_DARK.png"
fig.savefig(png,dpi=175,bbox_inches="tight")
plt.close(fig)
with Image.open(png) as img:img.verify();print("REVIEW_IMAGE_VALIDATED",img.size)
assert all(hashlib.sha256(path.read_bytes()).hexdigest()==SHA[key] for key,path in P.items())
(O/"README_HANDOFF.md").write_text("""# R26 — Q2–Q5 choir masonry rhythm comparison, 2D milestone

**Approved baseline distinction:** User approved R24 Option A at Q1–Q2 as a *visual architectural corner treatment*. Neither its 960 visual span nor tapered facing changes the true 1160 vault-face separation, physical pier, arch or structure.

**New study:** Read-only R25 junction geometry at Q2–Q3, Q3–Q4, Q4–Q5. At each junction the main-vault face gap is 520 native units and all north/south A1–A3 aisle face gaps are 270. The original transverse band is 320 in Y.

Two north/south treatments at all three junctions: (1) full rectangular 520×320 facing with 125-wide right-angled shoulders where it meets A1, and (2) R25 direct trapezoid taper 520→270 over 320; slope angle ~21.34° from transverse centerline. Entrance Q1–Q2 direct visual taper 960→470 over 320 has ~37.44° side slope, so its emphasis stays stronger.

Both treatments fit existing reserved masonry and maintain 520 and 270 face contacts. Each rectangular visual annotation contains 40,000 more native square units of area than the trapezoidal study per side, but this is **a visual overlay comparison, not material removed or structural masonry reduced**. Across 6 side treatments the difference is 240,000 square units.

**Recommendation:** Retain R25 direct taper at Q2–Q5 as the *preferred experimental* visual option. Its single oblique faces are more consistent with the approved restrained Q1–Q2 treatment, while the 520/270 scale remains subordinate. No R26 architectural approval inferred.

**Validation:** Automated source hash regression, geometric coverage and clear-space/doorway intersections, 520/270 contact continuity, symmetry and consistency checks. Historical and structural validations not performed. Physical unit conversion and F5ZL-C schedule unresolved. Q5-to-chevet remains future work.

**Artifacts:** one dark-mode PNG (whole cathedral and side-by-side comparison), GeoJSON options, CSV measurements, JSON QA, generator and this handoff. Reproduce in the unchanged R12C workspace:
python3 R26_CHOIR_RHYTHM_MILESTONE_2D.py
""")
shutil.copy2(png,Path.home()/"Downloads"/png.name)
outzip=Path.home()/"Downloads"/"F5ZP_R26_CHOIR_RHYTHM_2D_MILESTONE_EXPERIMENTAL.zip"
with zipfile.ZipFile(outzip,"w",compression=zipfile.ZIP_DEFLATED) as z:
 z.write(Path(__file__),arcname=Path(__file__).name)
 for path in sorted(O.iterdir()):z.write(path,arcname=path.name)
with zipfile.ZipFile(outzip) as z:assert z.testzip() is None
print("R26_MILESTONE_PASS",len(records),"measurements",len(candidates),"candidates",outzip)