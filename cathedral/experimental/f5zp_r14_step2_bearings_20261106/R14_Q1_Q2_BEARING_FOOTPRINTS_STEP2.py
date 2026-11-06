#!/usr/bin/env python3
"""R14 step 2 — Q1-Q2 experimental bearing footprints inside R13 Option B remaining masonry.
No permanent changes to R11, R12C, saved generators, or approved supports.
"""
from pathlib import Path
import csv,json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPatch, Patch
from matplotlib.lines import Line2D
from shapely.geometry import shape,box,mapping
from shapely.ops import unary_union
from shapely.validation import explain_validity
from PIL import Image
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'R14_Q1_Q2_BEARING_FOOTPRINTS_STEP2_EXPERIMENTAL'
OUT.mkdir(exist_ok=True)
R12C=ROOT/'R12C_PLAN_NATIVE.geojson'
R11=ROOT/'R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson'
R13=ROOT/'R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson'
REC=ROOT/'R14_Q1_Q2_SUPPORT_RECOVERY_EXPERIMENTAL/R14_Q1_Q2_SUPPORT_CLASSIFICATION.csv'
source={key:hashlib.sha256(path.read_bytes()).hexdigest() for key,path in
        [('R12C',R12C),('R11',R11),('R13',R13),('R14_step1',REC)]}
orig={z['properties']['id']:shape(z['geometry']) for z in json.loads(R12C.read_text())['features']}
r11f=json.loads(R11.read_text())['features']
clear={z['properties']['id']:shape(z['geometry']) for z in r11f if z['properties'].get('role')=='CLEAR'}
clearunion=unary_union(list(clear.values()))
masonry=next(shape(z['geometry']) for z in r11f if z['properties'].get('id')=='CHOIR_MASONRY_R10')
q13=json.loads(R13.read_text())['features']
passages={z['properties']['id']:shape(z['geometry']) for z in q13 if z['properties'].get('variant')=='B_BALANCED'
          and z['properties'].get('layer')=='EXPERIMENTAL_PASSAGE_VOID'}
assert len(passages)==7
openingunion=unary_union(list(passages.values()))
retained=masonry.difference(openingunion)
assert retained.is_valid
xmain=4505
assert abs((clear['Q1'].bounds[2]+clear['Q2_MAIN'].bounds[0])/2-xmain)<1e-9
oldclass=list(csv.DictReader(REC.open()))
assert sum(x['status']=='GEOMETRICALLY_COMPATIBLE' for x in oldclass)==4
# Original positions are never changed. Four are reused as exact experimental references.
compatible=[f'Q1_Q2_major_{i}' for i in (1,-1)]+['Q1_Q2_step_132','Q1_Q2_step_133']
outer_partial=['Q1_Q2_step_134','Q1_Q2_step_135','E_N_Lower node 3-3','E_S_Lower node 3-3']
outer_unfit=['Q1_Q2_step_136','Q1_Q2_step_137']
for n in compatible:
    assert orig[n].difference(retained).area<.00001
for n in outer_unfit:
    assert orig[n].intersection(retained).area<.00001
# Candidate P: exact core and 2D sub-footprint "respond-face" reservations. Keep
# central x extent 235 units, but do NOT label this structural load-bearing capacity.
# Retain recovered masonry at B between 7 proposed passages. Regular cross-strips
# and upper peripheral rim are extracted in verified y windows.
bands_north=[
 ('MAJOR_TO_A1',2573.,3413.),
 ('A1_TO_A2',4245.,4762.),
 ('A2_TO_A3',5757.,6458.),
 ('A3_TO_OUTER_EDGE',7492.,8094.)
]
# In final outer band, the existing A3 vault extends to y7774, so the continuous
# 235 core y7492..8094 is NOT inside masonry. Intersect and split into valid segments.
core_strip=box(xmain-117.5,-8094,xmain+117.5,8094)
for side in ('N','S'):
 for label,yl,yh in bands_north:
    window=box(4000,yl,5000,yh) if side=='N' else box(4000,-yh,5000,-yl)
    proposed=core_strip.intersection(window)
    if label!='A3_TO_OUTER_EDGE':
       assert proposed.difference(retained).area<.0001,(side,label,proposed.difference(retained).area)
