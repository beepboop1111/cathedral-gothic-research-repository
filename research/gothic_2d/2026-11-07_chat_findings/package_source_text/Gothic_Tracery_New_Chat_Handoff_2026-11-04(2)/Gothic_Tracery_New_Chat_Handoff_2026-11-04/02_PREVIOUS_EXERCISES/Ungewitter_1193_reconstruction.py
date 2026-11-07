#!/usr/bin/env python3
"""Single figure 1193, approximate pixel-circle fit and annotated SVG output.

Reference image stays unchanged. Four visible arc segments appear to require four
circle constructions: two lower, and separately raised upper-left and upper-right.
Source x/y in image pixels with y downward; no architectural scale inferred.
"""
import math, json, hashlib, csv, itertools
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Arc
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parent
SOURCE=Path('/mnt/data/1UM_II_p277_pointed_arch_setout.png')
img=np.array(Image.open(SOURCE).convert('RGB'))
gray=np.array(Image.open(SOURCE).convert('L'))
# x,y, radius, start/end polar angles in the original raster convention (y down)
# Limits avoid the printed ink of construction axes and printed title.
INITIAL={
 'LOWER_LEFT':((72.3,185),44.,185,267),
 'UPPER_LEFT':((115.4,142.8),42.8,184,267),
 'UPPER_RIGHT':((115.7,130),43.,273,353),
 'LOWER_RIGHT':((157.5,187),43.4,275,352),
}
results={}
for name,(c,r,start,end) in INITIAL.items():
 sample=[]
 for deg in np.linspace(start,end,82):
  a=np.deg2rad(deg)
  x=c[0]+r*np.cos(a);y=c[1]+r*np.sin(a)
  candidates=[]
  for dy in range(-3,4):
   for dx in range(-3,4):
    xx=round(x+dx);yy=round(y+dy)
    if 15<xx<220 and 70<yy<210:
     v=int(gray[yy,xx])
     if v<180 and abs(np.hypot(xx-c[0],yy-c[1])-r)<4:
      candidates.append((xx,yy,v,np.hypot(xx-x,yy-y)))
  if candidates:
   q=min(candidates,key=lambda t:t[3]+.012*t[2]);sample.append(q[:2])
 pts=np.array(sample,float)
 def res(v):return np.linalg.norm(pts-v[:2],axis=1)-v[2]
 sol=least_squares(res,[*c,r],loss='soft_l1',f_scale=1.2)
 x,y,rr=sol.x
 results[name]={'cx_px':float(x),'cy_px':float(y),'r_px':float(rr),
  'fit_rmse_px':float(np.sqrt(np.mean(res(sol.x)**2))),
  'angular_range_deg_image':[start,end],'sample_count':int(len(pts)),
  'source_status':'Circle fitted to an ink segment; complete circle is an extension, not full historical ink'}

def intersections(a,b):
 x0,y0,r0=a['cx_px'],a['cy_px'],a['r_px']
 x1,y1,r1=b['cx_px'],b['cy_px'],b['r_px']
 dx=x1-x0;dy=y1-y0;d=math.hypot(dx,dy)
 if d>r0+r1 or d<abs(r0-r1) or d<1e-8:return []
 al=(r0*r0-r1*r1+d*d)/(2*d)
 h=math.sqrt(max(0.,r0*r0-al*al))
 px=x0+al*dx/d;py=y0+al*dy/d
 return [(px-h*dy/d,py+h*dx/d),(px+h*dy/d,py-h*dx/d)]

crossings=[]
for a,b in itertools.combinations(results,2):
 for i,(x,y) in enumerate(intersections(results[a],results[b]),1):
  crossings.append({'id':f'{a}__{b}__{i}','a':a,'b':b,'x_px':x,'y_px':y})
# Show calculated intersections inside the figure neighbourhood; others retain numerical record.
in_frame=[p for p in crossings if 22<=p['x_px']<=210 and 78<=p['y_px']<=198]
# First group: original untouched crop (separate from analytical drawing)
source=Image.open(SOURCE)
crop=source.crop((19,70,211,216))
crop.resize((960,730),resample=Image.Resampling.LANCZOS).save(ROOT/'GROUP_1_ORIGINAL_1193.png')

