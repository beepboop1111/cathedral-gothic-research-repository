#!/usr/bin/env python3
"""Reproducible 1:1 plan reservations. Reads snapshots; writes outputs only.

Run: python build_masonry_study.py
Dependencies: numpy, shapely>=2, matplotlib. No Blender or cathedral generator.
"""
from pathlib import Path
import csv, hashlib, json, math, platform, xml.etree.ElementTree as ET
import numpy as np
import shapely
from shapely.geometry import Polygon, LineString, box, mapping
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, Polygon as MplPolygon

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)
CFG = json.loads((ROOT/'CONFIG.json').read_text())
SRC = json.loads((ROOT/'inputs/RECOVERED_SOURCE_EXTRACT.json').read_text())
GRID = SRC['F5ZE_GLOBAL_COORDINATE_DATA.json']['data']
R07 = SRC['R07_CURRENT_PLAN_GEOMETRY.json']['data']
COMPACT = json.loads((ROOT/'inputs/R07_PLAN_CELLS_COMPACT.json').read_text())
CELLS = SRC['cells']
BLACK, GRAY, RED = '#242b30', '#7d858a', '#b43c36'
BLUE, GREEN, TAN = '#e2eff5', '#e6efdf', '#d9bc8b'
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10,
                     'svg.fonttype':'none', 'axes.spines.top':False,
                     'axes.spines.right':False})

def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def parts(geom):
    if geom.geom_type == 'Polygon':
        yield geom
    elif hasattr(geom, 'geoms'):
        for g in geom.geoms:
            yield from parts(g)

def draw_geom(ax, geom, face='none', edge=BLACK, lw=.9, ls='-', alpha=1):
    for p in parts(geom):
        # Shapely orients the rings differently when necessary; use explicit orientation.
        p = shapely.geometry.polygon.orient(p, sign=1)
        vs, cs = [], []
        for ring in [p.exterior, *p.interiors]:
            pts = list(ring.coords)
            vs.extend(pts)
            cs.extend([MplPath.MOVETO]+[MplPath.LINETO]*(len(pts)-2)+[MplPath.CLOSEPOLY])
        ax.add_patch(PathPatch(MplPath(vs,cs),facecolor=face,edgecolor=edge,
                               linewidth=lw,linestyle=ls,alpha=alpha))

def dimension(ax, a, b, label, offset=(0,0), fontsize=9, color=BLACK):
    a,b=np.array(a,float),np.array(b,float)
    off=np.array(offset,float)
    q,r=a+off,b+off
    for p,z in [(a,q),(b,r)]:
        ax.plot([p[0],z[0]],[p[1],z[1]],color=GRAY,lw=.55)
    ax.annotate('',xy=r,xytext=q,arrowprops={'arrowstyle':'|-|','lw':.7,'color':color})
    c=(q+r)/2
    vertical=abs(r[1]-q[1])>abs(r[0]-q[0])
    ax.annotate(label,c,xytext=(-9,0) if vertical else (0,6),textcoords='offset points',ha='center',
                va='center' if vertical else 'bottom',rotation=90 if vertical else 0,fontsize=fontsize,color=color,
                bbox={'facecolor':'white','edgecolor':'none','pad':1.5})

def finish(fig, stem):
    fig.savefig(OUT/(stem+'.png'), dpi=170, facecolor='white')
    fig.savefig(OUT/(stem+'_SHEET.svg'), facecolor='white')
    plt.close(fig)

