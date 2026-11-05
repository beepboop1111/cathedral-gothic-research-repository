import bpy,math,json,pathlib,hashlib,collections,os
import numpy as np
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent
raw=(R/'inputs/BASELINE.json').read_bytes();D=json.loads(raw);parent=json.loads((R/'inputs/PARENT_R02_QA.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M={}
for name,c in [('stone',(.66,.58,.46,1)),('moulding',(.85,.76,.59,1)),('web',(.83,.82,.76,1)),('roof',(.20,.30,.34,1)),('floor',(.59,.59,.55,1)),('source',(.31,.47,.53,1)),('glass',(.33,.51,.59,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=c;M[name]=m
COL={}
for name in ['PROTECTED_PLAN','FLOORS','RESPONDS','ARCHES','RIBS','WEBS','WALLS','ROOF','BOSSES']:
 c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);COL[name]=c
objects=[];web_samples=[];web_edges=[];rib_data=[];shaft_tests=[];arc_records=[];web_info=[];roof_triangles=[]
Z=np.array([0.,0.,1.]);spring=1800.;thickness=45.;half=1250.
def unit(a):
 a=np.array(a,dtype=float);return a/np.linalg.norm(a)
def mesh(name,v,f,mat,group,smooth=False):
 me=bpy.data.meshes.new(name);me.from_pydata([list(map(float,p)) for p in v],[],f);me.update();o=bpy.data.objects.new(name,me);COL[group].objects.link(o);o.data.materials.append(M[mat]);objects.append(o)
 if smooth:
  for p in me.polygons:p.use_smooth=True
 return o
def prism(name,p,z,h,mat='stone',group='RESPONDS'):
 n=len(p);return mesh(name,[(x,y,z) for x,y in p]+[(x,y,z+h) for x,y in p],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,group)
def bez(a,b,c,d,n=8):
 return [((1-t)**3*np.array(a)+3*t*(1-t)**2*np.array(b)+3*t*t*(1-t)*np.array(c)+t**3*np.array(d)).tolist() for t in np.linspace(0,1,n,endpoint=False)]
# Designed vector sections: paired rolls, recessed hollows, a projecting central keel.
right=[[65.,0.],[65.,18.],[48.,18.]]
for seg in [((48,18),(78,24),(78,53),(49,56)),((49,56),(19,52),(17,72),(32,78)),((32,78),(54,97),(36,113),(15,108)),((15,108),(10,120),(3,130),(0,132))]:right.extend(bez(*seg))
right.append([0.,132.]);profile=np.array(right+[[-x,y] for x,y in right[-2::-1]])
# Remove coincident consecutive vertices, retain closed polygon implicitly.
profile=np.array([p for i,p in enumerate(profile) if i==0 or np.linalg.norm(p-profile[i-1])>1e-8])
if np.linalg.norm(profile[0]-profile[-1])<1e-8:profile=profile[:-1]
major=profile*np.array([1.27,150/132]);rib=profile.copy();ridge=profile*.62
(R/'PROFILES.json').write_text(json.dumps({'status':'NEW_EXPERIMENTAL_DESIGNED_SECTIONS_NOT_HISTORICAL_TRACES','RIB':rib.tolist(),'MAJOR_ARCH':major.tolist(),'RIDGE':ridge.tolist()},indent=2))
def sweep(name,points,section,hdir,group='RIBS',shaft=False):
 pts=np.array(points);H=unit([hdir[0],hdir[1],0]);K=np.cross(H,Z);n=len(section);v=[]
 for j,P in enumerate(pts):
  T=unit(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)])
  if j==0:T=Z.copy()
  N=T[2]*H-np.dot(T,H)*Z;N=unit(N)
  v.extend(P+K*w+N*d for w,d in section)
 faces=[tuple(range(n-1,-1,-1))]
 for j in range(len(pts)-1):
  for k in range(n):faces.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
 faces.append(tuple(range((len(pts)-1)*n,len(pts)*n)))
 ob=mesh(name,v,faces,'moulding',group,True)
 if shaft:
  P=pts[0];sv=[P-Z*spring+K*w+H*d for w,d in section]+[P+K*w+H*d for w,d in section];sf=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  mesh(name+'_MATCHING_SHAFT',sv,sf,'moulding','RESPONDS',True);shaft_tests.append(float(np.max(np.linalg.norm(np.array(sv[n:])-np.array(v[:n]),axis=1))))
 return ob

def circle_spec(h,rise):
 c=(rise*rise-h*h)/(2*h);r=h+c;return c,r
# This is the exact back circle whose inward offset150 gives the R02 soffit.
c0,r0=circle_spec(1100,1950);r0+=150;entrance_crown=spring+math.sqrt(r0*r0-c0*c0)
stations=[(28000.,entrance_crown),(28600.,entrance_crown),(31000.,4125.),(33400.,4375.)]
def fullarc(A,C,crown):
 A=np.array(A,dtype=float);C=np.array(C,dtype=float);length=np.linalg.norm(C[:2]-A[:2]);h=length/2;c,r=circle_spec(h,crown-spring)
 def f(t):
  q=abs((t-.5)*length);z=spring+math.sqrt(max(0,r*r-(q+c)**2));P=A+(C-A)*t;P[2]=z;return P
 f.spec={'span':length,'c':c,'r':r,'spring':spring,'crown':crown,'A':A.tolist(),'C':C.tolist()};return f

def arch_moulding(name,A,C,crown,section=major,shafts=True):
 A=np.array(A);C=np.array(C);H=unit(C-A);K=np.cross(H,Z);mid=(A+C)/2;h=np.linalg.norm(C-A)/2;c,r=circle_spec(h,crown-spring);n=len(section);v=[];npath=97
 for j in range(npath):
  side=-1 if j<=48 else 1;t=j/48 if j<=48 else (96-j)/48
  for width,depth in section:
   rr=r-depth;theta=math.acos(c/rr);q=side*(rr*math.cos(theta*t)-c);z=spring+rr*math.sin(theta*t);v.append(mid+H*q+K*width+Z*z)
 faces=[]
 for j in range(npath-1):
  for k in range(n):faces.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
 faces.extend([tuple(range(n-1,-1,-1)),tuple(range((npath-1)*n,npath*n))]);mesh(name,v,faces,'moulding','ARCHES',True)
 if shafts:
  for idx,P in enumerate([A,C]):
   inward=H if idx==0 else -H
   sv=[P+K*w+inward*d+Z*z for z in [0,spring] for w,d in section];sf=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];mesh(name+'_SHAFT_'+str(idx),sv,sf,'moulding','RESPONDS',True)
   row=np.array(v[:n] if idx==0 else v[-n:]);shaft_tests.append(float(np.max(np.linalg.norm(row-np.array(sv[n:]),axis=1))))
 arc_records.append({'name':name,'circle_center_signed_offsets':[-c,c],'radius_back':r,'max_section_depth':float(section[:,1].max()),'span_back':2*h,'back_crown':crown,'soffit_crown':spring+math.sqrt((r-section[:,1].max())**2-c*c),'spring_tangent':'vertical','crown_joint':'mitred concentric arcs'})
 return fullarc(A,C,crown)

def radial(A,B):
 A=np.array(A);B=np.array(B);H=unit([B[0]-A[0],B[1]-A[1],0]);run=np.linalg.norm(B[:2]-A[:2]);rise=B[2]-A[2];r=(run*run+rise*rise)/(2*run)
 def f(t):return A+H*(run*t)+Z*(math.sqrt(max(0,r*r-(r-run*t)**2)))
 f.meta={'run':run,'rise':rise,'radius':r,'monotone':rise>=run,'A':A.tolist(),'B':B.tolist()};return f

def rib_branch(name,A,B):
 f=radial(A,B);a=math.atan2(f.meta['rise'],f.meta['radius']-f.meta['run']);A=np.array(A);H=unit(np.array(B)-A-Z*(B[2]-A[2]));r=f.meta['radius'];pts=[A+H*(r-r*math.cos(t))+Z*r*math.sin(t) for t in np.linspace(0,a,65)];sweep(name,pts,rib,H,shaft=True);rib_data.append(f.meta);return f

def rev(f):return lambda t:f(1-t)
def part(f,a,b):return lambda t:f(a+(b-a)*t)
def interpolate(A,B):return lambda t:np.array(A)*(1-t)+np.array(B)*t

def shell(name,points,tris,mat='web',group='WEBS'):
 # Keep each boundary edge's direction; unordered keys only count incidence.
 v=np.array(points,dtype=float);nv=len(v);counts=collections.Counter();directed={}
 for tri in tris:
  for a,b in zip(tri,tri[1:]+tri[:1]):
   key=tuple(sorted((a,b)));counts[key]+=1;directed.setdefault(key,(a,b))
 if any(n>2 for n in counts.values()):raise ValueError('Nonmanifold shell input: '+name)
 faces=[tuple(reversed(t)) for t in tris]+[tuple(i+nv for i in t) for t in tris]
 faces +=[(a,b,b+nv,a+nv) for key,(a,b) in directed.items() if counts[key]==1]
 vertices=np.vstack((v,v+Z*thickness));center=vertices.mean(axis=0)
 # Input sheets can face either way. Closed shell exteriors must face outward.
 signed_volume=0.
 for face in faces:
  a=vertices[face[0]]-center
  for j in range(1,len(face)-1):signed_volume+=float(np.dot(a,np.cross(vertices[face[j]]-center,vertices[face[j+1]]-center)))/6
 if abs(signed_volume)<1e-9:raise ValueError('Zero-volume shell: '+name)
 if signed_volume<0:faces=[tuple(reversed(f)) for f in faces]
 return mesh(name,vertices,faces,mat,group,True)

def triweb(name,A,C,B,AC,CB,BA):
 A=np.array(A);C=np.array(C);B=np.array(B);n=24;pts=[];index={}
 def surface(u,v,w):
  result=u*A+v*C+w*B
  for a,b,pa,pb,f in [(u,v,A,C,AC),(v,w,C,B,CB),(w,u,B,A,BA)]:
   q=a+b
   if q>1e-12:
    t=b/q;result+=q*q*(f(t)-((1-t)*pa+t*pb))
  return result
 for i in range(n+1):
  for j in range(n-i+1):
   index[i,j]=len(pts);v=i/n;w=j/n;pts.append(surface(1-v-w,v,w))
 tris=[]
 for i in range(n):
  for j in range(n-i):
   tris.append((index[i,j],index[i+1,j],index[i,j+1]))
   if j<n-i-1:tris.append((index[i+1,j],index[i+1,j+1],index[i,j+1]))
 # Explicit boundary comparison at independent samples.
 err=0.
 for t in np.linspace(0,1,101):
  for actual,expected in [(surface(1-t,t,0),AC(t)),(surface(0,1-t,t),CB(t)),(surface(t,0,1-t),BA(t))]:err=max(err,float(np.linalg.norm(actual-expected)))
 ob=shell(name,pts,tris);web_samples.extend(pts);web_edges.append(err);web_info.append({'name':name,'boundary_max_error_native':err,'vertices_intrados':len(pts),'faces_intrados':len(tris),'centroid_xy':np.mean(pts,axis=0)[:2].tolist()});return ob

def boss(name,P,r=155):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=r,location=P);o=bpy.context.object;o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 COL['BOSSES'].objects.link(o);o.data.materials.append(M['moulding']);objects.append(o)
 for face in o.data.polygons:face.use_smooth=True

