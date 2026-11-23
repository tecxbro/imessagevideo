"""Fit the dark slot and reflected lip over the editable shell model."""
from pathlib import Path
import json
import sys
import numpy as np
from PIL import Image
from casing import speaker_slot_basis,paint_speaker_slot

w=Path(sys.argv[1])
p=w/'project/scene.json'
scene=json.loads(p.read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
fitted={}
for k,entry in scene['assistantExitCasing'].items():
    frame=int(k)
    if not 139<=frame<=161:
        continue
    top=round(entry[0][1])
    rect=(375,top+5,630,top+28)
    y,x=np.ogrid[rect[1]:rect[3],rect[0]:rect[2]]
    target,base=[np.asarray(Image.open(d/f'{frame:06}.png').convert('RGB').crop(rect),float)
                 for d in (src,w/'casing-probes')]
    residual=target-base
    rgb=residual.reshape(-1,3)
    bound=np.stack(np.broadcast_arrays(x,y),axis=-1)
    metric=lambda image: float(np.mean(np.abs(image-target)))
    original=metric(base)
    def solve(pos):
        basis=speaker_slot_basis(x+.5,y+.5,pos)
        mat=basis.reshape(-1,2)
        coefficients=np.linalg.solve(mat.T@mat+np.eye(2)*.5,mat.T@rgb)
        coefficients=np.clip(coefficients,-63,63)
        composite=np.clip(np.rint(base+basis@coefficients),0,255)
        return metric(composite),coefficients
    g=[501,top+14,91,4,4]
    best,col=solve(g)
    for scale in (1,.48,.23):
        for i,step in enumerate((3,1.35,8,.88,1.15)):
            first=g.copy()
            for n in (-2,-1,1,2):
                proposed=first.copy()
                proposed[i]+=n*step*scale
                if i>=3 and proposed[i]<1.2:
                    continue
                val,c=solve(proposed)
                if val<best:
                    g,best,col=proposed,val,c
    if original-best>.30:
        fitted[k]=[rect,[round(val,3) for val in g],np.round(col,2).tolist()]
    print(frame,round(original,4),round(best,4),k in fitted)
scene['assistantSpeakerSlot']=fitted
p.write_text(json.dumps(scene,indent=2)+'\n')
(w/'slot-fit.json').write_text(json.dumps(fitted,indent=2)+'\n')
