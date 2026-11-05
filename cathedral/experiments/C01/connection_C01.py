from pathlib import Path
import sys,json,hashlib
sys.path.append('.x04_deps')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
from shapely.geometry import shape,LineString,box,mapping
from shapely.ops import transform
r=Path('.');s=Path('F5ZP_X02_R06_CONTEXT_REVIEW/sources');a=json.loads((s/'R03_GEOMETRY.json').read_text());b=json.loads((s/'R02_CONTEXT.json').read_text());e=json.loads((r/'connection_C01_G40_evidence.json').read_text())
def native(q):return transform(lambda x,z:(x*1000/1.3,(z-2.7584)*1000/1.3),q)
fig=plt.figure(figsize=(13,8));ax=fig.add_axes([.06,.10,.68,.80]);notes=fig.add_axes([.77,.10,.22,.80]);notes.axis('off')
def draw(q,fill='none',color='#78838a',dash='--',lw=.8):
 for p in getattr(q,'geoms',[q]):
  if p.geom_type=='Polygon':ax.add_patch(Patch(list(p.exterior.coords),facecolor=fill,edgecolor=color,linestyle=dash,linewidth=lw))
for f in a['features']:
 role=f['properties']['role']
 if role=='building':draw(native(shape(f['geometry'])),fill='#f3f1ea')
 elif role=='court':draw(native(shape(f['geometry'])),fill='#edf0e4',color='#adb5a3')
for f in b['features']:
 if f['id']=='wall' or f['id'].startswith('ROOT'):draw(native(shape(f['geometry'])),fill='#d8d8d4',color='#444a4e',dash='-')
 if f['id']=='chapel_reference':draw(native(shape(f['geometry'])),color='#a8443b')
for f in e:
 if f['name'].startswith('G40I3A3__JAMB') or f['name']=='G40K1_PREFERRED_SYMMETRIC_REAR_THREE_ARCH_WALL':
  lo=f['bounds']['min'];hi=f['bounds']['max'];draw(box(lo[0],lo[1],hi[0],hi[1]),fill='#c8d4da',color='#263640',dash='-',lw=1.2)
# No cathedral mesh is transformed: existing precinct is compared in native source coordinates.
start=(-31.75*1000/1.3,(20.65-2.7584)*1000/1.3);route=LineString([start,(0,start[1]),(0,10901)]);inside=LineString([(0,10901),(0,9700)])
xs,ys=route.xy;ax.plot(xs,ys,'--',color='#b24539',lw=2.2);ax.plot(*inside.xy,':',color='#b24539',lw=2)
ax.scatter([0],[10901],c='#b24539',s=45,zorder=8);ax.annotate('PROPOSED PORTAL\nopening still uncut',(0,10901),xytext=(3300,16000),arrowprops={'arrowstyle':'->','color':'#a8443b'},fontsize=9,ha='center',color='#8d342c')
ax.annotate('Intended internal arrival:\ncentral rear arcade',(0,9700),xytext=(-6500,6000),arrowprops={'arrowstyle':'->'},fontsize=8,ha='center')
for x,y,t in [(-32500,23000,'CLOISTER'),(-13500,25000,'CHAPTER HOUSE'),(-20000,16800,'NIGHT LOBBY / STAIR'),(-26000,11500,'LONGER CONNECTING GALLERY'),(-28000,6400,'NAVE NORTH EDGE'),(-25800,8500,'N4 no longer fixed')]:ax.text(x,y,t,fontsize=8,ha='center',color='#38434b')
ax.set(xlim=(-43000,6500),ylim=(4000,35000),xlabel='Cathedral source X - project units',ylabel='Cathedral source north coordinate - project units');ax.set_aspect('equal');ax.grid(alpha=.12)
fig.suptitle('C01 | Cathedral-first connection proposal',fontsize=17,x=.06,ha='left')
text=[('Preferred candidate','North-transept central portal, using the recorded G40 jamb / ogive study and intended rear-arcade arrival.'),('Monastery consequence','A longer gallery from the cloister southeast corner. Its position leaves the gate hall unfixed. No new rooms or walls are modeled.'),('What the evidence proves','G40 portal clear span: 1200 source units between jambs. Framed outer width: 1968. Typical nave-root gaps in this reference: 1320.'),('What remains unresolved','The G40 portal is unapproved and uncut. Existing backing and the internal passage need a local opening / clearance study before adoption.'),('Registration limit','Cathedral geometry stays in its native coordinates. The precinct is shown through the inverse inherited X01 transform; physical scale and registration remain provisional.'),('Protection','No cathedral geometry, generators, room layout, stair or roofs changed. F5ZL-C remains unresolved.')]
y=.99
import textwrap
for title,body in text:
 notes.text(0,y,title,fontsize=10,weight='bold',va='top');y-=.035
 for line in textwrap.wrap(body,44):notes.text(0,y,line,fontsize=8.2,va='top');y-=.024
 y-=.022
fig.savefig('C01_CATHEDRAL_CONNECTION.png',dpi=150,facecolor='white');plt.close(fig)
ck={'id':'C01','status':'PROVISIONAL CONNECTION PROPOSAL; NOT AN APPROVED OPENING','preferred_threshold_native':[0,10901],'intended_internal_arrival_native':[0,9700],'external_route':mapping(route),'route_length_native_units':route.length,'portal_clear_width_source_units':1200,'framed_portal_outer_width_source_units':1968,'typical_nave_root_gap_source_units':1320,'source_G40':'/home/christopher/Desktop/Cathedral_F5ZP_G40_Working.blend','cathedral_geometry_changed':False,'registration':'Precinct-only inverse X01 transform; cathedral source geometry unscaled. Shared coordinate registration remains provisional.','hold':'Portal is an unapproved uncut G40 study; verify backing opening and internal route before adopting. Gate hall remains unfixed. F5ZL-C unresolved.'}
Path('C01_CONNECTION_CHECKPOINT.json').write_text(json.dumps(ck,indent=2)+'\n');print(json.dumps({'proposal_length_source_units':route.length,'geometry_changes':False}))
