from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from copy import copy,deepcopy
from PIL import Image
import numpy as np
import json,sys
from render import Film

p=Path(sys.argv[1])
scene=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
def fit(frame):
    f=str(frame)
    data=copy(scene)
    data['threadRegistration']=deepcopy(scene['threadRegistration'])
    data['sofiaSuggestionRegistration']=deepcopy(scene['sofiaSuggestionRegistration'])
    staged=data['threadRegistration']['sofia'].get(f)
    suggestion=data['sofiaSuggestionRegistration'][f]
    source_frame=np.array(Image.open(source/f'{frame:06}.png').convert('RGB'),dtype=np.int16)
    def score():
        return float(np.abs(np.array(Film(data).frame(frame),dtype=np.int16)-source_frame).mean())
    before=score()
    best=before
    original=3.5*max(0,1-abs(frame-355)/3)
    best_focus=original
    for rad in np.arange(0,5.75,.35):
        suggestion['focus']=float(rad)
        e=score()
        if e<best:
            best,best_focus=e,float(rad)
    patch={}
    if abs(best_focus-original)>.06:
        patch['suggestion']=round(best_focus,3)
        suggestion['focus']=best_focus
    else:
        suggestion.pop('focus',None)
    if staged:
        width=staged['items'][0][0][3]-staged['items'][0][0][1]
        soft=1.25+1.1*(frame-352)
        values=[0,0,soft]
        for i,(scale,initial) in enumerate(zip((1.5,2.0,.5),values.copy(),strict=True)):
            pick=initial
            for offset in (-3,-2,-1,1,2,3):
                values[i]=initial+scale*offset
                if values[2]<.4: continue
                staged['focus']=values
                err=score()
                if err<best:
                    best,pick=err,values[i]
            values[i]=pick
        if values!=[0,0,soft]:
            patch['stage']=values
    print(frame,before,best,patch,flush=True)
    return f,patch

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        result=dict(pool.map(fit,range(352,360)))
    (p/'sofia-focus.json').write_text(json.dumps(result,indent=2)+'\n')
