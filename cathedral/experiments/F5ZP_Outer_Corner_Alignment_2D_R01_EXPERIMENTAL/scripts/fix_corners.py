"""Isolated 2D corner correction; no entrance/receiver/window placement study."""
from pathlib import Path
import json,copy,hashlib,math
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype']='none'
R=Path(__file__).resolve().parents[1];I=R/'inputs'
def put(n,x):(R/n).write_text(json.dumps(x,indent=2)+'\n')
def polygon(ax,v,color,ls='-',fill=False):
 v=np.array(v);v=np.vstack([v,v[0]])
 if fill:ax.fill(v[:,0],v[:,1],color=color,alpha=.06)
 ax.plot(v[:,0],v[:,1],color=color,ls=ls,lw=.9)
def main():
 p=json.loads((I/'PLAN_GEOMETRY.json').read_text());low=json.loads((I/'LOW14_GEOMETRY.json').read_text());c=copy.deepcopy(p);l=copy.deepcopy(low);rows=[];checks=[]
 def check(n,ok,value=None):checks.append(dict(name=n,pass_=bool(ok),value=value))
 for sector,node,chap,win in [('T2',2,'D2','D3'),('T6',7,'D8','D7')]:
  pair=next(x for x in l['pairs'] if x['sector']==sector);v=np.array(c['cells'][sector]['vertices']);mid=np.array(pair['inner_midpoint']);old=np.array(pair['outer_receiver']);u=(v[-1]-v[0]);u/=np.linalg.norm(u);n=np.array([u[1],-u[0]])
  if (old-mid)@n<0:n=-n
  # Ray / fixed ellipse intersection: center (20213,0), axes (7169,6657).
  q=(mid-np.array([20213.,0]))/np.array([7169.,6657.]);nn=n/np.array([7169.,6657.]);roots=np.roots([nn@nn,2*q@nn,q@q-1]);dist=max(float(x.real) for x in roots if abs(x.imag)<1e-9 and x.real>0);new=mid+n*dist
  # Replace every matching plan endpoint in this independent candidate only.
  def replace(obj):
   if isinstance(obj,list):
    if len(obj)==2 and all(isinstance(x,(int,float)) for x in obj) and np.linalg.norm(np.array(obj)-old)<.005:return new.tolist()
    return [replace(x) for x in obj]
   if isinstance(obj,dict):return {k:replace(x) for k,x in obj.items()}
   return obj
  c=replace(c);l=replace(l)
  # Respect fixed chapel-body entry corners. D3/D7 side runs through that fixed
  # junction before following the unchanged distal compartment edge.
  body=np.array(p['program'][chap]['source_body']);oldwin=np.array(p['program'][win]['source_body']);near=min(body,key=lambda x:LineString([oldwin[0],oldwin[1]] if win=='D3' else [oldwin[-1],oldwin[-2]]).distance(__import__('shapely').geometry.Point(x)))
  w=c['program'][win]['source_body']
  for j,pt in enumerate(w):
   for nodept in c['outer_passage_nodes']:
    if np.linalg.norm(np.array(pt)-nodept)<.005:w[j]=list(nodept);break
  if win=='D3':w.insert(1,near.tolist())
  else:w.insert(len(w)-1,near.tolist())
  cv=np.array(c['cells'][sector]['vertices']);neck=c['program'][chap]['entry_neck'];window=c['program'][win]['source_body'];parts=[Polygon(cv),Polygon(neck),Polygon(window)]
  front=LineString([v[0],v[-1]])
  metric=dict(sector=sector,old_corner=old.tolist(),new_corner=new.tolist(),old_lateral_offset=float((old-mid)@u),new_lateral_offset=float((new-mid)@u),movement=float(np.linalg.norm(new-old)),new_normal_depth=dist,new_ellipse_parameter_deg=float(math.degrees(math.atan2((new[0]-20213)/7169,-new[1]/6657))),fixed_chapel_junction=near.tolist(),source_input_hashes={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in I.glob('*.json')})
  rows.append(metric)
  check(sector+' offset removed',abs(metric['new_lateral_offset'])<1e-8,metric['new_lateral_offset'])
  check(sector+' ellipse preserved',abs(np.sum(((new-[20213,0])/[7169,6657])**2)-1)<1e-12)
  check(sector+' candidate polygons valid',all(x.is_valid and x.area>0 for x in parts))
  check(sector+' middle frontage unchanged',np.array_equal(v[[0,-1]],cv[[0,-1]]))
  check(sector+' chapel body unchanged',c['program'][chap]['source_body']==p['program'][chap]['source_body'])
  for a,b,label in [(0,1,'passage/chapel neck'),(0,2,'passage/window compartment'),(1,2,'chapel neck/window compartment')]:
   overlap=parts[a].intersection(parts[b]).area
   check(sector+' no overlap '+label,overlap<1e-5,float(overlap))
  for a,b,label in [(0,1,'chapel frontage'),(0,2,'window frontage'),(1,2,'side junction')]:
   contact=parts[a].boundary.intersection(parts[b].boundary.buffer(1e-6)).length
   check(sector+' continuous '+label,contact>100,float(contact))
  fig,(ax,detail)=plt.subplots(1,2,figsize=(14,8),gridspec_kw={'width_ratios':[1.5,1]})
  for axis in [ax,detail]:
   for k in [pair['middle_bay']]:polygon(axis,p['cells'][k]['vertices'],'k',fill=True)
   polygon(axis,v,'.6','--');polygon(axis,p['program'][chap]['entry_neck'],'.6','--');polygon(axis,oldwin,'.6','--')
   for z in [cv,neck,window]:polygon(axis,z,'#b32b25','--',fill=True)
   polygon(axis,body,'k',fill=True)
   axis.plot([mid[0],new[0]],[mid[1],new[1]],c='.45',ls='--',lw=.8)
   axis.scatter([old[0]],[old[1]],c='.5',s=18);axis.scatter([new[0]],[new[1]],c='#b32b25',s=24)
   axis.annotate('',new,old,arrowprops=dict(arrowstyle='->',color='#b32b25',lw=1.4))
   axis.set_aspect('equal');axis.grid(c='.9',ls='--',lw=.4);axis.set(xlabel='Project X east [native units]',ylabel='Project Y north [native units]')
  ax.text(*Polygon(cv).representative_point().coords[0],sector+' corrected',ha='center',fontsize=10)
  ax.text(*Polygon(body).representative_point().coords[0],chap+' body unchanged',ha='center',fontsize=9)
  ax.text(*Polygon(window).representative_point().coords[0],win+' boundary candidate',ha='center',fontsize=9)
  ax.set_title('Adjoining plan | original gray, correction red',loc='left',fontsize=11)
  detail.set(xlim=(min(old[0],new[0])-330,max(old[0],new[0])+330),ylim=(min(old[1],new[1])-330,max(old[1],new[1])+330));detail.set_title('Corner displacement detail',loc='left',fontsize=11)
  detail.annotate('OLD',old,(old[0]+75,old[1]+120),fontsize=9,color='.4');detail.annotate('CORRECTED',new,(new[0]-270,new[1]-180),fontsize=9,color='#b32b25')
  fig.suptitle(f'F5ZP {sector} | outer corner aligned to bay normal — 2D EXPERIMENT',fontsize=15,x=.055,ha='left')
  fig.text(.055,.045,f'Lateral offset {metric["old_lateral_offset"]:+.3f} → {metric["new_lateral_offset"]:.3f} · total movement {metric["movement"]:.3f} native units\nEllipse unchanged. Chapel body and middle ambulatory unchanged. Red boundary remains experimental. No opening, receiver or upper-window positions developed.',fontsize=9)
  fig.tight_layout(rect=[0,.11,1,.95])
  for ext in ['png','svg']:fig.savefig(R/f'{sector}_CORNER_CORRECTION.{ext}',dpi=180)
  plt.close(fig)
 check('All inner/middle source cells preserved',all(c['cells'][k]==p['cells'][k] for k in p['cells'] if k.startswith(('I_','M_'))))
 check('Unaffected passage sectors preserved',all(c['cells'][k]==p['cells'][k] for k in p['cells'] if k.startswith('T') and k not in ['T2','T6']))
 check('Fourteen low footprints retained',len(l['vaults'])==14)
 check('Mirrored corrected corner X',abs(rows[0]['new_corner'][0]-rows[1]['new_corner'][0])<1e-8)
 check('Mirrored corrected corner Y',abs(rows[0]['new_corner'][1]+rows[1]['new_corner'][1])<1e-8)
 c['outer_ellipse_parameters_deg_south_to_north'][2]=rows[0]['new_ellipse_parameter_deg'];c['outer_ellipse_parameters_deg_south_to_north'][7]=rows[1]['new_ellipse_parameter_deg']
 for key in ['D2','D3','D7','D8']:c['program'][key]['status']='EXPERIMENTAL_CORNER_CORRECTION; source bodies retained separately in inputs'
 for key in ['T2','T6']:c['cells'][key]['status']='EXPERIMENTAL_CORNER_CORRECTION'
 put('CORRECTED_PLAN_CANDIDATE.json',c);put('CORRECTED_LOW14_FOOTPRINTS_CANDIDATE.json',l)
 put('QA_AND_MOVEMENTS.json',dict(status='EXPERIMENTAL_2D_ONLY',measurements=rows,checks=checks,passed=sum(x['pass_'] for x in checks),failed=sum(not x['pass_'] for x in checks),physical_m_per_native_unit=None,missing_F5ZL_C_support_schedule='UNRESOLVED'))
 assert all(x['pass_'] for x in checks),[x for x in checks if not x['pass_']]
 print(json.dumps(rows,indent=2));print('PASS',len(checks))
if __name__=='__main__':main()
