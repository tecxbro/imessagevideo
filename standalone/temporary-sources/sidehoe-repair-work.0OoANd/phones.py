from pathlib import Path
import json
import numpy as np
from PIL import Image

ROOT=Path('/tmp/sidehoe-fidelity.ESHOT4')
SCENE=json.loads(Path('sidehoe-skill-trial/project/scene.json').read_text())
def load(folder,f):
    return np.asarray(Image.open(ROOT/folder/f'{f:06d}.png'),dtype=np.int16)
def track(name,f):
    a=np.array(SCENE['tracks'][name])
    return [np.interp(f,a[:,0],a[:,i]) for i in range(1,a.shape[1])]
def runs(mask):
    return np.flatnonzero(np.diff(np.r_[False,mask,False])).reshape(-1,2)
def rim(a, name,f):
    sy,scale=track(name+'Camera',f)
    y=a.max(2)
    xl=(500-200*scale)/2
    xr=(500+200*scale)/2
    max_dist=38
    top_rows=np.maximum(0,sy*.5+23)
    bottom_rows=min(500,sy*.5+413.5*scale-18)
    counts=(y[int(top_rows):int(bottom_rows)]<108).sum(0)
    threshold=max(24,round((bottom_rows-top_rows)*.24))
    selected=[(int(l),int(r)) for l,r in runs(counts>threshold) if r-l>=2]
    left=[l for l,r in selected if abs(l-xl)<=max_dist]
    right=[r for l,r in selected if abs(r-xr)<=max_dist]
    if not left or not right:return
    l,r=min(left),max(right)
    if r-l<100:return
    active=(y[:,l+3:r-3]<110).sum(1)
    heavy=np.flatnonzero(active>(r-l)*.42)
    if len(heavy):
        top=min(heavy)
        bottom=max(heavy)+1
    else:top=bottom=None
    return (l,r,top,bottom,selected)

if __name__=='__main__':
 for name,numbers in [('sofia',[313,315,317,318,319,321,325,327,329,330,331,332,333,334,335,336,338,340,345,349,354]),('follow',[624,625,626,628,630,632,634,640,648,650,653,655,659,663,665,667,670,675,680,684,686,687,688,689,690,691,692,693,694,695])]:
    print(name)
    for f in numbers:
        print(f,[rim(load(folder,f),name,f) for folder in ['source','i-boards/review-frames']])
