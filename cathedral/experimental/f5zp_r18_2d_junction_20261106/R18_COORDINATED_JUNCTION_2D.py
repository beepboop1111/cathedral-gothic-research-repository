#!/usr/bin/env python3
"""R18: consolidate existing R16/R17 references, audit junctions, study 235 emphasis.
2D only; originals are immutable; no new pier or arch construction.
"""
from pathlib import Path
import json,csv,hashlib,zipfile,shutil,collections,xml.etree.ElementTree as ET
from shapely.geometry import shape,box,mapping
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch,Patch as LegendPatch
from matplotlib.lines import Line2D
from PIL import Image
R=Path(__file__).resolve().parent
O=R/'R18_Q1_Q2_COORDINATED_JUNCTION_EXPERIMENTAL';O.mkdir(exist_ok=True)
P={
 'R11':R/'R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson',
 'R13':R/'R13_Q1_Q2_ENTRANCE_BEARINGS_EXPERIMENTAL/R13_Q1_Q2_OPENINGS_AND_BEARINGS_EXPERIMENTAL.geojson',
 'R16':R/'R16_Q1_Q2_BEARING_FACE_CONTACT_EXPERIMENTAL/R16_Q1_Q2_EXACT_FACE_CONTACT_STRIPS.geojson',
 'R17':R/'R17_Q1_Q2_MASONRY_JUNCTION_2D_EXPERIMENTAL/R17_EXISTING_MASONRY_JUNCTION_REFERENCES.geojson'}
hashes={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in P.items()}
a={k:json.loads(p.read_text())['features'] for k,p in P.items()}
clear={f['properties']['id']:shape(f['geometry']) for f in a['R11'] if f['properties'].get('role')=='CLEAR'}
sol=next(shape(f['geometry']) for f in a['R11'] if f['properties'].get('id')=='CHOIR_MASONRY_R10')
void={f['properties']['id']:shape(f['geometry']) for f in a['R13'] if f['properties'].get('variant')=='B_BALANCED' and f['properties'].get('layer')=='EXPERIMENTAL_PASSAGE_VOID'}
contacts={f['properties']['opening']+'_'+f['properties']['end']:shape(f['geometry']) for f in a['R16']}
bridges={f['properties']['name']:shape(f['geometry']) for f in a['R17']}
assert len(clear)==218 and len(void)==7 and len(contacts)==14 and len(bridges)==8
vu=unary_union(list(void.values()));cu=unary_union(list(clear.values()));ret=sol.difference(vu)
# Consolidated layer is the union of cited references only; retain original
# polygons separately in export for independently verifiable provenance.
allrefs={**{'R16_'+k:g for k,g in contacts.items()},**{'R17_'+k:g for k,g in bridges.items()}}
union=unary_union(list(allrefs.values()))
assert union.is_valid and union.difference(ret).area<1e-4
assert union.intersection(vu).area<1e-4 and union.intersection(cu).area<1e-4
# R16 contact strips and R17 wall rectangles should form 2 separate assemblies
# (north and south) with no unwanted geometric disconnection.
sides={}
for side in 'NS':
 names=[n for n in allrefs if n.startswith('R17_'+side+'_') or n.startswith('R16_'+side+'_')]
 names+=['R16_C_MAIN_'+('UPPER' if side=='N' else 'LOWER')]
 geom=unary_union([allrefs[n] for n in names])
 sides[side]=geom
 # Each planned doorway separates neighboring junction blocks; require four
 # distinct connected groups, one per transverse support zone.
 assert geom.geom_type=='MultiPolygon' and len(geom.geoms)==4,(side,geom.geom_type,len(getattr(geom,'geoms',[])))
