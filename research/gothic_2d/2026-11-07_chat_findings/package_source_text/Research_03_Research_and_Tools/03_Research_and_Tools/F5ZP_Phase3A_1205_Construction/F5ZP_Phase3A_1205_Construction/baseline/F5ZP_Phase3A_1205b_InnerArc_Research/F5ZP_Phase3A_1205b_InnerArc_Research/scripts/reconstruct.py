#!/usr/bin/env python3
"""Isolated 1205b research wrapper. Never writes supplied sources or tools.

Run: python scripts/reconstruct.py (from any directory).
The higher-resolution PDF derivative is bundled so the complete book is optional.
Coordinates: baseline crop pixel centers, X right, Y down. High-res index (i-1)/3.
"""
from pathlib import Path
import sys, json, csv, hashlib, subprocess, io, base64, math
from dataclasses import asdict
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source_handoff'; OUT=ROOT/'derived'; OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(SRC/'tools/V08'))
from gothic_geometry import circle_fit, sample_arc
from gothic_plate_reader import inspect_plate, extract_ink

BASE=json.loads((SRC/'experiment/measurements.json').read_text())
OC=np.array(BASE['circle_center_crop_px']); OR=BASE['radius_px']
SPECS={
 'N':([110,60],43,165,375),
 'E_upper':([161,111],43,-104,-4),
 'E_lower':([167,111],37,4,135),
 'S':([109,169],36,-38,222),
 'W_lower':([52,111],37,42,176),
 'W_upper':([58,111],43,184,286)}
COLORS=dict(zip(SPECS,['#0072b2','#009e73','#d55e00','#a125aa','#d78c00','#3b59bf']))