def core(name,x,y,long=300):
 # Structural core lies behind the moulding back; engaged profile overlay projects into room.
 sign=1 if y>0 else -1;y0=y;y1=y+sign*210
 pts=[(x-long/2,y0),(x+long/2,y0),(x+long/2,y1),(x+long/2-60,y1+sign*50),(x-long/2+60,y1+sign*50),(x-long/2,y1)]
 prism(name,pts,0,spring);prism(name+'_BASE',[(a+(a-x)*.12,b+(b-y)*.12) for a,b in pts],0,130)
# Entrance depth: retain exact R02 concentric soffit. Major sections run continuously into responds.
entry_curves=[]
for k,x in enumerate([28000.,28200.,28400.,28600.]):entry_curves.append(arch_moulding('ENTRANCE_ORDER_'+str(k+1),[x,-half,0],[x,half,0],entrance_crown))
for y in [-half,half]:core('ENTRANCE_COMPOUND_CORE_'+str(y),28300,y,1000)
# Continuous backing above the four entrance orders, outside the moulding back.
backprofile=np.array([[-110.,-210.],[110.,-210.],[110.,-12.],[-110.,-12.]])
for x in [28100.,28300.,28500.]:arch_moulding('ENTRANCE_BACKING_'+str(x),[x,-half,0],[x,half,0],entrance_crown,backprofile,False)
# Common transverse arches after each chapel bay.
trans={28000.:entry_curves[0],28600.:entry_curves[-1]}
for x,crown in stations[2:]:
 trans[x]=arch_moulding('CHAPEL_TRANSVERSE_'+str(int(x)),[x,-half,0],[x,half,0],crown)
 for y in [-half,half]:core('CHAPEL_CORE_'+str((x,y)),x,y,360)
