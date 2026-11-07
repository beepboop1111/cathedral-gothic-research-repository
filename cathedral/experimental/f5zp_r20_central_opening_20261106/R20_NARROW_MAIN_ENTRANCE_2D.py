#!/usr/bin/env python3
"""R20: exact dark 2D plan overlay, only central R13-B opening shrunk.
Experimental only; no source geometry changed or approved.
"""
from pathlib import Path
import json,csv,hashlib,zipfile,shutil,xml.etree.ElementTree as ET
from shapely.geometry import shape,box,mapping
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as P,Patch,Rectangle
from matplotlib.lines import Line2D
from PIL import Image
R=Path(__file__).resolve().parent
O=R/'R20_Q1_Q2_MAIN_ENTRANCE_NARROWING_EXPERIMENTAL';O.mkdir(exist_ok=True)
src={'R11':R/'R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson',
'R13':R/'R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson'}
sha={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in src.items()}
read=lambda k:json.loads(src[k].read_text())['features']
r11,r13=read('R11'),read('R13')
clear={f['properties']['id']:shape(f['geometry']) for f in r11 if f['properties'].get('role')=='CLEAR'}
masonry=[shape(f['geometry']) for f in r11 if 'MASONRY' in f['properties'].get('id','')]
choir=next(shape(f['geometry']) for f in r11 if f['properties'].get('id')=='CHOIR_MASONRY_R10')
passages={f['properties']['id']:shape(f['geometry']) for f in r13 if f['properties'].get('variant')=='B_BALANCED' and f['properties'].get('layer')=='EXPERIMENTAL_PASSAGE_VOID'}
assert len(clear)==218 and len(passages)==7
old=passages['B_BALANCED_MAIN_PASSAGE']
assert old.bounds==(3925.,-2573.,5085.,2573.)
new=box(3925,-2000,5085,2000)
assert old.covers(new) and old.area>new.area
unchanged={k:v for k,v in passages.items() if k!='B_BALANCED_MAIN_PASSAGE'}
oldvoid=unary_union(list(passages.values()))
newvoid=unary_union(list(unchanged.values())+[new])
cv=unary_union(list(clear.values()))
assert new.intersection(cv).area<1e-5
assert new.difference(choir).area<1e-5
assert all(g.intersection(new).area<1e-5 for g in unchanged.values())
assert oldvoid.symmetric_difference(newvoid).area==old.difference(new).area
restored=old.difference(new)
assert restored.area==1160*1146
assert new.bounds[0]+(new.bounds[2]-new.bounds[0])/2==4505
assert new.bounds[3]==2000 and new.bounds[1]==-2000
assert (2933-2573)==360 and (2933-2000)==933
assert old.difference(new).geom_type=='MultiPolygon'
# exact edited variation of R13 passages as separate versioned layer
features=[]
for key,poly in passages.items():
 altered=key=='B_BALANCED_MAIN_PASSAGE'
 g=new if altered else poly
 features.append({'type':'Feature','properties':{'id':key.replace('B_BALANCED','R20_EXPERIMENTAL'),
 'source_id':key,'type':'ENTRANCE_VOID','variant':'R20_MAIN_4000_SIX_AISLES_UNCHANGED',
 'status':'EXPERIMENTAL_NOT_APPROVED','changed_from_R13':altered},'geometry':mapping(g)})
(O/'R20_OPTION_B_CENTRAL_4000_PASSAGE_ONLY.geojson').write_text(json.dumps({
'type':'FeatureCollection','properties':{'status':'EXPERIMENTAL ONLY','source_sha256':sha,
 'main_axis_x':4505,'main_opening_clear_y':4000},'features':features},separators=(',',':'))+'\n')
# PNG summary with full R11 cathedral and two large close-up arrangements.
plt.rcParams.update({'text.color':'#edf4f9','axes.labelcolor':'#bfd1dc',
 'xtick.color':'#a7bfcd','ytick.color':'#a7bfcd','axes.edgecolor':'#7892a4',
 'font.size':10,'savefig.facecolor':'#0c1420'})
