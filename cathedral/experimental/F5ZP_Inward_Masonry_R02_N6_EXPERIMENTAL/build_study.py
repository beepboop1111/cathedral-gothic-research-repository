#!/usr/bin/env python3
"""A bounded N6 clearance study; no approved source geometry is changed."""
from pathlib import Path
import csv, hashlib, json, xml.etree.ElementTree as ET, zipfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from shapely.geometry import box, mapping
from shapely.ops import unary_union

R=Path(__file__).resolve().parent
OUT=R/'outputs';OUT.mkdir(exist_ok=True)
SOURCE=R.parent/'F5ZP_Masonry_2D_R01_EXPERIMENTAL/inputs/F5ZE_GLOBAL_COORDINATES.json'
# Prefer bundled source after delivery; reference the prior package during initial build.
if (R/'inputs/F5ZE_GLOBAL_COORDINATES.json').exists(): SOURCE=R/'inputs/F5ZE_GLOBAL_COORDINATES.json'
raw=SOURCE.read_bytes();grid=json.loads(raw)
source_hash=hashlib.sha256(raw).hexdigest()
(R/'inputs').mkdir(exist_ok=True)
if SOURCE.parent != R/'inputs': (R/'inputs/F5ZE_GLOBAL_COORDINATES.json').write_bytes(raw)
assert grid['nave']['depths'][5]==3600
assert grid['radial_bands']['R3']-grid['radial_bands']['R2']==1536
C={'revision':'R02_N6_CLEARANCE_EXPERIMENT','status':'EXPERIMENTAL_NOT_A_PIER_DESIGN',
   'user_decision':'All masonry, shafts and bases stay outside reserved vault space',
   'source':'F5ZE native grid, N6 north outer aisle A3',
   'source_sha256':source_hash,'cell_length':1800,'cell_width':1536,
   'source_west_X':grid['nave']['x_stations'][5],
   'source_inner_Y':grid['radial_bands']['R2'],
   'trial_complete_support_envelopes':[320,480,640],
   'outer_respond_reservation':250,'perimeter_wall_thickness':320,
   'respond_reservation_status':'illustrative allowance, actual profile/base projection not recovered',
   'scope':'two clear outer-aisle cells; adjacent A2 edge anchored; no propagation',
   'semantics':'Original set-out sizes reused as clear reservations by user instruction, not historical proof of original floor clearance'}
(R/'CONFIG.json').write_text(json.dumps(C,indent=2)+'\n')
W,L=C['cell_width'],C['cell_length'];D=C['outer_respond_reservation'];T=C['perimeter_wall_thickness']
BLACK,GRAY,RED,TAN,BLUE='#242b30','#81898c','#b43c36','#dcc59f','#e2eff5'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})

def geometry(p):
    pitch=L+p;stations=[0,pitch,2*pitch]
    cells=[box(p/2+i*pitch,p,p/2+i*pitch+L,p+W) for i in range(2)]
    bases=[box(x-p/2,0,x+p/2,p) for x in stations]
    responds=[box(x-p/2,p+W,x+p/2,p+W+D) for x in stations]
    wall=box(-p/2,p+W+D,2*pitch+p/2,p+W+D+T)
    return stations,cells,bases,responds,wall

def dim(ax,a,b,label,vertical=False):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'|-|','lw':.65,'color':BLACK})
    ax.annotate(label,((a[0]+b[0])/2,(a[1]+b[1])/2),
                xytext=(-9,0) if vertical else (0,5),textcoords='offset points',
                rotation=90 if vertical else 0,ha='center',va='center' if vertical else 'bottom',fontsize=8,
                bbox={'facecolor':'white','edgecolor':'none','pad':1})

