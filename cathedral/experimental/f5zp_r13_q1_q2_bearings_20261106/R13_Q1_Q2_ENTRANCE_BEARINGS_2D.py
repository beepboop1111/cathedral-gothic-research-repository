#!/usr/bin/env python3
"""F5ZP R13 Q1-Q2 entrance and bearing experimental 2D alternatives.
Immutable R11 geometry; no architectural promotion or structural certification.
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
R11=ROOT/'R11_FULL_COORDINATED_2D_EXPERIMENTAL'/'F5ZP_R11_COORDINATED_NATIVE_2D.geojson'
R12=ROOT/'R12_GRADUAL_CHOIR_TRANSITION_EXPERIMENTAL'/'R12_STUDY_QA.json'
OUT=ROOT/'R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL'
OUT.mkdir(exist_ok=True)
src=R11.read_bytes();data=json.loads(src)
assert json.loads(R12.read_text())['r11_sha256']==hashlib.sha256(src).hexdigest()
clear={f['properties']['id']:shape(f['geometry']) for f in data['features'] if f['properties'].get('role')=='CLEAR'}
masonry={f['properties']['id']:shape(f['geometry']) for f in data['features'] if f['properties'].get('role')=='RESERVED_MASONRY'}
assert all(g.is_valid for g in clear.values())
choir=masonry['CHOIR_MASONRY_R10']
allclear=unary_union(list(clear.values()))
refs=[f for f in data['features'] if f['properties'].get('role') not in ('CLEAR','RESERVED_MASONRY')]
roi=box(3850,-8300,5140,8300)
oldnear=[(f['properties']['id'],shape(f['geometry'])) for f in refs if shape(f['geometry']).intersects(roi)]
baseline_r11_area=sum(g.area for g in clear.values())
mainA,mainB=clear['Q1'],clear['Q2_MAIN']
assert (mainA.bounds[2],mainB.bounds[0])==(3925.0,5085.0)
xmain=(mainA.bounds[2]+mainB.bounds[0])/2
assert xmain==4505
# Exact bounds across all six Q1-Q2 paired aisle cells (not equal at outer rows).
aisles=[]
for s in 'NS':
    for row in (1,2,3):
        west=clear[f'E_{s}_J1 R{row}C3'];east=clear[f'Q2_{s}_A{row}_1']
        xa,xb=west.bounds[2],east.bounds[0]
        ya,yb=max(west.bounds[1],east.bounds[1]),min(west.bounds[3],east.bounds[3])
        assert xb-xa==470. and yb>ya
        aisles.append(dict(id=f'{s}_A{row}',side=s,layer=row,xw=xa,xe=xb,ys=ya,yn=yb,
                           west_id=f'E_{s}_J1 R{row}C3',east_id=f'Q2_{s}_A{row}_1'))
# All proposed opening shapes touch both existing vaults but do NOT change either vault polygon.
options=[
 dict(id='A_CONSERVATIVE',label='A • Conservative bearings',
      main_shoulder=440,aisle_shoulders=(200,210,240),
      description='Thicker jamb margins. More reserved masonry; narrower aisle passages.'),
 dict(id='B_BALANCED',label='B • Gradual processional threshold',
      main_shoulder=360,aisle_shoulders=(160,160,220),
      description='Passages with generous transverse bearing bands; 235-wide visual respond emphasis.'),
 dict(id='C_OPEN',label='C • Maximum visual openness',
      main_shoulder=280,aisle_shoulders=(120,120,120),
      description='Wider passages; legacy support overlaps and lower local margins require correction.')]
# Transverse bands are based on actual adjacent vault row heights; inner two
# levels are exact; third has a staggered edge across east and west clear cells.
bands=[(2933,3253),(4405,4602),(5946,6194.5),(7774,8094)]
concept_core=box(xmain-117.5,-8100,xmain+117.5,8100)
def core_visual(retained):
    b=[]
    for lo,hi in bands[:3]:
        for s in (-1,1):
            y0,y1=(lo,hi) if s==1 else (-hi,-lo)
            z=retained.intersection(concept_core).intersection(box(4150,y0,4900,y1))
            if z.area>1e-4:b.append(z)
    return unary_union(b)
rows=[];models={};out_summary=[]
for option in options:
    name=option['id'];openings=[]
    main_margin=option['main_shoulder']
    main=box(mainA.bounds[2],-2933+main_margin,mainB.bounds[0],2933-main_margin)
    openings.append(dict(id='MAIN',side='C',layer=0,polygon=main,span=main.bounds[3]-main.bounds[1],
                         passage_depth=1160.,shoulder=main_margin,
                         west_id='Q1',east_id='Q2_MAIN'))
    for record in aisles:
        shoulder=option['aisle_shoulders'][record['layer']-1]
        op=box(record['xw'],record['ys']+shoulder,record['xe'],record['yn']-shoulder)
        assert op.area>0
        openings.append({**record,'polygon':op,'span':op.bounds[3]-op.bounds[1],
                         'passage_depth':470.,'shoulder':shoulder})
    voids=unary_union([p['polygon'] for p in openings])
    assert voids.is_valid
    # Explicit technical feasibility: one connected clear entrance for each pair;
    # no change to source R11 clear vault polygon, no cutting outside reserved masonry.
    assert all(p['polygon'].difference(choir).area<.0001 for p in openings)
    assert all(p['polygon'].intersection(allclear).area<.0001 for p in openings)
    assert len(openings)==7
    for p in openings:
        oa,ob=clear[p['west_id']],clear[p['east_id']]
        # Flat opening faces share measurable border segments with original clear vaults.
        west_contact=p['polygon'].boundary.intersection(oa.boundary).length
        east_contact=p['polygon'].boundary.intersection(ob.boundary).length
        assert west_contact>p['span']-.00001,(name,p['id'],'west',west_contact,p['span'])
        assert east_contact>p['span']-.00001,(name,p['id'],'east',east_contact,p['span'])
        p['west_contact']=west_contact;p['east_contact']=east_contact
    remaining=choir.difference(voids)
    assert remaining.is_valid
    assert remaining.intersection(allclear).area<.0001
    assert abs(choir.area-remaining.area-voids.area)<.01
    # Original R11 support patches are unregistered; compare as collision warnings,
    # not as authorities that the variant silently "repairs."
    collisions=[]
    for label,g in oldnear:
        a=g.intersection(voids).area
        if a>.00001:collisions.append({'reference':label,'area':round(a,3)})
    core=core_visual(remaining)
    assert core.is_valid
    assert core.intersection(voids).area<.00001
    assert core.difference(remaining).area<.00001
    # Geometric support remains around each opened aperture; margins are measurable
    # 2D space only, not structurally tested bearing.
    clearance=[]
    for p in openings:
        rc=dict(option=name,passage=p['id'],side=p['side'],layer=p['layer'],
          span_native=p['span'],depth_native=p['passage_depth'],
          jamb_each_side_native=p['shoulder'],
          opening_area_native2=p['polygon'].area,
          west_vault_contact=p['west_contact'],
          east_vault_contact=p['east_contact'],
          status='EXPERIMENTAL_PASSAGE_NOT_STRUCTURALLY_VALIDATED')
        rows.append(rc);clearance.append(rc)
    # Test material between adjacent openings; these y distances are actual
    # continuous masonry band dimensions between opening edges.
    n=[p for p in openings if p['side']=='N']
    n.sort(key=lambda p:p['polygon'].bounds[1])
    upper_gaps=[n[i+1]['polygon'].bounds[1]-n[i]['polygon'].bounds[3]
                for i in range(len(n)-1)]
    assert min(upper_gaps)>0,(name,upper_gaps)
    central=next(p for p in openings if p['id']=='MAIN')
    central_to_n=n[0]['polygon'].bounds[1]-central['polygon'].bounds[3]
    assert central_to_n>0
    out_summary.append({'option':name,'main_clear_width':central['span'],
        'aisle_clear_widths':[p['span'] for p in n],
        'aisle_jamb_each':list(option['aisle_shoulders']),
        'main_jamb_each':main_margin,'major_to_A1_solid_band':central_to_n,
        'A1_A2_solid_band':upper_gaps[0],'A2_A3_solid_band':upper_gaps[1],
        'legacy_support_reference_collisions':collisions,
        'removed_masonry_area':voids.area,
        'legacy_pier_reference_notes':'Old R12C support overlays unregistered at revised bays',
        'no_intrusion_into_original_clear_polygons':True,
        'masonry_remainder_valid':remaining.is_valid})
    models[name]=dict(openings=openings,voids=voids,solid=remaining,
                      core=core,collisions=collisions,params=option)
    print(name,'clear',central['span'],[p['span'] for p in n],
          'bands',central_to_n,*upper_gaps,'old support overlaps',collisions)
assert all(shape(mapping(item)).is_valid for m in models.values() for item in (m['solid'],m['core']))
# Export standalone alternative reserved-solid and true opening layers. Do not
# mix these proposed openings into the historical/approved R11 authority.
features=[]
for name,m in models.items():
    for p in m['openings']:
        features.append({'type':'Feature','properties':{
          'id':name+'_'+p['id']+'_PASSAGE','variant':name,'layer':'EXPERIMENTAL_PASSAGE_VOID',
          'span':p['span'],'wall_depth':p['passage_depth'],
          'jamb_each':p['shoulder']},'geometry':mapping(p['polygon'])})
    features.append({'type':'Feature','properties':{
        'id':name+'_CHOIR_REMAINING_MASONRY','variant':name,
        'layer':'EXPERIMENTAL_REMAINING_CHOIR_MASONRY'},
         'geometry':mapping(m['solid'])})
    features.append({'type':'Feature','properties':{
        'id':name+'_235_RESPOND_FACE_VISUAL_ONLY','variant':name,
        'layer':'EXPERIMENTAL_235_VISUAL_ARTICULATION_NOT_SUPPORT'},
         'geometry':mapping(m['core'])})
fpath=OUT/'R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson'
fpath.write_text(json.dumps({'type':'FeatureCollection','properties':{
     'source':str(R11),'source_sha256':hashlib.sha256(src).hexdigest(),
     'native_1to1':True,'not_approved_or_structurally_validated':True},
    'features':features},separators=(',',':'))+'\n')
with (OUT/'R13_PASSAGE_CLEARANCES.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Rendering: three identical north-half plan frames, one full symmetric context
def draw(ax,g,fc,ec='#455461',lw=.4,alpha=1,z=3,holes=True):
    if g.is_empty:return
    polys=[g] if g.geom_type=='Polygon' else [v for v in getattr(g,'geoms',[]) if v.geom_type=='Polygon']
    for poly in polys:
        ax.add_patch(PlotPoly(list(poly.exterior.coords),facecolor=fc,edgecolor=ec,lw=lw,alpha=alpha,zorder=z))
        if holes and fc!='none':
            for inn in poly.interiors:
                ax.add_patch(PlotPoly(list(inn.coords),facecolor='#fffefa',edgecolor='none',zorder=z+.1))
def panel(ax,option,xlim=(3100,5650),ylim=(-100,8130),label=True):
    m=models[option]
    draw(ax,m['solid'],'#c6ae91','#886c52',.4)
    for key,g in clear.items():
        if g.bounds[2]<xlim[0] or g.bounds[0]>xlim[1]:continue
        if key=='Q1' or key=='Q2_MAIN': fc='#dfe8e2'
        elif key.startswith(('Q2_','E_')):fc='#e3efe9'
        else:continue
        draw(ax,g,fc,'#456478',.55,z=5)
    for p in m['openings']:draw(ax,p['polygon'],'#abd8eb','#36799a',.5,z=7)
    draw(ax,m['core'],'#ae6d47','none',.0,z=9)
    # The main separator axis is a shared reference, not the old aisle axis.
    ax.axvline(xmain,color='#8e4c38',ls='--',lw=.75,zorder=10)
    if label:
        ax.text(xmain,2850,'520/270 axes different from Q1 special junction',
            ha='center',fontsize=7,rotation=90,color='#764a3d',va='top')
    ax.set_xlim(*xlim);ax.set_ylim(*ylim);ax.set_aspect('equal','box')
    ax.grid(alpha=.1);ax.set_xlabel('X native units');ax.set_ylabel('Y native units')
fig,axes=plt.subplots(1,3,figsize=(17.5,13),facecolor='white')
for ax,o in zip(axes,options):
    panel(ax,o['id'])
    summ=next(s for s in out_summary if s['option']==o['id'])
    ax.set_title(o['label']+'\n'+
          'Main '+str(summ['main_clear_width'])+'  |  Aisles '+', '.join(str(round(v)) for v in summ['aisle_clear_widths']),
          loc='left',fontsize=10.2,weight='bold',pad=13)
    if summ['legacy_support_reference_collisions']:
        ax.text(3450,7900,'CAUTION: intersects old support overlay',fontsize=8,color='#b14b3d',weight='bold')
fig.suptitle('F5ZP  R13   Q1–Q2 ENTRANCE & BEARING ARRANGEMENTS — EXPERIMENTAL 2D\n'
    'Same protected vault footprints in all three alternatives • north half shown',
    x=.055,y=.969,ha='left',fontsize=16,weight='bold',color='#2d424a')
fig.legend(handles=[Patch(facecolor='#c6ae91',label='Retained experimental masonry'),
   Patch(facecolor='#e3efe9',label='R11 unmodified clear vault'),
   Patch(facecolor='#abd8eb',label='Proposed clear passage'),
   Patch(facecolor='#ae6d47',label='235-unit visible respond concept, not structural proof'),
   Line2D([0],[0],color='#8e4c38',ls='--',label='Q1-Q2 main separator axis')],
  loc='lower center',bbox_to_anchor=(.5,.056),ncol=3,fontsize=9,frameon=False)
fig.text(.055,.025,'Main gap remains 1160; aisle gap 470; 235 is facade articulation only. C overlaps unregistered old step supports; all require architectural and structural review.',
  fontsize=9.4,color='#8a4b42')
fig.subplots_adjust(left=.045,right=.985,bottom=.11,top=.885,wspace=.27)
compare=OUT/'F5ZP_R13_Q1_Q2_THREE_ENTRANCE_ALTERNATIVES.png'
fig.savefig(compare,dpi=185,bbox_inches='tight')
fig.savefig(OUT/'F5ZP_R13_Q1_Q2_THREE_ENTRANCE_ALTERNATIVES.svg',bbox_inches='tight')
plt.close(fig)
# Two synchronized B detail views show passage alignment on BOTH sides and north detail
fig,axes=plt.subplots(1,2,figsize=(14.5,11.3),facecolor='white')
panel(axes[0],'B_BALANCED',xlim=(2700,7100),ylim=(-8140,8140),label=False)
axes[0].set_title('B1 | Full north + south entrance / bearing plan',loc='left',fontsize=11,weight='bold')
panel(axes[1],'B_BALANCED',xlim=(3900,5140),ylim=(2620,7990),label=False)
axes[1].set_title('B2 | Three northern openings and separator nodes',loc='left',fontsize=11,weight='bold')
for p in models['B_BALANCED']['openings']:
    if p['side']=='S':continue
    b=p['polygon'].bounds
    axes[1].text((b[0]+b[2])/2,(b[1]+b[3])/2,
        str(round(p['span']))+' opening',fontsize=7.9,ha='center',va='center',color='#225875',weight='bold',rotation=90)
axes[0].text(4505,100,'235 visual\ncenterline',fontsize=9,color='#9e6949',ha='center',rotation=90)
fig.suptitle('F5ZP  R13-B  |  PROCESSIONAL THRESHOLD — 2D CANDIDATE\n'
      'Six aisle openings + one main opening • 235 visible cores inside retained support bands',
      x=.045,y=.96,ha='left',fontsize=15.7,weight='bold')
fig.text(.045,.03,'Bearings shown are only reserved planar material; load paths, voussoirs, arch springing and opening feasibility remain unresolved.',
         fontsize=9.3,color='#8a4b42')
fig.tight_layout(rect=(0,.06,1,.9),w_pad=2)
detail=OUT/'F5ZP_R13_OPTION_B_NORTH_SOUTH_PLAN.png'
fig.savefig(detail,dpi=195,bbox_inches='tight')
fig.savefig(OUT/'F5ZP_R13_OPTION_B_NORTH_SOUTH_PLAN.svg',bbox_inches='tight')
plt.close(fig)
# Saved checks include actual boundary contacts and exact original source digest
report={
 'status':'EXPERIMENTAL 2D PASSAGE AND BEARING OPTIONS; NOT APPROVED',
 'input':str(R11),'R11_SHA256':hashlib.sha256(src).hexdigest(),
 'R11_feature_count':len(data['features']),
 'original_vault_count':len(clear),'original_vault_area_sum':baseline_r11_area,
 'source_vaults_changed':False,'Q1_Q2_main_separator_axis_x':xmain,
 'Q1_Q2_main_gap_native':1160,'Q1_Q2_aisle_gap_native':470,
 'Q1_Q2_aisle_axis_offset_from_main_native':-25,
 'virtual_visible_core_width_native':235,
 'summary':out_summary,
 'technical_checks':{'7_passages_per_option':True,
 'each_opening_touches_west_and_east_source_vault_faces':True,
 'all_voids_within_existing_R11_choir_masonry':True,
 'all_original_vault_intersection_areas':0,
 'R11_original_geojson_unchanged_SHA256':hashlib.sha256(R11.read_bytes()).hexdigest(),
 'all_cut_masonry_valid':True,
 '235_visual_respond_only_on_existing_material':True},
 'source_uncertainties':[
  'Old R12C support refs are not registered to current R11 adjusted cells; collision flags are indicative.',
  'F5ZL-C support schedule remains missing.',
  'Native project scale 1:1; physical conversion unresolved.',
  'No verified historic arch section or structural jamb/support capacity.',
  'These openings remove experimental reserved masonry only in alternative models; not in R11 baseline.'
 ]}
(OUT/'R13_NUMERICAL_QA.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'README_HANDOFF.md').write_text("""# F5ZP R13 — Q1–Q2 entrance and bearing study (2D)
Status **experimental, not approved**. R11 vault coordinates immutable. No actual masonry openings approved.