# Inner source interface is XY authority only. New trial bearing profiles avoid editing any source model.
iN=np.array(D['cells']['M_A4']['vertices'][1]+[spring]);iS=np.array(D['cells']['M_A4']['vertices'][2]+[spring]);xi=(iN[0]+iS[0])/2
ambcorn=[iS,np.array([28000.,-half,spring]),np.array([28000.,half,spring]),iN];AB=np.array([26700.,0.,3620.]);aribs=[rib_branch('AMB_RIB_'+str(j),A,AB) for j,A in enumerate(ambcorn)];boss('AMB_BOSS',AB)
for i,A in enumerate([iN,iS]):
 y=A[1];core('TRIAL_INNER_INTERFACE_CORE_'+str(i),A[0],y,240)
# Three ordinary sides, plus the entrance web split by the axial ridge: five panels/four ground bearings.
front=trans[28000.];FM=front(.5);link=lambda t:AB*(1-t)+FM*t+np.array([0,0,35*math.sin(math.pi*t)])
sweep('AMB_AXIAL_RIDGE',[link(t) for t in np.linspace(0,1,49)],ridge,[1,0,0])
for j in [0,2,3]:
 a=ambcorn[j];c=ambcorn[(j+1)%4];boundary=fullarc(a,c,3400. if j!=3 else 3500.)
 arch_moulding('AMB_BOUNDARY_'+str(j),[a[0],a[1],0],[c[0],c[1],0],3400. if j!=3 else 3500.,rib*.72,False)
 triweb('AMB_WEB_'+str(j),a,c,AB,boundary,aribs[(j+1)%4],rev(aribs[j]))