assert sides['N'].disjoint(sides['S'])
# Quantified attachment: contact segment between R16 and R17 pieces at original interfaces.
links=[];fragile=[]
for side in 'NS':
 main=contacts['C_MAIN_'+('UPPER' if side=='N' else 'LOWER')]
 a1=contacts[f'{side}_A1_'+('LOWER' if side=='N' else 'UPPER')]
 orig=bridges[f'{side}_MAJOR_ORIGINAL_800']
 east=bridges[f'{side}_EAST_360']
 for label,u,v in [('MAIN_TO_MAJOR',main,orig),('MAJOR_TO_A1',orig,a1),
                   ('MAJOR_TO_EAST',orig,east),('EAST_TO_MAIN',east,main)]:
  length=u.boundary.intersection(v.boundary).length
  links.append(dict(side=side,junction=label,shared_boundary_length=length,
                    contact_type='LINE' if length>1e-4 else 'POINT_OR_GAP'))
 for i in (1,2):
  low=contacts[f'{side}_A{i}_'+('UPPER' if side=='N' else 'LOWER')]
  high=contacts[f'{side}_A{i+1}_'+('LOWER' if side=='N' else 'UPPER')]
  b=bridges[f'{side}_A{i}_TO_A{i+1}']
  for label,part in [('LOWER',low),('UPPER',high)]:
   length=part.boundary.intersection(b.boundary).length
   links.append(dict(side=side,junction=f'A{i}_A{i+1}_{label}',shared_boundary_length=length,
                     contact_type='LINE' if length>1e-4 else 'POINT_OR_GAP'))
 assert all(q['shared_boundary_length']>0 for q in links if q['side']==side)
# Measured 2D narrowness, NOT a structural threshold. Preserve split at 197,321.
sections=[]
for side in 'NS':
 for n,g in bridges.items():
  if n.startswith(side+'_'):
   b=g.bounds
   sections.append(dict(side=side,region=n,x_span=b[2]-b[0],y_span=b[3]-b[1],
      total_area=g.area,min_bbox_dimension=min(b[2]-b[0],b[3]-b[1]),
      remark=('197-unit A1-A2 existing narrow band' if '_A1_TO_A2' in n else
         '321-unit effective Q1-A2/A3 stagger, not general 292 schedule' if '_A2_TO_A3' in n else
         'Original 800 and east 360 preserve main-axis 4505 reference')))
# detect internal overlaps between annotated regions; may be intentional overlay.
overlap=[]
keys=list(allrefs)
for i,k in enumerate(keys):
 for h in keys[i+1:]:
  area=allrefs[k].intersection(allrefs[h]).area
  if area>1e-4:overlap.append(dict(first=k,second=h,overlap_area=area))
# 235 visual line: only the original six facing rectangles from R14 step2,
# or identical y windows measured in main-to-A1 and A1-A2/A2-A3 bridges.
x0,x1=4505-117.5,4505+117.5
core=box(x0,-8200,x1,8200)
emphasis=union.intersection(core)
assert emphasis.area>0 and emphasis.difference(ret).area<1e-4
# Relative to actual aisle 4480, its x-span is asymmetrically placed:
# core x4387.5..4622.5 => 142.5 west, 92.5 east.
core_offset=(x0+x1)/2-4480
assert core_offset==25
# Key architectural caveat: applying 235 line to full union is a graphic overlay,
# not choosing future pier thickness, and must not erase the 197/321 bands.
visual_qa={'x0':x0,'x1':x1,'width':x1-x0,'center_x':4505,
            'aisle_center_x':4480,'center_offset_to_aisle_x':25,
            'extends_to_west_of_aisle_center':4480-x0,
            'extends_to_east_of_aisle_center':x1-4480,
            'overlap_current_integrated_reservation_area':emphasis.area,
            'status':'NON_STRUCTURAL_GRAPHIC_ONLY'}
