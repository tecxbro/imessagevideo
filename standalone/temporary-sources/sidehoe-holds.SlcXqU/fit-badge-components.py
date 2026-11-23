"""Measure the closing artwork's four movable parts inside its authored case."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from render import Film

w=Path(sys.argv[1])
scene=json.loads((w/'project/scene.json').read_text())
reference=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
neutral=np.tile((0.0,0.0,1.0,1.0),(4,1))


def keyframe(frame):
    film=Film(scene)
    key=str(frame)
    x,y,width,height=film.track('closingBadgeShape',frame)[:4]
    bounds=round(x-.35*width),round(y-.30*height),round(x+.35*width),round(y+.34*height)
    ref=np.asarray(Image.open(reference/f'{frame:06d}.png').convert('RGB').crop(bounds),np.int16)
    controls={}
    local={**scene,'closingBadgeArtwork':controls}
    film=Film(local)
    def cost():
        a=np.asarray(film.frame(frame).crop(bounds),np.int16)
        return np.abs(a-ref).mean()
    first=best=cost()
    parameters=neutral.copy()
    for precision in (1,.46,.18):
        for i in range(4):
            for k,step in enumerate((2.8,2.6,.026,.022)):
                old=parameters.copy()
                for delta in (-2,-1,1,2):
                    sample=old.copy()
                    sample[i,k]+=delta*step*precision
                    controls[key]=sample.tolist()
                    score=cost()
                    if score<best:
                        best,parameters=score,sample
    print(frame,round(float(first),4),round(float(best),4),parameters.round(4).tolist(),flush=True)
    return frame,parameters


if __name__=='__main__':
    marks=(701,706,716,732,751,765)
    with ProcessPoolExecutor(max_workers=5) as pool:
        fitted=dict(pool.map(keyframe,marks))
    (w/'badge-part-anchors.json').write_text(json.dumps({f:a.round(5).tolist() for f,a in fitted.items()},indent=2)+'\n')