def draw(ax,geom,color,edge='#8eacb6',lw=.32,z=1,alpha=1):
 ps=[geom] if geom.geom_type=='Polygon' else [v for v in getattr(geom,'geoms',[]) if v.geom_type=='Polygon']
 for poly in ps:
  ax.add_patch(P(list(poly.exterior.coords),facecolor=color,edgecolor=edge,linewidth=lw,
    alpha=alpha,zorder=z))
  if color!='none':
   for hole in poly.interiors:
    ax.add_patch(P(list(hole.coords),facecolor='#13202c',edgecolor='none',zorder=z+.01))
def base(ax,which):
 ax.set_facecolor('#13202c')
 for g in masonry:draw(ax,g,'#515f70',edge='#515f70',lw=.2)
 for g in clear.values():draw(ax,g,'#1c3341',edge='#749bac',lw=.35,z=2)
 for key,g in passages.items():
  plot=new if which=='new' and key=='B_BALANCED_MAIN_PASSAGE' else g
  draw(ax,plot,'#2e86ac',edge='#8ee7ff',lw=.85,z=4)
 if which=='new':
  draw(ax,restored,'#d5ae64',edge='#f3d49b',lw=.7,alpha=.98,z=5)
 ax.axvline(4505,color='#ffb45f',ls='--',lw=1,zorder=10)
 ax.grid(alpha=.09);ax.set_aspect('equal','box')
 ax.set_xlabel('Global X • native units')
 ax.set_ylabel('Global Y • native units')
fig=plt.figure(figsize=(18,12),facecolor='#0c1420')
gr=fig.add_gridspec(2,2,height_ratios=[.9,1.6],left=.065,right=.987,top=.88,bottom=.115,hspace=.32,wspace=.18)
full=fig.add_subplot(gr[0,:]);left=fig.add_subplot(gr[1,0]);right=fig.add_subplot(gr[1,1])
base(full,'new');base(left,'old');base(right,'new')
allbounds=unary_union(list(clear.values())).bounds
full.set_xlim(allbounds[0]-1900,allbounds[2]+1900)
full.set_ylim(allbounds[1]-1800,allbounds[3]+1800)
# Highlight placement on entire floor plan
full.add_patch(Rectangle((3100,-8100),2700,16200,facecolor='none',edgecolor='#fd66c8',lw=2.4,zorder=12))
full.annotate('Q1–Q2  |  CENTER OF STUDY',xy=(5800,8000),xytext=(10900,10800),
  fontsize=10.8,color='#ff80d1',weight='bold',arrowprops={'arrowstyle':'->','color':'#ff80d1'})
for ax in (left,right):
 ax.set_xlim(3100,5900);ax.set_ylim(-8300,8300)
 ax.axhline(2933,color='#f9c26b',lw=.55,ls=':',alpha=.55)
 ax.axhline(-2933,color='#f9c26b',lw=.55,ls=':',alpha=.55)
left.set_title('BEFORE  |  R13 Option B',loc='left',pad=10,fontsize=13,weight='bold')
right.set_title('AFTER  |  R20 central only',loc='left',pad=10,fontsize=13,weight='bold')
full.set_title('1  |  Entire cathedral — same R11 floor plan',loc='left',pad=11,fontsize=13,weight='bold')
left.text(5730,1000,'5,146\nMAIN',fontsize=15,color='#9ce6ff',ha='right',weight='bold',zorder=15)
right.text(5730,1000,'4,000\nMAIN',fontsize=15,color='#9ce6ff',ha='right',weight='bold',zorder=15)
right.annotate('933 end masonry\n(previously 360)',xy=(4930,2470),xytext=(5170,3900),
 color='#f3d49b',fontsize=11,ha='left',weight='bold',
 arrowprops=dict(arrowstyle='->',color='#f3d49b'),zorder=15)
fig.suptitle('F5ZP — CHOIR ENTRANCE IN THE COMPLETE 2D FLOOR PLAN\n'
 'Central sanctuary opening only: 5,146 → 4,000  |  six aisle entrances unchanged',
 x=.065,y=.981,ha='left',fontsize=17,weight='bold')
