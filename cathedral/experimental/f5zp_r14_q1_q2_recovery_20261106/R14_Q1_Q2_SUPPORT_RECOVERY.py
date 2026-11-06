#!/usr/bin/env python3
"""R14 step 1 only: recover saved Q1-Q2 support reservations vs R13 Option B.
Read-only original R12C source and saved Blender inventory; no redesign or promotion.
"""
from pathlib import Path
import json,csv,hashlib,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlotPoly,Patch
from matplotlib.lines import Line2D
from shapely.geometry import shape,box,mapping
from shapely.ops import unary_union
from PIL import Image
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'R14_Q1_Q2_SUPPORT_RECOVERY_EXPERIMENTAL';OUT.mkdir(exist_ok=True)
ORIGINAL=ROOT/'R12C_PLAN_NATIVE.geojson'
R11=ROOT/'R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson'
R13=ROOT/'R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson'
BLEND_INV=OUT/'R12C_SAVED_BLEND_Q1_Q2_OBJECTS.json'
sources={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in
         [('R12C_original',ORIGINAL),('R11_current',R11),('R13_option_B',R13),
          ('R12C_blender_inventory',BLEND_INV)]}
orig=json.loads(ORIGINAL.read_text())['features']
r11=json.loads(R11.read_text())['features']
r13=json.loads(R13.read_text())['features']
blender=json.loads(BLEND_INV.read_text())['objects']
source_shapes={f['properties']['id']:shape(f['geometry']) for f in orig}
source_props={f['properties']['id']:f['properties'] for f in orig}
blender_obj={ob['name'].split('__',1)[-1].replace('_',' '):ob for ob in blender}
blender_exact={ob['name'].split('__',1)[-1]:ob for ob in blender}
clear={f['properties']['id']:shape(f['geometry']) for f in r11 if f['properties'].get('role')=='CLEAR'}
allclear=unary_union(list(clear.values()))
choir=next(shape(f['geometry']) for f in r11 if f['properties'].get('id')=='CHOIR_MASONRY_R10')
passages={f['properties']['id']:shape(f['geometry']) for f in r13 if
          f['properties'].get('variant')=='B_BALANCED' and
          f['properties'].get('layer')=='EXPERIMENTAL_PASSAGE_VOID'}
assert len(passages)==7
void=unary_union(list(passages.values()))
remaining=choir.difference(void)
concept=next(shape(f['geometry']) for f in r13 if
             f['properties'].get('variant')=='B_BALANCED' and
             f['properties'].get('layer')=='EXPERIMENTAL_235_VISUAL_ARTICULATION_NOT_SUPPORT')
ids=[f'Q1_Q2_major_{i}' for i in (1,-1)]
ids += [f'Q1_Q2_step_{i}' for i in range(132,138)]
ids += [f'E_{s}_Lower node 3-3' for s in 'NS']
lanes=[f'lane_{i}' for i in range(7,17)]
assert len(ids)==10 and len(blender)==20
def bbox_close(a,b,eps=1e-5):return all(abs(x-y)<eps for x,y in zip(a,b))
rows=[];overlay=[]
for n in ids+lanes:
    g=source_shapes[n];props=source_props[n]
    assert g.is_valid
    source_mismatch=False
    blender_name=next((k for k in blender_exact if k==n),None)
    assert blender_name is not None,n
    assert bbox_close(g.bounds,blender_exact[blender_name]['bounds_native']),(n,g.bounds,blender_exact[blender_name])
    outside=g.difference(choir).area
    inside=g.intersection(choir).area
    inc=g.intersection(remaining).area
    voidhit=g.intersection(void).area
    clearhit=g.intersection(allclear).area
    # Some allocation lanes are superseded by newly translated vault polygons,
    # and must not be treated as structural supports.
    if props['role']=='ALLOCATION_LANE':
        category='ALLOCATION_ONLY_UNREGISTERED'
    elif clearhit>1e-4 or voidhit>1e-4:
        category='CONFLICT'
    elif outside<1e-4:
        category='GEOMETRICALLY_COMPATIBLE'
    elif inside>1e-4:
        category='PARTIALLY_OUTSIDE_REBUILT_MASONRY'
    else:
        category='OUTSIDE_REBUILT_MASONRY'
    dist=max(g.distance(choir),g.distance(void)) if category=='OUTSIDE_REBUILT_MASONRY' else g.distance(void)
    record={'name':n,'original_role':props['role'],'status':category,
      'x0':g.bounds[0],'y0':g.bounds[1],'x1':g.bounds[2],'y1':g.bounds[3],
      'area':round(g.area,5),'within_R11_masonry_area':round(inside,5),
      'outside_R11_masonry_area':round(outside,5),
      'overlap_R11_clear_vault_area':round(clearhit,5),
      'overlap_R13_B_passage_area':round(voidhit,5),
      'within_B_retained_masonry_area':round(inc,5),
      'overlap_235_visual_emphasis_area':round(g.intersection(concept).area,5),
      'nearest_B_passage_distance':round(g.distance(void),5),
      'saved_blend_bounds_match':True,'can_claim_structurally_usable':False}
    rows.append(record)
    overlay.append({'type':'Feature','properties':record,'geometry':mapping(g)})
