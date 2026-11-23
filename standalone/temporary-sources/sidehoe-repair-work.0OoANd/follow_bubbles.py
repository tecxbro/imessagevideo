from pathlib import Path
import json
import numpy as np
from phones import load,runs
p=Path('sidehoe-skill-trial/repair/project/scene.json')
scene=json.loads(p.read_text()); t=scene['tracks']
for label,nominal in [('followMessageLift',221),('followLowerLift',423)]:
    keys=[[624,0]]
    for f,x,y,s in t['followMeasuredCamera']:
        if f<629:
            continue
        rgb=load('source',f)
        x0=max(0,int((x+(145 if nominal==221 else 53)*s)/2))
        x1=min(500,round((x+(360 if nominal==221 else 306)*s)/2))
        y0=max(0,int((y+(nominal-74)*s)/2))
        y1=min(500,round((y+(nominal+49)*s)/2))
        if y0>=y1:
            continue
        r,g,b=rgb[y0:y1,x0:x1].transpose(2,0,1)
        if nominal==221:
            mask=(g-r>10)&(b-r>13)&(b>214)&(r>140)
        else:
            mask=(r>=193)&(r<241)&(g>=193)&(g<241)&(abs(r-g)<8)&(abs(r-b)<13)
        runs_found=runs(mask.sum(1)>round((x1-x0)*.42))
        if not len(runs_found):
            continue
        ending=y0+max(runs_found,key=lambda q:q[1]-q[0])[1]
        lift=(2*ending-y)/s-nominal
        if abs(lift)>42:
            continue
        keys.append([f,round(float(lift),2)])
    print(label,keys[1::4])
    t[label]=keys
scene['followContact']['measuredContactFrame']=675
p.write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
