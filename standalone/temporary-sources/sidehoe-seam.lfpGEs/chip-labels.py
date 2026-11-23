from pathlib import Path
import json,sys
from PIL import Image
import numpy as np
p=Path(__file__).parent;sys.path.insert(0,str(p/'project'))
from render import interpolate
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-surface.oiqQZp/final-frames')
cfg=p/'project/scene.json';state=json.loads(cfg.read_text());t=state['tracks']
entries=[]
for f,*boxes in t['sendHandoffControls']:
 fade=interpolate(t['sendOutgoingOpacity'],f)[0] if f>=399 else 1
 row=[f]
 for index in range(2):
  x,y,w,h=boxes[index*4:index*4+4]
  a0,b0,a1,b1=map(round,(x+w*.10,y+h*.21,x+w*.9,y+h*.81))
  for name in (source,prior,p/'calendar'):
   vals=np.asarray(Image.open(name/f'{f:06}.png').convert('RGB'),dtype=float)
   q=vals[b0:b1,a0:a1]
   k=(q.mean(2) < 253-fade*(112 if index==0 else 125))&(np.ptp(q,axis=2)<31)
   rows,cols=np.where(k)
   if len(cols)<10: print(f,index,name.name,'missing'); continue
   x0,y0,u,v=np.round([[cols.min()+a0-x,rows.min()+b0-y,cols.max()-cols.min()+1,rows.max()-rows.min()+1]],2)[0]
   print(f,index,name.name,[int(t) for t in (x0,y0,u,v)])
   if name==source:
    u+=.8
    v+=2
    row.extend(map(float,[x0-.4,y0-1,u,v]))
 if len(row)==9: entries.append(row)
print('complete',len(entries))
t['sendControlInk']=entries
cfg.write_text(json.dumps(state,indent=2)+'\n')
