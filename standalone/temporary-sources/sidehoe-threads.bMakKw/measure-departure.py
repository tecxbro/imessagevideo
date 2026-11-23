from pathlib import Path
from PIL import Image
import numpy as np,json,sys
r=Path(__file__).parent;d=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage'); old=Path('/tmp/sidehoe-reveal-clean.DeKHma/frames')
sys.path.insert(0,str(r/'project'))
from render import interpolate
spec=json.loads((r/'project/scene.json').read_text());t=spec['tracks']
results={}
for f in range(360,403):
 imgs=[np.asarray(Image.open(q/f'{f:06}.png').convert('RGB')) for q in (d,old)]
 arr=imgs[0].astype('int16')
 R,G,B=np.moveaxis(arr,2,0)
 expected=interpolate(t['sendOutgoingOpacity'],f)[0]
 new=[]
 for index,role in enumerate(('sendReplyBox','sendSuggestionBox')):
  x,y,X,Y=interpolate(t[role],f);h=Y-y
  a,b,c,e=map(round,(x+(X-x)*.07,y+h*.26,X-(X-x)*.20,Y-h*.17))
  hues=R[b:e,a:c]
  base_r=float(np.percentile(hues,12))
  opacity=np.clip((253-base_r)/(253-(18 if index==0 else 15)),0,1)
  z=[]
  zones=[(.16,.84)] if index==0 else [(.10,.51),(.51,.89)]
  for i,(v0,v1) in enumerate(zones):
   l0,t0,r0,b0=map(round,(x+(X-x)*.032,y+h*v0,X-(X-x)*.08,y+h*v1))
   rr=R[t0:b0,l0:r0];gg=G[t0:b0,l0:r0];bb=B[t0:b0,l0:r0]
   # White ink absorbs the blue fill's chroma. Keep the fully covered core
   # inside the bubble shoulder and outside the rounded caps.
   p=(rr>base_r+120*opacity)&(rr>gg-50*opacity)&(bb>=220)
   rs=np.flatnonzero(p.sum(1)>6)
   cs=np.flatnonzero(p.sum(0)>4)
   if len(rs)<7 or len(cs)<35:
    z.append(None)
    continue
   x0=int(l0+cs[0]); w=int(cs[-1]+1-cs[0])
   top=int(t0+rs[0]); height=int(rs[-1]+1-rs[0])
   z.append([x0,top,w,height])
  new.append([float(opacity),z,base_r])
 results[f]=new
 if f in (360,364,374,381,390,395,397,398,399,400,401,402): print(f,new)
(r/'send-fit.json').write_text(json.dumps(results,indent=2))
