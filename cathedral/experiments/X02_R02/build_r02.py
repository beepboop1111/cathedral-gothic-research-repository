#!/usr/bin/env python3
"""Research-led X02 R02. New experiment only; never edits R01 or cathedral files."""
from pathlib import Path
import sys,json,hashlib,csv,textwrap,math
from xml.sax.saxutils import escape
deps=Path(__file__).resolve().parent.parent/'.x02_deps'
if deps.exists():sys.path.append(str(deps))
from shapely.geometry import shape,mapping,box,Polygon,LineString
from shapely.ops import unary_union
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor,black
R=Path(__file__).resolve().parent;O=R/'outputs';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={p.name:sha(p) for p in (R/'sources').iterdir() if p.is_file()}
old=json.loads((R/'sources/R01_X02_GEOMETRY.json').read_text())
g={f['id']:shape(f['geometry']) for f in old['features']}
cx=-34.2277;nc=cx+.4;wf=12.0625
throat=box(cx-.6,wf,cx+.6,14.1625)
transition=Polygon([(cx-.6,14.1625),(cx+.6,14.1625),(nc+1.75,15.1625),(nc-1.75,15.1625)])
gallery=box(nc-1.75,15.1625,nc+1.75,18.9)
link=unary_union([throat,transition,gallery])
vestibule=box(-30,32.25,-21,35.75)
stair_lobby=box(-30,22.9,-21,29.5)
entry_lobby=box(nc-1.75,18.9,nc+1.75,22.4)
ceremony=LineString([(cx,wf),(cx,14.4625),(nc,15.1625),(nc,20.65),(-31.75,20.65),(-31.75,34),(-15,34)])
refectory_route=LineString([(-31.75,34),(-31.75,43.15),(-42,43.15),(-42,48)])
walks=g['cloister_outer'].difference(g['cloister_garden'])
roots=unary_union([q for n,q in g.items() if n.startswith('ROOT-')])
domain=unary_union([link,walks,g['east_wing'],g['chapter_hall'],g['refectory']])
sweep=ceremony.buffer(.6,cap_style=2,join_style=2)
rsweep=refectory_route.buffer(.6,cap_style=2,join_style=2)
new=dict(g);new['n4_link']=link;new['CEREMONY_R1']=ceremony;new['CEREMONY_1p2m_SWEEP']=sweep
new.update(CHAPTER_VESTIBULE=vestibule,NIGHT_STAIR_LOBBY_ZONE=stair_lobby,
           CONTROLLED_ENTRY_LOBBY=entry_lobby,REFECTORY_ROUTE=refectory_route)
tests=[]
def ck(id,condition,note):tests.append({'id':id,'result':'PASS' if bool(condition) else 'FAIL','evidence':note})
for n in g:
 if n not in ['n4_link','CEREMONY_R1','CEREMONY_1p2m_SWEEP']:
  ck('RETAINED_'+n,new[n].equals_exact(g[n],1e-10),'R01 geometry identical within 1e-10 m; no source-body relocation.')
for n in ['n4_link','CHAPTER_VESTIBULE','NIGHT_STAIR_LOBBY_ZONE','CONTROLLED_ENTRY_LOBBY']:
 ck('VALID_'+n,new[n].is_valid and not new[n].is_empty,'Valid nonempty polygon; no automatic repair.')
metrics={'gallery_width_R01_m':2.7,'gallery_width_R02_m':3.5,'gallery_center_shift_east_m':.4,
 'portal_center_X_m':cx,'gallery_center_X_m':nc,'throat_width_retained_m':1.2,
 'link_area_R01_m2':g['n4_link'].area,'link_area_R02_m2':link.area,
 'link_root_gap_m':link.distance(roots),'link_garden_gap_m':link.distance(g['new_garden']),
 'link_root_overlap_m2':link.intersection(roots).area,'link_garden_overlap_m2':link.intersection(g['new_garden']).area,
 'conditional_chapel_overlap_m2':link.intersection(g['chapel_reference']).area,
 'ceremony_garden_overlap_m2':sweep.intersection(g['cloister_garden']).area,
 'ceremony_root_overlap_m2':sweep.intersection(roots).area,'ceremony_outside_domain_m2':sweep.difference(domain).area,
 'refectory_outside_domain_m2':rsweep.difference(domain).area,
 'refectory_garden_overlap_m2':rsweep.intersection(g['cloister_garden']).area,
 'vestibule_length_m':9,'vestibule_width_m':3.5,'vestibule_area_m2':vestibule.area,
 'night_lobby_zone_area_m2':stair_lobby.area,'entry_lobby_area_m2':entry_lobby.area,
 'screened_root_count':sum(n.startswith('ROOT-') for n in g)}
