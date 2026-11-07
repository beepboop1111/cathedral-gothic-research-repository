#!/usr/bin/env python3
"""R19: 2D schematic proportion comparison using R18 references. No changes to source geometry."""
from pathlib import Path
import json,csv,hashlib,zipfile,shutil,xml.etree.ElementTree as ET
from shapely.geometry import shape,box,mapping
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Poly,Rectangle,Patch
from matplotlib.lines import Line2D
from PIL import Image
R=Path(__file__).resolve().parent;O=R/'R19_MASONRY_PROPORTIONS_EXPERIMENTAL';O.mkdir(exist_ok=True)
sources={'R11':R/'R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson',
'R13':R/'R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson',
'R18':R/'R18_Q1_Q2_COORDINATED_JUNCTION_EXPERIMENTAL/R18_CONSOLIDATED_2D_JUNCTION_REFERENCES.geojson'}
dig={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in sources.items()}
data={k:json.loads(p.read_text())['features'] for k,p in sources.items()}
clear={f['properties']['id']:shape(f['geometry']) for f in data['R11'] if f['properties'].get('role')=='CLEAR'}
solid=next(shape(f['geometry']) for f in data['R11'] if f['properties'].get('id')=='CHOIR_MASONRY_R10')
openings=[shape(f['geometry']) for f in data['R13'] if f['properties'].get('variant')=='B_BALANCED' and f['properties'].get('layer')=='EXPERIMENTAL_PASSAGE_VOID']
assert len(openings)==7 and len(clear)==218
void=unary_union(openings);available=solid.difference(void)
ref={f['properties']['id']:shape(f['geometry']) for f in data['R18'] if f['properties'].get('status')=='EXISTING_R16_R17_REVIEW_REFERENCE'}
assert len(ref)==22
base=unary_union(list(ref.values()))
assert base.difference(available).area<1e-5
# Study A: uniformly colored existing R18 reserved polygons. Study B:
# the same polygons with an additive graphic annotation only, clipped to them.
face=box(4387.5,-8250,4622.5,8250)
visual=base.intersection(face)
assert visual.difference(base).area<1e-5
# no 3D, no actual masonry subtraction or modification
rows=[]
for side in 'NS':
 for pair,expected in [('A1_TO_A2',197),('A2_TO_A3',321)]:
  g=ref[f'R17_{side}_{pair}'];x0,y0,x1,y1=g.bounds
  assert x1-x0==470 and y1-y0==expected
  emphasis=g.intersection(face)
  assert emphasis.area==235*expected
  rows.append({'side':side,'bridge':pair,'transverse_y_depth':expected,'available_x_width':470,
               'graphic_x_width':235,'side_margin_x_each':(470-235)/2 if False else None,
               'graphic_offset_from_bridge_center_x':4505-4480,
               'left_margin_to_visual_from_bridge_edge_x':4387.5-x0,
               'right_margin_to_visual_from_bridge_edge_x':x1-4622.5,
               'visual_area_inside_bridge':emphasis.area,
               'diameter_235_circular_respond_fits_within_bridge_y':expected>=235,
               'actual_pier_or_respond_not_defined':True})
assert all(row['graphic_offset_from_bridge_center_x']==25 and row['left_margin_to_visual_from_bridge_edge_x']==142.5 and row['right_margin_to_visual_from_bridge_edge_x']==92.5 for row in rows)
# Additional check: visual emphasis is an x width only; 197 < 235
assert all(not row['diameter_235_circular_respond_fits_within_bridge_y'] for row in rows if row['bridge']=='A1_TO_A2')
assert all(row['diameter_235_circular_respond_fits_within_bridge_y'] for row in rows if row['bridge']=='A2_TO_A3')
# Main existing support x3925..4725 and east complement x4725..5085.
original=ref['R17_N_MAJOR_ORIGINAL_800'];east=ref['R17_N_EAST_360']
assert original.bounds==(3925,2933,4725,3253) and east.bounds==(4725,2933,5085,3253)
assert original.boundary.intersection(east.boundary).length==320
# Render one comparison image.
def shape_draw(ax,g,color,edge='#526973',alpha=1,z=1,lw=.5):
 parts=[g] if g.geom_type=='Polygon' else [t for t in getattr(g,'geoms',[]) if t.geom_type=='Polygon']
 for p in parts:
  ax.add_patch(Poly(list(p.exterior.coords),facecolor=color,edgecolor=edge,linewidth=lw,alpha=alpha,zorder=z))
  if color!='none':
   for ring in p.interiors:
    ax.add_patch(Poly(list(ring.coords),facecolor='#fffefa',edgecolor='none',zorder=z+.1))
fig,axs=plt.subplots(1,2,figsize=(14,10),facecolor='white')
for i,ax in enumerate(axs):
 shape_draw(ax,available,'#d3bfa6',lw=.2)
 for n,g in clear.items():
  if g.bounds[0]>5300 or g.bounds[2]<3850:continue
  shape_draw(ax,g,'#e7eee9',lw=.4,z=2)
 for g in openings:shape_draw(ax,g,'#b4dbe6',lw=.6,z=3)
 for name,g in ref.items():
  shape_draw(ax,g,'#7c9d92' if 'R16_' in name else '#ab8a58',lw=.5,alpha=.9,z=4)
 if i==1:shape_draw(ax,visual,'#965c90',edge='none',alpha=.9,z=6,lw=0)
 ax.axvline(4505,color='#a44d4a',ls='--',lw=1,zorder=8)
 ax.axvline(4480,color='#5079b2',ls=':',lw=.8,zorder=8)
 ax.set_xlim(3890,5260);ax.set_ylim(2500,6550)
 ax.set_aspect('equal','box');ax.grid(alpha=.08)
 ax.set_xlabel('Global X, native units');ax.set_ylabel('Global Y, native units')
 axs[i].set_title(['A — Continuous existing masonry reservations','B — Articulated 235-unit visual band'][i],loc='left',fontsize=11,weight='bold')
