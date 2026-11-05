#!/usr/bin/env python3
"""F5ZP E5-S2 X01: independent, non-authoritative 2D northern gate screening study.

Reproduces plan geometry only. DOES NOT edit source files or authorize cuts,
construction, or baseline updates. Units are metres throughout.
Run: python3 build_gate_study.py (from this folder or any working directory).

Provenance of reconstructed SOURCE geometries: original F5ZM-C wall and roots
SHA256 6b3f35c35aeca588cbb8c7c81498bb9fbc58c92e30f4a0b63372f2940312a597
Chapel vault from UG canonical generator, SHA256
 eb68a0c16ca5dadea3f055c03c32376fee6408c5c4935dc3de7bbc68a12c45f6
E5-R3 experimental north monastery coordinates transcribed from E5_R3 notes;
protected E5-C3-L1 is a distinct southern scheme; no file is overwritten.
"""
import json, math
from pathlib import Path
import numpy as np
from shapely.geometry import box, Polygon, LineString, Point
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PolyPatch
from matplotlib.lines import Line2D

OUT=Path(__file__).resolve().parent
SC=1.3
R3=11.8129
WALL_THICK=0.192*SC
WF=R3+WALL_THICK        # 12.0625
P_TIP=WF+1.5*SC        # 14.0125
S_TIP=WF+0.320*SC      # 12.4785
R0,R1,R2=3.8129,6.4129,9.0129
Y_GATE=3.9
# Normalized source north-wall support stations, taken from F5ZM-C source records.
original=[(-34433,'S'),(-32597,'P'),(-30797,'S'),(-28997,'P'),(-27197,'S'),(-25397,'P'),(-23597,'S'),(-21797,'P'),(-19997,'S'),(-18197,'P'),(-16397,'S'),(-14597,'P')]
roots=[]
for xs,kind in original:
    x=xs*SC/1000
    if kind=='P':
        half_w0=(448*SC/1000)/2
        half_w1=(640*SC/1000)/2
        p=Polygon([(x-half_w0,WF),(x+half_w0,WF),(x+half_w1,P_TIP),(x-half_w1,P_TIP)])
    else:
        half_w0=(320*SC/1000)/2
        p=box(x-half_w0,WF,x+half_w0,S_TIP)
    roots.append({'source_id':f'ROOT-NV-R3-{abs(xs)}-N','class':kind,'x':x,'geometry':p})
# 2D source envelope is aligned by applying the 130% X scale and a further
# +2.7584m transverse translation beyond a uniform scale. No source modification.
wall=box(-40.013*SC,R3,-6.965*SC,WF)

N4=(-28.997*SC,-25.397*SC)
N5=(-25.397*SC,-21.797*SC)
N6=(-21.797*SC,-18.197*SC)
N4_mid=(N4[0]+N4[1])/2; N5_mid=(N5[0]+N5[1])/2; N6_mid=(N6[0]+N6[1])/2

def gate_center(a,b):
    """Center of available wall-face gap between OW-S at left, OW-P at right (or reverse)."""
    left=(a['x']+(0.416/2 if a['class']=='S' else 0.5824/2))
    right=(b['x']-(0.416/2 if b['class']=='S' else 0.5824/2))
    return (left+right)/2, right-left
byid={r['source_id']:r for r in roots}
n4_s=byid['ROOT-NV-R3-27197-N'];n4_e=byid['ROOT-NV-R3-25397-N']
n5_w=n4_e;n5_s=byid['ROOT-NV-R3-23597-N']
n6_s=byid['ROOT-NV-R3-19997-N'];n6_e=byid['ROOT-NV-R3-18197-N']
n4_gate,n4_gap=gate_center(n4_s,n4_e)
n5_gate,n5_gap=gate_center(n5_w,n5_s)
n6_night,n6_gap=gate_center(n6_s,n6_e)

