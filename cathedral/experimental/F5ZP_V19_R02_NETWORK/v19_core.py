"""V19 isolated connected skeleton kernel. Native units, Z up, no display scaling."""
import math,json,copy,hashlib
from pathlib import Path
ROOT=Path("/home/christopher/Downloads/F5ZP_V19_CONNECTED_SKELETON_EXPERIMENTAL")
def mix(a,b,t):return tuple((1-t)*x+t*y for x,y in zip(a,b))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def length(a):return math.sqrt(sum(x*x for x in a))
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Graph:
 def __init__(self,cfg):
  self.cfg=copy.deepcopy(cfg);self.nodes=copy.deepcopy(cfg["nodes"])
  for n in cfg["shared_nodes"]:self.nodes[n]=add(self.nodes[n],cfg["translation"])
  self.arches=cfg["arches"];self.vaults=cfg["vaults"]
 def arch(self,key,t):
  a=self.arches[key];P=self.nodes[a["ends"][0]];Q=self.nodes[a["ends"][1]]
  L=math.dist(P[:2],Q[:2]);z=(P[2]+Q[2])/2+a["rise"]
  if not 0<=t<=1:raise ValueError("ARCH_PARAMETER")
  if t==0:return tuple(P)
  if t==1:return tuple(Q)
  left=t<=.5;H=z-(P[2] if left else Q[2]);d=L*(t if left else 1-t)
  c=L/4+H*H/L
  if H<=L/2:raise ValueError("NOT_POINTED_OR_UNSAFE_SPRING_SHIFT")
  return (*mix(P[:2],Q[:2],t),(P[2] if left else Q[2])+math.sqrt(max(0,c*c-(d-c)**2)))
 def edge(self,v,k,t):
  key,rev=v["edges"][k];return self.arch(key,1-t if rev else t)
 def groin(self,v,k,r):
  P=self.nodes[v["corners"][k]];B=v["boss"];run=math.dist(P[:2],B[:2]);rise=B[2]-P[2]
  if run<=1e-8 or rise<=0:raise ValueError("GROIN_SPAN_OR_RISE")
  a=max(run,(run*run+rise*rise)/(2*run));b=(run*run+rise*rise-2*a*run)/(2*rise)
  z=P[2]+b+math.sqrt(max(0,a*a+b*b-(run*r-a)**2))
  return (*mix(P[:2],B[:2],r),P[2] if r==0 else B[2] if r==1 else z)
 def meridian(self,v,k,r):
  E=self.edge(v,k,.5);B=v["boss"];run=math.dist(E[:2],B[:2])
  return (*mix(E[:2],B[:2],r),(1-r)*E[2]+r*B[2]+self.hump(r)*run/self.cfg["hermite"]["reference_run"]*v["meridian_strength"])
 def hump(self,s):
  h=self.cfg["hermite"];T=h["t"];H=h["h"];S=h["slope"]
  if s==0 or s==1:return 0.
  k=next((k for k in range(len(T)-1) if s<=T[k+1]),len(T)-2)
  dt=T[k+1]-T[k];u=(s-T[k])/dt
  return (2*u**3-3*u*u+1)*H[k]+(u**3-2*u*u+u)*dt*S[k]+(-2*u**3+3*u*u)*H[k+1]+(u**3-u*u)*dt*S[k+1]
 def base(self,v,k,t,r):
  E=self.edge(v,k,t);P=self.edge(v,k,0);Q=self.edge(v,k,1)
  L=self.groin(v,k,r)[2];R=self.groin(v,(k+1)%len(v["corners"]),r)[2]
  radial=(1-t)*L+t*R;rise=E[2]-((1-t)*P[2]+t*Q[2])
  z=radial+(1-r)**v["exponent"]*rise
  z+=v["dome_lift"]*(v["boss"][2]-z)*math.sin(math.pi*t)**2*math.sin(math.pi*r)**2
  return (*mix(E[:2],v["boss"][:2],r),z)
 def web(self,v,k,t,r):
  if r==1:return tuple(v["boss"])
  if r==0:return self.edge(v,k,t)
  if t==0:return self.groin(v,k,r)
  if t==1:return self.groin(v,(k+1)%len(v["corners"]),r)
  p=self.base(v,k,t,r);z=p[2]+math.sin(math.pi*t)**2*(self.meridian(v,k,r)[2]-self.base(v,k,.5,r)[2])
  return (*p[:2],z)
 def validate(self):
  """No web evaluations. Validate authoritative graph, set-out, incidence, collisions."""
  users={a:[] for a in self.arches};paths=[];maxend=0.;bossres=0.
  for key,a in self.arches.items():
   for t,n in ((0,a["ends"][0]),(1,a["ends"][1])):maxend=max(maxend,math.dist(self.arch(key,t),self.nodes[n]))
   self.arch(key,.5)
   paths.append((key,a["ends"],[self.arch(key,j/128) for j in range(129)]))
  for vid,v in self.vaults.items():
   C=[self.nodes[n] for n in v["corners"]];N=len(C);B=v["boss"]
   if len(v["edges"])!=N:raise ValueError("EDGE_COUNT")
   signs=[]
   for k,P in enumerate(C):
    Q=C[(k+1)%N];R=C[(k+2)%N]
    signs.append(cross2(sub(Q,P),sub(R,Q)))
    if cross2(sub(Q,P),sub(B,P))<=1e-7:raise ValueError("BOSS_OUTSIDE_OR_INVALID_WINDING")
    key,rev=v["edges"][k];ends=self.arches[key]["ends"][::(-1 if rev else 1)]
    if ends!=[v["corners"][k],v["corners"][(k+1)%N]]:raise ValueError("INCIDENCE")
    users[key].append(vid)
    if B[2]<self.edge(v,k,.5)[2]-1e-7:raise ValueError("CROWN_BELOW_BOUNDARY_APEX")
    maxend=max(maxend,math.dist(self.groin(v,k,0),P))
    bossres=max(bossres,math.dist(self.groin(v,k,1),B))
    paths.append((vid+"_G"+str(k),[v["corners"][k],vid+"_BOSS"],[self.groin(v,k,j/128) for j in range(129)]))
   if min(signs)<=0:raise ValueError("NONCONVEX_PLAN")
  if any(len(u)>2 or len(u)==0 for u in users.values()):raise ValueError("NONMANIFOLD_REGISTRY")
  # Straight XY projections: all true 3D path crossings must appear in this test.
  hits=[];allowed=0;separation=[]
  for i,(ki,ei,pi) in enumerate(paths):
   for kj,ej,pj in paths[i+1:]:
    p,q=pi[0],pj[0];a=sub(pi[-1],p);b=sub(pj[-1],q);den=cross2(a,b)
    if abs(den)<1e-8:
     if abs(cross2(sub(q,p),a))<1e-7:
      axis=0 if abs(a[0])>abs(a[1]) else 1
      overlap=min(max(x[axis] for x in (pi[0],pi[-1])),max(x[axis] for x in (pj[0],pj[-1])))-max(min(x[axis] for x in (pi[0],pi[-1])),min(x[axis] for x in (pj[0],pj[-1])))
      if overlap>1e-7:hits.append([ki,kj,"UNEXPECTED_COLLINEAR_OVERLAP"])
     continue
    t=cross2(sub(q,p),b)/den;u=cross2(sub(q,p),a)/den
    if -1e-8<=t<=1+1e-8 and -1e-8<=u<=1+1e-8:
     if set(ei)&set(ej) and (t<1e-7 or t>1-1e-7) and (u<1e-7 or u>1-1e-7):allowed+=1;continue
     def sample(points,x):
      f=max(0,min(1,x))*128;j=min(127,int(f));return mix(points[j],points[j+1],f-j)
     gap=math.dist(sample(pi,t),sample(pj,u));separation.append(gap)
     if gap<1e-5:hits.append([ki,kj,gap])
  if hits:raise ValueError("SKELETON_COLLISIONS "+str(hits[:5]))
  return {"status":"PASS","vault_count":len(self.vaults),"arch_components":len(self.arches),"shared_registry":{k:u for k,u in users.items() if len(u)==2},
    "endpoint_residual":maxend,"boss_residual":bossres,"unexpected_centerline_collisions":hits,
    "intended_node_junctions":allowed,"nonincident_projected_crossings":len(separation),
    "minimum_crossing_Z_separation":min(separation) if separation else None,
    "skeleton_samples_per_component":129,"validation_before_any_web":True}
 def mesh(self,v,N):
  verts=[];faces=[];lookup={};grid={}
  def vi(p):
   key=tuple(round(x,8) for x in p)
   if key not in lookup:lookup[key]=len(verts);verts.append(p)
   return lookup[key]
  for k in range(len(v["corners"])):
   for j in range(N+1):
    for i in range(N-j+1):grid[j,i]=vi(self.web(v,k,i/(N-j) if j<N else .5,j/N))
   for j in range(N):
    for i in range(N-j):
     a,b,c=grid[j,i],grid[j,i+1],grid[j+1,i];faces.append((a,b,c))
     if i<N-j-1:faces.append((b,grid[j+1,i+1],c))
  return verts,faces
 def webqa(self,v,V,F,N):
  e={k:0. for k in ("arch","groin","groin_seam","boss","meridian")}
  for k in range(len(v["corners"])):
   for j in range(129):
    t=j/128;r=t
    e["arch"]=max(e["arch"],math.dist(self.web(v,k,t,0),self.edge(v,k,t)))
    e["groin"]=max(e["groin"],math.dist(self.web(v,k,0,r),self.groin(v,k,r)))
    e["groin_seam"]=max(e["groin_seam"],math.dist(self.web(v,k,1,r),self.web(v,(k+1)%len(v["corners"]),0,r)))
    e["boss"]=max(e["boss"],math.dist(self.web(v,k,t,1),v["boss"]))
    e["meridian"]=max(e["meridian"],math.dist(self.web(v,k,.5,r),self.meridian(v,k,r)))
  edges={};minarea=1e100;minxy=1e100
  for a,b,c in F:
   p=V[a];q=V[b];w=V[c];u=sub(q,p);v0=sub(w,p)
   n=(u[1]*v0[2]-u[2]*v0[1],u[2]*v0[0]-u[0]*v0[2],cross2(u,v0))
   minarea=min(minarea,length(n)/2);minxy=min(minxy,n[2]/2)
   for i,j in ((a,b),(b,c),(c,a)):
    key=tuple(sorted((i,j)));edges[key]=edges.get(key,0)+1
  Euler=len(V)-len(edges)+len(F)
  if max(e.values())>1e-7 or minarea<1e-8 or minxy<1e-8 or Euler!=1 or max(edges.values())!=2:raise ValueError("WEB_QA_FAIL")
  # Actual mesh boundary and groin stations use identical tessellation points.
  points={tuple(round(x,7) for x in p) for p in V}
  for k in range(len(v["corners"])):
   for j in range(N+1):
    for p in (self.edge(v,k,j/N),self.groin(v,k,j/N)):
     if tuple(round(x,7) for x in p) not in points:raise ValueError("MESH_INTERFACE_MISSING")
  return {"residuals_native":e,"vertices":len(V),"triangles":len(F),"Euler":Euler,"boundary_edges":sum(x==1 for x in edges.values()),
    "minimum_triangle_area":minarea,"minimum_signed_XY_area":minxy,"mesh_interface_stations":N+1,
    "peak_Z":max(p[2] for p in V),"boss":v["boss"],"peak_above_boss":max(p[2] for p in V)-v["boss"][2],
    "self_intersection":"Excluded by positive XY triangle Jacobians and convex fan partition; open height field"}