fig.suptitle('F5ZP R19 | Q1–Q2 MASONRY PROPORTION STUDY\nExisting polygons identical in A/B; visual overlay only, X=4505',x=.05,y=.975,ha='left',fontsize=15,weight='bold')
fig.legend(handles=[Patch(facecolor='#ab8a58',label='R17 existing bearing/bridge references'),Patch(facecolor='#7c9d92',label='R16 original contact strips'),Patch(facecolor='#965c90',label='235 visual annotation'),Line2D([0],[0],color='#a44d4a',ls='--',label='Main axis 4505')],loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(.5,.04),fontsize=9)
fig.text(.05,.012,'197-unit bridge permits 235 in X, but not a 235-diameter circle in Y. No structural or architectural approval.',fontsize=9.5,color='#894d45')
fig.subplots_adjust(left=.07,right=.98,top=.88,bottom=.145,wspace=.26)
png=O/'F5ZP_R19_MASONRY_PROPORTIONS_COMPARISON.png';svg=O/'F5ZP_R19_MASONRY_PROPORTIONS_COMPARISON.svg'
fig.savefig(png,dpi=165,bbox_inches='tight');fig.savefig(svg,bbox_inches='tight');plt.close(fig)
with (O/'R19_PROPORTION_CHECKS.csv').open('w',newline='') as f:
 keys=list(rows[0]);w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
(O/'R19_VISUAL_ONLY_OVERLAY.geojson').write_text(json.dumps({'type':'FeatureCollection','properties':{'status':'EXPERIMENTAL NON-STRUCTURAL GRAPHIC','source_sha256':dig},'features':[{'type':'Feature','properties':{'id':'235_VISUAL_ON_R18','not_physical_pier':True},'geometry':mapping(visual)}]},separators=(',',':'))+'\n')
qa={'status':'GEOMETRIC QA PASS — ARCHITECTURAL PROPORTIONS FOR REVIEW ONLY',
 'sources_sha256':dig,'A_B_geometry_identical':True,'preserved_vault_clear_polygons':218,
 'preserved_option_B_passages':7,'preserved_R18_references':22,
 'no_area_intrusions':True,'source_files_unchanged':True,'main_axis_x':4505,
 'aisle_axis_x':4480,'historic_major_x_range':[3925,4725],
 'east_remaining_x_range':[4725,5085],'historic_east_shared_contact_length':320,
 'visual_width_x':235,'visual_left_margin_at_aisle':142.5,
 'visual_right_margin_at_aisle':92.5,
 '197_y_band_allows_x_width_235_annotation':True,
 '197_y_band_allows_235_diameter_circle':False,
 '321_y_band_allows_235_diameter_circle':True,
 'circular_respond_design_is_only_a_hypothetical_fit_test':True,
 'historical_validation':False,'architectural_validation':False,'structural_validation':False,
 'unresolved':['197 native units in Y constrain any future circular 235-diameter respond; no circular respond has been specified.',
 '235 is a visual X emphasis, not an approved pier diameter or minimum structure.',
 'R18 has four separate junction groups per side; openings separate them.',
 'Original x3925..4725 major footprint remains asymmetrical about organizing axis x4505.',
 'F5ZL-C support schedule absent; physical conversion, arch springings, load paths unresolved.']}
(O/'R19_NUMERICAL_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
(O/'README_HANDOFF.md').write_text('''# R19 — Q1–Q2 2D masonry proportions
A and B use exactly the same source geometry: existing R18 22 regions, R11 protected clear vaults, and R13 Option B seven passages. B adds a **visual** 235 native-unit X-width layer within the existing R18 reference polygons. No actual walls or bearing footprints changed.

At A1–A2, the retained masonry bridge is 470 (X) × 197 (Y). The centered visual band X4387.5..4622.5 fits inside the 470 X reservation with 142.5 units west and 92.5 east of it (because main X4505 is offset 25 east of aisle X4480). Its Y depth is only 197. Thus a *hypothetical* 235-diameter circular respond would fail to fit that band in Y (38-unit deficit), but this DOES NOT mean the visual 235-wide X emphasis fails or the wall needs thickening. A1–A2 structural feasibility remains untested.

A2–A3 has an effective 321 Y depth locally, not replacing general 292 schedule. Recovered original main 800-long strip and existing east 360 remainder have 320-long shared plan edge. All source file hashes are recorded in QA. No actual masonry approved, moved or removed.

Reproduce: python3 R19_MASONRY_PROPORTION_2D.py
''')
ET.parse(svg)
with Image.open(png) as im: im.verify();print('image',im.size)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==dig[k] for k,p in sources.items())
copy=Path.home()/'Downloads'/'F5ZP_R19_MASONRY_PROPORTIONS_COMPARISON.png';shutil.copy2(png,copy)
archive=Path.home()/'Downloads'/'F5ZP_R19_MASONRY_PROPORTIONS_EXPERIMENTAL.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
 z.write(Path(__file__),arcname=Path(__file__).name)
 for f in sorted(O.iterdir()):z.write(f,arcname=f.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('PASS R19 geometry, SVG, PNG, source hashes, zip',archive)