def make_geometry():
    west=GRID['nave']['x_stations_west_to_crossing'][0]
    center=GRID['choir']['chevet_center'][0]
    half=GRID['crossing']['half_width']
    outer=GRID['radial_lines']['R3']
    end=CFG['choir_outer_preview']['end_half_width']
    terminal=GRID['transepts']['terminal_abs']
    nave=box(west,-outer,-half,outer)
    crossing=box(-half,-half,half,half)
    # Only the central transept width is represented; side complexes are unverified.
    transept=box(-half,-terminal,half,terminal)
    choir=Polygon([(half,-outer),(center,-end),(center,end),(half,outer)])
    main=unary_union([nave,crossing,transept,choir])
    h=R07['r03_geometry']['half_width']
    x0=R07['r03_geometry']['threshold'][0]
    apx=R07['r03_geometry']['apse_west_x']
    apse=[[apx+h*math.cos(math.radians(t)),h*math.sin(math.radians(t))]
          for t in R07['r03_geometry']['apse_angles_degrees']]
    chapel=Polygon([(x0,-h),*apse,(x0,h)])
    vaults={k:Polygon(v['vertices']) for k,v in CELLS.items()}
    reservations=unary_union([main,chapel,*vaults.values()])
    return main,nave,choir,chapel,vaults,reservations

MAIN,NAVE,CHOIR,CHAPEL,VAULTS,RESERVED=make_geometry()

def main_wall(t):
    # Open east join; no spurious wall across the sanctuary/ambulatory connection.
    x=GRID['choir']['chevet_center'][0]
    return MAIN.buffer(t,join_style=2).difference(MAIN).intersection(box(-1e6,-1e6,x,1e6))

def chapel_wall(t):
    # Mitred polygonal apse: perpendicular offsets, not radial vertex scaling.
    x=R07['r03_geometry']['threshold'][0]
    return CHAPEL.buffer(t,join_style=2).difference(CHAPEL).intersection(box(x,-1e6,1e6,1e6))

def feature(name, geom, status, **kw):
    return {'type':'Feature','properties':{'id':name,'status':status,**kw},
            'geometry':mapping(geom)}

def native_svg(stem, features, bounds):
    """SVG geometry uses numerical project units without physical-unit claims."""
    xmin,ymin,xmax,ymax=bounds
    root=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg',
                          'viewBox':f'{xmin} {-ymax} {xmax-xmin} {ymax-ymin}',
                          'width':'1800','height':str(round(1800*(ymax-ymin)/(xmax-xmin))),
                          'data-coordinate-system':'X east, Y north; group reflects SVG Y',
                          'data-units':'native project units; 1 SVG user unit = 1 project unit'})
    ET.SubElement(root,'title').text='F5ZP masonry study R01 — experimental plan reservations'
    ET.SubElement(root,'desc').text='Confirmed reference black; construction gray; proposed/uncertain red dashed. No structural approval.'
    ET.SubElement(root,'rect',{'x':str(xmin),'y':str(-ymax),'width':str(xmax-xmin),
                             'height':str(ymax-ymin),'fill':'white'})
    g=ET.SubElement(root,'g',{'transform':'scale(1,-1)'})
    for name,geom,status,fill in features:
        group=ET.SubElement(g,'g',{'id':name,'data-status':status})
        for i,p in enumerate(parts(geom)):
            rings=[p.exterior,*p.interiors]
            d=' '.join('M '+' L '.join(f'{x:.12g},{y:.12g}' for x,y in r.coords)+' Z' for r in rings)
            attr={'d':d,'fill':fill,'fill-rule':'evenodd','stroke':BLACK if status=='REFERENCE' else RED,
                  'stroke-width':'1','vector-effect':'non-scaling-stroke'}
            if status!='REFERENCE':attr['stroke-dasharray']='6 4'
            ET.SubElement(group,'path',attr)
    ET.ElementTree(root).write(OUT/(stem+'.svg'),encoding='unicode',xml_declaration=True)

