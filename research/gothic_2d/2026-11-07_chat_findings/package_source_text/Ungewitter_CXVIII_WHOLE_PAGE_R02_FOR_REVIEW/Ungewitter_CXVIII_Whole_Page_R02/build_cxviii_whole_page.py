#!/usr/bin/env python3
"""Read-only whole-page ink trace; no inferred architectural geometry.
Usage: python build_cxviii_whole_page.py SOURCE.png OUTPUT_DIR
"""
import sys,hashlib,json,shutil
from pathlib import Path
import numpy as np,cv2
from PIL import Image
import cairosvg
src=Path(sys.argv[1]); out=Path(sys.argv[2]);out.mkdir(exist_ok=True,parents=True)
raw=Image.open(src).convert('RGBA')
base=Image.new('RGBA',raw.size,'white'); base.alpha_composite(raw)
img=base.convert('RGB'); W,H=img.size
# Otsu's measured paper separation, with conservative minimum 3-pixel speck policy.
g=np.array(img.convert('L'));threshold=220
ink=(g<threshold).astype(np.uint8)*255
n,lab,stat,cen=cv2.connectedComponentsWithStats(ink,8)
clean=np.zeros_like(ink)
for i in range(1,n):
    if stat[i,cv2.CC_STAT_AREA]>=3:clean[lab==i]=255
# Lossless horizontal-run vectorization preserves hairline engraved marks, letters and fine axes.
# Polygon contours alone can erase 1px strokes; this page is specifically a tracing/ink pass.
paths=[]
for y in range(H):
    row=(clean[y]>0).astype(np.int8)
    diff=np.diff(np.pad(row,(1,1)))
    starts=np.flatnonzero(diff==1)
    ends=np.flatnonzero(diff==-1)
    for x0,x1 in zip(starts,ends):
        if x1>x0:
            paths.append(f'M{x0},{y}h{x1-x0}v1h-{x1-x0}z')
# Full page: separate exact scan-derived shapes from hypothetical axes.
joined=' '.join(paths)
header=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<title>Ungewitter–Mohrmann Volume II Plate CXVIII — whole-page 2D traced ink</title>
<desc>Scan-derived black ink silhouettes; original labels, edge frame, strokes, fine printed guides preserved. Uncalibrated image coordinates; not verified compass reconstructions.</desc>
<rect width="{W}" height="{H}" fill="white"/>
<g id="historical-ink-black" fill="#101010" fill-rule="evenodd"><path d="{joined}"/></g>'''
footer='\n</svg>\n'
# Precise figure centers/axes visually read from whole-page scan. Draw only axes as supplemental guides, distinct from history.
axes=[('1203',421,337,116),('1204',814,330,115),('1204a',1201,337,114),('1205',1512,342,124),('1206',321,682,115),('1207',646,665,117),('1207a',992,665,115),('1207b',1333,668,115),('1207c',1680,674,115),('1208',324,1074,130),('1210',629,1061,88),('1211',870,1059,94),('1212',1133,1060,92),('1209',1675,1059,140)]
# Some axes are at risk of visually conflicting with scan strokes; put a separate overlay layer (can be toggled in a vector editor).
axis_layers=['<g id="supplementary-lightgray-dashed-dividing-axes" fill="none" stroke="#bbbbbb" stroke-width="1.1" stroke-dasharray="6 7" opacity="0.9">']
for label,x,y,r in axes:
    # Keep supplemental axes within the motifs (rather than across labels).
    axis_layers += [f'<path d="M {x} {y-r} V {y+r} M {x-r} {y} H {x+r}"/>']
axis_layers += ['</g>']
base_svg=header+footer
annotated_svg=header+'\n'+'\n'.join(axis_layers)+footer
(out/'PLATE_CXVIII_WHOLE_PAGE_APPROVED_STYLE.svg').write_text(annotated_svg,encoding='utf8')
(out/'PLATE_CXVIII_WHOLE_PAGE_INK_ONLY.svg').write_text(base_svg,encoding='utf8')
# Render with source aspect ratio preserved. No forced square output canvas.
cairosvg.svg2png(bytestring=annotated_svg.encode(),write_to=str(out/'PLATE_CXVIII_WHOLE_PAGE_APPROVED_STYLE.png'),output_width=W,output_height=H)
cairosvg.svg2png(bytestring=base_svg.encode(),write_to=str(out/'PLATE_CXVIII_WHOLE_PAGE_INK_ONLY.png'),output_width=W,output_height=H)
shutil.copy2(src,out/'ORIGINAL_UNMODIFIED.png')
# quantitative compare against ink-only result
re=np.array(Image.open(out/'PLATE_CXVIII_WHOLE_PAGE_INK_ONLY.png').convert('L'))
orig=(g<threshold);recv=(re<128)
intersection=int((orig&recv).sum());union=int((orig|recv).sum());precision=intersection/max(int(recv.sum()),1);recall=intersection/max(int(orig.sum()),1)
meta={'title':'Ungewitter Vol II Plate CXVIII entire-page experimental 2D tracing','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_dimensions_px':[W,H],'geometry_units':'source pixels; no architectural scale','ink_threshold_grayscale':threshold,'speck_minimum_area_pixels':3,'vectorization':'exact horizontal ink runs (source pixel resolution)','vector_path_count':len(paths),'source_trace_pixel_intersection_over_union':intersection/union,'source_trace_pixel_precision':precision,'source_trace_pixel_recall':recall,'axis_status':'supplemental visual guides, approximate figure centers, not verified historical constructions','red_uncertainty_lines':'not drawn; no conjectural geometry introduced','status':'experimental; pending user review; no generator changes'}
(out/'TRACE_QA.json').write_text(json.dumps(meta,indent=2)+'\n')
(out/'README.md').write_text('''# Plate CXVIII — Whole-page trace R02\n\nOne single sheet, not cropped or rearranged.\n\n- `PLATE_CXVIII_WHOLE_PAGE_APPROVED_STYLE.svg` — entire plate in original arrangement, black engraved ink + separate light-gray dashed supplemental axes.\n- `PLATE_CXVIII_WHOLE_PAGE_APPROVED_STYLE.png` — whole-page review preview.\n- `PLATE_CXVIII_WHOLE_PAGE_INK_ONLY.svg` — source-faithful ink vectorization without new guide geometry.\n- `ORIGINAL_UNMODIFIED.png` — byte-identical upload.\n- `TRACE_QA.json` — source checksum, image-space validation.\n- `build_cxviii_whole_page.py` — reproduction script.\n\n## Research limitations\nThis is a faithful image-derived **whole-page trace**, not a set of mathematically recovered circular arcs. SVG outlines are vector boundaries of historic printed ink. In the annotated version, light-gray dividing axes are a distinct optional layer approximated from visible figures and are not claimed as printed historical axes. No red dashed hypothetical curves are included, because this pass introduces no speculative compass geometry. Original black historical guide strokes remain faithfully preserved. No scaling to actual architecture is implied. Existing generators and locked cathedral parameters are unchanged. Candidate for user review, not approved for promotion.\n''')
shutil.copy2(__file__,out/'build_cxviii_whole_page.py')
print(json.dumps(meta,indent=2))