# Junction polygon exterior edges and corners: check each source polygon as-is;
# local narrowness is recorded as BBOX width (not minimum structural section).
qa={'status':'R18 COORDINATED 2D STUDY ONLY; ARCHITECTURAL AND STRUCTURAL APPROVAL PENDING',
 'source_sha256':hashes,'R11_unchanged':True,'R13_B_unchanged':True,
 'R16_14_source_strips_unchanged':True,'R17_8_source_regions_unchanged':True,
 'features_in_integrated_set':len(allrefs),'integrated_area':union.area,
 'north_south_group_geometry':{side:{'geometry':sides[side].geom_type,'separate_junction_blocks':len(sides[side].geoms)} for side in sides},
 'all_connection_lengths_positive':True,'connection_count':len(links),
 'positive_area_overlaps_between_annotated_features':len(overlap),
 'overlap_pairs':overlap,'narrowness_is_geometric_not_structural':True,
 'bridge_sections':sections,'visual_emphasis':visual_qa,
 'no_intrusion_into_vaults_or_B_openings':True,
 'issues':['Each side has FOUR separate masonry junction blocks in this extracted contact-reference layer, separated by retained opening clear spaces; no continuous chain of solid bearing faces across all aisle rows is claimed.', 'Original major rectangle and east continuation are distinct annotations within R11 reserved masonry; not a certified joint.',
   'A1-A2 bridge is 197 native units; no safe structural threshold established.',
   'A2-A3 effective bridge is 321 at this staggered junction rather than standard 292.',
   '235-unit facing is an organizing graphic, not a supported pier width.',
   'R16 face contacts are planar only; no springing, arch elevations, courses or masonry bonding.',
   'Q1-Q2 aisle axis remains 25 units west of main separator reference.',
   'F5ZL-C support schedule remains unresolved.']}