fig.legend(handles=[Patch(facecolor='#2e86ac',edgecolor='#8ee7ff',label='Clear entrance (R13 / R20)'),
 Patch(facecolor='#d5ae64',label='Masonry reclaimed inside existing reservation'),
 Patch(facecolor='#1c3341',edgecolor='#749bac',label='Protected vault clearance'),
 Line2D([0],[0],color='#ffb45f',ls='--',label='Reference axis X4505')],
 loc='lower center',bbox_to_anchor=(.5,.047),ncol=2,frameon=False,labelcolor='#edf4f9',fontsize=10)
fig.text(.065,.013,'New opening is experimental, not approved. Total vaulted space, cathedral outline, and six side passages are unchanged.',
 fontsize=9.8,color='#b6c6d0')
png=O/'F5ZP_R20_FULL_PLAN_MAIN_ENTRANCE_BEFORE_AFTER_DARK.png'
svg=O/'F5ZP_R20_FULL_PLAN_MAIN_ENTRANCE_BEFORE_AFTER_DARK.svg'
fig.savefig(png,dpi=155,bbox_inches='tight');fig.savefig(svg,bbox_inches='tight');plt.close(fig)
qa={'status':'R20 EXPERIMENTAL 2D CENTRAL OPENING STUDY','sources_sha256':sha,
 'all_source_geometry_unchanged':True,'vault_polygons_unchanged':218,
 'six_aisle_openings_identical_to_R13_B':True,
 'main_opening_width_in_plan_Y_original':5146,
 'main_opening_width_in_plan_Y_trial':4000,
 'main_opening_depth_in_plan_X_unchanged':1160,
 'main_clear_reduction':1146,'main_side_end_masonry_original_each':360,
 'main_side_end_masonry_trial_each':933,
 'main_masonry_added_to_end_each':573,
 'masonry_return_area_total':restored.area,
 'trial_main_fits_R11_masonry':True,
 'new_void_intersects_clear_vaults_area':new.intersection(cv).area,
 'main_axis_x':4505,'architectural_approval':False,
 'structural_validation':False,'historical_validation':False,
 'limitations':['Proportions and visual dominance still require architectural review.',
 'R16/R17 prior measured main jamb lengths 360 refer to R13 B. R20 has 933 reserved at each end; do not silently relabel old physical bearing checks.',
 'No arch heights, springing, masonry bonding or loading were assessed.',
 'R11, R13 and all earlier experimental outputs remain unchanged.']}
(O/'R20_NUMERICAL_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
(O/'README_HANDOFF.md').write_text('''# R20 — Reduce ONLY the central choir entrance in plan
Dark-mode three-part image: entire cathedral, R13-B original Q1-Q2, R20 narrowed Q1-Q2. Main passage is 4,000 native units on Y, centered at Y=0; old 5,146. Each receiving end reserve rises 360→933 native units (addition 573); recovered area is 1,329,360 square units. In-plane through-wall depth X stays 1,160. All six secondary entrances remain exactly as before, along with 218 clear vault polygons. Main organizing X axis remains 4,505. Read-only sources.

This is architectural proportion research, NOT approved pier sizes, changed structural supports, arch springing or actual masonry construction. R16/R17 earlier 360-unit main contacts are historical measurements for R13-B and should not be cited as the updated R20 main end dimension. F5ZL-C remains missing.

Reproduce: python3 R20_NARROW_MAIN_ENTRANCE_2D.py
''')
ET.parse(svg)
with Image.open(png) as im:print('PNG',im.size);im.verify()
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[k] for k,p in src.items())
out=Path.home()/'Downloads'/png.name;shutil.copy2(png,out)
archive=Path.home()/'Downloads'/'F5ZP_R20_CENTRAL_ENTRANCE_4000_EXPERIMENTAL.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
 z.write(Path(__file__),arcname=Path(__file__).name)
 for f in O.iterdir():z.write(f,arcname=f.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('R20 PASS; recovered masonry',restored.area,'QA+zip',archive)