# Source original R12C references are historical-to-this-working-plan, not
# architecturally approved in current R11. Some named ACCEPTED are provisional.
supports=[r for r in rows if r['name'] in ids]
lanes_rows=[r for r in rows if r['name'] in lanes]
from collections import Counter
counts=Counter(r['status'] for r in supports)
assert counts=={'GEOMETRICALLY_COMPATIBLE':4,
   'PARTIALLY_OUTSIDE_REBUILT_MASONRY':4,'OUTSIDE_REBUILT_MASONRY':2},counts
assert all(r['overlap_R13_B_passage_area']==0 for r in supports)
assert all(r['overlap_R11_clear_vault_area']==0 for r in supports)
assert all(r['saved_blend_bounds_match'] for r in rows)
assert sum(r['status']=='ALLOCATION_ONLY_UNREGISTERED' for r in lanes_rows)==10
# Recovered support footprints require no resynthesis; export raw original geometries.
with (OUT/'R14_Q1_Q2_SUPPORT_CLASSIFICATION.csv').open('w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'R14_Q1_Q2_RECOVERED_REFERENCES.geojson').write_text(json.dumps({
 'type':'FeatureCollection','properties':{'status':'EXPERIMENTAL_RECOVERED_REFERENCES_NOT_NEW_SUPPORTS',
 'source_original_sha256':sources['R12C_original'],'no_source_modification':True},
 'features':overlay},separators=(',',':'))+'\n')
# Two views: full +/- Y and close of outer nodes, both world native coordinates.
def draw(ax,g,fc,ec='#354d59',lw=.5,z=3,alpha=1):
    ps=[g] if g.geom_type=='Polygon' else [t for t in getattr(g,'geoms',[]) if t.geom_type=='Polygon']
    for p in ps:
        ax.add_patch(PlotPoly(list(p.exterior.coords),facecolor=fc,edgecolor=ec,
                              lw=lw,alpha=alpha,zorder=z))
        if fc!='none':
            for h in p.interiors:
                ax.add_patch(PlotPoly(list(h.coords),facecolor='#fffdfa',edgecolor='none',zorder=z+.1))
status_color={'GEOMETRICALLY_COMPATIBLE':'#387e6d',
              'PARTIALLY_OUTSIDE_REBUILT_MASONRY':'#c38336',
              'OUTSIDE_REBUILT_MASONRY':'#ac5153',
              'CONFLICT':'#a13c32',
              'ALLOCATION_ONLY_UNREGISTERED':'#8c78aa'}
fig,axes=plt.subplots(1,2,figsize=(18,13),facecolor='white')
for ax in axes:
    ax.set_facecolor('#fffdfa')
    draw(ax,choir,'#cdbba1','#8c7d6a',.2,1)
    for n,g in clear.items():
        if g.bounds[2]<3700 or g.bounds[0]>5450:continue
        draw(ax,g,'#e3efe5','#426876',.6,3)
    for n,g in passages.items():
        draw(ax,g,'#add8e5','#276d92',.7,6)
    for f in overlay:
        p=f['properties'];g=shape(f['geometry'])
        if p['original_role']=='ALLOCATION_LANE':
            # show historical allocation zones dashed gray outlines; no implied masonry
            draw(ax,g,'none','#897c99',.5,7,.4)
        else:
            draw(ax,g,status_color[p['status']],'#423e3c',.8,8,.8)
    ax.axvline(4505,color='#a54444',ls='--',lw=1.1,zorder=9)
    ax.axvline(4480,color='#466ca0',ls=':',lw=.8,zorder=9)
    ax.set_aspect('equal','box');ax.grid(alpha=.1)
    ax.set_xlabel('Global X (native 1:1)');ax.set_ylabel('Global Y (native 1:1)')
axes[0].set_xlim(3650,5450);axes[0].set_ylim(-8800,8800)
axes[0].set_title('Whole Q1–Q2 recovered support arrangement — north + south',
                  loc='left',pad=12,fontsize=11.5,weight='bold')
axes[1].set_xlim(4080,4890);axes[1].set_ylim(5580,8650)
axes[1].set_title('North A2–A3 junction and outer node registration',loc='left',
                  pad=12,fontsize=11.5,weight='bold')
for r in supports:
    if r['y0']>5500:
        axes[1].text((r['x0']+r['x1'])/2,(r['y0']+r['y1'])/2,
                     r['name'].replace('Q1_Q2_','').replace('E_N_',''),
                     ha='center',va='center',fontsize=7,color='#23282d',
                     rotation=90,zorder=10)
fig.suptitle('F5ZP R14-1 | RECOVERED Q1–Q2 SUPPORT FOOTPRINTS vs. R13-B\n'
    'Saved Blender coordinates confirmed against original R12C GeoJSON; no new supports modeled',
    x=.055,y=.974,ha='left',fontsize=16.5,weight='bold',color='#243b47')
