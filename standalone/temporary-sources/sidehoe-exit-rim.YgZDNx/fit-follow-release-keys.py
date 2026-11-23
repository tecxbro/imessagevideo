"""Measure key faces and letter ink independently during the follow-up withdrawal."""
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image
from render import Film

w=Path(sys.argv[1])
root=w/'follow-next'
config=root/'scene.json'
ref=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
current=json.loads(config.read_text())
previous=Film(current)
output={}
for frame in range(691,694):
    key=str(frame)
    entry=current['threadRegistration']['follow'][key]
    pic=np.asarray(Image.open(ref/f'{frame:06}.png').convert('RGB'),np.int16)
    rows=[]
    for (x,y,pitch,width,height,count),letters in zip(entry['keys'][2],('QWERTYUIOP','ASDFGHJKL','ZXCVBNM')):
        found=[]
        for i in range(len(letters)):
            cx=x+pitch*i+width/2
            # Scan through the clear top of each individual cap and its center band.
            l,r=round(cx-pitch*.50),round(cx+pitch*.5)
            t,b=max(0,round(y-7)),min(1000,round(y+height+8))
            if t>=993 or r>=1000:
                break
            expected_y=round(y-t)+round(height*.145)
            mask=pic[t:b,l:r,0]
            bright=mask[max(0,expected_y-3):expected_y+3].mean(0)>239
            real=np.flatnonzero(bright)
            if not len(real):
                break
            cap_cols=np.arange(real[0]+round(width*.20),real[-1]-round(width*.17)+1)
            top_bottom=np.flatnonzero(np.percentile(mask[:,cap_cols],84,axis=1)>239)
            if not len(top_bottom):
                break
            cap=[l+int(real[0]),t+int(top_bottom[0]),l+int(real[-1]),t+int(top_bottom[-1])]
            a,c,d,e=cap
            if abs((d-a)-width)>11 or abs((e-c)-height)>13:
                break
            left=a+round(width*.10)
            top=c+round(height*.14)
            ink=pic[top:e-round(height*.13),left:d-round(width*.095),0]
            yy,xx=np.where(ink<134)
            if len(xx)<18:
                break
            box=[left+int(xx.min()),top+int(yy.min()),int(xx.max()-xx.min()+1),int(yy.max()-yy.min()+1)]
            found.append([cap,box])
        rows.append(found if len(found)==len(letters) else None)
    baseline=np.asarray(previous.frame(frame),np.int16)
    entry['keyPoses']=rows
    new=np.asarray(Film(current).frame(frame),np.int16)
    a,b=(np.abs(pic-c) for c in (baseline,new))
    print(frame,[len(r) if r else 0 for r in rows],float(a[708:].mean()),float(b[708:].mean()),
          float(a.mean()),float(b.mean()),flush=True)
    if float(b.mean())<float(a.mean()):
        output[key]=rows
    else:
        entry.pop('keyPoses')
(w/'follow-release-keys.json').write_text(json.dumps(output,indent=2)+'\n')
config.write_text(json.dumps(current,indent=2)+'\n')
