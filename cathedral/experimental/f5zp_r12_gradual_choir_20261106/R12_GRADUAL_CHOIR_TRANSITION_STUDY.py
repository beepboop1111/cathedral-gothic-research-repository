#!/usr/bin/env python3
"""F5ZP R12: nave->choir->chevet gradual transition, 2D massing concept.
Uses R11 without moving, scaling, trimming any saved clear-vault geometry.
R12 highlighted cores are visual study regions, not certified supports.
"""
import csv,hashlib,json,zipfile
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PatchPoly,Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from PIL import Image
from shapely.geometry import box,shape,mapping
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'R11_FULL_COORDINATED_2D_EXPERIMENTAL'/'F5ZP_R11_COORDINATED_NATIVE_2D.geojson'
QA11=ROOT/'R11_FULL_COORDINATED_2D_EXPERIMENTAL'/'R11_GEOMETRIC_QA.json'
OUT=ROOT/'R12_GRADUAL_CHOIR_TRANSITION_EXPERIMENTAL';OUT.mkdir(exist_ok=True)
data=json.loads(SOURCE.read_text())
reference=data['features']
d={f['properties']['id']:shape(f['geometry']) for f in reference if f['properties'].get('role')=='CLEAR'}
masonry={f['properties']['id']:shape(f['geometry']) for f in reference if f['properties'].get('role')=='RESERVED_MASONRY'}
allclear=unary_union(list(d.values()))
solid=unary_union(list(masonry.values()))
assert len(d)==218 and len(masonry)==3
assert shape(next(f['geometry'] for f in reference if f['properties'].get('id')=='Crossing')).equals_exact(d['Crossing'],0)
# Build actual gap measurement ledger from 2D polygon faces, not buffered guesses.
records=[];highlight=[]
def note(section,area,key,gap,axis,offset,role):
    records.append(dict(section=section,area=area,junction=key,actual_clear_gap=round(gap,4),
                        axis_x=round(axis,4),arcade_offset=round(offset,4),status=role))
# Nominal widths are a graphic experiment: all actual reserved widths are retained.
def mark(section,key,main_a,main_b,aisle_a,aisle_b,study_width,where,kind):
    a=d[main_a];b=d[main_b]
    main_width=b.bounds[0]-a.bounds[2];axis=(a.bounds[2]+b.bounds[0])/2
    a1=d[aisle_a];b1=d[aisle_b];actual_gap=b1.bounds[0]-a1.bounds[2]
    aisle_axis=(a1.bounds[2]+b1.bounds[0])/2
    assert main_width>0 and actual_gap>0
    note(section,'CHOIR' if section!='NAVE' else 'NAVE',key,actual_gap,axis,aisle_axis-axis,kind)
    if section!='TRANSITION':
        assert abs(aisle_axis-axis)<1e-6,(key,aisle_axis-axis)
    # For the transition actual aisle gap=470, core=235; room is asymmetrically
    # flanked because Q1-Q2 aisle axis differs from main axis by -25.
    left=axis-study_width/2;right=axis+study_width/2
    assert left>=a1.bounds[2]-1e-6 and right<=b1.bounds[0]+1e-6
    # Clip to native masonry only, do not subtract from vaults or alter baseline
    north=max(d[aisle_a].bounds[3],d[aisle_b].bounds[3])
    # Carry north and south across all three aisle layers, including 320/197/292 bands.
    span=7750 if section!='CHOIR' else 7520
    if section=='TRANSITION':span=7750
    region=box(left,-span,right,span)
    clipped=region.intersection(solid)
    assert clipped.area>0 and clipped.intersection(allclear).area<1e-4
    # Unclipped entire study band must fit within reserved masonry for support continuity.
    outside=region.difference(solid).area
    assert outside<1e-4,(key,outside)
    highlight.append({'type':'Feature','properties':{
        'junction':key,'region':section,'status':kind,'actual_arcade_reservation':actual_gap,
        'conceptual_emphasis_width':study_width,'main_gap':main_width,
        'main_axis_x':axis,'actual_arcade_axis_offset':aisle_axis-axis,
        'does_not_change_r11_geometry':True},'geometry':mapping(clipped)})
    return dict(junction=key, main_gap=main_width, arcade_gap=actual_gap,
                main_axis_x=axis,arcade_axis_x=aisle_axis,axis_offset=aisle_axis-axis,
                conceptual_width=study_width, concept_left=left,concept_right=right,
                graphic_band_inside_masonry=outside<1e-4,
                clear_intrusion=clipped.intersection(allclear).area)
