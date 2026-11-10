import bpy,math,json,hashlib,pathlib,statistics
from xml.sax.saxutils import escape
O=pathlib.Path('/home/christopher/Desktop/F5ZP_CHEVET_THREE_CHAPEL_CAD_R01_20261110')
SRC=pathlib.Path(bpy.data.filepath)
CX,CY=20213.0,0.0
X0,Y0=19000.0,9300.0
W,H=23300,18700
def pos(x,y):return (x-X0,Y0-y)
def hull(P):
    pts=sorted(set((round(float(x),4),round(float(y),4)) for x,y in P))
    if len(pts)<3:return pts
    def c(a,b,d):return (b[0]-a[0])*(d[1]-a[1])-(b[1]-a[1])*(d[0]-a[0])
    low=[];up=[]
    for p in pts:
        while len(low)>=2 and c(low[-2],low[-1],p)<=0:low.pop()
        low.append(p)
    for p in pts[::-1]:
        while len(up)>=2 and c(up[-2],up[-1],p)<=0:up.pop()
        up.append(p)
    return low[:-1]+up[:-1]
def poly(o):
    verts=[o.matrix_world@v.co for v in o.data.vertices]
    if not verts:return []
    z=min(v.z for v in verts)
    return hull([(v.x,v.y) for v in verts if abs(v.z-z)<.02])
data={}
for o in bpy.data.objects:
    if o.type=='MESH':data[o.name]=poly(o)
grp={'NORTH':[],'AXIAL':[],'SOUTH':[]}
for n,p in data.items():
    for g in grp:
        if n.startswith('R18_'+g+'_WALL_'):grp[g].extend(p)
