#!/usr/bin/env python3
"""R27 — Q5 straight choir to seven-bay chevet, native-unit 2D geometric interface audit.
Read-only sources, no new or approved physical masonry, vault or openings.
"""
from pathlib import Path
import json,csv,hashlib,zipfile,shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as AP,Patch,Rectangle
from matplotlib.lines import Line2D
from shapely.geometry import shape,Polygon,box,LineString,Point,mapping
from shapely.ops import unary_union
from shapely.affinity import scale
from PIL import Image

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"R27_Q5_CHEVET_INTERFACE_2D_EXPERIMENTAL";OUT.mkdir(exist_ok=True)
SRC={
 "R11":ROOT/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "R13":ROOT/"R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson",
 "R26":ROOT/"R26_CHOIR_RHYTHM_MILESTONE_EXPERIMENTAL/R26_MILESTONE_NUMERICAL_QA.json",
 "R24_APPROVAL":ROOT/"R25_Q2_Q5_CHOIR_RHYTHM_2D_EXPERIMENTAL/R24_APPROVAL_SCOPE_CARRIED_FORWARD.json"
}
hashes={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in SRC.items()}
src=json.loads(SRC["R11"].read_text())["features"]
r13=json.loads(SRC["R13"].read_text())["features"]
qa26=json.loads(SRC["R26"].read_text())
approval=json.loads(SRC["R24_APPROVAL"].read_text())
assert len(src)>250 and qa26["choir_main_depth"]==520 and "Option A" in approval["reference"]
G={f["properties"]["id"]:shape(f["geometry"]) for f in src}
vault={f["properties"]["id"]:shape(f["geometry"]) for f in src if f["properties"].get("role")=="CLEAR"}
assert len(vault)==218
C=G["CHOIR_MASONRY_R10"];H=G["CHEVET_MASONRY_R10"]
sol=unary_union([C,H]);vu=unary_union(list(vault.values()))
voids=[shape(f["geometry"]) for f in r13 if f["properties"].get("variant")=="B_BALANCED" and f["properties"].get("layer")=="EXPERIMENTAL_PASSAGE_VOID"]
assert len(voids)==7
V=unary_union(voids)
assert sol.geom_type=="Polygon" and C.intersection(H).area==0
seam=C.boundary.intersection(H.boundary)
segments=sorted((g for g in seam.geoms if g.length>.001),key=lambda x:x.bounds[1])
assert len(segments)==2 and abs(seam.length-9699.259396401709)<.0001
assert abs(segments[0].length-segments[1].length)<1e-6
assert abs(segments[0].bounds[1]+7782.6296982)<.001 and abs(segments[-1].bounds[3]-7782.6296982)<.001
# Recover actual crossing surfaces from saved polygon edges; do not invent
# radial tangent or turn a measured quadrilateral into a uniform rectangle.
rows=[];corridors={};feats=[]
for rank,prefix in (("A1","I"),("A2","M"),("A3","T")):
 for side,idx in (("N",1),("S",7)):
  q=vault[f"Q5_{side}_{rank}_2"]
  ch=vault[f"{prefix}_A{idx}_R12C"]
  assert q.geom_type==ch.geom_type=="Polygon"
  east=q.bounds[2]
  pts=list(ch.exterior.coords)[:-1]
  westedge=sorted(sorted(pts,key=lambda t:t[0])[:2],key=lambda t:t[1])
  assert len(westedge)==2 and len(set(westedge))==2
  westxlo,ylow=westedge[0];westxhi,yhigh=westedge[1]
  qpts=list(q.exterior.coords)[:-1]
  qedge=sorted(sorted(qpts,key=lambda t:-t[0])[:2],key=lambda t:t[1])
  assert len(qedge)==2 and qedge[0][0]==qedge[1][0]==east
  qlow,qhigh=qedge[0][1],qedge[1][1]
  g=Polygon([(east,qlow),(east,qhigh),westedge[1],westedge[0]])
  assert g.is_valid and g.area>0
  assert g.difference(sol).area<1e-6,(rank,side,"unreserved",g.difference(sol).area)
  assert g.intersection(vu).area<1e-6
  assert g.intersection(V).area<1e-6
  w=g.boundary.intersection(q.boundary).length
  e=g.boundary.intersection(ch.boundary).length
  assert abs(w-(qhigh-qlow))<1e-6
  assert abs(e-LineString(westedge).length)<1e-6
  c_area=g.intersection(C).area;h_area=g.intersection(H).area
  assert c_area>0 and h_area>0 and abs(g.area-c_area-h_area)<1e-5
  assert east==20053
  assert min(westxlo,westxhi)>20213
  # Original chevet construction has a slightly sloped west boundary; record it.
  corridor_dist=min(ch.distance(q),abs(westxlo-east))
  r={
   "rank":rank,"side":side,"Q5_vault":f"Q5_{side}_{rank}_2",
   "chevet_vault":f"{prefix}_A{idx}_R12C",
   "Q5_face_X":east,"chevet_lower_face_X":westxlo,"chevet_upper_face_X":westxhi,
   "Q5_face_y_min":qlow,"Q5_face_y_max":qhigh,
   "chevet_face_y_min":ylow,"chevet_face_y_max":yhigh,
   "min_clear_polygon_distance":round(q.distance(ch),6),
   "min_connector_EW_width":round(min(westxlo,westxhi)-east,6),
   "max_connector_EW_width":round(max(westxlo,westxhi)-east,6),
   "contact_Q5_vault_boundary":w,"contact_chevet_vault_boundary":e,
   "existing_choir_masonry_overlap_area":round(c_area,6),
   "existing_chevet_masonry_overlap_area":round(h_area,6),
   "bridge_plan_area":round(g.area,6),
   "original_vault_overlap":0,"original_passage_overlap":0,
   "actual_open_passage_created":False,
   "status":"READONLY_MASONRY_INTERFACE_NOT_APPROVED_PASSAGE"}
  rows.append(r);corridors[rank,side]=g
  feats.append({"type":"Feature","properties":r,"geometry":mapping(g)})
