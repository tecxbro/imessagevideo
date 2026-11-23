import json
from pathlib import Path
from PIL import Image
import numpy as np
base=Path('/tmp/sidehoe-hyperframes.wG3QA2')
root=Path('/tmp/sidehoe-optical-path').read_text()
scene=json.loads((Path(root)/'project/scene.json').read_text())
t=scene['tracks']
def track(name,f):
 a=np.asarray(t[name])
 return [np.interp(f,a[:,0],a[:,i]) for i in range(1,a.shape[1])]
def frame(f):
 return np.asarray(Image.open(base/'source-stage'/f'{f:06}.png').convert('RGB'),dtype=np.int16)
res={}
for f in range(397,416):
 a=frame(f)
 x,y=track('calendarDay',f)
 l,r=max(0,round(x)-75),min(1000,round(x)+75)
 t0,b=max(0,round(y)-70),min(1000,round(y)+70)
 values=a[t0:b,l:r]
 R,G,B=values.transpose(2,0,1)
 scores=np.clip(R-G-9,0,255)*(R>B+7)
 yy,xx=np.mgrid[t0:b,l:r]
 mass=scores.sum()
 if not mass: continue
 x=(scores*xx).sum()/mass
 y=(scores*yy).sum()/mass
 sx=np.sqrt((scores*(xx-x)**2).sum()/mass)
 sy=np.sqrt((scores*(yy-y)**2).sum()/mass)
 med=np.median(values[scores>=.8*scores.max()],axis=0)
 res[f]=[f,*[round(float(x),3) for x in (x,y,sx,sy,mass,*med)]]
 print(f,res[f][1:])
(Path(root)/'calendar-date.json').write_text(json.dumps(res,indent=2))
res={}
for f in range(390,403):
 a=frame(f)
 vals=[]
 for key in ('sendReplyBox','sendSuggestionBox'):
  x,y,x1,b=track(key,f)
  l,r=round(x+(.45*(x1-x))),round(x+(.78*(x1-x)))
  top,bottom=round(y)-25,min(1000,round(b)+25)
  R,G,B=np.median(a[top:bottom,l:r],axis=1).T
  tint=(B-R)
  maximum=np.max(tint)
  i=np.flatnonzero(tint>maximum*.5)
  # A median of the saturated middle of the band insulates copy and blurred edges.
  use=(tint>=maximum*.87)
  color=np.median(np.stack([R,G,B],axis=1)[use],axis=0)
  def ramp(start):
   d=tint[max(0,start-6):start+6]
   return round(float(np.count_nonzero((d>maximum*.15)&(d<maximum*.85))),2)
  vals.append(tuple([top+int(i[0]),top+int(i[-1])+1,ramp(i[0]),ramp(i[-1]),
                         *[round(float(c),3) for c in color]]))
 res[f]=vals
 print(f,vals)
(Path(root)/'calendar-outgoing.json').write_text(json.dumps(res,indent=2))
