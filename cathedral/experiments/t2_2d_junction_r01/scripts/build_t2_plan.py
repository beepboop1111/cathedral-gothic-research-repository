"""Enlarged T2 plan: preserve R04, measure interfaces, and isolate one small source-vector recovery correction."""
from pathlib import Path
import json,csv,hashlib,math,xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import nearest_points
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch

R=Path(__file__).resolve().parents[1];I=R/'inputs'
def put(name,data): (R/name).write_text(json.dumps(data,indent=2)+'\n')
def coords(p):return np.array(p.exterior.coords[:-1])
def outline(ax,p,color='k',lw=.9,ls='-',fill=None,alpha=1):
 v=np.array(p.exterior.coords)
 if fill:ax.add_patch(Patch(v,facecolor=fill,edgecolor='none',alpha=alpha))
 ax.plot(v[:,0],v[:,1],color=color,lw=lw,ls=ls)
def label(ax,pt,text,offset=(7,7),size=8,color='k'):
 ax.annotate(text,pt,xytext=offset,textcoords='offset points',fontsize=size,color=color,
             bbox=dict(facecolor='white',edgecolor='none',alpha=.88,pad=1))
def dimension(ax,a,b,text,offset=160,color='.4'):
 a,b=np.array(a),np.array(b);dr=b-a;n=np.array([-dr[1],dr[0]])/np.linalg.norm(dr);aa=a+n*offset;bb=b+n*offset
 ax.plot([a[0],aa[0]],[a[1],aa[1]],c=color,lw=.55);ax.plot([b[0],bb[0]],[b[1],bb[1]],c=color,lw=.55)
 ax.annotate('',aa,xytext=bb,arrowprops=dict(arrowstyle='<->',color=color,lw=.8))
 mid=(aa+bb)/2;angle=math.degrees(math.atan2(dr[1],dr[0]));angle=angle+180 if angle>90 or angle< -90 else angle
 ax.text(*mid,text,ha='center',va='bottom',rotation=angle,rotation_mode='anchor',fontsize=8,c=color,
         bbox=dict(facecolor='white',edgecolor='none',alpha=.92,pad=1))
def save(fig,name):
 fig.savefig(R/(name+'.png'),dpi=180);fig.savefig(R/(name+'.svg'));plt.close(fig)
def setup(ax,title,lim):
 ax.set_aspect('equal');ax.set_xlim(lim[:2]);ax.set_ylim(lim[2:]);ax.grid(c='.9',ls='--',lw=.5)
 ax.set_title(title,loc='left',fontsize=11);ax.set_xlabel('X east [native units]');ax.set_ylabel('Y north [native units]')
