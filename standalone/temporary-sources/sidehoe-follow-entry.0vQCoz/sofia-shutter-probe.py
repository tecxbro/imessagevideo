from pathlib import Path
import json
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import minimize

root=Path(__file__).parent
sys.path.insert(0,str(root/'clean-dual-project'))
from render import Film, layer
scene=json.loads((root/'clean-dual-project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

class Screen(Film):
    def expose_phone(self, im, plate, x, y, scale, smear, radius, alpha=1, *, vertical_scale=1):
        if hasattr(self,'picture'):
            return
        # Measure the authored screen before blur and before adding the separate rail and prompt.
        clear=layer()
        super().expose_phone(clear,plate,x,y,scale,0,0,1,vertical_scale=vertical_scale)
        self.picture=np.asarray(clear.convert('RGBa'),dtype=np.float32)

samples={}
for f in (355,356,357,358,359):
    film=Screen(scene)
    film.frame(f)
    base=film.picture
    target=np.asarray(Image.open(source/f'{f:06d}.png').convert('RGB'),dtype=np.float32).mean(2)
    points=[(72,0,802,310),(58,748,878,999)]
    out=[]
    for index,(l,t,r,b) in enumerate(points):
        yy,xx=np.mgrid[t:b:4,l:r:4]
        true=target[yy,xx]
        # Shift in both directions, then average a short camera path during one exposure.
        def residual(p):
            ox,oy,sx,sy,alpha=p
            values=[]
            for k in np.linspace(-.5,.5,9):
                px,py=xx-ox-sx*k,yy-oy-sy*k
                tone=map_coordinates(base[:,:,0],(py,px),order=1,prefilter=False)
                mask=map_coordinates(base[:,:,3],(py,px),order=1,prefilter=False)/255
                values.append(tone+(1-mask)*253)
            avg=np.mean(values,axis=0)*alpha+253*(1-alpha)
            return float(np.mean(np.abs(avg-true)))+.0035*np.linalg.norm(p[2:4])
        initial=(0,0,0,0,.82 if f==355 else .28)
        runs=[]
        if f<=357 or index==1:
            seeds=([0,0,31,20,.85],[0,0,7,24,.55],[0,0,10,-15,.65])
        else:
            seeds=([0,0,0,0,.10],)
        for seed in seeds:
            lims=[(-60,60),(-55,55),(-50,50),(-55,55),(.0,1)]
            res=minimize(residual,seed,bounds=lims,method='Powell',options={'maxiter':17,'ftol':.0015})
            runs.append((res.fun,res.x))
        before=residual(initial)
        after,x=min(runs,key=lambda z:z[0])
        out.append([round(before,3),round(float(after),3),[round(float(k),3) for k in x]])
    print(f,out,flush=True)
    samples[f]=out
(root/'sofia-shutter-fit.json').write_text(json.dumps(samples,indent=2)+'\n')
