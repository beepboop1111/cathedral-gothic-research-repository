#!/usr/bin/env python3
"""R04 sixfoil circular-arc study; original R03 mirrored scan is read-only.
Usage: python reconstruct_r04.py SOURCE.png CIRCLE_FIT_REGISTER.csv OUTDIR
Requires numpy, scipy, opencv-python, pandas, pillow, matplotlib.
Source pixel units; no implied historical scale. Each circle fit is measured independently.
Selected angular windows exclude cusp regions; they are never auto-certified.
"""
import sys,json,csv,math,hashlib
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.ndimage import distance_transform_edt
from PIL import Image,ImageDraw

SRC=Path(sys.argv[1]); REG=Path(sys.argv[2]); OUT=Path(sys.argv[3]); OUT.mkdir(parents=True,exist_ok=True)
image=np.array(Image.open(SRC).convert('L'))
H,W=image.shape
white=(image>170).astype('uint8')
_, labels, stats, centers=cv2.connectedComponentsWithStats(white,8)
records=[]; shapes={}; fits={}
all_rows=pd.read_csv(REG)
upper=all_rows.iloc[:7]

def svgpoly(points,stroke='black',width=1.4,dash=None):
    pts=' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{stroke}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'

def svg_page(body,w=W,h=H,metadata=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><title>Gothic R04 sixfoil geometric study</title><desc>{metadata}</desc><rect x="0" y="0" width="{w}" height="{h}" fill="white"/>'+body+'</svg>'

for _,entry in upper.iterrows():
    name=entry['name']; cx=float(entry.center_x_px);cy=float(entry.center_y_px);R=float(entry.radius_px)
    label=labels[round(cy),round(cx)]
    if not label: raise RuntimeError('Center outside enclosed region '+name)
    region=(labels==label).astype('uint8')
    contours,_=cv2.findContours(region,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    pts=max(contours,key=cv2.contourArea)[:,0,:].astype(float)
    # Six lobes are rotated 30 deg in the single central ornament.
    orientation= -90.0 if name=='U_middle_C' else 0.0
    fitted=[]; selections=[]
    for k in range(6):
        a=math.radians(orientation+60*k)
        angle=np.arctan2(pts[:,1]-cy,pts[:,0]-cx)
        delta=np.angle(np.exp(1j*(angle-a)))
        sel=(np.abs(delta)<math.radians(24)) & (np.linalg.norm(pts-[cx,cy],axis=1)<0.88*R)
        p=pts[sel]
        guess=[cx+.67*R*math.cos(a),cy+.67*R*math.sin(a),.30*R]
        def residual(z): return np.linalg.norm(p-z[:2],axis=1)-z[2]
        fit=least_squares(residual,guess,loss='soft_l1',f_scale=1,max_nfev=200)
        x,y,rad=map(float,fit.x)
        rms=float(np.sqrt(np.mean(residual(fit.x)**2)))
        # Project actual sampled contour pixels onto the analytical circle for fitted-arc rendering.
        q=p-np.array([x,y]);unit=q/np.linalg.norm(q,axis=1)[:,None]
        sampled=np.array([x,y])+rad*unit
        # The angle about its own lobe center must travel along its visible outer portion.
        phi=np.arctan2(q[:,1],q[:,0]);ph0=np.angle(np.mean(np.exp(1j*phi)))
        local=np.angle(np.exp(1j*(phi-ph0)))
        span=(float(local.min()),float(local.max()))
        seq=np.linspace(span[0],span[1],160)+ph0
        arc=np.c_[x+rad*np.cos(seq),y+rad*np.sin(seq)]
        fitted.append(dict(name=name,lobe=k,orientation_deg=orientation+60*k,
                           center_x_px=x,center_y_px=y,radius_px=rad,rms_px=rms,
                           n_points=len(p),arc_span_degrees=math.degrees(span[1]-span[0]),
                           normalized_center_x=(x-cx)/R,normalized_center_y=(y-cy)/R,
                           normalized_radius=rad/R))
        selections.append((p,arc))
    fits[name]=fitted;shapes[name]=dict(center=(cx,cy),R=R,pts=pts,selections=selections,label=label)
    records+=fitted

# Predict six other motifs using the fitted master, only allowing translation, ring scale and known rotation.
master='U_middle_L';master_rec=fits[master];M=shapes[master]; transfer=[]
for name,shape in shapes.items():
    S=shape['R']/M['R']; angle=math.radians((-90 if name=='U_middle_C' else 0))
    rot=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    # nearest competing measured center/radius after rotation and scaling
    target=fits[name]
    errs=[];radius_dev=[]
    for k,fit in enumerate(master_rec):
        c=(np.array([fit['center_x_px'],fit['center_y_px']])-M['center'])
        pred=np.array(shape['center'])+S*(rot@c)
        target_k=(k+ (0 if name!='U_middle_C' else 0))%6
        # Match by bearing to avoid angular index ambiguity.
        measured=min(target,key=lambda t:np.linalg.norm(np.array([t['center_x_px'],t['center_y_px']])-pred))
        errs.append(float(np.linalg.norm(np.array([measured['center_x_px'],measured['center_y_px']])-pred)))
        radius_dev.append(float(abs(measured['radius_px']-S*fit['radius_px'])))
    transfer.append(dict(name=name,ring_scale=S,rotation_degrees=math.degrees(angle),
                         mean_center_deviation_px=float(np.mean(errs)),max_center_deviation_px=float(max(errs)),
                         mean_radius_deviation_px=float(np.mean(radius_dev)),
                         status='measured_transfer_test_not_historical_identity'))

# Exact construction circles (dotted black) and measured visible arc segments (solid black).
svg_body=[]
svg_body.append('<g id="light_gray_dividing_axes" fill="none" stroke="#aaaaaa" stroke-width="0.75" stroke-dasharray="7 6">')
for name,s in shapes.items():
    cx,cy=s['center'];r=s['R'];svg_body.append(f'<line x1="{cx-r}" y1="{cy}" x2="{cx+r}" y2="{cy}"/><line x1="{cx}" y1="{cy-r}" x2="{cx}" y2="{cy+r}"/>')
svg_body.append('</g><g id="recovered_complete_circles" fill="none" stroke="black" stroke-width="0.6" stroke-dasharray="1 5" opacity="0.68">')
for name,group in fits.items():
    for f in group:svg_body.append(f'<circle cx="{f["center_x_px"]:.3f}" cy="{f["center_y_px"]:.3f}" r="{f["radius_px"]:.3f}"/>')
svg_body.append('</g><g id="measured_circular_arc_segments" fill="none" stroke="black" stroke-width="1.6" stroke-linejoin="round">')
for name,s in shapes.items():
    for _,arc in s['selections']:svg_body.append(svgpoly(arc))
svg_body.append('</g>')
# Measured cusp connectors are not replaced by invented compass arcs; show scan contour dashed red in excluded windows.
svg_body.append('<g id="unverified_cusps_measured_not_circular" fill="none" stroke="#d22424" stroke-width="1.5" stroke-dasharray="5 4">')
for name,s in shapes.items():
    p=s['pts'];cx,cy=s['center'];R=s['R'];phi=np.arctan2(p[:,1]-cy,p[:,0]-cx)
    a0=math.radians(-90 if name=='U_middle_C' else 0)
    d=np.angle(np.exp(1j*(phi-a0- np.round((phi-a0)/(math.pi/3))*(math.pi/3))))
    excluded=(np.abs(d)>=math.radians(24))
    # groups contiguous in cv2 contour sequence
    ix=np.where(excluded)[0]
    if len(ix):
        splits=np.where(np.diff(ix)>1)[0]+1
        for part in np.split(ix,splits):
            if len(part)>2:svg_body.append(svgpoly(p[part],stroke='#d22424',width=1.3,dash='4 3'))
svg_body.append('</g>')
(OUT/'02_MEASURED_LOBE_ARCS.svg').write_text(svg_page(''.join(svg_body),metadata='Solid black fitted circular segments; dotted black complete fit circles; dashed red cusp contour not fitted; axes gray.'),encoding='utf8')

# zoom specimen on one source motif without layout displacement
spec=shapes[master];cx,cy=spec['center'];r=spec['R']; margins=22
x0=int(cx-r-margins);y0=int(cy-r-margins);ww=int(2*r+2*margins);hh=ww
from PIL import Image as PI
src=PI.open(SRC)
src.crop((x0,y0,x0+ww,y0+hh)).save(OUT/'01_MASTER_SOURCE_CROP.png')
# comparison overlay on source crop, genuine fit vs image
from PIL import ImageDraw
preview=src.convert('RGB').copy();dr=ImageDraw.Draw(preview)
for name,s in shapes.items():
    for p,arc in s['selections']:
        dr.line([tuple(v) for v in arc],fill=(220,30,30),width=2)
preview.crop((x0,y0,x0+ww,y0+hh)).resize((ww*3,hh*3)).save(OUT/'03_MASTER_FIT_OVERLAY.png')
# side by side full set modest view, transparent precise fit arcs
preview.save(OUT/'04_ALL_SEVEN_ARC_FIT_OVERLAY.png')
# black tracing original via R03 existing SVG, not regenerated or altered.
with (OUT/'CIRCULAR_ARC_FITS.csv').open('w',newline='') as file:
    w=csv.DictWriter(file,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
with (OUT/'MASTER_TRANSFER_QA.csv').open('w',newline='') as file:
    w=csv.DictWriter(file,fieldnames=list(transfer[0]));w.writeheader();w.writerows(transfer)
qa=dict(source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),source_dimensions=[W,H],
        master=master,n_roundels=len(shapes),n_circular_fits=len(records),
        pooled_arc_rmse_px=float(np.sqrt(np.mean([r['rms_px']**2 for r in records]))),
        arc_rmse_min_px=min(r['rms_px'] for r in records),arc_rmse_max_px=max(r['rms_px'] for r in records),
        number_complete_cusps_validated=0,source_units='pixels',architectural_scale_calibrated=False,
        status='experimental_fits_only; cusp geometry not certified; no cathedral modifications')
(OUT/'QA_REPORT.json').write_text(json.dumps(qa,indent=2))
print(json.dumps(qa,indent=2))