def regression(cfg):
 g=Graph(cfg);base=copy.deepcopy(cfg);base["translation"]=[0,0,0];b=Graph(base);d=cfg["translation"]
 errs=[]
 for j in range(257):errs.append(math.dist(g.arch("SHARED",j/256),add(b.arch("SHARED",j/256),d)))
 spans=[math.dist(x.arch("SHARED",0),x.arch("SHARED",1)) for x in (g,b)]
 for delta in ([0,0,0],[10,-20,5],[-12,8,-3],cfg["translation"]):
  c=copy.deepcopy(cfg);c["translation"]=delta;Graph(c).validate()
 invalid=copy.deepcopy(cfg);invalid["vaults"]["A"]["boss"][2]=-1
 try:Graph(invalid).validate()
 except ValueError:rejected=True
 else:raise AssertionError("INVALID_CROWN_NOT_REJECTED")
 # Extensibility: same graph schema, 16 connected four-sided vaults and 15 shared arches.
 c={"nodes":{},"arches":{},"vaults":{},"shared_nodes":[],"translation":[0,0,0],"hermite":cfg["hermite"]}
 for i in range(17):
  for y in (0,1):c["nodes"][f"n{i}_{y}"]=[i*1000,y*900,0]
 for i in range(16):
  ns=[f"n{i}_0",f"n{i+1}_0",f"n{i+1}_1",f"n{i}_1"];es=[]
  for k in range(4):
   a,b0=ns[k],ns[(k+1)%4];ends=sorted((a,b0));key=":".join(ends)
   c["arches"].setdefault(key,{"ends":ends,"rise":950.})
   es.append([key,a!=ends[0]])
  c["vaults"][str(i)]={"corners":ns,"edges":es,"boss":[i*1000+500,450,1250+i*3],"meridian_strength":1,"exponent":1.75,"dome_lift":.18}
 scale=Graph(c).validate()
 if max(errs)>1e-7 or abs(spans[0]-spans[1])>1e-7:raise AssertionError("RIGID_TRANSLATION")
 return {"rigid_translation_max_residual":max(errs),"span_before_after":spans,
 "curvature_preservation":"Entire analytic curve translated; identical two-circle radii and cusp angle",
 "offsets_native":d,"translation_cases_passed":4,"invalid_crown_rejected":rejected,
 "scale_test":scale,"no_webs_generated_for_scale_test":True}