## Real R11 geometry
Main Q1–Q2 clear gap x3925..5085 = 1160; main axis x4505.
All six aisle gaps x4245..4715 = 470; aisle axis x4480, 25 west of main.
Aisle overlap y widths: A1 1152; A2 1315; A3 1474. Six symmetric north/south passages.
Existing transverse masonry schedule stays 320 / 197 / 292. Chevet stays radial.

## Three independent opening alternatives
A Conservative: sanctuary jambs 440, aisle jambs [200,210,240].
B Balanced: sanctuary jambs 360, aisle jambs [160,160,220].
C Open: sanctuary jambs 280, aisle jambs [120,120,120].
Opening widths = minimum overlapping vault-row span minus twice jamb width.
All openings entirely inside existing R11 masonry reservations, and meet adjacent Q1 and Q2 clear vault faces.
The 235-wide visible respond is shown ONLY within retained transverse support bands, NOT as a load-bearing design.
C intersects original R12C unregistered step-support reference; it is flagged for rejection/rework, not approved.

## Interpretations and limits
Geometric collision/adjacency checks are necessary but do not prove actual support capacity, architectural coherence, structural adequacy, or historic plausibility. Old support reference polygons are not governing approved positions. No pier, pointed arch profile, or section designed in this 2D pass. The 1160/470 geometry itself remains provisional and must be reviewed before any protected change.

## Reproduce
Run python3 R13_Q1_Q2_ENTRANCE_BEARINGS_2D.py from the R12C workspace.
R11 and R12 outputs are read-only. Reusable data and QA included.
""")
with Image.open(compare) as im:im.verify()
with Image.open(detail) as im:im.verify()
print('DELIVERED',compare,detail,'features',len(features),'rows',len(rows),
      'R11 source unchanged',hashlib.sha256(src).hexdigest()==hashlib.sha256(R11.read_bytes()).hexdigest())