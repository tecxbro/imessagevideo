from pathlib import Path
import sys,subprocess,json,time
import numpy as np
from PIL import Image
root=Path('/workspace/imessage-recreations');sys.path.insert(0,str(root/'engines'));from run_alternative_batch import method_slot,active_any_worker
p=root/'outputs/alternative-methods/preflight/06-v20-shadow';f=613
with method_slot('motion-canvas'):
 while active_any_worker('motion-canvas'):time.sleep(2)
 subprocess.run(['node',str(root/'engines/render_motion_canvas.mjs'),'--scene',str(root/'outputs/06-gallery/final-v20/scene.json'),'--out',str(p/'000613-after.png'),'--frame',str(f)],cwd=root,check=True,stdout=subprocess.DEVNULL)
a=np.array(Image.open(root/f'outputs/06-gallery/frames-gsap/{f:06}.png').convert('RGB'),dtype=float);old=np.array(Image.open(root/f'outputs/06-gallery/cache/motion-canvas/{f:06}.png').convert('RGB'),dtype=float);new=np.array(Image.open(p/'000613-after.png').convert('RGB'),dtype=float);report={'frame':f,'oldMcVsGsapMae':float(abs(a-old).mean()),'newMcVsGsapMae':float(abs(a-new).mean()),'maxDifferenceFromOldMc':float(abs(new-old).max()),'purpose':'Real mixed nonconformal Gaussian+shadow+partial-opacity actor at near-plane size; no production cache change.'};(p/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report,flush=True)