with (O/'R18_JUNCTION_EDGE_CONTACTS.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(links[0]));w.writeheader();w.writerows(links)
with (O/'R18_MASONRY_NARROWNESS.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(sections[0]));w.writeheader();w.writerows(sections)
features=[]
for name,g in allrefs.items():
 features.append({'type':'Feature','properties':{'id':name,'status':'EXISTING_R16_R17_REVIEW_REFERENCE',
         'source':'R16' if name.startswith('R16_') else 'R17'},'geometry':mapping(g)})
features.append({'type':'Feature','properties':{'id':'235_AXIS_EMPHASIS_INSIDE_REFERENCES',
    'status':'VISUAL_ONLY_NOT_STRUCTURAL'},'geometry':mapping(emphasis)})
(O/'R18_CONSOLIDATED_2D_JUNCTION_REFERENCES.geojson').write_text(json.dumps({
 'type':'FeatureCollection','properties':{'sources_sha256':hashes,'experimental':True},
 'features':features},separators=(',',':'))+'\n')
(O/'R18_NUMERICAL_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
# Single review image, two aligned views.
def draw(ax,g,color,edge='#426371',lw=.5,alpha=1,z=1):
 gs=[g] if g.geom_type=='Polygon' else [s for s in getattr(g,'geoms',[]) if s.geom_type=='Polygon']
 for p in gs:
  ax.add_patch(Patch(list(p.exterior.coords),facecolor=color,edgecolor=edge,
                     linewidth=lw,alpha=alpha,zorder=z))
  if color!='none':
   for ring in p.interiors:ax.add_patch(Patch(list(ring.coords),facecolor='#fffefa',edgecolor='none',zorder=z+.1))
fig,ax=plt.subplots(1,2,figsize=(16.2,11),facecolor='white')
for axy in ax:
 draw(axy,ret,'#cdb9a0',lw=.2,z=1)
 for n,g in clear.items():
  if g.bounds[2]<3600 or g.bounds[0]>5550:continue
  draw(axy,g,'#e7efe8',lw=.45,z=3)
 for g in void.values():draw(axy,g,'#b2dceb',lw=.55,z=4)
 for name,g in allrefs.items():
  color='#6d9f92' if name.startswith('R16_') else ('#bc8951' if 'MAJOR' in name else '#7896b3')
  draw(axy,g,color,lw=.5,alpha=.84,z=6)
 draw(axy,emphasis,'#a65b88',edge='none',lw=0,alpha=.9,z=8)
 axy.axvline(4505,color='#a14444',ls='--',lw=1,zorder=10)
 axy.axvline(4480,color='#537cb2',ls=':',lw=.8,zorder=10)
 axy.set_aspect('equal','box');axy.grid(alpha=.1)
 axy.set_xlabel('Global X • native units');axy.set_ylabel('Global Y • native units')
ax[0].set_xlim(3700,5320);ax[0].set_ylim(-8140,8140)
ax[1].set_xlim(4100,4900);ax[1].set_ylim(2550,6580)
ax[0].set_title('North + south — full consolidated junction reference',fontsize=11,loc='left',pad=10,weight='bold')
ax[1].set_title('North — 320, 197, and 321 transverse bands',fontsize=11,loc='left',pad=10,weight='bold')
fig.suptitle('F5ZP R18 | 2D Q1–Q2 MASONRY COORDINATION\n'
 'R16+R17 source references combined; 235 visual emphasis independently marked',
 x=.05,y=.975,ha='left',fontsize=15.6,weight='bold',color='#283e48')
fig.legend(handles=[LegendPatch(facecolor='#6d9f92',label='R16 receiving contact strip'),
 LegendPatch(facecolor='#bc8951',label='R17 recovered major bearing'),
 LegendPatch(facecolor='#7896b3',label='R17 reserved-masonry bridge'),
 LegendPatch(facecolor='#a65b88',label='235 visual axis emphasis only'),
 LegendPatch(facecolor='#b2dceb',label='Option B preserved passage'),
 Line2D([0],[0],color='#a14444',ls='--',label='Main axis 4505')],
 loc='lower center',bbox_to_anchor=(.5,.045),ncol=3,fontsize=9,frameon=False)
fig.text(.05,.014,'No modified vaults, passages, or actual supports. Highlighted intersections are 2D references; load paths, bearing capacity and arch geometry remain unresolved.',fontsize=9.4,color='#895043')
fig.subplots_adjust(left=.045,right=.985,bottom=.14,top=.885,wspace=.2)
png=O/'F5ZP_R18_Q1_Q2_COORDINATED_JUNCTION.png'
svg=O/'F5ZP_R18_Q1_Q2_COORDINATED_JUNCTION.svg'
fig.savefig(png,dpi=160,bbox_inches='tight');fig.savefig(svg,bbox_inches='tight');plt.close(fig)
ET.parse(svg)
with Image.open(png) as im:im.verify();print('PNG verified',im.size)
(O/'README_HANDOFF.md').write_text('''# F5ZP R18 — Q1–Q2 three-task 2D consolidation

**Scope:** (1) consolidate unmodified R16 and R17 references, (2) inspect geometric continuity, overlaps and thin regions, (3) study the 235-wide *visual* central emphasis. No new arch, pier, or physical opening built.

Main organizing axis X4505, aisle opening axis X4480. All 14 receiving strips and eight masonry-junction extraction polygons retained exactly. North and south each have FOUR distinct junction blocks separated by openings; the reference strips must not be described as one continuously connected wall. Main-to-A1 through recovered 800×320 band + east 360 remainder; A1–A2 has a 470×197 strip; A2–A3 has 470×321 due to staggered end geometry (general 292 schedule unchanged).

The 235-unit axis emphasis is plotted only as the intersection of a centered strip with existing junction-reference polygons, rather than treated as real material thickness or a designed pier. It sits 142.5 west and 92.5 east of the x4480 aisle opening axis. Any overlaps among reference polygons are not additional masonry; consult numeric QA.

Nothing promoted to approved. R11/R13/R16/R17 unchanged. Geometric checks do not demonstrate structural feasibility. Original displaced outer supports and missing F5ZL-C support schedule remain unresolved.

Reproduce by running python3 R18_COORDINATED_JUNCTION_2D.py in the R12C workspace.
''')
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[k] for k,p in P.items())
dest=Path.home()/'Downloads'/'F5ZP_R18_Q1_Q2_COORDINATED_JUNCTION.png'
shutil.copy2(png,dest)
archive=Path.home()/'Downloads'/'F5ZP_R18_Q1_Q2_COORDINATED_JUNCTION_EXPERIMENTAL.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.write(Path(__file__),arcname=Path(__file__).name)
 for f in sorted(O.iterdir()):z.write(f,arcname=f.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('PASS',len(allrefs),'refs',len(links),'edge connections; overlaps',len(overlap),'zip',archive)