fig,ax=plt.subplots(figsize=(8.4,6.8),dpi=190)
ax.set_facecolor('white')
ax.set_aspect('equal')
for name,d in results.items():
 ax.add_patch(Circle((d['cx_px'],d['cy_px']),d['r_px'],fill=False,
                     edgecolor='black',lw=1.4,ls=(0,(1.2,4.0))))
 ax.scatter([d['cx_px']],[d['cy_px']],c='#00a934',s=70,zorder=6,
            edgecolor='white',linewidth=.6)
ax.axhline(185.8,color='#bcbfc3',lw=.7,ls=(0,(5,5)),zorder=0)
ax.axhline(142.4,color='#c8c9cc',lw=.7,ls=(0,(5,5)),zorder=0)
ax.axvline(115.5,color='#bfc2c6',lw=.75,ls=(0,(5,5)),zorder=0)
for name,d in results.items():
 ax.plot([d['cx_px'],d['cx_px']],[min(d['cy_px'],142.3),185.8],
         color='#d0d2d4',lw=.6,ls=(0,(4,5)),zorder=0)
for p in in_frame:
 ax.scatter([p['x_px']],[p['y_px']],c='#e62c2c',s=33,zorder=8)
# name annotations placed in spare areas on right of corresponding location
for label,px,py in [('LOWER L',38,177),('UPPER L',90,114),('UPPER R',153,107),('LOWER R',181,175)]:
 ax.text(px,py,label,fontsize=8,color='#434343',ha='center',va='center',
         bbox={'facecolor':'white','edgecolor':'none','alpha':.84,'pad':1})
ax.set(xlim=(18,210),ylim=(213,75))
ax.tick_params(labelsize=8)
ax.set_xlabel('Original plate X (pixels)',fontsize=9)
ax.set_ylabel('Original plate Y (pixels)',fontsize=9)
ax.set_title('GROUP 2 — 1193 analytical compass circles',fontsize=12,pad=12)
legend=[Line2D([0],[0],color='black',lw=1.4,ls=(0,(1.2,4)),label='Complete recovered circles (dotted black)'),
        Line2D([0],[0],color='#00a934',marker='o',ls='',markersize=7,label='Fitted circle center (green)'),
        Line2D([0],[0],color='#e62c2c',marker='o',ls='',markersize=6,label='Calculated circle intersection (red)'),
        Line2D([0],[0],color='#bfc2c6',ls=(0,(5,5)),lw=1,label='Dividing axis (thin dashed gray)')]
ax.legend(handles=legend,loc='lower center',bbox_to_anchor=(.5,-.27),ncol=2,fontsize=8,frameon=False)
fig.subplots_adjust(bottom=.22,top=.91)
fig.savefig(ROOT/'GROUP_2_CONSTRUCTION_CIRCLES_1193.png',facecolor='white',dpi=190)
plt.close(fig)

# A separate two-panel overview in the exact user requested order.
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(15,6.5),dpi=150)
ax1.imshow(img);ax1.set(xlim=(18,210),ylim=(211,76))
ax1.set_title('GROUP 1 — Original historical ink',fontsize=14)
ax1.axis('off');ax2.set_aspect('equal')
for name,d in results.items():
 ax2.add_patch(Circle((d['cx_px'],d['cy_px']),d['r_px'],fill=False,edgecolor='black',lw=1.5,ls=(0,(1.2,3.7))))
 ax2.scatter(d['cx_px'],d['cy_px'],s=72,color='#08a733',edgecolor='white',zorder=5)
for y in (185.8,142.4):ax2.axhline(y,color='#c3c7cb',lw=.75,ls=(0,(5,6)))
ax2.axvline(115.5,color='#c3c7cb',lw=.75,ls=(0,(5,6)))
for p in in_frame:ax2.scatter(p['x_px'],p['y_px'],s=37,color='#db2525',zorder=7)
ax2.set(xlim=(18,210),ylim=(211,76));ax2.axis('off')
ax2.set_title('GROUP 2 — Full dotted circles + geometry',fontsize=14)
fig.text(.5,.06,'GREEN = circle centers     RED = calculated intersections     LIGHT GRAY DASH = dividing axes     BLACK DOTS = full extended circles',ha='center',fontsize=10)
fig.text(.5,.025,'Circle fits estimated from small scan. All full circles are mathematical extensions of printed arcs, not printed full circumferences.',ha='center',fontsize=8,color='#666')
fig.tight_layout(rect=(0,.10,1,.98),w_pad=2.8)
fig.savefig(ROOT/'FIG1193_TWO_GROUPS_REVIEW.png',dpi=150,facecolor='white')
plt.close(fig)