def whole_plan(wm,wc):
    fig=plt.figure(figsize=(18,9.2))
    fig.text(.045,.95,'F5ZP  /  MASONRY R01     WHOLE-CATHEDRAL RESERVATION STUDY',weight='bold',fontsize=17)
    fig.text(.045,.915,'Proposed: 320 main perimeter + 250 axial chapel. Reserved vault geometry and station chain stay fixed.',fontsize=11)
    ax=fig.add_axes([.045,.265,.925,.60])
    draw_geom(ax,MAIN,'#f5f7f7',GRAY,.6)
    draw_geom(ax,wm,TAN,RED,.85,'--')
    # Unverified choir interpolation remains an uncertainty on the overview.
    for sign in [-1,1]:
        ax.plot([2933,20213],[sign*6965,sign*6657],color=RED,ls='--',lw=1.15)
    for k,p in VAULTS.items():
        draw_geom(ax,p,BLUE if k.startswith('I') else GREEN,BLACK,.6)
    draw_geom(ax,CHAPEL,'#fff5e7',BLACK,.8)
    draw_geom(ax,wc,TAN,RED,.9,'--')
    nav=GRID['nave']['x_stations_west_to_crossing']
    for i,(a,b) in enumerate(zip(nav[:-1],nav[1:]),1):
        ax.plot([a,a],[-6965,6965],color=GRAY,lw=.55,ls='--')
        ax.text((a+b)/2,0,'N'+str(i),ha='center',va='center',fontsize=8)
    for sign in [-1,1]:
        for y in [2933,4085,5429]:
            ax.plot([nav[0],-2933],[sign*y]*2,color=BLACK,lw=.55)
        for y in [2933,4085]:
            ax.plot([2933,20213],[sign*y]*2,color=BLACK,lw=.55)
    for i,(a,b) in enumerate(zip(GRID['choir']['x_stations_crossing_to_chevet'][:-1],
                                 GRID['choir']['x_stations_crossing_to_chevet'][1:]),1):
        ax.plot([a,a],[-6500,6500],color=GRAY,lw=.5,ls='--')
        ax.text((a+b)/2,0,'Q'+str(i),ha='center',va='center',fontsize=8)
    ax.text(0,0,'CR\n5866',ha='center',va='center',fontsize=8)
    for sign in [-1,1]:
        for a,b,l in [(2933,6965,'T1'),(6965,10709,'T2')]:
            ax.text(0,sign*(a+b)/2,l,ha='center',va='center',fontsize=8)
        ax.plot([-2933,2933],[sign*6965]*2,color=GRAY,lw=.5,ls='--')
    for a,b in COMPACT['r06']:
        ax.plot([a[0],b[0]],[a[1],b[1]],color=GRAY,lw=.75,ls='--')
    for x in [28000,28600,31000,33400]:
        ax.plot([x,x],[-1250,1250],color=GRAY,lw=.6,ls='--')
    ax.annotate('R07 axial chapel\n2 × 2400 + apse',xy=(31500,1500),xytext=(31000,6200),
                ha='center',fontsize=9,arrowprops={'arrowstyle':'-','lw':.7,'color':GRAY})
    ax.annotate('Eastern shoulder / outer enclosure\nnot resolved: no closure invented',xy=(23500,-5500),
                xytext=(28400,-9700),ha='center',fontsize=8,color=RED,
                arrowprops={'arrowstyle':'-','color':RED,'lw':.7})
    ax.annotate('29-unit R2 source discrepancy\nretained; no averaged junction',xy=(2933,5429),
                xytext=(10000,10000),ha='center',fontsize=8,color=RED,
                arrowprops={'arrowstyle':'-','color':RED,'lw':.7})
    dimension(ax,(-40013,-10709),(34588.82064536894,-10709),'Reference axial reach 74,601.821',offset=(0,-2400),fontsize=9)
    ax.annotate('N',xy=(-37600,11000),xytext=(-37600,8000),ha='center',weight='bold',
                arrowprops={'arrowstyle':'->','lw':1})
    ax.set(xlim=(-43000,36600),ylim=(-15000,13500),aspect='equal')
    ax.set_xlabel('X east — native project units');ax.set_ylabel('Y north')
    ax.tick_params(labelsize=8)
    notes=[('FIXED RESERVATIONS','Nave width 13,930 → enclosure 14,570 (+640)\nTransept terminal reach 21,418 → 22,058 (+640)\nAxial chapel width 2,500 → 3,000 (+500)'),
           ('FOOTPRINT EFFECT','Reference west-to-apse reach 74,601.821\nProposed reach 75,171.821 (+570 / +0.764%)\nExcludes towers, buttresses, porches and unknown shoulders.'),
           ('DRAWING LIMITS','Tan = proposed wall reservation; red dashed = unapproved.\nChoir outer taper is an endpoint-based preview only.\nTransept cores only; no new internal pier sizes or walls.')]
    for x,(h,t) in zip([.045,.365,.685],notes):
        fig.text(x,.19,h,fontsize=10,weight='bold')
        fig.text(x,.155,t,fontsize=9,linespacing=1.6,va='top')
    fig.text(.045,.035,'EXPERIMENTAL • Numerical 1:1. Physical metre conversion unresolved. Wall bands precede opening and bearing design.',fontsize=9,color=RED)
    finish(fig,'01_WHOLE_CATHEDRAL_MASONRY')

