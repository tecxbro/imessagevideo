"""Reproduce source02 scoped v11 refinements in dependency order.
Requires the declared native source measurement PNGs; never renders them as whole-frame assets.
Root-owned group-797/phonebook follow-ups compose afterward by stable ID.
"""
from pathlib import Path
import subprocess,shutil,sys
R=Path(__file__).resolve().parent
shutil.copyfile(R/'middle-refinement.json',R/'peak-middle-refinement.json')
steps=['refine-middle-every-frame.py','refine-v11-middle-checkpoint.py','refine-v11-card-edge.py','refine-v11-card-textures.py','build-v11-boundary.py','refine-v11-phone-exit.py','build-v11-end.py']
for name in steps:
 subprocess.run([sys.executable,'-m','py_compile',str(R/name)],check=True)
 subprocess.run([sys.executable,str(R/name)],check=True)
subprocess.run([sys.executable,str(R/'apply-v11-refinements.py'),str(R/'scene-combined-v10.json'),str(R/'scene-combined-v11.json')],check=True)
print('Source02 v11 rebuilt. Run the scoped rendered-frame proof and native checkpoint/encoded comparisons before freezing.',flush=True)
