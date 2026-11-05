"""R04: coordinate vault interfaces in plan. No vault generator or 3D source is executed."""
from pathlib import Path
import json,math,csv,hashlib,xml.etree.ElementTree as ET
import numpy as np
import fitz
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch

R=Path(__file__).resolve().parents[1];I=R/'inputs';CX=20213.
S=json.loads((I/'F5ZK_C.json').read_text());MP=json.loads((I/'MASTER_PLAN_V02.json').read_text())
angles=np.array(S['bay_boundaries_deg']);beta=np.linspace(.5,179.5,10)
def put(name,x): (R/name).write_text(json.dumps(x,indent=2)+'\n')
def station(r,a):return np.array([CX+r*math.sin(math.radians(a)),r*math.cos(math.radians(a))])
def ellipse(a,rx=7169,ry=6657):return np.array([CX+rx*math.sin(math.radians(a)),-ry*math.cos(math.radians(a))])
def coords(poly):return [list(x) for x in poly.exterior.coords[:-1]]
def poly_from_path(path,transform):
 pts=[np.array(it[1]) for it in path['items'] if it[0]=='l']
 return Polygon([transform(p) for p in pts])
def recover_pdf():
 doc=fitz.open(I/'SOURCE_MP01D.pdf');draw=doc[1].get_drawings()
 path=draw[1];pp=np.array([list(it[1]) for it in path['items']]+[list(path['items'][-1][2])])
 sol=np.linalg.lstsq(np.column_stack([2*pp,np.ones(len(pp))]),(pp*pp).sum(axis=1),rcond=None)[0]
 center=sol[:2];scale=math.sqrt(sol[2]+center@center)/2933
 def to_native(p):return np.array([CX+(p[0]-center[0])/scale,(center[1]-p[1])/scale])
 checks=[]
 for k,rad in [(1,2933),(2,4085),(3,5285)]:
  pp=np.array([to_native(it[1]) for it in draw[k]['items']]);res=np.abs(np.linalg.norm(pp-[CX,0],axis=1)-rad)
  checks.append({'radius':rad,'max_residual':float(res.max())})
 bodies={f'D{k+1}':poly_from_path(draw[48+k],to_native) for k in range(9)}
 # Verify the simple outer parameter schedule against four independent window entry edges.
 passage=[ellipse(a) for a in beta];matches=[]
 for k in [0,2,6,8]:
  ps=np.array(coords(bodies[f'D{k+1}']))
  for j in [k,k+1]:matches.append(float(np.min(np.linalg.norm(ps-passage[j],axis=1))))
 # Source page's 9/9 program labeling and 7/7 orientation are south-first.
 # The saved F5ZN-A guide uses A1 north-first: preserve both identities explicitly.
 rec={'method':'Invert vector PDF plot transform using R2933 circle; independently check R4085/R5285 and outer window entries','source_pdf_sha256':hashlib.sha256((I/'SOURCE_MP01D.pdf').read_bytes()).hexdigest(),'PDF_page':2,'pdf_center':center.tolist(),'pdf_points_per_native_unit':scale,'radial_checks':checks,'outer_parameter_recovery_max_error':max(matches),'acceptance_native':.005,'source_indices':{'program_bodies':list(range(48,57)),'transition_cells':[63,64]},'D5_status':'SOURCE VECTOR IS +640 F5ZN-D6 TRIAL; not adopted as selected D4/D5 body','original_source_modified':False}
 put('VECTOR_RECOVERY_QA.json',rec)
 put('RECOVERED_SOURCE_PROGRAM_POLYGONS.json',{n:{'vertices':coords(p),'status':'SOURCE_WORKING_VECTOR' if n!='D5' else 'SOURCE_D6_PLUS640_TRIAL_NOT_ADOPTED'} for n,p in bodies.items()})
 assert max(c['max_residual'] for c in checks)<.005 and max(matches)<.005
 return bodies,passage
