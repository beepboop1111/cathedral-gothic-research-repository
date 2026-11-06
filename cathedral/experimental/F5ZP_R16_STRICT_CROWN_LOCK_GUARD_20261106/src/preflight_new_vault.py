#!/usr/bin/env python3
"""R16 generic configurable STRICT crown/lock preflight for any vault topology.

Use BEFORE each new vault-type generation, and in guarded_vault_adapter
after in-memory geometry construction. This command does not create a mesh.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from strict_crown_guard import (enforce,preferred_crown,save_report,
                                CrownBelowArchApex,LockedGeometryChange,
                                UnverifiedBoundaryGeometry)
from guarded_vault_adapter import source_lock_snapshot

def parse_arches(items):
    arcs=[]
    for entry in items:
        ident=entry.get('id')
        file=Path(entry.get('source_csv',''))
        if not file.is_file():raise FileNotFoundError('Original boundary arch missing: '+str(file))
        data=np.loadtxt(file,delimiter=',',skiprows=1)
        if data.ndim!=2 or data.shape[1]!=3:
            raise UnverifiedBoundaryGeometry('Need XYZ CSV: '+str(file))
        sha=hashlib.sha256(file.read_bytes()).hexdigest()
        expected=entry.get('expected_sha256')
        if expected is not None and sha!=expected:
            raise LockedGeometryChange(
                'LOCKED_ARCH_CSV_CHANGED: '+str(file)+'; do not build')
        arcs.append({'id':ident,'points_xyz':data.tolist()})
    return arcs

def preflight(config):
    p=dict(config)
    arcs=parse_arches(p['boundary_arches'])
    locks=p.get('protected_source_files',[])
    before=source_lock_snapshot(locks) if locks else None
    expected=p.get('protected_source_hashes')
    if expected is not None and before!=expected:
        raise LockedGeometryChange(
            'LOCKED_SOURCE_SHA256_MISMATCH: do not generate before source recovery.')
    selected=p.get('crown_Z')
    if selected is None:
        if p.get('crown_locked',False):
            raise ValueError('LOCKED_CROWN_MISSING: cannot invent a locked height.')
        selected=preferred_crown(boundary_arches=arcs,spring_Z=p.get('spring_Z'))
    report=enforce(vault_id=p['vault_id'],crown_Z=selected,
                   spring_Z=p.get('spring_Z'),boundary_arches=arcs,
                   cap_Z=p.get('cap_Z'),web_peak_Z=p.get('web_peak_Z'),
                   crown_locked=p.get('crown_locked',False),
                   locks_before=before,locks_after=source_lock_snapshot(locks)
                   if locks else None,
                   intended_export=p.get('intended_export','open_intrados'))
    report['autoselected_preferred_for_NEW_unlocked_only']=p.get('crown_Z') is None
    if expected is None:
        report['warnings'].append({
             'code':'AUTHORITY_HASHES_NOT_SUPPLIED',
             'message':'Existing source SHA-256 records were read but not '
                       'reconciled with the current approved baseline.'})
        report['warning_codes'].append('AUTHORITY_HASHES_NOT_SUPPLIED')
    return report

def main():
    ap=argparse.ArgumentParser(description='R16 STRICT crown & locked geometry vault gate')
    ap.add_argument('--config',required=True,help='input JSON with actual arch CSV paths')
    ap.add_argument('--output',required=True,help='new QA report JSON; never overwrites')
    args=ap.parse_args()
    source=Path(args.config)
    cfg=json.loads(source.read_text())
    try:
        r=preflight(cfg)
    except (ValueError,PermissionError,FileNotFoundError,KeyError) as exc:
        failure={'status':'HARD_STOP_NO_GEOMETRY_GENERATED',
          'code':exc.__class__.__name__,'error':str(exc),
          'warnings':[{'code':'LOCKED_GEOMETRY_WARNING_ALWAYS',
             'message':'All original cathedral dimensions, arches, ribs, '
               'plan coordinates, boss heights and approved generator hashes '
               'must remain unchanged; no architectural approval inferred.'}],
          'source_config':str(source),'geometry_changed':False}
        save_report(args.output,failure)
        print('R16_HARD_STOP',str(exc),file=sys.stderr)
        return 2
    save_report(args.output,r)
    print('R16_CROWN_RULE',r['crown_relation'],
          'crown',r['crown_Z'],'highest arch apex',r['highest_apex_Z'])
    print('R16_LOCK_WARNINGS',','.join(r['warning_codes']))
    return 0

if __name__=='__main__':sys.exit(main())
