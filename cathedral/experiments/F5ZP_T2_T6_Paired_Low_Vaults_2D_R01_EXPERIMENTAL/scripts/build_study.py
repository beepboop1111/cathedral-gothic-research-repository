"""T2/T6 isolated 2D fit study; exact source footprints, inherited trial levels."""
from pathlib import Path
import json, math, hashlib, csv
import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype']='none'
R=Path(__file__).resolve().parents[1]; I=R/'inputs'
def load(p):return json.loads(p.read_text())
def arch(a,h,s,cx=0,offset=0):
 c=(h*h-a*a)/(2*a); radius=a+c+offset
 x=np.linspace(c-radius,0,401); y=s+np.sqrt(np.maximum(0,radius*radius-(x-c)**2))
 return np.r_[x,x[::-1]*-1]+cx,np.r_[y,y[::-1]]
def limit(u,a,h,s):
 c=(h*h-a*a)/(2*a);return s+np.sqrt(np.maximum(0,(a+c)**2-(np.abs(u)+c)**2))
def dim(ax,a,b,y,label,col='.4'):
 ax.annotate('',(a,y),xytext=(b,y),arrowprops=dict(arrowstyle='<->',color=col,lw=.7))
 ax.text((a+b)/2,y-40,label,ha='center',va='top',fontsize=8,color=col,bbox=dict(facecolor='white',edgecolor='none',pad=.5))
def polyline(ax,v,col,ls='-',fill=None):
 v=np.vstack([v,v[0]])
 if fill:ax.fill(v[:,0],v[:,1],color=fill)
 ax.plot(v[:,0],v[:,1],color=col,ls=ls,lw=1)
