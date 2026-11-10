from pathlib import Path
import sys,subprocess,time,json
import numpy as np
from PIL import Image
r=Path('/workspace/imessage-recreations');sys.path.insert(0,str(r/'engines'));from run_alternative_batch import method_slot,active_any_worker
out=r/'outputs/alternative-methods/preflight/04-v15-engine'
with method_slot('motion-canvas'):
 while active_any_worker('motion-canvas'):time.sleep(2)
 subprocess.run(['node','engines/fixtures/shadow-opacity/capture_probe.mjs','--scene','outputs/04-poke/final-v15/scene.json','--runtime','engines/motion-canvas-runtime.mjs','--frames','575,758','--out-dir',str(out)],cwd=r,check=True)
base=Path(json.load(open(r/'outputs/04-poke/gsap.mp4.render.json'))['frameDirectory'])
rows=[]
for f in (575,758):
 a=np.array(Image.open(out/f'{f:06}.png').convert('RGB'),dtype=float);b=np.array(Image.open(base/f'{f:06}.png').convert('RGB'),dtype=float);rows.append({'frame':f,'nativeMcVsGsapPngMae':float(abs(a-b).mean()),'maxChannelDifference':float(abs(a-b).max())})
(out/'report.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows,flush=True)
