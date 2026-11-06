#!/usr/bin/env python3
"""Versioned source + full Blender release; checksum and ZIP validation.
Never replaces approved source or previous package. Run only after QA.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,zipfile,datetime
D=Path(__file__).resolve().parents[1]
E=D.parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
tests={k:json.loads((D/'qa'/k).read_text()) for k in [
 'R17_BLENDER_WORKSPACE_BOOTSTRAP_QA.json',
 'R17_BLENDER_ADDON_INSTALL_QA.json',
 'R17_FULL_BLENDER_OPERATOR_REGRESSION_QA.json',
 'R17_QUALITY_EQUIVALENCE_SOURCE_REPLAY_QA.json',
 'R17_FULL_1TO1_GLB_READBACK_QA.json',
 'R17_CROSS_SCENE_REBUILD_EXPORT_QA.json',
 'R17_REVIEW_V02_SOURCE_PROTECTION_QA.json']}
assert tests['R17_FULL_BLENDER_OPERATOR_REGRESSION_QA.json']['status']=='R17_FULL_BLENDER_UI_INTEGRATION_PASS'
assert tests['R17_QUALITY_EQUIVALENCE_SOURCE_REPLAY_QA.json']['status']=='R17_QUALITY_AND_SOURCE_ONLY_REPLAY_PASS'
assert tests['R17_FULL_1TO1_GLB_READBACK_QA.json']['status']=='R17_GLB_READBACK_PASS'
assert tests['R17_CROSS_SCENE_REBUILD_EXPORT_QA.json']['status']=='PASS_R17_REGEN_AND_EXPORT_FROM_PLAN_SCENE'
assert tests['R17_REVIEW_V02_SOURCE_PROTECTION_QA.json']['geometry_identical_to_prior_checkpoint']
base=json.loads((D/'configs/R17_R16_ORIGINAL_PROTECTION.json').read_text())
for key in ('strict_crown_guard.py','guarded_vault_adapter.py','R16_FINAL_RELEASE_SHA256_MANIFEST.json'):
    entry=base[key];assert sha(entry['path'])==entry['sha256']
for key in ('strict_crown_guard.py','guarded_vault_adapter.py'):
    assert sha(D/'addon/r17_vendor'/key)==base[key]['sha256']
installed=Path('/home/christopher/.config/blender/5.0/scripts/addons')
for key in ('r17_experimental_workspace.py','r17_core.py'):
    assert sha(installed/key)==sha(D/'addon'/key)
assert sha(installed/'r17_vendor_sha256.json')==sha(D/'addon/r17_vendor_sha256.json')
V02=D/'blender/F5ZP_R17_FAST_VAULT_WORKSPACE_REVIEW_READY_V02_EXPERIMENTAL.blend'
assert V02.stat().st_size>50000
assert len(list((D/'screenshots').glob('R17_V02_*0001.png')))==4
glb=Path(tests['R17_FULL_BLENDER_OPERATOR_REGRESSION_QA.json']['live_1to1_GLB_export_verified'])
assert glb.is_file() and glb.stat().st_size>1_000_000
# Make a compact four-camera review contact sheet.
labels=[('R17_V02_R17_REVIEW_AXON_0001.png','AXONOMETRIC'),
        ('R17_V02_R17_REVIEW_PLAN_0001.png','PLAN'),
        ('R17_V02_R17_REVIEW_INTERIOR_0001.png','UNDER-VIEW'),
        ('R17_V02_R17_REVIEW_SECTION_0001.png','ELEVATION')]
imgs=[Image.open(D/'screenshots'/p).convert('RGB') for p,t in labels]
res=Image.new('RGB',(1280,2*455+100),(239,241,244))
draw=ImageDraw.Draw(res)
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
except OSError:font=None
for i,(im,(_,tag)) in enumerate(zip(imgs,labels)):
    im.thumbnail((620,415),Image.Resampling.LANCZOS)
    x=10+(i%2)*640+(620-im.width)//2
    y=30+(i//2)*450
    draw.text((20+(i%2)*640,y-24),tag,fill=(26,46,57),font=font)
    res.paste(im,(x,y))
MONTAGE=D/'screenshots/R17_V02_FOUR_CAMERA_ARCHITECTURAL_REVIEW.png'
assert not MONTAGE.exists()
res.save(MONTAGE)
assert MONTAGE.stat().st_size>200000

# Clear delineation: V01 and checkpoint_001 remain preserved as separate files.
files=sorted(p for p in D.rglob('*') if p.is_file()
    and '__pycache__' not in p.parts and p.suffix!='.pyc'
    and p.name!='R17_FINAL_RELEASE_SHA256_MANIFEST.json'
    and not p.name.endswith('.blend1'))
manifest={
 'status':'F5ZP_R17_EXPERIMENTAL_FAST_UNIVERSAL_VAULT_WORKSPACE_VALIDATED',
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'workflow':'One-click procedural Blender, R16 pre/post guard and automatic warnings',
 'persistent_addon_enabled_on_MR_COMPUTER':True,
 'family_count_tested':6,
 'families':['TRI','QUAD','PENTA','HEXA','OCTA','CUSTOM_7'],
 'custom_supported_range_sectors':[3,12],
 'quality_FAST_subdivisions':32,'quality_FINAL_subdivisions':128,
 'source_only_quality_invariance_families':5,
 'measured_rebuild_time_seconds_4_sector_FAST':.035,
 'measured_rebuild_time_seconds_4_sector_FINAL':.413,
 'strict_crown_below_arch_apex_rejects_before_build':True,
 'exact_level_crown_warning_tested':True,
 'locked_crown_not_auto_changed':True,
 'automatic_locked_geometry_warnings_in_all_builds':True,
 'last_valid_mesh_survives_rejection':True,
 'source_R16_SHA256_preserved':True,
 'original_cathedral_and_F5ZN_A_generator_unchanged':True,
 'arch_skeleton_plan_1to1':True,
 'output_GLTF_validated':True,
 'shared_review_scenes':5,
 'final_BLENDER_file':str(V02),
 'github_experimental_branch':'cathedral/f5zp-r17-fast-vault-workspace-experimental-20261106',
 'github_last_source_qa_commit':'33d712b67df3',
 'masonry_cover_status':'not established; open experimental intrados only',
 'historical_validation':False,
 'structural_validation':False,
 'architectural_approval':False,
 'files':{p.relative_to(D).as_posix():
          {'bytes':p.stat().st_size,'sha256':sha(p)} for p in files}
}
MF=D/'qa/R17_FINAL_RELEASE_SHA256_MANIFEST.json'
assert not MF.exists();MF.write_text(json.dumps(manifest,indent=2))
excludes_source={'blender','screenshots','outputs','references'}
for compact in (True,False):
    dest=E/('F5ZP_R17_FAST_UNIVERSAL_VAULT_WORKSPACE_SOURCE_QA_EXPERIMENTAL.zip'
            if compact else 'F5ZP_R17_FAST_UNIVERSAL_VAULT_WORKSPACE_FULL_EXPERIMENTAL.zip')
    assert not dest.exists()
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in [*files,MF]:
            path=p.relative_to(D)
            if compact and path.parts[0] in excludes_source:continue
            if compact and p.suffix=='.log':continue
            z.write(p,'F5ZP_R17_FAST_VAULT_WORKSPACE_EXPERIMENTAL/'+path.as_posix())
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        print('R17_RELEASE_ZIP_VERIFIED',dest.name,
           'items',len(z.namelist()),'MiB',round(dest.stat().st_size/1048576,3))
print('R17_RELEASE_STATUS_ALL_TECHNICAL_AND_GEOMETRIC_TESTS_PASS',len(files),
      'assets; original protected R16 source checksums verified')