# Design two independent options:
# P — exact preserved support footprints plus 235-wide designated facing in
# transverse wall bands (geometric/subset). Outer 2 "outside" excluded.
# Q — same, plus 235-wide internal envelope rim bearers from y7774..8094.
# Differences vs P are an extra new candidate rim, not claim of recovered originals.
candidate={}
for option in ('P_PRESERVE','Q_INTEGRATED_RIM'):
    footprints=[];metadata=[]
    for n in compatible:
        g=orig[n]
        footprints.append(g)
        metadata.append(('RECOVERED_UNMODIFIED',n,g))
    # Candidate experimental clipped outer references, which are expressly NOT
    # recoveries: clipped intersection with R11 retained masonry.
    for side,src_names in [('N',['Q1_Q2_step_134','E_N_Lower node 3-3']),
                           ('S',['Q1_Q2_step_135','E_S_Lower node 3-3'])]:
        pieces=[orig[n].intersection(retained) for n in src_names]
        combined=unary_union(pieces)
        assert combined.area>0 and combined.is_valid
        footprints.append(combined)
        metadata.append(('RECONCILED_OUTER_FRAGMENT',side+'_A3_OUTER',combined))
    for side in ('N','S'):
        for label,yl,yh in bands_north[:-1]:
            window=box(4000,yl,5000,yh) if side=='N' else box(4000,-yh,5000,-yl)
            g=core_strip.intersection(window)
            assert g.difference(retained).area<1e-4
            metadata.append(('235_VISUAL_RESPOND_FACING',side+'_'+label,g))
        if option=='Q_INTEGRATED_RIM':
            # Explicit usable-band test: take a 235-wide portion inside upper
            # outer masonry, avoiding A3 vault at its maximum Y (7774).
            window=box(4000,7774,5000,8094) if side=='N' else box(4000,-8094,5000,-7774)
            g=core_strip.intersection(window).intersection(retained)
            assert g.is_valid and g.area>0 and g.difference(retained).area<1e-4
            metadata.append(('NEW_PROVISIONAL_OUTER_RIM_FACING',side+'_OUTER_RIM',g))
    candidate[option]=metadata
# Analyze all geometry and original interfaces, distinguish overlap of itself
# from actual physical connection with surrounding masonry.
rows=[];geom=[]
for opt,data in candidate.items():
    for kind,n,g in data:
        assert g.is_valid, (opt,n,explain_validity(g))
        if g.geom_type=='GeometryCollection':
            g=unary_union([s for s in g.geoms if s.geom_type=='Polygon'])
        assert g.area>0,(opt,n)
        assert g.intersection(openingunion).area<1e-4,(opt,n,'opening')
        assert g.intersection(clearunion).area<1e-4,(opt,n,'vault')
        assert g.difference(retained).area<1e-4,(opt,n,'outside')
        touches=[k for k,p in passages.items() if p.distance(g)<1e-4]
        qs={'variant':opt,'kind':kind,'id':n,'x0':g.bounds[0],
            'y0':g.bounds[1],'x1':g.bounds[2],'y1':g.bounds[3],
            'area':g.area,'bounds_width_x':g.bounds[2]-g.bounds[0],
            'bounds_height_y':g.bounds[3]-g.bounds[1],
            'overlap_vault':g.intersection(clearunion).area,
            'overlap_B_passage':g.intersection(openingunion).area,
            'outside_retained_masonry':g.difference(retained).area,
            'touching_passages_count':len(touches),
            'status':'EXPERIMENTAL_NO_STRUCTURAL_CERTIFICATION'}
        rows.append(qs)
        geom.append({'type':'Feature','properties':qs,'geometry':mapping(g)})
# Critical edge: old Q1 major strip is x3925..4725 and reuses this exact footprint
# but is not sized from a structural load schedule, so never classify as approved.
assert all(orig[n].equals_exact(next(g for kind,k,g in candidate['P_PRESERVE'] if k==n),1e-8)
           for n in compatible)
assert all(any(x['kind']=='NEW_PROVISIONAL_OUTER_RIM_FACING' for x in rows if x['variant']=='Q_INTEGRATED_RIM')
           for _ in [0])
# Main vs secondary bearings share an axis but major strip is asymmetrical relative
# to main Q1-Q2 axis; this must be visible in the diagram / QA.
major_mid=(orig['Q1_Q2_major_1'].bounds[0]+orig['Q1_Q2_major_1'].bounds[2])/2
assert major_mid==4325 and xmain-major_mid==180
# Q outer rim projection candidates remain completely inside revised wall envelope,
# which is precisely why original outermost R12C footprints cannot be recovered.
for s in ('N','S'):
 a=next(g for kind,n,g in candidate['Q_INTEGRATED_RIM']
         if kind=='NEW_PROVISIONAL_OUTER_RIM_FACING' and n==s+'_OUTER_RIM')
 assert a.area>0
