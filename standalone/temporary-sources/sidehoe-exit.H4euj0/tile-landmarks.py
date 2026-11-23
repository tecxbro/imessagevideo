from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import label,find_objects,binary_closing,binary_fill_holes,binary_erosion
import json,sys

root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
s=json.loads((root/'project/scene.json').read_text())['tracks']
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-assistant.lwAAJj/final-inbox-frames')

def field(im):
    l,t,r,b=345,455,665,1000
    rgb=im[t:b,l:r]
    R,G,B=np.moveaxis(rgb,2,0)
    blue=(B-G>40)&(B-R>51)&(B>=214)&(G<198)&(G>95)
    marks,num=label(binary_closing(blue,iterations=2))
    cells=[]
    for j,(yy,xx) in enumerate(find_objects(marks),1):
        count=(marks[yy,xx]==j).sum()
        if count>=650:
            cells.append((int(count),[l+xx.start,t+yy.start,l+xx.stop,t+yy.stop],j))
    if not cells:
        return {}
    mass,bb,which = max(cells)
    l0,t0,r0,b0=bb
    mask=binary_fill_holes(marks==which)
    interior=binary_erosion(mask,iterations=5)
    neutral=(rgb.min(2)>=209)&(np.ptp(rgb,axis=2)<31)&interior
    ink,k=label(binary_closing(neutral,iterations=1))
    letters=[]
    for j,(yy,xx) in enumerate(find_objects(ink),1):
        count=(ink[yy,xx]==j).sum()
        if count>45 and 30<=yy.stop-yy.start<=170 and xx.stop-xx.start>5:
            letters.append([int(count),[l+xx.start,t+yy.start,l+xx.stop,t+yy.stop]])
    tone=[]
    for v in (.05,.15,.25,.37,.49,.57,.64,.76,.86,.94):
        row=int(t0+(b0-t0)*v)
        a0=round(l0+(r0-l0)*.12);a1=round(l0+(r0-l0)*.88)
        sec=im[row-2:row+3,a0:a1]
        use=(sec[:,:,2]-sec[:,:,0]>51)&(sec[:,:,2]-sec[:,:,1]>40)
        tone.append([row,np.rint(np.median(sec[use],axis=0)).astype(int).tolist()] if use.sum()>20 else None)
    return {'face':bb,'ink':sorted(letters,key=lambda row:row[1][0]),'tone':tone}
records={}
for f in range(602,620):
    q=[field(np.asarray(Image.open(r/f'{f:06d}.png').convert('RGB'),dtype=np.int16)) for r in (source,prior)]
    records[f]=q
    if f in (605,610,613,616,618):
        print(f,*q,sep='\n')
(root/'tile-native-landmarks.json').write_text(json.dumps(records,indent=2)+'\n')