# Source CH-N5 vault named 2304 x 1728mm; this projected chapel rectangle is a
# conditional, deliberately unapproved test: vault dimensions do not determine
# built chapel footprint, and source does not establish its exterior placement.
chapel_width_trial=2.304*SC
chapel_depth_trial=1.728*SC
chapel_reference=box(N5_mid-chapel_width_trial/2,WF,N5_mid+chapel_width_trial/2,WF+chapel_depth_trial)

# Accepted experiment E5-R3 NORTH monastery (distinct from protected E5-C3-L1 SOUTH).
cloister_outer=box(-52,18.9,-30,44.9)
cloister_garden=box(-48.5,22.4,-33.5,41.4)
east_wing=box(-30,22.9,-21,55.9)
chapter_hall=unary_union([box(-21,29.5,-9,38.5),Polygon([(-9,29.5),(-6,31),(-6,37),(-9,38.5)])])
refectory=box(-52,44.9,-32,54.9)
old_entrance_garden=box(-41,9,-30,18.9)

# Two independent, not-yet-approved door reservations.
# N4: private-sacred ceremonial corridor, throat 1.2m at north wall.
T=1.20
n4_throat=box(n4_gate-T/2,WF,n4_gate+T/2,14.1625)
# Widen only north of the modeled outer tips, from 1.2m to 2.7m over one metre.
gallery_transition=Polygon([(n4_gate-.6,14.1625),(n4_gate+.6,14.1625),
                            (n4_gate+1.35,15.1625),(n4_gate-1.35,15.1625)])
n4_gallery=box(n4_gate-1.35,15.1625,n4_gate+1.35,18.9)
n4_link=unary_union([n4_throat,gallery_transition,n4_gallery])
new_garden=box(-46.5,14.25,n4_gate-1.7,18.75)
# N6 night corridor is deliberately dotted RESERVATION only; it would require
# substituting a door for a side-window and designing a separate locked threshold.
night_throat=box(n6_night-.6,WF,n6_night+.6,14.1625)
night_corridor=box(n6_night-.75,14.1625,n6_night+.75,22.9)
night_route=unary_union([night_throat,night_corridor])

# Intersections with real source support envelopes reconstructed from F5ZM-C.
root_union=unary_union([r['geometry'] for r in roots])
def geometry_qa(name,g):
    intersections={r['source_id']:round(g.intersection(r['geometry']).area,8) for r in roots
                   if g.intersection(r['geometry']).area>1e-9}
    nearest=min(g.distance(r['geometry']) for r in roots)
    return dict(name=name,footprint_area_sqm=round(g.area,4),
                root_overlaps_sqm=intersections,minimum_root_gap_m=round(nearest,4),
                overlaps_wall_sqm=round(g.intersection(wall).area,4),
                overlaps_chapel_test_sqm=round(g.intersection(chapel_reference).area,4),
                overlaps_cloister_outer_sqm=round(g.intersection(cloister_outer).area,4))

N5_THROAT=box(n5_gate-.6,WF,n5_gate+.6,14.1625)
checks={x:geometry_qa(x,g) for x,g in [
    ('N4_gate_throat',n4_throat),('N4_gallery_transition',gallery_transition),
    ('N4_gallery_full',n4_gallery),('N4_combined_link',n4_link),
    ('N5_original_candidate_throat',N5_THROAT),
    ('N6_night_throat_reservation',night_throat),
    ('N6_night_corridor_reservation',night_corridor),
    ('N4_relocated_entrance_garden',new_garden),
    ('E5_R3_old_entrance_garden',old_entrance_garden)]}

# Use axis-aligned R1/R2 trial envelope widths solely for cross-aisle screening.
# At N4 eastern half-bay, nominal gap is 2.34-.666=1.674m.
mid_clear_center=(N4_mid+N4[1])/2
inner_gap=2.34-.666
interior_margin=(inner_gap-T)/2-abs(n4_gate-mid_clear_center)
# source chapel rectangle centered on N5 is an assumption, NOT a verified placement.
chapel_edge_gap=chapel_reference.bounds[0]-(n4_gate+T/2)
root_margin_near_tip=min(n4_throat.distance(r['geometry']) for r in roots)
root_margin_wall=(n4_gap-T)/2

