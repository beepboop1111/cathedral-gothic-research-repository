"""Dimensioned 2D receiving-wall elevation and radial height-coordination section; no 3D."""
from pathlib import Path
import json,csv,hashlib,math,xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import Polygon,LineString
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype']='none'
from matplotlib.patches import Polygon as Patch,Rectangle

R=Path(__file__).resolve().parents[1];I=R/'inputs'
def put(n,d):(R/n).write_text(json.dumps(d,indent=2)+'\n')
def arch(a,h,spring,cx=0,normal_offset=0):
 c=(h*h-a*a)/(2*a);rad=a+c+normal_offset
 xleft=np.linspace(c-rad,0,250);y=spring+np.sqrt(np.maximum(rad*rad-(xleft-c)**2,0))
 return np.r_[cx+xleft,cx-xleft[::-1]],np.r_[y,y[::-1]],{'center_offset':c,'circle_radius':rad,'spring':spring,'crown':float(y[-1])}
def reference_y(u,a,h,spring):
 c=(h*h-a*a)/(2*a);rad=a+c
 return spring+np.sqrt(np.maximum(rad*rad-(np.abs(u)+c)**2,0))
def dimh(ax,x0,x1,y,text,color='.35',fs=8):
 ax.annotate('',(x0,y),xytext=(x1,y),arrowprops=dict(arrowstyle='<->',lw=.7,color=color));ax.text((x0+x1)/2,y-38,text,ha='center',va='top',fontsize=fs,c=color,bbox=dict(facecolor='white',edgecolor='none',alpha=.92,pad=.5))
def dimv(ax,x,y0,y1,text,color='.35',fs=8):
 ax.annotate('',(x,y0),xytext=(x,y1),arrowprops=dict(arrowstyle='<->',lw=.7,color=color));ax.text(x+24,(y0+y1)/2,text,rotation=90,ha='left',va='center',fontsize=fs,c=color,bbox=dict(facecolor='white',edgecolor='none',alpha=.92,pad=.5))
def save(fig,name):fig.savefig(R/(name+'.png'),dpi=180);fig.savefig(R/(name+'.svg'));plt.close(fig)
def outline(ax,pts,color='k',ls='-',fill=None,lw=.8):
 p=np.array(pts)
 if fill:ax.add_patch(Patch(p,facecolor=fill,edgecolor='none'))
 ax.plot(p[:,0],p[:,1],c=color,ls=ls,lw=lw)