for n in ['link_root_overlap_m2','link_garden_overlap_m2','conditional_chapel_overlap_m2',
          'ceremony_garden_overlap_m2','ceremony_root_overlap_m2','ceremony_outside_domain_m2',
          'refectory_outside_domain_m2','refectory_garden_overlap_m2']:
 ck(n,metrics[n]<1e-8,f'{metrics[n]:.10f} m2; conditional X01 geometry only.')
ck('VESTIBULE_INSIDE_RANGE',g['east_wing'].covers(vestibule),'31.5 m2 vestibule reserved inside the unchanged east wing.')
ck('NIGHT_ZONE_INSIDE_RANGE',g['east_wing'].covers(stair_lobby),'59.4 m2 functional room zone; not a designed stair.')
ck('EXISTING_STAIR_RESERVE_RETAINED',stair_lobby.covers(g['NIGHT_STAIR_RESERVATION']),'R01 hypothetical stair box retained within larger night/lobby functional zone.')
ck('ENTRY_LOBBY_IN_WALK',walks.covers(entry_lobby),'Controlled-entry reservation uses south walk, no garden intrusion.')
ck('VESTIBULE_TOUCHES_WALK',vestibule.distance(walks)<1e-10,'East walk meets vestibule at X=-30.')
ck('VESTIBULE_TOUCHES_HALL',vestibule.distance(g['chapter_hall'])<1e-10,'Vestibule meets hall at X=-21.')
ck('GALLERY_TOUCHES_WALK',link.distance(walks)<1e-10,'External gallery meets south walk at Z=18.9.')
ck('GARDEN_MARGIN_RETAINED',abs(link.distance(g['new_garden'])-.35)<1e-9,'0.35 m planning margin retained by +0.40 m center offset.')
ck('N4_THROAT_RETAINED',abs(link.distance(roots)-.1956)<1e-9,'Same 195.6 mm root-only screening gap as R01.')
ck('SOUTH_NOT_PLACED',old['unplaced_protected_south']['site_X'] is None,'No guessed southern site polygon or replacement baseline.')