extents={g: [round(min(x for x,y in P),3),round(min(y for x,y in P),3),round(max(x for x,y in P),3),round(max(y for x,y in P),3)] for g,P in grp.items()}
assert all(len(v)>=28 for v in grp.values())
assert all(any(k.startswith('R18_'+g+'_CONNECTOR_CHEEK') for k in data) for g in grp)
items=[]
def S(x):items.append(x)
S(f'<svg xmlns="http://www.w3.org/2000/svg" width="2330mm" height="1870mm" viewBox="0 0 {W} {H}">')
S("""<defs>
<pattern id="dots" width="100" height="100" patternUnits="userSpaceOnUse"><path d="M0 100L100 0" stroke="#efdfdb" stroke-width="6"/></pattern>
<marker id="arrow" viewBox="0 0 12 12" refX="6" refY="6" markerWidth="12" markerHeight="12" orient="auto-start-reverse"><path d="M0 0L12 6L0 12Z" fill="#343b41"/></marker>
</defs>
<rect width="100%" height="100%" fill="#ffffff"/>
<style>
.head{font-family:'DejaVu Sans',sans-serif;font-weight:700;font-size:385px;fill:#1c2530}
.sub{font-family:'DejaVu Sans',sans-serif;font-size:205px;fill:#475569}
.group{font-family:'DejaVu Sans',sans-serif;font-size:270px;font-weight:700;fill:#1b2933}
.label{font-family:'DejaVu Sans',sans-serif;font-size:187px;fill:#334155}
.small{font-family:'DejaVu Sans',sans-serif;font-size:155px;fill:#445466}
.mini{font-family:'DejaVu Sans',sans-serif;font-size:131px;fill:#6a747c}
.red{fill:#ae2934;font-family:'DejaVu Sans',sans-serif;font-size:165px;font-weight:600}
.hdr{font-family:'DejaVu Sans',sans-serif;font-size:190px;font-weight:700;fill:#1f2937}
</style>""")
S('<text class="head" x="750" y="560">F5ZP  /  CHEVET THREE-CHAPEL RECEIVER STUDY</text>')
S('<text class="sub" x="750" y="940">SOURCE-TRACED 2D PLAN  ·  ORIGINAL WORLD XY UNITS  ·  R21 A (70° / 90° / 110°)  ·  2026-11-10</text>')
S('<path d="M650 1090 H22650" stroke="#1f2937" stroke-width="18"/>')
S('<text class="small" x="820" y="1450">Black outlines = traced R21 A mesh geometry (EXPERIMENTAL, NOT approved). Dashed features = construction or unverified proposals.</text>')
# radial station references, not approved masonry
cc=pos(CX,CY)
for r,tag in [(5285,'R5285 preliminary pier reference'),(6685,'R6685 outer trial setout')]:
    pts=[]
    for i in range(121):
        ang=math.radians(0+180*i/120)
        x,y=pos(CX+r*math.sin(ang),r*math.cos(ang))
        pts.append(f'{x:.2f},{y:.2f}')
    S(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#99a2ac" stroke-width="16" stroke-dasharray="95 95"/>')
    tx,ty=pos(CX+r*math.sin(math.radians(155)),r*math.cos(math.radians(155)))
    S(f'<text class="mini" x="{tx-200:.1f}" y="{ty+260:.1f}">{tag}</text>')
for a in (30,50,70,90,110,130,150):
    th=math.radians(a)
    p=pos(CX+8350*math.sin(th),8350*math.cos(th))
    S(f'<line x1="{cc[0]}" y1="{cc[1]}" x2="{p[0]:.2f}" y2="{p[1]:.2f}" stroke="#b2b9c0" stroke-dasharray="85 125" stroke-width="11"/>')
    t=pos(CX+4720*math.sin(th),4720*math.cos(th))
    S(f'<text class="small" x="{t[0]-100:.1f}" y="{t[1]+15:.1f}">{a}°</text>')
# source mesh object footprint. Exclude V03 hidden archive. R21 preliminary piers are unapproved snapshots.
members=[]
for name,vertices in sorted(data.items()):
    if not vertices or len(vertices)<3:continue
    role=None
    if name.startswith('R18_') and '_WALL_' in name:role='wall'
    elif name.startswith('R18_') and '_CONNECTOR_CHEEK_' in name:role='cheek'
    elif name.startswith('R18_') and '_BUTTRESS_' in name:role='buttress'
    elif name.startswith('PIER_CORE_R5285_') and name.endswith('_SNAPSHOT'):role='trialpier'
    elif name.startswith('TRIAL_PAD_O_'):role='trialpad'
    if role is None:continue
    p=' '.join(f'{pos(x,y)[0]:.2f},{pos(x,y)[1]:.2f}' for x,y in vertices)
    fill,stroke,sw,dash={
        'wall':('#333c44','#19232b',19,''),
        'cheek':('#56616a','#29343d',19,''),
        'buttress':('#96a1aa','#64717e',15,''),
        'trialpier':('#d6dadd','#78858b',13,''),
        'trialpad':('#f4f4f1','#8b98a1',10,'70 85'),
    }[role]
    S(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-dasharray="{dash}"/>')
    members.append((name,role))
# layout labels from actual envelope; avoid invented pavilion dimensions
for g,t in [('NORTH','NORTH COMPANION'),('AXIAL','AXIAL CHAPEL'),('SOUTH','SOUTH COMPANION')]:
    bb=extents[g];mx=(bb[0]+bb[2])/2;my=(bb[1]+bb[3])/2
    a,b=pos(mx,my)
    S(f'<rect x="{a-1200:.1f}" y="{b-245:.1f}" width="2400" height="340" fill="#fff" opacity=".9"/>')
    S(f'<text class="group" x="{a:.1f}" y="{b:.1f}" text-anchor="middle">{t}</text>')
# source physical x-extent native measurements for all 3 chapel wall groups
for g,yw in [('NORTH',7400),('AXIAL',0),('SOUTH',-7350)]:
    bb=extents[g];y=pos(0,yw)[1]
    x1=pos(bb[0],0)[0];x2=pos(bb[2],0)[0]
    # only dimension if it clears source drawings: dimension string horizontal
    if g=='AXIAL':y=pos(0,-2350)[1]
    elif g=='NORTH':y=pos(0,7850)[1]
    else:y=pos(0,-7950)[1]
    S(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="#475569" stroke-width="12" marker-start="url(#arrow)" marker-end="url(#arrow)"/>')
    S(f'<text class="small" text-anchor="middle" x="{(x1+x2)/2:.1f}" y="{y-90:.1f}">{g} source wall ΔX = {bb[2]-bb[0]:,.1f} native</text>')
# anchor candidates computed from nearest source cheek vertex pairs, not authoritative supports
anchors=[]
for side in ('NORTH','SOUTH'):
    P=[p for n,p in data.items() if n.startswith('R18_'+side+'_CONNECTOR_CHEEK_') for p in p]
    Q=[p for n,p in data.items() if n.startswith('R18_AXIAL_CONNECTOR_CHEEK_') for p in p]
    assert P and Q
    a,b=min(((a,b) for a in P for b in Q),key=lambda ab:(ab[0][0]-ab[1][0])**2+(ab[0][1]-ab[1][1])**2)
    m=((a[0]+b[0])/2,(a[1]+b[1])/2)
    anchors.append(dict(side=side,xy=m,edge_gap=math.dist(a,b)))
    x,y=pos(*m)
    S(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="210" fill="#fff2f0" stroke="#b42330" stroke-width="24" stroke-dasharray="65 55"/>')
    S(f'<path d="M{x-160:.1f} {y:.1f} h320 M{x:.1f} {y-160:.1f} v320" stroke="#b42330" stroke-width="24"/>')
    S(f'<text class="red" x="{x-420:.1f}" y="{y-330:.1f}">{side} junction study</text>')
# Candidate 1:1 plan trial outlines; all red dashed and explicitly not approved
for row in anchors:
    x,y=pos(*row['xy'])
    if row['side']=='NORTH':
        S(f'<rect x="{x-160:.1f}" y="{y-440:.1f}" width="320" height="880" fill="#f8d9d9" fill-opacity=".36" stroke="#b42330" stroke-width="24" stroke-dasharray="75 55"/>')
        S(f'<text class="red" x="{x+210:.1f}" y="{y+345:.1f}">A*</text>')
        S(f'<rect x="{x+620:.1f}" y="{y-690:.1f}" width="320" height="320" fill="url(#dots)" stroke="#b42330" stroke-width="22" stroke-dasharray="65 60"/>')
        S(f'<text class="red" x="{x+970:.1f}" y="{y-490:.1f}">C*</text>')
    else:
        P=[(x-160,y-440),(x+160,y-440),(x+160,y-170),(x+480,y-170),(x+480,y+170),(x+160,y+170),(x+160,y+440),(x-160,y+440)]
        S('<polygon points="'+' '.join(f'{a:.1f},{b:.1f}' for a,b in P)+'" fill="#f8d9d9" fill-opacity=".30" stroke="#b42330" stroke-width="24" stroke-dasharray="75 55"/>')
        S(f'<text class="red" x="{x+535:.1f}" y="{y+200:.1f}">B*</text>')

# windows are NOT cut in existing source wall meshes. Provide candidate stations only, no fake holes.
for a in (30,70,110,150):
    th=math.radians(a)
    xy=pos(CX+7650*math.sin(th),7650*math.cos(th))
    S(f'<circle cx="{xy[0]:.1f}" cy="{xy[1]:.1f}" r="155" fill="none" stroke="#bd3944" stroke-width="21" stroke-dasharray="60 62"/>')
    S(f'<text class="red" x="{xy[0]+160:.1f}" y="{xy[1]-185:.1f}">W{a}?</text>')
# experimental landing regions located radially beyond actual buttress source outermost centroids; schematic, not masonry
for g in ('NORTH','AXIAL','SOUTH'):
    P=[p for n,poly in data.items() if n.startswith('R18_'+g+'_BUTTRESS_') for p in poly]
    if not P:continue
    x=max(p[0] for p in P)+360
    yy=statistics.mean(p[1] for p in P)
    if g=='NORTH':yy=max(p[1] for p in P)+200
    if g=='SOUTH':yy=min(p[1] for p in P)-200
    sx,sy=pos(x,yy)
    S(f'<rect x="{sx-235:.1f}" y="{sy-235:.1f}" width="470" height="470" stroke="#bf3944" stroke-width="20" stroke-dasharray="70 60" fill="url(#dots)"/>')
    S(f'<text class="red" x="{sx+280:.1f}" y="{sy:.1f}">{g[0]} FLYER?</text>')
# panel starts outside model, alternatives are symbolic, explicitly no architectural scale
px=17050
S(f'<rect x="{px}" y="1830" width="5500" height="13570" rx="35" fill="#fbfcfc" stroke="#bec8d0" stroke-width="18"/>')
S(f'<text class="hdr" x="{px+330}" y="2350">RECEIVING-PIER OPTIONS</text>')
S(f'<text class="small" x="{px+330}" y="2720">Non-dimensional symbols — NOT placed solids</text>')
symbols=[
    ('A','WALL-INTEGRATED','Wall &amp; engaged buttress',3300),
    ('B','T-SHAPED','Projecting receiver arm',5300),
    ('C','INTERMEDIATE','Separate support / transfer',7300),
]
for k,title,sub,y in symbols:
    S(f'<text class="red" x="{px+330}" y="{y}">{k}  /  {title}</text>')
    S(f'<text class="small" x="{px+330}" y="{y+310}">{sub}</text>')
    x=px+2600; yy=y+290
    S(f'<path d="M{x} {yy+100} H{x+1400}" stroke="#29333b" stroke-width="75"/>')
    if k=='A':S(f'<rect x="{x+480}" y="{yy-260}" width="400" height="360" fill="none" stroke="#ad2937" stroke-width="28" stroke-dasharray="100 65"/>')
    elif k=='B':S(f'<path d="M{x+480} {yy+150} v-340 h350 v340" fill="none" stroke="#ad2937" stroke-width="28" stroke-dasharray="100 65"/>')
    else:S(f'<rect x="{x+610}" y="{yy-540}" width="430" height="310" fill="none" stroke="#ad2937" stroke-width="28" stroke-dasharray="100 65"/>')
S(f'<text class="hdr" x="{px+330}" y="9500">INTERPRETATION</text>')
for i,line in enumerate([
 'R21 A source: chapel bodies + trial buttresses.',
 'A/B/C overlays are UNAPPROVED experimental.',
 'W30/W70/W110/W150: candidate window stations.',
 'No verified cuts in the recorded source walls.',
 'Red flyer zones: conceptual, no capacity or',
 'landing-face dimensions established.',
 'Outer ring is not reinstated or rebuilt.',
 'Avoid using trial pads as approved supports.'
]):
    S(f'<text class="small" x="{px+330}" y="{9940+i*370}">{escape(line)}</text>')
S(f'<text class="hdr" x="{px+330}" y="13500">PRESERVATION / RELEASE</text>')
for i,line in enumerate(['F5ZN-A / Pass 6J unchanged','F5ZL-C 248 positions: MISSING','Structural capacity: OPEN','Scale conversion: UNRESOLVED']):
    S(f'<text class="small" x="{px+330}" y="{13880+i*320}">{escape(line)}</text>')
# overall legends + native-unit witness 1000
S('<rect x="660" y="16800" width="21900" height="1340" fill="#f8fafc" stroke="#b8c2cd" stroke-width="15"/>')
S('<text class="hdr" x="920" y="17210">SOURCE &amp; VALIDATION</text>')
S('<text class="small" x="920" y="17560">Source: R21 A portable Blender checkpoint (experimental). Coordinate plan: Blender world XY, +Z up, chevet center (20213, 0).</text>')
S('<text class="small" x="920" y="17860">CAD geometry uses original native units; screen/print depiction is NOT physical 1:1. Wall mesh silhouettes are exact source-derived, but unapproved.</text>')
S('<text class="small" x="920" y="18140">Verified dimension strings = source ΔX; no unsupported 320/197/292 ring construction or chapel/window widths are imposed.</text>')
S('</svg>')
(O/'F5ZP_CHEVET_THREE_CHAPEL_CAD_R01.svg').write_text('\n'.join(items))
tests=dict(source=str(SRC),source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),source_model_objects=len(data), source_groups={g:sum(1 for n in data if n.startswith('R18_'+g+'_WALL_')) for g in grp}, chapel_bounds_native=extents, anchors=anchors,footprint_count=len(members), native_coordinate_units=True,physical_scale_unresolved=True,source_status='R21 A experimental', windows='CANDIDATE ONLY not cut or validated',receiver='NOT INSTALLED symbolic only',f5zl_c='UNRESOLVED',technical='SVG generated from saved world mesh vertex coordinates',geometric='three source wall envelopes and candidate nearest cheek vertex pairs',architectural='unresolved passage and landing clearances',historical='analogies only',structural='unvalidated')
(O/'CAD_SOURCE_QA.json').write_text(json.dumps(tests,indent=2))
print('CAD_SVG_DONE',len(members),tests['source_groups'],extents,'anchors',anchors)