status={
 'id':'F5ZP-E5-S2-N4-NORTH-GATE-X01',
 'status':'SEPARATE EXPERIMENTAL PLANNING OUTPUT ONLY - NO SOURCE GEOMETRY CHANGED OR PORTALS CUT',
 'coordinate_system':'X east; Z north; Y height; 1 model unit = 1 mm; drawings in metres',
 'source_checksums':{
  'F5ZM_C_JSON':'6b3f35c35aeca588cbb8c7c81498bb9fbc58c92e30f4a0b63372f2940312a597',
  'UG_VAULT_GENERATOR':'eb68a0c16ca5dadea3f055c03c32376fee6408c5c4935dc3de7bbc68a12c45f6',
  'E5_R3_NOTES':'73d3e974846f39ed09453dc95fce5dd0fbe41617a4df688f902975c50cd123bb',
  'E5_C3_L1_HANDOFF':'17f81329f56c7803743189e9235cebcb6ddeeec64773c608ce034e2b83b0b995'},
 'baseline_separation':{
  'E5_C3_L1':'PROTECTED SOUTH monastic house/cloister at Z -69 to -35; never moved or overwritten',
  'E5_R3':'EXPERIMENTAL NORTH monastery/cloister Z +18.9 to +44.9, used here solely as a candidate',
  'E5_S2':'EXPANDED CATHEDRAL EXPERIMENT, not an approved replacement for source F5ZP'},
 'reference_geometry':{
  'N4_fullbay_x_m':[round(v,4) for v in N4],
  'N5_fullbay_x_m':[round(v,4) for v in N5],
  'N6_fullbay_x_m':[round(v,4) for v in N6],
  'R0_R1_R2_R3_z_m':[R0,R1,R2,R3],
  'north_wall_outer_face_z_m':WF,
  'principal_buttress_tip_z_m':P_TIP,
  'secondary_buttress_tip_z_m':S_TIP,
  'CH_N5_source_vault_mm':[2304,1728],
  'CH_N5_scaled_vault_trial_m':[chapel_width_trial,chapel_depth_trial],
  'CH_N5_test_rectangle':tuple(round(v,4) for v in chapel_reference.bounds),
  'chapel_test_limitation':'vault dimensions are not established chapel exterior footprint, position, or total projection'},
 'candidate_comparison':{
  'N5_west':{'x_m':round(n5_gate,4),'wall_face_support_gap_m':round(n5_gap,4),
             'chapel_trial_overlap_sqm':checks['N5_original_candidate_throat']['overlaps_chapel_test_sqm'],
             'finding':'DO NOT CLEAR: overlaps conditional scaled CH-N5 projection'},
  'N4_east':{'x_m':round(n4_gate,4),'wall_face_support_gap_m':round(n4_gap,4),
             'chapel_trial_min_clearance_from_throat_m':round(chapel_edge_gap,4),
             'closest_R1_R2_trial_envelope_margin_m':round(interior_margin,4),
             'finding':'PREFERRED EXPERIMENTAL PORTAL; no root or assumed chapel test rectangle overlap'},
  'N6_east_night_reservation':{'x_m':round(n6_night,4),
             'wall_face_support_gap_m':round(n6_gap,4),
             'finding':'separate private route reservation; not a selected or cleared wall opening'}},
 'planning_widths':{'throat_m':T,'widened_gallery_m':2.70,'original_E5_R3_gallery_m':3.50,
                    'R1_R2_envelopes_m':0.666,'R3_gap_width_m':round(n4_gap,4),
                    'N4_root_gap_to_throat_m':round(root_margin_near_tip,4),
                    'N4_root_gap_at_wall_m':round(root_margin_wall,4)},
 'checks':checks,
 'source_authority_warnings':[
   'At every door line the original source wall is still continuous: no actual opening, jamb, lintel, roof or stair geometry is authorized.',
   'Source F5ZM-C roots have been scaled and shifted in this E5-S2 experiment; their original footprint locations are preserved in the source.',
   'CH-N5 is definitely a named chapel vault, but its real exterior chapel body is not in the support-root schedule.',
   'N4 throat uses conceptual 1.2m clear screening width; masonry portals/capitals may reduce it.',
   'Night route at N6 east is reserved to preserve circulation separation; it is not a tested chapel-free or approved cathedral doorway.',
   'The relocated garden in X01 changes ONLY the E5-R3 exploratory garden, not protected E5-C3-L1 gardens.',
   'No site levels, rainwater routing, daylight model, human accessibility/egress, foundations, or 3D collisions are certified.'
 ]
}
assert not checks['N4_gate_throat']['root_overlaps_sqm']
assert not checks['N4_gallery_transition']['root_overlaps_sqm']
assert not checks['N4_gallery_full']['root_overlaps_sqm']
assert not checks['N4_relocated_entrance_garden']['root_overlaps_sqm']
assert checks['N5_original_candidate_throat']['overlaps_chapel_test_sqm']>0
assert checks['N4_gate_throat']['overlaps_chapel_test_sqm']==0
assert interior_margin>0
assert n4_link.distance(cloister_outer)==0
assert n4_link.is_valid and night_route.is_valid
(OUT/'X01_QA.json').write_text(json.dumps(status,indent=2)+'\n')

