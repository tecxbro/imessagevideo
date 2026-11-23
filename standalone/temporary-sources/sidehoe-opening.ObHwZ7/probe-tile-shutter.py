from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from pathlib import Path
from PIL import Image
from render import Film
import numpy as np
import json

p=Path(__file__).parent
project=p/'tile-cursor-clean'
scene=json.loads((project/'scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
rects={616:(380,649,622,925),617:(380,668,622,950),618:(380,698,622,987),
       619:(380,736,622,1000),620:(380,782,622,1000)}
def score(f):
    s=deepcopy(scene)
    i=next(i for i,t in enumerate(s['tracks']['calendarTileTreatment']) if t[0]==f)
    start=scene['tracks']['calendarTileTreatment'][i]
    shutter=s['tracks']['calendarTileShutter']
    j=next((j for j,t in enumerate(shutter) if t[0]==f),None)
    name=f'{f:06}.png'
    rect=rects[f]
    true=np.asarray(Image.open(source/name).convert('RGB').crop(rect),dtype=np.int16)
    def test(blur, rise, ratio):
        track=s['tracks']['calendarTileTreatment'][i]
        track[1]=start[1]+rise
        track[4]=start[4]*blur
        track[5]=start[5]*ratio
        if j is not None:
            shutter[j][1]=scene['tracks']['calendarTileShutter'][j][1]*blur
        candidate=np.asarray(Film(s).frame(f).crop(rect),dtype=np.int16)
        d=np.abs(candidate-true)
        return float(d.mean())
    control=test(1,0,1)
    before=control
    best=(1,0,1)
    for _ in range(2):
        for i_param,candidates in enumerate(((.55,.65,.75,.85,1,1.15,1.25),(-5,-3,-1,0,1,3,5),
                                               (.975,.99,1,1.01,1.025))):
            for value in candidates:
                options=list(best)
                options[i_param]=value
                current=test(*options)
                if current<control:
                    control=current
                    best=tuple(options)
    print(f,before,control,best,flush=True)
    return f,before,control,best
if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        records=list(pool.map(score, rects))
    (p/'next-tile-shutter.json').write_text(json.dumps(records,indent=2)+'\n')