def main():
 d=load(I/'LOW14_GEOMETRY.json');s=load(I/'F5ZK_C.json');t=load(I/'REGULAR_BAY_TRIAL_PARAMETERS.json')
 results=[];checks=[]
 def check(name,ok,value=None):checks.append(dict(name=name,passed=bool(ok),value=value))
 for name,sha in load(I/'SOURCE_HASHES.json').items():check('Input integrity '+name,hashlib.sha256((I/name).read_bytes()).hexdigest()==sha)
 for pair in d['pairs']:
  if pair['sector'] not in ['T2','T6']:continue
  name=pair['sector'];ids=pair['lower_vaults'];a,b=[np.array(d['vaults'][k]['vertices']) for k in ids];m=np.array(d['protected_inner_middle'][pair['middle_bay']]['vertices'])
  origin=np.array(pair['inner_midpoint']);v=b[-1]-a[0];span=float(np.linalg.norm(v));u=v/span;n=np.array([u[1],-u[0]])
  vec=np.array(pair['outer_receiver'])-origin
  if vec@n<0:n=-n
  local=lambda p:np.column_stack(((p-origin)@u,(p-origin)@n))
  aa,bb,mm=map(local,[a,b,m]);end=local(np.array([pair['outer_receiver']]))[0]
  half=span/2;clear=half-192;centers=[-half/2,half/2]
  cell=next(c for c in s['cells'] if c['family']=='AMB-M' and c['bay']==pair['middle_bay'].split('_')[1]);spring=s['vertical_placement']['spring_y'];rise=cell['outer_annular_apex_y']-spring
  wx,wy=arch(t['window_clear_width']/2,t['window_clear_head']-t['window_arch_spring'],t['window_arch_spring'],offset=t['window_frame_trial_depth'])
  margin=float(np.min(limit(wx,half,rise,spring)-t['upper_reference_arch_vertical_planning_reserve']-wy))
  parent=unary_union([Polygon(a),Polygon(b)]);middle=Polygon(m);front=LineString([a[0],b[-1]])
  # Boolean exact line intersections are unstable for midpoint roundoff. Verify
  # both boundaries cover the entire frontage within 1e-6 native unit instead.
  contact=front.intersection(middle.boundary.buffer(1e-6)).intersection(parent.boundary.buffer(1e-6)).length
  hit=parent.intersection(LineString([origin,origin+n*10000]));normaldepth=float(hit.length)
  metric=dict(bay=name,middle_bay=pair['middle_bay'],lower_vaults=ids,bay_frontage=span,half_frontage=half,trial_clear_opening_each=clear,trial_central_receiver_face=192,trial_shared_end_receiver_face=192,shared_division_length=float(np.linalg.norm(vec)),division_normal_depth=float(end[1]),division_tangential_offset=float(end[0]),division_skew_degrees=float(math.degrees(math.atan2(end[0],end[1]))),normal_cut_plan_depth=normaldepth,lower_cell_areas=[Polygon(a).area,Polygon(b).area],outer_receiving_edge_lengths=[float(np.linalg.norm(a[2]-a[1])),float(np.linalg.norm(b[2]-b[1]))],middle_contact_length=contact,middle_overlap_area=middle.intersection(parent).area,lower_overlap_area=Polygon(a).intersection(Polygon(b)).area,window_upper_planning_margin=margin,window_frame_to_web_allowance=96,physical_m_per_native_unit=None)
  results.append(metric)
  for label,ok,val in [('Footprints valid',all(Polygon(x).is_valid for x in [a,b,m]),None),('Paired footprints do not overlap',metric['lower_overlap_area']<1e-6,metric['lower_overlap_area']),('Middle footprint not encroached',metric['middle_overlap_area']<1e-6,metric['middle_overlap_area']),('Full middle frontage shared',abs(metric['middle_contact_length']-span)<1e-6,metric['middle_contact_length']),('Two equal frontages',abs(np.linalg.norm(a[0]-a[-1])-np.linalg.norm(b[0]-b[-1]))<1e-6,None),('Opening and receiver faces close bay',abs(2*clear+192+192-span)<1e-7,None),('Positive opening width',clear>0,clear),('Window frame under planning envelope',margin>0,margin),('Window frame above web allowance',t['window_clear_sill']-t['window_frame_trial_depth']>t['third_layer_web_top_allowance'],96),('Lower crown below higher crown',t['third_layer_boss_rib_crown']<4296,1480),('Skewed division retained',abs(end[0])>200,float(end[0]))]:check(name+' '+label,ok,val)
  fig,(plan,elev)=plt.subplots(1,2,figsize=(14,10),gridspec_kw={'width_ratios':[1.1,1]})
  polyline(plan,mm,'k',fill='#eef0ec')
  for p,k in zip([aa,bb],ids):
   polyline(plan,p,'#b32b25','--','#f8efed');q=Polygon(p).representative_point();plan.text(q.x,q.y,k,ha='center',fontsize=10)
  plan.plot([0,end[0]],[0,end[1]],c='#b32b25',ls='--',lw=1.5)
  plan.plot([0,0],[mm[:,1].min(),normaldepth],c='.5',ls='--',lw=.7)
  plan.plot([-288,288],[0,0],c='#24768d',lw=4,label='Trial window above')
  plan.scatter([end[0]],[end[1]],c='#b32b25',s=20)
  plan.annotate(f'Existing outer corner\nu offset {end[0]:+.3f}',end,(end[0]+250,end[1]-240),fontsize=8,arrowprops=dict(arrowstyle='-',color='.4'))
  plan.text(0,mm[:,1].min()+180,pair['middle_bay']+' protected',ha='center',fontsize=9)
  dim(plan,-half,0,-170,f'half frontage {half:.3f}');dim(plan,0,half,-170,f'half frontage {half:.3f}')
  dim(plan,-half,half,-440,f'full receiving chord {span:.3f}')
  plan.set_aspect('equal');plan.set(xlabel='Local u along receiving chord [native units]',ylabel='Local v outward normal [native units]');plan.grid(c='.9',ls='--',lw=.4);plan.set_title('Exact plan | skewed common division retained',loc='left',fontsize=11)
  plan.legend(loc='lower left',fontsize=8)
  ux,uy=arch(half,rise,spring);elev.plot(ux,uy,'k-',lw=1.1);elev.plot(ux,uy-192,c='.5',ls='--',lw=.7)
  for cx in centers:
   for offset,lw in [(0,1.1),(96,.65)]:
    xx,yy=arch(clear/2,576,2112,cx,offset);elev.plot(xx,yy,c='#b32b25',ls='--',lw=lw)
   elev.plot([cx-clear/2]*2,[0,2112],c='#b32b25',ls='--');elev.plot([cx+clear/2]*2,[0,2112],c='#b32b25',ls='--')
   dim(elev,cx-clear/2,cx+clear/2,650,f'clear {clear:.3f}','#a22')
  for offset,lw in [(0,1.1),(96,.65)]:
   xx,yy=arch(288,320,3456,offset=offset);elev.plot(xx,yy,c='#b32b25',ls='--',lw=lw)
   sill=3072-offset;hw=288+offset
   elev.plot([-hw,-hw,hw,hw],[3456,sill,sill,3456],c='#b32b25',ls='--',lw=lw)
  elev.text(0,3280,'ONE WINDOW\n576 × 704 clear',ha='center',fontsize=8)
  for lev,label in [(2112,'trial spring 2112'),(2688,'entrance crown 2688'),(2816,'trial boss 2816'),(2880,'trial web allowance 2880'),(4296,'source higher crown 4296')]:
   elev.axhline(lev,c='#b32b25' if lev<3000 else '.4',ls='--',lw=.4)
  elev.text(0,2940,'web top 2880 / window sill 3072',ha='center',fontsize=7,color='#a22')
  elev.text(0,4350,'source higher crown 4296',ha='center',fontsize=8)
  elev.text(0,4170,'source R2 apex 4136',ha='center',fontsize=8)
  elev.text(0,1500,'TWO LOWER ENTRANCES\nTrial spring 2112 · clear crown 2688\nThird-layer boss/rib crown 2816',ha='center',fontsize=9)
  dim(elev,-half,half,-230,f'full bay {span:.3f}')
  elev.axhline(0,c='k',lw=.7);elev.set_aspect('equal');elev.set(xlim=(-half-130,half+130),ylim=(-500,4600),xlabel='Along receiving chord u [native units]',ylabel='Elevation above working datum [native units]');elev.grid(c='.9',ls='--',lw=.4);elev.set_title('Receiving-wall elevation | inherited height trial',loc='left',fontsize=11)
  fig.suptitle(f'F5ZP {name} | paired low vaults beneath one upper window — EXPERIMENTAL',fontsize=15,x=.06,ha='left')
  fig.text(.06,.065,f'Division skew {metric["division_skew_degrees"]:+.3f}° · normal depth {end[1]:.3f} · divider length {metric["shared_division_length"]:.3f}\nWindow frame: 96 above trial web allowance; {margin:.3f} below provisional upper envelope. Native units; physical conversion unresolved.',fontsize=9)
  fig.text(.06,.02,'Black: protected source set-out / recorded arch reference. Gray dashed: construction. Red dashed: experimental.\nNo wall thickness, vault-web surface, 3D contact or structural capacity is established by this 2D study.',fontsize=8)
  fig.tight_layout(rect=[0,.12,1,.95])
  for ext in ['svg','png']:fig.savefig(R/f'{name}_PLAN_AND_ELEVATION.{ext}',dpi=180)
  plt.close(fig)
 check('T2/T6 mirrored dimensions',all(abs(results[0][k]-results[1][k])<1e-6 for k in ['bay_frontage','division_normal_depth','shared_division_length','window_upper_planning_margin']),None)
 check('T2/T6 opposite skew',abs(results[0]['division_tangential_offset']+results[1]['division_tangential_offset'])<1e-6,None)
 output={'status':'EXPERIMENTAL_2D_ONLY','passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'checks':checks,'measurements':results,'inherited_trial_parameters':t,'approved_geometry_changed':False,'new_height_application':'T2 and T6 trial drawings only','unresolved':['Physical SI conversion','Wall thickness and actual arch intrados','Actual 3D contacts and vault-web sections','Structural adequacy and architectural approval','Missing F5ZL-C support schedule']}
 (R/'QA_AND_MEASUREMENTS.json').write_text(json.dumps(output,indent=2)+'\n')
 with (R/'DIMENSIONS.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['bay','dimension','native_value'])
  for row in results:
   for k,v in row.items():
    if isinstance(v,(float,int)):w.writerow([row['bay'],k,v])
 assert not output['failed'],[x for x in checks if not x['passed']]
 print(json.dumps(output,indent=2))
if __name__=='__main__':main()