assert len(rows)==6
for rank in ("A1","A2","A3"):
 n=corridors[rank,"N"];s=corridors[rank,"S"]
 assert n.symmetric_difference(scale(s,xfact=1,yfact=-1,origin=(0,0))).area<1e-5
assert max(r["min_connector_EW_width"] for r in rows if r["rank"]=="A1")<min(r["min_connector_EW_width"] for r in rows if r["rank"]=="A2")
assert max(r["min_connector_EW_width"] for r in rows if r["rank"]=="A2")<min(r["min_connector_EW_width"] for r in rows if r["rank"]=="A3")
# Key unresolved architectural interface. The full 320-thick choir terminal
# masonry band is not pierced by an actual recorded R11/R13 through-passage.
AXIAL=box(19893,-2933,20213,2933)
assert AXIAL.difference(C).area<1e-6
assert AXIAL.intersection(vu).area==0
assert AXIAL.intersection(V).area==0
assert (vault["Q5_MAIN"].bounds[2],AXIAL.bounds[2])==(19893,20213)
seam_center=seam.intersection(LineString([(20213,-2933),(20213,2933)]))
assert seam_center.length==0
# Axial chevet inner ring edge begins far to east of saved choir terminal face.
centerline=LineString([(20213,0),(24500,0)])
axial_chev=H.intersection(centerline)
assert not axial_chev.is_empty
outer_x=axial_chev.bounds[0]
assert abs(outer_x-23081.9)<.2
unclassified_span=outer_x-20213
assert unclassified_span>2800
feats.append({"type":"Feature","properties":{"name":"Q5_CENTER_AXIAL_TERMINAL_BAND",
 "status":"EXISTING_SOLID_MASONRY; NO_RECORDED_THROUGH_PASSAGE", "physical_width_X":320,
 "is_proposed_opening":False},"geometry":mapping(AXIAL)})
(OUT/"R27_ACTUAL_RESERVED_MASONRY_CONNECTORS.geojson").write_text(json.dumps({
 "type":"FeatureCollection","properties":{"status":"Existing plan audit only; not approved piers/openings",
 "source_sha256":hashes},"features":feats},separators=(",",":"))+"\n")
