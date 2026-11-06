#!/usr/bin/env python3
"""F5ZP R16 hard crown gate. Pre-build and post-build, all bay topologies.
Reject crown below highest pointed-arch apex, warn if level; NEVER
auto-move locked elevations or silently change protected geometry.
"""
import hashlib,json,math
from dataclasses import dataclass,asdict

PROTECTED=("F5ZK-C and native 1:1 cathedral floorplan",
 "F5ZN-A dimensions and existing working inner/middle vault generator",
 "Approved Gothic boundary arches, ogives, responds and boss locations",
 "Pass 6J source and asymmetric pier bearings",
 "Unresolved F5ZL-C support schedule — do not invent")
class CrownBelowArchApex(ValueError):pass
class LockedGeometryChange(PermissionError):pass
class UnverifiedBoundaryGeometry(ValueError):pass

@dataclass(frozen=True)
class CrownRule:
    level_tolerance_native:float=1e-5
    preferred_rise_fraction:float=.08
    minimum_preferred_rise_native:float=25.
    minimum_cover_for_closed_masonry_native:float=0.
    def check(self):
        if min(self.level_tolerance_native,self.preferred_rise_fraction,
               self.minimum_preferred_rise_native)<=0:
            raise ValueError("Invalid R16 crown policy")
        if self.minimum_cover_for_closed_masonry_native<0:
            raise ValueError("Required cover cannot be negative")
        return self

def numeric(x,name):
    try:v=float(x)
    except (ValueError,TypeError) as ex:
        raise UnverifiedBoundaryGeometry("Missing "+name) from ex
    if not math.isfinite(v):raise UnverifiedBoundaryGeometry("Nonfinite "+name)
    return v

def fingerprint(obj):
    raw=json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def measure_arches(boundary_arches):
    """Required [{id:..., points_xyz:[[x,y,z],...]},...], sampled >=129."""
    if not isinstance(boundary_arches,(list,tuple)) or not boundary_arches:
        raise UnverifiedBoundaryGeometry("No measured boundary-arch curves provided")
    info=[];alerts=[];seen=set()
    for arc in boundary_arches:
        if not isinstance(arc,dict):raise UnverifiedBoundaryGeometry("Invalid arch")
        ident=str(arc.get('id','')).strip()
        pts=arc.get('points_xyz')
        if not ident or ident in seen:raise UnverifiedBoundaryGeometry("Invalid or duplicate arch ID")
        seen.add(ident)
        if not isinstance(pts,(list,tuple)) or len(pts)<3:
            raise UnverifiedBoundaryGeometry(ident+" requires >=3 measured XYZ points")
        heights=[]
        for p in pts:
            if not isinstance(p,(list,tuple)) or len(p)!=3:
                raise UnverifiedBoundaryGeometry(ident+" has malformed XYZ point")
            for j,x in enumerate(p):numeric(x,ident+" coordinate "+str(j))
            heights.append(float(p[2]))
        info.append({'id':ident,'apex_Z':max(heights),
                     'apex_sample_index':heights.index(max(heights)),
                     'sample_count':len(pts)})
        if len(pts)<129:alerts.append(
            {'code':'LOW_ARCH_SAMPLING','message':ident+
             ' has <129 samples. Confirm analytic apex or resample for actual build.'})
    return info,alerts

def preferred_crown(*,boundary_arches,spring_Z=None,rule=None):
    """Suggestion ONLY; never change a locked crown automatically."""
    r=(rule or CrownRule()).check()
    info,_=measure_arches(boundary_arches)
    apex=max(x['apex_Z'] for x in info)
    spring=numeric(spring_Z,'spring_Z') if spring_Z is not None else apex
    return apex+max(r.minimum_preferred_rise_native,
                    r.preferred_rise_fraction*max(0.,apex-spring))