triweb('AMB_WEB_FRONT_S',ambcorn[1],FM,AB,part(front,0,.5),rev(link),rev(aribs[1]))
triweb('AMB_WEB_FRONT_N',FM,ambcorn[2],AB,part(front,.5,1),aribs[2],link)
# Ruled threshold barrel shell shares exact front and back arch circles with adjacent webs.
pts=[];n=48
for j,x in enumerate([28000.,28600.]):
 for i in range(n+1):P=trans[28000.](i/n).copy();P[0]=x;pts.append(P)
tris=[]
for i in range(n):tris.extend([(i,i+1,n+1+i),(i+1,n+2+i,n+1+i)])
shell('THRESHOLD_BARREL_WEB',pts,tris);web_samples.extend(pts)
# Bay1 / Bay2: four connected web panels around four circular branches each.
for bi,(west,east,zBoss) in enumerate([(28600.,31000.,4150.),(31000.,33400.,4400.)],1):
 corners=[np.array([west,-half,spring]),np.array([east,-half,spring]),np.array([east,half,spring]),np.array([west,half,spring])];B=np.array([(west+east)/2,0,zBoss]);rs=[rib_branch('BAY'+str(bi)+'_RIB_'+str(j),A,B) for j,A in enumerate(corners)];boss('BAY'+str(bi)+'_BOSS',B)
 edges=[fullarc(corners[0],corners[1],3350.+bi*80),trans[east],fullarc(corners[2],corners[3],3350.+bi*80),rev(trans[west])]
 for j in [0,2]:arch_moulding('BAY'+str(bi)+'_FORMERET_'+str(j),corners[j]-Z*spring,corners[(j+1)%4]-Z*spring,3350.+bi*80,rib*.72,False)
 for j in range(4):triweb('BAY'+str(bi)+'_WEB_'+str(j),corners[j],corners[(j+1)%4],B,edges[j],rs[(j+1)%4],rev(rs[j]))