def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def savejson(p,obj):p.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def run_preprocessing():
    cmds=[['pages_grayscale.py',str(OUT/'inputs'),str(OUT/'grayscale')],
          ['pages_bw.py',str(OUT/'grayscale'),str(OUT/'bw155'),'--threshold','155'],
          ['pages_bw.py',str(OUT/'grayscale'),str(OUT/'bw180'),'--threshold','180'],
          ['pages_bw.py',str(OUT/'grayscale'),str(OUT/'adaptive'),'--local','--radius','24','--offset','10'],
          ['fill_hatching.py',str(OUT/'bw155'),str(OUT/'hatch_diagnostic'),'--length','3','--angle','45','--no-fill','--min-area','0','--report']]
    (OUT/'inputs').mkdir(exist_ok=True)
    (OUT/'inputs/1205b.png').write_bytes((OUT/'1205b_crop_432dpi.png').read_bytes())
    log=[]
    for c in cmds:
        p=subprocess.run([sys.executable,str(SRC/'tools/preprocessing'/c[0]),*c[1:]],capture_output=True,text=True)
        log.append({'tool':c[0],'args':c[1:],'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
        if p.returncode:raise RuntimeError(p.stderr)
    savejson(OUT/'preprocessing_log.json',log)
    # Hatch closure is a sensitivity diagnostic only; never used to measure arcs.

GRAY=np.array(Image.open(OUT/'1205b_crop_432dpi.png').convert('L')).astype(float)
def sample_stroke(spec,threshold=155):
    c,r,start,end=spec; rows=[]
    for angle in np.arange(start+5,end-5+.01,2):
        if min(abs((angle-k+180)%360-180) for k in [0,90,180,270])<6:continue
        u=np.array([np.cos(np.deg2rad(angle)),np.sin(np.deg2rad(angle))])
        rr=np.arange(r-4,r+4.001,.08);xy=np.array(c)+rr[:,None]*u
        # Pixel centers, not image edges: baseline x -> high-res index 3*x+1.
        v=map_coordinates(GRAY,[xy[:,1]*3+1,xy[:,0]*3+1],order=1,mode='nearest')
        ix=np.flatnonzero(v<threshold)
        runs=np.split(ix,np.where(np.diff(ix)>1)[0]+1)
        runs=[a for a in runs if len(a)>1 and len(a)*.08<2.5]
        if not runs:continue
        a=min(runs,key=lambda a:abs(np.mean(rr[a])-r))
        rad=np.average(rr[a],weights=threshold-v[a]);p=np.array(c)+rad*u
        rows.append([float(angle),float(p[0]),float(p[1]),len(a)*.08])
    return np.array(rows)

def fit_stroke(spec,threshold=155):
    rows=sample_stroke(spec,threshold);p=rows[:,1:3];seed=circle_fit(p)
    opt=least_squares(lambda q:np.linalg.norm(p-q[:2],axis=1)-q[2],[*seed.center,seed.radius],loss='soft_l1',f_scale=.4)
    mask=np.abs(np.linalg.norm(p-opt.x[:2],axis=1)-opt.x[2])<1
    fit=circle_fit(p[mask])
    return fit,rows,mask

def residual(f,p):return np.linalg.norm(p-np.array(f.center),axis=1)-f.radius
def intersections(a,b):
    c=np.array(a['center']);q=np.array(b['center']);r=a['radius'];s=b['radius'];v=q-c;d=float(np.linalg.norm(v))
    obj={'center_distance_px':d,'external_gap_px':d-r-s,'internal_margin_px':d-abs(r-s),'points':[]}
    if d>r+s:obj['relation']='separate';return obj
    if d<abs(r-s):obj['relation']='nested_disjoint';return obj
    if d==0:obj['relation']='concentric';return obj
    along=(r*r-s*s+d*d)/(2*d);h=math.sqrt(max(0,r*r-along*along));u=v/d;n=np.array([-u[1],u[0]])
    obj['relation']='two_intersections' if h>1e-8 else 'tangent'
    obj['points']=[(c+along*u+h*n).tolist(),(c+along*u-h*n).tolist()]
    obj['radius_vector_angle_deg']=math.degrees(math.acos(np.clip((r*r+s*s-d*d)/(2*r*s),-1,1)))
    obj['acute_tangent_crossing_angle_deg']=min(obj['radius_vector_angle_deg'],180-obj['radius_vector_angle_deg'])
    return obj

def angle(c,p):return float(np.degrees(np.arctan2(*(np.array(p)-c)[::-1])))
def point(c,r,a):return (np.array(c)+r*np.array([np.cos(np.deg2rad(a)),np.sin(np.deg2rad(a))])).tolist()
def svg_path(rec):
    c=rec['center'];r=rec['radius'];a,b=rec['svg_span_deg'];p=point(c,r,a);q=point(c,r,b)
    return f'M {p[0]:.9f},{p[1]:.9f} A {r:.9f},{r:.9f} 0 {int(b-a>180)} 1 {q[0]:.9f},{q[1]:.9f}'

def main():
    supplied=json.loads((SRC/'MANIFEST_SHA256.json').read_text())
    preserved={p:hashfile(SRC/p)==h for p,h in supplied.items()};assert all(preserved.values())
    run_preprocessing()
    fits={};records={};pointsets={};sensitivity={};csvrows=[];holdout={}
    rng=np.random.default_rng(1205)
    for name,spec in SPECS.items():
        f,rows,keep=fit_stroke(spec);fits[name]=f;p=rows[keep,1:3];pointsets[name]=p
        # Six contiguous blocks, bootstrap whole blocks: sensitivity, not metrological CI.
        blocks=np.array_split(p,6);boot=[]
        for _ in range(250):
            q=np.concatenate([blocks[i] for i in rng.integers(0,6,6)]);v=circle_fit(q);boot.append([*v.center,v.radius])
        boot=np.array(boot);lo,hi=np.percentile(boot,[2.5,97.5],axis=0)
        # Hold out every fifth contiguous angular block, before residual rejection.
        raw=rows[:,1:3];rs=[]
        for test in np.array_split(np.arange(len(raw)),5):
            train=np.setdiff1d(np.arange(len(raw)),test);ff=circle_fit(raw[train]);rs.extend(residual(ff,raw[test]))
        holdout[name]=float(np.sqrt(np.mean(np.array(rs)**2)))
        records[name]={'center':list(f.center),'radius':f.radius,'r_over_outer_R':f.radius/OR,'inlier_rmse_px':f.rmse,
            'sample_count':len(rows),'retained_count':int(sum(keep)),'max_inlier_residual_px':float(max(abs(residual(f,p)))),
            'raw_sample_rmse_px':float(np.sqrt(np.mean(residual(f,raw)**2))),
            'angular_block_holdout_raw_rmse_px':holdout[name],
            'block_bootstrap_95_percentile_center_x_y_radius':{'low':lo.tolist(),'high':hi.tolist()},
            'seed_and_angle_window':list(spec),'status':'EXPERIMENTAL_measured_circular_candidate'}
        sensitivity[name]=[]
        for th in [110,135,155,180]:
            ff,rr,kk=fit_stroke(spec,th)
            sensitivity[name].append({'threshold':th,'center':ff.center,'radius':ff.radius,'rmse':ff.rmse,'n':int(sum(kk)),
                                      'center_shift_from_155_px':float(np.linalg.norm(np.array(ff.center)-f.center)),
                                      'radius_shift_from_155_px':ff.radius-f.radius})
        for row,k in zip(rows,keep):
            csvrows.append([name,*row,int(k),float(residual(f,row[1:3][None,:])[0])])
    with (OUT/'stroke_samples.csv').open('w') as fh:
        w=csv.writer(fh);w.writerow(['arc','seed_angle_deg','x_crop_px','y_crop_px','stroke_width_px','retained','radial_residual_px']);w.writerows(csvrows)
    # Model comparison: identical raw stroke sample set for both models, no selective dropping.
    rawsets={n:sample_stroke(s)[:,1:3] for n,s in SPECS.items()}
    comps={}
    for model,groups in {'four_circles':[['N'],['E_upper','E_lower'],['S'],['W_lower','W_upper']],
                         'six_arcs':[[n] for n in SPECS]}.items():
        resid=[];by=[]
        for g in groups:
            p=np.concatenate([rawsets[n] for n in g]);f=circle_fit(p);rr=residual(f,p);resid.extend(rr)
            by.append({'arcs':g,'center':f.center,'radius':f.radius,'raw_rmse_px':float(np.sqrt(np.mean(rr**2)))})
        comps[model]={'parameter_count':len(groups)*3,'n_samples':len(resid),'raw_rmse_px':float(np.sqrt(np.mean(np.array(resid)**2))),'groups':by}
    comps['comparison_scope']='same manually seeded raw samples; geometric descriptive comparison, not independent recognition'
    joins={}
    for a,b in [('N','W_upper'),('N','E_upper'),('W_upper','W_lower'),('E_upper','E_lower'),('S','W_lower'),('S','E_lower')]:
        joins[a+'__'+b]=intersections(records[a],records[b])
    cusps={}
    for key,target in [('N__W_upper',[69,70]),('N__E_upper',[151,71])]:
        j=joins[key];cp=min(j['points'],key=lambda p:np.linalg.norm(np.array(p)-target))
        cusps[key]={'point':cp,'radius_vector_angle_deg':j['radius_vector_angle_deg'],
                    'acute_tangent_crossing_angle_deg':j['acute_tangent_crossing_angle_deg'],'status':'derived_observed_upper_cusp_candidate',
                    'circle_equation_error_px':max(abs(np.linalg.norm(np.array(cp)-records[n]['center'])-records[n]['radius']) for n in key.split('__'))}
    nw=cusps['N__W_upper']['point'];ne=cusps['N__E_upper']['point']
    # Only upper cusp joins use actual circle intersections. Lower free ends stay open.
    records['N']['svg_span_deg']=[angle(records['N']['center'],nw)%360,angle(records['N']['center'],ne)%360+360]
    records['E_upper']['svg_span_deg']=[angle(records['E_upper']['center'],ne),0]
    records['E_lower']['svg_span_deg']=[0,angle(records['E_lower']['center'],[145.4,141.7])]
    records['S']['svg_span_deg']=[angle(records['S']['center'],[137.6,147.4]),angle(records['S']['center'],[82.4,145])%360]
    records['W_lower']['svg_span_deg']=[angle(records['W_lower']['center'],[76.2,137.5]),180]
    records['W_upper']['svg_span_deg']=[180,angle(records['W_upper']['center'],nw)%360]
    for n,r in records.items():
        a,b=r['svg_span_deg'];r['span_length_deg']=b-a;r['arc_length_px']=r['radius']*np.deg2rad(b-a)
        r['start_point']=point(r['center'],r['radius'],a);r['end_point']=point(r['center'],r['radius'],b)
        r['outer_internal_tangency_error_px']=float(np.linalg.norm(np.array(r['center'])-OC)+r['radius']-OR)
        r['endpoint_policy']='analytic upper cusp intersections; cardinal side projections; lower free endpoints estimated from scan within ~1 px'
    side_gaps={
      'E_side_endpoint_gap_px':float(np.linalg.norm(np.array(records['E_upper']['end_point'])-records['E_lower']['start_point'])),
      'W_side_endpoint_gap_px':float(np.linalg.norm(np.array(records['W_upper']['start_point'])-records['W_lower']['end_point']))}
    meta=inspect_plate(OUT/'1205b_crop_432dpi.png')
    mask,inkmeta=extract_ink(OUT/'1205b_crop_432dpi.png',threshold=155/255)
    Image.fromarray((~mask*255).astype('uint8')).save(OUT/'v08_ink_mask.png')
    geometry={'schema':'f5zp.phase3a.1205b.six_arc_research.v1','date':'2026-11-03',
       'source':BASE,'higher_resolution_derivative':dict(meta,source_pdf_sha256=BASE['source_pdf_sha256'],pdf_page_1based=281,render_dpi=432,crop_box_px=[342,717,1017,1395]),
       'coordinate_system':{'units':'144-DPI reference crop pixels','origin':'center of original crop top-left pixel, index (0,0)','x':'right','y':'down','angles':'degrees, clockwise from +X','higher_resolution_coordinates':'crop_px=(high_resolution_pixel_index-1)/3; pixel-center registration','page_transform':'page_px=crop_px+(114,239)','physical_scale':'unknown; no architectural dimensions'},
       'outer_circle_fixed':{'center':OC.tolist(),'radius':OR,'status':'inherited conditional local reference, not refit'},
       'arcs':records,'adjacent_circle_relations':joins,'upper_cusps':cusps,'side_junction_discrepancies':side_gaps,
       'topology':'six separate measured arcs; upper cusps meet analytically; lower pairs disjoint; no closed opening or masonry mask claimed'}
    import itertools
    allcircles=dict(records,OUTER={'center':OC.tolist(),'radius':OR})
    geometry['all_support_circle_intersections']={a+'__'+b:intersections(allcircles[a],allcircles[b]) for a,b in itertools.combinations(allcircles,2)}
    savejson(OUT/'geometry.json',geometry);savejson(OUT/'threshold_sensitivity.json',sensitivity);savejson(OUT/'model_comparison.json',comps)
    # Exact SVG circular A commands, without polygon approximation or forced closure.
    head='<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="900" height="904" viewBox="0 0 225 226">'
    paths=[]
    for n,r in records.items():
        paths.append(f'<path id="{n}" d="{svg_path(r)}" fill="none" stroke="{COLORS[n]}" stroke-width="0.55"/>')
    outer=f'<circle id="inherited_outer" cx="{OC[0]:.12f}" cy="{OC[1]:.12f}" r="{OR:.12f}" fill="none" stroke="#777" stroke-width="0.35" stroke-dasharray="2 2"/>'
    centers=[]
    for n,r in records.items():
        x,y=r['center'];centers.append(f'<g id="center_{n}" stroke="{COLORS[n]}" stroke-width="0.35"><path d="M{x-2},{y}h4 M{x},{y-2}v4"/></g>')
    metadata='<title>1205b measured six-arc experiment; pixel units; lower gaps preserved</title>'
    (OUT/'1205b_measured.svg').write_text(head+metadata+outer+''.join(paths+centers)+'</svg>')
    b64=base64.b64encode((SRC/'experiment/1205b_original_crop.png').read_bytes()).decode()
    background=f'<image x="-0.5" y="-0.5" width="225" height="226" xlink:href="data:image/png;base64,{b64}" opacity="0.72"/>'
    (OUT/'1205b_overlay.svg').write_text(head+metadata+background+outer+''.join(paths+centers)+'</svg>')
    # Matched views and residual diagnostics use same crop scale and extents.
    fig,axes=plt.subplots(1,3,figsize=(16,5.8),layout='constrained')
    for ax in axes:
        ax.set_aspect('equal');ax.set_xlim(0,225);ax.set_ylim(226,0);ax.set_xlabel('crop x (px)');ax.set_ylabel('crop y (px)')
    axes[0].imshow(Image.open(SRC/'experiment/1205b_original_crop.png'),extent=(-.5,224.5,225.5,-.5));axes[0].set_title('Untouched 144 DPI source crop')
    axes[1].imshow(Image.open(OUT/'1205b_crop_432dpi.png'),extent=(-.5,224.5,225.5,-.5),alpha=.65);axes[1].set_title('Six measured arcs over source derivative')
    axes[2].set_title('Circle centers, upper cusps, lower gaps')
    theta=np.linspace(0,2*np.pi,500)
    for ax in axes[1:]:
        ax.plot(OC[0]+OR*np.cos(theta),OC[1]+OR*np.sin(theta),'--',color='.5',lw=.8)
        for n,r in records.items():
            p=sample_arc(r['center'],r['radius'],*r['svg_span_deg'],n=250)
            ax.plot(*p.T,color=COLORS[n],lw=1.5,label=n);ax.plot(*r['center'],'+',color=COLORS[n])
            if ax==axes[2]:
                offset={'W_upper':[-12,-7],'W_lower':[-17,8],'E_upper':[-12,-7],'E_lower':[-10,8]}.get(n,[2,-3])
                ax.text(*np.array(r['center'])+offset,n,color=COLORS[n],fontsize=8)
        for j in cusps.values():ax.plot(*j['point'],'o',ms=3,color='black')
    axes[1].legend(fontsize=7,loc='lower left');fig.suptitle('F5ZP Phase 3A · CXVIII / 1205b · Experimental image geometry, no architectural scale')
    fig.savefig(OUT/'comparison.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(3,2,figsize=(11,9),layout='constrained')
    for ax,(n,f) in zip(axes.flat,fits.items()):
        rows=sample_stroke(SPECS[n]);ax.plot(rows[:,0],residual(f,rows[:,1:3]),'.',ms=3,color=COLORS[n]);ax.axhline(0,color='.6',lw=.6);ax.set_title(n);ax.set_xlabel('seed ray angle (deg)');ax.set_ylabel('radial residual (px)')
    fig.savefig(OUT/'radial_residuals.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,8),layout='constrained')
    ax.imshow(Image.open(OUT/'1205b_crop_432dpi.png'),extent=(-.5,224.5,225.5,-.5),alpha=.6)
    for n,f in fits.items():
        rows=sample_stroke(SPECS[n]);res=residual(f,rows[:,1:3]);keep=abs(res)<1
        ax.scatter(rows[keep,1],rows[keep,2],s=8,color=COLORS[n],label=n)
        ax.scatter(rows[~keep,1],rows[~keep,2],s=35,color='red',marker='x')
    ax.legend(fontsize=8);ax.set_title('Selected ink samples; red crosses show rejected samples')
    ax.set_xlim(0,225);ax.set_ylim(226,0);ax.set_aspect('equal');fig.savefig(OUT/'selected_samples.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,4,figsize=(14,4),layout='constrained')
    for ax,(p,title) in zip(axes,[(OUT/'bw155/1205b.png','Fixed 155'),(OUT/'bw180/1205b.png','Fixed 180'),(OUT/'adaptive/1205b.png','Adaptive r24 / offset10'),(OUT/'hatch_diagnostic/1205b.png','Closure diagnostic — not fitted')]):
        ax.imshow(Image.open(p),cmap='gray');ax.set_title(title,fontsize=9);ax.axis('off')
    fig.savefig(OUT/'segmentation_alternatives.png',dpi=150);plt.close(fig)
    # Round-trip exported path values, independently checking radii and endpoints.
    import xml.etree.ElementTree as ET,re
    rt=[];tree=ET.parse(OUT/'1205b_measured.svg')
    for e in tree.findall('{http://www.w3.org/2000/svg}path'):
        n=e.attrib.get('id')
        if n not in records:continue
        nums=[float(x) for x in re.findall(r'-?\d+\.?\d*',e.attrib['d'])];r=records[n]
        # M x y A rx ry rotation large sweep x y
        p=np.array(nums[:2]);q=np.array(nums[-2:]);err=max(abs(np.linalg.norm(p-r['center'])-r['radius']),abs(np.linalg.norm(q-r['center'])-r['radius']))
        assert err<1e-7 and abs(nums[2]-r['radius'])<1e-8
        rt.append({'arc':n,'endpoint_circle_equation_error_px':err})
    assert len(rt)==6
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(SRC/'tools/V08'),'-p','test_v08.py','-v'],capture_output=True,text=True)
    (OUT/'v08_tests.txt').write_text(test.stdout+test.stderr);assert test.returncode==0
    qc={'source_handoff_hashes_unchanged':preserved,'all_preserved':all(preserved.values()),'v08_test_exitcode':test.returncode,
        'svg_roundtrip':rt,'circle_intersection_max_equation_error_px':max(j['circle_equation_error_px'] for j in cusps.values()),
        'analytic_vs_image_validation':'roundtrip errors are algebraic only; residuals conditional on seeded stroke selection',
        'architectural_geometry_modified':False,'tool_sources_modified':False,'source_images_modified':False}
    savejson(OUT/'validation.json',qc)
    print(json.dumps({'radii':{n:r['radius'] for n,r in records.items()},'comparison':comps,'cusps':cusps,'side_gaps':side_gaps},indent=2))

if __name__=='__main__':main()