def main():
 d=json.loads((I/'R04_PLAN_GEOMETRY.json').read_text());v=np.array(d['cells']['T2']['vertices']);T=Polygon(v)
 M=Polygon(d['cells']['M_A6']['vertices']);A=Polygon(d['cells']['I_A6']['vertices'])
 body=Polygon(d['program']['D2']['source_body']);neck=Polygon(d['program']['D2']['entry_neck'])
 raw3=np.array(d['program']['D3']['source_body']);aligned3=raw3.copy();aligned3[0]=v[2];aligned3[-1]=v[3]
 D3=Polygon(aligned3);rawD3=Polygon(raw3)
 boss=LineString([v[0],v[3]]).intersection(LineString([v[4],v[1]]));B=np.array(boss.coords[0])
 names=['I1','O1','O2','O3','I2'];roles=['existing inner receiver','existing outer receiver','existing extra outer receiver','existing outer receiver','existing inner receiver']
 inner=LineString([v[0],v[4]]);outer=LineString(v[1:4]);p,q=nearest_points(inner,outer)
 branches=[LineString([pt,B]) for pt in v]
 edges=[]
 owners=['T1 passage panel','D2 proposed entry neck','D3 window compartment','T3 passage panel','M_A6 middle ambulatory']
 for k,(name,owner) in enumerate(zip(names,owners)):
  a,b=v[k],v[(k+1)%5]
  edges.append({'edge':names[k]+'-'+names[(k+1)%5],'neighbor':owner,'length':float(np.linalg.norm(b-a)),'point_a':a.tolist(),'point_b':b.tolist(),'status':'CANDIDATE_NECK' if k==1 else ('DERIVED_D3_ENDPOINT_ALIGNMENT' if k==2 else 'UNCHANGED_R04_BOUNDARY')})
 pointrows=[{'point':n,'X':float(pt[0]),'Y':float(pt[1]),'role':role} for n,pt,role in zip(names,v,roles)]
 pointrows.append({'point':'B','X':float(B[0]),'Y':float(B[1]),'role':'plan diagonal intersection; no height or carved boss implied'})
 for name,rows in [('POINTS.csv',pointrows),('EDGES.csv',edges)]:
  with (R/name).open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 residual=np.linalg.norm(raw3[[0,-1]]-v[[2,3]],axis=1)
 metrics={'shared_middle_frontage':inner.length,'D2_passage_frontage':LineString(v[1:3]).length,'D3_passage_frontage':LineString(v[2:4]).length,'D2_body_entry_face':LineString([coords(body)[0],coords(body)[-1]]).length,'min_inner_to_outer_boundary_separation':inner.distance(outer),'separation_points':[list(p.coords[0]),list(q.coords[0])],'T2_plan_area':T.area,'D2_neck_area':neck.area,'D3_raw_to_candidate_endpoint_displacements':residual.tolist(),'D3_max_displacement':float(residual.max()),'boss_plan':B.tolist(),'clear_walking_width':None,'note':'Boundary separation is a plan set-out distance; wall/arch/profile thicknesses and physical SI calibration are not established.'}
 # One context view, preserving the exact source/candidate distinction.
 fig,ax=plt.subplots(figsize=(12,11))
 for poly,fill in [(A,'#f6f6f4'),(M,'#eef2f1'),(T,'#f0f2ef'),(body,'#f5ebdb'),(D3,'#e9f0f4')]:outline(ax,poly,fill=fill)
 outline(ax,neck,color='#b22828',ls='--',lw=1.2,fill='#fae8e8',alpha=.7)
 for br in branches:
  pp=np.array(br.coords);ax.plot(pp[:,0],pp[:,1],c='.5',ls='--',lw=.9)
 for k,(n,pt) in enumerate(zip(names,v)):
  ax.plot(*pt,'ko',ms=4);label(ax,pt,n,offset=[(-20,8),(-22,-15),(-4,-20),(9,3),(5,10)][k])
 ax.plot(*B,'ko',ms=3);label(ax,B,'B',(8,8),8)
 ax.plot(v[[0,4],0],v[[0,4],1],'k-',lw=2)
 ax.plot(v[[2,3],0],v[[2,3],1],color='#b22828',ls='--',lw=1.2)
 for poly,txt in [(A,'Inner A6\nprotected'),(M,'Middle A6\nprotected'),(body,'D2 chapel body\nsource working'),(D3,'D3 window bay\nsource working')]:
  pt=poly.representative_point();ax.text(pt.x,pt.y,txt,ha='center',va='center',fontsize=9)
 npnt=neck.representative_point();ax.text(npnt.x,npnt.y,'D2 entry neck\nR04 candidate',ha='center',fontsize=9,c='#a22')
 ax.text(24400,-3800,'T2\nfive-sided passage panel',ha='center',fontsize=10)
 dimension(ax,v[4],v[0],f'Middle / T2 shared edge {inner.length:.3f}',offset=-240)
 dimension(ax,v[1],v[2],f'D2 frontage {edges[1]["length"]:.3f}',offset=-150,color='#a22')
 dimension(ax,v[2],v[3],f'D3 frontage {edges[2]["length"]:.3f}',offset=-170,color='#a22')
 setup(ax,'T2 | middle ambulatory to D2 chapel and D3 window bay',(21300,29000,-9300,-1500))
 fig.suptitle('F5ZP | enlarged 2D junction plan',x=.08,ha='left',fontsize=16)
 fig.text(.08,.035,'Black: unchanged set-out / source working boundaries. Gray dashed: plan rib branches only.\nRed dashed: candidate D2 neck and D3 entry alignment. Node dots are datums, not new pier footprints. Native units; SI unset.',fontsize=8)
 fig.tight_layout(rect=[0,.07,1,.95]);save(fig,'T2_ENLARGED_PLAN')
 # Receiving-edge geometry is measured without inventing wall thickness or an opening width.
 fig,(ax,info)=plt.subplots(1,2,figsize=(14,8),gridspec_kw={'width_ratios':[1.3,1]})
 outline(ax,T,fill='#f1f3f1');outline(ax,M,color='.6',lw=.65)
 for br in branches:
  pp=np.array(br.coords);ax.plot(pp[:,0],pp[:,1],c='.55',ls='--',lw=.8)
 for name,pt in zip(names,v):ax.plot(*pt,'ko',ms=3);label(ax,pt,name)
 ax.plot(*B,'ko',ms=3);label(ax,B,'B',(-14,10))
 # This is the geometric shortest separation, not certified pedestrian clearance.
 ax.annotate('',p.coords[0],xytext=q.coords[0],arrowprops=dict(arrowstyle='<->',color='#a22',lw=1))
 mid=(np.array(p.coords[0])+np.array(q.coords[0]))/2
 ax.text(mid[0]+180,mid[1]-40,f'{inner.distance(outer):.3f}\nminimum plan separation',fontsize=8,c='#a22',ha='left',bbox=dict(facecolor='white',edgecolor='none',alpha=.9,pad=1))
 dimension(ax,v[0],v[1],f'{edges[0]["length"]:.3f}',offset=160)
 dimension(ax,v[3],v[4],f'{edges[3]["length"]:.3f}',offset=180)
 setup(ax,'Five receivers and five branches',(21900,27100,-6800,-2600));info.axis('off')
 info.text(0,.98,'MEASURED 2D INTERFACES',fontsize=12,weight='bold',va='top')
 notes=[f'Middle / T2: {inner.length:.3f}',f'T2 / D2 neck: {edges[1]["length"]:.3f}',f'T2 / D3 window: {edges[2]["length"]:.3f}',f'D2 body receiving edge: {metrics["D2_body_entry_face"]:.3f}',f'B = ({B[0]:.3f}, {B[1]:.3f})','I1 and I2: original middle-ring receivers.','O2: existing outer division; no inner pier added.',f'D3 source-vector endpoint residuals:\n{residual[0]:.9f} / {residual[1]:.9f} native units.','D3 candidate shares T2 endpoints exactly.\nRaw source polygon retained unchanged.','Clear walking width remains unmeasured;\nwall and profile thickness are not supplied.']
 for k,n in enumerate(notes):info.text(0,.89-k*.079,n,fontsize=9,va='top')
 fig.text(.065,.025,'Plan geometry only. No elevations, 3D geometry, vault generator changes or architectural promotion.',fontsize=9)
 fig.tight_layout(rect=[0,.06,1,1]);save(fig,'T2_INTERFACE_DETAIL')
 # Native coordinate SVG: this is a direct coordinate export rather than a sheet-fit graphic.
 root=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','viewBox':'21300 1500 7700 7800','width':'7700','height':'7800'})
 ET.SubElement(root,'metadata').text='Native X east/Y north; display Y inverted. 2D experimental study. SI coefficient null. R04 data immutable.'
 g=ET.SubElement(root,'g',{'transform':'scale(1,-1)','fill':'none','stroke-width':'8'})
 for n,poly,col,dash in [('inner_A6',A,'black',False),('middle_A6',M,'black',False),('T2',T,'black',False),('D2_body_source',body,'black',False),('D2_neck_candidate',neck,'#b22828',True),('D3_body_raw',rawD3,'gray',True),('D3_body_aligned_candidate',D3,'#b22828',True)]:
  at={'id':n,'points':' '.join(f'{x:.15g},{y:.15g}' for x,y in coords(poly)),'stroke':col}
  if dash:at['stroke-dasharray']='45 30'
  ET.SubElement(g,'polygon',at)
 for k,br in enumerate(branches):ET.SubElement(g,'polyline',{'id':'plan_branch_'+str(k+1),'points':' '.join(f'{x:.15g},{y:.15g}' for x,y in br.coords),'stroke':'gray','stroke-dasharray':'45 30'})
 ET.ElementTree(root).write(R/'T2_NATIVE_COORDINATES.svg',encoding='utf-8',xml_declaration=True)
 # Geometric checks: unchanged sources, direct shared edges and numerical containment.
 tests=[]
 def test(n,ok,value=None):tests.append({'name':n,'pass':bool(ok),'value':value})
 for n,poly in [('T2',T),('middle_A6',M),('D2_neck',neck),('D2_body',body),('D3_candidate',D3)]:test('Valid polygon '+n,poly.is_valid and poly.area>0)
 test('Five T2 receivers',len(v)==5)
 test('Exactly two inner receivers',len([n for n in names if n.startswith('I')])==2)
 test('Original M_A6 / T2 full shared edge',abs(M.boundary.intersection(T.boundary).length-inner.length)<1e-8)
 test('D2 neck full frontage',abs(neck.boundary.intersection(T.boundary).length-edges[1]['length'])<1e-7)
 test('D2 neck full body entry',abs(neck.boundary.intersection(body.boundary).length-metrics['D2_body_entry_face'])<1e-7)
 test('D3 aligned full frontage',abs(D3.boundary.intersection(T.boundary).length-edges[2]['length'])<1e-7)
 test('D3 correction within recovered-source uncertainty',residual.max()<.005,float(residual.max()))
 test('D3 other corners unchanged',np.array_equal(aligned3[1:-1],raw3[1:-1]))
 test('D2/T2 no positive-area overlap',neck.intersection(T).area<1e-6)
 test('D3/T2 no positive-area overlap',D3.intersection(T).area<1e-6)
 test('Plan branch intersection inside T2',T.contains(boss))
 for k,br in enumerate(branches):test('Branch inside T2 '+str(k+1),T.buffer(1e-8).covers(br))
 unavailable=[]
 for path,before in json.loads((I/'PARENT_HASHES.json').read_text()).items():
  pth=Path(path)
  if pth.exists():test('Parent unchanged '+pth.name,hashlib.sha256(pth.read_bytes()).hexdigest()==before)
  else:
   unavailable.append(path);snapshot=I/('R04_'+pth.name)
   if snapshot.exists():test('Parent snapshot hash '+pth.name,hashlib.sha256(snapshot.read_bytes()).hexdigest()==before)
 for pth in R.glob('*.svg'):ET.parse(pth);test('SVG parses '+pth.name,True)
 out={'status':'EXPERIMENTAL_2D_ONLY','checks':tests,'passed':sum(t['pass'] for t in tests),'failed':sum(not t['pass'] for t in tests),'metrics':metrics,'parent_paths_unavailable_on_this_host':unavailable,'approved_geometry_changed':False,'new_inner_piers':0,'3D_geometry_generated':False,'structural_validation':False,'physical_m_per_unit':None,'D2_neck':'R04 experimental candidate, not approved','D3_delta':'Two candidate entry corners aligned to unchanged T2: source-vector recovery correction below 0.005. Parent source unchanged.'}
 put('T2_QA.json',out)
 put('T2_GEOMETRY.json',{'T2':v.tolist(),'M_A6':coords(M).tolist(),'I_A6':coords(A).tolist(),'D2_body':coords(body).tolist(),'D2_neck_candidate':coords(neck).tolist(),'D3_source':raw3.tolist(),'D3_aligned_candidate':aligned3.tolist(),'B':B.tolist(),'plan_branches':[list(br.coords) for br in branches],'metrics':metrics})
 assert all(t['pass'] for t in tests),[t for t in tests if not t['pass']]
 print('T2_2D_COMPLETE',out['passed'],'checks')
if __name__=='__main__':main()
