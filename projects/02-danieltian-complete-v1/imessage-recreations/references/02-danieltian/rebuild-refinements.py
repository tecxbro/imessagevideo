"""Regenerate source02 scoped refinements and a unified authoring preview without mutating the birth-merged base."""
from pathlib import Path
import subprocess,sys
R=Path(__file__).parent
def run(*args):subprocess.run([sys.executable,*map(str,args)],check=True)
for name in ['refine-middle.py','refine-middle-motion.py','refine-middle-avatar-checkpoint.py','refine-middle-final-checkpoint.py','refine-early-end.py','refine-phone-checkpoint.py','refine-flight-checkpoint.py','refine-reasoning-checkpoint.py']:
 run(R/name)
run(R/'apply-middle-refinement.py',R/'scene-final-v9.json',R/'scene-middle-v10.json')
run(R/'apply-early-end-refinement.py',R/'scene-middle-v10.json',R/'scene-combined-v10.json')
