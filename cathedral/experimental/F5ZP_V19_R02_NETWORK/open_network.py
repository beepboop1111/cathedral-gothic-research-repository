from pathlib import Path
import subprocess
p=Path(__file__).resolve().parent
subprocess.Popen(['blender',str(p/'V19_R02_NETWORK_EXPERIMENTAL.blend'),'--python',str(p/'network_workspace.py')])
