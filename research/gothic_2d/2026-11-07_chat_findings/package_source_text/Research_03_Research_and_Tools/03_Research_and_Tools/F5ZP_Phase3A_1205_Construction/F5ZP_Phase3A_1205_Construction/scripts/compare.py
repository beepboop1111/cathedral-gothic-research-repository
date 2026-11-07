from pathlib import Path
import zipfile,json,csv,io,hashlib,math,base64
import numpy as np
from scipy.optimize import minimize_scalar
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1];OUT=P/'results';OUT.mkdir(exist_ok=True)
z=zipfile.ZipFile(next((P/'baseline').glob('*.zip')));prefix='F5ZP_Phase3A_1205b_InnerArc_Research/'
g=json.loads(z.read(prefix+'derived/geometry.json'));O=np.array(g['outer_circle_fixed']['center']);R=g['outer_circle_fixed']['radius']
rows=list(csv.DictReader(io.StringIO(z.read(prefix+'derived/stroke_samples.csv').decode())))
pts={n:np.array([[float(r['x_crop_px']),float(r['y_crop_px'])] for r in rows if r['arc']==n and r['retained']=='1']) for n in g['arcs']}
u={'N':np.array([0,-1]),'E_upper':np.array([1,0]),'E_lower':np.array([1,0]),'S':np.array([0,1]),'W_lower':np.array([-1,0]),'W_upper':np.array([-1,0])}
groups={'upper':['N','E_upper','W_upper'],'lower':['S','E_lower','W_lower'],'single_all':list(pts)}
def residual(d,n):return np.linalg.norm(pts[n]-(O+d*u[n]),axis=1)-(R-d)
models={}
for group,names in groups.items():
 f=lambda d:float(np.mean(np.concatenate([residual(d,n) for n in names])**2))
 d=float(minimize_scalar(f,bounds=(.4*R,.8*R),method='bounded').x)
 models[group]={'d_px':d,'r_px':R-d,'d_over_R':d/R,'r_over_R':1-d/R,'sample_count':sum(len(pts[n]) for n in names),'rms_px':math.sqrt(f(d)),
  'scope':names,'per_arc_rms_px':{n:float(np.sqrt(np.mean(residual(d,n)**2))) for n in names},
  'centers':{n:(O+d*u[n]).tolist() for n in names},'status':'exact_family_construction_with_measured_parameter_not_author_prescribed_ratio'}
critical=(2-math.sqrt(2))*R
free=np.concatenate([np.linalg.norm(pts[n]-g['arcs'][n]['center'],axis=1)-g['arcs'][n]['radius'] for n in pts])
split=np.concatenate([residual(models['upper' if n in groups['upper'] else 'lower']['d_px'],n) for n in pts])
qc={'coordinates':g['coordinate_system'],'outer_reference':g['outer_circle_fixed'],'models':models,
 'same_retained_samples_comparison':{'n':len(free),'free_six_circle_rms_px':float(np.sqrt(np.mean(free**2))),'two_parameter_exact_family_rms_px':float(np.sqrt(np.mean(split**2))),'single_parameter_exact_family_rms_px':models['single_all']['rms_px']},
 'critical_tangency':{'d_px':critical,'r_px':R-critical,'d_over_R':2-math.sqrt(2),'r_over_R':math.sqrt(2)-1,'status':'mathematical_transition_candidate_for_mark_c_not_textually_identified'},
 'mark_positions':{'a':{'approx_x_px':44,'uncertainty_px':1.5},'c':{'approx_x_px':53,'uncertainty_px':1.5},'b':{'approx_x_px':64,'uncertainty_px':1.5}},
 'critical_predicted_west_center_x':O[0]-critical}
qc['analytic_checks']={}
for name,m in models.items():
 d=m['d_px'];r=m['r_px'];dist=math.sqrt(2)*d;gap=dist-2*r
 rec={'outer_internal_tangency_error_px':abs(d+r-R),'adjacent_circle_gap_px':gap,'relation':'intersect' if gap<0 else 'separate'}
 if gap<0:
  # Adjacent N and E: outer diagonal solution of equal-radius circles.
  mid=O+np.array([d/2,-d/2]);h=math.sqrt(r*r-d*d/2);pt=mid+np.array([1,-1])*h/math.sqrt(2)
  rec['NE_outward_intersection']=pt.tolist();rec['circle_equation_error_px']=max(abs(np.linalg.norm(pt-(O+np.array([0,-d])))-r),abs(np.linalg.norm(pt-(O+np.array([d,0])))-r))
 qc['analytic_checks'][name]=rec
(OUT/'construction_measurements.json').write_text(json.dumps(qc,indent=2)+'\n')
fig,axes=plt.subplots(1,3,figsize=(15,5.4),layout='constrained')
from PIL import Image
im=Image.open(io.BytesIO(z.read(prefix+'source_handoff/experiment/1205b_original_crop.png')))
theta=np.linspace(0,2*np.pi,600)
for ax,(name,d) in zip(axes,[('upper',models['upper']['d_px']),('lower',models['lower']['d_px']),('critical c hypothesis',critical)]):
 ax.imshow(im,extent=(-.5,224.5,225.5,-.5),alpha=.55)
 ax.plot(O[0]+R*np.cos(theta),O[1]+R*np.sin(theta),'--',color='.4',lw=.8)
 r=R-d
 for vec in [np.array([0,-1]),np.array([1,0]),np.array([0,1]),np.array([-1,0])]:
  c=O+d*vec;ax.plot(c[0]+r*np.cos(theta),c[1]+r*np.sin(theta),color='#d55e00',lw=.9);ax.plot(*c,'+',color='#d55e00')
 for n,a in g['arcs'].items():
  t=np.deg2rad(np.linspace(*a['svg_span_deg'],200));ax.plot(a['center'][0]+a['radius']*np.cos(t),a['center'][1]+a['radius']*np.sin(t),color='#0072b2',lw=1.3)
 ax.set_title(f'{name}\nd/R={d/R:.5f}; r/R={r/R:.5f}');ax.set_xlim(0,225);ax.set_ylim(226,0);ax.set_aspect('equal');ax.set_xlabel('crop pixels')
fig.suptitle('Figure 1205 · blue: measured arcs · orange: exact construction circles · gray: fixed outer reference')
fig.savefig(OUT/'construction_comparison.png',dpi=160);plt.close(fig)
for name,d in [('upper',models['upper']['d_px']),('lower',models['lower']['d_px']),('critical_candidate',critical)]:
 r=R-d;elements=[f'<circle cx="{O[0]:.12f}" cy="{O[1]:.12f}" r="{R:.12f}" stroke="#555"/>']
 for i,vec in enumerate([np.array([0,-1]),np.array([1,0]),np.array([0,1]),np.array([-1,0])]):
  c=O+d*vec;elements.append(f'<circle id="construction_{i}" cx="{c[0]:.12f}" cy="{c[1]:.12f}" r="{r:.12f}" stroke="#d55e00"/>')
 for n,a in g['arcs'].items():
  x,y=a['start_point'];ex,ey=a['end_point'];rr=a['radius'];large=int(a['span_length_deg']>180)
  elements.append(f'<path id="measured_{n}" d="M{x},{y} A{rr},{rr} 0 {large} 1 {ex},{ey}" stroke="#0072b2"/>')
 (OUT/(name+'_comparison.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="904" viewBox="0 0 225 226"><title>Experimental exact construction compared with preserved measured arcs; image-pixel units</title><g fill="none" stroke-width="0.45">'+''.join(elements)+'</g></svg>')
print(json.dumps(qc,indent=2))
