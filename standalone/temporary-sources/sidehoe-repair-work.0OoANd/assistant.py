from pathlib import Path
import json
import numpy as np
from phones import load,track
p=Path('sidehoe-skill-trial/repair/project')
d=json.loads((p/'scene.json').read_text())
t=d['tracks']
placement=[]
ripple={}
for f in range(134,162):
    img=load('source',f)
    y0=track('assistantY',f)[0]/2
    dark=(img.max(2)<100)
    y_range=slice(round(y0)+90,min(500,round(y0)+130))
    if y_range.stop-y_range.start<5:
        l,r=26,474
    else:
        hits=dark[y_range].sum(0)>(y_range.stop-y_range.start)*.39
        left,right=np.flatnonzero(hits[:72]),np.flatnonzero(hits[428:])+428
        l,r=(left.min(),right.max()+1) if len(left) and len(right) else (26,474)
    ys=[]
    for local in np.linspace(.23,.77,17):
        x=round(l+local*(r-l))
        span=dark[max(0,round(y0)-17):round(y0)+34,x-1:x+2]
        hits=np.flatnonzero(span.sum(1)>1)
        ys.append(int(hits[0]+max(0, round(y0)-17)) if len(hits) else round(y0))
    base=np.percentile(ys,34)
    placement.append([f,round(float(l)*2,2),round(float(base*2),2),round(float(r-l)*2,2)])
    if f in (135,136,137):
        ripple[str(f)]=[[round(i*900,3),round((base-y)*2,3)] for i,y in zip(np.linspace(.23,.77,17),ys)]
t['assistantMeasuredPosition']=placement
d['measuredRimDisplacement']=ripple
(p/"scene.json").write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
f=p/'render.py';s=f.read_text()
s=s.replace('def lens_ripple(image, amplitude):','def lens_ripple(image, displacement_samples):')
s=s.replace('''    def displacement(x):
        local = (x-w*.49)/(w*.34)
        return amplitude*np.exp(-local*local)*np.sin((x-w*.50)*.104)''','''    samples=[(0,0),*displacement_samples,(w,0)]
    px,py=zip(*samples)
    def displacement(x):
        return np.interp(x,px,py)''')
s=s.replace('''        y,=self.track("assistantY",f)''','''        x,y,width=self.track("assistantMeasuredPosition",f)''')
s=s.replace('''            curved = lens_ripple(body, {135: 8, 136: 13, 137: 6}[f])
            body = apply_fringe(curved, shift, shift*.55)
        composite(im,body,50,y)''','''            curved=lens_ripple(body,self.s["measuredRimDisplacement"][str(f)])
            body=apply_fringe(curved,shift*.80,shift*.48)
        composite(im,body.resize((round(width),body.height),Image.Resampling.BICUBIC),x,y)''')
f.write_text(s)
