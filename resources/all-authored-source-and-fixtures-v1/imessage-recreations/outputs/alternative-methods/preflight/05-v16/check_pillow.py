from pathlib import Path
import json,sys,hashlib
import numpy as np
from PIL import Image,ImageDraw
root=Path('/workspace/imessage-recreations');sys.path.insert(0,str(root/'engines'));import render_pillow as rp
scenePath=root/'outputs/05-linq/final-v16/scene.json';s=json.load(open(scenePath));rp.register_fonts(s,str(scenePath.parent));out=root/'outputs/alternative-methods/preflight/05-v16';rows=[]
for f in (259,1105):
 new=rp.render(s,f/s['fps'],str(scenePath.parent));new.save(out/f'{f:06}-pillow.png');baseline=Image.open(root/f'outputs/05-linq/frames-gsap/{f:06}.png').convert('RGB');delta=abs(np.array(new,dtype=float)-np.array(baseline,dtype=float));rows.append({'frame':f,'nativePillowVsGsapPngMae':float(delta.mean()),'maximumChannelDifference':float(delta.max()),'sceneSha256':hashlib.sha256(scenePath.read_bytes()).hexdigest()});print(rows[-1],flush=True);(out/'pillow-parity.json').write_text(json.dumps(rows,indent=2)+'\n');sheet=Image.new('RGB',(s['width']*2,s['height']),'#eee');sheet.paste(baseline,(0,0));sheet.paste(new,(s['width'],0));sheet.save(out/f'{f:06}-contact.jpg')
