#!/usr/bin/env python3
"""Install only NEW isolated R17 addon files for persistent Blender UI.
Does not edit factory, approved cathedral, or other Blender addons.
Refuses to overwrite differing preexisting R17 installations.
"""
import bpy,pathlib,hashlib,shutil,sys,json
D=pathlib.Path(__file__).resolve().parents[1]
source=D/'addon'
dest=pathlib.Path(bpy.utils.user_resource(
    'SCRIPTS',path='addons',create=True))
assert dest.is_dir()
paths=['r17_experimental_workspace.py','r17_core.py',
       'r17_vendor_sha256.json',
       'r17_vendor/strict_crown_guard.py',
       'r17_vendor/guarded_vault_adapter.py']
installed=[]
for item in paths:
    src=source/item
    target=dest/item
    assert src.is_file(),src
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        if hashlib.sha256(target.read_bytes()).digest()!=hashlib.sha256(src.read_bytes()).digest():
            raise FileExistsError('R17 addon version differs. No automatic overwrite: '+str(target))
    else:
        shutil.copy2(src,target)
    assert hashlib.sha256(src.read_bytes()).digest()==hashlib.sha256(target.read_bytes()).digest()
    installed.append(str(target))
# Activate ONLY our new module; do not change other enabled addons.
if str(dest) not in sys.path:sys.path.insert(0,str(dest))
bpy.ops.preferences.addon_enable(module='r17_experimental_workspace')
assert 'r17_experimental_workspace' in bpy.context.preferences.addons
assert hasattr(bpy.types.Scene,'r17_props')
bpy.ops.wm.save_userpref()
p=D/'qa/R17_BLENDER_ADDON_INSTALL_QA.json'
assert not p.exists()
p.write_text(json.dumps({'status':'R17_PERSISTENT_ADDON_INSTALLED',
  'addon_location':str(dest),
  'files_source_matched_SHA256':installed,
  'addon_enabled_and_blender_preferences_saved':True,
  'other_addons_or_approved_architecture_modified':False,
  'blender_version':bpy.app.version_string},indent=2))
print('R17_ADDON_PERSISTENT_UI_ENABLED',str(dest),
      'source_files',len(installed),flush=True)
