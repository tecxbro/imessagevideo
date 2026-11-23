from pathlib import Path
from collections import defaultdict
import json
import sys
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates, gaussian_filter
from scipy.optimize import minimize

root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import Film,layer
scene=json.loads((root/'project/scene.json').read_text())
reference=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def window(t,l,r,b,step):
    return np.mgrid[t:b:step,l:r:step]

measurements={}
for f in (355,356,357,358,359):
 film=Film(scene)
 x,y,s=film.track('sofiaMeasuredCamera',f)
 keyboard_y,=film.track('sofiaKeyboardY',f)
 plate=film.thread_plate('sofia',f,keyboard_y)
 inside=Image.new('L',plate.size)
 ImageDraw.Draw(inside).rounded_rectangle((14,14,385,812),52,fill=255)
 plate.putalpha(inside)
 margin=85
 canvas=layer(1000+2*margin,1000+2*margin)
 film.expose_phone(canvas,plate,x+margin,y+margin,s,0,0)
 rgb=np.asarray(canvas.convert('RGBa'),dtype=np.float32)
 signal=(253*rgb[:,:,3]/255-rgb[:,:,:3].mean(2))
 target=253-np.asarray(Image.open(reference/f'{f:06d}.png'),dtype=np.float32).mean(2)
 records=scene['sofiaPullbackOptics'][str(f)]
 row={}
 for name,bands in (
    ('history',[(0,35,835,222,4),(225,367,553,309,3)]),
    ('composerAndKeyboard',[(732,0,916,853,4),(853,0,918,1000,4)]),
 ):
    prior=records[name]
    if prior[-1]==0:continue
    ranges=[window(*t) for t in bands]
    coeff=[1,.52] if name=='history' else [.63,1]
    yy=np.concatenate([y.flatten() for y,x in ranges])+margin
    xx=np.concatenate([x.flatten() for y,x in ranges])+margin
    lock=target[yy-margin,xx-margin]
    wt=np.concatenate([np.full(y.size,w) for w,(y,_x) in zip(coeff,ranges)])
    focus=[0,.7,1.35,2.1,3.0,3.8,4.8,6,7.5]
    initial=prior.copy()
    trials=[]
    for sigma in focus:
        lens=gaussian_filter(signal,sigma) if sigma else signal
        def error(q):
            dx,dy,sx,sy,alpha=q
            stack=0
            for ray in np.linspace(-.5,.5,9):
                stack += map_coordinates(lens,(yy-dy-sy*ray,xx-dx-sx*ray),order=1,prefilter=False)
            delta=stack*(alpha/9)-lock
            # Include both the average miss and large visible strokes in the fit.
            return float(np.mean((abs(delta)+delta*delta*.007)*wt))
        lims=[(initial[0]-13,initial[0]+13),(initial[1]-10,initial[1]+10),
              (min(0,initial[2])-12,max(0,initial[2])+12),
              (min(0,initial[3])-12,max(0,initial[3])+12),(0,1)]
        opt=minimize(error,initial,bounds=lims,method='Powell',options={'maxiter':12,'ftol':.002})
        score=min(opt.fun,error(initial))
        point=opt.x if score==opt.fun else initial
        trials.append((score,[*np.round(point,3).tolist(),sigma],error(prior) if sigma==0 else None))
    best=min(trials,key=lambda q:q[0])
    print(f,name,[round(x[0],4) for x in trials],best,flush=True)
    row[name]=best[1]
 measurements[f]=row
(root/'shutter-focus.json').write_text(json.dumps(measurements,indent=2)+'\n')