with (OUT/"R27_Q5_CHEVET_FACE_CONTACTS.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
qa={
 "status":"R27 TECHNICAL AND 2D GEOMETRIC CHECKS PASS; AXIAL AND OPEN-PASSAGE ARCHITECTURE UNRESOLVED",
 "source_sha256":hashes,"source_files_unchanged":True,
 "approved_baseline_protected":True,
 "original_chevet_inner_bay_count_in_R11":7,
 "original_chevet_middle_bay_count_in_R11":7,
 "original_chevet_T_ring_bay_count_in_R11":7,
 "note":"R11 currently carries seven T-ring polygon records; does NOT certify completion of separately discussed paired 14-vault lower outer rhythm.",
 "chevet_bay_identity_and_geometry_unchanged":True,
 "choir_and_chevet_masonry_union_connected":True,
 "geometric_source_masonry_shared_face_length":round(seam.length,6),
 "source_masonry_common_seam_y_ranges":[[round(g.bounds[1],6),round(g.bounds[3],6)] for g in segments],
 "number_of_vault_pair_2D_reserved_masonry_bridges":6,
 "all_six_bridge_regions_inside_existing_union_masonry":True,
 "each_bridge_touches_original_Q5_and_corresponding_chevet_vault_face":True,
 "all_protected_vault_spaces_and_existing_R13_passages_unchanged":True,
 "main_Q5_east_vault_face_X":19893,"choir_masonry_terminal_east_X":20213,
 "central_terminal_masonry_depth_X":320,
 "unpierced_centerline_masonry_band_between_X":[19893,20213],
 "chevet_masonry_continues_on_centerline_from_X":round(outer_x,6),
 "axial_unclassified_centerline_between_masonry_regions":round(unclassified_span,6),
 "no_axial_opening_defined":True,
 "A1_A2_A3_actual_open_passages_not_yet_defined":True,
 "structural_support_capacity_verified":False,
 "validation":{"technical":"PASS: original inputs hashed; output ZIP checked; reproducible generated figures",
 "geometric":"PASS: six 2D face connectors non-overlapping with clear vaults and inside reserved masonry; seam measured",
 "architectural":"INCOMPLETE: six connections are solid masonry reservations, not designed passages; main axial opening is unpierced",
 "historical":"NOT ASSESSED: no new vault or source plate interpretation",
 "structural":"NOT ASSESSED: no live supports, thrust or bearing capacity"},
 "open_items":["The actual axial passage through existing 320-thick terminal band requires separate design approval.",
 "Six side masonry connectors would require proportioned architectural openings and receiving geometry before being described as passages.",
 "F5ZL-C support schedule remains missing.",
 "Outer paired 14-vault rhythm is not established by seven T-ring polygons in the current saved R11 source.",
 "Q5–chevet ring geometry and approved source authority have not been modified."]}
(OUT/"R27_NUMERICAL_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
# ONE DARK-MODE image with whole plan, outer junction, and central axial condition.
plt.rcParams.update({"text.color":"#eef4fa","axes.labelcolor":"#bfd2dc",
 "xtick.color":"#adc6d2","ytick.color":"#adc6d2",
 "axes.edgecolor":"#7996a8","font.size":10,"savefig.facecolor":"#0a1521"})
def draw(ax,g,color,edge="#7693a4",lw=.32,alpha=1,z=1):
 poly=[g] if g.geom_type=="Polygon" else [p for p in getattr(g,"geoms",[]) if p.geom_type=="Polygon"]
 for p in poly:
  ax.add_patch(AP(list(p.exterior.coords),facecolor=color,edgecolor=edge,
    linewidth=lw,alpha=alpha,zorder=z))
  if color!="none":
   for ring in p.interiors:
    ax.add_patch(AP(list(ring.coords),facecolor="#142635",edgecolor="none",zorder=z+.03))
def base(ax):
 ax.set_facecolor("#142635")
 for g in (C,H):draw(ax,g,"#4e6070",lw=.3,z=1)
 for f in vault.values():draw(ax,f,"#1a3c4a",edge="#7196a5",lw=.33,z=2)
 for g in voids:draw(ax,g,"#2b82a3",edge="#7bdafa",lw=.6,z=3)
 for (rank,side),g in corridors.items():
  colors={"A1":"#58d4c9","A2":"#82c592","A3":"#b6b06c"}
  draw(ax,g,colors[rank],edge="#dffadf",lw=.55,alpha=.95,z=7)
 draw(ax,AXIAL,"#db7297",edge="#ffbdd6",lw=.65,alpha=.9,z=8)
 ax.set_aspect("equal","box");ax.grid(alpha=.075)
 ax.set_xlabel("Global X • native units");ax.set_ylabel("Global Y • native units")
fig=plt.figure(figsize=(19,12.5),facecolor="#0a1521")
grid=fig.add_gridspec(2,2,height_ratios=[.85,1.2],width_ratios=[1.27,1],
 left=.055,right=.985,top=.865,bottom=.125,wspace=.15,hspace=.23)
full=fig.add_subplot(grid[0,:]);junction=fig.add_subplot(grid[1,0]);axial=fig.add_subplot(grid[1,1])
for a in (full,junction,axial):base(a)
bb=unary_union(list(vault.values())).bounds
full.set_xlim(bb[0]-1500,bb[2]+1500);full.set_ylim(bb[1]-1200,bb[3]+1200)
full.add_patch(Rectangle((18250,-7950),6100,15900,fill=False,ec="#ff9cdd",lw=2.3,zorder=20))
full.annotate("Q5-to-chevet junction → details",xy=(24100,8100),xytext=(15400,10400),color="#ff9cdd",
 fontsize=11,weight="bold",arrowprops=dict(arrowstyle="->",color="#ff9cdd"))
junction.set_xlim(18250,24200);junction.set_ylim(-8000,8000)
for side,sign in (("N",1),("S",-1)):
 for rank,index in (("A1","I"),("A2","M"),("A3","T")):
  g=corridors[rank,side];mid=g.centroid
  junction.text(mid.x,mid.y,rank,color="#0d2730",ha="center",va="center",
      fontsize=9,weight="bold",zorder=15)
# Highlight the genuine material seam and axial center not joined across seam.
junction.axvline(20213,color="#f0d88e",ls=":",lw=.95,zorder=10)
junction.text(20350,7700,"20213: saved masonry seam",color="#ffe3a8",fontsize=8.5,rotation=0)
axial.set_xlim(19450,24700);axial.set_ylim(-3150,3150)
axial.axvline(19893,color="#fc9ec6",ls=":",lw=1.15,zorder=13)
axial.axvline(20213,color="#fc9ec6",ls=":",lw=1.15,zorder=13)
axial.annotate("",xy=(20213,0),xytext=(19893,0),arrowprops=dict(arrowstyle="<->",color="#ffd9e6",lw=2),zorder=17)
axial.text(20053,410,"320 solid",color="#ffe2eb",ha="center",fontsize=10,weight="bold",zorder=17)
axial.annotate("Axial passage NOT defined",xy=(20213,0),xytext=(21000,2350),
 color="#ffb5ce",fontsize=10,weight="bold",
 arrowprops={"arrowstyle":"->","color":"#ffb5ce"},zorder=18)
axial.annotate("",xy=(outer_x,0),xytext=(20213,0),
 arrowprops={"arrowstyle":"<->","color":"#83c8df","lw":1.25,"linestyle":"dashed"},zorder=16)
axial.text((20213+outer_x)/2,-500,"Unresolved axial approach",color="#90d6ec",ha="center",fontsize=9,zorder=18)
full.set_title("1 · Full cathedral, Q5-to-chevet marked",loc="left",pad=9,fontsize=12,weight="bold")
junction.set_title("2 · Six side interfaces: solid masonry contacts, not doorways",loc="left",pad=9,fontsize=11.2,weight="bold")
axial.set_title("3 · Central sanctuary: terminal masonry remains unpierced",loc="left",pad=9,fontsize=10.9,weight="bold")
fig.suptitle("F5ZP R27 | STRAIGHT CHOIR → CURVED CHEVET — 2D JUNCTION AUDIT\n"
 "Protected R11 seven-bay identities intact • aisle interfaces verified • axial passage unresolved",
 x=.055,y=.98,ha="left",fontsize=15.6,weight="bold")
fig.legend(handles=[Patch(facecolor="#1a3c4a",edgecolor="#7196a5",label="Protected clear vault"),
 Patch(facecolor="#58d4c9",label="Q5 → inner I interface"),
 Patch(facecolor="#82c592",label="Q5 → middle M interface"),
 Patch(facecolor="#b6b06c",label="Q5 → outer T interface"),
 Patch(facecolor="#db7297",label="Unpierced 320-deep axial masonry")],
 loc="lower center",ncol=3,frameon=False,bbox_to_anchor=(.5,.052),
 fontsize=9.3,labelcolor="#eaf2f7")
fig.text(.055,.013,"2D masonry continuity validated. No passage geometry, support load path, historical authenticity, or physical unit conversion is inferred.",color="#afc8d6",fontsize=9.5)
png=OUT/"F5ZP_R27_FULL_PLAN_Q5_CHEVET_JUNCTION_DARK.png"
fig.savefig(png,dpi=170,bbox_inches="tight");plt.close(fig)
with Image.open(png) as im:print("PNG_VERIFIED",im.size);im.verify()
assert all(hashlib.sha256(v.read_bytes()).hexdigest()==hashes[k] for k,v in SRC.items())
(OUT/"README_HANDOFF.md").write_text("""# F5ZP R27 — Q5 to chevet transition / architectural junction audit

**Baseline:** Read-only R11 coordinated 2D; R13-B Q1 entrance, R26 choir rhythm work, R24 approved Q1 visual Option A. All source file SHA256 values appear in JSON QA. Seven chevet bay identities retained exactly, no new vault shapes; existing saved R11 has 7 I, 7 M and 7 T polygon records. This does not certify the independently discussed 14 outer low-vault rhythm.

## Findings
- Choir masonry and chevet masonry share exactly 9699.2594 native units of edge along X20213, split into north and south seam segments Y±2933..±7782.63, no shared masonry edge on axial Y0.
- Six candidate **solid masonry connection polygons** between the actual Q5 A1/A2/A3 east faces (X20053) and actual sloping west faces of I_A1/A7, M_A1/A7 and T_A1/A7. All six overlap both original masonry polygons, touch both real clear-vault boundaries with positive line lengths, and avoid every clear-vault polygon. North and south are mirror matches.
- Measured closest face-to-face distances approximately A1=224.886, A2=259.128, A3=305.452 native units, increasing outward. Exact measurements in CSV.
- **Unfinished axial entrance:** Q5_MAIN clear vault ends at X19893. The intervening x19893..20213 is a **solid 320-wide masonry terminal band**, with no recorded door opening at the centerline. At y0 the chevet masonry ring begins around X23081.91; the intervening axial approach is not a designed passage or verified clearance. Need architectural design and approval before changing this band.
- The six side connectors are retained masonry **for future receiving/opening studies**, not already open passages or approved piers.

## Validation levels
Technical: source hashes, reproducible generator, PNG and ZIP integrity PASS.
Geometric: existing reserved masonry continuity, actual vault-face edge contacts, symmetry and zero collisions PASS.
Architectural: INCOMPLETE (no designed Q5-to-chevet axial or side openings).
Historical: no new plate-supported interpretation.
Structural: no load path, thrust, masonry thickness adequacy or bearing proof.
F5ZL-C schedule absent. Nothing from R24/R26/R27 promoted to new physical/locked architecture.

## Reproduction
Run: python3 R27_Q5_CHEVET_JUNCTION_2D.py (in the R12C experimental workspace).
""")
shutil.copy2(png,Path.home()/"Downloads"/png.name)
zipf=Path.home()/"Downloads"/"F5ZP_R27_Q5_CHEVET_JUNCTION_2D_EXPERIMENTAL.zip"
with zipfile.ZipFile(zipf,"w",compression=zipfile.ZIP_DEFLATED) as z:
 z.write(Path(__file__),arcname=Path(__file__).name)
 for p in sorted(OUT.iterdir()):z.write(p,arcname=p.name)
with zipfile.ZipFile(zipf) as z:assert z.testzip() is None
print("R27 VALIDATED",len(rows),"side connections, 320 center solid, package",zipf)