qa_junctions=[]
for q in range(2,9):
    qa_junctions.append(mark('NAVE',f'N{q}-N{q+1}',f'N{q}_MAIN',f'N{q+1}_MAIN',
      f'N{q}_N_A1_2',f'N{q+1}_N_A1_1',200,'nave','EXISTING_200_FULL_RESERVATION'))
qa_junctions.append(mark('TRANSITION','Q1-Q2','Q1','Q2_MAIN',
   'E_N_J1 R1C3','Q2_N_A1_1',235,'Q1','CONCEPTUAL_235_CORE_WITHIN_470_RESERVATION'))
for q in range(2,5):
    qa_junctions.append(mark('CHOIR',f'Q{q}-Q{q+1}',f'Q{q}_MAIN',f'Q{q+1}_MAIN',
       f'Q{q}_N_A1_2',f'Q{q+1}_N_A1_1',270,'choir','EXISTING_270_FULL_RESERVATION'))
assert [r['actual_arcade_reservation'] for r in [z['properties'] for z in highlight]]==[200]*7+[470]+[270]*3
assert qa_junctions[7]['main_gap']==1160 and qa_junctions[7]['axis_offset']==-25
assert all(abs(q['axis_offset'])<1e-6 for q in qa_junctions if q['junction']!='Q1-Q2')
# Q1 relief zones graphically identified, but ARE STILL THE ORIGINAL MASONRY, NOT OPENINGS.
q=qa_junctions[7];a=d['E_N_J1 R1C3'];b=d['Q2_N_A1_1']
flanks=(q['concept_left']-a.bounds[2],b.bounds[0]-q['concept_right'])
assert all(v>0 for v in flanks)
for j,prop in enumerate(['west','east']):
    note('TRANSITION_REMAINING_MASONRY',prop,'Q1-Q2',flanks[j],q['main_axis_x'],q['axis_offset'],
         'NO_OPENING_ADOPTED')
# Track east radius chevet only as separate curvature; no ungrounded uniform 270
for bay in range(1,8):
    for ia,ib in (('I','M'),('M','T')):
        dist=d[f'{ia}_A{bay}_R12C'].distance(d[f'{ib}_A{bay}_R12C'])
        note('CHEVET',f'BAY {bay}',f'{ia}-{ib}',dist,0,0,'RADIAL_SEPARATION_REFERENCE')
# Render original R11 geometry identically in both panels
def draw(ax,g,color,edge='#5d6a71',lw=.34,alpha=1,z=3):
    polys=[g] if g.geom_type=='Polygon' else [p for p in getattr(g,'geoms',[]) if p.geom_type=='Polygon']
    for p in polys:
        ax.add_patch(PatchPoly(list(p.exterior.coords),closed=True,facecolor=color,
                               edgecolor=edge,lw=lw,alpha=alpha,zorder=z))
        if color!='none':
            for hole in p.interiors:
                ax.add_patch(PatchPoly(list(hole.coords),closed=True,facecolor='#fffefa',
                                       edgecolor='none',zorder=z+.1))
def view(ax,xlims,ylims,show_core=False,show_label=False):
    ax.set_facecolor('#fffefa')
    for g in masonry.values():draw(ax,g,'#cdb9a3',edge='#9b8370',lw=.22)
    for name,g in d.items():
        if name.startswith(('I_','M_','T_A')):fc='#e0eddc'
        elif name.startswith(('Q','E_')):fc='#e7ebde'
        elif name=='Crossing':fc='#d5e2e8'
        else:fc='#e3edf5'
        draw(ax,g,fc,edge='#576b79',lw=.43,z=5)
    if show_core:
        for f in highlight:
            name=f['properties']['region']
            shade={'NAVE':'#4d758d','CHOIR':'#9b6a46','TRANSITION':'#bb8745'}[name]
            draw(ax,shape(f['geometry']),shade,edge=shade,alpha=.88,lw=.7,z=8)
    # All meaningful section centerlines are original R11 ones
    for item in qa_junctions:
        if item['main_axis_x']<xlims[0] or item['main_axis_x']>xlims[1]:continue
        ax.axvline(item['main_axis_x'],color='#8d5d53',lw=.55,ls=(0,(2,4)),zorder=9)
        if show_label:
            lbl=item['junction']; actual=int(item['arcade_gap'])
            ax.text(item['main_axis_x'],7500 if ylims[1]>8000 else 6770,
                    f'{lbl}\n{actual}',color='#604d42',fontsize=7.6,ha='center',va='top',zorder=10)
    ax.set_xlim(*xlims);ax.set_ylim(*ylims);ax.set_aspect('equal','box')
    ax.grid(alpha=.1);ax.set_xlabel('X • native architectural units');ax.set_ylabel('Y • native architectural units')
