from concurrent.futures import ProcessPoolExecutor
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.optimize import minimize

sys.path.insert(0, str(Path('project').resolve()))
from treatments import follow_pointer

scratch = Path('/tmp/sidehoe-hyperframes.wG3QA2')
scene = json.loads(Path('project/scene.json').read_text())

def fit(row):
    f, x, y, w, h, soft, alpha = row
    im = Image.open(scratch/'source-stage'/f'{f:06}.png').convert('RGB')
    left, top = int(x)-10, int(y)-9
    shape = (int(w)+28, int(h)+29)
    rgb = np.array(im.crop((left,top,left+shape[0],top+shape[1])), dtype=np.float32)
    observed = np.clip((190-rgb.max(axis=2))/165, 0, 1)
    # The dark alpha metric excludes vivid emoji below the cursor's tip.
    observed[(rgb.max(axis=2)-rgb.min(axis=2))>49] = 0
    def cost(v):
        px,py,wide,high,blur,a = map(float, v)
        rendered=Image.new('RGBA', shape, 'white')
        follow_pointer(rendered,px-left,py-top,wide,high,blur,a)
        icon=np.clip((190-np.asarray(rendered)[:,:,0].astype(float))/165,0,1)
        return np.abs(observed-icon).sum()
    start=[x,y,w,h,soft,alpha]
    bounds=[(x-5,x+5),(y-5,y+5),(w*.73,w*1.38),
            (h*.74,h*1.28),(.28,max(5.4,soft+2)),(min(.66,alpha-.16),1)]
    result=minimize(cost,start,method='Powell',bounds=bounds,
                    options={'maxiter':12,'ftol':.00025,'xtol':.04})
    if cost(start)-result.fun<1.2:
        values=start
    else:
        values=result.x
    return [f,*[round(v,3) for v in values]], round(cost(start),3), round(result.fun,3)

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(fit,scene['tracks']['followPointerStage']))
    (scratch/'fitted-cursor.json').write_text(json.dumps(results,indent=2))
    print(results[:3], results[15],results[-1])