def chapel_comparison():
    fig,axes=plt.subplots(3,1,figsize=(12,14))
    fig.subplots_adjust(left=.065,right=.94,top=.88,bottom=.08,hspace=.28)
    fig.suptitle('AXIAL CHAPEL  /  OUTWARD MASONRY COMPARISON',x=.065,ha='left',fontsize=17,weight='bold',y=.965)
    fig.text(.065,.92,'The black 2,500-wide reserved space and both 2,400-long bays are identical in every trial.',fontsize=11)
    for ax,t in zip(axes,CFG['trial_thicknesses']):
        w=chapel_wall(t)
        draw_geom(ax,CHAPEL,'#fff8ed',BLACK,1)
        draw_geom(ax,w,TAN,RED,1,'--')
        for x in [28000,28600,31000,33400]:
            ax.plot([x,x],[-1250,1250],color=GRAY,ls='--',lw=.65)
        for x,label in [(28300,'600\nthreshold'),(29800,'2400\nBay 1'),(32200,'2400\nBay 2')]:
            ax.text(x,0,label,ha='center',va='center',fontsize=9)
        ax.text(33850,0,'five-facet\napse',ha='center',va='center',fontsize=8)
        dimension(ax,(28600,-1250),(28600,1250),'2500 fixed',offset=(-1250,0),fontsize=9)
        dimension(ax,(32200,-1250-t),(32200,1250+t),f'{2500+2*t} outside',offset=(3500,0),fontsize=9,color=RED)
        ax.set_title(f't = {t} outward  |  width +{2*t}  |  apse nose X{CHAPEL.bounds[2]+t:,.3f}',loc='left',fontsize=10)
        ax.set(xlim=(26900,36500),ylim=(-1750,1750),aspect='equal')
        ax.axis('off')
    fig.text(.065,.035,'170 = recovered R03 chapel-wall parameter; original threshold returns were 250. All trials here use a uniform plan band. No entrance cap.',fontsize=9,color=GRAY)
    finish(fig,'02_AXIAL_CHAPEL_THICKNESS_COMPARISON')