# Deliver an editable clean SVG and a PNG preview, matching the same plan geometry.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
fig, ax = plt.subplots(figsize=(13,10.5),facecolor='#f9f8f4')
ax.set_facecolor('#f9f8f4')
def patch(g,fc,ec=None,lw=1,ls='-',alpha=1,z=4,hatch=None):
    for p in getattr(g,'geoms',[g]):
        if p.geom_type=='Polygon':
            ax.add_patch(PolyPatch(np.asarray(p.exterior.coords),closed=True,
              facecolor=fc,edgecolor=ec or fc,linewidth=lw,linestyle=ls,
              alpha=alpha,zorder=z,hatch=hatch))
patch(box(-52.02,-3.8129,-9.0545,R3),'#e8e4dc','#d2c9ba',z=0)
for z,col in [(R0,'#bc9d75'),(R1,'#c9ac81'),(R2,'#c9ac81'),(R3,'#7d766d')]:
    ax.plot([-41,-19],[z,z],color=col,lw=.95,ls='--',alpha=.65,zorder=2)
for bx,label in [(N4,'N4'),(N5,'N5'),(N6,'N6')]:
    for x in bx: ax.axvline(x,ls=':',lw=.7,color='#7e756b',zorder=1)
    ax.text(sum(bx)/2,5.45,label,ha='center',color='#5e5248',fontweight='bold',fontsize=10)
