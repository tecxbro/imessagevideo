"""Measure individual visible key faces while letter exposures remain independent."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image
from render import Film

work=Path(sys.argv[1])
cfg=work/'project/scene.json'
s=json.loads(cfg.read_text())
baseline=json.loads(cfg.read_text())
reference=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
accepted={}
for f in range(693,696):
    k=str(f)
    thread=s['threadRegistration']['follow'][k]
    old=thread.get('keyPoses',[None,None,None])
    target=np.asarray(Image.open(reference/f'{f:06d}.png').convert('RGB'),np.int16)
    src=target[:,:,1]
    base=np.asarray(Film(baseline).frame(f),np.int16)
    key_zone=(slice(675,1000),slice(130,880))
    orig=float(np.abs(base-target)[key_zone].mean())
    result=[list(row) if isinstance(row,list) else [None]*len(keys) for row,keys in
            zip(old,('QWERTYUIOP','ASDFGHJKL','ZXCVBNM'),strict=True)]
    for ri,((x,y,pitch,w,h,count),keys) in enumerate(zip(thread['keys'][2],('QWERTYUIOP','ASDFGHJKL','ZXCVBNM'))):
        for i,letter in enumerate(keys):
            if result[ri][i] or not thread.get('keyInkRegistration',[[],[],[]])[ri][i]:
                continue
            cx=x+i*pitch+w/2
            a,b=round(cx-pitch*.46),round(cx+pitch*.46)
            t,d=max(0,round(y-8)),min(1000,round(y+h+8))
            if t>=988 or b>=1000:
                continue
            view=src[t:d,a:b]
            top_face=max(0,round(y-t+h*.17))
            if not top_face+2<view.shape[0]:
                continue
            peaks=np.quantile(view[max(0,top_face-3):top_face+4],.70,axis=0)
            tonal=np.quantile(view,.80,axis=1)
            indices_x=np.where(peaks>=234)[0]
            indices_y=np.where(tonal>=234)[0]
            if not len(indices_x) or not len(indices_y):
                continue
            left,right=a+indices_x[0],a+indices_x[-1]
            upper,lower=t+indices_y[0],t+indices_y[-1]
            if abs(right-left-w)>11 or abs(lower-upper-h)>13 or abs(left-cx+w/2)>9:
                continue
            glyph=thread['keyInkRegistration'][ri][i]
            ix,iy,iw,ih=glyph[:4]
            result[ri][i]=[[int(left),int(upper),int(right),int(lower)],[ix-iw/2,iy-ih/2,iw,ih]]
    thread['keyPoses']=result
    new=np.asarray(Film(s).frame(f),np.int16)
    score=float(np.abs(new-target)[key_zone].mean())
    full=[float(np.abs(image-target).mean()) for image in (base,new)]
    counts=[sum(pose is not None for pose in row) for row in result]
    print(f,round(orig,4),round(score,4),[round(n,5) for n in full],counts,flush=True)
    if score<orig and full[1]<full[0]:
        accepted[k]=result
    elif 'keyPoses' in baseline['threadRegistration']['follow'][k]:
        thread['keyPoses']=baseline['threadRegistration']['follow'][k]['keyPoses']
    else:
        thread.pop('keyPoses')
cfg.write_text(json.dumps(s,indent=2)+'\n')
(work/'keycap-fit.json').write_text(json.dumps(accepted,indent=2)+'\n')
