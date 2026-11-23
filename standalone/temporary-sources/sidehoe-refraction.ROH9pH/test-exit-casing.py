"""Ablate overlapping casing effects before recalibrating the handset exit."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image

scratch=Path(sys.argv[1])
sys.path.insert(0,str(scratch/'clean'))
from render import Film

source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
scene=json.loads((scratch/'clean/scene.json').read_text())
omit_options=((), ('RimRegistration',), ('UpperBevel',), ('SideBevels',),
              ('UpperBevel','SideBevels'),('RimRegistration','UpperBevel','SideBevels'))
result={}
for frame in range(156,162):
    target=np.asarray(Image.open(source/f'{frame:06}.png').convert('RGB'),np.int16)
    base_y=Film(scene).track('assistantMeasuredPosition',frame)[1]
    rulers=[]
    for omitted in omit_options:
        version=deepcopy(scene)
        for name in omitted:
            version['assistant'+name].pop(str(frame),None)
        image=Film(version).frame(frame)
        delta=np.abs(np.asarray(image,np.int16)-target)
        y=max(0,round(base_y)-22)
        result.setdefault(str(frame),[]).append(dict(
            removed=omitted, picture=float(delta.mean()), casing=float(delta[y:y+170,42:958].mean())))
        if frame==160:
            rulers.append(image.crop((42,y,958,y+170)))
    if frame==160:
        board=Image.new('RGB',(916,170*7))
        board.paste(Image.fromarray(np.uint8(target[y:y+170,42:958])),(0,0))
        for j,view in enumerate(rulers,1):
            board.paste(view,(0,j*170))
        board.save(scratch/'exit-casing-160.jpg',quality=94)
(scratch/'exit-casing-ablation.json').write_text(json.dumps(result,indent=2)+'\n')
for f,variants in result.items():
    print(f,'base',variants[0]['picture'],'best',min(variants,key=lambda v:v['picture']))
