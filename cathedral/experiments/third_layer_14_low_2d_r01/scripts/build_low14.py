"""User-corrected third layer: 14 lower vault footprints, paired per seven bays. 2D only."""
from pathlib import Path
import json,hashlib,csv,xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch

R=Path(__file__).resolve().parents[1];I=R/'inputs'
def put(n,d):(R/n).write_text(json.dumps(d,indent=2)+'\n')
def points(p):return np.array(p.exterior.coords[:-1])
def outline(ax,p,color='k',lw=.8,ls='-',fill=None):
 pp=np.array(p.exterior.coords)
 if fill:ax.add_patch(Patch(pp,facecolor=fill,edgecolor='none'))
 ax.plot(pp[:,0],pp[:,1],c=color,lw=lw,ls=ls)
def boss_and_guides(ax,p,label=None):
 v=points(p);b=LineString([v[0],v[2]]).intersection(LineString([v[1],v[3]]));bp=np.array(b.coords[0])
 for pt in v:ax.plot([pt[0],bp[0]],[pt[1],bp[1]],c='.68',lw=.5,ls='--')
 if label:ax.text(*bp,label,fontsize=7,ha='center',va='center',bbox=dict(facecolor='white',edgecolor='none',pad=.6))
 return bp
def save(fig,n):
 fig.savefig(R/(n+'.png'),dpi=170);fig.savefig(R/(n+'.svg'));plt.close(fig)
