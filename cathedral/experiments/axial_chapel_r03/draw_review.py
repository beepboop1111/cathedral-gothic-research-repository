import json,pathlib,math,csv,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon as Patch
from shapely.geometry import Polygon
R=pathlib.Path(__file__).resolve().parent;q=json.loads((R/'QA.json').read_text());D=json.loads((R/'inputs/BASELINE.json').read_text());pr=json.loads((R/'PROFILES.json').read_text());sec=json.loads((R/'LONGITUDINAL_MESH_SECTION.json').read_text());red='#aa303a';gray='#90969b'
q['checks']['designed_profile_polygons_valid']=all(Polygon(pr[n]).is_valid and Polygon(pr[n]).area>0 for n in ['RIB','MAJOR_ARCH','RIDGE'])
q['checks']['two_bays_have_eight_web_panels']=sum(x['name'].startswith(('BAY1_WEB','BAY2_WEB')) for x in q['measured']['web_patch_details'])==8
q['checks']['input_plan_hash_unchanged']=hashlib.sha256((R/'inputs/BASELINE.json').read_bytes()).hexdigest()==q['source_sha256']
(R/'QA.json').write_text(json.dumps(q,indent=2))
fig,axes=plt.subplots(3,1,figsize=(15,13),gridspec_kw={'height_ratios':[1.2,1.2,1]})
ax=axes[0]
for k,c in D['cells'].items():
 if k.startswith(('I_','M_')):
  p=np.array(c['vertices']+[c['vertices'][0]]);ax.plot(*p.T,color='black',lw=.7)
a=[(33400+1250*math.cos(math.radians(t)),1250*math.sin(math.radians(t))) for t in [-90,-54,-18,18,54,90]]
outline=[(28000,-1250),(28600,-1250),(31000,-1250),(33400,-1250)]+a[1:]+[(31000,1250),(28600,1250),(28000,1250),(28000,-1250)]
p=np.array(outline);ax.plot(*p.T,color=red,ls='--',lw=1.3)
for x in [28000,28600,31000,33400]:
 ax.plot([x,x],[-1250,1250],color=red,ls='--',lw=.8)
 ax.text(x,1500,str(x),ha='center',fontsize=8)
for r in q['measured']['rib_branches']:
 ax.plot([r['A'][0],r['B'][0]],[r['A'][1],r['B'][1]],color=gray,ls='--',lw=.7)
for x,z in [(26700,3620),(29800,4150),(32200,4400),(33850,4550)]:ax.plot(x,0,'+',color=red);ax.text(x,-220,f'{z}',ha='center',fontsize=8)
ax.text(28300,-1700,'600 threshold',ha='center',fontsize=8);ax.text(29800,1650,'BAY 1 · 2400',ha='center');ax.text(32200,1650,'BAY 2 · 2400',ha='center');ax.text(34000,1650,'APSE',ha='center');ax.set_aspect('equal');ax.set_xlim(24800,35200);ax.set_ylim(-2100,2200);ax.set_title('Plan: source inner/middle edge in black; all new axial geometry experimental');ax.set_xlabel('X east · native project units');ax.set_ylabel('Y north')
ax=axes[1]
for name,segments in sec.items():ax.add_collection(LineCollection(segments,colors=red if name!='ROOF' else gray,linewidths=.55 if name!='ROOF' else .9,linestyles='--'))
for x,z,name in [(26700,3620,'AMB'),(29800,4150,'BAY 1'),(32200,4400,'BAY 2'),(33850,4550,'APSE')]:ax.annotate(f'{name} {z}',(x,z),xytext=(x,z+600),ha='center',fontsize=8,arrowprops={'arrowstyle':'-','color':gray,'lw':.6})
ax.set_aspect('equal');ax.set_xlim(24800,35200);ax.set_ylim(-150,5600);ax.set_title('Longitudinal Y=0 section extracted from actual meshes; gray dashed = roof');ax.set_xlabel('X east');ax.set_ylabel('Z elevation')
ax=axes[2]
for name,offset in [('RIB',0),('MAJOR_ARCH',310),('RIDGE',650)]:
 p=np.array(pr[name]);pp=np.vstack([p,p[0]]);ax.plot(pp[:,0]+offset,-pp[:,1],color=red,ls='--');ax.text(offset,35,name,ha='center');ax.text(offset,-200,f'{p[:,0].ptp() if hasattr(p[:,0],"ptp") else np.ptp(p[:,0]):.2f} wide / {p[:,1].max():.2f} deep',ha='center',fontsize=8)
ax.set_aspect('equal');ax.set_xlim(-180,820);ax.set_ylim(-230,70);ax.axis('off');ax.set_title('New designed vector profiles · rolls / hollows / central keel · no historical trace claim')
fig.suptitle('F5ZP axial chapel R03 — EXPERIMENTAL · protected cathedral unchanged',fontsize=16);fig.tight_layout();fig.savefig(R/'MEASURED_REVIEW.svg');fig.savefig(R/'MEASURED_REVIEW.png',dpi=150);plt.close(fig)
# Export profile geometry at numerical drawing scale for reuse.
fig,ax=plt.subplots(figsize=(10,4))
for name,offset in [('RIB',0),('MAJOR_ARCH',310),('RIDGE',650)]:
 p=np.array(pr[name]);ax.add_patch(Patch(p*np.array([1,-1])+[offset,0],fill=False,edgecolor=red,ls='--'));ax.text(offset,25,name,ha='center')
ax.set_aspect('equal');ax.set_xlim(-150,800);ax.set_ylim(-180,60);ax.set_xlabel('Native section units');fig.tight_layout();fig.savefig(R/'PROFILE_SECTIONS.svg');plt.close(fig)
with open(R/'DIMENSIONS.csv','w') as f:
 w=csv.writer(f);w.writerow(['element','x_start','x_end','boss_crown_Z','note']);w.writerows([['ambulatory',D['cells']['M_A4']['vertices'][1][0],28000,3620,'four bearings / five webs'],['threshold',28000,28600,3750,'soffit crown; 600 deep;2200 clear'],['bay1',28600,31000,4150,'new experimental'],['bay2',31000,33400,4400,'new experimental'],['apse',33400,max(p[0] for p in a),4550,'five external faces']])
print('QA',sum(q['checks'].values()),'/',len(q['checks']))
