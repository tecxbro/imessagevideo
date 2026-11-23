from pathlib import Path
from PIL import Image
import sys,json
import numpy as np
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
flag=sys.argv[1] if len(sys.argv)>1 else 'both'
p=root/'project/scene.json'
s=json.loads(p.read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
before=root/'probe-a'
for f in range(155,162):
    ref,prev=[np.asarray(Image.open(path/f'{f:06}.png').convert('RGB'),dtype=np.int16) for path in (source,before)]
    x,y,w=interpolate(s['tracks']['assistantMeasuredPosition'],f)
    _,iy,_,ih=interpolate(s['tracks']['assistantIslandBox'],f)
    island=(372,round(y+iy),630,round(y+iy+ih))
    l,t,r,b=island
    delta=np.rint(np.median(prev[t+7:b-7,430:555]-ref[t+7:b-7,430:555],axis=(0,1))).astype(int)
    delta=np.clip(delta,0,30).tolist()
    if flag in ('both','island'):
        s['assistantScreenRegistration'][str(f)]['islandShade']=[l+2,t+1,r-1,b-1,delta,round(2+(f-155)*.21,2)]
    if flag not in ('both','bevel'):
        continue
    raw=[]
    start=round(y+200)
    for yy in range(start,995,28):
        values=[]
        for img in (ref,prev):
            strip=img[yy-7:yy+8,871:973].mean((0,2))
            matte=np.median(strip[-14:])
            deepest=np.min(strip)
            indexes=np.flatnonzero(strip<deepest+(matte-deepest)*.61)
            if len(indexes)<8:
                values=[]
                break
            values.extend((129-indexes[-1]-1,129-indexes[0]-1,matte-deepest))
        if not values:
            continue
        a,b,src_gain,u,v,prior_gain=values
        if abs(a-u)>19 or abs(b-v)>21:
            continue
        scale=round(float(np.clip(src_gain/max(2,prior_gain),.75,1.40)),4)
        raw.append([yy,*map(int,(a,b,u,v)),scale])
    if len(raw)>1:
        s['assistantSideBevels'][str(f)]['right']=[24,156,raw]
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
