from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np
R=Path('/workspace/imessage-recreations');D=R/'verification/final/06-gallery/v23';rows=[];cases=[('remotion',552),('html',552),('pillow',552),('motion-canvas',1067),('motion-canvas',1106)]
canvas=Image.new('RGB',(1440,300*len(cases)),'#ddd');draw=ImageDraw.Draw(canvas)
for j,(m,n) in enumerate(cases):
 g=Image.open(R/f'outputs/06-gallery/frames-gsap/{n:06d}.png').convert('RGB');folder=R/f'outputs/06-gallery/frames-{m}' if m in ['remotion','html'] else R/f'outputs/06-gallery/cache/{m}';c=Image.open(folder/f'{n:06d}.png').convert('RGB');A,B=np.array(g).astype(int),np.array(c).astype(int);delta=np.abs(A-B);mask=delta.max(2)>0;y,x=np.where(mask);bb=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None;rows.append({'method':m,'frame':n,'nativeMAEvsG':float(delta.mean()),'maxNativeDelta':int(delta.max()),'nativeDifferenceBBox':bb,'changedPixels':int(mask.sum())});diff=Image.fromarray(np.minimum(255,delta*4).astype('uint8'))
 for xx,im,label in [(0,g,'native G'),(480,c,'native '+m),(960,diff,'4x absolute difference')]:
  im=im.resize((480,270),Image.Resampling.LANCZOS);canvas.paste(im,(xx,j*300+25));draw.text((xx+4,j*300+4),f'{n} {label}',fill='black')
canvas.save(D/'dense-parity-worst-native.jpg',quality=95);(D/'dense-parity-worst-native.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
