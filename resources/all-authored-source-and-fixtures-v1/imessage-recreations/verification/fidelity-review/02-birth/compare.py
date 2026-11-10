from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,shutil,hashlib
ROOT=Path('/workspace/imessage-recreations');P=ROOT/'verification/fidelity-review/02-birth';shutil.copy2(ROOT/'references/02-danieltian/phonebook-native/track-02.png',P/'source-420.png');frames=list(range(414,421));sheet=Image.new('RGB',(1920,len(frames)*380),'white');d=ImageDraw.Draw(sheet);out=[]
for i,f in enumerate(frames):
 a=Image.open(P/f'source-{f}.png').convert('RGB');aa=np.array(a).astype(float);panes=[a];metrics={}
 for name in ['base','patch']:
  b=Image.open(P/f'{name}-{f}.png').convert('RGB');bb=np.array(b).astype(float);delta=np.abs(aa-bb);mask=np.any(aa<245,2)|np.any(bb<245,2);metrics[name+'_global_mae']=float(delta.mean());metrics[name+'_foreground_mae']=float(delta[mask].mean()) if mask.any() else 0;metrics[name+'_image_sha256']=hashlib.sha256((P/f'{name}-{f}.png').read_bytes()).hexdigest();panes.append(b)
 equal=np.array_equal(np.array(panes[1]),np.array(panes[2]));out.append(dict(frame=f,time=f/30,control=f in [414,420],base_patch_pixels_identical=equal,**metrics))
 for j,b in enumerate(panes):
  im=b.copy();im.thumbnail((640,360));sheet.paste(im,(j*640,i*380+20));d.text((j*640+5,i*380),f'{f} '+['source','v8 baseline','birth patch'][j],fill='red')
sheet.save(P/'comparison.jpg',quality=94);(P/'metrics.json').write_text(json.dumps(out,indent=2));print(json.dumps([{k:v for k,v in m.items() if 'sha256' not in k} for m in out],indent=2))
