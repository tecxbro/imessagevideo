from pathlib import Path
from PIL import Image
import numpy as np,json
old=Path('/tmp/sidehoe-hyperframes.wG3QA2')
tmp=Path('/tmp/sidehoe-optical-path').read_text()
tracks=json.loads((Path(tmp)/'project/scene.json').read_text())['tracks']
pose=dict((f,(x,y,s)) for f,x,y,s in tracks['sofiaMeasuredCamera'])
for f in range(320,354):
 x,y,s=pose[f]
 def profile(k):
  a=np.asarray(Image.open(old/k/f'{f:06}.png').convert('RGB')).astype(np.float32)
  mid=a[:,round(420):round(581)].mean(axis=(1,2))
  top=np.flatnonzero(mid[:max(19,int(y+60))]<185)
  upper=float(top[0]) if top.size else None
  keys=np.mean(a[:,max(0,round(x+34*s)):min(1000,round(x+369*s)),:],axis=(1,2))
  d=np.mean(keys[:-1][list(range(0,len(keys)-1))].reshape(-1,1),axis=1)
  dif=keys[:-4]-keys[4:]
  topkeyboard=round(np.interp(f,[320,326,331,335,338,341,346,353],[557,632,675,708,756,716,733,738]))
  n=50
  strongest=int(np.argmax(dif[topkeyboard-n:topkeyboard+n])+topkeyboard-n+2)
  return (upper,strongest,round(float(dif[strongest-2]),1))
 print(f,profile('source-stage'),profile('complete-motion-frames'))
