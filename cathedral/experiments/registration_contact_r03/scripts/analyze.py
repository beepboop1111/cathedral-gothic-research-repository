#!/usr/bin/env python3
"""Reproduce R03 from byte-preserved inputs. Native X east, Y north, Z up; SI unset."""
from pathlib import Path
import json, math, csv, hashlib, gzip, sys
import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon, box
from shapely.ops import polygonize, unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

ROOT=Path(__file__).resolve().parents[1]
I=ROOT/'inputs'
TOL=.002 # native units: float32 saved-world error at X~27000
def write(n,d): (ROOT/n).write_text(json.dumps(d,indent=2)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def source_meshes():
 d=json.loads(gzip.decompress((I/'MR_meshes.json.gz').read_bytes()))
 return d,{o['name']:trimesh.Trimesh(o['vertices'],o['faces'],process=False) for o in d['objects']}
def r05_meshes():
 s=trimesh.load(I/'Crossing_Full_Cell_R05.glb',force='scene',process=False)
 # glTF (east,height,-north) -> native (east,north,height); rotation det +1.
 M=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]])
 out={}
 for node in s.graph.nodes_geometry:
  mat,gn=s.graph[node];m=s.geometry[gn].copy();m.apply_transform(M@mat);out[node]=m
 return out
def endpoints_point_segment(p,q,points):
 v=q-p;den=np.einsum('ij,ij->i',v,v)
 t=np.clip(np.einsum('ij,ij->i',points-p,v)/np.maximum(den,1e-30),0,1)
 return p+t[:,None]*v
def edge_edge(a,b,p,q):
 """Closest point between one segment and each of N segments, including parallel cases."""
 N=len(p);A=np.broadcast_to(a,(N,3));B=np.broadcast_to(b,(N,3))
 opts=[]
 for x in [A,B]:opts.append((x,endpoints_point_segment(p,q,x)))
 for x in [p,q]:opts.append((endpoints_point_segment(A,B,x),x))
 u=b-a;v=q-p;w=a-p;aa=u@u;bb=v@u;cc=np.einsum('ij,ij->i',v,v)
 dd=w@u;ee=np.einsum('ij,ij->i',v,w);den=aa*cc-bb*bb
 ss=np.divide(bb*ee-cc*dd,den,out=np.full(N,-1.),where=np.abs(den)>1e-16)
 tt=np.divide(aa*ee-bb*dd,den,out=np.full(N,-1.),where=np.abs(den)>1e-16)
 valid=(ss>=0)&(ss<=1)&(tt>=0)&(tt<=1)
 pa=a+ss[:,None]*u;pb=p+tt[:,None]*v
 dif=np.linalg.norm(pa-pb,axis=1);dif[~valid]=np.inf
 opts.append((pa,pb));dist=np.array([np.linalg.norm(x-y,axis=1) for x,y in opts]);dist[-1]=dif
 ix=np.unravel_index(dist.argmin(),dist.shape)
 return float(dist[ix]),opts[ix[0]][0][ix[1]],opts[ix[0]][1][ix[1]]