evidence=[
 {'id':'P01','type':'project research reviewed','source':'sources/01_Cathedral_Cloisters_and_Attached_Buildings.md','finding':'Cloister adjacency, attached ranges, separate access hierarchies, chapter vestibule and two distinct cloister programs were already researched.','use':'Carry relationships forward; do not reopen general north/south historic plausibility as a missing fact.'},
 {'id':'P02','type':'retrieved user decisions - original transcript not packaged','source':'Cathedral Cloister Comparison, 2026-11-03 13:35 and 14:28 UTC','finding':'3.5 m L-shaped gallery; 22 x 26 m north cloister, 15 x 19 m garden; 9 x 12 m chapter hall plus 3 m polygonal termination; refectory north, dormitory east, dedicated night route.','use':'Restore the 3.5 m planning module in the new experiment; retain accepted program. This is not proof of final source-model approval.'},
 {'id':'H01','type':'primary text rechecked','source':'Viollet-le-Duc, Dictionnaire raisonne, III, Cloitre, printed p.442, figs.27-28','url':'https://fr.wikisource.org/wiki/Page:Viollet-le-Duc_-_Dictionnaire_raisonn%C3%A9_de_l%E2%80%99architecture_fran%C3%A7aise_du_XIe_au_XVIe_si%C3%A8cle,_1854-1868,_tome_3.djvu/445','finding':'Noyon wall-side rib supports use corbels to limit projections into the walk.','use':'Research basis for a circulation-conscious support strategy; no masonry capacity or actual corbel design inferred.'},
 {'id':'H02','type':'primary text rechecked','source':'Viollet-le-Duc, III, Cloitre, opening discussion','url':'https://fr.wikisource.org/wiki/Dictionnaire_raisonn%C3%A9_de_l%E2%80%99architecture_fran%C3%A7aise_du_XIe_au_XVIe_si%C3%A8cle/Clo%C3%AEtre','finding':'His historical synthesis recognizes cathedral cloisters on either side of the nave and distinguishes communal from more secluded institutional spaces.','use':'Supports keeping the north study viable; does not choose its site for this project.'},
 {'id':'H03','type':'institutional source rechecked','source':'Durham Cathedral, The Cloister','url':'https://www.durhamcathedral.co.uk/explore/the-cathedral-building-and-grounds/cloisters','finding':'The cloister connects nave, chapter house and refectory and acts as a daily circulation hub.','use':'Plan a continuous community circuit with named room thresholds.'},
 {'id':'H04','type':'institutional source rechecked','source':'Westminster Abbey, The Cloisters','url':'https://www.westminster-abbey.org/history/explore-our-history/the-cloisters','finding':'East walk accesses chapter house and dormitory/library; a separate passage reaches the Little Cloister.','use':'Maintain direct chapter access and a distinct private/secondary route.'},
 {'id':'H05','type':'previous project research + current search-index corroboration only','source':'Salisbury Cathedral Archive, The Salisbury Chapter House','url':'https://salisbury.art.virginia.edu/pdf/PZBSalisburyChapterHouse.pdf','finding':'Indexed text describes east walk -> two-bay vestibule -> chapter house. Direct page/PDF retrieval failed in this run.','use':'Supports the vestibule sequence. The proposed 4.5 x 3.5 m modules are our design, not measured Salisbury geometry.'},
 {'id':'L01','type':'legacy proposal, not current authority','source':'Library CATHEDRAL_F5I_CLOISTER_CHECKPOINT.json, libfile_9ba7fea921ec8191b52e6417e7855c22','finding':'Older F5I proposal already records east-walk chapter vestibule, dedicated upper stair and independent transept entry. Its dimensions and coordinate convention differ.','use':'Relationship history only; do not reuse 960-unit walks, chapter radius or old coordinates.'},
 {'id':'I01','type':'new experimental interpretation','source':'build_r02.py','finding':'Offset the 3.5 m gallery center 0.40 m east; define a 9 x 3.5 m vestibule in two 4.5 m planning bays and a night-lobby functional zone.','use':'Concrete R02 proposal for architectural review; no new dimension lock.'}
]
(O/'RESEARCH_EVIDENCE_LEDGER.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\n')
model=dict(old);model['id']='F5ZP-X02-R02';model['authority']='EXPERIMENTAL PLANNING PROPOSAL FOR REVIEW'
model['features']=[{'type':'Feature','id':n,'properties':{'status':'R02_PROPOSAL' if n not in g or n in ['n4_link','CEREMONY_R1','CEREMONY_1p2m_SWEEP'] else 'RETAINED_R01_EXPERIMENT','units':'metres'},'geometry':mapping(q)} for n,q in new.items()]
(O/'X02_R02_GEOMETRY.json').write_text(json.dumps(model,indent=2)+'\n')
with (O/'DIMENSION_AND_DELTA_REGISTER.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['measurement','value','scope']);w.writerows((n,v,'experimental / geometry only') for n,v in metrics.items())

RED='#a33737';GRAY='#aaaaaa';INK='#232a30'
def pathdata(q):
 if q.geom_type=='Polygon':
  return ['M '+' L '.join(f'{x:.7f},{-z:.7f}' for x,z in ring.coords)+' Z' for ring in [q.exterior,*q.interiors]]
 if q.geom_type=='LineString':return ['M '+' L '.join(f'{x:.7f},{-z:.7f}' for x,z in q.coords)]
 return [p for a in q.geoms for p in pathdata(a)]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="57000mm" height="60000mm" viewBox="-56 -60 57 60">','<title>X02 R02 experimental north-sector layout; physical 1:1; 1 coordinate unit = 1 metre</title>']
for n,q in new.items():
 if 'SWEEP' in n or n=='CHAPTER_R3':continue
 svg.append(f'<g id="{escape(n)}">')
 for p in pathdata(q):svg.append(f'<path d="{p}" fill="none" stroke="{RED}" stroke-width=".035" stroke-dasharray=".18 .10"/>')
 svg.append('</g>')
for x,z,t in [(-41,32,'CLOISTER / GARDEN RETAINED'),(nc,17,'3.50m GALLERY'),(-25.5,34,'9 x 3.5m VESTIBULE'),(-25.5,27,'NIGHT LOBBY / STAIR ZONE'),(-42,50,'REFECTORY')]:
 svg.append(f'<text x="{x}" y="{-z}" font-family="sans-serif" text-anchor="middle" font-size=".45">{escape(t)}</text>')
svg.append('</svg>');(O/'X02_R02_NORTH_SECTOR_1to1.svg').write_text('\n'.join(svg))

pdf=O/'F5ZP_X02_R02_RESEARCH_AND_LAYOUT_REVIEW.pdf';c=Canvas(str(pdf),pagesize=(420*mm,297*mm))
c.setTitle('F5ZP X02 R02 - Research and northern layout proposal')
def head(t,s,p):
 c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',17);c.drawString(15*mm,282*mm,t)
 c.setFont('Helvetica',8);c.drawString(15*mm,275*mm,s)
 c.setStrokeColor(HexColor(GRAY));c.line(15*mm,270*mm,405*mm,270*mm)
 c.setFont('Helvetica',7);c.drawString(15*mm,10*mm,'F5ZP | X02 R02 | EXPERIMENTAL PROPOSAL - NO BASELINE PROMOTION | 05 NOV 2026');c.drawRightString(405*mm,10*mm,str(p))
def note(x,y,title,body,width=140):
 c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',10);c.drawString(x*mm,y*mm,title);y-=6;c.setFont('Helvetica',9)
 for par in body.split('\n'):
  for line in textwrap.wrap(par,width=int(width/1.7)) or ['']:c.drawString(x*mm,y*mm,line);y-=4.5
  y-=2
 return y-4
def panel(bounds,left,bottom,scale,grid=True):
 xmin,zmin,xmax,zmax=bounds;s=1000/scale*mm
 def pt(x,z):return left*mm+(x-xmin)*s,bottom*mm+(z-zmin)*s
 def label(x,z,t,size=7,bold=False,align='center'):
  c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold' if bold else 'Helvetica',size)
  getattr(c,{'center':'drawCentredString','left':'drawString','right':'drawRightString'}[align])(*pt(x,z),t)
 def draw(q,lw=.5,col=RED,fill=False):
  c.setStrokeColor(HexColor(col));c.setLineWidth(lw);c.setDash([2,1.6]);c.setFillColor(HexColor('#fff5f4'))
  for a in getattr(q,'geoms',[q]):
   p=c.beginPath()
   for ring in ([a.exterior,*a.interiors] if a.geom_type=='Polygon' else [a]):
    co=list(ring.coords);p.moveTo(*pt(*co[0]))
    for v in co[1:]:p.lineTo(*pt(*v))
    if a.geom_type=='Polygon':p.close()
   c.drawPath(p,stroke=1,fill=int(fill))
  c.setDash([])
 def dim(x1,x2,z,t):
  c.setStrokeColor(black);c.setLineWidth(.45);c.setDash([]);c.line(*pt(x1,z),*pt(x2,z))
  for x in [x1,x2]:c.line(*pt(x-.08,z-.12),*pt(x+.08,z+.12))
  label((x1+x2)/2,z+.25,t,7)
 if grid:
  c.setStrokeColor(HexColor(GRAY));c.setLineWidth(.2);c.setDash([1,2])
  for x in range(math.ceil(xmin/5)*5,math.floor(xmax/5)*5+1,5):c.line(*pt(x,zmin),*pt(x,zmax));label(x,zmin-.6,str(x),6)
  for z in range(math.ceil(zmin/5)*5,math.floor(zmax/5)*5+1,5):c.line(*pt(xmin,z),*pt(xmax,z));label(xmin-.4,z,str(z),6,align='right')
  c.setDash([])
 return pt,draw,label,dim

head('X02 R02 | RESEARCH-LED NORTHERN LAYOUT','1:250 at A3 / metre coordinates / source bodies retained / new connector and room reservations only',1)
pt,d,l,dm=panel((-56,0,1,60),15,25,250)
for n in ['wall','cloister_outer','cloister_garden','east_wing','chapter_hall','refectory','new_garden','chapel_reference']:
 d(g[n],fill=True)
for n,q in g.items():
 if n.startswith('ROOT-'):d(q,fill=True)
for q in [link,vestibule,entry_lobby,stair_lobby]:d(q,.95)
d(ceremony,1.25);d(g['NIGHT_R2'],1.1);d(refectory_route,.9)
for x,z,t in [(-41,32,'22 x 26 m CLOISTER'),(-41,30.5,'15 x 19 m GARDEN'),(-42,50,'REFECTORY'),(-15,34,'CHAPTER HALL'),(-25.5,43,'EAST RANGE'),(-25.5,27,'NIGHT LOBBY'),(-25.5,35,'VESTIBULE'),(-41,16.5,'GARDEN RETAINED')]:l(x,z,t,7,True)
l(nc,17,'3.5 m',7,True);l(-42,5,'PARTIAL E5-S2 NAVE CONTEXT',7)
l(-54,59,'NORTH ^',7,True,align='left');dm(-54,-44,2,'10 m')
y=259
for title,body in [
 ('Research conclusion','The cloister should organize the community rooms. Retain the eastern chapter-house approach, northern refectory, eastern residential/night zone and separate public / scholarly access.'),
 ('1 / Restore the gallery module','Widen the upper external gallery reservation from 2.70 to 3.50 m, matching the earlier planning preference. Offset its center 0.40 m east to retain the garden and a 0.35 m planning margin.'),
 ('2 / Give the chapter house a vestibule','Reserve 9.00 x 3.50 m inside the existing east range, in two 4.50 m planning bays. This defines the approach without enlarging or moving the chapter hall.'),
 ('3 / Keep the private night connection','Retain the N6 route and existing hypothetical stair box. Define a 9.00 x 6.60 m night-lobby functional zone within the south end of the east range. No stair is designed or certified.'),
 ('Threshold hold','The N4 root-constrained throat remains 1.20 m. This is a candidate private monastic connection, not a cleared public entrance. Actual chapel, jamb and respond geometry must be checked before a wall opening.'),
 ('Authority','All red dashed geometry remains experimental. No southern relocation or north-versus-south precinct selection is made. Reported dimensions of protected work are unchanged.')]:y=note(259,y,title,body)
c.showPage()

head('X02 R02 | CONNECTOR AND CHAPTER APPROACH','1:100 at A3 / planning-band dimensions; actual clear widths after masonry remain unverified',2)
for left,name,q,center,w in [(20,'R01 / 2.70 m',g['n4_link'],cx,2.7),(133,'R02 / 3.50 m',link,nc,3.5)]:
 c.saveState();clip=c.beginPath();clip.rect(left*mm,153*mm,80*mm,110*mm);c.clipPath(clip,stroke=0,fill=0)
 pt,d,l,dm=panel((-38,11,-30,22),left,153,100,False)
 d(q,.9);d(g['new_garden']);d(g['chapel_reference']);d(g['wall'])
 for n,a in g.items():
  if n.startswith('ROOT-') and a.intersects(box(-38,11,-30,22)):d(a)
 l(-34,21.5,name,9,True);dm(center-w/2,center+w/2,17.4,f'{w:.2f} m')
 l(cx,13,'1.20 m retained',6);l(-36.3,16,'GARDEN',7)
 c.restoreState()
y=258
for t,b in [('Connector change','Only the experimental upper connector widens. N4 portal center, throat, buttress references and garden stay fixed.'),('Numerical screen',f'Root overlap 0 m2; garden overlap 0 m2; conditional chapel overlap 0 m2. Root gap {metrics["link_root_gap_m"]*1000:.1f} mm; garden margin {metrics["link_garden_gap_m"]:.2f} m.'),('Interpretation','These are reservation widths, not verified finished clear widths. No real chapel exterior or masonry opening was recovered.')]:y=note(250,y,t,b,155)
c.saveState();clip=c.beginPath();clip.rect(20*mm,25*mm,310*mm,115*mm);c.clipPath(clip,stroke=0,fill=0)
pt,d,l,dm=panel((-35,28.5,-4,40),20,25,100,False)
d(g['east_wing']);d(g['chapter_hall'],.8);d(vestibule,1.1)
d(LineString([(-25.5,32.25),(-25.5,35.75)]),.5,GRAY)
d(LineString([(-33.5,28.5),(-33.5,40)]),.45,GRAY);d(LineString([(-30,28.5),(-30,40)]),.45,GRAY)
l(-31.75,38.8,'EAST WALK',7);l(-25.5,36.4,'TWO-BAY VESTIBULE',8,True)
l(-27.75,34,'4.50 x 3.50 m',7);l(-23.25,34,'4.50 x 3.50 m',7)
l(-15,34,'CHAPTER HALL / 12 x 9 m',8,True);l(-7.3,34,'3 m END',7)
dm(-30,-21,31,'9.00 m');l(-15,29,'Hall and polygonal end retained',7)
c.restoreState()
c.setFont('Helvetica',8);c.drawString(20*mm,18*mm,'Vestibule bay dimensions are a new project proposal; Salisbury supplies an approach precedent, not these measurements.')
c.showPage()

head('X02 R02 | WHAT THE RESEARCH ACTUALLY RESOLVES','Reviewed project reports + targeted primary-source checks / geometry, historical evidence and design choices kept distinct',3)
y=259
for title,body in [
 ('Existing project research / 3 November','The two recovered reports already studied Salisbury, Durham, Westminster, Noyon, Choisy and scale relationships. Their recommendations were adjacency, attached ranges, hierarchical circulation, a chapter vestibule and separate scholarly facilities.'),
 ('Noyon / Viollet-le-Duc / printed p.442','The primary text describes wall-side rib bearings on corbels to avoid obstructing circulation. Use this as support-placement logic for later development; no corbel dimensions or masonry capacity are adopted.'),
 ('Durham / official cathedral account','The cloister connects the nave, chapter house and refectory and serves daily monastic circulation. This supports a connected walk circuit with clearly named room entries.'),
 ('Westminster / official abbey account','The east walk gives access to chapter house and dormitory/library; a distinct passage reaches the Little Cloister. This supports differentiated primary and private / scholarly circulation.'),
 ('Salisbury / archived chapter-house study','The earlier project report and current indexed archive text describe an east-walk approach through a two-bay vestibule. Direct archive page and PDF retrieval failed this run. R02 uses the sequence; our 4.5 x 3.5 m bays are a new design interpretation.')]:y=note(18,y,title,body,180)
y=259
for title,body in [
 ('Earlier decisions recovered','3.50 m L-shaped gallery; 22 x 26 m north cloister and 15 x 19 m garden; 9 x 12 m chapter hall plus 3 m termination; refectory north; dormitory east; dedicated night connection; separate scholarly cloister. These are prior experimental planning choices, not blanket approval of construction.'),
 ('Do not import the older F5I proposal','An older south-cloister checkpoint was found. It is explicitly a review proposal with a different coordinate convention and smaller dimensions. Its useful history is the dedicated vestibule and private upper access, not its old dimensions.'),
 ('Retained boundaries','E5-C3-L1 remains protected; north E5-R3/E5-S2 stays an alternative. F5ZK-C, F5ZN-A, working ambulatory generator and Pass 6J are untouched. No full cathedral rescaling, no generator operation and no Blender operation occurred.'),
 ('Research limit','Historic examples support a relationship and design logic. They cannot reveal this project chapel footprint, actual door geometry, original southern placement or missing support schedule. These require project source evidence or a separately approved redesign.')]:y=note(222,y,title,body,180)
c.showPage()

head('X02 R02 | PLANNING DECISION AND HOLD REGISTER','A concrete northern planning proposal for review / physical openings and final precinct selection remain protected decisions',4)
y=259
for title,body in [
 ('Recommended planning package','Retain the 22 x 26 m cloister and its 3.5 m walks, chapter hall and termination, refectory, east range and garden. Use the restored 3.5 m external gallery, controlled south-walk entry, 9 x 3.5 m chapter vestibule, refectory walk connection and separate night-lobby zone.'),
 ('Can be settled at this review','The northern alternative now has a coherent dimensioned circulation arrangement and a definite chapter-house approach. The research basis and exact R01-to-R02 changes are recorded. It can be accepted as a working planning proposal without approving cathedral cuts or replacing the southern baseline.'),
 ('Hold 1 / cathedral opening','CH-N5 exterior, N4 opening/window/jamb/respond envelopes and finished clear width remain unverified. Keep the continuous cathedral wall in the source. The red chapel rectangle is a conditional X01 test, not recovered exterior geometry.'),
 ('Hold 2 / site and building interfaces','Original protected southern site coordinates, public transept entrance, Great Library footprint, scholarly courtyard, actual night stair/floor levels and roof interfaces are not recovered. Do not draw guessed final site bodies or claim a full precinct comparison.'),
 ('Hold 3 / other cathedral authorities','F5ZL-C 248 supports remain missing. Bay angles, gallery Y4521/Y4950, Q1/J1 radii and working 14-vault generator identity remain separate unresolved records. This proposal does not select among them.')]:y=note(18,y,title,body,180)
note(222,259,'Decision requested after review','Review the 3.5 m connector and chapter vestibule as the northern working planning arrangement. Approval to promote the northern site, cut cathedral masonry or replace E5-C3-L1 is not implied.',180)
note(222,205,'Validation scope','Exact numerical results and preservation comparisons are in X02_R02_QA.json. Checked: retained R01 geometry, source hashes, valid polygons, gallery/root/garden fit, 1.2 m swept route reservations, chapter vestibule and night-zone containment. This is not structural or built-clearance approval.',180)
note(222,135,'Source register','P01-P02: recovered project reports and earlier chat decisions. H01-H02: Viollet-le-Duc. H03: Durham Cathedral. H04: Westminster Abbey. H05: Salisbury indexed archive text / prior project report, direct access unavailable. L01: older F5I proposal, not current authority. I01: R02 design interpretation. Full URLs and reliability notes are in the evidence ledger.',180)
note(222,63,'Next action','After architectural review, recover or explicitly redesign the held physical interfaces. Broad historical research need not be repeated to establish the circulation principles already documented.',180)
c.showPage();c.save()

after={p.name:sha(p) for p in (R/'sources').iterdir() if p.is_file()}
ck('SOURCE_BYTES_UNCHANGED',before==after,'All retained source SHA-256 values unchanged.')
qa={'revision':'X02_R02','status':'EXPERIMENTAL PLANNING PROPOSAL FOR REVIEW','checks':tests,'pass_count':sum(t['result']=='PASS' for t in tests),'fail_count':sum(t['result']=='FAIL' for t in tests),'metrics':metrics,'source_hashes_before':before,'source_hashes_after':after,'architectural_approval':False,'structural_validation':False,'actual_chapel_clearance_verified':False}
(O/'X02_R02_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
if qa['fail_count']:raise ValueError([t for t in tests if t['result']=='FAIL'])
report=f'''# X02 R02 - Research and Layout Proposal

Status: EXPERIMENTAL NORTHERN PLANNING PROPOSAL FOR ARCHITECTURAL REVIEW. No baseline promotion.

## Research recovered and checked
Two existing project reports (3 November 2026) were read in full from Research_03_Research_and_Tools.zip. Earlier experimental decisions for 3.5 m gallery, 22 x 26 m cloister, 9 x 12 m chapter hall plus 3 m end, northern refectory, eastern dormitory and separate night access were recovered from chat history. Original chat transcripts are not packaged, so these are recorded as retrieved decisions, not independently verified approval of saved geometry.

Targeted primary/institutional checking confirms Noyon circulation-conscious wall supports (Viollet-le-Duc III p.442), Durham's cloister as the hub of nave/chapter/refectory circulation, and Westminster's differentiated chapter/dormitory and secondary cloister access. The Salisbury indexed archive excerpt corroborates the previously researched two-bay vestibule sequence, but live page/PDF retrieval failed. No new historical dimensions are imposed on the project.

## Concrete revision
- Restore the external gallery planning band from 2.70 to 3.50 m; shift its widened center 0.40 m east. Portal center, 1.20 m throat, roots, north cloister, garden and range footprints remain fixed.
- Define a 9.00 x 3.50 m chapter vestibule within the unchanged east range, in two 4.50 m planning bays. These bay dimensions are a new design proposal, not a copied Salisbury measurement.
- Define a 9.00 x 6.60 m night-lobby functional zone; retain R01's night route and hypothetical stair box. No actual stair is designed.
- Add an explicit refectory-route reservation through the existing north/east walks. Public and scholarly access remain separate functional requirements pending their actual site source.

## Numerical comparison
New connector area {link.area:.5f} m2 vs R01 {g['n4_link'].area:.5f} m2. Modeled root gap {link.distance(roots):.4f} m; garden margin {link.distance(g['new_garden']):.4f} m. No root, garden or conditional chapel-test overlap. The conditional chapel rectangle still does not establish real chapel clearance. Vestibule area 31.50 m2, contained within the east range. Route widths are reservation bands, not verified finished clearances after stonework.

{qa['pass_count']} preservation / 2D geometry checks pass, {qa['fail_count']} fail. No architectural acceptance or structural validation claimed. Screen uses the same 12 transformed X01 roots, not the full 88 roots or missing 248-support F5ZL-C schedule.

## Protected and unresolved
F5ZK-C, F5ZN-A, the working inner/middle vault generator, Pass 6J, southern E5-C3-L1, R01 sources and all original research remain untouched. No Blender or generator operation. The recovered F5I legacy proposal is not a substitute for E5-C3-L1. North E5-R3/E5-S2 remains experimental; no final north-versus-south selection.

Hold physical cathedral cuts until actual CH-N5 exterior and jamb/respond/window geometry are recovered or explicitly redesigned. Original southern site placement, Great Library/public transept source, night stair/floor levels and roof interfaces remain unresolved. Further general historical research cannot recover this project's missing saved geometry.

## Deliverables
Four-page A3 PDF; physical 1:1 SVG (1 coordinate unit=1 metre); full geometry; dimensions/deltas; research evidence ledger; QA; sources; build script. PDF scales are presentation scales.

## Reproduce
Run python3 build_r02.py with shapely and reportlab installed. It reads only retained R01 JSON and research references, writes only outputs/ and this README, and never runs a cathedral generator. PDF visual QA is performed after rendering. SHA256SUMS.txt identifies packaged bytes.

## Next decision
Review the revised connector and chapter vestibule as the northern working planning arrangement. Cathedral masonry opening approval, northern site promotion and replacement of protected southern E5-C3-L1 remain separate protected decisions.
'''
(R/'README.md').write_text(report)
(R/'requirements.txt').write_text('shapely>=2.0\nreportlab>=4\n')
print(json.dumps({'pass':qa['pass_count'],'fail':qa['fail_count'],'metrics':metrics},indent=2))