features=[];checks=[];rows=[]
def check(name,ok,**kw):checks.append({'check':name,'pass':bool(ok),**kw})
fig,axes=plt.subplots(1,3,figsize=(16,7.3))
fig.subplots_adjust(left=.055,right=.975,bottom=.27,top=.81,wspace=.27)
fig.text(.055,.945,'N6 NORTH OUTER AISLE  /  ALL MASONRY OUTSIDE THE VAULT RESERVATIONS',fontsize=14,weight='bold')
fig.text(.055,.902,'Two identical clear cells: 1800 × 1536. Only the space allocated around them changes.',fontsize=11)
for ax,p in zip(axes,C['trial_complete_support_envelopes']):
    stations,cells,bases,responds,wall=geometry(p)
    total=2*(L+p);cross=p+W+D+T
    row={'support_envelope':p,'clear_cell_length':L,'clear_cell_width':W,
         'cell_to_cell_pitch':L+p,'two_cell_module_between_end_support_centres':total,
         'increase_over_3600_reference_module':2*p,'allocated_inner_arcade_strip':p,
         'outer_respond_allowance':D,'outer_wall_thickness':T,
         'adjacent_A2_edge_to_outer_wall':cross,
         'outward_increase_over_R01_wall_position':p+D,
         'outer_wall_Y_if_A2_edge_anchored':C['source_inner_Y']+cross,
         'notional_east_end_support_X':C['source_west_X']+total,
         'full_three_support_review_extent_X':total+p,
         'status':'LOCAL_EXPERIMENT_NOT_APPLIED_TO_MASTER_PLAN'}
    rows.append(row)
    for i,cell in enumerate(cells):
        x,y,x2,y2=cell.bounds
        ax.add_patch(Rectangle((x,y),x2-x,y2-y,facecolor=BLUE,edgecolor=BLACK,lw=1))
        ax.text((x+x2)/2,(y+y2)/2,f'Cell {i+1}\n1800 × 1536\nCLEAR',ha='center',va='center',fontsize=9)
        features.append({'type':'Feature','properties':{'trial':p,'id':f'clear_cell_{i+1}','role':'CLEAR_RESERVATION'},'geometry':mapping(cell)})
        check(f'{p} cell {i+1} exact retained size',x2-x==L and y2-y==W)
    for kind,geoms in [('base_envelope',bases),('respond_envelope',responds),('wall',[wall])]:
        for j,g in enumerate(geoms):
            x,y,x2,y2=g.bounds
            ax.add_patch(Rectangle((x,y),x2-x,y2-y,facecolor=TAN if kind=='wall' else '#f4eadb',
                                   edgecolor=RED,lw=.9,ls='--'))
            features.append({'type':'Feature','properties':{'trial':p,'id':f'{kind}_{j}','role':'EXPERIMENTAL_RESERVATION'},'geometry':mapping(g)})
    # Support reservation strips are open arcade bays between individual footprints.
    for y in [0,p,p+W,p+W+D]:
        ax.plot([-p/2,total+p/2],[y,y],ls='--',color=GRAY,lw=.45,zorder=0)
    for x in stations:
        ax.plot([x,x],[-70,cross+100],color=GRAY,lw=.55,ls='--')
    ax.text(total/2,cross-T/2,'320 wall',ha='center',va='center',fontsize=8)
    ax.text((stations[0]+stations[1])/2,p+W+D/2,'250 respond allowance',ha='center',va='center',fontsize=7,color=RED)
    ax.text(total/2,p/2,'Open arcade between support envelopes',ha='center',va='center',fontsize=7,color=GRAY)
    dim(ax,(0,-300),(total,-300),f'{total} module = 3600 + {2*p}')
    dim(ax,(-p/2-210,0),(-p/2-210,cross),f'{cross} across allocated zone',True)
    ax.set(xlim=(-850,5700),ylim=(-550,3250),aspect='equal')
    ax.set_title(f'{p}-UNIT SUPPORT / BASE ENVELOPE',fontsize=10,pad=16)
    ax.axis('off')
    occupied=unary_union([*bases,*responds,wall]);clear=unary_union(cells)
    check(f'{p} no positive masonry intrusion',occupied.intersection(clear).area==0)
    check(f'{p} valid reservations',all(g.is_valid for g in [*cells,*bases,*responds,wall]))
    check(f'{p} shared gap equals one complete support envelope',cells[1].bounds[0]-cells[0].bounds[2]==p)
    check(f'{p} west support ends at first cell',bases[0].bounds[2]==cells[0].bounds[0])
    check(f'{p} internal support fills middle gap',bases[1].bounds[0]==cells[0].bounds[2] and bases[1].bounds[2]==cells[1].bounds[0])
    check(f'{p} wall outside respond allowance',wall.bounds[1]==responds[0].bounds[3])
    check(f'{p} module counts shared supports once',total==2*L+2*p)
