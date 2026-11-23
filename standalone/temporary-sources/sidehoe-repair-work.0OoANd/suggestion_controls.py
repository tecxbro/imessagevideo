from pathlib import Path
import json
import numpy as np
from phones import load, runs
p=Path('sidehoe-skill-trial/repair/project/scene.json')
d=json.loads(p.read_text()); t=d['tracks']
y_run=[]
for f, x,y,w,h in t['sofiaSuggestedBounds']:
    if f<341:
        continue
    right=x+w
    left=max(0, int((right-173)/2))
    top=int((y+h+1)/2)
    image=load('source',f)
    rgb=image[top:top+45,left:min(500,round(right/2)+6)]
    r,g,b=rgb.transpose(2,0,1)
    pink=(b-r>5)&(b-g>9)&(r>165)&(g>143)&(r-g>-21)
    indices=np.argwhere(pink)
    if len(indices)>15:
        ys=np.percentile(indices[:,0],[3,97])
        xs=np.percentile(indices[:,1],[6,98])
        extent=[float(v) for v in (2*(left+xs[1]),2*(top+ys[0]),2*(ys[1]-ys[0]+1))]
        y_run.append([f,*extent])
print('send',y_run)
t['sofiaSendMeasurement']=y_run
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