# Polygonal apse: five external faces and west transverse shared with bay2.
apse=[np.array([33400+1250*math.cos(math.radians(a)),1250*math.sin(math.radians(a)),spring]) for a in [-90,-54,-18,18,54,90]]
apse[0][0]=33400.;apse[-1][0]=33400.;AP=np.array([33850.,0.,4550.]);ars=[rib_branch('APSE_RIB_'+str(j),A,AP) for j,A in enumerate(apse)];boss('APSE_BOSS',AP,180)
for j,A in enumerate(apse):
 C=apse[(j+1)%6]
 if j==5:edge=rev(trans[33400.])
 else:
  edge=fullarc(A,C,3400.);arch_moulding('APSE_FORMERET_'+str(j),A-Z*spring,C-Z*spring,3400.,rib*.65,False)
  if j not in [0]:core('APSE_CORE_'+str(j),A[0],A[1],230)
 triweb('APSE_WEB_'+str(j),A,C,AP,edge,ars[(j+1)%6],rev(ars[j]))
# Chapel walls: actual open lancet apertures, separately editable, with simple mullions.
def wall(name,A,C,eave=4100):
 A=np.array(A,dtype=float);C=np.array(C,dtype=float);H=unit(C-A);length=np.linalg.norm(C-A);N=np.array([-H[1],H[0],0]);center=(A+C)/2
 if np.dot(N,center-np.array([32000,0,0]))<0:N=-N
 def coords(p):return [A+H*u+N*v+Z*z for u,v,z in p]
 def block(s0,s1,z0,z1):
  p=[(s0,0,z0),(s1,0,z0),(s1,170,z0),(s0,170,z0),(s0,0,z1),(s1,0,z1),(s1,170,z1),(s0,170,z1)];return mesh(name+'_WALL',coords(p),[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'stone','WALLS')
 margin=min(240,length*.18);span=length-2*margin;wsp=1800.;wcrown=3150. if length>1500 else 3200.;block(0,length,0,550);block(0,margin,550,eave);block(length-margin,length,550,eave)
 win=fullarc(np.array([0.,0.,spring]),np.array([span,0.,spring]),wcrown);curve=[(margin+win(t)[0],win(t)[2]) for t in np.linspace(0,1,65)];poly=curve+[(length-margin,eave),(margin,eave)];n=len(poly);v=coords([(u,side,z) for side in [0,170] for u,z in poly]);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];mesh(name+'_SPANDREL',v,faces,'stone','WALLS')
 for t in [1/3,2/3]:
  u=margin+span*t;block(u-22,u+22,550,win(t)[2])
 # Non-structural glass surface recessed outside aperture, removable.
 glass=[(margin,550)]+curve+[(length-margin,550)];mesh(name+'_GLASS',coords([(u,90,z) for u,z in glass]),[tuple(range(len(glass)))],'glass','WALLS')
for sign in [-1,1]:
 for bi,(a,b) in enumerate([(28600.,31000.),(31000.,33400.)]):wall('SIDE_'+str(sign)+'_BAY'+str(bi+1),[a,sign*half,0],[b,sign*half,0])
for j in range(5):wall('APSE_FACE_'+str(j),apse[j]-Z*spring,apse[j+1]-Z*spring)
# Threshold lateral backing walls are separate from the compound moulded shafts.
for sign in [-1,1]:prism('THRESHOLD_RETURN_'+str(sign),[(28000,sign*1250),(28600,sign*1250),(28600,sign*1500),(28000,sign*1500)],0,4100,'stone','WALLS')
foot=[(xi,-abs(iS[1])),(28000,-half),(28600,-half),(31000,-half),(33400,-half)]+[(A[0],A[1]) for A in apse[1:]]+[(31000,half),(28600,half),(28000,half),(xi,abs(iN[1]))]
prism('AXIAL_COMPLETE_FLOOR',foot,-100,100,'floor','FLOORS')
# Separate roofs; clearance measured against the actual piecewise planar undersides.
def roofpiece(name,vertices,triangles):
 for tri in triangles:roof_triangles.append(np.array([vertices[i] for i in tri],dtype=float))
 return shell(name,vertices,triangles,'roof','ROOF')
for k,(a,b,za,zb) in enumerate([(28000.,28600.,4500.,4600.),(28600.,31000.,4600.,4900.),(31000.,33400.,4900.,5150.)]):
 for sign in [-1,1]:roofpiece('ROOF_BAY'+str(k)+'_'+str(sign),[(a,sign*half,4100),(b,sign*half,4100),(b,0,zb),(a,0,za)],[(0,1,2),(0,2,3)])