def space_rules():
    fig=plt.figure(figsize=(16,9))
    fig.text(.055,.945,'RESERVED SPACE FIRST  /  MASONRY ADDS OUTWARD',fontsize=17,weight='bold')
    ax=fig.add_axes([.07,.48,.86,.35])
    bands=[-6965,-5429,-4085,-2933,2933,4085,5429,6965]
    labels=['1536','1344','1152','5866','1152','1344','1536']
    for i,(a,b) in enumerate(zip(bands[:-1],bands[1:])):
        draw_geom(ax,box(a,0,b,1800),BLUE if i%2 else GREEN,BLACK,.8)
        ax.text((a+b)/2,900,labels[i],ha='center',va='center',fontsize=9)
    for a,b in [(-7285,-6965),(6965,7285)]:
        draw_geom(ax,box(a,0,b,1800),TAN,RED,1,'--')
    dimension(ax,(-6965,0),(6965,0),'13,930 reserved — unchanged',offset=(0,-700))
    dimension(ax,(-7285,1800),(7285,1800),'14,570 outside — 320 added each side',offset=(0,700),color=RED)
    ax.set(xlim=(-7900,7900),ylim=(-1500,3600),aspect='equal');ax.axis('off')
    fig.text(.07,.42,'No extra full-height wall strips are placed on the internal arcade lines.',weight='bold',fontsize=11)
    fig.text(.07,.375,'Piers, responds and buttresses need their own bearing footprints. Wall thickness is not their diameter.',fontsize=11)
    ax=fig.add_axes([.07,.13,.42,.18])
    W,t=1152,250
    for a,b,l in [(-t,0,'250'),(0,W,'1152 clear'),(W,W+t,'250'),(W+t,2*W+t,'1152 clear'),(2*W+t,2*W+2*t,'250')]:
        wall=l=='250';draw_geom(ax,box(a,0,b,600),TAN if wall else BLUE,RED if wall else BLACK,.7,'--' if wall else '-')
        ax.text((a+b)/2,300,l,ha='center',va='center',fontsize=8,rotation=90 if wall else 0)
    ax.set(xlim=(-350,3000),ylim=(-180,900),aspect='equal');ax.axis('off')
    fig.text(.07,.085,'Illustrative new set-out only: 2W + one shared wall + two outside walls = 3054.',fontsize=9)
    fig.text(.55,.29,'AT AN EXISTING SHARED VAULT EDGE',fontsize=11,weight='bold')
    fig.text(.55,.245,'There is zero free strip between touching reserved cells.\nA positive wall cannot be inserted there while every\ncell coordinate and full reservation remain fixed.\n\nInternal re-spacing is a separate architectural decision;\nthis study does not move the approved 14 vaults.',fontsize=10,va='top',linespacing=1.5)
    fig.text(.07,.035,'EXPERIMENTAL • Plan-envelope dimensions are not floor-clearance or structural-capacity certification.',fontsize=9,color=RED)
    finish(fig,'03_SPACE_AND_MASONRY_RULES')