def build_cells(bodies,P):
 cells={};radii=[2933,4085,5285]
 for j,fam in enumerate(['I','M']):
  for k in range(7):
   a,b=angles[k:k+2];pts=[station(radii[j],a),station(radii[j+1],a),station(radii[j+1],b),station(radii[j],b)]
   cells[f'{fam}_A{k+1}']={'poly':Polygon(pts),'status':'PROTECTED_SOURCE_SET_OUT','group':fam,'source':'F5ZK-C numeric identity / saved F5ZN-A guide','aliases':f'MP01D {fam}{7-k} (south-first)'}
 # Passage panels are not nine arbitrary copies of an inner bay.
 outer_stops=[0,1,3,4,5,6,8,9]
 for k in range(7):
  a,b=angles[::-1][k:k+2];lo,hi=outer_stops[k:k+2]
  pts=[station(5285,a)]+P[lo:hi+1]+[station(5285,b)]
  cells[f'T{k+1}']={'poly':Polygon(pts),'status':'SELECTED_WORKING_PASSAGE_PANEL','group':'T','source':'MP01D Study D','source_middle':'M_A'+str(7-k),'D_frontages':[f'D{x+1}' for x in range(lo,hi)]}
 # Recovered bodies are display references. Chapel necks below are a new plan-only candidate.
 necks={};program={}
 chapel_ids={'D2','D4','D5','D6','D8'}
 for k in range(9):
  name=f'D{k+1}';body=bodies[name];pts=np.array(coords(body))
  if name in chapel_ids:
   neck=Polygon([P[k],pts[0],pts[-1],P[k+1]])
   necks[name]=neck
  else:neck=Polygon()
  # Never promote or trim the source D6 +640 cap into an alleged D4/D5 original.
  program[name]={'body':body,'neck':neck,'status':'SOURCE_WORKING_BODY_PLUS_CANDIDATE_NECK' if name!='D5' else 'ENTRY_CANDIDATE_ONLY_BODY_BASELINE_UNRECOVERED','kind':'CHAPEL' if name in chapel_ids else 'WINDOW','frontage':LineString([P[k],P[k+1]])}
 # Shared ownership: retain the exact new positive-area overlaps as experimental divider reservations.
 raw={n:p['body'].union(p['neck']) for n,p in program.items()}
 dividers={};overlap_rows=[]
 for j in range(1,9):
  a,b=f'D{j}',f'D{j+1}';intersection=raw[a].intersection(raw[b]);old=bodies[a].intersection(bodies[b])
  if intersection.area>1e-5:
   dividers[f'B{j}']=intersection
   overlap_rows.append({'divider':f'B{j}','owners':[a,b],'source_body_overlap_area':old.area,'candidate_neck_and_body_overlap_area':intersection.area,'status':'PROPOSED_SINGLE_OWNER_PLAN_RESERVATION_NOT_MASONRY'})
 for name in program:
  program[name]['usable_candidate']=raw[name].difference(unary_union(list(dividers.values())))
 return cells,program,necks,dividers,overlap_rows
