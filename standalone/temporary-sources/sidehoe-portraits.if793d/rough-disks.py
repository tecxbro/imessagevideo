from PIL import Image,ImageDraw,ImageColor
from pathlib import Path
from scipy.ndimage import label,find_objects
import numpy as np,sys,json
root=Path(__file__).parent;sys.path.insert(0,str(root/'project'))
from render import interpolate
d=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
s=json.loads((root/'project'/'scene.json').read_text())
for f in (220,223,226,227,230,240,250,253):
 print('frame',f)
 q=np.array(Image.open(d/f'{f:06}.png').convert('RGB'),dtype=np.int16)
 tracks=s['tracks']['clusterEntrance' if f<=226 else 'clusterVisibleDisks']
 for idx,((name,*_,col),track) in enumerate(zip(s['cluster'],tracks,strict=True)):
  x,y,diam,a=interpolate(track,f)
  r=diam/2
  lo,top,hi,bot=map(round,(max(x-r*1.22,0),max(y-r*1.22,0),min(1000,x+r*1.22),min(1000,y+r*1.22)))
  a=q[top:bot,lo:hi]; baseline=np.array(ImageColor.getrgb(col))
  errors=np.linalg.norm(a-baseline,axis=2)
  rough=(errors<25)
  inside=rough & (errors<np.min(errors)+8)
  if not rough.any(): print(idx,name,'no mask');continue
  vv,uu=np.where(rough)
  color=np.median(a[inside],axis=0).round().astype(int)
  e=np.linalg.norm(a-color,axis=2)
  yy,xx=np.where(e<14)
  hit=np.array([xx.min()+lo,yy.min()+top,xx.max()+lo+1,yy.max()+top+1])
  print(idx,name or '-',*[round(t,1) for t in (x,y,r*2)],color.tolist(),hit.tolist(),len(xx))