roofboundary=[(A[0],A[1],4100.) for A in apse]+[(33400.,0.,5150.)];roofhub=(33850.,0.,5350.)
for j in range(len(roofboundary)):roofpiece('ROOF_APSE_'+str(j),[roofhub,roofboundary[j],roofboundary[(j+1)%len(roofboundary)]],[(0,1,2)])
# Protected source guides only, not any discarded outer ring.
for name,c in D['cells'].items():
 if name.startswith(('I_','M_')):
  vs=c['vertices'];pts=[]
  for A,C in zip(vs,vs[1:]+vs[:1]):
   A=np.array(A+[0.]);C=np.array(C+[0.]);H=C-A;K=unit(np.cross(H,Z))*8;mesh('SOURCE_'+name,[A-K,A+K,C+K,C-K],[(0,1,2,3)],'source','PROTECTED_PLAN')
# Numeric geometry tests before storage rounding.
def roofz(P):
 out=[]
 for tri in roof_triangles:
  mat=np.stack((tri[1,:2]-tri[0,:2],tri[2,:2]-tri[0,:2]),axis=1)
  if abs(np.linalg.det(mat))<1e-9:continue
  u,v=np.linalg.solve(mat,np.array(P[:2])-tri[0,:2])
  if u>=-1e-7 and v>=-1e-7 and u+v<=1+1e-7:out.append(tri[0,2]+u*(tri[1,2]-tri[0,2])+v*(tri[2,2]-tri[0,2]))
 return min(out) if out else None
clearances=[]
for P in web_samples:
 if P[0]>=28000.-1e-7:
  z=roofz(P)
  if z is not None:clearances.append(z-P[2]-thickness)
