"""Independent analytic checks of the distance kernel and source preservation."""
from analyze import *
def cube(center):
 m=trimesh.creation.box(extents=[2,2,2]);m.apply_translation(center);return m
checks=[]
for pos,expected in [([5,0,0],3.),([5,6,0],5.),([0,0,0],0.),([2,0,0],0.)]:
 a=cube([0,0,0]);b=cube(pos);dist,_,_=exact_surface_distance(a,b)
 checks.append({'name':'analytic box separation '+str(pos),'expected':expected,'actual':dist,'pass':abs(dist-expected)<1e-8})
d,p,q=edge_edge(np.array([-1.,0,0]),np.array([1.,0,0]),np.array([[0.,-1,2]]),np.array([[0.,1,2]]))
checks.append({'name':'skew interior edge minimum','actual':d,'expected':2.,'pass':abs(d-2.)<1e-8})
source=r05_meshes();study=trimesh.load(ROOT/'F5ZP_Registration_Contact_R03.glb',force='scene',process=False)
M=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]])
for n,m in source.items():
 mat,gn=study.graph['R05__'+n];re=study.geometry[gn].copy();re.apply_transform(M@mat)
 err=float(np.max(np.abs(re.vertices-m.vertices)))
 checks.append({'name':'R05 vertex regression '+n,'max_coordinate_error':err,'faces_identical':bool(np.array_equal(m.faces,re.faces)),'pass':err<1e-8 and np.array_equal(m.faces,re.faces)})
for p in ROOT.glob('*.svg'):
 import xml.etree.ElementTree as ET
 ET.parse(p);checks.append({'name':'SVG XML '+p.name,'pass':True})
write('REGRESSION_QA.json',{'checks':checks,'passed':sum(x['pass'] for x in checks),'failed':sum(not x['pass'] for x in checks),'scope':'Technical and numerical only. Architectural/structural approval not implied.'})
assert all(x['pass'] for x in checks)
print('REGRESSION_PASS',len(checks))
