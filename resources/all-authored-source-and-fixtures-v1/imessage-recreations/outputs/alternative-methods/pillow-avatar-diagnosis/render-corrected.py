from pathlib import Path
import json,importlib.util,sys,numpy as np,cv2
from PIL import Image
R=Path('/workspace/imessage-recreations');sp=importlib.util.spec_from_file_location('conditioned',R/'engines/render_pillow.conditioning-experiment.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
sp=importlib.util.spec_from_file_location('cmp',R/'verification/compare.py');cmp=importlib.util.module_from_spec(sp);sp.loader.exec_module(cmp)
S=R/'outputs/03-photon-mini/final-v18/scene.json';scene=json.loads(S.read_text());m.register_fonts(scene,str(S.parent));out=R/'outputs/alternative-methods/pillow-avatar-diagnosis/conditioned';out.mkdir(exist_ok=True)
frames=list(range(436,480))+list(range(486,495))+[435,480,485,495,536];rows=[]
for f in frames:
 im=m.render(scene,f/scene['fps'],str(S.parent),1);im.save(out/f'{f:06}.png',compress_level=1)
 g=np.asarray(Image.open(R/f'outputs/03-photon-mini/frames-gsap/{f:06}.png').convert('RGB'),dtype=np.int16);old=np.asarray(Image.open(R/f'outputs/03-photon-mini/cache/pillow/{f:06}.png').convert('RGB'),dtype=np.int16);new=np.asarray(im,dtype=np.int16)
 before=float(abs(g-old).mean());after=float(abs(g-new).mean());sm,_=cmp.ssim_map(cv2.resize(g.astype('uint8'),(480,270)),cv2.resize(new.astype('uint8'),(480,270)))
 rows.append({'frame':f,'beforeMae':before,'afterMae':after,'ssim480':float(sm.mean()),'oldNewMax':int(abs(old-new).max())});print(json.dumps(rows[-1]),flush=True)
(out/'metrics.json').write_text(json.dumps(rows,indent=2)+'\n')