fig.text(.055,.222,'HOW TO READ THIS',fontsize=10,weight='bold')
fig.text(.055,.18,'Blue = protected clear space. Red dashed = trial masonry envelopes, including the base.\nThe 250 outer respond allowance is illustrative; actual profiles still need fitting. No pier shape or capacity is asserted.',fontsize=9,linespacing=1.6)
fig.text(.055,.094,'Module lengths run between end-support centres: half an end support + 1800 + one shared support + 1800 + half an end support.\nThe full end supports are drawn for context; neighboring bays share them. Additional spacing is not a vault enlargement.',fontsize=9,linespacing=1.6)
fig.text(.055,.025,'EXPERIMENTAL • Native units, numerical 1:1. No approved vault coordinates, generators or masonry have been altered.',fontsize=9,color=RED)
fig.savefig(OUT/'N6_CLEAR_SPACE_COMPARISON.png',dpi=160,facecolor='white')
plt.close(fig)
(OUT/'PLAN_GEOMETRY.json').write_text(json.dumps({'type':'FeatureCollection','coordinates':'local X east Y north; not geodetic','features':features},indent=2)+'\n')
(OUT/'MEASUREMENTS.json').write_text(json.dumps(rows,indent=2)+'\n')
with (OUT/'MEASUREMENTS.csv').open('w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=rows[0]);wr.writeheader();wr.writerows(rows)
# One native-coordinate SVG per trial, generated from the same simple rectangles.
for p in C['trial_complete_support_envelopes']:
    fs=[f for f in features if f['properties']['trial']==p]
    root=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','viewBox':'-850 -3250 6550 3800',
                         'width':'1400','height':'812','data-units':'one SVG user unit per native project unit'})
    ET.SubElement(root,'title').text=f'N6 clear-space trial {p}; unapproved masonry envelopes'
    grp=ET.SubElement(root,'g',{'transform':'scale(1,-1)'})
    for f in fs:
        pts=f['geometry']['coordinates'][0];fixed=f['properties']['role']=='CLEAR_RESERVATION'
        at={'points':' '.join(f'{x},{y}' for x,y in pts),'id':f['properties']['id'],
            'fill':BLUE if fixed else TAN,'stroke':BLACK if fixed else RED,'stroke-width':'1',
            'vector-effect':'non-scaling-stroke'}
        if not fixed:at['stroke-dasharray']='6 4'
        ET.SubElement(grp,'polygon',at)
    ET.ElementTree(root).write(OUT/f'N6_TRIAL_{p}_NATIVE.svg',encoding='unicode',xml_declaration=True)
    ET.parse(OUT/f'N6_TRIAL_{p}_NATIVE.svg')
check('source bytes unchanged',hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash)
saved=json.loads((OUT/'PLAN_GEOMETRY.json').read_text())
check('exported feature count',len(saved['features'])==len(features)==27)
check('exported geometry round trip',saved['features']==json.loads(json.dumps(features)))
qa={'result':'PASS' if all(c['pass'] for c in checks) else 'FAIL','passed':sum(c['pass'] for c in checks),'total':len(checks),
    'checks':checks,'validation_scope':'technical and 2D rectangular reservation geometry only; no architectural/historical/structural approval'}
(OUT/'QA.json').write_text(json.dumps(qa,indent=2)+'\n')
assert qa['result']=='PASS',qa
print(json.dumps({'result':qa['result'],'checks':f"{qa['passed']}/{qa['total']}",'trials':rows},indent=2))