patch(wall,'#877d70','#62584e',lw=1,z=4)
for r in roots: patch(r['geometry'],'#8c7b69' if r['class']=='P' else '#a89b8a','#6c6258',lw=.75,z=5)
patch(chapel_reference,'#df9f89','#9c493a',lw=1.15,ls='--',alpha=.55,z=7)
ax.text(N5_mid,13.45,'CH-N5\ntrial only',color='#913c32',fontsize=7,ha='center',zorder=15)
patch(old_entrance_garden,'none','#bd8476',lw=1.1,ls='--',alpha=.7,z=6)
patch(new_garden,'#d8e6c8','#8ea578',lw=1.2,alpha=.82,z=6)
patch(cloister_outer,'#f2e1b6','#a98951',lw=1.6,z=3)
patch(cloister_garden,'#bed3a4','#809866',lw=1.2,z=4)
patch(east_wing,'#d4c2b1','#95765d',lw=1.2,z=4)
patch(chapter_hall,'#ddc6a6','#9e7752',lw=1.2,z=4)
patch(refectory,'#d9c2a7','#9c7e62',lw=1.2,z=4)
patch(n4_throat,'#efe6c9','#a17644',lw=1.6,z=9)
patch(gallery_transition,'#f5e8bf','#a17644',lw=1.6,z=9)
patch(n4_gallery,'#f5e8bf','#a17644',lw=1.6,z=9)
# Reserved night corridor: future option, not selected or cut.
patch(night_route,'none','#45718a',lw=1.4,ls=(0,(3,3)),z=9)
# Original N5 west door marker (rejected due to chapel reserve).
ax.scatter([n5_gate],[WF],marker='x',s=110,color='#a94a41',zorder=11,linewidths=2)
# View axes through the new portal.
ax.plot([n4_gate,n4_gate],[R0,WF],color='#c59b5a',lw=2.1,alpha=.8,zorder=8)
ax.plot([n4_gate,n4_gate],[15.1625,20.65],color='#ac8752',lw=1.7,alpha=.9,zorder=11)
# Turn within southern walk to eastern cloister walk at -31.75.
ax.annotate('',xy=(-31.75,20.65),xytext=(n4_gate,20.65),arrowprops={'arrowstyle':'->','color':'#866340','lw':2},zorder=11)
ax.plot([-31.75,-31.75],[20.65,27.0],color='#866340',lw=1.3,ls=':',zorder=11)
# Main coordinates and labels.
ax.text(-40.9,16.5,'reconfigured\nentrance garden',color='#4d7540',ha='center',fontsize=9,zorder=15)
ax.text(n4_gate-.45,16.95,'N4 entrance',rotation=90,ha='center',va='center',fontsize=8,color='#765532',zorder=15)
ax.text(-38.3,37.7,'MONASTIC\nCLOISTER',ha='center',fontweight='bold',fontsize=11,color='#675a42',zorder=15)
ax.text(-38.3,31.4,'GARDEN',ha='center',fontsize=9,color='#5f8053',zorder=15)
ax.text(-25.5,39,'EAST RANGE',ha='center',fontsize=9,color='#6a5141',zorder=15)
ax.text(-12.5,35.4,'CHAPTER',ha='center',fontsize=9,color='#6a5141',zorder=15)
ax.text(n6_night+1.0,17.7,'night route\nreserved',ha='left',fontsize=8,color='#426b85',zorder=15)
ax.text(-35.3,8.2,'CATHEDRAL NORTH AISLES',ha='left',fontsize=11,fontweight='bold',color='#554c44')
ax.text(-36.0,3.8,'toward nave',ha='center',fontsize=8,color='#8b7355')
ax.text(-38.9,12.6,'R3 wall',color='#64584e',fontsize=8,ha='center')
ax.annotate('N5 gate conflict',xy=(n5_gate,WF),xytext=(-29.0,16.8),
            arrowprops={'arrowstyle':'->','color':'#a94a41','lw':1.0},fontsize=8,color='#a94a41',zorder=12)
ax.set_xlim(-49,-8);ax.set_ylim(1,51)
ax.set_aspect('equal');ax.grid(color='#c9c5ba',alpha=.45,lw=.55)
ax.set_xticks(np.arange(-48,-7,4));ax.set_yticks(np.arange(2,51,4))
ax.set_xlabel('X east–west (metres)');ax.set_ylabel('Z north–south (metres)')
ax.set_title('F5ZP  |  E5-S2 / X01: NORTH MONASTIC ENTRANCE INTEGRATION',loc='left',fontsize=14,pad=15,fontweight='bold')
fig.text(.12,.052,'1:1 coordinate study  •  NORTH E5-R3 is experimental  •  original SOUTH E5-C3-L1 locked  •  no existing cathedral walls cut',fontsize=9,color='#5f5a52')
legend=[Line2D([0],[0],color='#9d8666',lw=6,label='Existing source root envelopes, E5-S2 trial placement'),
        Line2D([0],[0],color='#b59351',lw=5,label='N4 sacred entrance and gallery (new experiment)'),
        Line2D([0],[0],color='#a94a41',lw=2,ls='--',label='CH-N5 scaled-vault footprint assumption'),
        Line2D([0],[0],color='#426b85',lw=2,ls='--',label='Private night route reservation only')]
