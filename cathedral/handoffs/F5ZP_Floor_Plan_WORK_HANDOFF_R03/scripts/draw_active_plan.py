"""Render only carried-forward plan set-out; chapel bodies and openings excluded."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype']='none'
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'ACTIVE_2D_PLAN_CANDIDATE.json').read_text())
fig,ax=plt.subplots(figsize=(10,10))
def draw(vertices,col,ls,lw):
 p=vertices+[vertices[0]];ax.plot([q[0] for q in p],[q[1] for q in p],c=col,ls=ls,lw=lw)
for key,v in d['cells'].items():
 if key.startswith(('I_','M_')):draw(v['vertices'],'k','-',.8)
for key,v in d['lower_vault_footprints'].items():
 draw(v['vertices'],'#b32b25','--',.8)
 x=sum(p[0] for p in v['vertices'])/len(v['vertices']);y=sum(p[1] for p in v['vertices'])/len(v['vertices']);ax.text(x,y,key.replace('L3-',''),ha='center',fontsize=7,color='#922')
for idx,key in [(2,'T2'),(7,'T6')]:
 p=d['outer_passage_nodes'][idx];ax.scatter(*p,c='#b32b25',s=18)
 ax.annotate(key+' corrected corner',p,(p[0]+1700,p[1]),fontsize=9,color='#922',arrowprops=dict(arrowstyle='-',color='.5',lw=.6))
ax.axhline(0,c='.6',ls='--',lw=.5);ax.set_aspect('equal');ax.grid(c='.9',ls='--',lw=.4)
ax.set(xlabel='Project X east [native units]',ylabel='Project Y north [native units]',title='F5ZP | 7 inner · 7 middle · 14 lower vault footprints\n2D working handoff R03 — EXPERIMENTAL')
fig.text(.09,.025,'Black: recovered inner/middle set-out. Red dashed: experimental outer footprints.\nChapel bodies and opening/receiver positions deferred. Native units; physical conversion unresolved.',fontsize=8)
fig.tight_layout(rect=[0,.07,1,1])
for ext in ['png','svg']:fig.savefig(R/f'CURRENT_2D_PLAN.{ext}',dpi=180)
