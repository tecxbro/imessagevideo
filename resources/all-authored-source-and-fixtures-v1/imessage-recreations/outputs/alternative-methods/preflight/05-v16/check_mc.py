from pathlib import Path
import sys,subprocess,json,time
import numpy as np
from PIL import Image
root=Path('/workspace/imessage-recreations');sys.path.insert(0,str(root/'engines'));from run_alternative_batch import method_slot,active_any_worker
out=root/'outputs/alternative-methods/preflight/05-v16';rows=[]
with method_slot('motion-canvas'):
 while active_any_worker('motion-canvas'):time.sleep(2)
 for f in (259,1105):
  path=out/f'{f:06}-motion-canvas.png';subprocess.run(['node',str(root/'engines/render_motion_canvas.mjs'),'--scene',str(root/'outputs/05-linq/final-v16/scene.json'),'--out',str(path),'--frame',str(f)],cwd=root,check=True,stdout=subprocess.DEVNULL)
  native=np.array(Image.open(path).convert('RGB'),dtype=float);web=np.array(Image.open(root/f'outputs/05-linq/frames-gsap/{f:06}.png').convert('RGB'),dtype=float);rows.append({'frame':f,'nativeMcVsGsapPngMae':float(abs(native-web).mean()),'maxChannelDifference':float(abs(native-web).max())});(out/'motion-canvas-parity.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows[-1],flush=True)