def tables_and_qa(wm,wc):
    apse=CHAPEL.bounds[2];west=GRID['nave']['x_stations_west_to_crossing'][0]
    trial_rows=[]
    for t in CFG['trial_thicknesses']:
        trial_rows.append({'wall_thickness':t,'chapel_reserved_width':2500,
                           'chapel_outside_width':2500+2*t,'chapel_nose_X':apse+t,
                           'nave_reserved_width':13930,'nave_outside_width':13930+2*t,
                           'main_terminal_N_S_reach':21418+2*t,
                           'uniform_wall_axial_reach':apse-west+2*t,
                           'status':'EXPERIMENTAL_CONSTANT_THICKNESS_COMPARISON'})
    with (OUT/'THICKNESS_COMPARISON.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=trial_rows[0].keys());w.writeheader();w.writerows(trial_rows)
    features=[feature(k,p,'PROTECTED_SOURCE_SET_OUT',source=CELLS[k]['source']) for k,p in VAULTS.items()]
    features += [feature('R07_CHAPEL_RESERVATION',CHAPEL,'RETAINED_EXPERIMENTAL_REFERENCE'),
                 feature('MAIN_BODY_PREVIEW',MAIN,'EXPERIMENTAL_PARTLY_SCHEMATIC',note='Choir taper interpolated; transept cores only'),
                 feature('MAIN_MASONRY_320',wm,'EXPERIMENTAL',thickness=320),
                 feature('CHAPEL_MASONRY_250',wc,'EXPERIMENTAL',thickness=250)]
    dump(OUT/'PLAN_GEOMETRY_NATIVE.geojson',{'type':'FeatureCollection',
         'coordinate_system':'LOCAL native project units, X east Y north; not geodetic',
         'features':features})
    dump(OUT/'PROTECTED_VAULT_COORDINATES.json',CELLS)
    checks=[]
    def check(name, passed, **measure):checks.append({'check':name,'pass':bool(passed),**measure})
    check('14 protected polygons valid',len(VAULTS)==14 and all(p.is_valid for p in VAULTS.values()))
    saved=json.loads((OUT/'PROTECTED_VAULT_COORDINATES.json').read_text())
    check('exact protected source coordinates and IDs round trip',saved==CELLS)
    ns=GRID['nave']['x_stations_west_to_crossing'];qs=GRID['choir']['x_stations_crossing_to_chevet']
    check('all ten nave station differences',np.array_equal(np.diff(ns),GRID['nave']['bay_depths_N1_to_N10']))
    check('all five choir station differences',np.array_equal(np.diff(qs),GRID['choir']['bay_depths_Q1_to_Q5']))
    seams=[]
    for i in range(1,8):
        a,b=VAULTS[f'I_A{i}'],VAULTS[f'M_A{i}']
        # Exact shared endpoints, allowing only source floating point noise.
        pts=np.array(CELLS[f'I_A{i}']['vertices']);other=np.array(CELLS[f'M_A{i}']['vertices'])
        d=np.linalg.norm(pts[:,None,:]-other[None,:,:],axis=2).min(axis=1)
        shared=pts[d<1e-7]
        l=LineString(shared).length if len(shared)==2 else 0
        seams.append(l)
    check('seven retained inner-middle shared edges',len(seams)==7 and min(seams)>1600,edge_lengths=seams)
    src_xy=np.array(R07['rear_chord']);rv=np.array(CELLS['M_A4']['vertices'])
    rear_error=float(np.linalg.norm(src_xy[:,None,:]-rv[None,:,:],axis=2).min(axis=1).max())
    check('R07 rear interface remains fixed',rear_error<1e-8,max_error=rear_error)
    compact_err=0.
    for short,pts,_ in COMPACT['cells']:
        key=short[0]+'_A'+short[1:]
        a=np.array(pts);b=np.array(CELLS[key]['vertices'])
        compact_err=max(compact_err,float(np.linalg.norm(a[:,None,:]-b[None,:,:],axis=2).min(axis=1).max()))
    check('compact R07 coordinates agree at stated 0.01 precision',compact_err<.008,max_distance=compact_err)
    areas=[];offset_errors=[]
    for t in CFG['trial_thicknesses']:
        m,c=main_wall(t),chapel_wall(t)
        intrusion=m.union(c).intersection(RESERVED).area
        areas.append(intrusion)
        check(f't={t} no reserved-space area consumed',intrusion<1e-6,intrusion_area=intrusion)
        check(f't={t} wall polygons valid',m.is_valid and c.is_valid)
        ys=sorted(c.intersection(LineString([(29800,-10000),(29800,10000)])).bounds[1::2])
        check(f't={t} chapel outside width exact',abs(ys[-1]-ys[0]-(2500+2*t))<1e-7)
        check(f't={t} apse normal offset exact',abs(c.bounds[2]-(apse+t))<1e-7)
        # For every retained apse / side face, verify an outward midpoint at t/2.
        poly=shapely.geometry.polygon.orient(CHAPEL,sign=1)
        for p,q in zip(list(poly.exterior.coords)[:-1],list(poly.exterior.coords)[1:]):
            p,q=np.array(p),np.array(q)
            if abs(p[0]-28000)<1e-7 and abs(q[0]-28000)<1e-7:continue
            e=q-p;n=np.array([e[1],-e[0]])/np.linalg.norm(e)
            mid=(p+q)/2+n*t/2
            offset_errors.append(abs(shapely.Point(mid).distance(CHAPEL.boundary)-t/2))
            check(f't={t} face midpoint lies in outward band {len(offset_errors)}',c.covers(shapely.Point(mid)))
        check(f't={t} chapel entrance is uncapped',c.intersection(box(27999,-1200,28001,1200)).area<1e-7)
        check(f't={t} main east join is uncapped',m.intersection(box(20212,-5000,20214,5000)).area<1e-7)
    check('face normal distances accurate',max(offset_errors)<1e-7,max_error=max(offset_errors))
    check('600-deep threshold retained',R07['r03_geometry']['threshold']==[28000,28600])
    check('two original 2400-deep bays retained',R07['r03_geometry']['chapel_bays']==[[28600,31000],[31000,33400]])
    baseline_length=apse-west;proposed_length=baseline_length+320+250
    measures={'baseline_axial_reach':baseline_length,'proposed_axial_reach':proposed_length,
              'axial_increase':570,'axial_increase_percent':570/baseline_length*100,
              'nave_reserved_width':13930,'nave_outside_width':14570,'nave_increase_percent':640/13930*100,
              'transept_terminal_reserved_reach':21418,'transept_terminal_outside_reach':22058,
              'chapel_reserved_width':2500,'chapel_outside_width':3000,
              'chapel_nose_reference_X':apse,'chapel_nose_with_250_X':apse+250,
              'whole_building_total_extent':'UNRESOLVED: other chapels/towers/porches/shoulders not fully recovered',
              'source_compact_max_difference':compact_err}
    qa={'result':'PASS' if all(c['pass'] for c in checks) else 'FAIL',
        'scope':'technical and 2D geometric reservation checks only',
        'checks_passed':sum(c['pass'] for c in checks),'checks_count':len(checks),
        'checks':checks,'measurements':measures,
        'architectural_approval':False,'historical_dimension_validation':False,
        'structural_validation':False,'physical_metre_conversion':None,
        'runtime':{'python':platform.python_version(),'numpy':np.__version__,
                   'shapely':shapely.__version__,'matplotlib':matplotlib.__version__}}
    dump(OUT/'NUMERICAL_QA.json',qa)
    dump(OUT/'MEASUREMENTS.json',measures)
    assert qa['result']=='PASS', [c for c in checks if not c['pass']]
    return qa

def main():
    before={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'inputs').iterdir() if p.is_file()}
    wm=main_wall(320);wc=chapel_wall(250)
    qa=tables_and_qa(wm,wc)
    whole_plan(wm,wc);chapel_comparison();space_rules()
    fs=[('MAIN_BODY_PREVIEW',MAIN,'UNCERTAIN','#f7f7f7'),
        ('MAIN_MASONRY_320',wm,'EXPERIMENTAL',TAN),
        ('R07_CHAPEL',CHAPEL,'REFERENCE','#fff5e7'),
        ('CHAPEL_MASONRY_250',wc,'EXPERIMENTAL',TAN)]
    fs += [(k,p,'REFERENCE',BLUE if k.startswith('I') else GREEN) for k,p in VAULTS.items()]
    native_svg('MASTER_PLAN_NATIVE_1TO1',fs,(-41000,-11500,36000,11500))
    native_svg('AXIAL_CHAPEL_NATIVE_1TO1',fs[2:4],(27500,-2100,35500,2100))
    for p in OUT.glob('*.svg'):ET.parse(p)
    assert before=={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'inputs').iterdir() if p.is_file()}
    dump(OUT/'INPUT_SHA256_UNCHANGED.json',{'result':'PASS','inputs_before_equal_after':True,'sha256':before})
    print(json.dumps({'result':qa['result'],'checks':f"{qa['checks_passed']}/{qa['checks_count']}",
                      'all_inputs_unchanged':True,'measurements':qa['measurements']},indent=2))

if __name__=='__main__':main()
