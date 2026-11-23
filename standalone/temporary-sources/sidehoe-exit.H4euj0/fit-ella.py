from pathlib import Path
import json,sys
from PIL import Image
import numpy as np
from scipy.optimize import minimize
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import registered_portrait, composite, blur
scene=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
before=root/'profiles-v1'
result={}
for f in range(287,313):
    entry=scene['profileMotionRegistration'][str(f)]
    rec=entry['actors'][1]
    if rec is None:
        continue
    x,y,w,h=rec['oval']
    left=max(0,round(x-w*.53))
    right=min(1000,round(x+w*.53))
    top=max(0,round(y-h*.53))
    bottom=min(1000,round(y+h*.53))
    box=(left,top,right,bottom)
    a=np.asarray(Image.open(source/f'{f:06d}.png').convert('RGB').crop(box),dtype=np.float32)
    z=np.asarray(Image.open(before/f'{f:06d}.png').convert('RGB').crop(box),dtype=np.float32)
    yy,xx=np.mgrid[top:bottom:3,left:right:3]
    weights=np.where(np.hypot((xx-x)/(w/2),(yy-y)/(h/2))<.78,1.,.47)
    base=[rec['veil'],(1-rec['veil'])*.72,0,0]
    def loss(params):
        head,side,white,fill=params
        patch,l,t=registered_portrait(x,y,w,h,rec['tone'][0],'ella',rec['head'],
                gradient=rec['tone'],head_opacity=head,right_fade=side,head_wash=white,disk_wash=fill)
        canvas=Image.new('RGBA',(right-left,bottom-top),(253,253,253,255))
        composite(canvas,blur(patch,tuple(entry['focus'])),l-left,t-top)
        v=np.asarray(canvas.convert('RGB'),dtype=np.float32)[::3,::3]
        d=np.abs(v-a[::3,::3])
        return float(np.mean(weights[...,None]*(d+d*d*.007))) + .36*(head-.92)**2
    v=minimize(loss,base,method='Powell',
               bounds=((.60,1),(0,.97),(0,.94),(0,.55)),options={'maxiter':15,'ftol':.001})
    opts=v.x.tolist()
    print(f,round(float(abs(a-z).mean()),2),round(loss(base),3),round(loss(opts),3),opts,flush=True)
    result[f]=[round(x,4) for x in opts]
(root/'ella-exposure.json').write_text(json.dumps(result,indent=2)+'\n')