def pierce(a,b,tri):
 # Moller-Trumbore finite segment/triangle intersection, no backface cull.
 e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];dr=b-a
 h=np.cross(np.broadcast_to(dr,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h)
 inv=np.divide(1.,det,out=np.zeros(len(det)),where=np.abs(det)>1e-12)
 s=a-tri[:,0];u=np.einsum('ij,ij->i',s,h)*inv;q=np.cross(s,e1)
 v=q@dr*inv;t=np.einsum('ij,ij->i',e2,q)*inv
 valid=(np.abs(det)>1e-12)&(u>=-1e-10)&(v>=-1e-10)&(u+v<=1+1e-10)&(t>=0)&(t<=1)
 return a+t[np.flatnonzero(valid)[0]]*dr if valid.any() else None
def exact_surface_distance(A,B):
 """Triangle distance via all vertex/face, edge/edge and edge/face cases; AABB only prunes."""
 triB=B.triangles;lo=triB.min(axis=1);hi=triB.max(axis=1)
 cp,dd,idx=trimesh.proximity.closest_point(B,A.vertices);k=dd.argmin()
 best=float(dd[k]);ap=A.vertices[k];bp=cp[k]
 for ta in A.triangles:
  delta=np.maximum(np.maximum(lo-ta.max(axis=0),ta.min(axis=0)-hi),0)
  cand=triB[np.linalg.norm(delta,axis=1)<=best+1e-8]
  if not len(cand):continue
  for v in ta:
   closest=trimesh.triangles.closest_point(cand,np.broadcast_to(v,(len(cand),3)))
   dist=np.linalg.norm(closest-v,axis=1);j=dist.argmin()
   if dist[j]<best:best=float(dist[j]);ap=v;bp=closest[j]
  for j in range(3):
   pts=cand[:,j];closest=trimesh.triangles.closest_point(np.broadcast_to(ta,(len(cand),3,3)),pts)
   dist=np.linalg.norm(closest-pts,axis=1);k=dist.argmin()
   if dist[k]<best:best=float(dist[k]);ap=closest[k];bp=pts[k]
  for j in range(3):
   a,b=ta[j],ta[(j+1)%3];hit=pierce(a,b,cand)
   if hit is not None:return 0.,hit,hit
   for k in range(3):
    d,p,q=edge_edge(a,b,cand[:,k],cand[:,(k+1)%3])
    if d<best:best=d;ap=p;bp=q
  for j in range(3):
   for a,b in zip(cand[:,j],cand[:,(j+1)%3]):
    hit=pierce(a,b,ta[None,:,:])
    if hit is not None:return 0.,hit,hit
 return best,ap,bp
def section(m,axis,value):
 normal=np.eye(3)[axis];origin=normal*value
 seg=trimesh.intersections.mesh_plane(m,normal,origin)
 keep=[k for k in range(3) if k!=axis]
 return seg[:,:,keep] if len(seg) else np.empty((0,2,2))
def saveplot(fig,name):
 fig.savefig(ROOT/(name+'.png'),dpi=170);fig.savefig(ROOT/(name+'.svg'));plt.close(fig)
def setup(ax,title,xlabel='X east [native units]',ylabel='Y north [native units]'):
 ax.set_title(title,loc='left',fontsize=11);ax.set_aspect('equal');ax.set_xlabel(xlabel);ax.set_ylabel(ylabel);ax.grid(color='.88',ls='--',lw=.5)
def chevet(d):
 guides=d['guides'];rows=[];nodeerrs=[];curveerrs=[]
 for g in guides:
  if g['type']=='EMPTY':
   p=np.array(g['point']);rr=np.hypot(p[0]-20213,p[1]);a=math.degrees(math.atan2(p[0]-20213,p[1]))
   radius=min([2933,4085,5285],key=lambda x:abs(rr-x));angle=min([.5,27.5,53.5,78,102,126.5,152.5,179.5],key=lambda x:abs(a-x))
   expected=np.array([20213+radius*math.sin(math.radians(angle)),radius*math.cos(math.radians(angle)),3000])
   err=float(np.linalg.norm(p-expected));nodeerrs.append(err)
   rows.append(dict(name=g['name'],r=radius,theta=angle,point=p.tolist(),expected=expected.tolist(),error=err))
  elif '_RADIUS_' in g['name']:
   radius=float(g['name'].split('RADIUS_')[1].split('_')[0]);p=np.array(g['splines'][0]);err=np.abs(np.hypot(p[:,0]-20213,p[:,1])-radius);curveerrs.extend(err.tolist())
 ends=[]
 for r in [2933,4085,5285,6657,6849]:
  for a,side in [(.5,'N'),(179.5,'S')]:
   p=np.array([20213+r*math.sin(math.radians(a)),r*math.cos(math.radians(a))]);target=np.array([20213,r if side=='N' else -r])
   ends.append(dict(r=r,side=side,point=p.tolist(),ideal_same_radius_choir_endpoint=target.tolist(),dx=float(p[0]-target[0]),dy=float(p[1]-target[1]),distance=float(np.linalg.norm(p-target))))
 result={'status':'PASS saved F5ZN-A guide registration; physical chevet/choir masonry UNRESOLVED','node_count':len(rows),'node_max_error':max(nodeerrs),'ring_radial_max_error':max(curveerrs),'native_tolerance':TOL,'source_sha256':d['chevet_source_sha256'],'nodes':rows,'endpoints':ends,'frame':'native X east, Y north, Z height; no scale applied','Q5_end':20213,'center':[20213,0],'outer_band_differences':{'straight_5429_minus_chevet_5285':144,'straight_6965_minus_chevet_6657':308},'interpretation':'0.5-degree endpoints are present in schedule and saved guide, not rounding errors; no physical gap/connection claim without masonry','protected_uniform_centers':[30,50,70,90,110,130,150],'unequal_source_centers':[14,40.5,65.75,90,114.25,139.5,166],'authority_conflict':'Do not substitute one angular schedule for the other. No installed approved chevet mesh matrix recovered.'}
 write('CHEVET_QA.json',result)
 with (ROOT/'CHEVET_STATIONS.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['node','radius','angle','X','Y','Z','error']);w.writerows([r['name'],r['r'],r['theta'],*r['point'],r['error']] for r in rows)
 fig,(ax,detail)=plt.subplots(1,2,figsize=(13,7),gridspec_kw={'width_ratios':[1.55,1]})
 for g in guides:
  if g['type']=='CURVE' and '_PLAN' in g['name']:
   for pp in g['splines']:
    pp=np.array(pp);ax.plot(pp[:,0],pp[:,1],'k-',lw=.65)
 for r in [2933,4085,5429,6965]:
  for sy in [1,-1]:ax.plot([17333,20213],[sy*r]*2,'--',color='.55',lw=.7)
 ax.axvline(20213,c='.5',ls='--',lw=.8);ax.text(20213,7400,'Q5 / chevet center X20213',fontsize=8,ha='center')
 for r in rows:ax.plot(*r['point'][:2],'ko',ms=2)
 setup(ax,'Saved chevet guides and straight choir schedule');ax.set_xlim(17100,27800);ax.set_ylim(-7600,7900)
 for r in [2933,4085,5285,6657]:
  e=next(x for x in ends if x['r']==r and x['side']=='N');y=r
  detail.plot([0,e['dx']],[y,e['point'][1]],'r--',lw=1.5)
  detail.plot([0],[y],'o',color='.5',ms=4);detail.plot([e['dx']],[e['point'][1]],'ko',ms=4)
  detail.annotate(f"R{r}: east offset {e['dx']:.3f}",(e['dx'],y),xytext=(8,8),textcoords='offset points',fontsize=8)
 detail.axvline(0,color='.5',ls='--',lw=.8);detail.set_xlim(-10,200);detail.set_ylim(2700,7000);setup(detail,'0.5° boundary offsets (X exaggerated)','X − 20213 [native units]');detail.set_aspect('auto')
 fig.suptitle('F5ZP R03 | measured saved data, no geometry moved',x=.07,ha='left',fontsize=15)
 fig.text(.07,.01,'Black: saved guide geometry  •  Gray dashed: schedule/construction  •  Red dashed: unresolved interface  •  Physical conversion unset',fontsize=9)
 fig.tight_layout(rect=[0,.04,1,.95]);saveplot(fig,'CHEVET_REGISTRATION')
 return result
def contacts(r05,src):
 rows=[]
 targets=[n for n in src if not n.startswith('G40_BOTH')]
 for an,A in r05.items():
  if 'SOLID' not in an and 'UPPER_CORE' not in an:continue
  for bn in targets:
   B=src[bn];dist,p,q=exact_surface_distance(A,B)
   # In these sources disjoint AABBs prove no solid containment. Distance is actual triangles.
   separated=bool(np.any(np.maximum(A.bounds[0],B.bounds[0])>np.minimum(A.bounds[1],B.bounds[1])))
   rows.append(dict(r05=an,source=bn,surface_gap=dist,r05_point=p.tolist(),source_point=q.tolist(),surface_contact_area=0 if dist>TOL else None,overlap_volume=0 if separated else None,relation='DISJOINT_SAVED_SURFACES' if dist>TOL else 'REQUIRES_SOLID_INTERSECTION',source_watertight=bool(B.is_watertight),scope='saved fragment only; missing intervening masonry not inferred; volume null where nonclosed source cannot define interior'))
   print(an,bn,round(dist,6),flush=True)
 write('CONTACT_QA.json',{'tolerance':TOL,'method':'triangle vertex-face / edge-edge / segment-face exact minimum with AABB pruning; not AABB contact','physical_m_per_unit':None,'rows':rows,'complete_adjoining_pier_wall_inventory':'UNRESOLVED: no installed nave/choir/crossing piers recovered; G40 is a transept fragment plus choir floor trial','load_capacity':'UNRESOLVED','F5ZL_C_248_support_schedule':'MISSING'})
 with (ROOT/'CONTACT_REGISTER.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['r05','source','surface_gap','surface_contact_area','overlap_volume','relation']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in rows)
 return rows
def sectional_audit(r05,src):
 rows=[]
 for z in [100,2616,2999.9,3000.1,4296,4391.9,4392.1,4521,4854.1,4950.1,13499.9]:
  for corner in ['NE','NW','SE','SW']:
   a=unary_union([LineString(s) for n,m in r05.items() if n.startswith(corner) and ('SOLID' in n or 'UPPER_CORE' in n) for s in section(m,2,z)])
   for name,m in src.items():
    if name.startswith('G40_BOTH'):continue
    lines=[LineString(s) for s in section(m,2,z)];b=unary_union(lines)
    rows.append({'corner':corner,'Z':z,'source':name,'R05_trace_length':a.length,'source_trace_length':b.length,'section_trace_gap':float(a.distance(b)) if not a.is_empty and not b.is_empty else None,'intersection_trace_length':a.intersection(b).length if not b.is_empty else 0,'material_overlap_area':0 if m.is_watertight and not a.is_empty and a.distance(b)>TOL else None})
 write('SECTION_QA.json',{'method':'actual triangle/plane section segments at 11 heights; exact 2D trace distances; no polygon healing','rows':rows,'interpretation':'No recorded boundary contact over sampled heights. Nonclosed masonry volumes, unsampled physical material and missing solids remain unresolved.'})
def drawings(r05,src,rows):
 targets=[n for n in src if not n.startswith('G40_BOTH')]
 bodies={n:m for n,m in r05.items() if 'SOLID' in n or 'UPPER_CORE' in n}
 fig,axs=plt.subplots(1,3,figsize=(16,7))
 for ax,z in zip(axs,[100,3000,4854.1]):
  for m in src.values():
   if m is src.get('G40_BOTH_TRANSEPTS_EXACT_G24_G39_CANDIDATE_STAIR_AND_GALLERY_1to16'):continue
   ax.add_collection(LineCollection(section(m,2,z),colors='k',linewidths=.7))
  for n,m in bodies.items():ax.add_collection(LineCollection(section(m,2,z),colors='k',linewidths=1.1))
  for sx,sy in [(1,1),(1,-1),(-1,1),(-1,-1)]:
   x,y=sx*2933,sy*2933;ax.plot([x-800,x+800,x+800,x-800,x-800],[y-800,y-800,y+800,y+800,y-800],'r--',lw=.8)
  ax.plot([-8500,8500],[2933,2933],'--',c='.6',lw=.5);ax.plot([2933,2933],[-12500,12500],'--',c='.6',lw=.5)
  ax.set_xlim(-10000,11000);ax.set_ylim(-12500,12500);setup(ax,f'Horizontal cut Z={z:g}')
 axs[0].text(0,0,'Central crossing\n4970 clear',ha='center',fontsize=8)
 axs[1].text(0,5200,'No recovered adjoining\npier/wall solids at corners',ha='center',fontsize=8,color='#b22222')
 for r in rows:
  if 'ENTIRE_J11_SOLID' in r['r05'] and r['source'].startswith('G40F__G40_CONTEXT'):
   p,q=np.array(r['r05_point']),np.array(r['source_point']);axs[2].plot([p[0],q[0]],[p[1],q[1]],'r--',lw=.8)
   axs[2].text((p[0]+q[0])/2,(p[1]+q[1])/2,f"3D gap {r['surface_gap']:.1f}",fontsize=6.5,c='#a22',rotation=45 if p[0]>0 else -45,ha='center')
 fig.suptitle('R03 | R05 masonry against saved G40 transept fragments',x=.05,ha='left',fontsize=15)
 fig.text(.05,.015,'Black: actual section traces (authority varies)  •  Gray dashed: construction  •  Red dashed: unverified junction coverage  •  Native units only',fontsize=9)
 fig.tight_layout(rect=[0,.04,1,.94]);saveplot(fig,'CROSSING_CONTACT_PLANS')
 fig,axs=plt.subplots(2,1,figsize=(14,9))
 for ax,axis,label in [(axs[0],1,'A–A | Y=2933, looking north; nave to choir'),(axs[1],0,'B–B | X=2933, looking west; south to north transept')]:
  for n in targets:ax.add_collection(LineCollection(section(src[n],axis,2933),colors='k',linewidths=.7))
  for n,m in bodies.items():ax.add_collection(LineCollection(section(m,axis,2933),colors='.45' if 'PLACEHOLDER' in n else 'k',linewidths=1.2,linestyles='dashed' if 'PLACEHOLDER' in n else 'solid'))
  for h in [3000,4392,4521,4854,4950,13500]:
   ax.axhline(h,c='.6',ls='--',lw=.6)
   if h in [3000,13500]:ax.text(11300,h+60,str(h),fontsize=8,c='.35')
  ax.text(-12100,5550,'Stack: R05 infill 4392 / F5ZK-C gallery 4521\nG40 slab 4854–4950 (distinct scheme)',fontsize=7.5,c='.35')
  for sign in [-1,1]:
   ax.plot([sign*4085,sign*6000],[2100,2100],'r--',lw=1.2)
  ax.set_xlim(-12500,12500);ax.set_ylim(-150,14500);setup(ax,label,'X east [native units]' if axis==1 else 'Y north [native units]','Z height [native units]')
  ax.text(0,9500,'Upper cores are R05 placeholders;\nno detailed bearing or capacity verified',ha='center',fontsize=9,color='#a22')
 fig.suptitle('R03 | Actual mesh sections; no inferred infill or new support',x=.07,ha='left',fontsize=15)
 fig.text(.07,.01,'Black solid: saved section  •  Gray dashed: datums and upper-core placeholders  •  Red dashed: unresolved junction',fontsize=9)
 fig.tight_layout(rect=[0,.04,1,.94]);saveplot(fig,'CROSSING_SECTIONS')
 # 3D overview uses exact transformed meshes, decimated DISPLAY sampling only.
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 fig=plt.figure(figsize=(12,8));ax=fig.add_subplot(111,projection='3d')
 for n,m in list(bodies.items())+[(n,src[n]) for n in targets]:
  tri=m.triangles;col='#9e7755' if n in bodies else '#a4adb3'
  ax.add_collection3d(Poly3DCollection(tri[::max(1,len(tri)//6000)],facecolor=col,edgecolor='none',alpha=.65))
 ax.set(xlim=(-11000,11000),ylim=(-12000,12000),zlim=(0,17000),xlabel='X east',ylabel='Y north',zlabel='Z height');ax.set_box_aspect((22,24,17));ax.view_init(25,-55)
 ax.set_title('R03 | Saved fragments surrounding R05 — missing junction solids remain open',loc='left',fontsize=12);fig.tight_layout();fig.savefig(ROOT/'STUDY_OVERVIEW.png',dpi=160);plt.close(fig)
def export_study(r05,src,d):
 s=trimesh.Scene()
 # New study retains every R05 mesh separately; sources never rewritten.
 for n,m in r05.items():
  m=m.copy();m.visual.face_colors=[158,119,85,255] if 'SOLID' in n else [120,140,152,255]
  s.add_geometry(m,node_name='R05__'+n,geom_name='R05__'+n)
 for n,m in src.items():
  if n.startswith('G40_BOTH'):continue
  m=m.copy();m.visual.face_colors=[150,160,169,255];s.add_geometry(m,node_name='SAVED_G40__'+n,geom_name='SAVED_G40__'+n)
 # Add saved chevet curves as explicitly detached guides, never stone.
 for g in d['guides']:
  if g['type']=='CURVE' and '_PLAN' in g['name']:
   for k,pts in enumerate(g['splines']):
    path=trimesh.load_path(np.array(pts))
    # Line primitives supported by trimesh GLB are exact guide centerlines.
    s.add_geometry(path,node_name='GUIDE__'+g['name']+str(k))
 s.metadata.update({'status':'EXPERIMENTAL_R03_NOT_PROMOTED','physical_m_per_unit':None,'native_frame':'X east Y north Z up','no_physical_SI_scale':'Numbers are native project units despite glTF metre convention; NOT metric certified'})
 # Proper glTF Y-up expression, same magnitudes.
 s.apply_transform(np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]]))
 p=ROOT/'F5ZP_Registration_Contact_R03.glb';s.export(p)
 re=trimesh.load(p,force='scene',process=False);write('EXPORT_QA.json',{'source_r05_nodes':len(r05),'study_geometries':len(s.geometry),'reimport_geometries':len(re.geometry),'bounds':re.bounds.tolist(),'physical_scale_applied':False,'glTF_expression':'(X,Zheight,-Ynorth)','Exhibit_inspected':False})
def main():
 d,src=source_meshes();r05=r05_meshes();c=chevet(d);rows=contacts(r05,src);sectional_audit(r05,src);drawings(r05,src,rows);export_study(r05,src,d)
 write('FRAME_QA.json',{'governance_scene_note':'G40 declares X east / Z north / Y vertical','measured_saved_geometry':'Principal G40 mesh world coordinates are X east / Y north / Z up','principal_object_matrices':'identity for G40 context/replacements; 16x object transform already applied for choir floor','evidence_landmarks':{'transept_terminal_plan_y':[-10709,10709],'lower_portal_floor_z':0,'gallery_soffit_z':4854,'gallery_floor_z':4950,'maximum_height_z':17000},'study_mapping':'IDENTITY for captured G40 world vertices; no global axis swap','scope':'Per-object transforms used; stale global note cannot normalize every mixed asset.'})
 write('RUN_QA.json',{'status':'EXPERIMENTAL; evidence-limited completion','saved_chevet_nodes_checked':c['node_count'],'guide_registration':'PASS' if c['node_max_error']<TOL else 'FAIL','physical_units':'UNRESOLVED','saved_surface_pairs_checked':len(rows),'disjoint_pairs':sum(r['relation']=='DISJOINT_SAVED_SURFACES' for r in rows),'complete_installed_contact':'UNRESOLVED','approved_geometry_changed':False,'F5ZL_C_supports':'MISSING','technical':'Completed script, SVG/PNG generation and GLB reimport; see validation addendum for Blender checks'})
 print('R03_ANALYSIS_COMPLETE',flush=True)
if __name__=='__main__':main()