def main():
 d=json.loads((I/'R04_PLAN_GEOMETRY.json').read_text());parents={k:Polygon(v['vertices']) for k,v in d['cells'].items() if k.startswith('T')}
 children={};pairs=[];dividers={};metrics=[]
 for k in range(1,8):
  name='T'+str(k);v=points(parents[name]);inner_a,inner_b=v[0],v[-1];im=(inner_a+inner_b)/2
  # Preserve the existing extra outer receiver at T2/T6. Else bisect the existing outer edge.
  if len(v)==5:oa,om,ob=v[1:4]
  else:oa,ob=v[1:3];om=(oa+ob)/2
  polygons=[Polygon([inner_a,oa,om,im]),Polygon([im,om,ob,inner_b])]
  ids=[]
  for j,p in enumerate(polygons):
   n=f'L3-{2*k-1+j:02d}';ids.append(n)
   children[n]={'parent_sector':name,'middle_bay':d['cells'][name]['source_middle'],'poly':p,'status':'EXPERIMENTAL_2D_FOOTPRINT','height_status':'LOWER_THAN_INNER_AND_MIDDLE; exact levels unresolved'}
  dividers[name]=LineString([im,om])
  pairs.append({'sector':name,'middle_bay':d['cells'][name]['source_middle'],'lower_vaults':ids,'window_above_pair':'W'+str(k),'inner_midpoint':im.tolist(),'outer_receiver':om.tolist(),'new_inner_receiver':'Low intermediate receiving line proposed; no final pier/shaft dimensions established','exact_vertical_levels':None})
  for j,n in enumerate(ids):
   boundary=LineString([inner_a,im] if j==0 else [im,inner_b])
   metrics.append({'vault':n,'sector':name,'middle_bay':d['cells'][name]['source_middle'],'inner_receiving_frontage':boundary.length,'area':polygons[j].area,'window_above_pair':'W'+str(k)})
 put('PAIR_REGISTER.json',pairs)
 with (R/'LOW_VAULT_REGISTER.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)
 # Full chevet context: 7 +7 preserved; 14 new lower-layer footprints; 9 exterior bodies distinct.
 fig,ax=plt.subplots(figsize=(12,11))
 for n,data in d['cells'].items():
  if not n.startswith(('I_','M_')):continue
  p=Polygon(data['vertices']);outline(ax,p,lw=.65);boss_and_guides(ax,p,n.replace('_',' '))
 for n,data in children.items():
  p=data['poly'];outline(ax,p,lw=.8,fill='#eef2f3');boss_and_guides(ax,p,n)
 for name,line in dividers.items():
  pp=np.array(line.coords);ax.plot(pp[:,0],pp[:,1],c='#b22b25',lw=1.1,ls='--')
 for n,data in d['program'].items():
  p=Polygon(data['source_body']);outline(ax,p,color='.62',lw=.65,ls='--',fill='#f5f3ed')
  cp=p.representative_point();ax.text(cp.x,cp.y,n+'\n'+data['kind'].lower(),ha='center',fontsize=7,c='.4')
  if data['entry_neck']:outline(ax,Polygon(data['entry_neck']),color='.72',lw=.5,ls='--')
 for p in pairs:
  im=np.array(p['inner_midpoint']);ax.plot(*im,marker='D',ms=3,color='.35');ax.annotate(p['window_above_pair'],im,xytext=(-9,8),textcoords='offset points',fontsize=7,color='.3')
 ax.axvline(20213,c='.65',ls='--',lw=.5);ax.text(18750,0,'Choir / Q5\ncontext',ha='center',fontsize=9)
 ax.set(xlim=(17000,32600),ylim=(-10000,10000),xlabel='X east [native units]',ylabel='Y north [native units]');ax.set_aspect('equal');ax.grid(c='.91',ls='--',lw=.5)
 ax.set_title('7 inner + 7 middle + 14 lower third-layer vaults',loc='left',fontsize=13)
 fig.suptitle('F5ZP | corrected third-layer rhythm',x=.08,ha='left',fontsize=16)
 fig.text(.08,.033,'Red dashed: proposed low-vault divisions. Gray rib lines: 2D guides. W1–W7: windows ABOVE each pair.\nNine gray exterior chapel/window compartments are a separate program, not the third-layer vault count. Exact lower levels remain unset.',fontsize=8)
 fig.tight_layout(rect=[0,.07,1,.95]);save(fig,'THIRD_LAYER_14_PLAN')
 # Enlarged former T2: two quads replace the previous single five-branch vault reading.
 fig,ax=plt.subplots(figsize=(10,8));T=parents['T2'];M=Polygon(d['cells']['M_A6']['vertices']);outline(ax,M,color='.5',fill='#f5f5f2')
 for n in ['L3-03','L3-04']:
  p=children[n]['poly'];outline(ax,p,fill='#edf2f3');boss_and_guides(ax,p,n)
 pp=np.array(dividers['T2'].coords);ax.plot(pp[:,0],pp[:,1],c='#b22b25',ls='--',lw=1.5)
 midpoint=pp[0];ax.plot(*midpoint,'D',c='.3',ms=4);ax.annotate('W2: one upper window\nabove both low entrances',midpoint,xytext=(26400,-2700),textcoords='data',ha='center',fontsize=8,arrowprops=dict(arrowstyle='-',color='.4'),bbox=dict(facecolor='white',edgecolor='none',alpha=.9))
 for name in ['D2','D3']:
  p=Polygon(d['program'][name]['source_body']);outline(ax,p,color='.65',lw=.65,ls='--');pt=p.representative_point();ax.text(pt.x,pt.y,name+' context',c='.5',fontsize=8,ha='center')
  if d['program'][name]['entry_neck']:outline(ax,Polygon(d['program'][name]['entry_neck']),color='.65',lw=.65,ls='--')
 tv=points(T);ax.text(23200,-3400,'Middle A6\none higher vault',ha='center',fontsize=10)
 ax.set(xlim=(21900,28600),ylim=(-9000,-2300),xlabel='X east [native units]',ylabel='Y north [native units]');ax.set_aspect('equal');ax.grid(c='.91',ls='--',lw=.5)
 ax.set_title('T2 sector | two LOWER vaults, not one five-branch vault',loc='left',fontsize=12)
 fig.text(.09,.035,'Existing sector outline retained. New divider goes to the existing outer O2 receiver.\nIts inner end is a low receiving-line proposal; supporting masonry dimensions are unresolved.',fontsize=8)
 fig.tight_layout(rect=[0,.075,1,1]);save(fig,'T2_TWO_LOWER_VAULTS')
 # Relative elevation: precise topology, deliberately no invented project heights.
 def pointed(cx,half,spring,rise):
  c=(rise*rise-half*half)/(2*half);rad=half+c;x=np.linspace(-half,0,120)
  y=spring+np.sqrt(np.maximum(rad*rad-(x-c)**2,0))
  return np.r_[cx+x,cx-x[::-1]],np.r_[y,y[::-1]]
 fig,ax=plt.subplots(figsize=(12,7))
 ax.fill_between([-.08,1.08],[0,0],[1.23,1.23],color='#f1f0eb')
 # A higher supporting wall/elevation envelope, kept symbolic.
 x,y=pointed(.5,.5,.35,.85);ax.plot(x,y,c='.6',ls='--',lw=1)
 for c in [.25,.75]:
  x,y=pointed(c,.215,.2,.28)
  polygon=np.array([[c-.215,0],[c-.215,.2],*zip(x,y),[c+.215,0]])
  ax.add_patch(Patch(polygon,facecolor='white',edgecolor='black',lw=1.2))
  ax.text(c,.11,'low vault\nentrance',ha='center',fontsize=11)
 x,y=pointed(.5,.14,.85,.18)
 window=np.array([[.36,.64],[.36,.85],*zip(x,y),[.64,.64]])
 ax.add_patch(Patch(window,facecolor='#e4f0f5',edgecolor='black',lw=1.2));ax.text(.5,.74,'ONE\nWINDOW',ha='center',fontsize=11)
 ax.axhline(.48,c='#b22b25',ls='--',lw=.8);ax.text(1.1,.48,'third-layer vaults\nsignificantly lower',va='center',fontsize=10,c='#a22')
 ax.axhline(1.2,c='.55',ls='--',lw=.8);ax.text(1.1,1.2,'inner / middle\nhigher-vault zone',va='center',fontsize=10,c='.4')
 ax.annotate('',(.03,-.08),xytext=(.97,-.08),arrowprops=dict(arrowstyle='<->',lw=.8,color='.4'));ax.text(.5,-.13,'ONE BAY = TWO LOWER VAULTS',ha='center',fontsize=12)
 ax.text(.5,.52,'solid wall / spandrel above the two openings',ha='center',fontsize=9,c='.4')
 ax.set_xlim(-.2,1.53);ax.set_ylim(-.19,1.34);ax.set_aspect('equal');ax.axis('off')
 ax.set_title('Bay elevation | one window above two vault entrances',loc='left',fontsize=14)
 fig.text(.08,.025,'SCHEMATIC HEIGHT RELATION ONLY. No spring, crown, sill or head elevation selected.\nThe drawn vertical proportions illustrate the user’s intent and are not dimensional defaults.',fontsize=9)
 fig.tight_layout(rect=[0,.08,1,1]);save(fig,'ONE_WINDOW_TWO_ENTRANCES')
 # Native-coordinate plan export; schematic heights never enter this file.
 root=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','viewBox':'17000 -10000 15600 20000','width':'15600','height':'20000'})
 ET.SubElement(root,'metadata').text='2D native project coordinates. 14 lower third-layer vault footprint candidates. Exact heights null. X east/Y north, display Y inverted. No approved geometry changed.'
 g=ET.SubElement(root,'g',{'transform':'scale(1,-1)','fill':'none','stroke':'black','stroke-width':'10'})
 for n,data in children.items():ET.SubElement(g,'polygon',{'id':n,'points':' '.join(f'{x:.15g},{y:.15g}' for x,y in points(data['poly']))})
 for n,line in dividers.items():ET.SubElement(g,'polyline',{'id':n+'_low_division','points':' '.join(f'{x:.15g},{y:.15g}' for x,y in line.coords),'stroke':'#b22b25','stroke-dasharray':'55 35'})
 ET.ElementTree(root).write(R/'LOW14_NATIVE_COORDINATES.svg',encoding='utf-8',xml_declaration=True)
 tests=[]
 def check(n,ok,value=None):tests.append({'name':n,'pass':bool(ok),'value':value})
 check('14 third-layer vault footprints',len(children)==14)
 check('7 paired bays/windows',len(pairs)==7)
 check('14 inner/middle cells retained',sum(n.startswith(('I_','M_')) for n in d['cells'])==14)
 for k,pair in enumerate(pairs,1):
  ps=[children[n]['poly'] for n in pair['lower_vaults']];parent=parents[pair['sector']];union=unary_union(ps)
  check('Two vaults in '+pair['sector'],len(ps)==2)
  check('Original sector coverage '+pair['sector'],parent.symmetric_difference(union).area<1e-5,parent.symmetric_difference(union).area)
  check('No double-covered vault area '+pair['sector'],ps[0].intersection(ps[1]).area<1e-5,ps[0].intersection(ps[1]).area)
  v=points(parent);expected=np.linalg.norm(v[0]-v[-1])/2
  for n in pair['lower_vaults']:
   poly=children[n]['poly'];check('Valid quadrilateral '+n,poly.is_valid and len(points(poly))==4 and poly.area>0)
   measure=next(m for m in metrics if m['vault']==n)['inner_receiving_frontage'];check('Half-bay receiving rhythm '+n,abs(measure-expected)<1e-7)
 check('T2 division uses original outer receiver',np.array_equal(np.array(dividers['T2'].coords)[1],points(parents['T2'])[2]))
 check('T6 division uses original outer receiver',np.array_equal(np.array(dividers['T6'].coords)[1],points(parents['T6'])[2]))
 unavailable=[]
 for path,h in json.loads((I/'PARENT_HASHES.json').read_text()).items():
  pth=Path(path)
  if pth.exists():check('Parent unchanged '+pth.name,hashlib.sha256(pth.read_bytes()).hexdigest()==h)
  else:unavailable.append(path)
 for p in R.glob('*.svg'):ET.parse(p);check('SVG parses '+p.name,True)
 put('LOW14_QA.json',{'status':'EXPERIMENTAL_2D_USER_CORRECTION','checks':tests,'passed':sum(t['pass'] for t in tests),'failed':sum(not t['pass'] for t in tests),'parent_paths_unavailable':unavailable,'third_layer_count':14,'two_per_bay':True,'third_layer_significantly_lower':True,'exact_spring':None,'exact_crown':None,'window_sill':None,'window_head':None,'clear_opening_width':None,'physical_m_per_native_unit':None,'3D_generated':False,'approved_geometry_modified':False,'structural_validation':False})
 put('LOW14_GEOMETRY.json',{'plan_units':'native project units; SI unset','vaults':{n:{**{k:v for k,v in data.items() if k!='poly'},'vertices':points(data['poly']).tolist()} for n,data in children.items()},'pairs':pairs,'protected_inner_middle':{n:data for n,data in d['cells'].items() if n.startswith(('I_','M_'))},'relative_height_requirement':'Third layer significantly lower than inner and middle; one upper window over the two lower entrances in each bay','vertical_dimensions':None,'nine_exterior_compartments':'Separate Study D program retained as context; not the third-layer vault count','elevation_plot_coordinates':'dimensionless illustration only, never architectural height inputs'})
 assert all(t['pass'] for t in tests),[t for t in tests if not t['pass']]
 print('LOW14_COMPLETE',sum(t['pass'] for t in tests),'checks')
if __name__=='__main__':main()
