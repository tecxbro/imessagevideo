"""Reject favorite-label aliases and locate faint real inbox entry separately."""
from pathlib import Path
from PIL import Image
import json,numpy as np
p=Path(__file__).parent;source=p/'measurements-v8/decoded';reference=np.array(Image.open(source/'000030.png').convert('RGB')).mean(2);left,right,top,bottom=330,710,813,867;template=255-reference[top:bottom,left:right]
def feature(c):
    f=c.reshape(c.shape[0],20,-1).mean(2);return f-f.mean(1,keepdims=True)
tf=feature(template);tn=np.linalg.norm(tf);rows=[]
for n in range(10,31):
    a=np.array(Image.open(source/f'{n:06}.png').convert('RGB')).mean(2);best=None
    for y in range(790,1020):
        if y+template.shape[0]>1080:continue
        crop=255-a[y:y+template.shape[0],left:right];f=feature(crop);denom=np.linalg.norm(f)*tn
        score=float((f*tf).sum()/denom)if denom>1e-5 else 0
        if best is None or score>best['score']:
            projection=float((f*tf).sum()/(tf*tf).sum());best=dict(frame=n,time=n*1001/30000,score=score,y=y,scale=1.4,opacity=max(0,min(1,projection*.20784313725490197)))
    rows.append(best)
(p/'measurements-v8/intro-inbox-birth-v11.json').write_text(json.dumps(dict(method='Native30faint real Nikki glyph profile,20horizontalbins, rowmeanremoved; scan onlybelow favorites, robust to uniform haze. Aliases2–9are favorites/captions, not inbox.',reference=[left,top,right,bottom],measurements=rows),indent=2));print(json.dumps(rows,indent=2))