def enforce(*,vault_id,crown_Z,boundary_arches,spring_Z=None,cap_Z=None,
            web_peak_Z=None,crown_locked=False,locks_before=None,
            locks_after=None,intended_export='open_intrados',
            rule=None,phase='PREBUILD'):
    """Mandatory call before generating and after exporting each vault."""
    r=(rule or CrownRule()).check()
    name=str(vault_id).strip()
    if not name:raise ValueError("vault_id missing")
    if intended_export not in ('open_intrados','closed_masonry'):
        raise ValueError('Unsupported export category')
    crown=numeric(crown_Z,'crown_Z')
    arches,sample_warnings=measure_arches(boundary_arches)
    apex=max(a['apex_Z'] for a in arches)
    cap=numeric(cap_Z,'cap_Z') if cap_Z is not None else None
    web_peak=numeric(web_peak_Z,'web_peak_Z') if web_peak_Z is not None else None
    warnings=[{'code':'LOCKED_GEOMETRY_WARNING_ALWAYS',
      'message':'Preserve approved originals and locked coordinates, profiles, '
      '1:1 scale and generator hashes. No automatic unlock/promotion.',
      'protected':list(PROTECTED)}]+sample_warnings
    if locks_before is None or locks_after is None:
        verified=False
        warnings.append({'code':'LOCK_REFERENCE_NOT_FULLY_VERIFIED',
           'message':'No paired complete baseline checksums: claim no lock regression pass.'})
    else:
        if fingerprint(locks_before)!=fingerprint(locks_after):
            raise LockedGeometryChange('LOCKED_GEOMETRY_MUTATION_HARD_STOP: '+name)
        verified=True
    # Floating-point arch samples may exceed nominal Z by ~1e-12 native.
    # Treat <=1e-8 as numerical equality ONLY; any substantive negative
    # crown-to-apex difference is a HARD STOP, without changing coordinates.
    measurement_roundoff_native=1e-8
    if crown<apex-measurement_roundoff_native:
        raise CrownBelowArchApex('CROWN_BELOW_ARCH_APEX_HARD_STOP: '+
             name+' crown Z='+str(crown)+' is below highest arch apex Z='+str(apex)+
             '. LOCKED_GEOMETRY_WARNING: all original arches, ribs, plan, '
             'boss records and generator source remain protected and unchanged.')
    delta=crown-apex
    if delta<=r.level_tolerance_native:
        warnings.append({'code':'LEVEL_CROWN_REDUCES_DOME_EFFECT',
          'message':'Crown is LEVEL with highest boundary apex: dome rise '
             'diminished. Prefer higher in NEW unlocked design; do not move locked geometry.'})
    recommended=preferred_crown(boundary_arches=boundary_arches,
                                spring_Z=spring_Z,rule=r)
    if crown_locked:
        warnings.append({'code':'CROWN_LOCKED_DO_NOT_RAISE',
          'message':'Crown locked: proposed preferred height informational only. '
              'Do not change without approval.'})
    elif crown<recommended:
        warnings.append({'code':'PREFER_HIGHER_CROWN',
          'message':'For NEW unlocked vault prefer crown >= '+str(round(recommended,6))+
              '; proposal, never automatic architectural edit.'})
    high=max(crown,web_peak) if web_peak is not None else crown
    if web_peak is not None and web_peak>crown:
        warnings.append({'code':'WEB_ABOVE_CROWN_REVIEW_CAP',
          'message':'Web exceeds boss: crown/apex guard does not prove '
                    'masonry or roof clearance.'})
    clearance=cap-high if cap is not None else None
    if intended_export=='closed_masonry' and r.minimum_cover_for_closed_masonry_native<=0:
        raise ValueError('CLOSED_EXPORT_HARD_STOP_COVER_NOT_SPECIFIED: set '
            'an explicitly reviewed positive minimum masonry cover first. '
            'LOCKED_GEOMETRY_WARNING: no approved masonry was modified.')
    if cap is None:
        warnings.append({'code':'NO_CAP_CLEARANCE_VERIFICATION',
          'message':'No upper masonry cap verified; do not claim closed-solid fit.'})
        if intended_export=='closed_masonry':
            raise ValueError('CLOSED_EXPORT_HARD_STOP_CAP_UNVERIFIED')
    elif clearance<r.minimum_cover_for_closed_masonry_native:
        warnings.append({'code':'CAP_INTERSECTION_OR_INSUFFICIENT_COVER',
          'message':'Top envelope clearance '+str(clearance)+
                     ' native units: open study only until approved thickness.'})
        if intended_export=='closed_masonry':
            raise ValueError('CLOSED_EXPORT_HARD_STOP_INADEQUATE_CAP')
    if cap is not None and recommended>cap:
        warnings.append({'code':'PREFERRED_CROWN_CONFLICTS_WITH_CAP',
          'message':'Preferred crown would exceed existing cap; roof change requires approval.'})
    return {'vault_id':name,'phase':phase,'status':'PASS_WITH_WARNINGS',
      'rule':'CROWN_Z >= MAX(all sampled boundary-arch apex_Z); strict rejection below',
      'arch_count':len(arches),'arch_apices':arches,'highest_apex_Z':apex,
      'crown_Z':crown,'rise_above_apex_native':delta,
      'crown_relation':'LEVEL_WARNING' if delta<=r.level_tolerance_native else 'RAISED',
      'recommended_for_new_unlocked_only_Z':recommended,
      'no_automatic_crown_changes':True,'crown_locked':bool(crown_locked),
      'locked_snapshot_hash_verified':verified,
      'web_peak_Z':web_peak,'cap_Z':cap,'cap_clearance_native':clearance,
      'intended_export':intended_export,'geometry_modified':False,
      'warning_codes':[w['code'] for w in warnings],
      'warnings':warnings,'rule_settings':asdict(r)}

def save_report(path,data):
    from pathlib import Path
    p=Path(path)
    if p.exists():raise FileExistsError('R16 refuses to overwrite report: '+str(p))
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2))
    return p