ax.legend(handles=legend,loc='upper left',fontsize=7,framealpha=.92)
fig.tight_layout(rect=[0,.075,1,1])
fig.savefig(OUT/'X01_NORTH_MASTER_PLAN.svg',facecolor=fig.get_facecolor())
fig.savefig(OUT/'X01_NORTH_MASTER_PLAN.png',dpi=190,facecolor=fig.get_facecolor())
plt.close(fig)

# Enlarged N4/N5 gate-detail plate.
fig,ax=plt.subplots(figsize=(12,7.8),facecolor='#faf9f6');ax.set_facecolor('#faf9f6')
patch(box(-38,11.5,-28,12.06),'#e9e5da','#bab1a3',z=0)
patch(wall,'#877d70','#6a5d51',z=3)
for r in roots:
 if -39<r['x']<-28:patch(r['geometry'],'#9a8b77','#6b6052',lw=1,z=5)
patch(chapel_reference,'#e6a28d','#b3483d',lw=1.2,ls='--',alpha=.53,z=6)
patch(n4_throat,'#eadfb8','#b58a47',lw=1.8,z=9)
patch(gallery_transition,'#f1e3b7','#b58a47',lw=1.8,z=9)
patch(n4_gallery,'#f1e3b7','#b58a47',lw=1.8,z=9)
patch(N5_THROAT,'none','#b3483d',ls='--',lw=1.7,z=10)
ax.text(n4_gate,16.6,'N4 west/east threshold\naxis X = %.3f'%n4_gate,fontsize=10,ha='center',color='#68502c')
ax.text(N5_mid,15.5,'CH-N5 source vault: 2.304 × 1.728 m\nScaled footprint only if centered/projection assumed',ha='center',color='#ac3d38',fontsize=8)
ax.text(n5_gate,14.7,'N5 rejected\nwithin trial chapel envelope',ha='center',color='#a64137',fontsize=8)
ax.plot([n4_gate-.6,n4_gate+.6],[11.72,11.72],lw=2.1,color='#856742')
ax.annotate('1.20 m trial throat',xy=(n4_gate,12.2),xytext=(-37.9,10.95),arrowprops={'arrowstyle':'->','lw':1,'color':'#836739'},fontsize=9,color='#836739')
ax.annotate('Principal root projection\nends Z%.3f'%P_TIP,xy=(-33.01,14.01),xytext=(-30.2,16.9),arrowprops={'arrowstyle':'->','lw':1,'color':'#6a6054'},fontsize=9,color='#6a6054')
for x,label in [(N4_mid,'N4 midpoint OW-S'),(N4[1],'N4/N5 OW-P'),(N5_mid,'N5 midpoint OW-S')]:
 ax.text(x,11.0,label,rotation=90,fontsize=7.3,ha='center',va='top',color='#554c44')
ax.set_aspect('equal');ax.set_xlim(-38.35,-28.1);ax.set_ylim(10.2,18.35);ax.grid(color='#d1ccc3',lw=.55,alpha=.6)
ax.set_xlabel('X (metres)');ax.set_ylabel('Z (metres)')
ax.set_title('N4 vs N5: masonry root reservation and chapel uncertainty',loc='left',fontweight='bold',pad=12)
fig.tight_layout()
fig.savefig(OUT/'X01_N4_N5_GATE_DETAIL.svg',facecolor=fig.get_facecolor())
fig.savefig(OUT/'X01_N4_N5_GATE_DETAIL.png',dpi=220,facecolor=fig.get_facecolor())
plt.close(fig)

