from pathlib import Path
import json
import numpy as np
from phones import load
p=Path('sidehoe-skill-trial/repair/project/scene.json')
d=json.loads(p.read_text()); t=d['tracks']
spec=[('the',717,149,197,0),('most',721,197,253,0),('personal',726,253,347,0),
      ('imessage',741,126,236,1),('assistant',749,236,337,1),('yet',757,337,375,1)]
for name,enter,x0,x1,j in spec:
    ink=[]
    for f in range(enter,766):
        rgb=load('source',f)[321:357 if f<=743 else 349,x0:x1] if j else load('source',f)[290:320 if f>=741 else 331,x0:x1]
        y0=321 if j else 290
        values=rgb.max(2)
        floor=226 if f<=enter+2 else 188
        rows,cols=np.where(values<floor)
        if len(cols)<12:
            continue
        xx=np.percentile(cols,[1,99])
        yy=np.percentile(rows,[1,99])
        alpha=float(np.clip((252-np.percentile(values[rows,cols],16))/230,.14,1))
        ink.append([f,round(float(2*(x0+xx[0])),2),round(float(2*(y0+yy[0])),2),
                    round(float(2*(xx[1]-xx[0]+1)),2),round(float(2*(yy[1]-yy[0]+1)),2),round(alpha,3)])
    print(name,ink[:3],ink[-1])
    t[f'closingInk-{name}']=ink
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