# Side-by-side comparative plan with same geometry and zoom
fig=plt.figure(figsize=(21,16),facecolor='white')
gs=fig.add_gridspec(3,1,height_ratios=[.5,1,1],left=.055,right=.98,top=.87,bottom=.09,hspace=.38)
axoverview=fig.add_subplot(gs[0]);axA=fig.add_subplot(gs[1]);axB=fig.add_subplot(gs[2])
view(axoverview,(-47700,29600),(-9800,9800),show_core=True)
axoverview.set_title('Full cathedral sequence, west → east   •   studied geometry remains R11',loc='left',pad=13,fontsize=12,weight='bold')
view(axA,(-20700,21100),(-8050,8050))
axA.set_title('A  |  ACTUAL R11 MASONRY RESERVATIONS   •   200 nave → 470 Q1 threshold → 270 choir',loc='left',pad=13,fontsize=12,weight='bold')
view(axB,(-20700,21100),(-8050,8050),show_core=True,show_label=True)
axB.set_title('B  |  GRADUAL EXPERIMENT   •   200 nave → 235 notional Q1 visible core → 270 choir',loc='left',pad=13,fontsize=12,weight='bold')
fig.suptitle('F5ZP  R12  |  GRADUAL CHOIR TRANSITION — 2D MASONRY RHYTHM STUDY\n'
    'A comparison, not a revision: all vault clearances, chevet, crossing and R11 masonry polygons preserved',
    fontsize=18,weight='bold',x=.055,ha='left',y=.977,color='#283c46')
fig.text(.055,.9,'Finding: the actual Q1→Q2 aisle division is 470 wide; a 235-wide emphasized core could reduce the perceived jump without moving vaults.',fontsize=11,color='#8a563b')
fig.legend(handles=[Patch(facecolor='#cdb9a3',label='Unchanged R11 masonry reservation'),
                    Patch(facecolor='#4d758d',label='200 nave strip (actual)'),
                    Patch(facecolor='#bb8745',label='235 Q1 conceptual emphasis'),
                    Patch(facecolor='#9b6a46',label='270 choir strip (actual)'),
                    Patch(facecolor='#e0eddc',label='Protected radial chevet')],
           loc='lower left',bbox_to_anchor=(.055,.035),ncol=3,fontsize=10,frameon=False)
fig.text(.055,.015,'Q1 concept is graphic designation inside existing 470 reserve; NOT an opening, structural pier, or architectural approval. Q1 remains 1160 at main bay.',fontsize=10,color='#884e46')
img=OUT/'F5ZP_R12_GRADUAL_CHOIR_COMPARE.png'
svg=OUT/'F5ZP_R12_GRADUAL_CHOIR_COMPARE.svg'
fig.savefig(img,dpi=170,bbox_inches='tight');fig.savefig(svg,bbox_inches='tight');plt.close(fig)
# Independent close view of Q1/choir edge with explicit step dimensions
fig,ax=plt.subplots(figsize=(15,8.5),facecolor='white')
view(ax,(-1300,9500),(-8100,8100),show_core=True)
axis=q['main_axis_x']
for side,y in [('north',3800),('south',-3800)]:
    left=d['E_N_J1 R1C3'].bounds[2];right=d['Q2_N_A1_1'].bounds[0]
    ax.plot([left,right],[y,y],color='#3d6a82',lw=1.8,zorder=10)
    ax.plot([q['concept_left'],q['concept_right']],[y,y],color='#d5a15b',lw=5,zorder=11)
    ax.text(axis,y+350,f'470 actual reserved • 235 indicated core • axis error {q["axis_offset"]:+.0f}',
            ha='center',fontsize=9,color='#693f33',zorder=12)
ax.set_title('Q1 → Q2 transition | concept centered on the MAIN bay axis X=4505\n'
   'Flanking masonry remains reserved; no physical openings designed',loc='left',fontsize=14,weight='bold')