# textual report: measured and conditional claims explicitly separated.
report=f'''# F5ZP — E5-S2 North Gallery Entrance, X01 Research Checkpoint

**Status:** new independent 2D planning test; not approved construction; no F5ZP authority replaced. Generated from the accompanying script and QA JSON. All dimensions in metres unless noted. X east, Z north.

## Evidence recovered

The preserved UG vault generator (`ug_vault_generator(1).py`, around lines 695–704) contains **CH-N5**, a named chapel at N5, with a **2304 × 1728 mm single vault**. These are vault dimensions, **not a verified exterior chapel footprint or exact coordinates**. The source F5ZE plan also lists exceptional CH-N5 at N5. The original F5ZM-C masonry root schedule contains no complete CH-N5 building projection.

Conditional reconstruction at 130%: vault width {chapel_width_trial:.4f}, depth {chapel_depth_trial:.4f}. **Assuming the scaled vault is centered on N5 and projects north from the exterior wall** gives an illustrative plan rectangle X {chapel_reference.bounds[0]:.4f}..{chapel_reference.bounds[2]:.4f}, Z {chapel_reference.bounds[1]:.4f}..{chapel_reference.bounds[3]:.4f}. Neither positioning assumption is source-authorized. The N5 west throat overlaps this test reservation by {checks['N5_original_candidate_throat']['overlaps_chapel_test_sqm']:.4f} m², and should not be selected without resolving the chapel.

## Resolved experimental adjustment

- **Sacred north entrance moved for the experiment from N5 west to N4 east**; this is a routine conflict resolution under user-approved experimental workflow, not a cathedral baseline change.
- N4 east portal center X **{n4_gate:.4f}**, north wall face Z **{WF:.4f}**; between N4 half-bay OW-S and N4/N5 principal OW-P.
- N4 throat screening width **{T:.2f} m** through the outer buttress zone; distance from modeled roots at closest point **{root_margin_near_tip:.4f} m**. Source root overlap **0 m²**. This is *not* proof of an approvable masonry door; wall-opening stone details missing.
- After the principal buttress roots end at Z **{P_TIP:.4f}**, the gallery begins widening at Z **14.1625** to **2.70 m** by Z **15.1625**, continuing to the E5-R3 south cloister walk at Z **18.900**.
- The direct covered link enters the **existing experimental E5-R3 southern cloister walk**, then turns east toward the eastern walk at X ~−31.75. This avoids cutting through the cloister garden. The 22 × 26 m E5-R3 cloister and primary buildings are not moved.
- Under provisional 666 mm R1/R2 pier envelopes, the 1.2m transverse N4 passage has a limiting nominal plan margin of **{interior_margin:.4f} m**. This is only a 2D centerline/footprint check; built responds may reduce clearance.
- N4 eastern exterior window is replaced conceptually by a portal; the western window in N4 remains a planning reservation. No glazing or door opening is physically drawn into the authoritative cathedral.

## Entrance garden correction

Earlier E5-R3 entrance garden occupied X −41..−30 / Z +9..+18.9 and is geometrically incompatible with the enlarged north outer wall and buttresses. X01 uses a provisional long garden rectangle X {new_garden.bounds[0]:.4f}..{new_garden.bounds[2]:.4f}, Z {new_garden.bounds[1]:.4f}..{new_garden.bounds[3]:.4f}, area **{new_garden.area:.2f} m²**; no overlap with the modeled relevant source root envelopes. Its reduced size and eventual access landscaping need broader precinct review. **Only this exploratory garden reservation changes**; source E5-R3 plans and locked E5-C3-L1 remain intact.

## Separate circulation remains separate

**Monastic ceremonial**: N4 east → narrow Gothic threshold → wider covered gallery → E5-R3 south cloister walk → eastern cloister walk. Reception/security threshold unbuilt.

**Private night access**: Preserve a distinct **N6 eastern half-bay** reserved route (X **{n6_night:.4f}**, running south from the east-wing stair area). This is *only a corridor reservation*: creating a private door in N6 would replace an outer-aisle window and require a new masonry, circulation and security study. Not approved as a wall opening.

**Public access**: retain independent north transept public approach; its precise north doorway/stairs remain unsourced. **Library visitors and service routes** remain separate from the cloister.

## Quantitative gates

| Item | Result | Scope |
|---|---:|---|
| N4 west-side full-bay? | No, N4 **east half-bay** | N4 midpoint to N4/N5 boundary |
| N4 portal center X | {n4_gate:.4f} | Candidate only |
| Wall-face gap between OW-S/OW-P | {n4_gap:.4f} m | Based on scaled F5ZM-C |
| N4 throat width | {T:.3f} m | Hypothetical clear plan width |
| N4 closest buttress-root gap | {root_margin_near_tip:.4f} m | Plan only, existing study roots |
| R1/R2 limiting trial clearance beyond 1.2m passage | {interior_margin:.4f} m | Assuming 666mm trial envelopes |
| Portal-to-CH-N5 test rectangle horizontal clearance | {chapel_edge_gap:.4f} m | **Conditional chapel location** |
| Full-width gallery north of roots | 2.700 m | Hypothetical |
| N4 root intersections | {len(checks['N4_combined_link']['root_overlaps_sqm'])} | Computed 2D |
| New garden root intersections | {len(checks['N4_relocated_entrance_garden']['root_overlaps_sqm'])} | Computed 2D |
| N5 west source chapel overlap | {checks['N5_original_candidate_throat']['overlaps_chapel_test_sqm']:.4f} m² | **Only the conditional chapel test** |

## Deferred major architectural requirements

1. Recover complete **CH-N5** external footprint, side-wall access and roof from real source geometry; the vault preset alone cannot authorize a clearance claim.
2. Determine actual lower-aisle pier/respond moulding envelopes and N4 threshold opening; an empty centerline strip is not a finished doorway.
3. Coordinate roof/gutter/valley and gallery roof height under the unapproved single-slope E5-S2 outer aisle roof test.
4. Resolve separate night route and its relationship to the east-wing stair, plus public transept entrance and terraces at real site elevations.
5. Compare this northern E5-R3 alternative against the **protected SOUTH E5-C3-L1** master in an eventual precinct-level architectural decision before any source promotion.

## Authority and safety

- **Do not** promote N4 over N5 into approved cathedral baseline until exterior chapel source and actual openings are established.
- No exterior stone, base supports, 88 root schedule, 1:1 coordinate system, vaulted elements, roofs, original monastery plan, 3D file, or generator has been changed.
- This experiment is **evidence-based plan screening, not structural engineering, accessibility, day-lighting or clearance certification**.
'''
(OUT/'X01_ARCHITECTURAL_REPORT.md').write_text(report)
readme='''# F5ZP E5-S2 N4 Northern Gate — X01 experimental package

Independent 2D schematic and validation. Do not import as authoritative geometry.

## Files
- X01_NORTH_MASTER_PLAN.svg / .png — editable plan and raster preview
- X01_N4_N5_GATE_DETAIL.svg / .png — junction detail
- X01_ARCHITECTURAL_REPORT.md — source evidence and recommendations
- X01_QA.json — numerical tests and source-protection register
- build_gate_study.py — reproducible study generator; uses Python 3, shapely, numpy, matplotlib

## Reproduce
```
python3 build_gate_study.py
```

## Version and provenance
E5-S2 X01, separate from locked southern E5-C3-L1 and experimental northern E5-R3.
Model plan units: metres for plots and calculations; reference data was measured in mm.
**This does not create a cathedral doorway or modify any project source.**
'''
(OUT/'README.md').write_text(readme)
print('SUCCESS: output',OUT)
print('N4 x',n4_gate,'root gap',root_margin_near_tip,'N4 chapel trial gap',chapel_edge_gap,'interior margin',interior_margin)
print('N5 chapel trial overlap',checks['N5_original_candidate_throat']['overlaps_chapel_test_sqm'])
for f in sorted(OUT.glob('*')):print(f.name,f.stat().st_size)
