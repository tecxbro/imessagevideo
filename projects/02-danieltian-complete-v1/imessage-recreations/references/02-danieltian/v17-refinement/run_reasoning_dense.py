from pathlib import Path
import subprocess,json,os
R=Path(__file__).resolve().parent;ROOT=R.parents[2]
frames=list(range(271,376));subset=[271,272,273,275,280,292,293,295,300,320,350,360,361,363,364,367,370,372,374,375]
probe=R/'reasoning-combined-probe.scene.json'
def run(args):print('RUN',*map(str,args),flush=True);subprocess.run(list(map(str,args)),cwd=ROOT,check=True)
run(['node',R/'prepare_reasoning_probe.mjs',R/'reasoning-combined-candidate.json',probe,','.join(map(str,frames)),'--house'])
D=R/'reasoning-dense-native';D.mkdir(exist_ok=True)
for f in subset:
 original=R/'reasoning-combined-native'/f'{f/30:.3f}.png';target=D/original.name
 if not target.exists():os.link(original,target)
remaining=[f for f in frames if f not in subset]
run(['node','engines/render_checkpoints.mjs','--scene',probe,'--frames',','.join(map(str,remaining)),'--method','gsap','--out',D])
assert all((D/f'{f/30:.3f}.png').exists()for f in frames)
run(['python3',R/'validate_reasoning.py','--directory','reasoning-dense-native','--frames',','.join(map(str,frames)),'--name','reasoning-dense'])