fig.tight_layout()
detail=OUT/'F5ZP_R12_Q1_Q2_TRANSITION_DETAIL.png'
fig.savefig(detail,dpi=185,bbox_inches='tight');plt.close(fig)
with (OUT/'R12_MASONRY_RHYTHM_MEASUREMENTS.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
geo=OUT/'R12_CONCEPTUAL_CORE_REGIONS.geojson'
geo.write_text(json.dumps({'type':'FeatureCollection','properties':{
 'status':'NON-STRUCTURAL GRAPHIC STUDY — NO BASELINE REVISION',
 'geometry_source':str(SOURCE),'dimension_units':'native 1:1',
 'frozen_r11_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()},
 'features':highlight},separators=(',',':'))+'\n')
qareport={'status':'R12 EXPERIMENTAL 2D GRAPHIC/ARCHITECTURAL IDEA; NOT APPROVED',
 'r11_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'baseline_features':len(reference),'actual_r11_geom_changed':False,
 'nave_200_junctions':7,'choir_270_junctions':3,
 'same_separator_axes_aligned':all(abs(v['axis_offset'])<1e-6 for v in qa_junctions if v['junction']!='Q1-Q2'),
 'Q1_Q2_main_gap':1160,'Q1_Q2_actual_aisle_gap':470,
 'Q1_Q2_axis_offset':-25,'Q1_Q2_conceptual_core_width':235,
 'remaining_reservation_flanks_west_east':flanks,
 'consequential_warning':'235 conceptual core designation is NOT a verified physical masonry support or future opening',
 'clear_area_overlap_with_concept':max(shape(f['geometry']).intersection(allclear).area for f in highlight),
 'all_concept_within_existing_masonry':all(shape(f['geometry']).difference(solid).area<1e-4 for f in highlight),
 'recomputed_vault_geometry':'NONE',
 'invariants_from_R11':json.loads(QA11.read_text())['geometry'],
 'existing_issues':['Crossing, west termination, Q1-Q2 support configuration provisional',
  'Axial chapel native 2D outline not registered','F5ZL-C support schedule unresolved',
  'No pier load-path, door opening, structural capacity, or historical design validation']}
(OUT/'R12_STUDY_QA.json').write_text(json.dumps(qareport,indent=2)+'\n')
(OUT/'README_HANDOFF.md').write_text('''# F5ZP R12 — Gradual choir transition, experimental 2D plan comparison

**This study does not modify R11, protected geometry, or approved models.**

### What the actual R11 geometry says
- Straight nave arcade interbay masonry: **200**; all seven regular separator axes registered with main bay centerlines; main separators remain **520**.
- Choir Q2–Q5 arcade interbay masonry: **270**, exact 520 main-axis alignment.
- Q1→Q2 special entrance: **470** between aisle vaults, **1160** between main vaults. Arcade axis is **25 units west** of main divider axis.
- Chevet uses separate radial pattern; preserve its seven-bay plan and existing 320 / 197 / 292 transverse arcade bands.
- No vault clear footprints changed.

### Design comparison
- **A (current):** physical reservation rhythm 200 → 470 → 270. Wide Q1 threshold breaks a strictly gradual impression.
- **B (experimental graphic emphasis):** 200 nave → **235 visual Q1 core** → 270 choir; retain 470 full masonry reserve and its unaltered 1160 main envelope. The 235 notional core is centered on the MAIN separator axis; this does not register the entire 470 aisle separator with the main axis.
- Conceptual core leaves 142.5 west and 92.5 east of the original aisle reservation. These remain masonry reservations, NOT approved apertures or physical relief.

### Caution
Visual subzones can illustrate emphasis but do not reduce the material actually reserved in the 470-wide entrance; do not claim the 200→235→270 pattern is already realized as physical construction. Architectural feasibility and actual relief openings require separate pier/arch studies. No structural or historical validation implied.

### Deliverables
- A/B comparison PNG and matching SVG
- Detailed Q1 transition PNG
- R12 study overlay GeoJSON (11 separate graphic regions)
- Actual measurement CSV, quantitative QA JSON
- Reproducible Python script (requires R11 original in same working root)

### Current next decision
Review whether the 470-wide Q1→Q2 entrance should be maintained as a ceremonial pause (option A), or whether selective visual articulation within that reservation (option B) is worthy of later structural/architectural study. Either way, restore no unwanted pier or vault changes.
''')
print('R12',img,'DETAIL',detail,'concepts',len(highlight),'measurements',len(records),
      'Q1 flanks',flanks,'r11 source unchanged','QA',qareport['all_concept_within_existing_masonry'])