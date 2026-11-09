from pathlib import Path
import bpy
p=Path('/home/christopher/tab.py')
assert p.is_file()
o=bpy.ops.preferences.keyconfig_import(filepath=str(p),keep_original=False)
active=bpy.context.window_manager.keyconfigs.active
found=bpy.context.window_manager.keyconfigs.get('tab')
print('R50_KEYMAP_TEST',o,'active',active.name if active else None,'exists',found is not None,'items',sum(len(m.keymap_items) for m in found.keymaps) if found else 0,flush=True)
assert active is not None and active.name=='tab'
