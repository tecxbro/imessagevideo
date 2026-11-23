"""Evaluate independent tile registrations, including the boundaries of the orbit."""
from pathlib import Path
from PIL import Image
import json,sys
import numpy as np
from render import Film

work=Path(sys.argv[1])
measured=work/'orbit-full-scene.json'
previous=work/'clean/scene.json'
scene=json.loads(measured.read_text())
base=Film(json.loads(previous.read_text()))
next_film=Film(scene)
ref=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
metrics=[]
prev_arrays=None
for f in range(485,615):
    pc=np.asarray(base.frame(f),np.int16)
    fc=np.asarray(next_film.frame(f),np.int16)
    source=np.asarray(Image.open(ref/f'{f:06d}.png').convert('RGB'),np.int16)
    a,b=[float(np.abs(v-source).mean()) for v in (pc,fc)]
    if b>a:
        scene.get('orbitActorFit',{}).pop(str(f),None)
        fc=pc
        b=a
    row={'frame':f,'stage':[a,b]}
    if prev_arrays:
        target=source-prev_arrays[0]
        before=pc-prev_arrays[1]; after=fc-prev_arrays[2]
        row['motion']=[float(np.abs(target-v).mean()) for v in (before,after)]
    metrics.append(row)
    prev_arrays=(source,pc,fc)
    if f in (486,536,554,555,557,558,562,575,612):
        bound=(128,250,900,835)
        strip=Image.new('RGB',(3*(bound[2]-bound[0]),bound[3]-bound[1]))
        for i,arr in enumerate((source,pc,fc)):
            strip.paste(Image.fromarray(arr.astype(np.uint8)).crop(bound),(i*(bound[2]-bound[0]),0))
        strip.thumbnail((1440,540))
        strip.save(work/f'orbit-matched-{f}.jpg',quality=92)
out={'stage_wins':sum(r['stage'][1]<r['stage'][0] for r in metrics),
     'motion_wins':sum(r['motion'][1]<r['motion'][0] for r in metrics if 'motion' in r),
     'views':metrics}
(work/'orbit-stage-metrics.json').write_text(json.dumps(out,indent=2)+'\n')
(work/'orbit-next/scene.json').write_text(json.dumps(scene,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='views'}))
