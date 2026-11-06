#!/usr/bin/env python3
"""Mandatory strict R16 guard wrapper for existing and new Gothic vaults.

An adapter is used rather than changing protected generator source.
Builders must generate in memory; guard runs BEFORE and AFTER building.
No exports happen until both checks pass. No automatic crown elevation
changes, especially when boundary arches use the same crown parameter.
"""
import importlib.util,hashlib,json,math,sys
from pathlib import Path
import numpy as np
from strict_crown_guard import (enforce,save_report,UnverifiedBoundaryGeometry,
                                LockedGeometryChange,fingerprint)

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'reference'
def _legacy():
    # Isolated, bit-identical source copy. Historical sources untouched.
    path=REF/'vault_generator.py'
    spec=importlib.util.spec_from_file_location('r16_original_legacy',path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module

def _xyz(v):
    return [float(x) for x in v]

def _arch(name,pts):
    p=np.asarray(pts,float)
    if p.ndim!=2 or p.shape[1]!=3:raise ValueError('bad arch dimensions')
    return {'id':str(name),'points_xyz':p.tolist()}

def rectangular_arches(generator,samples=257):
    """Real original Gothic arch soffits, not invented apex assumptions."""
    bay=generator.bay
    ss=np.linspace(0,1,samples)
    result=[]
    # Coordinates x, plan-z, elevation, as in old source geometry.
    edge_specs=[
        ('south',[(bay.x0+(bay.x1-bay.x0)*u,bay.z0) for u in ss]),
        ('north',[(bay.x0+(bay.x1-bay.x0)*u,bay.z1) for u in ss]),
        ('west',[(bay.x0,bay.z0+(bay.z1-bay.z0)*u) for u in ss]),
        ('east',[(bay.x1,bay.z0+(bay.z1-bay.z0)*u) for u in ss])]
    for ident,pairs in edge_specs:
        points=[(x,z,generator.soffit(x,z)) for x,z in pairs]
        result.append(_arch(ident,points))
    return result

def polygon_R07_arches():
    """Recover all six original R07 authoritative experimental arch CSVs."""
    exp=ROOT.parent
    output=exp/'CHAPEL_POLYGONAL_APSE_V4_SKELETON_R07_EXPERIMENTAL'/'outputs'
    profiles=[]
    for i in range(6):
        path=output/f'R07_BOUNDARY_POINTED_ARCH_{i:02d}.csv'
        if not path.is_file():raise UnverifiedBoundaryGeometry(
            'Missing original R07 arch profile: '+str(path))
        data=np.loadtxt(path,delimiter=',',skiprows=1)
        assert data.shape==(257,3)
        profiles.append(_arch(f'R07_arch_{i:02d}',data))
    return profiles

def source_lock_snapshot(paths):
    """Read source bytes before AND after. Missing files are errors."""
    result={}
    for path in paths:
        p=Path(path)
        if not p.is_file():raise FileNotFoundError('Protected source file '+str(p))
        result[str(p.resolve())]=hashlib.sha256(p.read_bytes()).hexdigest()
    return result

def preflight_existing_rectangular(config):
    """Existing protected geometry must remain at original boss height."""
    module=_legacy()
    b=module.Bay(**config)
    g=module.GothicVault(b)
    arches=rectangular_arches(g)
    # Existing legacy crown parameter drives pointed boundary arches.
    # Raising only that parameter does NOT create separate vault-boss rise.
    sources=[REF/'vault_generator.py',REF/'gothic_kernel_source.py']
    locks=source_lock_snapshot(sources)
    report=enforce(vault_id=config['id'],crown_Z=b.crown,
          spring_Z=b.spring,cap_Z=b.top,boundary_arches=arches,
          crown_locked=True,locks_before=locks,locks_after=locks,
          intended_export='open_intrados',phase='PREBUILD')
    report['legacy_generator_couples_arch_apex_and_boss']=True
    report['architectural_warning']="Original rectangular generator's crown "
    report['architectural_warning']+="drives boundary arches too. Do not just "
    report['architectural_warning']+="raise Bay.crown; a new independent boss/"
    report['architectural_warning']+="groin/web skeleton will be required."
    return report

def guarded_build(*,name,boundary_arches,crown_Z,spring_Z,
         source_paths,build_in_memory_fn,output_dir,
         locked_baseline_fn=None,crown_locked=False,cap_Z=None,
         rule=None,intended_export='open_intrados'):
    """Reusable strict generator boundary for future 3/4/5/6/8-way bays.

    build_in_memory_fn() must return a dict:
      {'mesh': trimesh.Trimesh, 'boundary_arches': arch records,
       'crown_Z':actual elevation,'web_peak_Z':actual max intrados,
       'locks':optional dict of protected original geometry signatures}.
    Source geometry and lock reference are checked before/after.
    Output (1:16 STL, full-scale GLB, JSON QA) only after postbuild PASS.
    """
    import trimesh
    if not callable(build_in_memory_fn):
        raise TypeError('R16 requires in-memory generator callback')
    baseline=source_lock_snapshot(source_paths)
    expected=locked_baseline_fn() if locked_baseline_fn else None
    # Make immutable deep snapshots: a builder might mutate an input
    # list/dict in place and accidentally fool a reference-equality check.
    archived_arches=json.loads(json.dumps(boundary_arches))
    archived_arch_sha=fingerprint(archived_arches)
    archived_locks=json.loads(json.dumps(expected)) if expected is not None else None
    locks={'source_sha256':baseline,'architectural':archived_locks}
    first=enforce(vault_id=name,crown_Z=crown_Z,spring_Z=spring_Z,
             boundary_arches=boundary_arches,cap_Z=cap_Z,
             crown_locked=crown_locked,locks_before=locks,locks_after=locks,
             intended_export=intended_export,rule=rule,phase='PREBUILD')
    generated=build_in_memory_fn()
    if not isinstance(generated,dict) or not isinstance(generated.get('mesh'),trimesh.Trimesh):
        raise TypeError('Builder must return in-memory trimesh and measured geometry')
    mesh=generated['mesh']
    if not np.isfinite(mesh.vertices).all() or not mesh.is_winding_consistent:
        raise ValueError('POSTBUILD_MESH_INVALID, no export permitted')
    if fingerprint(boundary_arches)!=archived_arch_sha:
        raise LockedGeometryChange('POSTBUILD_LOCKED_BOUNDARY_INPUT_MUTATED')
    after={'source_sha256':source_lock_snapshot(source_paths),
           'architectural':locked_baseline_fn() if locked_baseline_fn else None}
    if 'locks' in generated and fingerprint(generated['locks'])!=fingerprint(archived_locks):
        raise LockedGeometryChange('POSTBUILD_LOCKED_ARCHITECTURAL_GEOMETRY_CHANGED')
    # Postbuild must measure actual arches, rather than trusting inputs.
    actual_arches=generated.get('boundary_arches')
    if not actual_arches:raise UnverifiedBoundaryGeometry('POSTBUILD_NO_MEASURED_ARCHES')
    if len(actual_arches)!=len(boundary_arches):
        raise UnverifiedBoundaryGeometry('POSTBUILD_ARCH_COUNT_CHANGED')
    for a,b in zip(archived_arches,actual_arches):
        if a!=b:raise LockedGeometryChange('POSTBUILD_ORIGINAL_ARCH_BOUNDARY_CHANGED')
    actual_crown=float(generated['crown_Z'])
    if actual_crown!=float(crown_Z):
        raise ValueError('POSTBUILD_CROWN_ELEVATION_CHANGED')
    if intended_export=='closed_masonry' and not mesh.is_watertight:
        raise ValueError('CLOSED_MASONRY_MUST_BE_WATERTIGHT')
    second=enforce(vault_id=name,crown_Z=actual_crown,spring_Z=spring_Z,
             boundary_arches=actual_arches,
             cap_Z=cap_Z,web_peak_Z=generated.get('web_peak_Z'),
             crown_locked=crown_locked,locks_before=locks,
             locks_after=after,intended_export=intended_export,
             rule=rule,phase='POSTBUILD')
    dest=Path(output_dir)
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError('R16 refuses to overwrite existing outputs')
    dest.mkdir(parents=True,exist_ok=True)
    # Full native coordinates in GLB, 1:16 for STL as used by project.
    small=mesh.copy();small.apply_scale(1/16)
    small.export(dest/(name+'_1to16.stl'))
    mesh.export(dest/(name+'_FULL_1to1.glb'))
    save_report(dest/(name+'_CROWN_LOCK_QA.json'),
                {'prebuild':first,'postbuild':second,
                 'geometric_verification':'pass; NOT structural validation'})
    return {'prebuild':first,'postbuild':second,'export_folder':str(dest)}
