#!/usr/bin/env python3
"""F5ZP R18 source-protected crown and geometry regression, synthetic only."""
import sys,pathlib,hashlib,json,time,dataclasses
HERE=pathlib.Path(__file__).resolve().parents[1]
R17=pathlib.Path("/home/christopher/Downloads/F5ZP_UNIVERSAL_GOTHIC_VAULT_GENERATOR_R01_EXPERIMENTAL/experiments/F5ZP_R17_FAST_UNIVERSAL_VAULT_WORKSPACE_EXPERIMENTAL")
sys.path[:0]=[str(HERE),str(R17/"addon"),str(R17/"addon/r17_vendor")]
import r18_core as core
import r17_core as old
from strict_crown_guard import enforce,preferred_crown,CrownBelowArchApex

def hashes():
    manifest=json.loads((R17/"addon/r17_vendor_sha256.json").read_text())
    files=[R17/"addon/r17_core.py",R17/"addon/r17_experimental_workspace.py",
       R17/"addon/r17_vendor/strict_crown_guard.py",
       R17/"addon/r17_vendor/guarded_vault_adapter.py",
       R17/"blender/F5ZP_R17_FAST_VAULT_WORKSPACE_REVIEW_READY_V02_EXPERIMENTAL.blend"]
    out={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    for name in ("strict_crown_guard.py","guarded_vault_adapter.py"):
        p=R17/"addon/r17_vendor"/name
        if out[str(p)]!=manifest[name]:raise ValueError("R16_VENDOR_SOURCE_MODIFIED "+name)
    return out

def protected_run(settings):
    settings.check();before=hashes()
    arches=old.measured_boundary_arches(settings,257)
    apex=max(max(p[2] for p in a["points_xyz"]) for a in arches)
    crown=(preferred_crown(boundary_arches=arches,spring_Z=settings.spring_Z)
           if settings.crown_mode=="AUTO" else apex
           if settings.crown_mode=="LEVEL" else settings.crown_Z)
    kwargs=dict(vault_id="R18_SYNTHETIC_"+settings.vault_type,
      crown_Z=crown,boundary_arches=arches,spring_Z=settings.spring_Z,
      cap_Z=settings.cap_Z if settings.cap_enabled else None,
      crown_locked=settings.crown_locked,intended_export="open_intrados")
    pre=enforce(**kwargs,locks_before=before,locks_after=before,phase="PREBUILD")
    d=core.generate(settings,crown)
    if d["arches"]!=arches:raise ValueError("ARCHES_MUTATED")
    geometry=core.qa(settings,d)
    after=hashes()
    if before!=after:raise ValueError("LOCKED_SOURCE_HASH_CHANGED")
    post=enforce(**kwargs,web_peak_Z=d["web_peak_Z"],
       locks_before=before,locks_after=after,phase="POSTBUILD")
    return d,{"crown_Z":crown,"highest_arch_apex_Z":apex,
      "guard_PREBUILD":pre,"guard_POSTBUILD":post,"geometry_QA":geometry,
      "locked_geometry_warning":"LOCKED_GEOMETRY_WARNING_ALWAYS",
      "baseline_hashes_before":before,"baseline_hashes_after":after,
      "source_mutations":False,"type":"synthetic experimental not approved"}

def suite():
    records=[];start=time.perf_counter()
    configs=[("TRI",3,"FAST",.07),("QUAD",4,"FAST",0.),
     ("PENTA",5,"FAST",.07),("HEXA",6,"FAST",.12),
     ("CUSTOM",7,"FAST",.11),("OCTA",8,"FAST",.09),
     ("QUAD",4,"FINAL",0.),("HEXA",6,"FINAL",.08)]
    for family,n,quality,irreg in configs:
        s=old.Settings(vault_type=family,custom_sectors=n,quality=quality,
           irregularity=irreg,crown_mode="AUTO")
        t=time.perf_counter();d,report=protected_run(s)
        records.append({"family":family,"sectors":n,"quality":quality,
          "irregularity":irreg,"seconds":round(time.perf_counter()-t,3),
          "test_status":"PASS","QA":report["geometry_QA"],
          "R16_codes":report["guard_POSTBUILD"].get("warning_codes",[])})
    # Negative tests: hard stop BEFORE generating or replacing anything.
    cases={}
    s=old.Settings(crown_mode="MANUAL",crown_Z=3010.)
    try:protected_run(s)
    except CrownBelowArchApex:cases["below_apex"]="REJECTED_AS_REQUIRED"
    else:raise AssertionError("BELOW-APEX ACCEPTED!")
    s=old.Settings(crown_mode="AUTO",crown_locked=True)
    try:protected_run(s)
    except ValueError as exc:
        assert "LOCKED_CROWN" in str(exc)
        cases["locked_crown_auto"]="REJECTED_AS_REQUIRED"
    else:raise AssertionError("LOCKED CROWN AUTO ACCEPTED")
    s=old.Settings(crown_mode="LEVEL")
    _,r=protected_run(s)
    assert any("LEVEL" in c for c in r["guard_POSTBUILD"]["warning_codes"])
    cases["exact_level_warning"]="PASSED_WITH_WARNING"
    final={"status":"R18_EXPERIMENTAL_REGRESSION_PASS","tests_passed":len(records)+len(cases),
       "tests":records,"negative_and_warning_cases":cases,
       "total_seconds":round(time.perf_counter()-start,2),
       "R16_guard_and_original_R17_hashes":hashes(),
       "original_cathedral_generators_untouched":True,
       "architectural_validation":False,"historical_validation":False,
       "structural_validation":False}
    out=HERE/"qa/R18_REGRESSION.json"
    if out.exists():raise FileExistsError(out)
    out.write_text(json.dumps(final,indent=2)+"\n")
    print("R18_TESTS_PASS",final["tests_passed"],"duration",final["total_seconds"],"QA",out,flush=True)

if __name__=="__main__":suite()