fig.legend(handles=[Patch(facecolor='#387e6d',label='4 geometrically compatible'),
                    Patch(facecolor='#c38336',label='4 partly outside R11 masonry'),
                    Patch(facecolor='#ac5153',label='2 outside R11 masonry'),
                    Patch(facecolor='#add8e5',label='Option B proposed passage'),
                    Line2D([0],[0],color='#897c99',label='Original allocation lane (not support)'),
                    Line2D([0],[0],color='#a54444',ls='--',label='Main axis 4505')],
          loc='lower left',bbox_to_anchor=(.055,.035),ncol=3,fontsize=9.5,frameon=False)
fig.text(.055,.012,'Original status tags ACCEPTED_800 / ACCEPTED_STEP are preserved source labels, not architectural or structural approvals in R14.',
         fontsize=9.3,color='#87483a')
fig.tight_layout(rect=(0,.07,1,.905))
png=OUT/'F5ZP_R14_Q1_Q2_RECOVERED_SUPPORT_OVERLAY.png'
svg=OUT/'F5ZP_R14_Q1_Q2_RECOVERED_SUPPORT_OVERLAY.svg'
fig.savefig(png,dpi=180,bbox_inches='tight')
fig.savefig(svg,bbox_inches='tight');plt.close(fig)
qa={'status':'R14 STEP 1 COMPLETE — SUPPORT RECOVERY ONLY, EXPERIMENTAL',
 'source_SHA256':sources,
 'saved_blender_file':json.loads(BLEND_INV.read_text())['blend_path'],
 'saved_blender_SHA256':json.loads(BLEND_INV.read_text())['blend_sha256'],
 'recovered_object_count':20,'recovered_support_count':10,'allocation_lane_count':10,
 'support_class_counts':dict(counts),'support_vs_option_B_openings_overlap_area':0,
 'support_vs_R11_clear_vaults_overlap_area':0,
 'old_object_blender_coordinates_identical_to_source_geojson':True,
 'original_R11_and_R13_unchanged':True,
 'classification_basis':'2D footprint subsets of R11 rebuilt masonry; no load path, area or capacity endorsement',
 'unresolved':['F5ZL-C support schedule not available.',
  'Q1-Q2 source support status labels do not independently certify approval.',
  'Two uppermost step footprints no longer fit R11 choir masonry envelope.',
  'Four other outer step/lower node footprints are partly outside R11 masonry envelope.',
  'Allocation lane geometry is historical reserve and must not be interpreted as current load-bearing masonry.',
  'Actual pier-bearing connectivity and arch springing cannot be certified from 2D footprints.',
  'Recent Q1-Q2 openings remain experimental, not approved.'],
 'future_step':'Review geometry registration/architectural decisions before designing new bearing footprints; no step 2 performed.'}
(OUT/'R14_Q1_Q2_SUPPORT_RECOVERY_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
(OUT/'README_HANDOFF.md').write_text("""# F5ZP R14-1 — recovery of saved Q1-Q2 support positions
Date: 2026-11-06
Status: **Experimental evidence and compatibility audit ONLY**. No modeling step 2 performed.

## Recovered sources
- Original saved R12C GeoJSON: ten named Q1-Q2 supports and ten allocation lanes.
- Saved original R12C Blender scene: 20 corresponding mesh objects, world-coordinate bounds match the GeoJSON 1:1.
- Current R11 rebuilt choir masonry and original 218 clear spaces, unchanged.
- R13 Option B seven candidate passage footprints, unchanged.

## Findings
- 2 Q1_Q2_major +/-1 ACCEPTED_800 and 2 Q1_Q2_step_132/133 ACCEPTED_STEP: **geometrically compatible**, fully within current R11 masonry and outside R13-B openings.
- 2 Q1_Q2_step_134/135 and 2 E_N/S_Lower node 3-3: **partially outside** current R11 rebuilt choir masonry.
- 2 Q1_Q2_step_136/137: **entirely outside** current R11 masonry.
- Original 10 ALLOCATION_LANE strips: **reference lanes only** (some crossed by shifted R11 vault cells); not actual support footprints.

All ten named source support polygons avoid both protected vault-clear spaces and R13-B proposed passage voids. Only four are entirely within the current R11 masonry reservation. The 235-wide visible core remains non-structural experiment.

## Scope and limits
Source names ACCEPTED_800 and ACCEPTED_STEP are not independent evidence of architectural approval. The saved Blender object's status is EXPERIMENTAL_R12C. The reference 2D alignment is checked, but no 3D bearing, structural or historical validation. Do not automatically resize/translate the six displaced footprints. F5ZL-C remains missing. No approved geometry changed.

## Reproduce
Run R14_Q1_Q2_SUPPORT_RECOVERY.py from the R12C workspace after the saved-Blender inventory is recovered; inventory generated by inspect_r12c_saved_blender.py using Blender 5.0.1. Exports editable source-footprint GeoJSON, SVG + PNG, classification CSV and QA JSON.
""")
with Image.open(png) as im:print('PNG VERIFIED',im.size);im.verify()
print('R14 STEP1 GENERATED','support categories',dict(counts),'rows',len(rows),'plot',png)