with (OUT/'R14_STEP2_FOOTPRINT_MEASUREMENTS.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
geo=OUT/'R14_Q1_Q2_CANDIDATE_BEARINGS_R02_EXPERIMENTAL.geojson'
geo.write_text(json.dumps({'type':'FeatureCollection',
 'properties':{'status':'R14 STEP2 EXPERIMENTAL 2D CANDIDATES ONLY',
  'R11_SHA256':source['R11'],'R13_SHA256':source['R13']},
 'features':geom},separators=(',',':'))+'\n')
# Plot original recovered support vs both experimental candidates, using accurate
# source 2D geometry rather than stylized placeholders.
fig,axes=plt.subplots(1,3,figsize=(19,12.5),facecolor='white')
def add(ax,g,fc,ec='#5c5c5c',lw=.42,alpha=1,z=4):
    if g.is_empty:return
    polys=[g] if g.geom_type=='Polygon' else [p for p in getattr(g,'geoms',[]) if p.geom_type=='Polygon']
    for p in polys:
        ax.add_patch(plt.Polygon(list(p.exterior.coords),facecolor=fc,edgecolor=ec,
                                 linewidth=lw,alpha=alpha,zorder=z))
        if fc!='none':
            for inner in p.interiors:
                ax.add_patch(plt.Polygon(list(inner.coords),facecolor='#fffefa',edgecolor='none',zorder=z+.1))
def render(ax,variant=None):
    add(ax,retained,'#cdb99f',lw=.15,z=1)
    for k,g in clear.items():
        if g.bounds[0]>5200 or g.bounds[2]<3600:continue
        add(ax,g,'#e5eee5','#4d6571',.35,1,2)
    for n,g in passages.items():add(ax,g,'#add9e9','#40778b',.65,z=5)
    if variant is None:
        for n in compatible+outer_partial+outer_unfit:
            g=orig[n]
            color=('#397c6c' if n in compatible else
                   '#bd8539' if n in outer_partial else '#aa4a48')
            add(ax,g,color,'#4b433c',.55,.8,8)
    else:
        for kind,n,g in candidate[variant]:
            if kind=='RECOVERED_UNMODIFIED':color='#397c6c'
            elif kind=='RECONCILED_OUTER_FRAGMENT':color='#bd8539'
            elif kind=='NEW_PROVISIONAL_OUTER_RIM_FACING':color='#ab6a44'
            else:color='#8668a9'
            add(ax,g,color,'#4e423a',.4,.78 if kind!='235_VISUAL_RESPOND_FACING' else .85,8)
    ax.axvline(xmain,color='#9f4c45',ls='--',lw=.8,zorder=9)
    ax.set_xlim(3800,5050);ax.set_ylim(-8480,8480)
    ax.set_aspect('equal','box');ax.grid(alpha=.12)
    ax.set_xlabel('X • native units');ax.set_ylabel('Y • native units')
for ax,mode,head in zip(axes,[None,'P_PRESERVE','Q_INTEGRATED_RIM'],[
    'Recovery: original supports (six no longer fit)',
    'P • compatible + clipped outer fragments',
    'Q • P plus 235-wide internal rim studies']):
    render(ax,mode);ax.set_title(head,loc='left',fontsize=10.1,weight='bold',pad=11)
fig.suptitle('F5ZP R14 STEP 2 | Q1–Q2 PIER-BEARING FOOTPRINTS (2D EXPERIMENTS)\n'
 'No approved source modified • R13 Option B openings unchanged • original outer 2 remain unresolved',
 x=.045,y=.973,fontsize=15.2,weight='bold',ha='left',color='#2c4248')
fig.legend(handles=[Patch(facecolor='#397c6c',label='Four original compatible supports'),
 Patch(facecolor='#bd8539',label='Clipped historical outer fragments'),
 Patch(facecolor='#aa4a48',label='Original supports outside R11 envelope'),
 Patch(facecolor='#8668a9',label='235-wide facing (nonstructural)'),
 Patch(facecolor='#ab6a44',label='Provisional new rim facing (Q only)'),
 Patch(facecolor='#add9e9',label='R13-B passage openings')],
 loc='lower center',bbox_to_anchor=(.5,.042),ncol=3,fontsize=9,frameon=False)
fig.text(.045,.013,'These are plan-footprint studies, not complete piers. No arch bearings, load transfers, springing profiles or structural checks established.',
 fontsize=9.5,color='#895047')
fig.subplots_adjust(top=.885,bottom=.12,left=.04,right=.985,wspace=.18)
png=OUT/'F5ZP_R14_STEP2_Q1_Q2_BEARING_FOOTPRINTS_COMPARE.png'
svg=OUT/'F5ZP_R14_STEP2_Q1_Q2_BEARING_FOOTPRINTS_COMPARE.svg'
fig.savefig(png,dpi=165,bbox_inches='tight');fig.savefig(svg,bbox_inches='tight');plt.close(fig)
qa={
 'status':'EXPERIMENTAL STEP2 2D footprint studies; no design approval',
 'inputs_sha256':source,'baseline_changed':False,'source_r11_unchanged':True,
 'source_r13_optionB_unchanged':True,
 'recovered_unmodified_supports':compatible,'partially_outside_reconciled_only_in_separate_candidates':outer_partial,
 'outermost_not_fitted_or_moved':outer_unfit,
 'main_axis_x':xmain,'recovered_major_support_axis_x':major_mid,
 'major_support_offset_from_main_axis':major_mid-xmain,
 'candidate_feature_counts':{k:len(v) for k,v in candidate.items()},
 'unmodified_recovered_support_count':4,'seven_B_openings_preserved':True,
 'all_candidate_regions_within_R11_retained_masonry':True,
 'candidate_intrusion_into_original_vaults':0,
 'candidate_intrusion_into_R13_B_openings':0,
 'physical_235_pier_width_approved':False,
 'structural_capacity_validated':False,
 'issues':['Only four saved support footprints are unchanged and geometric-compatible.',
 'Clipping the outer historical support polygons does not verify their architectural function.',
 'Both far-outer source footprints lie outside current R11 envelope; no replacement source schedule is available.',
 'R13-B doorway voids were designed in plan only; arch springing, tas-de-charge and pier interfaces not determined.',
 'Original major support strips are offset 180 west from the main bay axis.',
 'Masonry continuity does not prove bearing load or structural adequacy.',
 'F5ZL-C support schedule remains unresolved.']}
(OUT/'R14_STEP2_BEARING_FOOTPRINTS_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
(OUT/'README_HANDOFF.md').write_text("""# R14 Step 2 — experimental Q1–Q2 bearing footprints

## Output scope
Two candidate **2D bearing footprint overlays**, not structural or approved masonry redesign.
No change to R11 clear vaults, R13-B seven passages, crossing, chevet, protected dimensions or Pass 6J.

## P — preservation-first
Reuses Q1_Q2_major_1, Q1_Q2_major_-1, Q1_Q2_step_132, Q1_Q2_step_133 unchanged.
Only experimental clipped overlaps of Q1_Q2_step_134/135 and E_N/S_Lower node 3-3 inside R11 remaining masonry;
does not relocate the original footprints or claim they are structurally adequate.
A 235-wide visual facing is drawn at the main x=4505 axis in three genuine transverse masonry bands
on each side, wholly inside retained R13-B masonry (not inside a passage).

## Q — internal rim study
Same as P, plus two provisional 235-wide face strips in the actual outer rim of the
existing R11 choir masonry. This avoids extending outside the fixed boundary, but is
a **new experimental architectural suggestion**, not a recovered historic support.

## Verified constraints
R11 coordinate source SHA-256 and R13-B geometry preserved. All candidate regions fit within
current retained masonry and avoid every source vault-clear space and seven R13-B passages.
The original major Q1-Q2 bearing band is centered at x4325 while the main bay axis is x4505,
180 units east; that asymmetry remains visible. No assumption that simply painting a
235-wide facing solves pier bearings or full masonry support.

## Remaining blockers
The original two extreme step supports Q1_Q2_step_136/137 lie wholly outside R11 masonry and
remain unresolved (F5ZL-C missing). No structural capacity, profile, tas-de-charge, or
arch jamb-bonding validation. No candidate here is approved.

## Reproduction
Run python3 R14_Q1_Q2_BEARING_FOOTPRINTS_STEP2.py in the R12C workspace.
""")
with Image.open(png) as im:im.verify();print('PNG',im.size)
print('R14 STEP2 COMPLETED',len(geom),'candidate footprints',len(rows),
      'types',{k:len(v) for k,v in candidate.items()})