def main():
 t=json.loads((R/'TRIAL_PARAMETERS.json').read_text());d=json.loads((I/'LOW14_GEOMETRY.json').read_text());src=json.loads((I/'F5ZK_C.json').read_text())
 pair=next(x for x in d['pairs'] if x['sector']=='T4');left=np.array(d['vaults']['L3-07']['vertices']);right=np.array(d['vaults']['L3-08']['vertices']);M=np.array(d['protected_inner_middle']['M_A4']['vertices'])
 half=float(np.linalg.norm(left[0]-left[-1]));bay=2*half
 clear=half-t['end_receiver_full_trial_width']/2-t['central_receiver_trial_width']/2
 centers=[-half/2,half/2];opening_half=clear/2
 upper=next(c for c in src['cells'] if c['family']=='AMB-M' and c['bay']=='A4')
 upper_spring=src['vertical_placement']['spring_y'];upper_apex=upper['outer_annular_apex_y'];upper_rise=upper_apex-upper_spring
 recorded=src['vertical_placement'];lower_rise=t['lower_opening_intrados_crown']-t['lower_opening_spring'];window_rise=t['window_clear_head']-t['window_arch_spring']
 op=[]
 for cx in centers:
  x,y,par=arch(opening_half,lower_rise,t['lower_opening_spring'],cx)
  ox,oy,opar=arch(opening_half,lower_rise,t['lower_opening_spring'],cx,t['lower_arch_ring_trial_normal_depth'])
  op.append({'x':x,'y':y,'outer_x':ox,'outer_y':oy,'parameters':par,'outer_parameters':opar,'center':cx})
 wx,wy,wpar=arch(t['window_clear_width']/2,window_rise,t['window_arch_spring'])
 wox,woy,wopar=arch(t['window_clear_width']/2,window_rise,t['window_arch_spring'],normal_offset=t['window_frame_trial_depth'])
 window_outer_bottom=t['window_clear_sill']-t['window_frame_trial_depth']
 reserve=t['upper_reference_arch_vertical_planning_reserve']
 window_clearance=reference_y(wox,half,upper_rise,upper_spring)-reserve-woy
 depth_middle=float(pair['inner_midpoint'][0]-M[:,0].min());depth_low=float(pair['outer_receiver'][0]-pair['inner_midpoint'][0])
 metrics={'source_bay':'M_A4 / T4','vaults':['L3-07','L3-08'],'bay_axis_to_axis':bay,'each_half_bay':half,'each_trial_clear_opening':clear,'central_trial_receiver':t['central_receiver_trial_width'],'end_receiver_inside_each_bay':t['end_receiver_full_trial_width']/2,'window_clear_width':t['window_clear_width'],'window_clear_height':t['window_clear_head']-t['window_clear_sill'],'lower_opening_outer_crown':max(o['outer_parameters']['crown'] for o in op),'window_frame_outer_head':wopar['crown'],'window_frame_bottom':window_outer_bottom,'web_top_to_frame_bottom':window_outer_bottom-t['third_layer_web_top_allowance'],'min_window_frame_to_upper_planning_limit':float(window_clearance.min()),'third_to_middle_boss_drop':recorded['boss_rib_crown_y']-t['third_layer_boss_rib_crown'],'middle_chordal_plan_depth':depth_middle,'third_layer_plan_depth':depth_low,'absolute_section_X':pair['inner_midpoint'][0],'radial_section_Y':0,'window_offset_along_wall':0,'physical_m_per_native_unit':None}
 rows=[['Ground',0,'REFERENCE'],['Lower entrance spring',t['lower_opening_spring'],'TRIAL'],['Lower entrance clear crown',t['lower_opening_intrados_crown'],'TRIAL'],['Third-layer rib/boss crown',t['third_layer_boss_rib_crown'],'TRIAL'],['Third-layer web top allowance',t['third_layer_web_top_allowance'],'TRIAL'],['Window frame bottom',window_outer_bottom,'DERIVED TRIAL'],['Existing inner/middle spring',upper_spring,'SOURCE'],['Window clear sill',t['window_clear_sill'],'TRIAL'],['Window arch spring',t['window_arch_spring'],'TRIAL'],['Window clear head',t['window_clear_head'],'TRIAL'],['Window frame outer head',wopar['crown'],'DERIVED TRIAL'],['R2 center planning limit',upper_apex-reserve,'PLANNING ONLY'],['R2 reference arch apex',upper_apex,'SOURCE'],['Inner/middle rib/boss crown',recorded['boss_rib_crown_y'],'SOURCE'],['Gallery soffit',recorded['gallery_soffit_y'],'SOURCE'],['Gallery floor',recorded['gallery_floor_y'],'SOURCE']]
 with (R/'LEVEL_SCHEDULE.csv').open('w') as f:w=csv.writer(f);w.writerow(['datum','native_elevation','authority']);w.writerows(rows)
 # A-A developed receiving-wall sectional elevation, dimensioned in native units.
 fig,(ax,tab)=plt.subplots(1,2,figsize=(14,12),gridspec_kw={'width_ratios':[1.15,1]})
 ax.add_patch(Rectangle((-half,0),bay,recorded['gallery_floor_y'],facecolor='#f4f2ed',edgecolor='none'))
 ux,uy,upar=arch(half,upper_rise,upper_spring);ax.plot(ux,uy,'k-',lw=1.1)
 ax.plot(ux,uy-reserve,c='.55',ls='--',lw=.8)
 for o in op:
  cx=o['center'];body=np.array([[cx-opening_half,0],[cx-opening_half,t['lower_opening_spring']],*zip(o['x'],o['y']),[cx+opening_half,0]])
  outline(ax,body,color='#b32b25',ls='--',fill='white',lw=1)
  ax.plot(o['outer_x'],o['outer_y'],c='#b32b25',ls='--',lw=.7)
  ax.text(cx,1400,'LOW VAULT\nENTRANCE',ha='center',va='center',fontsize=9)
  dimh(ax,cx-opening_half,cx+opening_half,650,f'clear {clear:.3f}',color='#a22')
 window=np.array([[-t['window_clear_width']/2,t['window_clear_sill']],[-t['window_clear_width']/2,t['window_arch_spring']],*zip(wx,wy),[t['window_clear_width']/2,t['window_clear_sill']]])
 outline(ax,window,color='#b32b25',ls='--',fill='#e6f0f3',lw=1)
 ax.plot(wox,woy,c='#b32b25',ls='--',lw=.7)
 ax.plot([-384,-384],[window_outer_bottom,t['window_arch_spring']],c='#b32b25',ls='--',lw=.7);ax.plot([384,384],[window_outer_bottom,t['window_arch_spring']],c='#b32b25',ls='--',lw=.7);ax.plot([-384,384],[window_outer_bottom]*2,c='#b32b25',ls='--',lw=.7)
 ax.text(0,3295,'ONE\nWINDOW',ha='center',fontsize=9)
 dimh(ax,-288,288,3135,'576 clear',color='#a22',fs=7)
 dimv(ax,450,t['window_clear_sill'],t['window_clear_head'],'704 clear',color='#a22',fs=7)
 for lev,col,ls in [(upper_spring,'.3','--'),(upper_apex,'.3','--'),(recorded['boss_rib_crown_y'],'k','--'),(t['third_layer_boss_rib_crown'],'#b32b25','--'),(t['third_layer_web_top_allowance'],'#b32b25',':')]:
  ax.plot([-half-60,half+60],[lev,lev],c=col,ls=ls,lw=.5)
 ax.text(0,recorded['boss_rib_crown_y']+65,'recorded higher crown 4296',ha='center',fontsize=8)
 ax.text(0,upper_apex+50,'R2 reference apex 4136',ha='center',fontsize=8)
 ax.text(0,t['third_layer_boss_rib_crown']+60,'trial lower crown 2816 / web allowance 2880',ha='center',fontsize=7,c='#a22')
 dimv(ax,-half-250,0,t['lower_opening_spring'],'2112 trial spring',color='#a22')
 dimv(ax,half+210,0,t['third_layer_boss_rib_crown'],'2816 trial crown',color='#a22')
 dimv(ax,half+480,t['third_layer_boss_rib_crown'],recorded['boss_rib_crown_y'],'1480 below higher crown',color='#a22')
 dimh(ax,-half,0,-180,f'half bay {half:.3f}');dimh(ax,0,half,-180,f'half bay {half:.3f}')
 dimh(ax,-half,half,-390,f'full axis-to-axis bay {bay:.3f}')
 dimh(ax,-96,96,180,'192 trial central receiver',color='#a22',fs=7)
 ax.axhline(0,c='k',lw=.8);ax.axvline(0,c='.65',ls='--',lw=.5)
 ax.set(xlim=(-half-650,half+650),ylim=(-600,4750),xlabel='Along receiving-wall chord u [native units]',ylabel='Absolute elevation [native units]');ax.set_aspect('equal');ax.grid(c='.9',ls='--',lw=.4)
 ax.set_title('A-A | developed bay sectional elevation',loc='left',fontsize=11)
 tab.axis('off');tab.set_title('LEVEL AND FIT SCHEDULE',loc='left',fontsize=11)
 ct=[[label,f'{val:.3f}' if val!=int(val) else str(int(val)),status] for label,val,status in rows]
 table=tab.table(cellText=ct,colLabels=['Datum','Elevation','Status'],colWidths=[.61,.17,.22],cellLoc='left',bbox=[0,.31,1,.65]);table.auto_set_font_size(False);table.set_fontsize(8)
 for (rr,cc),cell in table.get_celld().items():
  cell.set_edgecolor('.8');cell.set_linewidth(.35)
  if rr==0:cell.set_facecolor('#e8ecec')
  elif 'TRIAL' in ct[rr-1][2]:cell.get_text().set_color('#a22')
 notes=[f'Window frame to web allowance: {metrics["web_top_to_frame_bottom"]:.3f}',f'Minimum upper planning margin: {metrics["min_window_frame_to_upper_planning_limit"]:.3f}',f'Two equal lower clear openings: {clear:.3f} each','192 end receivers are shared at bay axes;\n96 of each lies within this bay.','Black = recorded reference. Red dashed = trial.','The 192 upper reserve is a planning deduction,\nnot a measured existing intrados.','One-bay trial only. No height propagation\nto the other third-layer vaults.']
 for k,n in enumerate(notes):tab.text(0,.265-k*.033,n,fontsize=8,va='top')
 fig.suptitle('F5ZP | regular T4 / M_A4 bay — dimensioned 2D study',x=.055,ha='left',fontsize=15)
 fig.text(.055,.012,'Native project units; SI coefficient unresolved. All new low-vault, jamb and window dimensions are EXPERIMENTAL. No approved geometry or generator changed.',fontsize=8)
 fig.tight_layout(rect=[0,.065,1,.96]);save(fig,'DIMENSIONED_BAY_SECTION_AA')
 # B-B at the bay center crosses the common low receiving line; adjoining vault levels are projected.
 fig,(ax,plan)=plt.subplots(1,2,figsize=(14,8),gridspec_kw={'width_ratios':[1.6,1]})
 ax.add_patch(Rectangle((-depth_middle,upper_spring),depth_middle,recorded['boss_rib_crown_y']-upper_spring,facecolor='#eef0ed',edgecolor='.55',ls='--',lw=.6))
 ax.add_patch(Rectangle((0,t['lower_opening_spring']),depth_low,t['third_layer_boss_rib_crown']-t['lower_opening_spring'],facecolor='#f7eeee',edgecolor='#b32b25',ls='--',lw=.7))
 ax.plot([0,depth_low],[t['third_layer_web_top_allowance']]*2,c='#b32b25',ls='--',lw=.8)
 ax.plot([-depth_middle,0],[recorded['gallery_soffit_y']]*2,c='k',lw=.65);ax.plot([-depth_middle,0],[recorded['gallery_floor_y']]*2,c='k',lw=.65)
 ax.plot([0,0],[0,t['window_clear_sill']],c='.4',lw=1);ax.plot([0,0],[t['window_clear_head'],recorded['gallery_soffit_y']],c='.4',lw=1)
 ax.plot([0,0],[t['window_clear_sill'],t['window_clear_head']],c='#23809b',lw=3)
 for y,label,col in [(recorded['boss_rib_crown_y'],'higher crown 4296','k'),(t['third_layer_boss_rib_crown'],'trial lower crown 2816','#a22'),(t['third_layer_web_top_allowance'],'trial web top 2880','#a22')]:
  ax.axhline(y,c=col,ls='--',lw=.5)
 ax.text(-depth_middle/2,3550,'MIDDLE A4\nrecorded height zone\n(projected)',ha='center',fontsize=9)
 ax.text(depth_low/2,2400,'PAIRED THIRD-LAYER VAULTS\nlower trial zone, projected\ncentral section crosses their common division',ha='center',fontsize=8,c='#a22')
 ax.annotate('window clear\n3072–3776',(0,3424),(650,3650),fontsize=9,arrowprops=dict(arrowstyle='-',color='.4'))
 dimh(ax,-depth_middle,0,-230,f'middle depth {depth_middle:.3f}')
 dimh(ax,0,depth_low,-230,f'third-layer depth {depth_low:.3f}')
 ax.axhline(0,c='k',lw=.8);ax.set(xlim=(-depth_middle-250,depth_low+300),ylim=(-450,4750),xlabel='Radial offset from middle/third receiving wall [native units]',ylabel='Absolute elevation [native units]');ax.set_aspect('equal');ax.grid(c='.9',ls='--',lw=.4);ax.set_title('B-B | radial level-coordination section',loc='left',fontsize=11)
 for n,poly,col,fill in [('middle',M,'k','#edf0ed'),('L3-07',left,'#a22','#f7eeee'),('L3-08',right,'#a22','#f7eeee')]:
  pp=np.vstack([poly,poly[0]]);outline(plan,pp,color=col,ls='--' if col=='#a22' else '-',fill=fill)
 lo=float(M[:,0].min());hi=float(left[:,0].max());plan.plot([lo,hi],[0,0],c='#355c87',lw=1.1)
 wallx=pair['inner_midpoint'][0];plan.plot([wallx,wallx],[-half,half],c='#355c87',lw=1.1)
 plan.text(wallx+50,1250,'A-A receiving wall',fontsize=8,c='#355c87');plan.text((lo+hi)/2,70,'B-B central radial cut',fontsize=8,c='#355c87',ha='center')
 for poly,txt in [(M,'M_A4'),(left,'L3-07'),(right,'L3-08')]:
  p=Polygon(poly).representative_point();plan.text(p.x,p.y,txt,ha='center',fontsize=8)
 plan.set_aspect('equal');plan.set(xlabel='Project X east',ylabel='Project Y north');plan.grid(c='.9',ls='--',lw=.4);plan.set_title('Exact plan locator',loc='left',fontsize=11)
 fig.suptitle('F5ZP | paired lower vaults and upper window — regular bay',x=.06,ha='left',fontsize=15)
 fig.text(.06,.025,'B-B uses exact plan depths and coordinate Y=0. Dashed rectangles show projected crown/spring zones, NOT recovered vault-web sections.\nThe center cut follows the shared low-vault division and passes through the upper window; support wall thickness remains unresolved.',fontsize=8)
 fig.tight_layout(rect=[0,.07,1,.95]);save(fig,'RADIAL_SECTION_BB_AND_PLAN')
 # Numerical fit and source regression; no construction/code/structural claim.
 tests=[]
 def check(n,ok,val=None):tests.append({'name':n,'pass':bool(ok),'value':val})
 check('Regular bay chosen, T4',pair['sector']=='T4')
 check('Equal paired plan frontages',abs(np.linalg.norm(left[0]-left[-1])-np.linalg.norm(right[0]-right[-1]))<1e-7)
 check('Full source chord matches radius/span',abs(bay-2*5285*math.sin(math.radians(12)))<1e-7)
 check('Clear openings and shared jambs close bay',abs(2*clear+192+2*96-bay)<1e-7)
 check('Lower spring below source spring',t['lower_opening_spring']<upper_spring)
 check('Lower rib crown below source crown',t['third_layer_boss_rib_crown']<recorded['boss_rib_crown_y'])
 check('Opening ring below low rib crown',metrics['lower_opening_outer_crown']<t['third_layer_boss_rib_crown'],metrics['lower_opening_outer_crown'])
 check('Low web allowance above rib crown',t['third_layer_web_top_allowance']>t['third_layer_boss_rib_crown'])
 check('Window frame above low web allowance',metrics['web_top_to_frame_bottom']>0,metrics['web_top_to_frame_bottom'])
 check('Window outer frame below upper planning envelope',window_clearance.min()>0,float(window_clearance.min()))
 check('Window centered above paired entrances',centers[0]==-centers[1])
 check('Window cap solves declared head',abs(wpar['crown']-t['window_clear_head'])<1e-7)
 check('Lower arches solve declared clear crowns',all(abs(o['parameters']['crown']-t['lower_opening_intrados_crown'])<1e-7 for o in op))
 for path,h in json.loads((I/'PARENT_HASHES.json').read_text()).items():
  p=Path(path)
  check('Packaged source matches '+p.name,hashlib.sha256((I/p.name).read_bytes()).hexdigest()==h)
  if p.exists():check('Parent unchanged '+p.name,hashlib.sha256(p.read_bytes()).hexdigest()==h)
 for p in R.glob('*.svg'):ET.parse(p);check('SVG parses '+p.name,True)
 put('SECTION_QA.json',{'status':'EXPERIMENTAL_2D_TRIAL_FOR_ONE_BAY','passed':sum(x['pass'] for x in tests),'failed':sum(not x['pass'] for x in tests),'checks':tests,'metrics':metrics,'parameters':t,'source_datums':recorded,'source_R2_reference':{'spring':upper_spring,'apex':upper_apex,'profile':[168,192],'profile_intrados_unverified':True},'actual_vault_web_sections_recovered':False,'actual_clearance_to_existing_moulding_verified':False,'structural_capacity_verified':False,'approved_geometry_changed':False,'propagated_to_other_bays':False})
 put('MEASUREMENTS.json',metrics)
 assert all(x['pass'] for x in tests),[x for x in tests if not x['pass']]
 print('REGULAR_BAY_SECTION_COMPLETE',sum(x['pass'] for x in tests),'checks')
if __name__=='__main__':main()
