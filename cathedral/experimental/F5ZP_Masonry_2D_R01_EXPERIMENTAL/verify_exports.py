#!/usr/bin/env python3
"""Read saved SVG/GeoJSON independently of the builder; test actual exports."""
from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET
from shapely.geometry import shape,Polygon,LineString,box
from shapely.ops import unary_union
import numpy as np

R=Path(__file__).resolve().parent;O=R/'outputs'
s=json.loads((R/'inputs/RECOVERED_SOURCE_EXTRACT.json').read_text())
features=json.loads((O/'PLAN_GEOMETRY_NATIVE.geojson').read_text())['features']
geo={f['properties']['id']:shape(f['geometry']) for f in features}
checks=[]
def test(name,condition,**kw):checks.append({'check':name,'pass':bool(condition),**kw})

test('GeoJSON feature IDs unique',len(geo)==len(features))
test('all saved polygon geometries valid',all(g.is_valid for g in geo.values()))
for name,c in s['cells'].items():
    coords=list(geo[name].exterior.coords)[:-1]
    test(name+' exact source vertices in actual GeoJSON',coords==[tuple(p) for p in c['vertices']])
res=unary_union([geo[k] for k in s['cells']]+[geo['R07_CHAPEL_RESERVATION'],geo['MAIN_BODY_PREVIEW']])
walls=geo['MAIN_MASONRY_320'].union(geo['CHAPEL_MASONRY_250'])
area=walls.intersection(res).area
test('exported masonry consumes zero reservation area',area<1e-6,area=area)
cross=geo['MAIN_MASONRY_320'].intersection(LineString([(-20000,-20000),(-20000,20000)]))
test('exported nave wall outer width',abs(cross.bounds[3]-cross.bounds[1]-14570)<1e-7)
cross=geo['CHAPEL_MASONRY_250'].intersection(LineString([(29800,-10000),(29800,10000)]))
test('exported chapel wall outer width',abs(cross.bounds[3]-cross.bounds[1]-3000)<1e-7)
test('exported chapel entrance open',walls.intersection(box(27999,-1200,28001,1200)).area<1e-7)
test('exported choir east interface open',walls.intersection(box(20212,-5000,20214,5000)).area<1e-7)
root=ET.parse(O/'MASTER_PLAN_NATIVE_1TO1.svg').getroot()
ns={'s':'http://www.w3.org/2000/svg'}
test('native SVG reflects Y once',len(root.findall(".//s:g[@transform='scale(1,-1)']",ns))==1)
maximum=0.
for name,c in s['cells'].items():
    e=root.find(f".//s:g[@id='{name}']/s:path",ns)
    nums=[float(n) for n in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',e.attrib['d'])]
    pts=np.array(nums).reshape(-1,2)[:-1]
    err=float(np.max(np.abs(pts-np.array(c['vertices']))))
    maximum=max(maximum,err)
    test(name+' native SVG matches source',err<1e-6,max_coordinate_error=err)
for p in O.glob('*.svg'):ET.parse(p)
test('five SVG files parse',len(list(O.glob('*.svg')))==5)
h=json.loads((O/'INPUT_SHA256_UNCHANGED.json').read_text())['sha256']
test('every input still matches pre-build hash',all(hashlib.sha256((R/k).read_bytes()).hexdigest()==v for k,v in h.items()))
report={'result':'PASS' if all(t['pass'] for t in checks) else 'FAIL',
        'checks_passed':sum(t['pass'] for t in checks),'checks_count':len(checks),
        'max_native_svg_coordinate_error':maximum,'checks':checks,
        'visual_review':'Three PNG sheets inspected; chapel dimension label overlap corrected before final inspection.'}
(O/'INDEPENDENT_EXPORT_QA.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
assert report['result']=='PASS',[t for t in checks if not t['pass']]