def interfaces(cells,program,P):
 rows=[]
 for k in range(1,8):
  shared=cells[f'I_A{k}']['poly'].boundary.intersection(cells[f'M_A{k}']['poly'].boundary)
  rows.append({'from':f'I_A{k}','to':f'M_A{k}','type':'SHARED_R1_ARCH','length':shared.length,'status':'SOURCE_SET_OUT_MATCH','extra_inner_piers':0})
  tk=8-k;shared=cells[f'M_A{k}']['poly'].boundary.intersection(cells[f'T{tk}']['poly'].boundary)
  rows.append({'from':f'M_A{k}','to':f'T{tk}','type':'SHARED_R2_ARCH','length':shared.length,'status':'SELECTED_WORKING_PASSAGE_SET_OUT','extra_inner_piers':0})
 for t,data in cells.items():
  if data['group']!='T':continue
  for n in data['D_frontages']:
   length=program[n]['frontage'].length
   rows.append({'from':t,'to':n,'type':'OUTER_ENTRY_FRONTAGE','length':length,'status':'CANDIDATE_CHAPEL_NECK' if program[n]['kind']=='CHAPEL' else 'SOURCE_WINDOW_ENTRY','extra_inner_piers':0})
 collars={}
 for side,sgn,a in [('N',1,.5),('S',-1,179.5)]:
  for fam,ri,ro in [('I',2933,4085),('M',4085,5285),('T',5285,6657)]:
   inner=station(ri,a);outer=station(ro,a) if fam!='T' else ellipse(.5 if side=='S' else 179.5)
   q0=[CX,sgn*ri];q1=[CX,sgn*ro]
   collar=Polygon([q0,q1,outer,inner]);name=f'Q5_{side}_{fam}'
   collars[name]=collar
   rows.append({'from':f'Q5_{side}_{fam}','to':f'{fam}_'+('A1' if side=='N' else 'A7') if fam!='T' else ('T7' if side=='N' else 'T1'),'type':'SHOULDER_RECEIVING_STRIP','length':float(np.linalg.norm(outer-inner)),'status':'SOURCE_WORKING_COLLAR' if fam=='T' else 'DERIVED_PLAN_ONLY_STRIP_NOT_NEW_VAULT','extra_inner_piers':0,'inner_offset':float(np.linalg.norm(inner-q0)),'outer_offset':float(np.linalg.norm(outer-q1)),'area':collar.area})
 put('CONNECTION_REGISTER.json',rows)
 with (R/'CONNECTION_REGISTER.csv').open('w') as f:
  cols=['from','to','type','length','status','extra_inner_piers','inner_offset','outer_offset','area'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
 return rows,collars
def trace(ax,p,color='k',lw=.8,ls='-',fill=None,alpha=1):
 if p.is_empty:return
 if p.geom_type=='MultiPolygon':
  for g in p.geoms:trace(ax,g,color,lw,ls,fill,alpha)
  return
 v=np.array(p.exterior.coords);ax.plot(v[:,0],v[:,1],color=color,lw=lw,ls=ls)
 if fill:ax.add_patch(Patch(v,facecolor=fill,edgecolor='none',alpha=alpha))
def save(fig,name):
 fig.savefig(R/(name+'.png'),dpi=180);fig.savefig(R/(name+'.svg'));plt.close(fig)
def decorations(ax,title,lim):
 ax.set_aspect('equal');ax.set_xlim(lim[:2]);ax.set_ylim(lim[2:]);ax.set_title(title,loc='left',fontsize=11);ax.grid(c='.9',lw=.4,ls='--');ax.set_xlabel('X east [native units]');ax.set_ylabel('Y north [native units]')
def draw_chevet(ax,cells,program,dividers,collars,labels=True):
 for n,d in cells.items():
  p=d['poly'];trace(ax,p,lw=.65 if d['group']!='T' else .8,fill='#edf1ef' if d['group']=='T' else None)
  v=np.array(coords(p));boss=np.array(p.representative_point().coords[0])
  if len(v)==4:
   # Exact diagonal intersection, not a changed vault mesh.
   boss=np.array(LineString([v[0],v[2]]).intersection(LineString([v[1],v[3]])).coords[0])
  elif len(v)==5:
   boss=np.array(LineString([v[0],v[3]]).intersection(LineString([v[4],v[1]])).coords[0])
  for pt in v:ax.plot([pt[0],boss[0]],[pt[1],boss[1]],c='.65',lw=.45,ls='--')
  if labels:ax.text(boss[0],boss[1],n,fontsize=6,ha='center',va='center',bbox=dict(facecolor='white',edgecolor='none',pad=.5))
 for n,d in program.items():
  body=d['body'];trace(ax,body,color='.5' if n=='D5' else 'k',ls='--' if n=='D5' else '-',lw=.8,fill='#f4ecdf' if d['kind']=='CHAPEL' else '#eaf0f3')
  if not d['neck'].is_empty:trace(ax,d['neck'],color='#b52c28',ls='--',lw=1,fill='#faeeee',alpha=.7)
  if labels:
   pt=body.representative_point();ax.text(pt.x,pt.y,n+'\n'+d['kind'],fontsize=7,ha='center',va='center')
 for n,p in dividers.items():
  trace(ax,p,color='#b52c28',ls='--',lw=.7,fill='#e6c1c0',alpha=.9)
 for n,p in collars.items():trace(ax,p,color='#b52c28',ls='--',lw=.9)
def context_geometry():
 qa=json.loads((I/'R05_PLAN_QA.json').read_text());D=json.loads((I/'R05_PARENT_GEOMETRY.json').read_text())
 masonry={}
 for p in D['variants']['square_infill']['parts']:
  if p['role']=='lower_mass':
   pts=np.array(p['vertices']);pts=pts[pts[:,2]==pts[:,2].min(),:2]
   # Use scheduled source part's bottom face vertex order.
   faces=[f for f in p['faces'] if all(p['vertices'][k][2]==0 for k in f)];masonry[p['corner']]=unary_union([Polygon([p['vertices'][k][:2] for k in f]) for f in faces])
 return masonry,qa
def drawing(cells,program,dividers,rows,collars):
 fig,ax=plt.subplots(figsize=(12,11));draw_chevet(ax,cells,program,dividers,collars)
 for sign in [-1,1]:
  for r in [2933,4085,5285,6657]:ax.plot([17333,CX],[sign*r]*2,c='.55',ls='--',lw=.5)
 ax.axvline(CX,c='.5',ls='--',lw=.5)
 ax.text(18500,0,'Q5 / choir\nreceiving strips\nat north + south',fontsize=8,ha='center')
 ax.annotate('T6: D7 + D8\n5-sided passage panel',(23900,4500),(17800,7200),arrowprops=dict(arrowstyle='-',color='#a22'),fontsize=7,c='#a22')
 ax.annotate('T2: D2 + D3\n5-sided passage panel',(23900,-4500),(17800,-7000),arrowprops=dict(arrowstyle='-',color='#a22'),fontsize=7,c='#a22')
 ax.annotate('D5 +640 source trial shown gray;\nselected cap baseline still missing',(31286,0),(27400,9200),arrowprops=dict(arrowstyle='-',color='.5'),fontsize=7,c='.4')
 decorations(ax,'CHEVET | 7 inner + 7 middle + 9 outer compartments',(16600,32600,-10100,10100))
 fig.suptitle('F5ZP R04 | Study D vault connections in plan',x=.08,ha='left',fontsize=15)
 fig.text(.08,.035,'Black: recovered set-out / source working boundaries  |  Gray dashed: rib guides and excluded D5 trial\nRed dashed: proposed entry necks, receiving strips and divider reservations  |  No new interior piers',fontsize=8)
 fig.tight_layout(rect=[0,.07,1,.95]);save(fig,'CHEVET_779_CONNECTIONS')
 # Whole plan: keep recovered bay envelopes, special R05 mass and half-stations separate.
 masonry,qa=context_geometry();mask=unary_union(list(masonry.values()))
 fig,ax=plt.subplots(figsize=(18,7))
 for ob in MP['objects']:
  if ob.get('type') not in ['polyline','polygon'] or not ob.get('points') or ob['id'].startswith(('AMB','CHEVET')):continue
  pts=np.array(ob['points'])
  if pts.shape[1]!=2:continue
  if len(pts)<4:
   ax.plot(pts[:,0],pts[:,1],color='k',lw=.45)
   continue
  p=Polygon(pts)
  if not p.is_valid or p.area==0:continue
  if p.centroid.x>CX:continue
  geom=p.difference(mask);trace(ax,geom,lw=.45)
  # Large envelopes are not asserted to be final individual vault subdivisions.
  if '-CENTRAL' in ob['id'] and ob['id'].startswith(('N','Q')):
   ax.text(p.centroid.x,0,ob['id'].split('-')[0],fontsize=6,ha='center')
   # Explicit diagram guides only: no assertion of a recovered high-rib plan.
   vv=np.array(coords(p))
   if len(vv)==4:
    for a,b in [(0,2),(1,3)]:ax.plot(vv[[a,b],0],vv[[a,b],1],c='.75',ls='--',lw=.35)
 # Documented transept bands are missing from the previous reconstruction's object list.
 # Add set-out rectangles only; these are not new masonry or certified vault meshes.
 for sg in [-1,1]:
  for a,b in [(2933,6965),(6965,8837),(8837,10709)]:
   for sx in [-1,1]:
    for ri,ro in zip([2933,4085,5429],[4085,5429,6965]):
     p=box(min(sx*ri,sx*ro),min(sg*a,sg*b),max(sx*ri,sx*ro),max(sg*a,sg*b)).difference(mask)
     trace(ax,p,lw=.45)
 for x in [2933,6965,10709,14165,17333,CX]:
  outer=6965+(6657-6965)*(x-2933)/(CX-2933)
  for sg in [-1,1]:ax.plot([x,x],[sg*2933,sg*outer],color='k',lw=.45)
 for p in masonry.values():trace(ax,p,lw=1,fill='#82786f')
 for v in qa['vault_cells']:
  p=box(*v['bounds']);trace(ax,p,lw=.7)
  xy=np.array(coords(p));ax.plot(xy[[0,2],0],xy[[0,2],1],c='.6',ls='--',lw=.4);ax.plot(xy[[1,3],0],xy[[1,3],1],c='.6',ls='--',lw=.4)
 draw_chevet(ax,cells,program,dividers,collars,False)
 # N1–N9 midpoint lines are documented in MP02; do not invent Q1 subdivisions.
 stations=[-40013,-36269,-32597,-28997,-25397,-21797,-18197,-14597,-10853,-6965]
 for a,b in zip(stations[:-1],stations[1:]):
  x=(a+b)/2
  for sg in [-1,1]:ax.plot([x,x],np.array([2933,6965])*sg,c='.6',ls='--',lw=.45)
 for x,txt in [(-22000,'Nave: three lower lateral bands each side'),(0,'R05: J11 solid; J12/J13 retained'),(11600,'Choir taper + Q5 receiving edges'),(25700,'Selected Study D 7–7–9')]:ax.annotate(txt,(x,0),(x,12500),ha='center',fontsize=8,arrowprops=dict(arrowstyle='-',color='.6',lw=.5))
 decorations(ax,'WHOLE FLOOR PLAN | source bay envelopes, selected crossing and chevet interfaces',(-41200,33000,-12000,14700));fig.text(.065,.02,'Native units; SI unset. Lower Q1/N10/T1 subdivisions and physical supports remain subject to source recovery. Rib guide lines do not certify arch profiles or bearing contact.',fontsize=8)
 fig.tight_layout(rect=[0,.05,1,.98]);save(fig,'WHOLE_FLOOR_PLAN_CONNECTIONS')
 # Explicit south-first to north-first mapping and the 7-to-9 topology.
 fig,(a,b)=plt.subplots(1,2,figsize=(13,7));a.axis('off');b.axis('off')
 labels=['MP01D passage','Saved middle','Outer frontages','Panel sides']
 table=[[f'T{k}',f'M_A{8-k}',', '.join(cells[f'T{k}']['D_frontages']),len(coords(cells[f'T{k}']['poly']))] for k in range(1,8)]
 t=a.table(cellText=table,colLabels=labels,loc='center',cellLoc='center',colWidths=[.2,.2,.4,.2]);t.auto_set_font_size(False);t.set_fontsize(9);t.scale(1,2)
 a.set_title('Connection ownership | IDs kept distinct',loc='left',fontsize=11)
 b.text(0,1,'Architectural coordination carried forward',fontsize=12,weight='bold',va='top')
 notes=['14 protected inner/middle cells retain their coordinates.','9 outer compartments: 5 chapels + 4 windows.','T2 and T6 each have two outer frontages and five sides.','Seven passage panels explain the 7-to-9 handoff;\nthey are not nine copied radial wedges.','Five red entry necks are a new plan-only candidate.','B1/B3/B6/B8 remain single-owner divider reservations.','Q5 strips are receiving geometry, not extra vaults/piers.','D5 +640 trial is displayed separately, not adopted.','R05 crossing concept remains unchanged.','No new detailed ribs, mouldings or 3D vaults generated.']
 for k,n in enumerate(notes):b.text(0,.9-k*.085,n,fontsize=9,va='top')
 fig.tight_layout();save(fig,'VAULT_CONNECTION_OWNERSHIP')
def native_svg(cells,program,collars,dividers):
 root=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','viewBox':'16500 -10200 16500 20400','width':'16500','height':'20400'})
 ET.SubElement(root,'metadata').text='Native project coordinate geometry, X east Y north. Display Y is inverted by group transform. Physical SI coefficient null. Experimental R04.'
 g=ET.SubElement(root,'g',{'transform':'scale(1,-1)','fill':'none','stroke-width':'12'})
 for n,d in cells.items():
  ET.SubElement(g,'polygon',{'id':n,'points':' '.join(f'{x:.12g},{y:.12g}' for x,y in coords(d['poly'])),'stroke':'black'})
 for n,d in program.items():
  ET.SubElement(g,'polygon',{'id':n+'_source_body','points':' '.join(f'{x:.12g},{y:.12g}' for x,y in coords(d['body'])),'stroke':'gray' if n=='D5' else 'black',**({'stroke-dasharray':'60 40'} if n=='D5' else {})})
 for prefix,group in [('neck_', {n:d['neck'] for n,d in program.items()}),('collar_',collars),('divider_',dividers)]:
  for n,p in group.items():
   if p.is_empty:continue
   ET.SubElement(g,'polygon',{'id':prefix+n,'points':' '.join(f'{x:.12g},{y:.12g}' for x,y in coords(p)),'stroke':'#b52c28','stroke-dasharray':'60 40'})
 ET.ElementTree(root).write(R/'CHEVET_779_NATIVE_COORDINATES.svg',encoding='utf-8',xml_declaration=True)
def validate(cells,program,rows,dividers,overlap_rows):
 tests=[]
 def check(n,result,detail=None):tests.append({'name':n,'pass':bool(result),'detail':detail})
 check('Protected I/M cell count',sum(d['group'] in ['I','M'] for d in cells.values())==14)
 check('Nine outer compartments',len(program)==9)
 check('Five chapels/four windows',sum(d['kind']=='CHAPEL' for d in program.values())==5)
 check('T2/T6 five-sided',all(len(coords(cells[n]['poly']))==5 for n in ['T2','T6']))
 check('No added inner piers',all(r['extra_inner_piers']==0 for r in rows))
 for n in ['T2','T6']:
  p=cells[n]['poly'];v=np.array(coords(p));boss=LineString([v[0],v[3]]).intersection(LineString([v[4],v[1]]))
  check('Five plan branches inside '+n,all(p.buffer(1e-7).covers(LineString([pt,boss.coords[0]])) for pt in v),{'boss':list(boss.coords[0])})
 for n,d in cells.items():check('Valid cell '+n,d['poly'].is_valid and d['poly'].area>0)
 for fam,sourcefam in [('I','AMB-I'),('M','AMB-M')]:
  for k in range(1,8):
   ob=next(o for o in MP['objects'] if o['id']==f'{sourcefam}-A{k}-CHORDAL-FOOTPRINT')
   error=cells[f'{fam}_A{k}']['poly'].symmetric_difference(Polygon(ob['points'])).area
   check('Protected source footprint regression '+fam+str(k),error<1e-6,error)
 for r in rows:
  if 'SHARED' in r['type']:check(r['type']+' '+r['from']+' '+r['to'],r['length']>0)
 for n,d in program.items():
  if not d['neck'].is_empty:
   check('Neck valid '+n,d['neck'].is_valid and d['neck'].area>0)
   length=d['neck'].boundary.intersection(d['frontage']).length
   check('Neck has full passage frontage '+n,abs(length-d['frontage'].length)<1e-7,{'length':length})
   check('Neck touches source body '+n,d['neck'].boundary.intersection(d['body'].boundary).length>0)
 for i in range(1,10):
  for j in range(i+1,10):
   area=program[f'D{i}']['usable_candidate'].intersection(program[f'D{j}']['usable_candidate']).area
   check(f'Exclusive candidate ownership D{i}/D{j}',area<1e-4,area)
 masonry,qa=context_geometry()
 for part in qa['masonry_parts']:
  check('Selected R05 full footprint '+part['corner'],abs(masonry[part['corner']].area-part['plan_area_project_units2'])<1e-6)
 for p in R.glob('*.svg'):ET.parse(p);check('SVG parses '+p.name,True)
 put('PLAN_QA.json',{'status':'EXPERIMENTAL 2D COORDINATION','checks':tests,'passed':sum(t['pass'] for t in tests),'failed':sum(not t['pass'] for t in tests),'physical_m_per_unit':None,'approved_geometry_changed':False,'new_inner_piers':0,'new_chapel_necks':5,'source_body_overlap_ownership':overlap_rows,'structural_validation':False,'D5_selected_cap':'UNRESOLVED; +640 source trial not adopted','vault_count_definition':'7 inner +7 middle +9 exterior program compartments. Seven passage receiving panels are separately named T1–T7; this is not a certificate of 23 complete built vault meshes.'})
 assert all(t['pass'] for t in tests),[t for t in tests if not t['pass']]
def main():
 bodies,P=recover_pdf();cells,program,necks,dividers,overlaps=build_cells(bodies,P);rows,collars=interfaces(cells,program,P);drawing(cells,program,dividers,rows,collars);native_svg(cells,program,collars,dividers);validate(cells,program,rows,dividers,overlaps)
 put('PLAN_GEOMETRY.json',{'units':'native 1:1, SI unset','cells':{n:{**{k:v for k,v in d.items() if k!='poly'},'vertices':coords(d['poly'])} for n,d in cells.items()},'program':{n:{'kind':d['kind'],'status':d['status'],'source_body':coords(d['body']),'entry_neck':coords(d['neck']) if not d['neck'].is_empty else []} for n,d in program.items()},'outer_passage_nodes':[p.tolist() for p in P],'outer_ellipse_parameters_deg_south_to_north':beta.tolist(),'source_angular_authority_conflict':'F5ZK-C unequal schedule retained for source comparison; 30..150 protected historical prose remains a separate unresolved record.'})
 print('R04_PLAN_COMPLETE')
if __name__=='__main__':main()
