#!/usr/bin/env python3
from pathlib import Path
import numpy as np,json,zipfile,hashlib,csv
root=Path(__file__).resolve().parent
data=json.loads((root/'results/data/R11_CURVE_METRICS.json').read_text())
def interp(name,x):
 p=np.array(data[name]['all_points_px'],float)
 return np.interp(x,p[:,0],p[:,1])
comparisons={}
for name,up,low in [('upper','upper_coping','upper_intrados'),('lower','lower_coping','lower_intrados')]:
 left=max(data[up]['core_supported_range_px'][0],data[low]['core_supported_range_px'][0])
 right=min(data[up]['core_supported_range_px'][1],data[low]['core_supported_range_px'][1])
 xx=np.arange(left,right+1)
 t=interp(low,xx)-interp(up,xx)
 dy_up=np.diff(interp(up,xx));dy_lo=np.diff(interp(low,xx))
 comparisons[name]={
 'x_intersection_range_px':[int(left),int(right)],
 'min_ink_geometry_separation_px':float(np.min(t)),
 'max_ink_geometry_separation_px':float(np.max(t)),
 'median_separation_px':float(np.median(t)),
 'no_crossing_in_measured_core':bool(np.all(t>0)),
 'nonincreasing_y_fraction_up':float(np.mean(dy_up<=0)),
 'nonincreasing_y_fraction_lower':float(np.mean(dy_lo<=0)),
 'note':'Only image-space gap between line-tracing candidates; NOT physical masonry thickness'
 }
 assert comparisons[name]['no_crossing_in_measured_core']
assert all(len(v['core_points_px'])>40 for v in data.values())
# selected runs near end pier, and estimated ranges do not overlap
assert data['upper_coping']['core_supported_range_px'][1]<370
assert data['upper_intrados']['core_supported_range_px'][1]<370
report={
 'source_size_px':[630,1021],
 'architectural_scale_verified':False,
 'source_figure_dimensions_visible':['4,50','6,45','46,50 jusqu au sol'],
 'dimension_calibration_status':'labels legible; no common exact calibration adopted because printed interval origins, projection and scan geometry not verified',
 'comparisons':comparisons,
 'visual_classification':'upper and lower exposed main-span masonry rails; short spans beyond pier A excluded; springing and wall junction not reconstructed',
 'interpretation':'Experimental, independent of Ungewitter figure 912. No historical compass centers or pier geometries approved.'
}
(root/'results/data/R11_SPAN_TOPOLOGY_QA.json').write_text(json.dumps(report,indent=2))
rd=root/'README_R11.md'
rd.write_text(rd.read_text()+'\n## Span topology (image-only)\n'+''.join(f"- {n}: min rail separation {x['min_ink_geometry_separation_px']:.1f}px; max {x['max_ink_geometry_separation_px']:.1f}px; no crossing in core = {x['no_crossing_in_measured_core']}.\n" for n,x in comparisons.items())+'\nFigure 61 labels 4,50 and 6,45, and gives 46,50 to ground. This study intentionally does not derive an architectural unit calibration from them.\n')
# Renew manifest and archive after second QA
checks={}
for p in (root/'results').rglob('*'):
 if p.is_file():checks[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
(root/'OUTPUT_SHA256.json').write_text(json.dumps(checks,indent=2))
zip_path=root/'F5ZP_Buttress_R11_HighRes_FOR_REVIEW.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for p in [root/'Beauvais_fig61_Wikimedia_630x1021.png',root/'build_r11.py',root/'qa_r11.py',root/'README_R11.md',root/'OUTPUT_SHA256.json']+list((root/'results').rglob('*')):
  if p.is_file(): z.write(p,p.relative_to(root))
with zipfile.ZipFile(zip_path) as z: assert z.testzip() is None
print(json.dumps(report['comparisons'],indent=2))
print('CHECKED ZIP:',str(zip_path),zip_path.stat().st_size)
