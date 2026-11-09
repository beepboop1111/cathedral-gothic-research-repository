"""R43 profile input: preserve chosen moulding sections without implicit scaling.
A profile is an independently authored cross-section in millimetres, never a
reconstruction of rear stone geometry inferred from an unrelated publication.
"""
import json,math,hashlib
from pathlib import Path
def area(p):
 return .5*sum(x*v-u*y for (x,y),(u,v) in zip(p,p[1:]+p[:1]))
def crossing(p):
 def orient(a,b,c):
  return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 for i in range(len(p)):
  a=p[i];b=p[(i+1)%len(p)]
  for j in range(i+2,len(p)):
   if i==0 and j==len(p)-1:continue
   c=p[j];d=p[(j+1)%len(p)]
   if orient(a,b,c)*orient(a,b,d)<0 and orient(c,d,a)*orient(c,d,b)<0:return True
 return False
def levels_to_contour(front,rear):
 """Convert separately selected front/rear positive half-width station sequences."""
 def verify(a,label):
  if len(a)<3:raise ValueError('NEED_THREE_'+label+'_STATIONS')
  if any(len(z)!=2 for z in a):raise ValueError('LEVEL_WIDTH_MALFORMED')
  if any(z[1]<=0 for z in a):raise ValueError('NONPOSITIVE_HALF_WIDTH')
  if any(v[0]<=u[0] for u,v in zip(a,a[1:])):raise ValueError('NONMONOTONIC_DEPTH')
 verify(front,'FRONT');verify(rear,'REAR')
 if front[0][0]>=0 or rear[-1][0]<=0:raise ValueError('DEPTH_FACE_ORDER')
 if front[-1][0]!=0 or rear[0][0]!=0:raise ValueError('CENTRE_DEPTH_IS_NOT_ZERO')
 if abs(front[-1][1]-rear[0][1])>1e-6:raise ValueError('FRONT_REAR_NOT_CONTINUOUS_AT_MIDDLE')
 combined=front+rear[1:]
 return [(w,y) for y,w in combined]+[(-w,y) for y,w in reversed(combined)]
def load_section(path):
 p=Path(path)
 blob=json.loads(p.read_text())
 if blob.get('format')!='R43_Section_V1':raise ValueError('BAD_PROFILE_SCHEMA')
 if blob.get('units')!='mm':raise ValueError('UNITS_MUST_BE_EXPLICIT_MM')
 if not blob.get('profile_id'):raise ValueError('PROFILE_IDENTIFIER_REQUIRED')
 ev=blob.get('evidence_class')
 if ev not in ('SYNTHETIC','MEASURED_2D','EXPERIMENTAL'):raise ValueError('HISTORICAL_APPROVAL_REQUIRES_INDEPENDENT_REVIEW')
 if ev=='MEASURED_2D' and not blob.get('source_document'):raise ValueError('NO_SOURCE_DOCUMENT')
 if blob.get('historical_3d_joint_certified',False):raise ValueError('NO_CERTIFIED_3D_JOINT_IN_R43')
 if 'closed_points_mm' in blob:
  mm=blob['closed_points_mm']
  if len(mm)>3 and mm[0]==mm[-1]:mm=mm[:-1]
 else:
  mm=levels_to_contour(blob['front_halfwidth_stations_mm'],blob['rear_halfwidth_stations_mm'])
 if len(mm)<8 or len(mm)>2048:raise ValueError('POINT_COUNT_INVALID')
 if any(len(pt)!=2 or not all(math.isfinite(float(v)) for v in pt) for pt in mm):
  raise ValueError('MALFORMED_PROFILE_COORDINATES')
 pts=[(float(x),float(y)) for x,y in mm]
 if crossing(pts):raise ValueError('SELF_INTERSECTING_PROFILE')
 width=max(v[0] for v in pts)-min(v[0] for v in pts)
 depth=max(v[1] for v in pts)-min(v[1] for v in pts)
 if not (5<=width<=1000 and 5<=depth<=1000):raise ValueError('PROFILE_OUT_OF_RANGE_MM')
 if abs(area(pts))<100:raise ValueError('INSUFFICIENT_PROFILE_AREA')
 if area(pts)<0:pts.reverse()
 trace_sha=hashlib.sha256(p.read_bytes()).hexdigest()
 return [(x/1000,y/1000) for x,y in pts],{'profile_id':blob['profile_id'],'evidence_class':ev,
 'source_document':blob.get('source_document'),'source_sha256':trace_sha,
 'section_area_mm2':abs(area(pts)),
 'width_mm':width,'depth_mm':depth,'profile_point_count':len(pts),
 'historical_contact_geometry':'NOT PROVIDED'}