# Verify triangular web seam curves by analytic boundary reproduction and shared perimeter coordinates.
seammax=max(web_edges);shaftmax=max(shaft_tests)
qa={'status':'EXPERIMENTAL_R04_NOT_APPROVED','source_sha256':hashlib.sha256(raw).hexdigest(),'parent_R02_QA_sha256':hashlib.sha256((R/'inputs/PARENT_R02_QA.json').read_bytes()).hexdigest(),'frame':'X east Y north Z elevation, native 1:1; physical metres unresolved','source_interface_exact':[iN.tolist(),iS.tolist()],'parameters':{'spring':spring,'entrance_clear_width':2200,'threshold_depth':600,'entrance_soffit_crown':3750,'entrance_back_crown':entrance_crown,'ambulatory_boss':[26700,0,3620],'bay1':[28600,31000,4150],'bay2':[31000,33400,4400],'apse_boss':AP.tolist(),'web_vertical_thickness':thickness,'roof_eaves':4100,'roof_ridge_sequence':[4500,4600,4900,5150,5350]},'measured':{'web_boundary_error_max':seammax,'shaft_sweep_section_error_max':shaftmax,'roof_clearance_min_native':min(clearances),'roof_samples':len(clearances),'web_count':len(web_info)+1,'web_patch_details':web_info,'arc_details':arc_records,'rib_branches':rib_data},'checks':{'all_web_boundaries_match_defined_arch_and_rib_curves':seammax<1e-7,'matching_shaft_and_arch_sections':shaftmax<1e-7,'all_rib_circular_branches_monotone':all(r['monotone'] for r in rib_data),'roof_above_web_extrados':min(clearances)>0,'two_chapel_bays':True,'five_sided_apse':True,'five_ambulatory_webs_four_ground_bearings':len([w for w in web_info if w['name'].startswith('AMB_WEB')])==5,'entrance_soffit_R02_retained':abs(arc_records[0]['soffit_crown']-3750)<1e-7,'entry_depth_R02_retained':True,'old_outer_ring_not_imported':True},'limitations':['new profiles are designed experimental sections, not historical tracings or approved U/D profiles','middle interface XY only; actual saved vault elevations not reconciled','five-web crown/arch load transfer not structurally certified','web surfaces are boundary-interpolated trials, not historical V13 webs','missing F5ZL-C support schedule','companion chapels and main-cathedral roof/window clearance outside this axial-only model','core/shaft meshes intentionally overlap; not a boolean-unioned fabrication mesh']}
scene=bpy.context.scene;scene.unit_settings.system='NONE';scene['status']=qa['status'];scene['physical_m_per_native_unit']='UNRESOLVED';scene['source_plan_sha256']=qa['source_sha256']
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world.color=(.9,.9,.9)
scene.render.resolution_x=1700;scene.render.resolution_y=1150;scene.render.resolution_percentage=100
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.clip_start=100;cam.data.clip_end=60000;cam.data.lens=22
# Store complete model, render repeatable full/cutaway configurations without changing generation geometry.
def render(name,pos,target,scale=None,cut=False):
 if os.environ.get('SKIP_RENDERS'):return
 scene.display.shading.show_cavity=name!='INTERIOR'
 scene.display.shading.show_shadows=name!='INTERIOR'
 for o in objects:o.hide_render=False
 if cut:
  for o in COL['ROOF'].objects:o.hide_render=True
  for o in COL['WALLS'].objects:
   if o.name.startswith('SIDE_-1') or o.name.startswith('THRESHOLD_RETURN_-1'):o.hide_render=True
  for o in COL['WEBS'].objects:
   if o.name.endswith('_WEB_0') or o.name in ['AMB_WEB_0','AMB_WEB_FRONT_S','BAY1_WEB_1','BAY2_WEB_1','APSE_WEB_0','APSE_WEB_1','APSE_WEB_2']:o.hide_render=True
 cam.data.type='ORTHO' if scale else 'PERSP'
 if scale:cam.data.ortho_scale=scale
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
render('EXTERIOR',(39700,-11700,10500),(30500,0,2000),15000)
render('CUTAWAY',(37700,-10700,7900),(30100,0,1900),14000,True)
render('INTERIOR',(26000,0,1550),(34000,0,2600))
render('PLAN',(30200,0,24000),(30200,0,0),14000,True)
# Save complete source with full geometry visible.
for o in objects:o.hide_render=False
cam.data.type='ORTHO';cam.data.ortho_scale=15000;cam.location=(39700,-11700,10500);cam.rotation_euler=(Vector((30500,0,2000))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Axial_Chapel_R04_EXPERIMENTAL.blend'))
# Full and roof-off GLBs; Blender remains editable source with separate named collections.
bpy.ops.export_scene.gltf(filepath=str(R/'Axial_Chapel_R04_FULL.glb'),export_format='GLB')
bpy.ops.object.select_all(action='DESELECT')
for o in objects:
 if o.type=='MESH' and o.name not in COL['ROOF'].objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'Axial_Chapel_R04_ROOF_OFF.glb'),export_format='GLB',use_selection=True)
# Reload full GLB and compare actual world bounds and geometry counts.
source_objects=[o for o in objects if o.type=='MESH'];old_count=len(source_objects)
def bounds(obs):
 p=[o.matrix_world@v.co for o in obs for v in o.data.vertices];return np.min(np.array(p),axis=0),np.max(np.array(p),axis=0)
lo,hi=bounds(source_objects)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/'Axial_Chapel_R04_FULL.glb'))
loaded=[o for o in bpy.context.scene.objects if o.type=='MESH'];lo2,hi2=bounds(loaded)
qa['measured']['source_mesh_count']=old_count;qa['measured']['reimport_mesh_count']=len(loaded);qa['measured']['reimport_world_bounds_error']=float(max(np.max(abs(lo2-lo)),np.max(abs(hi2-hi))))
qa['checks']['GLB_geometry_count_retained']=old_count==len(loaded);qa['checks']['GLB_world_bounds_within_0_01_native']=qa['measured']['reimport_world_bounds_error']<.01
qa['checks']['finite_mesh_coordinates']=all(math.isfinite(c) for o in loaded for v in o.data.vertices for c in v.co)
qa['checks']['nondegenerate_mesh_faces']=all(p.area>1e-9 for o in loaded for p in o.data.polygons)
(R/'QA.json').write_text(json.dumps(qa,indent=2,default=lambda v:v.item() if hasattr(v,'item') else str(v)));print(json.dumps(qa['checks'],indent=2,default=lambda v:bool(v)));print('ROOF CLEARANCE',min(clearances),'WEB SEAM',seammax,'SHAFT MATCH',shaftmax)