# Full editable SVG with independently selectable layers via groups.
import xml.etree.ElementTree as ET
ET.register_namespace('', 'http://www.w3.org/2000/svg')
sns='http://www.w3.org/2000/svg';S=lambda n:'{'+sns+'}'+n
svg=ET.Element(S('svg'),{'width':'960','height':'690','viewBox':'0 0 230 165', 'xmlns':sns})
ET.SubElement(svg,S('rect'),{'x':'0','y':'0','width':'230','height':'165','fill':'white'})
g=ET.SubElement(svg,S('g'),{'id':'dividing_axes','stroke':'#bdc2c6','stroke-width':'.55','stroke-dasharray':'3 3','fill':'none'})
for x1,y1,x2,y2 in [(0,115.8,230,115.8),(0,72.4,230,72.4),(95.5,0,95.5,165)]:
 ET.SubElement(g,S('line'),{'x1':str(x1),'y1':str(y1),'x2':str(x2),'y2':str(y2)})
g=ET.SubElement(svg,S('g'),{'id':'recovered_full_circles_dotted_black','fill':'none','stroke':'#111','stroke-width':'.9','stroke-dasharray':'1.2 3.2'})
for name,d in results.items():
 ET.SubElement(g,S('circle'),{'id':name,'cx':str(d['cx_px']-20),'cy':str(d['cy_px']-70),'r':str(d['r_px'])})
g=ET.SubElement(svg,S('g'),{'id':'circle_centers_green','fill':'#00a934','stroke':'white','stroke-width':'.45'})
for name,d in results.items():ET.SubElement(g,S('circle'),{'cx':str(d['cx_px']-20),'cy':str(d['cy_px']-70),'r':'2.0'})
g=ET.SubElement(svg,S('g'),{'id':'calculated_intersections_red','fill':'#e62c2c'})
for p in in_frame:ET.SubElement(g,S('circle'),{'cx':str(p['x_px']-20),'cy':str(p['y_px']-70),'r':'1.5'})
ET.ElementTree(svg).write(ROOT/'GROUP_2_EDITABLE_ANALYTICAL_CIRCLES_1193.svg',encoding='unicode',xml_declaration=True)

j={'source_image':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
   'figure':1193,'trace_scope':'Four arc segments only; exclude neighboring figures 1194–1198',
   'source_image_size_px':list(img.shape[:2][::-1]),'image_units':'unalibrated pixel locations',
   'circles':results,'intersections':crossings,'intersections_visible_in_study':len(in_frame),
   'important_note':'Upper left and upper right arc are distinct vertically offset governing circles; do not impose a single upper center. Digitization is preliminary from low resolution plate crop.',
   'styles':{'historical_image':'original black/gray, no overpainting','recovered_full_circles':'dotted black','circle_centers':'green','intersections':'red','axes':'thin dashed light gray'},
   'limitations':['Small historical raster: fitted centers and radii require checking on higher resolution original','Arc-circle intersections are theoretical, not all used as Gothic arch junction points','No pointed arches, 3D or new rotation introduced']}
(ROOT/'FIG1193_MEASUREMENTS.json').write_text(json.dumps(j,indent=2)+'\n')
with (ROOT/'FIG1193_CIRCLES.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['id','center_x_original_px','center_y_original_px','radius_original_px','rmse_px','angular_start_deg_image','angular_end_deg_image'])
 for name,d in results.items():w.writerow([name,d['cx_px'],d['cy_px'],d['r_px'],d['fit_rmse_px'],*d['angular_range_deg_image']])
print(json.dumps({'circles':results,'intersection_count':len(crossings),'in_frame':len(in_frame)},indent=2))
