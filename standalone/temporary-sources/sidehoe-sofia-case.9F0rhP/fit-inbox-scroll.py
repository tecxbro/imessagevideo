"""Fit separate shutter intervals for pinned chrome and independently scrolling rows."""
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image
from render import Film,layer,paint_scroll_plane

p=Path(sys.argv[1]); cfg=p/'inbox-next/scene.json'
s=json.loads(cfg.read_text())
reference=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')


def fit(f):
    k=str(f)
    loaded={**s,'inboxScrollRegistration':{k:deepcopy(s['inboxScrollRegistration'][k])}}
    shot=loaded['inboxScrollRegistration'][k]
    source=Image.open(reference/f'{f:06d}.png').convert('RGB')
    estimate=Film(loaded)
    before=np.asarray(estimate.frame(f),np.int16)
    true=np.asarray(source,np.int16)
    row=layer()
    estimate.inbox_scroll_rows(row,f,shot['rows'],shot['home'],focus=(0,0))
    header=None
    if f<=59:
        shot['chromeExposure']=[0,0,0,0]
        dummy=Film(loaded)
        dummy.inbox_scroll_rows=lambda *args,**kwargs: None
        header=layer()
        dummy.inbox(header,f)
    initial=s['inboxScrollRegistration'][k]
    old_row=initial.get('rowExposure',(.38,max(.12,estimate.track('inboxScrollSmear',f)[0]*.26),0,0))
    old_chrome=initial.get('chromeExposure',(0,0,0,0))
    bounds=(138,0,870,1000)
    # The exposed colors are assessed in the exact stage ROI, with alpha
    # compositing over the unchanged paper on which the film is assembled.
    cells=[im.crop(bounds) if im is not None else None for im in (row,header)]
    target=np.asarray(source.crop(bounds),np.int16)
    def patch(index, q):
        plane=Image.new('RGBA',cells[index].size)
        paint_scroll_plane(plane,cells[index],q)
        return plane
    options=[[*old_row,0],[*old_chrome,0]]
    images=[patch(i,q) if cells[i] is not None else None for i,q in enumerate(options)]
    def compare(rows):
        test=Image.new('RGBA',cells[0].size,(253,253,253,255))
        for exposure in rows:
            if exposure is not None:
                test.alpha_composite(exposure)
        return float(np.abs(np.asarray(test,np.int16)[:,:,:3]-target).mean())
    best=first=compare(images)
    for k0 in range(2 if header else 1):
        params=options[k0]
        for scale in (1,.47):
            for i,d in enumerate((.58,1.36,1.6,2.25,4.0)):
                anchor=params.copy()
                for d0 in (-2,-1,1,2):
                    proposed=anchor.copy()
                    proposed[i]+=d0*d*scale
                    # The row position and shutter are bounded by the existing measured pass.
                    if not (0<=proposed[0]<=4 and 0<=proposed[1]<=12 and abs(proposed[2])<=6 and
                            abs(proposed[3])<=9 and 0<=proposed[4]<=22):
                        continue
                    rendered=patch(k0,proposed)
                    revised=images.copy()
                    revised[k0]=rendered
                    current=compare(revised)
                    if current<best:
                        params,best,images=proposed,current,revised
        options[k0]=params
    live=Film({**s,'inboxScrollRegistration':{k:deepcopy(initial)}})
    setup=live.s['inboxScrollRegistration'][k]
    setup['rowShutter']=[round(v,5) for v in options[0]]
    if header:
        setup['chromeShutter']=[round(v,5) for v in options[1]]
    a,b=[float(np.abs(o-true).mean()) for o in (before,np.asarray(live.frame(f),np.int16))]
    print(f,round(a,6),round(b,6),round(first-best,5),flush=True)
    data={key:setup[key] for key in ('rowShutter','chromeShutter') if key in setup}
    return str(f),data if b<a else None

if __name__=='__main__':
    frames=range(42,102)
    with ProcessPoolExecutor(max_workers=7) as pool:
        accepted={f:v for f,v in pool.map(fit,frames) if v}
    for f,q in accepted.items():
        s['inboxScrollRegistration'][f].update(q)
    cfg.write_text(json.dumps(s,indent=2)+'\n')
    (p/'inbox-scroll-next.json').write_text(json.dumps(accepted,indent=2)+'\n')
